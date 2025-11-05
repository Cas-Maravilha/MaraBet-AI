"""
Coletores de Dados - Sistema Básico
Módulo para coleta de dados esportivos de APIs gratuitas
"""

from .base_collector import BaseCollector
from .football_collector import FootballCollector
from .odds_collector import OddsCollector

__all__ = [
    'BaseCollector',
    'FootballCollector', 
    'OddsCollector'
]

__version__ = '1.0.0'
__author__ = 'MaraBet AI Team'
