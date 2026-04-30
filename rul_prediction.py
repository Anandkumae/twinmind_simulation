import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import xgboost as xgb
import joblib
import os

print("📊 RUL PREDICTION FOR C-MAPSS DATASET")
print("=" * 50)

# 📂 3. LOAD DATASET (FD001)
print("\n📂 Loading FD001 dataset...")

# Column names
cols = ["unit", "cycle"] + \
       [f"op_setting_{i}" for i in range(1,4)] + \
       [f"sensor_{i}" for i in range(1,22)]

# Load train file
train_path = "archive (9)/train_FD001.txt"
train = pd.read_csv(train_path, sep=" ", header=None)
train = train.dropna(axis=1)
train.columns = cols

print(f"Training data shape: {train.shape}")
print(f"Number of engines: {train['unit'].nunique()}")
print(f"Max cycles per engine: {train.groupby('unit')['cycle'].max().describe()}")

# 🧠 4. CREATE RUL TARGET
print("\n🧠 Creating RUL target variable...")

# Max cycle per engine
max_cycle = train.groupby("unit")["cycle"].max().reset_index()
max_cycle.columns = ["unit", "max_cycle"]

# Merge
train = train.merge(max_cycle, on="unit")

# RUL = max - current
train["RUL"] = train["max_cycle"] - train["cycle"]

# IMPORTANT: Cap RUL at 125 (common practice)
train["RUL"] = train["RUL"].clip(upper=125)

print(f"RUL statistics: {train['RUL'].describe()}")

# ⚡ 5. NORMALIZE DATA
print("\n⚡ Normalizing data...")

features = train.columns[2:26]  # op_setting + sensor columns

scaler = MinMaxScaler()
train[features] = scaler.fit_transform(train[features])

print(f"Features normalized: {list(features)}")

# 🔥 PART A: LSTM MODEL (BEST)
print("\n🔥 PART A: LSTM MODEL")
print("=" * 30)

# 🧱 6. CREATE SEQUENCES
sequence_length = 30

def create_sequences(data, seq_len):
    X, y = [], []
    
    for unit in data["unit"].unique():
        unit_data = data[data["unit"] == unit].sort_values("cycle")
        
        for i in range(len(unit_data) - seq_len):
            X.append(unit_data.iloc[i:i+seq_len][features].values)
            y.append(unit_data.iloc[i+seq_len]["RUL"])
    
    return np.array(X), np.array(y)

print(f"\n🧱 Creating sequences with length {sequence_length}...")
X, y = create_sequences(train, sequence_length)

print(f"Sequences created: X shape = {X.shape}, y shape = {y.shape}")

# 🧠 7. BUILD LSTM MODEL
print("\n🧠 Building LSTM model...")

model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(sequence_length, len(features))),
    Dropout(0.2),
    LSTM(32),
    Dropout(0.2),
    Dense(1)
])

model.compile(optimizer="adam", loss="mse")

print("Model architecture:")
model.summary()

# 🚀 8. TRAIN MODEL
print("\n🚀 Training LSTM model...")

# Callbacks for better training
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)

history = model.fit(
    X, y,
    epochs=50,
    batch_size=64,
    validation_split=0.2,
    callbacks=[early_stopping, lr_scheduler],
    verbose=1
)

# 💾 9. SAVE MODEL
print("\n💾 Saving LSTM model...")
model.save("lstm_rul_model.h5")
joblib.dump(scaler, "scaler.pkl")

# ⚡ PART B: XGBOOST (FASTER BASELINE)
print("\n⚡ PART B: XGBOOST BASELINE")
print("=" * 30)

# 🧱 10. FEATURE ENGINEERING
print("\n🧱 Engineering features for XGBoost...")

def create_flat_features(data):
    df = data.copy()
    
    # Rolling means for sensors
    for i in range(1, 22):
        df[f"sensor_{i}_mean"] = df.groupby("unit")[f"sensor_{i}"].transform(lambda x: x.rolling(5).mean())
    
    # Rolling std for sensors
    for i in range(1, 22):
        df[f"sensor_{i}_std"] = df.groupby("unit")[f"sensor_{i}"].transform(lambda x: x.rolling(5).std())
    
    df = df.dropna()
    return df

df_xgb = create_flat_features(train)

print(f"XGBoost feature set shape: {df_xgb.shape}")

X_xgb = df_xgb.drop(["unit", "cycle", "max_cycle", "RUL"], axis=1)
y_xgb = df_xgb["RUL"]

print(f"XGBoost features: {X_xgb.shape[1]}")

# 🚀 11. TRAIN XGBOOST
print("\n🚀 Training XGBoost model...")

X_train, X_test, y_train, y_test = train_test_split(X_xgb, y_xgb, test_size=0.2, random_state=42)

model_xgb = xgb.XGBRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    random_state=42
)

model_xgb.fit(X_train, y_train)

# 📊 12. EVALUATE
print("\n📊 Evaluating models...")

# XGBoost evaluation
preds_xgb = model_xgb.predict(X_test)
rmse_xgb = np.sqrt(mean_squared_error(y_test, preds_xgb))
print(f"XGBoost RMSE: {rmse_xgb:.4f}")

# LSTM evaluation (using validation split)
val_loss = min(history.history['val_loss'])
print(f"LSTM Validation Loss (MSE): {val_loss:.4f}")
print(f"LSTM Validation RMSE: {np.sqrt(val_loss):.4f}")

# 💾 SAVE XGBOOST
print("\n💾 Saving XGBoost model...")
joblib.dump(model_xgb, "xgb_model.pkl")

print("\n✅ Models saved successfully!")
print("Files created:")
print("- lstm_rul_model.h5")
print("- xgb_model.pkl") 
print("- scaler.pkl")

# 🚀 13. PREDICTION FUNCTIONS
print("\n🚀 Creating prediction functions...")

def predict_rul_lstm(sequence_data):
    """Predict RUL using LSTM model"""
    sequence = np.array(sequence_data).reshape(1, sequence_length, len(features))
    prediction = model.predict(sequence)[0][0]
    return float(prediction)

def predict_rul_xgb(feature_data):
    """Predict RUL using XGBoost model"""
    prediction = model_xgb.predict(feature_data)[0]
    return float(prediction)

print("Prediction functions ready!")
print("\n🎯 IMPLEMENTATION COMPLETE!")
