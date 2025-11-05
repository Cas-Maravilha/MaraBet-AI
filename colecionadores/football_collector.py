from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from .base_collector import BaseCollector
from settings.settings import API_FOOTBALL_KEY, API_FOOTBALL_HOST, MONITORED_LEAGUES

logger = logging.getLogger(__name__)

class FootballCollector(BaseCollector):
    """Coletor de dados de futebol via API-Football"""
    
    def __init__(self):
        super().__init__(
            api_key=API_FOOTBALL_KEY,
            base_url=f"https://{API_FOOTBALL_HOST}"
        )
        self.headers = {
            'x-rapidapi-host': API_FOOTBALL_HOST,
            'x-rapidapi-key': API_FOOTBALL_KEY
        }
    
    def get_live_matches(self) -> List[Dict]:
        """Obtém partidas ao vivo"""
        logger.info("Coletando partidas ao vivo...")
        
        response = self._make_request(
            'fixtures',
            params={'live': 'all'},
            headers=self.headers
        )
        
        matches = response.get('response', [])
        logger.info(f"✅ {len(matches)} partidas ao vivo encontradas")
        return matches
    
    def get_fixtures_by_date(self, date: Optional[str] = None) -> List[Dict]:
        """Obtém partidas por data"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Coletando partidas do dia {date}...")
        
        response = self._make_request(
            'fixtures',
            params={'date': date},
            headers=self.headers
        )
        
        matches = response.get('response', [])
        logger.info(f"✅ {len(matches)} partidas encontradas")
        return matches
    
    def get_fixtures_by_league(self, league_id: int, season: int) -> List[Dict]:
        """Obtém partidas de uma liga específica"""
        logger.info(f"Coletando partidas da liga {league_id}...")
        
        response = self._make_request(
            'fixtures',
            params={
                'league': league_id,
                'season': season
            },
            headers=self.headers
        )
        
        matches = response.get('response', [])
        logger.info(f"✅ {len(matches)} partidas encontradas")
        return matches
    
    def get_match_statistics(self, fixture_id: int) -> Dict:
        """Obtém estatísticas detalhadas de uma partida"""
        logger.debug(f"Coletando estatísticas do jogo {fixture_id}")
        
        response = self._make_request(
            'fixtures/statistics',
            params={'fixture': fixture_id},
            headers=self.headers
        )
        
        return response.get('response', [])
    
    def get_match_events(self, fixture_id: int) -> List[Dict]:
        """Obtém eventos de uma partida (gols, cartões, etc)"""
        logger.debug(f"Coletando eventos do jogo {fixture_id}")
        
        response = self._make_request(
            'fixtures/events',
            params={'fixture': fixture_id},
            headers=self.headers
        )
        
        return response.get('response', [])
    
    def get_h2h(self, team1_id: int, team2_id: int, last: int = 10) -> List[Dict]:
        """Obtém histórico de confrontos diretos"""
        logger.debug(f"Coletando H2H: {team1_id} vs {team2_id}")
        
        response = self._make_request(
            'fixtures/headtohead',
            params={
                'h2h': f"{team1_id}-{team2_id}",
                'last': last
            },
            headers=self.headers
        )
        
        return response.get('response', [])
    
    def get_team_statistics(self, team_id: int, league_id: int, season: int) -> Dict:
        """Obtém estatísticas de um time na temporada"""
        logger.debug(f"Coletando estatísticas do time {team_id}")
        
        response = self._make_request(
            'teams/statistics',
            params={
                'team': team_id,
                'league': league_id,
                'season': season
            },
            headers=self.headers
        )
        
        return response.get('response', {})
    
    def collect(self, mode: str = 'live', **kwargs) -> List[Dict]:
        """Método principal de coleta"""
        if mode == 'live':
            return self.get_live_matches()
        elif mode == 'today':
            return self.get_fixtures_by_date()
        elif mode == 'date':
            return self.get_fixtures_by_date(kwargs.get('date'))
        elif mode == 'league':
            return self.get_fixtures_by_league(
                kwargs.get('league_id'),
                kwargs.get('season', datetime.now().year)
            )
        else:
            logger.error(f"Modo desconhecido: {mode}")
            return []
