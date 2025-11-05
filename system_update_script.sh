#!/bin/bash
# Script de Atualização do Sistema - MaraBet AI

echo "🔄 MARABET AI - ATUALIZAÇÃO DO SISTEMA"
echo "======================================"
echo "📅 Data/Hora: $(date)"

# Configurações
LOG_FILE="/var/log/marabet_updates.log"
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Função para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "🚀 Iniciando atualização do sistema"

# 1. Fazer backup antes da atualização
log "💾 Criando backup antes da atualização..."
if [ -f "/home/ubuntu/marabet-ai/backup_script.sh" ]; then
    /home/ubuntu/marabet-ai/backup_script.sh
    if [ $? -eq 0 ]; then
        log "✅ Backup criado com sucesso"
    else
        log "❌ Falha no backup, continuando com atualização"
    fi
else
    log "⚠️ Script de backup não encontrado, pulando backup"
fi

# 2. Atualizar lista de pacotes
log "📦 Atualizando lista de pacotes..."
apt update

if [ $? -eq 0 ]; then
    log "✅ Lista de pacotes atualizada"
else
    log "❌ Falha ao atualizar lista de pacotes"
    exit 1
fi

# 3. Atualizar pacotes do sistema
log "🔄 Atualizando pacotes do sistema..."
apt upgrade -y

if [ $? -eq 0 ]; then
    log "✅ Pacotes do sistema atualizados"
else
    log "❌ Falha na atualização de pacotes do sistema"
    exit 1
fi

# 4. Atualizar Docker
log "🐳 Atualizando Docker..."
apt install -y docker.io docker-compose

if [ $? -eq 0 ]; then
    log "✅ Docker atualizado"
else
    log "❌ Falha na atualização do Docker"
fi

# 5. Atualizar Nginx
log "🌐 Atualizando Nginx..."
apt install -y nginx

if [ $? -eq 0 ]; then
    log "✅ Nginx atualizado"
else
    log "❌ Falha na atualização do Nginx"
fi

# 6. Atualizar Certbot
log "🔒 Atualizando Certbot..."
apt install -y certbot python3-certbot-nginx

if [ $? -eq 0 ]; then
    log "✅ Certbot atualizado"
else
    log "❌ Falha na atualização do Certbot"
fi

# 7. Limpar pacotes desnecessários
log "🧹 Limpando pacotes desnecessários..."
apt autoremove -y
apt autoclean

if [ $? -eq 0 ]; then
    log "✅ Limpeza concluída"
else
    log "❌ Falha na limpeza"
fi

# 8. Reiniciar serviços
log "🔄 Reiniciando serviços..."
systemctl restart nginx
systemctl restart docker

if [ $? -eq 0 ]; then
    log "✅ Serviços reiniciados"
else
    log "❌ Falha ao reiniciar serviços"
fi

# 9. Verificar status dos serviços
log "🔍 Verificando status dos serviços..."
systemctl status nginx --no-pager
systemctl status docker --no-pager

# 10. Verificar espaço em disco
log "💾 Verificando espaço em disco..."
df -h

# 11. Verificar memória
log "🧠 Verificando memória..."
free -h

# 12. Verificar logs de erro
log "📝 Verificando logs de erro..."
if [ -f "/var/log/nginx/error.log" ]; then
    error_count=$(grep -c "error" /var/log/nginx/error.log | tail -1)
    if [ $error_count -gt 0 ]; then
        log "⚠️ Encontrados $error_count erros no log do Nginx"
    else
        log "✅ Nenhum erro encontrado no log do Nginx"
    fi
fi

log "🎉 ATUALIZAÇÃO DO SISTEMA CONCLUÍDA!"
log "====================================="
log "📅 Data: $(date)"
log "✅ Sistema atualizado e funcionando"
