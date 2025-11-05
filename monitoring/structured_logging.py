#!/usr/bin/env python3
"""
Sistema de Logs Estruturados para o MaraBet AI
Logs em formato JSON para melhor análise e monitoramento
"""

import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import traceback
from enum import Enum

class LogLevel(Enum):
    """Níveis de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class JSONFormatter(logging.Formatter):
    """Formatador JSON para logs"""
    
    def format(self, record):
        """Formata log em JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Adicionar campos extras se existirem
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'bet_id'):
            log_entry['bet_id'] = record.bet_id
        if hasattr(record, 'match_id'):
            log_entry['match_id'] = record.match_id
        if hasattr(record, 'roi'):
            log_entry['roi'] = record.roi
        if hasattr(record, 'profit_loss'):
            log_entry['profit_loss'] = record.profit_loss
        if hasattr(record, 'duration_ms'):
            log_entry['duration_ms'] = record.duration_ms
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        if hasattr(record, 'error_code'):
            log_entry['error_code'] = record.error_code
        
        # Adicionar stack trace para erros
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_entry, ensure_ascii=False)

class StructuredLogger:
    """Logger estruturado para o MaraBet AI"""
    
    def __init__(self, name: str = "marabet"):
        """Inicializa logger estruturado"""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remover handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Configurar handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura handlers de log"""
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(console_handler)
        
        # Handler para arquivo de logs gerais
        file_handler = logging.FileHandler('logs/mara_bet.json', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(file_handler)
        
        # Handler para logs de erro
        error_handler = logging.FileHandler('logs/mara_bet_errors.json', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(error_handler)
        
        # Handler para logs de negócio
        business_handler = logging.FileHandler('logs/mara_bet_business.json', encoding='utf-8')
        business_handler.setLevel(logging.INFO)
        business_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(business_handler)
    
    def _log_with_context(self, level: LogLevel, message: str, **kwargs):
        """Log com contexto adicional"""
        extra = {}
        for key, value in kwargs.items():
            extra[key] = value
        
        getattr(self.logger, level.value.lower())(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log de debug"""
        self._log_with_context(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log de informação"""
        self._log_with_context(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de aviso"""
        self._log_with_context(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de erro"""
        self._log_with_context(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log crítico"""
        self._log_with_context(LogLevel.CRITICAL, message, **kwargs)
    
    # Métodos específicos para diferentes tipos de logs
    
    def log_bet_placed(self, bet_id: str, match_id: str, bet_type: str, 
                      stake: float, odds: float, user_id: str = None):
        """Log de aposta realizada"""
        self.info(
            "Aposta realizada",
            bet_id=bet_id,
            match_id=match_id,
            bet_type=bet_type,
            stake=stake,
            odds=odds,
            user_id=user_id,
            event_type="bet_placed"
        )
    
    def log_bet_result(self, bet_id: str, match_id: str, profit_loss: float, 
                      roi: float, win: bool, user_id: str = None):
        """Log de resultado de aposta"""
        self.info(
            "Resultado de aposta",
            bet_id=bet_id,
            match_id=match_id,
            profit_loss=profit_loss,
            roi=roi,
            win=win,
            user_id=user_id,
            event_type="bet_result"
        )
    
    def log_prediction(self, match_id: str, home_team: str, away_team: str,
                      prediction: str, confidence: float, expected_value: float):
        """Log de predição"""
        self.info(
            "Predição gerada",
            match_id=match_id,
            home_team=home_team,
            away_team=away_team,
            prediction=prediction,
            confidence=confidence,
            expected_value=expected_value,
            event_type="prediction"
        )
    
    def log_api_call(self, endpoint: str, method: str, status_code: int,
                    duration_ms: float, response_size: int = None):
        """Log de chamada de API"""
        self.info(
            "Chamada de API",
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms,
            response_size=response_size,
            event_type="api_call"
        )
    
    def log_alert(self, alert_id: str, rule_name: str, severity: str,
                 message: str, metadata: Dict = None):
        """Log de alerta"""
        self.warning(
            "Alerta disparado",
            alert_id=alert_id,
            rule_name=rule_name,
            severity=severity,
            message=message,
            metadata=metadata or {},
            event_type="alert"
        )
    
    def log_performance(self, operation: str, duration_ms: float,
                       success: bool, details: Dict = None):
        """Log de performance"""
        level = LogLevel.INFO if success else LogLevel.WARNING
        self._log_with_context(
            level,
            f"Operação de performance: {operation}",
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            details=details or {},
            event_type="performance"
        )
    
    def log_business_metrics(self, total_bets: int, total_stake: float,
                           total_profit: float, roi: float, win_rate: float):
        """Log de métricas de negócio"""
        self.info(
            "Métricas de negócio atualizadas",
            total_bets=total_bets,
            total_stake=total_stake,
            total_profit=total_profit,
            roi=roi,
            win_rate=win_rate,
            event_type="business_metrics"
        )
    
    def log_security_event(self, event_type: str, user_id: str = None,
                          ip_address: str = None, details: Dict = None):
        """Log de evento de segurança"""
        self.warning(
            f"Evento de segurança: {event_type}",
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            details=details or {},
            security_event=True
        )
    
    def log_system_event(self, event_type: str, component: str,
                        status: str, details: Dict = None):
        """Log de evento do sistema"""
        level = LogLevel.INFO if status == "ok" else LogLevel.WARNING
        self._log_with_context(
            level,
            f"Evento do sistema: {event_type}",
            event_type=event_type,
            component=component,
            status=status,
            details=details or {},
            system_event=True
        )

# Instância global
structured_logger = StructuredLogger()

# Decorator para logging automático
def log_function_call(func):
    """Decorator para log automático de chamadas de função"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            structured_logger.log_performance(
                operation=func.__name__,
                duration_ms=duration,
                success=True
            )
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            structured_logger.error(
                f"Erro em {func.__name__}",
                operation=func.__name__,
                duration_ms=duration,
                success=False,
                error=str(e)
            )
            
            raise
    
    return wrapper

if __name__ == "__main__":
    # Teste do sistema de logs estruturados
    print("🧪 TESTANDO LOGS ESTRUTURADOS")
    print("=" * 40)
    
    # Criar diretório de logs
    Path('logs').mkdir(exist_ok=True)
    
    # Testar diferentes tipos de logs
    structured_logger.info("Sistema iniciado", component="main")
    
    structured_logger.log_bet_placed(
        bet_id="bet_001",
        match_id="39_12345",
        bet_type="home_win",
        stake=100.0,
        odds=1.85
    )
    
    structured_logger.log_bet_result(
        bet_id="bet_001",
        match_id="39_12345",
        profit_loss=85.0,
        roi=0.85,
        win=True
    )
    
    structured_logger.log_prediction(
        match_id="39_12346",
        home_team="Manchester City",
        away_team="Liverpool",
        prediction="home_win",
        confidence=0.75,
        expected_value=0.12
    )
    
    structured_logger.log_api_call(
        endpoint="/api/predictions",
        method="POST",
        status_code=200,
        duration_ms=150.5
    )
    
    structured_logger.log_business_metrics(
        total_bets=10,
        total_stake=1000.0,
        total_profit=150.0,
        roi=0.15,
        win_rate=0.60
    )
    
    structured_logger.warning("Teste de aviso", component="test")
    structured_logger.error("Teste de erro", component="test")
    
    print("✅ Logs estruturados testados!")
    print("Verifique os arquivos em logs/")
    print("  - mara_bet.json (todos os logs)")
    print("  - mara_bet_errors.json (apenas erros)")
    print("  - mara_bet_business.json (métricas de negócio)")
    
    print("\n🎉 TESTES DE LOGS CONCLUÍDOS!")
