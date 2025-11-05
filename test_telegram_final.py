#!/usr/bin/env python3
"""
Script para testar notificações do Telegram com suas credenciais
"""

import requests
import json
from datetime import datetime

# Suas credenciais
TELEGRAM_BOT_TOKEN = "8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg"
TELEGRAM_CHAT_ID = "5550091597"

def test_telegram_connection():
    """Testa conexão com o Telegram"""
    print("🤖 MARABET AI - TESTE DO TELEGRAM")
    print("=" * 50)
    
    print(f"📱 Bot: @MaraBetAIBot")
    print(f"🔑 Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"🆔 Chat ID: {TELEGRAM_CHAT_ID}")
    
    try:
        # Testar conexão
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info['ok']:
                print("✅ Conexão com Telegram estabelecida!")
                print(f"🤖 Bot: {bot_info['result']['first_name']}")
                print(f"📱 Username: @{bot_info['result']['username']}")
                return True
            else:
                print("❌ Erro na resposta da API")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def send_test_message():
    """Envia mensagem de teste"""
    print("\n📤 ENVIANDO MENSAGEM DE TESTE")
    print("=" * 50)
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        message = f"""🎉 <b>MaraBet AI - Teste de Notificação</b>

✅ <b>Telegram configurado com sucesso!</b>

📊 <b>Informações do Sistema:</b>
🤖 Bot: @MaraBetAIBot
🆔 Chat ID: {TELEGRAM_CHAT_ID}
📧 Email: kilamu_10@yahoo.com.br
⏰ Teste: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

🎯 <b>Você receberá notificações sobre:</b>
• 🔮 Predições com valor (EV ≥ 5%)
• 🤖 Status do sistema
• ❌ Alertas de erro
• 📊 Relatórios de performance
• 📈 Relatórios diários

🚀 <b>Sistema pronto para uso!</b>

💡 <b>Próximos passos:</b>
1. Configure a senha de app do Yahoo
2. Execute: python test_my_notifications.py
3. Inicie o sistema: python run_automated_collector.py
4. Acesse o dashboard: python run_dashboard.py"""

        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Mensagem enviada com sucesso!")
            print("📱 Verifique seu Telegram para confirmar o recebimento")
            return True
        else:
            print(f"❌ Erro ao enviar mensagem: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def send_prediction_example():
    """Envia exemplo de notificação de predição"""
    print("\n🔮 ENVIANDO EXEMPLO DE PREDIÇÃO")
    print("=" * 50)
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        message = f"""🔮 <b>Nova Predição Encontrada!</b>
🟠 <b>PREDICTION</b>

Valor detectado: <b>8.00% EV</b>

📊 <b>Detalhes da Predição:</b>
🎯 Mercado: h2h
🎲 Seleção: Home
🟢 EV: 8.00%
🎯 Confiança: 75.0%
💰 Stake: 3.0%
⚽ Manchester City vs Arsenal
🏆 Premier League

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

💡 <i>Esta é uma notificação de exemplo</i>"""

        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Exemplo de predição enviado!")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def send_system_status_example():
    """Envia exemplo de status do sistema"""
    print("\n🤖 ENVIANDO EXEMPLO DE STATUS")
    print("=" * 50)
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        message = f"""🤖 <b>Status do Sistema</b>
🟢 <b>SYSTEM_STATUS</b>

O sistema está executando normalmente.

🤖 <b>Status do Sistema:</b>
Status: 🟢 Executando
⚽ Partidas: 150
🔮 Predições: 25
⭐ Recomendadas: 8
⏰ Próxima execução: 2025-10-14 19:00:00

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

💡 <i>Esta é uma notificação de exemplo</i>"""

        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Exemplo de status enviado!")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🔮 MARABET AI - TESTE FINAL DO TELEGRAM")
    print("=" * 60)
    
    # Testar conexão
    if not test_telegram_connection():
        print("\n❌ Falha na conexão com Telegram")
        return
    
    # Enviar mensagem de teste
    if not send_test_message():
        print("\n❌ Falha ao enviar mensagem de teste")
        return
    
    # Enviar exemplos
    send_prediction_example()
    send_system_status_example()
    
    print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 50)
    print("✅ Telegram configurado e funcionando")
    print("📱 Verifique seu Telegram para ver as mensagens")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Configure a senha de app do Yahoo")
    print("2. Execute: python test_my_notifications.py")
    print("3. Inicie o sistema: python run_automated_collector.py")
    print("4. Acesse o dashboard: python run_dashboard.py")

if __name__ == "__main__":
    main()
