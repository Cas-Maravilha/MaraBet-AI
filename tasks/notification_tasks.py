"""
Tarefas de Notificação para MaraBet AI
Processamento assíncrono de notificações via Telegram e Email
"""

from celery import current_task
from tasks.celery_app import celery_app
from cache.redis_cache import cache
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import traceback
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks.notification_tasks.send_telegram_message')
def send_telegram_message(self, message: str, chat_id: Optional[str] = None, 
                         parse_mode: str = 'HTML', disable_notification: bool = False):
    """
    Envia mensagem via Telegram
    
    Args:
        message: Mensagem para enviar
        chat_id: ID do chat (opcional, usa padrão se não fornecido)
        parse_mode: Modo de parsing (HTML ou Markdown)
        disable_notification: Desabilitar notificação
    
    Returns:
        Dict com resultado do envio
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Enviando mensagem via Telegram', 'progress': 0}
        )
        
        import os
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN não configurado")
        
        if not chat_id:
            chat_id = os.getenv('TELEGRAM_CHAT_ID')
            if not chat_id:
                raise ValueError("TELEGRAM_CHAT_ID não configurado")
        
        # URL da API do Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Dados da mensagem
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': parse_mode,
            'disable_notification': disable_notification
        }
        
        # Envia mensagem
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('ok'):
            logger.info(f"Mensagem Telegram enviada com sucesso para chat {chat_id}")
            
            self.update_state(
                state='PROGRESS',
                meta={'status': 'Mensagem enviada com sucesso', 'progress': 100}
            )
            
            return {
                'status': 'success',
                'message_id': result['result']['message_id'],
                'chat_id': chat_id
            }
        else:
            raise Exception(f"Erro na API do Telegram: {result.get('description', 'Erro desconhecido')}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem Telegram: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro no envio', 'error': str(e)}
        )
        
        raise

@celery_app.task(bind=True, name='tasks.notification_tasks.send_email')
def send_email(self, subject: str, body: str, to_emails: List[str], 
               is_html: bool = True, attachments: Optional[List[Dict]] = None):
    """
    Envia email
    
    Args:
        subject: Assunto do email
        body: Corpo do email
        to_emails: Lista de emails destinatários
        is_html: Se o corpo é HTML
        attachments: Lista de anexos (opcional)
    
    Returns:
        Dict com resultado do envio
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Enviando email', 'progress': 0}
        )
        
        import os
        
        smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('FROM_EMAIL', smtp_username)
        
        if not smtp_username or not smtp_password:
            raise ValueError("Configurações SMTP não encontradas")
        
        # Cria mensagem
        msg = MimeMultipart()
        msg['From'] = from_email
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject
        
        # Adiciona corpo
        if is_html:
            msg.attach(MimeText(body, 'html'))
        else:
            msg.attach(MimeText(body, 'plain'))
        
        # Adiciona anexos se houver
        if attachments:
            for attachment in attachments:
                part = MimeText(attachment['content'])
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment["filename"]}'
                )
                msg.attach(part)
        
        # Conecta e envia
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        text = msg.as_string()
        server.sendmail(from_email, to_emails, text)
        server.quit()
        
        logger.info(f"Email enviado com sucesso para {len(to_emails)} destinatários")
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Email enviado com sucesso', 'progress': 100}
        )
        
        return {
            'status': 'success',
            'recipients': len(to_emails),
            'subject': subject
        }
        
    except Exception as e:
        logger.error(f"Erro ao enviar email: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro no envio', 'error': str(e)}
        )
        
        raise

@celery_app.task(bind=True, name='tasks.notification_tasks.send_value_bet_alert')
def send_value_bet_alert(self, value_bet: Dict):
    """
    Envia alerta de value bet encontrado
    
    Args:
        value_bet: Dados do value bet
    
    Returns:
        Dict com resultado do envio
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Enviando alerta de value bet', 'progress': 0}
        )
        
        # Prepara mensagem
        message = self._format_value_bet_message(value_bet)
        
        # Envia via Telegram
        telegram_result = send_telegram_message.delay(
            message=message,
            parse_mode='HTML'
        )
        
        # Envia via Email se configurado
        email_recipients = self._get_email_recipients()
        if email_recipients:
            email_subject = f"🚨 Value Bet Encontrado - {value_bet['home_team']} vs {value_bet['away_team']}"
            email_body = self._format_value_bet_email(value_bet)
            
            send_email.delay(
                subject=email_subject,
                body=email_body,
                to_emails=email_recipients,
                is_html=True
            )
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Alerta de value bet enviado', 'progress': 100}
        )
        
        logger.info(f"Alerta de value bet enviado para partida {value_bet['match_id']}")
        
        return {
            'status': 'success',
            'value_bet_id': value_bet['match_id'],
            'telegram_sent': True,
            'email_sent': bool(email_recipients)
        }
        
    except Exception as e:
        logger.error(f"Erro ao enviar alerta de value bet: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro no envio', 'error': str(e)}
        )
        
        raise

def _format_value_bet_message(self, value_bet: Dict) -> str:
    """
    Formata mensagem de value bet para Telegram
    
    Args:
        value_bet: Dados do value bet
    
    Returns:
        Mensagem formatada
    """
    message = f"""
🚨 <b>VALUE BET ENCONTRADO!</b>

⚽ <b>Partida:</b> {value_bet['home_team']} vs {value_bet['away_team']}
🏆 <b>Liga:</b> {value_bet['league_name']}
📅 <b>Data:</b> {value_bet['match_date']}

💰 <b>Detalhes da Aposta:</b>
• <b>Tipo:</b> {value_bet['bet_type']}
• <b>Odds:</b> {value_bet['odds']}
• <b>Probabilidade Modelo:</b> {value_bet['model_prob']:.1%}
• <b>Probabilidade Implícita:</b> {value_bet['implied_prob']:.1%}
• <b>Value:</b> {value_bet['value']:.1%}

📊 <b>Confiança:</b> {value_bet.get('confidence', 'N/A')}

⏰ <b>Encontrado em:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
    
    return message

def _format_value_bet_email(self, value_bet: Dict) -> str:
    """
    Formata email de value bet
    
    Args:
        value_bet: Dados do value bet
    
    Returns:
        HTML do email
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .bet-details {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .value {{ color: #28a745; font-weight: bold; }}
            .warning {{ color: #dc3545; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚨 Value Bet Encontrado!</h1>
        </div>
        <div class="content">
            <h2>⚽ {value_bet['home_team']} vs {value_bet['away_team']}</h2>
            <p><strong>Liga:</strong> {value_bet['league_name']}</p>
            <p><strong>Data:</strong> {value_bet['match_date']}</p>
            
            <div class="bet-details">
                <h3>💰 Detalhes da Aposta</h3>
                <p><strong>Tipo:</strong> {value_bet['bet_type']}</p>
                <p><strong>Odds:</strong> {value_bet['odds']}</p>
                <p><strong>Probabilidade Modelo:</strong> {value_bet['model_prob']:.1%}</p>
                <p><strong>Probabilidade Implícita:</strong> {value_bet['implied_prob']:.1%}</p>
                <p class="value"><strong>Value:</strong> {value_bet['value']:.1%}</p>
            </div>
            
            <p><strong>Confiança:</strong> {value_bet.get('confidence', 'N/A')}</p>
            <p><strong>Encontrado em:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            
            <p class="warning">⚠️ Lembre-se: Apostas envolvem risco. Aposte com responsabilidade!</p>
        </div>
    </body>
    </html>
    """
    
    return html

def _get_email_recipients(self) -> List[str]:
    """
    Obtém lista de destinatários de email
    
    Returns:
        Lista de emails
    """
    import os
    
    recipients_str = os.getenv('NOTIFICATION_EMAIL_RECIPIENTS', '')
    if recipients_str:
        return [email.strip() for email in recipients_str.split(',')]
    
    return []

@celery_app.task(bind=True, name='tasks.notification_tasks.send_weekly_report')
def send_weekly_report(self):
    """
    Envia relatório semanal de performance
    
    Returns:
        Dict com resultado do envio
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Gerando relatório semanal', 'progress': 0}
        )
        
        logger.info("Gerando relatório semanal")
        
        from armazenamento.banco_de_dados import DatabaseManager
        
        db = DatabaseManager()
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Coletando dados de performance', 'progress': 30}
        )
        
        # Coleta dados da semana
        week_start = datetime.now() - timedelta(days=7)
        
        # Estatísticas gerais
        stats = self._collect_weekly_stats(db, week_start)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Formatando relatório', 'progress': 70}
        )
        
        # Formata relatório
        report = self._format_weekly_report(stats)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Enviando relatório', 'progress': 90}
        )
        
        # Envia via Telegram
        send_telegram_message.delay(
            message=report['telegram_message'],
            parse_mode='HTML'
        )
        
        # Envia via Email
        email_recipients = self._get_email_recipients()
        if email_recipients:
            send_email.delay(
                subject=report['email_subject'],
                body=report['email_body'],
                to_emails=email_recipients,
                is_html=True
            )
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Relatório semanal enviado', 'progress': 100}
        )
        
        logger.info("Relatório semanal enviado com sucesso")
        
        return {
            'status': 'success',
            'report_period': f"{week_start.strftime('%d/%m/%Y')} - {datetime.now().strftime('%d/%m/%Y')}",
            'telegram_sent': True,
            'email_sent': bool(email_recipients)
        }
        
    except Exception as e:
        logger.error(f"Erro ao enviar relatório semanal: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro no envio', 'error': str(e)}
        )
        
        raise

def _collect_weekly_stats(self, db: DatabaseManager, week_start: datetime) -> Dict:
    """
    Coleta estatísticas da semana
    
    Args:
        db: Instância do banco de dados
        week_start: Início da semana
    
    Returns:
        Dict com estatísticas
    """
    stats = {}
    
    # Total de partidas analisadas
    matches_query = """
        SELECT COUNT(*) as total_matches
        FROM matches 
        WHERE match_date >= ? AND status = 'finished'
    """
    matches_result = db.execute_query(matches_query, (week_start,))
    stats['total_matches'] = matches_result[0]['total_matches'] if matches_result else 0
    
    # Total de value bets encontrados
    value_bets_query = """
        SELECT COUNT(*) as total_value_bets
        FROM value_bets 
        WHERE created_at >= ?
    """
    value_bets_result = db.execute_query(value_bets_query, (week_start,))
    stats['total_value_bets'] = value_bets_result[0]['total_value_bets'] if value_bets_result else 0
    
    # Performance dos modelos
    models_query = """
        SELECT model_type, AVG(CAST(JSON_EXTRACT(metrics, '$.accuracy') AS REAL)) as avg_accuracy
        FROM ml_models 
        WHERE created_at >= ?
        GROUP BY model_type
    """
    models_result = db.execute_query(models_query, (week_start,))
    stats['model_performance'] = {row['model_type']: row['avg_accuracy'] for row in models_result}
    
    # Backtesting results
    backtesting_query = """
        SELECT strategy_name, AVG(roi) as avg_roi, AVG(win_rate) as avg_win_rate
        FROM backtesting_results 
        WHERE created_at >= ?
        GROUP BY strategy_name
    """
    backtesting_result = db.execute_query(backtesting_query, (week_start,))
    stats['backtesting_performance'] = {
        row['strategy_name']: {
            'avg_roi': row['avg_roi'],
            'avg_win_rate': row['avg_win_rate']
        } for row in backtesting_result
    }
    
    return stats

def _format_weekly_report(self, stats: Dict) -> Dict:
    """
    Formata relatório semanal
    
    Args:
        stats: Estatísticas da semana
    
    Returns:
        Dict com relatório formatado
    """
    # Mensagem para Telegram
    telegram_message = f"""
📊 <b>RELATÓRIO SEMANAL - MaraBet AI</b>

📅 <b>Período:</b> {datetime.now().strftime('%d/%m/%Y')}

⚽ <b>Partidas Analisadas:</b> {stats['total_matches']}
💰 <b>Value Bets Encontrados:</b> {stats['total_value_bets']}

🤖 <b>Performance dos Modelos:</b>
"""
    
    for model, accuracy in stats['model_performance'].items():
        telegram_message += f"• {model}: {accuracy:.1%}\n"
    
    telegram_message += "\n📈 <b>Performance das Estratégias:</b>\n"
    
    for strategy, performance in stats['backtesting_performance'].items():
        telegram_message += f"• {strategy}: ROI {performance['avg_roi']:.1%}, Win Rate {performance['avg_win_rate']:.1%}\n"
    
    telegram_message += f"\n⏰ <b>Relatório gerado em:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    
    # Email HTML
    email_subject = f"📊 Relatório Semanal MaraBet AI - {datetime.now().strftime('%d/%m/%Y')}"
    
    email_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .stats {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: white; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Relatório Semanal - MaraBet AI</h1>
            <p>Período: {datetime.now().strftime('%d/%m/%Y')}</p>
        </div>
        <div class="content">
            <div class="stats">
                <h2>📈 Resumo da Semana</h2>
                <div class="metric">
                    <h3>⚽ Partidas Analisadas</h3>
                    <p>{stats['total_matches']}</p>
                </div>
                <div class="metric">
                    <h3>💰 Value Bets</h3>
                    <p>{stats['total_value_bets']}</p>
                </div>
            </div>
            
            <div class="stats">
                <h2>🤖 Performance dos Modelos</h2>
    """
    
    for model, accuracy in stats['model_performance'].items():
        email_body += f"<p><strong>{model}:</strong> {accuracy:.1%}</p>"
    
    email_body += """
            </div>
            
            <div class="stats">
                <h2>📈 Performance das Estratégias</h2>
    """
    
    for strategy, performance in stats['backtesting_performance'].items():
        email_body += f"<p><strong>{strategy}:</strong> ROI {performance['avg_roi']:.1%}, Win Rate {performance['avg_win_rate']:.1%}</p>"
    
    email_body += f"""
            </div>
            
            <p><em>Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</em></p>
        </div>
    </body>
    </html>
    """
    
    return {
        'telegram_message': telegram_message,
        'email_subject': email_subject,
        'email_body': email_body
    }

@celery_app.task(bind=True, name='tasks.notification_tasks.send_error_alert')
def send_error_alert(self, error_type: str, error_message: str, 
                    context: Optional[Dict] = None):
    """
    Envia alerta de erro crítico
    
    Args:
        error_type: Tipo do erro
        error_message: Mensagem do erro
        context: Contexto adicional (opcional)
    
    Returns:
        Dict com resultado do envio
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Enviando alerta de erro', 'progress': 0}
        )
        
        # Prepara mensagem de erro
        message = f"""
🚨 <b>ALERTA DE ERRO - MaraBet AI</b>

❌ <b>Tipo:</b> {error_type}
📝 <b>Mensagem:</b> {error_message}
⏰ <b>Horário:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        if context:
            message += f"\n📊 <b>Contexto:</b>\n"
            for key, value in context.items():
                message += f"• {key}: {value}\n"
        
        # Envia via Telegram
        send_telegram_message.delay(
            message=message,
            parse_mode='HTML'
        )
        
        # Envia via Email
        email_recipients = self._get_email_recipients()
        if email_recipients:
            send_email.delay(
                subject=f"🚨 Alerta de Erro - {error_type}",
                body=message.replace('<b>', '<strong>').replace('</b>', '</strong>'),
                to_emails=email_recipients,
                is_html=True
            )
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Alerta de erro enviado', 'progress': 100}
        )
        
        logger.info(f"Alerta de erro enviado: {error_type}")
        
        return {
            'status': 'success',
            'error_type': error_type,
            'telegram_sent': True,
            'email_sent': bool(email_recipients)
        }
        
    except Exception as e:
        logger.error(f"Erro ao enviar alerta de erro: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro no envio', 'error': str(e)}
        )
        
        raise
