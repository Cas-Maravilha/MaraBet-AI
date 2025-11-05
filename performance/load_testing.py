#!/usr/bin/env python3
"""
Sistema de Testes de Carga e Escalabilidade
MaraBet AI - Validação de performance real
"""

import asyncio
import aiohttp
import time
import statistics
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import psutil
import requests
from threading import Thread
import queue

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LoadTestConfig:
    """Configuração de teste de carga"""
    base_url: str = "http://localhost:5000"
    max_concurrent_users: int = 1000
    test_duration_seconds: int = 300  # 5 minutos
    ramp_up_seconds: int = 60
    target_rps: int = 1000  # requests por segundo
    max_response_time_ms: int = 200
    target_uptime_percent: float = 99.9

@dataclass
class PerformanceMetrics:
    """Métricas de performance"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = None
    throughput_rps: float = 0.0
    average_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    min_response_time_ms: float = 0.0
    error_rate_percent: float = 0.0
    uptime_percent: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0

class LoadTester:
    """Testador de carga e escalabilidade"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.metrics = PerformanceMetrics()
        self.metrics.response_times = []
        self.start_time = None
        self.end_time = None
        self.results_queue = queue.Queue()
        self.monitoring_active = False
        
    async def run_load_test(self) -> PerformanceMetrics:
        """Executa teste de carga completo"""
        logger.info("🚀 INICIANDO TESTE DE CARGA E ESCALABILIDADE")
        logger.info(f"Target: {self.config.target_rps} RPS por {self.config.test_duration_seconds}s")
        logger.info(f"Max concurrent users: {self.config.max_concurrent_users}")
        
        self.start_time = time.time()
        
        # Iniciar monitoramento de sistema
        self._start_system_monitoring()
        
        # Executar teste de carga
        await self._execute_load_test()
        
        self.end_time = time.time()
        
        # Parar monitoramento
        self.monitoring_active = False
        
        # Calcular métricas finais
        self._calculate_final_metrics()
        
        return self.metrics
    
    async def _execute_load_test(self):
        """Executa o teste de carga"""
        tasks = []
        
        # Criar tasks para usuários simultâneos
        for user_id in range(self.config.max_concurrent_users):
            task = asyncio.create_task(self._simulate_user(user_id))
            tasks.append(task)
        
        # Aguardar conclusão do teste
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _simulate_user(self, user_id: int):
        """Simula um usuário fazendo requests"""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            end_time = start_time + self.config.test_duration_seconds
            
            while time.time() < end_time:
                # Calcular delay baseado no RPS target
                delay = 1.0 / (self.config.target_rps / self.config.max_concurrent_users)
                
                # Fazer request
                await self._make_request(session, user_id)
                
                # Aguardar delay
                await asyncio.sleep(delay)
    
    async def _make_request(self, session: aiohttp.ClientSession, user_id: int):
        """Faz uma request HTTP"""
        request_start = time.time()
        
        try:
            # Escolher endpoint aleatório
            endpoint = self._get_random_endpoint()
            url = f"{self.config.base_url}{endpoint}"
            
            # Fazer request
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                response_time = (time.time() - request_start) * 1000  # ms
                
                # Registrar métricas
                self._record_request_metrics(response.status, response_time)
                
        except Exception as e:
            response_time = (time.time() - request_start) * 1000
            self._record_request_metrics(500, response_time, str(e))
    
    def _get_random_endpoint(self) -> str:
        """Retorna endpoint aleatório para teste"""
        endpoints = [
            "/api/health",
            "/api/matches",
            "/api/risk/status",
            "/api/risk/report",
            "/api/predictions"
        ]
        import random
        return random.choice(endpoints)
    
    def _record_request_metrics(self, status_code: int, response_time_ms: float, error: str = None):
        """Registra métricas de uma request"""
        self.metrics.total_requests += 1
        
        if 200 <= status_code < 300:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        self.metrics.response_times.append(response_time_ms)
        
        # Atualizar min/max
        if response_time_ms > self.metrics.max_response_time_ms:
            self.metrics.max_response_time_ms = response_time_ms
        
        if self.metrics.min_response_time_ms == 0 or response_time_ms < self.metrics.min_response_time_ms:
            self.metrics.min_response_time_ms = response_time_ms
    
    def _start_system_monitoring(self):
        """Inicia monitoramento do sistema"""
        self.monitoring_active = True
        monitor_thread = Thread(target=self._monitor_system_resources)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def _monitor_system_resources(self):
        """Monitora recursos do sistema"""
        cpu_samples = []
        memory_samples = []
        
        while self.monitoring_active:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_samples.append(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_samples.append(memory.percent)
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                break
        
        # Calcular médias
        if cpu_samples:
            self.metrics.cpu_usage_percent = statistics.mean(cpu_samples)
        if memory_samples:
            self.metrics.memory_usage_percent = statistics.mean(memory_samples)
    
    def _calculate_final_metrics(self):
        """Calcula métricas finais"""
        if not self.metrics.response_times:
            return
        
        # Throughput
        test_duration = self.end_time - self.start_time
        self.metrics.throughput_rps = self.metrics.total_requests / test_duration
        
        # Response times
        self.metrics.average_response_time_ms = statistics.mean(self.metrics.response_times)
        
        if len(self.metrics.response_times) > 1:
            self.metrics.p95_response_time_ms = self._calculate_percentile(self.metrics.response_times, 95)
            self.metrics.p99_response_time_ms = self._calculate_percentile(self.metrics.response_times, 99)
        
        # Error rate
        if self.metrics.total_requests > 0:
            self.metrics.error_rate_percent = (self.metrics.failed_requests / self.metrics.total_requests) * 100
        
        # Uptime
        if self.metrics.total_requests > 0:
            self.metrics.uptime_percent = (self.metrics.successful_requests / self.metrics.total_requests) * 100
    
    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calcula percentil dos dados"""
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def generate_report(self) -> str:
        """Gera relatório de performance"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE TESTE DE CARGA E ESCALABILIDADE - MARABET AI")
        report.append("=" * 80)
        
        # Configuração do teste
        report.append(f"\n📋 CONFIGURAÇÃO DO TESTE:")
        report.append(f"  URL Base: {self.config.base_url}")
        report.append(f"  Usuários Simultâneos: {self.config.max_concurrent_users}")
        report.append(f"  Duração: {self.config.test_duration_seconds} segundos")
        report.append(f"  Target RPS: {self.config.target_rps}")
        report.append(f"  Ramp-up: {self.config.ramp_up_seconds} segundos")
        
        # Métricas de requests
        report.append(f"\n📊 MÉTRICAS DE REQUESTS:")
        report.append(f"  Total de Requests: {self.metrics.total_requests:,}")
        report.append(f"  Requests Bem-sucedidas: {self.metrics.successful_requests:,}")
        report.append(f"  Requests Falharam: {self.metrics.failed_requests:,}")
        report.append(f"  Taxa de Erro: {self.metrics.error_rate_percent:.2f}%")
        report.append(f"  Uptime: {self.metrics.uptime_percent:.2f}%")
        
        # Métricas de performance
        report.append(f"\n⚡ MÉTRICAS DE PERFORMANCE:")
        report.append(f"  Throughput: {self.metrics.throughput_rps:.2f} RPS")
        report.append(f"  Tempo de Resposta Médio: {self.metrics.average_response_time_ms:.2f} ms")
        report.append(f"  Tempo de Resposta P95: {self.metrics.p95_response_time_ms:.2f} ms")
        report.append(f"  Tempo de Resposta P99: {self.metrics.p99_response_time_ms:.2f} ms")
        report.append(f"  Tempo de Resposta Máximo: {self.metrics.max_response_time_ms:.2f} ms")
        report.append(f"  Tempo de Resposta Mínimo: {self.metrics.min_response_time_ms:.2f} ms")
        
        # Métricas de sistema
        report.append(f"\n💻 MÉTRICAS DE SISTEMA:")
        report.append(f"  CPU Usage: {self.metrics.cpu_usage_percent:.2f}%")
        report.append(f"  Memory Usage: {self.metrics.memory_usage_percent:.2f}%")
        
        # Validação de objetivos
        report.append(f"\n🎯 VALIDAÇÃO DE OBJETIVOS:")
        
        # Throughput
        if self.metrics.throughput_rps >= self.config.target_rps:
            report.append(f"  ✅ Throughput: {self.metrics.throughput_rps:.2f} RPS >= {self.config.target_rps} RPS")
        else:
            report.append(f"  ❌ Throughput: {self.metrics.throughput_rps:.2f} RPS < {self.config.target_rps} RPS")
        
        # Response time
        if self.metrics.average_response_time_ms <= self.config.max_response_time_ms:
            report.append(f"  ✅ Response Time: {self.metrics.average_response_time_ms:.2f} ms <= {self.config.max_response_time_ms} ms")
        else:
            report.append(f"  ❌ Response Time: {self.metrics.average_response_time_ms:.2f} ms > {self.config.max_response_time_ms} ms")
        
        # Uptime
        if self.metrics.uptime_percent >= self.config.target_uptime_percent:
            report.append(f"  ✅ Uptime: {self.metrics.uptime_percent:.2f}% >= {self.config.target_uptime_percent}%")
        else:
            report.append(f"  ❌ Uptime: {self.metrics.uptime_percent:.2f}% < {self.config.target_uptime_percent}%")
        
        # P95 response time
        if self.metrics.p95_response_time_ms <= self.config.max_response_time_ms:
            report.append(f"  ✅ P95 Response Time: {self.metrics.p95_response_time_ms:.2f} ms <= {self.config.max_response_time_ms} ms")
        else:
            report.append(f"  ❌ P95 Response Time: {self.metrics.p95_response_time_ms:.2f} ms > {self.config.max_response_time_ms} ms")
        
        # Recomendações
        report.append(f"\n💡 RECOMENDAÇÕES:")
        
        if self.metrics.throughput_rps < self.config.target_rps:
            report.append(f"  ⚠️ Throughput abaixo do target - considere otimizações")
        
        if self.metrics.average_response_time_ms > self.config.max_response_time_ms:
            report.append(f"  ⚠️ Response time alto - implemente cache ou otimizações")
        
        if self.metrics.uptime_percent < self.config.target_uptime_percent:
            report.append(f"  ⚠️ Uptime abaixo do target - verifique estabilidade")
        
        if self.metrics.cpu_usage_percent > 80:
            report.append(f"  ⚠️ CPU usage alto - considere escalar horizontalmente")
        
        if self.metrics.memory_usage_percent > 80:
            report.append(f"  ⚠️ Memory usage alto - otimize uso de memória")
        
        report.append("=" * 80)
        
        return "\n".join(report)

class ScalabilityTester:
    """Testador de escalabilidade"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
    
    async def test_scalability(self) -> Dict[str, Any]:
        """Testa escalabilidade com diferentes cargas"""
        logger.info("🔍 TESTANDO ESCALABILIDADE")
        
        test_scenarios = [
            {"users": 100, "duration": 60, "rps": 100},
            {"users": 500, "duration": 120, "rps": 500},
            {"users": 1000, "duration": 180, "rps": 1000},
            {"users": 2000, "duration": 240, "rps": 2000}
        ]
        
        results = {}
        
        for i, scenario in enumerate(test_scenarios):
            logger.info(f"Teste {i+1}/{len(test_scenarios)}: {scenario['users']} usuários, {scenario['rps']} RPS")
            
            config = LoadTestConfig(
                base_url=self.base_url,
                max_concurrent_users=scenario['users'],
                test_duration_seconds=scenario['duration'],
                target_rps=scenario['rps'],
                max_response_time_ms=200
            )
            
            tester = LoadTester(config)
            metrics = await tester.run_load_test()
            
            results[f"test_{i+1}"] = {
                "scenario": scenario,
                "metrics": metrics,
                "passed": self._evaluate_scalability(metrics, scenario)
            }
        
        return results
    
    def _evaluate_scalability(self, metrics: PerformanceMetrics, scenario: Dict[str, Any]) -> bool:
        """Avalia se o teste de escalabilidade passou"""
        # Critérios de aprovação
        throughput_ok = metrics.throughput_rps >= scenario['rps'] * 0.8  # 80% do target
        response_time_ok = metrics.average_response_time_ms <= 200
        uptime_ok = metrics.uptime_percent >= 99.0
        error_rate_ok = metrics.error_rate_percent <= 1.0
        
        return throughput_ok and response_time_ok and uptime_ok and error_rate_ok

async def main():
    """Função principal para teste de carga"""
    print("🚀 INICIANDO TESTES DE CARGA E ESCALABILIDADE")
    print("=" * 60)
    
    # Configuração do teste
    config = LoadTestConfig(
        base_url="http://localhost:5000",
        max_concurrent_users=1000,
        test_duration_seconds=300,  # 5 minutos
        target_rps=1000,
        max_response_time_ms=200
    )
    
    # Executar teste de carga
    tester = LoadTester(config)
    metrics = await tester.run_load_test()
    
    # Gerar relatório
    report = tester.generate_report()
    print(report)
    
    # Salvar relatório
    with open("load_test_report.txt", "w") as f:
        f.write(report)
    
    print("\n🎉 TESTE DE CARGA CONCLUÍDO!")
    print("Relatório salvo em: load_test_report.txt")

if __name__ == "__main__":
    asyncio.run(main())
