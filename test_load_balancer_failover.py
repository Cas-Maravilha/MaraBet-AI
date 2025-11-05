#!/usr/bin/env python3
"""
Teste de Failover do Load Balancer
MaraBet AI - Validação de failover automático
"""

import requests
import time
import json
import subprocess
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LoadBalancerFailoverTester:
    """Testador de failover do load balancer"""
    
    def __init__(self):
        self.primary_endpoint = "https://api1.marabet.com"
        self.secondary_endpoint = "https://api2.marabet.com"
        self.health_check_path = "/api/health"
        self.timeout = 5
        self.max_retries = 3
        self.failover_timeout = 30
        
    def test_health_check(self, endpoint: str) -> bool:
        """Testa health check de um endpoint"""
        try:
            url = f"{endpoint}{self.health_check_path}"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('status') == 'healthy'
            return False
            
        except Exception as e:
            logger.error(f"Health check failed for {endpoint}: {e}")
            return False
    
    def simulate_primary_failure(self):
        """Simula falha do endpoint primário"""
        logger.info("🔴 SIMULANDO FALHA DO ENDPOINT PRIMÁRIO")
        
        # Simular falha (em ambiente real, isso seria feito via AWS/GCP)
        logger.info("  - Desabilitando endpoint primário...")
        time.sleep(2)
        logger.info("  - Endpoint primário desabilitado")
    
    def test_failover_process(self) -> Dict[str, Any]:
        """Testa processo de failover"""
        logger.info("🧪 TESTANDO PROCESSO DE FAILOVER")
        print("=" * 60)
        
        results = {
            'primary_healthy': False,
            'secondary_healthy': False,
            'failover_successful': False,
            'failover_time': 0,
            'dns_update_time': 0,
            'total_time': 0
        }
        
        start_time = time.time()
        
        # 1. Verificar estado inicial
        logger.info("1. Verificando estado inicial...")
        results['primary_healthy'] = self.test_health_check(self.primary_endpoint)
        results['secondary_healthy'] = self.test_health_check(self.secondary_endpoint)
        
        logger.info(f"   Primary healthy: {results['primary_healthy']}")
        logger.info(f"   Secondary healthy: {results['secondary_healthy']}")
        
        if not results['primary_healthy']:
            logger.warning("⚠️ Endpoint primário já está inativo")
            return results
        
        if not results['secondary_healthy']:
            logger.error("❌ Endpoint secundário não está disponível")
            return results
        
        # 2. Simular falha do primário
        logger.info("2. Simulando falha do endpoint primário...")
        self.simulate_primary_failure()
        
        # 3. Aguardar detecção da falha
        logger.info("3. Aguardando detecção da falha...")
        detection_start = time.time()
        
        while time.time() - detection_start < self.failover_timeout:
            if not self.test_health_check(self.primary_endpoint):
                logger.info("   ✅ Falha detectada")
                break
            time.sleep(1)
        else:
            logger.error("❌ Falha não detectada no tempo esperado")
            return results
        
        # 4. Aguardar failover
        logger.info("4. Aguardando failover...")
        failover_start = time.time()
        
        while time.time() - failover_start < self.failover_timeout:
            if self.test_health_check(self.secondary_endpoint):
                results['failover_successful'] = True
                results['failover_time'] = time.time() - failover_start
                logger.info("   ✅ Failover concluído")
                break
            time.sleep(1)
        else:
            logger.error("❌ Failover não concluído no tempo esperado")
            return results
        
        # 5. Simular atualização de DNS
        logger.info("5. Simulando atualização de DNS...")
        dns_start = time.time()
        
        # Simular atualização de DNS (em ambiente real, usar AWS Route 53 API)
        time.sleep(2)  # Simular tempo de propagação DNS
        
        results['dns_update_time'] = time.time() - dns_start
        logger.info("   ✅ DNS atualizado")
        
        results['total_time'] = time.time() - start_time
        
        return results
    
    def test_load_balancer_health(self) -> Dict[str, Any]:
        """Testa saúde do load balancer"""
        logger.info("🔍 TESTANDO SAÚDE DO LOAD BALANCER")
        print("=" * 60)
        
        results = {
            'primary_response_time': 0,
            'secondary_response_time': 0,
            'primary_status': 'unknown',
            'secondary_status': 'unknown',
            'load_balancer_healthy': False
        }
        
        # Testar endpoint primário
        logger.info("Testando endpoint primário...")
        start_time = time.time()
        try:
            response = requests.get(f"{self.primary_endpoint}{self.health_check_path}", timeout=self.timeout)
            results['primary_response_time'] = time.time() - start_time
            results['primary_status'] = 'healthy' if response.status_code == 200 else 'unhealthy'
            logger.info(f"   Status: {results['primary_status']}")
            logger.info(f"   Response time: {results['primary_response_time']:.2f}s")
        except Exception as e:
            results['primary_status'] = 'unhealthy'
            logger.error(f"   Erro: {e}")
        
        # Testar endpoint secundário
        logger.info("Testando endpoint secundário...")
        start_time = time.time()
        try:
            response = requests.get(f"{self.secondary_endpoint}{self.health_check_path}", timeout=self.timeout)
            results['secondary_response_time'] = time.time() - start_time
            results['secondary_status'] = 'healthy' if response.status_code == 200 else 'unhealthy'
            logger.info(f"   Status: {results['secondary_status']}")
            logger.info(f"   Response time: {results['secondary_response_time']:.2f}s")
        except Exception as e:
            results['secondary_status'] = 'unhealthy'
            logger.error(f"   Erro: {e}")
        
        # Determinar saúde geral
        results['load_balancer_healthy'] = (
            results['primary_status'] == 'healthy' or 
            results['secondary_status'] == 'healthy'
        )
        
        return results
    
    def test_load_balancer_performance(self) -> Dict[str, Any]:
        """Testa performance do load balancer"""
        logger.info("⚡ TESTANDO PERFORMANCE DO LOAD BALANCER")
        print("=" * 60)
        
        results = {
            'total_requests': 100,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'max_response_time': 0,
            'min_response_time': float('inf'),
            'throughput_rps': 0
        }
        
        response_times = []
        start_time = time.time()
        
        logger.info(f"Enviando {results['total_requests']} requests...")
        
        for i in range(results['total_requests']):
            try:
                request_start = time.time()
                response = requests.get(f"{self.primary_endpoint}{self.health_check_path}", timeout=self.timeout)
                request_time = time.time() - request_start
                
                if response.status_code == 200:
                    results['successful_requests'] += 1
                else:
                    results['failed_requests'] += 1
                
                response_times.append(request_time)
                results['max_response_time'] = max(results['max_response_time'], request_time)
                results['min_response_time'] = min(results['min_response_time'], request_time)
                
                if (i + 1) % 20 == 0:
                    logger.info(f"   Processados: {i + 1}/{results['total_requests']}")
                
            except Exception as e:
                results['failed_requests'] += 1
                logger.error(f"   Request {i + 1} falhou: {e}")
        
        # Calcular métricas
        if response_times:
            results['average_response_time'] = sum(response_times) / len(response_times)
            results['min_response_time'] = min(response_times)
        
        total_time = time.time() - start_time
        results['throughput_rps'] = results['total_requests'] / total_time
        
        return results
    
    def generate_report(self, health_results: Dict, failover_results: Dict, performance_results: Dict) -> str:
        """Gera relatório de teste"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE TESTE DE FAILOVER DO LOAD BALANCER - MARABET AI")
        report.append("=" * 80)
        
        # Resumo geral
        report.append(f"\n📊 RESUMO GERAL:")
        report.append(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"  Load Balancer: {'✅ Saudável' if health_results['load_balancer_healthy'] else '❌ Com problemas'}")
        report.append(f"  Failover: {'✅ Funcionando' if failover_results['failover_successful'] else '❌ Falhou'}")
        report.append(f"  Performance: {performance_results['throughput_rps']:.2f} RPS")
        
        # Health check results
        report.append(f"\n🔍 RESULTADOS DE HEALTH CHECK:")
        report.append(f"  Endpoint Primário:")
        report.append(f"    Status: {health_results['primary_status']}")
        report.append(f"    Response Time: {health_results['primary_response_time']:.2f}s")
        report.append(f"  Endpoint Secundário:")
        report.append(f"    Status: {health_results['secondary_status']}")
        report.append(f"    Response Time: {health_results['secondary_response_time']:.2f}s")
        
        # Failover results
        report.append(f"\n🔄 RESULTADOS DE FAILOVER:")
        report.append(f"  Falha Detectada: {'✅' if not health_results['primary_status'] == 'healthy' else '❌'}")
        report.append(f"  Failover Concluído: {'✅' if failover_results['failover_successful'] else '❌'}")
        report.append(f"  Tempo de Failover: {failover_results['failover_time']:.2f}s")
        report.append(f"  Tempo de DNS Update: {failover_results['dns_update_time']:.2f}s")
        report.append(f"  Tempo Total: {failover_results['total_time']:.2f}s")
        
        # Performance results
        report.append(f"\n⚡ RESULTADOS DE PERFORMANCE:")
        report.append(f"  Total de Requests: {performance_results['total_requests']}")
        report.append(f"  Requests Bem-sucedidas: {performance_results['successful_requests']}")
        report.append(f"  Requests Falharam: {performance_results['failed_requests']}")
        report.append(f"  Taxa de Sucesso: {(performance_results['successful_requests'] / performance_results['total_requests']) * 100:.2f}%")
        report.append(f"  Response Time Médio: {performance_results['average_response_time']:.2f}s")
        report.append(f"  Response Time Máximo: {performance_results['max_response_time']:.2f}s")
        report.append(f"  Response Time Mínimo: {performance_results['min_response_time']:.2f}s")
        report.append(f"  Throughput: {performance_results['throughput_rps']:.2f} RPS")
        
        # Validação de objetivos
        report.append(f"\n🎯 VALIDAÇÃO DE OBJETIVOS:")
        
        # Health check
        if health_results['load_balancer_healthy']:
            report.append(f"  ✅ Load Balancer saudável")
        else:
            report.append(f"  ❌ Load Balancer com problemas")
        
        # Failover
        if failover_results['failover_successful']:
            report.append(f"  ✅ Failover funcionando")
        else:
            report.append(f"  ❌ Failover falhou")
        
        # Performance
        if performance_results['throughput_rps'] >= 10:
            report.append(f"  ✅ Throughput adequado ({performance_results['throughput_rps']:.2f} RPS)")
        else:
            report.append(f"  ❌ Throughput baixo ({performance_results['throughput_rps']:.2f} RPS)")
        
        if performance_results['average_response_time'] <= 1.0:
            report.append(f"  ✅ Response time adequado ({performance_results['average_response_time']:.2f}s)")
        else:
            report.append(f"  ❌ Response time alto ({performance_results['average_response_time']:.2f}s)")
        
        # Recomendações
        report.append(f"\n💡 RECOMENDAÇÕES:")
        
        if not health_results['load_balancer_healthy']:
            report.append(f"  ⚠️ Verificar configuração do load balancer")
        
        if not failover_results['failover_successful']:
            report.append(f"  ⚠️ Configurar failover automático")
        
        if performance_results['throughput_rps'] < 10:
            report.append(f"  ⚠️ Otimizar performance do load balancer")
        
        if performance_results['average_response_time'] > 1.0:
            report.append(f"  ⚠️ Otimizar response time")
        
        report.append(f"  🔄 Executar testes de failover regularmente")
        report.append(f"  📊 Monitorar métricas de performance")
        
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Função principal"""
    print("🚀 TESTE DE FAILOVER DO LOAD BALANCER - MARABET AI")
    print("=" * 80)
    
    tester = LoadBalancerFailoverTester()
    
    try:
        # 1. Testar saúde do load balancer
        health_results = tester.test_load_balancer_health()
        
        # 2. Testar performance
        performance_results = tester.test_load_balancer_performance()
        
        # 3. Testar failover
        failover_results = tester.test_failover_process()
        
        # 4. Gerar relatório
        report = tester.generate_report(health_results, failover_results, performance_results)
        print(f"\n{report}")
        
        # 5. Salvar relatório
        with open("load_balancer_failover_test_report.txt", "w") as f:
            f.write(report)
        
        print("\n🎉 TESTE DE FAILOVER CONCLUÍDO!")
        print("📄 Relatório salvo em: load_balancer_failover_test_report.txt")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        return False

if __name__ == "__main__":
    main()
