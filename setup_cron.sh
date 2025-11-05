#!/bin/bash
# Script para configurar Cron Job - MaraBet AI

echo "⏰ MARABET AI - CONFIGURAÇÃO DE CRON JOB"
echo "========================================"

# Configurações
BACKUP_SCRIPT="/home/ubuntu/marabet-ai/backup_script.sh"
CRON_JOB="0 2 * * * $BACKUP_SCRIPT >> /var/log/marabet_backup.log 2>&1"

echo "📅 Configurando backup diário às 02:00..."

# Adicionar cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job configurado com sucesso"
    echo "📋 Backup será executado diariamente às 02:00"
else
    echo "❌ Falha ao configurar cron job"
    exit 1
fi

# Verificar cron job
echo "🔍 Verificando cron job..."
crontab -l | grep marabet

echo "🎉 CONFIGURAÇÃO DE CRON JOB CONCLUÍDA!"
