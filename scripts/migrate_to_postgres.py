#!/usr/bin/env python3
"""
Script de migração de SQLite para PostgreSQL
Migra todos os dados existentes do SQLite para PostgreSQL
"""

import os
import sys
import sqlite3
import psycopg2
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SQLiteToPostgreSQLMigrator:
    """Migrador de SQLite para PostgreSQL"""
    
    def __init__(self, sqlite_path: str, postgres_url: str):
        """
        Inicializa o migrador
        
        Args:
            sqlite_path: Caminho para o arquivo SQLite
            postgres_url: URL de conexão do PostgreSQL
        """
        self.sqlite_path = sqlite_path
        self.postgres_url = postgres_url
        self.sqlite_conn = None
        self.postgres_conn = None
        
    def connect_databases(self) -> bool:
        """Conecta aos bancos de dados"""
        try:
            # Conectar ao SQLite
            if not os.path.exists(self.sqlite_path):
                logger.error(f"❌ Arquivo SQLite não encontrado: {self.sqlite_path}")
                return False
            
            self.sqlite_conn = sqlite3.connect(self.sqlite_path)
            logger.info("✅ Conectado ao SQLite")
            
            # Conectar ao PostgreSQL
            self.postgres_conn = psycopg2.connect(self.postgres_url)
            self.postgres_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            logger.info("✅ Conectado ao PostgreSQL")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar aos bancos: {e}")
            return False
    
    def get_sqlite_tables(self) -> list:
        """Obtém lista de tabelas do SQLite"""
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"📋 Tabelas encontradas no SQLite: {tables}")
            return tables
        except Exception as e:
            logger.error(f"❌ Erro ao obter tabelas do SQLite: {e}")
            return []
    
    def get_table_schema(self, table_name: str) -> dict:
        """Obtém schema de uma tabela do SQLite"""
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            schema = {}
            for col in columns:
                col_id, name, col_type, not_null, default_val, pk = col
                schema[name] = {
                    'type': col_type,
                    'not_null': bool(not_null),
                    'default': default_val,
                    'primary_key': bool(pk)
                }
            
            return schema
        except Exception as e:
            logger.error(f"❌ Erro ao obter schema da tabela {table_name}: {e}")
            return {}
    
    def migrate_table(self, table_name: str) -> bool:
        """Migra uma tabela específica"""
        try:
            logger.info(f"🔄 Migrando tabela: {table_name}")
            
            # Verificar se a tabela existe no SQLite
            cursor = self.sqlite_conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            if row_count == 0:
                logger.info(f"⚠️ Tabela {table_name} está vazia, pulando")
                return True
            
            # Ler dados do SQLite
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.sqlite_conn)
            logger.info(f"📊 Lendo {len(df)} registros da tabela {table_name}")
            
            # Preparar dados para PostgreSQL
            df = self.prepare_dataframe_for_postgres(df, table_name)
            
            # Inserir dados no PostgreSQL
            postgres_cursor = self.postgres_conn.cursor()
            
            # Limpar tabela no PostgreSQL (se existir)
            postgres_cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE")
            
            # Inserir dados
            if not df.empty:
                # Converter DataFrame para lista de tuplas
                data_tuples = [tuple(row) for row in df.values]
                
                # Obter nomes das colunas
                columns = list(df.columns)
                columns_str = ', '.join(columns)
                placeholders = ', '.join(['%s'] * len(columns))
                
                # Query de inserção
                insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                
                # Inserir em lotes
                batch_size = 1000
                for i in range(0, len(data_tuples), batch_size):
                    batch = data_tuples[i:i + batch_size]
                    postgres_cursor.executemany(insert_query, batch)
                    logger.info(f"📝 Inseridos {min(i + batch_size, len(data_tuples))}/{len(data_tuples)} registros")
            
            logger.info(f"✅ Tabela {table_name} migrada com sucesso: {len(df)} registros")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao migrar tabela {table_name}: {e}")
            return False
    
    def prepare_dataframe_for_postgres(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Prepara DataFrame para inserção no PostgreSQL"""
        try:
            # Converter tipos de dados
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Converter strings para string Python
                    df[col] = df[col].astype(str)
                elif df[col].dtype == 'int64':
                    # Converter int64 para int Python
                    df[col] = df[col].astype(int)
                elif df[col].dtype == 'float64':
                    # Converter float64 para float Python
                    df[col] = df[col].astype(float)
                elif 'datetime' in str(df[col].dtype):
                    # Converter datetime para string ISO
                    df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Tratar valores NaN
            df = df.fillna(None)
            
            # Tratar valores infinitos
            df = df.replace([float('inf'), float('-inf')], None)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro ao preparar DataFrame: {e}")
            return df
    
    def verify_migration(self, table_name: str) -> bool:
        """Verifica se a migração foi bem-sucedida"""
        try:
            # Contar registros no SQLite
            sqlite_cursor = self.sqlite_conn.cursor()
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            sqlite_count = sqlite_cursor.fetchone()[0]
            
            # Contar registros no PostgreSQL
            postgres_cursor = self.postgres_conn.cursor()
            postgres_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            postgres_count = postgres_cursor.fetchone()[0]
            
            if sqlite_count == postgres_count:
                logger.info(f"✅ Verificação OK - {table_name}: {postgres_count} registros")
                return True
            else:
                logger.error(f"❌ Verificação FALHOU - {table_name}: SQLite={sqlite_count}, PostgreSQL={postgres_count}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na verificação da tabela {table_name}: {e}")
            return False
    
    def migrate_all(self) -> bool:
        """Migra todas as tabelas"""
        try:
            logger.info("🚀 Iniciando migração de SQLite para PostgreSQL")
            
            # Conectar aos bancos
            if not self.connect_databases():
                return False
            
            # Obter lista de tabelas
            tables = self.get_sqlite_tables()
            if not tables:
                logger.error("❌ Nenhuma tabela encontrada no SQLite")
                return False
            
            # Migrar cada tabela
            success_count = 0
            for table in tables:
                if self.migrate_table(table):
                    if self.verify_migration(table):
                        success_count += 1
                    else:
                        logger.error(f"❌ Verificação falhou para tabela {table}")
                else:
                    logger.error(f"❌ Migração falhou para tabela {table}")
            
            logger.info(f"📊 Migração concluída: {success_count}/{len(tables)} tabelas migradas com sucesso")
            
            return success_count == len(tables)
            
        except Exception as e:
            logger.error(f"❌ Erro na migração: {e}")
            return False
        finally:
            # Fechar conexões
            if self.sqlite_conn:
                self.sqlite_conn.close()
            if self.postgres_conn:
                self.postgres_conn.close()
    
    def create_backup(self) -> str:
        """Cria backup do SQLite antes da migração"""
        try:
            backup_path = f"{self.sqlite_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Copiar arquivo
            import shutil
            shutil.copy2(self.sqlite_path, backup_path)
            
            logger.info(f"💾 Backup criado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            return None


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migração de SQLite para PostgreSQL")
    parser.add_argument("--sqlite-path", required=True, help="Caminho para arquivo SQLite")
    parser.add_argument("--postgres-url", required=True, help="URL de conexão do PostgreSQL")
    parser.add_argument("--backup", action="store_true", help="Criar backup antes da migração")
    parser.add_argument("--verify-only", action="store_true", help="Apenas verificar migração")
    
    args = parser.parse_args()
    
    migrator = SQLiteToPostgreSQLMigrator(args.sqlite_path, args.postgres_url)
    
    if args.backup:
        backup_path = migrator.create_backup()
        if not backup_path:
            sys.exit(1)
    
    if args.verify_only:
        # Apenas verificar migração
        if not migrator.connect_databases():
            sys.exit(1)
        
        tables = migrator.get_sqlite_tables()
        all_ok = True
        
        for table in tables:
            if not migrator.verify_migration(table):
                all_ok = False
        
        sys.exit(0 if all_ok else 1)
    else:
        # Executar migração completa
        success = migrator.migrate_all()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
