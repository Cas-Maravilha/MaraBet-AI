#!/usr/bin/env python3
"""
Gerenciador de Tarefas Celery para MaraBet AI
Script para gerenciar workers, monitorar tarefas e executar comandos
"""

import os
import sys
import argparse
import subprocess
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.celery_app import celery_app, get_task_info, get_active_tasks, get_worker_stats

class CeleryManager:
    """Gerenciador de tarefas Celery"""
    
    def __init__(self):
        self.celery_app = celery_app
    
    def start_worker(self, queue: str, concurrency: int = 1, loglevel: str = 'info'):
        """Inicia um worker para uma fila específica"""
        cmd = [
            'celery', '-A', 'tasks.celery_app', 'worker',
            '-Q', queue,
            '-l', loglevel,
            '--concurrency', str(concurrency)
        ]
        
        print(f"Iniciando worker para fila {queue} com {concurrency} processos...")
        subprocess.run(cmd)
    
    def start_beat(self):
        """Inicia o scheduler (beat)"""
        cmd = ['celery', '-A', 'tasks.celery_app', 'beat', '-l', 'info']
        
        print("Iniciando Celery Beat (scheduler)...")
        subprocess.run(cmd)
    
    def start_flower(self, port: int = 5555):
        """Inicia o Flower (monitoramento)"""
        cmd = [
            'celery', '-A', 'tasks.celery_app', 'flower',
            '--port', str(port)
        ]
        
        print(f"Iniciando Flower na porta {port}...")
        subprocess.run(cmd)
    
    def get_status(self):
        """Obtém status dos workers e tarefas"""
        try:
            # Status dos workers
            worker_stats = get_worker_stats()
            
            # Tarefas ativas
            active_tasks = get_active_tasks()
            
            # Tarefas agendadas
            scheduled_tasks = self.celery_app.control.inspect().scheduled()
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'workers': worker_stats,
                'active_tasks': active_tasks,
                'scheduled_tasks': scheduled_tasks
            }
            
            return status
            
        except Exception as e:
            print(f"Erro ao obter status: {e}")
            return None
    
    def get_task_result(self, task_id: str):
        """Obtém resultado de uma tarefa específica"""
        try:
            result = get_task_info(task_id)
            return {
                'task_id': task_id,
                'status': result.status,
                'result': result.result,
                'traceback': result.traceback
            }
        except Exception as e:
            return {'error': str(e)}
    
    def revoke_task(self, task_id: str, terminate: bool = False):
        """Cancela uma tarefa"""
        try:
            self.celery_app.control.revoke(task_id, terminate=terminate)
            return {'status': 'success', 'message': f'Tarefa {task_id} cancelada'}
        except Exception as e:
            return {'error': str(e)}
    
    def purge_queue(self, queue_name: str):
        """Limpa uma fila específica"""
        try:
            with self.celery_app.connection() as conn:
                conn.default_channel.queue_purge(queue_name)
            return {'status': 'success', 'message': f'Fila {queue_name} limpa'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_queue_length(self, queue_name: str):
        """Obtém tamanho de uma fila"""
        try:
            with self.celery_app.connection() as conn:
                length = conn.default_channel.queue_declare(queue_name, passive=True).message_count
            return {'queue': queue_name, 'length': length}
        except Exception as e:
            return {'error': str(e)}
    
    def list_queues(self):
        """Lista todas as filas"""
        try:
            with self.celery_app.connection() as conn:
                queues = conn.default_channel.queue_declare(passive=True)
            return {'queues': list(queues) if queues else []}
        except Exception as e:
            return {'error': str(e)}
    
    def execute_task(self, task_name: str, args: List = None, kwargs: Dict = None):
        """Executa uma tarefa específica"""
        try:
            if args is None:
                args = []
            if kwargs is None:
                kwargs = {}
            
            result = self.celery_app.send_task(task_name, args=args, kwargs=kwargs)
            return {
                'status': 'success',
                'task_id': result.id,
                'task_name': task_name
            }
        except Exception as e:
            return {'error': str(e)}
    
    def monitor_tasks(self, duration: int = 60):
        """Monitora tarefas por um período específico"""
        print(f"Monitorando tarefas por {duration} segundos...")
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            status = self.get_status()
            if status:
                print(f"\n--- Status em {datetime.now().strftime('%H:%M:%S')} ---")
                
                # Workers
                if status['workers']:
                    print("Workers:")
                    for worker, stats in status['workers'].items():
                        print(f"  {worker}: {stats.get('status', 'unknown')}")
                
                # Tarefas ativas
                if status['active_tasks']:
                    print("Tarefas ativas:")
                    for worker, tasks in status['active_tasks'].items():
                        print(f"  {worker}: {len(tasks)} tarefas")
                        for task in tasks:
                            print(f"    - {task['name']} ({task['id']})")
                
                # Tarefas agendadas
                if status['scheduled_tasks']:
                    print("Tarefas agendadas:")
                    for worker, tasks in status['scheduled_tasks'].items():
                        print(f"  {worker}: {len(tasks)} tarefas")
            
            time.sleep(10)
    
    def show_help(self):
        """Mostra ajuda do gerenciador"""
        help_text = """
MaraBet AI - Gerenciador de Tarefas Celery

Comandos disponíveis:
  start-worker <queue> [concurrency] [loglevel]  - Inicia worker para fila
  start-beat                                     - Inicia scheduler
  start-flower [port]                            - Inicia monitoramento
  status                                         - Mostra status dos workers
  task <task_id>                                 - Mostra resultado de tarefa
  revoke <task_id> [--terminate]                - Cancela tarefa
  purge <queue_name>                             - Limpa fila
  queue-length <queue_name>                      - Mostra tamanho da fila
  list-queues                                    - Lista todas as filas
  execute <task_name> [args] [kwargs]            - Executa tarefa
  monitor [duration]                             - Monitora tarefas
  help                                           - Mostra esta ajuda

Exemplos:
  python celery_manager.py start-worker ml_queue 2 info
  python celery_manager.py start-beat
  python celery_manager.py start-flower 5555
  python celery_manager.py status
  python celery_manager.py task abc123-def456-ghi789
  python celery_manager.py revoke abc123-def456-ghi789 --terminate
  python celery_manager.py purge ml_queue
  python celery_manager.py queue-length ml_queue
  python celery_manager.py list-queues
  python celery_manager.py execute tasks.ml_tasks.train_model --args '["random_forest", 39]'
  python celery_manager.py monitor 120
        """
        print(help_text)

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Gerenciador de Tarefas Celery')
    parser.add_argument('command', help='Comando a executar')
    parser.add_argument('args', nargs='*', help='Argumentos do comando')
    parser.add_argument('--terminate', action='store_true', help='Terminar tarefa imediatamente')
    
    args = parser.parse_args()
    
    manager = CeleryManager()
    
    if args.command == 'start-worker':
        queue = args.args[0] if args.args else 'default'
        concurrency = int(args.args[1]) if len(args.args) > 1 else 1
        loglevel = args.args[2] if len(args.args) > 2 else 'info'
        manager.start_worker(queue, concurrency, loglevel)
    
    elif args.command == 'start-beat':
        manager.start_beat()
    
    elif args.command == 'start-flower':
        port = int(args.args[0]) if args.args else 5555
        manager.start_flower(port)
    
    elif args.command == 'status':
        status = manager.get_status()
        if status:
            print(json.dumps(status, indent=2, default=str))
        else:
            print("Erro ao obter status")
    
    elif args.command == 'task':
        if not args.args:
            print("Erro: task_id é obrigatório")
            return
        result = manager.get_task_result(args.args[0])
        print(json.dumps(result, indent=2, default=str))
    
    elif args.command == 'revoke':
        if not args.args:
            print("Erro: task_id é obrigatório")
            return
        result = manager.revoke_task(args.args[0], args.terminate)
        print(json.dumps(result, indent=2, default=str))
    
    elif args.command == 'purge':
        if not args.args:
            print("Erro: queue_name é obrigatório")
            return
        result = manager.purge_queue(args.args[0])
        print(json.dumps(result, indent=2, default=str))
    
    elif args.command == 'queue-length':
        if not args.args:
            print("Erro: queue_name é obrigatório")
            return
        result = manager.get_queue_length(args.args[0])
        print(json.dumps(result, indent=2, default=str))
    
    elif args.command == 'list-queues':
        result = manager.list_queues()
        print(json.dumps(result, indent=2, default=str))
    
    elif args.command == 'execute':
        if not args.args:
            print("Erro: task_name é obrigatório")
            return
        task_name = args.args[0]
        task_args = json.loads(args.args[1]) if len(args.args) > 1 else []
        task_kwargs = json.loads(args.args[2]) if len(args.args) > 2 else {}
        result = manager.execute_task(task_name, task_args, task_kwargs)
        print(json.dumps(result, indent=2, default=str))
    
    elif args.command == 'monitor':
        duration = int(args.args[0]) if args.args else 60
        manager.monitor_tasks(duration)
    
    elif args.command == 'help':
        manager.show_help()
    
    else:
        print(f"Comando desconhecido: {args.command}")
        manager.show_help()

if __name__ == '__main__':
    main()
