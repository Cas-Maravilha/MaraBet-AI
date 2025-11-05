#!/usr/bin/env python3
"""
Configuração do Sentry para o MaraBet AI
Rastreamento de erros e monitoramento de performance
"""

import os
import logging
from typing import Dict, Any, Optional
from flask import Flask, request, g
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger(__name__)

class SentryConfig:
    """Configuração do Sentry"""
    
    def __init__(self, app: Flask = None):
        """Inicializa configuração do Sentry"""
        self.app = app
        self.dsn = os.getenv('SENTRY_DSN')
        self.environment = os.getenv('SENTRY_ENVIRONMENT', 'production')
        self.release = os.getenv('SENTRY_RELEASE', '1.0.0')
        self.sample_rate = float(os.getenv('SENTRY_SAMPLE_RATE', '1.0'))
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Inicializa Sentry na aplicação Flask"""
        if not self.dsn:
            logger.warning("SENTRY_DSN não configurado. Sentry desabilitado.")
            return
        
        # Configurar Sentry
        sentry_sdk.init(
            dsn=self.dsn,
            environment=self.environment,
            release=self.release,
            sample_rate=self.sample_rate,
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                )
            ],
            traces_sample_rate=0.1,  # 10% das transações
            profiles_sample_rate=0.1,  # 10% dos profiles
            before_send=self.before_send,
            before_send_transaction=self.before_send_transaction
        )
        
        # Middleware para contexto adicional
        @app.before_request
        def set_sentry_context():
            """Define contexto do Sentry para cada requisição"""
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("component", "marabet_ai")
                scope.set_tag("version", self.release)
                
                # Adicionar informações da requisição
                if request:
                    scope.set_tag("method", request.method)
                    scope.set_tag("path", request.path)
                    scope.set_tag("user_agent", request.headers.get('User-Agent', ''))
                    
                    # Adicionar IP do usuário
                    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
                    scope.set_user({"ip_address": client_ip})
        
        logger.info("Sentry configurado com sucesso")
    
    def before_send(self, event, hint):
        """Filtra eventos antes de enviar para o Sentry"""
        # Filtrar eventos de desenvolvimento
        if self.environment == 'development':
            return None
        
        # Filtrar erros específicos
        if 'exc_info' in hint:
            exc_type, exc_value, tb = hint['exc_info']
            
            # Filtrar erros conhecidos que não precisam ser reportados
            if exc_type.__name__ in ['ValidationError', 'BadRequest']:
                return None
        
        # Adicionar contexto personalizado
        event.setdefault('tags', {})
        event['tags']['marabet_component'] = 'api'
        
        return event
    
    def before_send_transaction(self, event, hint):
        """Filtra transações antes de enviar para o Sentry"""
        # Filtrar transações de health check
        if event.get('transaction') == '/health':
            return None
        
        return event
    
    def capture_bet_event(self, bet_id: str, event_type: str, 
                         data: Dict[str, Any] = None):
        """Captura evento relacionado a apostas"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("bet_id", bet_id)
            scope.set_tag("event_type", event_type)
            scope.set_context("bet_data", data or {})
            
            sentry_sdk.capture_message(
                f"Bet event: {event_type}",
                level="info"
            )
    
    def capture_prediction_event(self, match_id: str, prediction: str,
                               confidence: float, expected_value: float):
        """Captura evento de predição"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("match_id", match_id)
            scope.set_tag("prediction", prediction)
            scope.set_context("prediction_data", {
                "confidence": confidence,
                "expected_value": expected_value
            })
            
            sentry_sdk.capture_message(
                f"Prediction generated for match {match_id}",
                level="info"
            )
    
    def capture_business_metrics(self, metrics: Dict[str, Any]):
        """Captura métricas de negócio"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_context("business_metrics", metrics)
            
            # Alertar se ROI for muito baixo
            if metrics.get('roi', 0) < -0.2:  # ROI < -20%
                sentry_sdk.capture_message(
                    f"Low ROI detected: {metrics['roi']:.2%}",
                    level="warning"
                )
    
    def capture_api_error(self, endpoint: str, method: str, 
                         status_code: int, error: str):
        """Captura erro de API"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("endpoint", endpoint)
            scope.set_tag("method", method)
            scope.set_tag("status_code", status_code)
            scope.set_context("api_error", {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "error": error
            })
            
            sentry_sdk.capture_message(
                f"API Error: {method} {endpoint} - {status_code}",
                level="error"
            )
    
    def capture_alert(self, alert_id: str, rule_name: str, 
                     severity: str, message: str):
        """Captura alerta do sistema"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("alert_id", alert_id)
            scope.set_tag("rule_name", rule_name)
            scope.set_tag("severity", severity)
            scope.set_context("alert", {
                "alert_id": alert_id,
                "rule_name": rule_name,
                "severity": severity,
                "message": message
            })
            
            level = "warning" if severity in ["low", "medium"] else "error"
            sentry_sdk.capture_message(
                f"Alert: {rule_name} - {message}",
                level=level
            )
    
    def capture_performance_issue(self, operation: str, duration_ms: float,
                                 threshold_ms: float = 1000):
        """Captura problema de performance"""
        if duration_ms > threshold_ms:
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("operation", operation)
                scope.set_context("performance", {
                    "operation": operation,
                    "duration_ms": duration_ms,
                    "threshold_ms": threshold_ms
                })
                
                sentry_sdk.capture_message(
                    f"Performance issue: {operation} took {duration_ms:.2f}ms",
                    level="warning"
                )
    
    def set_user_context(self, user_id: str, username: str = None,
                        email: str = None):
        """Define contexto do usuário"""
        sentry_sdk.set_user({
            "id": user_id,
            "username": username,
            "email": email
        })
    
    def clear_user_context(self):
        """Limpa contexto do usuário"""
        sentry_sdk.set_user(None)
    
    def add_breadcrumb(self, message: str, category: str = "default",
                      level: str = "info", data: Dict[str, Any] = None):
        """Adiciona breadcrumb para rastreamento"""
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )
    
    def get_sentry_client(self):
        """Obtém cliente do Sentry"""
        return sentry_sdk

# Instância global
sentry_config = SentryConfig()

# Decorator para captura automática de erros
def capture_errors(func):
    """Decorator para captura automática de erros"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Adicionar contexto antes de capturar
            sentry_sdk.set_context("function", {
                "name": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs)
            })
            
            sentry_sdk.capture_exception(e)
            raise
    
    return wrapper

# Decorator para rastreamento de performance
def track_performance(operation_name: str = None):
    """Decorator para rastreamento de performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            operation = operation_name or func.__name__
            
            with sentry_sdk.start_transaction(
                op=operation,
                name=f"{operation} - {func.__name__}"
            ) as transaction:
                try:
                    result = func(*args, **kwargs)
                    transaction.set_status("ok")
                    return result
                except Exception as e:
                    transaction.set_status("internal_error")
                    sentry_sdk.capture_exception(e)
                    raise
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # Teste da configuração do Sentry
    print("🧪 TESTANDO CONFIGURAÇÃO DO SENTRY")
    print("=" * 40)
    
    # Verificar se DSN está configurado
    dsn = os.getenv('SENTRY_DSN')
    if dsn:
        print(f"✅ SENTRY_DSN configurado: {dsn[:20]}...")
        
        # Testar captura de evento
        sentry_config.capture_bet_event(
            bet_id="test_001",
            event_type="bet_placed",
            data={"stake": 100, "odds": 1.85}
        )
        
        print("✅ Evento de teste enviado para Sentry")
    else:
        print("⚠️ SENTRY_DSN não configurado")
        print("Configure a variável SENTRY_DSN para habilitar o Sentry")
    
    print("\n🎉 TESTE DO SENTRY CONCLUÍDO!")
