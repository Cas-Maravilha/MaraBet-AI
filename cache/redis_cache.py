"""
Sistema de Cache Redis para MaraBet AI
Implementa cache para dados estáticos e de alta frequência
"""

import json
import pickle
import redis
from typing import Any, Optional, Union, List, Dict
from datetime import datetime, timedelta
import logging
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

class RedisCache:
    """
    Classe principal para gerenciamento de cache Redis
    """
    
    def __init__(self, 
                 host: str = 'localhost',
                 port: int = 6379,
                 db: int = 0,
                 password: Optional[str] = None,
                 decode_responses: bool = True,
                 socket_timeout: int = 5,
                 socket_connect_timeout: int = 5,
                 retry_on_timeout: bool = True,
                 max_connections: int = 20):
        """
        Inicializa conexão com Redis
        
        Args:
            host: Endereço do servidor Redis
            port: Porta do servidor Redis
            db: Número do banco de dados Redis
            password: Senha do Redis (opcional)
            decode_responses: Decodificar respostas automaticamente
            socket_timeout: Timeout do socket
            socket_connect_timeout: Timeout de conexão
            retry_on_timeout: Tentar novamente em timeout
            max_connections: Máximo de conexões no pool
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        
        # Pool de conexões para melhor performance
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            retry_on_timeout=retry_on_timeout,
            max_connections=max_connections
        )
        
        self.redis_client = redis.Redis(connection_pool=self.pool)
        
        # Prefixos para diferentes tipos de cache
        self.prefixes = {
            'odds': 'marabet:odds:',
            'stats': 'marabet:stats:',
            'models': 'marabet:models:',
            'predictions': 'marabet:predictions:',
            'leagues': 'marabet:leagues:',
            'teams': 'marabet:teams:',
            'matches': 'marabet:matches:',
            'api': 'marabet:api:',
            'session': 'marabet:session:',
            'temp': 'marabet:temp:'
        }
        
        # Configurações de TTL padrão (em segundos)
        self.default_ttl = {
            'odds': 300,        # 5 minutos
            'stats': 1800,      # 30 minutos
            'models': 3600,     # 1 hora
            'predictions': 600, # 10 minutos
            'leagues': 86400,   # 24 horas
            'teams': 86400,     # 24 horas
            'matches': 3600,    # 1 hora
            'api': 300,         # 5 minutos
            'session': 1800,    # 30 minutos
            'temp': 60          # 1 minuto
        }
    
    def _get_key(self, cache_type: str, key: str) -> str:
        """
        Gera chave completa com prefixo
        
        Args:
            cache_type: Tipo de cache
            key: Chave específica
            
        Returns:
            Chave completa com prefixo
        """
        if cache_type not in self.prefixes:
            raise ValueError(f"Tipo de cache inválido: {cache_type}")
        
        return f"{self.prefixes[cache_type]}{key}"
    
    def _serialize(self, data: Any) -> str:
        """
        Serializa dados para armazenamento
        
        Args:
            data: Dados para serializar
            
        Returns:
            Dados serializados
        """
        try:
            # Tenta JSON primeiro (mais eficiente)
            return json.dumps(data, default=str)
        except (TypeError, ValueError):
            # Fallback para pickle
            return pickle.dumps(data).hex()
    
    def _deserialize(self, data: str) -> Any:
        """
        Deserializa dados do armazenamento
        
        Args:
            data: Dados serializados
            
        Returns:
            Dados deserializados
        """
        try:
            # Tenta JSON primeiro
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            try:
                # Fallback para pickle
                return pickle.loads(bytes.fromhex(data))
            except (pickle.PickleError, ValueError):
                # Se falhar, retorna como string
                return data
    
    def set(self, 
            cache_type: str, 
            key: str, 
            value: Any, 
            ttl: Optional[int] = None) -> bool:
        """
        Armazena valor no cache
        
        Args:
            cache_type: Tipo de cache
            key: Chave específica
            value: Valor para armazenar
            ttl: Time to live em segundos (opcional)
            
        Returns:
            True se armazenado com sucesso
        """
        try:
            full_key = self._get_key(cache_type, key)
            serialized_value = self._serialize(value)
            
            if ttl is None:
                ttl = self.default_ttl.get(cache_type, 300)
            
            result = self.redis_client.setex(full_key, ttl, serialized_value)
            
            if result:
                logger.debug(f"Cache SET: {full_key} (TTL: {ttl}s)")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao armazenar no cache: {e}")
            return False
    
    def get(self, cache_type: str, key: str) -> Optional[Any]:
        """
        Recupera valor do cache
        
        Args:
            cache_type: Tipo de cache
            key: Chave específica
            
        Returns:
            Valor armazenado ou None se não encontrado
        """
        try:
            full_key = self._get_key(cache_type, key)
            data = self.redis_client.get(full_key)
            
            if data is None:
                logger.debug(f"Cache MISS: {full_key}")
                return None
            
            logger.debug(f"Cache HIT: {full_key}")
            return self._deserialize(data)
            
        except Exception as e:
            logger.error(f"Erro ao recuperar do cache: {e}")
            return None
    
    def delete(self, cache_type: str, key: str) -> bool:
        """
        Remove valor do cache
        
        Args:
            cache_type: Tipo de cache
            key: Chave específica
            
        Returns:
            True se removido com sucesso
        """
        try:
            full_key = self._get_key(cache_type, key)
            result = self.redis_client.delete(full_key)
            
            if result:
                logger.debug(f"Cache DELETE: {full_key}")
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Erro ao deletar do cache: {e}")
            return False
    
    def exists(self, cache_type: str, key: str) -> bool:
        """
        Verifica se chave existe no cache
        
        Args:
            cache_type: Tipo de cache
            key: Chave específica
            
        Returns:
            True se chave existe
        """
        try:
            full_key = self._get_key(cache_type, key)
            return bool(self.redis_client.exists(full_key))
            
        except Exception as e:
            logger.error(f"Erro ao verificar existência no cache: {e}")
            return False
    
    def ttl(self, cache_type: str, key: str) -> int:
        """
        Retorna TTL restante da chave
        
        Args:
            cache_type: Tipo de cache
            key: Chave específica
            
        Returns:
            TTL em segundos (-1 se não expira, -2 se não existe)
        """
        try:
            full_key = self._get_key(cache_type, key)
            return self.redis_client.ttl(full_key)
            
        except Exception as e:
            logger.error(f"Erro ao obter TTL do cache: {e}")
            return -2
    
    def extend_ttl(self, cache_type: str, key: str, ttl: int) -> bool:
        """
        Estende TTL de uma chave existente
        
        Args:
            cache_type: Tipo de cache
            key: Chave específica
            ttl: Novo TTL em segundos
            
        Returns:
            True se TTL estendido com sucesso
        """
        try:
            full_key = self._get_key(cache_type, key)
            result = self.redis_client.expire(full_key, ttl)
            
            if result:
                logger.debug(f"Cache TTL EXTENDED: {full_key} (TTL: {ttl}s)")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao estender TTL do cache: {e}")
            return False
    
    def clear_type(self, cache_type: str) -> int:
        """
        Limpa todas as chaves de um tipo específico
        
        Args:
            cache_type: Tipo de cache
            
        Returns:
            Número de chaves removidas
        """
        try:
            pattern = f"{self.prefixes[cache_type]}*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                result = self.redis_client.delete(*keys)
                logger.info(f"Cache CLEAR TYPE: {cache_type} ({result} chaves removidas)")
                return result
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao limpar tipo de cache: {e}")
            return 0
    
    def clear_all(self) -> int:
        """
        Limpa todo o cache do MaraBet
        
        Returns:
            Número de chaves removidas
        """
        try:
            pattern = "marabet:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                result = self.redis_client.delete(*keys)
                logger.info(f"Cache CLEAR ALL: {result} chaves removidas")
                return result
            
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao limpar todo o cache: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            info = self.redis_client.info()
            
            stats = {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'used_memory_peak': info.get('used_memory_peak_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0),
                'redis_version': info.get('redis_version', 'unknown')
            }
            
            # Calcula hit rate
            hits = stats['keyspace_hits']
            misses = stats['keyspace_misses']
            total = hits + misses
            
            if total > 0:
                stats['hit_rate'] = round((hits / total) * 100, 2)
            else:
                stats['hit_rate'] = 0.0
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do cache: {e}")
            return {}


def cache_result(cache_type: str, 
                ttl: Optional[int] = None,
                key_func: Optional[callable] = None):
    """
    Decorator para cache automático de resultados de função
    
    Args:
        cache_type: Tipo de cache
        ttl: Time to live em segundos
        key_func: Função para gerar chave personalizada
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gera chave do cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Gera chave baseada nos argumentos
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Tenta recuperar do cache
            cache = RedisCache()
            cached_result = cache.get(cache_type, cache_key)
            
            if cached_result is not None:
                logger.debug(f"Cache HIT (decorator): {func.__name__}")
                return cached_result
            
            # Executa função e armazena resultado
            result = func(*args, **kwargs)
            cache.set(cache_type, cache_key, result, ttl)
            
            logger.debug(f"Cache SET (decorator): {func.__name__}")
            return result
        
        return wrapper
    return decorator


# Instância global do cache
cache = RedisCache()

# Funções de conveniência
def cache_odds(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Cache específico para odds"""
    return cache.set('odds', key, value, ttl)

def get_odds(key: str) -> Optional[Any]:
    """Recupera odds do cache"""
    return cache.get('odds', key)

def cache_stats(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Cache específico para estatísticas"""
    return cache.set('stats', key, value, ttl)

def get_stats(key: str) -> Optional[Any]:
    """Recupera estatísticas do cache"""
    return cache.get('stats', key)

def cache_predictions(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Cache específico para previsões"""
    return cache.set('predictions', key, value, ttl)

def get_predictions(key: str) -> Optional[Any]:
    """Recupera previsões do cache"""
    return cache.get('predictions', key)
