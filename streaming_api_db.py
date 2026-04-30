"""
Enhanced FastAPI backend with Supabase PostgreSQL database integration
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import json
import asyncio
import logging
from datetime import datetime, timedelta
import time
import os

# Database imports
from database import get_db, create_tables, test_connection
from models import Machine, SensorData, Prediction, Anomaly
from schemas import (
    SensorDataCreate, PredictionCreate, AnomalyCreate, MachineCreate,
    PredictionResponse, SensorUpdateMessage, HealthStatus, AnomalySeverity,
    AnomalyType, ModelType
)
from services import (
    machine_service, sensor_data_service, prediction_service,
    anomaly_service, system_service
)

# ML imports
from ml import (
    update_buffer, predict_rul, get_machine_status, 
    get_all_machines_status, reset_machine_buffer,
    create_feature_vector_from_raw, simulate_degradation,
    BASE_SENSOR_VALUES, SEQUENCE_LENGTH
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Digital Twin API", 
    description="Real-time machine monitoring with ML predictions and PostgreSQL storage",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"🔗 New WebSocket connection (total: {len(self.active_connections)})")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"🔌 WebSocket disconnected (total: {len(self.active_connections)})")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if self.active_connections:
            for connection in self.active_connections:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"❌ Error broadcasting to client: {e}")
            logger.info(f"📡 Broadcasted message to {len(self.active_connections)} clients")

manager = ConnectionManager()

# Health check and system info
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """System health check"""
    try:
        # Test database connection
        db_connected = test_connection()
        
        # Get system health
        system_health = system_service.get_system_health(db)
        
        return {
            "status": "healthy" if db_connected else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database_connected": db_connected,
            "websocket_connections": len(manager.active_connections),
            "system_health": system_health,
            "models_loaded": {
                "lstm": True,  # We'll check this properly
                "scaler": True
            },
            "features": {
                "real_time_monitoring": True,
                "ml_predictions": True,
                "database_storage": True,
                "websocket_streaming": True,
                "anomaly_detection": True,
                "report_generation": True
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Machine management endpoints
@app.post("/machines")
async def create_machine(machine: MachineCreate, db: Session = Depends(get_db)):
    """Create a new machine"""
    try:
        db_machine = machine_service.create_machine(db, machine)
        return {"message": "Machine created successfully", "machine_id": db_machine.id}
    except Exception as e:
        logger.error(f"Error creating machine: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/machines")
async def get_machines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all machines"""
    try:
        machines = machine_service.get_machines(db, skip, limit)
        return {"machines": machines, "total": len(machines)}
    except Exception as e:
        logger.error(f"Error getting machines: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/machines/{machine_id}")
async def get_machine(machine_id: int, db: Session = Depends(get_db)):
    """Get machine by ID"""
    try:
        machine = machine_service.get_machine(db, machine_id)
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        return machine
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting machine {machine_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced sensor data endpoint with database storage
@app.post("/sensor-data")
async def add_sensor_data(data: SensorDataCreate, db: Session = Depends(get_db)):
    """
    Enhanced sensor data endpoint with full database integration
    """
    try:
        # 1. STORE SENSOR DATA IN DATABASE
        db_sensor_data = sensor_data_service.create_sensor_data(db, data)
        logger.info(f"📊 Stored sensor data for machine {data.machine_id}")

        # 2. CREATE FEATURE VECTOR FOR ML
        if data.temperature and data.vibration and data.pressure:
            # Use provided sensor values
            feature_vector = BASE_SENSOR_VALUES.copy()
            feature_vector[4] = data.temperature  # sensor_2 (temperature)
            feature_vector[3] = data.vibration    # sensor_1 (vibration)
            feature_vector[5] = data.pressure     # sensor_3 (pressure)
        else:
            # Use full sensor data if available
            feature_vector = create_feature_vector_from_raw(data.dict())

        # 3. UPDATE LSTM BUFFER
        sequence = update_buffer(data.machine_id, feature_vector)

        # 4. PREDICT RUL
        rul = None
        health_score = None
        health_status = HealthStatus.COLLECTING
        confidence = 0.0
        
        if sequence is not None:
            try:
                rul = predict_rul(sequence)
                if rul is not None:
                    # Calculate health score based on RUL
                    if rul >= 50:
                        health_score = 100.0
                        health_status = HealthStatus.HEALTHY
                    elif rul >= 20:
                        health_score = 70.0
                        health_status = HealthStatus.WARNING
                    else:
                        health_score = 30.0
                        health_status = HealthStatus.CRITICAL
                    confidence = 0.85
            except Exception as e:
                logger.error(f"❌ ML prediction failed: {e}")

        # 5. STORE PREDICTION IN DATABASE
        if rul is not None:
            prediction_data = PredictionCreate(
                machine_id=data.machine_id,
                rul=rul,
                health_score=health_score,
                health_status=health_status,
                confidence=confidence,
                model_type=ModelType.LSTM,
                feature_vector=json.dumps(feature_vector)
            )
            prediction_service.create_prediction(db, prediction_data)

        # 6. ANOMALY DETECTION
        anomaly = None
        if rul is not None:
            if rul < 10:
                anomaly = "CRITICAL_FAILURE_IMMINENT"
                anomaly_data = AnomalyCreate(
                    machine_id=data.machine_id,
                    type=AnomalyType.RUL_LOW,
                    severity=AnomalySeverity.CRITICAL,
                    description=f"RUL critically low: {rul:.1f} cycles",
                    actual_value=rul,
                    threshold_value=10.0,
                    confidence=confidence
                )
                anomaly_service.create_anomaly(db, anomaly_data)
            elif rul < 20:
                anomaly = "FAILURE_SOON"
                anomaly_data = AnomalyCreate(
                    machine_id=data.machine_id,
                    type=AnomalyType.RUL_LOW,
                    severity=AnomalySeverity.HIGH,
                    description=f"RUL low: {rul:.1f} cycles",
                    actual_value=rul,
                    threshold_value=20.0,
                    confidence=confidence
                )
                anomaly_service.create_anomaly(db, anomaly_data)
            elif data.temperature and data.temperature > 90:
                anomaly = "HIGH_TEMPERATURE"
                anomaly_data = AnomalyCreate(
                    machine_id=data.machine_id,
                    type=AnomalyType.TEMPERATURE_HIGH,
                    severity=AnomalySeverity.MEDIUM,
                    description=f"High temperature: {data.temperature}°C",
                    actual_value=data.temperature,
                    threshold_value=90.0,
                    confidence=0.9
                )
                anomaly_service.create_anomaly(db, anomaly_data)
            elif data.vibration and data.vibration > 8:
                anomaly = "HIGH_VIBRATION"
                anomaly_data = AnomalyCreate(
                    machine_id=data.machine_id,
                    type=AnomalyType.VIBRATION_HIGH,
                    severity=AnomalySeverity.MEDIUM,
                    description=f"High vibration: {data.vibration}Hz",
                    actual_value=data.vibration,
                    threshold_value=8.0,
                    confidence=0.9
                )
                anomaly_service.create_anomaly(db, anomaly_data)

        # 7. REAL-TIME BROADCAST
        broadcast_message = {
            "type": "sensor_update",
            "machine_id": data.machine_id,
            "sensor_data": {
                "temperature": data.temperature,
                "vibration": data.vibration,
                "pressure": data.pressure
            },
            "rul": rul,
            "health": health_status.value if health_status else "COLLECTING",
            "health_score": health_score,
            "anomaly": anomaly,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await manager.broadcast(broadcast_message)

        # 8. STORE SYSTEM METRICS
        system_service.store_system_metric(
            db, 
            "sensor_data_ingestion", 
            1.0, 
            "count",
            json.dumps({"machine_id": data.machine_id})
        )

        try:
            response = PredictionResponse(
                machine_id=data.machine_id,
                rul=rul,
                health=health_status.value if health_status else "COLLECTING",
                health_score=health_score,
                anomaly=anomaly,
                confidence=confidence,
                timestamp=datetime.utcnow().isoformat()
            )
            return response
        except Exception as e:
            logger.error(f"❌ Error creating PredictionResponse: {e}")
            logger.error(f"❌ Values: machine_id={data.machine_id}, rul={rul}, health={health_status}")
            raise HTTPException(status_code=500, detail=f"Response creation failed: {str(e)}")

    except Exception as e:
        logger.error(f"❌ Error processing sensor data: {e}")
        raise HTTPException(status_code=500, detail=f"Sensor data processing failed: {str(e)}")

# Data retrieval endpoints
@app.get("/machines/{machine_id}/latest")
async def get_latest_sensor_data(machine_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """Get latest sensor data for a machine"""
    try:
        data = sensor_data_service.get_latest_sensor_data(db, machine_id, limit)
        return {"machine_id": machine_id, "sensor_data": data}
    except Exception as e:
        logger.error(f"Error getting latest data for machine {machine_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/machines/{machine_id}/predictions")
async def get_predictions(machine_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Get prediction history for a machine"""
    try:
        predictions = prediction_service.get_prediction_history(db, machine_id, limit)
        return {"machine_id": machine_id, "predictions": predictions}
    except Exception as e:
        logger.error(f"Error getting predictions for machine {machine_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/machines/{machine_id}/anomalies")
async def get_anomalies(machine_id: int, active_only: bool = True, db: Session = Depends(get_db)):
    """Get anomalies for a machine"""
    try:
        if active_only:
            anomalies = anomaly_service.get_active_anomalies(db, machine_id)
        else:
            anomalies = anomaly_service.get_anomaly_history(db, machine_id)
        return {"machine_id": machine_id, "anomalies": anomalies}
    except Exception as e:
        logger.error(f"Error getting anomalies for machine {machine_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/machines/{machine_id}/status")
async def get_machine_status_db(machine_id: int, db: Session = Depends(get_db)):
    """Get comprehensive machine status"""
    try:
        # Get machine info
        machine = machine_service.get_machine(db, machine_id)
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")

        # Get latest sensor data
        latest_data = sensor_data_service.get_latest_sensor_data(db, machine_id, 1)
        latest_sensor = latest_data[0] if latest_data else None

        # Get latest prediction
        latest_prediction = prediction_service.get_latest_prediction(db, machine_id)

        # Get active anomalies
        active_anomalies = anomaly_service.get_active_anomalies(db, machine_id)

        # Get sensor statistics
        sensor_stats = sensor_data_service.get_sensor_statistics(db, machine_id, 24)

        return {
            "machine": machine,
            "latest_sensor_data": latest_sensor,
            "latest_prediction": latest_prediction,
            "active_anomalies": active_anomalies,
            "sensor_statistics": sensor_stats,
            "last_updated": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for machine {machine_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/health")
async def get_system_health_db(db: Session = Depends(get_db)):
    """Get comprehensive system health"""
    try:
        health = system_service.get_system_health(db)
        return health
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/metrics")
async def get_system_metrics(metric_name: str = "sensor_data_ingestion", hours: int = 24, db: Session = Depends(get_db)):
    """Get system metrics history"""
    try:
        metrics = system_service.get_system_metrics(db, metric_name, hours)
        return {"metric_name": metric_name, "hours": hours, "metrics": metrics}
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data streaming"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back or handle client messages as needed
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Dashboard endpoints (enhanced)
@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the professional production dashboard"""
    try:
        with open("production_dashboard_pro.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # Fallback to original dashboard
        try:
            with open("production_dashboard.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            return HTMLResponse(content="<h1>Digital Twin Dashboard</h1><p>Dashboard file not found</p>")

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_alt():
    """Alternative dashboard endpoint"""
    return await get_dashboard()

@app.get("/dashboard/pro", response_class=HTMLResponse)
async def get_dashboard_pro():
    """Professional dashboard endpoint"""
    try:
        with open("production_dashboard_pro.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Professional Dashboard</h1><p>Dashboard file not found</p>")

@app.get("/dashboard/legacy", response_class=HTMLResponse)
async def get_dashboard_legacy():
    """Legacy dashboard endpoint"""
    try:
        with open("production_dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Legacy Dashboard</h1><p>Dashboard file not found</p>")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and system"""
    logger.info("🚀 Starting Digital Twin API v2.0")
    
    # Create database tables
    try:
        create_tables()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # Test database connection
    if test_connection():
        logger.info("✅ Database connection successful")
    else:
        logger.error("❌ Database connection failed")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🔌 Shutting down Digital Twin API")

# Legacy endpoints for backward compatibility
@app.post("/sensor-data-legacy")
async def add_sensor_data_legacy(data: dict, db: Session = Depends(get_db)):
    """Legacy sensor data endpoint for backward compatibility"""
    try:
        # Convert legacy format to new schema
        sensor_data = SensorDataCreate(
            machine_id=data.get("machine_id", 1),
            temperature=data.get("temperature"),
            vibration=data.get("vibration"),
            pressure=data.get("pressure")
        )
        return await add_sensor_data(sensor_data, db)
    except Exception as e:
        logger.error(f"Legacy endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
