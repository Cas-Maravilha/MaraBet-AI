"""
Utilitários de logging para o sistema MaraBet AI
"""
import logging
import functools
import time
from typing import Any, Callable, Optional
from config.logging_config import get_logger

def log_function_call(logger_name: str = "function"):
    """Decorator para log de chamadas de função"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger(logger_name)
            start_time = time.time()
            
            try:
                logger.debug(f"🔄 Iniciando {func.__name__}")
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"✅ {func.__name__} concluído em {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {func.__name__} falhou em {duration:.3f}s: {str(e)}")
                raise
        
        return wrapper
    return decorator

def log_performance(operation: str):
    """Decorator para log de performance"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger("performance")
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"⏱️ {operation} executado em {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {operation} falhou em {duration:.3f}s: {str(e)}")
                raise
        
        return wrapper
    return decorator

def log_api_endpoint(endpoint: str):
    """Decorator para log de endpoints de API"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            logger = get_logger("api")
            start_time = time.time()
            
            try:
                logger.info(f"🌐 Acessando {endpoint}")
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"✅ {endpoint} respondido em {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {endpoint} falhou em {duration:.3f}s: {str(e)}")
                raise
        
        return wrapper
    return decorator

def log_data_operation(operation: str):
    """Decorator para log de operações de dados"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger("data")
            start_time = time.time()
            
            try:
                logger.debug(f"📊 Iniciando {operation}")
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"✅ {operation} concluído em {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {operation} falhou em {duration:.3f}s: {str(e)}")
                raise
        
        return wrapper
    return decorator

def log_ml_operation(model_name: str):
    """Decorator para log de operações de ML"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger("ml")
            start_time = time.time()
            
            try:
                logger.info(f"🤖 Iniciando {model_name}")
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"✅ {model_name} concluído em {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {model_name} falhou em {duration:.3f}s: {str(e)}")
                raise
        
        return wrapper
    return decorator

class LoggerMixin:
    """Mixin para adicionar logging a classes"""
    
    @property
    def logger(self):
        """Logger para a classe"""
        return get_logger(self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs):
        """Log de informação"""
        self.logger.info(f"ℹ️ {message}", extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log de aviso"""
        self.logger.warning(f"⚠️ {message}", extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log de erro"""
        self.logger.error(f"❌ {message}", extra=kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Log de debug"""
        self.logger.debug(f"🔍 {message}", extra=kwargs)
    
    def log_success(self, message: str, **kwargs):
        """Log de sucesso"""
        self.logger.info(f"✅ {message}", extra=kwargs)

def create_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Criar logger personalizado"""
    logger = get_logger(name)
    logger.setLevel(getattr(logging, level.upper()))
    return logger

def log_business_event(event: str, value: Any = None, context: str = ""):
    """Log de eventos de negócio"""
    logger = get_logger("business")
    message = f"📈 {event}"
    if value is not None:
        message += f" - Valor: {value}"
    if context:
        message += f" - Contexto: {context}"
    logger.info(message)

def log_security_event(event: str, details: str = ""):
    """Log de eventos de segurança"""
    logger = get_logger("security")
    logger.warning(f"🔒 {event} - {details}")

def log_system_metric(metric: str, value: float, unit: str = ""):
    """Log de métricas do sistema"""
    logger = get_logger("metrics")
    message = f"📊 {metric}: {value}"
    if unit:
        message += f" {unit}"
    logger.info(message)

# Logger padrão para importação
default_logger = get_logger(__name__)
