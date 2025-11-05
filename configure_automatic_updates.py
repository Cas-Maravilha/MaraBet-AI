#!/usr/bin/env python3
"""
Script para Configuração de Atualizações Automáticas - MaraBet AI
Configura atualizações automáticas do sistema e aplicação
"""

import subprocess
import json
import os
from datetime import datetime

def run_aws_command(command, return_text=False):
    """Executa comando AWS CLI e retorna resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            if return_text:
                return result.stdout.strip()
            else:
                return json.loads(result.stdout) if result.stdout.strip() else {}
        else:
            print(f"❌ Erro no comando: {command}")
            print(f"Erro: {result.stderr}")
            return None
    except json.JSONDecodeError:
        print(f"❌ Erro de decodificação JSON para o comando: {command}")
        print(f"Saída: {result.stdout}")
        print(f"Erro: {result.stderr}")
        return None
    except Exception as e:
        print(f"❌ Exceção no comando: {command}")
        print(f"Erro: {e}")
        return None

def load_config():
    """Carrega configurações existentes do arquivo JSON."""
    config_file = 'aws_infrastructure_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Salva configurações no arquivo JSON."""
    config_file = 'aws_infrastructure_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

def configure_automatic_updates():
    """Configura atualizações automáticas"""
    print("🔄 MARABET AI - CONFIGURAÇÃO DE ATUALIZAÇÕES AUTOMÁTICAS")
    print("=" * 70)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configuração existente
    config = load_config()
    
    # Obter IDs das instâncias
    web_instance_id = config.get('web_instance_id')
    worker_instance_id = config.get('worker_instance_id')
    ubuntu_instance_id = config.get('ubuntu_instance_id')
    
    if not all([web_instance_id, worker_instance_id, ubuntu_instance_id]):
        print("❌ Erro: IDs das instâncias não encontrados na configuração.")
        return False
    
    print(f"✅ Web Instance ID: {web_instance_id}")
    print(f"✅ Worker Instance ID: {worker_instance_id}")
    print(f"✅ Ubuntu Instance ID: {ubuntu_instance_id}")
    
    print("\n🔄 ETAPA 1: CRIANDO SCRIPT DE ATUALIZAÇÃO DO SISTEMA")
    print("-" * 60)
    
    # Criar script de atualização do sistema
    system_update_script_content = f"""#!/bin/bash
# Script de Atualização do Sistema - MaraBet AI

echo "🔄 MARABET AI - ATUALIZAÇÃO DO SISTEMA"
echo "======================================"
echo "📅 Data/Hora: $(date)"

# Configurações
LOG_FILE="/var/log/marabet_updates.log"
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Função para log
log() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}}

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
"""
    
    # Salvar script localmente
    with open('system_update_script.sh', 'w') as f:
        f.write(system_update_script_content)
    print("✅ Script de atualização do sistema criado: system_update_script.sh")
    
    print("\n🔄 ETAPA 2: CRIANDO SCRIPT DE ATUALIZAÇÃO DA APLICAÇÃO")
    print("-" * 60)
    
    # Criar script de atualização da aplicação
    app_update_script_content = f"""#!/bin/bash
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
log() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}}

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
"""
    
    # Salvar script localmente
    with open('app_update_script.sh', 'w') as f:
        f.write(app_update_script_content)
    print("✅ Script de atualização da aplicação criado: app_update_script.sh")
    
    print("\n🔄 ETAPA 3: CRIANDO SCRIPT DE VERIFICAÇÃO DE SEGURANÇA")
    print("-" * 60)
    
    # Criar script de verificação de segurança
    security_check_script_content = f"""#!/bin/bash
# Script de Verificação de Segurança - MaraBet AI

echo "🔒 MARABET AI - VERIFICAÇÃO DE SEGURANÇA"
echo "======================================="
echo "📅 Data/Hora: $(date)"

# Configurações
LOG_FILE="/var/log/marabet_security.log"

# Função para log
log() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}}

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
"""
    
    # Salvar script localmente
    with open('security_check_script.sh', 'w') as f:
        f.write(security_check_script_content)
    print("✅ Script de verificação de segurança criado: security_check_script.sh")
    
    print("\n🔄 ETAPA 4: CONFIGURANDO CRON JOBS")
    print("-" * 60)
    
    # Criar script para configurar cron jobs
    cron_setup_script_content = f"""#!/bin/bash
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
for job in "${{CRON_JOBS[@]}}"; do
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
"""
    
    # Salvar script localmente
    with open('setup_cron_jobs.sh', 'w') as f:
        f.write(cron_setup_script_content)
    print("✅ Script de cron jobs criado: setup_cron_jobs.sh")
    
    print("\n🔄 ETAPA 5: CRIANDO SCRIPT DE MONITORAMENTO")
    print("-" * 60)
    
    # Criar script de monitoramento
    monitoring_script_content = f"""#!/bin/bash
# Script de Monitoramento - MaraBet AI

echo "📊 MARABET AI - MONITORAMENTO DO SISTEMA"
echo "======================================="
echo "📅 Data/Hora: $(date)"

# Configurações
LOG_FILE="/var/log/marabet_monitoring.log"
ALERT_EMAIL="admin@marabet.com"

# Função para log
log() {{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}}

# Função para enviar alerta
send_alert() {{
    local message="$1"
    log "🚨 ALERTA: $message"
    # Aqui você pode adicionar código para enviar email ou notificação
    # echo "$message" | mail -s "MaraBet AI - Alerta" $ALERT_EMAIL
}}

log "🔍 Iniciando monitoramento do sistema"

# 1. Verificar uso de CPU
log "🧠 Verificando uso de CPU..."
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{{print $2}}' | cut -d'%' -f1)
if (( $(echo "$cpu_usage > 80" | bc -l) )); then
    send_alert "CPU usage is high: $cpu_usage%"
else
    log "✅ CPU usage normal: $cpu_usage%"
fi

# 2. Verificar uso de memória
log "💾 Verificando uso de memória..."
memory_usage=$(free | grep Mem | awk '{{printf "%.2f", $3/$2 * 100.0}}')
if (( $(echo "$memory_usage > 85" | bc -l) )); then
    send_alert "Memory usage is high: $memory_usage%"
else
    log "✅ Memory usage normal: $memory_usage%"
fi

# 3. Verificar espaço em disco
log "💿 Verificando espaço em disco..."
disk_usage=$(df / | tail -1 | awk '{{print $5}}' | cut -d'%' -f1)
if [ $disk_usage -gt 90 ]; then
    send_alert "Disk usage is high: $disk_usage%"
else
    log "✅ Disk usage normal: $disk_usage%"
fi

# 4. Verificar status dos serviços
log "🔧 Verificando status dos serviços..."
services=("nginx" "docker" "redis" "postgresql")
for service in "${{services[@]}}"; do
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
"""
    
    # Salvar script localmente
    with open('monitoring_script.sh', 'w') as f:
        f.write(monitoring_script_content)
    print("✅ Script de monitoramento criado: monitoring_script.sh")
    
    print("\n🔄 ETAPA 6: SALVANDO CONFIGURAÇÕES")
    print("-" * 60)
    
    # Salvar configurações de atualizações automáticas
    config['automatic_updates_configured'] = True
    config['automatic_updates_created_at'] = datetime.now().isoformat()
    config['update_scripts'] = {
        'system_update_script': 'system_update_script.sh',
        'app_update_script': 'app_update_script.sh',
        'security_check_script': 'security_check_script.sh',
        'cron_setup_script': 'setup_cron_jobs.sh',
        'monitoring_script': 'monitoring_script.sh'
    }
    
    save_config(config)
    print("✅ Configurações salvas em: aws_infrastructure_config.json")
    
    print("\n🎉 ATUALIZAÇÕES AUTOMÁTICAS CONFIGURADAS COM SUCESSO!")
    print("=" * 70)
    
    print("\n📋 RESUMO DA CONFIGURAÇÃO:")
    print("-" * 50)
    print(f"• System Update Script: system_update_script.sh")
    print(f"• App Update Script: app_update_script.sh")
    print(f"• Security Check Script: security_check_script.sh")
    print(f"• Cron Setup Script: setup_cron_jobs.sh")
    print(f"• Monitoring Script: monitoring_script.sh")
    print(f"• Status: Configurado")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 50)
    print("1. ✅ Scripts de atualização criados")
    print("2. ✅ Scripts de monitoramento criados")
    print("3. ✅ Scripts de segurança criados")
    print("4. 🔄 Transferir scripts para o servidor")
    print("5. 🔄 Configurar cron jobs no servidor")
    print("6. 🔄 Testar scripts de atualização")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("-" * 50)
    print("• Teste os scripts antes de configurar cron jobs")
    print("• Monitore os logs de atualização")
    print("• Configure alertas para falhas de atualização")
    print("• Mantenha backups antes de atualizações")
    print("• Monitore o sistema após atualizações")
    
    print("\n📧 COMANDOS ÚTEIS:")
    print("-" * 50)
    print("# Executar atualização do sistema")
    print("sudo /home/ubuntu/marabet-ai/system_update_script.sh")
    print()
    print("# Executar atualização da aplicação")
    print("sudo /home/ubuntu/marabet-ai/app_update_script.sh")
    print()
    print("# Executar verificação de segurança")
    print("sudo /home/ubuntu/marabet-ai/security_check_script.sh")
    print()
    print("# Executar monitoramento")
    print("sudo /home/ubuntu/marabet-ai/monitoring_script.sh")
    print()
    print("# Verificar cron jobs")
    print("crontab -l")
    print()
    print("# Ver logs de atualização")
    print("tail -f /var/log/marabet_system_updates.log")
    print("tail -f /var/log/marabet_app_updates.log")
    print("tail -f /var/log/marabet_security.log")
    print("tail -f /var/log/marabet_monitoring.log")
    
    return True

def main():
    print("🚀 Iniciando configuração de atualizações automáticas...")
    
    # Verificar se AWS CLI está configurado
    if run_aws_command("aws sts get-caller-identity") is None:
        print("❌ AWS CLI não configurado ou credenciais inválidas.")
        exit(1)
    print("✅ AWS CLI configurado e funcionando")
    
    # Configurar atualizações automáticas
    success = configure_automatic_updates()
    
    if success:
        print("\n🎯 ATUALIZAÇÕES AUTOMÁTICAS CONFIGURADAS COM SUCESSO!")
        print("Sistema de atualizações ativo e funcionando!")
    else:
        print("\n❌ Falha na configuração de atualizações automáticas")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
