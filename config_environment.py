"""
Configurações de Ambiente para MaraBet AI
Centraliza todas as configurações do sistema
"""

import os
from typing import Dict, Any

class EnvironmentConfig:
    """Configurações de ambiente centralizadas"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações do ambiente"""
        return {
            # Configurações básicas
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'debug': os.getenv('DEBUG', 'true').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            
            # Portas dos serviços
            'api_port': int(os.getenv('API_PORT', 5000)),
            'dashboard_port': int(os.getenv('DASHBOARD_PORT', 8000)),
            'flower_port': int(os.getenv('FLOWER_PORT', 5555)),
            'redis_port': int(os.getenv('REDIS_PORT', 6379)),
            
            # Banco de dados
            'database_url': os.getenv('DATABASE_URL', 'sqlite:///data/sports_data.db'),
            
            # Redis
            'redis': {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', 6379)),
                'db': int(os.getenv('REDIS_DB', 0)),
                'password': os.getenv('REDIS_PASSWORD'),
                'max_connections': int(os.getenv('REDIS_MAX_CONNECTIONS', 20)),
                'max_memory': os.getenv('REDIS_MAX_MEMORY', '512mb'),
                'max_memory_policy': os.getenv('REDIS_MAX_MEMORY_POLICY', 'allkeys-lru')
            },
            
            # APIs externas
            'api_football': {
                'key': os.getenv('API_FOOTBALL_KEY'),
                'host': os.getenv('API_FOOTBALL_HOST', 'api-football-v1.p.rapidapi.com')
            },
            'odds_api': {
                'key': os.getenv('THE_ODDS_API_KEY')
            },
            
            # Notificações
            'telegram': {
                'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
                'chat_id': os.getenv('TELEGRAM_CHAT_ID')
            },
            'email': {
                'smtp_host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('SMTP_PORT', 587)),
                'username': os.getenv('SMTP_USERNAME'),
                'password': os.getenv('SMTP_PASSWORD'),
                'from_email': os.getenv('FROM_EMAIL'),
                'recipients': os.getenv('NOTIFICATION_EMAIL_RECIPIENTS', '').split(',')
            },
            
            # Celery
            'celery': {
                'broker_url': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
                'result_backend': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
                'worker_concurrency': int(os.getenv('CELERY_WORKER_CONCURRENCY', 4)),
                'max_memory_per_child': int(os.getenv('CELERY_MAX_MEMORY_PER_CHILD', 200000)),
                'task_compression': os.getenv('CELERY_TASK_COMPRESSION', 'gzip'),
                'result_compression': os.getenv('CELERY_RESULT_COMPRESSION', 'gzip')
            },
            
            # Cache
            'cache': {
                'odds_ttl': int(os.getenv('CACHE_ODDS_TTL', 300)),  # 5 minutos
                'stats_ttl': int(os.getenv('CACHE_STATS_TTL', 1800)),  # 30 minutos
                'predictions_ttl': int(os.getenv('CACHE_PREDICTIONS_TTL', 600)),  # 10 minutos
                'leagues_ttl': int(os.getenv('CACHE_LEAGUES_TTL', 86400)),  # 24 horas
                'teams_ttl': int(os.getenv('CACHE_TEAMS_TTL', 86400))  # 24 horas
            },
            
            # Machine Learning
            'ml': {
                'model_retrain_hours': int(os.getenv('ML_MODEL_RETRAIN_HOURS', 24)),
                'prediction_cache_ttl': int(os.getenv('ML_PREDICTION_CACHE_TTL', 600)),
                'min_training_samples': int(os.getenv('ML_MIN_TRAINING_SAMPLES', 100)),
                'max_training_samples': int(os.getenv('ML_MAX_TRAINING_SAMPLES', 10000))
            },
            
            # Configurações de apostas
            'betting': {
                'default_currency': os.getenv('DEFAULT_CURRENCY', 'AOA'),
                'min_bet_amount': float(os.getenv('MIN_BET_AMOUNT', 10.0)),
                'max_bet_amount': float(os.getenv('MAX_BET_AMOUNT', 10000.0)),
                'default_bet_size': float(os.getenv('DEFAULT_BET_SIZE', 0.02)),
                'kelly_criterion_max': float(os.getenv('KELLY_CRITERION_MAX', 0.25))
            },
            
            # Configurações regionais
            'region': {
                'country': os.getenv('DEFAULT_COUNTRY', 'AO'),
                'timezone': os.getenv('DEFAULT_TIMEZONE', 'Africa/Luanda'),
                'language': os.getenv('DEFAULT_LANGUAGE', 'pt')
            },
            
            # Monitoramento
            'monitoring': {
                'prometheus_port': int(os.getenv('PROMETHEUS_PORT', 9090)),
                'grafana_port': int(os.getenv('GRAFANA_PORT', 3000)),
                'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', 60))
            },
            
            # Backup
            'backup': {
                'enabled': os.getenv('BACKUP_ENABLED', 'true').lower() == 'true',
                'schedule': os.getenv('BACKUP_SCHEDULE', '0 2 * * *'),
                'retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', 30)),
                'backup_dir': os.getenv('BACKUP_DIR', 'backups')
            },
            
            # Segurança
            'security': {
                'secret_key': os.getenv('SECRET_KEY', 'marabet-secret-key-2024'),
                'jwt_secret_key': os.getenv('JWT_SECRET_KEY', 'marabet-jwt-secret-2024'),
                'redis_password': os.getenv('REDIS_PASSWORD_PROD'),
                'encryption_key': os.getenv('ENCRYPTION_KEY', 'marabet-encryption-key-2024')
            },
            
            # Casas de apostas (Angola)
            'bookmakers': {
                'elephantbet': {
                    'api_key': os.getenv('ELEPHANTBET_API_KEY'),
                    'base_url': os.getenv('ELEPHANTBET_BASE_URL', 'https://api.elephantbet.ao'),
                    'enabled': os.getenv('ELEPHANTBET_ENABLED', 'true').lower() == 'true'
                },
                'kwanzabet': {
                    'api_key': os.getenv('KWANZABET_API_KEY'),
                    'base_url': os.getenv('KWANZABET_BASE_URL', 'https://api.kwanzabet.ao'),
                    'enabled': os.getenv('KWANZABET_ENABLED', 'true').lower() == 'true'
                },
                'premierbet': {
                    'api_key': os.getenv('PREMIERBET_API_KEY'),
                    'base_url': os.getenv('PREMIERBET_BASE_URL', 'https://api.premierbet.ao'),
                    'enabled': os.getenv('PREMIERBET_ENABLED', 'true').lower() == 'true'
                },
                'bantubet': {
                    'api_key': os.getenv('BANTUBET_API_KEY'),
                    'base_url': os.getenv('BANTUBET_BASE_URL', 'https://api.bantubet.ao'),
                    'enabled': os.getenv('BANTUBET_ENABLED', 'true').lower() == 'true'
                },
                '1xbet': {
                    'api_key': os.getenv('ONEXBET_API_KEY'),
                    'base_url': os.getenv('ONEXBET_BASE_URL', 'https://api.1xbet.ao'),
                    'enabled': os.getenv('ONEXBET_ENABLED', 'true').lower() == 'true'
                },
                'mobet': {
                    'api_key': os.getenv('MOBET_API_KEY'),
                    'base_url': os.getenv('MOBET_BASE_URL', 'https://api.mobet.ao'),
                    'enabled': os.getenv('MOBET_ENABLED', 'true').lower() == 'true'
                }
            },
            
            # URLs de produção
            'urls': {
                'production': os.getenv('PRODUCTION_URL', 'https://app.marabet.ai'),
                'staging': os.getenv('STAGING_URL', 'https://staging.marabet.ai'),
                'api': os.getenv('API_URL', 'http://localhost:5000'),
                'dashboard': os.getenv('DASHBOARD_URL', 'http://localhost:8000'),
                'flower': os.getenv('FLOWER_URL', 'http://localhost:5555')
            },
            
            # Configurações de teste
            'testing': {
                'test_mode': os.getenv('TEST_MODE', 'false').lower() == 'true',
                'mock_api_responses': os.getenv('MOCK_API_RESPONSES', 'false').lower() == 'true',
                'test_data_enabled': os.getenv('TEST_DATA_ENABLED', 'true').lower() == 'true',
                'test_matches_count': int(os.getenv('TEST_MATCHES_COUNT', 100))
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_redis_url(self) -> str:
        """Obtém URL do Redis"""
        redis_config = self.config['redis']
        password = f":{redis_config['password']}@" if redis_config['password'] else ""
        return f"redis://{password}{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"
    
    def get_database_url(self) -> str:
        """Obtém URL do banco de dados"""
        return self.config['database_url']
    
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return self.config['environment'] == 'production'
    
    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento"""
        return self.config['environment'] == 'development'
    
    def is_staging(self) -> bool:
        """Verifica se está em staging"""
        return self.config['environment'] == 'staging'
    
    def get_enabled_bookmakers(self) -> list:
        """Obtém lista de casas de apostas habilitadas"""
        enabled = []
        for name, config in self.config['bookmakers'].items():
            if config['enabled'] and config['api_key']:
                enabled.append(name)
        return enabled
    
    def validate_config(self) -> Dict[str, list]:
        """Valida configurações obrigatórias"""
        errors = []
        warnings = []
        
        # Verificações obrigatórias
        if not self.config['api_football']['key']:
            errors.append("API_FOOTBALL_KEY é obrigatória")
        
        if not self.config['telegram']['bot_token']:
            warnings.append("TELEGRAM_BOT_TOKEN não configurado - notificações via Telegram desabilitadas")
        
        if not self.config['email']['username']:
            warnings.append("SMTP_USERNAME não configurado - notificações via email desabilitadas")
        
        # Verificar casas de apostas
        enabled_bookmakers = self.get_enabled_bookmakers()
        if not enabled_bookmakers:
            warnings.append("Nenhuma casa de apostas configurada")
        
        return {
            'errors': errors,
            'warnings': warnings
        }
    
    def print_config(self):
        """Imprime configurações (sem dados sensíveis)"""
        print("🔧 Configurações do MaraBet AI")
        print("=" * 50)
        
        # Configurações básicas
        print(f"Ambiente: {self.config['environment']}")
        print(f"Debug: {self.config['debug']}")
        print(f"Log Level: {self.config['log_level']}")
        
        # Portas
        print(f"\nPortas:")
        print(f"  API: {self.config['api_port']}")
        print(f"  Dashboard: {self.config['dashboard_port']}")
        print(f"  Flower: {self.config['flower_port']}")
        print(f"  Redis: {self.config['redis_port']}")
        
        # Redis
        print(f"\nRedis:")
        print(f"  Host: {self.config['redis']['host']}")
        print(f"  Port: {self.config['redis']['port']}")
        print(f"  DB: {self.config['redis']['db']}")
        print(f"  Max Memory: {self.config['redis']['max_memory']}")
        
        # APIs
        print(f"\nAPIs:")
        print(f"  API-Football: {'✅' if self.config['api_football']['key'] else '❌'}")
        print(f"  The Odds API: {'✅' if self.config['odds_api']['key'] else '❌'}")
        
        # Notificações
        print(f"\nNotificações:")
        print(f"  Telegram: {'✅' if self.config['telegram']['bot_token'] else '❌'}")
        print(f"  Email: {'✅' if self.config['email']['username'] else '❌'}")
        
        # Casas de apostas
        enabled_bookmakers = self.get_enabled_bookmakers()
        print(f"\nCasas de Apostas: {len(enabled_bookmakers)} habilitadas")
        for bookmaker in enabled_bookmakers:
            print(f"  ✅ {bookmaker}")
        
        # Validação
        validation = self.validate_config()
        if validation['errors']:
            print(f"\n❌ Erros:")
            for error in validation['errors']:
                print(f"  • {error}")
        
        if validation['warnings']:
            print(f"\n⚠️  Avisos:")
            for warning in validation['warnings']:
                print(f"  • {warning}")

# Instância global
config = EnvironmentConfig()

# Funções de conveniência
def get_config(key: str, default: Any = None) -> Any:
    """Obtém valor de configuração"""
    return config.get(key, default)

def get_redis_url() -> str:
    """Obtém URL do Redis"""
    return config.get_redis_url()

def get_database_url() -> str:
    """Obtém URL do banco de dados"""
    return config.get_database_url()

def is_production() -> bool:
    """Verifica se está em produção"""
    return config.is_production()

def is_development() -> bool:
    """Verifica se está em desenvolvimento"""
    return config.is_development()

def is_staging() -> bool:
    """Verifica se está em staging"""
    return config.is_staging()

def get_enabled_bookmakers() -> list:
    """Obtém lista de casas de apostas habilitadas"""
    return config.get_enabled_bookmakers()

def validate_config() -> Dict[str, list]:
    """Valida configurações obrigatórias"""
    return config.validate_config()

def print_config():
    """Imprime configurações"""
    config.print_config()

if __name__ == '__main__':
    print_config()
    
    print("\n" + "=" * 50)
    print("Validação de Configurações:")
    validation = validate_config()
    
    if validation['errors']:
        print("❌ Configuração inválida!")
        for error in validation['errors']:
            print(f"  • {error}")
    else:
        print("✅ Configuração válida!")
    
    if validation['warnings']:
        print("\n⚠️  Avisos:")
        for warning in validation['warnings']:
            print(f"  • {warning}")
