"""
Configurações do Sistema MaraBet AI
Centraliza todas as configurações do sistema
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Configurações principais do sistema"""
    
    # ===========================================
    # CONFIGURAÇÕES GERAIS
    # ===========================================
    app_name: str = Field(default="MaraBet AI", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    
    # ===========================================
    # SERVIDOR
    # ===========================================
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # ===========================================
    # BANCO DE DADOS
    # ===========================================
    database_url: str = Field(default="sqlite:///./data/marabet.db", env="DATABASE_URL")
    postgres_url: Optional[str] = Field(default=None, env="POSTGRES_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # ===========================================
    # APIS EXTERNAS
    # ===========================================
    api_football_key: Optional[str] = Field(default=None, env="API_FOOTBALL_KEY")
    api_football_base_url: str = Field(default="https://v3.football.api-sports.io", env="API_FOOTBALL_BASE_URL")
    
    odds_api_key: Optional[str] = Field(default=None, env="THE_ODDS_API_KEY")
    odds_api_base_url: str = Field(default="https://api.the-odds-api.com/v4", env="ODDS_API_BASE_URL")
    
    # ===========================================
    # CONFIGURAÇÕES DE COLETA
    # ===========================================
    collection_interval: int = Field(default=60, env="COLLECTION_INTERVAL")
    max_concurrent_requests: int = Field(default=5, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    monitored_leagues: str = Field(default="39,140,78,135,61,71", env="MONITORED_LEAGUES")
    
    # ===========================================
    # CONFIGURAÇÕES DE ANÁLISE
    # ===========================================
    min_confidence: float = Field(default=0.70, env="MIN_CONFIDENCE")
    max_confidence: float = Field(default=0.90, env="MAX_CONFIDENCE")
    min_value_ev: float = Field(default=0.05, env="MIN_VALUE_EV")
    kelly_fraction: float = Field(default=0.25, env="KELLY_FRACTION")
    
    # ===========================================
    # NOTIFICAÇÕES
    # ===========================================
    telegram_bot_token: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(default=None, env="TELEGRAM_CHAT_ID")
    
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    email_from: Optional[str] = Field(default=None, env="EMAIL_FROM")
    
    # ===========================================
    # CONFIGURAÇÕES ANGOLANAS
    # ===========================================
    currency: str = Field(default="AOA", env="CURRENCY")
    timezone: str = Field(default="Africa/Luanda", env="TIMEZONE")
    language: str = Field(default="pt-AO", env="LANGUAGE")
    
    # ===========================================
    # CASAS DE APOSTAS ANGOLANAS
    # ===========================================
    elephant_api_key: Optional[str] = Field(default=None, env="ELEPHANT_API_KEY")
    elephant_api_url: str = Field(default="https://api.elephantbet.com/v1", env="ELEPHANT_API_URL")
    
    kwanza_api_key: Optional[str] = Field(default=None, env="KWANZA_API_KEY")
    kwanza_api_url: str = Field(default="https://api.kwanzabet.com/v1", env="KWANZA_API_URL")
    
    premier_api_key: Optional[str] = Field(default=None, env="PREMIER_API_KEY")
    premier_api_url: str = Field(default="https://api.premierbet.com/v1", env="PREMIER_API_URL")
    
    bantu_api_key: Optional[str] = Field(default=None, env="BANTU_API_KEY")
    bantu_api_url: str = Field(default="https://api.bantubet.com/v1", env="BANTU_API_URL")
    
    onexbet_api_key: Optional[str] = Field(default=None, env="ONEXBET_API_KEY")
    onexbet_api_url: str = Field(default="https://api.1xbet.com/v1", env="ONEXBET_API_URL")
    
    mobet_api_key: Optional[str] = Field(default=None, env="MOBET_API_KEY")
    mobet_api_url: str = Field(default="https://api.mobet.com/v1", env="MOBET_API_URL")
    
    # ===========================================
    # MACHINE LEARNING
    # ===========================================
    ml_model_path: str = Field(default="./models/", env="ML_MODEL_PATH")
    training_data_path: str = Field(default="./data/training/", env="TRAINING_DATA_PATH")
    prediction_threshold: float = Field(default=0.6, env="PREDICTION_THRESHOLD")
    
    # ===========================================
    # CACHE E PERFORMANCE
    # ===========================================
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    max_cache_size: int = Field(default=1000, env="MAX_CACHE_SIZE")
    enable_cache: bool = Field(default=True, env="ENABLE_CACHE")
    
    # ===========================================
    # SEGURANÇA
    # ===========================================
    jwt_secret_key: str = Field(default="your-jwt-secret-key", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=30, env="JWT_EXPIRE_MINUTES")
    cors_origins: str = Field(default="http://localhost:3000", env="CORS_ORIGINS")
    allowed_hosts: str = Field(default="localhost,127.0.0.1", env="ALLOWED_HOSTS")
    
    # ===========================================
    # LOGS
    # ===========================================
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    log_max_bytes: int = Field(default=10485760, env="LOG_MAX_BYTES")
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    # ===========================================
    # MONITORAMENTO
    # ===========================================
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    grafana_port: int = Field(default=3000, env="GRAFANA_PORT")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    
    # ===========================================
    # BACKUP
    # ===========================================
    backup_enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    backup_interval: int = Field(default=86400, env="BACKUP_INTERVAL")
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    backup_path: str = Field(default="./backups/", env="BACKUP_PATH")
    enable_auto_backup: bool = Field(default=True, env="ENABLE_AUTO_BACKUP")
    
    # ===========================================
    # CONFIGURAÇÕES COMPUTADAS
    # ===========================================
    @property
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return not self.debug
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento"""
        return self.debug
    
    @property
    def database_connection_string(self) -> str:
        """Retorna string de conexão do banco"""
        if self.postgres_url and self.is_production:
            return self.postgres_url
        return self.database_url
    
    @property
    def supported_bookmakers(self) -> List[str]:
        """Retorna lista de casas de apostas suportadas"""
        return [
            "elephant", "kwanza", "premier", 
            "bantu", "1xbet", "mobet"
        ]
    
    @property
    def monitored_leagues_list(self) -> List[int]:
        """Retorna lista de IDs das ligas monitoradas"""
        try:
            return [int(league_id.strip()) for league_id in self.monitored_leagues.split(",")]
        except (ValueError, AttributeError):
            return [39, 140, 78, 135, 61, 71]  # Default leagues
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Retorna lista de origens CORS permitidas"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Retorna lista de hosts permitidos"""
        return [host.strip() for host in self.allowed_hosts.split(",")]
    
    @property
    def api_keys_configured(self) -> bool:
        """Verifica se as chaves de API estão configuradas"""
        return bool(
            self.api_football_key and 
            self.odds_api_key
        )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignorar campos extras

# Instância global das configurações
settings = Settings()

# Função para obter configurações
def get_settings() -> Settings:
    """Retorna as configurações do sistema"""
    return settings

# Função para validar configurações
def validate_settings() -> bool:
    """Valida se as configurações estão corretas"""
    try:
        # Verificar se os diretórios existem
        Path(settings.ml_model_path).mkdir(parents=True, exist_ok=True)
        Path(settings.training_data_path).mkdir(parents=True, exist_ok=True)
        Path(settings.backup_path).mkdir(parents=True, exist_ok=True)
        
        # Verificar se as chaves de API estão configuradas
        if not settings.api_keys_configured:
            print("⚠️  Aviso: Chaves de API não configuradas")
            print("   Configure as chaves no arquivo .env")
        
        return True
    except Exception as e:
        print(f"❌ Erro na validação das configurações: {e}")
        return False
