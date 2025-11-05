#!/usr/bin/env python3
"""
Sistema de Alertas Específicos de Negócio
MaraBet AI - Alertas para ROI, drift de modelo e anomalias
"""

import json
import smtplib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertChannel(Enum):
    """Canais de alerta"""
    EMAIL = "email"
    TELEGRAM = "telegram"
    SLACK = "slack"
    WEBHOOK = "webhook"
    LOG = "log"

class AlertSeverity(Enum):
    """Severidade dos alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AlertRule:
    """Regra de alerta"""
    name: str
    condition: str
    threshold: float
    severity: AlertSeverity
    channels: List[AlertChannel]
    cooldown_minutes: int = 60
    enabled: bool = True

@dataclass
class Alert:
    """Alerta"""
    rule_name: str
    severity: AlertSeverity
    message: str
    value: float
    threshold: float
    timestamp: datetime
    channels_sent: List[AlertChannel] = None

class BusinessAlertManager:
    """Gerenciador de alertas de negócio"""
    
    def __init__(self):
        self.alert_rules = self._load_default_rules()
        self.alert_history = []
        self.last_alert_times = {}
        
        # Configurar canais
        self._setup_channels()
        
        # Configurar logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging para alertas"""
        log_dir = "logs/business_alerts"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/alerts_{datetime.now().strftime('%Y%m%d')}.log"
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    def _load_default_rules(self) -> List[AlertRule]:
        """Carrega regras de alerta padrão"""
        return [
            # Alertas de ROI
            AlertRule(
                name="negative_roi_daily",
                condition="roi < -0.05",
                threshold=-0.05,
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.TELEGRAM],
                cooldown_minutes=60
            ),
            AlertRule(
                name="negative_roi_weekly",
                condition="roi < -0.15",
                threshold=-0.15,
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.TELEGRAM, AlertChannel.SLACK],
                cooldown_minutes=30
            ),
            
            # Alertas de Win Rate
            AlertRule(
                name="low_win_rate",
                condition="win_rate < 0.4",
                threshold=0.4,
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.EMAIL, AlertChannel.TELEGRAM],
                cooldown_minutes=120
            ),
            AlertRule(
                name="very_low_win_rate",
                condition="win_rate < 0.3",
                threshold=0.3,
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.TELEGRAM, AlertChannel.SLACK],
                cooldown_minutes=60
            ),
            
            # Alertas de PnL
            AlertRule(
                name="high_daily_loss",
                condition="daily_pnl < -1000",
                threshold=-1000,
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.TELEGRAM, AlertChannel.SLACK],
                cooldown_minutes=15
            ),
            AlertRule(
                name="high_weekly_loss",
                condition="weekly_pnl < -5000",
                threshold=-5000,
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.TELEGRAM, AlertChannel.SLACK],
                cooldown_minutes=30
            ),
            
            # Alertas de Modelo
            AlertRule(
                name="model_drift_detected",
                condition="drift_score > 0.2",
                threshold=0.2,
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.TELEGRAM],
                cooldown_minutes=180
            ),
            AlertRule(
                name="model_accuracy_drop",
                condition="accuracy < 0.6",
                threshold=0.6,
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.EMAIL, AlertChannel.TELEGRAM],
                cooldown_minutes=240
            ),
            
            # Alertas de Anomalia
            AlertRule(
                name="prediction_anomaly",
                condition="anomaly_score > 0.8",
                threshold=0.8,
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.TELEGRAM],
                cooldown_minutes=60
            ),
            AlertRule(
                name="data_quality_issue",
                condition="data_quality < 0.7",
                threshold=0.7,
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.EMAIL, AlertChannel.TELEGRAM],
                cooldown_minutes=120
            ),
            
            # Alertas de Sistema
            AlertRule(
                name="high_error_rate",
                condition="error_rate > 0.05",
                threshold=0.05,
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.TELEGRAM, AlertChannel.SLACK],
                cooldown_minutes=30
            ),
            AlertRule(
                name="low_throughput",
                condition="throughput < 100",
                threshold=100,
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.EMAIL, AlertChannel.TELEGRAM],
                cooldown_minutes=180
            )
        ]
    
    def _setup_channels(self):
        """Configura canais de alerta"""
        self.channel_configs = {
            AlertChannel.EMAIL: {
                'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'username': os.getenv('SMTP_USERNAME', ''),
                'password': os.getenv('SMTP_PASSWORD', ''),
                'from_email': os.getenv('FROM_EMAIL', ''),
                'to_emails': os.getenv('TO_EMAILS', '').split(',')
            },
            AlertChannel.TELEGRAM: {
                'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
                'chat_id': os.getenv('TELEGRAM_CHAT_ID', '')
            },
            AlertChannel.SLACK: {
                'webhook_url': os.getenv('SLACK_WEBHOOK_URL', '')
            },
            AlertChannel.WEBHOOK: {
                'url': os.getenv('WEBHOOK_URL', ''),
                'headers': json.loads(os.getenv('WEBHOOK_HEADERS', '{}'))
            }
        }
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Verifica alertas baseado nas métricas"""
        alerts = []
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # Verificar cooldown
            if self._is_in_cooldown(rule):
                continue
            
            # Verificar condição
            if self._evaluate_condition(rule, metrics):
                alert = Alert(
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=self._generate_alert_message(rule, metrics),
                    value=self._get_metric_value(rule.condition, metrics),
                    threshold=rule.threshold,
                    timestamp=datetime.now(),
                    channels_sent=[]
                )
                
                # Enviar alerta
                self._send_alert(alert, rule.channels)
                
                # Registrar alerta
                alerts.append(alert)
                self.alert_history.append(alert)
                self.last_alert_times[rule.name] = datetime.now()
        
        return alerts
    
    def _is_in_cooldown(self, rule: AlertRule) -> bool:
        """Verifica se a regra está em cooldown"""
        if rule.name not in self.last_alert_times:
            return False
        
        last_alert = self.last_alert_times[rule.name]
        cooldown_end = last_alert + timedelta(minutes=rule.cooldown_minutes)
        
        return datetime.now() < cooldown_end
    
    def _evaluate_condition(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Avalia condição da regra"""
        try:
            # Substituir variáveis na condição
            condition = rule.condition
            for key, value in metrics.items():
                condition = condition.replace(key, str(value))
            
            # Avaliar condição
            return eval(condition)
        except Exception as e:
            logger.error(f"Erro ao avaliar condição {rule.condition}: {e}")
            return False
    
    def _get_metric_value(self, condition: str, metrics: Dict[str, Any]) -> float:
        """Extrai valor da métrica da condição"""
        try:
            # Extrair nome da métrica da condição
            metric_name = condition.split()[0]
            return float(metrics.get(metric_name, 0))
        except:
            return 0.0
    
    def _generate_alert_message(self, rule: AlertRule, metrics: Dict[str, Any]) -> str:
        """Gera mensagem do alerta"""
        value = self._get_metric_value(rule.condition, metrics)
        
        message = f"🚨 ALERTA {rule.severity.value.upper()}: {rule.name}\n"
        message += f"📊 Valor atual: {value:.4f}\n"
        message += f"⚠️ Threshold: {rule.threshold:.4f}\n"
        message += f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # Adicionar contexto específico
        if "roi" in rule.name:
            message += f"💰 ROI: {value:.2%}\n"
        elif "win_rate" in rule.name:
            message += f"🎯 Win Rate: {value:.2%}\n"
        elif "pnl" in rule.name:
            message += f"💸 PnL: R$ {value:,.2f}\n"
        elif "drift" in rule.name:
            message += f"📈 Drift Score: {value:.4f}\n"
        elif "anomaly" in rule.name:
            message += f"🔍 Anomaly Score: {value:.4f}\n"
        
        return message
    
    def _send_alert(self, alert: Alert, channels: List[AlertChannel]):
        """Envia alerta pelos canais especificados"""
        for channel in channels:
            try:
                if channel == AlertChannel.EMAIL:
                    self._send_email(alert)
                elif channel == AlertChannel.TELEGRAM:
                    self._send_telegram(alert)
                elif channel == AlertChannel.SLACK:
                    self._send_slack(alert)
                elif channel == AlertChannel.WEBHOOK:
                    self._send_webhook(alert)
                elif channel == AlertChannel.LOG:
                    self._send_log(alert)
                
                alert.channels_sent.append(channel)
                logger.info(f"✅ Alerta enviado via {channel.value}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao enviar alerta via {channel.value}: {e}")
    
    def _send_email(self, alert: Alert):
        """Envia alerta por email"""
        config = self.channel_configs[AlertChannel.EMAIL]
        
        if not config['username'] or not config['password']:
            logger.warning("⚠️ Configuração de email não encontrada")
            return
        
        msg = MIMEMultipart()
        msg['From'] = config['from_email']
        msg['To'] = ', '.join(config['to_emails'])
        msg['Subject'] = f"MaraBet AI - {alert.severity.value.upper()} Alert"
        
        msg.attach(MIMEText(alert.message, 'plain'))
        
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
    
    def _send_telegram(self, alert: Alert):
        """Envia alerta por Telegram"""
        config = self.channel_configs[AlertChannel.TELEGRAM]
        
        if not config['bot_token'] or not config['chat_id']:
            logger.warning("⚠️ Configuração do Telegram não encontrada")
            return
        
        url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
        data = {
            'chat_id': config['chat_id'],
            'text': alert.message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
    
    def _send_slack(self, alert: Alert):
        """Envia alerta por Slack"""
        config = self.channel_configs[AlertChannel.SLACK]
        
        if not config['webhook_url']:
            logger.warning("⚠️ Configuração do Slack não encontrada")
            return
        
        # Determinar cor baseada na severidade
        color_map = {
            AlertSeverity.LOW: "good",
            AlertSeverity.MEDIUM: "warning",
            AlertSeverity.HIGH: "danger",
            AlertSeverity.CRITICAL: "danger"
        }
        
        payload = {
            "attachments": [{
                "color": color_map[alert.severity],
                "title": f"MaraBet AI Alert - {alert.rule_name}",
                "text": alert.message,
                "timestamp": int(alert.timestamp.timestamp())
            }]
        }
        
        response = requests.post(config['webhook_url'], json=payload, timeout=10)
        response.raise_for_status()
    
    def _send_webhook(self, alert: Alert):
        """Envia alerta por webhook"""
        config = self.channel_configs[AlertChannel.WEBHOOK]
        
        if not config['url']:
            logger.warning("⚠️ Configuração de webhook não encontrada")
            return
        
        payload = {
            "alert": {
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "message": alert.message,
                "value": alert.value,
                "threshold": alert.threshold,
                "timestamp": alert.timestamp.isoformat()
            }
        }
        
        headers = config['headers']
        response = requests.post(config['url'], json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    
    def _send_log(self, alert: Alert):
        """Registra alerta no log"""
        logger.warning(f"ALERT: {alert.rule_name} - {alert.message}")
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obtém resumo de alertas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [alert for alert in self.alert_history 
                        if alert.timestamp >= cutoff_time]
        
        summary = {
            'total_alerts': len(recent_alerts),
            'by_severity': {},
            'by_rule': {},
            'by_channel': {},
            'last_alert': None
        }
        
        # Contar por severidade
        for alert in recent_alerts:
            severity = alert.severity.value
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            rule = alert.rule_name
            summary['by_rule'][rule] = summary['by_rule'].get(rule, 0) + 1
            
            for channel in alert.channels_sent:
                channel_name = channel.value
                summary['by_channel'][channel_name] = summary['by_channel'].get(channel_name, 0) + 1
        
        if recent_alerts:
            summary['last_alert'] = max(recent_alerts, key=lambda x: x.timestamp).timestamp.isoformat()
        
        return summary
    
    def generate_alert_report(self) -> str:
        """Gera relatório de alertas"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE ALERTAS DE NEGÓCIO - MARABET AI")
        report.append("=" * 80)
        
        # Resumo das últimas 24h
        summary = self.get_alert_summary(24)
        
        report.append(f"\n📊 RESUMO DAS ÚLTIMAS 24H:")
        report.append(f"  Total de alertas: {summary['total_alerts']}")
        report.append(f"  Último alerta: {summary['last_alert'] or 'Nenhum'}")
        
        # Por severidade
        report.append(f"\n🚨 ALERTAS POR SEVERIDADE:")
        for severity, count in summary['by_severity'].items():
            report.append(f"  {severity.upper()}: {count}")
        
        # Por regra
        report.append(f"\n📋 ALERTAS POR REGRA:")
        for rule, count in summary['by_rule'].items():
            report.append(f"  {rule}: {count}")
        
        # Por canal
        report.append(f"\n📡 ALERTAS POR CANAL:")
        for channel, count in summary['by_channel'].items():
            report.append(f"  {channel}: {count}")
        
        # Regras ativas
        active_rules = [rule for rule in self.alert_rules if rule.enabled]
        report.append(f"\n⚙️ REGRAS ATIVAS: {len(active_rules)}")
        for rule in active_rules:
            report.append(f"  {rule.name}: {rule.condition} (threshold: {rule.threshold})")
        
        # Recomendações
        report.append(f"\n💡 RECOMENDAÇÕES:")
        if summary['total_alerts'] > 50:
            report.append(f"  ⚠️ Muitos alertas - revisar thresholds")
        
        critical_alerts = summary['by_severity'].get('critical', 0)
        if critical_alerts > 0:
            report.append(f"  🚨 {critical_alerts} alertas críticos - ação imediata necessária")
        
        if summary['total_alerts'] == 0:
            report.append(f"  ✅ Nenhum alerta nas últimas 24h - sistema estável")
        
        report.append("=" * 80)
        
        return "\n".join(report)

# Instância global
alert_manager = BusinessAlertManager()

if __name__ == "__main__":
    # Teste do sistema de alertas
    print("🧪 TESTANDO SISTEMA DE ALERTAS DE NEGÓCIO")
    print("=" * 60)
    
    # Métricas de teste
    test_metrics = {
        'roi': -0.08,  # ROI negativo
        'win_rate': 0.35,  # Win rate baixo
        'daily_pnl': -1200,  # Perda alta
        'drift_score': 0.25,  # Drift detectado
        'accuracy': 0.55,  # Accuracy baixa
        'anomaly_score': 0.85,  # Anomalia alta
        'data_quality': 0.65,  # Qualidade baixa
        'error_rate': 0.08,  # Taxa de erro alta
        'throughput': 80  # Throughput baixo
    }
    
    # Verificar alertas
    alerts = alert_manager.check_alerts(test_metrics)
    print(f"✅ Alertas gerados: {len(alerts)}")
    
    for alert in alerts:
        print(f"  {alert.rule_name}: {alert.message[:50]}...")
    
    # Gerar relatório
    report = alert_manager.generate_alert_report()
    print(f"\n{report}")
    
    print("\n🎉 TESTE DE ALERTAS CONCLUÍDO!")
