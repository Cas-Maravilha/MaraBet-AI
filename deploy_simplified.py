#!/usr/bin/env python3
"""
Script de Deploy Simplificado - MaraBet AI
Deploy com docker-compose.production.yml simplificado
"""

import subprocess
import os
import sys
from datetime import datetime

def check_docker():
    """Verifica se Docker está instalado e funcionando"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker não encontrado")
            return False
    except FileNotFoundError:
        print("❌ Docker não instalado")
        return False

def check_docker_compose():
    """Verifica se Docker Compose está disponível"""
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker Compose encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker Compose não encontrado")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose não instalado")
        return False

def check_env_file():
    """Verifica se arquivo .env.production existe"""
    if os.path.exists('.env.production'):
        print("✅ Arquivo .env.production encontrado")
        return True
    else:
        print("❌ Arquivo .env.production não encontrado")
        print("💡 Execute: python create_production_structure.py")
        return False

def check_nginx_config():
    """Verifica se nginx.conf existe"""
    if os.path.exists('nginx.conf'):
        print("✅ Arquivo nginx.conf encontrado")
        return True
    else:
        print("❌ Arquivo nginx.conf não encontrado")
        print("💡 Copiando nginx.conf do diretório deploy...")
        try:
            subprocess.run(['copy', 'deploy\\nginx\\nginx.conf', 'nginx.conf'], shell=True)
            print("✅ nginx.conf copiado com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao copiar nginx.conf: {e}")
            return False

def build_and_deploy():
    """Constrói e faz deploy da aplicação"""
    print("\n🚀 Iniciando deploy do MaraBet AI...")
    
    try:
        # Parar containers existentes
        print("🛑 Parando containers existentes...")
        subprocess.run(['docker-compose', '-f', 'docker-compose.production.yml', 'down'], 
                      check=False)
        
        # Construir e iniciar containers
        print("🔨 Construindo e iniciando containers...")
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.production.yml', 'up', '--build', '-d'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Deploy realizado com sucesso!")
            return True
        else:
            print(f"❌ Erro no deploy: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante deploy: {e}")
        return False

def check_containers():
    """Verifica status dos containers"""
    print("\n📊 Status dos containers:")
    try:
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.production.yml', 'ps'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Erro ao verificar containers: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def show_logs():
    """Mostra logs da aplicação"""
    print("\n📝 Logs da aplicação:")
    try:
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.production.yml', 'logs', 'web'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Erro ao obter logs: {result.stderr}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    print("🎯 MARABET AI - DEPLOY SIMPLIFICADO")
    print("=" * 50)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Verificações pré-deploy
    print("\n🔍 VERIFICAÇÕES PRÉ-DEPLOY:")
    print("-" * 30)
    
    checks = [
        ("Docker", check_docker),
        ("Docker Compose", check_docker_compose),
        (".env.production", check_env_file),
        ("nginx.conf", check_nginx_config)
    ]
    
    all_checks_passed = True
    for name, check_func in checks:
        if not check_func():
            all_checks_passed = False
    
    if not all_checks_passed:
        print("\n❌ Verificações falharam. Corrija os problemas antes de continuar.")
        return False
    
    print("\n✅ Todas as verificações passaram!")
    
    # Deploy
    if build_and_deploy():
        print("\n🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        
        # Verificar containers
        check_containers()
        
        # Mostrar logs
        show_logs()
        
        print("\n🌐 ACESSO À APLICAÇÃO:")
        print("-" * 30)
        print("• Aplicação: http://localhost:8000")
        print("• Nginx: http://localhost:80")
        print("• Redis: localhost:6379")
        
        print("\n📊 COMANDOS ÚTEIS:")
        print("-" * 30)
        print("• Ver status: docker-compose -f docker-compose.production.yml ps")
        print("• Ver logs: docker-compose -f docker-compose.production.yml logs")
        print("• Parar: docker-compose -f docker-compose.production.yml down")
        print("• Reiniciar: docker-compose -f docker-compose.production.yml restart")
        
        return True
    else:
        print("\n❌ Deploy falhou. Verifique os logs acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
