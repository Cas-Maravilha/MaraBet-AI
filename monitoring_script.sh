#!/bin/bash
# Script de Monitoramento - MaraBet AI

echo "📊 MARABET AI - MONITORAMENTO DO SISTEMA"
echo "======================================="
echo "📅 Data/Hora: $(date)"

# Configurações
LOG_FILE="/var/log/marabet_monitoring.log"
ALERT_EMAIL="admin@marabet.com"

# Função para log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Função para enviar alerta
send_alert() {
    local message="$1"
    log "🚨 ALERTA: $message"
    # Aqui você pode adicionar código para enviar email ou notificação
    # echo "$message" | mail -s "MaraBet AI - Alerta" $ALERT_EMAIL
}

log "🔍 Iniciando monitoramento do sistema"

# 1. Verificar uso de CPU
log "🧠 Verificando uso de CPU..."
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
if (( $(echo "$cpu_usage > 80" | bc -l) )); then
    send_alert "CPU usage is high: $cpu_usage%"
else
    log "✅ CPU usage normal: $cpu_usage%"
fi

# 2. Verificar uso de memória
log "💾 Verificando uso de memória..."
memory_usage=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
if (( $(echo "$memory_usage > 85" | bc -l) )); then
    send_alert "Memory usage is high: $memory_usage%"
else
    log "✅ Memory usage normal: $memory_usage%"
fi

# 3. Verificar espaço em disco
log "💿 Verificando espaço em disco..."
disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
if [ $disk_usage -gt 90 ]; then
    send_alert "Disk usage is high: $disk_usage%"
else
    log "✅ Disk usage normal: $disk_usage%"
fi

# 4. Verificar status dos serviços
log "🔧 Verificando status dos serviços..."
services=("nginx" "docker" "redis" "postgresql")
for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        log "✅ $service is running"
    else
        send_alert "$service is not running"
    fi
done

# 5. Verificar status da aplicação
log "🚀 Verificando status da aplicação..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log "✅ Application is healthy"
else
    send_alert "Application health check failed"
fi

# 6. Verificar logs de erro
log "📝 Verificando logs de erro..."
if [ -f "/var/log/nginx/error.log" ]; then
    error_count=$(grep -c "error" /var/log/nginx/error.log | tail -1)
    if [ $error_count -gt 10 ]; then
        send_alert "High number of errors in Nginx log: $error_count"
    else
        log "✅ Nginx log errors normal: $error_count"
    fi
fi

# 7. Verificar conectividade com banco de dados
log "🗄️ Verificando conectividade com banco de dados..."
if pg_isready -h marabet-db.cmvmwskgiabr.us-east-1.rds.amazonaws.com -p 5432 > /dev/null 2>&1; then
    log "✅ Database connection is healthy"
else
    send_alert "Database connection failed"
fi

# 8. Verificar conectividade com Redis
log "⚡ Verificando conectividade com Redis..."
if redis-cli -h marabet-redis.ve5qk7.0001.use1.cache.amazonaws.com ping > /dev/null 2>&1; then
    log "✅ Redis connection is healthy"
else
    send_alert "Redis connection failed"
fi

# 9. Verificar certificados SSL
log "🔒 Verificando certificados SSL..."
if [ -f "/etc/letsencrypt/live/marabet.com/fullchain.pem" ]; then
    cert_expiry=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/marabet.com/fullchain.pem | cut -d= -f2)
    days_until_expiry=$(( ($(date -d "$cert_expiry" +%s) - $(date +%s)) / 86400 ))
    if [ $days_until_expiry -lt 30 ]; then
        send_alert "SSL certificate expires in $days_until_expiry days"
    else
        log "✅ SSL certificate valid for $days_until_expiry days"
    fi
else
    send_alert "SSL certificate not found"
fi

# 10. Verificar backup
log "💾 Verificando backup..."
if [ -f "/home/ubuntu/backups/marabet_backup_$(date +%Y%m%d)*.tar.gz" ]; then
    log "✅ Backup for today exists"
else
    send_alert "No backup found for today"
fi

log "🎉 MONITORAMENTO CONCLUÍDO!"
log "=========================="
log "📅 Data: $(date)"
log "✅ Sistema monitorado"
