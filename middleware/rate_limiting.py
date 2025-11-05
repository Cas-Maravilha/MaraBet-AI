#!/usr/bin/env python3
"""
Middleware de Rate Limiting para o MaraBet AI
Implementa rate limiting robusto para proteção contra abuso
"""

import time
import redis
import json
from functools import wraps
from flask import request, jsonify, g
from werkzeug.exceptions import TooManyRequests
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Implementação de rate limiting usando Redis"""
    
    def __init__(self, redis_url='redis://localhost:6379'):
        """Inicializa o rate limiter"""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()  # Testa conexão
            self.connected = True
        except Exception as e:
            logger.warning(f"Redis não disponível: {e}")
            self.redis_client = None
            self.connected = False
    
    def is_allowed(self, key, limit, window):
        """
        Verifica se a requisição é permitida
        
        Args:
            key: Chave única (IP, usuário, etc.)
            limit: Número máximo de requisições
            window: Janela de tempo em segundos
        
        Returns:
            tuple: (is_allowed, remaining, reset_time)
        """
        if not self.connected:
            return True, limit, int(time.time()) + window
        
        try:
            # Usar sliding window counter
            current_time = int(time.time())
            window_start = current_time - window
            
            # Pipeline para operações atômicas
            pipe = self.redis_client.pipeline()
            
            # Remover entradas antigas
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Contar requisições na janela
            pipe.zcard(key)
            
            # Adicionar requisição atual
            pipe.zadd(key, {str(current_time): current_time})
            
            # Definir expiração
            pipe.expire(key, window)
            
            # Executar pipeline
            results = pipe.execute()
            
            current_count = results[1]
            
            if current_count >= limit:
                # Calcular tempo de reset
                oldest_request = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_request:
                    reset_time = int(oldest_request[0][1]) + window
                else:
                    reset_time = current_time + window
                
                return False, 0, reset_time
            else:
                remaining = limit - current_count - 1
                reset_time = current_time + window
                return True, remaining, reset_time
                
        except Exception as e:
            logger.error(f"Erro no rate limiting: {e}")
            return True, limit, int(time.time()) + window
    
    def get_client_ip(self, request):
        """Obtém IP real do cliente"""
        # Verificar headers de proxy
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def get_rate_limit_key(self, request, endpoint=None):
        """Gera chave única para rate limiting"""
        ip = self.get_client_ip(request)
        
        if endpoint:
            return f"rate_limit:{endpoint}:{ip}"
        else:
            return f"rate_limit:global:{ip}"

# Instância global do rate limiter
rate_limiter = RateLimiter()

def rate_limit(limit=100, window=3600, per='ip', endpoint=None):
    """
    Decorator para rate limiting
    
    Args:
        limit: Número máximo de requisições
        window: Janela de tempo em segundos
        per: 'ip' ou 'user'
        endpoint: Nome do endpoint para rate limiting específico
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Gerar chave de rate limiting
            if per == 'ip':
                key = rate_limiter.get_rate_limit_key(request, endpoint)
            else:
                # Implementar rate limiting por usuário se necessário
                key = f"rate_limit:user:{request.remote_addr}"
            
            # Verificar rate limit
            is_allowed, remaining, reset_time = rate_limiter.is_allowed(key, limit, window)
            
            if not is_allowed:
                # Adicionar headers de rate limit
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Muitas requisições. Tente novamente mais tarde.',
                    'retry_after': reset_time - int(time.time())
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(reset_time)
                response.headers['Retry-After'] = str(reset_time - int(time.time()))
                return response
            
            # Adicionar headers de rate limit
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Reset'] = str(reset_time)
            
            return response
        
        return decorated_function
    return decorator

# Configurações de rate limiting por endpoint
RATE_LIMITS = {
    'api.matches': {'limit': 100, 'window': 3600},  # 100 req/hora
    'api.predictions': {'limit': 50, 'window': 3600},  # 50 req/hora
    'api.notifications': {'limit': 20, 'window': 3600},  # 20 req/hora
    'api.status': {'limit': 200, 'window': 3600},  # 200 req/hora
    'api.metrics': {'limit': 30, 'window': 3600},  # 30 req/hora
    'default': {'limit': 1000, 'window': 3600}  # 1000 req/hora
}

def apply_rate_limiting(app):
    """Aplica rate limiting global à aplicação"""
    
    @app.before_request
    def before_request():
        """Middleware de rate limiting global"""
        # Pular rate limiting para health checks
        if request.endpoint in ['health', 'metrics']:
            return
        
        # Obter configuração de rate limit
        endpoint_config = RATE_LIMITS.get(request.endpoint, RATE_LIMITS['default'])
        limit = endpoint_config['limit']
        window = endpoint_config['window']
        
        # Aplicar rate limiting
        key = rate_limiter.get_rate_limit_key(request, request.endpoint)
        is_allowed, remaining, reset_time = rate_limiter.is_allowed(key, limit, window)
        
        if not is_allowed:
            response = jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Muitas requisições. Tente novamente mais tarde.',
                'retry_after': reset_time - int(time.time())
            })
            response.status_code = 429
            response.headers['X-RateLimit-Limit'] = str(limit)
            response.headers['X-RateLimit-Remaining'] = '0'
            response.headers['X-RateLimit-Reset'] = str(reset_time)
            response.headers['Retry-After'] = str(reset_time - int(time.time()))
            return response
        
        # Adicionar informações de rate limit ao contexto
        g.rate_limit_info = {
            'limit': limit,
            'remaining': remaining,
            'reset_time': reset_time
        }
    
    @app.after_request
    def after_request(response):
        """Adiciona headers de rate limit às respostas"""
        if hasattr(g, 'rate_limit_info'):
            response.headers['X-RateLimit-Limit'] = str(g.rate_limit_info['limit'])
            response.headers['X-RateLimit-Remaining'] = str(g.rate_limit_info['remaining'])
            response.headers['X-RateLimit-Reset'] = str(g.rate_limit_info['reset_time'])
        
        return response

# Função para verificar status do rate limiter
def check_rate_limiter_status():
    """Verifica status do rate limiter"""
    if rate_limiter.connected:
        try:
            # Testar conexão Redis
            rate_limiter.redis_client.ping()
            return {
                'status': 'connected',
                'redis_url': rate_limiter.redis_client.connection_pool.connection_kwargs.get('host', 'localhost'),
                'port': rate_limiter.redis_client.connection_pool.connection_kwargs.get('port', 6379)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    else:
        return {
            'status': 'disconnected',
            'message': 'Redis não disponível'
        }

if __name__ == "__main__":
    # Teste do rate limiter
    print("🧪 TESTANDO RATE LIMITER")
    print("=" * 40)
    
    # Verificar status
    status = check_rate_limiter_status()
    print(f"Status: {status['status']}")
    
    if status['status'] == 'connected':
        print("✅ Rate limiter funcionando!")
    else:
        print("⚠️ Rate limiter com problemas")
        print(f"Erro: {status.get('error', 'N/A')}")
