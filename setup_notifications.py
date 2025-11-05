#!/usr/bin/env python3
"""
Script para configurar notificações do MaraBet AI
"""

import os
import sys
import asyncio
import requests
import time

# Suas credenciais
TELEGRAM_BOT_TOKEN = "8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg"
YAHOO_EMAIL = "kilamu_10@yahoo.com.br"

def create_env_file():
    """Cria arquivo .env com as configurações"""
    print("📝 CRIANDO ARQUIVO .env")
    print("=" * 30)
    
    env_content = f"""# Configurações do MaraBet AI
# Gerado automaticamente em {time.strftime('%Y-%m-%d %H:%M:%S')}

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

def get_telegram_chat_id():
    """Obtém o Chat ID do Telegram"""
    print("\n🤖 CONFIGURANDO TELEGRAM")
    print("=" * 30)
    
    print(f"📱 Bot: @MaraBetAIBot")
    print(f"🔑 Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    
    print("\n📋 INSTRUÇÕES:")
    print("1. Abra o Telegram")
    print("2. Procure por @MaraBetAIBot")
    print("3. Inicie uma conversa com o bot")
    print("4. Envie qualquer mensagem (ex: /start)")
    print("5. Pressione Enter quando estiver pronto...")
    
    input("Pressione Enter quando tiver enviado a mensagem...")
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['ok'] and data['result']:
                last_message = data['result'][-1]
                chat_id = last_message['message']['chat']['id']
                username = last_message['message']['from'].get('username', 'N/A')
                first_name = last_message['message']['from'].get('first_name', 'N/A')
                
                print("✅ Chat ID encontrado!")
                print(f"👤 Nome: {first_name}")
                print(f"📱 Username: @{username}")
                print(f"🆔 Chat ID: {chat_id}")
                
                # Testar envio de mensagem
                print("\n🧪 Testando envio de mensagem...")
                test_message_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                test_payload = {
                    'chat_id': chat_id,
                    'text': '🎉 Teste de notificação do MaraBet AI!\n\nSe você recebeu esta mensagem, a configuração está correta!',
                    'parse_mode': 'HTML'
                }
                
                test_response = requests.post(test_message_url, json=test_payload, timeout=10)
                
                if test_response.status_code == 200:
                    print("✅ Mensagem de teste enviada com sucesso!")
                    print("📱 Verifique seu Telegram para confirmar o recebimento.")
                else:
                    print(f"❌ Erro ao enviar mensagem de teste: {test_response.status_code}")
                
                return chat_id
            else:
                print("❌ Nenhuma mensagem encontrada!")
                return None
        else:
            print(f"❌ Erro na API do Telegram: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def setup_yahoo_email():
    """Configura email do Yahoo"""
    print("\n📧 CONFIGURANDO EMAIL YAHOO")
    print("=" * 30)
    
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
    print("9. 🔄 Use esta senha no lugar da sua senha normal")
    
    print(f"\n⚠️  IMPORTANTE:")
    print("- Use a senha de app, NÃO sua senha normal do Yahoo")
    print("- A senha de app tem 16 caracteres")
    print("- Se não encontrar a opção, ative a verificação em duas etapas primeiro")
    
    print(f"\n🔑 Digite sua senha de app do Yahoo (16 caracteres):")
    password = input("Senha: ").strip()
    
    if len(password) != 16:
        print("⚠️  A senha de app do Yahoo deve ter 16 caracteres")
        return None
    
    return password

def update_env_file(chat_id, yahoo_password):
    """Atualiza o arquivo .env com as credenciais"""
    print("\n📝 ATUALIZANDO ARQUIVO .env")
    print("=" * 30)
    
    try:
        # Ler arquivo .env
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir valores
        content = content.replace('your_telegram_chat_id_here', str(chat_id))
        content = content.replace('your_yahoo_app_password_here', yahoo_password)
        
        # Salvar arquivo atualizado
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Arquivo .env atualizado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar .env: {e}")
        return False

async def test_notifications():
    """Testa o sistema de notificações"""
    print("\n🧪 TESTANDO SISTEMA DE NOTIFICAÇÕES")
    print("=" * 30)
    
    try:
        # Importar após criar .env
        from notifications.notification_integrator import test_notifications
        
        print("🔔 Testando notificações...")
        results = await test_notifications()
        
        success_count = sum(results.values())
        total_tests = len(results)
        
        print(f"\n📊 Resultado: {success_count}/{total_tests} testes aprovados")
        
        if success_count == total_tests:
            print("🎉 Todas as notificações funcionando!")
        else:
            print("⚠️  Algumas notificações falharam")
        
        return success_count == total_tests
        
    except Exception as e:
        print(f"❌ Erro ao testar notificações: {e}")
        return False

def main():
    """Função principal"""
    print("🔮 MARABET AI - CONFIGURAÇÃO DE NOTIFICAÇÕES")
    print("=" * 60)
    
    print(f"📱 Telegram: @MaraBetAIBot")
    print(f"📧 Email: {YAHOO_EMAIL}")
    
    # Criar arquivo .env
    if not create_env_file():
        return
    
    # Configurar Telegram
    chat_id = get_telegram_chat_id()
    if not chat_id:
        print("❌ Não foi possível configurar Telegram")
        return
    
    # Configurar Email
    yahoo_password = setup_yahoo_email()
    if not yahoo_password:
        print("❌ Não foi possível configurar Email")
        return
    
    # Atualizar arquivo .env
    if not update_env_file(chat_id, yahoo_password):
        return
    
    print(f"\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 30)
    print(f"📱 Telegram: @MaraBetAIBot (Chat ID: {chat_id})")
    print(f"📧 Email: {YAHOO_EMAIL}")
    print(f"📁 Arquivo: .env")
    
    print(f"\n🧪 Para testar o sistema completo:")
    print(f"python test_notifications.py")
    
    print(f"\n🚀 Para iniciar o sistema:")
    print(f"python run_automated_collector.py")
    
    print(f"\n🌐 Para acessar o dashboard:")
    print(f"python run_dashboard.py")

if __name__ == "__main__":
    main()
