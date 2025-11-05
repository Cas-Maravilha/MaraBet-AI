#!/usr/bin/env python3
"""
Script para Atualizar .env.production - MaraBet AI
Atualiza o arquivo .env.production com os endpoints reais do RDS e Redis
"""

import subprocess
import os
import json
from datetime import datetime

def run_command(command, shell=True):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ Erro no comando: {command}")
            print(f"Erro: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Exceção no comando: {command}")
        print(f"Erro: {e}")
        return None

def update_env_production():
    """Atualiza o arquivo .env.production com os endpoints reais"""
    print("🔧 MARABET AI - ATUALIZANDO .ENV.PRODUCTION")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configuração existente
    try:
        with open('aws_infrastructure_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de configuração não encontrado")
        return False
    
    ubuntu_public_ip = config.get('ubuntu_public_ip')
    rds_endpoint = config.get('rds_endpoint')
    redis_endpoint = config.get('redis_endpoint')
    key_path = os.path.expanduser("~/.ssh/marabet-key.pem")
    
    if not all([ubuntu_public_ip, rds_endpoint, redis_endpoint]):
        print("❌ Endpoints do RDS ou Redis não encontrados na configuração")
        return False
    
    print(f"✅ IP Público: {ubuntu_public_ip}")
    print(f"✅ RDS Endpoint: {rds_endpoint}")
    print(f"✅ Redis Endpoint: {redis_endpoint}")
    print(f"✅ Chave SSH: {key_path}")
    
    print("\n🔧 ETAPA 1: CRIANDO ARQUIVO .ENV.PRODUCTION ATUALIZADO")
    print("-" * 50)
    
    # Criar conteúdo do .env.production com endpoints reais
    env_content = f"""# Configurações de Produção - MaraBet AI
# Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

# Database Configuration
DATABASE_URL=postgresql://marabetadmin:MaraBet2024!SuperSecret@{rds_endpoint}:5432/postgres

# Redis Configuration
REDIS_URL=redis://{redis_endpoint}:6379/0

# API Keys
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Security
SECRET_KEY=MaraBet2024!SuperSecretKey

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Application Settings
APP_NAME=MaraBet AI
APP_VERSION=1.0.0
APP_HOST=0.0.0.0
APP_PORT=8000

# Database Settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Redis Settings
REDIS_POOL_SIZE=10
REDIS_TIMEOUT=5
REDIS_RETRY_ON_TIMEOUT=true

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090

# Logging
LOG_FILE=/var/log/marabet/app.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5

# CORS Settings
CORS_ORIGINS=*
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=*

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Cache Settings
CACHE_TTL=300
CACHE_MAX_SIZE=1000

# Prediction Settings
PREDICTION_CACHE_TTL=600
PREDICTION_BATCH_SIZE=10
PREDICTION_TIMEOUT=30

# Notification Settings
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
NOTIFICATION_ENABLED=true

# Backup Settings
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30

# Health Check Settings
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10

# Performance Settings
WORKER_PROCESSES=4
WORKER_THREADS=2
WORKER_CONNECTIONS=1000

# Security Settings
JWT_SECRET_KEY=MaraBet2024!JWTSecretKey
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# SSL Settings (para produção com domínio)
SSL_ENABLED=false
SSL_CERT_PATH=/etc/ssl/certs/marabet.crt
SSL_KEY_PATH=/etc/ssl/private/marabet.key

# Load Balancer Settings
LOAD_BALANCER_ENABLED=false
LOAD_BALANCER_HEALTH_CHECK_PATH=/health
LOAD_BALANCER_TIMEOUT=30

# Auto Scaling Settings
AUTO_SCALING_ENABLED=false
AUTO_SCALING_MIN_INSTANCES=1
AUTO_SCALING_MAX_INSTANCES=5
AUTO_SCALING_TARGET_CPU=70

# Monitoring and Alerting
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
ALERT_MANAGER_ENABLED=true

# Log Aggregation
ELASTICSEARCH_ENABLED=false
ELASTICSEARCH_URL=http://localhost:9200
KIBANA_ENABLED=false

# Message Queue
CELERY_BROKER_URL=redis://{redis_endpoint}:6379/1
CELERY_RESULT_BACKEND=redis://{redis_endpoint}:6379/2
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_ACCEPT_CONTENT=json
CELERY_TIMEZONE=UTC
CELERY_ENABLE_UTC=true

# Email Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_TLS=true

# File Storage
STORAGE_TYPE=local
STORAGE_PATH=/var/lib/marabet/storage
MAX_FILE_SIZE=10MB
ALLOWED_EXTENSIONS=txt,pdf,png,jpg,jpeg,gif

# API Rate Limiting
API_RATE_LIMIT=1000
API_RATE_LIMIT_WINDOW=3600
API_RATE_LIMIT_PER_IP=100

# WebSocket Settings
WEBSOCKET_ENABLED=true
WEBSOCKET_PORT=8001
WEBSOCKET_PING_INTERVAL=30
WEBSOCKET_PING_TIMEOUT=10

# Real-time Updates
REALTIME_UPDATES_ENABLED=true
REALTIME_UPDATE_INTERVAL=5
REALTIME_MAX_CONNECTIONS=1000

# Machine Learning Settings
ML_MODEL_PATH=/var/lib/marabet/models
ML_MODEL_CACHE_SIZE=10
ML_PREDICTION_BATCH_SIZE=50
ML_PREDICTION_TIMEOUT=60

# Data Collection Settings
DATA_COLLECTION_ENABLED=true
DATA_COLLECTION_INTERVAL=300
DATA_RETENTION_DAYS=365
DATA_CLEANUP_SCHEDULE=0 3 * * *

# Backup and Recovery
BACKUP_S3_BUCKET=marabet-backups
BACKUP_S3_REGION=us-east-1
BACKUP_ENCRYPTION_KEY=your_backup_encryption_key

# Disaster Recovery
DR_ENABLED=true
DR_RTO=4
DR_RPO=1
DR_BACKUP_FREQUENCY=hourly

# Compliance and Auditing
AUDIT_LOG_ENABLED=true
AUDIT_LOG_RETENTION_DAYS=2555
COMPLIANCE_MODE=strict

# Development and Testing
TEST_MODE=false
MOCK_EXTERNAL_APIS=false
DEBUG_SQL=false
PROFILING_ENABLED=false
"""
    
    # Salvar arquivo .env.production local
    with open('.env.production', 'w') as f:
        f.write(env_content)
    print("✅ Arquivo .env.production atualizado localmente")
    
    print("\n🔧 ETAPA 2: TRANSFERINDO ARQUIVO ATUALIZADO")
    print("-" * 50)
    
    # Transferir arquivo .env.production para o servidor
    print("📤 Transferindo arquivo .env.production para o servidor...")
    scp_command = f'scp -i "{key_path}" -o StrictHostKeyChecking=no .env.production ubuntu@{ubuntu_public_ip}:/home/ubuntu/marabet-ai/'
    
    print(f"Executando: {scp_command}")
    scp_result = run_command(scp_command)
    
    if scp_result is not None:
        print("✅ Arquivo .env.production transferido com sucesso")
    else:
        print("⚠️ Falha na transferência do arquivo")
        print("💡 Tente executar manualmente:")
        print(f"scp -i {key_path} .env.production ubuntu@{ubuntu_public_ip}:/home/ubuntu/marabet-ai/")
    
    print("\n🔧 ETAPA 3: VERIFICANDO ARQUIVO NO SERVIDOR")
    print("-" * 50)
    
    # Verificar se arquivo foi transferido
    print("🔍 Verificando arquivo no servidor...")
    verify_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "cd /home/ubuntu/marabet-ai && ls -la .env.production"'
    verify_result = run_command(verify_command)
    
    if verify_result:
        print("✅ Arquivo .env.production encontrado no servidor")
        print(verify_result)
    else:
        print("⚠️ Arquivo .env.production não encontrado no servidor")
    
    print("\n🔧 ETAPA 4: MOSTRANDO CONTEÚDO DO ARQUIVO")
    print("-" * 50)
    
    # Mostrar conteúdo do arquivo no servidor
    print("📋 Conteúdo do arquivo .env.production no servidor:")
    content_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "cd /home/ubuntu/marabet-ai && head -20 .env.production"'
    content_result = run_command(content_command)
    
    if content_result:
        print(content_result)
    else:
        print("⚠️ Falha ao ler conteúdo do arquivo")
    
    print("\n🔧 ETAPA 5: INSTRUÇÕES PARA EDICAO MANUAL")
    print("-" * 50)
    
    print("📝 INSTRUÇÕES PARA EDITAR O ARQUIVO MANUALMENTE:")
    print("-" * 60)
    print("1. Conectar via SSH:")
    print(f"   ssh -i {key_path} ubuntu@{ubuntu_public_ip}")
    print()
    print("2. Ir para pasta do projeto:")
    print("   cd /home/ubuntu/marabet-ai")
    print()
    print("3. Editar arquivo .env.production:")
    print("   nano .env.production")
    print()
    print("4. Verificar configurações importantes:")
    print(f"   DATABASE_URL=postgresql://marabetadmin:MaraBet2024!SuperSecret@{rds_endpoint}:5432/postgres")
    print(f"   REDIS_URL=redis://{redis_endpoint}:6379/0")
    print("   API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045")
    print("   SECRET_KEY=MaraBet2024!SuperSecretKey")
    print()
    print("5. Salvar arquivo:")
    print("   Ctrl+O, Enter, Ctrl+X")
    print()
    print("6. Verificar arquivo:")
    print("   cat .env.production")
    
    print("\n🔧 ETAPA 6: COMANDOS DE VERIFICAÇÃO")
    print("-" * 50)
    
    print("🧪 COMANDOS PARA TESTAR CONFIGURAÇÃO:")
    print("-" * 60)
    print("Execute no servidor Ubuntu:")
    print()
    print("# 1. Verificar variáveis de ambiente")
    print("source .env.production")
    print("echo $DATABASE_URL")
    print("echo $REDIS_URL")
    print()
    print("# 2. Testar conexão com RDS")
    print("psql $DATABASE_URL -c 'SELECT version();'")
    print()
    print("# 3. Testar conexão com Redis")
    print("redis-cli -u $REDIS_URL ping")
    print()
    print("# 4. Verificar se aplicação está rodando")
    print("docker ps")
    print()
    print("# 5. Ver logs da aplicação")
    print("docker-compose logs --tail=20")
    print()
    print("# 6. Testar endpoint de health")
    print("curl http://localhost:8000/health")
    
    print("\n🎉 ARQUIVO .ENV.PRODUCTION ATUALIZADO!")
    print("=" * 60)
    
    print("\n📋 RESUMO DA ATUALIZAÇÃO:")
    print("-" * 40)
    print(f"• RDS Endpoint: {rds_endpoint}")
    print(f"• Redis Endpoint: {redis_endpoint}")
    print(f"• Arquivo: .env.production")
    print(f"• Status: Atualizado com endpoints reais")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Arquivo .env.production atualizado")
    print("2. 🔄 Verificar configurações")
    print("3. 🔄 Testar conexões")
    print("4. 🔄 Reiniciar aplicação")
    print("5. 🔄 Verificar logs")
    print("6. 🔄 Testar endpoints")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("-" * 40)
    print("• Verifique se as senhas estão corretas")
    print("• Teste as conexões antes de reiniciar a aplicação")
    print("• Monitore os logs após a reinicialização")
    print("• Configure backup automático do arquivo .env")
    
    return True

def main():
    print("🚀 Iniciando atualização do arquivo .env.production...")
    
    # Atualizar .env.production
    success = update_env_production()
    
    if success:
        print("\n🎯 ARQUIVO .ENV.PRODUCTION ATUALIZADO COM SUCESSO!")
        print("O arquivo foi atualizado com os endpoints reais do RDS e Redis!")
    else:
        print("\n❌ Falha na atualização do arquivo .env.production")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
