#!/usr/bin/env python3
"""
Script para configurar as credenciais originais no arquivo .env
"""

import os
import shutil
from pathlib import Path

def configurar_credenciais_originais():
    """Configura as credenciais originais no arquivo .env"""
    
    print("🔧 CONFIGURANDO CREDENCIAIS ORIGINAIS - MARABET AI")
    print("=" * 60)
    
    # Credenciais originais
    credenciais = {
        'API_FOOTBALL_KEY': '747d6e19a2d3a435fdb7a419007a45fa',
        'TELEGRAM_BOT_TOKEN': '8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg',
        'TELEGRAM_CHAT_ID': '5550091597',
        'SMTP_USERNAME': 'kilamu_10@yahoo.com.br',
        'SMTP_PASSWORD': 'your_yahoo_app_password_here',  # Precisa ser configurada
        'NOTIFICATION_EMAIL': 'kilamu_10@yahoo.com.br',
        'ADMIN_EMAIL': 'kilamu_10@yahoo.com.br'
    }
    
    # Conteúdo do arquivo .env
    env_content = f"""# Configurações pessoais do MaraBet AI
# NUNCA commite este arquivo para o repositório!

# Configurações da API (opcional - para dados premium)
API_FOOTBALL_KEY={credenciais['API_FOOTBALL_KEY']}
THE_ODDS_API_KEY=your_the_odds_api_key_here

# Configurações do banco de dados
DATABASE_URL=sqlite:///mara_bet.db

# Redis (opcional)
REDIS_URL=redis://localhost:6379

# Configurações da aplicação
SECRET_KEY=your_secret_key_here
DEBUG=False
HOST=0.0.0.0
PORT=5000

# Configurações de notificações
# Telegram - Bot: @MaraBetAIBot
TELEGRAM_BOT_TOKEN={credenciais['TELEGRAM_BOT_TOKEN']}
TELEGRAM_CHAT_ID={credenciais['TELEGRAM_CHAT_ID']}

# Email - Yahoo
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME={credenciais['SMTP_USERNAME']}
SMTP_PASSWORD={credenciais['SMTP_PASSWORD']}
NOTIFICATION_EMAIL={credenciais['NOTIFICATION_EMAIL']}
ADMIN_EMAIL={credenciais['ADMIN_EMAIL']}
"""
    
    # Fazer backup do arquivo atual
    if Path('.env').exists():
        print("📁 Fazendo backup do arquivo .env atual...")
        shutil.copy('.env', '.env.backup')
        print("✅ Backup criado: .env.backup")
    
    # Escrever novo arquivo .env
    print("🔧 Configurando credenciais originais...")
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env configurado com credenciais originais!")
    
    # Mostrar credenciais configuradas
    print("\n📋 CREDENCIAIS CONFIGURADAS:")
    print("-" * 40)
    for key, value in credenciais.items():
        if 'PASSWORD' in key:
            print(f"✅ {key}: {'*' * len(value)}")
        else:
            print(f"✅ {key}: {value}")
    
    print("\n⚠️  IMPORTANTE:")
    print("   - As credenciais originais foram configuradas")
    print("   - Você ainda precisa configurar a senha do Yahoo")
    print("   - Configure SMTP_PASSWORD no arquivo .env")
    
    return True

def testar_configuracao():
    """Testa a configuração das credenciais"""
    
    print("\n🧪 TESTANDO CONFIGURAÇÃO:")
    print("-" * 30)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Verificar credenciais
        credenciais = {
            'API_FOOTBALL_KEY': os.getenv('API_FOOTBALL_KEY'),
            'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
            'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
            'SMTP_USERNAME': os.getenv('SMTP_USERNAME'),
            'NOTIFICATION_EMAIL': os.getenv('NOTIFICATION_EMAIL'),
            'ADMIN_EMAIL': os.getenv('ADMIN_EMAIL')
        }
        
        configuradas = 0
        for key, value in credenciais.items():
            if value and value != 'your_yahoo_email_here':
                print(f"✅ {key}: Configurada")
                configuradas += 1
            else:
                print(f"❌ {key}: NÃO configurada")
        
        print(f"\n📊 Status: {configuradas}/{len(credenciais)} credenciais configuradas")
        
        if configuradas == len(credenciais):
            print("🎉 CONFIGURAÇÃO COMPLETA!")
            return True
        else:
            print("⚠️ CONFIGURAÇÃO INCOMPLETA")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar configuração: {e}")
        return False

def main():
    """Função principal"""
    
    print("🔮 MARABET AI - CONFIGURAÇÃO DE CREDENCIAIS ORIGINAIS")
    print("=" * 70)
    
    # Configurar credenciais
    if configurar_credenciais_originais():
        print("\n🔧 CONFIGURAÇÃO CONCLUÍDA!")
        
        # Testar configuração
        if testar_configuracao():
            print("\n🎉 SISTEMA CONFIGURADO COM SUCESSO!")
            print("✅ Credenciais originais configuradas")
            print("✅ Sistema pronto para uso")
            
            print("\n🚀 PRÓXIMOS PASSOS:")
            print("1. Configure a senha do Yahoo no arquivo .env")
            print("2. Execute: python teste_final_sistema.py")
            print("3. Execute: python test_api_keys.py")
        else:
            print("\n⚠️ Erro na configuração")
    else:
        print("\n❌ Erro ao configurar credenciais")

if __name__ == "__main__":
    main()
