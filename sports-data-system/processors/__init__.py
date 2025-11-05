"""
Processadores de Dados - Sistema Básico
Módulo para processamento e análise de dados esportivos
"""

from .statistics import StatisticsProcessor
from .predictions import PredictionsProcessor

__all__ = [
    'StatisticsProcessor',
    'PredictionsProcessor'
]

__version__ = '1.0.0'
__author__ = 'MaraBet AI Team'
