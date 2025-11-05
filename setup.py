#!/usr/bin/env python3
"""
Script de configuração e instalação do MaraBet AI
"""

import subprocess
import sys
import os

def install_requirements():
    """Instala as dependências necessárias"""
    print("Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Erro ao instalar dependências: {e}")
        return False

def create_directories():
    """Cria diretórios necessários"""
    directories = ['models', 'static', 'templates', 'logs', 'data']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Diretório criado: {directory}")
        else:
            print(f"✓ Diretório já existe: {directory}")

def create_env_file():
    """Cria arquivo .env se não existir"""
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("""# Configurações da API (opcional - para dados premium)
API_KEY=your_api_key_here

# Configurações do banco de dados
DATABASE_URL=sqlite:///mara_bet.db

# Configurações da aplicação
SECRET_KEY=mara-bet-secret-key-2024
DEBUG=False
HOST=0.0.0.0
PORT=5000
""")
        print("✓ Arquivo .env criado")
    else:
        print("✓ Arquivo .env já existe")

def test_installation():
    """Testa se a instalação foi bem-sucedida"""
    print("\nTestando instalação...")
    try:
        from data_collector import SportsDataCollector
        from feature_engineering import FeatureEngineer
        from ml_models import BettingPredictor
        print("✓ Imports funcionando corretamente")
        
        # Teste básico
        collector = SportsDataCollector()
        matches = collector.get_football_matches()
        print(f"✓ Coleta de dados funcionando ({len(matches)} jogos)")
        
        return True
    except Exception as e:
        print(f"✗ Erro no teste: {e}")
        return False

def main():
    print("=== MARABET AI - CONFIGURAÇÃO ===")
    print("Sistema de Análise Preditiva de Apostas Esportivas")
    print("=" * 40)
    
    # Instala dependências
    if not install_requirements():
        print("Falha na instalação das dependências")
        return False
    
    # Cria diretórios
    create_directories()
    
    # Cria arquivo .env
    create_env_file()
    
    # Testa instalação
    if test_installation():
        print("\n✓ Instalação concluída com sucesso!")
        print("\nPara executar o sistema:")
        print("  python main.py --web          # Interface web")
        print("  python main.py --mode full    # Pipeline completo")
        print("  python run_example.py         # Exemplo de execução")
        return True
    else:
        print("\n✗ Instalação falhou")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
