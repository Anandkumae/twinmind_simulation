"""
Enhanced streaming demo with database integration
"""
import asyncio
import logging
import time
import json
from datetime import datetime
import threading
import requests
import random
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseIntegratedDemo:
    """Enhanced demo with database storage"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8000"
        self.simulator_running = False
        self.simulation_thread = None
        
    def check_api_health(self) -> bool:
        """Check if API is running"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ API Health: {data['status']}")
                logger.info(f"📊 Database Connected: {data['database_connected']}")
                logger.info(f"🔗 WebSocket Connections: {data['websocket_connections']}")
                return True
        except Exception as e:
            logger.error(f"❌ API health check failed: {e}")
        return False
    
    def test_database_endpoints(self) -> bool:
        """Test database-specific endpoints"""
        try:
            # Test machines endpoint
            response = requests.get(f"{self.api_base_url}/machines")
            if response.status_code == 200:
                machines = response.json()
                logger.info(f"🏭 Found {len(machines['machines'])} machines")
                
                # Test system health
                response = requests.get(f"{self.api_base_url}/system/health")
                if response.status_code == 200:
                    health = response.json()
                    logger.info(f"📈 System Health Score: {health['system_health_score']}")
                    logger.info(f"📊 Total Anomalies: {health['total_anomalies']}")
                
                return True
        except Exception as e:
            logger.error(f"❌ Database endpoint test failed: {e}")
        return False
    
    def send_sensor_data_with_db(self, machine_id: int) -> bool:
        """Send sensor data and verify database storage"""
        try:
            # Generate realistic sensor data
            temperature = 60 + random.uniform(0, 40)  # 60-100°C
            vibration = 2 + random.uniform(0, 8)     # 2-10Hz
            pressure = 1.5 + random.uniform(0, 3.5)  # 1.5-5kPa
            
            sensor_data = {
                "machine_id": machine_id,
                "temperature": temperature,
                "vibration": vibration,
                "pressure": pressure
            }
            
            # Send to API
            response = requests.post(
                f"{self.api_base_url}/sensor-data",
                json=sensor_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                rul = result.get('rul')
                health = result.get('health')
                if rul is not None:
                    logger.info(f"📊 Machine {machine_id}: RUL={rul:.1f}, Health={health}")
                else:
                    logger.info(f"📊 Machine {machine_id}: RUL=N/A, Health={health}")
                
                # Verify data was stored in database
                self.verify_data_storage(machine_id)
                return True
            else:
                logger.error(f"❌ Failed to send data for machine {machine_id}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending sensor data for machine {machine_id}: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            return False
    
    def verify_data_storage(self, machine_id: int):
        """Verify data was stored in database"""
        try:
            # Check latest sensor data
            response = requests.get(f"{self.api_base_url}/machines/{machine_id}/latest?limit=1")
            if response.status_code == 200:
                data = response.json()
                if data['sensor_data']:
                    latest = data['sensor_data'][0]
                    # Handle both dict and object formats
                    if hasattr(latest, 'temperature'):
                        temp = latest.temperature
                        vib = latest.vibration
                        pres = latest.pressure
                    else:
                        temp = latest.get('temperature')
                        vib = latest.get('vibration')
                        pres = latest.get('pressure')
                    logger.info(f"✅ Stored: Temp={temp}°C, Vib={vib}Hz, Pres={pres}kPa")
            
            # Check predictions
            response = requests.get(f"{self.api_base_url}/machines/{machine_id}/predictions?limit=1")
            if response.status_code == 200:
                data = response.json()
                if data['predictions']:
                    pred = data['predictions'][0]
                    # Handle both dict and object formats
                    rul = pred.get('rul') if hasattr(pred, 'get') else getattr(pred, 'rul', None)
                    health_status = pred.get('health_status') if hasattr(pred, 'get') else getattr(pred, 'health_status', None)
                    logger.info(f"✅ Prediction: RUL={rul:.1f if rul is not None else 'N/A'}, Health={health_status}")
            
            # Check anomalies
            response = requests.get(f"{self.api_base_url}/machines/{machine_id}/anomalies?active_only=true")
            if response.status_code == 200:
                data = response.json()
                if data['anomalies']:
                    for anomaly in data['anomalies']:
                        logger.warning(f"⚠️ Anomaly: {anomaly.type} - {anomaly.severity}")
                        
        except Exception as e:
            logger.error(f"❌ Error verifying data storage: {e}")
    
    def simulate_machine_data(self, machine_id: int, cycles: int = 20):
        """Simulate sensor data for a machine with degradation"""
        logger.info(f"🔄 Starting simulation for machine {machine_id} ({cycles} cycles)")
        
        base_temp = 70 + (machine_id * 5)  # Different base temps for each machine
        base_vib = 3 + (machine_id * 0.5)
        base_pressure = 2.5 + (machine_id * 0.2)
        
        for cycle in range(cycles):
            if not self.simulator_running:
                break
            
            # Simulate degradation (values increase over time)
            degradation_factor = 1 + (cycle * 0.02)  # 2% degradation per cycle
            
            temperature = base_temp * degradation_factor + random.uniform(-5, 5)
            vibration = base_vib * degradation_factor + random.uniform(-1, 1)
            pressure = base_pressure * degradation_factor + random.uniform(-0.5, 0.5)
            
            sensor_data = {
                "machine_id": machine_id,
                "temperature": min(temperature, 120),  # Cap at realistic max
                "vibration": min(vibration, 15),
                "pressure": min(pressure, 8)
            }
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/sensor-data",
                    json=sensor_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if cycle % 5 == 0:  # Log every 5 cycles
                        rul = result.get('rul', 0)
                        health = result.get('health', 'UNKNOWN')
                        if rul is not None and rul != 0:
                            logger.info(f"📊 Cycle {cycle+1}: RUL={rul:.1f}, Health={health}")
                        else:
                            logger.info(f"📊 Cycle {cycle+1}: RUL=N/A, Health={health}")
                
            except Exception as e:
                logger.error(f"❌ Simulation error at cycle {cycle+1}: {e}")
            
            time.sleep(2)  # Wait 2 seconds between cycles
        
        logger.info(f"✅ Simulation completed for machine {machine_id}")
    
    def run_multi_machine_simulation(self):
        """Run simulation for multiple machines concurrently"""
        logger.info("🚀 Starting multi-machine simulation with database storage")
        
        # Get available machines
        try:
            response = requests.get(f"{self.api_base_url}/machines")
            if response.status_code != 200:
                logger.error("❌ Failed to get machines list")
                return
            
            machines_data = response.json()
            machines = machines_data['machines']
            
            if not machines:
                logger.error("❌ No machines found. Please run database initialization first.")
                return
            
            logger.info(f"🏭 Found {len(machines)} machines")
            
            # Start simulation threads for each machine
            threads = []
            for machine in machines:
                # Handle both dict and object formats
                machine_id = machine.id if hasattr(machine, 'id') else machine.get('id')
                thread = threading.Thread(
                    target=self.simulate_machine_data,
                    args=(machine_id, 30)  # 30 cycles per machine
                )
                thread.start()
                threads.append(thread)
                time.sleep(1)  # Stagger machine starts
            
            # Wait for all simulations to complete
            for thread in threads:
                thread.join()
            
            logger.info("🎉 All simulations completed!")
            
            # Show final database status
            self.show_final_status()
            
        except Exception as e:
            logger.error(f"❌ Multi-machine simulation failed: {e}")
    
    def show_final_status(self):
        """Show final database and system status"""
        try:
            logger.info("📊 Final System Status:")
            
            # System health
            response = requests.get(f"{self.api_base_url}/system/health")
            if response.status_code == 200:
                health = response.json()
                logger.info(f"  📈 System Health Score: {health['system_health_score']}")
                logger.info(f"  🏭 Total Machines: {health['total_machines']}")
                logger.info(f"  ✅ Healthy: {health['healthy_machines']}")
                logger.info(f"  ⚠️ Warning: {health['warning_machines']}")
                logger.info(f"  🚨 Critical: {health['critical_machines']}")
                logger.info(f"  📊 Collecting: {health['collecting_machines']}")
                logger.info(f"  ⚠️ Total Anomalies: {health['total_anomalies']}")
                logger.info(f"  🔴 Unresolved Anomalies: {health['unresolved_anomalies']}")
            
            # Database metrics
            response = requests.get(f"{self.api_base_url}/system/metrics?metric_name=sensor_data_ingestion")
            if response.status_code == 200:
                metrics = response.json()
                logger.info(f"  📡 Data Points Ingested: {len(metrics['metrics'])}")
            
        except Exception as e:
            logger.error(f"❌ Error getting final status: {e}")
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.simulator_running = False
        logger.info("🛑 Simulation stopped")

def main():
    """Main demo function"""
    print("🚀 Digital Twin Database-Integrated Demo")
    print("=" * 50)
    
    demo = DatabaseIntegratedDemo()
    
    try:
        # Step 1: Check API health
        print("\n📡 Step 1: Checking API health...")
        if not demo.check_api_health():
            print("❌ API is not running. Please start the API first:")
            print("   python streaming_api_db.py")
            return
        
        # Step 2: Test database endpoints
        print("\n🗄️ Step 2: Testing database endpoints...")
        if not demo.test_database_endpoints():
            print("❌ Database endpoints not working. Please check database configuration.")
            return
        
        # Step 3: Test single machine data flow
        print("\n📊 Step 3: Testing single machine data flow...")
        demo.simulator_running = True
        
        # Test with machine 1
        if not demo.send_sensor_data_with_db(1):
            print("❌ Single machine test failed")
            return
        
        print("✅ Single machine data flow working!")
        
        # Step 4: Run multi-machine simulation
        print("\n🏭 Step 4: Running multi-machine simulation...")
        demo.run_multi_machine_simulation()
        
        print("\n🎉 Demo completed successfully!")
        print("\n📊 Check the dashboard at: http://localhost:8000/dashboard")
        print("📊 Check the API health at: http://localhost:8000/health")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        demo.stop_simulation()
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        demo.stop_simulation()
    finally:
        demo.stop_simulation()

if __name__ == "__main__":
    main()
