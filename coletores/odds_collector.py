from typing import Dict, List
import logging
from .base_collector import BaseCollector
from settings.settings import THE_ODDS_API_KEY

logger = logging.getLogger(__name__)

class OddsCollector(BaseCollector):
    """Coletor de odds via The Odds API"""
    
    def __init__(self):
        super().__init__(
            api_key=THE_ODDS_API_KEY,
            base_url="https://api.the-odds-api.com/v4"
        )
        
        self.sports_map = {
            'soccer_epl': 'Premier League',
            'soccer_spain_la_liga': 'La Liga',
            'soccer_germany_bundesliga': 'Bundesliga',
            'soccer_italy_serie_a': 'Serie A',
            'soccer_france_ligue_one': 'Ligue 1',
            'soccer_brazil_campeonato': 'Brasileirão',
        }
    
    def get_sports(self) -> List[Dict]:
        """Lista esportes disponíveis"""
        logger.info("Obtendo lista de esportes...")
        
        response = self._make_request(
            'sports',
            params={'apiKey': self.api_key}
        )
        
        return response if isinstance(response, list) else []
    
    def get_odds(self, sport: str, regions: str = 'uk,us,eu', 
                 markets: str = 'h2h,spreads,totals') -> List[Dict]:
        """Obtém odds para um esporte"""
        logger.info(f"Coletando odds para {sport}...")
        
        response = self._make_request(
            f'sports/{sport}/odds',
            params={
                'apiKey': self.api_key,
                'regions': regions,
                'markets': markets,
                'oddsFormat': 'decimal'
            }
        )
        
        matches = response if isinstance(response, list) else []
        logger.info(f"✅ Odds de {len(matches)} jogos coletadas")
        return matches
    
    def get_all_football_odds(self) -> Dict[str, List[Dict]]:
        """Coleta odds de todas as ligas de futebol"""
        all_odds = {}
        
        for sport_key, league_name in self.sports_map.items():
            try:
                odds = self.get_odds(sport_key)
                all_odds[league_name] = odds
            except Exception as e:
                logger.error(f"Erro ao coletar odds de {league_name}: {e}")
        
        return all_odds
    
    def collect(self, **kwargs) -> List[Dict]:
        """Método principal de coleta"""
        sport = kwargs.get('sport', 'soccer_epl')
        return self.get_odds(sport)