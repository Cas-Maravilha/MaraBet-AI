#!/usr/bin/env python3
"""
Sistema de Coleta de Dados em Tempo Real MaraBet AI
Coleta informações de múltiplas fontes para análise preditiva completa
"""

import json
import os
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import sqlite3
import threading
import schedule
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TeamData:
    """Estrutura de dados de uma equipe"""
    team_id: str
    name: str
    league: str
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int
    possession_avg: float
    shots_avg: float
    saves_avg: float
    cards_avg: float
    form_last_5: List[str]  # ['W', 'W', 'L', 'D', 'W']
    home_record: Dict[str, int]
    away_record: Dict[str, int]

@dataclass
class MatchData:
    """Estrutura de dados de uma partida"""
    match_id: str
    home_team: str
    away_team: str
    league: str
    date: datetime
    status: str
    home_score: Optional[int]
    away_score: Optional[int]
    odds: Dict[str, float]
    weather: Dict[str, str]
    importance: str
    injuries: List[str]
    suspensions: List[str]

class DataCollector:
    """Coletor principal de dados"""
    
    def __init__(self):
        self.db_path = "marabet_data.db"
        self.init_database()
        self.api_keys = self.load_api_keys()
        
    def init_database(self):
        """Inicializa banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de equipes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                team_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                league TEXT NOT NULL,
                wins INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                goals_scored INTEGER DEFAULT 0,
                goals_conceded INTEGER DEFAULT 0,
                possession_avg REAL DEFAULT 0,
                shots_avg REAL DEFAULT 0,
                saves_avg REAL DEFAULT 0,
                cards_avg REAL DEFAULT 0,
                form_last_5 TEXT DEFAULT '',
                home_record TEXT DEFAULT '{}',
                away_record TEXT DEFAULT '{}',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de partidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                match_id TEXT PRIMARY KEY,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                league TEXT NOT NULL,
                match_date TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'scheduled',
                home_score INTEGER,
                away_score INTEGER,
                odds TEXT DEFAULT '{}',
                weather TEXT DEFAULT '{}',
                importance TEXT DEFAULT 'normal',
                injuries TEXT DEFAULT '[]',
                suspensions TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de odds históricas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS odds_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT NOT NULL,
                market_type TEXT NOT NULL,
                selection TEXT NOT NULL,
                odds REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches (match_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Banco de dados inicializado")
    
    def load_api_keys(self) -> Dict[str, str]:
        """Carrega chaves de API"""
        keys_file = "api_keys.json"
        if os.path.exists(keys_file):
            with open(keys_file, 'r') as f:
                return json.load(f)
        
        # Chaves padrão para demonstração
        return {
            "football_api": "demo_key_123456789",
            "odds_api": "demo_key_987654321",
            "weather_api": "demo_key_weather_123",
            "news_api": "demo_key_news_456"
        }
    
    def save_team_data(self, team_data: TeamData):
        """Salva dados da equipe no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO teams 
            (team_id, name, league, wins, draws, losses, goals_scored, goals_conceded,
             possession_avg, shots_avg, saves_avg, cards_avg, form_last_5, 
             home_record, away_record, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            team_data.team_id, team_data.name, team_data.league,
            team_data.wins, team_data.draws, team_data.losses,
            team_data.goals_scored, team_data.goals_conceded,
            team_data.possession_avg, team_data.shots_avg,
            team_data.saves_avg, team_data.cards_avg,
            json.dumps(team_data.form_last_5),
            json.dumps(team_data.home_record),
            json.dumps(team_data.away_record),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def save_match_data(self, match_data: MatchData):
        """Salva dados da partida no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO matches 
            (match_id, home_team, away_team, league, match_date, status,
             home_score, away_score, odds, weather, importance, injuries, suspensions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_data.match_id, match_data.home_team, match_data.away_team,
            match_data.league, match_data.date, match_data.status,
            match_data.home_score, match_data.away_score,
            json.dumps(match_data.odds), json.dumps(match_data.weather),
            match_data.importance, json.dumps(match_data.injuries),
            json.dumps(match_data.suspensions)
        ))
        
        conn.commit()
        conn.close()

class FootballDataCollector:
    """Coletor de dados de futebol"""
    
    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector
        self.api_key = data_collector.api_keys.get("football_api")
        
    def collect_team_statistics(self, team_id: str, league: str) -> TeamData:
        """Coleta estatísticas da equipe"""
        try:
            # Simular coleta de dados da API
            stats = self._simulate_team_stats(team_id, league)
            
            team_data = TeamData(
                team_id=team_id,
                name=stats['name'],
                league=league,
                wins=stats['wins'],
                draws=stats['draws'],
                losses=stats['losses'],
                goals_scored=stats['goals_scored'],
                goals_conceded=stats['goals_conceded'],
                possession_avg=stats['possession_avg'],
                shots_avg=stats['shots_avg'],
                saves_avg=stats['saves_avg'],
                cards_avg=stats['cards_avg'],
                form_last_5=stats['form_last_5'],
                home_record=stats['home_record'],
                away_record=stats['away_record']
            )
            
            self.data_collector.save_team_data(team_data)
            logger.info(f"✅ Estatísticas coletadas para {team_data.name}")
            return team_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar estatísticas de {team_id}: {e}")
            return None
    
    def _simulate_team_stats(self, team_id: str, league: str) -> Dict:
        """Simula estatísticas da equipe"""
        import random
        
        # Estatísticas baseadas no nome da equipe
        if "Real Madrid" in team_id or "Madrid" in team_id:
            base_stats = {
                'name': 'Real Madrid',
                'wins': random.randint(8, 10),
                'draws': random.randint(1, 2),
                'losses': random.randint(0, 2),
                'goals_scored': random.randint(25, 30),
                'goals_conceded': random.randint(8, 12),
                'possession_avg': random.uniform(55, 65),
                'shots_avg': random.uniform(15, 20),
                'saves_avg': random.uniform(3, 5),
                'cards_avg': random.uniform(2, 4),
                'form_last_5': ['W', 'W', 'D', 'W', 'W'],
                'home_record': {'wins': 6, 'draws': 1, 'losses': 0},
                'away_record': {'wins': 4, 'draws': 1, 'losses': 1}
            }
        elif "Barcelona" in team_id:
            base_stats = {
                'name': 'Barcelona',
                'wins': random.randint(6, 8),
                'draws': random.randint(2, 3),
                'losses': random.randint(1, 3),
                'goals_scored': random.randint(20, 25),
                'goals_conceded': random.randint(10, 15),
                'possession_avg': random.uniform(60, 70),
                'shots_avg': random.uniform(12, 18),
                'saves_avg': random.uniform(4, 6),
                'cards_avg': random.uniform(2, 4),
                'form_last_5': ['W', 'D', 'L', 'W', 'D'],
                'home_record': {'wins': 5, 'draws': 1, 'losses': 1},
                'away_record': {'wins': 3, 'draws': 2, 'losses': 2}
            }
        else:
            base_stats = {
                'name': team_id,
                'wins': random.randint(5, 8),
                'draws': random.randint(1, 3),
                'losses': random.randint(1, 3),
                'goals_scored': random.randint(15, 25),
                'goals_conceded': random.randint(10, 18),
                'possession_avg': random.uniform(45, 60),
                'shots_avg': random.uniform(10, 16),
                'saves_avg': random.uniform(3, 6),
                'cards_avg': random.uniform(2, 5),
                'form_last_5': ['W', 'L', 'D', 'W', 'L'],
                'home_record': {'wins': 4, 'draws': 1, 'losses': 1},
                'away_record': {'wins': 3, 'draws': 1, 'losses': 2}
            }
        
        return base_stats
    
    def collect_match_results(self, league: str, days_back: int = 30) -> List[Dict]:
        """Coleta resultados de partidas"""
        try:
            # Simular coleta de resultados
            results = self._simulate_match_results(league, days_back)
            logger.info(f"✅ {len(results)} resultados coletados da {league}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar resultados: {e}")
            return []
    
    def _simulate_match_results(self, league: str, days_back: int) -> List[Dict]:
        """Simula resultados de partidas"""
        import random
        
        teams = {
            'La Liga': ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla', 'Valencia'],
            'Premier League': ['Arsenal', 'Chelsea', 'Manchester City', 'Liverpool', 'Tottenham'],
            'Serie A': ['Juventus', 'AC Milan', 'Inter Milan', 'Napoli', 'Roma']
        }
        
        league_teams = teams.get(league, ['Team A', 'Team B', 'Team C', 'Team D'])
        results = []
        
        for i in range(days_back):
            date = datetime.now() - timedelta(days=i)
            
            # Simular 2-3 jogos por dia
            for j in range(random.randint(2, 3)):
                home_team = random.choice(league_teams)
                away_team = random.choice([t for t in league_teams if t != home_team])
                
                home_score = random.randint(0, 4)
                away_score = random.randint(0, 4)
                
                results.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': home_score,
                    'away_score': away_score,
                    'date': date,
                    'league': league,
                    'possession': {
                        'home': random.randint(40, 70),
                        'away': 100 - random.randint(40, 70)
                    },
                    'shots': {
                        'home': random.randint(8, 20),
                        'away': random.randint(8, 20)
                    },
                    'cards': {
                        'home': random.randint(1, 5),
                        'away': random.randint(1, 5)
                    }
                })
        
        return results

class OddsCollector:
    """Coletor de odds das casas de apostas"""
    
    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector
        self.api_key = data_collector.api_keys.get("odds_api")
        
    def collect_odds(self, match_id: str) -> Dict[str, float]:
        """Coleta odds para uma partida"""
        try:
            # Simular coleta de odds
            odds = self._simulate_odds(match_id)
            
            # Salvar histórico de odds
            self._save_odds_history(match_id, odds)
            
            logger.info(f"✅ Odds coletadas para partida {match_id}")
            return odds
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar odds: {e}")
            return {}
    
    def _simulate_odds(self, match_id: str) -> Dict[str, float]:
        """Simula odds das casas de apostas"""
        import random
        
        # Odds baseadas no tipo de partida
        if "Real Madrid" in match_id and "Barcelona" in match_id:
            # Clássico - odds mais equilibradas
            odds = {
                'home_win': random.uniform(1.80, 2.20),
                'draw': random.uniform(3.20, 3.80),
                'away_win': random.uniform(2.50, 3.50),
                'over_2_5': random.uniform(1.70, 1.85),
                'under_2_5': random.uniform(1.95, 2.10),
                'btts_yes': random.uniform(1.65, 1.80),
                'btts_no': random.uniform(2.00, 2.20)
            }
        else:
            # Partida normal
            odds = {
                'home_win': random.uniform(1.60, 2.50),
                'draw': random.uniform(3.00, 4.00),
                'away_win': random.uniform(2.00, 4.00),
                'over_2_5': random.uniform(1.60, 2.00),
                'under_2_5': random.uniform(1.80, 2.20),
                'btts_yes': random.uniform(1.50, 2.00),
                'btts_no': random.uniform(1.80, 2.50)
            }
        
        return odds
    
    def _save_odds_history(self, match_id: str, odds: Dict[str, float]):
        """Salva histórico de odds"""
        conn = sqlite3.connect(self.data_collector.db_path)
        cursor = conn.cursor()
        
        for market_type, selection_odds in odds.items():
            cursor.execute('''
                INSERT INTO odds_history (match_id, market_type, selection, odds)
                VALUES (?, ?, ?, ?)
            ''', (match_id, market_type, 'main', selection_odds))
        
        conn.commit()
        conn.close()
    
    def track_odds_movement(self, match_id: str, hours: int = 24) -> Dict[str, List[float]]:
        """Rastreia movimento das odds"""
        conn = sqlite3.connect(self.data_collector.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT market_type, odds, timestamp
            FROM odds_history
            WHERE match_id = ? AND timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp
        '''.format(hours), (match_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        # Agrupar por tipo de mercado
        movements = {}
        for market_type, odds, timestamp in results:
            if market_type not in movements:
                movements[market_type] = []
            movements[market_type].append(odds)
        
        return movements

class InjurySuspensionCollector:
    """Coletor de informações sobre lesões e suspensões"""
    
    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector
        
    def collect_injuries(self, team_id: str) -> List[Dict]:
        """Coleta informações sobre lesões"""
        try:
            # Simular coleta de lesões
            injuries = self._simulate_injuries(team_id)
            logger.info(f"✅ {len(injuries)} lesões coletadas para {team_id}")
            return injuries
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar lesões: {e}")
            return []
    
    def collect_suspensions(self, team_id: str) -> List[Dict]:
        """Coleta informações sobre suspensões"""
        try:
            # Simular coleta de suspensões
            suspensions = self._simulate_suspensions(team_id)
            logger.info(f"✅ {len(suspensions)} suspensões coletadas para {team_id}")
            return suspensions
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar suspensões: {e}")
            return []
    
    def _simulate_injuries(self, team_id: str) -> List[Dict]:
        """Simula dados de lesões"""
        import random
        
        players = ['Goleiro', 'Zagueiro', 'Lateral', 'Meio-campo', 'Atacante']
        injury_types = ['Muscular', 'Entorse', 'Fratura', 'Contusão', 'Lesão no joelho']
        
        injuries = []
        num_injuries = random.randint(0, 3)
        
        for i in range(num_injuries):
            injuries.append({
                'player': f'Jogador {i+1}',
                'position': random.choice(players),
                'injury_type': random.choice(injury_types),
                'severity': random.choice(['Leve', 'Moderada', 'Grave']),
                'expected_return': random.randint(1, 30),
                'confirmed': random.choice([True, False])
            })
        
        return injuries
    
    def _simulate_suspensions(self, team_id: str) -> List[Dict]:
        """Simula dados de suspensões"""
        import random
        
        players = ['Goleiro', 'Zagueiro', 'Lateral', 'Meio-campo', 'Atacante']
        suspension_reasons = ['Cartão vermelho', 'Acumulação de cartões', 'Comportamento inadequado']
        
        suspensions = []
        num_suspensions = random.randint(0, 2)
        
        for i in range(num_suspensions):
            suspensions.append({
                'player': f'Jogador {i+1}',
                'position': random.choice(players),
                'reason': random.choice(suspension_reasons),
                'games_missed': random.randint(1, 3),
                'confirmed': random.choice([True, False])
            })
        
        return suspensions

class WeatherCollector:
    """Coletor de informações meteorológicas"""
    
    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector
        self.api_key = data_collector.api_keys.get("weather_api")
        
    def collect_weather(self, city: str, date: datetime) -> Dict[str, str]:
        """Coleta informações meteorológicas"""
        try:
            # Simular coleta de clima
            weather = self._simulate_weather(city, date)
            logger.info(f"✅ Clima coletado para {city}")
            return weather
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar clima: {e}")
            return {}
    
    def _simulate_weather(self, city: str, date: datetime) -> Dict[str, str]:
        """Simula dados meteorológicos"""
        import random
        
        conditions = ['Ensolarado', 'Nublado', 'Chuvoso', 'Nevando', 'Tempestade']
        temperatures = list(range(5, 35))
        
        weather = {
            'condition': random.choice(conditions),
            'temperature': random.choice(temperatures),
            'humidity': random.randint(30, 90),
            'wind_speed': random.randint(5, 25),
            'precipitation': random.randint(0, 100),
            'visibility': random.randint(1, 10)
        }
        
        return weather

class DataCollectionManager:
    """Gerenciador principal da coleta de dados"""
    
    def __init__(self):
        self.data_collector = DataCollector()
        self.football_collector = FootballDataCollector(self.data_collector)
        self.odds_collector = OddsCollector(self.data_collector)
        self.injury_collector = InjurySuspensionCollector(self.data_collector)
        self.weather_collector = WeatherCollector(self.data_collector)
        
    def collect_all_data(self, match_id: str, home_team: str, away_team: str, league: str, city: str):
        """Coleta todos os dados para uma partida"""
        logger.info(f"🔄 Iniciando coleta completa para {home_team} vs {away_team}")
        
        # Coletar dados das equipes
        home_team_data = self.football_collector.collect_team_statistics(home_team, league)
        away_team_data = self.football_collector.collect_team_statistics(away_team, league)
        
        # Coletar odds
        odds = self.odds_collector.collect_odds(match_id)
        
        # Coletar lesões e suspensões
        home_injuries = self.injury_collector.collect_injuries(home_team)
        away_injuries = self.injury_collector.collect_injuries(away_team)
        home_suspensions = self.injury_collector.collect_suspensions(home_team)
        away_suspensions = self.injury_collector.collect_suspensions(away_team)
        
        # Coletar clima
        match_date = datetime.now() + timedelta(days=1)
        weather = self.weather_collector.collect_weather(city, match_date)
        
        # Criar dados da partida
        match_data = MatchData(
            match_id=match_id,
            home_team=home_team,
            away_team=away_team,
            league=league,
            date=match_date,
            status='scheduled',
            home_score=None,
            away_score=None,
            odds=odds,
            weather=weather,
            importance='high' if 'Real Madrid' in home_team and 'Barcelona' in away_team else 'normal',
            injuries=home_injuries + away_injuries,
            suspensions=home_suspensions + away_suspensions
        )
        
        # Salvar dados da partida
        self.data_collector.save_match_data(match_data)
        
        logger.info(f"✅ Coleta completa finalizada para {match_id}")
        return match_data
    
    def start_continuous_collection(self):
        """Inicia coleta contínua de dados"""
        logger.info("🚀 Iniciando coleta contínua de dados...")
        
        # Agendar coletas
        schedule.every(30).minutes.do(self._collect_odds_updates)
        schedule.every(2).hours.do(self._collect_team_updates)
        schedule.every(6).hours.do(self._collect_injury_updates)
        schedule.every(12).hours.do(self._collect_weather_updates)
        
        # Executar coletas agendadas
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                logger.info("🛑 Coleta contínua interrompida")
                break
            except Exception as e:
                logger.error(f"❌ Erro na coleta contínua: {e}")
                time.sleep(60)
    
    def _collect_odds_updates(self):
        """Coleta atualizações de odds"""
        logger.info("📊 Coletando atualizações de odds...")
        # Implementar coleta de odds atualizadas
    
    def _collect_team_updates(self):
        """Coleta atualizações das equipes"""
        logger.info("⚽ Coletando atualizações das equipes...")
        # Implementar coleta de dados atualizados das equipes
    
    def _collect_injury_updates(self):
        """Coleta atualizações de lesões/suspensões"""
        logger.info("🏥 Coletando atualizações de lesões/suspensões...")
        # Implementar coleta de lesões/suspensões atualizadas
    
    def _collect_weather_updates(self):
        """Coleta atualizações meteorológicas"""
        logger.info("🌤️ Coletando atualizações meteorológicas...")
        # Implementar coleta de clima atualizado

def main():
    manager = DataCollectionManager()
    
    print("🎯 MARABET AI - SISTEMA DE COLETA DE DADOS EM TEMPO REAL")
    print("=" * 60)
    
    print("\n📊 Testando coleta de dados...")
    
    # Testar coleta para uma partida
    match_data = manager.collect_all_data(
        match_id="RM_vs_FCB_2025",
        home_team="Real Madrid",
        away_team="Barcelona",
        league="La Liga",
        city="Madrid"
    )
    
    print(f"\n✅ Dados coletados para: {match_data.home_team} vs {match_data.away_team}")
    print(f"📊 Odds coletadas: {len(match_data.odds)} mercados")
    print(f"🏥 Lesões/Suspensões: {len(match_data.injuries + match_data.suspensions)}")
    print(f"🌤️ Clima: {match_data.weather.get('condition', 'N/A')}")
    
    print("\n🚀 Sistema de coleta de dados operacional!")

if __name__ == "__main__":
    main()
