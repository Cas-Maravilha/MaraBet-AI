#!/bin/bash

################################################################################
# MARABET AI - BACKUP AUTOMÁTICO PARA S3
# Executar na EC2 via cron
################################################################################

set -e

# Configurações
BUCKET_NAME="marabet-backups"
REGION="eu-west-1"
BACKUP_DIR="/opt/marabet/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DAY_OF_WEEK=$(date +%u)  # 1-7 (Monday-Sunday)
DAY_OF_MONTH=$(date +%d)

# Criar diretório de backups
mkdir -p $BACKUP_DIR

echo "========================================================================"
echo "💾 MaraBet AI - Backup Automático"
echo "========================================================================"
echo "Data: $(date)"
echo "Bucket: s3://$BUCKET_NAME"
echo ""

################################################################################
# 1. BACKUP DATABASE (PostgreSQL)
################################################################################

echo "1. Backup Database (RDS PostgreSQL)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Carregar credenciais do .env
source /opt/marabet/.env

BACKUP_FILE="$BACKUP_DIR/database_${DATE}.sql.gz"

# Fazer backup
PGPASSWORD=$DB_PASSWORD pg_dump \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d $DB_NAME \
    -F c \
    | gzip > $BACKUP_FILE

if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[✓] Backup database criado: $BACKUP_FILE ($SIZE)"
else
    echo "[✗] Falha ao criar backup database"
    exit 1
fi

################################################################################
# 2. BACKUP REDIS (Snapshot)
################################################################################

echo ""
echo "2. Backup Redis (snapshot via AWS)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Redis Serverless não suporta snapshots manuais
# Usar backup de dados via Redis CLI se necessário
echo "[ℹ] Redis Serverless: Backup gerenciado pela AWS"
echo "[ℹ] Dados em cache são temporários por natureza"

################################################################################
# 3. BACKUP ARQUIVOS ESTÁTICOS
################################################################################

echo ""
echo "3. Backup arquivos estáticos e media..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "/opt/marabet/static" ] || [ -d "/opt/marabet/media" ]; then
    STATIC_BACKUP="$BACKUP_DIR/static_media_${DATE}.tar.gz"
    
    tar -czf $STATIC_BACKUP \
        -C /opt/marabet \
        static media 2>/dev/null || true
    
    if [ -f "$STATIC_BACKUP" ]; then
        SIZE=$(du -h "$STATIC_BACKUP" | cut -f1)
        echo "[✓] Backup static/media: $STATIC_BACKUP ($SIZE)"
    fi
else
    echo "[ℹ] Diretórios static/media não encontrados"
fi

################################################################################
# 4. BACKUP .ENV (Criptografado)
################################################################################

echo ""
echo "4. Backup .env (criptografado)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "/opt/marabet/.env" ]; then
    ENV_BACKUP="$BACKUP_DIR/env_${DATE}.enc"
    
    # Criptografar .env (usando senha da AWS)
    openssl enc -aes-256-cbc -salt \
        -in /opt/marabet/.env \
        -out $ENV_BACKUP \
        -pass pass:$DB_PASSWORD 2>/dev/null
    
    if [ -f "$ENV_BACKUP" ]; then
        echo "[✓] Backup .env criptografado: $ENV_BACKUP"
    fi
fi

################################################################################
# 5. UPLOAD PARA S3
################################################################################

echo ""
echo "5. Upload para S3..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Determinar pasta de destino
if [ "$DAY_OF_WEEK" == "7" ]; then
    # Domingo = weekly
    S3_PREFIX="weekly"
elif [ "$DAY_OF_MONTH" == "01" ]; then
    # Dia 1 = monthly
    S3_PREFIX="monthly"
else
    # Outros dias = daily
    S3_PREFIX="daily"
fi

echo "[ℹ] Tipo de backup: $S3_PREFIX"

# Upload database
if [ -f "$BACKUP_FILE" ]; then
    echo "[ℹ] Uploading database backup..."
    aws s3 cp "$BACKUP_FILE" \
        "s3://$BUCKET_NAME/$S3_PREFIX/database_${DATE}.sql.gz" \
        --region $REGION \
        --storage-class STANDARD
    
    echo "[✓] Database backup enviado para S3"
fi

# Upload static/media
if [ -f "$STATIC_BACKUP" ]; then
    aws s3 cp "$STATIC_BACKUP" \
        "s3://$BUCKET_NAME/$S3_PREFIX/static_media_${DATE}.tar.gz" \
        --region $REGION
    
    echo "[✓] Static/media backup enviado para S3"
fi

# Upload .env
if [ -f "$ENV_BACKUP" ]; then
    aws s3 cp "$ENV_BACKUP" \
        "s3://$BUCKET_NAME/$S3_PREFIX/env_${DATE}.enc" \
        --region $REGION
    
    echo "[✓] .env backup enviado para S3"
fi

################################################################################
# 6. LIMPAR BACKUPS LOCAIS ANTIGOS
################################################################################

echo ""
echo "6. Limpando backups locais antigos..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Manter apenas últimos 7 dias localmente
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.enc" -mtime +7 -delete

echo "[✓] Backups locais antigos removidos (>7 dias)"

################################################################################
# 7. VERIFICAR S3
################################################################################

echo ""
echo "7. Verificando backups no S3..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Listar backups recentes
echo ""
echo "Backups recentes em S3:"
aws s3 ls "s3://$BUCKET_NAME/$S3_PREFIX/" \
    --human-readable \
    --summarize | tail -10

################################################################################
# RESUMO
################################################################################

echo ""
echo "========================================================================"
echo "✅ BACKUP COMPLETO!"
echo "========================================================================"
echo ""

echo "Backups criados:"
echo "  • Database:      $([ -f "$BACKUP_FILE" ] && echo "✅" || echo "❌")"
echo "  • Static/Media:  $([ -f "$STATIC_BACKUP" ] && echo "✅" || echo "❌")"
echo "  • .env:          $([ -f "$ENV_BACKUP" ] && echo "✅" || echo "❌")"
echo ""

echo "Upload S3:"
echo "  • Bucket:        s3://$BUCKET_NAME"
echo "  • Pasta:         $S3_PREFIX/"
echo "  • Região:        $REGION"
echo ""

echo "Executado em:      $(date)"
echo ""

# Log
echo "[$(date)] Backup completo: $S3_PREFIX | Files: $BACKUP_FILE" >> /var/log/marabet/backup.log

