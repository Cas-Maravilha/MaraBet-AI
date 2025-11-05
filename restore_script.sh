#!/bin/bash
# Script de Restauração - MaraBet AI

echo "🔄 MARABET AI - RESTAURAÇÃO DE BACKUP"
echo "====================================="
echo "📅 Data/Hora: $(date)"

# Configurações
BACKUP_DIR="/home/ubuntu/backups"
RDS_ENDPOINT="marabet-db.cmvmwskgiabr.us-east-1.rds.amazonaws.com"
REDIS_ENDPOINT="marabet-redis.ve5qk7.0001.use1.cache.amazonaws.com"

# Verificar se foi fornecido um arquivo de backup
if [ -z "$1" ]; then
    echo "❌ Uso: $0 <arquivo_backup.tar.gz>"
    echo "💡 Exemplo: $0 marabet_backup_20241023_134500.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"

# Verificar se o arquivo existe
if [ ! -f "$BACKUP_PATH" ]; then
    echo "❌ Arquivo de backup não encontrado: $BACKUP_PATH"
    exit 1
fi

echo "📁 Restaurando backup: $BACKUP_FILE"

# 1. Parar serviços
echo "⏹️ Parando serviços..."
docker-compose -f docker-compose.production.yml down

# 2. Extrair backup
echo "📦 Extraindo backup..."
cd $BACKUP_DIR
tar -xzf $BACKUP_FILE
BACKUP_NAME=$(basename $BACKUP_FILE .tar.gz)

# 3. Restaurar banco de dados
if [ -f "$BACKUP_NAME/database_backup.sql" ] && [ ! -z "$RDS_ENDPOINT" ]; then
    echo "🗄️ Restaurando banco de dados..."
    psql -h $RDS_ENDPOINT -U marabetadmin -d postgres < $BACKUP_NAME/database_backup.sql
    if [ $? -eq 0 ]; then
        echo "✅ Banco de dados restaurado"
    else
        echo "❌ Falha na restauração do banco de dados"
    fi
else
    echo "⚠️ Backup do banco de dados não encontrado ou RDS não configurado"
fi

# 4. Restaurar Redis
if [ -f "$BACKUP_NAME/redis_backup.rdb" ] && [ ! -z "$REDIS_ENDPOINT" ]; then
    echo "⚡ Restaurando Redis..."
    redis-cli -h $REDIS_ENDPOINT --rdb $BACKUP_NAME/redis_backup.rdb
    if [ $? -eq 0 ]; then
        echo "✅ Redis restaurado"
    else
        echo "❌ Falha na restauração do Redis"
    fi
else
    echo "⚠️ Backup do Redis não encontrado ou Redis não configurado"
fi

# 5. Restaurar arquivos de configuração
echo "📄 Restaurando arquivos de configuração..."
cp -r $BACKUP_NAME/.env* /home/ubuntu/marabet-ai/ 2>/dev/null || true
cp -r $BACKUP_NAME/docker-compose* /home/ubuntu/marabet-ai/ 2>/dev/null || true
cp -r $BACKUP_NAME/nginx.conf /home/ubuntu/marabet-ai/ 2>/dev/null || true
cp -r $BACKUP_NAME/aws_infrastructure_config.json /home/ubuntu/marabet-ai/ 2>/dev/null || true

# 6. Restaurar logs
echo "📝 Restaurando logs..."
cp -r $BACKUP_NAME/logs/* /var/log/nginx/ 2>/dev/null || true
cp -r $BACKUP_NAME/logs/* /home/ubuntu/marabet-ai/logs/ 2>/dev/null || true

# 7. Restaurar dados da aplicação
echo "📊 Restaurando dados da aplicação..."
cp -r $BACKUP_NAME/data/* /home/ubuntu/marabet-ai/data/ 2>/dev/null || true
cp -r $BACKUP_NAME/data/* /home/ubuntu/marabet-ai/backups/ 2>/dev/null || true

# 8. Reiniciar serviços
echo "🔄 Reiniciando serviços..."
docker-compose -f docker-compose.production.yml up -d

# 9. Verificar status dos serviços
echo "🔍 Verificando status dos serviços..."
sleep 30
docker-compose -f docker-compose.production.yml ps

# 10. Limpar arquivos temporários
echo "🧹 Limpando arquivos temporários..."
rm -rf $BACKUP_NAME/

echo "🎉 RESTAURAÇÃO CONCLUÍDA!"
echo "========================="
echo "📅 Data: $(date)"
echo "✅ Serviços reiniciados"
echo "💡 Verifique os logs se necessário"
