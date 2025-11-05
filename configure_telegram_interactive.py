#!/usr/bin/env python3
"""
Configuração Interativa do Telegram
MaraBet AI - Configura o Telegram de forma interativa
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
                return True
            else:
                print(f"❌ Token inválido: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar token: {e}")
        return False

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
                        print(f"✅ Chat ID encontrado: {chat_id}")
                        print(f"   Nome: {chat.get('first_name', 'N/A')}")
                        print(f"   Username: @{chat.get('username', 'N/A')}")
                        return chat_id
                    else:
                        print("❌ Nenhum chat ID encontrado")
                        return None
                else:
                    print("❌ Nenhuma mensagem encontrada")
                    print("💡 Envie uma mensagem para o bot primeiro")
                    return None
            else:
                print(f"❌ Erro na API: {data.get('description', 'Erro desconhecido')}")
                return None
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao obter chat ID: {e}")
        return None

def test_telegram_send(token, chat_id):
    """Testa envio de mensagem"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': f"🎉 <b>MaraBet AI - Configuração Concluída!</b>\n\n"
                   f"✅ Bot configurado com sucesso!\n"
                   f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                   f"🌍 Sistema de predições internacionais ativo\n\n"
                   f"🚀 Pronto para receber predições automáticas!",
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✅ Mensagem de teste enviada com sucesso!")
                return True
            else:
                print(f"❌ Erro ao enviar: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False

def save_config(token, chat_id):
    """Salva configuração no .env"""
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
        
        print(f"✅ Configuração salva no arquivo .env")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar configuração: {e}")
        return False

def configure_telegram():
    """Configuração interativa do Telegram"""
    print("🤖 CONFIGURAÇÃO INTERATIVA DO TELEGRAM - MARABET AI")
    print("=" * 60)
    
    print("\n📋 PASSO A PASSO:")
    print("1. Abra o Telegram e procure por @BotFather")
    print("2. Digite /newbot")
    print("3. Escolha um nome para o bot")
    print("4. Escolha um username (deve terminar com 'bot')")
    print("5. Copie o TOKEN fornecido")
    print("6. Envie uma mensagem para o bot criado")
    print("7. Cole o token aqui")
    
    print("\n" + "=" * 60)
    
    # Solicitar token
    while True:
        token = input("\n🔑 Cole o TOKEN do bot aqui: ").strip()
        
        if not token:
            print("❌ Token não pode estar vazio")
            continue
        
        print(f"\n🧪 Testando token...")
        if test_telegram_token(token):
            break
        else:
            print("❌ Token inválido. Tente novamente.")
            continue
    
    # Obter chat ID
    print(f"\n🔍 Procurando chat ID...")
    chat_id = get_chat_id_from_token(token)
    
    if not chat_id:
        print("\n❌ Chat ID não encontrado")
        print("💡 Certifique-se de ter enviado uma mensagem para o bot")
        return False
    
    # Testar envio
    print(f"\n🧪 Testando envio de mensagem...")
    if test_telegram_send(token, chat_id):
        print("✅ Teste de envio bem-sucedido!")
    else:
        print("❌ Erro no teste de envio")
        return False
    
    # Salvar configuração
    print(f"\n💾 Salvando configuração...")
    if save_config(token, chat_id):
        print("✅ Configuração salva com sucesso!")
    else:
        print("❌ Erro ao salvar configuração")
        return False
    
    print(f"\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 50)
    print("✅ Bot do Telegram configurado")
    print("✅ Teste de envio realizado")
    print("✅ Configuração salva")
    print("\n🚀 Agora você pode executar:")
    print("   python run_telegram_auto.py")
    print("\n📱 E receberá predições automaticamente no Telegram!")
    
    return True

def main():
    """Função principal"""
    try:
        return configure_telegram()
    except KeyboardInterrupt:
        print("\n🛑 Configuração cancelada pelo usuário")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 Execute novamente quando estiver pronto para configurar")
