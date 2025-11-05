"""
Validador de Performance - MaraBet AI
Validação empírica de desempenho para produção
"""

import time
import psutil
import requests
import threading
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import statistics
import concurrent.futures
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Métricas de performance"""
    response_time: float
    throughput: float
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    error_rate: float
    concurrent_users: int
    timestamp: datetime

@dataclass
class PerformanceTest:
    """Teste de performance"""
    name: str
    duration: int
    concurrent_users: int
    ramp_up_time: int
    target_url: str
    expected_response_time: float
    expected_throughput: float
    max_error_rate: float

@dataclass
class PerformanceReport:
    """Relatório de performance"""
    test_name: str
    timestamp: datetime
    duration: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput: float
    error_rate: float
    cpu_usage_avg: float
    memory_usage_avg: float
    disk_io_avg: float
    network_io_avg: float
    bottlenecks: List[str]
    recommendations: List[str]
    passed: bool

class PerformanceValidator:
    """
    Validador de performance para MaraBet AI
    Executa testes empíricos de desempenho
    """
    
    def __init__(self, config_file: str = "performance/config.json"):
        """
        Inicializa o validador de performance
        
        Args:
            config_file: Arquivo de configuração
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.metrics_history = []
        
        logger.info("PerformanceValidator inicializado")
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração de performance"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                default_config = {
                    "base_url": "http://localhost:8000",
                    "timeout": 30,
                    "max_concurrent": 100,
                    "test_duration": 300,
                    "ramp_up_time": 60,
                    "expected_response_time": 2.0,
                    "expected_throughput": 100,
                    "max_error_rate": 0.01
                }
                self._save_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configuração: {e}")
            return {}
    
    def _save_config(self, config: Dict[str, Any]):
        """Salva configuração"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar configuração: {e}")
    
    def run_performance_test(self, test: PerformanceTest) -> PerformanceReport:
        """
        Executa teste de performance
        
        Args:
            test: Configuração do teste
            
        Returns:
            Relatório de performance
        """
        try:
            logger.info(f"🚀 Iniciando teste de performance: {test.name}")
            
            # Inicializar métricas
            start_time = time.time()
            metrics = []
            request_times = []
            errors = 0
            total_requests = 0
            
            # Monitorar recursos do sistema
            system_metrics = []
            
            # Executar teste
            with concurrent.futures.ThreadPoolExecutor(max_workers=test.concurrent_users) as executor:
                # Ramp up
                self._ramp_up_users(test.concurrent_users, test.ramp_up_time)
                
                # Executar requests
                futures = []
                for _ in range(test.concurrent_users):
                    future = executor.submit(self._execute_request_loop, test, test.duration)
                    futures.append(future)
                
                # Monitorar sistema durante o teste
                monitor_thread = threading.Thread(
                    target=self._monitor_system_resources,
                    args=(test.duration, system_metrics)
                )
                monitor_thread.start()
                
                # Coletar resultados
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        request_times.extend(result['response_times'])
                        errors += result['errors']
                        total_requests += result['total_requests']
                    except Exception as e:
                        logger.error(f"❌ Erro no teste: {e}")
                        errors += 1
                
                monitor_thread.join()
            
            # Calcular métricas
            end_time = time.time()
            actual_duration = end_time - start_time
            
            successful_requests = total_requests - errors
            error_rate = errors / total_requests if total_requests > 0 else 0
            
            # Calcular tempos de resposta
            if request_times:
                avg_response_time = statistics.mean(request_times)
                p95_response_time = self._calculate_percentile(request_times, 95)
                p99_response_time = self._calculate_percentile(request_times, 99)
            else:
                avg_response_time = 0
                p95_response_time = 0
                p99_response_time = 0
            
            # Calcular throughput
            throughput = successful_requests / actual_duration if actual_duration > 0 else 0
            
            # Calcular métricas do sistema
            if system_metrics:
                cpu_usage_avg = statistics.mean([m['cpu'] for m in system_metrics])
                memory_usage_avg = statistics.mean([m['memory'] for m in system_metrics])
                disk_io_avg = statistics.mean([m['disk_io'] for m in system_metrics])
                network_io_avg = statistics.mean([m['network_io'] for m in system_metrics])
            else:
                cpu_usage_avg = 0
                memory_usage_avg = 0
                disk_io_avg = 0
                network_io_avg = 0
            
            # Identificar gargalos
            bottlenecks = self._identify_bottlenecks(
                avg_response_time, p95_response_time, p99_response_time,
                throughput, error_rate, cpu_usage_avg, memory_usage_avg
            )
            
            # Gerar recomendações
            recommendations = self._generate_recommendations(
                avg_response_time, throughput, error_rate,
                cpu_usage_avg, memory_usage_avg, bottlenecks
            )
            
            # Verificar se passou no teste
            passed = self._evaluate_test_results(
                avg_response_time, throughput, error_rate,
                test.expected_response_time, test.expected_throughput, test.max_error_rate
            )
            
            # Criar relatório
            report = PerformanceReport(
                test_name=test.name,
                timestamp=datetime.now(),
                duration=actual_duration,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=errors,
                average_response_time=avg_response_time,
                p95_response_time=p95_response_time,
                p99_response_time=p99_response_time,
                throughput=throughput,
                error_rate=error_rate,
                cpu_usage_avg=cpu_usage_avg,
                memory_usage_avg=memory_usage_avg,
                disk_io_avg=disk_io_avg,
                network_io_avg=network_io_avg,
                bottlenecks=bottlenecks,
                recommendations=recommendations,
                passed=passed
            )
            
            # Salvar relatório
            self._save_performance_report(report)
            
            logger.info(f"✅ Teste concluído - Throughput: {throughput:.2f} req/s, Response Time: {avg_response_time:.2f}s")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de performance: {e}")
            return self._empty_performance_report(test.name)
    
    def _execute_request_loop(self, test: PerformanceTest, duration: int) -> Dict[str, Any]:
        """Executa loop de requests"""
        start_time = time.time()
        response_times = []
        errors = 0
        total_requests = 0
        
        while time.time() - start_time < duration:
            try:
                request_start = time.time()
                
                # Fazer request
                response = requests.get(
                    test.target_url,
                    timeout=self.config.get('timeout', 30)
                )
                
                request_end = time.time()
                response_time = request_end - request_start
                
                response_times.append(response_time)
                total_requests += 1
                
                # Verificar se é erro
                if response.status_code >= 400:
                    errors += 1
                
                # Pequena pausa entre requests
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Erro no request: {e}")
                errors += 1
                total_requests += 1
        
        return {
            'response_times': response_times,
            'errors': errors,
            'total_requests': total_requests
        }
    
    def _ramp_up_users(self, max_users: int, ramp_up_time: int):
        """Ramp up gradual de usuários"""
        if ramp_up_time <= 0:
            return
        
        step_time = ramp_up_time / max_users
        for i in range(max_users):
            time.sleep(step_time)
    
    def _monitor_system_resources(self, duration: int, metrics: List[Dict[str, float]]):
        """Monitora recursos do sistema"""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memória
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Disk I/O
                disk_io = psutil.disk_io_counters()
                disk_io_rate = disk_io.read_bytes + disk_io.write_bytes if disk_io else 0
                
                # Network I/O
                network_io = psutil.net_io_counters()
                network_io_rate = network_io.bytes_sent + network_io.bytes_recv if network_io else 0
                
                metrics.append({
                    'cpu': cpu_percent,
                    'memory': memory_percent,
                    'disk_io': disk_io_rate,
                    'network_io': network_io_rate,
                    'timestamp': time.time()
                })
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(1)
    
    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calcula percentil dos dados"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _identify_bottlenecks(self, avg_response_time: float, p95_response_time: float,
                             p99_response_time: float, throughput: float, error_rate: float,
                             cpu_usage: float, memory_usage: float) -> List[str]:
        """Identifica gargalos de performance"""
        bottlenecks = []
        
        # Gargalos de tempo de resposta
        if avg_response_time > 2.0:
            bottlenecks.append("Tempo de resposta médio alto")
        
        if p95_response_time > 5.0:
            bottlenecks.append("P95 de tempo de resposta alto")
        
        if p99_response_time > 10.0:
            bottlenecks.append("P99 de tempo de resposta alto")
        
        # Gargalos de throughput
        if throughput < 50:
            bottlenecks.append("Throughput baixo")
        
        # Gargalos de erro
        if error_rate > 0.01:
            bottlenecks.append("Taxa de erro alta")
        
        # Gargalos de recursos
        if cpu_usage > 80:
            bottlenecks.append("Uso de CPU alto")
        
        if memory_usage > 80:
            bottlenecks.append("Uso de memória alto")
        
        # Gargalos de consistência
        if p99_response_time > avg_response_time * 5:
            bottlenecks.append("Inconsistência de performance")
        
        return bottlenecks
    
    def _generate_recommendations(self, avg_response_time: float, throughput: float,
                                 error_rate: float, cpu_usage: float, memory_usage: float,
                                 bottlenecks: List[str]) -> List[str]:
        """Gera recomendações de otimização"""
        recommendations = []
        
        # Recomendações baseadas em gargalos
        if "Tempo de resposta médio alto" in bottlenecks:
            recommendations.append("⚡ Otimizar consultas de banco de dados")
            recommendations.append("🔄 Implementar cache Redis")
            recommendations.append("📊 Otimizar algoritmos de ML")
        
        if "P95 de tempo de resposta alto" in bottlenecks:
            recommendations.append("🎯 Otimizar queries mais lentas")
            recommendations.append("📈 Implementar paginação")
            recommendations.append("🔍 Adicionar índices de banco")
        
        if "Throughput baixo" in bottlenecks:
            recommendations.append("🚀 Implementar load balancing")
            recommendations.append("⚡ Usar processamento assíncrono")
            recommendations.append("📦 Implementar CDN")
        
        if "Taxa de erro alta" in bottlenecks:
            recommendations.append("🛡️ Melhorar tratamento de erros")
            recommendations.append("🔍 Implementar logging detalhado")
            recommendations.append("🔄 Adicionar retry logic")
        
        if "Uso de CPU alto" in bottlenecks:
            recommendations.append("⚡ Otimizar algoritmos")
            recommendations.append("🔄 Implementar cache")
            recommendations.append("📊 Reduzir complexidade computacional")
        
        if "Uso de memória alto" in bottlenecks:
            recommendations.append("💾 Otimizar uso de memória")
            recommendations.append("🔄 Implementar garbage collection")
            recommendations.append("📊 Reduzir tamanho de datasets")
        
        # Recomendações gerais
        if avg_response_time > 1.0:
            recommendations.append("🎯 Implementar otimizações gerais de performance")
        
        if throughput < 100:
            recommendations.append("🚀 Escalar horizontalmente")
        
        if error_rate > 0.005:
            recommendations.append("🛡️ Melhorar robustez do sistema")
        
        return recommendations
    
    def _evaluate_test_results(self, avg_response_time: float, throughput: float,
                              error_rate: float, expected_response_time: float,
                              expected_throughput: float, max_error_rate: float) -> bool:
        """Avalia se o teste passou"""
        return (
            avg_response_time <= expected_response_time and
            throughput >= expected_throughput and
            error_rate <= max_error_rate
        )
    
    def run_load_test(self, concurrent_users: int = 50, duration: int = 300) -> PerformanceReport:
        """Executa teste de carga"""
        test = PerformanceTest(
            name="Load Test",
            duration=duration,
            concurrent_users=concurrent_users,
            ramp_up_time=60,
            target_url=self.config.get('base_url', 'http://localhost:8000'),
            expected_response_time=self.config.get('expected_response_time', 2.0),
            expected_throughput=self.config.get('expected_throughput', 100),
            max_error_rate=self.config.get('max_error_rate', 0.01)
        )
        
        return self.run_performance_test(test)
    
    def run_stress_test(self, max_concurrent_users: int = 200, duration: int = 600) -> PerformanceReport:
        """Executa teste de stress"""
        test = PerformanceTest(
            name="Stress Test",
            duration=duration,
            concurrent_users=max_concurrent_users,
            ramp_up_time=120,
            target_url=self.config.get('base_url', 'http://localhost:8000'),
            expected_response_time=5.0,  # Mais tolerante para stress test
            expected_throughput=50,     # Menor para stress test
            max_error_rate=0.05        # Mais tolerante para stress test
        )
        
        return self.run_performance_test(test)
    
    def run_spike_test(self, spike_users: int = 300, duration: int = 180) -> PerformanceReport:
        """Executa teste de picos"""
        test = PerformanceTest(
            name="Spike Test",
            duration=duration,
            concurrent_users=spike_users,
            ramp_up_time=30,  # Ramp up rápido para simular pico
            target_url=self.config.get('base_url', 'http://localhost:8000'),
            expected_response_time=3.0,
            expected_throughput=30,
            max_error_rate=0.02
        )
        
        return self.run_performance_test(test)
    
    def _save_performance_report(self, report: PerformanceReport):
        """Salva relatório de performance"""
        try:
            filename = f"performance_report_{report.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join("performance", filename)
            
            # Converter para dicionário
            report_dict = {
                "test_name": report.test_name,
                "timestamp": report.timestamp.isoformat(),
                "duration": report.duration,
                "total_requests": report.total_requests,
                "successful_requests": report.successful_requests,
                "failed_requests": report.failed_requests,
                "average_response_time": report.average_response_time,
                "p95_response_time": report.p95_response_time,
                "p99_response_time": report.p99_response_time,
                "throughput": report.throughput,
                "error_rate": report.error_rate,
                "cpu_usage_avg": report.cpu_usage_avg,
                "memory_usage_avg": report.memory_usage_avg,
                "disk_io_avg": report.disk_io_avg,
                "network_io_avg": report.network_io_avg,
                "bottlenecks": report.bottlenecks,
                "recommendations": report.recommendations,
                "passed": report.passed
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Relatório de performance salvo em {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {e}")
    
    def _empty_performance_report(self, test_name: str) -> PerformanceReport:
        """Retorna relatório vazio"""
        return PerformanceReport(
            test_name=test_name,
            timestamp=datetime.now(),
            duration=0,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            average_response_time=0.0,
            p95_response_time=0.0,
            p99_response_time=0.0,
            throughput=0.0,
            error_rate=0.0,
            cpu_usage_avg=0.0,
            memory_usage_avg=0.0,
            disk_io_avg=0.0,
            network_io_avg=0.0,
            bottlenecks=[],
            recommendations=[],
            passed=False
        )
