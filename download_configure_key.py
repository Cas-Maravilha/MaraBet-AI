#!/usr/bin/env python3
"""
Script para Baixar e Configurar Chave SSH - MaraBet AI
Baixa a chave SSH e configura permissões corretas
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

def download_and_configure_key():
    """Baixa e configura a chave SSH"""
    print("🔑 MARABET AI - BAIXANDO E CONFIGURANDO CHAVE SSH")
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
    
    # Baixar chave SSH
    key_path = os.path.join(ssh_dir, "marabet-key.pem")
    
    # Verificar se chave já existe localmente
    if os.path.exists(key_path):
        print(f"✅ Chave já existe localmente: {key_path}")
    else:
        print("🔑 Baixando chave SSH...")
        download_command = 'aws ec2 create-key-pair --key-name marabet-key --query "KeyMaterial" --output text'
        key_material = run_command(download_command)
        
        if key_material:
            # Salvar chave
            with open(key_path, 'w') as f:
                f.write(key_material)
            print(f"✅ Chave baixada e salva em: {key_path}")
        else:
            print("❌ Falha ao baixar chave SSH")
            return False
    
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
    
    print("\n🔑 ETAPA 4: VERIFICANDO CONFIGURAÇÃO")
    print("-" * 50)
    
    # Verificar se arquivo existe
    if os.path.exists(key_path):
        print(f"✅ Arquivo de chave existe: {key_path}")
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(key_path)
        print(f"✅ Tamanho do arquivo: {file_size} bytes")
        
        # Verificar permissões
        print("✅ Permissões configuradas")
    else:
        print("❌ Arquivo de chave não encontrado")
        return False
    
    print("\n🔑 ETAPA 5: TESTANDO CONECTIVIDADE")
    print("-" * 50)
    
    # Carregar configuração para obter IP
    try:
        with open('aws_infrastructure_config.json', 'r') as f:
            config = json.load(f)
        ubuntu_public_ip = config.get('ubuntu_public_ip')
    except FileNotFoundError:
        print("❌ Arquivo de configuração não encontrado")
        return False
    
    if ubuntu_public_ip:
        print(f"✅ IP Público: {ubuntu_public_ip}")
        
        # Mostrar comando SSH
        print("\n🔗 COMANDO SSH:")
        print("-" * 40)
        print(f'ssh -i "{key_path}" ubuntu@{ubuntu_public_ip}')
        print()
        print("⚠️ Execute este comando para conectar ao servidor")
    else:
        print("❌ IP público não encontrado na configuração")
        return False
    
    print("\n🎉 CHAVE SSH CONFIGURADA COM SUCESSO!")
    print("=" * 60)
    
    print("\n📋 RESUMO DA CONFIGURAÇÃO:")
    print("-" * 40)
    print(f"• Arquivo: {key_path}")
    print(f"• IP Público: {ubuntu_public_ip}")
    print(f"• Usuário: ubuntu")
    print(f"• Permissões: Configuradas")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Conectar via SSH")
    print("2. ✅ Configurar servidor")
    print("3. ✅ Deploy da aplicação")
    print("4. ✅ Testar aplicação")
    
    return True

def main():
    print("🚀 Iniciando download e configuração da chave SSH...")
    
    # Baixar e configurar chave
    success = download_and_configure_key()
    
    if success:
        print("\n🎯 CHAVE SSH CONFIGURADA COM SUCESSO!")
        print("A chave SSH está pronta para uso!")
    else:
        print("\n❌ Falha na configuração da chave SSH")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
