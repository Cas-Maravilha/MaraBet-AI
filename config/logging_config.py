"""
Configuração de logging para o sistema MaraBet AI
"""
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from config.settings import settings

def setup_logging():
    """Configurar sistema de logging"""
    
    # Criar diretório de logs se não existir
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar formato de log
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remover handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # Handler para arquivo
    file_handler = logging.handlers.RotatingFileHandler(
        settings.log_file,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # Handler para erros
    error_handler = logging.handlers.RotatingFileHandler(
        "logs/error.log",
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    root_logger.addHandler(error_handler)
    
    # Configurar loggers específicos
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Log de inicialização
    logger = logging.getLogger(__name__)
    logger.info("🔧 Sistema de logging configurado com sucesso")
    logger.info(f"📁 Diretório de logs: {log_dir.absolute()}")
    logger.info(f"📊 Nível de log: {settings.log_level}")

def get_logger(name: str) -> logging.Logger:
    """Obter logger para um módulo específico"""
    return logging.getLogger(name)

def log_performance(func_name: str, duration: float, **kwargs):
    """Log de performance de funções"""
    logger = logging.getLogger("performance")
    logger.info(f"⏱️ {func_name} executado em {duration:.3f}s - {kwargs}")

def log_api_call(endpoint: str, method: str, status_code: int, duration: float):
    """Log de chamadas de API"""
    logger = logging.getLogger("api")
    level = logging.INFO if status_code < 400 else logging.WARNING
    logger.log(level, f"🌐 {method} {endpoint} - {status_code} - {duration:.3f}s")

def log_ml_prediction(model_name: str, accuracy: float, duration: float):
    """Log de previsões de ML"""
    logger = logging.getLogger("ml")
    logger.info(f"🤖 {model_name} - Acurácia: {accuracy:.3f} - Tempo: {duration:.3f}s")

def log_data_collection(source: str, records: int, duration: float):
    """Log de coleta de dados"""
    logger = logging.getLogger("collector")
    logger.info(f"📊 {source} - {records} registros coletados em {duration:.3f}s")

def log_error(error: Exception, context: str = ""):
    """Log de erros com contexto"""
    logger = logging.getLogger("error")
    logger.error(f"❌ Erro em {context}: {str(error)}", exc_info=True)

def log_security(event: str, details: str = ""):
    """Log de eventos de segurança"""
    logger = logging.getLogger("security")
    logger.warning(f"🔒 {event} - {details}")

def log_business_metric(metric: str, value: float, context: str = ""):
    """Log de métricas de negócio"""
    logger = logging.getLogger("business")
    logger.info(f"📈 {metric}: {value} - {context}")

# Configurar logging na importação
if __name__ != "__main__":
    setup_logging()
