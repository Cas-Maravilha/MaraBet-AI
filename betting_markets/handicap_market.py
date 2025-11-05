#!/usr/bin/env python3
"""
Mercado de Handicap - MaraBet AI
Implementa predições para handicap asiático e europeu
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
from .expanded_markets import MarketType, MarketPrediction

logger = logging.getLogger(__name__)

class HandicapMarket:
    """Mercado especializado em predições de handicap"""
    
    def __init__(self):
        self.asian_handicaps = [-2.5, -2, -1.5, -1, -0.5, 0.5, 1, 1.5, 2, 2.5]
        self.european_handicaps = [-3, -2, -1, 0, 1, 2, 3]
    
    def predict_asian_handicap(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz handicap asiático"""
        predictions = []
        
        # Dados da partida
        home_strength = match_data.get('home_strength', 0.5)
        away_strength = match_data.get('away_strength', 0.5)
        home_advantage = match_data.get('home_advantage', 0.1)
        
        # Calcular diferença de força
        strength_diff = home_strength - away_strength + home_advantage
        
        # Fatores de ajuste
        form_factor = match_data.get('form_factor', 1.0)
        injury_factor = match_data.get('injury_factor', 1.0)
        weather_factor = match_data.get('weather_factor', 1.0)
        
        # Ajustar diferença de força
        adjusted_diff = strength_diff * form_factor * injury_factor * weather_factor
        
        for handicap in self.asian_handicaps:
            # Calcular probabilidades
            home_prob, away_prob = self._calculate_handicap_probabilities(
                adjusted_diff, handicap, is_asian=True
            )
            
            # Confiança baseada na clareza da diferença
            confidence = self._calculate_handicap_confidence(adjusted_diff, handicap)
            
            predictions.extend([
                MarketPrediction(
                    market_type=MarketType.ASIAN_HANDICAP,
                    selection=f"Casa {handicap}",
                    predicted_probability=home_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Diferença de força ajustada: {adjusted_diff:.2f}"
                ),
                MarketPrediction(
                    market_type=MarketType.ASIAN_HANDICAP,
                    selection=f"Visitante {handicap}",
                    predicted_probability=away_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Diferença de força ajustada: {adjusted_diff:.2f}"
                )
            ])
        
        return predictions
    
    def predict_european_handicap(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz handicap europeu"""
        predictions = []
        
        # Dados da partida
        home_strength = match_data.get('home_strength', 0.5)
        away_strength = match_data.get('away_strength', 0.5)
        home_advantage = match_data.get('home_advantage', 0.1)
        
        # Calcular diferença de força
        strength_diff = home_strength - away_strength + home_advantage
        
        # Fatores de ajuste
        form_factor = match_data.get('form_factor', 1.0)
        injury_factor = match_data.get('injury_factor', 1.0)
        weather_factor = match_data.get('weather_factor', 1.0)
        
        # Ajustar diferença de força
        adjusted_diff = strength_diff * form_factor * injury_factor * weather_factor
        
        for handicap in self.european_handicaps:
            # Calcular probabilidades
            home_prob, away_prob = self._calculate_handicap_probabilities(
                adjusted_diff, handicap, is_asian=False
            )
            
            # Confiança baseada na clareza da diferença
            confidence = self._calculate_handicap_confidence(adjusted_diff, handicap)
            
            predictions.extend([
                MarketPrediction(
                    market_type=MarketType.EUROPEAN_HANDICAP,
                    selection=f"Casa {handicap}",
                    predicted_probability=home_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Diferença de força ajustada: {adjusted_diff:.2f}"
                ),
                MarketPrediction(
                    market_type=MarketType.EUROPEAN_HANDICAP,
                    selection=f"Visitante {handicap}",
                    predicted_probability=away_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Diferença de força ajustada: {adjusted_diff:.2f}"
                )
            ])
        
        return predictions
    
    def _calculate_handicap_probabilities(self, strength_diff: float, handicap: float, 
                                        is_asian: bool = True) -> Tuple[float, float]:
        """Calcula probabilidades para handicap"""
        # Ajustar handicap baseado na diferença de força
        effective_handicap = handicap - strength_diff
        
        if is_asian:
            # Handicap asiático com meio gols
            if effective_handicap > 0:
                home_prob = 0.5 + min(effective_handicap * 0.3, 0.4)
            else:
                home_prob = 0.5 + max(effective_handicap * 0.3, -0.4)
        else:
            # Handicap europeu com gols inteiros
            if effective_handicap > 0:
                home_prob = 0.5 + min(effective_handicap * 0.25, 0.45)
            else:
                home_prob = 0.5 + max(effective_handicap * 0.25, -0.45)
        
        # Garantir que as probabilidades estejam entre 0.05 e 0.95
        home_prob = max(0.05, min(0.95, home_prob))
        away_prob = 1 - home_prob
        
        return home_prob, away_prob
    
    def _calculate_handicap_confidence(self, strength_diff: float, handicap: float) -> float:
        """Calcula confiança para handicap"""
        # Confiança baseada na proximidade entre diferença de força e handicap
        distance = abs(strength_diff - handicap)
        
        if distance <= 0.5:
            return 0.8  # Alta confiança
        elif distance <= 1.0:
            return 0.6  # Média confiança
        elif distance <= 1.5:
            return 0.4  # Baixa confiança
        else:
            return 0.2  # Muito baixa confiança
    
    def predict_corner_handicap(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz handicap de cantos"""
        predictions = []
        
        # Dados de cantos
        home_corners_avg = match_data.get('home_corners_avg', 5.5)
        away_corners_avg = match_data.get('away_corners_avg', 5.0)
        
        # Diferença de cantos
        corners_diff = home_corners_avg - away_corners_avg
        
        # Fatores de ajuste
        possession_factor = match_data.get('possession_factor', 1.0)
        style_factor = match_data.get('style_factor', 1.0)
        
        adjusted_diff = corners_diff * possession_factor * style_factor
        
        # Handicaps de cantos
        corner_handicaps = [-2, -1, 0, 1, 2]
        
        for handicap in corner_handicaps:
            # Calcular probabilidades
            home_prob, away_prob = self._calculate_corner_handicap_probabilities(
                adjusted_diff, handicap
            )
            
            confidence = self._calculate_corner_confidence(adjusted_diff, handicap)
            
            predictions.extend([
                MarketPrediction(
                    market_type=MarketType.CORNER_HANDICAP,
                    selection=f"Casa {handicap}",
                    predicted_probability=home_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Diferença de cantos ajustada: {adjusted_diff:.1f}"
                ),
                MarketPrediction(
                    market_type=MarketType.CORNER_HANDICAP,
                    selection=f"Visitante {handicap}",
                    predicted_probability=away_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Diferença de cantos ajustada: {adjusted_diff:.1f}"
                )
            ])
        
        return predictions
    
    def _calculate_corner_handicap_probabilities(self, corners_diff: float, 
                                               handicap: float) -> Tuple[float, float]:
        """Calcula probabilidades para handicap de cantos"""
        effective_handicap = handicap - corners_diff
        
        if effective_handicap > 0:
            home_prob = 0.5 + min(effective_handicap * 0.2, 0.4)
        else:
            home_prob = 0.5 + max(effective_handicap * 0.2, -0.4)
        
        home_prob = max(0.05, min(0.95, home_prob))
        away_prob = 1 - home_prob
        
        return home_prob, away_prob
    
    def _calculate_corner_confidence(self, corners_diff: float, handicap: float) -> float:
        """Calcula confiança para handicap de cantos"""
        distance = abs(corners_diff - handicap)
        
        if distance <= 1.0:
            return 0.7
        elif distance <= 2.0:
            return 0.5
        else:
            return 0.3
    
    def get_handicap_statistics(self, match_data: Dict[str, Any]) -> Dict[str, float]:
        """Retorna estatísticas de handicap para a partida"""
        home_strength = match_data.get('home_strength', 0.5)
        away_strength = match_data.get('away_strength', 0.5)
        home_advantage = match_data.get('home_advantage', 0.1)
        
        strength_diff = home_strength - away_strength + home_advantage
        
        return {
            'strength_difference': strength_diff,
            'recommended_asian_handicap': round(strength_diff * 2) / 2,  # Arredondar para 0.5
            'recommended_european_handicap': round(strength_diff),
            'home_advantage': home_advantage,
            'confidence_level': self._calculate_handicap_confidence(strength_diff, 0)
        }

if __name__ == "__main__":
    # Demo do mercado de handicap
    print("⚖️ MERCADO DE HANDICAP - MARABET AI")
    print("=" * 40)
    
    handicap_market = HandicapMarket()
    
    # Dados de exemplo
    match_data = {
        'home_strength': 0.65,
        'away_strength': 0.45,
        'home_advantage': 0.12,
        'form_factor': 1.1,
        'injury_factor': 0.95,
        'weather_factor': 1.0,
        'home_corners_avg': 6.2,
        'away_corners_avg': 4.8,
        'possession_factor': 1.05,
        'style_factor': 1.0
    }
    
    # Estatísticas
    stats = handicap_market.get_handicap_statistics(match_data)
    print("📊 ESTATÍSTICAS DE HANDICAP:")
    for key, value in stats.items():
        print(f"  {key}: {value:.3f}")
    
    print(f"\n🎯 PREDIÇÕES HANDICAP ASIÁTICO:")
    asian_predictions = handicap_market.predict_asian_handicap(match_data)
    for pred in asian_predictions[:8]:  # Primeiras 8
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n🏛️ PREDIÇÕES HANDICAP EUROPEU:")
    european_predictions = handicap_market.predict_european_handicap(match_data)
    for pred in european_predictions[:6]:  # Primeiras 6
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n📐 PREDIÇÕES HANDICAP CANTOS:")
    corner_predictions = handicap_market.predict_corner_handicap(match_data)
    for pred in corner_predictions:
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print("\n✅ Mercado de handicap implementado com sucesso!")
