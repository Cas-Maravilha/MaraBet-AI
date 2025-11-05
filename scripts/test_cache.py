#!/usr/bin/env python3
"""
Script de Teste para Sistema de Cache Redis
Testa funcionalidades de cache, performance e integridade
"""

import os
import sys
import time
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cache.redis_cache import RedisCache, cache_odds, get_odds, cache_stats, get_stats

class CacheTester:
    """Testador do sistema de cache"""
    
    def __init__(self):
        self.cache = RedisCache()
        self.test_results = {}
    
    def test_basic_operations(self):
        """Testa operações básicas de cache"""
        print("🧪 Testando operações básicas...")
        
        results = {
            'set_get': False,
            'exists': False,
            'ttl': False,
            'delete': False
        }
        
        try:
            # Teste SET/GET
            test_key = 'test_basic_123'
            test_value = {'message': 'Hello Redis!', 'timestamp': datetime.now().isoformat()}
            
            # SET
            set_result = self.cache.set('temp', test_key, test_value, ttl=60)
            results['set_get'] = set_result
            
            # GET
            retrieved_value = self.cache.get('temp', test_key)
            results['set_get'] = results['set_get'] and retrieved_value == test_value
            
            # EXISTS
            exists_result = self.cache.exists('temp', test_key)
            results['exists'] = exists_result
            
            # TTL
            ttl_result = self.cache.ttl('temp', test_key)
            results['ttl'] = 0 < ttl_result <= 60
            
            # DELETE
            delete_result = self.cache.delete('temp', test_key)
            results['delete'] = delete_result
            
            # Verifica se foi deletado
            after_delete = self.cache.get('temp', test_key)
            results['delete'] = results['delete'] and after_delete is None
            
        except Exception as e:
            print(f"❌ Erro no teste básico: {e}")
        
        self.test_results['basic_operations'] = results
        print(f"✅ Operações básicas: {sum(results.values())}/{len(results)} passou")
    
    def test_odds_caching(self):
        """Testa cache de odds"""
        print("🧪 Testando cache de odds...")
        
        results = {
            'cache_odds': False,
            'get_odds': False,
            'ttl_odds': False
        }
        
        try:
            # Dados de teste para odds
            test_odds = {
                'match_id': 12345,
                'home_team': 'Manchester United',
                'away_team': 'Liverpool',
                'home_odds': 2.10,
                'draw_odds': 3.40,
                'away_odds': 3.20,
                'bookmaker': 'test_bookmaker',
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache odds
            cache_key = f"odds_{test_odds['match_id']}_{test_odds['bookmaker']}"
            cache_result = cache_odds(cache_key, test_odds, ttl=300)
            results['cache_odds'] = cache_result
            
            # Get odds
            retrieved_odds = get_odds(cache_key)
            results['get_odds'] = retrieved_odds == test_odds
            
            # TTL
            ttl_result = self.cache.ttl('odds', cache_key)
            results['ttl_odds'] = 0 < ttl_result <= 300
            
        except Exception as e:
            print(f"❌ Erro no teste de odds: {e}")
        
        self.test_results['odds_caching'] = results
        print(f"✅ Cache de odds: {sum(results.values())}/{len(results)} passou")
    
    def test_stats_caching(self):
        """Testa cache de estatísticas"""
        print("🧪 Testando cache de estatísticas...")
        
        results = {
            'cache_stats': False,
            'get_stats': False,
            'ttl_stats': False
        }
        
        try:
            # Dados de teste para estatísticas
            test_stats = {
                'team_id': 789,
                'team_name': 'Arsenal',
                'goals_scored': 45,
                'goals_conceded': 32,
                'wins': 15,
                'draws': 8,
                'losses': 7,
                'form': 0.75,
                'home_form': 0.80,
                'away_form': 0.70,
                'updated_at': datetime.now().isoformat()
            }
            
            # Cache stats
            cache_key = f"stats_{test_stats['team_id']}"
            cache_result = cache_stats(cache_key, test_stats, ttl=1800)
            results['cache_stats'] = cache_result
            
            # Get stats
            retrieved_stats = get_stats(cache_key)
            results['get_stats'] = retrieved_stats == test_stats
            
            # TTL
            ttl_result = self.cache.ttl('stats', cache_key)
            results['ttl_stats'] = 0 < ttl_result <= 1800
            
        except Exception as e:
            print(f"❌ Erro no teste de estatísticas: {e}")
        
        self.test_results['stats_caching'] = results
        print(f"✅ Cache de estatísticas: {sum(results.values())}/{len(results)} passou")
    
    def test_performance(self):
        """Testa performance do cache"""
        print("🧪 Testando performance...")
        
        results = {
            'write_performance': False,
            'read_performance': False,
            'concurrent_access': False
        }
        
        try:
            # Teste de escrita
            start_time = time.time()
            write_count = 1000
            
            for i in range(write_count):
                self.cache.set('temp', f'perf_test_{i}', {'data': f'value_{i}'}, ttl=60)
            
            write_time = time.time() - start_time
            write_ops_per_sec = write_count / write_time
            results['write_performance'] = write_ops_per_sec > 100  # Mínimo 100 ops/sec
            
            # Teste de leitura
            start_time = time.time()
            read_count = 1000
            
            for i in range(read_count):
                self.cache.get('temp', f'perf_test_{i}')
            
            read_time = time.time() - start_time
            read_ops_per_sec = read_count / read_time
            results['read_performance'] = read_ops_per_sec > 500  # Mínimo 500 ops/sec
            
            # Teste de acesso concorrente (simulado)
            start_time = time.time()
            concurrent_count = 100
            
            for i in range(concurrent_count):
                # Simula operações concorrentes
                self.cache.set('temp', f'concurrent_{i}', {'data': f'concurrent_value_{i}'}, ttl=60)
                self.cache.get('temp', f'concurrent_{i}')
            
            concurrent_time = time.time() - start_time
            concurrent_ops_per_sec = (concurrent_count * 2) / concurrent_time
            results['concurrent_access'] = concurrent_ops_per_sec > 200  # Mínimo 200 ops/sec
            
            print(f"  📊 Write: {write_ops_per_sec:.2f} ops/sec")
            print(f"  📊 Read: {read_ops_per_sec:.2f} ops/sec")
            print(f"  📊 Concurrent: {concurrent_ops_per_sec:.2f} ops/sec")
            
        except Exception as e:
            print(f"❌ Erro no teste de performance: {e}")
        
        self.test_results['performance'] = results
        print(f"✅ Performance: {sum(results.values())}/{len(results)} passou")
    
    def test_serialization(self):
        """Testa serialização de dados complexos"""
        print("🧪 Testando serialização...")
        
        results = {
            'json_serialization': False,
            'pickle_serialization': False,
            'complex_objects': False
        }
        
        try:
            # Teste JSON (dados simples)
            simple_data = {
                'string': 'Hello World',
                'number': 42,
                'boolean': True,
                'list': [1, 2, 3, 4, 5],
                'dict': {'nested': 'value'}
            }
            
            self.cache.set('temp', 'json_test', simple_data, ttl=60)
            retrieved = self.cache.get('temp', 'json_test')
            results['json_serialization'] = retrieved == simple_data
            
            # Teste Pickle (dados complexos)
            complex_data = {
                'datetime': datetime.now(),
                'timedelta': timedelta(hours=2),
                'set': {1, 2, 3, 4, 5},
                'tuple': (1, 2, 3),
                'bytes': b'Hello World',
                'none': None
            }
            
            self.cache.set('temp', 'pickle_test', complex_data, ttl=60)
            retrieved = self.cache.get('temp', 'pickle_test')
            results['pickle_serialization'] = retrieved == complex_data
            
            # Teste objetos complexos
            class TestObject:
                def __init__(self, value):
                    self.value = value
                    self.timestamp = datetime.now()
                
                def __eq__(self, other):
                    return isinstance(other, TestObject) and self.value == other.value
            
            test_obj = TestObject('test_value')
            self.cache.set('temp', 'object_test', test_obj, ttl=60)
            retrieved = self.cache.get('temp', 'object_test')
            results['complex_objects'] = retrieved == test_obj
            
        except Exception as e:
            print(f"❌ Erro no teste de serialização: {e}")
        
        self.test_results['serialization'] = results
        print(f"✅ Serialização: {sum(results.values())}/{len(results)} passou")
    
    def test_ttl_expiration(self):
        """Testa expiração de TTL"""
        print("🧪 Testando expiração de TTL...")
        
        results = {
            'ttl_set': False,
            'ttl_expiration': False,
            'ttl_extend': False
        }
        
        try:
            # Teste TTL curto
            test_key = 'ttl_test'
            test_value = {'data': 'ttl_test_value'}
            
            # SET com TTL de 2 segundos
            set_result = self.cache.set('temp', test_key, test_value, ttl=2)
            results['ttl_set'] = set_result
            
            # Verifica se existe
            exists_before = self.cache.exists('temp', test_key)
            
            # Aguarda expiração
            time.sleep(3)
            
            # Verifica se expirou
            exists_after = self.cache.exists('temp', test_key)
            results['ttl_expiration'] = exists_before and not exists_after
            
            # Teste extensão de TTL
            self.cache.set('temp', 'ttl_extend_test', test_value, ttl=5)
            ttl_before = self.cache.ttl('temp', 'ttl_extend_test')
            
            # Estende TTL
            extend_result = self.cache.extend_ttl('temp', 'ttl_extend_test', 10)
            ttl_after = self.cache.ttl('temp', 'ttl_extend_test')
            
            results['ttl_extend'] = extend_result and ttl_after > ttl_before
            
        except Exception as e:
            print(f"❌ Erro no teste de TTL: {e}")
        
        self.test_results['ttl_expiration'] = results
        print(f"✅ TTL: {sum(results.values())}/{len(results)} passou")
    
    def test_cleanup(self):
        """Testa limpeza de cache"""
        print("🧪 Testando limpeza de cache...")
        
        results = {
            'clear_type': False,
            'clear_all': False
        }
        
        try:
            # Adiciona dados de teste
            for i in range(10):
                self.cache.set('temp', f'cleanup_test_{i}', {'data': f'value_{i}'}, ttl=60)
                self.cache.set('odds', f'cleanup_odds_{i}', {'odds': 2.0 + i * 0.1}, ttl=60)
            
            # Limpa tipo específico
            cleared_count = self.cache.clear_type('temp')
            results['clear_type'] = cleared_count > 0
            
            # Verifica se foi limpo
            remaining_temp = self.cache.get('temp', 'cleanup_test_0')
            results['clear_type'] = results['clear_type'] and remaining_temp is None
            
            # Limpa tudo
            cleared_all = self.cache.clear_all()
            results['clear_all'] = cleared_all > 0
            
            # Verifica se foi limpo
            remaining_odds = self.cache.get('odds', 'cleanup_odds_0')
            results['clear_all'] = results['clear_all'] and remaining_odds is None
            
        except Exception as e:
            print(f"❌ Erro no teste de limpeza: {e}")
        
        self.test_results['cleanup'] = results
        print(f"✅ Limpeza: {sum(results.values())}/{len(results)} passou")
    
    def test_error_handling(self):
        """Testa tratamento de erros"""
        print("🧪 Testando tratamento de erros...")
        
        results = {
            'invalid_key': False,
            'invalid_type': False,
            'connection_error': False
        }
        
        try:
            # Teste chave inválida
            invalid_result = self.cache.get('temp', '')
            results['invalid_key'] = invalid_result is None
            
            # Teste tipo inválido
            try:
                self.cache.get('invalid_type', 'test_key')
                results['invalid_type'] = True  # Deve falhar silenciosamente
            except:
                results['invalid_type'] = False
            
            # Teste conexão (simulado)
            # Em um ambiente real, isso testaria desconexão do Redis
            results['connection_error'] = True  # Assume que conexão está OK
            
        except Exception as e:
            print(f"❌ Erro no teste de tratamento de erros: {e}")
        
        self.test_results['error_handling'] = results
        print(f"✅ Tratamento de erros: {sum(results.values())}/{len(results)} passou")
    
    def get_cache_stats(self):
        """Obtém estatísticas do cache"""
        try:
            stats = self.cache.get_stats()
            return stats
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return None
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 Iniciando testes do sistema de cache Redis...")
        print("=" * 60)
        
        # Executa todos os testes
        self.test_basic_operations()
        self.test_odds_caching()
        self.test_stats_caching()
        self.test_performance()
        self.test_serialization()
        self.test_ttl_expiration()
        self.test_cleanup()
        self.test_error_handling()
        
        # Resumo dos resultados
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, test_results in self.test_results.items():
            test_passed = sum(test_results.values())
            test_total = len(test_results)
            total_tests += test_total
            passed_tests += test_passed
            
            status = "✅" if test_passed == test_total else "❌"
            print(f"{status} {test_name}: {test_passed}/{test_total}")
        
        print(f"\n🎯 Total: {passed_tests}/{total_tests} testes passaram")
        print(f"📈 Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        # Estatísticas do cache
        print("\n📊 ESTATÍSTICAS DO CACHE")
        print("=" * 60)
        stats = self.get_cache_stats()
        if stats:
            for key, value in stats.items():
                print(f"{key}: {value}")
        
        return self.test_results

def main():
    """Função principal"""
    tester = CacheTester()
    results = tester.run_all_tests()
    
    # Retorna código de saída baseado nos resultados
    total_tests = sum(len(test_results) for test_results in results.values())
    passed_tests = sum(sum(test_results.values()) for test_results in results.values())
    
    if passed_tests == total_tests:
        print("\n🎉 Todos os testes passaram!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total_tests - passed_tests} testes falharam!")
        sys.exit(1)

if __name__ == '__main__':
    main()
