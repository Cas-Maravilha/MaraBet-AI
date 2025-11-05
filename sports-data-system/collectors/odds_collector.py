"""
Coletor de Odds - Sistema Básico
Coleta odds de APIs gratuitas (simulado para demonstração)
"""

import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .base_collector import BaseCollector

logger = logging.getLogger(__name__)

class OddsCollector(BaseCollector):
    """Coletor de odds (simulado para demonstração)"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            name="Odds",
            base_url="https://api.the-odds-api.com/v4",  # URL de exemplo
            api_key=api_key,
            rate_limit=100,  # Simulado
            timeout=30
        )
        
        # Bookmakers simulados
        self.bookmakers = [
            "bet365", "betfair", "williamhill", "pinnacle", 
            "unibet", "bwin", "betway", "sportingbet"
        ]
        
        # Mercados simulados
        self.markets = [
            "h2h",  # Resultado da partida
            "totals",  # Over/Under
            "btts",  # Ambas marcam
            "double_chance"  # Dupla chance
        ]
    
    def collect_match_odds(self, home_team: str, away_team: str, 
                          league: str = "Premier League") -> List[Dict[str, Any]]:
        """Coleta odds de uma partida específica"""
        # Simula coleta de odds (em produção, usaria API real)
        odds_data = []
        
        for bookmaker in self.bookmakers:
            # Simula odds realistas
            home_odd = round(random.uniform(1.5, 4.0), 2)
            draw_odd = round(random.uniform(2.8, 4.5), 2)
            away_odd = round(random.uniform(1.8, 6.0), 2)
            
            # Ajusta odds baseado no "favoritismo" simulado
            if random.random() > 0.5:  # Home team favorito
                home_odd = round(random.uniform(1.3, 2.5), 2)
                away_odd = round(random.uniform(2.5, 5.0), 2)
            else:  # Away team favorito
                home_odd = round(random.uniform(2.0, 4.5), 2)
                away_odd = round(random.uniform(1.4, 2.8), 2)
            
            # Simula odds de Over/Under
            over_2_5 = round(random.uniform(1.2, 2.8), 2)
            under_2_5 = round(random.uniform(1.3, 3.2), 2)
            
            # Simula odds de Ambas Marcam
            btts_yes = round(random.uniform(1.4, 2.5), 2)
            btts_no = round(random.uniform(1.3, 2.8), 2)
            
            bookmaker_odds = {
                'bookmaker': bookmaker,
                'match': {
                    'home_team': home_team,
                    'away_team': away_team,
                    'league': league,
                    'date': (datetime.now() + timedelta(days=random.randint(1, 7))).isoformat()
                },
                'odds': {
                    'h2h': {
                        'home_win': home_odd,
                        'draw': draw_odd,
                        'away_win': away_odd
                    },
                    'totals': {
                        'over_2_5': over_2_5,
                        'under_2_5': under_2_5,
                        'over_1_5': round(random.uniform(1.1, 1.8), 2),
                        'under_1_5': round(random.uniform(1.8, 3.5), 2),
                        'over_3_5': round(random.uniform(1.8, 4.0), 2),
                        'under_3_5': round(random.uniform(1.2, 2.2), 2)
                    },
                    'btts': {
                        'yes': btts_yes,
                        'no': btts_no
                    },
                    'double_chance': {
                        'home_or_draw': round(random.uniform(1.1, 1.6), 2),
                        'away_or_draw': round(random.uniform(1.2, 2.0), 2),
                        'home_or_away': round(random.uniform(1.1, 1.4), 2)
                    }
                },
                'collected_at': datetime.now().isoformat()
            }
            
            odds_data.append(bookmaker_odds)
        
        self.stats['total_data_points'] += len(odds_data)
        return odds_data
    
    def collect_league_odds(self, league: str, date_from: str = None) -> List[Dict[str, Any]]:
        """Coleta odds de uma liga inteira"""
        # Simula times da liga
        teams = {
            "Premier League": [
                "Manchester City", "Arsenal", "Liverpool", "Chelsea", "Tottenham",
                "Manchester United", "Newcastle", "Brighton", "Aston Villa", "West Ham"
            ],
            "La Liga": [
                "Real Madrid", "Barcelona", "Atletico Madrid", "Real Sociedad", "Villarreal",
                "Real Betis", "Athletic Bilbao", "Valencia", "Sevilla", "Osasuna"
            ],
            "Serie A": [
                "Inter Milan", "AC Milan", "Juventus", "Napoli", "Atalanta",
                "Roma", "Lazio", "Fiorentina", "Bologna", "Torino"
            ],
            "Bundesliga": [
                "Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen", "Eintracht Frankfurt",
                "Freiburg", "Union Berlin", "Wolfsburg", "Mainz", "Borussia Monchengladbach"
            ],
            "Ligue 1": [
                "PSG", "Marseille", "Monaco", "Lens", "Rennes",
                "Lille", "Nice", "Lorient", "Reims", "Toulouse"
            ]
        }
        
        league_teams = teams.get(league, [])
        if not league_teams:
            return []
        
        all_odds = []
        
        # Simula partidas da liga
        for i in range(0, len(league_teams), 2):
            if i + 1 < len(league_teams):
                home_team = league_teams[i]
                away_team = league_teams[i + 1]
                
                match_odds = self.collect_match_odds(home_team, away_team, league)
                all_odds.extend(match_odds)
        
        return all_odds
    
    def collect_historical_odds(self, team: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """Coleta odds históricas de um time"""
        historical_odds = []
        
        for i in range(days_back):
            date = datetime.now() - timedelta(days=i)
            
            # Simula odds históricas
            for bookmaker in random.sample(self.bookmakers, 3):  # 3 bookmakers por dia
                odds_entry = {
                    'team': team,
                    'date': date.isoformat(),
                    'bookmaker': bookmaker,
                    'odds': {
                        'home_win': round(random.uniform(1.2, 5.0), 2),
                        'draw': round(random.uniform(2.5, 4.5), 2),
                        'away_win': round(random.uniform(1.3, 6.0), 2),
                        'over_2_5': round(random.uniform(1.1, 3.0), 2),
                        'under_2_5': round(random.uniform(1.2, 3.5), 2)
                    },
                    'collected_at': datetime.now().isoformat()
                }
                historical_odds.append(odds_entry)
        
        self.stats['total_data_points'] += len(historical_odds)
        return historical_odds
    
    def collect_data(self, data_type: str, **kwargs) -> List[Dict[str, Any]]:
        """Coleta dados baseado no tipo solicitado"""
        try:
            if data_type == 'match_odds':
                return self.collect_match_odds(
                    kwargs.get('home_team', 'Team A'),
                    kwargs.get('away_team', 'Team B'),
                    kwargs.get('league', 'Premier League')
                )
            elif data_type == 'league_odds':
                return self.collect_league_odds(
                    kwargs.get('league', 'Premier League'),
                    kwargs.get('date_from')
                )
            elif data_type == 'historical_odds':
                return self.collect_historical_odds(
                    kwargs.get('team', 'Team'),
                    kwargs.get('days_back', 30)
                )
            else:
                logger.error(f"Tipo de dados não suportado: {data_type}")
                return []
                
        except Exception as e:
            logger.error(f"Erro na coleta de odds {data_type}: {e}")
            self.stats['errors'].append(f"Erro em {data_type}: {str(e)}")
            return []
    
    def get_available_bookmakers(self) -> List[str]:
        """Retorna bookmakers disponíveis"""
        return self.bookmakers.copy()
    
    def get_available_markets(self) -> List[str]:
        """Retorna mercados disponíveis"""
        return self.markets.copy()
    
    def calculate_average_odds(self, odds_list: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcula odds médias de uma lista de odds"""
        if not odds_list:
            return {}
        
        # Agrupa odds por mercado
        markets = {}
        for odds_data in odds_list:
            bookmaker = odds_data['bookmaker']
            odds = odds_data['odds']
            
            for market, market_odds in odds.items():
                if market not in markets:
                    markets[market] = {}
                
                for outcome, odd_value in market_odds.items():
                    if outcome not in markets[market]:
                        markets[market][outcome] = []
                    markets[market][outcome].append(odd_value)
        
        # Calcula médias
        average_odds = {}
        for market, outcomes in markets.items():
            average_odds[market] = {}
            for outcome, values in outcomes.items():
                if values:
                    average_odds[market][outcome] = round(sum(values) / len(values), 2)
        
        return average_odds
