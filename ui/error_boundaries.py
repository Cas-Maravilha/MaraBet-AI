#!/usr/bin/env python3
"""
Sistema de Error Boundaries para o MaraBet AI
Captura e tratamento de erros para melhorar UX
"""

import traceback
import logging
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass
from enum import Enum
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Severidade do erro"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorType(Enum):
    """Tipo de erro"""
    VALIDATION = "validation"
    NETWORK = "network"
    DATABASE = "database"
    ML_MODEL = "ml_model"
    API = "api"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    UNKNOWN = "unknown"

@dataclass
class ErrorInfo:
    """Informações de erro"""
    error_id: str
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    user_message: str
    technical_details: str
    timestamp: datetime
    context: Dict[str, Any]
    stack_trace: str
    recoverable: bool
    suggestions: List[str]

class ErrorBoundary:
    """Boundary para captura de erros"""
    
    def __init__(self, name: str, fallback_handler: Callable = None):
        """Inicializa error boundary"""
        self.name = name
        self.fallback_handler = fallback_handler
        self.error_count = 0
        self.last_error_time = None
        self.error_history: List[ErrorInfo] = []
    
    def catch_error(self, func: Callable, *args, **kwargs) -> Any:
        """Captura erros de uma função"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = self._create_error_info(e, func.__name__, args, kwargs)
            self._handle_error(error_info)
            
            if self.fallback_handler:
                return self.fallback_handler(error_info)
            
            # Retornar erro amigável em vez de re-raise
            return {
                "error": True,
                "message": error_info.user_message,
                "suggestions": error_info.suggestions,
                "error_id": error_info.error_id
            }
    
    def _create_error_info(self, error: Exception, func_name: str, 
                          args: tuple, kwargs: dict) -> ErrorInfo:
        """Cria informações de erro"""
        error_id = f"{self.name}_{int(time.time())}"
        
        # Determinar tipo e severidade
        error_type, severity = self._classify_error(error)
        
        # Criar mensagens
        message = str(error)
        user_message = self._create_user_message(error, error_type)
        technical_details = f"Function: {func_name}, Args: {args}, Kwargs: {kwargs}"
        
        # Obter stack trace
        stack_trace = traceback.format_exc()
        
        # Determinar se é recuperável
        recoverable = self._is_recoverable(error, error_type)
        
        # Gerar sugestões
        suggestions = self._generate_suggestions(error, error_type)
        
        return ErrorInfo(
            error_id=error_id,
            error_type=error_type,
            severity=severity,
            message=message,
            user_message=user_message,
            technical_details=technical_details,
            timestamp=datetime.now(),
            context={
                'function': func_name,
                'args': str(args),
                'kwargs': str(kwargs),
                'boundary': self.name
            },
            stack_trace=stack_trace,
            recoverable=recoverable,
            suggestions=suggestions
        )
    
    def _classify_error(self, error: Exception) -> tuple:
        """Classifica tipo e severidade do erro"""
        error_str = str(error).lower()
        error_type = error.__class__.__name__
        
        # Classificar por tipo
        if 'validation' in error_str or 'ValueError' in error_type:
            return ErrorType.VALIDATION, ErrorSeverity.LOW
        elif 'network' in error_str or 'ConnectionError' in error_type:
            return ErrorType.NETWORK, ErrorSeverity.MEDIUM
        elif 'database' in error_str or 'sqlite' in error_str:
            return ErrorType.DATABASE, ErrorSeverity.HIGH
        elif 'model' in error_str or 'ml' in error_str:
            return ErrorType.ML_MODEL, ErrorSeverity.HIGH
        elif 'api' in error_str or 'http' in error_str:
            return ErrorType.API, ErrorSeverity.MEDIUM
        elif 'system' in error_str or 'OSError' in error_type:
            return ErrorType.SYSTEM, ErrorSeverity.CRITICAL
        elif 'input' in error_str or 'user' in error_str:
            return ErrorType.USER_INPUT, ErrorSeverity.LOW
        else:
            return ErrorType.UNKNOWN, ErrorSeverity.MEDIUM
    
    def _create_user_message(self, error: Exception, error_type: ErrorType) -> str:
        """Cria mensagem amigável para o usuário"""
        messages = {
            ErrorType.VALIDATION: "Os dados fornecidos não são válidos. Verifique as informações e tente novamente.",
            ErrorType.NETWORK: "Problema de conexão. Verifique sua internet e tente novamente.",
            ErrorType.DATABASE: "Erro interno do sistema. Nossa equipe foi notificada.",
            ErrorType.ML_MODEL: "Erro no processamento de dados. Tente novamente em alguns minutos.",
            ErrorType.API: "Serviço temporariamente indisponível. Tente novamente mais tarde.",
            ErrorType.SYSTEM: "Erro crítico do sistema. Nossa equipe foi notificada imediatamente.",
            ErrorType.USER_INPUT: "Entrada inválida. Verifique os dados e tente novamente.",
            ErrorType.UNKNOWN: "Ocorreu um erro inesperado. Tente novamente ou entre em contato conosco."
        }
        
        return messages.get(error_type, messages[ErrorType.UNKNOWN])
    
    def _is_recoverable(self, error: Exception, error_type: ErrorType) -> bool:
        """Determina se erro é recuperável"""
        recoverable_types = {
            ErrorType.VALIDATION: True,
            ErrorType.NETWORK: True,
            ErrorType.USER_INPUT: True,
            ErrorType.API: True,
            ErrorType.DATABASE: False,
            ErrorType.ML_MODEL: True,
            ErrorType.SYSTEM: False,
            ErrorType.UNKNOWN: True
        }
        
        return recoverable_types.get(error_type, True)
    
    def _generate_suggestions(self, error: Exception, error_type: ErrorType) -> List[str]:
        """Gera sugestões para resolver o erro"""
        suggestions = {
            ErrorType.VALIDATION: [
                "Verifique se todos os campos obrigatórios foram preenchidos",
                "Confirme se os dados estão no formato correto",
                "Tente novamente com dados diferentes"
            ],
            ErrorType.NETWORK: [
                "Verifique sua conexão com a internet",
                "Tente novamente em alguns segundos",
                "Verifique se o servidor está funcionando"
            ],
            ErrorType.DATABASE: [
                "Tente novamente em alguns minutos",
                "Entre em contato com o suporte técnico",
                "Verifique se há problemas conhecidos"
            ],
            ErrorType.ML_MODEL: [
                "Aguarde alguns minutos e tente novamente",
                "Verifique se os dados de entrada são válidos",
                "Tente com dados mais recentes"
            ],
            ErrorType.API: [
                "Tente novamente mais tarde",
                "Verifique se o serviço está funcionando",
                "Entre em contato com o suporte"
            ],
            ErrorType.SYSTEM: [
                "Nossa equipe foi notificada",
                "Tente novamente em alguns minutos",
                "Entre em contato com o suporte imediatamente"
            ],
            ErrorType.USER_INPUT: [
                "Verifique os dados inseridos",
                "Use o formato correto para cada campo",
                "Consulte a documentação se necessário"
            ],
            ErrorType.UNKNOWN: [
                "Tente novamente em alguns minutos",
                "Entre em contato com o suporte",
                "Verifique se há atualizações disponíveis"
            ]
        }
        
        return suggestions.get(error_type, ["Tente novamente mais tarde"])
    
    def _handle_error(self, error_info: ErrorInfo):
        """Trata erro capturado"""
        self.error_count += 1
        self.last_error_time = datetime.now()
        self.error_history.append(error_info)
        
        # Log do erro
        logger.error(f"Error in {self.name}: {error_info.message}")
        logger.debug(f"Stack trace: {error_info.stack_trace}")
        
        # Notificar se for crítico
        if error_info.severity == ErrorSeverity.CRITICAL:
            self._notify_critical_error(error_info)
    
    def _notify_critical_error(self, error_info: ErrorInfo):
        """Notifica erro crítico"""
        # Em produção, enviar para sistema de monitoramento
        logger.critical(f"CRITICAL ERROR in {self.name}: {error_info.message}")
        
        # Aqui você pode integrar com Sentry, Slack, etc.
        print(f"🚨 ERRO CRÍTICO: {error_info.message}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de erros"""
        if not self.error_history:
            return {"total_errors": 0}
        
        recent_errors = [e for e in self.error_history 
                        if (datetime.now() - e.timestamp).seconds < 3600]  # Última hora
        
        error_types = {}
        severities = {}
        
        for error in self.error_history:
            error_types[error.error_type.value] = error_types.get(error.error_type.value, 0) + 1
            severities[error.severity.value] = severities.get(error.severity.value, 0) + 1
        
        return {
            "total_errors": len(self.error_history),
            "recent_errors": len(recent_errors),
            "error_types": error_types,
            "severities": severities,
            "last_error": self.last_error_time.isoformat() if self.last_error_time else None
        }

class ErrorBoundaryManager:
    """Gerenciador de error boundaries"""
    
    def __init__(self):
        """Inicializa gerenciador"""
        self.boundaries: Dict[str, ErrorBoundary] = {}
        self.global_error_handler: Optional[Callable] = None
    
    def create_boundary(self, name: str, fallback_handler: Callable = None) -> ErrorBoundary:
        """Cria novo error boundary"""
        boundary = ErrorBoundary(name, fallback_handler)
        self.boundaries[name] = boundary
        return boundary
    
    def get_boundary(self, name: str) -> Optional[ErrorBoundary]:
        """Obtém error boundary por nome"""
        return self.boundaries.get(name)
    
    def set_global_error_handler(self, handler: Callable):
        """Define handler global de erros"""
        self.global_error_handler = handler
    
    def handle_global_error(self, error_info: ErrorInfo):
        """Trata erro global"""
        if self.global_error_handler:
            self.global_error_handler(error_info)
    
    def get_all_error_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de todos os boundaries"""
        stats = {}
        total_errors = 0
        
        for name, boundary in self.boundaries.items():
            boundary_stats = boundary.get_error_stats()
            stats[name] = boundary_stats
            total_errors += boundary_stats.get('total_errors', 0)
        
        stats['total_errors_all_boundaries'] = total_errors
        return stats

# Decorator para error boundaries
def error_boundary(boundary_name: str, fallback_handler: Callable = None):
    """Decorator para error boundary"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Obter ou criar boundary
            manager = ErrorBoundaryManager()
            boundary = manager.get_boundary(boundary_name)
            if not boundary:
                boundary = manager.create_boundary(boundary_name, fallback_handler)
            
            return boundary.catch_error(func, *args, **kwargs)
        return wrapper
    return decorator

# Error boundaries específicos do MaraBet AI
class MaraBetErrorBoundaries:
    """Error boundaries específicos do sistema"""
    
    def __init__(self):
        """Inicializa boundaries específicos"""
        self.manager = ErrorBoundaryManager()
        
        # Criar boundaries específicos
        self.prediction_boundary = self.manager.create_boundary(
            "predictions",
            self._prediction_fallback
        )
        
        self.odds_boundary = self.manager.create_boundary(
            "odds",
            self._odds_fallback
        )
        
        self.analysis_boundary = self.manager.create_boundary(
            "analysis",
            self._analysis_fallback
        )
        
        self.database_boundary = self.manager.create_boundary(
            "database",
            self._database_fallback
        )
    
    def _prediction_fallback(self, error_info: ErrorInfo) -> Dict[str, Any]:
        """Fallback para erros de predição"""
        return {
            "error": True,
            "message": error_info.user_message,
            "suggestions": error_info.suggestions,
            "fallback_data": {
                "prediction": "unknown",
                "confidence": 0.0,
                "message": "Predição não disponível devido a erro interno"
            }
        }
    
    def _odds_fallback(self, error_info: ErrorInfo) -> Dict[str, Any]:
        """Fallback para erros de odds"""
        return {
            "error": True,
            "message": error_info.user_message,
            "suggestions": error_info.suggestions,
            "fallback_data": {
                "odds": {},
                "message": "Odds não disponíveis no momento"
            }
        }
    
    def _analysis_fallback(self, error_info: ErrorInfo) -> Dict[str, Any]:
        """Fallback para erros de análise"""
        return {
            "error": True,
            "message": error_info.user_message,
            "suggestions": error_info.suggestions,
            "fallback_data": {
                "analysis": {},
                "message": "Análise não disponível no momento"
            }
        }
    
    def _database_fallback(self, error_info: ErrorInfo) -> Dict[str, Any]:
        """Fallback para erros de banco de dados"""
        return {
            "error": True,
            "message": error_info.user_message,
            "suggestions": error_info.suggestions,
            "fallback_data": {
                "data": [],
                "message": "Dados não disponíveis no momento"
            }
        }

# Instância global
error_boundaries = MaraBetErrorBoundaries()

if __name__ == "__main__":
    # Teste do sistema de error boundaries
    print("🧪 TESTANDO SISTEMA DE ERROR BOUNDARIES")
    print("=" * 40)
    
    # Testar boundary de predições
    @error_boundary("predictions")
    def test_prediction_function(match_id: str):
        if match_id == "error":
            raise ValueError("Erro de validação: Match ID inválido")
        elif match_id == "critical":
            raise RuntimeError("Erro crítico do sistema")
        else:
            return {"prediction": "home_win", "confidence": 0.75}
    
    # Teste com erro de validação
    print("Teste com erro de validação:")
    result = test_prediction_function("error")
    print(f"Resultado: {result}")
    
    # Teste com erro crítico
    print("\nTeste com erro crítico:")
    result = test_prediction_function("critical")
    print(f"Resultado: {result}")
    
    # Teste sem erro
    print("\nTeste sem erro:")
    result = test_prediction_function("39_12345")
    print(f"Resultado: {result}")
    
    # Estatísticas
    stats = error_boundaries.manager.get_all_error_stats()
    print(f"\nEstatísticas de erros:")
    print(f"  Total de erros: {stats.get('total_errors_all_boundaries', 0)}")
    
    print("\n🎉 TESTES DE ERROR BOUNDARIES CONCLUÍDOS!")
