#!/usr/bin/env python3
"""
Obter Token Válido do Telegram
MaraBet AI - Ajuda a obter um token válido do Telegram
"""

import requests
import json

def test_token(token):
    """Testa se um token é válido"""
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                return True, bot_info
            else:
                return False, data.get('description', 'Erro desconhecido')
        else:
            return False, f"Erro HTTP {response.status_code}"
            
    except Exception as e:
        return False, str(e)

def get_chat_id_from_token(token):
    """Obtém chat ID usando o token"""
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
                        return True, chat_id, chat
                    else:
                        return False, "Nenhum chat ID encontrado", None
                else:
                    return False, "Nenhuma mensagem encontrada", None
            else:
                return False, data.get('description', 'Erro na API'), None
        else:
            return False, f"Erro HTTP {response.status_code}", None
            
    except Exception as e:
        return False, str(e), None

def send_test_message(token, chat_id):
    """Envia mensagem de teste"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': f"🎉 <b>MaraBet AI - Teste de Configuração</b>\n\n"
                   f"✅ Configuração funcionando perfeitamente!\n"
                   f"👤 Usuário: Mara Maravilha\n"
                   f"🌍 Idioma: pt-br\n"
                   f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                   f"🤖 Sistema de predições internacionais ativo\n\n"
                   f"🚀 Pronto para receber predições automáticas!",
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                return True, "Mensagem enviada com sucesso!"
            else:
                return False, data.get('description', 'Erro ao enviar')
        else:
            return False, f"Erro HTTP {response.status_code}"
            
    except Exception as e:
        return False, str(e)

def main():
    """Função principal"""
    print("🔍 DIAGNÓSTICO DO TELEGRAM - MARABET AI")
    print("=" * 50)
    
    # Token atual (exemplo - precisa ser substituído por um válido)
    current_token = "8227157482:AAHqJqJqJqJqJqJqJqJqJqJqJqJqJqJqJq"
    current_chat_id = "5550091597"
    
    print(f"📋 CONFIGURAÇÃO ATUAL:")
    print(f"   Token: {current_token[:10]}...")
    print(f"   Chat ID: {current_chat_id}")
    
    # Testar token atual
    print(f"\n🧪 TESTANDO TOKEN ATUAL...")
    print("-" * 30)
    is_valid, result = test_token(current_token)
    
    if is_valid:
        print(f"✅ Token válido!")
        print(f"   Bot: {result.get('first_name', 'N/A')}")
        print(f"   Username: @{result.get('username', 'N/A')}")
        
        # Testar envio
        print(f"\n🧪 TESTANDO ENVIO DE MENSAGEM...")
        print("-" * 30)
        success, message = send_test_message(current_token, current_chat_id)
        
        if success:
            print(f"✅ {message}")
            print(f"📱 Verifique se recebeu a mensagem no Telegram")
            print(f"\n🎉 CONFIGURAÇÃO FUNCIONANDO PERFEITAMENTE!")
            return True
        else:
            print(f"❌ Erro ao enviar: {message}")
            return False
    else:
        print(f"❌ Token inválido: {result}")
        
        print(f"\n💡 SOLUÇÃO:")
        print("=" * 20)
        print("1. O token atual é inválido ou expirado")
        print("2. Você precisa criar um novo bot no Telegram")
        print("3. Siga estes passos:")
        print("   • Abra o Telegram")
        print("   • Procure por @BotFather")
        print("   • Digite /newbot")
        print("   • Escolha um nome: 'MaraBet AI Predictions'")
        print("   • Escolha username: 'marabet_ai_bot'")
        print("   • Copie o TOKEN fornecido")
        print("   • Envie uma mensagem para o bot")
        print("   • Execute este script novamente")
        
        return False

if __name__ == "__main__":
    from datetime import datetime
    main()
