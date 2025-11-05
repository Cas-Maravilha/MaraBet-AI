import asyncio
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import json
from dataclasses import dataclass
from enum import Enum

from settings.settings import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, 
    SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD,
    NOTIFICATION_EMAIL, ADMIN_EMAIL
)

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Tipos de notificação"""
    PREDICTION = "prediction"
    SYSTEM_STATUS = "system_status"
    ERROR = "error"
    PERFORMANCE = "performance"
    DAILY_REPORT = "daily_report"

@dataclass
class Notification:
    """Estrutura de uma notificação"""
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict] = None
    priority: str = "normal"  # low, normal, high, urgent
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class NotificationManager:
    """Gerenciador de notificações"""
    
    def __init__(self):
        self.telegram_enabled = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
        self.email_enabled = bool(SMTP_SERVER and SMTP_USERNAME and SMTP_PASSWORD)
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        
        logger.info(f"📱 Telegram: {'✅ Ativado' if self.telegram_enabled else '❌ Desativado'}")
        logger.info(f"📧 Email: {'✅ Ativado' if self.email_enabled else '❌ Desativado'}")
    
    async def send_notification(self, notification: Notification, 
                              channels: List[str] = None) -> Dict[str, bool]:
        """
        Envia notificação pelos canais especificados
        
        Args:
            notification: Objeto de notificação
            channels: Lista de canais ['telegram', 'email']
        
        Returns:
            Dict com status de cada canal
        """
        if channels is None:
            channels = []
            if self.telegram_enabled:
                channels.append('telegram')
            if self.email_enabled:
                channels.append('email')
        
        results = {}
        
        # Enviar por Telegram
        if 'telegram' in channels and self.telegram_enabled:
            try:
                results['telegram'] = await self._send_telegram(notification)
            except Exception as e:
                logger.error(f"Erro ao enviar Telegram: {e}")
                results['telegram'] = False
        
        # Enviar por Email
        if 'email' in channels and self.email_enabled:
            try:
                results['email'] = await self._send_email(notification)
            except Exception as e:
                logger.error(f"Erro ao enviar Email: {e}")
                results['email'] = False
        
        return results
    
    async def _send_telegram(self, notification: Notification) -> bool:
        """Envia notificação via Telegram"""
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            
            # Formatar mensagem
            message = self._format_telegram_message(notification)
            
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Telegram enviado: {notification.title}")
                return True
            else:
                logger.error(f"❌ Erro Telegram: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar Telegram: {e}")
            return False
    
    async def _send_email(self, notification: Notification) -> bool:
        """Envia notificação via Email"""
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = SMTP_USERNAME
            msg['To'] = NOTIFICATION_EMAIL
            msg['Subject'] = f"[MaraBet AI] {notification.title}"
            
            # Formatar conteúdo
            text_content, html_content = self._format_email_content(notification)
            
            # Adicionar partes
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Enviar email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                if SMTP_USERNAME and SMTP_PASSWORD:
                    server.starttls()
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                
                server.send_message(msg)
            
            logger.info(f"✅ Email enviado: {notification.title}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar Email: {e}")
            return False
    
    def _format_telegram_message(self, notification: Notification) -> str:
        """Formata mensagem para Telegram"""
        emoji_map = {
            NotificationType.PREDICTION: "🔮",
            NotificationType.SYSTEM_STATUS: "🤖",
            NotificationType.ERROR: "❌",
            NotificationType.PERFORMANCE: "📊",
            NotificationType.DAILY_REPORT: "📈"
        }
        
        priority_map = {
            "low": "🟢",
            "normal": "🟡",
            "high": "🟠",
            "urgent": "🔴"
        }
        
        emoji = emoji_map.get(notification.type, "📢")
        priority_emoji = priority_map.get(notification.priority, "🟡")
        
        message = f"{emoji} <b>{notification.title}</b>\n"
        message += f"{priority_emoji} <i>{notification.type.value.upper()}</i>\n\n"
        message += f"{notification.message}\n\n"
        message += f"⏰ {notification.timestamp.strftime('%d/%m/%Y %H:%M:%S')}"
        
        # Adicionar dados específicos se disponíveis
        if notification.data:
            if notification.type == NotificationType.PREDICTION:
                message += self._format_prediction_data(notification.data)
            elif notification.type == NotificationType.SYSTEM_STATUS:
                message += self._format_system_data(notification.data)
            elif notification.type == NotificationType.PERFORMANCE:
                message += self._format_performance_data(notification.data)
        
        return message
    
    def _format_email_content(self, notification: Notification) -> tuple:
        """Formata conteúdo para Email (texto e HTML)"""
        # Conteúdo texto
        text_content = f"""
MaraBet AI - {notification.title}
{'=' * 50}

{notification.message}

Tipo: {notification.type.value}
Prioridade: {notification.priority}
Timestamp: {notification.timestamp.strftime('%d/%m/%Y %H:%M:%S')}
"""
        
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
        .footer {{ color: #666; font-size: 12px; margin-top: 20px; }}
        .prediction {{ background: white; padding: 15px; border-left: 4px solid #28a745; 
                      border-radius: 4px; margin: 10px 0; }}
        .system {{ background: white; padding: 15px; border-left: 4px solid #17a2b8; 
                  border-radius: 4px; margin: 10px 0; }}
        .error {{ background: white; padding: 15px; border-left: 4px solid #dc3545; 
                 border-radius: 4px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🔮 MaraBet AI</h2>
        <h3>{notification.title}</h3>
    </div>
    
    <div class="content">
        <p>{notification.message}</p>
        
        <div class="info">
            <p><strong>Tipo:</strong> {notification.type.value}</p>
            <p><strong>Prioridade:</strong> {notification.priority}</p>
            <p><strong>Timestamp:</strong> {notification.timestamp.strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        {self._format_email_data(notification.data, notification.type) if notification.data else ''}
    </div>
    
    <div class="footer">
        <p>MaraBet AI - Sistema de Apostas Esportivas Inteligentes</p>
        <p>Este é um email automático, não responda.</p>
    </div>
</body>
</html>
"""
        
        return text_content, html_content
    
    def _format_prediction_data(self, data: Dict) -> str:
        """Formata dados de predição para Telegram"""
        if not data:
            return ""
        
        message = "\n📊 <b>Detalhes da Predição:</b>\n"
        
        if 'market' in data:
            message += f"🎯 Mercado: {data['market']}\n"
        if 'selection' in data:
            message += f"🎲 Seleção: {data['selection']}\n"
        if 'expected_value' in data:
            ev = data['expected_value']
            emoji = "🟢" if ev > 0 else "🔴"
            message += f"{emoji} EV: {ev:.2%}\n"
        if 'confidence' in data:
            conf = data['confidence']
            message += f"🎯 Confiança: {conf:.1%}\n"
        if 'stake_percentage' in data:
            stake = data['stake_percentage']
            message += f"💰 Stake: {stake:.1%}\n"
        if 'match' in data and data['match']:
            match = data['match']
            message += f"⚽ {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}\n"
            message += f"🏆 {match.get('league', 'N/A')}\n"
        
        return message
    
    def _format_system_data(self, data: Dict) -> str:
        """Formata dados do sistema para Telegram"""
        if not data:
            return ""
        
        message = "\n🤖 <b>Status do Sistema:</b>\n"
        
        if 'running' in data:
            status = "🟢 Executando" if data['running'] else "🔴 Parado"
            message += f"Status: {status}\n"
        if 'total_matches' in data:
            message += f"⚽ Partidas: {data['total_matches']:,}\n"
        if 'total_predictions' in data:
            message += f"🔮 Predições: {data['total_predictions']:,}\n"
        if 'recommended_predictions' in data:
            message += f"⭐ Recomendadas: {data['recommended_predictions']:,}\n"
        if 'next_execution' in data:
            message += f"⏰ Próxima execução: {data['next_execution']}\n"
        
        return message
    
    def _format_performance_data(self, data: Dict) -> str:
        """Formata dados de performance para Telegram"""
        if not data:
            return ""
        
        message = "\n📊 <b>Métricas de Performance:</b>\n"
        
        if 'total_predictions' in data:
            message += f"🔮 Total: {data['total_predictions']:,}\n"
        if 'average_ev' in data:
            ev = data['average_ev']
            emoji = "🟢" if ev > 0 else "🔴"
            message += f"{emoji} EV Médio: {ev:.2%}\n"
        if 'average_confidence' in data:
            conf = data['average_confidence']
            message += f"🎯 Confiança Média: {conf:.1%}\n"
        if 'success_rate' in data:
            rate = data['success_rate']
            emoji = "🟢" if rate > 0.6 else "🟡" if rate > 0.4 else "🔴"
            message += f"{emoji} Taxa de Sucesso: {rate:.1%}\n"
        
        return message
    
    def _format_email_data(self, data: Dict, notification_type: NotificationType) -> str:
        """Formata dados para HTML do email"""
        if not data:
            return ""
        
        if notification_type == NotificationType.PREDICTION:
            return f"""
            <div class="prediction">
                <h4>📊 Detalhes da Predição</h4>
                <p><strong>Mercado:</strong> {data.get('market', 'N/A')}</p>
                <p><strong>Seleção:</strong> {data.get('selection', 'N/A')}</p>
                <p><strong>EV:</strong> {data.get('expected_value', 0):.2%}</p>
                <p><strong>Confiança:</strong> {data.get('confidence', 0):.1%}</p>
                <p><strong>Stake:</strong> {data.get('stake_percentage', 0):.1%}</p>
            </div>
            """
        elif notification_type == NotificationType.SYSTEM_STATUS:
            return f"""
            <div class="system">
                <h4>🤖 Status do Sistema</h4>
                <p><strong>Status:</strong> {'🟢 Executando' if data.get('running') else '🔴 Parado'}</p>
                <p><strong>Partidas:</strong> {data.get('total_matches', 0):,}</p>
                <p><strong>Predições:</strong> {data.get('total_predictions', 0):,}</p>
                <p><strong>Recomendadas:</strong> {data.get('recommended_predictions', 0):,}</p>
            </div>
            """
        elif notification_type == NotificationType.PERFORMANCE:
            return f"""
            <div class="prediction">
                <h4>📊 Métricas de Performance</h4>
                <p><strong>Total de Predições:</strong> {data.get('total_predictions', 0):,}</p>
                <p><strong>EV Médio:</strong> {data.get('average_ev', 0):.2%}</p>
                <p><strong>Confiança Média:</strong> {data.get('average_confidence', 0):.1%}</p>
                <p><strong>Taxa de Sucesso:</strong> {data.get('success_rate', 0):.1%}</p>
            </div>
            """
        
        return ""

# Funções de conveniência
async def send_prediction_alert(prediction_data: Dict, channels: List[str] = None):
    """Envia alerta de predição"""
    notification = Notification(
        type=NotificationType.PREDICTION,
        title="🔮 Nova Predição Encontrada!",
        message=f"Valor detectado: {prediction_data.get('expected_value', 0):.2%} EV",
        data=prediction_data,
        priority="high"
    )
    
    manager = NotificationManager()
    return await manager.send_notification(notification, channels)

async def send_system_status(status_data: Dict, channels: List[str] = None):
    """Envia status do sistema"""
    notification = Notification(
        type=NotificationType.SYSTEM_STATUS,
        title="🤖 Status do Sistema",
        message="Atualização do status do MaraBet AI",
        data=status_data,
        priority="normal"
    )
    
    manager = NotificationManager()
    return await manager.send_notification(notification, channels)

async def send_error_alert(error_message: str, error_data: Dict = None, channels: List[str] = None):
    """Envia alerta de erro"""
    notification = Notification(
        type=NotificationType.ERROR,
        title="❌ Erro no Sistema",
        message=error_message,
        data=error_data,
        priority="urgent"
    )
    
    manager = NotificationManager()
    return await manager.send_notification(notification, channels)

async def send_performance_report(performance_data: Dict, channels: List[str] = None):
    """Envia relatório de performance"""
    notification = Notification(
        type=NotificationType.PERFORMANCE,
        title="📊 Relatório de Performance",
        message="Métricas de performance do MaraBet AI",
        data=performance_data,
        priority="normal"
    )
    
    manager = NotificationManager()
    return await manager.send_notification(notification, channels)

async def send_daily_report(report_data: Dict, channels: List[str] = None):
    """Envia relatório diário"""
    notification = Notification(
        type=NotificationType.DAILY_REPORT,
        title="📈 Relatório Diário",
        message="Resumo das atividades do dia",
        data=report_data,
        priority="low"
    )
    
    manager = NotificationManager()
    return await manager.send_notification(notification, channels)
