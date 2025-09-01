#!/usr/bin/env python3
"""
Production Environment Setup Script
Configures the ZeroDev AI application for production deployment
"""

import os
import sys
import secrets
import base64
import pyotp
from pathlib import Path
import subprocess
import shutil

class ProductionSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_path = self.project_root / "backend"
        self.frontend_path = self.project_root / "frontend"
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        import time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def generate_secure_key(self, length: int = 32) -> str:
        """Generate a secure random key"""
        return base64.urlsafe_b64encode(os.urandom(length)).decode('utf-8')
        
    def generate_jwt_secret(self) -> str:
        """Generate JWT secret key"""
        return secrets.token_urlsafe(64)
        
    def generate_totp_secret(self) -> str:
        """Generate TOTP secret for 2FA"""
        return pyotp.random_base32()
        
    def create_production_env(self):
        """Create production environment file"""
        self.log("Creating production environment configuration...")
        
        env_path = self.backend_path / ".env"
        env_example_path = self.backend_path / ".env.example"
        
        if env_path.exists():
            backup_path = self.backend_path / f".env.backup.{int(time.time())}"
            shutil.copy(env_path, backup_path)
            self.log(f"Backed up existing .env to {backup_path}")
        
        # Generate secure keys
        jwt_secret = self.generate_jwt_secret()
        encryption_key = self.generate_secure_key()
        emergency_key = self.generate_secure_key()
        totp_secret = self.generate_totp_secret()
        
        # Create production environment
        env_content = f"""# Production Environment Configuration
# Generated on {time.strftime("%Y-%m-%d %H:%M:%S")}

# Environment
ENVIRONMENT=production
DEBUG=False

# Database Configuration (Update with your production database)
POSTGRES_SERVER=your-production-db-host
POSTGRES_USER=your-db-user
POSTGRES_PASSWORD=your-secure-db-password
POSTGRES_DB=zerodev_prod

# Redis Configuration (Update with your production Redis)
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_DB=0

# Security Keys (DO NOT SHARE THESE)
JWT_SECRET={jwt_secret}
ENCRYPTION_KEY={encryption_key}
OWNER_EMERGENCY_KEY={emergency_key}
ADMIN_TOTP_SECRET={totp_secret}

# API Keys (Add your production API keys)
OPENAI_API_KEY=your-openai-api-key

# Vault Configuration (for production secrets management)
VAULT_ADDR=https://your-vault-server:8200
VAULT_TOKEN=your-vault-token

# Optional: Additional production settings
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
"""
        
        with open(env_path, 'w') as f:
            f.write(env_content)
            
        # Set secure permissions
        os.chmod(env_path, 0o600)
        
        self.log(f"✅ Production environment created at {env_path}")
        self.log(f"🔐 TOTP Secret for 2FA: {totp_secret}")
        self.log("⚠️  Please update database and Redis URLs in the .env file")
        
    def optimize_docker_config(self):
        """Create optimized Docker configuration for production"""
        self.log("Creating production Docker configuration...")
        
        # Production docker-compose override
        docker_prod_content = """version: '3.8'

services:
  backend:
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  db:
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=zerodev_prod
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    restart: unless-stopped
    volumes:
      - redis_data:/data
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  celery-worker:
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  celery-beat:
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
"""
        
        docker_prod_path = self.project_root / "docker-compose.prod.yml"
        with open(docker_prod_path, 'w') as f:
            f.write(docker_prod_content)
            
        self.log(f"✅ Production Docker config created at {docker_prod_path}")
        
    def create_nginx_config(self):
        """Create Nginx configuration for production"""
        self.log("Creating Nginx configuration...")
        
        nginx_content = """# Nginx configuration for ZeroDev AI Production
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL configuration (update paths to your certificates)
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'";
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
    
    # Frontend routes
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Backend API routes
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Authentication endpoints (more restrictive rate limiting)
    location /auth/ {
        limit_req zone=auth burst=5 nodelay;
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files caching
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"""
        
        nginx_path = self.project_root / "nginx" / "nginx.conf"
        nginx_path.parent.mkdir(exist_ok=True)
        
        with open(nginx_path, 'w') as f:
            f.write(nginx_content)
            
        self.log(f"✅ Nginx configuration created at {nginx_path}")
        
    def create_systemd_services(self):
        """Create systemd service files for production"""
        self.log("Creating systemd service files...")
        
        service_content = f"""[Unit]
Description=ZeroDev AI Application
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory={self.project_root}
ExecStart=/usr/bin/docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
"""
        
        service_path = self.project_root / "scripts" / "zerodev-ai.service"
        with open(service_path, 'w') as f:
            f.write(service_content)
            
        self.log(f"✅ Systemd service created at {service_path}")
        self.log("To install: sudo cp scripts/zerodev-ai.service /etc/systemd/system/")
        self.log("Then run: sudo systemctl enable zerodev-ai && sudo systemctl start zerodev-ai")
        
    def create_backup_script(self):
        """Create automated backup script"""
        self.log("Creating backup script...")
        
        backup_script = f"""#!/bin/bash
# ZeroDev AI Automated Backup Script

BACKUP_DIR="/backup/zerodev-ai"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_ROOT="{self.project_root}"

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Backup database
docker-compose exec -T db pg_dump -U user zerodev_prod | gzip > $BACKUP_DIR/$DATE/database_$DATE.sql.gz

# Backup Redis data
docker-compose exec -T redis redis-cli --rdb /data/dump.rdb
docker cp $(docker-compose ps -q redis):/data/dump.rdb $BACKUP_DIR/$DATE/redis_$DATE.rdb

# Backup application files (excluding node_modules, __pycache__, etc.)
tar --exclude='node_modules' --exclude='__pycache__' --exclude='.git' --exclude='*.log' \\
    -czf $BACKUP_DIR/$DATE/app_files_$DATE.tar.gz -C $PROJECT_ROOT .

# Backup environment files (encrypted)
gpg --symmetric --cipher-algo AES256 --output $BACKUP_DIR/$DATE/env_$DATE.gpg $PROJECT_ROOT/backend/.env

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {{}} +

echo "Backup completed: $BACKUP_DIR/$DATE"
"""
        
        backup_path = self.project_root / "scripts" / "backup.sh"
        with open(backup_path, 'w') as f:
            f.write(backup_script)
            
        os.chmod(backup_path, 0o755)
        
        self.log(f"✅ Backup script created at {backup_path}")
        
    def create_monitoring_config(self):
        """Create monitoring and logging configuration"""
        self.log("Creating monitoring configuration...")
        
        # Create Prometheus configuration
        prometheus_content = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'zerodev-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'zerodev-frontend'
    static_configs:
      - targets: ['frontend:3000']
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['db:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
"""
        
        monitoring_path = self.project_root / "monitoring"
        monitoring_path.mkdir(exist_ok=True)
        
        with open(monitoring_path / "prometheus.yml", 'w') as f:
            f.write(prometheus_content)
            
        # Create logging configuration
        logging_content = """version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  json:
    format: '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: INFO
    formatter: json
    filename: /app/logs/application.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: json
    filename: /app/logs/error.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  backend:
    level: INFO
    handlers: [console, file, error_file]
    propagate: false

  uvicorn:
    level: INFO
    handlers: [console, file]
    propagate: false

  fastapi:
    level: INFO
    handlers: [console, file]
    propagate: false

root:
  level: INFO
  handlers: [console, file]
"""
        
        with open(monitoring_path / "logging.yml", 'w') as f:
            f.write(logging_content)
            
        self.log(f"✅ Monitoring configuration created at {monitoring_path}")
        
    def run_setup(self):
        """Run complete production setup"""
        self.log("🚀 Starting ZeroDev AI Production Setup")
        
        try:
            import time
            self.create_production_env()
            self.optimize_docker_config()
            self.create_nginx_config()
            self.create_systemd_services()
            self.create_backup_script()
            self.create_monitoring_config()
            
            self.log("✅ Production setup complete!")
            self.log("📋 Next steps:")
            self.log("   1. Update database and Redis URLs in backend/.env")
            self.log("   2. Add your API keys to backend/.env")
            self.log("   3. Update domain names in nginx/nginx.conf")
            self.log("   4. Install SSL certificates")
            self.log("   5. Deploy using: docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d")
            
        except Exception as e:
            self.log(f"❌ Setup failed: {e}", "ERROR")
            return False
            
        return True

def main():
    """Main entry point"""
    setup = ProductionSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
