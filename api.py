from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import joblib
from typing import List, Optional
import uvicorn

app = FastAPI(title="RUL Prediction API", description="API for predicting Remaining Useful Life using LSTM and XGBoost models")

# Load models and scaler at startup
print("🔄 Loading models...")
try:
    lstm_model = load_model("lstm_rul_model.h5", compile=False)
    lstm_model.compile(optimizer="adam", loss="mse")
    xgb_model = joblib.load("xgb_model.pkl")
    scaler = joblib.load("scaler.pkl")
    print("✅ Models loaded successfully!")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    lstm_model = None
    xgb_model = None
    scaler = None

# Feature names
features = [f"op_setting_{i}" for i in range(1,4)] + [f"sensor_{i}" for i in range(1,22)]
sequence_length = 30

class SensorData(BaseModel):
    unit: int
    cycle: int
    op_setting_1: float
    op_setting_2: float
    op_setting_3: float
    sensor_1: float
    sensor_2: float
    sensor_3: float
    sensor_4: float
    sensor_5: float
    sensor_6: float
    sensor_7: float
    sensor_8: float
    sensor_9: float
    sensor_10: float
    sensor_11: float
    sensor_12: float
    sensor_13: float
    sensor_14: float
    sensor_15: float
    sensor_16: float
    sensor_17: float
    sensor_18: float
    sensor_19: float
    sensor_20: float
    sensor_21: float

class SequenceData(BaseModel):
    sequence: List[SensorData]

class PredictionResponse(BaseModel):
    lstm_prediction: float
    xgb_prediction: float
    unit: int
    cycle: int

@app.get("/")
async def root():
    return {"message": "RUL Prediction API", "status": "active"}

@app.get("/health")
async def health_check():
    if lstm_model is None or xgb_model is None or scaler is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    return {"status": "healthy", "models_loaded": True}

@app.post("/predict/lstm", response_model=dict)
async def predict_lstm(sequence: SequenceData):
    """Predict RUL using LSTM model"""
    if lstm_model is None:
        raise HTTPException(status_code=503, detail="LSTM model not loaded")
    
    try:
        # Convert sequence to DataFrame
        sequence_data = []
        for data in sequence.sequence:
            row = {
                'unit': data.unit,
                'cycle': data.cycle,
                'op_setting_1': data.op_setting_1,
                'op_setting_2': data.op_setting_2,
                'op_setting_3': data.op_setting_3,
            }
            for i in range(1, 22):
                row[f'sensor_{i}'] = getattr(data, f'sensor_{i}')
            sequence_data.append(row)
        
        df = pd.DataFrame(sequence_data)
        
        # Check sequence length
        if len(df) != sequence_length:
            raise HTTPException(status_code=400, detail=f"Sequence length must be {sequence_length}")
        
        # Normalize features
        df[features] = scaler.transform(df[features])
        
        # Create sequence array
        sequence_array = df[features].values.reshape(1, sequence_length, len(features))
        
        # Make prediction
        prediction = lstm_model.predict(sequence_array)[0][0]
        
        return {
            "lstm_prediction": float(prediction),
            "unit": sequence.sequence[-1].unit,
            "cycle": sequence.sequence[-1].cycle,
            "sequence_length": sequence_length
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/xgb", response_model=dict)
async def predict_xgb(data: SensorData):
    """Predict RUL using XGBoost model"""
    if xgb_model is None:
        raise HTTPException(status_code=503, detail="XGBoost model not loaded")
    
    try:
        # Create feature vector
        feature_dict = {
            'op_setting_1': data.op_setting_1,
            'op_setting_2': data.op_setting_2,
            'op_setting_3': data.op_setting_3,
        }
        for i in range(1, 22):
            feature_dict[f'sensor_{i}'] = getattr(data, f'sensor_{i}')
        
        # Create rolling features (simplified - in production, you'd need historical data)
        for i in range(1, 22):
            feature_dict[f'sensor_{i}_mean'] = getattr(data, f'sensor_{i}')
            feature_dict[f'sensor_{i}_std'] = 0.0  # Placeholder
        
        # Convert to DataFrame
        df = pd.DataFrame([feature_dict])
        
        # Ensure all required columns are present
        required_cols = [col for col in xgb_model.get_booster().feature_names if col in df.columns]
        df = df[required_cols]
        
        # Make prediction
        prediction = xgb_model.predict(df)[0]
        
        return {
            "xgb_prediction": float(prediction),
            "unit": data.unit,
            "cycle": data.cycle
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/both", response_model=PredictionResponse)
async def predict_both(sequence: SequenceData):
    """Predict RUL using both LSTM and XGBoost models"""
    if lstm_model is None or xgb_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # LSTM prediction
        sequence_data = []
        for data in sequence.sequence:
            row = {
                'unit': data.unit,
                'cycle': data.cycle,
                'op_setting_1': data.op_setting_1,
                'op_setting_2': data.op_setting_2,
                'op_setting_3': data.op_setting_3,
            }
            for i in range(1, 22):
                row[f'sensor_{i}'] = getattr(data, f'sensor_{i}')
            sequence_data.append(row)
        
        df = pd.DataFrame(sequence_data)
        
        if len(df) != sequence_length:
            raise HTTPException(status_code=400, detail=f"Sequence length must be {sequence_length}")
        
        df[features] = scaler.transform(df[features])
        sequence_array = df[features].values.reshape(1, sequence_length, len(features))
        lstm_pred = lstm_model.predict(sequence_array)[0][0]
        
        # XGBoost prediction (using last data point)
        last_data = sequence.sequence[-1]
        feature_dict = {
            'op_setting_1': last_data.op_setting_1,
            'op_setting_2': last_data.op_setting_2,
            'op_setting_3': last_data.op_setting_3,
        }
        for i in range(1, 22):
            feature_dict[f'sensor_{i}'] = getattr(last_data, f'sensor_{i}')
            feature_dict[f'sensor_{i}_mean'] = getattr(last_data, f'sensor_{i}')
            feature_dict[f'sensor_{i}_std'] = 0.0
        
        df_xgb = pd.DataFrame([feature_dict])
        required_cols = [col for col in xgb_model.get_booster().feature_names if col in df_xgb.columns]
        df_xgb = df_xgb[required_cols]
        xgb_pred = xgb_model.predict(df_xgb)[0]
        
        return PredictionResponse(
            lstm_prediction=float(lstm_pred),
            xgb_prediction=float(xgb_pred),
            unit=sequence.sequence[-1].unit,
            cycle=sequence.sequence[-1].cycle
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/models/info")
async def models_info():
    """Get information about loaded models"""
    if lstm_model is None or xgb_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    return {
        "lstm_model": {
            "input_shape": lstm_model.input_shape,
            "output_shape": lstm_model.output_shape,
            "sequence_length": sequence_length,
            "features": len(features)
        },
        "xgb_model": {
            "n_features": len(xgb_model.get_booster().feature_names),
            "feature_names": xgb_model.get_booster().feature_names[:10]  # First 10 features
        },
        "scaler": {
            "n_features": scaler.n_features_in_,
            "feature_names": features[:10]  # First 10 features
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
