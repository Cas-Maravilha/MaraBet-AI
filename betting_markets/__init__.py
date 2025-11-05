"""
Sistema Expandido de Mercados de Apostas - MaraBet AI
Implementa múltiplos mercados de apostas para predições mais específicas
"""

from .expanded_markets import ExpandedBettingMarkets
from .goals_market import GoalsMarket
from .handicap_market import HandicapMarket
from .cards_market import CardsMarket
from .corners_market import CornersMarket
from .double_chance_market import DoubleChanceMarket
from .exact_score_market import ExactScoreMarket

__all__ = [
    'ExpandedBettingMarkets',
    'GoalsMarket',
    'HandicapMarket', 
    'CardsMarket',
    'CornersMarket',
    'DoubleChanceMarket',
    'ExactScoreMarket'
]
