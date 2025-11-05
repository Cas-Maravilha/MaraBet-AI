#!/usr/bin/env python3
"""
Sistema de Health Checks para o MaraBet AI
Monitoramento completo da saúde do sistema
"""

import time
import psutil
import redis
import sqlite3
import requests
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
import logging

logger = logging.getLogger(__name__)

class HealthChecker:
    """Sistema de verificação de saúde do sistema"""
    
    def __init__(self):
        """Inicializa o health checker"""
        self.start_time = datetime.now()
        self.checks = {}
        self.last_check = None
    
    def check_database(self):
        """Verifica saúde do banco de dados"""
        try:
            # Testar conexão SQLite
            conn = sqlite3.connect('mara_bet.db')
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            conn.close()
            
            return {
                'status': 'healthy',
                'response_time': 0.001,  # Simulado
                'message': 'Database connection successful'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Database connection failed'
            }
    
    def check_redis(self):
        """Verifica saúde do Redis"""
        try:
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            start_time = time.time()
            r.ping()
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': response_time,
                'message': 'Redis connection successful'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Redis connection failed'
            }
    
    def check_api_football(self):
        """Verifica saúde da API Football"""
        try:
            from settings.settings import API_FOOTBALL_KEY
            
            if not API_FOOTBALL_KEY:
                return {
                    'status': 'unhealthy',
                    'error': 'API key not configured',
                    'message': 'API Football key not set'
                }
            
            url = "https://v3.football.api-sports.io/status"
            headers = {"X-API-Key": API_FOOTBALL_KEY}
            
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': response_time,
                    'message': 'API Football accessible'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f'HTTP {response.status_code}',
                    'message': 'API Football returned error'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'API Football connection failed'
            }
    
    def check_telegram(self):
        """Verifica saúde do Telegram Bot"""
        try:
            from settings.settings import TELEGRAM_BOT_TOKEN
            
            if not TELEGRAM_BOT_TOKEN:
                return {
                    'status': 'unhealthy',
                    'error': 'Bot token not configured',
                    'message': 'Telegram bot token not set'
                }
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
            
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': response_time,
                    'message': 'Telegram bot accessible'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f'HTTP {response.status_code}',
                    'message': 'Telegram bot returned error'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Telegram bot connection failed'
            }
    
    def check_system_resources(self):
        """Verifica recursos do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Status baseado em thresholds
            status = 'healthy'
            if cpu_percent > 80 or memory_percent > 80 or disk_percent > 90:
                status = 'warning'
            if cpu_percent > 95 or memory_percent > 95 or disk_percent > 95:
                status = 'critical'
            
            return {
                'status': status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'message': 'System resources checked'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'System resources check failed'
            }
    
    def check_uptime(self):
        """Verifica uptime do sistema"""
        try:
            uptime = datetime.now() - self.start_time
            uptime_seconds = uptime.total_seconds()
            
            return {
                'status': 'healthy',
                'uptime_seconds': uptime_seconds,
                'uptime_human': str(uptime),
                'start_time': self.start_time.isoformat(),
                'message': 'Uptime calculated'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Uptime calculation failed'
            }
    
    def run_all_checks(self):
        """Executa todos os checks"""
        self.last_check = datetime.now()
        
        checks = {
            'database': self.check_database(),
            'redis': self.check_redis(),
            'api_football': self.check_api_football(),
            'telegram': self.check_telegram(),
            'system_resources': self.check_system_resources(),
            'uptime': self.check_uptime()
        }
        
        self.checks = checks
        
        # Determinar status geral
        overall_status = 'healthy'
        for check_name, check_result in checks.items():
            if check_result['status'] == 'unhealthy':
                overall_status = 'unhealthy'
                break
            elif check_result['status'] == 'warning' and overall_status == 'healthy':
                overall_status = 'warning'
            elif check_result['status'] == 'critical':
                overall_status = 'critical'
        
        return {
            'overall_status': overall_status,
            'timestamp': self.last_check.isoformat(),
            'checks': checks
        }
    
    def get_health_summary(self):
        """Retorna resumo da saúde do sistema"""
        if not self.checks:
            self.run_all_checks()
        
        healthy_count = sum(1 for check in self.checks.values() if check['status'] == 'healthy')
        total_count = len(self.checks)
        
        return {
            'overall_status': self.checks.get('overall_status', 'unknown'),
            'healthy_checks': healthy_count,
            'total_checks': total_count,
            'health_percentage': (healthy_count / total_count) * 100,
            'last_check': self.last_check.isoformat() if self.last_check else None
        }

# Instância global do health checker
health_checker = HealthChecker()

# Blueprint para endpoints de health
health_bp = Blueprint('health', __name__, url_prefix='/health')

@health_bp.route('/')
def health_check():
    """Endpoint principal de health check"""
    try:
        result = health_checker.run_all_checks()
        
        # Determinar código de status HTTP
        status_code = 200
        if result['overall_status'] == 'unhealthy':
            status_code = 503
        elif result['overall_status'] == 'critical':
            status_code = 503
        
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'overall_status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@health_bp.route('/summary')
def health_summary():
    """Endpoint de resumo de saúde"""
    try:
        summary = health_checker.get_health_summary()
        return jsonify(summary), 200
    except Exception as e:
        logger.error(f"Health summary failed: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@health_bp.route('/ready')
def readiness_check():
    """Endpoint de readiness check (Kubernetes)"""
    try:
        # Verificar apenas componentes críticos
        critical_checks = ['database', 'api_football']
        
        for check_name in critical_checks:
            if check_name == 'database':
                result = health_checker.check_database()
            elif check_name == 'api_football':
                result = health_checker.check_api_football()
            else:
                continue
            
            if result['status'] != 'healthy':
                return jsonify({
                    'status': 'not_ready',
                    'failed_check': check_name,
                    'error': result.get('error', 'Unknown error')
                }), 503
        
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            'status': 'not_ready',
            'error': str(e)
        }), 503

@health_bp.route('/live')
def liveness_check():
    """Endpoint de liveness check (Kubernetes)"""
    try:
        # Verificar se a aplicação está respondendo
        uptime_result = health_checker.check_uptime()
        
        if uptime_result['status'] == 'healthy':
            return jsonify({
                'status': 'alive',
                'uptime': uptime_result['uptime_human'],
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'not_alive',
                'error': uptime_result.get('error', 'Unknown error')
            }), 503
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        return jsonify({
            'status': 'not_alive',
            'error': str(e)
        }), 503

@health_bp.route('/metrics')
def health_metrics():
    """Endpoint de métricas de saúde"""
    try:
        if not health_checker.checks:
            health_checker.run_all_checks()
        
        metrics = {
            'mara_bet_health_status': 1 if health_checker.checks.get('overall_status') == 'healthy' else 0,
            'mara_bet_uptime_seconds': health_checker.checks.get('uptime', {}).get('uptime_seconds', 0),
            'mara_bet_cpu_percent': health_checker.checks.get('system_resources', {}).get('cpu_percent', 0),
            'mara_bet_memory_percent': health_checker.checks.get('system_resources', {}).get('memory_percent', 0),
            'mara_bet_disk_percent': health_checker.checks.get('system_resources', {}).get('disk_percent', 0)
        }
        
        # Formato Prometheus
        prometheus_format = []
        for metric_name, metric_value in metrics.items():
            prometheus_format.append(f"# HELP {metric_name} MaraBet AI health metric")
            prometheus_format.append(f"# TYPE {metric_name} gauge")
            prometheus_format.append(f"{metric_name} {metric_value}")
        
        return '\n'.join(prometheus_format), 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        logger.error(f"Health metrics failed: {e}")
        return f"# ERROR: {str(e)}", 500, {'Content-Type': 'text/plain'}

if __name__ == "__main__":
    # Teste do health checker
    print("🧪 TESTANDO HEALTH CHECKER")
    print("=" * 40)
    
    # Executar todos os checks
    result = health_checker.run_all_checks()
    
    print(f"Status Geral: {result['overall_status']}")
    print(f"Timestamp: {result['timestamp']}")
    print("\nDetalhes dos Checks:")
    
    for check_name, check_result in result['checks'].items():
        status = check_result['status']
        message = check_result.get('message', 'N/A')
        print(f"  {check_name}: {status} - {message}")
    
    # Resumo
    summary = health_checker.get_health_summary()
    print(f"\nResumo:")
    print(f"  Checks saudáveis: {summary['healthy_checks']}/{summary['total_checks']}")
    print(f"  Percentual de saúde: {summary['health_percentage']:.1f}%")
