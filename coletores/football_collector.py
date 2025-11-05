from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from .base_collector import BaseCollector
from settings.settings import API_FOOTBALL_KEY, API_FOOTBALL_HOST, MONITORED_LEAGUES

logger = logging.getLogger(__name__)

class FootballCollector(BaseCollector):
    """Coletor para dados da API-Football"""
    
    def __init__(self):
        super().__init__(
            api_key=API_FOOTBALL_KEY,
            base_url=f"https://{API_FOOTBALL_HOST}"
        )
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': API_FOOTBALL_HOST
        }
    
    def collect_matches(self, league_id: int, season: int = 2024, 
                       from_date: Optional[str] = None, 
                       to_date: Optional[str] = None) -> List[Dict]:
        """Coleta partidas de uma liga específica"""
        params = {
            'league': league_id,
            'season': season
        }
        
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
            
        try:
            data = self._make_request('fixtures', params=params, headers=self.headers)
            return data.get('response', [])
        except Exception as e:
            logger.error(f"Erro ao coletar partidas da liga {league_id}: {e}")
            return []
    
    def collect_league_standings(self, league_id: int, season: int = 2024) -> List[Dict]:
        """Coleta tabela de classificação"""
        params = {
            'league': league_id,
            'season': season
        }
        
        try:
            data = self._make_request('standings', params=params, headers=self.headers)
            return data.get('response', [])
        except Exception as e:
            logger.error(f"Erro ao coletar classificação da liga {league_id}: {e}")
            return []
    
    def collect_team_statistics(self, team_id: int, season: int = 2024) -> Dict:
        """Coleta estatísticas de um time"""
        params = {
            'team': team_id,
            'season': season
        }
        
        try:
            data = self._make_request('teams/statistics', params=params, headers=self.headers)
            return data.get('response', {})
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas do time {team_id}: {e}")
            return {}
    
    def collect_fixture_events(self, fixture_id: int) -> List[Dict]:
        """Coleta eventos de uma partida específica"""
        params = {'fixture': fixture_id}
        
        try:
            data = self._make_request('fixtures/events', params=params, headers=self.headers)
            return data.get('response', [])
        except Exception as e:
            logger.error(f"Erro ao coletar eventos da partida {fixture_id}: {e}")
            return []
    
    def collect_fixture_statistics(self, fixture_id: int) -> Dict:
        """Coleta estatísticas de uma partida específica"""
        params = {'fixture': fixture_id}
        
        try:
            data = self._make_request('fixtures/statistics', params=params, headers=self.headers)
            return data.get('response', {})
        except Exception as e:
            logger.error(f"Erro ao coletar estatísticas da partida {fixture_id}: {e}")
            return {}
    
    def collect_all_monitored_leagues(self, days: int = 7) -> List[Dict]:
        """Coleta partidas de todas as ligas monitoradas"""
        all_matches = []
        from_date = datetime.now().strftime('%Y-%m-%d')
        to_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        for league_id in MONITORED_LEAGUES:
            logger.info(f"Coletando partidas da liga {league_id}")
            matches = self.collect_matches(league_id, from_date=from_date, to_date=to_date)
            all_matches.extend(matches)
            
        return all_matches
    
    def collect(self, **kwargs) -> List[Dict]:
        """Implementação do método abstrato"""
        league_id = kwargs.get('league_id')
        days = kwargs.get('days', 7)
        
        if league_id:
            return self.collect_matches(league_id)
        else:
            return self.collect_all_monitored_leagues(days)
