#!/bin/bash
# Script de Verificação de Segurança - MaraBet AI

echo "🔒 MARABET AI - VERIFICAÇÃO DE SEGURANÇA"
echo "======================================="
echo "📅 Data/Hora: $(date)"

# Configurações
LOG_FILE="/var/log/marabet_security.log"

# Função para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "🔍 Iniciando verificação de segurança"

# 1. Verificar atualizações de segurança
log "🛡️ Verificando atualizações de segurança..."
apt list --upgradable | grep -i security

if [ $? -eq 0 ]; then
    log "⚠️ Atualizações de segurança disponíveis"
else
    log "✅ Nenhuma atualização de segurança pendente"
fi

# 2. Verificar portas abertas
log "🔌 Verificando portas abertas..."
netstat -tuln | grep LISTEN

# 3. Verificar processos suspeitos
log "🔍 Verificando processos suspeitos..."
ps aux | grep -E "(python|node|java)" | grep -v grep

# 4. Verificar logs de autenticação
log "🔐 Verificando logs de autenticação..."
if [ -f "/var/log/auth.log" ]; then
    failed_logins=$(grep "Failed password" /var/log/auth.log | wc -l)
    if [ $failed_logins -gt 0 ]; then
        log "⚠️ Encontrados $failed_logins tentativas de login falhadas"
    else
        log "✅ Nenhuma tentativa de login falhada encontrada"
    fi
fi

# 5. Verificar configuração do firewall
log "🔥 Verificando configuração do firewall..."
ufw status

# 6. Verificar certificados SSL
log "🔒 Verificando certificados SSL..."
if [ -f "/etc/letsencrypt/live/marabet.com/fullchain.pem" ]; then
    cert_expiry=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/marabet.com/fullchain.pem | cut -d= -f2)
    log "📅 Certificado SSL expira em: $cert_expiry"
else
    log "⚠️ Certificado SSL não encontrado"
fi

# 7. Verificar permissões de arquivos
log "📁 Verificando permissões de arquivos..."
find /home/ubuntu/marabet-ai -type f -perm 777 2>/dev/null

# 8. Verificar variáveis de ambiente
log "🌍 Verificando variáveis de ambiente..."
env | grep -E "(PASSWORD|SECRET|KEY)" | wc -l

# 9. Verificar logs de erro
log "📝 Verificando logs de erro..."
if [ -f "/var/log/nginx/error.log" ]; then
    error_count=$(grep -c "error" /var/log/nginx/error.log | tail -1)
    if [ $error_count -gt 0 ]; then
        log "⚠️ Encontrados $error_count erros no log do Nginx"
    else
        log "✅ Nenhum erro encontrado no log do Nginx"
    fi
fi

# 10. Verificar uso de recursos
log "💾 Verificando uso de recursos..."
df -h
free -h
uptime

log "🎉 VERIFICAÇÃO DE SEGURANÇA CONCLUÍDA!"
log "====================================="
log "📅 Data: $(date)"
log "✅ Verificação de segurança concluída"
