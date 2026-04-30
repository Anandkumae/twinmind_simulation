"""
Database service layer for Digital Twin system
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from models import Machine, SensorData, Prediction, Anomaly, Maintenance, SystemMetrics
from schemas import (
    MachineCreate, MachineUpdate, SensorDataCreate, PredictionCreate, 
    AnomalyCreate, MaintenanceCreate, MaintenanceUpdate, HealthStatus, 
    AnomalySeverity, AnomalyType
)

logger = logging.getLogger(__name__)

class MachineService:
    """Service for machine operations"""
    
    @staticmethod
    def create_machine(db: Session, machine: MachineCreate) -> Machine:
        """Create a new machine"""
        db_machine = Machine(**machine.dict())
        db.add(db_machine)
        db.commit()
        db.refresh(db_machine)
        logger.info(f"Created machine: {db_machine.name}")
        return db_machine
    
    @staticmethod
    def get_machines(db: Session, skip: int = 0, limit: int = 100) -> List[Machine]:
        """Get all machines"""
        return db.query(Machine).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_machine(db: Session, machine_id: int) -> Optional[Machine]:
        """Get machine by ID"""
        return db.query(Machine).filter(Machine.id == machine_id).first()
    
    @staticmethod
    def update_machine(db: Session, machine_id: int, machine: MachineUpdate) -> Optional[Machine]:
        """Update machine"""
        db_machine = db.query(Machine).filter(Machine.id == machine_id).first()
        if db_machine:
            for key, value in machine.dict(exclude_unset=True).items():
                setattr(db_machine, key, value)
            db_machine.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_machine)
            logger.info(f"Updated machine: {db_machine.name}")
        return db_machine
    
    @staticmethod
    def delete_machine(db: Session, machine_id: int) -> bool:
        """Delete machine"""
        db_machine = db.query(Machine).filter(Machine.id == machine_id).first()
        if db_machine:
            db.delete(db_machine)
            db.commit()
            logger.info(f"Deleted machine: {machine_id}")
            return True
        return False
    
    @staticmethod
    def get_machine_count(db: Session) -> int:
        """Get total machine count"""
        return db.query(Machine).count()

class SensorDataService:
    """Service for sensor data operations"""
    
    @staticmethod
    def create_sensor_data(db: Session, sensor_data: SensorDataCreate) -> SensorData:
        """Create new sensor reading"""
        db_sensor_data = SensorData(**sensor_data.dict())
        db.add(db_sensor_data)
        db.commit()
        db.refresh(db_sensor_data)
        return db_sensor_data
    
    @staticmethod
    def get_latest_sensor_data(db: Session, machine_id: int, limit: int = 10) -> List[SensorData]:
        """Get latest sensor data for machine"""
        return db.query(SensorData)\
                .filter(SensorData.machine_id == machine_id)\
                .order_by(desc(SensorData.timestamp))\
                .limit(limit)\
                .all()
    
    @staticmethod
    def get_sensor_data_by_timerange(
        db: Session, 
        machine_id: int, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[SensorData]:
        """Get sensor data for specific time range"""
        return db.query(SensorData)\
                .filter(
                    and_(
                        SensorData.machine_id == machine_id,
                        SensorData.timestamp >= start_time,
                        SensorData.timestamp <= end_time
                    )
                )\
                .order_by(desc(SensorData.timestamp))\
                .all()
    
    @staticmethod
    def get_all_latest_data(db: Session) -> List[Dict[str, Any]]:
        """Get latest data for all machines"""
        # Subquery to get latest timestamp for each machine
        latest_data = db.query(
            SensorData.machine_id,
            func.max(SensorData.timestamp).label('latest_timestamp')
        ).group_by(SensorData.machine_id).subquery()
        
        # Join with main table to get full records
        return db.query(SensorData)\
                .join(
                    latest_data,
                    and_(
                        SensorData.machine_id == latest_data.c.machine_id,
                        SensorData.timestamp == latest_data.c.latest_timestamp
                    )
                )\
                .all()
    
    @staticmethod
    def get_sensor_statistics(db: Session, machine_id: int, hours: int = 24) -> Dict[str, float]:
        """Get sensor statistics for last N hours"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        stats = db.query(
            func.avg(SensorData.temperature).label('avg_temp'),
            func.min(SensorData.temperature).label('min_temp'),
            func.max(SensorData.temperature).label('max_temp'),
            func.avg(SensorData.vibration).label('avg_vib'),
            func.min(SensorData.vibration).label('min_vib'),
            func.max(SensorData.vibration).label('max_vib'),
            func.avg(SensorData.pressure).label('avg_pressure'),
            func.min(SensorData.pressure).label('min_pressure'),
            func.max(SensorData.pressure).label('max_pressure'),
            func.count(SensorData.id).label('data_points')
        ).filter(
            and_(
                SensorData.machine_id == machine_id,
                SensorData.timestamp >= start_time
            )
        ).first()
        
        return {
            'temperature': {
                'avg': float(stats.avg_temp) if stats.avg_temp else 0,
                'min': float(stats.min_temp) if stats.min_temp else 0,
                'max': float(stats.max_temp) if stats.max_temp else 0
            },
            'vibration': {
                'avg': float(stats.avg_vib) if stats.avg_vib else 0,
                'min': float(stats.min_vib) if stats.min_vib else 0,
                'max': float(stats.max_vib) if stats.max_vib else 0
            },
            'pressure': {
                'avg': float(stats.avg_pressure) if stats.avg_pressure else 0,
                'min': float(stats.min_pressure) if stats.min_pressure else 0,
                'max': float(stats.max_pressure) if stats.max_pressure else 0
            },
            'data_points': int(stats.data_points) if stats.data_points else 0
        }

class PredictionService:
    """Service for prediction operations"""
    
    @staticmethod
    def create_prediction(db: Session, prediction: PredictionCreate) -> Prediction:
        """Create new prediction"""
        db_prediction = Prediction(**prediction.dict())
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        return db_prediction
    
    @staticmethod
    def get_latest_prediction(db: Session, machine_id: int) -> Optional[Prediction]:
        """Get latest prediction for machine"""
        return db.query(Prediction)\
                .filter(Prediction.machine_id == machine_id)\
                .order_by(desc(Prediction.created_at))\
                .first()
    
    @staticmethod
    def get_prediction_history(db: Session, machine_id: int, limit: int = 50) -> List[Prediction]:
        """Get prediction history for machine"""
        return db.query(Prediction)\
                .filter(Prediction.machine_id == machine_id)\
                .order_by(desc(Prediction.created_at))\
                .limit(limit)\
                .all()
    
    @staticmethod
    def get_rul_trend(db: Session, machine_id: int, hours: int = 24) -> List[Dict[str, Any]]:
        """Get RUL trend for last N hours"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        predictions = db.query(Prediction)\
                       .filter(
                           and_(
                               Prediction.machine_id == machine_id,
                               Prediction.created_at >= start_time
                           )
                       )\
                       .order_by(Prediction.created_at)\
                       .all()
        
        return [
            {
                'timestamp': pred.created_at,
                'rul': pred.rul,
                'health_score': pred.health_score,
                'health_status': pred.health_status
            }
            for pred in predictions
        ]

class AnomalyService:
    """Service for anomaly operations"""
    
    @staticmethod
    def create_anomaly(db: Session, anomaly: AnomalyCreate) -> Anomaly:
        """Create new anomaly"""
        db_anomaly = Anomaly(**anomaly.dict())
        db.add(db_anomaly)
        db.commit()
        db.refresh(db_anomaly)
        logger.warning(f"Created anomaly: {anomaly.type} for machine {anomaly.machine_id}")
        return db_anomaly
    
    @staticmethod
    def get_active_anomalies(db: Session, machine_id: Optional[int] = None) -> List[Anomaly]:
        """Get active (unresolved) anomalies"""
        query = db.query(Anomaly).filter(Anomaly.resolved == False)
        if machine_id:
            query = query.filter(Anomaly.machine_id == machine_id)
        return query.order_by(desc(Anomaly.created_at)).all()
    
    @staticmethod
    def get_anomaly_history(db: Session, machine_id: int, limit: int = 50) -> List[Anomaly]:
        """Get anomaly history for machine"""
        return db.query(Anomaly)\
                .filter(Anomaly.machine_id == machine_id)\
                .order_by(desc(Anomaly.created_at))\
                .limit(limit)\
                .all()
    
    @staticmethod
    def resolve_anomaly(db: Session, anomaly_id: int) -> Optional[Anomaly]:
        """Mark anomaly as resolved"""
        db_anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if db_anomaly:
            db_anomaly.resolved = True
            db_anomaly.resolved_at = datetime.utcnow()
            db.commit()
            db.refresh(db_anomaly)
            logger.info(f"Resolved anomaly: {anomaly_id}")
        return db_anomaly
    
    @staticmethod
    def get_anomaly_statistics(db: Session, hours: int = 24) -> Dict[str, Any]:
        """Get anomaly statistics for last N hours"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        total_anomalies = db.query(Anomaly)\
                          .filter(Anomaly.created_at >= start_time)\
                          .count()
        
        unresolved_anomalies = db.query(Anomaly)\
                               .filter(
                                   and_(
                                       Anomaly.created_at >= start_time,
                                       Anomaly.resolved == False
                                   )
                               )\
                               .count()
        
        severity_counts = db.query(
            Anomaly.severity,
            func.count(Anomaly.id).label('count')
        ).filter(Anomaly.created_at >= start_time)\
         .group_by(Anomaly.severity)\
         .all()
        
        return {
            'total_anomalies': total_anomalies,
            'unresolved_anomalies': unresolved_anomalies,
            'severity_breakdown': {
                sev: count for sev, count in severity_counts
            }
        }

class MaintenanceService:
    """Service for maintenance operations"""
    
    @staticmethod
    def create_maintenance(db: Session, maintenance: MaintenanceCreate) -> Maintenance:
        """Create new maintenance record"""
        db_maintenance = Maintenance(**maintenance.dict())
        db.add(db_maintenance)
        db.commit()
        db.refresh(db_maintenance)
        return db_maintenance
    
    @staticmethod
    def get_upcoming_maintenance(db: Session, machine_id: Optional[int] = None, days: int = 30) -> List[Maintenance]:
        """Get upcoming maintenance"""
        future_date = datetime.utcnow() + timedelta(days=days)
        query = db.query(Maintenance)\
                .filter(
                    and_(
                        Maintenance.scheduled_date <= future_date,
                        Maintenance.status == 'scheduled'
                    )
                )
        if machine_id:
            query = query.filter(Maintenance.machine_id == machine_id)
        return query.order_by(Maintenance.scheduled_date).all()
    
    @staticmethod
    def update_maintenance(db: Session, maintenance_id: int, maintenance: MaintenanceUpdate) -> Optional[Maintenance]:
        """Update maintenance record"""
        db_maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
        if db_maintenance:
            for key, value in maintenance.dict(exclude_unset=True).items():
                setattr(db_maintenance, key, value)
            db_maintenance.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_maintenance)
        return db_maintenance

class SystemService:
    """Service for system-wide operations"""
    
    @staticmethod
    def get_system_health(db: Session) -> Dict[str, Any]:
        """Get overall system health"""
        total_machines = db.query(Machine).count()
        
        # Get latest predictions for all machines
        latest_predictions = db.query(
            Prediction.machine_id,
            Prediction.health_status,
            Prediction.rul
        ).distinct(Prediction.machine_id)\
         .order_by(Prediction.machine_id, desc(Prediction.created_at))\
         .all()
        
        # Count health statuses
        health_counts = {
            'HEALTHY': 0,
            'WARNING': 0,
            'CRITICAL': 0,
            'COLLECTING': 0
        }
        
        total_rul = 0
        valid_rul_count = 0
        
        for pred in latest_predictions:
            status = pred.health_status or 'COLLECTING'
            health_counts[status] = health_counts.get(status, 0) + 1
            
            if pred.rul and pred.rul > 0:
                total_rul += pred.rul
                valid_rul_count += 1
        
        # Calculate system health score
        health_weights = {'HEALTHY': 100, 'WARNING': 60, 'CRITICAL': 20, 'COLLECTING': 80}
        total_weighted_score = sum(
            health_counts[status] * weight 
            for status, weight in health_weights.items()
        )
        system_health_score = total_weighted_score / total_machines if total_machines > 0 else 0
        
        # Get anomaly statistics
        anomaly_stats = AnomalyService.get_anomaly_statistics(db, hours=24)
        
        return {
            'total_machines': total_machines,
            'healthy_machines': health_counts['HEALTHY'],
            'warning_machines': health_counts['WARNING'],
            'critical_machines': health_counts['CRITICAL'],
            'collecting_machines': health_counts['COLLECTING'],
            'average_rul': total_rul / valid_rul_count if valid_rul_count > 0 else 0,
            'system_health_score': round(system_health_score, 1),
            'total_anomalies': anomaly_stats['total_anomalies'],
            'unresolved_anomalies': anomaly_stats['unresolved_anomalies'],
            'last_updated': datetime.utcnow()
        }
    
    @staticmethod
    def store_system_metric(db: Session, metric_name: str, metric_value: float, unit: str = None, tags: str = None):
        """Store system metric"""
        metric = SystemMetrics(
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=unit,
            tags=tags
        )
        db.add(metric)
        db.commit()
    
    @staticmethod
    def get_system_metrics(db: Session, metric_name: str, hours: int = 24) -> List[SystemMetrics]:
        """Get system metrics history"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        return db.query(SystemMetrics)\
                .filter(
                    and_(
                        SystemMetrics.metric_name == metric_name,
                        SystemMetrics.timestamp >= start_time
                    )
                )\
                .order_by(desc(SystemMetrics.timestamp))\
                .all()

# Service instances
machine_service = MachineService()
sensor_data_service = SensorDataService()
prediction_service = PredictionService()
anomaly_service = AnomalyService()
maintenance_service = MaintenanceService()
system_service = SystemService()
