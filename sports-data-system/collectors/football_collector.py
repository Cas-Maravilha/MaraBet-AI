"""
Coletor de Dados de Futebol - Sistema Básico
Coleta dados da API-Football (plano gratuito)
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .base_collector import BaseCollector

logger = logging.getLogger(__name__)

class FootballCollector(BaseCollector):
    """Coletor de dados de futebol usando API-Football"""
    
    def __init__(self, api_key: str):
        super().__init__(
            name="Football",
            base_url="https://v3.football.api-sports.io",
            api_key=api_key,
            rate_limit=10,  # Plano gratuito: 10 requests/min
            timeout=30
        )
        
        # Configurações específicas
        self.leagues = {
            39: "Premier League",
            140: "La Liga", 
            135: "Serie A",
            78: "Bundesliga",
            61: "Ligue 1"
        }
    
    def collect_leagues(self, country: str = None) -> List[Dict[str, Any]]:
        """Coleta informações das ligas"""
        params = {}
        if country:
            params['country'] = country
        
        data = self._make_request('/leagues', params)
        if not data or 'response' not in data:
            return []
        
        leagues = []
        for league_data in data['response']:
            league_info = {
                'id': league_data['league']['id'],
                'name': league_data['league']['name'],
                'country': league_data['country']['name'],
                'logo': league_data['league'].get('logo', ''),
                'type': league_data['league'].get('type', 'League'),
                'collected_at': datetime.now().isoformat()
            }
            leagues.append(league_info)
        
        self.stats['total_data_points'] += len(leagues)
        return leagues
    
    def collect_teams(self, league_id: int, season: int = 2024) -> List[Dict[str, Any]]:
        """Coleta times de uma liga"""
        params = {
            'league': league_id,
            'season': season
        }
        
        data = self._make_request('/teams', params)
        if not data or 'response' not in data:
            return []
        
        teams = []
        for team_data in data['response']:
            team_info = {
                'id': team_data['team']['id'],
                'name': team_data['team']['name'],
                'code': team_data['team'].get('code', ''),
                'country': team_data['team'].get('country', ''),
                'founded': team_data['team'].get('founded'),
                'logo': team_data['team'].get('logo', ''),
                'venue': {
                    'name': team_data['venue'].get('name', ''),
                    'city': team_data['venue'].get('city', ''),
                    'capacity': team_data['venue'].get('capacity', 0)
                },
                'league_id': league_id,
                'season': season,
                'collected_at': datetime.now().isoformat()
            }
            teams.append(team_info)
        
        self.stats['total_data_points'] += len(teams)
        return teams
    
    def collect_fixtures(self, league_id: int, season: int = 2024, 
                        date_from: str = None, date_to: str = None) -> List[Dict[str, Any]]:
        """Coleta partidas de uma liga"""
        params = {
            'league': league_id,
            'season': season
        }
        
        if date_from:
            params['from'] = date_from
        if date_to:
            params['to'] = date_to
        
        data = self._make_request('/fixtures', params)
        if not data or 'response' not in data:
            return []
        
        fixtures = []
        for fixture_data in data['response']:
            fixture_info = {
                'id': fixture_data['fixture']['id'],
                'date': fixture_data['fixture']['date'],
                'timestamp': fixture_data['fixture']['timestamp'],
                'timezone': fixture_data['fixture']['timezone'],
                'periods': fixture_data['fixture'].get('periods', {}),
                'venue': {
                    'id': fixture_data['venue'].get('id'),
                    'name': fixture_data['venue'].get('name', ''),
                    'city': fixture_data['venue'].get('city', '')
                },
                'status': {
                    'long': fixture_data['status']['long'],
                    'short': fixture_data['status']['short'],
                    'elapsed': fixture_data['status'].get('elapsed')
                },
                'league': {
                    'id': fixture_data['league']['id'],
                    'name': fixture_data['league']['name'],
                    'country': fixture_data['league']['country'],
                    'logo': fixture_data['league'].get('logo', ''),
                    'flag': fixture_data['league'].get('flag', ''),
                    'season': fixture_data['league']['season'],
                    'round': fixture_data['league'].get('round', '')
                },
                'teams': {
                    'home': {
                        'id': fixture_data['teams']['home']['id'],
                        'name': fixture_data['teams']['home']['name'],
                        'logo': fixture_data['teams']['home'].get('logo', ''),
                        'winner': fixture_data['teams']['home'].get('winner')
                    },
                    'away': {
                        'id': fixture_data['teams']['away']['id'],
                        'name': fixture_data['teams']['away']['name'],
                        'logo': fixture_data['teams']['away'].get('logo', ''),
                        'winner': fixture_data['teams']['away'].get('winner')
                    }
                },
                'goals': {
                    'home': fixture_data['goals'].get('home'),
                    'away': fixture_data['goals'].get('away')
                },
                'score': {
                    'halftime': {
                        'home': fixture_data['score'].get('halftime', {}).get('home'),
                        'away': fixture_data['score'].get('halftime', {}).get('away')
                    },
                    'fulltime': {
                        'home': fixture_data['score'].get('fulltime', {}).get('home'),
                        'away': fixture_data['score'].get('fulltime', {}).get('away')
                    }
                },
                'collected_at': datetime.now().isoformat()
            }
            fixtures.append(fixture_info)
        
        self.stats['total_data_points'] += len(fixtures)
        return fixtures
    
    def collect_team_statistics(self, team_id: int, league_id: int, 
                               season: int = 2024) -> List[Dict[str, Any]]:
        """Coleta estatísticas de um time"""
        params = {
            'team': team_id,
            'league': league_id,
            'season': season
        }
        
        data = self._make_request('/teams/statistics', params)
        if not data or 'response' not in data:
            return []
        
        stats_data = data['response']
        statistics = {
            'team_id': team_id,
            'league_id': league_id,
            'season': season,
            'league': stats_data.get('league', {}),
            'team': stats_data.get('team', {}),
            'form': stats_data.get('form', ''),
            'fixtures': stats_data.get('fixtures', {}),
            'goals': stats_data.get('goals', {}),
            'biggest': stats_data.get('biggest', {}),
            'clean_sheet': stats_data.get('clean_sheet', {}),
            'failed_to_score': stats_data.get('failed_to_score', {}),
            'penalty': stats_data.get('penalty', {}),
            'lineups': stats_data.get('lineups', []),
            'cards': stats_data.get('cards', {}),
            'collected_at': datetime.now().isoformat()
        }
        
        self.stats['total_data_points'] += 1
        return [statistics]
    
    def collect_head_to_head(self, team1_id: int, team2_id: int, 
                           last: int = 10) -> List[Dict[str, Any]]:
        """Coleta confrontos diretos entre dois times"""
        params = {
            'h2h': f"{team1_id}-{team2_id}",
            'last': last
        }
        
        data = self._make_request('/fixtures/headtohead', params)
        if not data or 'response' not in data:
            return []
        
        h2h_fixtures = []
        for fixture_data in data['response']:
            fixture_info = {
                'id': fixture_data['fixture']['id'],
                'date': fixture_data['fixture']['date'],
                'timestamp': fixture_data['fixture']['timestamp'],
                'status': fixture_data['status']['short'],
                'league': {
                    'id': fixture_data['league']['id'],
                    'name': fixture_data['league']['name'],
                    'season': fixture_data['league']['season']
                },
                'teams': {
                    'home': {
                        'id': fixture_data['teams']['home']['id'],
                        'name': fixture_data['teams']['home']['name'],
                        'winner': fixture_data['teams']['home'].get('winner')
                    },
                    'away': {
                        'id': fixture_data['teams']['away']['id'],
                        'name': fixture_data['teams']['away']['name'],
                        'winner': fixture_data['teams']['away'].get('winner')
                    }
                },
                'goals': {
                    'home': fixture_data['goals'].get('home'),
                    'away': fixture_data['goals'].get('away')
                },
                'collected_at': datetime.now().isoformat()
            }
            h2h_fixtures.append(fixture_info)
        
        self.stats['total_data_points'] += len(h2h_fixtures)
        return h2h_fixtures
    
    def collect_data(self, data_type: str, **kwargs) -> List[Dict[str, Any]]:
        """Coleta dados baseado no tipo solicitado"""
        try:
            if data_type == 'leagues':
                return self.collect_leagues(kwargs.get('country'))
            elif data_type == 'teams':
                return self.collect_teams(
                    kwargs.get('league_id'),
                    kwargs.get('season', 2024)
                )
            elif data_type == 'fixtures':
                return self.collect_fixtures(
                    kwargs.get('league_id'),
                    kwargs.get('season', 2024),
                    kwargs.get('date_from'),
                    kwargs.get('date_to')
                )
            elif data_type == 'team_stats':
                return self.collect_team_statistics(
                    kwargs.get('team_id'),
                    kwargs.get('league_id'),
                    kwargs.get('season', 2024)
                )
            elif data_type == 'h2h':
                return self.collect_head_to_head(
                    kwargs.get('team1_id'),
                    kwargs.get('team2_id'),
                    kwargs.get('last', 10)
                )
            else:
                logger.error(f"Tipo de dados não suportado: {data_type}")
                return []
                
        except Exception as e:
            logger.error(f"Erro na coleta de dados {data_type}: {e}")
            self.stats['errors'].append(f"Erro em {data_type}: {str(e)}")
            return []
    
    def get_available_leagues(self) -> Dict[int, str]:
        """Retorna ligas disponíveis"""
        return self.leagues.copy()
    
    def is_api_key_valid(self) -> bool:
        """Verifica se a chave da API é válida"""
        if not self.api_key:
            return False
        
        # Tenta fazer uma requisição simples
        data = self._make_request('/status')
        return data is not None and 'response' in data
