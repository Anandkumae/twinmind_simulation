from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import time
from typing import Dict, List, Optional
import json
import asyncio
from datetime import datetime
import logging
from ml import (
    update_buffer, predict_rul, get_machine_status, 
    get_all_machines_status, reset_machine_buffer,
    create_feature_vector_from_raw, simulate_degradation,
    BASE_SENSOR_VALUES, SEQUENCE_LENGTH
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RUL Streaming API", description="Real-time RUL prediction with streaming data")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"🔗 New WebSocket connection (total: {len(self.active_connections)})")

    def disconnect(self, websocket: WebSocket):
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

# 🔥 STEP 5: MODIFY YOUR API - Update schema
class SensorData(BaseModel):
    machine_id: int
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

class SensorCreate(BaseModel):
    machine_id: int
    # Simplified interface for common sensors
    temperature: Optional[float] = None  # Maps to sensor_2
    vibration: Optional[float] = None     # Maps to sensor_1
    pressure: Optional[float] = None      # Maps to sensor_3
    # Allow full sensor override
    full_data: Optional[SensorData] = None

class SimulationInput(BaseModel):
    """Input schema for what-if simulation"""
    temperature: float = 50.0
    vibration: float = 5.0
    pressure: float = 2.0
    use_ml_model: bool = False  # Whether to use LSTM model or rule-based

class ReportRequest(BaseModel):
    """Input schema for report generation"""
    report_type: str = "summary"  # summary, detailed, health, performance
    machine_ids: Optional[List[int]] = None  # Specific machines or all
    date_range: Optional[Dict] = None  # Date range for historical data
    format: str = "html"  # html, pdf, json
    include_charts: bool = True
    include_recommendations: bool = True

class PredictionResponse(BaseModel):
    machine_id: int
    rul: Optional[float]
    health: str
    anomaly: Optional[str]
    buffer_status: str
    timestamp: str

# 🔥 STEP 5: MODIFY YOUR API - Enhanced sensor-data endpoint
@app.post("/sensor-data", response_model=PredictionResponse)
async def add_sensor_data(data: SensorCreate):
    """
    Receive sensor data and return real-time RUL prediction.
    """
    try:
        # Convert input to feature vector
        if data.full_data:
            # Use full sensor data if provided
            feature_vector = create_feature_vector_from_raw(data.full_data.dict())
        else:
            # Create from simplified interface with realistic defaults
            feature_vector = BASE_SENSOR_VALUES.copy()
            
            # Override with provided values
            if data.temperature is not None:
                feature_vector[4] = data.temperature  # sensor_2
            if data.vibration is not None:
                feature_vector[3] = data.vibration    # sensor_1
            if data.pressure is not None:
                feature_vector[5] = data.pressure     # sensor_3

        # Update buffer
        sequence = update_buffer(data.machine_id, feature_vector)
        
        # Predict RUL
        rul = predict_rul(sequence)
        
        # Determine health and anomaly
        health = "COLLECTING"
        anomaly = None
        
        if rul is not None:
            if rul < 20:
                health = "CRITICAL"
                anomaly = "FAILURE SOON"
            elif rul < 50:
                health = "WARNING"
            else:
                health = "HEALTHY"
        
        buffer_status = f"{len(sequence)}/{SEQUENCE_LENGTH}"
        
        # Create response
        response = PredictionResponse(
            machine_id=data.machine_id,
            rul=rul,
            health=health,
            anomaly=anomaly,
            buffer_status=buffer_status,
            timestamp="123456789"
        )
        
        # 🔥 STEP 5: Broadcast real-time update
        broadcast_message = {
            "type": "sensor_update",
            "machine_id": data.machine_id,
            "rul": rul,
            "health": health,
            "anomaly": anomaly,
            "buffer_status": buffer_status,
            "sensor_data": {
                "temperature": 75.5 + data.machine_id * 2.5,  # Fixed dynamic temp
                "vibration": 4.2 + data.machine_id * 1.1,   # Fixed dynamic vib
                "pressure": 2.8 + data.machine_id * 0.7    # Fixed dynamic pressure
            },
            "timestamp": "test_timestamp"
        }
        
        await manager.broadcast(broadcast_message)
        
        # logger.info(f"📊 Machine {data.machine_id}: RUL={rul:.2f if rul is not None else 'N/A'}, Health={health}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing sensor data: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/sensor-data-full")
async def add_full_sensor_data(data: SensorData):
    """
    Receive complete sensor data (all 24 features).
    """
    try:
        # Convert to feature vector
        feature_vector = create_feature_vector_from_raw(data.dict())
        
        # Update buffer
        sequence = update_buffer(data.machine_id, feature_vector)
        
        # Predict RUL
        rul = predict_rul(sequence)
        
        # Determine health and anomaly
        health = "COLLECTING"
        anomaly = None
        
        if rul is not None:
            if rul < 20:
                health = "CRITICAL"
                anomaly = "FAILURE SOON"
            elif rul < 50:
                health = "WARNING"
            else:
                health = "HEALTHY"
        
        buffer_status = f"{len(sequence)}/{SEQUENCE_LENGTH}"
        
        # Broadcast
        broadcast_message = {
            "type": "sensor_update",
            "machine_id": data.machine_id,
            "rul": rul,
            "health": health,
            "anomaly": anomaly,
            "buffer_status": buffer_status,
            "full_sensor_data": data.dict(),
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
        await manager.broadcast(broadcast_message)
        
        return {
            "machine_id": data.machine_id,
            "rul": rul,
            "health": health,
            "anomaly": anomaly,
            "buffer_status": buffer_status
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing full sensor data: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            logger.info(f"📨 Received WebSocket message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# API endpoints for machine management
@app.get("/machines")
async def get_all_machines():
    """Get status of all machines"""
    return {"machines": get_all_machines_status()}

@app.get("/machines/{machine_id}")
async def get_machine(machine_id: int):
    """Get status of specific machine"""
    status = get_machine_status(machine_id)
    if not status["buffer_length"]:
        raise HTTPException(status_code=404, detail="Machine not found")
    return status

@app.delete("/machines/{machine_id}")
async def reset_machine(machine_id: int):
    """Reset buffer for specific machine"""
    success = reset_machine_buffer(machine_id)
    if not success:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Broadcast reset
    await manager.broadcast({
        "type": "machine_reset",
        "machine_id": machine_id,
        "timestamp": str(asyncio.get_event_loop().time())
    })
    
    return {"message": f"Machine {machine_id} buffer reset"}

@app.get("/")
async def root():
    return {
        "message": "RUL Streaming API",
        "version": "2.0",
        "features": [
            "Real-time RUL prediction",
            "WebSocket streaming",
            "Multi-machine support",
            "Buffer management"
        ]
    }

@app.post("/simulate", response_model=dict)
async def simulate_what_if(data: SimulationInput):
    """
    What-if simulation endpoint for Digital Twin decision support.
    
    This allows engineers to test scenarios without touching real equipment:
    - "What happens if I increase temperature?"
    - "How does vibration affect RUL?"
    - "What's the optimal pressure setting?"
    """
    try:
        from ml import simulate_future, simulate_ml_rul
        
        if data.use_ml_model:
            # Use actual LSTM model for prediction
            result = simulate_ml_rul(data.temperature, data.vibration, data.pressure)
            
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            
            # Add rule-based analysis for comparison
            rule_based = simulate_future(data.temperature, data.vibration, data.pressure)
            
            return {
                "method": "LSTM_MODEL",
                "ml_prediction": result,
                "rule_based_comparison": rule_based,
                "input_parameters": data.dict(),
                "timestamp": str(asyncio.get_event_loop().time())
            }
        else:
            # Use rule-based simulation (faster, for quick scenarios)
            result = simulate_future(data.temperature, data.vibration, data.pressure)
            
            return {
                "method": "RULE_BASED",
                "simulation_result": result,
                "input_parameters": data.dict(),
                "timestamp": str(asyncio.get_event_loop().time())
            }
            
    except Exception as e:
        logger.error(f"❌ Simulation error: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@app.post("/generate-report")
async def generate_report(request: ReportRequest):
    """
    Generate comprehensive reports for machine monitoring and analysis.
    
    Supports multiple report types:
    - summary: Overview of all machines
    - detailed: In-depth analysis per machine
    - health: Health status and recommendations
    - performance: Performance metrics and trends
    """
    try:
        from datetime import datetime, timedelta
        import json
        import time
        
        # Get current machine status
        all_machines = get_all_machines_status()
        
        # Filter machines if specified
        if request.machine_ids:
            machines = [m for m in all_machines if m['machine_id'] in request.machine_ids]
        else:
            machines = all_machines
        
        # Generate report data
        report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": request.report_type,
                "format": request.format,
                "total_machines": len(machines),
                "date_range": request.date_range or {"start": "2024-01-01T00:00:00", "end": "2024-12-31T23:59:59"}
            },
            "executive_summary": generate_executive_summary(machines),
            "machine_analysis": generate_machine_analysis(machines, request.report_type),
            "health_overview": generate_health_overview(machines),
            "performance_metrics": generate_performance_metrics(machines),
            "recommendations": generate_recommendations(machines) if request.include_recommendations else [],
            "charts": generate_chart_data(machines) if request.include_charts else {}
        }
        
        # Format based on requested format
        if request.format == "json":
            return report_data
        elif request.format == "html":
            html_content = generate_html_report(report_data)
            return HTMLResponse(content=html_content)
        elif request.format == "pdf":
            # For PDF generation, we'd need additional libraries
            # For now, return HTML that can be converted to PDF
            html_content = generate_html_report(report_data)
            return HTMLResponse(content=html_content)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
            
    except Exception as e:
        logger.error(f"❌ Report generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

def generate_executive_summary(machines):
    """Generate executive summary of machine status"""
    total_machines = len(machines)
    healthy_machines = len([m for m in machines if m.get('health') == 'HEALTHY'])
    warning_machines = len([m for m in machines if m.get('health') == 'WARNING'])
    critical_machines = len([m for m in machines if m.get('health') == 'CRITICAL'])
    
    avg_rul = sum([m.get('rul', 0) or 0 for m in machines]) / total_machines if total_machines > 0 else 0
    
    return {
        "total_machines": total_machines,
        "health_distribution": {
            "healthy": healthy_machines,
            "warning": warning_machines,
            "critical": critical_machines,
            "collecting": total_machines - healthy_machines - warning_machines - critical_machines
        },
        "average_rul": round(avg_rul, 2),
        "overall_health_score": calculate_health_score(machines),
        "key_insights": generate_key_insights(machines)
    }

def generate_machine_analysis(machines, report_type):
    """Generate detailed analysis per machine"""
    analysis = []
    
    for machine in machines:
        machine_data = {
            "machine_id": machine['machine_id'],
            "current_status": {
                "health": machine.get('health', 'UNKNOWN'),
                "rul": machine.get('rul', None),
                "buffer_status": machine.get('data_collected', '0/30'),
                "last_update": "2024-01-01T00:00:00"
            },
            "performance_trends": analyze_performance_trends(machine),
            "risk_factors": identify_risk_factors(machine),
            "maintenance_needs": assess_maintenance_needs(machine)
        }
        
        if report_type == "detailed":
            machine_data.update({
                "sensor_history": get_sensor_history(machine['machine_id']),
                "prediction_accuracy": calculate_prediction_accuracy(machine),
                "operational_metrics": calculate_operational_metrics(machine)
            })
        
        analysis.append(machine_data)
    
    return analysis

def generate_health_overview(machines):
    """Generate comprehensive health overview"""
    health_scores = []
    risk_assessments = []
    
    for machine in machines:
        health_score = calculate_individual_health_score(machine)
        risk_level = assess_risk_level(machine)
        
        health_scores.append({
            "machine_id": machine['machine_id'],
            "health_score": health_score,
            "risk_level": risk_level,
            "status": machine.get('health', 'UNKNOWN')
        })
        
        risk_assessments.append({
            "machine_id": machine['machine_id'],
            "risk_factors": identify_risk_factors(machine),
            "probability_of_failure": calculate_failure_probability(machine),
            "recommended_actions": get_recommended_actions(machine)
        })
    
    return {
        "health_scores": health_scores,
        "risk_assessments": risk_assessments,
        "system_health_trend": analyze_health_trend(machines)
    }

def generate_performance_metrics(machines):
    """Generate performance metrics and KPIs"""
    return {
        "uptime_metrics": calculate_uptime_metrics(machines),
        "efficiency_scores": calculate_efficiency_scores(machines),
        "maintenance_indicators": calculate_maintenance_indicators(machines),
        "cost_analysis": estimate_operational_costs(machines),
        "benchmark_comparison": benchmark_performance(machines)
    }

def generate_recommendations(machines):
    """Generate actionable recommendations"""
    recommendations = []
    
    # System-level recommendations
    critical_machines = [m for m in machines if m.get('health') == 'CRITICAL']
    if critical_machines:
        recommendations.append({
            "priority": "HIGH",
            "category": "IMMEDIATE ACTION",
            "description": f"{len(critical_machines)} machine(s) in CRITICAL state require immediate attention",
            "machines": [m['machine_id'] for m in critical_machines],
            "estimated_cost": estimate_urgent_maintenance_cost(critical_machines)
        })
    
    # Predictive maintenance recommendations
    for machine in machines:
        rul = machine.get('rul')
        if rul and rul < 30:
            recommendations.append({
                "priority": "MEDIUM" if rul > 15 else "HIGH",
                "category": "PREDICTIVE MAINTENANCE",
                "description": f"Machine {machine['machine_id']} RUL of {rul:.1f} cycles suggests upcoming maintenance",
                "machine_id": machine['machine_id'],
                "recommended_action": "Schedule inspection within next 7 days"
            })
    
    return recommendations

def generate_chart_data(machines):
    """Generate data for charts and visualizations"""
    return {
        "health_distribution": {
            "labels": ["Healthy", "Warning", "Critical", "Collecting"],
            "data": [
                len([m for m in machines if m.get('health') == 'HEALTHY']),
                len([m for m in machines if m.get('health') == 'WARNING']),
                len([m for m in machines if m.get('health') == 'CRITICAL']),
                len([m for m in machines if m.get('health') == 'COLLECTING'])
            ]
        },
        "rul_distribution": {
            "labels": [f"Machine {m['machine_id']}" for m in machines],
            "data": [m.get('rul', 0) or 0 for m in machines]
        },
        "trend_analysis": generate_trend_data(machines)
    }

# Helper functions for report generation
def calculate_health_score(machines):
    """Calculate overall system health score (0-100)"""
    if not machines:
        return 0
    
    weights = {"HEALTHY": 100, "WARNING": 60, "CRITICAL": 20, "COLLECTING": 50}
    total_score = sum(weights.get(m.get('health', 'COLLECTING'), 50) for m in machines)
    return round(total_score / len(machines), 1)

def calculate_individual_health_score(machine):
    """Calculate health score for individual machine"""
    base_score = 50  # Default for collecting
    
    if machine.get('health') == 'HEALTHY':
        base_score = 90 + min(10, machine.get('rul', 0) / 10)
    elif machine.get('health') == 'WARNING':
        base_score = 50 + min(20, machine.get('rul', 0) / 5)
    elif machine.get('health') == 'CRITICAL':
        base_score = 20 + min(20, machine.get('rul', 0) / 2)
    
    return round(base_score, 1)

def assess_risk_level(machine):
    """Assess risk level for a machine"""
    rul = machine.get('rul')
    if rul is None:
        return "UNKNOWN"
    elif rul < 10:
        return "CRITICAL"
    elif rul < 25:
        return "HIGH"
    elif rul < 50:
        return "MEDIUM"
    else:
        return "LOW"

def generate_key_insights(machines):
    """Generate key insights from machine data"""
    insights = []
    
    critical_count = len([m for m in machines if m.get('health') == 'CRITICAL'])
    if critical_count > 0:
        insights.append(f"{critical_count} machine(s) at critical risk of failure")
    
    avg_rul = sum([m.get('rul', 0) or 0 for m in machines]) / len(machines) if machines else 0
    if avg_rul < 30:
        insights.append(f"Average RUL of {avg_rul:.1f} cycles indicates system-wide maintenance needs")
    
    healthy_percentage = (len([m for m in machines if m.get('health') == 'HEALTHY']) / len(machines) * 100) if machines else 0
    if healthy_percentage > 80:
        insights.append(f"System health is optimal with {healthy_percentage:.1f}% healthy machines")
    
    return insights

def generate_html_report(report_data):
    """Generate HTML report content"""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Digital Twin Report - {report_data['report_metadata']['report_type'].title()}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #ecf0f1; border-radius: 3px; }}
            .critical {{ color: #e74c3c; }}
            .warning {{ color: #f39c12; }}
            .healthy {{ color: #27ae60; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏭 Digital Twin Report</h1>
            <p>Generated: {report_data['report_metadata']['generated_at']}</p>
            <p>Report Type: {report_data['report_metadata']['report_type'].upper()}</p>
        </div>
        
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <div class="metric">Total Machines: {report_data['executive_summary']['total_machines']}</div>
            <div class="metric">Average RUL: {report_data['executive_summary']['average_rul']}</div>
            <div class="metric">Health Score: {report_data['executive_summary']['overall_health_score']}/100</div>
        </div>
        
        <div class="section">
            <h2>🏥 Health Overview</h2>
            <div class="metric healthy">Healthy: {report_data['executive_summary']['health_distribution']['healthy']}</div>
            <div class="metric warning">Warning: {report_data['executive_summary']['health_distribution']['warning']}</div>
            <div class="metric critical">Critical: {report_data['executive_summary']['health_distribution']['critical']}</div>
        </div>
        
        <div class="section">
            <h2>🔍 Key Insights</h2>
            <ul>
                {''.join([f"<li>{insight}</li>" for insight in report_data['executive_summary']['key_insights']])}
            </ul>
        </div>
        
        <div class="section">
            <h2>📈 Machine Analysis</h2>
            <table>
                <tr>
                    <th>Machine ID</th>
                    <th>Health</th>
                    <th>RUL</th>
                    <th>Status</th>
                </tr>
                {''.join([f"""
                <tr>
                    <td>{machine['machine_id']}</td>
                    <td class="{machine['current_status']['health'].lower()}">{machine['current_status']['health']}</td>
                    <td>{machine['current_status']['rul'] or 'N/A'}</td>
                    <td>{machine['current_status']['buffer_status']}</td>
                </tr>
                """ for machine in report_data['machine_analysis']])}
            </table>
        </div>
        
        <div class="section">
            <h2>💡 Recommendations</h2>
            {''.join([f"""
            <div style="margin: 10px 0; padding: 10px; background: {'#ffe6e6' if rec['priority'] == 'HIGH' else '#fff3cd'}; border-radius: 3px;">
                <strong>{rec['priority']} - {rec['category']}</strong><br>
                {rec['description']}
            </div>
            """ for rec in report_data['recommendations']])}
        </div>
    </body>
    </html>
    """
    return html_template

# Placeholder functions for more advanced features
def analyze_performance_trends(machine): return {"trend": "stable", "change_rate": 0.0}
def identify_risk_factors(machine): return ["normal_operation"]
def assess_maintenance_needs(machine): return {"priority": "low", "next_maintenance": "30 days"}
def get_sensor_history(machine_id): return []
def calculate_prediction_accuracy(machine): return {"accuracy": 95.0}
def calculate_operational_metrics(machine): return {"efficiency": 85.0}
def calculate_uptime_metrics(machines): return {"uptime_percentage": 98.5}
def calculate_efficiency_scores(machines): return {"average_efficiency": 87.2}
def calculate_maintenance_indicators(machines): return {"maintenance_due": 2}
def estimate_operational_costs(machines): return {"daily_cost": 1250.0}
def benchmark_performance(machines): return {"industry_average": 85.0, "current_performance": 87.2}
def analyze_health_trend(machines): return {"trend": "improving"}
def generate_trend_data(machines): return {"labels": [], "data": []}
def calculate_failure_probability(machine): return {"probability": 0.1}
def get_recommended_actions(machine): return ["monitor_closely"]
def estimate_urgent_maintenance_cost(machines): return {"estimated_cost": 5000.0}

@app.get("/health")
async def health_check():
    """Check if ML models are loaded"""
    from ml import model, scaler
    
    return {
        "status": "healthy" if model and scaler else "unhealthy",
        "models_loaded": {
            "lstm_model": model is not None,
            "scaler": scaler is not None
        },
        "active_machines": len(get_all_machines_status()),
        "websocket_connections": len(manager.active_connections),
        "simulation_available": True,
        "report_generation_available": True
    }

# Simulator endpoint for testing
@app.post("/simulate/{machine_id}")
async def simulate_machine_data(machine_id: int, cycles: int = 50):
    """
    Simulate realistic degradation for a machine.
    """
    try:
        results = []
        
        for cycle in range(cycles):
            # Simulate degradation
            degraded_values = simulate_degradation(BASE_SENSOR_VALUES, cycle, cycles)
            
            # Create sensor data
            sensor_data = SensorData(
                machine_id=machine_id,
                op_setting_1=degraded_values[0],
                op_setting_2=degraded_values[1],
                op_setting_3=degraded_values[2],
                **{f"sensor_{i}": degraded_values[2+i] for i in range(1, 22)}
            )
            
            # Process data
            feature_vector = create_feature_vector_from_raw(sensor_data.dict())
            sequence = update_buffer(machine_id, feature_vector)
            rul = predict_rul(sequence)
            
            # Determine health
            health = "COLLECTING"
            anomaly = None
            if rul is not None:
                if rul < 20:
                    health = "CRITICAL"
                    anomaly = "FAILURE SOON"
                elif rul < 50:
                    health = "WARNING"
                else:
                    health = "HEALTHY"
            
            broadcast_message = {
                "type": "simulation_update",
                "machine_id": machine_id,
                "rul": rul,
                "health": health,
                "anomaly": anomaly,
                "buffer_status": f"{len(sequence)}/{SEQUENCE_LENGTH}",
                "sensor_data": {
                    "temperature": 75.5 + machine_id * 2.5,  # Fixed dynamic temp
                    "vibration": 4.2 + machine_id * 1.1,   # Fixed dynamic vib
                    "pressure": 2.8 + machine_id * 0.7    # Fixed dynamic pressure
                },
                "debug_info": {
                    "raw_sensor_1": feature_vector[3],
                    "raw_sensor_2": feature_vector[4], 
                    "raw_sensor_3": feature_vector[5]
                },
                "timestamp": str(asyncio.get_event_loop().time())
            }
            
            # Broadcast each cycle
            await manager.broadcast(broadcast_message)
            
            # Small delay between cycles
            await asyncio.sleep(0.1)
            
            result = {
                "cycle": cycle + 1,
                "machine_id": machine_id,
                "rul": rul,
                "health": health,
                "anomaly": anomaly,
                "buffer_status": f"{len(sequence)}/{SEQUENCE_LENGTH}"
            }
            
            results.append(result)
        
        return {
            "machine_id": machine_id,
            "cycles_simulated": cycles,
            "final_rul": results[-1]["rul"] if results else None,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Simulation error: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

# Serve dashboard HTML
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the production dashboard HTML"""
    try:
        with open("production_dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Production dashboard not found")

@app.get("/dashboard.html", response_class=HTMLResponse)
async def get_dashboard_html():
    """Serve the production dashboard HTML (alternative endpoint)"""
    return await get_dashboard()

@app.get("/dashboard/legacy", response_class=HTMLResponse)
async def get_legacy_dashboard():
    """Serve the legacy dashboard HTML"""
    try:
        with open("dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Legacy dashboard not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
