#!/usr/bin/env python3
"""
Script de Teste do Sistema MaraBet AI
Testa todos os componentes: Redis, Celery, Cache, Tarefas
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Any

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SystemTester:
    """Testador do sistema MaraBet AI"""
    
    def __init__(self):
        self.test_results = {}
        self.base_urls = {
            'api': 'http://localhost:5000',
            'dashboard': 'http://localhost:8000',
            'flower': 'http://localhost:5555'
        }
    
    def log(self, message: str, level: str = 'INFO'):
        """Log com timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_redis_connection(self):
        """Testa conexão com Redis"""
        self.log("🧪 Testando conexão Redis...")
        
        try:
            from cache.redis_cache import RedisCache
            cache = RedisCache()
            
            # Teste básico
            test_key = 'test_connection'
            test_value = {'test': True, 'timestamp': datetime.now().isoformat()}
            
            # SET
            set_result = cache.set('temp', test_key, test_value, ttl=60)
            
            # GET
            retrieved_value = cache.get('temp', test_key)
            
            # DELETE
            delete_result = cache.delete('temp', test_key)
            
            success = set_result and retrieved_value == test_value and delete_result
            
            self.test_results['redis_connection'] = {
                'status': 'success' if success else 'failed',
                'details': {
                    'set': set_result,
                    'get': retrieved_value == test_value,
                    'delete': delete_result
                }
            }
            
            self.log(f"✅ Redis: {'OK' if success else 'FALHOU'}")
            
        except Exception as e:
            self.log(f"❌ Redis: Erro - {e}", 'ERROR')
            self.test_results['redis_connection'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def test_celery_workers(self):
        """Testa workers do Celery"""
        self.log("🧪 Testando workers Celery...")
        
        try:
            from tasks.celery_app import get_worker_stats, get_active_tasks
            
            # Status dos workers
            worker_stats = get_worker_stats()
            
            # Tarefas ativas
            active_tasks = get_active_tasks()
            
            success = worker_stats is not None
            
            self.test_results['celery_workers'] = {
                'status': 'success' if success else 'failed',
                'details': {
                    'workers_count': len(worker_stats) if worker_stats else 0,
                    'active_tasks': sum(len(tasks) for tasks in active_tasks.values()) if active_tasks else 0
                }
            }
            
            self.log(f"✅ Celery Workers: {'OK' if success else 'FALHOU'}")
            
        except Exception as e:
            self.log(f"❌ Celery Workers: Erro - {e}", 'ERROR')
            self.test_results['celery_workers'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def test_celery_tasks(self):
        """Testa execução de tarefas Celery"""
        self.log("🧪 Testando tarefas Celery...")
        
        try:
            from tasks.celery_app import celery_app
            
            # Testa tarefa simples
            result = celery_app.send_task('tasks.maintenance_tasks.health_check')
            
            # Aguarda resultado (timeout 30 segundos)
            task_result = result.get(timeout=30)
            
            success = task_result is not None and task_result.get('status') == 'success'
            
            self.test_results['celery_tasks'] = {
                'status': 'success' if success else 'failed',
                'details': {
                    'task_id': result.id,
                    'task_status': result.status,
                    'result': task_result
                }
            }
            
            self.log(f"✅ Celery Tasks: {'OK' if success else 'FALHOU'}")
            
        except Exception as e:
            self.log(f"❌ Celery Tasks: Erro - {e}", 'ERROR')
            self.test_results['celery_tasks'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def test_cache_performance(self):
        """Testa performance do cache"""
        self.log("🧪 Testando performance do cache...")
        
        try:
            from cache.redis_cache import RedisCache
            cache = RedisCache()
            
            # Teste de escrita
            start_time = time.time()
            write_count = 100
            
            for i in range(write_count):
                cache.set('temp', f'perf_test_{i}', {'data': f'value_{i}'}, ttl=60)
            
            write_time = time.time() - start_time
            write_ops_per_sec = write_count / write_time
            
            # Teste de leitura
            start_time = time.time()
            
            for i in range(write_count):
                cache.get('temp', f'perf_test_{i}')
            
            read_time = time.time() - start_time
            read_ops_per_sec = write_count / read_time
            
            # Limpeza
            cache.clear_type('temp')
            
            success = write_ops_per_sec > 50 and read_ops_per_sec > 100
            
            self.test_results['cache_performance'] = {
                'status': 'success' if success else 'failed',
                'details': {
                    'write_ops_per_sec': write_ops_per_sec,
                    'read_ops_per_sec': read_ops_per_sec,
                    'write_time': write_time,
                    'read_time': read_time
                }
            }
            
            self.log(f"✅ Cache Performance: {'OK' if success else 'FALHOU'}")
            self.log(f"  📊 Write: {write_ops_per_sec:.2f} ops/sec")
            self.log(f"  📊 Read: {read_ops_per_sec:.2f} ops/sec")
            
        except Exception as e:
            self.log(f"❌ Cache Performance: Erro - {e}", 'ERROR')
            self.test_results['cache_performance'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def test_api_endpoints(self):
        """Testa endpoints da API"""
        self.log("🧪 Testando endpoints da API...")
        
        endpoints = [
            {'url': '/health', 'method': 'GET', 'expected_status': 200},
            {'url': '/api/leagues', 'method': 'GET', 'expected_status': 200},
            {'url': '/api/matches', 'method': 'GET', 'expected_status': 200}
        ]
        
        results = []
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_urls['api']}{endpoint['url']}"
                response = requests.get(url, timeout=10)
                
                success = response.status_code == endpoint['expected_status']
                results.append({
                    'endpoint': endpoint['url'],
                    'status': 'success' if success else 'failed',
                    'status_code': response.status_code,
                    'expected': endpoint['expected_status']
                })
                
                self.log(f"  {'✅' if success else '❌'} {endpoint['url']}: {response.status_code}")
                
            except Exception as e:
                results.append({
                    'endpoint': endpoint['url'],
                    'status': 'failed',
                    'error': str(e)
                })
                self.log(f"  ❌ {endpoint['url']}: Erro - {e}", 'ERROR')
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        success = success_count == len(endpoints)
        
        self.test_results['api_endpoints'] = {
            'status': 'success' if success else 'failed',
            'details': {
                'total_endpoints': len(endpoints),
                'successful_endpoints': success_count,
                'results': results
            }
        }
        
        self.log(f"✅ API Endpoints: {success_count}/{len(endpoints)} OK")
    
    def test_dashboard(self):
        """Testa dashboard"""
        self.log("🧪 Testando dashboard...")
        
        try:
            response = requests.get(self.base_urls['dashboard'], timeout=10)
            success = response.status_code == 200
            
            self.test_results['dashboard'] = {
                'status': 'success' if success else 'failed',
                'details': {
                    'status_code': response.status_code,
                    'response_size': len(response.content)
                }
            }
            
            self.log(f"✅ Dashboard: {'OK' if success else 'FALHOU'}")
            
        except Exception as e:
            self.log(f"❌ Dashboard: Erro - {e}", 'ERROR')
            self.test_results['dashboard'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def test_flower(self):
        """Testa Flower (monitoramento Celery)"""
        self.log("🧪 Testando Flower...")
        
        try:
            response = requests.get(self.base_urls['flower'], timeout=10)
            success = response.status_code == 200
            
            self.test_results['flower'] = {
                'status': 'success' if success else 'failed',
                'details': {
                    'status_code': response.status_code,
                    'response_size': len(response.content)
                }
            }
            
            self.log(f"✅ Flower: {'OK' if success else 'FALHOU'}")
            
        except Exception as e:
            self.log(f"❌ Flower: Erro - {e}", 'ERROR')
            self.test_results['flower'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def test_database_connection(self):
        """Testa conexão com banco de dados"""
        self.log("🧪 Testando banco de dados...")
        
        try:
            from armazenamento.banco_de_dados import DatabaseManager
            
            db = DatabaseManager()
            db.test_connection()
            
            # Testa query simples
            result = db.execute_query("SELECT 1 as test")
            
            success = result is not None and len(result) > 0
            
            self.test_results['database'] = {
                'status': 'success' if success else 'failed',
                'details': {
                    'connection': True,
                    'query_result': result[0] if result else None
                }
            }
            
            self.log(f"✅ Database: {'OK' if success else 'FALHOU'}")
            
        except Exception as e:
            self.log(f"❌ Database: Erro - {e}", 'ERROR')
            self.test_results['database'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def test_ml_models(self):
        """Testa modelos de machine learning"""
        self.log("🧪 Testando modelos ML...")
        
        try:
            from ml.ml_models import MLModelManager
            
            ml_manager = MLModelManager()
            
            # Testa criação de modelo
            model = ml_manager.create_model('random_forest')
            
            # Testa predição simples
            import numpy as np
            X_test = np.array([[1.0, 2.0, 3.0, 4.0]])
            model.fit(X_test, [1])  # Fit simples
            prediction = model.predict(X_test)
            
            success = model is not None and prediction is not None
            
            self.test_results['ml_models'] = {
                'status': 'success' if success else 'failed',
                'details': {
                    'model_created': model is not None,
                    'prediction_works': prediction is not None,
                    'prediction': prediction.tolist() if prediction is not None else None
                }
            }
            
            self.log(f"✅ ML Models: {'OK' if success else 'FALHOU'}")
            
        except Exception as e:
            self.log(f"❌ ML Models: Erro - {e}", 'ERROR')
            self.test_results['ml_models'] = {
                'status': 'failed',
                'error': str(e)
            }
    
    def run_all_tests(self):
        """Executa todos os testes"""
        self.log("🚀 Iniciando testes do Sistema MaraBet AI...")
        self.log("=" * 60)
        
        # Executa todos os testes
        self.test_redis_connection()
        self.test_celery_workers()
        self.test_celery_tasks()
        self.test_cache_performance()
        self.test_api_endpoints()
        self.test_dashboard()
        self.test_flower()
        self.test_database_connection()
        self.test_ml_models()
        
        # Resumo dos resultados
        self.log("\n" + "=" * 60)
        self.log("📊 RESUMO DOS TESTES")
        self.log("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if result['status'] == 'success')
        
        for test_name, result in self.test_results.items():
            status = "✅" if result['status'] == 'success' else "❌"
            self.log(f"{status} {test_name}: {result['status']}")
        
        self.log(f"\n🎯 Total: {passed_tests}/{total_tests} testes passaram")
        self.log(f"📈 Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        # Status geral
        if passed_tests == total_tests:
            self.log("\n🎉 Todos os testes passaram! Sistema funcionando perfeitamente!")
            return True
        else:
            self.log(f"\n⚠️  {total_tests - passed_tests} testes falharam!")
            return False
    
    def save_results(self, filename: str = None):
        """Salva resultados dos testes"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            
            self.log(f"📄 Resultados salvos em: {filename}")
            
        except Exception as e:
            self.log(f"❌ Erro ao salvar resultados: {e}", 'ERROR')

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Testador do Sistema MaraBet AI')
    parser.add_argument('--save', action='store_true', help='Salvar resultados em arquivo')
    parser.add_argument('--file', type=str, help='Nome do arquivo para salvar resultados')
    
    args = parser.parse_args()
    
    tester = SystemTester()
    success = tester.run_all_tests()
    
    if args.save:
        tester.save_results(args.file)
    
    # Retorna código de saída baseado nos resultados
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
