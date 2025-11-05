"""
Sistema de Logging - Sistema Básico
Configuração centralizada de logging
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional, Dict, Any

def setup_logger(name: str = "sports_system", 
                level: str = "INFO",
                log_file: Optional[str] = None,
                max_size: int = 10 * 1024 * 1024,  # 10MB
                backup_count: int = 5,
                format_string: Optional[str] = None) -> logging.Logger:
    """
    Configura logger com rotação de arquivos
    
    Args:
        name: Nome do logger
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho do arquivo de log
        max_size: Tamanho máximo do arquivo antes da rotação (bytes)
        backup_count: Número de arquivos de backup
        format_string: String de formatação personalizada
    
    Returns:
        Logger configurado
    """
    
    # Cria logger
    logger = logging.getLogger(name)
    
    # Evita duplicação de handlers
    if logger.handlers:
        return logger
    
    # Define nível
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Define formato padrão
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (se especificado)
    if log_file:
        # Cria diretório se não existir
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Handler com rotação
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = "sports_system") -> logging.Logger:
    """Retorna logger existente ou cria novo"""
    return logging.getLogger(name)

def configure_system_logging(config: Dict[str, Any]) -> Dict[str, logging.Logger]:
    """
    Configura logging para todo o sistema
    
    Args:
        config: Configuração de logging
    
    Returns:
        Dicionário com loggers configurados
    """
    
    loggers = {}
    
    # Logger principal
    main_logger = setup_logger(
        name="sports_system",
        level=config.get('level', 'INFO'),
        log_file=config.get('file'),
        max_size=config.get('max_size', 10 * 1024 * 1024),
        backup_count=config.get('backup_count', 5)
    )
    loggers['main'] = main_logger
    
    # Logger para coletores
    collectors_logger = setup_logger(
        name="collectors",
        level=config.get('level', 'INFO'),
        log_file=str(Path(config.get('file', 'logs/sports_system.log')).parent / 'collectors.log'),
        max_size=config.get('max_size', 10 * 1024 * 1024),
        backup_count=config.get('backup_count', 5)
    )
    loggers['collectors'] = collectors_logger
    
    # Logger para processadores
    processors_logger = setup_logger(
        name="processors",
        level=config.get('level', 'INFO'),
        log_file=str(Path(config.get('file', 'logs/sports_system.log')).parent / 'processors.log'),
        max_size=config.get('max_size', 10 * 1024 * 1024),
        backup_count=config.get('backup_count', 5)
    )
    loggers['processors'] = processors_logger
    
    # Logger para banco de dados
    database_logger = setup_logger(
        name="database",
        level=config.get('level', 'INFO'),
        log_file=str(Path(config.get('file', 'logs/sports_system.log')).parent / 'database.log'),
        max_size=config.get('max_size', 10 * 1024 * 1024),
        backup_count=config.get('backup_count', 5)
    )
    loggers['database'] = database_logger
    
    # Logger para análise
    analysis_logger = setup_logger(
        name="analysis",
        level=config.get('level', 'INFO'),
        log_file=str(Path(config.get('file', 'logs/sports_system.log')).parent / 'analysis.log'),
        max_size=config.get('max_size', 10 * 1024 * 1024),
        backup_count=config.get('backup_count', 5)
    )
    loggers['analysis'] = analysis_logger
    
    return loggers

class LoggerMixin:
    """Mixin para adicionar logging a classes"""
    
    @property
    def logger(self) -> logging.Logger:
        """Retorna logger da classe"""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
    
    def log_info(self, message: str, **kwargs):
        """Log de informação"""
        self.logger.info(message, **kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Log de debug"""
        self.logger.debug(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log de aviso"""
        self.logger.warning(message, **kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log de erro"""
        self.logger.error(message, **kwargs)
    
    def log_critical(self, message: str, **kwargs):
        """Log crítico"""
        self.logger.critical(message, **kwargs)

def log_function_call(func):
    """Decorator para logar chamadas de função"""
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Chamando {func.__name__} com args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} executada com sucesso")
            return result
        except Exception as e:
            logger.error(f"Erro em {func.__name__}: {e}")
            raise
    return wrapper

def log_performance(func):
    """Decorator para logar performance de função"""
    import time
    
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executada em {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Erro em {func.__name__} após {execution_time:.3f}s: {e}")
            raise
    return wrapper

def create_log_summary(log_file: str) -> Dict[str, Any]:
    """
    Cria resumo de logs
    
    Args:
        log_file: Caminho do arquivo de log
    
    Returns:
        Dicionário com resumo dos logs
    """
    
    try:
        log_path = Path(log_file)
        if not log_path.exists():
            return {'error': 'Arquivo de log não encontrado'}
        
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Conta níveis de log
        level_counts = {}
        error_lines = []
        warning_lines = []
        
        for i, line in enumerate(lines):
            if ' - ERROR - ' in line:
                level_counts['ERROR'] = level_counts.get('ERROR', 0) + 1
                error_lines.append((i + 1, line.strip()))
            elif ' - WARNING - ' in line:
                level_counts['WARNING'] = level_counts.get('WARNING', 0) + 1
                warning_lines.append((i + 1, line.strip()))
            elif ' - INFO - ' in line:
                level_counts['INFO'] = level_counts.get('INFO', 0) + 1
            elif ' - DEBUG - ' in line:
                level_counts['DEBUG'] = level_counts.get('DEBUG', 0) + 1
            elif ' - CRITICAL - ' in line:
                level_counts['CRITICAL'] = level_counts.get('CRITICAL', 0) + 1
        
        return {
            'total_lines': len(lines),
            'level_counts': level_counts,
            'error_lines': error_lines[-10:],  # Últimos 10 erros
            'warning_lines': warning_lines[-10:],  # Últimos 10 avisos
            'file_size_mb': log_path.stat().st_size / (1024 * 1024),
            'last_modified': log_path.stat().st_mtime
        }
        
    except Exception as e:
        return {'error': f'Erro ao processar log: {e}'}

if __name__ == "__main__":
    # Teste do sistema de logging
    print("🧪 TESTE DO SISTEMA DE LOGGING")
    print("=" * 50)
    
    # Configuração de teste
    config = {
        'level': 'DEBUG',
        'file': 'test_logs/test.log',
        'max_size': 1024 * 1024,  # 1MB
        'backup_count': 3
    }
    
    # Configura loggers
    loggers = configure_system_logging(config)
    
    # Testa diferentes loggers
    print("1. Testando loggers...")
    loggers['main'].info("Mensagem de informação")
    loggers['collectors'].debug("Mensagem de debug")
    loggers['processors'].warning("Mensagem de aviso")
    loggers['database'].error("Mensagem de erro")
    
    # Testa mixin
    print("2. Testando LoggerMixin...")
    
    class TestClass(LoggerMixin):
        def test_method(self):
            self.log_info("Método de teste executado")
            self.log_debug("Debug do método")
            self.log_warning("Aviso do método")
    
    test_obj = TestClass()
    test_obj.test_method()
    
    # Testa decorators
    print("3. Testando decorators...")
    
    @log_function_call
    @log_performance
    def test_function(x, y):
        import time
        time.sleep(0.1)
        return x + y
    
    result = test_function(1, 2)
    print(f"   Resultado: {result}")
    
    # Cria resumo de logs
    print("4. Criando resumo de logs...")
    summary = create_log_summary('test_logs/test.log')
    print(f"   Total de linhas: {summary.get('total_lines', 0)}")
    print(f"   Contagem por nível: {summary.get('level_counts', {})}")
    
    print("\n✅ Teste do logging concluído!")
