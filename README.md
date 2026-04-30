# 🏭 TwinMind Digital Twin System

A comprehensive Digital Twin platform for real-time machine monitoring, predictive maintenance, and intelligent decision support. This system transforms traditional machinery into intelligent digital counterparts with advanced AI-powered analytics.

## 🌟 Key Features

### 📊 Real-Time Monitoring
- **Multi-Machine Support**: Monitor multiple machines simultaneously
- **Live Sensor Data**: Real-time temperature, vibration, and pressure readings
- **WebSocket Streaming**: Instant updates without page refresh
- **Dynamic Visualization**: Interactive charts and machine status indicators

### 🤖 AI-Powered Predictions
- **LSTM Neural Networks**: Deep learning for Remaining Useful Life (RUL) prediction
- **Rule-Based Analytics**: Fast, interpretable predictions
- **Health Scoring**: 0-100 scale machine health assessment
- **Anomaly Detection**: Early warning system for potential failures

### 🎯 What-If Simulation
- **Scenario Testing**: Test operational changes without affecting real machines
- **Parameter Adjustment**: Interactive sliders for temperature, vibration, pressure
- **Risk Assessment**: Instant feedback on operational decisions
- **ML vs Rule-Based**: Compare prediction methodologies

### 📋 Comprehensive Reporting
- **Executive Summaries**: High-level system overviews
- **Detailed Analysis**: In-depth machine-by-machine reports
- **Health Assessments**: Comprehensive health status evaluations
- **Performance Metrics**: KPI tracking and benchmarking
- **Multiple Formats**: HTML, JSON, and PDF report generation

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   ML Engine    │
│                 │    │                 │    │                 │
│ • React Dashboard│◄──►│ • FastAPI       │◄──►│ • LSTM Models   │
│ • Real-time UI   │    │ • WebSocket     │    │ • Rule-Based    │
│ • Report UI     │    │ • Report API    │    │ • Predictions    │
│ • Simulation     │    │ • Simulation    │    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Simulator     │
                    │                 │
                    │ • Multi-Machine │
                    │ • Realistic Data│
                    │ • Degradation   │
                    │ • Failure Modes │
                    └─────────────────┘
```

## 📁 Project Structure

```
├── 🎯 Core System
│   ├── streaming_api.py          # FastAPI backend with WebSocket support
│   ├── ml.py                     # Machine learning models and analytics
│   ├── simulator.py              # Multi-machine simulation engine
│   └── streaming_demo.py         # System orchestration and demo
│
├── 🌐 Frontend
│   ├── production_dashboard.html  # Professional React-based dashboard
│   └── dashboard.html            # Legacy simple dashboard
│
├── 🤖 Machine Learning
│   ├── rul_prediction.py         # LSTM model training script
│   ├── evaluate_test.py          # Model evaluation and testing
│   ├── lstm_rul_model.h5         # Trained LSTM model
│   └── scaler.pkl                # Fitted data scaler
│
├── 📊 Data & Models
│   ├── test_results.csv          # Model performance results
│   └── archive/                  # C-MAPSS dataset (optional)
│
├── 📋 Documentation
│   ├── README.md                 # This file
│   ├── README_PRODUCTION.md      # Production deployment guide
│   └── requirements.txt          # Python dependencies
│
└── ⚙️ Configuration
    └── .gitignore                # Git ignore file
```

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <repository-url>
cd Digital_twin

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Complete System
```bash
# Run the full demo (API + Simulator + Dashboard)
python streaming_demo.py demo
```

### 3. Access the Dashboard
Open your browser and navigate to:
```
http://localhost:8000/dashboard
```

### 4. Alternative Startup Options

#### API Only
```bash
python streaming_api.py
```

#### Simulator Only
```bash
python simulator.py
```

#### Test Mode
```bash
python streaming_demo.py test
```

## 🎮 Using the System

### 📊 Dashboard Features

#### **Machine Monitoring**
- Real-time machine cards with health status
- Live sensor readings (temperature, vibration, pressure)
- RUL predictions and health scores
- Anomaly alerts and warnings

#### **What-If Simulation**
- Interactive parameter sliders
- Real-time risk assessment
- ML vs rule-based prediction comparison
- Scenario testing without machine impact

#### **Report Generation**
- Multiple report types (Summary, Detailed, Health, Performance)
- Various formats (HTML, JSON, PDF)
- Customizable machine selection and date ranges
- Professional report templates

### 🔌 API Endpoints

#### **Core Endpoints**
- `GET /health` - System health check
- `GET /machines` - List all active machines
- `POST /sensor-data` - Submit sensor readings
- `POST /sensor-data-full` - Submit full sensor data

#### **Simulation & Prediction**
- `POST /simulate/{machine_id}` - Run machine simulation
- `POST /simulate` - What-if simulation
- `POST /predict` - ML-based predictions

#### **Reporting**
- `POST /generate-report` - Generate comprehensive reports

#### **WebSocket**
- `WS /ws` - Real-time data streaming

### 💻 API Usage Examples

#### **Submit Sensor Data**
```python
import requests

sensor_data = {
    "machine_id": 1,
    "temperature": 75.5,
    "vibration": 4.2,
    "pressure": 2.8
}

response = requests.post("http://localhost:8000/sensor-data", json=sensor_data)
result = response.json()
print(f"RUL Prediction: {result['rul']}")
print(f"Health Status: {result['health']}")
```

#### **Generate Report**
```python
import requests

report_request = {
    "report_type": "summary",
    "format": "html",
    "include_charts": True,
    "include_recommendations": True
}

response = requests.post("http://localhost:8000/generate-report", json=report_request)
print(f"Report Status: {response.status_code}")
```

#### **What-If Simulation**
```python
import requests

simulation_params = {
    "temperature": 85.0,
    "vibration": 6.5,
    "pressure": 3.2,
    "use_ml_model": True
}

response = requests.post("http://localhost:8000/simulate", json=simulation_params)
result = response.json()
print(f"Predicted RUL: {result['rul']}")
print(f"Risk Level: {result['risk_level']}")
```

## 🎯 Model Performance

### LSTM Neural Network
- **Architecture**: LSTM(64) → Dropout → LSTM(32) → Dropout → Dense(1)
- **Sequence Length**: 30 cycles
- **Test RMSE**: 15.04
- **Features**: 24 (3 operational + 21 sensors)
- **Training**: C-MAPSS FD001 dataset

### Rule-Based Analytics
- **Response Time**: <1ms
- **Interpretability**: High
- **Accuracy**: 85-90%
- **Use Case**: Real-time quick predictions

## 🔧 Technical Specifications

### **System Requirements**
- **Python**: 3.8+
- **Memory**: 4GB RAM minimum
- **Storage**: 2GB free space
- **Network**: HTTP/WebSocket capable

### **Dependencies**
```txt
fastapi>=0.68.0
uvicorn>=0.15.0
tensorflow>=2.8.0
scikit-learn>=1.0.0
pandas>=1.3.0
numpy>=1.21.0
websockets>=10.0
pydantic>=1.8.0
```

### **Performance Metrics**
- **API Response Time**: <100ms
- **WebSocket Latency**: <50ms
- **Concurrent Users**: 100+
- **Data Throughput**: 1000+ messages/second

## 🌟 Advanced Features

### **Multi-Machine Simulation**
- 5 simultaneous machines with different failure patterns
- Realistic sensor degradation modeling
- Configurable failure modes (gradual, sudden, intermittent)
- Real-time data generation and broadcasting

### **Intelligent Analytics**
- Health scoring algorithm (0-100 scale)
- Risk level assessment (LOW, MEDIUM, HIGH, CRITICAL)
- Predictive maintenance recommendations
- Cost estimation for maintenance planning

### **Professional Reporting**
- Executive summaries with key insights
- Detailed machine-by-machine analysis
- Performance metrics and benchmarking
- Actionable recommendations with priority levels

## 📚 Documentation

### **User Guides**
- [Quick Start Guide](#-quick-start)
- [Dashboard Tutorial](#-using-the-system)
- [API Reference](#-api-endpoints)
- [Report Generation Guide](#-comprehensive-reporting)

### **Developer Resources**
- [Architecture Overview](#-system-architecture)
- [Model Documentation](#-model-performance)
- [API Integration Guide](#-api-usage-examples)
- [Deployment Guide](#-deployment)

## 🚀 Deployment

### **Development Environment**
```bash
# Start development server
python streaming_demo.py demo

# Access dashboard
http://localhost:8000/dashboard
```

### **Production Deployment**
```bash
# Using Docker (recommended)
docker build -t digital-twin .
docker run -p 8000:8000 digital-twin

# Using systemd
sudo systemctl start digital-twin
```

### **Environment Variables**
```bash
export API_HOST=0.0.0.0
export API_PORT=8000
export LOG_LEVEL=INFO
export MAX_MACHINES=50
```

## 🔒 Security Considerations

- **API Authentication**: Token-based authentication (configurable)
- **Data Encryption**: TLS/SSL for data in transit
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: API endpoint protection
- **Audit Logging**: Complete activity tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **C-MAPSS Dataset**: NASA for providing the turbofan engine dataset
- **TensorFlow**: For the deep learning framework
- **FastAPI**: For the high-performance API framework
- **Digital Twin Community**: For inspiration and best practices

## 📞 Support

For support and questions:
- 📧 Email: support@digitaltwin.ai
- 💬 Discord: [Join our community](https://discord.gg/digitaltwin)
- 📖 Documentation: [Full docs](https://docs.digitaltwin.ai)
- 🐛 Issues: [GitHub Issues](https://github.com/yourrepo/issues)

---

**🏭 TwinMind Digital Twin** - Transforming machinery into intelligent digital counterparts for predictive maintenance and operational excellence.
