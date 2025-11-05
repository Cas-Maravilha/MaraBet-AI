"""
MaraBet AI - Redis Configuration
Gerenciamento de conexão com ElastiCache Redis
"""

import os
import json
import redis
from typing import Optional, Dict
from urllib.parse import quote_plus


class RedisConfig:
    """Gerenciador de configuração do ElastiCache Redis"""
    
    def __init__(self):
        # Endpoints (obtidos do ElastiCache)
        self.primary_host = os.getenv(
            'REDIS_HOST',
            'marabet-redis.xxxxx.cache.amazonaws.com'
        )
        self.reader_host = os.getenv(
            'REDIS_READER_HOST',
            self.primary_host
        )
        self.port = int(os.getenv('REDIS_PORT', 6379))
        self.password = os.getenv('REDIS_PASSWORD', '')
        self.ssl = os.getenv('REDIS_SSL', 'true').lower() == 'true'
        self.db = int(os.getenv('REDIS_DB', 0))
        
        self._primary_client = None
        self._reader_client = None
    
    def get_connection_url(self, use_reader: bool = False) -> str:
        """
        Gera connection URL para Redis
        
        Args:
            use_reader: Usar endpoint de leitura (read-only)
        
        Returns:
            Redis URL
        """
        host = self.reader_host if use_reader else self.primary_host
        scheme = 'rediss' if self.ssl else 'redis'
        
        if self.password:
            # URL encode da senha
            password_encoded = quote_plus(self.password)
            return f"{scheme}://:{password_encoded}@{host}:{self.port}/{self.db}"
        else:
            return f"{scheme}://{host}:{self.port}/{self.db}"
    
    @property
    def primary_client(self) -> redis.Redis:
        """
        Obtém cliente Redis Primary (Read/Write)
        
        Returns:
            Cliente Redis configurado
        """
        if self._primary_client is None:
            self._primary_client = redis.from_url(
                self.get_connection_url(use_reader=False),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
        return self._primary_client
    
    @property
    def reader_client(self) -> redis.Redis:
        """
        Obtém cliente Redis Reader (Read-Only)
        
        Returns:
            Cliente Redis configurado para leitura
        """
        if self._reader_client is None:
            self._reader_client = redis.from_url(
                self.get_connection_url(use_reader=True),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
        return self._reader_client
    
    def get_client(self, read_only: bool = False) -> redis.Redis:
        """
        Obtém cliente Redis
        
        Args:
            read_only: Se True, usa endpoint reader
        
        Returns:
            Cliente Redis
        """
        return self.reader_client if read_only else self.primary_client
    
    def test_connection(self) -> bool:
        """
        Testa conexão com Redis
        
        Returns:
            True se conectou com sucesso
        """
        try:
            # Testar primary
            response = self.primary_client.ping()
            
            if response:
                print("✅ Conexão Primary bem-sucedida!")
                
                # Informações do servidor
                info = self.primary_client.info('server')
                print(f"   Redis Version: {info['redis_version']}")
                print(f"   OS: {info['os']}")
                print(f"   Uptime: {info['uptime_in_days']} dias")
                
                # Testar comandos básicos
                self.primary_client.set('test_key', 'MaraBet AI')
                value = self.primary_client.get('test_key')
                
                if value == 'MaraBet AI':
                    print("   ✓ SET/GET funcionando")
                
                self.primary_client.delete('test_key')
                
                return True
            
            return False
            
        except redis.ConnectionError as e:
            print(f"❌ Erro de conexão: {e}")
            print("\nVerifique:")
            print("  1. Security Group permite conexão")
            print("  2. Endpoint está correto")
            print("  3. Auth token está correto")
            print("  4. TLS/SSL está habilitado")
            return False
        except redis.AuthenticationError:
            print("❌ Erro de autenticação!")
            print("   Verifique o auth token")
            return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def health_check(self) -> Dict:
        """
        Verifica saúde do Redis
        
        Returns:
            Dict com status e métricas
        """
        try:
            # Ping
            self.primary_client.ping()
            
            # Informações
            info = self.primary_client.info()
            memory_info = self.primary_client.info('memory')
            stats = self.primary_client.info('stats')
            
            return {
                'status': 'healthy',
                'redis_version': info['redis_version'],
                'uptime_days': info['uptime_in_days'],
                'connected_clients': info['connected_clients'],
                'used_memory_human': memory_info['used_memory_human'],
                'used_memory_peak_human': memory_info['used_memory_peak_human'],
                'total_commands_processed': stats['total_commands_processed'],
                'instantaneous_ops_per_sec': stats['instantaneous_ops_per_sec'],
                'keyspace': self.primary_client.dbsize()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def clear_cache(self, pattern: Optional[str] = None):
        """
        Limpa cache
        
        Args:
            pattern: Padrão de chaves para deletar (ex: 'user:*')
                    Se None, limpa todo o database
        """
        if pattern:
            # Deletar por padrão
            keys = self.primary_client.keys(pattern)
            if keys:
                self.primary_client.delete(*keys)
                print(f"✅ {len(keys)} chaves deletadas (padrão: {pattern})")
        else:
            # Limpar tudo
            self.primary_client.flushdb()
            print("✅ Cache limpo completamente")
    
    def get_cache_stats(self) -> Dict:
        """
        Obtém estatísticas do cache
        
        Returns:
            Dict com estatísticas
        """
        info = self.primary_client.info()
        memory = self.primary_client.info('memory')
        
        return {
            'total_keys': self.primary_client.dbsize(),
            'used_memory_mb': round(memory['used_memory'] / 1024 / 1024, 2),
            'hit_rate': round(
                (info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses']) * 100)
                if (info['keyspace_hits'] + info['keyspace_misses']) > 0 else 0,
                2
            ),
            'connected_clients': info['connected_clients'],
            'ops_per_sec': info['instantaneous_ops_per_sec']
        }
    
    def print_info(self):
        """Imprime informações do Redis"""
        print("=" * 70)
        print("💾 MARABET AI - ELASTICACHE REDIS")
        print("=" * 70)
        print()
        print(f"Primary Endpoint:  {self.primary_host}:{self.port}")
        print(f"Reader Endpoint:   {self.reader_host}:{self.port}")
        print(f"Password:          {'*' * len(self.password) if self.password else 'Não configurado'}")
        print(f"SSL/TLS:           {'Habilitado' if self.ssl else 'Desabilitado'}")
        print(f"Database:          {self.db}")
        print()
        print("Connection URL (Primary):")
        print("-" * 70)
        print(self.get_connection_url(use_reader=False))
        print()
        print("Connection URL (Reader):")
        print("-" * 70)
        print(self.get_connection_url(use_reader=True))
        print()
        print("=" * 70)


# Instância global
redis_config = RedisConfig()


# Funções de conveniência
def get_redis_client(read_only: bool = False) -> redis.Redis:
    """Obtém cliente Redis"""
    return redis_config.get_client(read_only)


def get_redis_url(use_reader: bool = False) -> str:
    """Obtém URL de conexão"""
    return redis_config.get_connection_url(use_reader)


def test_redis_connection() -> bool:
    """Testa conexão Redis"""
    return redis_config.test_connection()


def redis_health_check() -> Dict:
    """Health check do Redis"""
    return redis_config.health_check()


if __name__ == "__main__":
    """
    Script executável para testar configuração
    
    Uso:
        python redis_config.py
    """
    import sys
    
    print("🚀 MaraBet AI - Redis Configuration\n")
    
    try:
        # Carregar .env.redis se existir
        if os.path.exists('.env.redis'):
            print("📄 Carregando .env.redis...")
            from dotenv import load_dotenv
            load_dotenv('.env.redis')
            print()
        
        # Mostrar informações
        redis_config.print_info()
        
        # Testar conexão
        print("\n🔌 Testando conexão...")
        print("-" * 70)
        test_redis_connection()
        
        # Health check
        print("\n📊 Health Check...")
        print("-" * 70)
        health = redis_health_check()
        print(json.dumps(health, indent=2))
        
        # Estatísticas
        if health.get('status') == 'healthy':
            print("\n📈 Estatísticas do Cache...")
            print("-" * 70)
            stats = redis_config.get_cache_stats()
            print(f"  Total de Chaves:     {stats['total_keys']}")
            print(f"  Memória Usada:       {stats['used_memory_mb']} MB")
            print(f"  Hit Rate:            {stats['hit_rate']}%")
            print(f"  Clientes Conectados: {stats['connected_clients']}")
            print(f"  Operações/seg:       {stats['ops_per_sec']}")
        
        print("\n" + "=" * 70)
        print("Exemplo de uso:")
        print("-" * 70)
        print("""
from redis_config import get_redis_client

# Obter cliente
redis_client = get_redis_client()

# Usar cache
redis_client.set('key', 'value', ex=3600)  # TTL 1h
value = redis_client.get('key')

# Cache de objetos
import json
redis_client.set('user:1', json.dumps({'name': 'Admin'}))
user = json.loads(redis_client.get('user:1'))
        """)
        print("=" * 70)
        
    except ImportError as e:
        print(f"\n⚠️  Dependência faltando: {e}")
        print("\nInstale:")
        print("  pip install redis python-dotenv")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

