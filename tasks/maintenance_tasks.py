"""
Tarefas de Manutenção para MaraBet AI
Processamento assíncrono de limpeza e otimização do sistema
"""

from celery import current_task
from tasks.celery_app import celery_app
from cache.redis_cache import cache, cache_stats, get_stats
import logging
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import traceback
import sqlite3

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks.maintenance_tasks.cleanup_cache')
def cleanup_cache(self):
    """
    Limpa cache Redis de dados antigos
    
    Returns:
        Dict com resumo da limpeza
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando limpeza do cache', 'progress': 0}
        )
        
        logger.info("Iniciando limpeza do cache Redis")
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Analisando cache', 'progress': 20}
        )
        
        # Obtém estatísticas do cache
        cache_stats_before = cache.get_stats()
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Limpando dados antigos', 'progress': 40}
        )
        
        # Limpa dados antigos por tipo
        cleanup_results = {}
        
        # Limpa odds antigas (mais de 1 hora)
        odds_cleaned = cache.clear_type('odds')
        cleanup_results['odds'] = odds_cleaned
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Limpando estatísticas antigas', 'progress': 60}
        )
        
        # Limpa estatísticas antigas (mais de 24 horas)
        stats_cleaned = cache.clear_type('stats')
        cleanup_results['stats'] = stats_cleaned
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Limpando previsões antigas', 'progress': 80}
        )
        
        # Limpa previsões antigas (mais de 2 horas)
        predictions_cleaned = cache.clear_type('predictions')
        cleanup_results['predictions'] = predictions_cleaned
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Finalizando limpeza', 'progress': 90}
        )
        
        # Obtém estatísticas após limpeza
        cache_stats_after = cache.get_stats()
        
        # Calcula resumo
        total_cleaned = sum(cleanup_results.values())
        memory_freed = cache_stats_before.get('used_memory', '0B') if cache_stats_before else '0B'
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Limpeza do cache concluída', 'progress': 100}
        )
        
        logger.info(f"Limpeza do cache concluída: {total_cleaned} chaves removidas")
        
        return {
            'status': 'success',
            'total_keys_cleaned': total_cleaned,
            'cleanup_by_type': cleanup_results,
            'memory_before': memory_freed,
            'memory_after': cache_stats_after.get('used_memory', '0B') if cache_stats_after else '0B'
        }
        
    except Exception as e:
        logger.error(f"Erro na limpeza do cache: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro na limpeza', 'error': str(e)}
        )
        
        raise

@celery_app.task(bind=True, name='tasks.maintenance_tasks.cleanup_logs')
def cleanup_logs(self):
    """
    Limpa logs antigos do sistema
    
    Returns:
        Dict com resumo da limpeza
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando limpeza de logs', 'progress': 0}
        )
        
        logger.info("Iniciando limpeza de logs")
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Analisando arquivos de log', 'progress': 20}
        )
        
        # Diretórios de logs
        log_dirs = ['logs', 'app/logs', '/var/log/marabet']
        
        cleanup_results = {}
        total_files_removed = 0
        total_size_freed = 0
        
        for log_dir in log_dirs:
            if not os.path.exists(log_dir):
                continue
            
            # Atualiza progresso
            self.update_state(
                state='PROGRESS',
                meta={'status': f'Limpando logs em {log_dir}', 'progress': 40}
            )
            
            # Limpa logs antigos (mais de 7 dias)
            cutoff_date = datetime.now() - timedelta(days=7)
            dir_results = self._cleanup_log_directory(log_dir, cutoff_date)
            
            cleanup_results[log_dir] = dir_results
            total_files_removed += dir_results['files_removed']
            total_size_freed += dir_results['size_freed']
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Comprimindo logs atuais', 'progress': 80}
        )
        
        # Comprime logs atuais (mais de 1 dia)
        compression_results = self._compress_old_logs()
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Limpeza de logs concluída', 'progress': 100}
        )
        
        logger.info(f"Limpeza de logs concluída: {total_files_removed} arquivos removidos")
        
        return {
            'status': 'success',
            'total_files_removed': total_files_removed,
            'total_size_freed': total_size_freed,
            'cleanup_by_directory': cleanup_results,
            'compression_results': compression_results
        }
        
    except Exception as e:
        logger.error(f"Erro na limpeza de logs: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro na limpeza', 'error': str(e)}
        )
        
        raise

def _cleanup_log_directory(self, log_dir: str, cutoff_date: datetime) -> Dict:
    """
    Limpa diretório de logs
    
    Args:
        log_dir: Diretório de logs
        cutoff_date: Data de corte
    
    Returns:
        Dict com resultados da limpeza
    """
    files_removed = 0
    size_freed = 0
    
    try:
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            
            if os.path.isfile(filepath) and filename.endswith('.log'):
                # Verifica idade do arquivo
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_mtime < cutoff_date:
                    # Remove arquivo antigo
                    file_size = os.path.getsize(filepath)
                    os.remove(filepath)
                    
                    files_removed += 1
                    size_freed += file_size
                    
                    logger.debug(f"Arquivo de log removido: {filepath}")
    
    except Exception as e:
        logger.error(f"Erro ao limpar diretório {log_dir}: {e}")
    
    return {
        'files_removed': files_removed,
        'size_freed': size_freed
    }

def _compress_old_logs(self) -> Dict:
    """
    Comprime logs antigos (mais de 1 dia)
    
    Returns:
        Dict com resultados da compressão
    """
    import gzip
    
    files_compressed = 0
    size_saved = 0
    
    try:
        # Diretórios de logs
        log_dirs = ['logs', 'app/logs']
        cutoff_date = datetime.now() - timedelta(days=1)
        
        for log_dir in log_dirs:
            if not os.path.exists(log_dir):
                continue
            
            for filename in os.listdir(log_dir):
                filepath = os.path.join(log_dir, filename)
                
                if os.path.isfile(filepath) and filename.endswith('.log'):
                    # Verifica se já está comprimido
                    if filename.endswith('.gz'):
                        continue
                    
                    # Verifica idade do arquivo
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if file_mtime < cutoff_date:
                        # Comprime arquivo
                        original_size = os.path.getsize(filepath)
                        
                        with open(filepath, 'rb') as f_in:
                            with gzip.open(f"{filepath}.gz", 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        
                        # Remove arquivo original
                        os.remove(filepath)
                        
                        # Calcula espaço economizado
                        compressed_size = os.path.getsize(f"{filepath}.gz")
                        space_saved = original_size - compressed_size
                        
                        files_compressed += 1
                        size_saved += space_saved
                        
                        logger.debug(f"Log comprimido: {filepath}")
    
    except Exception as e:
        logger.error(f"Erro ao comprimir logs: {e}")
    
    return {
        'files_compressed': files_compressed,
        'size_saved': size_saved
    }

@celery_app.task(bind=True, name='tasks.maintenance_tasks.optimize_database')
def optimize_database(self):
    """
    Otimiza banco de dados SQLite
    
    Returns:
        Dict com resumo da otimização
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando otimização do banco', 'progress': 0}
        )
        
        logger.info("Iniciando otimização do banco de dados")
        
        from armazenamento.banco_de_dados import DatabaseManager
        
        db = DatabaseManager()
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Analisando banco de dados', 'progress': 20}
        )
        
        # Obtém tamanho antes da otimização
        db_path = db.get_database_path()
        size_before = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Executando VACUUM', 'progress': 40}
        )
        
        # Executa VACUUM para reorganizar banco
        db.execute_query("VACUUM")
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Executando ANALYZE', 'progress': 60}
        )
        
        # Executa ANALYZE para atualizar estatísticas
        db.execute_query("ANALYZE")
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Limpando dados antigos', 'progress': 80}
        )
        
        # Remove dados antigos
        cleanup_results = self._cleanup_old_data(db)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Finalizando otimização', 'progress': 90}
        )
        
        # Obtém tamanho após otimização
        size_after = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        space_freed = size_before - size_after
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Otimização concluída', 'progress': 100}
        )
        
        logger.info(f"Otimização do banco concluída: {space_freed} bytes liberados")
        
        return {
            'status': 'success',
            'size_before': size_before,
            'size_after': size_after,
            'space_freed': space_freed,
            'cleanup_results': cleanup_results
        }
        
    except Exception as e:
        logger.error(f"Erro na otimização do banco: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro na otimização', 'error': str(e)}
        )
        
        raise

def _cleanup_old_data(self, db: DatabaseManager) -> Dict:
    """
    Remove dados antigos do banco
    
    Args:
        db: Instância do banco de dados
    
    Returns:
        Dict com resultados da limpeza
    """
    cleanup_results = {}
    
    try:
        # Remove logs antigos (mais de 30 dias)
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # Limpa logs de aplicação
        logs_query = "DELETE FROM application_logs WHERE created_at < ?"
        logs_result = db.execute_query(logs_query, (cutoff_date,))
        cleanup_results['application_logs'] = db.cursor.rowcount if hasattr(db, 'cursor') else 0
        
        # Limpa sessões antigas (mais de 7 dias)
        sessions_cutoff = datetime.now() - timedelta(days=7)
        sessions_query = "DELETE FROM user_sessions WHERE last_activity < ?"
        sessions_result = db.execute_query(sessions_query, (sessions_cutoff,))
        cleanup_results['user_sessions'] = db.cursor.rowcount if hasattr(db, 'cursor') else 0
        
        # Limpa cache antigo (mais de 1 dia)
        cache_cutoff = datetime.now() - timedelta(days=1)
        cache_query = "DELETE FROM cache_data WHERE expires_at < ?"
        cache_result = db.execute_query(cache_query, (cache_cutoff,))
        cleanup_results['cache_data'] = db.cursor.rowcount if hasattr(db, 'cursor') else 0
        
        # Limpa métricas antigas (mais de 90 dias)
        metrics_cutoff = datetime.now() - timedelta(days=90)
        metrics_query = "DELETE FROM performance_metrics WHERE created_at < ?"
        metrics_result = db.execute_query(metrics_query, (metrics_cutoff,))
        cleanup_results['performance_metrics'] = db.cursor.rowcount if hasattr(db, 'cursor') else 0
        
    except Exception as e:
        logger.error(f"Erro na limpeza de dados antigos: {e}")
    
    return cleanup_results

@celery_app.task(bind=True, name='tasks.maintenance_tasks.backup_database')
def backup_database(self):
    """
    Cria backup do banco de dados
    
    Returns:
        Dict com informações do backup
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando backup do banco', 'progress': 0}
        )
        
        logger.info("Iniciando backup do banco de dados")
        
        from armazenamento.banco_de_dados import DatabaseManager
        
        db = DatabaseManager()
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Criando diretório de backup', 'progress': 20}
        )
        
        # Cria diretório de backup
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Executando backup', 'progress': 50}
        )
        
        # Gera nome do arquivo de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"marabet_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Executa backup
        db.backup_database(backup_path)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Comprimindo backup', 'progress': 80}
        )
        
        # Comprime backup
        import gzip
        compressed_filename = f"{backup_filename}.gz"
        compressed_path = os.path.join(backup_dir, compressed_filename)
        
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove arquivo não comprimido
        os.remove(backup_path)
        
        # Obtém tamanho do backup
        backup_size = os.path.getsize(compressed_path)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Backup concluído', 'progress': 100}
        )
        
        logger.info(f"Backup do banco concluído: {compressed_path}")
        
        return {
            'status': 'success',
            'backup_path': compressed_path,
            'backup_size': backup_size,
            'backup_filename': compressed_filename,
            'created_at': datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Erro no backup do banco: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro no backup', 'error': str(e)}
        )
        
        raise

@celery_app.task(bind=True, name='tasks.maintenance_tasks.update_system_stats')
def update_system_stats(self):
    """
    Atualiza estatísticas do sistema
    
    Returns:
        Dict com estatísticas atualizadas
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Atualizando estatísticas do sistema', 'progress': 0}
        )
        
        logger.info("Atualizando estatísticas do sistema")
        
        from armazenamento.banco_de_dados import DatabaseManager
        
        db = DatabaseManager()
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Coletando métricas', 'progress': 30}
        )
        
        # Coleta métricas do sistema
        stats = self._collect_system_metrics(db)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Salvando estatísticas', 'progress': 70}
        )
        
        # Salva estatísticas
        self._save_system_stats(db, stats)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Estatísticas atualizadas', 'progress': 100}
        )
        
        logger.info("Estatísticas do sistema atualizadas")
        
        return {
            'status': 'success',
            'stats': stats,
            'updated_at': datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar estatísticas: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro na atualização', 'error': str(e)}
        )
        
        raise

def _collect_system_metrics(self, db: DatabaseManager) -> Dict:
    """
    Coleta métricas do sistema
    
    Args:
        db: Instância do banco de dados
    
    Returns:
        Dict com métricas coletadas
    """
    stats = {}
    
    try:
        # Conta registros por tabela
        tables = ['matches', 'predictions', 'value_bets', 'ml_models', 'backtesting_results']
        
        for table in tables:
            count_query = f"SELECT COUNT(*) as count FROM {table}"
            result = db.execute_query(count_query)
            stats[f'{table}_count'] = result[0]['count'] if result else 0
        
        # Estatísticas de performance dos modelos
        models_query = """
            SELECT 
                model_type,
                COUNT(*) as total_models,
                AVG(CAST(JSON_EXTRACT(metrics, '$.accuracy') AS REAL)) as avg_accuracy,
                AVG(CAST(JSON_EXTRACT(metrics, '$.f1_score') AS REAL)) as avg_f1_score
            FROM ml_models 
            WHERE status = 'trained'
            GROUP BY model_type
        """
        models_result = db.execute_query(models_query)
        stats['model_performance'] = {row['model_type']: row for row in models_result}
        
        # Estatísticas de backtesting
        backtesting_query = """
            SELECT 
                strategy_name,
                COUNT(*) as total_tests,
                AVG(roi) as avg_roi,
                AVG(win_rate) as avg_win_rate,
                MAX(roi) as max_roi,
                MIN(roi) as min_roi
            FROM backtesting_results 
            GROUP BY strategy_name
        """
        backtesting_result = db.execute_query(backtesting_query)
        stats['backtesting_performance'] = {row['strategy_name']: row for row in backtesting_result}
        
        # Estatísticas de value bets
        value_bets_query = """
            SELECT 
                COUNT(*) as total_value_bets,
                AVG(value) as avg_value,
                MAX(value) as max_value,
                COUNT(CASE WHEN value > 0.1 THEN 1 END) as high_value_bets
            FROM value_bets
        """
        value_bets_result = db.execute_query(value_bets_query)
        stats['value_bets_stats'] = value_bets_result[0] if value_bets_result else {}
        
        # Estatísticas de cache
        cache_stats = cache.get_stats()
        stats['cache_stats'] = cache_stats
        
        # Timestamp da coleta
        stats['collected_at'] = datetime.now()
        
    except Exception as e:
        logger.error(f"Erro ao coletar métricas do sistema: {e}")
    
    return stats

def _save_system_stats(self, db: DatabaseManager, stats: Dict):
    """
    Salva estatísticas do sistema
    
    Args:
        db: Instância do banco de dados
        stats: Estatísticas coletadas
    """
    try:
        # Salva estatísticas gerais
        db.execute_query("""
            INSERT INTO system_stats 
            (stats_data, collected_at)
            VALUES (?, ?)
        """, (json.dumps(stats, default=str), stats['collected_at']))
        
        # Mantém apenas últimas 30 entradas
        db.execute_query("""
            DELETE FROM system_stats 
            WHERE id NOT IN (
                SELECT id FROM system_stats 
                ORDER BY collected_at DESC 
                LIMIT 30
            )
        """)
        
    except Exception as e:
        logger.error(f"Erro ao salvar estatísticas do sistema: {e}")

@celery_app.task(bind=True, name='tasks.maintenance_tasks.health_check')
def health_check(self):
    """
    Executa verificação de saúde do sistema
    
    Returns:
        Dict com status de saúde
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Executando verificação de saúde', 'progress': 0}
        )
        
        logger.info("Executando verificação de saúde do sistema")
        
        health_status = {
            'overall_status': 'healthy',
            'checks': {},
            'timestamp': datetime.now()
        }
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Verificando banco de dados', 'progress': 20}
        )
        
        # Verifica banco de dados
        try:
            from armazenamento.banco_de_dados import DatabaseManager
            db = DatabaseManager()
            db.test_connection()
            health_status['checks']['database'] = {'status': 'healthy', 'message': 'Conexão OK'}
        except Exception as e:
            health_status['checks']['database'] = {'status': 'unhealthy', 'message': str(e)}
            health_status['overall_status'] = 'unhealthy'
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Verificando cache Redis', 'progress': 40}
        )
        
        # Verifica cache Redis
        try:
            cache_stats = cache.get_stats()
            health_status['checks']['redis'] = {'status': 'healthy', 'message': 'Cache OK'}
        except Exception as e:
            health_status['checks']['redis'] = {'status': 'unhealthy', 'message': str(e)}
            health_status['overall_status'] = 'unhealthy'
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Verificando APIs externas', 'progress': 60}
        )
        
        # Verifica APIs externas
        try:
            import requests
            import os
            
            # Testa API Football
            api_key = os.getenv('API_FOOTBALL_KEY')
            if api_key:
                response = requests.get(
                    'https://api-football-v1.p.rapidapi.com/status',
                    headers={'X-RapidAPI-Key': api_key},
                    timeout=10
                )
                if response.status_code == 200:
                    health_status['checks']['api_football'] = {'status': 'healthy', 'message': 'API OK'}
                else:
                    health_status['checks']['api_football'] = {'status': 'unhealthy', 'message': f'Status {response.status_code}'}
            else:
                health_status['checks']['api_football'] = {'status': 'warning', 'message': 'API key não configurada'}
        except Exception as e:
            health_status['checks']['api_football'] = {'status': 'unhealthy', 'message': str(e)}
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Verificando espaço em disco', 'progress': 80}
        )
        
        # Verifica espaço em disco
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            free_percent = (free / total) * 100
            
            if free_percent > 20:
                health_status['checks']['disk_space'] = {'status': 'healthy', 'message': f'{free_percent:.1f}% livre'}
            elif free_percent > 10:
                health_status['checks']['disk_space'] = {'status': 'warning', 'message': f'{free_percent:.1f}% livre'}
            else:
                health_status['checks']['disk_space'] = {'status': 'unhealthy', 'message': f'{free_percent:.1f}% livre'}
                health_status['overall_status'] = 'unhealthy'
        except Exception as e:
            health_status['checks']['disk_space'] = {'status': 'unhealthy', 'message': str(e)}
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Verificação de saúde concluída', 'progress': 100}
        )
        
        logger.info(f"Verificação de saúde concluída: {health_status['overall_status']}")
        
        return {
            'status': 'success',
            'health_status': health_status
        }
        
    except Exception as e:
        logger.error(f"Erro na verificação de saúde: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro na verificação', 'error': str(e)}
        )
        
        raise
