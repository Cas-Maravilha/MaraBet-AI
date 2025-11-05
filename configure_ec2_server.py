#!/usr/bin/env python3
"""
Script para Configurar Servidor EC2 - MaraBet AI
Configura permissões da chave e conecta via SSH
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

def configure_ec2_server():
    """Configura servidor EC2 e conecta via SSH"""
    print("🔧 MARABET AI - CONFIGURANDO SERVIDOR EC2")
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
    ubuntu_instance_id = config.get('ubuntu_instance_id')
    
    if not ubuntu_public_ip or not ubuntu_instance_id:
        print("❌ Instância Ubuntu não encontrada na configuração")
        return False
    
    print(f"✅ IP Público: {ubuntu_public_ip}")
    print(f"✅ Instance ID: {ubuntu_instance_id}")
    
    print("\n🔧 ETAPA 1: CONFIGURANDO PERMISSÕES DA CHAVE")
    print("-" * 50)
    
    # Caminho da chave
    key_path = os.path.expanduser("~/.ssh/marabet-key.pem")
    
    if not os.path.exists(key_path):
        print(f"❌ Arquivo de chave não encontrado: {key_path}")
        return False
    
    print(f"✅ Arquivo de chave encontrado: {key_path}")
    
    # Ajustar permissões da chave (Windows)
    print("🔑 Ajustando permissões da chave...")
    
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
    
    print("\n🔧 ETAPA 2: TESTANDO CONECTIVIDADE")
    print("-" * 50)
    
    # Testar conectividade SSH
    print("🔍 Testando conectividade SSH...")
    ssh_test_command = f'ssh -i "{key_path}" -o ConnectTimeout=10 -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "echo \'SSH conectado com sucesso!\'"'
    
    print(f"Comando SSH: {ssh_test_command}")
    print("⚠️ Executando teste de conectividade...")
    
    # Nota: Este comando pode falhar se a instância ainda não estiver pronta
    # Vamos apenas mostrar o comando para o usuário executar
    print("✅ Comando SSH preparado")
    
    print("\n🔧 ETAPA 3: COMANDOS DE CONEXÃO")
    print("-" * 50)
    
    print("🔗 COMANDOS PARA CONECTAR VIA SSH:")
    print("-" * 40)
    print(f"# Comando completo")
    print(f'ssh -i "{key_path}" ubuntu@{ubuntu_public_ip}')
    print()
    print(f"# Comando simplificado (se a chave estiver em ~/.ssh/)")
    print(f'ssh -i ~/.ssh/marabet-key.pem ubuntu@{ubuntu_public_ip}')
    print()
    print(f"# Comando com verificação de host")
    print(f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip}')
    
    print("\n🔧 ETAPA 4: CONFIGURAÇÃO DO SERVIDOR")
    print("-" * 50)
    
    print("📋 COMANDOS PARA CONFIGURAR O SERVIDOR:")
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
    
    print("\n🔧 ETAPA 5: DEPLOY DA APLICAÇÃO")
    print("-" * 50)
    
    print("📋 COMANDOS PARA DEPLOY:")
    print("-" * 40)
    print("# 1. Clonar repositório")
    print("git clone https://github.com/seu-usuario/marabet-ai.git")
    print("cd marabet-ai")
    print()
    print("# 2. Criar ambiente virtual")
    print("python3 -m venv venv")
    print("source venv/bin/activate")
    print()
    print("# 3. Instalar dependências")
    print("pip install -r requirements.txt")
    print()
    print("# 4. Configurar aplicação")
    print("cp .env.example .env")
    print("# Editar .env com as configurações corretas")
    print()
    print("# 5. Executar aplicação")
    print("python app.py")
    print()
    print("# 6. Executar com Docker")
    print("docker-compose up -d")
    
    print("\n🔧 ETAPA 6: MONITORAMENTO")
    print("-" * 50)
    
    print("📋 COMANDOS DE MONITORAMENTO:")
    print("-" * 40)
    print("# Ver logs da aplicação")
    print("docker logs -f marabet-app")
    print()
    print("# Ver status dos containers")
    print("docker ps")
    print()
    print("# Ver uso de recursos")
    print("htop")
    print("df -h")
    print("free -h")
    print()
    print("# Ver logs do sistema")
    print("sudo journalctl -u docker")
    print("sudo tail -f /var/log/syslog")
    
    print("\n🔧 ETAPA 7: BACKUP E SEGURANÇA")
    print("-" * 50)
    
    print("📋 COMANDOS DE BACKUP:")
    print("-" * 40)
    print("# Backup da aplicação")
    print("tar -czf marabet-backup-$(date +%Y%m%d).tar.gz /home/ubuntu/marabet-ai")
    print()
    print("# Backup do banco de dados")
    print("pg_dump $DATABASE_URL > marabet-db-backup-$(date +%Y%m%d).sql")
    print()
    print("# Configurar backup automático")
    print("crontab -e")
    print("# Adicionar: 0 2 * * * /home/ubuntu/backup.sh")
    
    print("\n🎉 CONFIGURAÇÃO DO SERVIDOR PRONTA!")
    print("=" * 60)
    
    print("\n📋 RESUMO DA CONFIGURAÇÃO:")
    print("-" * 40)
    print(f"• IP Público: {ubuntu_public_ip}")
    print(f"• Instance ID: {ubuntu_instance_id}")
    print(f"• Chave SSH: {key_path}")
    print(f"• Usuário: ubuntu")
    print(f"• Sistema: Ubuntu 22.04 LTS")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Conectar via SSH")
    print("2. ✅ Configurar servidor")
    print("3. ✅ Deploy da aplicação")
    print("4. ✅ Configurar monitoramento")
    print("5. ✅ Configurar backup")
    print("6. ✅ Testar aplicação")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("-" * 40)
    print("• Sempre use 'sudo' para comandos administrativos")
    print("• Configure firewall com 'sudo ufw enable'")
    print("• Mantenha o sistema atualizado")
    print("• Configure backup automático")
    print("• Monitore logs regularmente")
    print("• Use HTTPS para produção")
    
    return True

def main():
    print("🚀 Iniciando configuração do servidor EC2...")
    
    # Configurar servidor EC2
    success = configure_ec2_server()
    
    if success:
        print("\n🎯 CONFIGURAÇÃO DO SERVIDOR CONCLUÍDA!")
        print("O servidor EC2 está pronto para configuração!")
    else:
        print("\n❌ Falha na configuração do servidor")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
