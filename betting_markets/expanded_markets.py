#!/usr/bin/env python3
"""
Sistema Expandido de Mercados de Apostas - MaraBet AI
Implementa múltiplos mercados de apostas para predições mais específicas
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class MarketType(str, Enum):
    """Tipos de mercados de apostas"""
    # Mercados básicos
    MATCH_WINNER = "match_winner"  # 1X2
    DOUBLE_CHANCE = "double_chance"  # 1X, X2, 12
    
    # Mercados de golos
    OVER_UNDER = "over_under"  # Over/Under 0.5, 1.5, 2.5, 3.5, etc.
    BOTH_TEAMS_SCORE = "both_teams_score"  # BTTS Yes/No
    EXACT_GOALS = "exact_goals"  # 0, 1, 2, 3+ gols
    FIRST_HALF_GOALS = "first_half_goals"  # Over/Under 1ª parte
    
    # Mercados de handicap
    ASIAN_HANDICAP = "asian_handicap"  # Handicap asiático
    EUROPEAN_HANDICAP = "european_handicap"  # Handicap europeu
    
    # Mercados de resultado exato
    EXACT_SCORE = "exact_score"  # Resultado exato (1-0, 2-1, etc.)
    HALF_TIME_SCORE = "half_time_score"  # Resultado do intervalo
    
    # Mercados de cartões
    TOTAL_CARDS = "total_cards"  # Over/Under cartões
    YELLOW_CARDS = "yellow_cards"  # Cartões amarelos
    RED_CARDS = "red_cards"  # Cartões vermelhos
    FIRST_CARD = "first_card"  # Primeiro cartão
    
    # Mercados de cantos
    TOTAL_CORNERS = "total_corners"  # Over/Under cantos
    CORNER_HANDICAP = "corner_handicap"  # Handicap de cantos
    FIRST_CORNER = "first_corner"  # Primeiro canto
    
    # Mercados de tempo
    FIRST_GOAL = "first_goal"  # Primeiro gol
    LAST_GOAL = "last_goal"  # Último gol
    GOAL_INTERVAL = "goal_interval"  # Intervalo de gols
    
    # Mercados especiais
    CLEAN_SHEET = "clean_sheet"  # Jogo limpo
    WIN_TO_NIL = "win_to_nil"  # Vitória sem sofrer gols
    COMEBACK = "comeback"  # Virada

@dataclass
class MarketOdds:
    """Estrutura para odds de mercado"""
    market_type: MarketType
    selection: str
    odds: float
    probability: float
    bookmaker: str
    timestamp: datetime
    confidence: float = 0.0
    expected_value: float = 0.0

@dataclass
class MarketPrediction:
    """Estrutura para predição de mercado"""
    market_type: MarketType
    selection: str
    predicted_probability: float
    confidence: float
    expected_value: float
    kelly_fraction: float
    recommended: bool = False
    reasoning: str = ""

class ExpandedBettingMarkets:
    """Sistema expandido de mercados de apostas"""
    
    def __init__(self):
        self.markets = {}
        self._initialize_markets()
    
    def _initialize_markets(self):
        """Inicializa todos os mercados disponíveis"""
        self.markets = {
            MarketType.MATCH_WINNER: self._create_match_winner_market(),
            MarketType.DOUBLE_CHANCE: self._create_double_chance_market(),
            MarketType.OVER_UNDER: self._create_over_under_market(),
            MarketType.BOTH_TEAMS_SCORE: self._create_btts_market(),
            MarketType.EXACT_GOALS: self._create_exact_goals_market(),
            MarketType.ASIAN_HANDICAP: self._create_asian_handicap_market(),
            MarketType.EUROPEAN_HANDICAP: self._create_european_handicap_market(),
            MarketType.EXACT_SCORE: self._create_exact_score_market(),
            MarketType.TOTAL_CARDS: self._create_cards_market(),
            MarketType.TOTAL_CORNERS: self._create_corners_market(),
            MarketType.CLEAN_SHEET: self._create_clean_sheet_market(),
        }
    
    def _create_match_winner_market(self) -> Dict[str, Any]:
        """Cria mercado de resultado da partida (1X2)"""
        return {
            "name": "Resultado da Partida",
            "selections": ["1", "X", "2"],
            "description": "Vitória da casa, empate ou vitória visitante",
            "min_odds": 1.01,
            "max_odds": 50.0
        }
    
    def _create_double_chance_market(self) -> Dict[str, Any]:
        """Cria mercado de dupla chance"""
        return {
            "name": "Dupla Chance",
            "selections": ["1X", "X2", "12"],
            "description": "Casa ou empate, empate ou visitante, casa ou visitante",
            "min_odds": 1.01,
            "max_odds": 2.0
        }
    
    def _create_over_under_market(self) -> Dict[str, Any]:
        """Cria mercado over/under gols"""
        return {
            "name": "Total de Gols",
            "selections": ["Over 0.5", "Under 0.5", "Over 1.5", "Under 1.5", 
                          "Over 2.5", "Under 2.5", "Over 3.5", "Under 3.5"],
            "description": "Total de gols na partida",
            "min_odds": 1.01,
            "max_odds": 10.0
        }
    
    def _create_btts_market(self) -> Dict[str, Any]:
        """Cria mercado ambas marcam"""
        return {
            "name": "Ambas Marcam",
            "selections": ["Sim", "Não"],
            "description": "Ambas as equipes marcam pelo menos um gol",
            "min_odds": 1.10,
            "max_odds": 5.0
        }
    
    def _create_exact_goals_market(self) -> Dict[str, Any]:
        """Cria mercado gols exatos"""
        return {
            "name": "Gols Exatos",
            "selections": ["0", "1", "2", "3", "4", "5+"],
            "description": "Número exato de gols na partida",
            "min_odds": 1.50,
            "max_odds": 50.0
        }
    
    def _create_asian_handicap_market(self) -> Dict[str, Any]:
        """Cria mercado handicap asiático"""
        return {
            "name": "Handicap Asiático",
            "selections": ["-2.5", "-2", "-1.5", "-1", "-0.5", "+0.5", "+1", "+1.5", "+2", "+2.5"],
            "description": "Handicap asiático com meio gols",
            "min_odds": 1.50,
            "max_odds": 3.0
        }
    
    def _create_european_handicap_market(self) -> Dict[str, Any]:
        """Cria mercado handicap europeu"""
        return {
            "name": "Handicap Europeu",
            "selections": ["-3", "-2", "-1", "0", "+1", "+2", "+3"],
            "description": "Handicap europeu com gols inteiros",
            "min_odds": 1.50,
            "max_odds": 3.0
        }
    
    def _create_exact_score_market(self) -> Dict[str, Any]:
        """Cria mercado resultado exato"""
        return {
            "name": "Resultado Exato",
            "selections": ["1-0", "2-0", "2-1", "3-0", "3-1", "3-2", "0-0", "1-1", "2-2", "3-3"],
            "description": "Resultado exato da partida",
            "min_odds": 2.0,
            "max_odds": 100.0
        }
    
    def _create_cards_market(self) -> Dict[str, Any]:
        """Cria mercado de cartões"""
        return {
            "name": "Total de Cartões",
            "selections": ["Over 1.5", "Under 1.5", "Over 2.5", "Under 2.5", 
                          "Over 3.5", "Under 3.5", "Over 4.5", "Under 4.5"],
            "description": "Total de cartões na partida",
            "min_odds": 1.20,
            "max_odds": 8.0
        }
    
    def _create_corners_market(self) -> Dict[str, Any]:
        """Cria mercado de cantos"""
        return {
            "name": "Total de Cantos",
            "selections": ["Over 8.5", "Under 8.5", "Over 9.5", "Under 9.5",
                          "Over 10.5", "Under 10.5", "Over 11.5", "Under 11.5"],
            "description": "Total de cantos na partida",
            "min_odds": 1.20,
            "max_odds": 8.0
        }
    
    def _create_clean_sheet_market(self) -> Dict[str, Any]:
        """Cria mercado jogo limpo"""
        return {
            "name": "Jogo Limpo",
            "selections": ["Casa", "Visitante", "Nenhum"],
            "description": "Qual equipe não sofre gols",
            "min_odds": 1.50,
            "max_odds": 10.0
        }
    
    def get_available_markets(self) -> List[MarketType]:
        """Retorna lista de mercados disponíveis"""
        return list(self.markets.keys())
    
    def get_market_info(self, market_type: MarketType) -> Dict[str, Any]:
        """Retorna informações de um mercado específico"""
        return self.markets.get(market_type, {})
    
    def generate_predictions(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Gera predições para todos os mercados disponíveis"""
        predictions = []
        
        for market_type in self.get_available_markets():
            try:
                market_predictions = self._generate_market_predictions(market_type, match_data)
                predictions.extend(market_predictions)
            except Exception as e:
                logger.error(f"Erro ao gerar predições para {market_type}: {e}")
        
        return predictions
    
    def _generate_market_predictions(self, market_type: MarketType, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Gera predições para um mercado específico"""
        predictions = []
        
        if market_type == MarketType.MATCH_WINNER:
            predictions = self._predict_match_winner(match_data)
        elif market_type == MarketType.OVER_UNDER:
            predictions = self._predict_over_under(match_data)
        elif market_type == MarketType.BOTH_TEAMS_SCORE:
            predictions = self._predict_btts(match_data)
        elif market_type == MarketType.ASIAN_HANDICAP:
            predictions = self._predict_asian_handicap(match_data)
        elif market_type == MarketType.TOTAL_CARDS:
            predictions = self._predict_cards(match_data)
        elif market_type == MarketType.TOTAL_CORNERS:
            predictions = self._predict_corners(match_data)
        
        return predictions
    
    def _predict_match_winner(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz resultado da partida"""
        # Simulação de predições baseadas em dados históricos
        home_strength = match_data.get('home_strength', 0.5)
        away_strength = match_data.get('away_strength', 0.5)
        
        # Cálculo de probabilidades
        home_prob = home_strength / (home_strength + away_strength + 0.1)
        draw_prob = 0.25  # Probabilidade fixa de empate
        away_prob = 1 - home_prob - draw_prob
        
        predictions = [
            MarketPrediction(
                market_type=MarketType.MATCH_WINNER,
                selection="1",
                predicted_probability=home_prob,
                confidence=0.7,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning="Baseado na força das equipes"
            ),
            MarketPrediction(
                market_type=MarketType.MATCH_WINNER,
                selection="X",
                predicted_probability=draw_prob,
                confidence=0.6,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning="Probabilidade histórica de empate"
            ),
            MarketPrediction(
                market_type=MarketType.MATCH_WINNER,
                selection="2",
                predicted_probability=away_prob,
                confidence=0.7,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning="Baseado na força das equipes"
            )
        ]
        
        return predictions
    
    def _predict_over_under(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz over/under gols"""
        avg_goals = match_data.get('avg_goals', 2.5)
        
        # Probabilidades baseadas na distribuição de Poisson
        over_25_prob = self._poisson_probability(avg_goals, 2.5, "over")
        under_25_prob = 1 - over_25_prob
        
        predictions = [
            MarketPrediction(
                market_type=MarketType.OVER_UNDER,
                selection="Over 2.5",
                predicted_probability=over_25_prob,
                confidence=0.65,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Média de {avg_goals:.1f} gols por partida"
            ),
            MarketPrediction(
                market_type=MarketType.OVER_UNDER,
                selection="Under 2.5",
                predicted_probability=under_25_prob,
                confidence=0.65,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Média de {avg_goals:.1f} gols por partida"
            )
        ]
        
        return predictions
    
    def _predict_btts(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz ambas marcam"""
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        
        # Probabilidade de ambas marcarem
        btts_prob = (1 - np.exp(-home_goals_avg)) * (1 - np.exp(-away_goals_avg))
        
        predictions = [
            MarketPrediction(
                market_type=MarketType.BOTH_TEAMS_SCORE,
                selection="Sim",
                predicted_probability=btts_prob,
                confidence=0.6,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Probabilidade baseada em médias de gols"
            ),
            MarketPrediction(
                market_type=MarketType.BOTH_TEAMS_SCORE,
                selection="Não",
                predicted_probability=1 - btts_prob,
                confidence=0.6,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Probabilidade baseada em médias de gols"
            )
        ]
        
        return predictions
    
    def _predict_asian_handicap(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz handicap asiático"""
        home_strength = match_data.get('home_strength', 0.5)
        away_strength = match_data.get('away_strength', 0.5)
        
        # Handicap baseado na diferença de força
        handicap = (home_strength - away_strength) * 2
        
        predictions = []
        for h in [-1.5, -1, -0.5, 0.5, 1, 1.5]:
            if handicap > h:
                selection = f"Casa {h}"
                prob = 0.6
            else:
                selection = f"Visitante {h}"
                prob = 0.4
            
            predictions.append(MarketPrediction(
                market_type=MarketType.ASIAN_HANDICAP,
                selection=selection,
                predicted_probability=prob,
                confidence=0.5,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Handicap baseado na diferença de força: {handicap:.1f}"
            ))
        
        return predictions
    
    def _predict_cards(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz total de cartões"""
        avg_cards = match_data.get('avg_cards', 3.5)
        
        over_35_prob = self._poisson_probability(avg_cards, 3.5, "over")
        under_35_prob = 1 - over_35_prob
        
        predictions = [
            MarketPrediction(
                market_type=MarketType.TOTAL_CARDS,
                selection="Over 3.5",
                predicted_probability=over_35_prob,
                confidence=0.55,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Média de {avg_cards:.1f} cartões por partida"
            ),
            MarketPrediction(
                market_type=MarketType.TOTAL_CARDS,
                selection="Under 3.5",
                predicted_probability=under_35_prob,
                confidence=0.55,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Média de {avg_cards:.1f} cartões por partida"
            )
        ]
        
        return predictions
    
    def _predict_corners(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz total de cantos"""
        avg_corners = match_data.get('avg_corners', 10.5)
        
        over_105_prob = self._poisson_probability(avg_corners, 10.5, "over")
        under_105_prob = 1 - over_105_prob
        
        predictions = [
            MarketPrediction(
                market_type=MarketType.TOTAL_CORNERS,
                selection="Over 10.5",
                predicted_probability=over_105_prob,
                confidence=0.55,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Média de {avg_corners:.1f} cantos por partida"
            ),
            MarketPrediction(
                market_type=MarketType.TOTAL_CORNERS,
                selection="Under 10.5",
                predicted_probability=under_105_prob,
                confidence=0.55,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Média de {avg_corners:.1f} cantos por partida"
            )
        ]
        
        return predictions
    
    def _poisson_probability(self, lambda_param: float, threshold: float, direction: str) -> float:
        """Calcula probabilidade usando distribuição de Poisson"""
        if direction == "over":
            return 1 - sum(np.exp(-lambda_param) * (lambda_param ** k) / np.math.factorial(k) 
                          for k in range(int(threshold) + 1))
        else:  # under
            return sum(np.exp(-lambda_param) * (lambda_param ** k) / np.math.factorial(k) 
                      for k in range(int(threshold) + 1))
    
    def calculate_expected_value(self, prediction: MarketPrediction, odds: float) -> float:
        """Calcula valor esperado de uma aposta"""
        return (prediction.predicted_probability * odds) - 1
    
    def calculate_kelly_fraction(self, prediction: MarketPrediction, odds: float) -> float:
        """Calcula fração de Kelly para sizing da aposta"""
        if odds <= 1:
            return 0
        
        b = odds - 1  # Ganho líquido por unidade apostada
        p = prediction.predicted_probability
        q = 1 - p
        
        kelly = (b * p - q) / b
        return max(0, min(kelly, 0.25))  # Limitar entre 0 e 25%

if __name__ == "__main__":
    # Demo do sistema expandido de mercados
    print("🎯 SISTEMA EXPANDIDO DE MERCADOS DE APOSTAS")
    print("=" * 50)
    
    markets = ExpandedBettingMarkets()
    
    # Mostrar mercados disponíveis
    print(f"📊 Mercados disponíveis: {len(markets.get_available_markets())}")
    for market in markets.get_available_markets():
        info = markets.get_market_info(market)
        print(f"  • {info['name']}: {info['description']}")
    
    # Dados de exemplo para uma partida
    match_data = {
        'home_strength': 0.6,
        'away_strength': 0.4,
        'avg_goals': 2.8,
        'home_goals_avg': 1.6,
        'away_goals_avg': 1.2,
        'avg_cards': 4.2,
        'avg_corners': 11.3
    }
    
    # Gerar predições
    print(f"\n🔮 PREDIÇÕES PARA PARTIDA DE EXEMPLO")
    print("-" * 50)
    
    predictions = markets.generate_predictions(match_data)
    
    for pred in predictions[:10]:  # Mostrar apenas as primeiras 10
        print(f"📈 {pred.market_type.value}: {pred.selection}")
        print(f"   Probabilidade: {pred.predicted_probability:.1%}")
        print(f"   Confiança: {pred.confidence:.1%}")
        print(f"   Razão: {pred.reasoning}")
        print()
    
    print("✅ Sistema expandido de mercados implementado com sucesso!")
