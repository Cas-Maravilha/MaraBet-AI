#!/usr/bin/env python3
"""
Sistema Básico de Dados Esportivos - MaraBet AI
Script de Instalação e Configuração

Este script automatiza a instalação e configuração inicial do sistema.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Exibe o cabeçalho do sistema."""
    print("🏈 SISTEMA BÁSICO DE DADOS ESPORTIVOS - MARABET AI")
    print("=" * 60)
    print("Script de Instalação e Configuração")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica se a versão do Python é compatível."""
    print("🐍 Verificando versão do Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ é necessário!")
        print(f"   Versão atual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def install_dependencies():
    """Instala as dependências do sistema."""
    print("\n📦 Instalando dependências...")
    
    try:
        # Atualiza pip
        print("   • Atualizando pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Instala dependências
        print("   • Instalando dependências do requirements.txt...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        
        print("✅ Dependências instaladas com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def create_directories():
    """Cria os diretórios necessários."""
    print("\n📁 Criando estrutura de diretórios...")
    
    directories = [
        "data",
        "logs", 
        "cache",
        "backups",
        "models",
        "analysis"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")
    
    print("✅ Estrutura de diretórios criada!")

def create_env_file():
    """Cria arquivo .env de exemplo."""
    print("\n🔧 Criando arquivo de configuração...")
    
    env_content = """# Sistema Básico de Dados Esportivos - MaraBet AI
# Arquivo de configuração de ambiente

# API Keys (opcional - sistema funciona sem elas)
API_FOOTBALL_KEY=your_api_key_here
API_FOOTBALL_HOST=api-football-v1.p.rapidapi.com

# Configurações do Banco de Dados
DATABASE_URL=sqlite:///data/sports_data.db

# Configurações de Cache
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Configurações de Logging
LOG_LEVEL=INFO
LOG_FILE=logs/sports_system.log

# Configurações de ML
ML_MODEL_PATH=models/
ML_RETRAIN_DAYS=7

# Configurações de Análise
MIN_CONFIDENCE=0.70
MIN_EV=0.05
KELLY_FRACTION=0.25
"""
    
    env_file = Path("config/.env")
    env_file.parent.mkdir(exist_ok=True)
    
    if not env_file.exists():
        env_file.write_text(env_content)
        print("   ✅ config/.env criado")
    else:
        print("   ⚠️ config/.env já existe")
    
    print("✅ Arquivo de configuração criado!")

def test_installation():
    """Testa se a instalação foi bem-sucedida."""
    print("\n🧪 Testando instalação...")
    
    try:
        # Testa imports principais
        import requests
        import pandas
        import numpy
        import sqlalchemy
        import sklearn
        print("   ✅ Imports principais - OK")
        
        # Testa sistema básico
        from main import SportsDataSystem
        system = SportsDataSystem()
        print("   ✅ Sistema principal - OK")
        
        # Limpa recursos
        system.cleanup()
        print("   ✅ Limpeza de recursos - OK")
        
        print("✅ Instalação testada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def show_next_steps():
    """Mostra os próximos passos para o usuário."""
    print("\n🎯 PRÓXIMOS PASSOS")
    print("=" * 40)
    print()
    print("1. 🔑 Configure API Keys (opcional):")
    print("   • Edite config/.env")
    print("   • Adicione sua chave da API-Football")
    print("   • Sistema funciona sem API keys (modo simulado)")
    print()
    print("2. 🚀 Execute o sistema:")
    print("   • Demonstração completa: python demo.py")
    print("   • Análise específica: python main.py --home-team 'Manchester City' --away-team 'Arsenal'")
    print()
    print("3. 📊 Personalize configurações:")
    print("   • Edite config/settings.py")
    print("   • Ajuste parâmetros de ML e análise")
    print("   • Configure ligas e temporadas")
    print()
    print("4. 📚 Consulte a documentação:")
    print("   • README.md - Guia completo")
    print("   • Exemplos de uso e configuração")
    print()

def main():
    """Função principal de instalação."""
    print_header()
    
    # Verifica Python
    if not check_python_version():
        sys.exit(1)
    
    # Instala dependências
    if not install_dependencies():
        print("\n❌ Falha na instalação das dependências!")
        print("   Tente instalar manualmente: pip install -r requirements.txt")
        sys.exit(1)
    
    # Cria estrutura
    create_directories()
    
    # Cria configuração
    create_env_file()
    
    # Testa instalação
    if not test_installation():
        print("\n⚠️ Instalação concluída com avisos!")
        print("   O sistema pode ter limitações.")
    else:
        print("\n🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    
    # Mostra próximos passos
    show_next_steps()

if __name__ == "__main__":
    main()

