#!/usr/bin/env python3
"""
Integração Real com API-Football
MaraBet AI - Integração real com API-Football para dados em tempo real
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
import time
import json
import os
from dataclasses import dataclass
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class APIFootballConfig:
    """Configuração da API-Football"""
    api_key: str
    base_url: str = "https://v3.football.api-sports.io"
    rate_limit: float = 0.1  # 100ms entre requests
    max_retries: int = 3
    timeout: int = 30
    cache_duration: int = 300  # 5 minutos

class RealFootballAPI:
    """Integração real com API-Football"""
    
    def __init__(self, config: APIFootballConfig):
        """Inicializa integração com API-Football"""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'X-RapidAPI-Key': config.api_key,
            'X-RapidAPI-Host': 'v3.football.api-sports.io'
        })
        
        # Cache para evitar requests desnecessários
        self.cache = {}
        self.cache_timestamps = {}
        
        # Inicializar banco de dados para cache
        self.db_path = "data/api_cache.db"
        self._init_cache_database()
    
    def _init_cache_database(self):
        """Inicializa banco de dados para cache"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT,
                params TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _make_request(self, endpoint: str, params: Dict[str, Any], use_cache: bool = True) -> Optional[Dict]:
        """Faz requisição para API com cache"""
        # Verificar cache
        if use_cache:
            cache_key = f"{endpoint}_{hash(str(sorted(params.items())))}"
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                logger.debug(f"Cache hit para {endpoint}")
                return cached_data
        
        url = f"{self.config.base_url}/{endpoint}"
        
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=self.config.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('results') > 0:
                        # Salvar no cache
                        if use_cache:
                            self._save_to_cache(cache_key, data)
                        return data
                    else:
                        logger.warning(f"Nenhum resultado encontrado para {endpoint}")
                        return None
                elif response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limit atingido, aguardando {wait_time}s")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Erro HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                logger.error(f"Erro na requisição (tentativa {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return None
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Obtém dados do cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT data FROM api_cache 
            WHERE endpoint = ? AND expires_at > datetime('now')
            ORDER BY created_at DESC LIMIT 1
        ''', (cache_key,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Salva dados no cache"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(seconds=self.config.cache_duration)
        
        cursor.execute('''
            INSERT INTO api_cache (endpoint, data, expires_at)
            VALUES (?, ?, ?)
        ''', (cache_key, json.dumps(data), expires_at))
        
        conn.commit()
        conn.close()
    
    def get_live_matches(self) -> List[Dict]:
        """Obtém partidas ao vivo"""
        logger.info("Obtendo partidas ao vivo...")
        
        params = {'live': 'all'}
        data = self._make_request('fixtures', params)
        
        if not data:
            return []
        
        matches = []
        for fixture in data.get('response', []):
            match_data = {
                'match_id': fixture['fixture']['id'],
                'league_id': fixture['league']['id'],
                'league_name': fixture['league']['name'],
                'home_team': fixture['teams']['home']['name'],
                'away_team': fixture['teams']['away']['name'],
                'home_score': fixture['goals']['home'],
                'away_score': fixture['goals']['away'],
                'status': fixture['fixture']['status']['short'],
                'minute': fixture['fixture']['status']['elapsed'],
                'date': fixture['fixture']['date']
            }
            matches.append(match_data)
        
        logger.info(f"Encontradas {len(matches)} partidas ao vivo")
        return matches
    
    def get_today_matches(self) -> List[Dict]:
        """Obtém partidas de hoje"""
        logger.info("Obtendo partidas de hoje...")
        
        today = datetime.now().strftime('%Y-%m-%d')
        params = {'date': today}
        
        data = self._make_request('fixtures', params)
        
        if not data:
            return []
        
        matches = []
        for fixture in data.get('response', []):
            match_data = {
                'match_id': fixture['fixture']['id'],
                'league_id': fixture['league']['id'],
                'league_name': fixture['league']['name'],
                'home_team': fixture['teams']['home']['name'],
                'away_team': fixture['teams']['away']['name'],
                'home_score': fixture['goals']['home'],
                'away_score': fixture['goals']['away'],
                'status': fixture['fixture']['status']['short'],
                'date': fixture['fixture']['date']
            }
            matches.append(match_data)
        
        logger.info(f"Encontradas {len(matches)} partidas para hoje")
        return matches
    
    def get_upcoming_matches(self, days: int = 7) -> List[Dict]:
        """Obtém partidas próximas"""
        logger.info(f"Obtendo partidas dos próximos {days} dias...")
        
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        params = {
            'from': start_date,
            'to': end_date
        }
        
        data = self._make_request('fixtures', params)
        
        if not data:
            return []
        
        matches = []
        for fixture in data.get('response', []):
            match_data = {
                'match_id': fixture['fixture']['id'],
                'league_id': fixture['league']['id'],
                'league_name': fixture['league']['name'],
                'home_team': fixture['teams']['home']['name'],
                'away_team': fixture['teams']['away']['name'],
                'home_score': fixture['goals']['home'],
                'away_score': fixture['goals']['away'],
                'status': fixture['fixture']['status']['short'],
                'date': fixture['fixture']['date']
            }
            matches.append(match_data)
        
        logger.info(f"Encontradas {len(matches)} partidas próximas")
        return matches
    
    def get_match_odds(self, match_id: int) -> List[Dict]:
        """Obtém odds de uma partida"""
        logger.info(f"Obtendo odds da partida {match_id}...")
        
        params = {'fixture': match_id}
        data = self._make_request('odds', params)
        
        if not data:
            return []
        
        odds_list = []
        for odds_data in data.get('response', []):
            for bookmaker in odds_data.get('bookmakers', []):
                bookmaker_name = bookmaker['name']
                
                # Procurar por odds de resultado
                for bet in bookmaker.get('bets', []):
                    if bet['name'] == 'Match Winner':
                        home_win = None
                        draw = None
                        away_win = None
                        
                        for outcome in bet['values']:
                            if outcome['value'] == 'Home':
                                home_win = float(outcome['odd'])
                            elif outcome['value'] == 'Draw':
                                draw = float(outcome['odd'])
                            elif outcome['value'] == 'Away':
                                away_win = float(outcome['odd'])
                        
                        if home_win and draw and away_win:
                            odds_list.append({
                                'match_id': match_id,
                                'bookmaker': bookmaker_name,
                                'home_win': home_win,
                                'draw': draw,
                                'away_win': away_win,
                                'timestamp': datetime.now().isoformat()
                            })
        
        logger.info(f"Encontradas {len(odds_list)} odds para a partida {match_id}")
        return odds_list
    
    def get_match_statistics(self, match_id: int) -> List[Dict]:
        """Obtém estatísticas de uma partida"""
        logger.info(f"Obtendo estatísticas da partida {match_id}...")
        
        params = {'fixture': match_id}
        data = self._make_request('fixtures/statistics', params)
        
        if not data:
            return []
        
        stats = []
        for team_stats in data.get('response', []):
            team_id = team_stats['team']['id']
            team_name = team_stats['team']['name']
            
            team_data = {
                'match_id': match_id,
                'team_id': team_id,
                'team_name': team_name,
                'shots_total': 0,
                'shots_on_goal': 0,
                'possession': 0,
                'passes_total': 0,
                'passes_accurate': 0,
                'fouls': 0,
                'yellow_cards': 0,
                'red_cards': 0,
                'timestamp': datetime.now().isoformat()
            }
            
            for stat in team_stats['statistics']:
                stat_type = stat['type']
                value = stat['value']
                
                if stat_type == 'Shots Total':
                    team_data['shots_total'] = int(value) if value else 0
                elif stat_type == 'Shots on Goal':
                    team_data['shots_on_goal'] = int(value) if value else 0
                elif stat_type == 'Ball Possession':
                    team_data['possession'] = int(value.replace('%', '')) if value else 0
                elif stat_type == 'Total passes':
                    team_data['passes_total'] = int(value) if value else 0
                elif stat_type == 'Passes accurate':
                    team_data['passes_accurate'] = int(value) if value else 0
                elif stat_type == 'Fouls':
                    team_data['fouls'] = int(value) if value else 0
                elif stat_type == 'Yellow Cards':
                    team_data['yellow_cards'] = int(value) if value else 0
                elif stat_type == 'Red Cards':
                    team_data['red_cards'] = int(value) if value else 0
            
            stats.append(team_data)
        
        logger.info(f"Encontradas {len(stats)} estatísticas para a partida {match_id}")
        return stats
    
    def get_team_form(self, team_id: int, last_matches: int = 5) -> List[Dict]:
        """Obtém forma recente de um time"""
        logger.info(f"Obtendo forma do time {team_id}...")
        
        params = {
            'team': team_id,
            'last': last_matches
        }
        
        data = self._make_request('fixtures', params)
        
        if not data:
            return []
        
        matches = []
        for fixture in data.get('response', []):
            match_data = {
                'match_id': fixture['fixture']['id'],
                'home_team': fixture['teams']['home']['name'],
                'away_team': fixture['teams']['away']['name'],
                'home_score': fixture['goals']['home'],
                'away_score': fixture['goals']['away'],
                'status': fixture['fixture']['status']['short'],
                'date': fixture['fixture']['date']
            }
            matches.append(match_data)
        
        logger.info(f"Encontrados {len(matches)} jogos recentes do time {team_id}")
        return matches
    
    def get_league_standings(self, league_id: int, season: int = None) -> List[Dict]:
        """Obtém tabela de classificação de uma liga"""
        if season is None:
            season = datetime.now().year
        
        logger.info(f"Obtendo tabela da liga {league_id}, temporada {season}...")
        
        params = {
            'league': league_id,
            'season': season
        }
        
        data = self._make_request('standings', params)
        
        if not data:
            return []
        
        standings = []
        for league_data in data.get('response', []):
            for team in league_data['league']['standings'][0]:
                team_data = {
                    'league_id': league_id,
                    'season': season,
                    'position': team['rank'],
                    'team_id': team['team']['id'],
                    'team_name': team['team']['name'],
                    'points': team['points'],
                    'played': team['all']['played'],
                    'won': team['all']['win'],
                    'drawn': team['all']['draw'],
                    'lost': team['all']['lose'],
                    'goals_for': team['all']['goals']['for'],
                    'goals_against': team['all']['goals']['against'],
                    'goal_difference': team['goalsDiff']
                }
                standings.append(team_data)
        
        logger.info(f"Encontradas {len(standings)} equipes na tabela")
        return standings
    
    def get_league_fixtures(self, league_id: int, season: int = None) -> List[Dict]:
        """Obtém partidas de uma liga"""
        if season is None:
            season = datetime.now().year
        
        logger.info(f"Obtendo partidas da liga {league_id}, temporada {season}...")
        
        params = {
            'league': league_id,
            'season': season
        }
        
        data = self._make_request('fixtures', params)
        
        if not data:
            return []
        
        matches = []
        for fixture in data.get('response', []):
            match_data = {
                'match_id': fixture['fixture']['id'],
                'league_id': league_id,
                'season': season,
                'home_team': fixture['teams']['home']['name'],
                'away_team': fixture['teams']['away']['name'],
                'home_score': fixture['goals']['home'],
                'away_score': fixture['goals']['away'],
                'status': fixture['fixture']['status']['short'],
                'date': fixture['fixture']['date']
            }
            matches.append(match_data)
        
        logger.info(f"Encontradas {len(matches)} partidas da liga {league_id}")
        return matches
    
    def test_api_connection(self) -> bool:
        """Testa conexão com API"""
        logger.info("Testando conexão com API-Football...")
        
        params = {'live': 'all'}
        data = self._make_request('fixtures', params, use_cache=False)
        
        if data:
            logger.info("✅ Conexão com API-Football funcionando")
            return True
        else:
            logger.error("❌ Erro na conexão com API-Football")
            return False
    
    def get_api_status(self) -> Dict[str, Any]:
        """Obtém status da API"""
        logger.info("Verificando status da API...")
        
        # Testar diferentes endpoints
        endpoints = [
            ('fixtures', {'live': 'all'}),
            ('leagues', {'country': 'England'}),
            ('teams', {'country': 'England'})
        ]
        
        status = {
            'api_key_valid': False,
            'endpoints_working': [],
            'endpoints_failing': [],
            'rate_limit_ok': True,
            'last_check': datetime.now().isoformat()
        }
        
        for endpoint, params in endpoints:
            try:
                data = self._make_request(endpoint, params, use_cache=False)
                if data:
                    status['endpoints_working'].append(endpoint)
                    status['api_key_valid'] = True
                else:
                    status['endpoints_failing'].append(endpoint)
            except Exception as e:
                status['endpoints_failing'].append(f"{endpoint}: {str(e)}")
        
        return status

# Instância global
real_football_api = None

def initialize_real_football_api(api_key: str):
    """Inicializa integração real com API-Football"""
    global real_football_api
    config = APIFootballConfig(api_key=api_key)
    real_football_api = RealFootballAPI(config)
    return real_football_api

if __name__ == "__main__":
    # Teste da integração real com API-Football
    print("🧪 TESTANDO INTEGRAÇÃO REAL COM API-FOOTBALL")
    print("=" * 50)
    
    # Usar API key do ambiente
    import os
    api_key = os.getenv('API_FOOTBALL_KEY', '71b2b62386f2d1275cd3201a73e1e045')
    
    if api_key == 'your-api-key-here':
        print("❌ API key não configurada. Configure API_FOOTBALL_KEY no .env")
        exit(1)
    
    # Inicializar API
    api = initialize_real_football_api(api_key)
    
    # Testar conexão
    if not api.test_api_connection():
        print("❌ Falha na conexão com API-Football")
        exit(1)
    
    # Obter status da API
    status = api.get_api_status()
    print(f"\nStatus da API:")
    print(f"  API Key Válida: {'Sim' if status['api_key_valid'] else 'Não'}")
    print(f"  Endpoints Funcionando: {status['endpoints_working']}")
    print(f"  Endpoints com Falha: {status['endpoints_failing']}")
    
    # Testar diferentes funcionalidades
    print(f"\nTestando funcionalidades...")
    
    # Partidas ao vivo
    live_matches = api.get_live_matches()
    print(f"  Partidas ao vivo: {len(live_matches)}")
    
    # Partidas de hoje
    today_matches = api.get_today_matches()
    print(f"  Partidas de hoje: {len(today_matches)}")
    
    # Partidas próximas
    upcoming_matches = api.get_upcoming_matches(7)
    print(f"  Partidas próximas (7 dias): {len(upcoming_matches)}")
    
    # Tabela da Premier League
    standings = api.get_league_standings(39)  # Premier League
    print(f"  Times na tabela da Premier League: {len(standings)}")
    
    print("\n🎉 TESTE DE INTEGRAÇÃO REAL CONCLUÍDO!")
