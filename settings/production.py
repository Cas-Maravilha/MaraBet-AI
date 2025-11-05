#!/usr/bin/env python3
"""
Configurações de Produção para o MaraBet AI
Configuração segura e robusta para ambiente de produção
"""

import os
import secrets
import logging
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class ProductionConfig:
    """Configurações de produção seguras"""
    
    # ==================== SEGURANÇA ====================
    
    # SECRET_KEY - Gerar automaticamente se não existir
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_urlsafe(32)
    
    # Debug - SEMPRE False em produção
    DEBUG = False
    
    # Hosts permitidos
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    
    # ==================== HTTPS/SSL ====================
    
    # Redirecionamento HTTPS obrigatório
    SECURE_SSL_REDIRECT = True
    
    # Cookies seguros
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Headers de segurança
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # ==================== RATE LIMITING ====================
    
    # Rate limiting por IP
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Limites por endpoint
    RATELIMIT_DEFAULT = "1000 per hour"
    RATELIMIT_API = "100 per minute"
    RATELIMIT_PREDICTIONS = "50 per minute"
    RATELIMIT_NOTIFICATIONS = "20 per minute"
    
    # ==================== BANCO DE DADOS ====================
    
    # URL do banco de dados
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///mara_bet.db')
    
    # Pool de conexões
    DATABASE_POOL_SIZE = int(os.getenv('DATABASE_POOL_SIZE', '10'))
    DATABASE_MAX_OVERFLOW = int(os.getenv('DATABASE_MAX_OVERFLOW', '20'))
    DATABASE_POOL_TIMEOUT = int(os.getenv('DATABASE_POOL_TIMEOUT', '30'))
    
    # ==================== CACHE ====================
    
    # Redis para cache
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))
    
    # ==================== LOGGING ====================
    
    # Configuração de logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/mara_bet_production.log')
    
    # Configuração de logging
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'simple': {
                'format': '%(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'file': {
                'level': LOG_LEVEL,
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOG_FILE,
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'formatter': 'detailed'
            },
            'console': {
                'level': LOG_LEVEL,
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            }
        },
        'loggers': {
            'mara_bet': {
                'handlers': ['file', 'console'],
                'level': LOG_LEVEL,
                'propagate': False
            }
        }
    }
    
    # ==================== API CONFIGURATION ====================
    
    # Configurações da API
    API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY')
    THE_ODDS_API_KEY = os.getenv('THE_ODDS_API_KEY')
    
    # Timeouts
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
    API_RETRY_ATTEMPTS = int(os.getenv('API_RETRY_ATTEMPTS', '3'))
    
    # ==================== NOTIFICAÇÕES ====================
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Email
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.mail.yahoo.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    
    # ==================== MONITORAMENTO ====================
    
    # Sentry para monitoramento de erros
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    
    # Prometheus para métricas
    PROMETHEUS_ENABLED = True
    PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', '9090'))
    
    # ==================== PERFORMANCE ====================
    
    # Workers
    WORKERS = int(os.getenv('WORKERS', '4'))
    
    # Threads
    THREADS = int(os.getenv('THREADS', '2'))
    
    # Timeout
    TIMEOUT = int(os.getenv('TIMEOUT', '120'))
    
    # ==================== VALIDAÇÕES ====================
    
    @classmethod
    def validate_config(cls):
        """Valida configurações críticas"""
        errors = []
        
        # Validar SECRET_KEY
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'your_secret_key_here':
            errors.append("SECRET_KEY não configurado")
        
        # Validar DEBUG
        if cls.DEBUG:
            errors.append("DEBUG deve ser False em produção")
        
        # Validar API keys
        if not cls.API_FOOTBALL_KEY:
            errors.append("API_FOOTBALL_KEY não configurado")
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN não configurado")
        
        if not cls.SMTP_USERNAME:
            errors.append("SMTP_USERNAME não configurado")
        
        # Validar hosts
        if not cls.ALLOWED_HOSTS or cls.ALLOWED_HOSTS == ['']:
            errors.append("ALLOWED_HOSTS não configurado")
        
        return errors
    
    @classmethod
    def get_security_headers(cls):
        """Retorna headers de segurança"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
    
    @classmethod
    def setup_logging(cls):
        """Configura sistema de logging"""
        import logging.config
        
        # Criar diretório de logs se não existir
        log_dir = Path(cls.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging
        logging.config.dictConfig(cls.LOGGING_CONFIG)
        
        return logging.getLogger('mara_bet')

# Configuração padrão
config = ProductionConfig()

# Validar configuração na importação
if __name__ == "__main__":
    errors = config.validate_config()
    if errors:
        print("❌ ERROS DE CONFIGURAÇÃO:")
        for error in errors:
            print(f"   - {error}")
        exit(1)
    else:
        print("✅ CONFIGURAÇÃO DE PRODUÇÃO VÁLIDA!")
        print(f"   - SECRET_KEY: {'*' * 32}")
        print(f"   - DEBUG: {config.DEBUG}")
        print(f"   - ALLOWED_HOSTS: {config.ALLOWED_HOSTS}")
        print(f"   - SSL: {config.SECURE_SSL_REDIRECT}")
        print(f"   - RATE_LIMITING: {config.RATELIMIT_ENABLED}")
        print(f"   - LOG_LEVEL: {config.LOG_LEVEL}")
        print(f"   - WORKERS: {config.WORKERS}")
        print(f"   - TIMEOUT: {config.TIMEOUT}")
        print("🎉 SISTEMA PRONTO PARA PRODUÇÃO!")
