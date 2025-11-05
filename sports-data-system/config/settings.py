"""
Configurações do Sistema Básico - MaraBet AI
Sistema econômico com SQLite e APIs gratuitas
"""

import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).parent.parent

# Configurações do banco de dados SQLite
DATABASE_CONFIG = {
    'path': BASE_DIR / 'data' / 'sports_data.db',
    'timeout': 30,
    'check_same_thread': False
}

# Configurações da API-Football (plano gratuito)
API_FOOTBALL_CONFIG = {
    'base_url': 'https://v3.football.api-sports.io',
    'timeout': 30,
    'rate_limit': 10,  # requests per minute (plano gratuito)
    'max_retries': 3
}

# Configurações de cache
CACHE_CONFIG = {
    'enabled': True,
    'ttl': 3600,  # 1 hora em segundos
    'max_size': 1000,  # máximo de itens no cache
    'path': BASE_DIR / 'cache'
}

# Configurações de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': BASE_DIR / 'logs' / 'sports_system.log',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# Configurações de análise
ANALYSIS_CONFIG = {
    'min_matches': 5,  # mínimo de partidas para análise
    'confidence_threshold': 0.6,  # threshold mínimo de confiança
    'value_threshold': 0.05,  # threshold mínimo de value (5%)
    'max_odds': 10.0,  # odds máxima aceita
    'min_odds': 1.01  # odds mínima aceita
}

# Configurações de ML
ML_CONFIG = {
    'train_test_split': 0.8,
    'random_state': 42,
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'model_save_path': 'models/'
}

# Configurações de coleta de dados
DATA_COLLECTION_CONFIG = {
    'leagues': [
        {'id': 39, 'name': 'Premier League', 'country': 'England'},
        {'id': 140, 'name': 'La Liga', 'country': 'Spain'},
        {'id': 135, 'name': 'Serie A', 'country': 'Italy'},
        {'id': 78, 'name': 'Bundesliga', 'country': 'Germany'},
        {'id': 61, 'name': 'Ligue 1', 'country': 'France'}
    ],
    'seasons': ['2024', '2023'],
    'update_interval': 3600,  # 1 hora em segundos
    'batch_size': 50  # tamanho do lote para processamento
}

# Configurações de notificações
NOTIFICATION_CONFIG = {
    'enabled': True,
    'email': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': '',
        'password': ''
    },
    'webhook': {
        'enabled': False,
        'url': ''
    }
}

# Configurações de segurança
SECURITY_CONFIG = {
    'api_key_rotation': True,
    'max_failed_requests': 10,
    'block_duration': 3600,  # 1 hora em segundos
    'encrypt_sensitive_data': True
}

# Configurações de performance
PERFORMANCE_CONFIG = {
    'max_concurrent_requests': 5,
    'request_timeout': 30,
    'memory_limit': 512 * 1024 * 1024,  # 512MB
    'cpu_limit': 80  # 80% de uso máximo de CPU
}

# Configurações de backup
BACKUP_CONFIG = {
    'enabled': True,
    'interval': 86400,  # 24 horas em segundos
    'retention_days': 30,
    'path': BASE_DIR / 'backups',
    'compress': True
}

# Configurações de monitoramento
MONITORING_CONFIG = {
    'enabled': True,
    'metrics_interval': 300,  # 5 minutos
    'health_check_interval': 60,  # 1 minuto
    'alert_thresholds': {
        'error_rate': 0.1,  # 10%
        'response_time': 5.0,  # 5 segundos
        'memory_usage': 0.8,  # 80%
        'cpu_usage': 0.9  # 90%
    }
}

# Configurações de desenvolvimento
DEV_CONFIG = {
    'debug': True,
    'verbose_logging': True,
    'mock_apis': False,
    'test_data': True
}

def get_config():
    """Retorna todas as configurações"""
    return {
        'database': DATABASE_CONFIG,
        'api_football': API_FOOTBALL_CONFIG,
        'cache': CACHE_CONFIG,
        'logging': LOGGING_CONFIG,
        'analysis': ANALYSIS_CONFIG,
        'ml': ML_CONFIG,
        'data_collection': DATA_COLLECTION_CONFIG,
        'notification': NOTIFICATION_CONFIG,
        'security': SECURITY_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'backup': BACKUP_CONFIG,
        'monitoring': MONITORING_CONFIG,
        'dev': DEV_CONFIG
    }

def create_directories():
    """Cria diretórios necessários"""
    directories = [
        BASE_DIR / 'data',
        BASE_DIR / 'cache',
        BASE_DIR / 'logs',
        BASE_DIR / 'backups',
        BASE_DIR / 'models'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ Diretórios criados com sucesso")

if __name__ == "__main__":
    # Testa as configurações
    config = get_config()
    print("🔧 Configurações do Sistema Básico:")
    print(f"• Banco de dados: {config['database']['path']}")
    print(f"• API Football: {config['api_football']['base_url']}")
    print(f"• Cache: {'Ativado' if config['cache']['enabled'] else 'Desativado'}")
    print(f"• Logs: {config['logging']['file']}")
    print(f"• Análise: {config['analysis']['min_matches']} partidas mínimas")
    print(f"• ML: {config['ml']['n_estimators']} estimadores")
    
    # Cria diretórios
    create_directories()
