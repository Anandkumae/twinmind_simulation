import asyncio
import aiohttp
import time
import random
import numpy as np
import json
import logging
from typing import Dict, List
from ml import BASE_SENSOR_VALUES, simulate_degradation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MachineSimulator:
    """Simulates realistic C-MAPSS sensor data for multiple machines"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.machines: Dict[int, Dict] = {}
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def add_machine(self, machine_id: int, max_cycles: int = 200, failure_type: str = "gradual"):
        """Add a machine to simulate"""
        self.machines[machine_id] = {
            "current_cycle": 0,
            "max_cycles": max_cycles,
            "failure_type": failure_type,
            "base_values": BASE_SENSOR_VALUES.copy(),
            "start_time": time.time()
        }
        logger.info(f"🆕 Added machine {machine_id} (max cycles: {max_cycles}, type: {failure_type})")
    
    def add_random_machines(self, count: int = 5):
        """Add multiple machines with random configurations"""
        import random
        
        failure_types = ["gradual", "sudden", "intermittent"]
        
        for i in range(1, count + 1):
            machine_id = i
            max_cycles = random.randint(80, 150)
            failure_type = random.choice(failure_types)
            
            self.add_machine(machine_id, max_cycles, failure_type)
        
        logger.info(f"🎲 Added {count} random machines")
    
    def generate_sensor_reading(self, machine_id: int) -> Dict:
        """Generate a single sensor reading for a machine"""
        if machine_id not in self.machines:
            raise ValueError(f"Machine {machine_id} not found")
        
        machine = self.machines[machine_id]
        cycle = machine["current_cycle"]
        max_cycles = machine["max_cycles"]
        
        # Generate degraded sensor values
        degraded_values = simulate_degradation(machine["base_values"], cycle, max_cycles)
        
        # Create sensor data dictionary
        sensor_data = {
            "machine_id": machine_id,
            "op_setting_1": degraded_values[0],
            "op_setting_2": degraded_values[1], 
            "op_setting_3": degraded_values[2],
        }
        
        # Add sensor readings
        for i in range(1, 22):
            sensor_data[f"sensor_{i}"] = degraded_values[2 + i]
        
        # Add some noise and variations
        if machine["failure_type"] == "sudden":
            # Sudden failure simulation
            if cycle > max_cycles * 0.8:
                # Add spikes near failure
                for sensor_key in [k for k in sensor_data.keys() if k.startswith("sensor_")]:
                    if random.random() < 0.1:  # 10% chance of spike
                        sensor_data[sensor_key] *= random.uniform(1.5, 3.0)
        
        elif machine["failure_type"] == "intermittent":
            # Intermittent issues
            if random.random() < 0.05:  # 5% chance of intermittent issue
                sensor_key = random.choice([k for k in sensor_data.keys() if k.startswith("sensor_")])
                sensor_data[sensor_key] *= random.uniform(0.5, 2.0)
        
        machine["current_cycle"] += 1
        
        return sensor_data
    
    async def send_sensor_data(self, sensor_data: Dict) -> Dict:
        """Send sensor data to API"""
        try:
            url = f"{self.api_url}/sensor-data-full"
            
            async with self.session.post(url, json=sensor_data) as response:
                if response.status == 200:
                    result = await response.json()
                    rul = result.get('rul')
                    rul_str = f"{rul:.2f}" if rul is not None else "N/A"
                    health = result.get('health', 'N/A')
                    logger.info(f"📊 Machine {sensor_data['machine_id']}: RUL={rul_str}, Health={health}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"❌ API error: {response.status} - {error_text}")
                    return {"error": f"API error: {response.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Error sending data: {e}")
            return {"error": str(e)}
    
    async def simulate_machine(self, machine_id: int, interval: float = 1.0, max_cycles: int = None):
        """Simulate a single machine continuously"""
        if machine_id not in self.machines:
            raise ValueError(f"Machine {machine_id} not found")
        
        machine = self.machines[machine_id]
        if max_cycles:
            machine["max_cycles"] = max_cycles
        
        logger.info(f"🚀 Starting simulation for machine {machine_id}")
        
        while machine["current_cycle"] < machine["max_cycles"]:
            try:
                # Generate sensor reading
                sensor_data = self.generate_sensor_reading(machine_id)
                
                # Send to API
                result = await self.send_sensor_data(sensor_data)
                
                # Check if machine is in critical state
                if result.get("health") == "CRITICAL":
                    logger.warning(f"⚠️ Machine {machine_id} in CRITICAL state!")
                
                # Wait for next cycle
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Error in simulation for machine {machine_id}: {e}")
                await asyncio.sleep(interval)
        
        logger.info(f"✅ Simulation completed for machine {machine_id}")
    
    async def simulate_all_machines(self, interval: float = 1.0):
        """Simulate all machines concurrently"""
        if not self.machines:
            logger.warning("⚠️ No machines to simulate")
            return
        
        logger.info(f"🚀 Starting simulation for {len(self.machines)} machines")
        
        # Create tasks for all machines
        tasks = []
        for machine_id in self.machines.keys():
            task = asyncio.create_task(self.simulate_machine(machine_id, interval))
            tasks.append(task)
        
        # Wait for all simulations to complete
        await asyncio.gather(*tasks)
        
        logger.info("✅ All simulations completed")

class InteractiveSimulator:
    """Interactive simulator for testing and demonstration"""
    
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.simulator = MachineSimulator(self.api_url)
    
    async def run_demo_scenario(self):
        """Run a demonstration scenario with multiple machines"""
        print("🎬 Starting Demo Scenario")
        print("=" * 50)
        
        async with self.simulator:
            # Add multiple machines with different characteristics
            self.simulator.add_machine(1, max_cycles=50, failure_type="gradual")  # Fast gradual failure
            self.simulator.add_machine(2, max_cycles=80, failure_type="sudden")   # Sudden failure
            self.simulator.add_machine(3, max_cycles=100, failure_type="intermittent")  # Intermittent issues
            self.simulator.add_machine(4, max_cycles=120, failure_type="gradual")  # Slow gradual failure
            self.simulator.add_machine(5, max_cycles=90, failure_type="sudden")    # Another sudden failure
            
            print("📊 Added 5 machines with different failure patterns")
            print("   - Machine 1: Gradual failure (50 cycles)")
            print("   - Machine 2: Sudden failure (80 cycles)")
            print("   - Machine 3: Intermittent issues (100 cycles)")
            print("   - Machine 4: Gradual failure (120 cycles)")
            print("   - Machine 5: Sudden failure (90 cycles)")
            
            print("\n🚀 Starting simulations...")
            await self.simulator.simulate_all_machines(interval=0.5)
    
    async def run_single_machine_test(self, machine_id: int = 1, cycles: int = 30):
        """Test a single machine"""
        print(f"🧪 Testing single machine {machine_id} for {cycles} cycles")
        
        async with self.simulator:
            self.simulator.add_machine(machine_id, max_cycles=cycles)
            await self.simulator.simulate_machine(machine_id, interval=1.0)
    
    async def run_continuous_simulation(self, duration_minutes: int = 5):
        """Run continuous simulation for a specified duration"""
        print(f"⏰ Running continuous simulation for {duration_minutes} minutes")
        
        async with self.simulator:
            # Add machines with long lifespans
            self.simulator.add_machine(1, max_cycles=300, failure_type="gradual")
            self.simulator.add_machine(2, max_cycles=400, failure_type="sudden")
            
            # Calculate total cycles needed
            cycles_per_minute = 60  # 1 cycle per second
            total_cycles = duration_minutes * cycles_per_minute
            
            # Update machine max cycles
            for machine_id in self.simulator.machines:
                self.simulator.machines[machine_id]["max_cycles"] = total_cycles
            
            await self.simulator.simulate_all_machines(interval=1.0)

async def main():
    """Main function for running simulator"""
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        simulator = InteractiveSimulator()
        
        if mode == "demo":
            await simulator.run_demo_scenario()
        elif mode == "test":
            cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            await simulator.run_single_machine_test(cycles=cycles)
        elif mode == "continuous":
            minutes = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            await simulator.run_continuous_simulation(duration_minutes=minutes)
        else:
            print("Usage:")
            print("  python simulator.py demo          - Run demo scenario")
            print("  python simulator.py test 30       - Test single machine for 30 cycles")
            print("  python simulator.py continuous 5   - Run continuous for 5 minutes")
    else:
        print("Usage:")
        print("  python simulator.py demo          - Run demo scenario")
        print("  python simulator.py test 30       - Test single machine for 30 cycles")
        print("  python simulator.py continuous 5   - Run continuous for 5 minutes")

if __name__ == "__main__":
    asyncio.run(main())
