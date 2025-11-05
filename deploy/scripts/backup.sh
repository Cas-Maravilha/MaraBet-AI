#!/bin/bash
# Script de Backup - MaraBet AI

echo "💾 Iniciando backup do MaraBet AI..."

# Criar diretório de backup
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup do banco de dados
echo "📊 Fazendo backup do banco de dados..."
pg_dump $DATABASE_URL > "$BACKUP_DIR/database_backup.sql"

# Backup dos logs
echo "📝 Fazendo backup dos logs..."
cp -r logs/* "$BACKUP_DIR/"

# Backup das configurações
echo "⚙️ Fazendo backup das configurações..."
cp .env.production "$BACKUP_DIR/"
cp -r config/ "$BACKUP_DIR/"

# Comprimir backup
echo "🗜️ Comprimindo backup..."
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "✅ Backup concluído: $BACKUP_DIR.tar.gz"
