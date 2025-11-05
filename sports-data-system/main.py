#!/usr/bin/env python3
"""
Sistema Básico de Dados Esportivos - MaraBet AI
Sistema econômico com SQLite e APIs gratuitas
"""

import sys
import os
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa módulos do sistema
from config.settings import get_config, create_directories
from config.api_keys import api_keys
from collectors import FootballCollector, OddsCollector
from processors import StatisticsProcessor, PredictionsProcessor
from storage import DatabaseManager
from utils import CacheManager, setup_logger

class SportsDataSystem:
    """Sistema principal de dados esportivos"""
    
    def __init__(self):
        # Carrega configurações
        self.config = get_config()
        
        # Cria diretórios necessários
        create_directories()
        
        # Configura logging
        self.logger = setup_logger(
            name="sports_system",
            level=self.config['logging']['level'],
            log_file=str(self.config['logging']['file'])
        )
        
        # Inicializa componentes
        self._initialize_components()
        
        # Estatísticas do sistema
        self.stats = {
            'start_time': datetime.now(),
            'data_collected': 0,
            'data_processed': 0,
            'predictions_made': 0,
            'errors': 0
        }
    
    def _initialize_components(self):
        """Inicializa componentes do sistema"""
        try:
            self.logger.info("Inicializando componentes do sistema...")
            
            # Cache
            self.cache = CacheManager(
                cache_dir=str(self.config['cache']['path']),
                max_size=self.config['cache']['max_size'],
                ttl=self.config['cache']['ttl']
            )
            
            # Banco de dados
            self.db = DatabaseManager(str(self.config['database']['path']))
            
            # Coletores
            api_key = api_keys.get_key('api_football')
            if not api_key:
                self.logger.warning("Chave da API-Football não encontrada. Usando modo simulado.")
                api_key = "demo_key"
            
            self.football_collector = FootballCollector(api_key)
            self.odds_collector = OddsCollector(api_keys.get_key('odds_api'))
            
            # Processadores
            self.stats_processor = StatisticsProcessor()
            self.predictions_processor = PredictionsProcessor(
                models_dir=self.config['ml']['model_save_path']
            )
            
            self.logger.info("Componentes inicializados com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização: {e}")
            raise
    
    def collect_data(self, data_types: list, **kwargs) -> dict:
        """Coleta dados de diferentes fontes"""
        self.logger.info(f"Iniciando coleta de dados: {data_types}")
        
        collected_data = {}
        
        for data_type in data_types:
            try:
                if data_type in ['leagues', 'teams', 'fixtures', 'team_stats', 'h2h']:
                    data = self.football_collector.collect_data(data_type, **kwargs)
                elif data_type in ['match_odds', 'league_odds', 'historical_odds']:
                    data = self.odds_collector.collect_data(data_type, **kwargs)
                else:
                    self.logger.warning(f"Tipo de dados não suportado: {data_type}")
                    continue
                
                collected_data[data_type] = data
                self.stats['data_collected'] += len(data)
                
                self.logger.info(f"Coletados {len(data)} registros de {data_type}")
                
            except Exception as e:
                self.logger.error(f"Erro na coleta de {data_type}: {e}")
                self.stats['errors'] += 1
        
        return collected_data
    
    def process_data(self, raw_data: dict) -> dict:
        """Processa dados coletados"""
        self.logger.info("Iniciando processamento de dados")
        
        processed_data = {}
        
        try:
            # Processa estatísticas de times
            if 'team_stats' in raw_data:
                for team_data in raw_data['team_stats']:
                    stats = self.stats_processor.process_team_statistics([team_data])
                    processed_data['team_statistics'] = processed_data.get('team_statistics', [])
                    processed_data['team_statistics'].append(stats)
            
            # Processa partidas
            if 'fixtures' in raw_data:
                for match_data in raw_data['fixtures']:
                    match_stats = self.stats_processor.process_match_statistics(match_data)
                    processed_data['match_statistics'] = processed_data.get('match_statistics', [])
                    processed_data['match_statistics'].append(match_stats)
            
            # Processa confrontos diretos
            if 'h2h' in raw_data:
                h2h_stats = self.stats_processor.process_head_to_head(raw_data['h2h'])
                processed_data['h2h_statistics'] = h2h_stats
            
            # Processa odds
            if 'match_odds' in raw_data:
                odds_stats = self.stats_processor.process_odds_statistics(raw_data['match_odds'])
                processed_data['odds_statistics'] = odds_stats
            
            self.stats['data_processed'] += len(processed_data)
            self.logger.info("Processamento de dados concluído")
            
        except Exception as e:
            self.logger.error(f"Erro no processamento: {e}")
            self.stats['errors'] += 1
        
        return processed_data
    
    def make_predictions(self, match_data: dict, team_stats: dict) -> dict:
        """Faz predições para uma partida"""
        self.logger.info("Fazendo predições")
        
        try:
            # Prepara dados para treinamento (simulado)
            training_data = self._prepare_training_data()
            
            # Treina modelos se necessário
            if not self.predictions_processor.is_trained:
                X, y = self.predictions_processor.prepare_training_data(
                    training_data, team_stats
                )
                if X.size > 0:
                    self.predictions_processor.train_models(X, y)
                    self.predictions_processor.save_models()
            
            # Faz predição
            home_team_id = match_data.get('home_team_id')
            away_team_id = match_data.get('away_team_id')
            
            if home_team_id and away_team_id:
                predictions = self.predictions_processor.predict_match(
                    home_team_id, away_team_id, team_stats
                )
                
                self.stats['predictions_made'] += 1
                self.logger.info("Predições concluídas")
                
                return predictions
            
        except Exception as e:
            self.logger.error(f"Erro nas predições: {e}")
            self.stats['errors'] += 1
        
        return {}
    
    def _prepare_training_data(self) -> list:
        """Prepara dados de treinamento (simulados)"""
        # Em um sistema real, buscaria dados históricos do banco
        training_data = []
        
        for i in range(100):  # Simula 100 partidas
            match = {
                'id': i + 1,
                'teams': {
                    'home': {'id': 1 + (i % 5)},
                    'away': {'id': 6 + (i % 5)}
                },
                'goals': {
                    'home': i % 4,
                    'away': (i + 1) % 3
                },
                'date': (datetime.now() - timedelta(days=i)).isoformat()
            }
            training_data.append(match)
        
        return training_data
    
    def save_data(self, data: dict) -> bool:
        """Salva dados no banco"""
        try:
            self.logger.info("Salvando dados no banco")
            
            # Salva ligas
            if 'leagues' in data:
                for league_data in data['leagues']:
                    from storage.models import League
                    league = League(
                        id=league_data['id'],
                        name=league_data['name'],
                        country=league_data['country'],
                        logo=league_data.get('logo'),
                        type=league_data.get('type', 'League')
                    )
                    self.db.save_league(league)
            
            # Salva times
            if 'teams' in data:
                for team_data in data['teams']:
                    from storage.models import Team
                    team = Team(
                        id=team_data['id'],
                        name=team_data['name'],
                        code=team_data.get('code'),
                        country=team_data.get('country'),
                        founded=team_data.get('founded'),
                        logo=team_data.get('logo'),
                        venue_name=team_data.get('venue', {}).get('name'),
                        venue_city=team_data.get('venue', {}).get('city'),
                        venue_capacity=team_data.get('venue', {}).get('capacity'),
                        league_id=team_data.get('league_id'),
                        season=team_data.get('season')
                    )
                    self.db.save_team(team)
            
            # Salva partidas
            if 'fixtures' in data:
                for match_data in data['fixtures']:
                    from storage.models import Match
                    match = Match(
                        id=match_data['id'],
                        date=match_data['date'],
                        timestamp=match_data['timestamp'],
                        timezone=match_data['timezone'],
                        status=match_data['status']['short'],
                        status_long=match_data['status']['long'],
                        elapsed=match_data['status'].get('elapsed'),
                        league_id=match_data['league']['id'],
                        league_name=match_data['league']['name'],
                        league_country=match_data['league']['country'],
                        league_logo=match_data['league'].get('logo'),
                        league_flag=match_data['league'].get('flag'),
                        league_season=match_data['league']['season'],
                        league_round=match_data['league'].get('round'),
                        home_team_id=match_data['teams']['home']['id'],
                        home_team_name=match_data['teams']['home']['name'],
                        home_team_logo=match_data['teams']['home'].get('logo'),
                        home_team_winner=match_data['teams']['home'].get('winner'),
                        away_team_id=match_data['teams']['away']['id'],
                        away_team_name=match_data['teams']['away']['name'],
                        away_team_logo=match_data['teams']['away'].get('logo'),
                        away_team_winner=match_data['teams']['away'].get('winner'),
                        home_goals=match_data['goals'].get('home'),
                        away_goals=match_data['goals'].get('away'),
                        halftime_home=match_data['score'].get('halftime', {}).get('home'),
                        halftime_away=match_data['score'].get('halftime', {}).get('away'),
                        fulltime_home=match_data['score'].get('fulltime', {}).get('home'),
                        fulltime_away=match_data['score'].get('fulltime', {}).get('away')
                    )
                    self.db.save_match(match)
            
            self.logger.info("Dados salvos com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados: {e}")
            self.stats['errors'] += 1
            return False
    
    def run_analysis(self, home_team: str, away_team: str, league: str = "Premier League") -> dict:
        """Executa análise completa de uma partida"""
        self.logger.info(f"Iniciando análise: {home_team} vs {away_team}")
        
        try:
            # 1. Coleta dados
            collected_data = self.collect_data(
                ['fixtures', 'team_stats', 'h2h', 'match_odds'],
                home_team=home_team,
                away_team=away_team,
                league=league
            )
            
            # 2. Processa dados
            processed_data = self.process_data(collected_data)
            
            # 3. Faz predições
            predictions = self.make_predictions(
                collected_data.get('fixtures', [{}])[0],
                processed_data.get('team_statistics', {})
            )
            
            # 4. Salva dados
            self.save_data(collected_data)
            
            # 5. Compila resultado
            analysis_result = {
                'match': f"{home_team} vs {away_team}",
                'league': league,
                'analysis_date': datetime.now().isoformat(),
                'collected_data': collected_data,
                'processed_data': processed_data,
                'predictions': predictions,
                'system_stats': self.get_stats()
            }
            
            self.logger.info("Análise concluída com sucesso")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Erro na análise: {e}")
            self.stats['errors'] += 1
            return {'error': str(e)}
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do sistema"""
        uptime = datetime.now() - self.stats['start_time']
        
        return {
            'uptime_seconds': uptime.total_seconds(),
            'data_collected': self.stats['data_collected'],
            'data_processed': self.stats['data_processed'],
            'predictions_made': self.stats['predictions_made'],
            'errors': self.stats['errors'],
            'cache_stats': self.cache.get_stats(),
            'database_stats': self.db.get_database_stats()
        }
    
    def cleanup(self):
        """Limpa recursos do sistema"""
        self.logger.info("Limpando recursos do sistema")
        
        # Limpa cache
        self.cache.clear()
        
        # Desconecta banco
        self.db.disconnect()
        
        self.logger.info("Limpeza concluída")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Sistema Básico de Dados Esportivos')
    parser.add_argument('--home-team', required=True, help='Time da casa')
    parser.add_argument('--away-team', required=True, help='Time visitante')
    parser.add_argument('--league', default='Premier League', help='Liga')
    parser.add_argument('--collect-only', action='store_true', help='Apenas coletar dados')
    parser.add_argument('--predict-only', action='store_true', help='Apenas fazer predições')
    
    args = parser.parse_args()
    
    print("🏈 SISTEMA BÁSICO DE DADOS ESPORTIVOS - MARABET AI")
    print("=" * 60)
    
    try:
        # Inicializa sistema
        system = SportsDataSystem()
        
        if args.collect_only:
            # Apenas coleta dados
            print(f"📊 Coletando dados: {args.home_team} vs {args.away_team}")
            data = system.collect_data(['fixtures', 'team_stats', 'h2h'])
            print(f"✅ Coletados {sum(len(v) for v in data.values())} registros")
            
        elif args.predict_only:
            # Apenas predições
            print(f"🔮 Fazendo predições: {args.home_team} vs {args.away_team}")
            # Simula dados para predição
            match_data = {'home_team_id': 1, 'away_team_id': 2}
            team_stats = {'1': {}, '2': {}}
            predictions = system.make_predictions(match_data, team_stats)
            print(f"✅ Predições: {predictions}")
            
        else:
            # Análise completa
            print(f"🔍 Análise completa: {args.home_team} vs {args.away_team}")
            result = system.run_analysis(args.home_team, args.away_team, args.league)
            
            if 'error' in result:
                print(f"❌ Erro: {result['error']}")
            else:
                print("✅ Análise concluída com sucesso!")
                print(f"📊 Estatísticas: {result['system_stats']}")
        
        # Mostra estatísticas finais
        stats = system.get_stats()
        print(f"\n📈 ESTATÍSTICAS DO SISTEMA:")
        print(f"   • Uptime: {stats['uptime_seconds']:.1f}s")
        print(f"   • Dados coletados: {stats['data_collected']}")
        print(f"   • Dados processados: {stats['data_processed']}")
        print(f"   • Predições: {stats['predictions_made']}")
        print(f"   • Erros: {stats['errors']}")
        
        # Limpa recursos
        system.cleanup()
        
    except KeyboardInterrupt:
        print("\n⏹️ Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)
    
    print("\n🎉 Sistema finalizado!")

if __name__ == "__main__":
    main()
