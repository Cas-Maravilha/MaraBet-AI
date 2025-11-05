#!/usr/bin/env python3
"""
Script para obter o Chat ID do Telegram
"""

import requests
import json
import time

# Token do seu bot
BOT_TOKEN = "8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg"

def get_chat_id():
    """Obtém o Chat ID do Telegram"""
    print("🤖 MARABET AI - OBTENDO CHAT ID DO TELEGRAM")
    print("=" * 50)
    
    print(f"📱 Bot: @MaraBetAIBot")
    print(f"🔑 Token: {BOT_TOKEN[:10]}...")
    
    print("\n📋 INSTRUÇÕES:")
    print("1. Abra o Telegram")
    print("2. Procure por @MaraBetAIBot")
    print("3. Inicie uma conversa com o bot")
    print("4. Envie qualquer mensagem (ex: /start)")
    print("5. Aguarde 10 segundos...")
    
    # Aguardar 10 segundos
    for i in range(10, 0, -1):
        print(f"⏰ Aguardando {i} segundos...", end='\r')
        time.sleep(1)
    
    print("\n\n🔍 Buscando mensagens...")
    
    try:
        # URL da API do Telegram
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        
        # Fazer requisição
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['ok'] and data['result']:
                # Pegar a última mensagem
                last_message = data['result'][-1]
                chat_id = last_message['message']['chat']['id']
                username = last_message['message']['from'].get('username', 'N/A')
                first_name = last_message['message']['from'].get('first_name', 'N/A')
                
                print("✅ Chat ID encontrado!")
                print(f"👤 Nome: {first_name}")
                print(f"📱 Username: @{username}")
                print(f"🆔 Chat ID: {chat_id}")
                
                print(f"\n📝 Adicione esta linha ao seu arquivo .env:")
                print(f"TELEGRAM_CHAT_ID={chat_id}")
                
                # Testar envio de mensagem
                print(f"\n🧪 Testando envio de mensagem...")
                test_message_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
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
                print("💡 Certifique-se de ter enviado uma mensagem para @MaraBetAIBot")
                return None
        else:
            print(f"❌ Erro na API do Telegram: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def main():
    """Função principal"""
    chat_id = get_chat_id()
    
    if chat_id:
        print(f"\n🎉 Configuração do Telegram concluída!")
        print(f"🆔 Seu Chat ID: {chat_id}")
        print(f"\n📝 Próximos passos:")
        print(f"1. Copie o arquivo config_personal.env para .env")
        print(f"2. Substitua 'your_telegram_chat_id_here' por: {chat_id}")
        print(f"3. Configure a senha de app do Yahoo para email")
        print(f"4. Execute: python test_notifications.py")
    else:
        print(f"\n❌ Não foi possível obter o Chat ID")
        print(f"💡 Tente novamente enviando uma mensagem para @MaraBetAIBot")

if __name__ == "__main__":
    main()
