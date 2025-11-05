#!/bin/bash
# Script para configurar Cron Jobs - MaraBet AI

echo "⏰ MARABET AI - CONFIGURAÇÃO DE CRON JOBS"
echo "========================================="

# Configurações
SYSTEM_UPDATE_SCRIPT="/home/ubuntu/marabet-ai/system_update_script.sh"
APP_UPDATE_SCRIPT="/home/ubuntu/marabet-ai/app_update_script.sh"
SECURITY_CHECK_SCRIPT="/home/ubuntu/marabet-ai/security_check_script.sh"

# Cron jobs
CRON_JOBS=(
    "0 2 * * 0 $SYSTEM_UPDATE_SCRIPT >> /var/log/marabet_system_updates.log 2>&1"
    "0 3 * * 1 $APP_UPDATE_SCRIPT >> /var/log/marabet_app_updates.log 2>&1"
    "0 4 * * * $SECURITY_CHECK_SCRIPT >> /var/log/marabet_security.log 2>&1"
)

echo "📅 Configurando cron jobs..."

# Adicionar cron jobs
for job in "${CRON_JOBS[@]}"; do
    (crontab -l 2>/dev/null; echo "$job") | crontab -
    if [ $? -eq 0 ]; then
        echo "✅ Cron job configurado: $job"
    else
        echo "❌ Falha ao configurar cron job: $job"
    fi
done

# Verificar cron jobs
echo "🔍 Verificando cron jobs..."
crontab -l | grep marabet

echo "🎉 CONFIGURAÇÃO DE CRON JOBS CONCLUÍDA!"
echo "======================================"
echo "📅 Atualização do sistema: Domingos às 02:00"
echo "📅 Atualização da aplicação: Segundas-feiras às 03:00"
echo "📅 Verificação de segurança: Diariamente às 04:00"
