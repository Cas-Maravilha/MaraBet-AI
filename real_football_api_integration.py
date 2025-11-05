#!/usr/bin/env python3
"""
Sistema de Integração com Football API Real MaraBet AI
Coleta dados reais de partidas, estatísticas e odds usando API oficial
"""

import json
import os
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealFootballAPIClient:
    """Cliente para Football API com dados reais"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        self.db_path = "real_football_data.db"
        self.init_database()
        
    def init_database(self):
        """Inicializa banco de dados para dados reais"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de ligas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leagues (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                country TEXT NOT NULL,
                logo TEXT,
                flag TEXT,
                season INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de equipes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                country TEXT,
                founded INTEGER,
                logo TEXT,
                venue_name TEXT,
                venue_city TEXT,
                venue_capacity INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de partidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                home_team_id INTEGER,
                away_team_id INTEGER,
                league_id INTEGER,
                season INTEGER,
                round TEXT,
                date TIMESTAMP,
                status TEXT,
                home_score INTEGER,
                away_score INTEGER,
                home_goals TEXT,
                away_goals TEXT,
                venue TEXT,
                referee TEXT,
                weather TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (home_team_id) REFERENCES teams (id),
                FOREIGN KEY (away_team_id) REFERENCES teams (id),
                FOREIGN KEY (league_id) REFERENCES leagues (id)
            )
        ''')
        
        # Tabela de estatísticas de partidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                team_id INTEGER,
                shots_total INTEGER,
                shots_on INTEGER,
                possession INTEGER,
                passes_total INTEGER,
                passes_accuracy INTEGER,
                fouls INTEGER,
                corners INTEGER,
                offsides INTEGER,
                cards_yellow INTEGER,
                cards_red INTEGER,
                goalkeeper_saves INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches (id),
                FOREIGN KEY (team_id) REFERENCES teams (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Banco de dados de dados reais inicializado")
    
    def make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Faz requisição para a API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results') > 0:
                    return data
                else:
                    logger.warning(f"⚠️ Nenhum resultado encontrado para {endpoint}")
                    return None
            else:
                logger.error(f"❌ Erro HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na requisição para {endpoint}: {e}")
            return None
    
    def get_leagues(self, country: str = None) -> List[Dict]:
        """Obtém listagem de ligas"""
        params = {}
        if country:
            params['country'] = country
            
        data = self.make_request('leagues', params)
        if data:
            leagues = data.get('response', [])
            logger.info(f"✅ {len(leagues)} ligas encontradas")
            return leagues
        return []
    
    def get_teams_by_league(self, league_id: int, season: int = 2024) -> List[Dict]:
        """Obtém equipes de uma liga específica"""
        params = {
            'league': league_id,
            'season': season
        }
        
        data = self.make_request('teams', params)
        if data:
            teams = data.get('response', [])
            logger.info(f"✅ {len(teams)} equipes encontradas na liga {league_id}")
            return teams
        return []
    
    def get_fixtures(self, league_id: int = None, season: int = 2024, 
                     from_date: str = None, to_date: str = None) -> List[Dict]:
        """Obtém partidas/fixtures"""
        params = {
            'season': season
        }
        
        if league_id:
            params['league'] = league_id
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
            
        data = self.make_request('fixtures', params)
        if data:
            fixtures = data.get('response', [])
            logger.info(f"✅ {len(fixtures)} partidas encontradas")
            return fixtures
        return []
    
    def get_match_statistics(self, fixture_id: int) -> Dict:
        """Obtém estatísticas detalhadas de uma partida"""
        params = {'fixture': fixture_id}
        
        data = self.make_request('fixtures/statistics', params)
        if data:
            stats = data.get('response', [])
            logger.info(f"✅ Estatísticas obtidas para partida {fixture_id}")
            return stats
        return []
    
    def get_team_statistics(self, team_id: int, league_id: int, season: int = 2024) -> Dict:
        """Obtém estatísticas da equipe"""
        params = {
            'team': team_id,
            'league': league_id,
            'season': season
        }
        
        data = self.make_request('teams/statistics', params)
        if data:
            stats = data.get('response', [])
            if stats:
                logger.info(f"✅ Estatísticas obtidas para equipe {team_id}")
                return stats[0]
        return {}
    
    def get_head_to_head(self, team1_id: int, team2_id: int, last: int = 5) -> List[Dict]:
        """Obtém histórico de confrontos diretos"""
        params = {
            'h2h': f"{team1_id}-{team2_id}",
            'last': last
        }
        
        data = self.make_request('fixtures/headtohead', params)
        if data:
            h2h = data.get('response', [])
            logger.info(f"✅ {len(h2h)} confrontos diretos encontrados")
            return h2h
        return []
    
    def save_league_data(self, league_data: Dict):
        """Salva dados da liga"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        league = league_data['league']
        country = league_data['country']
        
        cursor.execute('''
            INSERT OR REPLACE INTO leagues 
            (id, name, country, logo, flag, season)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            league['id'], league['name'], country['name'],
            league.get('logo', ''), country.get('flag', ''),
            league_data.get('seasons', [{}])[0].get('year', 2024)
        ))
        
        conn.commit()
        conn.close()
    
    def save_team_data(self, team_data: Dict):
        """Salva dados da equipe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        team = team_data['team']
        venue = team_data.get('venue', {})
        
        cursor.execute('''
            INSERT OR REPLACE INTO teams 
            (id, name, country, founded, logo, venue_name, venue_city, venue_capacity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            team['id'], team['name'], team.get('country', ''),
            team.get('founded', 0), team.get('logo', ''),
            venue.get('name', ''), venue.get('city', ''),
            venue.get('capacity', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def save_match_data(self, match_data: Dict):
        """Salva dados da partida"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        fixture = match_data['fixture']
        teams = match_data['teams']
        league = match_data['league']
        goals = match_data.get('goals', {})
        
        cursor.execute('''
            INSERT OR REPLACE INTO matches 
            (id, home_team_id, away_team_id, league_id, season, round, date, 
             status, home_score, away_score, home_goals, away_goals, venue, referee)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fixture['id'], teams['home']['id'], teams['away']['id'],
            league['id'], league['season'], league.get('round', ''),
            fixture['date'], fixture['status']['short'],
            goals.get('home'), goals.get('away'),
            json.dumps(goals.get('home', {})), json.dumps(goals.get('away', {})),
            fixture.get('venue', {}).get('name', ''), fixture.get('referee', '')
        ))
        
        conn.commit()
        conn.close()
    
    def save_match_statistics(self, fixture_id: int, stats_data: List[Dict]):
        """Salva estatísticas da partida"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for team_stats in stats_data:
            team_id = team_stats['team']['id']
            stats = team_stats['statistics']
            
            # Converter estatísticas para valores numéricos
            stats_dict = {}
            for stat in stats:
                stats_dict[stat['type']] = stat['value']
            
            cursor.execute('''
                INSERT OR REPLACE INTO match_stats 
                (match_id, team_id, shots_total, shots_on, possession, passes_total,
                 passes_accuracy, fouls, corners, offsides, cards_yellow, cards_red, goalkeeper_saves)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fixture_id, team_id,
                stats_dict.get('Shots Total', 0),
                stats_dict.get('Shots on Goal', 0),
                stats_dict.get('Ball Possession', 0),
                stats_dict.get('Total Shots', 0),
                stats_dict.get('Passes %', 0),
                stats_dict.get('Fouls', 0),
                stats_dict.get('Corner Kicks', 0),
                stats_dict.get('Offsides', 0),
                stats_dict.get('Yellow Cards', 0),
                stats_dict.get('Red Cards', 0),
                stats_dict.get('Goalkeeper Saves', 0)
            ))
        
        conn.commit()
        conn.close()

class RealDataCollector:
    """Coletor de dados reais"""
    
    def __init__(self, api_key: str):
        self.api_client = RealFootballAPIClient(api_key)
        
    def collect_league_data(self, country: str = "Portugal"):
        """Coleta dados das ligas"""
        logger.info(f"📊 Coletando dados das ligas de {country}...")
        
        leagues = self.api_client.get_leagues(country)
        for league_data in leagues:
            self.api_client.save_league_data(league_data)
            logger.info(f"✅ Liga salva: {league_data['league']['name']}")
        
        return leagues
    
    def collect_teams_data(self, league_id: int, season: int = 2024):
        """Coleta dados das equipes"""
        logger.info(f"⚽ Coletando dados das equipes da liga {league_id}...")
        
        teams = self.api_client.get_teams_by_league(league_id, season)
        for team_data in teams:
            self.api_client.save_team_data(team_data)
            logger.info(f"✅ Equipe salva: {team_data['team']['name']}")
        
        return teams
    
    def collect_fixtures_data(self, league_id: int = None, days_ahead: int = 7):
        """Coleta dados das partidas"""
        logger.info(f"🏆 Coletando partidas dos próximos {days_ahead} dias...")
        
        from_date = datetime.now().strftime('%Y-%m-%d')
        to_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        fixtures = self.api_client.get_fixtures(
            league_id=league_id,
            from_date=from_date,
            to_date=to_date
        )
        
        for fixture_data in fixtures:
            self.api_client.save_match_data(fixture_data)
            logger.info(f"✅ Partida salva: {fixture_data['teams']['home']['name']} vs {fixture_data['teams']['away']['name']}")
        
        return fixtures
    
    def collect_match_statistics(self, fixture_id: int):
        """Coleta estatísticas de uma partida"""
        logger.info(f"📊 Coletando estatísticas da partida {fixture_id}...")
        
        stats = self.api_client.get_match_statistics(fixture_id)
        if stats:
            self.api_client.save_match_statistics(fixture_id, stats)
            logger.info(f"✅ Estatísticas salvas para partida {fixture_id}")
        
        return stats
    
    def collect_comprehensive_data(self):
        """Coleta dados abrangentes"""
        logger.info("🚀 Iniciando coleta abrangente de dados reais...")
        
        # Coletar ligas principais
        countries = ["Portugal", "Spain", "England", "Italy", "Germany", "France"]
        all_leagues = []
        
        for country in countries:
            leagues = self.collect_league_data(country)
            all_leagues.extend(leagues)
            time.sleep(1)  # Rate limiting
        
        # Coletar equipes das ligas principais
        main_leagues = [39, 140, 78, 135, 61]  # Premier League, La Liga, Bundesliga, Serie A, Ligue 1
        all_teams = []
        
        for league_id in main_leagues:
            teams = self.collect_teams_data(league_id)
            all_teams.extend(teams)
            time.sleep(1)
        
        # Coletar partidas dos próximos 7 dias
        fixtures = self.collect_fixtures_data(days_ahead=7)
        
        logger.info(f"✅ Coleta completa finalizada!")
        logger.info(f"📊 Ligas coletadas: {len(all_leagues)}")
        logger.info(f"⚽ Equipes coletadas: {len(all_teams)}")
        logger.info(f"🏆 Partidas coletadas: {len(fixtures)}")
        
        return {
            'leagues': all_leagues,
            'teams': all_teams,
            'fixtures': fixtures
        }

def main():
    # Chave da API fornecida pelo usuário
    API_KEY = "71b2b62386f2d1275cd3201a73e1e045"
    
    print("🎯 MARABET AI - INTEGRAÇÃO COM FOOTBALL API REAL")
    print("=" * 60)
    
    # Inicializar coletor
    collector = RealDataCollector(API_KEY)
    
    print(f"🔑 API Key configurada: {API_KEY[:10]}...")
    print("📊 Iniciando coleta de dados reais...")
    
    try:
        # Coletar dados abrangentes
        data = collector.collect_comprehensive_data()
        
        print("\n✅ COLETA DE DADOS REAIS CONCLUÍDA!")
        print("=" * 50)
        print(f"📊 Ligas processadas: {len(data['leagues'])}")
        print(f"⚽ Equipes processadas: {len(data['teams'])}")
        print(f"🏆 Partidas processadas: {len(data['fixtures'])}")
        
        # Mostrar algumas partidas coletadas
        print("\n🏆 PRÓXIMAS PARTIDAS COLETADAS:")
        for i, fixture in enumerate(data['fixtures'][:5], 1):
            home_team = fixture['teams']['home']['name']
            away_team = fixture['teams']['away']['name']
            date = fixture['fixture']['date'][:10]
            league = fixture['league']['name']
            
            print(f"{i}. {home_team} vs {away_team}")
            print(f"   📅 {date} | 🏟️ {league}")
        
        print(f"\n🎯 Sistema integrado com dados reais da Football API!")
        print("📊 Dados salvos no banco SQLite: real_football_data.db")
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta de dados: {e}")
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
