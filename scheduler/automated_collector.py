import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import threading
from concurrent.futures import ThreadPoolExecutor

from coletores.football_collector import FootballCollector
from coletores.odds_collector import OddsCollector
from análise.value_finder import ValueFinder
from armazenamento.banco_de_dados import SessionLocal, Match, Odds, Prediction
from settings.settings import COLLECTION_INTERVAL, MONITORED_LEAGUES
from notifications.notification_integrator import (
    notify_system_status, notify_error, notify_daily_report
)

logger = logging.getLogger(__name__)

class AutomatedCollector:
    """Sistema de coleta automatizada com agendamento"""
    
    def __init__(self):
        self.football_collector = FootballCollector()
        self.odds_collector = OddsCollector()
        self.value_finder = ValueFinder()
        self.db = SessionLocal()
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/automated_collector.log'),
                logging.StreamHandler()
            ]
        )
    
    def start_scheduler(self):
        """Inicia o agendador de tarefas"""
        logger.info("🚀 Iniciando sistema de coleta automatizada...")
        
        # Configurar tarefas agendadas
        self._setup_schedule()
        
        self.running = True
        
        # Executar em thread separada
        scheduler_thread = threading.Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        logger.info("✅ Sistema de coleta automatizada iniciado!")
        
        # Notificar sobre início do sistema
        try:
            import asyncio
            status_data = {
                'running': True,
                'total_matches': self.db.query(Match).count(),
                'total_predictions': self.db.query(Prediction).count(),
                'next_execution': 'Sistema iniciado'
            }
            asyncio.create_task(notify_system_status(status_data))
        except Exception as e:
            logger.error(f"Erro ao notificar início do sistema: {e}")
        
        return scheduler_thread
    
    def _setup_schedule(self):
        """Configura as tarefas agendadas"""
        
        # Coleta de dados de futebol - a cada 30 minutos
        schedule.every(30).minutes.do(self._collect_football_data)
        
        # Coleta de odds - a cada 15 minutos
        schedule.every(15).minutes.do(self._collect_odds_data)
        
        # Análise de valor - a cada 10 minutos
        schedule.every(10).minutes.do(self._analyze_matches)
        
        # Limpeza de dados antigos - diariamente às 2:00
        schedule.every().day.at("02:00").do(self._cleanup_old_data)
        
        # Relatório de status - diariamente às 8:00
        schedule.every().day.at("08:00").do(self._generate_status_report)
        
        logger.info("📅 Tarefas agendadas configuradas:")
        logger.info("   - Coleta de futebol: a cada 30 minutos")
        logger.info("   - Coleta de odds: a cada 15 minutos")
        logger.info("   - Análise de valor: a cada 10 minutos")
        logger.info("   - Limpeza de dados: diariamente às 2:00")
        logger.info("   - Relatório de status: diariamente às 8:00")
    
    def _run_scheduler(self):
        """Executa o loop do agendador"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
            except Exception as e:
                logger.error(f"Erro no agendador: {e}")
                time.sleep(60)
    
    def _collect_football_data(self):
        """Coleta dados de futebol"""
        logger.info("⚽ Iniciando coleta de dados de futebol...")
        
        try:
            # Coletar partidas de hoje
            today_matches = self.football_collector.collect(mode='today')
            logger.info(f"   Partidas de hoje: {len(today_matches)}")
            
            # Coletar partidas das ligas monitoradas
            for league_id in MONITORED_LEAGUES:
                league_matches = self.football_collector.collect(
                    mode='league', 
                    league_id=league_id, 
                    season=datetime.now().year
                )
                logger.info(f"   Liga {league_id}: {len(league_matches)} partidas")
                
                # Salvar no banco
                self._save_matches_to_db(league_matches)
            
            # Coletar partidas ao vivo
            live_matches = self.football_collector.collect(mode='live')
            logger.info(f"   Partidas ao vivo: {len(live_matches)}")
            
            logger.info("✅ Coleta de dados de futebol concluída!")
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta de futebol: {e}")
            # Notificar sobre erro
            try:
                import asyncio
                asyncio.create_task(notify_error(f"Erro na coleta de futebol: {e}"))
            except Exception as notify_error:
                logger.error(f"Erro ao notificar erro: {notify_error}")
    
    def _collect_odds_data(self):
        """Coleta dados de odds"""
        logger.info("🎯 Iniciando coleta de odds...")
        
        try:
            # Coletar odds de todas as ligas de futebol
            all_odds = self.odds_collector.get_all_football_odds()
            
            total_odds = 0
            for league, odds_list in all_odds.items():
                logger.info(f"   {league}: {len(odds_list)} conjuntos de odds")
                total_odds += len(odds_list)
                
                # Salvar no banco
                self._save_odds_to_db(odds_list)
            
            logger.info(f"✅ Coleta de odds concluída! Total: {total_odds}")
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta de odds: {e}")
            # Notificar sobre erro
            try:
                import asyncio
                asyncio.create_task(notify_error(f"Erro na coleta de odds: {e}"))
            except Exception as notify_error:
                logger.error(f"Erro ao notificar erro: {notify_error}")
    
    def _analyze_matches(self):
        """Analisa partidas e busca valor"""
        logger.info("🔍 Iniciando análise de partidas...")
        
        try:
            # Buscar partidas não analisadas
            unanalyzed_matches = self._get_unanalyzed_matches()
            logger.info(f"   Partidas para analisar: {len(unanalyzed_matches)}")
            
            predictions_found = 0
            for match in unanalyzed_matches:
                # Buscar odds para a partida
                odds_data = self._get_odds_for_match(match['fixture_id'])
                
                if odds_data:
                    # Analisar partida
                    prediction = self.value_finder.analyze_match(match, odds_data)
                    
                    if prediction:
                        predictions_found += 1
                        logger.info(f"   ✅ Valor encontrado: {prediction.market} - EV: {prediction.expected_value:.2%}")
            
            logger.info(f"✅ Análise concluída! {predictions_found} predições encontradas")
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            # Notificar sobre erro
            try:
                import asyncio
                asyncio.create_task(notify_error(f"Erro na análise de partidas: {e}"))
            except Exception as notify_error:
                logger.error(f"Erro ao notificar erro: {notify_error}")
    
    def _cleanup_old_data(self):
        """Limpa dados antigos do banco"""
        logger.info("🧹 Iniciando limpeza de dados antigos...")
        
        try:
            # Remover dados com mais de 30 dias
            cutoff_date = datetime.now() - timedelta(days=30)
            
            # Limpar odds antigas
            old_odds = self.db.query(Odds).filter(Odds.timestamp < cutoff_date).delete()
            logger.info(f"   Odds removidas: {old_odds}")
            
            # Limpar partidas antigas (exceto as que têm predições)
            old_matches = self.db.query(Match).filter(
                Match.created_at < cutoff_date,
                ~Match.fixture_id.in_(
                    self.db.query(Prediction.fixture_id).distinct()
                )
            ).delete()
            logger.info(f"   Partidas removidas: {old_matches}")
            
            self.db.commit()
            logger.info("✅ Limpeza de dados concluída!")
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza: {e}")
            self.db.rollback()
    
    def _generate_status_report(self):
        """Gera relatório de status do sistema"""
        logger.info("📊 Gerando relatório de status...")
        
        try:
            # Estatísticas do banco
            total_matches = self.db.query(Match).count()
            total_odds = self.db.query(Odds).count()
            total_predictions = self.db.query(Prediction).count()
            recommended_predictions = self.db.query(Prediction).filter(Prediction.recommended == True).count()
            
            # Estatísticas dos coletores
            football_stats = self.football_collector.get_stats()
            odds_stats = self.odds_collector.get_stats()
            
            report = f"""
📊 RELATÓRIO DE STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M')}
==================================================
🗄️  BANCO DE DADOS:
   Partidas: {total_matches:,}
   Odds: {total_odds:,}
   Predições: {total_predictions:,}
   Recomendadas: {recommended_predictions:,}

📡 COLETORES:
   Futebol: {football_stats['total_requests']} requisições
   Odds: {odds_stats['total_requests']} requisições

⏰ PRÓXIMAS EXECUÇÕES:
   Futebol: {schedule.next_run('_collect_football_data')}
   Odds: {schedule.next_run('_collect_odds_data')}
   Análise: {schedule.next_run('_analyze_matches')}
            """
            
            logger.info(report)
            
            # Salvar relatório em arquivo
            with open('logs/status_report.log', 'a') as f:
                f.write(report + '\n')
            
            # Enviar relatório diário por notificação
            try:
                import asyncio
                report_data = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'total_matches': total_matches,
                    'total_odds': total_odds,
                    'total_predictions': total_predictions,
                    'recommended_predictions': recommended_predictions,
                    'football_requests': football_stats['total_requests'],
                    'odds_requests': odds_stats['total_requests']
                }
                asyncio.create_task(notify_daily_report(report_data))
            except Exception as notify_error:
                logger.error(f"Erro ao notificar relatório diário: {notify_error}")
            
        except Exception as e:
            logger.error(f"❌ Erro no relatório: {e}")
            # Notificar sobre erro
            try:
                import asyncio
                asyncio.create_task(notify_error(f"Erro no relatório de status: {e}"))
            except Exception as notify_error:
                logger.error(f"Erro ao notificar erro: {notify_error}")
    
    def _save_matches_to_db(self, matches: List[Dict]):
        """Salva partidas no banco de dados"""
        try:
            for match_data in matches:
                fixture = match_data.get('fixture', {})
                teams = match_data.get('teams', {})
                
                match = Match(
                    fixture_id=fixture.get('id'),
                    league_id=match_data.get('league', {}).get('id'),
                    league_name=match_data.get('league', {}).get('name'),
                    date=datetime.fromisoformat(fixture.get('date', '').replace('Z', '+00:00')),
                    home_team_id=teams.get('home', {}).get('id'),
                    home_team_name=teams.get('home', {}).get('name'),
                    away_team_id=teams.get('away', {}).get('id'),
                    away_team_name=teams.get('away', {}).get('name'),
                    status=fixture.get('status', {}).get('short'),
                    elapsed_time=fixture.get('status', {}).get('elapsed'),
                    home_score=fixture.get('goals', {}).get('home'),
                    away_score=fixture.get('goals', {}).get('away'),
                    statistics=match_data.get('statistics'),
                    events=match_data.get('events')
                )
                
                # Verificar se já existe
                existing = self.db.query(Match).filter(Match.fixture_id == match.fixture_id).first()
                if not existing:
                    self.db.add(match)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao salvar partidas: {e}")
            self.db.rollback()
    
    def _save_odds_to_db(self, odds_list: List[Dict]):
        """Salva odds no banco de dados"""
        try:
            for odds_data in odds_list:
                fixture_id = odds_data.get('fixture_id')
                
                for bookmaker in odds_data.get('bookmakers', []):
                    for market in bookmaker.get('markets', []):
                        for outcome in market.get('outcomes', []):
                            odd = Odds(
                                fixture_id=fixture_id,
                                bookmaker=bookmaker.get('title'),
                                market=market.get('key'),
                                selection=outcome.get('name'),
                                odd=outcome.get('price')
                            )
                            
                            self.db.add(odd)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Erro ao salvar odds: {e}")
            self.db.rollback()
    
    def _get_unanalyzed_matches(self) -> List[Dict]:
        """Busca partidas não analisadas"""
        try:
            # Partidas que não têm predições
            matches = self.db.query(Match).filter(
                ~Match.fixture_id.in_(
                    self.db.query(Prediction.fixture_id).distinct()
                ),
                Match.status.in_(['NS', 'TBD'])  # Not Started, To Be Determined
            ).limit(50).all()
            
            return [
                {
                    'fixture': {'id': match.fixture_id},
                    'teams': {
                        'home': {'name': match.home_team_name},
                        'away': {'name': match.away_team_name}
                    }
                }
                for match in matches
            ]
            
        except Exception as e:
            logger.error(f"Erro ao buscar partidas: {e}")
            return []
    
    def _get_odds_for_match(self, fixture_id: int) -> List[Dict]:
        """Busca odds para uma partida específica"""
        try:
            odds = self.db.query(Odds).filter(Odds.fixture_id == fixture_id).all()
            
            if not odds:
                return []
            
            # Agrupar por bookmaker
            bookmakers = {}
            for odd in odds:
                bookmaker = odd.bookmaker
                if bookmaker not in bookmakers:
                    bookmakers[bookmaker] = {'markets': {}}
                
                market = odd.market
                if market not in bookmakers[bookmaker]['markets']:
                    bookmakers[bookmaker]['markets'][market] = {'outcomes': []}
                
                bookmakers[bookmaker]['markets'][market]['outcomes'].append({
                    'name': odd.selection,
                    'price': odd.odd
                })
            
            # Converter para formato esperado
            result = [{
                'fixture_id': fixture_id,
                'bookmakers': [{
                    'title': bookmaker,
                    'markets': [
                        {
                            'key': market,
                            'outcomes': data['outcomes']
                        }
                        for market, data in markets.items()
                    ]
                }]
            } for bookmaker, markets in bookmakers.items()]
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao buscar odds: {e}")
            return []
    
    def stop_scheduler(self):
        """Para o agendador"""
        logger.info("🛑 Parando sistema de coleta automatizada...")
        self.running = False
        self.executor.shutdown(wait=True)
        self.db.close()
        logger.info("✅ Sistema parado!")
    
    def get_status(self) -> Dict:
        """Retorna status do sistema"""
        return {
            'running': self.running,
            'next_football': schedule.next_run('_collect_football_data'),
            'next_odds': schedule.next_run('_collect_odds_data'),
            'next_analysis': schedule.next_run('_analyze_matches'),
            'total_matches': self.db.query(Match).count(),
            'total_odds': self.db.query(Odds).count(),
            'total_predictions': self.db.query(Prediction).count()
        }
