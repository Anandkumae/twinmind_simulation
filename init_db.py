"""
Database initialization script for Digital Twin system
"""
import logging
from database import create_tables, test_connection, get_database_info
from services import machine_service
from schemas import MachineCreate
from database import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_machines():
    """Create sample machines for testing"""
    db = SessionLocal()
    try:
        # Check if machines already exist
        existing_machines = machine_service.get_machine_count(db)
        if existing_machines > 0:
            logger.info(f"✅ Found {existing_machines} existing machines, skipping sample data creation")
            return
        
        # Create sample machines
        sample_machines = [
            MachineCreate(
                name="Motor-1",
                location="Plant A - Production Line 1",
                description="Main production motor for assembly line",
                machine_type="motor"
            ),
            MachineCreate(
                name="Motor-2", 
                location="Plant B - Packaging Area",
                description="Packaging system motor",
                machine_type="motor"
            ),
            MachineCreate(
                name="Motor-3",
                location="Plant C - Quality Control",
                description="Quality inspection motor",
                machine_type="motor"
            ),
            MachineCreate(
                name="Pump-1",
                location="Plant A - Cooling System",
                description="Main cooling water pump",
                machine_type="pump"
            ),
            MachineCreate(
                name="Compressor-1",
                location="Plant B - Air Supply",
                description="Industrial air compressor",
                machine_type="compressor"
            )
        ]
        
        created_machines = []
        for machine_data in sample_machines:
            machine = machine_service.create_machine(db, machine_data)
            created_machines.append(machine)
            logger.info(f"✅ Created machine: {machine.name} (ID: {machine.id})")
        
        logger.info(f"🏭 Created {len(created_machines)} sample machines successfully")
        return created_machines
        
    except Exception as e:
        logger.error(f"❌ Error creating sample machines: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_database_setup():
    """Verify database setup and show information"""
    logger.info("🔍 Verifying database setup...")
    
    # Get database info
    info = get_database_info()
    logger.info(f"📊 Database Type: {info['type']}")
    logger.info(f"📊 Connected: {info['connected']}")
    
    if not info['connected']:
        logger.error("❌ Database connection failed!")
        return False
    
    # Test table creation
    try:
        create_tables()
        logger.info("✅ Database tables verified")
        
        # Create sample machines
        create_sample_machines()
        
        logger.info("🎉 Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False

def reset_database():
    """Reset database (use with caution!)"""
    logger.warning("⚠️ Resetting database...")
    
    from database import drop_tables, create_tables
    
    try:
        drop_tables()
        logger.warning("🗑️ Database tables dropped")
        
        create_tables()
        logger.info("✅ Database tables recreated")
        
        create_sample_machines()
        logger.info("🏭 Sample machines recreated")
        
        logger.info("🔄 Database reset completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        return False

def show_database_status():
    """Show current database status"""
    db = SessionLocal()
    try:
        # Get machine count
        machine_count = machine_service.get_machine_count(db)
        
        # Get sensor data count
        from models import SensorData, Prediction, Anomaly
        sensor_count = db.query(SensorData).count()
        prediction_count = db.query(Prediction).count()
        anomaly_count = db.query(Anomaly).count()
        
        logger.info("📊 Database Status:")
        logger.info(f"  Machines: {machine_count}")
        logger.info(f"  Sensor Readings: {sensor_count}")
        logger.info(f"  Predictions: {prediction_count}")
        logger.info(f"  Anomalies: {anomaly_count}")
        
        return {
            "machines": machine_count,
            "sensor_readings": sensor_count,
            "predictions": prediction_count,
            "anomalies": anomaly_count
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting database status: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "init":
            verify_database_setup()
        elif command == "reset":
            reset_database()
        elif command == "status":
            show_database_status()
        else:
            print("Usage: python init_db.py [init|reset|status]")
            print("  init   - Initialize database with sample data")
            print("  reset  - Reset database (WARNING: deletes all data)")
            print("  status - Show database status")
    else:
        # Default: initialize database
        verify_database_setup()
        show_database_status()
