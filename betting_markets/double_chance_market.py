#!/usr/bin/env python3
"""
Mercado de Dupla Chance - MaraBet AI
Implementa predições para dupla chance e mercados relacionados
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
from .expanded_markets import MarketType, MarketPrediction

logger = logging.getLogger(__name__)

class DoubleChanceMarket:
    """Mercado especializado em predições de dupla chance"""
    
    def __init__(self):
        self.double_chance_types = ["1X", "X2", "12"]
        self.triple_chance_types = ["1X2", "1X", "X2", "12"]
    
    def predict_double_chance(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz dupla chance (1X, X2, 12)"""
        predictions = []
        
        # Dados da partida
        home_strength = match_data.get('home_strength', 0.5)
        away_strength = match_data.get('away_strength', 0.5)
        home_advantage = match_data.get('home_advantage', 0.1)
        
        # Calcular probabilidades básicas
        home_prob = self._calculate_home_probability(home_strength, away_strength, home_advantage)
        draw_prob = self._calculate_draw_probability(home_strength, away_strength)
        away_prob = 1 - home_prob - draw_prob
        
        # Fatores de ajuste
        form_factor = match_data.get('form_factor', 1.0)
        injury_factor = match_data.get('injury_factor', 1.0)
        weather_factor = match_data.get('weather_factor', 1.0)
        
        # Ajustar probabilidades
        home_prob *= form_factor * injury_factor * weather_factor
        away_prob *= form_factor * injury_factor * weather_factor
        draw_prob *= weather_factor  # Empate menos afetado por fatores externos
        
        # Normalizar probabilidades
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        # Calcular dupla chance
        double_chance_probs = {
            "1X": home_prob + draw_prob,
            "X2": draw_prob + away_prob,
            "12": home_prob + away_prob
        }
        
        # Confiança baseada na clareza das probabilidades
        confidence = self._calculate_double_chance_confidence(home_prob, draw_prob, away_prob)
        
        for dc_type, prob in double_chance_probs.items():
            predictions.append(MarketPrediction(
                market_type=MarketType.DOUBLE_CHANCE,
                selection=dc_type,
                predicted_probability=prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Baseado em: Casa {home_prob:.1%}, Empate {draw_prob:.1%}, Visitante {away_prob:.1%}"
            ))
        
        return predictions
    
    def predict_triple_chance(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz tripla chance (1X2, 1X, X2, 12)"""
        predictions = []
        
        # Dados da partida
        home_strength = match_data.get('home_strength', 0.5)
        away_strength = match_data.get('away_strength', 0.5)
        home_advantage = match_data.get('home_advantage', 0.1)
        
        # Calcular probabilidades básicas
        home_prob = self._calculate_home_probability(home_strength, away_strength, home_advantage)
        draw_prob = self._calculate_draw_probability(home_strength, away_strength)
        away_prob = 1 - home_prob - draw_prob
        
        # Fatores de ajuste
        form_factor = match_data.get('form_factor', 1.0)
        injury_factor = match_data.get('injury_factor', 1.0)
        weather_factor = match_data.get('weather_factor', 1.0)
        
        # Ajustar probabilidades
        home_prob *= form_factor * injury_factor * weather_factor
        away_prob *= form_factor * injury_factor * weather_factor
        draw_prob *= weather_factor
        
        # Normalizar probabilidades
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        # Calcular tripla chance
        triple_chance_probs = {
            "1X2": 1.0,  # Sempre 100% (qualquer resultado)
            "1X": home_prob + draw_prob,
            "X2": draw_prob + away_prob,
            "12": home_prob + away_prob
        }
        
        # Confiança
        confidence = self._calculate_double_chance_confidence(home_prob, draw_prob, away_prob)
        
        for tc_type, prob in triple_chance_probs.items():
            predictions.append(MarketPrediction(
                market_type=MarketType.DOUBLE_CHANCE,
                selection=tc_type,
                predicted_probability=prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Baseado em: Casa {home_prob:.1%}, Empate {draw_prob:.1%}, Visitante {away_prob:.1%}"
            ))
        
        return predictions
    
    def predict_win_draw_win(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz Win-Draw-Win (1X2) com probabilidades individuais"""
        predictions = []
        
        # Dados da partida
        home_strength = match_data.get('home_strength', 0.5)
        away_strength = match_data.get('away_strength', 0.5)
        home_advantage = match_data.get('home_advantage', 0.1)
        
        # Calcular probabilidades básicas
        home_prob = self._calculate_home_probability(home_strength, away_strength, home_advantage)
        draw_prob = self._calculate_draw_probability(home_strength, away_strength)
        away_prob = 1 - home_prob - draw_prob
        
        # Fatores de ajuste
        form_factor = match_data.get('form_factor', 1.0)
        injury_factor = match_data.get('injury_factor', 1.0)
        weather_factor = match_data.get('weather_factor', 1.0)
        
        # Ajustar probabilidades
        home_prob *= form_factor * injury_factor * weather_factor
        away_prob *= form_factor * injury_factor * weather_factor
        draw_prob *= weather_factor
        
        # Normalizar probabilidades
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        # Confiança
        confidence = self._calculate_double_chance_confidence(home_prob, draw_prob, away_prob)
        
        # Predições individuais
        for selection, prob in [("1", home_prob), ("X", draw_prob), ("2", away_prob)]:
            predictions.append(MarketPrediction(
                market_type=MarketType.MATCH_WINNER,
                selection=selection,
                predicted_probability=prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Força casa: {home_strength:.2f}, visitante: {away_strength:.2f}, vantagem casa: {home_advantage:.2f}"
            ))
        
        return predictions
    
    def predict_alternative_double_chance(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz dupla chance alternativa com handicaps"""
        predictions = []
        
        # Dados da partida
        home_strength = match_data.get('home_strength', 0.5)
        away_strength = match_data.get('away_strength', 0.5)
        home_advantage = match_data.get('home_advantage', 0.1)
        
        # Handicaps alternativos
        handicaps = [-1, 0, 1]
        
        for handicap in handicaps:
            # Ajustar força com handicap
            adj_home_strength = home_strength + (handicap * 0.1)
            adj_away_strength = away_strength - (handicap * 0.1)
            
            # Calcular probabilidades com handicap
            home_prob = self._calculate_home_probability(adj_home_strength, adj_away_strength, home_advantage)
            draw_prob = self._calculate_draw_probability(adj_home_strength, adj_away_strength)
            away_prob = 1 - home_prob - draw_prob
            
            # Normalizar
            total = home_prob + draw_prob + away_prob
            home_prob /= total
            draw_prob /= total
            away_prob /= total
            
            # Dupla chance com handicap
            double_chance_probs = {
                f"1X {handicap:+d}": home_prob + draw_prob,
                f"X2 {handicap:+d}": draw_prob + away_prob,
                f"12 {handicap:+d}": home_prob + away_prob
            }
            
            confidence = self._calculate_double_chance_confidence(home_prob, draw_prob, away_prob)
            
            for dc_type, prob in double_chance_probs.items():
                predictions.append(MarketPrediction(
                    market_type=MarketType.DOUBLE_CHANCE,
                    selection=dc_type,
                    predicted_probability=prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Handicap {handicap:+d}: Casa {home_prob:.1%}, Empate {draw_prob:.1%}, Visitante {away_prob:.1%}"
                ))
        
        return predictions
    
    def _calculate_home_probability(self, home_strength: float, away_strength: float, 
                                   home_advantage: float) -> float:
        """Calcula probabilidade de vitória da casa"""
        # Fórmula baseada na diferença de força + vantagem de casa
        strength_diff = home_strength - away_strength + home_advantage
        
        # Usar função sigmóide para converter diferença em probabilidade
        prob = 1 / (1 + np.exp(-strength_diff * 3))
        
        # Garantir que esteja entre 0.05 e 0.95
        return max(0.05, min(0.95, prob))
    
    def _calculate_draw_probability(self, home_strength: float, away_strength: float) -> float:
        """Calcula probabilidade de empate"""
        # Empate mais provável quando as forças são similares
        strength_diff = abs(home_strength - away_strength)
        
        # Probabilidade base inversamente proporcional à diferença
        base_prob = 0.25  # Probabilidade base de empate
        diff_factor = max(0, 1 - strength_diff * 2)  # Reduz com diferença
        
        prob = base_prob * diff_factor
        
        # Garantir que esteja entre 0.05 e 0.4
        return max(0.05, min(0.4, prob))
    
    def _calculate_double_chance_confidence(self, home_prob: float, draw_prob: float, 
                                          away_prob: float) -> float:
        """Calcula confiança para dupla chance"""
        # Confiança baseada na clareza das probabilidades
        probs = [home_prob, draw_prob, away_prob]
        max_prob = max(probs)
        min_prob = min(probs)
        
        # Maior diferença = maior confiança
        diff = max_prob - min_prob
        
        if diff >= 0.4:
            return 0.8  # Alta confiança
        elif diff >= 0.2:
            return 0.6  # Média confiança
        else:
            return 0.4  # Baixa confiança
    
    def get_double_chance_statistics(self, match_data: Dict[str, Any]) -> Dict[str, float]:
        """Retorna estatísticas de dupla chance para a partida"""
        home_strength = match_data.get('home_strength', 0.5)
        away_strength = match_data.get('away_strength', 0.5)
        home_advantage = match_data.get('home_advantage', 0.1)
        
        # Calcular probabilidades básicas
        home_prob = self._calculate_home_probability(home_strength, away_strength, home_advantage)
        draw_prob = self._calculate_draw_probability(home_strength, away_strength)
        away_prob = 1 - home_prob - draw_prob
        
        # Normalizar
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        return {
            'home_probability': home_prob,
            'draw_probability': draw_prob,
            'away_probability': away_prob,
            'double_chance_1x': home_prob + draw_prob,
            'double_chance_x2': draw_prob + away_prob,
            'double_chance_12': home_prob + away_prob,
            'confidence_level': self._calculate_double_chance_confidence(home_prob, draw_prob, away_prob),
            'strength_difference': home_strength - away_strength,
            'home_advantage': home_advantage
        }

if __name__ == "__main__":
    # Demo do mercado de dupla chance
    print("🎯 MERCADO DE DUPLA CHANCE - MARABET AI")
    print("=" * 45)
    
    double_chance_market = DoubleChanceMarket()
    
    # Dados de exemplo
    match_data = {
        'home_strength': 0.6,
        'away_strength': 0.4,
        'home_advantage': 0.15,
        'form_factor': 1.1,
        'injury_factor': 0.95,
        'weather_factor': 1.0
    }
    
    # Estatísticas
    stats = double_chance_market.get_double_chance_statistics(match_data)
    print("📊 ESTATÍSTICAS DE DUPLA CHANCE:")
    for key, value in stats.items():
        print(f"  {key}: {value:.3f}")
    
    print(f"\n🎯 PREDIÇÕES DUPLA CHANCE:")
    double_predictions = double_chance_market.predict_double_chance(match_data)
    for pred in double_predictions:
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n🏆 PREDIÇÕES WIN-DRAW-WIN:")
    wdw_predictions = double_chance_market.predict_win_draw_win(match_data)
    for pred in wdw_predictions:
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n⚖️ PREDIÇÕES DUPLA CHANCE ALTERNATIVA:")
    alt_predictions = double_chance_market.predict_alternative_double_chance(match_data)
    for pred in alt_predictions[:6]:  # Primeiras 6
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print("\n✅ Mercado de dupla chance implementado com sucesso!")
