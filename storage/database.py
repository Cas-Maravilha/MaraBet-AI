"""
Configuração do banco de dados para o sistema MaraBet AI
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from config.settings import settings
from .models import Base
import logging

logger = logging.getLogger(__name__)

# Configurar engine do banco de dados
if settings.is_production:
    # PostgreSQL para produção
    engine = create_engine(
        settings.database_connection_string,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.debug
    )
else:
    # SQLite para desenvolvimento
    engine = create_engine(
        settings.database_connection_string,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=settings.debug
    )

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Importar modelos para disponibilizar
from .models import (
    User, League, Team, Match, Odds, Statistics, 
    Prediction, BettingHistory, BacktestingResults, 
    SystemLog, Notification
)

# Função para obter sessão do banco
def get_db() -> Session:
    """Obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para criar tabelas
def create_tables():
    """Criar todas as tabelas"""
    try:
        Base.create_all(bind=engine)
        logger.info("✅ Tabelas do banco de dados criadas com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        raise

# Função para verificar conexão
def check_connection() -> bool:
    """Verificar se a conexão com o banco está funcionando"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✅ Conexão com banco de dados OK")
        return True
    except Exception as e:
        logger.error(f"❌ Erro de conexão com banco: {e}")
        return False

# Função para fechar conexões
def close_connections():
    """Fechar todas as conexões"""
    try:
        engine.dispose()
        logger.info("✅ Conexões do banco fechadas")
    except Exception as e:
        logger.error(f"❌ Erro ao fechar conexões: {e}")

# Configurar logging do SQLAlchemy
if settings.debug:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)
