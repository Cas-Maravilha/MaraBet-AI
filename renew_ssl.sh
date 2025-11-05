#!/bin/bash
# Script de Renovação SSL - MaraBet AI
# Renovação automática de certificados Let's Encrypt

# Configurações
LOG_FILE="/var/log/marabet-ssl-renewal.log"
COMPOSE_FILE="/opt/marabet/docker-compose-ssl.yml"

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "🔄 Iniciando renovação de certificados SSL..."

# Renovar certificados
certbot renew --quiet --deploy-hook "systemctl reload nginx"

if [ $? -eq 0 ]; then
    log "✅ Certificados renovados com sucesso!"
    
    # Copiar certificados para Docker
    cp -r /etc/letsencrypt/* /opt/marabet/certbot/conf/
    
    # Recarregar Nginx no Docker
    docker-compose -f $COMPOSE_FILE exec nginx nginx -s reload
    
    log "✅ Nginx recarregado com novos certificados!"
    
    # Verificar SSL
    DOMAIN=$(grep "server_name" /opt/marabet/nginx/nginx-ssl.conf | head -1 | awk '{print $2}' | sed 's/;//')
    
    SSL_EXPIRY=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates | grep "notAfter" | cut -d= -f2)
    
    log "📅 Certificado válido até: $SSL_EXPIRY"
    
else
    log "❌ Falha na renovação de certificados!"
    
    # Enviar alerta (pode integrar com Telegram/Email)
    # curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage"     #     -d "chat_id=$TELEGRAM_CHAT_ID"     #     -d "text=⚠️ Falha na renovação SSL do MaraBet AI!"
fi

log "🏁 Renovação concluída!"
