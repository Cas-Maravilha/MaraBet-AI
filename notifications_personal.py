#!/usr/bin/env python3
"""
Sistema de notificações personalizado com suas credenciais
"""

import asyncio
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

# Suas credenciais
TELEGRAM_BOT_TOKEN = "8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg"
TELEGRAM_CHAT_ID = "5550091597"
YAHOO_EMAIL = "kilamu_10@yahoo.com.br"

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalNotificationManager:
    """Gerenciador de notificações personalizado"""
    
    def __init__(self):
        self.telegram_token = TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = TELEGRAM_CHAT_ID
        self.email = YAHOO_EMAIL
        self.smtp_server = "smtp.mail.yahoo.com"
        self.smtp_port = 587
        
    async def send_telegram_message(self, message, parse_mode="HTML"):
        """Envia mensagem para o Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info("✅ Mensagem Telegram enviada")
                        return True
                    else:
                        logger.error(f"❌ Erro Telegram: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Erro Telegram: {e}")
            return False
    
    def send_email(self, subject, html_content, text_content):
        """Envia email"""
        try:
            # Verificar se senha está configurada
            password = "your_yahoo_app_password_here"  # Substitua pela senha de app
            if password == "your_yahoo_app_password_here":
                logger.warning("⚠️ Senha de app do Yahoo não configurada")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = self.email
            msg['Subject'] = subject
            
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, password)
                server.send_message(msg)
            
            logger.info("✅ Email enviado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro Email: {e}")
            return False
    
    async def notify_prediction(self, prediction_data):
        """Notifica predição"""
        message = f"""🔮 <b>Nova Predição Encontrada!</b>
🟠 <b>PREDICTION</b>

Valor detectado: <b>{prediction_data.get('expected_value', 0)*100:.2f}% EV</b>

📊 <b>Detalhes da Predição:</b>
🎯 Mercado: {prediction_data.get('market', 'N/A')}
🎲 Seleção: {prediction_data.get('selection', 'N/A')}
🟢 EV: {prediction_data.get('expected_value', 0)*100:.2f}%
🎯 Confiança: {prediction_data.get('confidence', 0)*100:.1f}%
💰 Stake: {prediction_data.get('stake_percentage', 0)*100:.1f}%
⚽ {prediction_data.get('match', {}).get('home_team', 'N/A')} vs {prediction_data.get('match', {}).get('away_team', 'N/A')}
🏆 {prediction_data.get('match', {}).get('league', 'N/A')}

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""
        
        return await self.send_telegram_message(message)
    
    async def notify_system_status(self, status_data):
        """Notifica status do sistema"""
        status_emoji = "🟢" if status_data.get('running', False) else "🔴"
        
        message = f"""🤖 <b>Status do Sistema</b>
{status_emoji} <b>SYSTEM_STATUS</b>

O sistema está {'executando normalmente' if status_data.get('running', False) else 'parado'}.

🤖 <b>Status do Sistema:</b>
Status: {status_emoji} {'Executando' if status_data.get('running', False) else 'Parado'}
⚽ Partidas: {status_data.get('total_matches', 0)}
🔮 Predições: {status_data.get('total_predictions', 0)}
⭐ Recomendadas: {status_data.get('recommended_predictions', 0)}
⏰ Próxima execução: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""
        
        return await self.send_telegram_message(message)
    
    async def notify_error(self, error_message):
        """Notifica erro"""
        message = f"""❌ <b>Alerta de Erro</b>
🔴 <b>ERROR</b>

{error_message}

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""
        
        return await self.send_telegram_message(message)

async def test_personal_notifications():
    """Testa notificações personalizadas"""
    print("🧪 MARABET AI - TESTE DE NOTIFICAÇÕES PESSOAIS")
    print("=" * 60)
    
    manager = PersonalNotificationManager()
    
    # Dados de teste
    test_prediction = {
        'market': 'h2h',
        'selection': 'Home',
        'expected_value': 0.08,
        'confidence': 0.75,
        'stake_percentage': 0.03,
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
    result1 = await manager.notify_prediction(test_prediction)
    print(f"   Resultado: {'✅ Enviada' if result1 else '❌ Falhou'}")
    
    print("🤖 Testando notificação de status...")
    result2 = await manager.notify_system_status(test_status)
    print(f"   Resultado: {'✅ Enviada' if result2 else '❌ Falhou'}")
    
    print("❌ Testando notificação de erro...")
    result3 = await manager.notify_error("Teste de erro do sistema")
    print(f"   Resultado: {'✅ Enviada' if result3 else '❌ Falhou'}")
    
    success_count = sum([result1, result2, result3])
    print(f"\n📊 Resultado: {success_count}/3 notificações enviadas")
    
    if success_count == 3:
        print("🎉 Todas as notificações funcionando!")
    else:
        print("⚠️ Algumas notificações falharam")
    
    return success_count == 3

if __name__ == "__main__":
    asyncio.run(test_personal_notifications())
