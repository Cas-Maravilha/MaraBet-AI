#!/bin/bash
# Script de Backup Automático - MaraBet AI

echo "💾 MARABET AI - BACKUP AUTOMÁTICO"
echo "================================="
echo "📅 Data/Hora: $(date)"

# Configurações
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="marabet_backup_$DATE"
S3_BUCKET="marabet-backups"
RDS_ENDPOINT="marabet-db.cmvmwskgiabr.us-east-1.rds.amazonaws.com"
REDIS_ENDPOINT="marabet-redis.ve5qk7.0001.use1.cache.amazonaws.com"

# Criar diretório de backup
mkdir -p $BACKUP_DIR/$BACKUP_NAME

echo "📁 Criando diretório de backup: $BACKUP_DIR/$BACKUP_NAME"

# 1. Backup do banco de dados RDS
if [ ! -z "$RDS_ENDPOINT" ]; then
    echo "🗄️ Fazendo backup do RDS..."
    pg_dump -h $RDS_ENDPOINT -U marabetadmin -d postgres > $BACKUP_DIR/$BACKUP_NAME/database_backup.sql
    if [ $? -eq 0 ]; then
        echo "✅ Backup do RDS concluído"
    else
        echo "❌ Falha no backup do RDS"
    fi
else
    echo "⚠️ RDS endpoint não configurado, pulando backup do banco"
fi

# 2. Backup do Redis
if [ ! -z "$REDIS_ENDPOINT" ]; then
    echo "⚡ Fazendo backup do Redis..."
    redis-cli -h $REDIS_ENDPOINT --rdb $BACKUP_DIR/$BACKUP_NAME/redis_backup.rdb
    if [ $? -eq 0 ]; then
        echo "✅ Backup do Redis concluído"
    else
        echo "❌ Falha no backup do Redis"
    fi
else
    echo "⚠️ Redis endpoint não configurado, pulando backup do cache"
fi

# 3. Backup dos arquivos de configuração
echo "📄 Fazendo backup dos arquivos de configuração..."
cp -r /home/ubuntu/marabet-ai/.env* $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || true
cp -r /home/ubuntu/marabet-ai/docker-compose* $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || true
cp -r /home/ubuntu/marabet-ai/nginx.conf $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || true
cp -r /home/ubuntu/marabet-ai/aws_infrastructure_config.json $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || true

# 4. Backup dos logs
echo "📝 Fazendo backup dos logs..."
mkdir -p $BACKUP_DIR/$BACKUP_NAME/logs
cp -r /var/log/nginx/* $BACKUP_DIR/$BACKUP_NAME/logs/ 2>/dev/null || true
cp -r /home/ubuntu/marabet-ai/logs/* $BACKUP_DIR/$BACKUP_NAME/logs/ 2>/dev/null || true

# 5. Backup dos dados da aplicação
echo "📊 Fazendo backup dos dados da aplicação..."
mkdir -p $BACKUP_DIR/$BACKUP_NAME/data
cp -r /home/ubuntu/marabet-ai/data/* $BACKUP_DIR/$BACKUP_NAME/data/ 2>/dev/null || true
cp -r /home/ubuntu/marabet-ai/backups/* $BACKUP_DIR/$BACKUP_NAME/data/ 2>/dev/null || true

# 6. Criar arquivo de metadados
echo "📋 Criando arquivo de metadados..."
cat > $BACKUP_DIR/$BACKUP_NAME/backup_info.txt << EOF
MaraBet AI - Backup Automático
=============================
Data/Hora: $(date)
Versão: 1.0.0
Instância: $(hostname)
IP Público: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
RDS Endpoint: $RDS_ENDPOINT
Redis Endpoint: $REDIS_ENDPOINT
Tamanho Total: $(du -sh $BACKUP_DIR/$BACKUP_NAME | cut -f1)
EOF

# 7. Compactar backup
echo "📦 Compactando backup..."
cd $BACKUP_DIR
tar -czf $BACKUP_NAME.tar.gz $BACKUP_NAME/
if [ $? -eq 0 ]; then
    echo "✅ Backup compactado: $BACKUP_NAME.tar.gz"
    # Remover diretório não compactado
    rm -rf $BACKUP_NAME/
else
    echo "❌ Falha na compactação do backup"
fi

# 8. Upload para S3 (se configurado)
if [ ! -z "$S3_BUCKET" ]; then
    echo "☁️ Enviando backup para S3..."
    aws s3 cp $BACKUP_NAME.tar.gz s3://$S3_BUCKET/backups/
    if [ $? -eq 0 ]; then
        echo "✅ Backup enviado para S3: s3://$S3_BUCKET/backups/$BACKUP_NAME.tar.gz"
    else
        echo "❌ Falha no upload para S3"
    fi
else
    echo "⚠️ S3 bucket não configurado, pulando upload"
fi

# 9. Limpar backups antigos (manter apenas os últimos 7 dias)
echo "🧹 Limpando backups antigos..."
find $BACKUP_DIR -name "marabet_backup_*.tar.gz" -mtime +7 -delete
echo "✅ Backups antigos removidos (mais de 7 dias)"

# 10. Verificar integridade do backup
echo "🔍 Verificando integridade do backup..."
if [ -f "$BACKUP_DIR/$BACKUP_NAME.tar.gz" ]; then
    tar -tzf $BACKUP_DIR/$BACKUP_NAME.tar.gz > /dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Backup íntegro e válido"
    else
        echo "❌ Backup corrompido!"
    fi
else
    echo "❌ Arquivo de backup não encontrado"
fi

echo "🎉 BACKUP AUTOMÁTICO CONCLUÍDO!"
echo "==============================="
echo "📁 Local: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo "📅 Data: $(date)"
echo "💾 Tamanho: $(du -sh $BACKUP_DIR/$BACKUP_NAME.tar.gz | cut -f1)"
