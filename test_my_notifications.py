#!/usr/bin/env python3
"""
Script para testar notificações com suas credenciais específicas
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Adiciona o diretório pai ao sys.path para permitir importações relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Suas credenciais
TELEGRAM_BOT_TOKEN = "8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg"
YAHOO_EMAIL = "kilamu_10@yahoo.com.br"

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_telegram_notification():
    """Testa notificação do Telegram"""
    print("📱 TESTANDO TELEGRAM")
    print("=" * 30)
    
    try:
        import requests
        
        # Verificar se o Chat ID está configurado
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not chat_id or chat_id == 'your_telegram_chat_id_here':
            print("❌ Chat ID não configurado!")
            print("💡 Execute: python get_telegram_chat_id.py")
            return False
        
        # Enviar mensagem de teste
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': '''🎉 <b>Teste de Notificação - MaraBet AI</b>

✅ <b>Telegram configurado com sucesso!</b>

📊 <b>Informações do Sistema:</b>
🤖 Bot: @MaraBetAIBot
📧 Email: kilamu_10@yahoo.com.br
🆔 Chat ID: {chat_id}
⏰ Teste: {timestamp}

🎯 <b>Você receberá notificações sobre:</b>
• 🔮 Predições com valor
• 🤖 Status do sistema
• ❌ Alertas de erro
• 📊 Relatórios de performance
• 📈 Relatórios diários

🚀 <b>Sistema pronto para uso!</b>'''.format(
                chat_id=chat_id,
                timestamp=datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            ),
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Mensagem enviada com sucesso!")
            print("📱 Verifique seu Telegram")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

async def test_email_notification():
    """Testa notificação por email"""
    print("\n📧 TESTANDO EMAIL")
    print("=" * 30)
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Verificar se a senha está configurada
        password = os.getenv('SMTP_PASSWORD')
        if not password or password == 'your_yahoo_app_password_here':
            print("❌ Senha de app do Yahoo não configurada!")
            print("💡 Configure no arquivo .env")
            return False
        
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['From'] = YAHOO_EMAIL
        msg['To'] = YAHOO_EMAIL
        msg['Subject'] = "🎉 Teste de Notificação - MaraBet AI"
        
        # Conteúdo HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; border-radius: 8px; }}
                .content {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 10px 0; }}
                .success {{ color: #28a745; font-weight: bold; }}
                .info {{ background: white; padding: 15px; border-left: 4px solid #17a2b8; 
                        border-radius: 4px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🔮 MaraBet AI</h2>
                <h3>Teste de Notificação de Email</h3>
            </div>
            
            <div class="content">
                <p class="success">✅ Email configurado com sucesso!</p>
                <p>Se você recebeu esta mensagem, o sistema de notificações por email está funcionando corretamente.</p>
                
                <div class="info">
                    <h4>📊 Informações do Sistema:</h4>
                    <ul>
                        <li><strong>Email:</strong> {YAHOO_EMAIL}</li>
                        <li><strong>Servidor:</strong> smtp.mail.yahoo.com</li>
                        <li><strong>Porta:</strong> 587</li>
                        <li><strong>Status:</strong> Configurado e funcionando</li>
                        <li><strong>Teste:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</li>
                    </ul>
                </div>
                
                <h4>🎯 Você receberá notificações sobre:</h4>
                <ul>
                    <li>🔮 Predições com valor</li>
                    <li>🤖 Status do sistema</li>
                    <li>❌ Alertas de erro</li>
                    <li>📊 Relatórios de performance</li>
                    <li>📈 Relatórios diários</li>
                </ul>
                
                <p><strong>🚀 Sistema pronto para uso!</strong></p>
            </div>
            
            <div style="color: #666; font-size: 12px; margin-top: 20px;">
                <p>MaraBet AI - Sistema de Apostas Esportivas Inteligentes</p>
                <p>Este é um email automático, não responda.</p>
            </div>
        </body>
        </html>
        """
        
        # Conteúdo texto
        text_content = f"""
        MaraBet AI - Teste de Notificação de Email
        ==========================================
        
        ✅ Email configurado com sucesso!
        
        Se você recebeu esta mensagem, o sistema de notificações por email está funcionando corretamente.
        
        Informações do Sistema:
        - Email: {YAHOO_EMAIL}
        - Servidor: smtp.mail.yahoo.com
        - Porta: 587
        - Status: Configurado e funcionando
        - Teste: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        
        Você receberá notificações sobre:
        - Predições com valor
        - Status do sistema
        - Alertas de erro
        - Relatórios de performance
        - Relatórios diários
        
        Sistema pronto para uso!
        
        MaraBet AI - Sistema de Apostas Esportivas Inteligentes
        Este é um email automático, não responda.
        """
        
        # Adicionar conteúdo
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Enviar email
        print("📤 Enviando email de teste...")
        with smtplib.SMTP('smtp.mail.yahoo.com', 587) as server:
            server.starttls()
            server.login(YAHOO_EMAIL, password)
            server.send_message(msg)
        
        print("✅ Email enviado com sucesso!")
        print("📧 Verifique sua caixa de entrada (e spam)")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Erro de autenticação!")
        print("💡 Verifique se a senha de app está correta")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

async def test_system_notifications():
    """Testa notificações do sistema"""
    print("\n🔔 TESTANDO SISTEMA DE NOTIFICAÇÕES")
    print("=" * 30)
    
    try:
        from notifications.notification_integrator import (
            notify_prediction, notify_system_status, notify_error
        )
        
        # Dados de teste
        test_prediction = {
            'fixture_id': 12345,
            'market': 'h2h',
            'selection': 'Home',
            'expected_value': 0.08,
            'confidence': 0.75,
            'stake_percentage': 0.03,
            'recommended': True,
            'match': {
                'home_team': 'Manchester City',
                'away_team': 'Arsenal',
                'league': 'Premier League'
            }
        }
        
        test_status = {
            'running': True,
            'total_matches': 150,
            'total_predictions': 25,
            'recommended_predictions': 8
        }
        
        # Testar notificações
        print("🔮 Testando notificação de predição...")
        result1 = await notify_prediction(test_prediction)
        print(f"   Resultado: {'✅ Enviada' if result1 else '❌ Falhou'}")
        
        print("🤖 Testando notificação de status...")
        result2 = await notify_system_status(test_status)
        print(f"   Resultado: {'✅ Enviada' if result2 else '❌ Falhou'}")
        
        print("❌ Testando notificação de erro...")
        result3 = await notify_error("Teste de erro do sistema")
        print(f"   Resultado: {'✅ Enviada' if result3 else '❌ Falhou'}")
        
        success_count = sum([result1, result2, result3])
        print(f"\n📊 Resultado: {success_count}/3 notificações enviadas")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def check_configuration():
    """Verifica configuração"""
    print("🔍 VERIFICANDO CONFIGURAÇÃO")
    print("=" * 30)
    
    # Verificar arquivo .env
    if not os.path.exists('.env'):
        print("❌ Arquivo .env não encontrado!")
        print("💡 Execute: python configure_notifications.py")
        return False
    
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verificar Telegram
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
    
    print(f"📱 Telegram Token: {'✅ Configurado' if telegram_token else '❌ Não configurado'}")
    print(f"📱 Telegram Chat ID: {'✅ Configurado' if telegram_chat and telegram_chat != 'your_telegram_chat_id_here' else '❌ Não configurado'}")
    
    # Verificar Email
    email_user = os.getenv('SMTP_USERNAME')
    email_pass = os.getenv('SMTP_PASSWORD')
    
    print(f"📧 Email Username: {'✅ Configurado' if email_user else '❌ Não configurado'}")
    print(f"📧 Email Password: {'✅ Configurado' if email_pass and email_pass != 'your_yahoo_app_password_here' else '❌ Não configurado'}")
    
    return bool(telegram_token and telegram_chat and email_user and email_pass)

async def main():
    """Função principal"""
    print("🧪 MARABET AI - TESTE DE NOTIFICAÇÕES PESSOAIS")
    print("=" * 60)
    
    # Verificar configuração
    if not check_configuration():
        print("\n❌ Configuração incompleta!")
        print("💡 Configure o Chat ID do Telegram e a senha de app do Yahoo")
        return
    
    # Testar notificações
    results = []
    
    # Teste individual do Telegram
    telegram_result = await test_telegram_notification()
    results.append(telegram_result)
    
    # Teste individual do Email
    email_result = await test_email_notification()
    results.append(email_result)
    
    # Teste do sistema completo
    system_result = await test_system_notifications()
    results.append(system_result)
    
    # Resultado final
    success_count = sum(results)
    total_tests = len(results)
    
    print(f"\n📊 RESULTADO FINAL")
    print("=" * 30)
    print(f"Testes aprovados: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 Todas as notificações funcionando!")
        print("\n🚀 Sistema pronto para uso:")
        print("• python run_automated_collector.py")
        print("• python run_dashboard.py")
    else:
        print("⚠️  Algumas notificações falharam")
        print("💡 Verifique as configurações no arquivo .env")

if __name__ == "__main__":
    asyncio.run(main())
