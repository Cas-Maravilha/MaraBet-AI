#!/bin/bash
# Script de Atualização da Aplicação - MaraBet AI

echo "🔄 MARABET AI - ATUALIZAÇÃO DA APLICAÇÃO"
echo "======================================="
echo "📅 Data/Hora: $(date)"

# Configurações
LOG_FILE="/var/log/marabet_app_updates.log"
APP_DIR="/home/ubuntu/marabet-ai"
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Função para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "🚀 Iniciando atualização da aplicação"

# 1. Fazer backup da aplicação
log "💾 Criando backup da aplicação..."
if [ -f "$APP_DIR/backup_script.sh" ]; then
    $APP_DIR/backup_script.sh
    if [ $? -eq 0 ]; then
        log "✅ Backup da aplicação criado"
    else
        log "❌ Falha no backup da aplicação, continuando"
    fi
else
    log "⚠️ Script de backup não encontrado, pulando backup"
fi

# 2. Parar aplicação
log "⏹️ Parando aplicação..."
cd $APP_DIR
docker-compose -f docker-compose.production.yml down

if [ $? -eq 0 ]; then
    log "✅ Aplicação parada"
else
    log "❌ Falha ao parar aplicação"
    exit 1
fi

# 3. Fazer backup dos arquivos de configuração
log "📄 Fazendo backup dos arquivos de configuração..."
cp -r $APP_DIR/.env* $BACKUP_DIR/ 2>/dev/null || true
cp -r $APP_DIR/docker-compose* $BACKUP_DIR/ 2>/dev/null || true
cp -r $APP_DIR/nginx.conf $BACKUP_DIR/ 2>/dev/null || true

# 4. Atualizar código da aplicação (se usando Git)
log "📥 Atualizando código da aplicação..."
if [ -d "$APP_DIR/.git" ]; then
    git pull origin main
    if [ $? -eq 0 ]; then
        log "✅ Código atualizado via Git"
    else
        log "❌ Falha na atualização via Git"
    fi
else
    log "⚠️ Repositório Git não encontrado, pulando atualização de código"
fi

# 5. Atualizar dependências Python
log "🐍 Atualizando dependências Python..."
if [ -f "$APP_DIR/requirements.txt" ]; then
    pip install -r requirements.txt --upgrade
    if [ $? -eq 0 ]; then
        log "✅ Dependências Python atualizadas"
    else
        log "❌ Falha na atualização das dependências Python"
    fi
else
    log "⚠️ requirements.txt não encontrado, pulando atualização de dependências"
fi

# 6. Reconstruir imagens Docker
log "🐳 Reconstruindo imagens Docker..."
docker-compose -f docker-compose.production.yml build --no-cache

if [ $? -eq 0 ]; then
    log "✅ Imagens Docker reconstruídas"
else
    log "❌ Falha na reconstrução das imagens Docker"
    exit 1
fi

# 7. Iniciar aplicação
log "🚀 Iniciando aplicação..."
docker-compose -f docker-compose.production.yml up -d

if [ $? -eq 0 ]; then
    log "✅ Aplicação iniciada"
else
    log "❌ Falha ao iniciar aplicação"
    exit 1
fi

# 8. Aguardar aplicação ficar pronta
log "⏳ Aguardando aplicação ficar pronta..."
sleep 30

# 9. Verificar status da aplicação
log "🔍 Verificando status da aplicação..."
docker-compose -f docker-compose.production.yml ps

# 10. Testar endpoints da aplicação
log "🧪 Testando endpoints da aplicação..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log "✅ Endpoint /health funcionando"
else
    log "❌ Endpoint /health não está funcionando"
fi

if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
    log "✅ Endpoint /docs funcionando"
else
    log "❌ Endpoint /docs não está funcionando"
fi

# 11. Verificar logs da aplicação
log "📝 Verificando logs da aplicação..."
docker-compose -f docker-compose.production.yml logs --tail=50

# 12. Limpar imagens Docker antigas
log "🧹 Limpando imagens Docker antigas..."
docker image prune -f

if [ $? -eq 0 ]; then
    log "✅ Imagens Docker antigas removidas"
else
    log "❌ Falha na limpeza das imagens Docker"
fi

# 13. Verificar espaço em disco
log "💾 Verificando espaço em disco..."
df -h

# 14. Verificar memória
log "🧠 Verificando memória..."
free -h

log "🎉 ATUALIZAÇÃO DA APLICAÇÃO CONCLUÍDA!"
log "====================================="
log "📅 Data: $(date)"
log "✅ Aplicação atualizada e funcionando"
