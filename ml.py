import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import joblib
from typing import List, Optional, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🟢 STEP 1: LOAD MODEL IN BACKEND
try:
    model = load_model("lstm_rul_model.h5", compile=False)
    model.compile(optimizer="adam", loss="mse")
    logger.info("✅ LSTM model loaded successfully")
except Exception as e:
    logger.error(f"❌ Error loading LSTM model: {e}")
    model = None

try:
    scaler = joblib.load("scaler.pkl")
    logger.info("✅ Scaler loaded successfully")
except Exception as e:
    logger.error(f"❌ Error loading scaler: {e}")
    scaler = None

# Constants
SEQUENCE_LENGTH = 30
FEATURES = 24  # 3 op_settings + 21 sensors

# 🟢 STEP 2: CREATE MEMORY BUFFER (VERY IMPORTANT)
machine_buffers: Dict[int, List[List[float]]] = {}

# 🟢 STEP 3: UPDATE BUFFER FUNCTION
def update_buffer(machine_id: int, new_data: List[float]) -> List[List[float]]:
    """
    Update the rolling buffer for a specific machine.
    
    Args:
        machine_id: Unique identifier for the machine
        new_data: Feature vector for the current reading
    
    Returns:
        Updated buffer (last SEQUENCE_LENGTH readings)
    """
    if machine_id not in machine_buffers:
        machine_buffers[machine_id] = []
        logger.info(f"🆕 Created new buffer for machine {machine_id}")

    machine_buffers[machine_id].append(new_data)

    # Keep only last SEQUENCE_LENGTH readings
    if len(machine_buffers[machine_id]) > SEQUENCE_LENGTH:
        machine_buffers[machine_id] = machine_buffers[machine_id][-SEQUENCE_LENGTH:]

    return machine_buffers[machine_id]

# 🟢 STEP 4: PREDICT FUNCTION
def predict_rul(sequence: List[List[float]]) -> Optional[float]:
    """
    Predict RUL using LSTM model from sequence data.
    
    Args:
        sequence: List of feature vectors (SEQUENCE_LENGTH x FEATURES)
    
    Returns:
        Predicted RUL or None if insufficient data
    """
    if model is None or scaler is None:
        logger.error("❌ Model or scaler not loaded")
        return None
    
    if len(sequence) < SEQUENCE_LENGTH:
        logger.info(f"⏳ Insufficient data: {len(sequence)}/{SEQUENCE_LENGTH}")
        return None

    try:
        # Convert to numpy array and reshape
        seq_array = np.array(sequence)
        
        # Scale the sequence (scale each reading)
        scaled_sequence = scaler.transform(seq_array)
        
        # Reshape for LSTM: (1, SEQUENCE_LENGTH, FEATURES)
        lstm_input = scaled_sequence.reshape(1, SEQUENCE_LENGTH, FEATURES)
        
        # Make prediction
        prediction = model.predict(lstm_input, verbose=0)
        
        rul = float(prediction[0][0])
        logger.info(f"🔮 RUL prediction: {rul:.2f}")
        
        return rul
        
    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        return None

def get_machine_status(machine_id: int) -> Dict:
    """
    Get current status of a machine including buffer length and last prediction.
    
    Args:
        machine_id: Machine identifier
    
    Returns:
        Status dictionary
    """
    buffer = machine_buffers.get(machine_id, [])
    
    status = {
        "machine_id": machine_id,
        "buffer_length": len(buffer),
        "is_ready": len(buffer) >= SEQUENCE_LENGTH,
        "last_reading": buffer[-1] if buffer else None,
        "data_collected": f"{len(buffer)}/{SEQUENCE_LENGTH}"
    }
    
    # Add RUL prediction if ready
    if status["is_ready"]:
        rul = predict_rul(buffer)
        status["rul"] = rul
        status["health"] = "CRITICAL" if rul and rul < 20 else "HEALTHY"
        status["anomaly"] = "FAILURE SOON" if rul and rul < 20 else None
    else:
        status["rul"] = None
        status["health"] = "COLLECTING"
        status["anomaly"] = None
    
    return status

def reset_machine_buffer(machine_id: int) -> bool:
    """
    Reset buffer for a specific machine.
    
    Args:
        machine_id: Machine identifier
    
    Returns:
        Success status
    """
    if machine_id in machine_buffers:
        del machine_buffers[machine_id]
        logger.info(f"🔄 Reset buffer for machine {machine_id}")
        return True
    return False

def get_all_machines_status() -> List[Dict]:
    """
    Get status of all machines.
    
    Returns:
        List of status dictionaries for all machines
    """
    return [get_machine_status(machine_id) for machine_id in machine_buffers.keys()]

def create_feature_vector_from_raw(raw_data: Dict) -> List[float]:
    """
    Convert raw sensor data to feature vector matching training format.
    
    Args:
        raw_data: Dictionary containing sensor readings
    
    Returns:
        Feature vector of length FEATURES (24)
    """
    # Expected feature order: op_setting_1, op_setting_2, op_setting_3, sensor_1...sensor_21
    feature_vector = []
    
    # Operational settings (3)
    feature_vector.extend([
        raw_data.get("op_setting_1", 0.0),
        raw_data.get("op_setting_2", 0.0), 
        raw_data.get("op_setting_3", 0.0)
    ])
    
    # Sensor measurements (21)
    for i in range(1, 22):
        feature_vector.append(raw_data.get(f"sensor_{i}", 0.0))
    
    return feature_vector

def simulate_degradation(base_values: List[float], cycle: int, max_cycles: int = 200) -> List[float]:
    """
    Simulate realistic sensor degradation over time.
    
    Args:
        base_values: Initial sensor values
        cycle: Current cycle number
        max_cycles: Maximum cycles before failure
    
    Returns:
        Degraded feature vector
    """
    degradation_factor = cycle / max_cycles
    
    # Simulate gradual degradation with some noise
    degraded = []
    for i, value in enumerate(base_values):
        # Different sensors degrade differently
        if i < 3:  # Operational settings remain relatively stable
            noise = np.random.normal(0, 0.01)
            degraded_value = value + noise
        else:  # Sensors show degradation
            # Some sensors increase, some decrease as failure approaches
            if i % 2 == 0:
                degradation = value * (1 + 0.3 * degradation_factor)
            else:
                degradation = value * (1 - 0.2 * degradation_factor)
            
            noise = np.random.normal(0, 0.05 * degradation_factor)
            degraded_value = degradation + noise
        
        degraded.append(degraded_value)
    
    return degraded

# Initialize with some default base values for simulation
BASE_SENSOR_VALUES = [
    20.0, 0.6, 100.0,  # op_setting_1, op_setting_2, op_setting_3
    518.67, 641.82, 1589.99, 1400.76, 14.62, 21.61, 554.26, 2388.06, 9046.19, 1.3, 47.47, 521.66, 2388.02, 8138.62, 8.42, 0.03, 392.0, 2388.0, 100.0, 38.72, 23.294  # sensor_1...sensor_21
]

# 🟢 STEP 1: Backend Simulation API
def simulate_future(temperature: float, vibration: float, pressure: float) -> dict:
    """
    Simulate future machine behavior based on sensor parameters.
    
    This is the core "what-if" simulation function that predicts
    how changes in operating conditions affect machine health.
    
    Args:
        temperature: Operating temperature (°C)
        vibration: Vibration level (Hz)
        pressure: System pressure (kPa)
    
    Returns:
        Dictionary with risk_score, status, and detailed analysis
    """
    
    # Risk calculation based on engineering principles
    # Temperature: Higher temps accelerate wear
    # Vibration: Direct correlation to mechanical stress
    # Pressure: Affects system load and fatigue
    
    # Normalized ranges (based on C-MAPSS data)
    temp_normalized = (temperature - 20) / 100  # Normalize around 20°C baseline
    vibration_normalized = vibration / 10      # Normalize to 0-10 scale
    pressure_normalized = pressure / 5        # Normalize to 0-5 scale
    
    # Weighted risk factors (tuned for industrial equipment)
    temp_risk = temp_normalized * 0.4          # 40% weight for temperature
    vibration_risk = vibration_normalized * 0.35 # 35% weight for vibration
    pressure_risk = pressure_normalized * 0.25  # 25% weight for pressure
    
    # Calculate base risk score
    risk_score = (temp_risk + vibration_risk + pressure_risk) * 100
    
    # Add non-linear effects for extreme conditions
    if temperature > 100:
        risk_score += (temperature - 100) * 2  # Exponential risk at high temps
    
    if vibration > 8:
        risk_score += (vibration - 8) * 5      # Severe vibration risk
    
    if pressure > 4:
        risk_score += (pressure - 4) * 3       # High pressure risk
    
    # Determine status based on risk score
    if risk_score > 150:
        status = "CRITICAL FAILURE LIKELY"
        recommendation = "IMMEDIATE SHUTDOWN REQUIRED"
        estimated_rul = "< 10 cycles"
    elif risk_score > 100:
        status = "HIGH RISK"
        recommendation = "REDUCE OPERATING LOAD"
        estimated_rul = "10-25 cycles"
    elif risk_score > 60:
        status = "MODERATE RISK"
        recommendation = "MONITOR CLOSELY"
        estimated_rul = "25-50 cycles"
    elif risk_score > 30:
        status = "LOW RISK"
        recommendation = "NORMAL OPERATION"
        estimated_rul = "50-100 cycles"
    else:
        status = "SAFE"
        recommendation = "OPTIMAL CONDITIONS"
        estimated_rul = "> 100 cycles"
    
    # Calculate contributing factors
    factors = {
        "temperature_contribution": temp_risk * 100,
        "vibration_contribution": vibration_risk * 100,
        "pressure_contribution": pressure_risk * 100
    }
    
    # Identify primary risk factor
    primary_risk = max(factors, key=factors.get)
    
    return {
        "risk_score": round(risk_score, 2),
        "status": status,
        "recommendation": recommendation,
        "estimated_rul": estimated_rul,
        "factors": factors,
        "primary_risk_factor": primary_risk.replace("_contribution", "").title(),
        "input_parameters": {
            "temperature": temperature,
            "vibration": vibration,
            "pressure": pressure
        },
        "analysis": {
            "temperature_assessment": "HIGH" if temperature > 80 else "NORMAL" if temperature > 50 else "LOW",
            "vibration_assessment": "SEVERE" if vibration > 8 else "HIGH" if vibration > 5 else "NORMAL",
            "pressure_assessment": "EXTREME" if pressure > 4 else "HIGH" if pressure > 3 else "NORMAL"
        }
    }

def simulate_ml_rul(temperature: float, vibration: float, pressure: float) -> dict:
    """
    Use the actual LSTM model to predict RUL for simulated conditions.
    
    This creates a realistic sensor sequence and uses the trained model
    to predict RUL under different operating conditions.
    """
    if model is None or scaler is None:
        return {"error": "ML model not loaded"}
    
    try:
        # Create a realistic sensor sequence based on input conditions
        # Start with base values and modify according to input parameters
        
        base_sequence = []
        for i in range(SEQUENCE_LENGTH):
            # Gradually change conditions over the sequence
            temp_factor = 1 + (temperature - BASE_SENSOR_VALUES[4]) / BASE_SENSOR_VALUES[4] * 0.3
            vib_factor = 1 + (vibration - BASE_SENSOR_VALUES[3]) / BASE_SENSOR_VALUES[3] * 0.3
            pressure_factor = 1 + (pressure - BASE_SENSOR_VALUES[5]) / BASE_SENSOR_VALUES[5] * 0.3
            
            # Create sensor reading with degradation
            sensor_reading = BASE_SENSOR_VALUES.copy()
            
            # Modify key sensors based on input conditions
            sensor_reading[3] *= vib_factor      # sensor_1 (vibration)
            sensor_reading[4] *= temp_factor     # sensor_2 (temperature)
            sensor_reading[5] *= pressure_factor # sensor_3 (pressure)
            
            # Add some realistic noise and degradation
            for j in range(len(sensor_reading)):
                noise = np.random.normal(0, 0.02)
                degradation = 1 - (i / SEQUENCE_LENGTH) * 0.1  # 10% degradation over sequence
                sensor_reading[j] = sensor_reading[j] * degradation + noise
            
            base_sequence.append(sensor_reading)
        
        # Scale the sequence
        scaled_sequence = scaler.transform(base_sequence)
        
        # Reshape for LSTM
        lstm_input = scaled_sequence.reshape(1, SEQUENCE_LENGTH, FEATURES)
        
        # Predict RUL
        predicted_rul = model.predict(lstm_input, verbose=0)[0][0]
        
        # Cap RUL at 125 (consistent with training)
        predicted_rul = min(predicted_rul, 125)
        
        # Determine status based on RUL
        if predicted_rul < 20:
            ml_status = "CRITICAL"
        elif predicted_rul < 50:
            ml_status = "WARNING"
        else:
            ml_status = "HEALTHY"
        
        return {
            "predicted_rul": round(float(predicted_rul), 2),
            "ml_status": ml_status,
            "confidence": "HIGH" if predicted_rul > 10 else "MEDIUM",
            "method": "LSTM_MODEL"
        }
        
    except Exception as e:
        logger.error(f"❌ ML simulation error: {e}")
        return {"error": f"ML simulation failed: {str(e)}"}

logger.info("🚀 ML module initialized successfully")
logger.info(f"📊 Sequence length: {SEQUENCE_LENGTH}")
logger.info(f"📊 Features: {FEATURES}")
logger.info(f"📊 Model loaded: {model is not None}")
logger.info(f"📊 Scaler loaded: {scaler is not None}")
logger.info("🔮 Simulation functions loaded")
