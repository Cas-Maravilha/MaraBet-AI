"""
Gerenciador de Banco de Dados - Sistema Básico
Interface para SQLite com operações CRUD
"""

import sqlite3
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path
from .models import League, Team, Match, Odds, Prediction, TeamStatistics, ValueBet

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gerenciador do banco de dados SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self._create_tables()
    
    def connect(self) -> bool:
        """Conecta ao banco de dados"""
        try:
            self.connection = sqlite3.connect(
                str(self.db_path),
                timeout=30,
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Conectado ao banco: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao banco: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do banco de dados"""
        if self.connection:
            self.connection.close()
            logger.info("Desconectado do banco de dados")
    
    def _create_tables(self):
        """Cria tabelas do banco de dados"""
        if not self.connect():
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Tabela de ligas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leagues (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    country TEXT NOT NULL,
                    logo TEXT,
                    type TEXT DEFAULT 'League',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de times
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    code TEXT,
                    country TEXT,
                    founded INTEGER,
                    logo TEXT,
                    venue_name TEXT,
                    venue_city TEXT,
                    venue_capacity INTEGER,
                    league_id INTEGER,
                    season INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (league_id) REFERENCES leagues (id)
                )
            ''')
            
            # Tabela de partidas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    timezone TEXT NOT NULL,
                    status TEXT NOT NULL,
                    status_long TEXT NOT NULL,
                    elapsed INTEGER,
                    venue_id INTEGER,
                    venue_name TEXT,
                    venue_city TEXT,
                    league_id INTEGER NOT NULL,
                    league_name TEXT NOT NULL,
                    league_country TEXT NOT NULL,
                    league_logo TEXT,
                    league_flag TEXT,
                    league_season INTEGER NOT NULL,
                    league_round TEXT,
                    home_team_id INTEGER NOT NULL,
                    home_team_name TEXT NOT NULL,
                    home_team_logo TEXT,
                    home_team_winner BOOLEAN,
                    away_team_id INTEGER NOT NULL,
                    away_team_name TEXT NOT NULL,
                    away_team_logo TEXT,
                    away_team_winner BOOLEAN,
                    home_goals INTEGER,
                    away_goals INTEGER,
                    halftime_home INTEGER,
                    halftime_away INTEGER,
                    fulltime_home INTEGER,
                    fulltime_away INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (league_id) REFERENCES leagues (id),
                    FOREIGN KEY (home_team_id) REFERENCES teams (id),
                    FOREIGN KEY (away_team_id) REFERENCES teams (id)
                )
            ''')
            
            # Tabela de odds
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS odds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    bookmaker TEXT NOT NULL,
                    market TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    odd_value REAL NOT NULL,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (match_id) REFERENCES matches (id)
                )
            ''')
            
            # Tabela de predições
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    model_name TEXT NOT NULL,
                    prediction_type TEXT NOT NULL,
                    prediction_value TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    probability REAL,
                    fair_odd REAL,
                    expected_value REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (match_id) REFERENCES matches (id)
                )
            ''')
            
            # Tabela de estatísticas de times
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id INTEGER NOT NULL,
                    league_id INTEGER NOT NULL,
                    season INTEGER NOT NULL,
                    matches_played INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    draws INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    goals_scored INTEGER DEFAULT 0,
                    goals_conceded INTEGER DEFAULT 0,
                    clean_sheets INTEGER DEFAULT 0,
                    failed_to_score INTEGER DEFAULT 0,
                    form_points INTEGER DEFAULT 0,
                    win_percentage REAL DEFAULT 0.0,
                    avg_goals_scored REAL DEFAULT 0.0,
                    avg_goals_conceded REAL DEFAULT 0.0,
                    clean_sheet_percentage REAL DEFAULT 0.0,
                    failed_to_score_percentage REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (team_id) REFERENCES teams (id),
                    FOREIGN KEY (league_id) REFERENCES leagues (id),
                    UNIQUE(team_id, league_id, season)
                )
            ''')
            
            # Tabela de value bets
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS value_bets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_id INTEGER NOT NULL,
                    market TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    market_odd REAL NOT NULL,
                    fair_odd REAL NOT NULL,
                    expected_value REAL NOT NULL,
                    value_percentage REAL NOT NULL,
                    recommendation TEXT NOT NULL,
                    bookmaker TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (match_id) REFERENCES matches (id)
                )
            ''')
            
            # Índices para performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_date ON matches (date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_league ON matches (league_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches (home_team_id, away_team_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_odds_match ON odds (match_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions (match_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_stats_team ON team_statistics (team_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_value_bets_match ON value_bets (match_id)')
            
            self.connection.commit()
            logger.info("Tabelas criadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
        finally:
            self.disconnect()
    
    def _get_connection(self):
        """Retorna conexão ativa"""
        if not self.connection:
            self.connect()
        return self.connection
    
    # Operações CRUD para Ligas
    def save_league(self, league: League) -> bool:
        """Salva uma liga"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO leagues 
                (id, name, country, logo, type, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                league.id, league.name, league.country, 
                league.logo, league.type, league.created_at or datetime.now()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar liga: {e}")
            return False
    
    def get_league(self, league_id: int) -> Optional[League]:
        """Recupera uma liga"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM leagues WHERE id = ?', (league_id,))
            row = cursor.fetchone()
            
            if row:
                return League(
                    id=row['id'],
                    name=row['name'],
                    country=row['country'],
                    logo=row['logo'],
                    type=row['type'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
            return None
            
        except Exception as e:
            logger.error(f"Erro ao recuperar liga: {e}")
            return None
    
    def get_all_leagues(self) -> List[League]:
        """Recupera todas as ligas"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM leagues ORDER BY name')
            rows = cursor.fetchall()
            
            leagues = []
            for row in rows:
                leagues.append(League(
                    id=row['id'],
                    name=row['name'],
                    country=row['country'],
                    logo=row['logo'],
                    type=row['type'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                ))
            
            return leagues
            
        except Exception as e:
            logger.error(f"Erro ao recuperar ligas: {e}")
            return []
    
    # Operações CRUD para Times
    def save_team(self, team: Team) -> bool:
        """Salva um time"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO teams 
                (id, name, code, country, founded, logo, venue_name, 
                 venue_city, venue_capacity, league_id, season, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                team.id, team.name, team.code, team.country, team.founded,
                team.logo, team.venue_name, team.venue_city, team.venue_capacity,
                team.league_id, team.season, team.created_at or datetime.now()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar time: {e}")
            return False
    
    def get_team(self, team_id: int) -> Optional[Team]:
        """Recupera um time"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM teams WHERE id = ?', (team_id,))
            row = cursor.fetchone()
            
            if row:
                return Team(
                    id=row['id'],
                    name=row['name'],
                    code=row['code'],
                    country=row['country'],
                    founded=row['founded'],
                    logo=row['logo'],
                    venue_name=row['venue_name'],
                    venue_city=row['venue_city'],
                    venue_capacity=row['venue_capacity'],
                    league_id=row['league_id'],
                    season=row['season'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
            return None
            
        except Exception as e:
            logger.error(f"Erro ao recuperar time: {e}")
            return None
    
    def get_teams_by_league(self, league_id: int) -> List[Team]:
        """Recupera times de uma liga"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM teams WHERE league_id = ? ORDER BY name', (league_id,))
            rows = cursor.fetchall()
            
            teams = []
            for row in rows:
                teams.append(Team(
                    id=row['id'],
                    name=row['name'],
                    code=row['code'],
                    country=row['country'],
                    founded=row['founded'],
                    logo=row['logo'],
                    venue_name=row['venue_name'],
                    venue_city=row['venue_city'],
                    venue_capacity=row['venue_capacity'],
                    league_id=row['league_id'],
                    season=row['season'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                ))
            
            return teams
            
        except Exception as e:
            logger.error(f"Erro ao recuperar times: {e}")
            return []
    
    # Operações CRUD para Partidas
    def save_match(self, match: Match) -> bool:
        """Salva uma partida"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO matches 
                (id, date, timestamp, timezone, status, status_long, elapsed,
                 venue_id, venue_name, venue_city, league_id, league_name,
                 league_country, league_logo, league_flag, league_season,
                 league_round, home_team_id, home_team_name, home_team_logo,
                 home_team_winner, away_team_id, away_team_name, away_team_logo,
                 away_team_winner, home_goals, away_goals, halftime_home,
                 halftime_away, fulltime_home, fulltime_away, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match.id, match.date, match.timestamp, match.timezone,
                match.status, match.status_long, match.elapsed,
                match.venue_id, match.venue_name, match.venue_city,
                match.league_id, match.league_name, match.league_country,
                match.league_logo, match.league_flag, match.league_season,
                match.league_round, match.home_team_id, match.home_team_name,
                match.home_team_logo, match.home_team_winner, match.away_team_id,
                match.away_team_name, match.away_team_logo, match.away_team_winner,
                match.home_goals, match.away_goals, match.halftime_home,
                match.halftime_away, match.fulltime_home, match.fulltime_away,
                match.created_at or datetime.now()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar partida: {e}")
            return False
    
    def get_match(self, match_id: int) -> Optional[Match]:
        """Recupera uma partida"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM matches WHERE id = ?', (match_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_match(row)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao recuperar partida: {e}")
            return None
    
    def get_matches_by_league(self, league_id: int, limit: int = 100) -> List[Match]:
        """Recupera partidas de uma liga"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM matches 
                WHERE league_id = ? 
                ORDER BY date DESC 
                LIMIT ?
            ''', (league_id, limit))
            
            rows = cursor.fetchall()
            matches = [self._row_to_match(row) for row in rows]
            return matches
            
        except Exception as e:
            logger.error(f"Erro ao recuperar partidas: {e}")
            return []
    
    def get_matches_by_date_range(self, date_from: str, date_to: str) -> List[Match]:
        """Recupera partidas por período"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM matches 
                WHERE date BETWEEN ? AND ?
                ORDER BY date
            ''', (date_from, date_to))
            
            rows = cursor.fetchall()
            matches = [self._row_to_match(row) for row in rows]
            return matches
            
        except Exception as e:
            logger.error(f"Erro ao recuperar partidas por data: {e}")
            return []
    
    def _row_to_match(self, row) -> Match:
        """Converte linha do banco para objeto Match"""
        return Match(
            id=row['id'],
            date=row['date'],
            timestamp=row['timestamp'],
            timezone=row['timezone'],
            status=row['status'],
            status_long=row['status_long'],
            elapsed=row['elapsed'],
            venue_id=row['venue_id'],
            venue_name=row['venue_name'],
            venue_city=row['venue_city'],
            league_id=row['league_id'],
            league_name=row['league_name'],
            league_country=row['league_country'],
            league_logo=row['league_logo'],
            league_flag=row['league_flag'],
            league_season=row['league_season'],
            league_round=row['league_round'],
            home_team_id=row['home_team_id'],
            home_team_name=row['home_team_name'],
            home_team_logo=row['home_team_logo'],
            home_team_winner=bool(row['home_team_winner']) if row['home_team_winner'] is not None else None,
            away_team_id=row['away_team_id'],
            away_team_name=row['away_team_name'],
            away_team_logo=row['away_team_logo'],
            away_team_winner=bool(row['away_team_winner']) if row['away_team_winner'] is not None else None,
            home_goals=row['home_goals'],
            away_goals=row['away_goals'],
            halftime_home=row['halftime_home'],
            halftime_away=row['halftime_away'],
            fulltime_home=row['fulltime_home'],
            fulltime_away=row['fulltime_away'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )
    
    # Operações CRUD para Odds
    def save_odds(self, odds: Odds) -> bool:
        """Salva odds"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO odds 
                (match_id, bookmaker, market, outcome, odd_value, collected_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                odds.match_id, odds.bookmaker, odds.market,
                odds.outcome, odds.odd_value, odds.collected_at or datetime.now()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar odds: {e}")
            return False
    
    def get_odds_by_match(self, match_id: int) -> List[Odds]:
        """Recupera odds de uma partida"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM odds 
                WHERE match_id = ? 
                ORDER BY bookmaker, market, outcome
            ''', (match_id,))
            
            rows = cursor.fetchall()
            odds_list = []
            
            for row in rows:
                odds_list.append(Odds(
                    id=row['id'],
                    match_id=row['match_id'],
                    bookmaker=row['bookmaker'],
                    market=row['market'],
                    outcome=row['outcome'],
                    odd_value=row['odd_value'],
                    collected_at=datetime.fromisoformat(row['collected_at']) if row['collected_at'] else None
                ))
            
            return odds_list
            
        except Exception as e:
            logger.error(f"Erro ao recuperar odds: {e}")
            return []
    
    # Operações CRUD para Predições
    def save_prediction(self, prediction: Prediction) -> bool:
        """Salva predição"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO predictions 
                (match_id, model_name, prediction_type, prediction_value,
                 confidence, probability, fair_odd, expected_value, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction.match_id, prediction.model_name, prediction.prediction_type,
                prediction.prediction_value, prediction.confidence, prediction.probability,
                prediction.fair_odd, prediction.expected_value, prediction.created_at or datetime.now()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar predição: {e}")
            return False
    
    def get_predictions_by_match(self, match_id: int) -> List[Prediction]:
        """Recupera predições de uma partida"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM predictions 
                WHERE match_id = ? 
                ORDER BY created_at DESC
            ''', (match_id,))
            
            rows = cursor.fetchall()
            predictions = []
            
            for row in rows:
                predictions.append(Prediction(
                    id=row['id'],
                    match_id=row['match_id'],
                    model_name=row['model_name'],
                    prediction_type=row['prediction_type'],
                    prediction_value=row['prediction_value'],
                    confidence=row['confidence'],
                    probability=row['probability'],
                    fair_odd=row['fair_odd'],
                    expected_value=row['expected_value'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                ))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Erro ao recuperar predições: {e}")
            return []
    
    # Operações CRUD para Estatísticas de Times
    def save_team_statistics(self, stats: TeamStatistics) -> bool:
        """Salva estatísticas de time"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO team_statistics 
                (team_id, league_id, season, matches_played, wins, draws, losses,
                 goals_scored, goals_conceded, clean_sheets, failed_to_score,
                 form_points, win_percentage, avg_goals_scored, avg_goals_conceded,
                 clean_sheet_percentage, failed_to_score_percentage, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stats.team_id, stats.league_id, stats.season, stats.matches_played,
                stats.wins, stats.draws, stats.losses, stats.goals_scored,
                stats.goals_conceded, stats.clean_sheets, stats.failed_to_score,
                stats.form_points, stats.win_percentage, stats.avg_goals_scored,
                stats.avg_goals_conceded, stats.clean_sheet_percentage,
                stats.failed_to_score_percentage, stats.created_at or datetime.now()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar estatísticas: {e}")
            return False
    
    def get_team_statistics(self, team_id: int, league_id: int, season: int) -> Optional[TeamStatistics]:
        """Recupera estatísticas de um time"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM team_statistics 
                WHERE team_id = ? AND league_id = ? AND season = ?
            ''', (team_id, league_id, season))
            
            row = cursor.fetchone()
            
            if row:
                return TeamStatistics(
                    id=row['id'],
                    team_id=row['team_id'],
                    league_id=row['league_id'],
                    season=row['season'],
                    matches_played=row['matches_played'],
                    wins=row['wins'],
                    draws=row['draws'],
                    losses=row['losses'],
                    goals_scored=row['goals_scored'],
                    goals_conceded=row['goals_conceded'],
                    clean_sheets=row['clean_sheets'],
                    failed_to_score=row['failed_to_score'],
                    form_points=row['form_points'],
                    win_percentage=row['win_percentage'],
                    avg_goals_scored=row['avg_goals_scored'],
                    avg_goals_conceded=row['avg_goals_conceded'],
                    clean_sheet_percentage=row['clean_sheet_percentage'],
                    failed_to_score_percentage=row['failed_to_score_percentage'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
            return None
            
        except Exception as e:
            logger.error(f"Erro ao recuperar estatísticas: {e}")
            return None
    
    # Operações CRUD para Value Bets
    def save_value_bet(self, value_bet: ValueBet) -> bool:
        """Salva value bet"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO value_bets 
                (match_id, market, outcome, market_odd, fair_odd, expected_value,
                 value_percentage, recommendation, bookmaker, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                value_bet.match_id, value_bet.market, value_bet.outcome,
                value_bet.market_odd, value_bet.fair_odd, value_bet.expected_value,
                value_bet.value_percentage, value_bet.recommendation,
                value_bet.bookmaker, value_bet.created_at or datetime.now()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar value bet: {e}")
            return False
    
    def get_value_bets(self, min_value: float = 0.05) -> List[ValueBet]:
        """Recupera value bets"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM value_bets 
                WHERE expected_value >= ?
                ORDER BY expected_value DESC
            ''', (min_value,))
            
            rows = cursor.fetchall()
            value_bets = []
            
            for row in rows:
                value_bets.append(ValueBet(
                    id=row['id'],
                    match_id=row['match_id'],
                    market=row['market'],
                    outcome=row['outcome'],
                    market_odd=row['market_odd'],
                    fair_odd=row['fair_odd'],
                    expected_value=row['expected_value'],
                    value_percentage=row['value_percentage'],
                    recommendation=row['recommendation'],
                    bookmaker=row['bookmaker'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                ))
            
            return value_bets
            
        except Exception as e:
            logger.error(f"Erro ao recuperar value bets: {e}")
            return []
    
    # Métodos de consulta e estatísticas
    def get_database_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco de dados"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Conta registros em cada tabela
            tables = ['leagues', 'teams', 'matches', 'odds', 'predictions', 'team_statistics', 'value_bets']
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                stats[f'{table}_count'] = cursor.fetchone()[0]
            
            # Tamanho do banco
            stats['database_size_mb'] = self.db_path.stat().st_size / (1024 * 1024)
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """Remove dados antigos"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            # Remove odds antigas
            cursor.execute('DELETE FROM odds WHERE collected_at < ?', (cutoff_date,))
            odds_deleted = cursor.rowcount
            
            # Remove predições antigas
            cursor.execute('DELETE FROM predictions WHERE created_at < ?', (cutoff_date,))
            predictions_deleted = cursor.rowcount
            
            # Remove value bets antigos
            cursor.execute('DELETE FROM value_bets WHERE created_at < ?', (cutoff_date,))
            value_bets_deleted = cursor.rowcount
            
            conn.commit()
            
            total_deleted = odds_deleted + predictions_deleted + value_bets_deleted
            logger.info(f"Limpeza concluída: {total_deleted} registros removidos")
            
            return total_deleted
            
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")
            return 0
