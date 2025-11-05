#!/usr/bin/env python3
"""
Configuração Automática do Telegram
MaraBet AI - Configura o Telegram automaticamente
"""

import os
import requests
import json
from datetime import datetime

def create_env_file():
    """Cria arquivo .env com configurações padrão"""
    env_content = """# Configurações do Telegram para MaraBet AI
# SUBSTITUA PELO SEU TOKEN E CHAT ID
TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI
TELEGRAM_CHAT_ID=SEU_CHAT_ID_AQUI

# Configurações da API Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Configurações do banco de dados
DATABASE_URL=sqlite:///mara_bet.db
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Arquivo .env criado com configurações padrão")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")
        return False

def show_telegram_guide():
    """Mostra guia para configurar o Telegram"""
    print("🤖 GUIA DE CONFIGURAÇÃO DO TELEGRAM - MARABET AI")
    print("=" * 60)
    
    print("\n📋 PASSO A PASSO DETALHADO:")
    print("=" * 40)
    
    print("\n1️⃣ CRIAR BOT DO TELEGRAM:")
    print("   • Abra o Telegram no seu celular ou computador")
    print("   • Procure por @BotFather na barra de pesquisa")
    print("   • Digite /newbot")
    print("   • Escolha um nome: 'MaraBet AI Predictions'")
    print("   • Escolha username: 'marabet_ai_bot' (deve terminar com 'bot')")
    print("   • Copie o TOKEN que aparece (ex: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)")
    
    print("\n2️⃣ OBTER CHAT ID:")
    print("   • Envie uma mensagem para o bot que você criou")
    print("   • Acesse esta URL no navegador (substitua SEU_TOKEN):")
    print("     https://api.telegram.org/botSEU_TOKEN/getUpdates")
    print("   • Procure por 'chat':{'id': NUMERO}")
    print("   • Copie o número que aparece após 'id': (ex: 123456789)")
    
    print("\n3️⃣ CONFIGURAR NO SISTEMA:")
    print("   • Abra o arquivo .env")
    print("   • Substitua 'SEU_TOKEN_AQUI' pelo token do bot")
    print("   • Substitua 'SEU_CHAT_ID_AQUI' pelo chat ID")
    print("   • Salve o arquivo")
    
    print("\n4️⃣ TESTAR CONFIGURAÇÃO:")
    print("   • Execute: python test_telegram_config.py")
    print("   • Se funcionar, execute: python run_telegram_auto.py")
    
    print("\n" + "=" * 60)
    
    print("\n💡 EXEMPLO DE CONFIGURAÇÃO:")
    print("=" * 30)
    print("TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
    print("TELEGRAM_CHAT_ID=123456789")
    
    print("\n🎯 APÓS CONFIGURAR:")
    print("=" * 20)
    print("• Execute: python run_telegram_auto.py")
    print("• Receba predições automaticamente no Telegram!")
    print("• Sistema funcionará 24/7 enviando predições")

def create_test_script():
    """Cria script de teste da configuração"""
    test_script = """#!/usr/bin/env python3
\"\"\"
Teste da Configuração do Telegram
MaraBet AI - Testa se o Telegram está configurado corretamente
\"\"\"

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

def test_telegram_config():
    \"\"\"Testa configuração do Telegram\"\"\"
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
    print("\\n🧪 Testando token...")
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
    print("\\n🧪 Testando envio de mensagem...")
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': f"🎉 <b>MaraBet AI - Teste de Configuração</b>\\n\\n"
                   f"✅ Configuração funcionando perfeitamente!\\n"
                   f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\\n"
                   f"🌍 Sistema de predições internacionais ativo\\n\\n"
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
        print("\\n🎉 CONFIGURAÇÃO FUNCIONANDO PERFEITAMENTE!")
        print("🚀 Execute: python run_telegram_auto.py")
    else:
        print("\\n💡 Siga o guia de configuração")
"""
    
    try:
        with open('test_telegram_config.py', 'w', encoding='utf-8') as f:
            f.write(test_script)
        print("✅ Script de teste criado: test_telegram_config.py")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar script de teste: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 CONFIGURAÇÃO AUTOMÁTICA DO TELEGRAM - MARABET AI")
    print("=" * 60)
    
    # Criar arquivo .env
    print("📝 Criando arquivo .env...")
    if not create_env_file():
        return False
    
    # Criar script de teste
    print("📝 Criando script de teste...")
    if not create_test_script():
        return False
    
    # Mostrar guia
    show_telegram_guide()
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("=" * 20)
    print("1. Configure o Telegram seguindo o guia acima")
    print("2. Execute: python test_telegram_config.py")
    print("3. Se funcionar, execute: python run_telegram_auto.py")
    
    return True

if __name__ == "__main__":
    main()
