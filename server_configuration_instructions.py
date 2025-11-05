#!/usr/bin/env python3
"""
Script para Instruções de Configuração do Servidor EC2 - MaraBet AI
Mostra instruções detalhadas para configurar o servidor EC2
"""

import json
from datetime import datetime

def show_server_configuration_instructions():
    """Mostra instruções detalhadas para configurar o servidor EC2"""
    
    print("\n" + "="*80)
    print("🔧 MARABET AI - INSTRUÇÕES DE CONFIGURAÇÃO DO SERVIDOR EC2")
    print("="*80)
    
    print(f"\n📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
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
    
    print(f"\n📋 INFORMAÇÕES DA INSTÂNCIA:")
    print("-" * 60)
    print(f"• IP Público: {ubuntu_public_ip}")
    print(f"• Instance ID: {ubuntu_instance_id}")
    print(f"• Sistema: Ubuntu 22.04 LTS")
    print(f"• Usuário: ubuntu")
    print(f"• Key Pair: marabet-key")
    
    print(f"\n🔑 ETAPA 1: CONFIGURAR CHAVE SSH")
    print("-" * 60)
    print("1. Baixar a chave SSH da AWS:")
    print("   aws ec2 create-key-pair --key-name marabet-key --query 'KeyMaterial' --output text > ~/.ssh/marabet-key.pem")
    print()
    print("2. Configurar permissões (Windows):")
    print("   icacls C:\\Users\\%USERNAME%\\.ssh\\marabet-key.pem /inheritance:r")
    print("   icacls C:\\Users\\%USERNAME%\\.ssh\\marabet-key.pem /grant:r \"%USERNAME%:R\"")
    print()
    print("3. Configurar permissões (Linux/Mac):")
    print("   chmod 600 ~/.ssh/marabet-key.pem")
    
    print(f"\n🔗 ETAPA 2: CONECTAR VIA SSH")
    print("-" * 60)
    print("Comando para conectar:")
    print(f"ssh -i ~/.ssh/marabet-key.pem ubuntu@{ubuntu_public_ip}")
    print()
    print("Comando PowerShell:")
    print(f'$PUBLIC_IP = "{ubuntu_public_ip}"')
    print('ssh -i ~/.ssh/marabet-key.pem ubuntu@$PUBLIC_IP')
    
    print(f"\n🔧 ETAPA 3: CONFIGURAR SERVIDOR")
    print("-" * 60)
    print("Execute os seguintes comandos no servidor Ubuntu:")
    print()
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
    print("# 6. Instalar ferramentas úteis")
    print("sudo apt install -y htop curl wget vim nano")
    
    print(f"\n🌐 ETAPA 4: CONFIGURAR VARIÁVEIS DE AMBIENTE")
    print("-" * 60)
    print("Configure as variáveis de ambiente no servidor:")
    print()
    print("# Adicionar ao ~/.bashrc")
    print("echo 'export DATABASE_URL=\"postgresql://marabetadmin:MaraBet2024!SuperSecret@marabet-db.cmvmwskgiabr.us-east-1.rds.amazonaws.com:5432/postgres\"' >> ~/.bashrc")
    print("echo 'export REDIS_URL=\"redis://marabet-redis.ve5qk7.0001.use1.cache.amazonaws.com:6379\"' >> ~/.bashrc")
    print("echo 'export API_FOOTBALL_KEY=\"71b2b62386f2d1275cd3201a73e1e045\"' >> ~/.bashrc")
    print("echo 'export SECRET_KEY=\"MaraBet2024!SuperSecretKey\"' >> ~/.bashrc")
    print("echo 'export ENVIRONMENT=\"production\"' >> ~/.bashrc")
    print("echo 'export DEBUG=\"false\"' >> ~/.bashrc")
    print()
    print("# Recarregar configurações")
    print("source ~/.bashrc")
    
    print(f"\n📦 ETAPA 5: DEPLOY DA APLICAÇÃO")
    print("-" * 60)
    print("1. Clonar repositório:")
    print("   git clone https://github.com/seu-usuario/marabet-ai.git")
    print("   cd marabet-ai")
    print()
    print("2. Criar ambiente virtual:")
    print("   python3 -m venv venv")
    print("   source venv/bin/activate")
    print()
    print("3. Instalar dependências:")
    print("   pip install -r requirements.txt")
    print()
    print("4. Configurar aplicação:")
    print("   cp .env.example .env")
    print("   # Editar .env com as configurações corretas")
    print()
    print("5. Executar aplicação:")
    print("   python app.py")
    print()
    print("6. Executar com Docker:")
    print("   docker-compose up -d")
    
    print(f"\n🔍 ETAPA 6: VERIFICAR CONECTIVIDADE")
    print("-" * 60)
    print("Teste a conectividade com os serviços:")
    print()
    print("# Testar conexão com RDS")
    print("psql $DATABASE_URL -c 'SELECT version();'")
    print()
    print("# Testar conexão com Redis")
    print("redis-cli -u $REDIS_URL ping")
    print()
    print("# Testar API Football")
    print("curl -H 'X-RapidAPI-Key: $API_FOOTBALL_KEY' 'https://api-football-v1.p.rapidapi.com/v3/status'")
    
    print(f"\n📊 ETAPA 7: CONFIGURAR MONITORAMENTO")
    print("-" * 60)
    print("Configure monitoramento e logs:")
    print()
    print("# Instalar CloudWatch agent")
    print("wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb")
    print("sudo dpkg -i amazon-cloudwatch-agent.deb")
    print()
    print("# Configurar logs")
    print("sudo mkdir -p /var/log/marabet")
    print("sudo chown ubuntu:ubuntu /var/log/marabet")
    print()
    print("# Ver logs da aplicação")
    print("tail -f /var/log/marabet/app.log")
    
    print(f"\n🔒 ETAPA 8: CONFIGURAR SEGURANÇA")
    print("-" * 60)
    print("Configure segurança do servidor:")
    print()
    print("# Configurar firewall")
    print("sudo ufw enable")
    print("sudo ufw allow ssh")
    print("sudo ufw allow 80")
    print("sudo ufw allow 443")
    print()
    print("# Configurar fail2ban")
    print("sudo apt install -y fail2ban")
    print("sudo systemctl enable fail2ban")
    print("sudo systemctl start fail2ban")
    print()
    print("# Configurar backup automático")
    print("sudo apt install -y cron")
    print("crontab -e")
    print("# Adicionar: 0 2 * * * /home/ubuntu/backup.sh")
    
    print(f"\n💡 COMANDOS ÚTEIS")
    print("-" * 60)
    print("# Ver status da instância")
    print(f"aws ec2 describe-instances --instance-ids {ubuntu_instance_id}")
    print()
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
    print("# Reiniciar aplicação")
    print("docker-compose restart")
    print()
    print("# Parar aplicação")
    print("docker-compose down")
    print()
    print("# Iniciar aplicação")
    print("docker-compose up -d")
    
    print(f"\n🎯 RESUMO DA CONFIGURAÇÃO")
    print("-" * 60)
    print("✅ Instância Ubuntu criada e configurada")
    print("✅ Security groups aplicados")
    print("✅ Sistema pronto para deploy")
    print("✅ Instruções detalhadas fornecidas")
    
    print(f"\n🔗 PRÓXIMOS PASSOS")
    print("-" * 60)
    print("1. ✅ Baixar e configurar chave SSH")
    print("2. ✅ Conectar via SSH")
    print("3. ✅ Configurar servidor")
    print("4. ✅ Deploy da aplicação")
    print("5. ✅ Testar aplicação")
    print("6. ✅ Configurar monitoramento")
    print("7. ✅ Configurar backup")
    
    print("\n" + "="*80)
    print("🔧 MARABET AI - INSTRUÇÕES DE CONFIGURAÇÃO DO SERVIDOR EC2")
    print("="*80)
    
    return True

def main():
    print("🚀 Iniciando instruções de configuração do servidor EC2...")
    
    # Mostrar instruções
    success = show_server_configuration_instructions()
    
    if success:
        print("\n🎯 INSTRUÇÕES DE CONFIGURAÇÃO PRONTAS!")
        print("Siga as instruções acima para configurar o servidor EC2!")
    else:
        print("\n❌ Falha ao carregar configurações")
        print("Verifique se o arquivo aws_infrastructure_config.json existe")

if __name__ == "__main__":
    main()
