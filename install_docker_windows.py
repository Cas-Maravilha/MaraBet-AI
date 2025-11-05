#!/usr/bin/env python3
"""
Instalação Automatizada do Docker Desktop no Windows - MaraBet AI
Script para instalar e configurar Docker + Docker Compose no Windows
"""

import subprocess
import sys
import os
from datetime import datetime

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(f"🐳 {text}")
    print("=" * 80)

def print_step(number, text):
    """Imprime passo formatado"""
    print(f"\n📌 PASSO {number}: {text}")
    print("-" * 60)

def run_command(command, description):
    """Executa comando e exibe resultado"""
    print(f"\n🔧 Executando: {description}")
    print(f"💻 Comando: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"✅ Sucesso!")
            if result.stdout:
                print(f"📋 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Erro!")
            if result.stderr:
                print(f"⚠️ Erro: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout - Comando demorou muito")
        return False
    except Exception as e:
        print(f"❌ Exceção: {e}")
        return False

def check_windows_version():
    """Verifica versão do Windows"""
    print_step(1, "VERIFICAR VERSÃO DO WINDOWS")
    
    print("🔍 Verificando sistema operacional...")
    print(f"📊 Sistema: {os.name}")
    print(f"📊 Plataforma: {sys.platform}")
    
    if sys.platform != "win32":
        print("❌ Este script é apenas para Windows!")
        return False
    
    # Verificar versão do Windows
    run_command("systeminfo | findstr /C:\"OS Name\" /C:\"OS Version\"", "Informações do sistema")
    
    print("\n✅ REQUISITOS MÍNIMOS:")
    print("• Windows 10 64-bit: Pro, Enterprise, ou Education (Build 19041 ou superior)")
    print("• Windows 11 64-bit")
    print("• Hyper-V e Containers habilitados")
    print("• 4GB RAM mínimo (8GB recomendado)")
    
    return True

def check_wsl2():
    """Verifica e instala WSL2"""
    print_step(2, "VERIFICAR E INSTALAR WSL2")
    
    print("🔍 Verificando WSL2...")
    
    # Verificar se WSL está instalado
    if run_command("wsl --status", "Verificar status WSL"):
        print("✅ WSL2 já está instalado!")
        return True
    
    print("⚠️ WSL2 não encontrado. Instalando...")
    
    # Instalar WSL2
    if run_command("wsl --install", "Instalar WSL2"):
        print("✅ WSL2 instalado com sucesso!")
        print("⚠️ IMPORTANTE: Você precisará REINICIAR o computador!")
        return True
    
    print("⚠️ Não foi possível instalar WSL2 automaticamente.")
    print("📋 Instale manualmente com: wsl --install")
    return False

def install_docker_desktop_winget():
    """Instala Docker Desktop usando winget"""
    print_step(3, "INSTALAR DOCKER DESKTOP (WINGET)")
    
    print("🔍 Verificando se winget está disponível...")
    
    if not run_command("winget --version", "Verificar winget"):
        print("❌ winget não disponível!")
        return False
    
    print("📥 Instalando Docker Desktop...")
    
    if run_command("winget install Docker.DockerDesktop --accept-source-agreements --accept-package-agreements", "Instalar Docker Desktop"):
        print("✅ Docker Desktop instalado com sucesso!")
        return True
    
    print("❌ Falha ao instalar via winget")
    return False

def install_docker_desktop_chocolatey():
    """Instala Docker Desktop usando chocolatey"""
    print_step(4, "INSTALAR DOCKER DESKTOP (CHOCOLATEY)")
    
    print("🔍 Verificando se chocolatey está disponível...")
    
    if not run_command("choco --version", "Verificar chocolatey"):
        print("❌ chocolatey não disponível!")
        print("📋 Instale chocolatey de: https://chocolatey.org/install")
        return False
    
    print("📥 Instalando Docker Desktop...")
    
    if run_command("choco install docker-desktop -y", "Instalar Docker Desktop"):
        print("✅ Docker Desktop instalado com sucesso!")
        return True
    
    print("❌ Falha ao instalar via chocolatey")
    return False

def download_docker_desktop_manual():
    """Fornece instruções para download manual"""
    print_step(5, "DOWNLOAD MANUAL DO DOCKER DESKTOP")
    
    print("📥 Para instalar manualmente:")
    print()
    print("1️⃣ Acesse: https://www.docker.com/products/docker-desktop")
    print("2️⃣ Clique em 'Download for Windows'")
    print("3️⃣ Execute o instalador 'Docker Desktop Installer.exe'")
    print("4️⃣ Siga as instruções do instalador")
    print("5️⃣ Reinicie o computador se solicitado")
    print()
    print("🔗 Link direto:")
    print("https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe")
    
    return False

def verify_docker_installation():
    """Verifica se Docker foi instalado corretamente"""
    print_step(6, "VERIFICAR INSTALAÇÃO DO DOCKER")
    
    print("🔍 Verificando Docker...")
    
    # Verificar Docker
    if run_command("docker --version", "Verificar versão Docker"):
        print("✅ Docker instalado com sucesso!")
    else:
        print("❌ Docker não encontrado!")
        print("⚠️ Você pode precisar:")
        print("  1. Reiniciar o computador")
        print("  2. Abrir o Docker Desktop manualmente")
        print("  3. Aguardar o Docker inicializar")
        return False
    
    # Verificar Docker Compose
    if run_command("docker-compose --version", "Verificar versão Docker Compose"):
        print("✅ Docker Compose instalado com sucesso!")
    else:
        print("⚠️ Docker Compose não encontrado, tentando docker compose (v2)...")
        if run_command("docker compose version", "Verificar versão Docker Compose V2"):
            print("✅ Docker Compose V2 instalado com sucesso!")
        else:
            print("❌ Docker Compose não encontrado!")
            return False
    
    # Testar Docker
    print("\n🧪 Testando Docker...")
    if run_command("docker run --rm hello-world", "Executar container de teste"):
        print("✅ Docker está funcionando corretamente!")
        return True
    else:
        print("❌ Falha ao executar container de teste")
        print("⚠️ Possíveis causas:")
        print("  1. Docker Desktop não está rodando")
        print("  2. WSL2 não está configurado")
        print("  3. Hyper-V não está habilitado")
        return False

def configure_docker():
    """Configura Docker para uso no projeto"""
    print_step(7, "CONFIGURAR DOCKER PARA MARABET AI")
    
    print("⚙️ Configurações recomendadas:")
    print()
    print("📊 RECURSOS:")
    print("• CPUs: 4 (mínimo 2)")
    print("• Memória: 8GB (mínimo 4GB)")
    print("• Swap: 2GB")
    print("• Disco: 20GB")
    print()
    print("🔧 CONFIGURAR NO DOCKER DESKTOP:")
    print("1. Abra Docker Desktop")
    print("2. Vá em Settings → Resources")
    print("3. Ajuste CPUs, Memória e Disco")
    print("4. Clique em 'Apply & Restart'")
    print()
    print("🔒 SEGURANÇA:")
    print("1. Vá em Settings → General")
    print("2. Habilite 'Use the WSL 2 based engine'")
    print("3. Vá em Settings → Resources → WSL Integration")
    print("4. Habilite sua distribuição WSL")
    
    return True

def create_test_docker_compose():
    """Cria arquivo docker-compose de teste"""
    print_step(8, "CRIAR ARQUIVO DE TESTE DOCKER-COMPOSE")
    
    test_compose = """version: '3.8'

services:
  test-nginx:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./test-html:/usr/share/nginx/html
    restart: unless-stopped

  test-redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
"""
    
    try:
        with open("docker-compose.test.yml", "w", encoding="utf-8") as f:
            f.write(test_compose)
        
        print("✅ Arquivo docker-compose.test.yml criado!")
        
        # Criar diretório de teste
        os.makedirs("test-html", exist_ok=True)
        
        # Criar página HTML de teste
        html_test = """<!DOCTYPE html>
<html>
<head>
    <title>MaraBet AI - Docker Test</title>
</head>
<body>
    <h1>🐳 Docker está funcionando!</h1>
    <p>Se você está vendo esta página, o Docker foi instalado com sucesso!</p>
    <p>MaraBet AI - Sistema de Previsões Esportivas</p>
</body>
</html>
"""
        
        with open("test-html/index.html", "w", encoding="utf-8") as f:
            f.write(html_test)
        
        print("✅ Página de teste criada!")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao criar arquivos: {e}")
        return False

def test_docker_compose():
    """Testa Docker Compose"""
    print_step(9, "TESTAR DOCKER COMPOSE")
    
    print("🧪 Iniciando containers de teste...")
    
    if run_command("docker-compose -f docker-compose.test.yml up -d", "Iniciar containers"):
        print("✅ Containers iniciados com sucesso!")
        print()
        print("🌐 Acesse: http://localhost:8080")
        print("📊 Redis: localhost:6379")
        print()
        print("🛑 Para parar os containers:")
        print("   docker-compose -f docker-compose.test.yml down")
        return True
    else:
        print("❌ Falha ao iniciar containers")
        return False

def print_next_steps():
    """Imprime próximos passos"""
    print_header("PRÓXIMOS PASSOS")
    
    print("""
🎯 DOCKER INSTALADO COM SUCESSO!

📋 PRÓXIMAS AÇÕES:

1️⃣ VERIFICAR DOCKER DESKTOP:
   • Abra o Docker Desktop
   • Aguarde a inicialização completa
   • Verifique se está rodando (ícone na bandeja)

2️⃣ CONFIGURAR RECURSOS:
   • Docker Desktop → Settings → Resources
   • Ajuste CPUs: 4
   • Ajuste Memória: 8GB
   • Ajuste Disco: 20GB

3️⃣ TESTAR MARABET AI:
   cd "d:\\Usuario\\Maravilha\\Desktop\\MaraBet AI"
   docker-compose -f docker-compose.production.yml up -d

4️⃣ VERIFICAR CONTAINERS:
   docker ps
   docker-compose -f docker-compose.production.yml logs -f

5️⃣ ACESSAR APLICAÇÃO:
   • Web: http://localhost:80
   • API: http://localhost:8000
   • Dashboard: http://localhost:8501

📞 SUPORTE:
   • Telefone/WhatsApp: +224 932027393
   • Telegram: @marabet_support
   • Email: suporte@marabet.ai

🎉 PARABÉNS! Docker está pronto para uso!
""")

def main():
    """Função principal"""
    print_header("INSTALAÇÃO DOCKER DESKTOP - MARABET AI")
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📞 Contato: +224 932027393")
    
    # Verificar Windows
    if not check_windows_version():
        print("\n❌ Sistema não compatível!")
        return False
    
    # Verificar WSL2
    check_wsl2()
    
    print("\n" + "=" * 80)
    print("🔄 MÉTODOS DE INSTALAÇÃO DISPONÍVEIS:")
    print("=" * 80)
    print("1. 🟢 winget (Recomendado)")
    print("2. 🟡 chocolatey (Alternativo)")
    print("3. 🔴 Download manual (Última opção)")
    print()
    
    # Tentar instalar via winget
    if install_docker_desktop_winget():
        print("\n✅ Instalação via winget concluída!")
    elif install_docker_desktop_chocolatey():
        print("\n✅ Instalação via chocolatey concluída!")
    else:
        print("\n⚠️ Instalação automática não disponível.")
        download_docker_desktop_manual()
        print("\n📋 Após instalar manualmente, execute este script novamente para verificar.")
        return False
    
    print("\n⏰ AGUARDE...")
    print("O Docker Desktop está sendo instalado.")
    print("Este processo pode levar alguns minutos.")
    print()
    print("⚠️ IMPORTANTE:")
    print("• Você precisará REINICIAR o computador")
    print("• Após reiniciar, abra o Docker Desktop manualmente")
    print("• Aguarde o Docker inicializar completamente")
    print("• Execute este script novamente para verificar")
    
    input("\n🔄 Pressione ENTER após reiniciar e abrir o Docker Desktop...")
    
    # Verificar instalação
    if verify_docker_installation():
        print("\n✅ DOCKER INSTALADO E FUNCIONANDO!")
        
        # Configurar Docker
        configure_docker()
        
        # Criar e testar Docker Compose
        if create_test_docker_compose():
            test_docker_compose()
        
        # Próximos passos
        print_next_steps()
        
        return True
    else:
        print("\n⚠️ Docker instalado mas não está funcionando corretamente.")
        print("📋 Verifique:")
        print("  1. Docker Desktop está aberto e rodando?")
        print("  2. WSL2 está instalado?")
        print("  3. Computador foi reiniciado?")
        return False

if __name__ == "__main__":
    try:
        success = main()
        
        if success:
            print("\n🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
            sys.exit(0)
        else:
            print("\n⚠️ INSTALAÇÃO INCOMPLETA")
            print("Siga as instruções acima para completar a instalação.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Instalação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

