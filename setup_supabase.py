"""
Supabase setup script for Digital Twin system
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if environment is properly configured"""
    logger.info("🔍 Checking environment configuration...")
    
    # Load environment variables
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("❌ DATABASE_URL not found in .env file")
        return False
    
    if database_url.startswith("sqlite"):
        logger.info("📊 Using SQLite database (development mode)")
        return True
    elif database_url.startswith("postgresql"):
        logger.info("🗄️ Using PostgreSQL database (production mode)")
        return True
    else:
        logger.error(f"❌ Unsupported database type: {database_url.split(':')[0]}")
        return False

def install_dependencies():
    """Install required dependencies"""
    logger.info("📦 Installing dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Dependencies installed successfully")
            return True
        else:
            logger.error(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Error installing dependencies: {e}")
        return False

def setup_database():
    """Setup and initialize database"""
    logger.info("🗄️ Setting up database...")
    
    try:
        # Import database modules
        from init_db import verify_database_setup, show_database_status
        
        # Initialize database
        if verify_database_setup():
            # Show status
            show_database_status()
            return True
        else:
            logger.error("❌ Database setup failed")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Failed to import database modules: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Database setup error: {e}")
        return False

def test_api():
    """Test API functionality"""
    logger.info("🔧 Testing API functionality...")
    
    try:
        import requests
        import time
        
        # Start API test
        api_url = "http://localhost:8000"
        
        # Test health endpoint
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ API health check passed")
                logger.info(f"  Status: {data['status']}")
                logger.info(f"  Database: {data['database_connected']}")
                return True
            else:
                logger.error(f"❌ API health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API not responding: {e}")
            logger.info("💡 Please start the API first:")
            logger.info("   python streaming_api_db.py")
            return False
            
    except Exception as e:
        logger.error(f"❌ API test error: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = ".env"
    env_example = ".env.example"
    
    if not os.path.exists(env_file):
        logger.info("📝 Creating .env file...")
        
        if os.path.exists(env_example):
            # Copy from example
            with open(env_example, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            logger.info("✅ .env file created from .env.example")
            logger.info("📝 Please update DATABASE_URL in .env file with your Supabase connection string")
        else:
            # Create basic .env
            basic_env = """# Database Configuration
# Replace with your Supabase connection string
# DATABASE_URL=postgresql://postgres:password@host:5432/postgres

# For development, using SQLite
DATABASE_URL=sqlite:///./digital_twin.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
"""
            with open(env_file, 'w') as f:
                f.write(basic_env)
            
            logger.info("✅ Basic .env file created")
        
        return True
    else:
        logger.info("✅ .env file already exists")
        return True

def show_next_steps():
    """Show next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. 🗄️ If using Supabase:")
    print("   - Update DATABASE_URL in .env with your Supabase connection string")
    print("   - Run: python init_db.py init")
    print("\n2. 🚀 Start the API:")
    print("   python streaming_api_db.py")
    print("\n3. 🧪 Run the demo:")
    print("   python streaming_demo_db.py")
    print("\n4. 🌐 Access the dashboard:")
    print("   http://localhost:8000/dashboard")
    print("\n5. 📊 Check API health:")
    print("   http://localhost:8000/health")
    print("\n📖 For more information, see USAGE.md")

def main():
    """Main setup function"""
    print("🚀 Digital Twin Supabase Setup")
    print("=" * 40)
    
    # Step 1: Create .env file
    print("\n📝 Step 1: Setting up environment...")
    if not create_env_file():
        print("❌ Failed to create .env file")
        return False
    
    # Step 2: Check environment
    print("\n🔍 Step 2: Checking environment...")
    if not check_environment():
        print("❌ Environment check failed")
        return False
    
    # Step 3: Install dependencies
    print("\n📦 Step 3: Installing dependencies...")
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
    # Step 4: Setup database
    print("\n🗄️ Step 4: Setting up database...")
    if not setup_database():
        print("❌ Database setup failed")
        return False
    
    # Step 5: Test API (optional)
    print("\n🔧 Step 5: Testing API (optional)...")
    test_api()  # Don't fail if API is not running
    
    # Show next steps
    show_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        sys.exit(1)
