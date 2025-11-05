#!/usr/bin/env python3
"""
Correção da Configuração do Telegram
MaraBet AI - Corrige problemas de configuração do Telegram
"""

import os
import requests
import json
from datetime import datetime

def test_telegram_token(token):
    """Testa se o token do Telegram é válido"""
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Token válido!")
                print(f"   Bot: {bot_info.get('first_name', 'N/A')}")
                print(f"   Username: @{bot_info.get('username', 'N/A')}")
                print(f"   ID: {bot_info.get('id', 'N/A')}")
                return True
            else:
                print(f"❌ Token inválido: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar token: {e}")
        return False

def test_telegram_chat_id(token, chat_id):
    """Testa se o chat ID é válido"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': f"🧪 <b>Teste de Configuração</b>\n\n"
                   f"✅ Chat ID válido!\n"
                   f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                   f"🤖 MaraBet AI funcionando corretamente",
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✅ Chat ID válido!")
                print(f"   Mensagem enviada com sucesso")
                return True
            else:
                print(f"❌ Chat ID inválido: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar chat ID: {e}")
        return False

def get_chat_id_from_updates(token):
    """Obtém chat ID das atualizações do bot"""
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                updates = data.get('result', [])
                if updates:
                    # Pegar o último chat ID
                    last_update = updates[-1]
                    message = last_update.get('message', {})
                    chat = message.get('chat', {})
                    chat_id = chat.get('id')
                    
                    if chat_id:
                        print(f"✅ Chat ID encontrado: {chat_id}")
                        print(f"   Nome: {chat.get('first_name', 'N/A')}")
                        print(f"   Username: @{chat.get('username', 'N/A')}")
                        return chat_id
                    else:
                        print("❌ Nenhum chat ID encontrado nas atualizações")
                        return None
                else:
                    print("❌ Nenhuma atualização encontrada")
                    print("💡 Envie uma mensagem para o bot primeiro")
                    return None
            else:
                print(f"❌ Erro na API: {data.get('description', 'Erro desconhecido')}")
                return None
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao obter chat ID: {e}")
        return None

def create_new_bot():
    """Guia para criar um novo bot"""
    print("\n🤖 GUIA PARA CRIAR NOVO BOT DO TELEGRAM")
    print("=" * 50)
    print("1. Abra o Telegram no seu celular ou computador")
    print("2. Procure por @BotFather")
    print("3. Digite /newbot")
    print("4. Escolha um nome para o bot (ex: MaraBet AI Predictions)")
    print("5. Escolha um username para o bot (ex: marabet_ai_bot)")
    print("6. Copie o TOKEN que o BotFather fornecer")
    print("7. Envie uma mensagem para o bot criado")
    print("8. Execute este script novamente para obter o Chat ID")
    print("\n" + "=" * 50)

def fix_telegram_config():
    """Corrige a configuração do Telegram"""
    print("🔧 CORREÇÃO DA CONFIGURAÇÃO DO TELEGRAM - MARABET AI")
    print("=" * 60)
    
    # Carregar configurações atuais
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("❌ python-dotenv não instalado")
        print("💡 Instale com: pip install python-dotenv")
        return False
    
    current_token = os.getenv('TELEGRAM_BOT_TOKEN')
    current_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"📋 CONFIGURAÇÃO ATUAL:")
    print(f"   Token: {current_token[:10] + '...' if current_token else 'NÃO ENCONTRADO'}")
    print(f"   Chat ID: {current_chat_id if current_chat_id else 'NÃO ENCONTRADO'}")
    
    # Testar token atual
    if current_token:
        print(f"\n🧪 TESTANDO TOKEN ATUAL...")
        print("-" * 30)
        token_valid = test_telegram_token(current_token)
        
        if token_valid and current_chat_id:
            print(f"\n🧪 TESTANDO CHAT ID ATUAL...")
            print("-" * 30)
            chat_valid = test_telegram_chat_id(current_token, current_chat_id)
            
            if chat_valid:
                print(f"\n✅ CONFIGURAÇÃO FUNCIONANDO PERFEITAMENTE!")
                return True
            else:
                print(f"\n❌ Chat ID inválido. Tentando obter novo...")
                print("-" * 30)
                new_chat_id = get_chat_id_from_updates(current_token)
                if new_chat_id:
                    # Atualizar .env com novo chat ID
                    update_env_file(current_token, new_chat_id)
                    return True
        else:
            print(f"\n❌ Token inválido. Precisa criar novo bot.")
            create_new_bot()
            return False
    else:
        print(f"\n❌ Token não encontrado. Precisa configurar.")
        create_new_bot()
        return False

def update_env_file(token, chat_id):
    """Atualiza o arquivo .env com as configurações corretas"""
    try:
        env_content = f"""# Configurações do Telegram para MaraBet AI
TELEGRAM_BOT_TOKEN={token}
TELEGRAM_CHAT_ID={chat_id}

# Configurações da API Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Configurações do banco de dados
DATABASE_URL=sqlite:///mara_bet.db
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ Arquivo .env atualizado com sucesso!")
        print(f"   Token: {token[:10]}...")
        print(f"   Chat ID: {chat_id}")
        
        # Testar nova configuração
        print(f"\n🧪 TESTANDO NOVA CONFIGURAÇÃO...")
        print("-" * 30)
        if test_telegram_chat_id(token, chat_id):
            print(f"\n🎉 CONFIGURAÇÃO CORRIGIDA COM SUCESSO!")
            return True
        else:
            print(f"\n❌ Ainda há problemas com a configuração")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao atualizar .env: {e}")
        return False

def main():
    """Função principal"""
    return fix_telegram_config()

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🚀 Agora você pode executar:")
        print(f"   python run_telegram_auto.py")
    else:
        print(f"\n💡 Siga as instruções para configurar o Telegram")
