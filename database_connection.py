#!/usr/bin/env python3
"""
Módulo de Conexão PostgreSQL
MaraBet AI - Gerenciamento de conexões com banco de dados
"""

import os
import sys
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, Dict, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Classe para gerenciar conexões PostgreSQL
    """
    
    def __init__(self):
        """Inicializa a configuração de conexão"""
        self.config = self._load_config()
        self.connection_pool: Optional[pool.ThreadedConnectionPool] = None
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega configuração do banco de dados
        Prioridade: .env > variáveis de ambiente > valores padrão
        """
        # Valores padrão
        config = {
            "host": "37.27.220.67",
            "port": 5432,
            "database": "meu_banco",
            "user": "meu_usuario",
            "password": "ctcaddTcMARvioDY4kso"
        }
        
        # Tentar carregar do .env se existir
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            logger.warning("python-dotenv não instalado, usando variáveis de ambiente")
        
        # Sobrescrever com variáveis de ambiente
        if os.getenv("DATABASE_URL"):
            # Parse DATABASE_URL: postgresql://user:password@host:port/database
            from urllib.parse import urlparse
            parsed = urlparse(os.getenv("DATABASE_URL"))
            config.update({
                "host": parsed.hostname or config["host"],
                "port": parsed.port or config["port"],
                "database": parsed.path.lstrip('/') or config["database"],
                "user": parsed.username or config["user"],
                "password": parsed.password or config["password"]
            })
        else:
            # Usar variáveis individuais se DATABASE_URL não existir
            config.update({
                "host": os.getenv("DB_HOST", config["host"]),
                "port": int(os.getenv("DB_PORT", config["port"])),
                "database": os.getenv("DB_NAME", config["database"]),
                "user": os.getenv("DB_USER", config["user"]),
                "password": os.getenv("DB_PASSWORD", config["password"])
            })
        
        return config
    
    def get_connection_string(self) -> str:
        """Retorna string de conexão"""
        return (
            f"postgresql://{self.config['user']}:{self.config['password']}"
            f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
        )
    
    def create_connection(self):
        """
        Cria uma nova conexão ao banco de dados
        
        Returns:
            psycopg2.connection: Conexão PostgreSQL
        """
        try:
            conn = psycopg2.connect(
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
                cursor_factory=RealDictCursor
            )
            logger.info(f"✅ Conexão estabelecida com {self.config['host']}/{self.config['database']}")
            return conn
        except psycopg2.OperationalError as e:
            logger.error(f"❌ Erro de conexão: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            raise
    
    def create_connection_pool(self, min_conn: int = 1, max_conn: int = 10):
        """
        Cria pool de conexões
        
        Args:
            min_conn: Número mínimo de conexões
            max_conn: Número máximo de conexões
        """
        try:
            self.connection_pool = pool.ThreadedConnectionPool(
                min_conn,
                max_conn,
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
                cursor_factory=RealDictCursor
            )
            logger.info(f"✅ Pool de conexões criado ({min_conn}-{max_conn} conexões)")
        except Exception as e:
            logger.error(f"❌ Erro ao criar pool: {e}")
            raise
    
    def get_connection_from_pool(self):
        """
        Obtém conexão do pool
        
        Returns:
            psycopg2.connection: Conexão do pool
        """
        if not self.connection_pool:
            self.create_connection_pool()
        
        try:
            return self.connection_pool.getconn()
        except Exception as e:
            logger.error(f"❌ Erro ao obter conexão do pool: {e}")
            raise
    
    def return_connection_to_pool(self, conn):
        """
        Retorna conexão ao pool
        
        Args:
            conn: Conexão a ser retornada
        """
        if self.connection_pool:
            self.connection_pool.putconn(conn)
    
    def close_connection_pool(self):
        """Fecha o pool de conexões"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("✅ Pool de conexões fechado")
    
    @contextmanager
    def get_connection(self, use_pool: bool = False):
        """
        Context manager para conexão (usa com 'with')
        
        Args:
            use_pool: Se True, usa pool de conexões
        
        Yields:
            psycopg2.connection: Conexão PostgreSQL
        """
        if use_pool:
            conn = self.get_connection_from_pool()
            try:
                yield conn
            finally:
                self.return_connection_to_pool(conn)
        else:
            conn = self.create_connection()
            try:
                yield conn
            finally:
                conn.close()
                logger.info("✅ Conexão fechada")
    
    def test_connection(self) -> bool:
        """
        Testa conexão com o banco de dados
        
        Returns:
            bool: True se conexão bem-sucedida
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version(), current_database(), current_user, now();")
                result = cursor.fetchone()
                
                logger.info("✅ Teste de conexão bem-sucedido!")
                logger.info(f"   PostgreSQL: {result['version'][:50]}...")
                logger.info(f"   Database: {result['current_database']}")
                logger.info(f"   User: {result['current_user']}")
                logger.info(f"   Data/Hora: {result['now']}")
                
                cursor.close()
                return True
        except Exception as e:
            logger.error(f"❌ Teste de conexão falhou: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None, use_pool: bool = False) -> list:
        """
        Executa uma query SELECT e retorna resultados
        
        Args:
            query: Query SQL
            params: Parâmetros da query (tupla)
            use_pool: Se True, usa pool de conexões
        
        Returns:
            list: Lista de resultados (dicts)
        """
        try:
            with self.get_connection(use_pool=use_pool) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()
                cursor.close()
                return results
        except Exception as e:
            logger.error(f"❌ Erro ao executar query: {e}")
            raise
    
    def execute_command(self, command: str, params: tuple = None, use_pool: bool = False) -> int:
        """
        Executa um comando (INSERT, UPDATE, DELETE)
        
        Args:
            command: Comando SQL
            params: Parâmetros do comando (tupla)
            use_pool: Se True, usa pool de conexões
        
        Returns:
            int: Número de linhas afetadas
        """
        try:
            with self.get_connection(use_pool=use_pool) as conn:
                cursor = conn.cursor()
                cursor.execute(command, params)
                conn.commit()
                rows_affected = cursor.rowcount
                cursor.close()
                return rows_affected
        except Exception as e:
            logger.error(f"❌ Erro ao executar comando: {e}")
            raise


# Instância global
db = DatabaseConnection()


# Funções de conveniência
def get_db_connection():
    """Retorna uma nova conexão"""
    return db.create_connection()


def test_db_connection():
    """Testa conexão com o banco"""
    return db.test_connection()


if __name__ == "__main__":
    # Teste ao executar diretamente
    print("=" * 60)
    print("🔍 TESTE DE CONEXÃO POSTGRESQL - MARABET AI")
    print("=" * 60)
    print()
    
    print("📋 Configuração:")
    print(f"   Host: {db.config['host']}")
    print(f"   Port: {db.config['port']}")
    print(f"   Database: {db.config['database']}")
    print(f"   User: {db.config['user']}")
    print(f"   Connection String: {db.get_connection_string()}")
    print()
    
    # Testar conexão
    if db.test_connection():
        print("\n✅ Módulo de conexão configurado e funcionando!")
        
        # Exemplo de uso
        print("\n📋 Exemplo de uso:")
        print("""
        from database_connection import db
        
        # Usar context manager
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sua_tabela LIMIT 5")
            results = cursor.fetchall()
            for row in results:
                print(row)
        """)
    else:
        print("\n❌ Erro na conexão. Verifique as credenciais e configurações.")
        sys.exit(1)

