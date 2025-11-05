#!/usr/bin/env python3
"""
Script de Configuração da API Key
MaraBet AI - Configuração automática da API key
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Cria arquivo .env com API key"""
    print("🔧 CONFIGURANDO API KEY PARA DADOS REAIS")
    print("=" * 50)
    
    # Conteúdo do arquivo .env
    env_content = """# Configurações do MaraBet AI
# API Keys para dados reais

# API-Football (OBRIGATÓRIA para dados reais)
API_FOOTBALL_KEY=747d6e19a2d3a435fdb7a419007a45fa

# The Odds API (opcional)
THE_ODDS_API_KEY=your_the_odds_api_key_here

# Configurações do banco de dados
DATABASE_URL=sqlite:///mara_bet.db

# Redis (opcional)
REDIS_URL=redis://localhost:6379

# Configurações da aplicação
SECRET_KEY=marabet_ai_secret_key_2024_production_ready
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Configurações de notificações
# Telegram - Bot: @MaraBetAIBot
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuVtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597

# Email - Yahoo
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=kilamu_10@yahoo.com.br
SMTP_PASSWORD=your_yahoo_app_password_here
NOTIFICATION_EMAIL=kilamu_10@yahoo.com.br
ADMIN_EMAIL=kilamu_10@yahoo.com.br
"""
    
    # Escrever arquivo .env
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ Arquivo .env criado com sucesso!")
        print("✅ API_FOOTBALL_KEY configurada")
        print("✅ Outras configurações definidas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {e}")
        return False

def verify_api_key():
    """Verifica se API key está configurada"""
    print("\n🔍 VERIFICANDO CONFIGURAÇÃO DA API KEY")
    print("=" * 50)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('API_FOOTBALL_KEY')
        
        if api_key and api_key != 'your_api_football_key_here':
            print(f"✅ API_FOOTBALL_KEY encontrada: {api_key[:10]}...")
            return True
        else:
            print("❌ API_FOOTBALL_KEY não configurada ou inválida")
            return False
            
    except ImportError:
        print("⚠️ python-dotenv não instalado, instalando...")
        os.system("pip install python-dotenv")
        return verify_api_key()
    except Exception as e:
        print(f"❌ Erro ao verificar API key: {e}")
        return False

def test_api_connection():
    """Testa conexão com API-Football"""
    print("\n🌐 TESTANDO CONEXÃO COM API-FOOTBALL")
    print("=" * 50)
    
    try:
        from api.real_football_api import initialize_real_football_api
        
        api_key = os.getenv('API_FOOTBALL_KEY')
        api = initialize_real_football_api(api_key)
        
        if api.test_api_connection():
            print("✅ Conexão com API-Football funcionando!")
            return True
        else:
            print("❌ Falha na conexão com API-Football")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 CONFIGURAÇÃO DO SISTEMA DE DADOS REAIS")
    print("=" * 60)
    
    # Criar arquivo .env
    if not create_env_file():
        print("❌ Falha na configuração do arquivo .env")
        return False
    
    # Verificar API key
    if not verify_api_key():
        print("❌ Falha na verificação da API key")
        return False
    
    # Testar conexão
    if not test_api_connection():
        print("❌ Falha na conexão com API-Football")
        return False
    
    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print("✅ API key configurada")
    print("✅ Conexão com API-Football funcionando")
    print("✅ Sistema pronto para coleta de dados reais")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Execute: python setup_real_data_system.py")
    print("2. Aguarde a coleta de dados históricos")
    print("3. Aguarde o treinamento dos modelos")
    print("4. Teste o sistema de validação")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
