#!/bin/bash

################################################################################
# MARABET AI - CONFIGURAR CRON PARA BACKUP AUTOMÁTICO
# Adiciona job de backup ao crontab do usuário marabet
################################################################################

set -e

echo "========================================================================"
echo "⏰ MaraBet AI - Configurar Cron Backup"
echo "========================================================================"
echo ""

# Verificar se está rodando como marabet
if [ "$(whoami)" != "marabet" ]; then
    echo "[!] Este script deve ser executado como usuário marabet"
    echo ""
    echo "Execute:"
    echo "  sudo su - marabet"
    echo "  cd /opt/marabet"
    echo "  ./configurar_cron_backup.sh"
    exit 1
fi

################################################################################
# 1. VERIFICAR SCRIPT DE BACKUP
################################################################################

echo "1. Verificando script de backup..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

BACKUP_SCRIPT="/opt/marabet/backups/scripts/backup_to_s3.sh"

if [ -f "$BACKUP_SCRIPT" ]; then
    echo "[✓] Script de backup encontrado: $BACKUP_SCRIPT"
    
    # Verificar permissões
    if [ -x "$BACKUP_SCRIPT" ]; then
        echo "[✓] Script é executável"
    else
        echo "[!] Tornando script executável..."
        chmod +x "$BACKUP_SCRIPT"
        echo "[✓] Permissões corrigidas"
    fi
else
    echo "[✗] Script de backup não encontrado!"
    echo ""
    echo "Crie o script primeiro:"
    echo "  mkdir -p /opt/marabet/backups/scripts"
    echo "  # Copiar backup_to_s3.sh para este diretório"
    exit 1
fi

################################################################################
# 2. CRIAR DIRETÓRIO DE LOGS
################################################################################

echo ""
echo "2. Criando diretório de logs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

mkdir -p /opt/marabet/logs
mkdir -p /var/log/marabet

echo "[✓] Diretórios criados"

################################################################################
# 3. VERIFICAR CRONTAB ATUAL
################################################################################

echo ""
echo "3. Verificando crontab atual..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ver crontab atual
CURRENT_CRON=$(crontab -l 2>/dev/null || echo "")

if echo "$CURRENT_CRON" | grep -q "backup_to_s3.sh"; then
    echo "[!] Job de backup já existe no crontab"
    echo ""
    echo "Crontab atual:"
    crontab -l | grep backup
    echo ""
    
    read -p "Deseja reconfigurar? (y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "[!] Configuração cancelada"
        exit 0
    fi
    
    # Remover linha antiga
    crontab -l | grep -v backup_to_s3.sh | crontab -
    echo "[✓] Job antigo removido"
fi

################################################################################
# 4. ADICIONAR CRON JOB
################################################################################

echo ""
echo "4. Adicionando cron job..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Adicionar novo job
(crontab -l 2>/dev/null; echo "# MaraBet AI - Backup Automático") | crontab -
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/marabet/backups/scripts/backup_to_s3.sh >> /opt/marabet/logs/backup.log 2>&1") | crontab -

echo "[✓] Cron job adicionado"

################################################################################
# 5. VERIFICAR CONFIGURAÇÃO
################################################################################

echo ""
echo "5. Verificando configuração..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Crontab do usuário marabet:"
crontab -l

################################################################################
# 6. TESTAR BACKUP MANUALMENTE
################################################################################

echo ""
echo "6. Testando backup manualmente..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Executar backup agora para testar? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Executando backup de teste..."
    $BACKUP_SCRIPT
    
    echo ""
    echo "[✓] Backup de teste concluído!"
    echo ""
    echo "Verificar logs:"
    echo "  tail -50 /opt/marabet/logs/backup.log"
    echo ""
    echo "Verificar S3:"
    echo "  aws s3 ls s3://marabet-backups/daily/"
fi

################################################################################
# RESUMO
################################################################################

echo ""
echo "========================================================================"
echo "✅ CRON BACKUP CONFIGURADO!"
echo "========================================================================"
echo ""

echo "Configuração:"
echo "  • Script:        $BACKUP_SCRIPT"
echo "  • Frequência:    Diário às 02:00 (Africa/Luanda)"
echo "  • Log:           /opt/marabet/logs/backup.log"
echo "  • S3 Bucket:     s3://marabet-backups"
echo ""

echo "Schedule de Backups:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Daily:           Todo dia às 02:00 (retenção 30 dias)"
echo "  Weekly:          Domingo às 02:00 (retenção 90 dias)"
echo "  Monthly:         Dia 1 às 02:00 (retenção 365 dias)"
echo ""

echo "Próxima execução:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Calcular próxima execução às 02:00
NEXT_RUN=$(date -d "tomorrow 02:00" "+%Y-%m-%d %H:%M:%S")
echo "  $NEXT_RUN"
echo ""

echo "Comandos Úteis:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Ver crontab:"
echo "    crontab -l"
echo ""
echo "  Executar backup manualmente:"
echo "    $BACKUP_SCRIPT"
echo ""
echo "  Ver logs:"
echo "    tail -f /opt/marabet/logs/backup.log"
echo ""
echo "  Listar backups S3:"
echo "    aws s3 ls s3://marabet-backups/daily/"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "✅ Backup automático configurado!"
echo ""

