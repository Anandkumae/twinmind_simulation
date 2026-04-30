import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import tensorflow as tf
from tensorflow.keras.models import load_model
import joblib
import os

print("📊 EVALUATING ON TEST DATASET")
print("=" * 50)

# Load saved models and scaler
print("\n🔄 Loading saved models...")
model = load_model("lstm_rul_model.h5", compile=False)
model.compile(optimizer="adam", loss="mse")
model_xgb = joblib.load("xgb_model.pkl")
scaler = joblib.load("scaler.pkl")

# Load test data
print("\n📂 Loading test dataset...")

# Column names
cols = ["unit", "cycle"] + \
       [f"op_setting_{i}" for i in range(1,4)] + \
       [f"sensor_{i}" for i in range(1,22)]

# Load test file
test_path = "archive (9)/test_FD001.txt"
test = pd.read_csv(test_path, sep=" ", header=None)
test = test.dropna(axis=1)
test.columns = cols

# Load true RUL values
rul_path = "archive (9)/RUL_FD001.txt"
true_rul = pd.read_csv(rul_path, sep=" ", header=None)
true_rul = true_rul.dropna(axis=1)
true_rul.columns = ["RUL"]

print(f"Test data shape: {test.shape}")
print(f"Number of test engines: {test['unit'].nunique()}")
print(f"True RUL values: {len(true_rul)}")

# Normalize test data using the same scaler
features = test.columns[2:26]
test[features] = scaler.transform(test[features])

# Get last cycle for each test engine
last_cycles = test.groupby("unit")["cycle"].max().reset_index()
print(f"\n🔍 Last cycles per engine:")
print(last_cycles.head())

# Create test sequences for LSTM
sequence_length = 30

def create_test_sequences(test_data, seq_len):
    X_test = []
    test_units = []
    
    for unit in test_data["unit"].unique():
        unit_data = test_data[test_data["unit"] == unit].sort_values("cycle")
        
        # Get the last sequence for each unit
        if len(unit_data) >= seq_len:
            last_sequence = unit_data.tail(seq_len)[features].values
            X_test.append(last_sequence)
            test_units.append(unit)
    
    return np.array(X_test), test_units

print(f"\n🧱 Creating test sequences...")
X_test, test_units = create_test_sequences(test, sequence_length)
print(f"Test sequences created: {X_test.shape}")

# LSTM predictions
print("\n🔥 LSTM Predictions...")
lstm_predictions = model.predict(X_test)
lstm_predictions = lstm_predictions.flatten()

# XGBoost predictions
print("\n⚡ XGBoost Predictions...")

# Create features for XGBoost (same as training)
def create_test_flat_features(data):
    df = data.copy()
    
    # Rolling means for sensors
    for i in range(1, 22):
        df[f"sensor_{i}_mean"] = df.groupby("unit")[f"sensor_{i}"].transform(lambda x: x.rolling(5).mean())
    
    # Rolling std for sensors
    for i in range(1, 22):
        df[f"sensor_{i}_std"] = df.groupby("unit")[f"sensor_{i}"].transform(lambda x: x.rolling(5).std())
    
    df = df.dropna()
    return df

test_xgb_features = create_test_flat_features(test)

# Get last cycle features for each engine
last_cycle_features = []
for unit in test_units:
    unit_data = test_xgb_features[test_xgb_features["unit"] == unit]
    last_cycle = unit_data.iloc[-1]
    last_cycle_features.append(last_cycle.drop(["unit", "cycle"]).values)

X_test_xgb = np.array(last_cycle_features)
xgb_predictions = model_xgb.predict(X_test_xgb)

# 📊 EVALUATION
print("\n📊 MODEL EVALUATION ON TEST DATA")
print("=" * 40)

# Ensure we have the right number of predictions
print(f"Number of LSTM predictions: {len(lstm_predictions)}")
print(f"Number of XGBoost predictions: {len(xgb_predictions)}")
print(f"Number of true RUL values: {len(true_rul)}")

# Calculate RMSE for both models
lstm_rmse = np.sqrt(mean_squared_error(true_rul["RUL"], lstm_predictions))
xgb_rmse = np.sqrt(mean_squared_error(true_rul["RUL"], xgb_predictions))

print(f"\n🎯 RESULTS:")
print(f"LSTM RMSE: {lstm_rmse:.4f}")
print(f"XGBoost RMSE: {xgb_rmse:.4f}")

# Detailed comparison
results_df = pd.DataFrame({
    'Unit': test_units,
    'True_RUL': true_rul["RUL"].values,
    'LSTM_Prediction': lstm_predictions,
    'XGBoost_Prediction': xgb_predictions,
    'LSTM_Error': np.abs(lstm_predictions - true_rul["RUL"].values),
    'XGBoost_Error': np.abs(xgb_predictions - true_rul["RUL"].values)
})

print(f"\n📋 Detailed Results (first 10 engines):")
print(results_df.head(10).round(2))

print(f"\n📈 Summary Statistics:")
print(f"LSTM - Mean Error: {results_df['LSTM_Error'].mean():.2f}")
print(f"LSTM - Std Error: {results_df['LSTM_Error'].std():.2f}")
print(f"XGBoost - Mean Error: {results_df['XGBoost_Error'].mean():.2f}")
print(f"XGBoost - Std Error: {results_df['XGBoost_Error'].std():.2f}")

# Save results
results_df.to_csv("test_results.csv", index=False)
print(f"\n💾 Results saved to test_results.csv")

print(f"\n🏆 WINNER: {'LSTM' if lstm_rmse < xgb_rmse else 'XGBoost'}")
print(f"🎯 IMPLEMENTATION COMPLETE!")
