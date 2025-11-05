#!/usr/bin/env python3
"""
Sistema de Mensagens de Erro Amigáveis para o MaraBet AI
Mensagens claras e úteis para melhorar UX
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ErrorCategory(Enum):
    """Categorias de erro"""
    VALIDATION = "validation"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    RATE_LIMIT = "rate_limit"
    SERVER_ERROR = "server_error"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"

@dataclass
class UserFriendlyError:
    """Erro amigável para o usuário"""
    error_code: str
    category: ErrorCategory
    title: str
    message: str
    suggestion: str
    action_required: str
    technical_details: str
    severity: str
    recoverable: bool
    help_url: Optional[str] = None

class ErrorMessageGenerator:
    """Gerador de mensagens de erro amigáveis"""
    
    def __init__(self):
        """Inicializa gerador de mensagens"""
        self.error_templates = self._load_error_templates()
        self.contextual_messages = self._load_contextual_messages()
    
    def _load_error_templates(self) -> Dict[str, Dict[str, Any]]:
        """Carrega templates de erro"""
        return {
            "validation_error": {
                "title": "Dados Inválidos",
                "message": "Os dados fornecidos não estão no formato correto.",
                "suggestion": "Verifique se todos os campos foram preenchidos corretamente.",
                "action_required": "Corrija os dados e tente novamente.",
                "severity": "low",
                "recoverable": True
            },
            "network_error": {
                "title": "Problema de Conexão",
                "message": "Não foi possível conectar ao servidor.",
                "suggestion": "Verifique sua conexão com a internet.",
                "action_required": "Tente novamente em alguns segundos.",
                "severity": "medium",
                "recoverable": True
            },
            "authentication_error": {
                "title": "Acesso Negado",
                "message": "Suas credenciais não foram reconhecidas.",
                "suggestion": "Verifique seu email e senha.",
                "action_required": "Faça login novamente ou recupere sua senha.",
                "severity": "medium",
                "recoverable": True
            },
            "authorization_error": {
                "title": "Permissão Insuficiente",
                "message": "Você não tem permissão para realizar esta ação.",
                "suggestion": "Entre em contato com o administrador se precisar de acesso.",
                "action_required": "Use uma conta com as permissões necessárias.",
                "severity": "medium",
                "recoverable": False
            },
            "not_found_error": {
                "title": "Não Encontrado",
                "message": "O recurso solicitado não foi encontrado.",
                "suggestion": "Verifique se o ID ou nome está correto.",
                "action_required": "Tente com um recurso diferente ou atualize a página.",
                "severity": "low",
                "recoverable": True
            },
            "rate_limit_error": {
                "title": "Muitas Solicitações",
                "message": "Você fez muitas solicitações em pouco tempo.",
                "suggestion": "Aguarde alguns minutos antes de tentar novamente.",
                "action_required": "Reduza a frequência das suas solicitações.",
                "severity": "medium",
                "recoverable": True
            },
            "server_error": {
                "title": "Erro Interno",
                "message": "Ocorreu um erro interno no servidor.",
                "suggestion": "Nossa equipe foi notificada e está trabalhando na correção.",
                "action_required": "Tente novamente em alguns minutos.",
                "severity": "high",
                "recoverable": True
            },
            "business_logic_error": {
                "title": "Regra de Negócio",
                "message": "A operação não pode ser realizada devido a regras do sistema.",
                "suggestion": "Verifique se você atende aos requisitos necessários.",
                "action_required": "Ajuste os parâmetros ou entre em contato conosco.",
                "severity": "medium",
                "recoverable": True
            },
            "external_service_error": {
                "title": "Serviço Externo Indisponível",
                "message": "Um serviço externo necessário está temporariamente indisponível.",
                "suggestion": "Aguarde alguns minutos para o serviço voltar ao normal.",
                "action_required": "Tente novamente mais tarde.",
                "severity": "medium",
                "recoverable": True
            }
        }
    
    def _load_contextual_messages(self) -> Dict[str, Dict[str, str]]:
        """Carrega mensagens contextuais específicas"""
        return {
            "prediction_errors": {
                "no_data": "Não há dados suficientes para gerar uma predição confiável.",
                "model_error": "O modelo de predição está temporariamente indisponível.",
                "invalid_match": "A partida especificada não é válida ou não existe.",
                "future_match": "A partida ainda não começou, predições podem ser imprecisas."
            },
            "odds_errors": {
                "no_odds": "Não há odds disponíveis para esta partida no momento.",
                "bookmaker_error": "Erro ao conectar com os bookmakers.",
                "odds_expired": "As odds exibidas podem estar desatualizadas.",
                "invalid_odds": "Os dados de odds recebidos são inválidos."
            },
            "analysis_errors": {
                "insufficient_data": "Dados insuficientes para realizar a análise solicitada.",
                "calculation_error": "Erro ao calcular as métricas de análise.",
                "timeout": "A análise está demorando mais que o esperado.",
                "invalid_period": "O período selecionado para análise não é válido."
            },
            "betting_errors": {
                "insufficient_balance": "Saldo insuficiente para realizar a aposta.",
                "bet_limit_exceeded": "Você excedeu o limite de apostas permitido.",
                "odds_changed": "As odds mudaram desde que você iniciou a aposta.",
                "bet_closed": "As apostas para esta partida foram encerradas."
            }
        }
    
    def create_user_friendly_error(self, error_code: str, category: ErrorCategory,
                                 technical_details: str = "", context: str = "",
                                 custom_message: str = None) -> UserFriendlyError:
        """Cria erro amigável para o usuário"""
        
        # Obter template base
        template = self.error_templates.get(error_code, self.error_templates["server_error"])
        
        # Ajustar mensagem baseada no contexto
        if context and context in self.contextual_messages:
            contextual_msg = self.contextual_messages[context].get(error_code, "")
            if contextual_msg:
                template = template.copy()
                template["message"] = contextual_msg
        
        # Usar mensagem customizada se fornecida
        if custom_message:
            template = template.copy()
            template["message"] = custom_message
        
        return UserFriendlyError(
            error_code=error_code,
            category=category,
            title=template["title"],
            message=template["message"],
            suggestion=template["suggestion"],
            action_required=template["action_required"],
            technical_details=technical_details,
            severity=template["severity"],
            recoverable=template["recoverable"],
            help_url=self._get_help_url(error_code, category)
        )
    
    def _get_help_url(self, error_code: str, category: ErrorCategory) -> Optional[str]:
        """Obtém URL de ajuda para o erro"""
        help_urls = {
            "validation_error": "/help/validation-errors",
            "network_error": "/help/connection-issues",
            "authentication_error": "/help/login-problems",
            "authorization_error": "/help/permissions",
            "not_found_error": "/help/not-found",
            "rate_limit_error": "/help/rate-limits",
            "server_error": "/help/server-issues",
            "business_logic_error": "/help/business-rules",
            "external_service_error": "/help/external-services"
        }
        
        return help_urls.get(error_code, "/help/general")
    
    def format_error_for_ui(self, error: UserFriendlyError) -> Dict[str, Any]:
        """Formata erro para exibição na UI"""
        return {
            "error": {
                "code": error.error_code,
                "category": error.category.value,
                "title": error.title,
                "message": error.message,
                "suggestion": error.suggestion,
                "action_required": error.action_required,
                "severity": error.severity,
                "recoverable": error.recoverable,
                "help_url": error.help_url
            },
            "ui": {
                "icon": self._get_error_icon(error.severity),
                "color": self._get_error_color(error.severity),
                "show_retry": error.recoverable,
                "show_help": error.help_url is not None
            },
            "technical": {
                "details": error.technical_details,
                "timestamp": error.timestamp.isoformat() if hasattr(error, 'timestamp') else None
            }
        }
    
    def _get_error_icon(self, severity: str) -> str:
        """Obtém ícone para o erro"""
        icons = {
            "low": "info",
            "medium": "warning",
            "high": "error",
            "critical": "critical"
        }
        return icons.get(severity, "error")
    
    def _get_error_color(self, severity: str) -> str:
        """Obtém cor para o erro"""
        colors = {
            "low": "blue",
            "medium": "orange",
            "high": "red",
            "critical": "dark-red"
        }
        return colors.get(severity, "red")

class ErrorMessageHandler:
    """Handler para mensagens de erro"""
    
    def __init__(self):
        """Inicializa handler"""
        self.generator = ErrorMessageGenerator()
        self.error_history: List[UserFriendlyError] = []
    
    def handle_error(self, error: Exception, context: str = "", 
                    custom_message: str = None) -> Dict[str, Any]:
        """Trata erro e retorna mensagem amigável"""
        
        # Classificar erro
        error_code, category = self._classify_error(error)
        
        # Criar erro amigável
        friendly_error = self.generator.create_user_friendly_error(
            error_code=error_code,
            category=category,
            technical_details=str(error),
            context=context,
            custom_message=custom_message
        )
        
        # Adicionar ao histórico
        self.error_history.append(friendly_error)
        
        # Formatar para UI
        return self.generator.format_error_for_ui(friendly_error)
    
    def _classify_error(self, error: Exception) -> tuple:
        """Classifica erro e retorna código e categoria"""
        error_str = str(error).lower()
        error_type = error.__class__.__name__
        
        # Classificação por tipo de erro
        if 'validation' in error_str or 'ValueError' in error_type:
            return "validation_error", ErrorCategory.VALIDATION
        elif 'network' in error_str or 'ConnectionError' in error_type:
            return "network_error", ErrorCategory.NETWORK
        elif 'auth' in error_str or 'AuthenticationError' in error_type:
            return "authentication_error", ErrorCategory.AUTHENTICATION
        elif 'permission' in error_str or 'PermissionError' in error_type:
            return "authorization_error", ErrorCategory.AUTHORIZATION
        elif 'not found' in error_str or 'NotFoundError' in error_type:
            return "not_found_error", ErrorCategory.NOT_FOUND
        elif 'rate limit' in error_str or 'RateLimitError' in error_type:
            return "rate_limit_error", ErrorCategory.RATE_LIMIT
        elif 'server' in error_str or 'ServerError' in error_type:
            return "server_error", ErrorCategory.SERVER_ERROR
        elif 'business' in error_str or 'BusinessLogicError' in error_type:
            return "business_logic_error", ErrorCategory.BUSINESS_LOGIC
        elif 'external' in error_str or 'ExternalServiceError' in error_type:
            return "external_service_error", ErrorCategory.EXTERNAL_SERVICE
        else:
            return "server_error", ErrorCategory.SERVER_ERROR
    
    def get_error_suggestions(self, error_code: str) -> List[str]:
        """Obtém sugestões para um código de erro"""
        suggestions = {
            "validation_error": [
                "Verifique se todos os campos obrigatórios foram preenchidos",
                "Confirme se os dados estão no formato correto",
                "Tente novamente com dados diferentes"
            ],
            "network_error": [
                "Verifique sua conexão com a internet",
                "Tente novamente em alguns segundos",
                "Verifique se o servidor está funcionando"
            ],
            "authentication_error": [
                "Verifique seu email e senha",
                "Tente recuperar sua senha",
                "Entre em contato com o suporte"
            ],
            "server_error": [
                "Tente novamente em alguns minutos",
                "Verifique se há problemas conhecidos",
                "Entre em contato com o suporte técnico"
            ]
        }
        
        return suggestions.get(error_code, ["Tente novamente mais tarde"])
    
    def get_error_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém histórico de erros"""
        recent_errors = self.error_history[-limit:]
        return [self.generator.format_error_for_ui(error) for error in recent_errors]

# Instância global
error_handler = ErrorMessageHandler()

# Decorator para tratamento automático de erros
def user_friendly_error(context: str = ""):
    """Decorator para tratamento automático de erros"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_response = error_handler.handle_error(e, context)
                return {
                    "success": False,
                    "error": error_response
                }
        return wrapper
    return decorator

if __name__ == "__main__":
    # Teste do sistema de mensagens amigáveis
    print("🧪 TESTANDO SISTEMA DE MENSAGENS AMIGÁVEIS")
    print("=" * 50)
    
    # Teste com diferentes tipos de erro
    test_errors = [
        ValueError("Dados de entrada inválidos"),
        ConnectionError("Falha na conexão com o servidor"),
        RuntimeError("Erro interno do servidor"),
        FileNotFoundError("Arquivo não encontrado")
    ]
    
    for error in test_errors:
        print(f"\nErro: {type(error).__name__}")
        print(f"Mensagem técnica: {error}")
        
        response = error_handler.handle_error(error, "prediction_errors")
        print(f"Título: {response['error']['title']}")
        print(f"Mensagem: {response['error']['message']}")
        print(f"Sugestão: {response['error']['suggestion']}")
        print(f"Ação: {response['error']['action_required']}")
        print(f"Severidade: {response['error']['severity']}")
        print(f"Recuperável: {response['error']['recoverable']}")
    
    # Teste com contexto específico
    print(f"\nTeste com contexto específico:")
    custom_error = ValueError("Não há dados suficientes para predição")
    response = error_handler.handle_error(custom_error, "prediction_errors")
    print(f"Mensagem contextual: {response['error']['message']}")
    
    print("\n🎉 TESTES DE MENSAGENS AMIGÁVEIS CONCLUÍDOS!")
