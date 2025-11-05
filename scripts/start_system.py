#!/usr/bin/env python3
"""
Script de Inicialização do Sistema MaraBet AI
Inicia todos os componentes: Redis, Celery Workers, Beat, Flower e Aplicação
"""

import os
import sys
import time
import subprocess
import signal
import threading
from datetime import datetime
from typing import List, Dict

class SystemManager:
    """Gerenciador do sistema MaraBet AI"""
    
    def __init__(self):
        self.processes = {}
        self.running = True
        
        # Configurações
        self.config = {
            'redis_host': os.getenv('REDIS_HOST', 'localhost'),
            'redis_port': int(os.getenv('REDIS_PORT', 6379)),
            'redis_db': int(os.getenv('REDIS_DB', 0)),
            'flower_port': int(os.getenv('FLOWER_PORT', 5555)),
            'dashboard_port': int(os.getenv('DASHBOARD_PORT', 8000),
            'api_port': int(os.getenv('API_PORT', 5000)
        }
        
        # Workers configurados
        self.workers = [
            {'name': 'ml-worker', 'queue': 'ml_queue', 'concurrency': 2},
            {'name': 'data-worker', 'queue': 'data_queue', 'concurrency': 3},
            {'name': 'backtesting-worker', 'queue': 'backtesting_queue', 'concurrency': 1},
            {'name': 'notification-worker', 'queue': 'notification_queue', 'concurrency': 2},
            {'name': 'maintenance-worker', 'queue': 'maintenance_queue', 'concurrency': 1}
        ]
    
    def log(self, message: str, level: str = 'INFO'):
        """Log com timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def check_redis_connection(self) -> bool:
        """Verifica conexão com Redis"""
        try:
            import redis
            r = redis.Redis(
                host=self.config['redis_host'],
                port=self.config['redis_port'],
                db=self.config['redis_db']
            )
            r.ping()
            return True
        except Exception as e:
            self.log(f"Erro ao conectar com Redis: {e}", 'ERROR')
            return False
    
    def start_redis(self):
        """Inicia Redis (se não estiver rodando)"""
        self.log("Verificando Redis...")
        
        if self.check_redis_connection():
            self.log("Redis já está rodando")
            return True
        
        self.log("Iniciando Redis...")
        try:
            # Tenta iniciar Redis via Docker
            result = subprocess.run([
                'docker', 'run', '-d',
                '--name', 'marabet-redis',
                '-p', f"{self.config['redis_port']}:6379",
                'redis:7-alpine'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Redis iniciado via Docker")
                time.sleep(3)  # Aguarda inicialização
                return self.check_redis_connection()
            else:
                self.log(f"Erro ao iniciar Redis via Docker: {result.stderr}", 'ERROR')
                return False
                
        except Exception as e:
            self.log(f"Erro ao iniciar Redis: {e}", 'ERROR')
            return False
    
    def start_worker(self, worker_config: Dict):
        """Inicia um worker Celery"""
        name = worker_config['name']
        queue = worker_config['queue']
        concurrency = worker_config['concurrency']
        
        self.log(f"Iniciando worker {name} para fila {queue}...")
        
        try:
            cmd = [
                'celery', '-A', 'tasks.celery_app', 'worker',
                '-Q', queue,
                '-l', 'info',
                '--concurrency', str(concurrency),
                '--hostname', f"{name}@%h"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[name] = process
            self.log(f"Worker {name} iniciado (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.log(f"Erro ao iniciar worker {name}: {e}", 'ERROR')
            return False
    
    def start_beat(self):
        """Inicia Celery Beat (scheduler)"""
        self.log("Iniciando Celery Beat...")
        
        try:
            cmd = ['celery', '-A', 'tasks.celery_app', 'beat', '-l', 'info']
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes['beat'] = process
            self.log(f"Celery Beat iniciado (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.log(f"Erro ao iniciar Celery Beat: {e}", 'ERROR')
            return False
    
    def start_flower(self):
        """Inicia Flower (monitoramento)"""
        self.log("Iniciando Flower...")
        
        try:
            cmd = [
                'celery', '-A', 'tasks.celery_app', 'flower',
                '--port', str(self.config['flower_port'])
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes['flower'] = process
            self.log(f"Flower iniciado (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.log(f"Erro ao iniciar Flower: {e}", 'ERROR')
            return False
    
    def start_dashboard(self):
        """Inicia dashboard FastAPI"""
        self.log("Iniciando Dashboard...")
        
        try:
            cmd = ['python', 'run_dashboard.py']
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes['dashboard'] = process
            self.log(f"Dashboard iniciado (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.log(f"Erro ao iniciar Dashboard: {e}", 'ERROR')
            return False
    
    def start_api(self):
        """Inicia API Flask"""
        self.log("Iniciando API...")
        
        try:
            cmd = ['python', 'app.py']
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes['api'] = process
            self.log(f"API iniciada (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.log(f"Erro ao iniciar API: {e}", 'ERROR')
            return False
    
    def monitor_processes(self):
        """Monitora processos em execução"""
        while self.running:
            for name, process in list(self.processes.items()):
                if process.poll() is not None:
                    self.log(f"Processo {name} terminou inesperadamente", 'WARNING')
                    del self.processes[name]
            
            time.sleep(5)
    
    def start_all(self):
        """Inicia todo o sistema"""
        self.log("🚀 Iniciando Sistema MaraBet AI...")
        self.log("=" * 60)
        
        # 1. Inicia Redis
        if not self.start_redis():
            self.log("Falha ao iniciar Redis. Abortando...", 'ERROR')
            return False
        
        # 2. Inicia workers
        for worker_config in self.workers:
            if not self.start_worker(worker_config):
                self.log(f"Falha ao iniciar worker {worker_config['name']}", 'WARNING')
        
        # 3. Inicia Beat
        if not self.start_beat():
            self.log("Falha ao iniciar Celery Beat", 'WARNING')
        
        # 4. Inicia Flower
        if not self.start_flower():
            self.log("Falha ao iniciar Flower", 'WARNING')
        
        # 5. Inicia Dashboard
        if not self.start_dashboard():
            self.log("Falha ao iniciar Dashboard", 'WARNING')
        
        # 6. Inicia API
        if not self.start_api():
            self.log("Falha ao iniciar API", 'WARNING')
        
        # 7. Inicia monitoramento
        monitor_thread = threading.Thread(target=self.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        self.log("✅ Sistema iniciado com sucesso!")
        self.log("=" * 60)
        self.log("🌐 Acessos disponíveis:")
        self.log(f"  • Dashboard: http://localhost:{self.config['dashboard_port']}")
        self.log(f"  • API: http://localhost:{self.config['api_port']}")
        self.log(f"  • Flower: http://localhost:{self.config['flower_port']}")
        self.log("=" * 60)
        
        return True
    
    def stop_all(self):
        """Para todo o sistema"""
        self.log("🛑 Parando Sistema MaraBet AI...")
        
        self.running = False
        
        for name, process in self.processes.items():
            try:
                self.log(f"Parando {name}...")
                process.terminate()
                process.wait(timeout=10)
                self.log(f"{name} parado")
            except subprocess.TimeoutExpired:
                self.log(f"Forçando parada de {name}...")
                process.kill()
            except Exception as e:
                self.log(f"Erro ao parar {name}: {e}", 'ERROR')
        
        self.processes.clear()
        self.log("✅ Sistema parado")
    
    def status(self):
        """Mostra status do sistema"""
        self.log("📊 Status do Sistema MaraBet AI")
        self.log("=" * 60)
        
        # Status Redis
        redis_status = "✅" if self.check_redis_connection() else "❌"
        self.log(f"Redis: {redis_status}")
        
        # Status processos
        for name, process in self.processes.items():
            status = "✅" if process.poll() is None else "❌"
            self.log(f"{name}: {status}")
        
        self.log("=" * 60)
    
    def signal_handler(self, signum, frame):
        """Handler para sinais do sistema"""
        self.log(f"Recebido sinal {signum}. Parando sistema...")
        self.stop_all()
        sys.exit(0)

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciador do Sistema MaraBet AI')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'restart'], 
                       help='Comando a executar')
    
    args = parser.parse_args()
    
    manager = SystemManager()
    
    # Configura handlers de sinal
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    if args.command == 'start':
        if manager.start_all():
            try:
                # Mantém o sistema rodando
                while manager.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                manager.stop_all()
    
    elif args.command == 'stop':
        manager.stop_all()
    
    elif args.command == 'status':
        manager.status()
    
    elif args.command == 'restart':
        manager.stop_all()
        time.sleep(2)
        manager.start_all()

if __name__ == '__main__':
    main()
