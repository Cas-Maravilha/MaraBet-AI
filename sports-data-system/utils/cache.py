"""
Gerenciador de Cache - Sistema Básico
Sistema de cache simples para otimizar performance
"""

import logging
import json
import time
import os
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class CacheManager:
    """Gerenciador de cache simples"""
    
    def __init__(self, cache_dir: str = "cache", max_size: int = 1000, ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.max_size = max_size
        self.ttl = ttl  # Time to live em segundos
        self.cache = {}
        self.access_times = {}
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Cria diretório de cache se não existir"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _is_expired(self, key: str) -> bool:
        """Verifica se uma chave expirou"""
        if key not in self.access_times:
            return True
        
        access_time = self.access_times[key]
        return time.time() - access_time > self.ttl
    
    def _cleanup_expired(self):
        """Remove itens expirados do cache"""
        expired_keys = [key for key in self.cache.keys() if self._is_expired(key)]
        for key in expired_keys:
            del self.cache[key]
            del self.access_times[key]
        
        if expired_keys:
            logger.debug(f"Removidos {len(expired_keys)} itens expirados do cache")
    
    def _evict_lru(self):
        """Remove item menos usado recentemente"""
        if not self.access_times:
            return
        
        # Encontra a chave com menor tempo de acesso
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[lru_key]
        del self.access_times[lru_key]
        logger.debug(f"Item LRU removido: {lru_key}")
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera item do cache"""
        if key not in self.cache:
            return None
        
        if self._is_expired(key):
            del self.cache[key]
            del self.access_times[key]
            return None
        
        # Atualiza tempo de acesso
        self.access_times[key] = time.time()
        
        logger.debug(f"Cache hit: {key}")
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Armazena item no cache"""
        try:
            # Limpa itens expirados
            self._cleanup_expired()
            
            # Remove item se já existe
            if key in self.cache:
                del self.cache[key]
                del self.access_times[key]
            
            # Verifica limite de tamanho
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            # Armazena item
            self.cache[key] = value
            self.access_times[key] = time.time()
            
            logger.debug(f"Item armazenado no cache: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao armazenar no cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove item do cache"""
        try:
            if key in self.cache:
                del self.cache[key]
                del self.access_times[key]
                logger.debug(f"Item removido do cache: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao remover do cache: {e}")
            return False
    
    def clear(self):
        """Limpa todo o cache"""
        self.cache.clear()
        self.access_times.clear()
        logger.info("Cache limpo")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        current_time = time.time()
        expired_count = sum(1 for key in self.cache.keys() if self._is_expired(key))
        
        return {
            'total_items': len(self.cache),
            'expired_items': expired_count,
            'active_items': len(self.cache) - expired_count,
            'max_size': self.max_size,
            'ttl': self.ttl,
            'hit_rate': 0.0,  # Implementar se necessário
            'memory_usage_mb': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estima uso de memória do cache"""
        try:
            total_size = 0
            for key, value in self.cache.items():
                total_size += len(str(key)) + len(str(value))
            return total_size / (1024 * 1024)  # MB
        except:
            return 0.0
    
    def save_to_disk(self, filename: str = None) -> bool:
        """Salva cache em disco"""
        try:
            if filename is None:
                filename = f"cache_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            filepath = self.cache_dir / filename
            
            cache_data = {
                'cache': self.cache,
                'access_times': self.access_times,
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'max_size': self.max_size,
                    'ttl': self.ttl
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, default=str, indent=2)
            
            logger.info(f"Cache salvo em: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
            return False
    
    def load_from_disk(self, filename: str) -> bool:
        """Carrega cache do disco"""
        try:
            filepath = self.cache_dir / filename
            
            if not filepath.exists():
                logger.warning(f"Arquivo de cache não encontrado: {filepath}")
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            self.cache = cache_data.get('cache', {})
            self.access_times = cache_data.get('access_times', {})
            
            # Limpa itens expirados
            self._cleanup_expired()
            
            logger.info(f"Cache carregado de: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {e}")
            return False
    
    def get_cache_files(self) -> list:
        """Retorna lista de arquivos de cache"""
        try:
            cache_files = []
            for file in self.cache_dir.glob("cache_*.json"):
                cache_files.append({
                    'filename': file.name,
                    'size_mb': file.stat().st_size / (1024 * 1024),
                    'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
            return sorted(cache_files, key=lambda x: x['modified'], reverse=True)
        except Exception as e:
            logger.error(f"Erro ao listar arquivos de cache: {e}")
            return []
    
    def cleanup_old_files(self, days: int = 7) -> int:
        """Remove arquivos de cache antigos"""
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            removed_count = 0
            
            for file in self.cache_dir.glob("cache_*.json"):
                if file.stat().st_mtime < cutoff_time:
                    file.unlink()
                    removed_count += 1
                    logger.debug(f"Arquivo de cache removido: {file.name}")
            
            if removed_count > 0:
                logger.info(f"{removed_count} arquivos de cache antigos removidos")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Erro na limpeza de arquivos: {e}")
            return 0

class APICache:
    """Cache específico para APIs"""
    
    def __init__(self, cache_manager: CacheManager, prefix: str = "api_"):
        self.cache = cache_manager
        self.prefix = prefix
    
    def get_api_data(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """Recupera dados de API do cache"""
        key = self._generate_key(endpoint, params)
        return self.cache.get(key)
    
    def set_api_data(self, endpoint: str, data: Any, params: Dict[str, Any] = None, 
                    ttl: int = 3600) -> bool:
        """Armazena dados de API no cache"""
        key = self._generate_key(endpoint, params)
        return self.cache.set(key, data, ttl)
    
    def _generate_key(self, endpoint: str, params: Dict[str, Any] = None) -> str:
        """Gera chave única para endpoint e parâmetros"""
        if params:
            param_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()))
            return f"{self.prefix}{endpoint}_{param_str}"
        return f"{self.prefix}{endpoint}"
    
    def clear_api_cache(self, endpoint: str = None):
        """Limpa cache de API"""
        if endpoint:
            # Remove apenas itens do endpoint específico
            keys_to_remove = [key for key in self.cache.cache.keys() 
                            if key.startswith(f"{self.prefix}{endpoint}")]
            for key in keys_to_remove:
                self.cache.delete(key)
        else:
            # Remove todos os itens de API
            keys_to_remove = [key for key in self.cache.cache.keys() 
                            if key.startswith(self.prefix)]
            for key in keys_to_remove:
                self.cache.delete(key)

if __name__ == "__main__":
    # Teste do gerenciador de cache
    print("🧪 TESTE DO GERENCIADOR DE CACHE")
    print("=" * 50)
    
    # Cria cache manager
    cache = CacheManager(cache_dir="test_cache", max_size=10, ttl=5)
    
    # Testa operações básicas
    print("1. Testando operações básicas...")
    cache.set("test_key", "test_value")
    value = cache.get("test_key")
    print(f"   Valor armazenado e recuperado: {value}")
    
    # Testa expiração
    print("2. Testando expiração...")
    cache.set("expire_key", "expire_value", ttl=1)
    time.sleep(2)
    expired_value = cache.get("expire_key")
    print(f"   Valor expirado: {expired_value}")
    
    # Testa estatísticas
    print("3. Estatísticas do cache:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Testa limpeza
    print("4. Limpando cache...")
    cache.clear()
    print(f"   Itens após limpeza: {len(cache.cache)}")
    
    print("\n✅ Teste do cache concluído!")
