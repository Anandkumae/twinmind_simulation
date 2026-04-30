# 🚀 TwinMind Digital Twin - Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Deployment](#local-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Production Configuration](#production-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### **System Requirements**
- **CPU**: 2+ cores (4+ recommended)
- **Memory**: 4GB RAM minimum (8GB+ recommended)
- **Storage**: 10GB free space (50GB+ for production)
- **Network**: HTTP/HTTPS and WebSocket support
- **Python**: 3.8+ (3.9+ recommended)

### **Software Dependencies**
- Docker & Docker Compose (for containerized deployment)
- Git (for version control)
- curl or wget (for health checks)
- SSL certificates (for HTTPS in production)

## 💻 Local Deployment

### **Option 1: Quick Start**
```bash
# Clone the repository
git clone <repository-url>
cd Digital_twin

# Install dependencies
pip install -r requirements.txt

# Start the system
python streaming_demo.py demo

# Access dashboard
# http://localhost:8000/dashboard
```

### **Option 2: Development Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python streaming_api.py
python simulator.py

# Access API
# http://localhost:8000/health
```

### **Option 3: Production Mode**
```bash
# Set environment variables
export API_HOST=0.0.0.0
export API_PORT=8000
export LOG_LEVEL=INFO
export MAX_MACHINES=50

# Start production server
python -m uvicorn streaming_api:app --host 0.0.0.0 --port 8000 --workers 4

# Run simulator separately
python simulator.py
```

## 🐳 Docker Deployment

### **Build Docker Image**
```bash
# Build the image
docker build -t digital-twin:latest .

# Run the container
docker run -d \
  --name digital-twin \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  digital-twin:latest
```

### **Docker Compose Deployment**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f digital-twin

# Stop services
docker-compose down
```

### **Production Docker Compose**
```bash
# Start with production profile
docker-compose --profile production up -d

# Start with database
docker-compose --profile database up -d

# Start with caching
docker-compose --profile cache up -d

# Full production stack
docker-compose --profile production --profile database --profile cache up -d
```

### **Docker Configuration Files**

#### **Dockerfile (Production Optimized)**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 digitaltwin
USER digitaltwin

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "streaming_demo.py", "demo"]
```

#### **docker-compose.yml (Production)**
```yaml
version: '3.8'

services:
  digital-twin:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
      - MAX_MACHINES=100
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./models:/app/models
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - digital-twin
    restart: unless-stopped

  postgres:
    image: postgres:13-alpine
    environment:
      - POSTGRES_DB=digital_twin
      - POSTGRES_USER=digitaltwin
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## ☁️ Cloud Deployment

### **AWS Deployment**

#### **EC2 Instance Setup**
```bash
# Launch EC2 instance (t3.medium or larger)
# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Clone repository
git clone <repository-url>
cd Digital_twin

# Deploy with Docker Compose
docker-compose up -d
```

#### **Elastic Beanstalk**
```bash
# Create Dockerfile (already included)
# Create .ebextensions/config.config
# Deploy with EB CLI
eb init digital-twin --platform "Docker running on 64bit Amazon Linux 2"
eb create digital-twin-env
eb deploy
```

#### **ECS (Elastic Container Service)**
```json
{
  "family": "digital-twin",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "digital-twin",
      "image": "your-account.dkr.ecr.region.amazonaws.com/digital-twin:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "API_HOST",
          "value": "0.0.0.0"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/digital-twin",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### **Google Cloud Platform**

#### **Cloud Run Deployment**
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/digital-twin

# Deploy to Cloud Run
gcloud run deploy digital-twin \
  --image gcr.io/PROJECT_ID/digital-twin \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 1
```

#### **GKE (Google Kubernetes Engine)**
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: digital-twin
spec:
  replicas: 3
  selector:
    matchLabels:
      app: digital-twin
  template:
    metadata:
      labels:
        app: digital-twin
    spec:
      containers:
      - name: digital-twin
        image: gcr.io/PROJECT_ID/digital-twin:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_HOST
          value: "0.0.0.0"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: digital-twin-service
spec:
  selector:
    app: digital-twin
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### **Microsoft Azure**

#### **Azure Container Instances**
```bash
# Create resource group
az group create digital-twin-rg --location eastus

# Deploy container
az container create \
  --resource-group digital-twin-rg \
  --name digital-twin \
  --image your-registry/digital-twin:latest \
  --cpu 1 \
  --memory 2 \
  --ports 8000 \
  --environment-variables API_HOST=0.0.0.0
```

#### **Azure Kubernetes Service (AKS)**
```bash
# Create AKS cluster
az aks create \
  --resource-group digital-twin-rg \
  --name digital-twin-aks \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Deploy application
kubectl apply -f k8s-deployment.yaml
```

## ⚙️ Production Configuration

### **Environment Variables**
```bash
# Core Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
MAX_MACHINES=100

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://yourdomain.com
API_KEY_HEADER=X-API-Key

# Database (if using)
DATABASE_URL=postgresql://user:password@localhost:5432/digital_twin
REDIS_URL=redis://localhost:6379/0

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_URL=https://your-grafana-instance.com
SENTRY_DSN=your-sentry-dsn

# Performance
WORKERS=4
MAX_CONNECTIONS=1000
CONNECTION_TIMEOUT=30
```

### **Nginx Configuration**
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream digital_twin {
        server digital-twin:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://digital_twin;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ws {
            proxy_pass http://digital_twin;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
```

### **Systemd Service**
```ini
# /etc/systemd/system/digital-twin.service
[Unit]
Description=Digital Twin Service
After=network.target

[Service]
Type=simple
User=digitaltwin
Group=digitaltwin
WorkingDirectory=/opt/digital-twin
Environment=PATH=/opt/digital-twin/venv/bin
ExecStart=/opt/digital-twin/venv/bin/python streaming_demo.py demo
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable digital-twin
sudo systemctl start digital-twin
sudo systemctl status digital-twin
```

## 📊 Monitoring & Maintenance

### **Health Checks**
```bash
# API Health
curl http://localhost:8000/health

# WebSocket Health
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: test" \
     -H "Sec-WebSocket-Version: 13" \
     http://localhost:8000/ws

# System Resources
docker stats digital-twin
```

### **Logging Configuration**
```python
# logging_config.py
import logging
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(funcName)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/digital-twin.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        'uvicorn': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### **Performance Monitoring**
```python
# monitoring.py
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active WebSocket connections')
SYSTEM_MEMORY = Gauge('system_memory_bytes', 'System memory usage')
SYSTEM_CPU = Gauge('system_cpu_percent', 'System CPU usage')

def update_system_metrics():
    """Update system metrics"""
    SYSTEM_MEMORY.set(psutil.virtual_memory().used)
    SYSTEM_CPU.set(psutil.cpu_percent())

# Start metrics server
start_http_server(8001)
```

### **Backup Strategy**
```bash
#!/bin/bash
# backup.sh

# Configuration
BACKUP_DIR="/backups/digital-twin"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="digital-twin_backup_${DATE}.tar.gz"

# Create backup
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    /opt/digital-twin/data \
    /opt/digital-twin/models \
    /opt/digital-twin/logs \
    /opt/digital-twin/config

# Upload to cloud storage (example with AWS S3)
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" "s3://your-backup-bucket/"

# Clean old backups (keep last 30 days)
find "${BACKUP_DIR}" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}"
```

### **Automated Updates**
```bash
#!/bin/bash
# update.sh

# Pull latest changes
git pull origin main

# Backup current data
./backup.sh

# Update dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart digital-twin

# Verify health
sleep 10
curl -f http://localhost:8000/health || {
    echo "Health check failed, rolling back..."
    sudo systemctl restart digital-twin
    exit 1
}

echo "Update completed successfully"
```

## 🔧 Troubleshooting

### **Common Issues**

#### **Container Won't Start**
```bash
# Check logs
docker logs digital-twin

# Check resource usage
docker stats

# Rebuild image
docker-compose build --no-cache
```

#### **WebSocket Connection Issues**
```bash
# Check WebSocket endpoint
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     http://localhost:8000/ws

# Check firewall settings
sudo ufw status
sudo ufw allow 8000
```

#### **High Memory Usage**
```bash
# Check memory usage
docker stats digital-twin

# Monitor Python process
ps aux | grep python

# Restart if needed
docker-compose restart digital-twin
```

#### **Database Connection Issues**
```bash
# Check database status
docker-compose logs postgres

# Test connection
psql -h localhost -U digitaltwin -d digital_twin

# Reset database if needed
docker-compose down postgres
docker volume rm digital-twin_postgres_data
docker-compose up -d postgres
```

### **Performance Optimization**

#### **Database Optimization**
```sql
-- Create indexes for better performance
CREATE INDEX idx_machine_id ON sensor_data(machine_id);
CREATE INDEX idx_timestamp ON sensor_data(timestamp);
CREATE INDEX idx_health_status ON machines(health);

-- Optimize queries
EXPLAIN ANALYZE SELECT * FROM machines WHERE health = 'CRITICAL';
```

#### **Caching Strategy**
```python
# cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=300):
    """Cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=300)
def get_machine_status(machine_id):
    """Get machine status with caching"""
    # Implementation here
    pass
```

### **Security Hardening**

#### **SSL/TLS Configuration**
```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Configure Nginx for HTTPS
# See nginx.conf example above
```

#### **API Security**
```python
# security.py
from fastapi import HTTPException, Depends
from fastapi.security import APIKeyHeader

API_KEY = "your-secret-api-key"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Protect endpoints
@app.post("/sensor-data", dependencies=[Depends(verify_api_key)])
async def protected_endpoint():
    pass
```

---

## 📞 Support

For deployment support:
- 📧 Email: support@digitaltwin.ai
- 📖 Documentation: [Full docs](https://docs.digitaltwin.ai)
- 🐛 Issues: [GitHub Issues](https://github.com/yourrepo/issues)
- 💬 Discord: [Community support](https://discord.gg/digitaltwin)

**Happy deploying!** 🚀✨
