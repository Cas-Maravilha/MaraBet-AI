#!/usr/bin/env python3
"""
Script de Validação de Configuração de Produção
Verifica se todas as configurações estão corretas para produção
"""

import os
import sys
import secrets
from pathlib import Path
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionValidator:
    """Validador de configuração de produção"""
    
    def __init__(self, env_file='config_production.env'):
        """Inicializa validador"""
        self.env_file = env_file
        self.errors = []
        self.warnings = []
        self.load_env()
    
    def load_env(self):
        """Carrega variáveis de ambiente"""
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
        else:
            logger.warning(f"Arquivo {self.env_file} não encontrado")
    
    def validate_security(self):
        """Valida configurações de segurança"""
        logger.info("🔐 Validando configurações de segurança...")
        
        # SECRET_KEY
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or secret_key == 'your_secret_key_here':
            self.errors.append("SECRET_KEY não configurado")
        elif len(secret_key) < 32:
            self.warnings.append("SECRET_KEY muito curto (recomendado: 32+ caracteres)")
        
        # DEBUG
        debug = os.getenv('DEBUG', 'False').lower()
        if debug == 'true':
            self.errors.append("DEBUG deve ser False em produção")
        
        # ALLOWED_HOSTS
        allowed_hosts = os.getenv('ALLOWED_HOSTS', '')
        if not allowed_hosts or allowed_hosts == 'localhost,127.0.0.1':
            self.warnings.append("ALLOWED_HOSTS usando valores padrão")
        
        # SSL
        ssl_cert = os.getenv('SSL_CERT_PATH')
        ssl_key = os.getenv('SSL_KEY_PATH')
        if not ssl_cert or not ssl_key:
            self.warnings.append("Certificados SSL não configurados")
        elif not os.path.exists(ssl_cert) or not os.path.exists(ssl_key):
            self.warnings.append("Arquivos de certificado SSL não encontrados")
    
    def validate_database(self):
        """Valida configurações do banco de dados"""
        logger.info("🗄️ Validando configurações do banco de dados...")
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            self.errors.append("DATABASE_URL não configurado")
        elif database_url.startswith('sqlite://'):
            self.warnings.append("Usando SQLite (recomendado PostgreSQL para produção)")
        
        # Pool de conexões
        pool_size = os.getenv('DATABASE_POOL_SIZE', '10')
        try:
            pool_size = int(pool_size)
            if pool_size < 5:
                self.warnings.append("DATABASE_POOL_SIZE muito baixo")
        except ValueError:
            self.errors.append("DATABASE_POOL_SIZE deve ser um número")
    
    def validate_redis(self):
        """Valida configurações do Redis"""
        logger.info("🔴 Validando configurações do Redis...")
        
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            self.warnings.append("REDIS_URL não configurado (rate limiting desabilitado)")
        else:
            # Testar conexão Redis
            try:
                import redis
                r = redis.from_url(redis_url)
                r.ping()
                logger.info("✅ Redis conectado com sucesso")
            except ImportError:
                self.warnings.append("Redis não instalado")
            except Exception as e:
                self.warnings.append(f"Redis não acessível: {e}")
    
    def validate_api_keys(self):
        """Valida chaves de API"""
        logger.info("🔑 Validando chaves de API...")
        
        # API Football
        api_football = os.getenv('API_FOOTBALL_KEY')
        if not api_football or api_football == 'your_api_football_key_here':
            self.warnings.append("API_FOOTBALL_KEY não configurado")
        
        # Telegram
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not telegram_token or telegram_token == 'your_telegram_bot_token_here':
            self.warnings.append("TELEGRAM_BOT_TOKEN não configurado")
        
        # Email
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        if not smtp_username or smtp_username == 'your_yahoo_email_here':
            self.warnings.append("SMTP_USERNAME não configurado")
        if not smtp_password or smtp_password == 'your_yahoo_app_password_here':
            self.warnings.append("SMTP_PASSWORD não configurado")
    
    def validate_performance(self):
        """Valida configurações de performance"""
        logger.info("⚡ Validando configurações de performance...")
        
        # Workers
        workers = os.getenv('WORKERS', '4')
        try:
            workers = int(workers)
            if workers < 2:
                self.warnings.append("WORKERS muito baixo (recomendado: 4+)")
        except ValueError:
            self.errors.append("WORKERS deve ser um número")
        
        # Timeout
        timeout = os.getenv('TIMEOUT', '120')
        try:
            timeout = int(timeout)
            if timeout < 60:
                self.warnings.append("TIMEOUT muito baixo (recomendado: 120+)")
        except ValueError:
            self.errors.append("TIMEOUT deve ser um número")
    
    def validate_logging(self):
        """Valida configurações de logging"""
        logger.info("📝 Validando configurações de logging...")
        
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            self.errors.append("LOG_LEVEL inválido")
        
        log_file = os.getenv('LOG_FILE', 'logs/mara_bet_production.log')
        log_dir = Path(log_file).parent
        if not log_dir.exists():
            self.warnings.append(f"Diretório de logs não existe: {log_dir}")
    
    def validate_monitoring(self):
        """Valida configurações de monitoramento"""
        logger.info("📊 Validando configurações de monitoramento...")
        
        sentry_dsn = os.getenv('SENTRY_DSN')
        if not sentry_dsn or sentry_dsn == 'your_sentry_dsn_here':
            self.warnings.append("SENTRY_DSN não configurado (monitoramento de erros desabilitado)")
        
        prometheus_port = os.getenv('PROMETHEUS_PORT', '9090')
        try:
            prometheus_port = int(prometheus_port)
            if prometheus_port < 1024:
                self.warnings.append("PROMETHEUS_PORT muito baixo (recomendado: 9090+)")
        except ValueError:
            self.errors.append("PROMETHEUS_PORT deve ser um número")
    
    def generate_secret_key(self):
        """Gera SECRET_KEY seguro"""
        return secrets.token_urlsafe(32)
    
    def fix_configuration(self):
        """Corrige configurações automaticamente"""
        logger.info("🔧 Corrigindo configurações...")
        
        # Gerar SECRET_KEY se necessário
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or secret_key == 'your_secret_key_here':
            new_secret = self.generate_secret_key()
            logger.info(f"✅ SECRET_KEY gerado: {new_secret}")
            return new_secret
        
        return None
    
    def run_validation(self):
        """Executa todas as validações"""
        logger.info("🚀 Iniciando validação de configuração de produção...")
        print("=" * 60)
        
        # Executar validações
        self.validate_security()
        self.validate_database()
        self.validate_redis()
        self.validate_api_keys()
        self.validate_performance()
        self.validate_logging()
        self.validate_monitoring()
        
        # Exibir resultados
        print("\n📋 RESULTADOS DA VALIDAÇÃO:")
        print("=" * 40)
        
        if self.errors:
            print("❌ ERROS CRÍTICOS:")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print("\n⚠️ AVISOS:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ CONFIGURAÇÃO PERFEITA!")
            print("   Todas as configurações estão corretas para produção.")
        
        # Status geral
        if self.errors:
            print(f"\n❌ VALIDAÇÃO FALHOU: {len(self.errors)} erro(s) crítico(s)")
            return False
        elif self.warnings:
            print(f"\n⚠️ VALIDAÇÃO COM AVISOS: {len(self.warnings)} aviso(s)")
            return True
        else:
            print(f"\n✅ VALIDAÇÃO APROVADA!")
            return True

def main():
    """Função principal"""
    print("🔮 MARABET AI - VALIDADOR DE CONFIGURAÇÃO DE PRODUÇÃO")
    print("=" * 60)
    
    # Verificar se arquivo de configuração existe
    config_file = 'config_production.env'
    if not os.path.exists(config_file):
        print(f"❌ Arquivo {config_file} não encontrado!")
        print("   Execute este script no diretório raiz do projeto.")
        return 1
    
    # Executar validação
    validator = ProductionValidator(config_file)
    success = validator.run_validation()
    
    # Oferecer correções
    if not success:
        print("\n🔧 CORREÇÕES DISPONÍVEIS:")
        print("=" * 40)
        
        # Gerar SECRET_KEY se necessário
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or secret_key == 'your_secret_key_here':
            new_secret = validator.generate_secret_key()
            print(f"1. SECRET_KEY gerado: {new_secret}")
            print("   Adicione ao arquivo de configuração:")
            print(f"   SECRET_KEY={new_secret}")
        
        print("\n2. Configure DEBUG=False no arquivo de configuração")
        print("3. Configure ALLOWED_HOSTS com seu domínio")
        print("4. Configure certificados SSL")
        print("5. Configure Redis para rate limiting")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
