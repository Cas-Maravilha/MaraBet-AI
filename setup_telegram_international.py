#!/usr/bin/env python3
"""
Configuração do Telegram para Competições Internacionais
MaraBet AI - Configura o bot do Telegram para envio automático
"""

import os
import sys
import requests
import json
from datetime import datetime

def setup_telegram_bot():
    """Configura o bot do Telegram"""
    print("🤖 CONFIGURAÇÃO DO TELEGRAM - MARABET AI")
    print("=" * 60)
    
    print("\n📋 PASSO A PASSO PARA CONFIGURAR O TELEGRAM:")
    print("=" * 50)
    print("1. Abra o Telegram no seu celular ou computador")
    print("2. Procure por @BotFather")
    print("3. Digite /newbot")
    print("4. Escolha um nome para o bot (ex: MaraBet AI Predictions)")
    print("5. Escolha um username para o bot (ex: marabet_ai_bot)")
    print("6. Copie o TOKEN que o BotFather fornecer")
    print("7. Para obter o CHAT_ID, envie uma mensagem para o bot e acesse:")
    print("   https://api.telegram.org/bot<SEU_TOKEN>/getUpdates")
    print("   Procure por 'chat':{'id': NUMERO}")
    
    print("\n" + "=" * 60)
    
    # Solicitar token do bot
    bot_token = input("\n🔑 Digite o TOKEN do bot (ou pressione Enter para pular): ").strip()
    
    if not bot_token:
        print("⚠️ Token não fornecido. Configuração cancelada.")
        return False
    
    # Solicitar chat ID
    chat_id = input("💬 Digite o CHAT_ID (ou pressione Enter para pular): ").strip()
    
    if not chat_id:
        print("⚠️ Chat ID não fornecido. Configuração cancelada.")
        return False
    
    # Testar configuração
    print("\n🧪 TESTANDO CONFIGURAÇÃO...")
    print("-" * 30)
    
    try:
        # Testar envio de mensagem
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': f"🤖 <b>MaraBet AI - Teste de Configuração</b>\n\n"
                   f"✅ Bot configurado com sucesso!\n"
                   f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                   f"🌍 Sistema de predições internacionais ativo\n\n"
                   f"🚀 Pronto para receber predições automáticas!",
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Teste de envio bem-sucedido!")
            print("📱 Verifique se recebeu a mensagem no Telegram")
            
            # Salvar configurações no .env
            env_content = f"""# Configurações do Telegram para MaraBet AI
TELEGRAM_BOT_TOKEN={bot_token}
TELEGRAM_CHAT_ID={chat_id}

# Configurações da API Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Configurações do banco de dados
DATABASE_URL=sqlite:///mara_bet.db
"""
            
            try:
                with open('.env', 'w', encoding='utf-8') as f:
                    f.write(env_content)
                print("✅ Configurações salvas no arquivo .env")
            except Exception as e:
                print(f"⚠️ Erro ao salvar .env: {e}")
                print("💡 Salve manualmente as configurações:")
                print(f"TELEGRAM_BOT_TOKEN={bot_token}")
                print(f"TELEGRAM_CHAT_ID={chat_id}")
            
            print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 50)
            print("✅ Bot do Telegram configurado")
            print("✅ Teste de envio realizado")
            print("✅ Configurações salvas")
            print("\n🚀 Agora você pode executar:")
            print("   python auto_telegram_international.py")
            print("\n📱 E receberá predições automaticamente no Telegram!")
            
            return True
            
        else:
            print(f"❌ Erro no teste: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False

def test_existing_config():
    """Testa configuração existente"""
    print("🧪 TESTANDO CONFIGURAÇÃO EXISTENTE...")
    print("=" * 50)
    
    # Carregar variáveis do .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv não instalado. Instale com: pip install python-dotenv")
        return False
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Configurações do Telegram não encontradas no .env")
        print("💡 Execute: python setup_telegram_international.py")
        return False
    
    print(f"✅ Token encontrado: {bot_token[:10]}...")
    print(f"✅ Chat ID encontrado: {chat_id}")
    
    # Testar envio
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': f"🧪 <b>Teste de Configuração Existente</b>\n\n"
                   f"✅ Configuração funcionando!\n"
                   f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
                   f"🌍 Sistema de predições internacionais ativo",
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Teste de envio bem-sucedido!")
            print("📱 Verifique se recebeu a mensagem no Telegram")
            return True
        else:
            print(f"❌ Erro no teste: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False

def main():
    """Função principal"""
    print("🤖 CONFIGURAÇÃO DO TELEGRAM - MARABET AI")
    print("=" * 60)
    
    print("Escolha uma opção:")
    print("1. Configurar novo bot do Telegram")
    print("2. Testar configuração existente")
    print("3. Sair")
    
    try:
        choice = input("\nDigite sua escolha (1-3): ").strip()
        
        if choice == "1":
            return setup_telegram_bot()
        elif choice == "2":
            return test_existing_config()
        elif choice == "3":
            print("👋 Até logo!")
            return True
        else:
            print("❌ Escolha inválida")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Operação cancelada pelo usuário")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
