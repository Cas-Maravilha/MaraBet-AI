"""
Modelos de Dados - Sistema Básico
Definições de tabelas e modelos para SQLite
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class League:
    """Modelo para liga"""
    id: int
    name: str
    country: str
    logo: Optional[str] = None
    type: str = "League"
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'logo': self.logo,
            'type': self.type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class Team:
    """Modelo para time"""
    id: int
    name: str
    code: Optional[str] = None
    country: Optional[str] = None
    founded: Optional[int] = None
    logo: Optional[str] = None
    venue_name: Optional[str] = None
    venue_city: Optional[str] = None
    venue_capacity: Optional[int] = None
    league_id: Optional[int] = None
    season: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'country': self.country,
            'founded': self.founded,
            'logo': self.logo,
            'venue_name': self.venue_name,
            'venue_city': self.venue_city,
            'venue_capacity': self.venue_capacity,
            'league_id': self.league_id,
            'season': self.season,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class Match:
    """Modelo para partida"""
    id: int
    date: str
    timestamp: int
    timezone: str
    status: str
    status_long: str
    league_id: int
    league_name: str
    league_country: str
    league_season: int
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str
    elapsed: Optional[int] = None
    venue_id: Optional[int] = None
    venue_name: Optional[str] = None
    venue_city: Optional[str] = None
    league_logo: Optional[str] = None
    league_flag: Optional[str] = None
    league_round: Optional[str] = None
    home_team_logo: Optional[str] = None
    home_team_winner: Optional[bool] = None
    away_team_logo: Optional[str] = None
    away_team_winner: Optional[bool] = None
    home_goals: Optional[int] = None
    away_goals: Optional[int] = None
    halftime_home: Optional[int] = None
    halftime_away: Optional[int] = None
    fulltime_home: Optional[int] = None
    fulltime_away: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'date': self.date,
            'timestamp': self.timestamp,
            'timezone': self.timezone,
            'status': self.status,
            'status_long': self.status_long,
            'elapsed': self.elapsed,
            'venue_id': self.venue_id,
            'venue_name': self.venue_name,
            'venue_city': self.venue_city,
            'league_id': self.league_id,
            'league_name': self.league_name,
            'league_country': self.league_country,
            'league_logo': self.league_logo,
            'league_flag': self.league_flag,
            'league_season': self.league_season,
            'league_round': self.league_round,
            'home_team_id': self.home_team_id,
            'home_team_name': self.home_team_name,
            'home_team_logo': self.home_team_logo,
            'home_team_winner': self.home_team_winner,
            'away_team_id': self.away_team_id,
            'away_team_name': self.away_team_name,
            'away_team_logo': self.away_team_logo,
            'away_team_winner': self.away_team_winner,
            'home_goals': self.home_goals,
            'away_goals': self.away_goals,
            'halftime_home': self.halftime_home,
            'halftime_away': self.halftime_away,
            'fulltime_home': self.fulltime_home,
            'fulltime_away': self.fulltime_away,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def total_goals(self) -> Optional[int]:
        """Total de gols na partida"""
        if self.home_goals is not None and self.away_goals is not None:
            return self.home_goals + self.away_goals
        return None
    
    @property
    def result(self) -> Optional[str]:
        """Resultado da partida"""
        if self.home_goals is None or self.away_goals is None:
            return None
        
        if self.home_goals > self.away_goals:
            return 'home_win'
        elif self.away_goals > self.home_goals:
            return 'away_win'
        else:
            return 'draw'
    
    @property
    def both_teams_score(self) -> Optional[bool]:
        """Ambas as equipes marcaram"""
        if self.home_goals is not None and self.away_goals is not None:
            return self.home_goals > 0 and self.away_goals > 0
        return None

@dataclass
class Odds:
    """Modelo para odds"""
    id: int
    match_id: int
    bookmaker: str
    market: str
    outcome: str
    odd_value: float
    collected_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'match_id': self.match_id,
            'bookmaker': self.bookmaker,
            'market': self.market,
            'outcome': self.outcome,
            'odd_value': self.odd_value,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None
        }

@dataclass
class Prediction:
    """Modelo para predição"""
    id: int
    match_id: int
    model_name: str
    prediction_type: str
    prediction_value: str
    confidence: float
    probability: Optional[float] = None
    fair_odd: Optional[float] = None
    expected_value: Optional[float] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'match_id': self.match_id,
            'model_name': self.model_name,
            'prediction_type': self.prediction_type,
            'prediction_value': self.prediction_value,
            'confidence': self.confidence,
            'probability': self.probability,
            'fair_odd': self.fair_odd,
            'expected_value': self.expected_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class TeamStatistics:
    """Modelo para estatísticas de time"""
    id: int
    team_id: int
    league_id: int
    season: int
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int
    clean_sheets: int
    failed_to_score: int
    form_points: int
    win_percentage: float
    avg_goals_scored: float
    avg_goals_conceded: float
    clean_sheet_percentage: float
    failed_to_score_percentage: float
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'team_id': self.team_id,
            'league_id': self.league_id,
            'season': self.season,
            'matches_played': self.matches_played,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'goals_scored': self.goals_scored,
            'goals_conceded': self.goals_conceded,
            'clean_sheets': self.clean_sheets,
            'failed_to_score': self.failed_to_score,
            'form_points': self.form_points,
            'win_percentage': self.win_percentage,
            'avg_goals_scored': self.avg_goals_scored,
            'avg_goals_conceded': self.avg_goals_conceded,
            'clean_sheet_percentage': self.clean_sheet_percentage,
            'failed_to_score_percentage': self.failed_to_score_percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class ValueBet:
    """Modelo para value bet"""
    id: int
    match_id: int
    market: str
    outcome: str
    market_odd: float
    fair_odd: float
    expected_value: float
    value_percentage: float
    recommendation: str
    bookmaker: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'match_id': self.match_id,
            'market': self.market,
            'outcome': self.outcome,
            'market_odd': self.market_odd,
            'fair_odd': self.fair_odd,
            'expected_value': self.expected_value,
            'value_percentage': self.value_percentage,
            'recommendation': self.recommendation,
            'bookmaker': self.bookmaker,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
