"""
Coletores de Dados - MaraBet AI
Módulo para coleta de dados de APIs externas
"""

from .base_collector import BaseCollector
from .football_collector import FootballCollector
from .odds_collector import OddsCollector

__all__ = [
    "BaseCollector",
    "FootballCollector",
    "OddsCollector"
]
