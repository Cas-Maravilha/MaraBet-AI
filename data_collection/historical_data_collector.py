#!/usr/bin/env python3
"""
Coletor de Dados Históricos Reais
MaraBet AI - Coleta de 3+ anos de dados históricos
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
class HistoricalDataConfig:
    """Configuração para coleta de dados históricos"""
    api_key: str
    base_url: str = "https://v3.football.api-sports.io"
    leagues: List[int] = None
    seasons: List[int] = None
    start_date: str = None
    end_date: str = None
    rate_limit: float = 0.1  # 100ms entre requests
    max_retries: int = 3
    timeout: int = 30

class HistoricalDataCollector:
    """Coletor de dados históricos reais"""
    
    def __init__(self, config: HistoricalDataConfig):
        """Inicializa coletor de dados históricos"""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'X-RapidAPI-Key': config.api_key,
            'X-RapidAPI-Host': 'v3.football.api-sports.io'
        })
        
        # Configurar ligas se não especificadas
        if not config.leagues:
            self.config.leagues = [39, 140, 78, 135, 61, 88, 94, 203, 262, 71]  # Principais ligas
        
        # Configurar temporadas se não especificadas
        if not config.seasons:
            current_year = datetime.now().year
            self.config.seasons = list(range(current_year - 3, current_year + 1))
        
        # Configurar datas se não especificadas
        if not config.start_date:
            self.config.start_date = f"{current_year - 3}-01-01"
        if not config.end_date:
            self.config.end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Inicializar banco de dados
        self.db_path = "data/historical_data.db"
        self._init_database()
    
    def _init_database(self):
        """Inicializa banco de dados SQLite"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de partidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER UNIQUE,
                league_id INTEGER,
                season INTEGER,
                date TEXT,
                home_team_id INTEGER,
                home_team_name TEXT,
                away_team_id INTEGER,
                away_team_name TEXT,
                home_score INTEGER,
                away_score INTEGER,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de estatísticas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                team_id INTEGER,
                shots_total INTEGER,
                shots_on_goal INTEGER,
                possession INTEGER,
                passes_total INTEGER,
                passes_accurate INTEGER,
                fouls INTEGER,
                yellow_cards INTEGER,
                red_cards INTEGER,
                FOREIGN KEY (match_id) REFERENCES matches (match_id)
            )
        ''')
        
        # Tabela de odds
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS odds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                bookmaker TEXT,
                home_win REAL,
                draw REAL,
                away_win REAL,
                over_2_5 REAL,
                under_2_5 REAL,
                btts_yes REAL,
                btts_no REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches (match_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados inicializado")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Faz requisição para API com retry"""
        url = f"{self.config.base_url}/{endpoint}"
        
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=self.config.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('results') > 0:
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
    
    def collect_league_fixtures(self, league_id: int, season: int) -> List[Dict]:
        """Coleta partidas de uma liga e temporada"""
        logger.info(f"Coletando partidas da liga {league_id}, temporada {season}")
        
        params = {
            'league': league_id,
            'season': season,
            'from': self.config.start_date,
            'to': self.config.end_date
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
                'date': fixture['fixture']['date'],
                'home_team_id': fixture['teams']['home']['id'],
                'home_team_name': fixture['teams']['home']['name'],
                'away_team_id': fixture['teams']['away']['id'],
                'away_team_name': fixture['teams']['away']['name'],
                'home_score': fixture['goals']['home'],
                'away_score': fixture['goals']['away'],
                'status': fixture['fixture']['status']['short']
            }
            matches.append(match_data)
        
        logger.info(f"Coletadas {len(matches)} partidas da liga {league_id}")
        return matches
    
    def collect_match_statistics(self, match_id: int) -> List[Dict]:
        """Coleta estatísticas de uma partida"""
        params = {'fixture': match_id}
        
        data = self._make_request('fixtures/statistics', params)
        if not data:
            return []
        
        stats = []
        for team_stats in data.get('response', []):
            team_id = team_stats['team']['id']
            team_data = {
                'match_id': match_id,
                'team_id': team_id,
                'shots_total': 0,
                'shots_on_goal': 0,
                'possession': 0,
                'passes_total': 0,
                'passes_accurate': 0,
                'fouls': 0,
                'yellow_cards': 0,
                'red_cards': 0
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
        
        return stats
    
    def collect_odds(self, match_id: int) -> List[Dict]:
        """Coleta odds de uma partida"""
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
                                'over_2_5': None,  # Implementar coleta de over/under
                                'under_2_5': None,
                                'btts_yes': None,  # Implementar coleta de BTTS
                                'btts_no': None
                            })
        
        return odds_list
    
    def save_to_database(self, matches: List[Dict], stats: List[Dict] = None, odds: List[Dict] = None):
        """Salva dados no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Salvar partidas
            for match in matches:
                cursor.execute('''
                    INSERT OR REPLACE INTO matches 
                    (match_id, league_id, season, date, home_team_id, home_team_name, 
                     away_team_id, away_team_name, home_score, away_score, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    match['match_id'], match['league_id'], match['season'], match['date'],
                    match['home_team_id'], match['home_team_name'], match['away_team_id'],
                    match['away_team_name'], match['home_score'], match['away_score'], match['status']
                ))
            
            # Salvar estatísticas
            if stats:
                for stat in stats:
                    cursor.execute('''
                        INSERT OR REPLACE INTO match_stats 
                        (match_id, team_id, shots_total, shots_on_goal, possession, 
                         passes_total, passes_accurate, fouls, yellow_cards, red_cards)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        stat['match_id'], stat['team_id'], stat['shots_total'], stat['shots_on_goal'],
                        stat['possession'], stat['passes_total'], stat['passes_accurate'],
                        stat['fouls'], stat['yellow_cards'], stat['red_cards']
                    ))
            
            # Salvar odds
            if odds:
                for odd in odds:
                    cursor.execute('''
                        INSERT OR REPLACE INTO odds 
                        (match_id, bookmaker, home_win, draw, away_win, over_2_5, 
                         under_2_5, btts_yes, btts_no)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        odd['match_id'], odd['bookmaker'], odd['home_win'], odd['draw'],
                        odd['away_win'], odd['over_2_5'], odd['under_2_5'], odd['btts_yes'], odd['btts_no']
                    ))
            
            conn.commit()
            logger.info(f"Salvos {len(matches)} partidas no banco de dados")
            
        except Exception as e:
            logger.error(f"Erro ao salvar no banco de dados: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def collect_all_historical_data(self) -> Dict[str, int]:
        """Coleta todos os dados históricos"""
        logger.info("Iniciando coleta de dados históricos...")
        
        total_matches = 0
        total_stats = 0
        total_odds = 0
        
        for league_id in self.config.leagues:
            for season in self.config.seasons:
                logger.info(f"Processando liga {league_id}, temporada {season}")
                
                # Coletar partidas
                matches = self.collect_league_fixtures(league_id, season)
                if not matches:
                    continue
                
                # Coletar estatísticas e odds para partidas finalizadas
                finished_matches = [m for m in matches if m['status'] == 'FT']
                stats = []
                odds = []
                
                for match in finished_matches[:10]:  # Limitar para teste
                    logger.info(f"Coletando estatísticas e odds da partida {match['match_id']}")
                    
                    # Coletar estatísticas
                    match_stats = self.collect_match_statistics(match['match_id'])
                    stats.extend(match_stats)
                    
                    # Coletar odds
                    match_odds = self.collect_odds(match['match_id'])
                    odds.extend(match_odds)
                    
                    # Rate limiting
                    time.sleep(self.config.rate_limit)
                
                # Salvar no banco de dados
                self.save_to_database(matches, stats, odds)
                
                total_matches += len(matches)
                total_stats += len(stats)
                total_odds += len(odds)
                
                logger.info(f"Liga {league_id}, temporada {season}: {len(matches)} partidas, {len(stats)} stats, {len(odds)} odds")
        
        return {
            'matches': total_matches,
            'stats': total_stats,
            'odds': total_odds
        }
    
    def export_to_csv(self, output_dir: str = "data/exports"):
        """Exporta dados para CSV"""
        os.makedirs(output_dir, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        
        # Exportar partidas
        matches_df = pd.read_sql_query("SELECT * FROM matches", conn)
        matches_df.to_csv(f"{output_dir}/matches.csv", index=False)
        
        # Exportar estatísticas
        stats_df = pd.read_sql_query("SELECT * FROM match_stats", conn)
        stats_df.to_csv(f"{output_dir}/match_stats.csv", index=False)
        
        # Exportar odds
        odds_df = pd.read_sql_query("SELECT * FROM odds", conn)
        odds_df.to_csv(f"{output_dir}/odds.csv", index=False)
        
        conn.close()
        logger.info(f"Dados exportados para {output_dir}")
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Obtém resumo dos dados coletados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM matches")
        matches_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM match_stats")
        stats_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM odds")
        odds_count = cursor.fetchone()[0]
        
        # Período dos dados
        cursor.execute("SELECT MIN(date), MAX(date) FROM matches")
        date_range = cursor.fetchone()
        
        # Ligas cobertas
        cursor.execute("SELECT DISTINCT league_id FROM matches")
        leagues = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'matches': matches_count,
            'stats': stats_count,
            'odds': odds_count,
            'date_range': date_range,
            'leagues': leagues,
            'database_path': self.db_path
        }

# Instância global
historical_collector = None

def initialize_historical_collector(api_key: str):
    """Inicializa coletor de dados históricos"""
    global historical_collector
    config = HistoricalDataConfig(api_key=api_key)
    historical_collector = HistoricalDataCollector(config)
    return historical_collector

if __name__ == "__main__":
    # Teste do coletor de dados históricos
    print("🧪 TESTANDO COLETOR DE DADOS HISTÓRICOS")
    print("=" * 50)
    
    # Usar API key do ambiente
    import os
    api_key = os.getenv('API_FOOTBALL_KEY', 'your-api-key-here')
    
    if api_key == 'your-api-key-here':
        print("❌ API key não configurada. Configure API_FOOTBALL_KEY no .env")
        exit(1)
    
    # Inicializar coletor
    collector = initialize_historical_collector(api_key)
    
    # Coletar dados (apenas algumas ligas para teste)
    collector.config.leagues = [39, 140]  # Premier League e La Liga
    collector.config.seasons = [2023, 2024]  # Últimas 2 temporadas
    
    print("Iniciando coleta de dados históricos...")
    results = collector.collect_all_historical_data()
    
    print(f"\nResultados da coleta:")
    print(f"  Partidas: {results['matches']}")
    print(f"  Estatísticas: {results['stats']}")
    print(f"  Odds: {results['odds']}")
    
    # Exportar para CSV
    collector.export_to_csv()
    
    # Resumo dos dados
    summary = collector.get_data_summary()
    print(f"\nResumo dos dados:")
    print(f"  Período: {summary['date_range'][0]} a {summary['date_range'][1]}")
    print(f"  Ligas: {summary['leagues']}")
    print(f"  Banco: {summary['database_path']}")
    
    print("\n🎉 TESTE DE COLETA DE DADOS HISTÓRICOS CONCLUÍDO!")
