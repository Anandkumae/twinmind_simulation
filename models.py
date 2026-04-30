"""
SQLAlchemy ORM models for Digital Twin system
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Machine(Base):
    """
    Machine entity representing monitored equipment
    """
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200))
    description = Column(Text)
    machine_type = Column(String(50), default="motor")
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sensor_data = relationship("SensorData", back_populates="machine", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="machine", cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="machine", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Machine(id={self.id}, name='{self.name}', location='{self.location}')>"

class SensorData(Base):
    """
    Sensor readings from machines
    """
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    temperature = Column(Float)
    vibration = Column(Float)
    pressure = Column(Float)
    # Additional sensor fields
    op_setting_1 = Column(Float)
    op_setting_2 = Column(Float)
    op_setting_3 = Column(Float)
    sensor_1 = Column(Float)  # vibration
    sensor_2 = Column(Float)  # temperature
    sensor_3 = Column(Float)  # pressure
    sensor_4 = Column(Float)
    sensor_5 = Column(Float)
    sensor_6 = Column(Float)
    sensor_7 = Column(Float)
    sensor_8 = Column(Float)
    sensor_9 = Column(Float)
    sensor_10 = Column(Float)
    sensor_11 = Column(Float)
    sensor_12 = Column(Float)
    sensor_13 = Column(Float)
    sensor_14 = Column(Float)
    sensor_15 = Column(Float)
    sensor_16 = Column(Float)
    sensor_17 = Column(Float)
    sensor_18 = Column(Float)
    sensor_19 = Column(Float)
    sensor_20 = Column(Float)
    sensor_21 = Column(Float)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    machine = relationship("Machine", back_populates="sensor_data")

    def __repr__(self):
        return f"<SensorData(machine_id={self.machine_id}, temp={self.temperature}, time={self.timestamp})>"

class Prediction(Base):
    """
    RUL predictions and health assessments
    """
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    rul = Column(Float, nullable=False)
    health_score = Column(Float)
    health_status = Column(String(20))  # HEALTHY, WARNING, CRITICAL
    confidence = Column(Float)
    model_type = Column(String(20), default="LSTM")  # LSTM, RULE_BASED
    feature_vector = Column(Text)  # JSON string of features
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    machine = relationship("Machine", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction(machine_id={self.machine_id}, rul={self.rul}, status={self.health_status})>"

class Anomaly(Base):
    """
    Anomaly detection results and alerts
    """
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # TEMPERATURE_HIGH, VIBRATION_HIGH, PRESSURE_LOW, etc.
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    description = Column(Text)
    threshold_value = Column(Float)
    actual_value = Column(Float)
    confidence = Column(Float)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    machine = relationship("Machine", back_populates="anomalies")

    def __repr__(self):
        return f"<Anomaly(machine_id={self.machine_id}, type='{self.type}', severity='{self.severity}')>"

class Maintenance(Base):
    """
    Maintenance records and schedules
    """
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # ROUTINE, URGENT, PREDICTIVE
    description = Column(Text)
    scheduled_date = Column(DateTime)
    completed_date = Column(DateTime)
    cost = Column(Float)
    technician = Column(String(100))
    notes = Column(Text)
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    machine = relationship("Machine")

    def __repr__(self):
        return f"<Maintenance(machine_id={self.machine_id}, type='{self.type}', status='{self.status}')>"

class SystemMetrics(Base):
    """
    System performance and health metrics
    """
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))
    tags = Column(Text)  # JSON string of additional tags
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<SystemMetrics(name='{self.metric_name}', value={self.metric_value})>"
