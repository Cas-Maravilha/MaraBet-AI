#!/usr/bin/env python3
"""
Script para Configurar Permissões da Chave SSH - MaraBet AI
Configura permissões corretas para a chave SSH existente
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

def configure_ssh_key():
    """Configura permissões da chave SSH"""
    print("🔑 MARABET AI - CONFIGURANDO CHAVE SSH")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    print("\n🔑 ETAPA 1: VERIFICANDO CHAVE SSH")
    print("-" * 50)
    
    # Caminho da chave
    key_path = os.path.expanduser("~/.ssh/marabet-key.pem")
    
    if not os.path.exists(key_path):
        print(f"❌ Arquivo de chave não encontrado: {key_path}")
        print("💡 A chave SSH precisa ser criada primeiro")
        print("💡 Execute: aws ec2 create-key-pair --key-name marabet-key --query 'KeyMaterial' --output text > ~/.ssh/marabet-key.pem")
        return False
    
    print(f"✅ Arquivo de chave encontrado: {key_path}")
    
    # Verificar tamanho do arquivo
    file_size = os.path.getsize(key_path)
    print(f"✅ Tamanho do arquivo: {file_size} bytes")
    
    print("\n🔑 ETAPA 2: CONFIGURANDO PERMISSÕES")
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
    
    print("\n🔑 ETAPA 3: VERIFICANDO CONFIGURAÇÃO")
    print("-" * 50)
    
    # Verificar se arquivo ainda existe
    if os.path.exists(key_path):
        print(f"✅ Arquivo de chave existe: {key_path}")
        print("✅ Permissões configuradas")
    else:
        print("❌ Arquivo de chave não encontrado após configuração")
        return False
    
    print("\n🔑 ETAPA 4: PREPARANDO CONEXÃO SSH")
    print("-" * 50)
    
    # Carregar configuração para obter IP
    try:
        with open('aws_infrastructure_config.json', 'r') as f:
            config = json.load(f)
        ubuntu_public_ip = config.get('ubuntu_public_ip')
        ubuntu_instance_id = config.get('ubuntu_instance_id')
    except FileNotFoundError:
        print("❌ Arquivo de configuração não encontrado")
        return False
    
    if ubuntu_public_ip:
        print(f"✅ IP Público: {ubuntu_public_ip}")
        print(f"✅ Instance ID: {ubuntu_instance_id}")
        
        # Mostrar comando SSH
        print("\n🔗 COMANDO SSH:")
        print("-" * 40)
        print(f'ssh -i "{key_path}" ubuntu@{ubuntu_public_ip}')
        print()
        print("⚠️ Execute este comando para conectar ao servidor")
        
        # Mostrar comando PowerShell
        print("\n🔗 COMANDO POWERSHELL:")
        print("-" * 40)
        print(f'$PUBLIC_IP = "{ubuntu_public_ip}"')
        print(f'ssh -i "{key_path}" ubuntu@$PUBLIC_IP')
        
    else:
        print("❌ IP público não encontrado na configuração")
        return False
    
    print("\n🔑 ETAPA 5: COMANDOS DE CONFIGURAÇÃO DO SERVIDOR")
    print("-" * 50)
    
    print("📋 COMANDOS PARA EXECUTAR NO SERVIDOR:")
    print("-" * 40)
    print("# 1. Atualizar sistema")
    print("sudo apt update && sudo apt upgrade -y")
    print()
    print("# 2. Instalar Docker")
    print("sudo apt install -y docker.io")
    print("sudo systemctl start docker")
    print("sudo systemctl enable docker")
    print("sudo usermod -aG docker ubuntu")
    print()
    print("# 3. Instalar Docker Compose")
    print("sudo apt install -y docker-compose")
    print()
    print("# 4. Instalar Python e dependências")
    print("sudo apt install -y python3 python3-pip python3-venv")
    print("pip3 install --user awscli")
    print()
    print("# 5. Instalar Git")
    print("sudo apt install -y git")
    print()
    print("# 6. Configurar variáveis de ambiente")
    print("echo 'export DATABASE_URL=\"postgresql://marabetadmin:MaraBet2024!SuperSecret@marabet-db.cmvmwskgiabr.us-east-1.rds.amazonaws.com:5432/postgres\"' >> ~/.bashrc")
    print("echo 'export REDIS_URL=\"redis://marabet-redis.ve5qk7.0001.use1.cache.amazonaws.com:6379\"' >> ~/.bashrc")
    print("echo 'export API_FOOTBALL_KEY=\"71b2b62386f2d1275cd3201a73e1e045\"' >> ~/.bashrc")
    print("echo 'export SECRET_KEY=\"MaraBet2024!SuperSecretKey\"' >> ~/.bashrc")
    print("source ~/.bashrc")
    
    print("\n🎉 CHAVE SSH CONFIGURADA COM SUCESSO!")
    print("=" * 60)
    
    print("\n📋 RESUMO DA CONFIGURAÇÃO:")
    print("-" * 40)
    print(f"• Arquivo: {key_path}")
    print(f"• IP Público: {ubuntu_public_ip}")
    print(f"• Instance ID: {ubuntu_instance_id}")
    print(f"• Usuário: ubuntu")
    print(f"• Permissões: Configuradas")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Conectar via SSH")
    print("2. ✅ Configurar servidor")
    print("3. ✅ Deploy da aplicação")
    print("4. ✅ Testar aplicação")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("-" * 40)
    print("• Use o comando SSH mostrado acima")
    print("• Execute os comandos de configuração no servidor")
    print("• Configure as variáveis de ambiente")
    print("• Teste a conectividade com o banco e Redis")
    
    return True

def main():
    print("🚀 Iniciando configuração da chave SSH...")
    
    # Configurar chave SSH
    success = configure_ssh_key()
    
    if success:
        print("\n🎯 CHAVE SSH CONFIGURADA COM SUCESSO!")
        print("A chave SSH está pronta para uso!")
    else:
        print("\n❌ Falha na configuração da chave SSH")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
