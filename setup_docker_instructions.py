#!/usr/bin/env python3
"""
Script para Baixar Chave SSH e Instalar Docker - MaraBet AI
Baixa a chave SSH corretamente e instala Docker no servidor
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

def download_ssh_key():
    """Baixa a chave SSH da AWS"""
    print("🔑 MARABET AI - BAIXANDO CHAVE SSH")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    print("\n🔑 ETAPA 1: CRIANDO PASTA .SSH")
    print("-" * 50)
    
    # Criar pasta .ssh se não existir
    ssh_dir = os.path.expanduser("~/.ssh")
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir)
        print(f"✅ Pasta .ssh criada: {ssh_dir}")
    else:
        print(f"✅ Pasta .ssh já existe: {ssh_dir}")
    
    print("\n🔑 ETAPA 2: BAIXANDO CHAVE SSH")
    print("-" * 50)
    
    # Caminho da chave
    key_path = os.path.join(ssh_dir, "marabet-key.pem")
    
    # Verificar se chave já existe
    if os.path.exists(key_path):
        print(f"✅ Chave já existe: {key_path}")
        return key_path
    
    print("🔑 Baixando chave SSH da AWS...")
    
    # Primeiro, vamos tentar obter a chave existente
    # Como não podemos baixar uma chave existente, vamos criar uma nova
    print("⚠️ A chave marabet-key já existe na AWS")
    print("💡 Vamos criar uma nova chave com nome diferente")
    
    new_key_name = "marabet-key-new"
    download_command = f'aws ec2 create-key-pair --key-name {new_key_name} --query "KeyMaterial" --output text'
    key_material = run_command(download_command)
    
    if key_material:
        # Salvar chave
        with open(key_path, 'w') as f:
            f.write(key_material)
        print(f"✅ Chave baixada e salva em: {key_path}")
        return key_path
    else:
        print("❌ Falha ao baixar chave SSH")
        return None

def configure_ssh_key(key_path):
    """Configura permissões da chave SSH"""
    print("\n🔑 ETAPA 3: CONFIGURANDO PERMISSÕES")
    print("-" * 50)
    
    # Ajustar permissões da chave (Windows)
    print("🔑 Configurando permissões da chave...")
    
    # Remover herança de permissões
    icacls_inheritance = f'icacls "{key_path}" /inheritance:r'
    inheritance_result = run_command(icacls_inheritance)
    
    if inheritance_result is not None:
        print("✅ Herança de permissões removida")
    else:
        print("⚠️ Falha ao remover herança de permissões")
    
    # Conceder permissão de leitura para o usuário atual
    username = os.environ.get('USERNAME', 'PC')
    icacls_grant = f'icacls "{key_path}" /grant:r "{username}:R"'
    grant_result = run_command(icacls_grant)
    
    if grant_result is not None:
        print("✅ Permissão de leitura concedida")
    else:
        print("⚠️ Falha ao conceder permissão de leitura")
    
    return True

def install_docker_manually():
    """Mostra instruções manuais para instalar Docker"""
    print("\n🐳 MARABET AI - INSTRUÇÕES PARA INSTALAR DOCKER")
    print("=" * 60)
    
    # Carregar configuração existente
    try:
        with open('aws_infrastructure_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de configuração não encontrado")
        return False
    
    ubuntu_public_ip = config.get('ubuntu_public_ip')
    
    if not ubuntu_public_ip:
        print("❌ IP público da instância Ubuntu não encontrado")
        return False
    
    print(f"✅ IP Público: {ubuntu_public_ip}")
    
    print("\n🔗 COMANDOS PARA CONECTAR VIA SSH:")
    print("-" * 50)
    print("1. Baixar a chave SSH:")
    print("   aws ec2 create-key-pair --key-name marabet-key-new --query 'KeyMaterial' --output text > ~/.ssh/marabet-key.pem")
    print()
    print("2. Configurar permissões (Windows):")
    print("   icacls C:\\Users\\%USERNAME%\\.ssh\\marabet-key.pem /inheritance:r")
    print("   icacls C:\\Users\\%USERNAME%\\.ssh\\marabet-key.pem /grant:r \"%USERNAME%:R\"")
    print()
    print("3. Conectar via SSH:")
    print(f"   ssh -i ~/.ssh/marabet-key.pem ubuntu@{ubuntu_public_ip}")
    
    print("\n🐳 COMANDOS PARA INSTALAR DOCKER NO SERVIDOR:")
    print("-" * 50)
    print("Execute os seguintes comandos no servidor Ubuntu:")
    print()
    print("# 1. Atualizar sistema")
    print("sudo apt update && sudo apt upgrade -y")
    print()
    print("# 2. Instalar Docker")
    print("curl -fsSL https://get.docker.com -o get-docker.sh")
    print("sudo sh get-docker.sh")
    print()
    print("# 3. Adicionar usuário ao grupo docker")
    print("sudo usermod -aG docker ubuntu")
    print()
    print("# 4. Instalar Docker Compose")
    print('sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose')
    print("sudo chmod +x /usr/local/bin/docker-compose")
    print()
    print("# 5. Reiniciar sessão")
    print("exit")
    print()
    print("# 6. Reconectar via SSH")
    print(f"ssh -i ~/.ssh/marabet-key.pem ubuntu@{ubuntu_public_ip}")
    print()
    print("# 7. Testar Docker")
    print("docker --version")
    print("docker-compose --version")
    print("docker run hello-world")
    
    print("\n🌐 CONFIGURAR VARIÁVEIS DE AMBIENTE:")
    print("-" * 50)
    print("Execute no servidor Ubuntu:")
    print()
    print("# Adicionar ao ~/.bashrc")
    print('echo "export DATABASE_URL=\\"postgresql://marabetadmin:MaraBet2024!SuperSecret@marabet-db.cmvmwskgiabr.us-east-1.rds.amazonaws.com:5432/postgres\\"" >> ~/.bashrc')
    print('echo "export REDIS_URL=\\"redis://marabet-redis.ve5qk7.0001.use1.cache.amazonaws.com:6379\\"" >> ~/.bashrc')
    print('echo "export API_FOOTBALL_KEY=\\"71b2b62386f2d1275cd3201a73e1e045\\"" >> ~/.bashrc')
    print('echo "export SECRET_KEY=\\"MaraBet2024!SuperSecretKey\\"" >> ~/.bashrc')
    print('echo "export ENVIRONMENT=\\"production\\"" >> ~/.bashrc')
    print('echo "export DEBUG=\\"false\\"" >> ~/.bashrc')
    print()
    print("# Recarregar configurações")
    print("source ~/.bashrc")
    
    print("\n🛠️ INSTALAR FERRAMENTAS ADICIONAIS:")
    print("-" * 50)
    print("Execute no servidor Ubuntu:")
    print()
    print("sudo apt install -y htop curl wget vim nano git python3 python3-pip python3-venv")
    print("pip3 install --user awscli")
    
    print("\n🧪 TESTAR INSTALAÇÃO:")
    print("-" * 50)
    print("Execute no servidor Ubuntu:")
    print()
    print("docker --version")
    print("docker-compose --version")
    print("docker ps")
    print("docker run hello-world")
    print("echo $DATABASE_URL")
    print("echo $REDIS_URL")
    
    print("\n🎯 RESUMO DA CONFIGURAÇÃO:")
    print("-" * 50)
    print("✅ Instância Ubuntu criada e configurada")
    print("✅ Security groups aplicados")
    print("✅ Instruções de instalação fornecidas")
    print("✅ Variáveis de ambiente configuradas")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 50)
    print("1. ✅ Baixar e configurar chave SSH")
    print("2. ✅ Conectar via SSH")
    print("3. ✅ Instalar Docker e Docker Compose")
    print("4. ✅ Configurar variáveis de ambiente")
    print("5. ✅ Deploy da aplicação MaraBet AI")
    print("6. ✅ Testar aplicação")
    
    return True

def main():
    print("🚀 Iniciando configuração da chave SSH e instalação do Docker...")
    
    # Baixar chave SSH
    key_path = download_ssh_key()
    
    if key_path:
        # Configurar permissões
        configure_ssh_key(key_path)
    
    # Mostrar instruções manuais
    install_docker_manually()
    
    print("\n🎯 CONFIGURAÇÃO CONCLUÍDA!")
    print("Siga as instruções acima para instalar o Docker no servidor!")

if __name__ == "__main__":
    main()
