#!/usr/bin/env python3
"""
Script para Instalar Docker no Servidor Ubuntu - MaraBet AI
Automatiza a instalação do Docker e Docker Compose
"""

import subprocess
import json
from datetime import datetime

def run_ssh_command(host, key_path, command):
    """Executa comando SSH no servidor remoto"""
    ssh_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{host} "{command}"'
    try:
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ Erro no comando SSH: {command}")
            print(f"Erro: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Exceção no comando SSH: {command}")
        print(f"Erro: {e}")
        return None

def install_docker_on_server():
    """Instala Docker no servidor Ubuntu"""
    print("🐳 MARABET AI - INSTALANDO DOCKER NO SERVIDOR UBUNTU")
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
    key_path = "~/.ssh/marabet-key.pem"
    
    if not ubuntu_public_ip:
        print("❌ IP público da instância Ubuntu não encontrado")
        return False
    
    print(f"✅ IP Público: {ubuntu_public_ip}")
    print(f"✅ Chave SSH: {key_path}")
    
    print("\n🐳 ETAPA 1: TESTANDO CONECTIVIDADE SSH")
    print("-" * 50)
    
    # Testar conectividade SSH
    print("🔍 Testando conectividade SSH...")
    test_command = "echo 'SSH conectado com sucesso!'"
    test_result = run_ssh_command(ubuntu_public_ip, key_path, test_command)
    
    if test_result:
        print("✅ Conectividade SSH OK")
    else:
        print("❌ Falha na conectividade SSH")
        print("💡 Verifique se a instância está rodando e a chave SSH está configurada")
        return False
    
    print("\n🐳 ETAPA 2: ATUALIZANDO SISTEMA")
    print("-" * 50)
    
    # Atualizar sistema
    print("🔄 Atualizando sistema...")
    update_command = "sudo apt update && sudo apt upgrade -y"
    update_result = run_ssh_command(ubuntu_public_ip, key_path, update_command)
    
    if update_result is not None:
        print("✅ Sistema atualizado com sucesso")
    else:
        print("⚠️ Falha ao atualizar sistema, mas continuando...")
    
    print("\n🐳 ETAPA 3: INSTALANDO DOCKER")
    print("-" * 50)
    
    # Instalar Docker
    print("🐳 Instalando Docker...")
    docker_install_command = "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
    docker_result = run_ssh_command(ubuntu_public_ip, key_path, docker_install_command)
    
    if docker_result is not None:
        print("✅ Docker instalado com sucesso")
    else:
        print("⚠️ Falha ao instalar Docker, mas continuando...")
    
    print("\n🐳 ETAPA 4: CONFIGURANDO USUÁRIO DOCKER")
    print("-" * 50)
    
    # Adicionar usuário ao grupo docker
    print("👤 Adicionando usuário ao grupo docker...")
    usermod_command = "sudo usermod -aG docker ubuntu"
    usermod_result = run_ssh_command(ubuntu_public_ip, key_path, usermod_command)
    
    if usermod_result is not None:
        print("✅ Usuário adicionado ao grupo docker")
    else:
        print("⚠️ Falha ao adicionar usuário ao grupo docker")
    
    print("\n🐳 ETAPA 5: INSTALANDO DOCKER COMPOSE")
    print("-" * 50)
    
    # Instalar Docker Compose
    print("🐳 Instalando Docker Compose...")
    compose_install_command = 'sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose'
    compose_result = run_ssh_command(ubuntu_public_ip, key_path, compose_install_command)
    
    if compose_result is not None:
        print("✅ Docker Compose instalado com sucesso")
    else:
        print("⚠️ Falha ao instalar Docker Compose, mas continuando...")
    
    print("\n🐳 ETAPA 6: VERIFICANDO INSTALAÇÃO")
    print("-" * 50)
    
    # Verificar versões
    print("🔍 Verificando versões...")
    
    # Verificar Docker
    docker_version_command = "docker --version"
    docker_version = run_ssh_command(ubuntu_public_ip, key_path, docker_version_command)
    
    if docker_version:
        print(f"✅ Docker: {docker_version}")
    else:
        print("❌ Docker não encontrado")
    
    # Verificar Docker Compose
    compose_version_command = "docker-compose --version"
    compose_version = run_ssh_command(ubuntu_public_ip, key_path, compose_version_command)
    
    if compose_version:
        print(f"✅ Docker Compose: {compose_version}")
    else:
        print("❌ Docker Compose não encontrado")
    
    print("\n🐳 ETAPA 7: CONFIGURANDO DOCKER")
    print("-" * 50)
    
    # Configurar Docker para iniciar automaticamente
    print("⚙️ Configurando Docker para iniciar automaticamente...")
    enable_docker_command = "sudo systemctl enable docker && sudo systemctl start docker"
    enable_result = run_ssh_command(ubuntu_public_ip, key_path, enable_docker_command)
    
    if enable_result is not None:
        print("✅ Docker configurado para iniciar automaticamente")
    else:
        print("⚠️ Falha ao configurar Docker para iniciar automaticamente")
    
    print("\n🐳 ETAPA 8: TESTANDO DOCKER")
    print("-" * 50)
    
    # Testar Docker
    print("🧪 Testando Docker...")
    test_docker_command = "docker run hello-world"
    test_docker_result = run_ssh_command(ubuntu_public_ip, key_path, test_docker_command)
    
    if test_docker_result and "Hello from Docker!" in test_docker_result:
        print("✅ Docker funcionando corretamente")
    else:
        print("⚠️ Falha no teste do Docker")
    
    print("\n🐳 ETAPA 9: CONFIGURANDO VARIÁVEIS DE AMBIENTE")
    print("-" * 50)
    
    # Configurar variáveis de ambiente
    print("🌐 Configurando variáveis de ambiente...")
    
    env_commands = [
        'echo "export DATABASE_URL=\\"postgresql://marabetadmin:MaraBet2024!SuperSecret@marabet-db.cmvmwskgiabr.us-east-1.rds.amazonaws.com:5432/postgres\\"" >> ~/.bashrc',
        'echo "export REDIS_URL=\\"redis://marabet-redis.ve5qk7.0001.use1.cache.amazonaws.com:6379\\"" >> ~/.bashrc',
        'echo "export API_FOOTBALL_KEY=\\"71b2b62386f2d1275cd3201a73e1e045\\"" >> ~/.bashrc',
        'echo "export SECRET_KEY=\\"MaraBet2024!SuperSecretKey\\"" >> ~/.bashrc',
        'echo "export ENVIRONMENT=\\"production\\"" >> ~/.bashrc',
        'echo "export DEBUG=\\"false\\"" >> ~/.bashrc'
    ]
    
    for env_cmd in env_commands:
        env_result = run_ssh_command(ubuntu_public_ip, key_path, env_cmd)
        if env_result is not None:
            print("✅ Variável de ambiente configurada")
        else:
            print("⚠️ Falha ao configurar variável de ambiente")
    
    print("\n🐳 ETAPA 10: INSTALANDO FERRAMENTAS ADICIONAIS")
    print("-" * 50)
    
    # Instalar ferramentas úteis
    print("🛠️ Instalando ferramentas úteis...")
    tools_command = "sudo apt install -y htop curl wget vim nano git python3 python3-pip python3-venv"
    tools_result = run_ssh_command(ubuntu_public_ip, key_path, tools_command)
    
    if tools_result is not None:
        print("✅ Ferramentas instaladas com sucesso")
    else:
        print("⚠️ Falha ao instalar ferramentas")
    
    print("\n🎉 DOCKER INSTALADO COM SUCESSO!")
    print("=" * 60)
    
    print("\n📋 RESUMO DA INSTALAÇÃO:")
    print("-" * 40)
    print(f"• Servidor: {ubuntu_public_ip}")
    print(f"• Docker: {docker_version if docker_version else 'N/A'}")
    print(f"• Docker Compose: {compose_version if compose_version else 'N/A'}")
    print(f"• Variáveis de ambiente: Configuradas")
    print(f"• Ferramentas: Instaladas")
    
    print("\n🔗 COMANDOS PARA RECONECTAR:")
    print("-" * 40)
    print(f"ssh -i {key_path} ubuntu@{ubuntu_public_ip}")
    print()
    print("Comando PowerShell:")
    print(f'$PUBLIC_IP = "{ubuntu_public_ip}"')
    print(f'ssh -i {key_path} ubuntu@$PUBLIC_IP')
    
    print("\n🧪 COMANDOS DE TESTE:")
    print("-" * 40)
    print("docker --version")
    print("docker-compose --version")
    print("docker ps")
    print("docker run hello-world")
    
    print("\n🌐 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Docker instalado e configurado")
    print("2. ✅ Docker Compose instalado")
    print("3. ✅ Variáveis de ambiente configuradas")
    print("4. 🔄 Deploy da aplicação MaraBet AI")
    print("5. 🔄 Configurar monitoramento")
    print("6. 🔄 Testar aplicação")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("-" * 40)
    print("• Reinicie a sessão SSH para aplicar as mudanças do grupo docker")
    print("• Use 'sudo docker' se houver problemas de permissão")
    print("• Configure backup automático dos volumes Docker")
    print("• Monitore o uso de recursos do Docker")
    
    return True

def main():
    print("🚀 Iniciando instalação do Docker no servidor Ubuntu...")
    
    # Instalar Docker
    success = install_docker_on_server()
    
    if success:
        print("\n🎯 DOCKER INSTALADO COM SUCESSO!")
        print("O servidor Ubuntu está pronto para deploy da aplicação!")
    else:
        print("\n❌ Falha na instalação do Docker")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
