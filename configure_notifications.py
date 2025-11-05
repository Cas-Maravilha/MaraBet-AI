#!/usr/bin/env python3
"""
Script para configurar notificações do MaraBet AI com suas credenciais
"""

import os
import time

# Suas credenciais
TELEGRAM_BOT_TOKEN = "8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg"
YAHOO_EMAIL = "kilamu_10@yahoo.com.br"

def create_env_file():
    """Cria arquivo .env com suas credenciais"""
    print("🔮 MARABET AI - CONFIGURAÇÃO DE NOTIFICAÇÕES")
    print("=" * 60)
    
    print(f"📱 Telegram: @MaraBetAIBot")
    print(f"📧 Email: {YAHOO_EMAIL}")
    
    env_content = f"""# Configurações do MaraBet AI
# Configurado automaticamente em {time.strftime('%Y-%m-%d %H:%M:%S')}

# Configurações da API (opcional - para dados premium)
API_FOOTBALL_KEY=your_api_football_key_here
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
TELEGRAM_BOT_TOKEN={TELEGRAM_BOT_TOKEN}
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Email - Yahoo
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME={YAHOO_EMAIL}
SMTP_PASSWORD=your_yahoo_app_password_here
NOTIFICATION_EMAIL={YAHOO_EMAIL}
ADMIN_EMAIL={YAHOO_EMAIL}
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Arquivo .env criado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")
        return False

def show_telegram_instructions():
    """Mostra instruções para configurar Telegram"""
    print("\n🤖 CONFIGURAÇÃO DO TELEGRAM")
    print("=" * 40)
    
    print(f"📱 Bot: @MaraBetAIBot")
    print(f"🔑 Token: {TELEGRAM_BOT_TOKEN}")
    
    print("\n📋 INSTRUÇÕES:")
    print("1. Abra o Telegram")
    print("2. Procure por @MaraBetAIBot")
    print("3. Inicie uma conversa com o bot")
    print("4. Envie qualquer mensagem (ex: /start)")
    print("5. Execute: python get_telegram_chat_id.py")
    print("6. Copie o Chat ID e atualize o arquivo .env")
    
    print(f"\n💡 Ou execute este comando para obter o Chat ID:")
    print(f"python get_telegram_chat_id.py")

def show_yahoo_instructions():
    """Mostra instruções para configurar Yahoo"""
    print("\n📧 CONFIGURAÇÃO DO EMAIL YAHOO")
    print("=" * 40)
    
    print(f"📧 Email: {YAHOO_EMAIL}")
    print(f"🌐 Servidor: smtp.mail.yahoo.com:587")
    
    print("\n📋 COMO CONFIGURAR SENHA DE APP DO YAHOO:")
    print("1. 🌐 Acesse: https://login.yahoo.com/")
    print("2. 🔐 Faça login na sua conta Yahoo")
    print("3. ⚙️  Vá em 'Account Info' ou 'Gerenciar Conta'")
    print("4. 🔒 Clique em 'Account Security' ou 'Segurança da Conta'")
    print("5. 🔑 Procure por 'App passwords' ou 'Senhas de App'")
    print("6. ➕ Clique em 'Generate app password' ou 'Gerar senha de app'")
    print("7. 📝 Digite um nome (ex: 'MaraBet AI')")
    print("8. 📋 Copie a senha gerada (16 caracteres)")
    print("9. 🔄 Substitua 'your_yahoo_app_password_here' no arquivo .env")
    
    print(f"\n⚠️  IMPORTANTE:")
    print("- Use a senha de app, NÃO sua senha normal do Yahoo")
    print("- A senha de app tem 16 caracteres")
    print("- Se não encontrar a opção, ative a verificação em duas etapas primeiro")
    
    print(f"\n💡 Ou execute este comando para configurar:")
    print(f"python setup_yahoo_email.py")

def show_test_instructions():
    """Mostra instruções para testar"""
    print("\n🧪 TESTANDO O SISTEMA")
    print("=" * 40)
    
    print("1. 📝 Configure o Chat ID do Telegram no arquivo .env")
    print("2. 📝 Configure a senha de app do Yahoo no arquivo .env")
    print("3. 🧪 Execute: python test_notifications.py")
    print("4. 🚀 Execute: python run_automated_collector.py")
    print("5. 🌐 Execute: python run_dashboard.py")

def show_env_example():
    """Mostra exemplo do arquivo .env configurado"""
    print("\n📝 EXEMPLO DO ARQUIVO .env CONFIGURADO")
    print("=" * 40)
    
    print("TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg")
    print("TELEGRAM_CHAT_ID=123456789  # ← Substitua pelo seu Chat ID")
    print("SMTP_USERNAME=kilamu_10@yahoo.com.br")
    print("SMTP_PASSWORD=abcd1234efgh5678  # ← Substitua pela sua senha de app")
    print("NOTIFICATION_EMAIL=kilamu_10@yahoo.com.br")
    print("ADMIN_EMAIL=kilamu_10@yahoo.com.br")

def main():
    """Função principal"""
    # Criar arquivo .env
    if not create_env_file():
        return
    
    # Mostrar instruções
    show_telegram_instructions()
    show_yahoo_instructions()
    show_test_instructions()
    show_env_example()
    
    print(f"\n🎉 CONFIGURAÇÃO INICIAL CONCLUÍDA!")
    print("=" * 40)
    print("📁 Arquivo .env criado com suas credenciais")
    print("📱 Telegram: @MaraBetAIBot")
    print("📧 Email: kilamu_10@yahoo.com.br")
    
    print(f"\n📋 PRÓXIMOS PASSOS:")
    print("1. Configure o Chat ID do Telegram")
    print("2. Configure a senha de app do Yahoo")
    print("3. Teste o sistema de notificações")
    print("4. Inicie o sistema automatizado")

if __name__ == "__main__":
    main()
