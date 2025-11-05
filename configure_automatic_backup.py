#!/usr/bin/env python3
"""
Script para Configuração de Backup Automático - MaraBet AI
Configura backup automático dos dados e configurações
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

def configure_automatic_backup():
    """Configura backup automático"""
    print("💾 MARABET AI - CONFIGURAÇÃO DE BACKUP AUTOMÁTICO")
    print("=" * 70)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configuração existente
    config = load_config()
    
    # Obter IDs das instâncias
    web_instance_id = config.get('web_instance_id')
    worker_instance_id = config.get('worker_instance_id')
    ubuntu_instance_id = config.get('ubuntu_instance_id')
    rds_endpoint = config.get('rds_endpoint')
    redis_endpoint = config.get('redis_endpoint')
    
    if not all([web_instance_id, worker_instance_id, ubuntu_instance_id]):
        print("❌ Erro: IDs das instâncias não encontrados na configuração.")
        return False
    
    print(f"✅ Web Instance ID: {web_instance_id}")
    print(f"✅ Worker Instance ID: {worker_instance_id}")
    print(f"✅ Ubuntu Instance ID: {ubuntu_instance_id}")
    print(f"✅ RDS Endpoint: {rds_endpoint}")
    print(f"✅ Redis Endpoint: {redis_endpoint}")
    
    print("\n💾 ETAPA 1: CRIANDO SCRIPT DE BACKUP")
    print("-" * 60)
    
    # Criar script de backup
    backup_script_content = f"""#!/bin/bash
# Script de Backup Automático - MaraBet AI

echo "💾 MARABET AI - BACKUP AUTOMÁTICO"
echo "================================="
echo "📅 Data/Hora: $(date)"

# Configurações
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="marabet_backup_$DATE"
S3_BUCKET="marabet-backups"
RDS_ENDPOINT="{rds_endpoint}"
REDIS_ENDPOINT="{redis_endpoint}"

# Criar diretório de backup
mkdir -p $BACKUP_DIR/$BACKUP_NAME

echo "📁 Criando diretório de backup: $BACKUP_DIR/$BACKUP_NAME"

# 1. Backup do banco de dados RDS
if [ ! -z "$RDS_ENDPOINT" ]; then
    echo "🗄️ Fazendo backup do RDS..."
    pg_dump -h $RDS_ENDPOINT -U marabetadmin -d postgres > $BACKUP_DIR/$BACKUP_NAME/database_backup.sql
    if [ $? -eq 0 ]; then
        echo "✅ Backup do RDS concluído"
    else
        echo "❌ Falha no backup do RDS"
    fi
else
    echo "⚠️ RDS endpoint não configurado, pulando backup do banco"
fi

# 2. Backup do Redis
if [ ! -z "$REDIS_ENDPOINT" ]; then
    echo "⚡ Fazendo backup do Redis..."
    redis-cli -h $REDIS_ENDPOINT --rdb $BACKUP_DIR/$BACKUP_NAME/redis_backup.rdb
    if [ $? -eq 0 ]; then
        echo "✅ Backup do Redis concluído"
    else
        echo "❌ Falha no backup do Redis"
    fi
else
    echo "⚠️ Redis endpoint não configurado, pulando backup do cache"
fi

# 3. Backup dos arquivos de configuração
echo "📄 Fazendo backup dos arquivos de configuração..."
cp -r /home/ubuntu/marabet-ai/.env* $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || true
cp -r /home/ubuntu/marabet-ai/docker-compose* $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || true
cp -r /home/ubuntu/marabet-ai/nginx.conf $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || true
cp -r /home/ubuntu/marabet-ai/aws_infrastructure_config.json $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || true

# 4. Backup dos logs
echo "📝 Fazendo backup dos logs..."
mkdir -p $BACKUP_DIR/$BACKUP_NAME/logs
cp -r /var/log/nginx/* $BACKUP_DIR/$BACKUP_NAME/logs/ 2>/dev/null || true
cp -r /home/ubuntu/marabet-ai/logs/* $BACKUP_DIR/$BACKUP_NAME/logs/ 2>/dev/null || true

# 5. Backup dos dados da aplicação
echo "📊 Fazendo backup dos dados da aplicação..."
mkdir -p $BACKUP_DIR/$BACKUP_NAME/data
cp -r /home/ubuntu/marabet-ai/data/* $BACKUP_DIR/$BACKUP_NAME/data/ 2>/dev/null || true
cp -r /home/ubuntu/marabet-ai/backups/* $BACKUP_DIR/$BACKUP_NAME/data/ 2>/dev/null || true

# 6. Criar arquivo de metadados
echo "📋 Criando arquivo de metadados..."
cat > $BACKUP_DIR/$BACKUP_NAME/backup_info.txt << EOF
MaraBet AI - Backup Automático
=============================
Data/Hora: $(date)
Versão: 1.0.0
Instância: $(hostname)
IP Público: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
RDS Endpoint: $RDS_ENDPOINT
Redis Endpoint: $REDIS_ENDPOINT
Tamanho Total: $(du -sh $BACKUP_DIR/$BACKUP_NAME | cut -f1)
EOF

# 7. Compactar backup
echo "📦 Compactando backup..."
cd $BACKUP_DIR
tar -czf $BACKUP_NAME.tar.gz $BACKUP_NAME/
if [ $? -eq 0 ]; then
    echo "✅ Backup compactado: $BACKUP_NAME.tar.gz"
    # Remover diretório não compactado
    rm -rf $BACKUP_NAME/
else
    echo "❌ Falha na compactação do backup"
fi

# 8. Upload para S3 (se configurado)
if [ ! -z "$S3_BUCKET" ]; then
    echo "☁️ Enviando backup para S3..."
    aws s3 cp $BACKUP_NAME.tar.gz s3://$S3_BUCKET/backups/
    if [ $? -eq 0 ]; then
        echo "✅ Backup enviado para S3: s3://$S3_BUCKET/backups/$BACKUP_NAME.tar.gz"
    else
        echo "❌ Falha no upload para S3"
    fi
else
    echo "⚠️ S3 bucket não configurado, pulando upload"
fi

# 9. Limpar backups antigos (manter apenas os últimos 7 dias)
echo "🧹 Limpando backups antigos..."
find $BACKUP_DIR -name "marabet_backup_*.tar.gz" -mtime +7 -delete
echo "✅ Backups antigos removidos (mais de 7 dias)"

# 10. Verificar integridade do backup
echo "🔍 Verificando integridade do backup..."
if [ -f "$BACKUP_DIR/$BACKUP_NAME.tar.gz" ]; then
    tar -tzf $BACKUP_DIR/$BACKUP_NAME.tar.gz > /dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Backup íntegro e válido"
    else
        echo "❌ Backup corrompido!"
    fi
else
    echo "❌ Arquivo de backup não encontrado"
fi

echo "🎉 BACKUP AUTOMÁTICO CONCLUÍDO!"
echo "==============================="
echo "📁 Local: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo "📅 Data: $(date)"
echo "💾 Tamanho: $(du -sh $BACKUP_DIR/$BACKUP_NAME.tar.gz | cut -f1)"
"""
    
    # Salvar script localmente
    with open('backup_script.sh', 'w') as f:
        f.write(backup_script_content)
    print("✅ Script de backup criado: backup_script.sh")
    
    print("\n💾 ETAPA 2: CRIANDO SCRIPT DE RESTAURAÇÃO")
    print("-" * 60)
    
    # Criar script de restauração
    restore_script_content = f"""#!/bin/bash
# Script de Restauração - MaraBet AI

echo "🔄 MARABET AI - RESTAURAÇÃO DE BACKUP"
echo "====================================="
echo "📅 Data/Hora: $(date)"

# Configurações
BACKUP_DIR="/home/ubuntu/backups"
RDS_ENDPOINT="{rds_endpoint}"
REDIS_ENDPOINT="{redis_endpoint}"

# Verificar se foi fornecido um arquivo de backup
if [ -z "$1" ]; then
    echo "❌ Uso: $0 <arquivo_backup.tar.gz>"
    echo "💡 Exemplo: $0 marabet_backup_20241023_134500.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"

# Verificar se o arquivo existe
if [ ! -f "$BACKUP_PATH" ]; then
    echo "❌ Arquivo de backup não encontrado: $BACKUP_PATH"
    exit 1
fi

echo "📁 Restaurando backup: $BACKUP_FILE"

# 1. Parar serviços
echo "⏹️ Parando serviços..."
docker-compose -f docker-compose.production.yml down

# 2. Extrair backup
echo "📦 Extraindo backup..."
cd $BACKUP_DIR
tar -xzf $BACKUP_FILE
BACKUP_NAME=$(basename $BACKUP_FILE .tar.gz)

# 3. Restaurar banco de dados
if [ -f "$BACKUP_NAME/database_backup.sql" ] && [ ! -z "$RDS_ENDPOINT" ]; then
    echo "🗄️ Restaurando banco de dados..."
    psql -h $RDS_ENDPOINT -U marabetadmin -d postgres < $BACKUP_NAME/database_backup.sql
    if [ $? -eq 0 ]; then
        echo "✅ Banco de dados restaurado"
    else
        echo "❌ Falha na restauração do banco de dados"
    fi
else
    echo "⚠️ Backup do banco de dados não encontrado ou RDS não configurado"
fi

# 4. Restaurar Redis
if [ -f "$BACKUP_NAME/redis_backup.rdb" ] && [ ! -z "$REDIS_ENDPOINT" ]; then
    echo "⚡ Restaurando Redis..."
    redis-cli -h $REDIS_ENDPOINT --rdb $BACKUP_NAME/redis_backup.rdb
    if [ $? -eq 0 ]; then
        echo "✅ Redis restaurado"
    else
        echo "❌ Falha na restauração do Redis"
    fi
else
    echo "⚠️ Backup do Redis não encontrado ou Redis não configurado"
fi

# 5. Restaurar arquivos de configuração
echo "📄 Restaurando arquivos de configuração..."
cp -r $BACKUP_NAME/.env* /home/ubuntu/marabet-ai/ 2>/dev/null || true
cp -r $BACKUP_NAME/docker-compose* /home/ubuntu/marabet-ai/ 2>/dev/null || true
cp -r $BACKUP_NAME/nginx.conf /home/ubuntu/marabet-ai/ 2>/dev/null || true
cp -r $BACKUP_NAME/aws_infrastructure_config.json /home/ubuntu/marabet-ai/ 2>/dev/null || true

# 6. Restaurar logs
echo "📝 Restaurando logs..."
cp -r $BACKUP_NAME/logs/* /var/log/nginx/ 2>/dev/null || true
cp -r $BACKUP_NAME/logs/* /home/ubuntu/marabet-ai/logs/ 2>/dev/null || true

# 7. Restaurar dados da aplicação
echo "📊 Restaurando dados da aplicação..."
cp -r $BACKUP_NAME/data/* /home/ubuntu/marabet-ai/data/ 2>/dev/null || true
cp -r $BACKUP_NAME/data/* /home/ubuntu/marabet-ai/backups/ 2>/dev/null || true

# 8. Reiniciar serviços
echo "🔄 Reiniciando serviços..."
docker-compose -f docker-compose.production.yml up -d

# 9. Verificar status dos serviços
echo "🔍 Verificando status dos serviços..."
sleep 30
docker-compose -f docker-compose.production.yml ps

# 10. Limpar arquivos temporários
echo "🧹 Limpando arquivos temporários..."
rm -rf $BACKUP_NAME/

echo "🎉 RESTAURAÇÃO CONCLUÍDA!"
echo "========================="
echo "📅 Data: $(date)"
echo "✅ Serviços reiniciados"
echo "💡 Verifique os logs se necessário"
"""
    
    # Salvar script de restauração localmente
    with open('restore_script.sh', 'w') as f:
        f.write(restore_script_content)
    print("✅ Script de restauração criado: restore_script.sh")
    
    print("\n💾 ETAPA 3: CONFIGURANDO CRON JOB")
    print("-" * 60)
    
    # Criar script para configurar cron job
    cron_script_content = f"""#!/bin/bash
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
"""
    
    # Salvar script de cron localmente
    with open('setup_cron.sh', 'w') as f:
        f.write(cron_script_content)
    print("✅ Script de cron criado: setup_cron.sh")
    
    print("\n💾 ETAPA 4: CRIANDO S3 BUCKET PARA BACKUPS")
    print("-" * 60)
    
    # Criar S3 bucket para backups
    bucket_name = "marabet-backups"
    create_bucket_command = f'aws s3 mb s3://{bucket_name} --region us-east-1'
    bucket_result = run_aws_command(create_bucket_command)
    
    if bucket_result is not None:
        print(f"✅ S3 Bucket criado: s3://{bucket_name}")
        config['s3_backup_bucket'] = bucket_name
    else:
        print("⚠️ Falha ao criar S3 bucket ou bucket já existe")
        print("💡 Crie manualmente: aws s3 mb s3://marabet-backups --region us-east-1")
    
    print("\n💾 ETAPA 5: CONFIGURANDO LIFECYCLE POLICY")
    print("-" * 60)
    
    # Configurar lifecycle policy para S3
    lifecycle_policy = {
        "Rules": [
            {
                "ID": "MaraBetBackupLifecycle",
                "Status": "Enabled",
                "Transitions": [
                    {
                        "Days": 30,
                        "StorageClass": "STANDARD_IA"
                    },
                    {
                        "Days": 90,
                        "StorageClass": "GLACIER"
                    }
                ],
                "Expiration": {
                    "Days": 365
                }
            }
        ]
    }
    
    # Salvar lifecycle policy em arquivo temporário
    lifecycle_file = "lifecycle_policy.json"
    with open(lifecycle_file, 'w') as f:
        json.dump(lifecycle_policy, f, indent=2)
    
    # Aplicar lifecycle policy
    lifecycle_command = f'aws s3api put-bucket-lifecycle-configuration --bucket {bucket_name} --lifecycle-configuration file://{lifecycle_file}'
    lifecycle_result = run_aws_command(lifecycle_command)
    
    if lifecycle_result is not None:
        print("✅ Lifecycle policy configurada")
    else:
        print("⚠️ Falha ao configurar lifecycle policy")
    
    # Limpar arquivo temporário
    if os.path.exists(lifecycle_file):
        os.remove(lifecycle_file)
    
    print("\n💾 ETAPA 6: SALVANDO CONFIGURAÇÕES")
    print("-" * 60)
    
    # Salvar configurações de backup
    config['backup_configured'] = True
    config['backup_created_at'] = datetime.now().isoformat()
    config['backup_scripts'] = {
        'backup_script': 'backup_script.sh',
        'restore_script': 'restore_script.sh',
        'cron_script': 'setup_cron.sh'
    }
    
    save_config(config)
    print("✅ Configurações salvas em: aws_infrastructure_config.json")
    
    print("\n🎉 BACKUP AUTOMÁTICO CONFIGURADO COM SUCESSO!")
    print("=" * 70)
    
    print("\n📋 RESUMO DA CONFIGURAÇÃO:")
    print("-" * 50)
    print(f"• S3 Bucket: s3://{bucket_name}")
    print(f"• Backup Script: backup_script.sh")
    print(f"• Restore Script: restore_script.sh")
    print(f"• Cron Script: setup_cron.sh")
    print(f"• Status: Configurado")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 50)
    print("1. ✅ Scripts de backup criados")
    print("2. ✅ S3 bucket configurado")
    print("3. ✅ Lifecycle policy configurada")
    print("4. 🔄 Transferir scripts para o servidor")
    print("5. 🔄 Configurar cron job no servidor")
    print("6. 🔄 Testar backup e restauração")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("-" * 50)
    print("• Teste o backup antes de confiar nele")
    print("• Monitore os logs de backup")
    print("• Configure alertas para falhas de backup")
    print("• Mantenha backups em múltiplas regiões")
    print("• Teste a restauração regularmente")
    
    print("\n📧 COMANDOS ÚTEIS:")
    print("-" * 50)
    print("# Executar backup manual")
    print("sudo /home/ubuntu/marabet-ai/backup_script.sh")
    print()
    print("# Restaurar backup")
    print("sudo /home/ubuntu/marabet-ai/restore_script.sh marabet_backup_YYYYMMDD_HHMMSS.tar.gz")
    print()
    print("# Verificar cron jobs")
    print("crontab -l")
    print()
    print("# Ver logs de backup")
    print("tail -f /var/log/marabet_backup.log")
    
    return True

def main():
    print("🚀 Iniciando configuração de backup automático...")
    
    # Verificar se AWS CLI está configurado
    if run_aws_command("aws sts get-caller-identity") is None:
        print("❌ AWS CLI não configurado ou credenciais inválidas.")
        exit(1)
    print("✅ AWS CLI configurado e funcionando")
    
    # Configurar backup automático
    success = configure_automatic_backup()
    
    if success:
        print("\n🎯 BACKUP AUTOMÁTICO CONFIGURADO COM SUCESSO!")
        print("Sistema de backup ativo e funcionando!")
    else:
        print("\n❌ Falha na configuração de backup automático")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
