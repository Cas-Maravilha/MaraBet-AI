"""
Configuração do Celery para MaraBet AI
Sistema de filas para processamento assíncrono de tarefas pesadas
"""

from celery import Celery
from celery.schedules import crontab
import os
import logging
from kombu import Queue, Exchange

logger = logging.getLogger(__name__)

# Configurações do Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# URL de conexão do Redis
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Configuração do Celery
celery_app = Celery(
    'marabet_ai',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'tasks.ml_tasks',
        'tasks.backtesting_tasks',
        'tasks.data_collection_tasks',
        'tasks.notification_tasks',
        'tasks.maintenance_tasks'
    ]
)

# Configurações do Celery
celery_app.conf.update(
    # Configurações básicas
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Configurações de worker
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    worker_max_tasks_per_child=1000,
    
    # Configurações de resultado
    result_expires=3600,  # 1 hora
    result_persistent=True,
    result_backend_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
    },
    
    # Configurações de retry
    task_default_retry_delay=60,  # 1 minuto
    task_max_retries=3,
    task_retry_jitter=True,
    
    # Configurações de timeout
    task_soft_time_limit=300,  # 5 minutos
    task_time_limit=600,       # 10 minutos
    
    # Configurações de filas
    task_routes={
        'tasks.ml_tasks.*': {'queue': 'ml_queue'},
        'tasks.backtesting_tasks.*': {'queue': 'backtesting_queue'},
        'tasks.data_collection_tasks.*': {'queue': 'data_queue'},
        'tasks.notification_tasks.*': {'queue': 'notification_queue'},
        'tasks.maintenance_tasks.*': {'queue': 'maintenance_queue'},
    },
    
    # Definição de filas
    task_queues=(
        Queue('ml_queue', Exchange('ml_exchange'), routing_key='ml'),
        Queue('backtesting_queue', Exchange('backtesting_exchange'), routing_key='backtesting'),
        Queue('data_queue', Exchange('data_exchange'), routing_key='data'),
        Queue('notification_queue', Exchange('notification_exchange'), routing_key='notification'),
        Queue('maintenance_queue', Exchange('maintenance_exchange'), routing_key='maintenance'),
        Queue('default', Exchange('default'), routing_key='default'),
    ),
    
    # Configurações de monitoramento
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Configurações de beat (agendamento)
    beat_schedule={
        # Treinamento de modelos diário
        'train-models-daily': {
            'task': 'tasks.ml_tasks.train_all_models',
            'schedule': crontab(hour=2, minute=0),  # 2:00 AM UTC
            'options': {'queue': 'ml_queue'}
        },
        
        # Coleta de dados a cada 15 minutos
        'collect-odds-data': {
            'task': 'tasks.data_collection_tasks.collect_odds_data',
            'schedule': crontab(minute='*/15'),  # A cada 15 minutos
            'options': {'queue': 'data_queue'}
        },
        
        # Coleta de estatísticas a cada hora
        'collect-stats-data': {
            'task': 'tasks.data_collection_tasks.collect_stats_data',
            'schedule': crontab(minute=0),  # A cada hora
            'options': {'queue': 'data_queue'}
        },
        
        # Backtesting semanal
        'weekly-backtesting': {
            'task': 'tasks.backtesting_tasks.run_weekly_backtesting',
            'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Segunda 3:00 AM UTC
            'options': {'queue': 'backtesting_queue'}
        },
        
        # Limpeza de cache diária
        'cleanup-cache': {
            'task': 'tasks.maintenance_tasks.cleanup_cache',
            'schedule': crontab(hour=1, minute=0),  # 1:00 AM UTC
            'options': {'queue': 'maintenance_queue'}
        },
        
        # Limpeza de logs diária
        'cleanup-logs': {
            'task': 'tasks.maintenance_tasks.cleanup_logs',
            'schedule': crontab(hour=1, minute=30),  # 1:30 AM UTC
            'options': {'queue': 'maintenance_queue'}
        },
        
        # Relatório de performance semanal
        'weekly-performance-report': {
            'task': 'tasks.notification_tasks.send_weekly_report',
            'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Segunda 9:00 AM UTC
            'options': {'queue': 'notification_queue'}
        },
    },
    
    # Configurações de logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
)

# Configurações específicas por ambiente
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    # Configurações de produção
    celery_app.conf.update(
        worker_concurrency=4,
        worker_max_memory_per_child=200000,  # 200MB
        task_compression='gzip',
        result_compression='gzip',
        broker_connection_retry_on_startup=True,
        broker_connection_retry=True,
        broker_connection_max_retries=10,
    )
elif ENVIRONMENT == 'staging':
    # Configurações de staging
    celery_app.conf.update(
        worker_concurrency=2,
        worker_max_memory_per_child=150000,  # 150MB
        task_compression='gzip',
        result_compression='gzip',
    )
else:
    # Configurações de desenvolvimento
    celery_app.conf.update(
        worker_concurrency=1,
        worker_max_memory_per_child=100000,  # 100MB
        task_compression=None,
        result_compression=None,
    )

# Configurações de monitoramento
celery_app.conf.update(
    # Flower para monitoramento (opcional)
    flower_basic_auth=['admin:marabet2024'],
    flower_port=5555,
    
    # Configurações de métricas
    worker_send_task_events=True,
    task_send_sent_event=True,
    task_track_started=True,
    task_ignore_result=False,
)

# Funções de conveniência
def get_celery_app():
    """Retorna instância do Celery"""
    return celery_app

def get_task_info(task_id: str):
    """Obtém informações de uma tarefa"""
    return celery_app.AsyncResult(task_id)

def revoke_task(task_id: str, terminate: bool = False):
    """Cancela uma tarefa"""
    celery_app.control.revoke(task_id, terminate=terminate)

def get_active_tasks():
    """Obtém lista de tarefas ativas"""
    return celery_app.control.inspect().active()

def get_scheduled_tasks():
    """Obtém lista de tarefas agendadas"""
    return celery_app.control.inspect().scheduled()

def get_worker_stats():
    """Obtém estatísticas dos workers"""
    return celery_app.control.inspect().stats()

def purge_queue(queue_name: str):
    """Limpa uma fila específica"""
    with celery_app.connection() as conn:
        conn.default_channel.queue_purge(queue_name)

def get_queue_length(queue_name: str):
    """Obtém tamanho de uma fila"""
    with celery_app.connection() as conn:
        return conn.default_channel.queue_declare(queue_name, passive=True).message_count

# Configurações de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
)

logger.info(f"Celery configurado para ambiente: {ENVIRONMENT}")
logger.info(f"Redis URL: {REDIS_URL}")

if __name__ == '__main__':
    celery_app.start()
