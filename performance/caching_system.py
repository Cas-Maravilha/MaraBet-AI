#!/usr/bin/env python3
"""
Sistema de Caching Agressivo para o MaraBet AI
Cache Redis com múltiplas estratégias de invalidação
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
import redis
import pickle
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Gerenciador de cache Redis"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Inicializa gerenciador de cache"""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            self.redis_client.ping()  # Testar conexão
            self.connected = True
            logger.info("Conectado ao Redis com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Redis: {e}")
            self.redis_client = None
            self.connected = False
    
    def _serialize(self, data: Any) -> bytes:
        """Serializa dados para cache"""
        try:
            return pickle.dumps(data)
        except Exception as e:
            logger.error(f"Erro na serialização: {e}")
            return json.dumps(data).encode('utf-8')
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserializa dados do cache"""
        try:
            return pickle.loads(data)
        except Exception as e:
            try:
                return json.loads(data.decode('utf-8'))
            except Exception as e2:
                logger.error(f"Erro na deserialização: {e2}")
                return None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Gera chave única para cache"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if not self.connected:
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                return self._deserialize(data)
            return None
        except Exception as e:
            logger.error(f"Erro ao obter cache {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """Define valor no cache"""
        if not self.connected:
            return False
        
        try:
            serialized = self._serialize(value)
            return self.redis_client.setex(key, timeout, serialized)
        except Exception as e:
            logger.error(f"Erro ao definir cache {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        if not self.connected:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Erro ao deletar cache {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Remove valores que correspondem ao padrão"""
        if not self.connected:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Erro ao deletar padrão {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Verifica se chave existe no cache"""
        if not self.connected:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Erro ao verificar existência {key}: {e}")
            return False
    
    def get_or_set(self, key: str, func: Callable, timeout: int = 300, *args, **kwargs) -> Any:
        """Obtém do cache ou executa função e armazena"""
        # Tentar obter do cache
        cached_value = self.get(key)
        if cached_value is not None:
            logger.debug(f"Cache hit: {key}")
            return cached_value
        
        # Executar função e armazenar
        logger.debug(f"Cache miss: {key}")
        value = func(*args, **kwargs)
        self.set(key, value, timeout)
        return value
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalida cache por padrão"""
        return self.delete_pattern(pattern)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        if not self.connected:
            return {"connected": False}
        
        try:
            info = self.redis_client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {"connected": True, "error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calcula taxa de acerto do cache"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0

# Instância global
cache_manager = CacheManager()

def cache_result(timeout: int = 300, key_prefix: str = "default"):
    """Decorator para cache de resultados de função"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave única
            key = cache_manager._generate_key(f"{key_prefix}:{func.__name__}", *args, **kwargs)
            
            # Tentar obter do cache
            cached_result = cache_manager.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit para {func.__name__}")
                return cached_result
            
            # Executar função e armazenar resultado
            logger.debug(f"Cache miss para {func.__name__}")
            result = func(*args, **kwargs)
            cache_manager.set(key, result, timeout)
            return result
        
        return wrapper
    return decorator

def cache_invalidate(pattern: str):
    """Decorator para invalidar cache após operação"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Invalidar cache após operação
            cache_manager.invalidate_by_pattern(pattern)
            logger.debug(f"Cache invalidado: {pattern}")
            return result
        return wrapper
    return decorator

class MatchCache:
    """Cache específico para dados de partidas"""
    
    def __init__(self):
        self.cache_manager = cache_manager
        self.timeouts = {
            'predictions': 300,      # 5 minutos
            'odds': 60,              # 1 minuto
            'statistics': 600,       # 10 minutos
            'lineups': 1800,         # 30 minutos
            'standings': 3600,       # 1 hora
            'fixtures': 1800,        # 30 minutos
        }
    
    def get_match_predictions(self, match_id: str) -> Optional[Dict]:
        """Obtém predições de partida do cache"""
        key = f"match:predictions:{match_id}"
        return self.cache_manager.get(key)
    
    def set_match_predictions(self, match_id: str, predictions: Dict, timeout: int = None) -> bool:
        """Armazena predições de partida no cache"""
        key = f"match:predictions:{match_id}"
        timeout = timeout or self.timeouts['predictions']
        return self.cache_manager.set(key, predictions, timeout)
    
    def get_match_odds(self, match_id: str) -> Optional[Dict]:
        """Obtém odds de partida do cache"""
        key = f"match:odds:{match_id}"
        return self.cache_manager.get(key)
    
    def set_match_odds(self, match_id: str, odds: Dict, timeout: int = None) -> bool:
        """Armazena odds de partida no cache"""
        key = f"match:odds:{match_id}"
        timeout = timeout or self.timeouts['odds']
        return self.cache_manager.set(key, odds, timeout)
    
    def get_league_standings(self, league_id: int) -> Optional[List[Dict]]:
        """Obtém tabela de classificação do cache"""
        key = f"league:standings:{league_id}"
        return self.cache_manager.get(key)
    
    def set_league_standings(self, league_id: int, standings: List[Dict], timeout: int = None) -> bool:
        """Armazena tabela de classificação no cache"""
        key = f"league:standings:{league_id}"
        timeout = timeout or self.timeouts['standings']
        return self.cache_manager.set(key, standings, timeout)
    
    def get_team_statistics(self, team_id: int) -> Optional[Dict]:
        """Obtém estatísticas de time do cache"""
        key = f"team:stats:{team_id}"
        return self.cache_manager.get(key)
    
    def set_team_statistics(self, team_id: int, stats: Dict, timeout: int = None) -> bool:
        """Armazena estatísticas de time no cache"""
        key = f"team:stats:{team_id}"
        timeout = timeout or self.timeouts['statistics']
        return self.cache_manager.set(key, stats, timeout)
    
    def invalidate_match_cache(self, match_id: str):
        """Invalida cache de uma partida específica"""
        patterns = [
            f"match:predictions:{match_id}",
            f"match:odds:{match_id}",
            f"match:stats:{match_id}",
            f"match:lineups:{match_id}"
        ]
        
        for pattern in patterns:
            self.cache_manager.delete(pattern)
        
        logger.info(f"Cache invalidado para partida {match_id}")
    
    def invalidate_league_cache(self, league_id: int):
        """Invalida cache de uma liga específica"""
        patterns = [
            f"league:standings:{league_id}",
            f"league:fixtures:{league_id}",
            f"league:teams:{league_id}"
        ]
        
        for pattern in patterns:
            self.cache_manager.delete_pattern(pattern)
        
        logger.info(f"Cache invalidado para liga {league_id}")

class BusinessCache:
    """Cache específico para métricas de negócio"""
    
    def __init__(self):
        self.cache_manager = cache_manager
        self.timeouts = {
            'roi_analysis': 300,     # 5 minutos
            'win_rate': 300,         # 5 minutos
            'profit_loss': 60,       # 1 minuto
            'trends': 600,           # 10 minutos
            'alerts': 30,            # 30 segundos
        }
    
    def get_roi_analysis(self, period_days: int = 30) -> Optional[Dict]:
        """Obtém análise de ROI do cache"""
        key = f"business:roi_analysis:{period_days}"
        return self.cache_manager.get(key)
    
    def set_roi_analysis(self, period_days: int, analysis: Dict, timeout: int = None) -> bool:
        """Armazena análise de ROI no cache"""
        key = f"business:roi_analysis:{period_days}"
        timeout = timeout or self.timeouts['roi_analysis']
        return self.cache_manager.set(key, analysis, timeout)
    
    def get_win_rate(self, bet_type: str = None) -> Optional[float]:
        """Obtém taxa de acerto do cache"""
        key = f"business:win_rate:{bet_type or 'all'}"
        return self.cache_manager.get(key)
    
    def set_win_rate(self, win_rate: float, bet_type: str = None, timeout: int = None) -> bool:
        """Armazena taxa de acerto no cache"""
        key = f"business:win_rate:{bet_type or 'all'}"
        timeout = timeout or self.timeouts['win_rate']
        return self.cache_manager.set(key, win_rate, timeout)
    
    def invalidate_business_cache(self):
        """Invalida todo o cache de negócio"""
        patterns = [
            "business:roi_analysis:*",
            "business:win_rate:*",
            "business:profit_loss:*",
            "business:trends:*"
        ]
        
        for pattern in patterns:
            self.cache_manager.delete_pattern(pattern)
        
        logger.info("Cache de negócio invalidado")

# Instâncias globais
match_cache = MatchCache()
business_cache = BusinessCache()

# Decorators específicos
def cache_match_predictions(timeout: int = 300):
    """Decorator para cache de predições de partidas"""
    return cache_result(timeout=timeout, key_prefix="match_predictions")

def cache_odds(timeout: int = 60):
    """Decorator para cache de odds"""
    return cache_result(timeout=timeout, key_prefix="odds")

def cache_business_metrics(timeout: int = 300):
    """Decorator para cache de métricas de negócio"""
    return cache_result(timeout=timeout, key_prefix="business")

def invalidate_match_cache(match_id: str):
    """Decorator para invalidar cache de partida"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            match_cache.invalidate_match_cache(match_id)
            return result
        return wrapper
    return decorator

if __name__ == "__main__":
    # Teste do sistema de cache
    print("🧪 TESTANDO SISTEMA DE CACHE")
    print("=" * 40)
    
    # Testar cache básico
    test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
    cache_manager.set("test_key", test_data, 60)
    
    cached_data = cache_manager.get("test_key")
    print(f"Cache básico: {'✅ OK' if cached_data == test_data else '❌ Falha'}")
    
    # Testar decorator
    @cache_result(timeout=60, key_prefix="test")
    def expensive_calculation(n: int) -> int:
        time.sleep(0.1)  # Simular operação custosa
        return n * n
    
    # Primeira chamada (cache miss)
    start_time = time.time()
    result1 = expensive_calculation(5)
    time1 = time.time() - start_time
    
    # Segunda chamada (cache hit)
    start_time = time.time()
    result2 = expensive_calculation(5)
    time2 = time.time() - start_time
    
    print(f"Decorator cache: {'✅ OK' if result1 == result2 and time2 < time1 else '❌ Falha'}")
    print(f"Tempo primeira chamada: {time1:.3f}s")
    print(f"Tempo segunda chamada: {time2:.3f}s")
    
    # Testar cache de partidas
    match_predictions = {
        "match_id": "39_12345",
        "predictions": {
            "home_win": 0.45,
            "draw": 0.30,
            "away_win": 0.25
        },
        "confidence": 0.85
    }
    
    match_cache.set_match_predictions("39_12345", match_predictions)
    cached_predictions = match_cache.get_match_predictions("39_12345")
    
    print(f"Cache de partidas: {'✅ OK' if cached_predictions == match_predictions else '❌ Falha'}")
    
    # Estatísticas
    stats = cache_manager.get_stats()
    print(f"\nEstatísticas do cache:")
    print(f"  Conectado: {stats.get('connected', False)}")
    if stats.get('connected'):
        print(f"  Memória usada: {stats.get('used_memory', 'N/A')}")
        print(f"  Taxa de acerto: {stats.get('hit_rate', 0):.1f}%")
    
    print("\n🎉 TESTES DE CACHE CONCLUÍDOS!")
