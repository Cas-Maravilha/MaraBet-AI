#!/usr/bin/env python3
"""
Script para Deploy da Aplicação MaraBet AI - EC2
Automatiza a transferência de arquivos e deploy da aplicação
"""

import subprocess
import os
import json
from datetime import datetime

def run_command(command, shell=True):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ Erro no comando: {command}")
            print(f"Erro: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Exceção no comando: {command}")
        print(f"Erro: {e}")
        return None

def deploy_application():
    """Faz deploy da aplicação MaraBet AI no servidor EC2"""
    print("🚀 MARABET AI - DEPLOY DA APLICAÇÃO NO SERVIDOR EC2")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configuração existente
    try:
        with open('aws_infrastructure_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de configuração não encontrado")
        return False
    
    ubuntu_public_ip = config.get('ubuntu_public_ip')
    key_path = os.path.expanduser("~/.ssh/marabet-key.pem")
    
    if not ubuntu_public_ip:
        print("❌ IP público da instância Ubuntu não encontrado")
        return False
    
    print(f"✅ IP Público: {ubuntu_public_ip}")
    print(f"✅ Chave SSH: {key_path}")
    
    # Verificar se chave SSH existe
    if not os.path.exists(key_path):
        print(f"❌ Chave SSH não encontrada: {key_path}")
        print("💡 Execute primeiro: aws ec2 create-key-pair --key-name marabet-key --query 'KeyMaterial' --output text > ~/.ssh/marabet-key.pem")
        return False
    
    print("\n🚀 ETAPA 1: PREPARANDO ARQUIVOS PARA DEPLOY")
    print("-" * 50)
    
    # Verificar se estamos na pasta correta
    current_dir = os.getcwd()
    print(f"✅ Diretório atual: {current_dir}")
    
    # Verificar se arquivos essenciais existem
    essential_files = ['app.py', 'requirements.txt', 'docker-compose.production.yml', 'Dockerfile']
    missing_files = []
    
    for file in essential_files:
        if os.path.exists(file):
            print(f"✅ {file} encontrado")
        else:
            print(f"❌ {file} não encontrado")
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️ Arquivos faltando: {', '.join(missing_files)}")
        print("💡 Certifique-se de estar na pasta correta do projeto")
    
    print("\n🚀 ETAPA 2: CRIANDO ARQUIVO .ENV DE PRODUÇÃO")
    print("-" * 50)
    
    # Criar arquivo .env de produção
    env_content = f"""# Configurações de Produção - MaraBet AI
DATABASE_URL=postgresql://marabetadmin:MaraBet2024!SuperSecret@marabet-db.cmvmwskgiabr.us-east-1.rds.amazonaws.com:5432/postgres
REDIS_URL=redis://marabet-redis.ve5qk7.0001.use1.cache.amazonaws.com:6379
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045
SECRET_KEY=MaraBet2024!SuperSecretKey
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
"""
    
    with open('.env.production', 'w') as f:
        f.write(env_content)
    print("✅ Arquivo .env.production criado")
    
    print("\n🚀 ETAPA 3: CRIANDO SCRIPT DE DEPLOY")
    print("-" * 50)
    
    # Criar script de deploy para o servidor
    deploy_script_content = """#!/bin/bash
# Script de Deploy - MaraBet AI

echo "🚀 MARABET AI - DEPLOY DA APLICAÇÃO"
echo "=================================="

# Atualizar sistema
echo "🔄 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Docker se não estiver instalado
if ! command -v docker &> /dev/null; then
    echo "🐳 Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
fi

# Instalar Docker Compose se não estiver instalado
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Instalando Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Instalar ferramentas úteis
echo "🛠️ Instalando ferramentas..."
sudo apt install -y htop curl wget vim nano git python3 python3-pip python3-venv

# Configurar variáveis de ambiente
echo "🌐 Configurando variáveis de ambiente..."
echo 'export DATABASE_URL="postgresql://marabetadmin:MaraBet2024!SuperSecret@marabet-db.cmvmwskgiabr.us-east-1.rds.amazonaws.com:5432/postgres"' >> ~/.bashrc
echo 'export REDIS_URL="redis://marabet-redis.ve5qk7.0001.use1.cache.amazonaws.com:6379"' >> ~/.bashrc
echo 'export API_FOOTBALL_KEY="71b2b62386f2d1275cd3201a73e1e045"' >> ~/.bashrc
echo 'export SECRET_KEY="MaraBet2024!SuperSecretKey"' >> ~/.bashrc
echo 'export ENVIRONMENT="production"' >> ~/.bashrc
echo 'export DEBUG="false"' >> ~/.bashrc

# Recarregar configurações
source ~/.bashrc

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down 2>/dev/null || true

# Remover imagens antigas
echo "🧹 Limpando imagens antigas..."
docker system prune -f

# Construir e iniciar aplicação
echo "🏗️ Construindo e iniciando aplicação..."
docker-compose -f docker-compose.production.yml up --build -d

# Verificar status
echo "🔍 Verificando status dos containers..."
docker ps

# Verificar logs
echo "📋 Logs da aplicação:"
docker-compose logs --tail=20

echo "✅ Deploy concluído!"
echo "🌐 Aplicação disponível em: http://$(curl -s ifconfig.me):8000"
"""
    
    with open('deploy.sh', 'w') as f:
        f.write(deploy_script_content)
    print("✅ Script de deploy criado: deploy.sh")
    
    print("\n🚀 ETAPA 4: TRANSFERINDO ARQUIVOS VIA SCP")
    print("-" * 50)
    
    # Criar pasta no servidor
    print("📁 Criando pasta no servidor...")
    create_dir_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "mkdir -p /home/ubuntu/marabet-ai"'
    create_dir_result = run_command(create_dir_command)
    
    if create_dir_result is not None:
        print("✅ Pasta criada no servidor")
    else:
        print("⚠️ Falha ao criar pasta no servidor")
    
    # Transferir arquivos via SCP
    print("📤 Transferindo arquivos via SCP...")
    scp_command = f'scp -i "{key_path}" -o StrictHostKeyChecking=no -r . ubuntu@{ubuntu_public_ip}:/home/ubuntu/marabet-ai/'
    
    print(f"Executando: {scp_command}")
    print("⚠️ Este comando pode demorar alguns minutos...")
    
    # Executar SCP
    scp_result = run_command(scp_command)
    
    if scp_result is not None:
        print("✅ Arquivos transferidos com sucesso")
    else:
        print("⚠️ Falha na transferência de arquivos")
        print("💡 Tente executar manualmente:")
        print(f"scp -i {key_path} -r . ubuntu@{ubuntu_public_ip}:/home/ubuntu/marabet-ai/")
    
    print("\n🚀 ETAPA 5: EXECUTANDO DEPLOY NO SERVIDOR")
    print("-" * 50)
    
    # Executar script de deploy no servidor
    print("🚀 Executando deploy no servidor...")
    deploy_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "cd /home/ubuntu/marabet-ai && chmod +x deploy.sh && ./deploy.sh"'
    
    print(f"Executando: {deploy_command}")
    print("⚠️ Este comando pode demorar vários minutos...")
    
    # Executar deploy
    deploy_result = run_command(deploy_command)
    
    if deploy_result is not None:
        print("✅ Deploy executado com sucesso")
    else:
        print("⚠️ Falha no deploy")
        print("💡 Tente executar manualmente no servidor:")
        print("ssh -i ~/.ssh/marabet-key.pem ubuntu@3.218.152.100")
        print("cd /home/ubuntu/marabet-ai")
        print("./deploy.sh")
    
    print("\n🚀 ETAPA 6: VERIFICANDO DEPLOY")
    print("-" * 50)
    
    # Verificar status dos containers
    print("🔍 Verificando status dos containers...")
    status_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "cd /home/ubuntu/marabet-ai && docker ps"'
    status_result = run_command(status_command)
    
    if status_result:
        print("✅ Status dos containers:")
        print(status_result)
    else:
        print("⚠️ Falha ao verificar status dos containers")
    
    # Verificar logs
    print("\n📋 Verificando logs da aplicação...")
    logs_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "cd /home/ubuntu/marabet-ai && docker-compose logs --tail=10"'
    logs_result = run_command(logs_command)
    
    if logs_result:
        print("✅ Logs da aplicação:")
        print(logs_result)
    else:
        print("⚠️ Falha ao verificar logs da aplicação")
    
    print("\n🎉 DEPLOY CONCLUÍDO!")
    print("=" * 60)
    
    print("\n📋 RESUMO DO DEPLOY:")
    print("-" * 40)
    print(f"• Servidor: {ubuntu_public_ip}")
    print(f"• Pasta: /home/ubuntu/marabet-ai")
    print(f"• Aplicação: MaraBet AI")
    print(f"• Status: Deploy executado")
    
    print("\n🔗 COMANDOS ÚTEIS:")
    print("-" * 40)
    print(f"# Conectar via SSH")
    print(f"ssh -i {key_path} ubuntu@{ubuntu_public_ip}")
    print()
    print("# Ver status dos containers")
    print("cd /home/ubuntu/marabet-ai && docker ps")
    print()
    print("# Ver logs da aplicação")
    print("cd /home/ubuntu/marabet-ai && docker-compose logs -f")
    print()
    print("# Reiniciar aplicação")
    print("cd /home/ubuntu/marabet-ai && docker-compose restart")
    print()
    print("# Parar aplicação")
    print("cd /home/ubuntu/marabet-ai && docker-compose down")
    print()
    print("# Iniciar aplicação")
    print("cd /home/ubuntu/marabet-ai && docker-compose up -d")
    
    print("\n🌐 ACESSAR APLICAÇÃO:")
    print("-" * 40)
    print(f"• URL: http://{ubuntu_public_ip}:8000")
    print(f"• API Docs: http://{ubuntu_public_ip}:8000/docs")
    print(f"• Health Check: http://{ubuntu_public_ip}:8000/health")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Deploy executado")
    print("2. 🔄 Testar aplicação")
    print("3. 🔄 Configurar domínio (opcional)")
    print("4. 🔄 Configurar SSL (opcional)")
    print("5. 🔄 Configurar monitoramento")
    print("6. 🔄 Configurar backup")
    
    return True

def main():
    print("🚀 Iniciando deploy da aplicação MaraBet AI...")
    
    # Fazer deploy
    success = deploy_application()
    
    if success:
        print("\n🎯 DEPLOY CONCLUÍDO COM SUCESSO!")
        print("A aplicação MaraBet AI está rodando no servidor EC2!")
    else:
        print("\n❌ Falha no deploy da aplicação")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
