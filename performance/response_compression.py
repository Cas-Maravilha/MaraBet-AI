#!/usr/bin/env python3
"""
Sistema de Compressão de Respostas para o MaraBet AI
Compressão gzip/brotli para reduzir largura de banda
"""

import gzip
import json
import time
from typing import Any, Dict, List, Optional
from functools import wraps
import logging

try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False
    brotli = None

logger = logging.getLogger(__name__)

class ResponseCompressor:
    """Compressor de respostas HTTP"""
    
    def __init__(self):
        """Inicializa compressor"""
        self.compression_levels = {
            'gzip': 6,      # Nível médio para gzip
            'brotli': 4,    # Nível médio para brotli
            'deflate': 6    # Nível médio para deflate
        }
        
        self.min_size_threshold = 1024  # Mínimo 1KB para comprimir
        self.max_size_threshold = 10 * 1024 * 1024  # Máximo 10MB para comprimir
    
    def compress_gzip(self, data: bytes, level: int = None) -> bytes:
        """Comprime dados usando gzip"""
        level = level or self.compression_levels['gzip']
        return gzip.compress(data, compresslevel=level)
    
    def compress_brotli(self, data: bytes, level: int = None) -> bytes:
        """Comprime dados usando brotli"""
        if not BROTLI_AVAILABLE:
            raise ImportError("Brotli não está disponível")
        
        level = level or self.compression_levels['brotli']
        return brotli.compress(data, quality=level)
    
    def compress_deflate(self, data: bytes, level: int = None) -> bytes:
        """Comprime dados usando deflate"""
        import zlib
        level = level or self.compression_levels['deflate']
        return zlib.compress(data, level)
    
    def should_compress(self, data: bytes, content_type: str = None) -> bool:
        """Determina se dados devem ser comprimidos"""
        # Verificar tamanho
        if len(data) < self.min_size_threshold:
            return False
        
        if len(data) > self.max_size_threshold:
            return False
        
        # Verificar tipo de conteúdo
        if content_type:
            compressible_types = [
                'application/json',
                'application/xml',
                'text/html',
                'text/css',
                'text/javascript',
                'text/plain',
                'application/javascript',
                'application/x-javascript'
            ]
            
            if not any(ct in content_type for ct in compressible_types):
                return False
        
        return True
    
    def get_best_compression(self, data: bytes, accepted_encodings: List[str] = None) -> tuple:
        """Determina a melhor compressão disponível"""
        if not self.should_compress(data):
            return None, data
        
        accepted_encodings = accepted_encodings or ['gzip', 'deflate']
        
        # Testar diferentes compressões
        compressions = {}
        
        if 'gzip' in accepted_encodings:
            try:
                compressed = self.compress_gzip(data)
                compressions['gzip'] = compressed
            except Exception as e:
                logger.warning(f"Erro na compressão gzip: {e}")
        
        if 'br' in accepted_encodings and BROTLI_AVAILABLE:
            try:
                compressed = self.compress_brotli(data)
                compressions['br'] = compressed
            except Exception as e:
                logger.warning(f"Erro na compressão brotli: {e}")
        
        if 'deflate' in accepted_encodings:
            try:
                compressed = self.compress_deflate(data)
                compressions['deflate'] = compressed
            except Exception as e:
                logger.warning(f"Erro na compressão deflate: {e}")
        
        if not compressions:
            return None, data
        
        # Escolher a melhor compressão (menor tamanho)
        best_encoding = min(compressions.keys(), key=lambda k: len(compressions[k]))
        return best_encoding, compressions[best_encoding]
    
    def compress_response(self, data: Any, content_type: str = "application/json", 
                         accepted_encodings: List[str] = None) -> Dict[str, Any]:
        """Comprime resposta completa"""
        # Converter dados para bytes
        if isinstance(data, (dict, list)):
            data_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            data_bytes = str(data).encode('utf-8')
        
        # Verificar se deve comprimir
        if not self.should_compress(data_bytes, content_type):
            return {
                'data': data_bytes,
                'encoding': None,
                'original_size': len(data_bytes),
                'compressed_size': len(data_bytes),
                'compression_ratio': 1.0
            }
        
        # Obter melhor compressão
        encoding, compressed_data = self.get_best_compression(data_bytes, accepted_encodings)
        
        if encoding is None:
            return {
                'data': data_bytes,
                'encoding': None,
                'original_size': len(data_bytes),
                'compressed_size': len(data_bytes),
                'compression_ratio': 1.0
            }
        
        compression_ratio = len(compressed_data) / len(data_bytes)
        
        return {
            'data': compressed_data,
            'encoding': encoding,
            'original_size': len(data_bytes),
            'compressed_size': len(compressed_data),
            'compression_ratio': compression_ratio
        }

class APIResponseOptimizer:
    """Otimizador de respostas de API"""
    
    def __init__(self):
        """Inicializa otimizador"""
        self.compressor = ResponseCompressor()
        self.compression_stats = {
            'total_requests': 0,
            'compressed_requests': 0,
            'total_bytes_saved': 0,
            'avg_compression_ratio': 0.0
        }
    
    def optimize_response(self, data: Any, content_type: str = "application/json",
                         accepted_encodings: List[str] = None) -> Dict[str, Any]:
        """Otimiza resposta de API"""
        start_time = time.time()
        
        # Comprimir resposta
        compressed = self.compressor.compress_response(data, content_type, accepted_encodings)
        
        # Atualizar estatísticas
        self.compression_stats['total_requests'] += 1
        if compressed['encoding']:
            self.compression_stats['compressed_requests'] += 1
            bytes_saved = compressed['original_size'] - compressed['compressed_size']
            self.compression_stats['total_bytes_saved'] += bytes_saved
            
            # Atualizar taxa média de compressão
            total_compressed = self.compression_stats['compressed_requests']
            current_avg = self.compression_stats['avg_compression_ratio']
            new_ratio = compressed['compression_ratio']
            self.compression_stats['avg_compression_ratio'] = (
                (current_avg * (total_compressed - 1) + new_ratio) / total_compressed
            )
        
        processing_time = time.time() - start_time
        
        # Adicionar headers de resposta
        headers = {
            'Content-Type': content_type,
            'X-Processing-Time': f"{processing_time:.3f}s",
            'X-Original-Size': str(compressed['original_size']),
            'X-Compressed-Size': str(compressed['compressed_size']),
            'X-Compression-Ratio': f"{compressed['compression_ratio']:.2f}"
        }
        
        if compressed['encoding']:
            headers['Content-Encoding'] = compressed['encoding']
            headers['Vary'] = 'Accept-Encoding'
        
        return {
            'data': compressed['data'],
            'headers': headers,
            'encoding': compressed['encoding'],
            'stats': {
                'original_size': compressed['original_size'],
                'compressed_size': compressed['compressed_size'],
                'compression_ratio': compressed['compression_ratio'],
                'processing_time': processing_time
            }
        }
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de compressão"""
        stats = self.compression_stats.copy()
        
        if stats['total_requests'] > 0:
            stats['compression_rate'] = stats['compressed_requests'] / stats['total_requests']
            stats['avg_bytes_saved'] = stats['total_bytes_saved'] / stats['compressed_requests'] if stats['compressed_requests'] > 0 else 0
        else:
            stats['compression_rate'] = 0.0
            stats['avg_bytes_saved'] = 0
        
        return stats

# Decorators para compressão automática
def compress_response(content_type: str = "application/json"):
    """Decorator para compressão automática de respostas"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Executar função original
            result = func(*args, **kwargs)
            
            # Se resultado for dicionário com 'data', otimizar
            if isinstance(result, dict) and 'data' in result:
                optimizer = APIResponseOptimizer()
                optimized = optimizer.optimize_response(
                    result['data'], 
                    content_type,
                    result.get('accepted_encodings')
                )
                
                # Combinar com resultado original
                result.update(optimized)
            
            return result
        return wrapper
    return decorator

def auto_compress(min_size: int = 1024):
    """Decorator para compressão automática baseada em tamanho"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Verificar se resultado é grande o suficiente
            if isinstance(result, (dict, list)):
                data_str = json.dumps(result, ensure_ascii=False)
                if len(data_str.encode('utf-8')) >= min_size:
                    optimizer = APIResponseOptimizer()
                    optimized = optimizer.optimize_response(result)
                    return optimized
            
            return result
        return wrapper
    return decorator

# Instância global
response_optimizer = APIResponseOptimizer()

if __name__ == "__main__":
    # Teste do sistema de compressão
    print("🧪 TESTANDO SISTEMA DE COMPRESSÃO")
    print("=" * 40)
    
    # Dados de teste
    test_data = {
        "matches": [
            {
                "id": f"match_{i}",
                "home_team": f"Team {i}A",
                "away_team": f"Team {i}B",
                "predictions": {
                    "home_win": 0.45,
                    "draw": 0.30,
                    "away_win": 0.25
                },
                "odds": {
                    "home_win": 2.20,
                    "draw": 3.40,
                    "away_win": 3.10
                }
            } for i in range(100)  # 100 partidas para teste
        ],
        "metadata": {
            "total": 100,
            "page": 1,
            "per_page": 100
        }
    }
    
    # Testar compressão
    optimizer = APIResponseOptimizer()
    result = optimizer.optimize_response(test_data, "application/json", ["gzip", "deflate"])
    
    print(f"Dados originais: {result['stats']['original_size']} bytes")
    print(f"Dados comprimidos: {result['stats']['compressed_size']} bytes")
    print(f"Taxa de compressão: {result['stats']['compression_ratio']:.2f}")
    print(f"Tempo de processamento: {result['stats']['processing_time']:.3f}s")
    print(f"Encoding usado: {result['encoding'] or 'Nenhum'}")
    
    # Testar com dados pequenos (não deve comprimir)
    small_data = {"message": "Hello World"}
    small_result = optimizer.optimize_response(small_data)
    
    print(f"\nDados pequenos:")
    print(f"  Tamanho: {small_result['stats']['original_size']} bytes")
    print(f"  Comprimido: {small_result['encoding'] or 'Não'}")
    
    # Estatísticas gerais
    stats = optimizer.get_compression_stats()
    print(f"\nEstatísticas de Compressão:")
    print(f"  Total de requisições: {stats['total_requests']}")
    print(f"  Taxa de compressão: {stats['compression_rate']:.1%}")
    print(f"  Bytes economizados: {stats['total_bytes_saved']}")
    print(f"  Taxa média: {stats['avg_compression_ratio']:.2f}")
    
    print("\n🎉 TESTES DE COMPRESSÃO CONCLUÍDOS!")
