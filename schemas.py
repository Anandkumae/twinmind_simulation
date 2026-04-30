"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums for validation
class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    COLLECTING = "COLLECTING"

class AnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AnomalyType(str, Enum):
    TEMPERATURE_HIGH = "TEMPERATURE_HIGH"
    TEMPERATURE_LOW = "TEMPERATURE_LOW"
    VIBRATION_HIGH = "VIBRATION_HIGH"
    VIBRATION_LOW = "VIBRATION_LOW"
    PRESSURE_HIGH = "PRESSURE_HIGH"
    PRESSURE_LOW = "PRESSURE_LOW"
    RUL_LOW = "RUL_LOW"
    SENSOR_FAILURE = "SENSOR_FAILURE"
    COMMUNICATION_ERROR = "COMMUNICATION_ERROR"

class ModelType(str, Enum):
    LSTM = "LSTM"
    RULE_BASED = "RULE_BASED"
    ENSEMBLE = "ENSEMBLE"

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Machine schemas
class MachineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    machine_type: str = Field(default="motor", max_length=50)
    status: str = Field(default="active", max_length=20)

class MachineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    machine_type: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=20)

class Machine(BaseModel):
    id: int
    name: str
    location: Optional[str]
    description: Optional[str]
    machine_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Sensor data schemas
class SensorDataCreate(BaseModel):
    machine_id: int = Field(..., gt=0)
    temperature: Optional[float] = Field(None, ge=-50, le=200)
    vibration: Optional[float] = Field(None, ge=0, le=50)
    pressure: Optional[float] = Field(None, ge=0, le=20)
    # Full sensor data option
    op_setting_1: Optional[float] = None
    op_setting_2: Optional[float] = None
    op_setting_3: Optional[float] = None
    sensor_1: Optional[float] = None
    sensor_2: Optional[float] = None
    sensor_3: Optional[float] = None
    sensor_4: Optional[float] = None
    sensor_5: Optional[float] = None
    sensor_6: Optional[float] = None
    sensor_7: Optional[float] = None
    sensor_8: Optional[float] = None
    sensor_9: Optional[float] = None
    sensor_10: Optional[float] = None
    sensor_11: Optional[float] = None
    sensor_12: Optional[float] = None
    sensor_13: Optional[float] = None
    sensor_14: Optional[float] = None
    sensor_15: Optional[float] = None
    sensor_16: Optional[float] = None
    sensor_17: Optional[float] = None
    sensor_18: Optional[float] = None
    sensor_19: Optional[float] = None
    sensor_20: Optional[float] = None
    sensor_21: Optional[float] = None

class SensorData(BaseModel):
    id: int
    machine_id: int
    temperature: Optional[float]
    vibration: Optional[float]
    pressure: Optional[float]
    timestamp: datetime

    class Config:
        from_attributes = True

# Prediction schemas
class PredictionCreate(BaseModel):
    machine_id: int = Field(..., gt=0)
    rul: float = Field(..., ge=0)
    health_score: Optional[float] = Field(None, ge=0, le=100)
    health_status: Optional[HealthStatus] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    model_type: Optional[ModelType] = ModelType.LSTM
    feature_vector: Optional[str] = None

class Prediction(BaseModel):
    id: int
    machine_id: int
    rul: float
    health_score: Optional[float]
    health_status: Optional[str]
    confidence: Optional[float]
    model_type: str
    feature_vector: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Anomaly schemas
class AnomalyCreate(BaseModel):
    machine_id: int = Field(..., gt=0)
    type: AnomalyType
    severity: AnomalySeverity
    description: Optional[str] = None
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)

class AnomalyUpdate(BaseModel):
    resolved: Optional[bool] = None
    resolved_at: Optional[datetime] = None
    description: Optional[str] = None

class Anomaly(BaseModel):
    id: int
    machine_id: int
    type: str
    severity: str
    description: Optional[str]
    threshold_value: Optional[float]
    actual_value: Optional[float]
    confidence: Optional[float]
    resolved: bool
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# Maintenance schemas
class MaintenanceCreate(BaseModel):
    machine_id: int = Field(..., gt=0)
    type: str = Field(..., max_length=50)
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    cost: Optional[float] = Field(None, ge=0)
    technician: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

class MaintenanceUpdate(BaseModel):
    type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    cost: Optional[float] = Field(None, ge=0)
    technician: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)

class Maintenance(BaseModel):
    id: int
    machine_id: int
    type: str
    description: Optional[str]
    scheduled_date: Optional[datetime]
    completed_date: Optional[datetime]
    cost: Optional[float]
    technician: Optional[str]
    notes: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Response schemas
class MachineStatus(BaseModel):
    machine_id: int
    machine_name: Optional[str]
    latest_sensor_data: Optional[SensorData]
    latest_prediction: Optional[Prediction]
    active_anomalies: List[Anomaly]
    health_score: Optional[float]
    health_status: Optional[str]
    last_updated: Optional[datetime]

class SystemHealth(BaseModel):
    total_machines: int
    healthy_machines: int
    warning_machines: int
    critical_machines: int
    collecting_machines: int
    total_anomalies: int
    unresolved_anomalies: int
    system_health_score: float
    last_updated: datetime

class PredictionResponse(BaseModel):
    machine_id: int
    rul: Optional[float]
    health: Optional[str]
    health_score: Optional[float]
    anomaly: Optional[str]
    confidence: Optional[float]
    timestamp: str

# Report schemas
class ReportRequest(BaseModel):
    report_type: str = Field(default="summary", pattern="^(summary|detailed|health|performance)$")
    machine_ids: Optional[List[int]] = None
    date_range: Optional[Dict[str, str]] = None
    format: str = Field(default="html", pattern="^(html|json|pdf)$")
    include_charts: bool = True
    include_recommendations: bool = True

# Simulation schemas
class SimulationInput(BaseModel):
    temperature: float = Field(..., ge=0, le=200)
    vibration: float = Field(..., ge=0, le=50)
    pressure: float = Field(..., ge=0, le=20)
    use_ml_model: bool = True

class SimulationResult(BaseModel):
    rul: Optional[float]
    health: Optional[str]
    health_score: Optional[float]
    risk_level: str
    confidence: Optional[float]
    recommendations: List[str]
    processing_time: float

# WebSocket message schemas
class WebSocketMessage(BaseModel):
    type: str
    machine_id: Optional[int]
    data: Dict[str, Any]
    timestamp: datetime

class SensorUpdateMessage(BaseModel):
    type: str = "sensor_update"
    machine_id: int
    temperature: Optional[float]
    vibration: Optional[float]
    pressure: Optional[float]
    rul: Optional[float]
    health: Optional[str]
    anomaly: Optional[str]
    timestamp: datetime
