#!/usr/bin/env python3
"""
Script de configuração e migração do PostgreSQL para MaraBet AI
Configura o banco de dados e migra dados do SQLite se necessário
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from armazenamento.banco_de_dados import DatabaseManager, Base
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostgreSQLSetup:
    """Configurador do PostgreSQL para MaraBet AI"""
    
    def __init__(self, postgres_url: str, sqlite_path: str = None):
        """
        Inicializa o configurador
        
        Args:
            postgres_url: URL de conexão do PostgreSQL
            sqlite_path: Caminho para o arquivo SQLite (opcional)
        """
        self.postgres_url = postgres_url
        self.sqlite_path = sqlite_path
        self.engine = None
        self.session = None
        
    def test_connection(self) -> bool:
        """Testa a conexão com o PostgreSQL"""
        try:
            engine = create_engine(self.postgres_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✅ Conexão com PostgreSQL estabelecida com sucesso")
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com PostgreSQL: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Cria todas as tabelas necessárias"""
        try:
            self.engine = create_engine(self.postgres_url)
            Base.metadata.create_all(bind=self.engine)
            
            # Criar sessão
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            logger.info("✅ Tabelas criadas com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            return False
    
    def create_indexes(self) -> bool:
        """Cria índices para otimização"""
        try:
            with self.engine.connect() as conn:
                # Índices para tabela de partidas
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_fixture_id 
                    ON matches(fixture_id)
                """))
                
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_date 
                    ON matches(date)
                """))
                
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_league 
                    ON matches(league_name)
                """))
                
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_matches_status 
                    ON matches(status)
                """))
                
                # Índices para tabela de odds
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_odds_fixture_id 
                    ON odds(fixture_id)
                """))
                
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_odds_bookmaker 
                    ON odds(bookmaker)
                """))
                
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_odds_market 
                    ON odds(market)
                """))
                
                # Índices para tabela de predições
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_predictions_fixture_id 
                    ON predictions(fixture_id)
                """))
                
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_predictions_created_at 
                    ON predictions(created_at)
                """))
                
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_predictions_recommended 
                    ON predictions(recommended)
                """))
                
                # Índices para tabela de usuários
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username 
                    ON users(username)
                """))
                
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email 
                    ON users(email)
                """))
                
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role 
                    ON users(role)
                """))
                
                conn.commit()
                
            logger.info("✅ Índices criados com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao criar índices: {e}")
            return False
    
    def migrate_from_sqlite(self) -> bool:
        """Migra dados do SQLite para PostgreSQL"""
        if not self.sqlite_path or not os.path.exists(self.sqlite_path):
            logger.warning("⚠️ Arquivo SQLite não encontrado, pulando migração")
            return True
        
        try:
            # Conectar ao SQLite
            sqlite_conn = sqlite3.connect(self.sqlite_path)
            
            # Conectar ao PostgreSQL
            postgres_conn = psycopg2.connect(self.postgres_url)
            postgres_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            postgres_cursor = postgres_conn.cursor()
            
            # Lista de tabelas para migrar
            tables = ['matches', 'odds', 'predictions', 'betting_history', 'users', 'user_sessions', 'user_activities']
            
            for table in tables:
                try:
                    # Verificar se a tabela existe no SQLite
                    sqlite_cursor = sqlite_conn.cursor()
                    sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    
                    if not sqlite_cursor.fetchone():
                        logger.info(f"⚠️ Tabela {table} não encontrada no SQLite, pulando")
                        continue
                    
                    # Ler dados do SQLite
                    df = pd.read_sql_query(f"SELECT * FROM {table}", sqlite_conn)
                    
                    if df.empty:
                        logger.info(f"⚠️ Tabela {table} está vazia, pulando")
                        continue
                    
                    # Limpar tabela no PostgreSQL
                    postgres_cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
                    
                    # Inserir dados no PostgreSQL
                    df.to_sql(table, self.engine, if_exists='append', index=False, method='multi')
                    
                    logger.info(f"✅ Migrada tabela {table}: {len(df)} registros")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao migrar tabela {table}: {e}")
                    continue
            
            # Fechar conexões
            sqlite_conn.close()
            postgres_conn.close()
            
            logger.info("✅ Migração do SQLite para PostgreSQL concluída")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na migração: {e}")
            return False
    
    def setup_optimization_tables(self) -> bool:
        """Configura tabelas para otimização de hiperparâmetros"""
        try:
            with self.engine.connect() as conn:
                # Criar tabela para estudos de otimização
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS optimization_studies (
                        id SERIAL PRIMARY KEY,
                        study_name VARCHAR(255) UNIQUE NOT NULL,
                        model_name VARCHAR(100) NOT NULL,
                        status VARCHAR(50) DEFAULT 'running',
                        best_score FLOAT,
                        best_params JSONB,
                        n_trials INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP
                    )
                """))
                
                # Criar tabela para trials de otimização
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS optimization_trials (
                        id SERIAL PRIMARY KEY,
                        study_id INTEGER REFERENCES optimization_studies(id),
                        trial_number INTEGER NOT NULL,
                        params JSONB NOT NULL,
                        value FLOAT,
                        state VARCHAR(50) DEFAULT 'running',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP
                    )
                """))
                
                # Criar índices para otimização
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_optimization_studies_name 
                    ON optimization_studies(study_name)
                """))
                
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_optimization_studies_model 
                    ON optimization_studies(model_name)
                """))
                
                conn.execute(text("""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_optimization_trials_study 
                    ON optimization_trials(study_id)
                """))
                
                conn.commit()
                
            logger.info("✅ Tabelas de otimização criadas com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas de otimização: {e}")
            return False
    
    def run_health_check(self) -> bool:
        """Executa verificação de saúde do banco"""
        try:
            with self.engine.connect() as conn:
                # Verificar conexão
                result = conn.execute(text("SELECT 1")).fetchone()
                if not result:
                    return False
                
                # Verificar tabelas principais
                tables = ['matches', 'odds', 'predictions', 'users']
                for table in tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                    logger.info(f"📊 Tabela {table}: {result[0]} registros")
                
                # Verificar configurações
                result = conn.execute(text("SHOW shared_buffers")).fetchone()
                logger.info(f"🔧 Shared buffers: {result[0]}")
                
                result = conn.execute(text("SHOW max_connections")).fetchone()
                logger.info(f"🔧 Max connections: {result[0]}")
                
            logger.info("✅ Verificação de saúde concluída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de saúde: {e}")
            return False
    
    def setup_complete(self) -> bool:
        """Executa configuração completa"""
        logger.info("🚀 Iniciando configuração do PostgreSQL para MaraBet AI")
        
        # Testar conexão
        if not self.test_connection():
            return False
        
        # Criar tabelas
        if not self.create_tables():
            return False
        
        # Criar índices
        if not self.create_indexes():
            return False
        
        # Migrar dados do SQLite (se existir)
        if self.sqlite_path:
            if not self.migrate_from_sqlite():
                logger.warning("⚠️ Migração do SQLite falhou, continuando...")
        
        # Configurar tabelas de otimização
        if not self.setup_optimization_tables():
            return False
        
        # Verificação de saúde
        if not self.run_health_check():
            return False
        
        logger.info("🎉 Configuração do PostgreSQL concluída com sucesso!")
        return True


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Configuração do PostgreSQL para MaraBet AI")
    parser.add_argument("--postgres-url", required=True, help="URL de conexão do PostgreSQL")
    parser.add_argument("--sqlite-path", help="Caminho para arquivo SQLite para migração")
    parser.add_argument("--migrate-only", action="store_true", help="Apenas migrar dados")
    parser.add_argument("--health-check-only", action="store_true", help="Apenas verificar saúde")
    
    args = parser.parse_args()
    
    setup = PostgreSQLSetup(args.postgres_url, args.sqlite_path)
    
    if args.health_check_only:
        success = setup.test_connection() and setup.run_health_check()
    elif args.migrate_only:
        success = setup.migrate_from_sqlite()
    else:
        success = setup.setup_complete()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
