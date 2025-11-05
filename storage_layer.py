"""
CAMADA DE ARMAZENAMENTO - MaraBet AI
Sistema modular para armazenamento de dados (PostgreSQL, Redis, MongoDB)
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import sqlite3
import redis
from pymongo import MongoClient
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Configuração do banco de dados"""
    host: str
    port: int
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None

@dataclass
class StorageRecord:
    """Registro de armazenamento"""
    id: str
    data_type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]
    ttl: Optional[int] = None  # Time to live in seconds

class DatabaseInterface(ABC):
    """Interface abstrata para bancos de dados"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Conecta ao banco de dados"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Desconecta do banco de dados"""
        pass
    
    @abstractmethod
    def insert(self, record: StorageRecord) -> bool:
        """Insere um registro"""
        pass
    
    @abstractmethod
    def get(self, record_id: str) -> Optional[StorageRecord]:
        """Recupera um registro"""
        pass
    
    @abstractmethod
    def query(self, query: Dict[str, Any]) -> List[StorageRecord]:
        """Executa uma consulta"""
        pass
    
    @abstractmethod
    def delete(self, record_id: str) -> bool:
        """Remove um registro"""
        pass

class PostgreSQLStorage(DatabaseInterface):
    """Armazenamento PostgreSQL"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = None
        self._create_tables()
    
    def connect(self) -> bool:
        """Conecta ao PostgreSQL"""
        try:
            # Simula conexão (em produção, usaria psycopg2)
            self.connection = sqlite3.connect(':memory:')  # Simulação com SQLite
            logger.info("Conectado ao PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"Erro na conexão PostgreSQL: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do PostgreSQL"""
        if self.connection:
            self.connection.close()
            logger.info("Desconectado do PostgreSQL")
    
    def _create_tables(self):
        """Cria tabelas necessárias"""
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS storage_records (
                    id TEXT PRIMARY KEY,
                    data_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    ttl INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.connection.commit()
    
    def insert(self, record: StorageRecord) -> bool:
        """Insere um registro no PostgreSQL"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO storage_records 
                (id, data_type, data, timestamp, source, metadata, ttl)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.id,
                record.data_type,
                json.dumps(record.data),
                record.timestamp.isoformat(),
                record.source,
                json.dumps(record.metadata),
                record.ttl
            ))
            self.connection.commit()
            logger.info(f"Registro {record.id} inserido no PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"Erro ao inserir no PostgreSQL: {e}")
            return False
    
    def get(self, record_id: str) -> Optional[StorageRecord]:
        """Recupera um registro do PostgreSQL"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT id, data_type, data, timestamp, source, metadata, ttl
                FROM storage_records WHERE id = ?
            ''', (record_id,))
            row = cursor.fetchone()
            
            if row:
                return StorageRecord(
                    id=row[0],
                    data_type=row[1],
                    data=json.loads(row[2]),
                    timestamp=datetime.fromisoformat(row[3]),
                    source=row[4],
                    metadata=json.loads(row[5]),
                    ttl=row[6]
                )
            return None
        except Exception as e:
            logger.error(f"Erro ao recuperar do PostgreSQL: {e}")
            return None
    
    def query(self, query: Dict[str, Any]) -> List[StorageRecord]:
        """Executa consulta no PostgreSQL"""
        try:
            cursor = self.connection.cursor()
            where_clauses = []
            params = []
            
            if 'data_type' in query:
                where_clauses.append('data_type = ?')
                params.append(query['data_type'])
            
            if 'source' in query:
                where_clauses.append('source = ?')
                params.append(query['source'])
            
            if 'start_date' in query:
                where_clauses.append('timestamp >= ?')
                params.append(query['start_date'])
            
            if 'end_date' in query:
                where_clauses.append('timestamp <= ?')
                params.append(query['end_date'])
            
            where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'
            sql = f'SELECT id, data_type, data, timestamp, source, metadata, ttl FROM storage_records WHERE {where_sql}'
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            records = []
            for row in rows:
                records.append(StorageRecord(
                    id=row[0],
                    data_type=row[1],
                    data=json.loads(row[2]),
                    timestamp=datetime.fromisoformat(row[3]),
                    source=row[4],
                    metadata=json.loads(row[5]),
                    ttl=row[6]
                ))
            
            return records
        except Exception as e:
            logger.error(f"Erro na consulta PostgreSQL: {e}")
            return []
    
    def delete(self, record_id: str) -> bool:
        """Remove um registro do PostgreSQL"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM storage_records WHERE id = ?', (record_id,))
            self.connection.commit()
            logger.info(f"Registro {record_id} removido do PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover do PostgreSQL: {e}")
            return False

class RedisStorage(DatabaseInterface):
    """Armazenamento Redis"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.redis_client = None
    
    def connect(self) -> bool:
        """Conecta ao Redis"""
        try:
            # Simula conexão (em produção, usaria redis-py)
            self.redis_client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                db=0,
                decode_responses=True
            )
            logger.info("Conectado ao Redis")
            return True
        except Exception as e:
            logger.error(f"Erro na conexão Redis: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do Redis"""
        if self.redis_client:
            self.redis_client.close()
            logger.info("Desconectado do Redis")
    
    def insert(self, record: StorageRecord) -> bool:
        """Insere um registro no Redis"""
        try:
            key = f"{record.data_type}:{record.id}"
            value = json.dumps({
                'data': record.data,
                'timestamp': record.timestamp.isoformat(),
                'source': record.source,
                'metadata': record.metadata
            })
            
            if record.ttl:
                self.redis_client.setex(key, record.ttl, value)
            else:
                self.redis_client.set(key, value)
            
            logger.info(f"Registro {record.id} inserido no Redis")
            return True
        except Exception as e:
            logger.error(f"Erro ao inserir no Redis: {e}")
            return False
    
    def get(self, record_id: str) -> Optional[StorageRecord]:
        """Recupera um registro do Redis"""
        try:
            # Tenta encontrar em qualquer data_type
            for data_type in ['matches', 'odds', 'statistics', 'h2h', 'news']:
                key = f"{data_type}:{record_id}"
                value = self.redis_client.get(key)
                if value:
                    data = json.loads(value)
                    return StorageRecord(
                        id=record_id,
                        data_type=data_type,
                        data=data['data'],
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        source=data['source'],
                        metadata=data['metadata']
                    )
            return None
        except Exception as e:
            logger.error(f"Erro ao recuperar do Redis: {e}")
            return None
    
    def query(self, query: Dict[str, Any]) -> List[StorageRecord]:
        """Executa consulta no Redis"""
        try:
            records = []
            data_type = query.get('data_type', '*')
            
            if data_type == '*':
                pattern = "*:*"
            else:
                pattern = f"{data_type}:*"
            
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                value = self.redis_client.get(key)
                if value:
                    data = json.loads(value)
                    record_id = key.split(':')[1]
                    
                    # Aplica filtros
                    if 'source' in query and data['source'] != query['source']:
                        continue
                    
                    records.append(StorageRecord(
                        id=record_id,
                        data_type=key.split(':')[0],
                        data=data['data'],
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        source=data['source'],
                        metadata=data['metadata']
                    ))
            
            return records
        except Exception as e:
            logger.error(f"Erro na consulta Redis: {e}")
            return []
    
    def delete(self, record_id: str) -> bool:
        """Remove um registro do Redis"""
        try:
            # Remove de todos os data_types
            for data_type in ['matches', 'odds', 'statistics', 'h2h', 'news']:
                key = f"{data_type}:{record_id}"
                self.redis_client.delete(key)
            
            logger.info(f"Registro {record_id} removido do Redis")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover do Redis: {e}")
            return False

class MongoDBStorage(DatabaseInterface):
    """Armazenamento MongoDB"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.client = None
        self.database = None
    
    def connect(self) -> bool:
        """Conecta ao MongoDB"""
        try:
            # Simula conexão (em produção, usaria pymongo)
            self.client = MongoClient(self.config.connection_string or f"mongodb://{self.config.host}:{self.config.port}")
            self.database = self.client[self.config.database]
            logger.info("Conectado ao MongoDB")
            return True
        except Exception as e:
            logger.error(f"Erro na conexão MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Desconectado do MongoDB")
    
    def insert(self, record: StorageRecord) -> bool:
        """Insere um registro no MongoDB"""
        try:
            collection = self.database[record.data_type]
            document = {
                '_id': record.id,
                'data': record.data,
                'timestamp': record.timestamp,
                'source': record.source,
                'metadata': record.metadata,
                'created_at': datetime.now()
            }
            
            if record.ttl:
                document['expires_at'] = datetime.now() + timedelta(seconds=record.ttl)
            
            collection.insert_one(document)
            logger.info(f"Registro {record.id} inserido no MongoDB")
            return True
        except Exception as e:
            logger.error(f"Erro ao inserir no MongoDB: {e}")
            return False
    
    def get(self, record_id: str) -> Optional[StorageRecord]:
        """Recupera um registro do MongoDB"""
        try:
            # Tenta encontrar em qualquer coleção
            for data_type in ['matches', 'odds', 'statistics', 'h2h', 'news']:
                collection = self.database[data_type]
                document = collection.find_one({'_id': record_id})
                if document:
                    return StorageRecord(
                        id=document['_id'],
                        data_type=data_type,
                        data=document['data'],
                        timestamp=document['timestamp'],
                        source=document['source'],
                        metadata=document['metadata']
                    )
            return None
        except Exception as e:
            logger.error(f"Erro ao recuperar do MongoDB: {e}")
            return None
    
    def query(self, query: Dict[str, Any]) -> List[StorageRecord]:
        """Executa consulta no MongoDB"""
        try:
            records = []
            data_type = query.get('data_type', 'matches')
            collection = self.database[data_type]
            
            mongo_query = {}
            if 'source' in query:
                mongo_query['source'] = query['source']
            if 'start_date' in query:
                mongo_query['timestamp'] = {'$gte': query['start_date']}
            if 'end_date' in query:
                if 'timestamp' in mongo_query:
                    mongo_query['timestamp']['$lte'] = query['end_date']
                else:
                    mongo_query['timestamp'] = {'$lte': query['end_date']}
            
            documents = collection.find(mongo_query)
            
            for document in documents:
                records.append(StorageRecord(
                    id=document['_id'],
                    data_type=data_type,
                    data=document['data'],
                    timestamp=document['timestamp'],
                    source=document['source'],
                    metadata=document['metadata']
                ))
            
            return records
        except Exception as e:
            logger.error(f"Erro na consulta MongoDB: {e}")
            return []
    
    def delete(self, record_id: str) -> bool:
        """Remove um registro do MongoDB"""
        try:
            # Remove de todas as coleções
            for data_type in ['matches', 'odds', 'statistics', 'h2h', 'news']:
                collection = self.database[data_type]
                collection.delete_one({'_id': record_id})
            
            logger.info(f"Registro {record_id} removido do MongoDB")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover do MongoDB: {e}")
            return False

class StorageManager:
    """Gerenciador da camada de armazenamento"""
    
    def __init__(self):
        self.storages: Dict[str, DatabaseInterface] = {}
        self.default_storage = None
    
    def add_storage(self, name: str, storage: DatabaseInterface):
        """Adiciona um armazenamento"""
        self.storages[name] = storage
        if not self.default_storage:
            self.default_storage = name
        logger.info(f"Armazenamento {name} adicionado")
    
    def connect_all(self) -> bool:
        """Conecta a todos os armazenamentos"""
        success = True
        for name, storage in self.storages.items():
            if not storage.connect():
                success = False
                logger.error(f"Falha na conexão com {name}")
        return success
    
    def disconnect_all(self):
        """Desconecta de todos os armazenamentos"""
        for storage in self.storages.values():
            storage.disconnect()
    
    def store_data(self, record: StorageRecord, storage_name: Optional[str] = None) -> bool:
        """Armazena dados"""
        storage = self.storages.get(storage_name or self.default_storage)
        if not storage:
            logger.error(f"Armazenamento {storage_name or self.default_storage} não encontrado")
            return False
        
        return storage.insert(record)
    
    def retrieve_data(self, record_id: str, storage_name: Optional[str] = None) -> Optional[StorageRecord]:
        """Recupera dados"""
        storage = self.storages.get(storage_name or self.default_storage)
        if not storage:
            logger.error(f"Armazenamento {storage_name or self.default_storage} não encontrado")
            return None
        
        return storage.get(record_id)
    
    def query_data(self, query: Dict[str, Any], storage_name: Optional[str] = None) -> List[StorageRecord]:
        """Consulta dados"""
        storage = self.storages.get(storage_name or self.default_storage)
        if not storage:
            logger.error(f"Armazenamento {storage_name or self.default_storage} não encontrado")
            return []
        
        return storage.query(query)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos armazenamentos"""
        stats = {}
        for name, storage in self.storages.items():
            try:
                # Simula estatísticas (em produção, implementaria métodos específicos)
                stats[name] = {
                    'status': 'connected',
                    'type': type(storage).__name__,
                    'records_count': 0  # Implementar contagem real
                }
            except Exception as e:
                stats[name] = {
                    'status': 'error',
                    'error': str(e)
                }
        return stats

if __name__ == "__main__":
    # Teste da camada de armazenamento
    manager = StorageManager()
    
    # Configurações
    postgres_config = DatabaseConfig(
        host="localhost",
        port=5432,
        database="marabet_ai",
        username="user",
        password="password"
    )
    
    redis_config = DatabaseConfig(
        host="localhost",
        port=6379,
        database="marabet_ai"
    )
    
    mongo_config = DatabaseConfig(
        host="localhost",
        port=27017,
        database="marabet_ai"
    )
    
    # Adiciona armazenamentos
    postgres_storage = PostgreSQLStorage(postgres_config)
    redis_storage = RedisStorage(redis_config)
    mongo_storage = MongoDBStorage(mongo_config)
    
    manager.add_storage("postgresql", postgres_storage)
    manager.add_storage("redis", redis_storage)
    manager.add_storage("mongodb", mongo_storage)
    
    # Conecta
    if manager.connect_all():
        print("Todos os armazenamentos conectados")
        
        # Testa inserção
        record = StorageRecord(
            id="test_001",
            data_type="matches",
            data={"home_team": "Manchester City", "away_team": "Arsenal"},
            timestamp=datetime.now(),
            source="api_football",
            metadata={"quality": 0.95}
        )
        
        manager.store_data(record, "postgresql")
        manager.store_data(record, "redis")
        manager.store_data(record, "mongodb")
        
        # Testa recuperação
        retrieved = manager.retrieve_data("test_001", "postgresql")
        if retrieved:
            print(f"Dados recuperados: {retrieved.data}")
        
        # Estatísticas
        stats = manager.get_storage_stats()
        print(f"Estatísticas: {stats}")
        
        manager.disconnect_all()
    
    print("Teste da camada de armazenamento concluído!")
