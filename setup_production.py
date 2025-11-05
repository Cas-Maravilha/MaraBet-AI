#!/usr/bin/env python3
"""
Script de Configuração Automática de Produção
Configura automaticamente o sistema para produção
"""

import os
import secrets
import shutil
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionSetup:
    """Configurador automático de produção"""
    
    def __init__(self):
        """Inicializa configurador"""
        self.secret_key = secrets.token_urlsafe(32)
        self.setup_directories()
    
    def setup_directories(self):
        """Cria diretórios necessários"""
        directories = [
            'logs',
            'ssl',
            'data',
            'backups',
            'monitoring/grafana/dashboards',
            'monitoring/grafana/datasources',
            'nginx'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Diretório criado: {directory}")
    
    def generate_secret_key(self):
        """Gera SECRET_KEY seguro"""
        return self.secret_key
    
    def create_production_env(self):
        """Cria arquivo .env de produção"""
        env_content = f"""# Configurações de Produção do MaraBet AI
# ⚠️ IMPORTANTE: Configure todas as variáveis antes de usar em produção!

# ==================== SEGURANÇA ====================
# SECRET_KEY gerado automaticamente
SECRET_KEY={self.secret_key}

# Debug - SEMPRE False em produção
DEBUG=False

# Hosts permitidos (separados por vírgula)
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# ==================== HTTPS/SSL ====================
# Caminhos dos certificados SSL
SSL_CERT_PATH=ssl/cert.pem
SSL_KEY_PATH=ssl/key.pem

# ==================== RATE LIMITING ====================
# Redis para rate limiting
REDIS_URL=redis://localhost:6379

# ==================== BANCO DE DADOS ====================
DATABASE_URL=sqlite:///mara_bet.db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30

# ==================== CACHE ====================
CACHE_TIMEOUT=300

# ==================== LOGGING ====================
LOG_LEVEL=INFO
LOG_FILE=logs/mara_bet_production.log

# ==================== API CONFIGURATION ====================
# Configurações da API (opcional - para dados premium)
API_FOOTBALL_KEY=747d6e19a2d3a435fdb7a419007a45fa
THE_ODDS_API_KEY=your_the_odds_api_key_here

# Timeouts
API_TIMEOUT=30
API_RETRY_ATTEMPTS=3

# ==================== NOTIFICAÇÕES ====================
# Telegram - Bot: @MaraBetAIBot
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597

# Email - Yahoo
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=kilamu_10@yahoo.com.br
SMTP_PASSWORD=your_yahoo_app_password_here
NOTIFICATION_EMAIL=kilamu_10@yahoo.com.br
ADMIN_EMAIL=kilamu_10@yahoo.com.br

# ==================== MONITORAMENTO ====================
# Sentry para monitoramento de erros
SENTRY_DSN=your_sentry_dsn_here

# Prometheus para métricas
PROMETHEUS_PORT=9090

# ==================== PERFORMANCE ====================
# Workers
WORKERS=4

# Threads
THREADS=2

# Timeout
TIMEOUT=120

# ==================== DOCKER ====================
# Senhas para Docker Compose
POSTGRES_PASSWORD=marabet_secure_password_123
REDIS_PASSWORD=redis_secure_password_123
GRAFANA_PASSWORD=grafana_admin_123
"""
        
        with open('.env.production', 'w') as f:
            f.write(env_content)
        
        logger.info("✅ Arquivo .env.production criado")
    
    def generate_ssl_certificate(self):
        """Gera certificado SSL auto-assinado"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from datetime import datetime, timedelta
            
            # Gerar chave privada
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Criar certificado
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "São Paulo"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "São Paulo"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MaraBet AI"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("127.0.0.1"),
                    x509.IPAddress("127.0.0.1"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Salvar certificado
            cert_path = Path('ssl/cert.pem')
            with open(cert_path, 'wb') as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Salvar chave privada
            key_path = Path('ssl/key.pem')
            with open(key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info("✅ Certificado SSL auto-assinado gerado")
            logger.info(f"   Certificado: {cert_path}")
            logger.info(f"   Chave: {key_path}")
            logger.info("   ⚠️ Use apenas para desenvolvimento!")
            
            return True
            
        except ImportError:
            logger.warning("cryptography não instalado. Execute: pip install cryptography")
            return False
        except Exception as e:
            logger.error(f"Erro ao gerar certificado: {e}")
            return False
    
    def create_nginx_config(self):
        """Cria configuração do Nginx"""
        nginx_config = """events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    # Upstream
    upstream marabet_app {
        server marabet-app:5000;
    }
    
    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }
    
    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name _;
        
        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=63072000" always;
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        
        # Proxy to application
        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://marabet_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check
        location /health {
            proxy_pass http://marabet_app;
            access_log off;
        }
        
        # Static files
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
"""
        
        with open('nginx/nginx.conf', 'w') as f:
            f.write(nginx_config)
        
        logger.info("✅ Configuração do Nginx criada")
    
    def create_monitoring_configs(self):
        """Cria configurações de monitoramento"""
        # Prometheus config
        prometheus_config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'marabet-app'
    static_configs:
      - targets: ['marabet-app:9090']
    scrape_interval: 5s
    metrics_path: '/metrics'
    
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
"""
        
        with open('monitoring/prometheus.yml', 'w') as f:
            f.write(prometheus_config)
        
        # Grafana datasource
        grafana_datasource = """apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
"""
        
        with open('monitoring/grafana/datasources/prometheus.yml', 'w') as f:
            f.write(grafana_datasource)
        
        logger.info("✅ Configurações de monitoramento criadas")
    
    def create_startup_script(self):
        """Cria script de inicialização"""
        startup_script = """#!/bin/bash
# Script de inicialização do MaraBet AI

echo "🚀 Iniciando MaraBet AI..."

# Verificar se Redis está rodando
echo "🔴 Verificando Redis..."
while ! redis-cli ping > /dev/null 2>&1; do
    echo "   Aguardando Redis..."
    sleep 2
done
echo "✅ Redis conectado"

# Verificar se banco de dados está acessível
echo "🗄️ Verificando banco de dados..."
python -c "import sqlite3; sqlite3.connect('mara_bet.db')"
echo "✅ Banco de dados acessível"

# Executar migrações se necessário
echo "📊 Executando migrações..."
python -c "from database import init_db; init_db()"
echo "✅ Migrações executadas"

# Iniciar aplicação
echo "🎉 Iniciando aplicação..."
exec python run_automated_collector.py
"""
        
        with open('start.sh', 'w') as f:
            f.write(startup_script)
        
        # Tornar executável
        os.chmod('start.sh', 0o755)
        
        logger.info("✅ Script de inicialização criado")
    
    def run_setup(self):
        """Executa configuração completa"""
        print("🔮 MARABET AI - CONFIGURAÇÃO AUTOMÁTICA DE PRODUÇÃO")
        print("=" * 60)
        
        logger.info("🚀 Iniciando configuração automática...")
        
        # Executar configurações
        self.create_production_env()
        self.generate_ssl_certificate()
        self.create_nginx_config()
        self.create_monitoring_configs()
        self.create_startup_script()
        
        print("\n✅ CONFIGURAÇÃO CONCLUÍDA!")
        print("=" * 40)
        print(f"SECRET_KEY gerado: {self.secret_key}")
        print("Arquivos criados:")
        print("  - .env.production")
        print("  - ssl/cert.pem")
        print("  - ssl/key.pem")
        print("  - nginx/nginx.conf")
        print("  - monitoring/prometheus.yml")
        print("  - monitoring/grafana/datasources/prometheus.yml")
        print("  - start.sh")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. Configure suas credenciais no arquivo .env.production")
        print("2. Execute: docker-compose -f docker-compose.production.yml up -d")
        print("3. Acesse: https://localhost")
        print("4. Monitoramento: http://localhost:3000 (Grafana)")
        
        print("\n⚠️ IMPORTANTE:")
        print("- Configure certificados SSL válidos para produção")
        print("- Configure senhas seguras no docker-compose")
        print("- Configure domínio real em ALLOWED_HOSTS")
        print("- Configure Sentry para monitoramento de erros")

def main():
    """Função principal"""
    setup = ProductionSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()
