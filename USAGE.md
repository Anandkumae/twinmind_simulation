# 📖 TwinMind Digital Twin - Usage Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [Dashboard Overview](#dashboard-overview)
3. [Machine Monitoring](#machine-monitoring)
4. [What-If Simulation](#what-if-simulation)
5. [Report Generation](#report-generation)
6. [API Integration](#api-integration)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Step 1: Launch the System
```bash
# Start the complete Digital Twin system
python streaming_demo.py demo
```

### Step 2: Access the Dashboard
Open your web browser and navigate to:
```
http://localhost:8000/dashboard
```

### Step 3: Explore the Interface
You'll see:
- **Sidebar**: Navigation and controls
- **Main Dashboard**: Machine cards and real-time data
- **What-If Section**: Interactive simulation controls
- **System Stats**: Overall system health

## 🎮 Dashboard Overview

### **Layout Components**

#### **Sidebar Navigation**
```
🏭 TwinMind Digital Twin
├── 📊 System Overview
├── 🤖 Machine Monitoring
├── 🎯 What-If Simulation
├── 📋 Report Generation
└── ⚙️ Settings & Controls
```

#### **Main Dashboard Area**
- **Machine Cards**: Real-time status for each machine
- **System Statistics**: Overall health and performance metrics
- **Real-time Updates**: WebSocket-driven live data

#### **Control Panel**
- **Start Demo**: Launch multi-machine simulation
- **Add Machine**: Add new machines to monitoring
- **Reset All**: Clear all machine data
- **Generate Report**: Create comprehensive reports

## 📊 Machine Monitoring

### **Understanding Machine Cards**

Each machine card displays:

#### **Header Section**
```
🟢 Machine 1    [HEALTHY]
Status: 30/30 cycles collected
```

#### **Sensor Readings**
```
🌡️ Temperature: 78.5°C    📈 Trend: ↗️
🔧 Vibration: 4.2Hz      📈 Trend: →  
💨 Pressure: 2.8kPa      📈 Trend: ↘️
```

#### **Predictive Analytics**
```
🎯 RUL: 45.2 cycles     [████████░░] 85%
⚠️ Health: HEALTHY      Risk: LOW
📅 Next Maintenance: 30 days
```

#### **Visual Indicators**
- **🟢 Green**: Healthy operation
- **🟡 Yellow**: Warning state
- **🔴 Red**: Critical attention needed
- **⚪ Gray**: Collecting data

### **Real-Time Features**

#### **Live Data Updates**
- **WebSocket Connection**: Real-time data streaming
- **Auto-Refresh**: No manual refresh needed
- **Status Changes**: Instant health status updates
- **Sensor Trends**: Visual trend indicators

#### **Interactive Elements**
- **Click Machine Card**: Detailed machine view
- **Hover Effects**: Additional information tooltips
- **Filter Options**: Show/Hide specific machines

## 🎯 What-If Simulation

### **Simulation Interface**

#### **Parameter Controls**
```
🌡️ Temperature: [━━━━━━━━━━] 75.0°C
🔧 Vibration:  [━━━━━━━] 4.2Hz
💨 Pressure:    [━━━━━━] 2.8kPa
```

#### **Prediction Options**
```
🤖 Use ML Model: ☑️ LSTM Neural Network
📊 Use Rule-Based: ☐ Fast Analytics
📈 Show Comparison: ☑️ Side-by-side
```

### **Running Simulations**

#### **Step 1: Adjust Parameters**
- **Temperature Slider**: 50°C - 100°C range
- **Vibration Slider**: 1.0Hz - 10.0Hz range  
- **Pressure Slider**: 0.5kPa - 5.0kPa range

#### **Step 2: Choose Prediction Method**
- **LSTM Model**: Deep learning predictions (more accurate)
- **Rule-Based**: Fast rule-based predictions (more interpretable)

#### **Step 3: Execute Simulation**
```bash
# Click "Run Simulation" button
# Results appear instantly in the results panel
```

### **Understanding Results**

#### **Prediction Output**
```
🔮 LSTM Prediction:
   RUL: 32.5 cycles
   Health: WARNING
   Risk: MEDIUM
   Confidence: 87%

📊 Rule-Based Prediction:
   RUL: 28.1 cycles  
   Health: WARNING
   Risk: MEDIUM
   Confidence: 82%
```

#### **Risk Assessment**
```
⚠️ Risk Analysis:
• Temperature increase: +15% risk
• Vibration elevation: +8% risk
• Pressure change: +3% risk
🎯 Overall Risk: MEDIUM-HIGH
```

#### **Recommendations**
```
💡 Recommendations:
• Schedule inspection within 7 days
• Monitor temperature closely
• Consider operational adjustments
💰 Estimated maintenance cost: $2,500
```

## 📋 Report Generation

### **Report Generation Modal**

#### **Report Type Selection**
```
📊 Executive Summary    - High-level overview
🔍 Detailed Analysis    - In-depth machine analysis  
🏥 Health Assessment    - Health status focus
📈 Performance Metrics  - KPI and benchmarking
```

#### **Format Options**
```
🌐 HTML Report         - View in browser (recommended)
📄 JSON Data Export    - Machine-readable format
📑 PDF Printable       - Professional documents
```

#### **Machine Selection**
```
🎯 All Machines        - Include all active machines
⚠️ Critical Only       - Only critical/warning machines
🔧 Custom Selection    - Choose specific machines
```

#### **Date Range**
```
📅 Today              - Current day only
📅 Last 7 Days         - Past week
📅 Last 30 Days        - Past month  
📅 All Time            - Complete history
```

#### **Additional Options**
```
📊 Include Charts      ☑️ Visual graphs and charts
💡 Include Recommendations ☑️ Actionable insights
📈 Include Trends     ☐ Historical trend analysis
```

### **Report Content**

#### **Executive Summary Report**
```
📊 Report Overview:
• Generated: 2024-01-15 14:30:22
• Total Machines: 5
• Report Type: Executive Summary
• Date Range: Last 7 days

🎯 Key Metrics:
• Overall Health Score: 87.5/100
• Average RUL: 42.3 cycles
• Critical Machines: 1
• Warning Machines: 2

📈 Health Distribution:
• Healthy: 2 machines (40%)
• Warning: 2 machines (40%)
• Critical: 1 machine (20%)

💡 Key Insights:
• Machine 3 requires immediate attention
• Overall system health is stable
• 2 machines showing early warning signs
```

#### **Detailed Analysis Report**
```
🔍 Machine-by-Machine Analysis:

Machine 1:
• Health: HEALTHY (92/100)
• RUL: 58.2 cycles
• Risk Level: LOW
• Performance: 94% efficiency
• Next Maintenance: 45 days

Machine 2:
• Health: WARNING (68/100)  
• RUL: 23.1 cycles
• Risk Level: MEDIUM
• Performance: 78% efficiency
• Next Maintenance: 7 days

[... additional machines ...]

📊 Performance Trends:
• Temperature trend: ↗️ +2.3% over 7 days
• Vibration trend: → stable
• Pressure trend: ↘️ -1.1% over 7 days
```

#### **Health Assessment Report**
```
🏥 System Health Overview:

Individual Health Scores:
• Machine 1: 92/100 (EXCELLENT)
• Machine 2: 68/100 (FAIR)
• Machine 3: 45/100 (POOR)
• Machine 4: 78/100 (GOOD)
• Machine 5: 85/100 (VERY GOOD)

Risk Assessments:
• CRITICAL: Machine 3 (failure probability: 35%)
• HIGH: Machine 2 (failure probability: 15%)
• MEDIUM: Machines 4, 5 (failure probability: 5-10%)
• LOW: Machine 1 (failure probability: <5%)

Recommended Actions:
• IMMEDIATE: Machine 3 - Schedule urgent maintenance
• URGENT: Machine 2 - Inspect within 48 hours
• ROUTINE: Machines 4, 5 - Next scheduled maintenance
• MONITOR: Machine 1 - Continue normal monitoring
```

### **Export and Sharing**

#### **HTML Reports**
- **View Online**: Opens in new browser tab
- **Print**: Use browser print function
- **Save As**: Download as HTML file
- **Share**: Direct link to report

#### **JSON Reports**
- **API Integration**: Machine-readable format
- **Data Analysis**: Import into analytics tools
- **Backup**: Complete data preservation
- **Custom Processing**: Programmatic report generation

#### **PDF Reports**
- **Professional Formatting**: Print-ready documents
- **Email Sharing**: Attach to communications
- **Archive**: Long-term document storage
- **Presentation**: Meeting handouts

## 🔌 API Integration

### **Authentication**
```python
import requests

# API endpoint
base_url = "http://localhost:8000"

# Health check (no auth required)
response = requests.get(f"{base_url}/health")
print(f"System Status: {response.json()['status']}")
```

### **Machine Data Submission**

#### **Simple Sensor Data**
```python
sensor_data = {
    "machine_id": 1,
    "temperature": 75.5,
    "vibration": 4.2,
    "pressure": 2.8
}

response = requests.post(f"{base_url}/sensor-data", json=sensor_data)
result = response.json()

print(f"RUL: {result['rul']}")
print(f"Health: {result['health']}")
print(f"Risk: {result['anomaly']}")
```

#### **Full Sensor Data**
```python
full_data = {
    "machine_id": 1,
    "op_setting_1": 20.0,
    "op_setting_2": 0.6,
    "op_setting_3": 100.0,
    "sensor_1": 518.67,
    "sensor_2": 641.82,
    "sensor_3": 1589.99,
    # ... all 21 sensors
}

response = requests.post(f"{base_url}/sensor-data-full", json=full_data)
result = response.json()
```

### **Simulation API**

#### **What-If Simulation**
```python
simulation_params = {
    "temperature": 85.0,
    "vibration": 6.5,
    "pressure": 3.2,
    "use_ml_model": True
}

response = requests.post(f"{base_url}/simulate", json=simulation_params)
result = response.json()

print(f"Predicted RUL: {result['rul']}")
print(f"Health Status: {result['health']}")
print(f"Risk Level: {result['risk_level']}")
```

#### **Machine Simulation**
```python
# Run 50 cycles of simulation for machine 1
response = requests.post(f"{base_url}/simulate/1?cycles=50")
result = response.json()

print(f"Final RUL: {result['final_rul']}")
print(f"Simulated Cycles: {result['cycles_simulated']}")
```

### **Report Generation API**

#### **Generate Summary Report**
```python
report_request = {
    "report_type": "summary",
    "format": "html",
    "include_charts": True,
    "include_recommendations": True
}

response = requests.post(f"{base_url}/generate-report", json=report_request)

if response.headers.get('content-type') == 'text/html':
    # Save HTML report
    with open('report.html', 'w') as f:
        f.write(response.text)
else:
    # Handle JSON response
    data = response.json()
    print(f"Report generated: {data['report_metadata']['generated_at']}")
```

#### **Generate Detailed Report**
```python
detailed_report = {
    "report_type": "detailed",
    "format": "json",
    "machine_ids": [1, 2, 3],  # Specific machines only
    "date_range": {
        "start": "2024-01-01T00:00:00",
        "end": "2024-01-15T23:59:59"
    },
    "include_charts": True,
    "include_recommendations": True
}

response = requests.post(f"{base_url}/generate-report", json=detailed_report)
data = response.json()

print(f"Machines analyzed: {len(data['machine_analysis'])}")
print(f"Recommendations: {len(data['recommendations'])}")
```

### **WebSocket Integration**

#### **Real-Time Data Streaming**
```python
import websockets
import asyncio
import json

async def monitor_machines():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data['type'] == 'sensor_update':
                machine_id = data['machine_id']
                rul = data['rul']
                health = data['health']
                sensors = data['sensor_data']
                
                print(f"Machine {machine_id}: RUL={rul}, Health={health}")
                print(f"  Temp: {sensors['temperature']}°C")
                print(f"  Vib: {sensors['vibration']}Hz")
                print(f"  Pres: {sensors['pressure']}kPa")

# Run the monitor
asyncio.run(monitor_machines())
```

## 🌟 Advanced Features

### **Multi-Machine Management**

#### **Adding Multiple Machines**
```python
# Add 10 machines with different configurations
for i in range(1, 11):
    machine_data = {
        "machine_id": i,
        "failure_type": ["gradual", "sudden", "intermittent"][i % 3],
        "max_cycles": 50 + (i * 10)
    }
    requests.post(f"{base_url}/machines", json=machine_data)
```

#### **Bulk Data Processing**
```python
# Process sensor data for multiple machines
bulk_data = [
    {"machine_id": i, "temperature": 70 + i, "vibration": 3 + i*0.5, "pressure": 2 + i*0.3}
    for i in range(1, 6)
]

for data in bulk_data:
    response = requests.post(f"{base_url}/sensor-data", json=data)
    print(f"Machine {data['machine_id']}: {response.json()['health']}")
```

### **Custom Analytics**

#### **Health Score Calculation**
```python
def calculate_health_score(machine_data):
    rul = machine_data.get('rul', 0)
    health = machine_data.get('health', 'UNKNOWN')
    
    base_score = 50  # Default for collecting
    
    if health == 'HEALTHY':
        base_score = 90 + min(10, rul / 10)
    elif health == 'WARNING':
        base_score = 50 + min(20, rul / 5)
    elif health == 'CRITICAL':
        base_score = 20 + min(20, rul / 2)
    
    return round(base_score, 1)

# Usage
response = requests.get(f"{base_url}/machines")
machines = response.json()['machines']

for machine in machines:
    score = calculate_health_score(machine)
    print(f"Machine {machine['machine_id']}: Health Score = {score}/100")
```

#### **Predictive Maintenance Scheduling**
```python
def schedule_maintenance(machine_data):
    rul = machine_data.get('rul', 0)
    health = machine_data.get('health', 'UNKNOWN')
    
    if health == 'CRITICAL':
        return {"priority": "URGENT", "days": 1, "cost": 5000}
    elif health == 'WARNING' and rul < 20:
        return {"priority": "HIGH", "days": 7, "cost": 2500}
    elif rul < 30:
        return {"priority": "MEDIUM", "days": 14, "cost": 1000}
    else:
        return {"priority": "LOW", "days": 30, "cost": 500}

# Generate maintenance schedule
response = requests.get(f"{base_url}/machines")
machines = response.json()['machines']

schedule = []
for machine in machines:
    maintenance = schedule_maintenance(machine)
    schedule.append({
        "machine_id": machine['machine_id'],
        **maintenance
    })

# Sort by priority
schedule.sort(key=lambda x: {"URGENT": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[x['priority']])

for item in schedule:
    print(f"Machine {item['machine_id']}: {item['priority']} - {item['days']} days")
```

### **Performance Monitoring**

#### **System Performance Metrics**
```python
import time

def measure_api_performance():
    start_time = time.time()
    
    # Test sensor data endpoint
    response = requests.post(f"{base_url}/sensor-data", 
                            json={"machine_id": 1, "temperature": 75.0})
    
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    
    print(f"API Response Time: {response_time:.2f}ms")
    print(f"Status Code: {response.status_code}")
    
    return response_time

# Monitor performance over time
performance_data = []
for i in range(10):
    response_time = measure_api_performance()
    performance_data.append(response_time)
    time.sleep(1)

avg_response = sum(performance_data) / len(performance_data)
print(f"Average Response Time: {avg_response:.2f}ms")
```

## 🔧 Troubleshooting

### **Common Issues**

#### **Dashboard Not Loading**
```bash
# Check if API server is running
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "models_loaded": {...}}
```

#### **WebSocket Connection Issues**
```javascript
// Check browser console for WebSocket errors
// Common errors:
// - "Failed to connect to WebSocket"
// - "Connection refused"

// Solutions:
// 1. Ensure API server is running
// 2. Check firewall settings
// 3. Verify port 8000 is available
```

#### **Report Generation Failures**
```python
# Check report API status
response = requests.get("http://localhost:8000/health")
health = response.json()

if not health.get('report_generation_available'):
    print("Report generation not available")
else:
    print("Report generation ready")
```

#### **Machine Data Not Updating**
```bash
# Check WebSocket connections
curl http://localhost:8000/health

# Look for:
# "websocket_connections": 1
# "active_machines": > 0
```

### **Debug Mode**

#### **Enable Debug Logging**
```python
# In streaming_api.py, modify log level
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### **Check System Logs**
```bash
# View real-time logs
python streaming_demo.py demo 2>&1 | tee system.log

# Filter for specific errors
grep "ERROR" system.log
grep "WebSocket" system.log
```

### **Performance Issues**

#### **High Memory Usage**
```python
# Monitor machine buffers
response = requests.get("http://localhost:8000/machines")
machines = response.json()['machines']

for machine in machines:
    buffer_length = machine.get('buffer_length', 0)
    if buffer_length > 100:
        print(f"Machine {machine['machine_id']}: Large buffer ({buffer_length})")
```

#### **Slow Response Times**
```python
import time

def benchmark_endpoint(endpoint, data=None):
    start = time.time()
    
    if data:
        response = requests.post(endpoint, json=data)
    else:
        response = requests.get(endpoint)
    
    end = time.time()
    return (end - start) * 1000

# Benchmark key endpoints
endpoints = [
    ("http://localhost:8000/health", None),
    ("http://localhost:8000/machines", None),
    ("http://localhost:8000/sensor-data", {"machine_id": 1, "temperature": 75.0})
]

for url, data in endpoints:
    time_ms = benchmark_endpoint(url, data)
    print(f"{url}: {time_ms:.2f}ms")
```

### **Data Validation**

#### **Check Data Quality**
```python
def validate_sensor_data(data):
    required_fields = ['machine_id', 'temperature', 'vibration', 'pressure']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"
    
    # Validate ranges
    if not (0 <= data['temperature'] <= 200):
        return False, "Temperature out of range (0-200°C)"
    
    if not (0 <= data['vibration'] <= 20):
        return False, "Vibration out of range (0-20Hz)"
    
    if not (0 <= data['pressure'] <= 10):
        return False, "Pressure out of range (0-10kPa)"
    
    return True, "Data valid"

# Test validation
test_data = {"machine_id": 1, "temperature": 75.5, "vibration": 4.2, "pressure": 2.8}
valid, message = validate_sensor_data(test_data)
print(f"Validation: {valid} - {message}")
```

---

## 📞 Additional Support

For additional help:
- 📖 Check the main [README.md](README.md)
- 🔍 Review [API documentation](#api-integration)
- 🐛 Report issues on GitHub
- 💬 Join our Discord community

**Happy monitoring with TwinMind Digital Twin!** 🏭✨
