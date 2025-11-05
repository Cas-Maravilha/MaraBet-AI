#!/usr/bin/env python3
"""
Sistema de Alertas para o MaraBet AI
Alertas configurados e testados para monitoramento
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Severidade do alerta"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Status do alerta"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class AlertRule:
    """Regra de alerta"""
    name: str
    description: str
    condition: Callable
    severity: AlertSeverity
    cooldown_minutes: int = 5
    enabled: bool = True
    channels: List[str] = None

@dataclass
class Alert:
    """Alerta ativo"""
    id: str
    rule_name: str
    message: str
    severity: AlertSeverity
    status: AlertStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None
    metadata: Dict = None

class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self):
        """Inicializa gerenciador de alertas"""
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.last_alert_time: Dict[str, datetime] = {}
        
        # Configurar regras padrão
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Configura regras de alerta padrão"""
        
        # Alerta de ROI baixo
        self.add_rule(AlertRule(
            name="low_roi",
            description="ROI abaixo de 5% nas últimas 24h",
            condition=self._check_low_roi,
            severity=AlertSeverity.MEDIUM,
            cooldown_minutes=30,
            channels=["telegram", "email"]
        ))
        
        # Alerta de taxa de acerto baixa
        self.add_rule(AlertRule(
            name="low_win_rate",
            description="Taxa de acerto abaixo de 40% nas últimas 24h",
            condition=self._check_low_win_rate,
            severity=AlertSeverity.HIGH,
            cooldown_minutes=60,
            channels=["telegram", "email", "sms"]
        ))
        
        # Alerta de perda consecutiva
        self.add_rule(AlertRule(
            name="consecutive_losses",
            description="5 apostas perdidas consecutivas",
            condition=self._check_consecutive_losses,
            severity=AlertSeverity.CRITICAL,
            cooldown_minutes=15,
            channels=["telegram", "email", "sms"]
        ))
        
        # Alerta de API indisponível
        self.add_rule(AlertRule(
            name="api_down",
            description="API Football indisponível",
            condition=self._check_api_availability,
            severity=AlertSeverity.HIGH,
            cooldown_minutes=10,
            channels=["telegram", "email"]
        ))
        
        # Alerta de alta volatilidade
        self.add_rule(AlertRule(
            name="high_volatility",
            description="Volatilidade de ROI acima de 50%",
            condition=self._check_high_volatility,
            severity=AlertSeverity.MEDIUM,
            cooldown_minutes=60,
            channels=["telegram"]
        ))
        
        # Alerta de volume anômalo
        self.add_rule(AlertRule(
            name="anomalous_volume",
            description="Volume de apostas 3x maior que a média",
            condition=self._check_anomalous_volume,
            severity=AlertSeverity.MEDIUM,
            cooldown_minutes=30,
            channels=["telegram", "email"]
        ))
    
    def add_rule(self, rule: AlertRule):
        """Adiciona regra de alerta"""
        self.rules.append(rule)
        logger.info(f"Regra de alerta adicionada: {rule.name}")
    
    def check_alerts(self):
        """Verifica todas as regras de alerta"""
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                # Verificar cooldown
                if self._is_in_cooldown(rule.name):
                    continue
                
                # Verificar condição
                if rule.condition():
                    self._trigger_alert(rule)
                    
            except Exception as e:
                logger.error(f"Erro ao verificar regra {rule.name}: {e}")
    
    def _is_in_cooldown(self, rule_name: str) -> bool:
        """Verifica se regra está em cooldown"""
        if rule_name not in self.last_alert_time:
            return False
        
        rule = next((r for r in self.rules if r.name == rule_name), None)
        if not rule:
            return False
        
        cooldown_end = self.last_alert_time[rule_name] + timedelta(minutes=rule.cooldown_minutes)
        return datetime.now() < cooldown_end
    
    def _trigger_alert(self, rule: AlertRule):
        """Dispara alerta"""
        alert_id = f"{rule.name}_{int(time.time())}"
        
        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            message=rule.description,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            created_at=datetime.now(),
            metadata={"rule": rule.name}
        )
        
        # Adicionar aos alertas ativos
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.last_alert_time[rule.name] = datetime.now()
        
        # Enviar notificações
        self._send_notifications(alert, rule.channels)
        
        logger.warning(f"Alerta disparado: {rule.name} - {rule.description}")
    
    def _send_notifications(self, alert: Alert, channels: List[str]):
        """Envia notificações do alerta"""
        for channel in channels:
            try:
                if channel == "telegram":
                    self._send_telegram_alert(alert)
                elif channel == "email":
                    self._send_email_alert(alert)
                elif channel == "sms":
                    self._send_sms_alert(alert)
            except Exception as e:
                logger.error(f"Erro ao enviar alerta via {channel}: {e}")
    
    def _send_telegram_alert(self, alert: Alert):
        """Envia alerta via Telegram"""
        from settings.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return
        
        emoji = {
            AlertSeverity.LOW: "ℹ️",
            AlertSeverity.MEDIUM: "⚠️",
            AlertSeverity.HIGH: "🚨",
            AlertSeverity.CRITICAL: "🔥"
        }
        
        message = f"""
{alert.severity.value.upper()} ALERT - MaraBet AI
{emoji.get(alert.severity, '⚠️')} {alert.message}

Regra: {alert.rule_name}
Severidade: {alert.severity.value}
Hora: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}

ID: {alert.id}
        """.strip()
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"Alerta Telegram enviado: {alert.id}")
        else:
            logger.error(f"Falha ao enviar alerta Telegram: {response.status_code}")
    
    def _send_email_alert(self, alert: Alert):
        """Envia alerta via email"""
        from notifications.notification_manager import NotificationManager
        
        notification_manager = NotificationManager()
        
        subject = f"[{alert.severity.value.upper()}] MaraBet AI Alert - {alert.rule_name}"
        message = f"""
Alerta do Sistema MaraBet AI

Regra: {alert.rule_name}
Descrição: {alert.message}
Severidade: {alert.severity.value}
Hora: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}

ID do Alerta: {alert.id}

Este é um alerta automático do sistema de monitoramento.
        """.strip()
        
        notification_manager.send_email_notification({
            "subject": subject,
            "message": message,
            "priority": alert.severity.value
        })
    
    def _send_sms_alert(self, alert: Alert):
        """Envia alerta via SMS (simulado)"""
        # Em produção, integrar com provedor SMS
        logger.info(f"SMS Alert: {alert.message}")
    
    def resolve_alert(self, alert_id: str):
        """Resolve alerta"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            
            del self.active_alerts[alert_id]
            logger.info(f"Alerta resolvido: {alert_id}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtém alertas ativos"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Obtém histórico de alertas"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.created_at >= cutoff]
    
    # Métodos de verificação de condições
    
    def _check_low_roi(self) -> bool:
        """Verifica ROI baixo"""
        from monitoring.business_metrics import business_metrics
        
        metrics = business_metrics.get_business_metrics(1)  # Últimas 24h
        return metrics.total_roi < 0.05  # ROI < 5%
    
    def _check_low_win_rate(self) -> bool:
        """Verifica taxa de acerto baixa"""
        from monitoring.business_metrics import business_metrics
        
        metrics = business_metrics.get_business_metrics(1)  # Últimas 24h
        return metrics.win_rate < 0.40  # Taxa < 40%
    
    def _check_consecutive_losses(self) -> bool:
        """Verifica perdas consecutivas"""
        from monitoring.business_metrics import business_metrics
        
        recent_bets = business_metrics.bet_results[-5:]  # Últimas 5 apostas
        if len(recent_bets) < 5:
            return False
        
        return all(bet.profit_loss < 0 for bet in recent_bets)
    
    def _check_api_availability(self) -> bool:
        """Verifica disponibilidade da API"""
        try:
            from settings.settings import API_FOOTBALL_KEY
            
            if not API_FOOTBALL_KEY:
                return True  # Não configurado, não alertar
            
            url = "https://v3.football.api-sports.io/status"
            headers = {"X-API-Key": API_FOOTBALL_KEY}
            
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code != 200
            
        except Exception:
            return True  # Erro = API indisponível
    
    def _check_high_volatility(self) -> bool:
        """Verifica alta volatilidade"""
        from monitoring.business_metrics import business_metrics
        
        trends = business_metrics.get_performance_trends(7)
        rois = [day['roi'] for day in trends['trends'] if day['roi'] != 0]
        
        if len(rois) < 3:
            return False
        
        # Calcular desvio padrão
        mean_roi = sum(rois) / len(rois)
        variance = sum((roi - mean_roi) ** 2 for roi in rois) / len(rois)
        std_dev = variance ** 0.5
        
        return std_dev > 0.5  # Volatilidade > 50%
    
    def _check_anomalous_volume(self) -> bool:
        """Verifica volume anômalo"""
        from monitoring.business_metrics import business_metrics
        
        # Volume das últimas 24h
        recent_volume = business_metrics.get_business_metrics(1).total_stake
        
        # Volume médio dos últimos 7 dias
        weekly_metrics = business_metrics.get_business_metrics(7)
        avg_daily_volume = weekly_metrics.total_stake / 7
        
        return recent_volume > (avg_daily_volume * 3)  # 3x maior que a média

# Instância global
alert_manager = AlertManager()

if __name__ == "__main__":
    # Teste do sistema de alertas
    print("🧪 TESTANDO SISTEMA DE ALERTAS")
    print("=" * 40)
    
    # Verificar alertas
    alert_manager.check_alerts()
    
    # Mostrar alertas ativos
    active_alerts = alert_manager.get_active_alerts()
    print(f"Alertas ativos: {len(active_alerts)}")
    
    for alert in active_alerts:
        print(f"  - {alert.rule_name}: {alert.message}")
    
    # Mostrar histórico
    history = alert_manager.get_alert_history(24)
    print(f"Histórico (24h): {len(history)} alertas")
    
    print("\n🎉 TESTES DE ALERTAS CONCLUÍDOS!")
