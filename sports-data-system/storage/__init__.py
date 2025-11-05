"""
Armazenamento - Sistema Básico
Módulo para armazenamento de dados usando SQLite
"""

from .database import DatabaseManager
from .models import Match, Team, League, Odds, Prediction

__all__ = [
    'DatabaseManager',
    'Match',
    'Team', 
    'League',
    'Odds',
    'Prediction'
]

__version__ = '1.0.0'
__author__ = 'MaraBet AI Team'
