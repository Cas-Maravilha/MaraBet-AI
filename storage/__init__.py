"""
Armazenamento de Dados - MaraBet AI
Módulo para gerenciamento de banco de dados e cache
"""

from .database import engine, Base, get_db, create_tables, check_connection, close_connections
from .models import (
    User, League, Team, Match, Odds, Statistics, 
    Prediction, BettingHistory, BacktestingResults, 
    SystemLog, Notification
)

__all__ = [
    "engine",
    "Base", 
    "get_db",
    "create_tables",
    "check_connection",
    "close_connections",
    "User",
    "League", 
    "Team",
    "Match",
    "Odds",
    "Statistics",
    "Prediction",
    "BettingHistory",
    "BacktestingResults",
    "SystemLog",
    "Notification"
]
