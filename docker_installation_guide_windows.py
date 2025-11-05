#!/usr/bin/env python3
"""
Guia de Instalação do Docker - Windows
MaraBet AI - Instalação completa do Docker Desktop
"""

import os
import subprocess
import webbrowser
from datetime import datetime

def check_system_requirements():
    """Verifica requisitos do sistema para Docker"""
    print("🔍 VERIFICANDO REQUISITOS DO SISTEMA")
    print("=" * 60)
    
    # Verificar versão do Windows
    try:
        result = subprocess.run(['ver'], capture_output=True, text=True, shell=True)
        print(f"✅ Versão do Windows: {result.stdout.strip()}")
    except:
        print("❌ Não foi possível verificar a versão do Windows")
    
    # Verificar se é Windows 10/11 Pro
    try:
        result = subprocess.run(['systeminfo'], capture_output=True, text=True, shell=True)
        if "Windows 10" in result.stdout or "Windows 11" in result.stdout:
            print("✅ Windows 10/11 detectado")
        else:
            print("⚠️ Recomendado: Windows 10/11")
    except:
        print("❌ Não foi possível verificar detalhes do sistema")
    
    # Verificar se Hyper-V está disponível
    try:
        result = subprocess.run(['dism', '/online', '/get-features', '/format:table'], capture_output=True, text=True, shell=True)
        if "Hyper-V" in result.stdout:
            print("✅ Hyper-V disponível")
        else:
            print("⚠️ Hyper-V pode não estar disponível")
    except:
        print("❌ Não foi possível verificar Hyper-V")
    
    # Verificar memória RAM
    try:
        result = subprocess.run(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory'], capture_output=True, text=True, shell=True)
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip().isdigit():
                    ram_gb = int(line.strip()) / (1024**3)
                    print(f"✅ RAM: {ram_gb:.1f} GB")
                    if ram_gb >= 4:
                        print("✅ RAM suficiente para Docker")
                    else:
                        print("⚠️ Recomendado: 4GB+ RAM")
                    break
    except:
        print("❌ Não foi possível verificar RAM")
    
    print("\n📋 REQUISITOS MÍNIMOS:")
    print("- Windows 10 64-bit: Pro, Enterprise, or Education (Build 15063+)")
    print("- Windows 11 64-bit: Home or Pro")
    print("- WSL 2 feature enabled")
    print("- Virtualization enabled in BIOS")
    print("- 4GB RAM minimum (8GB recommended)")
    print("- 20GB free disk space")

def install_docker_desktop():
    """Instala Docker Desktop no Windows"""
    print("\n🐳 INSTALANDO DOCKER DESKTOP")
    print("=" * 60)
    
    print("📥 MÉTODO 1: Download Manual (Recomendado)")
    print("-" * 40)
    print("1. Acesse: https://www.docker.com/products/docker-desktop/")
    print("2. Clique em 'Download for Windows'")
    print("3. Execute o arquivo Docker Desktop Installer.exe")
    print("4. Siga o assistente de instalação")
    print("5. Reinicie o computador quando solicitado")
    
    print("\n📥 MÉTODO 2: Download via PowerShell")
    print("-" * 40)
    print("Execute os comandos abaixo no PowerShell como Administrador:")
    print()
    print("# Baixar Docker Desktop")
    print("Invoke-WebRequest -Uri 'https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe' -OutFile 'DockerDesktopInstaller.exe'")
    print()
    print("# Executar instalador")
    print("Start-Process -FilePath 'DockerDesktopInstaller.exe' -ArgumentList 'install', '--quiet' -Wait")
    print()
    print("# Limpar arquivo temporário")
    print("Remove-Item 'DockerDesktopInstaller.exe'")
    
    print("\n📥 MÉTODO 3: Via Chocolatey (se instalado)")
    print("-" * 40)
    print("Execute no PowerShell como Administrador:")
    print()
    print("# Instalar via Chocolatey")
    print("choco install docker-desktop")
    
    print("\n📥 MÉTODO 4: Via Winget")
    print("-" * 40)
    print("Execute no PowerShell:")
    print()
    print("# Instalar via Winget")
    print("winget install Docker.DockerDesktop")

def configure_wsl2():
    """Configura WSL2 para Docker"""
    print("\n🔧 CONFIGURANDO WSL2")
    print("=" * 60)
    
    print("📋 PRÉ-REQUISITOS:")
    print("- Windows 10 versão 2004 e superior (Build 19041 e superior)")
    print("- Windows 11")
    print("- Atualizações do Windows instaladas")
    
    print("\n🔧 CONFIGURAÇÃO AUTOMÁTICA:")
    print("-" * 40)
    print("Execute no PowerShell como Administrador:")
    print()
    print("# Habilitar WSL")
    print("dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart")
    print()
    print("# Habilitar Virtual Machine Platform")
    print("dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart")
    print()
    print("# Reiniciar o computador")
    print("shutdown /r /t 0")
    print()
    print("# Após reiniciar, definir WSL2 como versão padrão")
    print("wsl --set-default-version 2")
    print()
    print("# Instalar Ubuntu (opcional)")
    print("wsl --install -d Ubuntu")
    
    print("\n🔧 CONFIGURAÇÃO MANUAL:")
    print("-" * 40)
    print("1. Abra 'Recursos do Windows' (Windows Features)")
    print("2. Marque 'Subsistema do Windows para Linux'")
    print("3. Marque 'Plataforma de Máquina Virtual'")
    print("4. Clique em OK e reinicie")
    print("5. Baixe e instale o pacote de atualização do kernel do Linux")
    print("6. Defina WSL2 como versão padrão")

def verify_installation():
    """Verifica se Docker foi instalado corretamente"""
    print("\n✅ VERIFICANDO INSTALAÇÃO")
    print("=" * 60)
    
    print("🔍 Comandos de verificação:")
    print("-" * 40)
    print("# Verificar versão do Docker")
    print("docker --version")
    print()
    print("# Verificar versão do Docker Compose")
    print("docker-compose --version")
    print()
    print("# Verificar status do Docker")
    print("docker info")
    print()
    print("# Testar Docker com Hello World")
    print("docker run hello-world")
    print()
    print("# Verificar containers em execução")
    print("docker ps")
    print()
    print("# Verificar imagens")
    print("docker images")

def troubleshoot_common_issues():
    """Solução de problemas comuns"""
    print("\n🔧 SOLUÇÃO DE PROBLEMAS COMUNS")
    print("=" * 60)
    
    print("❌ PROBLEMA: 'docker' não é reconhecido")
    print("✅ SOLUÇÃO:")
    print("1. Reinicie o computador após instalação")
    print("2. Verifique se Docker Desktop está executando")
    print("3. Adicione Docker ao PATH do sistema")
    print("4. Reinstale Docker Desktop")
    
    print("\n❌ PROBLEMA: WSL2 não está funcionando")
    print("✅ SOLUÇÃO:")
    print("1. Verifique se WSL2 está habilitado")
    print("2. Atualize o kernel do Linux")
    print("3. Reinicie o serviço Docker")
    print("4. Verifique se virtualização está habilitada no BIOS")
    
    print("\n❌ PROBLEMA: Docker Desktop não inicia")
    print("✅ SOLUÇÃO:")
    print("1. Execute como Administrador")
    print("2. Verifique se Hyper-V está habilitado")
    print("3. Verifique se virtualização está habilitada")
    print("4. Reinstale Docker Desktop")
    
    print("\n❌ PROBLEMA: Erro de permissão")
    print("✅ SOLUÇÃO:")
    print("1. Adicione usuário ao grupo 'docker-users'")
    print("2. Execute PowerShell como Administrador")
    print("3. Reinicie o computador")
    
    print("\n❌ PROBLEMA: Performance lenta")
    print("✅ SOLUÇÃO:")
    print("1. Aumente memória alocada para Docker")
    print("2. Desative antivírus temporariamente")
    print("3. Use WSL2 backend")
    print("4. Feche outros programas pesados")

def create_docker_scripts():
    """Cria scripts úteis para Docker"""
    print("\n📝 CRIANDO SCRIPTS ÚTEIS")
    print("=" * 60)
    
    # Script para verificar Docker
    docker_check_script = '''@echo off
echo 🔍 VERIFICANDO DOCKER...
echo.

echo 📊 Versão do Docker:
docker --version
echo.

echo 📊 Versão do Docker Compose:
docker-compose --version
echo.

echo 📊 Status do Docker:
docker info
echo.

echo 📊 Containers em execução:
docker ps
echo.

echo 📊 Imagens disponíveis:
docker images
echo.

echo ✅ Verificação concluída!
pause
'''
    
    with open('check_docker.bat', 'w', encoding='utf-8') as f:
        f.write(docker_check_script)
    
    print("✅ Script criado: check_docker.bat")
    
    # Script para iniciar MaraBet AI
    marabet_start_script = '''@echo off
echo 🚀 INICIANDO MARABET AI...
echo.

echo 📦 Construindo containers...
docker-compose -f docker-compose.production.yml build
echo.

echo 🚀 Iniciando serviços...
docker-compose -f docker-compose.production.yml up -d
echo.

echo 📊 Status dos containers:
docker-compose -f docker-compose.production.yml ps
echo.

echo ✅ MaraBet AI iniciado!
echo 🌐 Acesse: http://localhost:8000
echo 📊 Dashboard: http://localhost:8000/dashboard
echo.
pause
'''
    
    with open('start_marabet.bat', 'w', encoding='utf-8') as f:
        f.write(marabet_start_script)
    
    print("✅ Script criado: start_marabet.bat")
    
    # Script para parar MaraBet AI
    marabet_stop_script = '''@echo off
echo 🛑 PARANDO MARABET AI...
echo.

echo 📦 Parando containers...
docker-compose -f docker-compose.production.yml down
echo.

echo 🧹 Limpando containers órfãos...
docker system prune -f
echo.

echo ✅ MaraBet AI parado!
pause
'''
    
    with open('stop_marabet.bat', 'w', encoding='utf-8') as f:
        f.write(marabet_stop_script)
    
    print("✅ Script criado: stop_marabet.bat")

def main():
    print("🐳 MARABET AI - INSTALAÇÃO DO DOCKER NO WINDOWS")
    print("=" * 80)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📞 Contato: +224 932027393")
    
    # Verificar requisitos
    check_system_requirements()
    
    # Instalar Docker
    install_docker_desktop()
    
    # Configurar WSL2
    configure_wsl2()
    
    # Verificar instalação
    verify_installation()
    
    # Solução de problemas
    troubleshoot_common_issues()
    
    # Criar scripts
    create_docker_scripts()
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("=" * 60)
    print("1. 📥 Baixe e instale Docker Desktop")
    print("2. 🔧 Configure WSL2 se necessário")
    print("3. 🔄 Reinicie o computador")
    print("4. ✅ Execute 'check_docker.bat' para verificar")
    print("5. 🚀 Execute 'start_marabet.bat' para iniciar o sistema")
    
    print("\n📞 SUPORTE TÉCNICO:")
    print("-" * 60)
    print("• Telefone: +224 932027393")
    print("• WhatsApp: +224 932027393")
    print("• Telegram: @marabet_support")
    print("• Email: suporte@marabet.ai")
    
    print("\n🎉 INSTALAÇÃO DO DOCKER CONCLUÍDA!")
    print("Siga os próximos passos para finalizar a configuração!")

if __name__ == "__main__":
    main()
