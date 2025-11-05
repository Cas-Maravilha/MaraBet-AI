#!/usr/bin/env python3
"""
Teste da Configuração do Telegram
MaraBet AI - Testa se o Telegram está configurado corretamente
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

def test_telegram_config():
    """Testa configuração do Telegram"""
    print("🧪 TESTE DA CONFIGURAÇÃO DO TELEGRAM - MARABET AI")
    print("=" * 60)
    
    # Carregar configurações
    load_dotenv()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or token == 'SEU_TOKEN_AQUI':
        print("❌ Token não configurado")
        print("💡 Configure TELEGRAM_BOT_TOKEN no arquivo .env")
        return False
    
    if not chat_id or chat_id == 'SEU_CHAT_ID_AQUI':
        print("❌ Chat ID não configurado")
        print("💡 Configure TELEGRAM_CHAT_ID no arquivo .env")
        return False
    
    print(f"✅ Token: {token[:10]}...")
    print(f"✅ Chat ID: {chat_id}")
    
    # Testar token
    print("\n🧪 Testando token...")
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
            else:
                print(f"❌ Token inválido: {data.get('description')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar token: {e}")
        return False
    
    # Testar envio
    print("\n🧪 Testando envio de mensagem...")
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': f"🎉 <b>MaraBet AI - Teste de Configuração</b>\n\n"
                   f"✅ Configuração funcionando perfeitamente!\n"
                   f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                   f"🌍 Sistema de predições internacionais ativo\n\n"
                   f"🚀 Pronto para receber predições automáticas!",
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print("✅ Mensagem enviada com sucesso!")
                print("📱 Verifique se recebeu a mensagem no Telegram")
                return True
            else:
                print(f"❌ Erro ao enviar: {data.get('description')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False

if __name__ == "__main__":
    success = test_telegram_config()
    if success:
        print("\n🎉 CONFIGURAÇÃO FUNCIONANDO PERFEITAMENTE!")
        print("🚀 Execute: python run_telegram_auto.py")
    else:
        print("\n💡 Siga o guia de configuração")
