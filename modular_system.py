"""
SISTEMA MODULAR INTEGRADO - MaraBet AI
Arquitetura completa com 4 camadas: Coleta, Armazenamento, Processamento e Apresentação
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import threading
import queue
import schedule

# Importa todas as camadas
from data_collection_layer import DataCollectionManager, APIFootballCollector, TheOddsAPICollector, WebScrapingCollector
from storage_layer import StorageManager, PostgreSQLStorage, RedisStorage, MongoDBStorage, DatabaseConfig, StorageRecord
from processing_layer import ProcessingManager, MatchDataProcessor, OddsDataProcessor, MatchPredictionModel, ValueBettingModel
from presentation_layer import PresentationManager, DashboardData, Notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemConfig:
    """Configuração do sistema"""
    # Configurações de coleta
    api_football_key: str
    odds_api_key: str
    
    # Configurações de armazenamento
    postgres_config: DatabaseConfig
    redis_config: DatabaseConfig
    mongo_config: DatabaseConfig
    
    # Configurações de processamento
    model_save_path: str = "models/"
    
    # Configurações de apresentação
    dashboard_port: int = 5000
    api_port: int = 5001
    
    # Configurações gerais
    data_collection_interval: int = 300  # 5 minutos
    processing_interval: int = 600  # 10 minutos
    cleanup_interval: int = 3600  # 1 hora

class ModularSystem:
    """
    Sistema Modular Integrado MaraBet AI
    Gerencia todas as 4 camadas da arquitetura
    """
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self.is_running = False
        
        # Inicializa gerenciadores das camadas
        self.data_collection = DataCollectionManager()
        self.storage = StorageManager()
        self.processing = ProcessingManager()
        self.presentation = PresentationManager()
        
        # Fila de dados para processamento
        self.data_queue = queue.Queue()
        
        # Threads de processamento
        self.collection_thread = None
        self.processing_thread = None
        self.cleanup_thread = None
        
        # Estatísticas do sistema
        self.stats = {
            'data_collected': 0,
            'data_processed': 0,
            'predictions_made': 0,
            'notifications_sent': 0,
            'errors': 0,
            'start_time': None
        }
    
    def initialize(self) -> bool:
        """Inicializa o sistema"""
        try:
            logger.info("Inicializando sistema modular MaraBet AI")
            
            # Inicializa camada de coleta
            self._initialize_data_collection()
            
            # Inicializa camada de armazenamento
            self._initialize_storage()
            
            # Inicializa camada de processamento
            self._initialize_processing()
            
            # Inicializa camada de apresentação
            self._initialize_presentation()
            
            logger.info("Sistema inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            return False
    
    def _initialize_data_collection(self):
        """Inicializa camada de coleta"""
        logger.info("Inicializando camada de coleta")
        
        # Adiciona coletores
        api_football = APIFootballCollector(self.config.api_football_key)
        odds_api = TheOddsAPICollector(self.config.odds_api_key)
        web_scraper = WebScrapingCollector("https://example.com")
        
        self.data_collection.add_collector("api_football", api_football)
        self.data_collection.add_collector("odds_api", odds_api)
        self.data_collection.add_collector("web_scraper", web_scraper)
        
        logger.info("Camada de coleta inicializada")
    
    def _initialize_storage(self):
        """Inicializa camada de armazenamento"""
        logger.info("Inicializando camada de armazenamento")
        
        # Cria armazenamentos
        postgres_storage = PostgreSQLStorage(self.config.postgres_config)
        redis_storage = RedisStorage(self.config.redis_config)
        mongo_storage = MongoDBStorage(self.config.mongo_config)
        
        # Adiciona armazenamentos
        self.storage.add_storage("postgresql", postgres_storage)
        self.storage.add_storage("redis", redis_storage)
        self.storage.add_storage("mongodb", mongo_storage)
        
        # Conecta
        if not self.storage.connect_all():
            raise Exception("Falha na conexão com armazenamentos")
        
        logger.info("Camada de armazenamento inicializada")
    
    def _initialize_processing(self):
        """Inicializa camada de processamento"""
        logger.info("Inicializando camada de processamento")
        
        # Adiciona processadores
        match_processor = MatchDataProcessor()
        odds_processor = OddsDataProcessor()
        
        self.processing.add_processor("match", match_processor)
        self.processing.add_processor("odds", odds_processor)
        
        # Adiciona modelos
        match_model = MatchPredictionModel()
        value_model = ValueBettingModel()
        
        self.processing.add_model("match_prediction", match_model)
        self.processing.add_model("value_betting", value_model)
        
        logger.info("Camada de processamento inicializada")
    
    def _initialize_presentation(self):
        """Inicializa camada de apresentação"""
        logger.info("Inicializando camada de apresentação")
        
        # Configura notificações
        self.presentation.notifications.configure_email(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            username="marabet@example.com",
            password="password"
        )
        
        logger.info("Camada de apresentação inicializada")
    
    def start(self):
        """Inicia o sistema"""
        if self.is_running:
            logger.warning("Sistema já está em execução")
            return
        
        try:
            logger.info("Iniciando sistema modular")
            self.is_running = True
            self.stats['start_time'] = datetime.now()
            
            # Inicia threads de processamento
            self._start_collection_thread()
            self._start_processing_thread()
            self._start_cleanup_thread()
            
            # Inicia serviços de apresentação
            self.presentation.start_services(
                dashboard_port=self.config.dashboard_port,
                api_port=self.config.api_port
            )
            
            # Configura agendamentos
            self._setup_schedules()
            
            logger.info("Sistema iniciado com sucesso")
            logger.info(f"Dashboard: http://localhost:{self.config.dashboard_port}")
            logger.info(f"API: http://localhost:{self.config.api_port}")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar sistema: {e}")
            self.stop()
    
    def stop(self):
        """Para o sistema"""
        logger.info("Parando sistema modular")
        self.is_running = False
        
        # Para threads
        if self.collection_thread and self.collection_thread.is_alive():
            self.collection_thread.join(timeout=5)
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5)
        
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        
        # Desconecta armazenamentos
        self.storage.disconnect_all()
        
        logger.info("Sistema parado")
    
    def _start_collection_thread(self):
        """Inicia thread de coleta de dados"""
        def collection_worker():
            while self.is_running:
                try:
                    self._collect_data()
                    time.sleep(self.config.data_collection_interval)
                except Exception as e:
                    logger.error(f"Erro na coleta de dados: {e}")
                    self.stats['errors'] += 1
                    time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente
        
        self.collection_thread = threading.Thread(target=collection_worker, daemon=True)
        self.collection_thread.start()
        logger.info("Thread de coleta iniciada")
    
    def _start_processing_thread(self):
        """Inicia thread de processamento"""
        def processing_worker():
            while self.is_running:
                try:
                    self._process_queued_data()
                    time.sleep(self.config.processing_interval)
                except Exception as e:
                    logger.error(f"Erro no processamento: {e}")
                    self.stats['errors'] += 1
                    time.sleep(60)
        
        self.processing_thread = threading.Thread(target=processing_worker, daemon=True)
        self.processing_thread.start()
        logger.info("Thread de processamento iniciada")
    
    def _start_cleanup_thread(self):
        """Inicia thread de limpeza"""
        def cleanup_worker():
            while self.is_running:
                try:
                    self._cleanup_old_data()
                    time.sleep(self.config.cleanup_interval)
                except Exception as e:
                    logger.error(f"Erro na limpeza: {e}")
                    self.stats['errors'] += 1
                    time.sleep(300)  # Aguarda 5 minutos
        
        self.cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self.cleanup_thread.start()
        logger.info("Thread de limpeza iniciada")
    
    def _setup_schedules(self):
        """Configura agendamentos"""
        # Coleta de dados a cada 5 minutos
        schedule.every(5).minutes.do(self._collect_data)
        
        # Processamento a cada 10 minutos
        schedule.every(10).minutes.do(self._process_queued_data)
        
        # Limpeza a cada hora
        schedule.every().hour.do(self._cleanup_old_data)
        
        # Relatório de status a cada 30 minutos
        schedule.every(30).minutes.do(self._log_status)
    
    def _collect_data(self):
        """Coleta dados de todas as fontes"""
        try:
            logger.info("Iniciando coleta de dados")
            
            # Coleta dados de partidas
            match_data = self.data_collection.collect_all_data(
                ['matches', 'statistics', 'h2h'],
                league='Premier League',
                season='2024/25'
            )
            
            # Coleta dados de odds
            odds_data = self.data_collection.collect_all_data(
                ['odds'],
                sport='soccer_epl'
            )
            
            # Coleta dados de notícias
            news_data = self.data_collection.collect_all_data(
                ['news'],
                teams=['Manchester City', 'Arsenal']
            )
            
            # Armazena dados coletados
            all_data = match_data + odds_data + news_data
            
            for collected_data in all_data:
                storage_record = StorageRecord(
                    id=f"{collected_data.source}_{collected_data.data_type}_{datetime.now().timestamp()}",
                    data_type=collected_data.data_type,
                    data=collected_data.data,
                    timestamp=collected_data.timestamp,
                    source=collected_data.source,
                    metadata=collected_data.metadata,
                    ttl=3600  # 1 hora
                )
                
                # Armazena em todos os sistemas
                self.storage.store_data(storage_record, "postgresql")
                self.storage.store_data(storage_record, "redis")
                self.storage.store_data(storage_record, "mongodb")
                
                # Adiciona à fila de processamento
                self.data_queue.put(collected_data)
            
            self.stats['data_collected'] += len(all_data)
            logger.info(f"Coletados {len(all_data)} registros de dados")
            
        except Exception as e:
            logger.error(f"Erro na coleta de dados: {e}")
            self.stats['errors'] += 1
    
    def _process_queued_data(self):
        """Processa dados da fila"""
        try:
            processed_count = 0
            
            while not self.data_queue.empty() and processed_count < 100:  # Processa até 100 por vez
                try:
                    collected_data = self.data_queue.get_nowait()
                    
                    # Processa dados baseado no tipo
                    if collected_data.data_type in ['matches', 'statistics', 'h2h']:
                        processed = self.processing.process_data(collected_data.data, "match")
                    elif collected_data.data_type == 'odds':
                        processed = self.processing.process_data(collected_data.data, "odds")
                    else:
                        continue
                    
                    # Armazena dados processados
                    if processed and processed.data_type != 'error':
                        storage_record = StorageRecord(
                            id=f"processed_{processed.id}",
                            data_type=processed.data_type,
                            data=processed.processed_data,
                            timestamp=processed.timestamp,
                            source="processing_layer",
                            metadata=processed.metadata
                        )
                        
                        self.storage.store_data(storage_record, "postgresql")
                        self.storage.store_data(storage_record, "redis")
                    
                    processed_count += 1
                    self.stats['data_processed'] += 1
                    
                except queue.Empty:
                    break
                except Exception as e:
                    logger.error(f"Erro no processamento individual: {e}")
                    self.stats['errors'] += 1
            
            if processed_count > 0:
                logger.info(f"Processados {processed_count} registros")
            
        except Exception as e:
            logger.error(f"Erro no processamento em lote: {e}")
            self.stats['errors'] += 1
    
    def _cleanup_old_data(self):
        """Limpa dados antigos"""
        try:
            logger.info("Iniciando limpeza de dados antigos")
            
            # Remove dados mais antigos que 7 dias
            cutoff_date = datetime.now() - timedelta(days=7)
            
            # Limpa Redis (TTL já gerencia isso)
            # Limpa PostgreSQL
            old_records = self.storage.query_data({
                'start_date': cutoff_date.isoformat()
            }, "postgresql")
            
            for record in old_records:
                self.storage.delete(record.id)
            
            logger.info(f"Limpeza concluída: {len(old_records)} registros removidos")
            
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")
            self.stats['errors'] += 1
    
    def _log_status(self):
        """Registra status do sistema"""
        uptime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else timedelta(0)
        
        logger.info(f"Status do Sistema - Uptime: {uptime}")
        logger.info(f"Dados coletados: {self.stats['data_collected']}")
        logger.info(f"Dados processados: {self.stats['data_processed']}")
        logger.info(f"Predições feitas: {self.stats['predictions_made']}")
        logger.info(f"Notificações enviadas: {self.stats['notifications_sent']}")
        logger.info(f"Erros: {self.stats['errors']}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status do sistema"""
        uptime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else timedelta(0)
        
        return {
            'is_running': self.is_running,
            'uptime_seconds': uptime.total_seconds(),
            'stats': self.stats.copy(),
            'data_queue_size': self.data_queue.qsize(),
            'storage_stats': self.storage.get_storage_stats(),
            'processing_stats': self.processing.get_processing_stats(),
            'data_quality': self.data_collection.get_data_quality_report()
        }
    
    def create_analysis(self, home_team: str, away_team: str, league: str, 
                       match_date: str) -> Dict[str, Any]:
        """Cria análise personalizada"""
        try:
            logger.info(f"Criando análise: {home_team} vs {away_team}")
            
            # Coleta dados específicos da partida
            match_data = self.data_collection.collect_all_data(
                ['matches', 'statistics', 'h2h', 'odds'],
                home_team=home_team,
                away_team=away_team,
                league=league,
                match_date=match_date
            )
            
            # Processa dados
            processed_data = []
            for data in match_data:
                if data.data_type in ['matches', 'statistics', 'h2h']:
                    processed = self.processing.process_data(data.data, "match")
                elif data.data_type == 'odds':
                    processed = self.processing.process_data(data.data, "odds")
                else:
                    continue
                
                if processed and processed.data_type != 'error':
                    processed_data.append(processed)
            
            # Cria dashboard com resultados
            dashboard_data = self.presentation.create_dashboard_data(
                title=f"Análise {home_team} vs {away_team}",
                data_type="analysis",
                data={
                    'home_team': home_team,
                    'away_team': away_team,
                    'league': league,
                    'match_date': match_date,
                    'processed_data': processed_data
                }
            )
            
            dashboard_id = self.presentation.dashboard.create_dashboard(dashboard_data)
            
            # Envia notificação
            notification = self.presentation.notifications.create_notification(
                type='email',
                recipient='user@example.com',
                subject=f'Análise Concluída: {home_team} vs {away_team}',
                content=f'Análise da partida {home_team} vs {away_team} foi concluída e está disponível no dashboard.',
                priority='high'
            )
            
            self.presentation.notifications.send_notification(notification)
            self.stats['notifications_sent'] += 1
            
            return {
                'analysis_id': dashboard_id,
                'home_team': home_team,
                'away_team': away_team,
                'league': league,
                'match_date': match_date,
                'dashboard_url': f"http://localhost:{self.config.dashboard_port}",
                'api_url': f"http://localhost:{self.config.api_port}",
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Erro na criação de análise: {e}")
            self.stats['errors'] += 1
            return {'error': str(e), 'status': 'failed'}

def create_default_config() -> SystemConfig:
    """Cria configuração padrão"""
    return SystemConfig(
        api_football_key="demo_api_key",
        odds_api_key="demo_odds_key",
        postgres_config=DatabaseConfig(
            host="localhost",
            port=5432,
            database="marabet_ai",
            username="user",
            password="password"
        ),
        redis_config=DatabaseConfig(
            host="localhost",
            port=6379,
            database="marabet_ai"
        ),
        mongo_config=DatabaseConfig(
            host="localhost",
            port=27017,
            database="marabet_ai"
        ),
        model_save_path="models/",
        dashboard_port=5000,
        api_port=5001,
        data_collection_interval=300,
        processing_interval=600,
        cleanup_interval=3600
    )

if __name__ == "__main__":
    # Teste do sistema modular
    print("🚀 MARABET AI - SISTEMA MODULAR INTEGRADO")
    print("=" * 60)
    
    # Cria configuração
    config = create_default_config()
    
    # Inicializa sistema
    system = ModularSystem(config)
    
    if system.initialize():
        print("✅ Sistema inicializado com sucesso")
        
        # Inicia sistema
        system.start()
        print("✅ Sistema iniciado")
        
        # Aguarda um pouco para ver o sistema funcionando
        time.sleep(10)
        
        # Cria análise de exemplo
        print("\n📊 Criando análise de exemplo...")
        analysis = system.create_analysis(
            "Manchester City", "Arsenal", "Premier League", "2024-01-15"
        )
        print(f"Análise criada: {analysis}")
        
        # Mostra status
        print("\n📈 Status do Sistema:")
        status = system.get_system_status()
        print(f"Executando: {status['is_running']}")
        print(f"Uptime: {status['uptime_seconds']:.1f} segundos")
        print(f"Dados coletados: {status['stats']['data_collected']}")
        print(f"Dados processados: {status['stats']['data_processed']}")
        print(f"Erros: {status['stats']['errors']}")
        
        # Para o sistema
        print("\n🛑 Parando sistema...")
        system.stop()
        print("✅ Sistema parado")
        
    else:
        print("❌ Falha na inicialização do sistema")
    
    print("\n🎉 Teste do sistema modular concluído!")
