#!/usr/bin/env python3
"""
🚀 Streaming RUL Prediction Demo
================================

This script demonstrates the complete real-time RUL prediction system:
1. Starts the FastAPI backend with WebSocket support
2. Runs realistic machine simulations
3. Shows real-time predictions and health monitoring

Usage:
    python streaming_demo.py demo          - Run full demo with 3 machines
    python streaming_demo.py test         - Test single machine
    python streaming_demo.py api-only      - Start API only
    python streaming_demo.py simulate-only - Run simulator only
"""

import asyncio
import subprocess
import sys
import time
import signal
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StreamingDemo:
    """Manages the complete streaming demo system"""
    
    def __init__(self):
        self.api_process = None
        self.demo_running = False
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        logger.info("🛑 Shutting down demo...")
        self.stop_demo()
        sys.exit(0)
    
    def start_api_server(self):
        """Start the FastAPI server"""
        logger.info("🚀 Starting FastAPI server...")
        
        try:
            # Start the streaming API server
            self.api_process = subprocess.Popen([
                sys.executable, "streaming_api.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            logger.info("✅ API server started on http://localhost:8000")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start API server: {e}")
            return False
    
    def stop_api_server(self):
        """Stop the FastAPI server"""
        if self.api_process:
            logger.info("🛑 Stopping API server...")
            self.api_process.terminate()
            self.api_process.wait()
            self.api_process = None
            logger.info("✅ API server stopped")
    
    async def run_demo(self):
        """Run the complete demo with multiple machines"""
        logger.info("🎬 Starting Complete Demo")
        logger.info("=" * 50)
        
        # Start API server
        if not self.start_api_server():
            return
        
        # Wait for API server to start
        logger.info("⏳ Waiting for API server to initialize...")
        await asyncio.sleep(3)
        
        try:
            # Import and run simulator
            from simulator import InteractiveSimulator
            
            simulator = InteractiveSimulator()
            
            # Run demo scenario
            await simulator.run_demo_scenario()
            
        except Exception as e:
            logger.error(f"❌ Demo error: {e}")
        
        finally:
            self.stop_demo()
    
    async def run_test(self):
        """Run single machine test"""
        logger.info("🧪 Running Single Machine Test")
        
        # Start API server
        if not self.start_api_server():
            return
        
        # Wait for API server to start
        await asyncio.sleep(3)
        
        try:
            from simulator import InteractiveSimulator
            
            simulator = InteractiveSimulator()
            await simulator.run_single_machine_test(machine_id=1, cycles=30)
            
        except Exception as e:
            logger.error(f"❌ Test error: {e}")
        
        finally:
            self.stop_demo()
    
    def run_api_only(self):
        """Start only the API server"""
        logger.info("🔧 Starting API Server Only")
        logger.info("📊 Dashboard available at: http://localhost:8000/dashboard.html")
        logger.info("📡 WebSocket endpoint: ws://localhost:8000/ws")
        logger.info("📖 API docs: http://localhost:8000/docs")
        
        if not self.start_api_server():
            return
        
        try:
            # Keep API server running and show logs
            for line in iter(self.api_process.stdout.readline, ''):
                if line.strip():
                    print(f"API: {line.strip()}")
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_demo()
    
    async def run_simulator_only(self):
        """Run simulator only (API must be running separately)"""
        logger.info("🤖 Running Simulator Only")
        logger.info("⚠️ Make sure API server is running on http://localhost:8000")
        
        try:
            from simulator import InteractiveSimulator
            
            simulator = InteractiveSimulator()
            await simulator.run_demo_scenario()
            
        except Exception as e:
            logger.error(f"❌ Simulator error: {e}")
    
    def stop_demo(self):
        """Stop all demo components"""
        logger.info("🛑 Stopping demo...")
        self.stop_api_server()
        self.demo_running = False
        logger.info("✅ Demo stopped")

def print_usage():
    """Print usage instructions"""
    print("🚀 Streaming RUL Prediction Demo")
    print("=" * 40)
    print("Usage:")
    print("  python streaming_demo.py demo          - Full demo with 3 machines")
    print("  python streaming_demo.py test         - Test single machine (30 cycles)")
    print("  python streaming_demo.py api-only      - Start API server only")
    print("  python streaming_demo.py simulate-only - Run simulator only")
    print("")
    print("📊 Access Points:")
    print("  🌐 Dashboard: http://localhost:8000/dashboard.html")
    print("  📚 API Docs: http://localhost:8000/docs")
    print("  🔌 WebSocket: ws://localhost:8000/ws")
    print("")
    print("🎮 Manual Testing:")
    print("  curl -X POST http://localhost:8000/simulate/1?cycles=30")
    print("  curl -X GET http://localhost:8000/machines")
    print("  curl -X POST http://localhost:8000/sensor-data -d '{\"machine_id\":1,\"temperature\":100.0}'")

async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    mode = sys.argv[1]
    demo = StreamingDemo()
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, demo.signal_handler)
    signal.signal(signal.SIGTERM, demo.signal_handler)
    
    try:
        if mode == "demo":
            await demo.run_demo()
        elif mode == "test":
            await demo.run_test()
        elif mode == "api-only":
            demo.run_api_only()
        elif mode == "simulate-only":
            await demo.run_simulator_only()
        else:
            print(f"❌ Unknown mode: {mode}")
            print_usage()
    
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
    except Exception as e:
        logger.error(f"❌ Demo error: {e}")
    finally:
        demo.stop_demo()

if __name__ == "__main__":
    # Check if required files exist
    required_files = [
        "streaming_api.py",
        "simulator.py", 
        "ml.py",
        "lstm_rul_model.h5",
        "scaler.pkl"
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print("❌ Missing required files:")
        for f in missing_files:
            print(f"   - {f}")
        print("\n💡 Make sure you've run the training first:")
        print("   python rul_prediction.py")
        sys.exit(1)
    
    print("✅ All required files found")
    print()
    
    # Run the demo
    asyncio.run(main())
