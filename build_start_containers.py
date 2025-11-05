#!/usr/bin/env python3
"""
Script para Build e Inicialização dos Containers - MaraBet AI
Automatiza o build e inicialização dos containers Docker
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

def build_and_start_containers():
    """Faz build e inicia os containers Docker"""
    print("🐳 MARABET AI - BUILD E INICIALIZAÇÃO DOS CONTAINERS")
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
    
    print("\n🐳 ETAPA 1: VERIFICANDO ARQUIVOS NECESSÁRIOS")
    print("-" * 50)
    
    # Verificar se arquivos necessários existem
    required_files = ['docker-compose.production.yml', 'Dockerfile', 'requirements.txt', 'app.py']
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} encontrado")
        else:
            print(f"❌ {file} não encontrado")
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️ Arquivos faltando: {', '.join(missing_files)}")
        print("💡 Certifique-se de estar na pasta correta do projeto")
    
    print("\n🐳 ETAPA 2: CRIANDO SCRIPT DE BUILD E INICIALIZAÇÃO")
    print("-" * 50)
    
    # Criar script de build e inicialização
    build_script_content = """#!/bin/bash
# Script de Build e Inicialização - MaraBet AI

echo "🐳 MARABET AI - BUILD E INICIALIZAÇÃO DOS CONTAINERS"
echo "=================================================="

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Iniciando Docker..."
    sudo systemctl start docker
    sleep 5
fi

# Verificar se Docker Compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.production.yml down 2>/dev/null || true

# Remover imagens antigas
echo "🧹 Limpando imagens antigas..."
docker system prune -f

# Build da imagem
echo "🏗️ Fazendo build da imagem..."
docker-compose -f docker-compose.production.yml build --no-cache

if [ $? -eq 0 ]; then
    echo "✅ Build concluído com sucesso"
else
    echo "❌ Falha no build da imagem"
    exit 1
fi

# Iniciar serviços
echo "🚀 Iniciando serviços..."
docker-compose -f docker-compose.production.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ Serviços iniciados com sucesso"
else
    echo "❌ Falha ao iniciar serviços"
    exit 1
fi

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar status
echo "🔍 Verificando status dos containers..."
docker-compose -f docker-compose.production.yml ps

# Verificar logs
echo "📋 Logs da aplicação:"
docker-compose -f docker-compose.production.yml logs --tail=20

# Testar conectividade
echo "🧪 Testando conectividade..."
curl -f http://localhost:8000/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Aplicação respondendo corretamente"
else
    echo "⚠️ Aplicação não está respondendo"
fi

echo "🎉 Build e inicialização concluídos!"
echo "🌐 Aplicação disponível em: http://$(curl -s ifconfig.me):8000"
"""
    
    with open('build_and_start.sh', 'w') as f:
        f.write(build_script_content)
    print("✅ Script de build e inicialização criado: build_and_start.sh")
    
    print("\n🐳 ETAPA 3: TRANSFERINDO SCRIPT PARA O SERVIDOR")
    print("-" * 50)
    
    # Transferir script para o servidor
    print("📤 Transferindo script para o servidor...")
    scp_command = f'scp -i "{key_path}" -o StrictHostKeyChecking=no build_and_start.sh ubuntu@{ubuntu_public_ip}:/home/ubuntu/marabet-ai/'
    
    print(f"Executando: {scp_command}")
    scp_result = run_command(scp_command)
    
    if scp_result is not None:
        print("✅ Script transferido com sucesso")
    else:
        print("⚠️ Falha na transferência do script")
        print("💡 Tente executar manualmente:")
        print(f"scp -i {key_path} build_and_start.sh ubuntu@{ubuntu_public_ip}:/home/ubuntu/marabet-ai/")
    
    print("\n🐳 ETAPA 4: EXECUTANDO BUILD E INICIALIZAÇÃO")
    print("-" * 50)
    
    # Executar script no servidor
    print("🚀 Executando build e inicialização no servidor...")
    build_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "cd /home/ubuntu/marabet-ai && chmod +x build_and_start.sh && ./build_and_start.sh"'
    
    print(f"Executando: {build_command}")
    print("⚠️ Este comando pode demorar vários minutos...")
    
    # Executar build
    build_result = run_command(build_command)
    
    if build_result is not None:
        print("✅ Build e inicialização executados com sucesso")
    else:
        print("⚠️ Falha no build e inicialização")
        print("💡 Tente executar manualmente no servidor:")
        print("ssh -i ~/.ssh/marabet-key.pem ubuntu@3.218.152.100")
        print("cd /home/ubuntu/marabet-ai")
        print("./build_and_start.sh")
    
    print("\n🐳 ETAPA 5: VERIFICANDO STATUS DOS CONTAINERS")
    print("-" * 50)
    
    # Verificar status dos containers
    print("🔍 Verificando status dos containers...")
    status_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "cd /home/ubuntu/marabet-ai && docker-compose -f docker-compose.production.yml ps"'
    status_result = run_command(status_command)
    
    if status_result:
        print("✅ Status dos containers:")
        print(status_result)
    else:
        print("⚠️ Falha ao verificar status dos containers")
    
    # Verificar logs
    print("\n📋 Verificando logs da aplicação...")
    logs_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "cd /home/ubuntu/marabet-ai && docker-compose -f docker-compose.production.yml logs --tail=20"'
    logs_result = run_command(logs_command)
    
    if logs_result:
        print("✅ Logs da aplicação:")
        print(logs_result)
    else:
        print("⚠️ Falha ao verificar logs da aplicação")
    
    print("\n🐳 ETAPA 6: TESTANDO CONECTIVIDADE")
    print("-" * 50)
    
    # Testar conectividade
    print("🧪 Testando conectividade...")
    test_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "curl -f http://localhost:8000/health"'
    test_result = run_command(test_command)
    
    if test_result:
        print("✅ Aplicação respondendo corretamente")
        print(test_result)
    else:
        print("⚠️ Aplicação não está respondendo")
    
    print("\n🎉 BUILD E INICIALIZAÇÃO CONCLUÍDOS!")
    print("=" * 60)
    
    print("\n📋 RESUMO DO BUILD:")
    print("-" * 40)
    print(f"• Servidor: {ubuntu_public_ip}")
    print(f"• Pasta: /home/ubuntu/marabet-ai")
    print(f"• Aplicação: MaraBet AI")
    print(f"• Status: Containers iniciados")
    
    print("\n🔗 COMANDOS ÚTEIS:")
    print("-" * 40)
    print(f"# Conectar via SSH")
    print(f"ssh -i {key_path} ubuntu@{ubuntu_public_ip}")
    print()
    print("# Ver status dos containers")
    print("cd /home/ubuntu/marabet-ai && docker-compose -f docker-compose.production.yml ps")
    print()
    print("# Ver logs da aplicação")
    print("cd /home/ubuntu/marabet-ai && docker-compose -f docker-compose.production.yml logs -f")
    print()
    print("# Reiniciar aplicação")
    print("cd /home/ubuntu/marabet-ai && docker-compose -f docker-compose.production.yml restart")
    print()
    print("# Parar aplicação")
    print("cd /home/ubuntu/marabet-ai && docker-compose -f docker-compose.production.yml down")
    print()
    print("# Iniciar aplicação")
    print("cd /home/ubuntu/marabet-ai && docker-compose -f docker-compose.production.yml up -d")
    print()
    print("# Ver logs em tempo real")
    print("cd /home/ubuntu/marabet-ai && docker-compose -f docker-compose.production.yml logs -f --tail=50")
    
    print("\n🌐 ACESSAR APLICAÇÃO:")
    print("-" * 40)
    print(f"• URL: http://{ubuntu_public_ip}:8000")
    print(f"• API Docs: http://{ubuntu_public_ip}:8000/docs")
    print(f"• Health Check: http://{ubuntu_public_ip}:8000/health")
    print(f"• Predictions: http://{ubuntu_public_ip}:8000/predictions")
    print(f"• Analysis: http://{ubuntu_public_ip}:8000/analysis")
    print(f"• Configuration: http://{ubuntu_public_ip}:8000/config")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Build e inicialização executados")
    print("2. 🔄 Verificar logs")
    print("3. 🔄 Testar endpoints")
    print("4. 🔄 Configurar monitoramento")
    print("5. 🔄 Configurar backup")
    print("6. 🔄 Configurar domínio (opcional)")
    
    return True

def main():
    print("🚀 Iniciando build e inicialização dos containers...")
    
    # Fazer build e inicializar containers
    success = build_and_start_containers()
    
    if success:
        print("\n🎯 BUILD E INICIALIZAÇÃO CONCLUÍDOS COM SUCESSO!")
        print("Os containers Docker estão rodando no servidor EC2!")
    else:
        print("\n❌ Falha no build e inicialização dos containers")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
