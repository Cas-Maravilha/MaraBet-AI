#!/bin/bash
# Script de Configuração de Backup - MaraBet AI

echo "💾 MARABET AI - CONFIGURAÇÃO DE BACKUP NO SERVIDOR"
echo "================================================="

# Configurações
BACKUP_SCRIPT="/home/ubuntu/backup.sh"
LOG_FILE="/var/log/marabet_backup.log"

echo "📅 Configurando backup automático..."

# 1. Criar script de backup
echo "📝 Criando script de backup..."
cat > $BACKUP_SCRIPT << 'EOF'
#!/bin/bash
# Script de Backup Automático - MaraBet AI
# Executado diariamente às 02:00

echo "💾 MARABET AI - BACKUP AUTOMÁTICO"
echo "================================="
echo "📅 Data/Hora: $(date)"

# Configurações
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
LOG_FILE="/var/log/marabet_backup.log"
APP_DIR="/home/ubuntu/marabet-ai"
RDS_ENDPOINT="marabet-db.cmvmwskgiabr.us-east-1.rds.amazonaws.com"
REDIS_ENDPOINT="marabet-redis.ve5qk7.0001.use1.cache.amazonaws.com"

# Função para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "🚀 Iniciando backup automático"

# Criar diretório de backup
mkdir -p $BACKUP_DIR
log "📁 Diretório de backup: $BACKUP_DIR"

# 1. Backup do banco de dados RDS
log "🗄️ Fazendo backup do banco de dados..."
if [ ! -z "$RDS_ENDPOINT" ]; then
    # Usar pg_dump diretamente no RDS
    PGPASSWORD="MaraBet2024!SuperSecret" pg_dump -h $RDS_ENDPOINT -U marabetadmin -d postgres > $BACKUP_DIR/db_$DATE.sql
    
    if [ $? -eq 0 ]; then
        log "✅ Backup do banco de dados concluído: db_$DATE.sql"
    else
        log "❌ Falha no backup do banco de dados"
    fi
else
    log "⚠️ RDS endpoint não configurado, pulando backup do banco"
fi

# 2. Backup do Redis
log "⚡ Fazendo backup do Redis..."
if [ ! -z "$REDIS_ENDPOINT" ]; then
    # Usar redis-cli para fazer backup
    redis-cli -h $REDIS_ENDPOINT --rdb $BACKUP_DIR/redis_$DATE.rdb
    
    if [ $? -eq 0 ]; then
        log "✅ Backup do Redis concluído: redis_$DATE.rdb"
    else
        log "❌ Falha no backup do Redis"
    fi
else
    log "⚠️ Redis endpoint não configurado, pulando backup do cache"
fi

# 3. Backup dos arquivos de configuração
log "📄 Fazendo backup dos arquivos de configuração..."
cp -r $APP_DIR/.env* $BACKUP_DIR/ 2>/dev/null || true
cp -r $APP_DIR/docker-compose* $BACKUP_DIR/ 2>/dev/null || true
cp -r $APP_DIR/nginx.conf $BACKUP_DIR/ 2>/dev/null || true
cp -r $APP_DIR/aws_infrastructure_config.json $BACKUP_DIR/ 2>/dev/null || true
log "✅ Arquivos de configuração copiados"

# 4. Backup dos logs
log "📝 Fazendo backup dos logs..."
mkdir -p $BACKUP_DIR/logs
cp -r /var/log/nginx/* $BACKUP_DIR/logs/ 2>/dev/null || true
cp -r $APP_DIR/logs/* $BACKUP_DIR/logs/ 2>/dev/null || true
log "✅ Logs copiados"

# 5. Backup dos dados da aplicação
log "📊 Fazendo backup dos dados da aplicação..."
mkdir -p $BACKUP_DIR/data
cp -r $APP_DIR/data/* $BACKUP_DIR/data/ 2>/dev/null || true
cp -r $APP_DIR/backups/* $BACKUP_DIR/data/ 2>/dev/null || true
log "✅ Dados da aplicação copiados"

# 6. Backup dos scripts
log "🔧 Fazendo backup dos scripts..."
mkdir -p $BACKUP_DIR/scripts
cp -r $APP_DIR/*.sh $BACKUP_DIR/scripts/ 2>/dev/null || true
log "✅ Scripts copiados"

# 7. Criar arquivo de metadados
log "📋 Criando arquivo de metadados..."
cat > $BACKUP_DIR/backup_info_$DATE.txt << EOF
MaraBet AI - Backup Automático
=============================
Data/Hora: $(date)
Versão: 1.0.0
Instância: $(hostname)
IP Público: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
RDS Endpoint: $RDS_ENDPOINT
Redis Endpoint: $REDIS_ENDPOINT
Tamanho Total: $(du -sh $BACKUP_DIR | cut -f1)
Arquivos:
$(ls -la $BACKUP_DIR)
EOF

# 8. Compactar backup
log "📦 Compactando backup..."
cd $BACKUP_DIR
tar -czf backup_$DATE.tar.gz db_$DATE.sql redis_$DATE.rdb *.env* docker-compose* nginx.conf aws_infrastructure_config.json logs/ data/ scripts/ backup_info_$DATE.txt 2>/dev/null

if [ $? -eq 0 ]; then
    log "✅ Backup compactado: backup_$DATE.tar.gz"
    # Remover arquivos não compactados
    rm -f db_$DATE.sql redis_$DATE.rdb backup_info_$DATE.txt
    rm -rf logs/ data/ scripts/
else
    log "❌ Falha na compactação do backup"
fi

# 9. Upload para S3 (se configurado)
S3_BUCKET="marabet-backups"
if [ ! -z "$S3_BUCKET" ]; then
    log "☁️ Enviando backup para S3..."
    aws s3 cp backup_$DATE.tar.gz s3://$S3_BUCKET/backups/
    
    if [ $? -eq 0 ]; then
        log "✅ Backup enviado para S3: s3://$S3_BUCKET/backups/backup_$DATE.tar.gz"
    else
        log "❌ Falha no upload para S3"
    fi
else
    log "⚠️ S3 bucket não configurado, pulando upload"
fi

# 10. Limpar backups antigos (manter apenas os últimos 7 dias)
log "🧹 Limpando backups antigos..."
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "redis_*.rdb" -mtime +7 -delete
log "✅ Backups antigos removidos (mais de 7 dias)"

# 11. Verificar integridade do backup
log "🔍 Verificando integridade do backup..."
if [ -f "backup_$DATE.tar.gz" ]; then
    tar -tzf backup_$DATE.tar.gz > /dev/null
    if [ $? -eq 0 ]; then
        log "✅ Backup íntegro e válido"
    else
        log "❌ Backup corrompido!"
    fi
else
    log "❌ Arquivo de backup não encontrado"
fi

# 12. Verificar espaço em disco
log "💾 Verificando espaço em disco..."
df -h

# 13. Verificar tamanho do backup
log "📏 Verificando tamanho do backup..."
if [ -f "backup_$DATE.tar.gz" ]; then
    backup_size=$(du -sh backup_$DATE.tar.gz | cut -f1)
    log "📦 Tamanho do backup: $backup_size"
fi

log "🎉 BACKUP AUTOMÁTICO CONCLUÍDO!"
log "==============================="
log "📅 Data: $(date)"
log "📁 Local: $BACKUP_DIR/backup_$DATE.tar.gz"
log "💾 Tamanho: $(du -sh backup_$DATE.tar.gz | cut -f1)"

EOF

# 2. Tornar executável
echo "🔧 Tornando script executável..."
chmod +x $BACKUP_SCRIPT

# 3. Criar diretório de backup
echo "📁 Criando diretório de backup..."
mkdir -p /home/ubuntu/backups

# 4. Configurar cron job
echo "⏰ Configurando cron job..."
(crontab -l 2>/dev/null; echo "0 2 * * * $BACKUP_SCRIPT >> $LOG_FILE 2>&1") | crontab -

# 5. Verificar cron job
echo "🔍 Verificando cron job..."
crontab -l | grep backup

# 6. Testar script
echo "🧪 Testando script de backup..."
$BACKUP_SCRIPT

if [ $? -eq 0 ]; then
    echo "✅ Script de backup testado com sucesso"
else
    echo "❌ Falha no teste do script de backup"
fi

echo "🎉 CONFIGURAÇÃO DE BACKUP CONCLUÍDA!"
echo "==================================="
echo "📅 Backup será executado diariamente às 02:00"
echo "📁 Diretório: /home/ubuntu/backups"
echo "📝 Log: $LOG_FILE"
