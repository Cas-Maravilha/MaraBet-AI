#!/usr/bin/env python3
"""
Mercado de Cantos - MaraBet AI
Implementa predições para mercados relacionados a cantos
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
from scipy.stats import poisson
from .expanded_markets import MarketType, MarketPrediction

logger = logging.getLogger(__name__)

class CornersMarket:
    """Mercado especializado em predições de cantos"""
    
    def __init__(self):
        self.corner_thresholds = [8.5, 9.5, 10.5, 11.5, 12.5, 13.5]
        self.corner_handicaps = [-2, -1, 0, 1, 2]
    
    def predict_total_corners(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz total de cantos na partida"""
        predictions = []
        
        # Dados da partida
        home_corners_avg = match_data.get('home_corners_avg', 5.5)
        away_corners_avg = match_data.get('away_corners_avg', 5.0)
        total_corners_avg = home_corners_avg + away_corners_avg
        
        # Fatores de ajuste
        possession_factor = match_data.get('possession_factor', 1.0)
        style_factor = match_data.get('style_factor', 1.0)
        weather_factor = match_data.get('weather_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        
        # Ajustar média de cantos
        adjusted_corners = total_corners_avg * possession_factor * style_factor * weather_factor * importance_factor
        
        for threshold in self.corner_thresholds:
            # Probabilidade over
            over_prob = self._calculate_over_probability(adjusted_corners, threshold)
            under_prob = 1 - over_prob
            
            # Confiança baseada na proximidade da média
            confidence = self._calculate_corners_confidence(adjusted_corners, threshold)
            
            predictions.extend([
                MarketPrediction(
                    market_type=MarketType.TOTAL_CORNERS,
                    selection=f"Over {threshold}",
                    predicted_probability=over_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Média ajustada: {adjusted_corners:.1f} cantos"
                ),
                MarketPrediction(
                    market_type=MarketType.TOTAL_CORNERS,
                    selection=f"Under {threshold}",
                    predicted_probability=under_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Média ajustada: {adjusted_corners:.1f} cantos"
                )
            ])
        
        return predictions
    
    def predict_corner_handicap(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz handicap de cantos"""
        predictions = []
        
        # Dados da partida
        home_corners_avg = match_data.get('home_corners_avg', 5.5)
        away_corners_avg = match_data.get('away_corners_avg', 5.0)
        
        # Diferença de cantos
        corners_diff = home_corners_avg - away_corners_avg
        
        # Fatores de ajuste
        possession_factor = match_data.get('possession_factor', 1.0)
        style_factor = match_data.get('style_factor', 1.0)
        
        adjusted_diff = corners_diff * possession_factor * style_factor
        
        for handicap in self.corner_handicaps:
            # Calcular probabilidades
            home_prob, away_prob = self._calculate_corner_handicap_probabilities(
                adjusted_diff, handicap
            )
            
            confidence = self._calculate_corner_handicap_confidence(adjusted_diff, handicap)
            
            predictions.extend([
                MarketPrediction(
                    market_type=MarketType.CORNER_HANDICAP,
                    selection=f"Casa {handicap}",
                    predicted_probability=home_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Diferença ajustada: {adjusted_diff:.1f} cantos"
                ),
                MarketPrediction(
                    market_type=MarketType.CORNER_HANDICAP,
                    selection=f"Visitante {handicap}",
                    predicted_probability=away_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Diferença ajustada: {adjusted_diff:.1f} cantos"
                )
            ])
        
        return predictions
    
    def predict_first_corner(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz qual equipe faz o primeiro canto"""
        predictions = []
        
        # Dados da partida
        home_corners_avg = match_data.get('home_corners_avg', 5.5)
        away_corners_avg = match_data.get('away_corners_avg', 5.0)
        
        # Fatores de ajuste
        possession_factor = match_data.get('possession_factor', 1.0)
        style_factor = match_data.get('style_factor', 1.0)
        
        adj_home_corners = home_corners_avg * possession_factor * style_factor
        adj_away_corners = away_corners_avg * possession_factor * style_factor
        
        # Probabilidade de fazer primeiro canto
        total_corners = adj_home_corners + adj_away_corners
        home_first_prob = adj_home_corners / total_corners if total_corners > 0 else 0.5
        away_first_prob = 1 - home_first_prob
        
        # Confiança baseada na diferença
        confidence = min(abs(home_first_prob - away_first_prob) * 2, 0.8)
        
        predictions.extend([
            MarketPrediction(
                market_type=MarketType.FIRST_CORNER,
                selection="Casa",
                predicted_probability=home_first_prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Casa: {adj_home_corners:.1f}, Visitante: {adj_away_corners:.1f} cantos"
            ),
            MarketPrediction(
                market_type=MarketType.FIRST_CORNER,
                selection="Visitante",
                predicted_probability=away_first_prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Casa: {adj_home_corners:.1f}, Visitante: {adj_away_corners:.1f} cantos"
            )
        ])
        
        return predictions
    
    def predict_corner_timing(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz timing dos cantos (primeiro tempo, segundo tempo)"""
        predictions = []
        
        # Dados da partida
        total_corners_avg = match_data.get('total_corners_avg', 10.5)
        
        # Fatores de ajuste
        possession_factor = match_data.get('possession_factor', 1.0)
        style_factor = match_data.get('style_factor', 1.0)
        
        adjusted_corners = total_corners_avg * possession_factor * style_factor
        
        # Distribuição temporal (55% no segundo tempo)
        first_half_corners = adjusted_corners * 0.45
        second_half_corners = adjusted_corners * 0.55
        
        # Mercados de timing
        timing_markets = [
            ("1º Tempo Over 4.5", first_half_corners, 4.5),
            ("1º Tempo Under 4.5", first_half_corners, 4.5),
            ("2º Tempo Over 5.5", second_half_corners, 5.5),
            ("2º Tempo Under 5.5", second_half_corners, 5.5)
        ]
        
        for selection, avg_corners, threshold in timing_markets:
            if "Over" in selection:
                prob = self._calculate_over_probability(avg_corners, threshold)
            else:
                prob = 1 - self._calculate_over_probability(avg_corners, threshold)
            
            confidence = self._calculate_corners_confidence(avg_corners, threshold)
            
            predictions.append(MarketPrediction(
                market_type=MarketType.TOTAL_CORNERS,
                selection=selection,
                predicted_probability=prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Média {selection.split()[0]}: {avg_corners:.1f} cantos"
            ))
        
        return predictions
    
    def predict_corner_race(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz corrida de cantos (primeiro a X cantos)"""
        predictions = []
        
        # Dados da partida
        home_corners_avg = match_data.get('home_corners_avg', 5.5)
        away_corners_avg = match_data.get('away_corners_avg', 5.0)
        
        # Fatores de ajuste
        possession_factor = match_data.get('possession_factor', 1.0)
        style_factor = match_data.get('style_factor', 1.0)
        
        adj_home_corners = home_corners_avg * possession_factor * style_factor
        adj_away_corners = away_corners_avg * possession_factor * style_factor
        
        # Corridas de cantos
        corner_races = [3, 5, 7, 9]
        
        for race in corner_races:
            # Probabilidade de cada equipe chegar primeiro ao número de cantos
            home_prob = self._calculate_corner_race_probability(adj_home_corners, adj_away_corners, race)
            away_prob = 1 - home_prob
            
            confidence = self._calculate_corner_race_confidence(adj_home_corners, adj_away_corners, race)
            
            predictions.extend([
                MarketPrediction(
                    market_type=MarketType.TOTAL_CORNERS,
                    selection=f"Casa primeiro a {race}",
                    predicted_probability=home_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Casa: {adj_home_corners:.1f}, Visitante: {adj_away_corners:.1f} cantos"
                ),
                MarketPrediction(
                    market_type=MarketType.TOTAL_CORNERS,
                    selection=f"Visitante primeiro a {race}",
                    predicted_probability=away_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Casa: {adj_home_corners:.1f}, Visitante: {adj_away_corners:.1f} cantos"
                )
            ])
        
        return predictions
    
    def _calculate_over_probability(self, lambda_param: float, threshold: float) -> float:
        """Calcula probabilidade over usando Poisson"""
        return 1 - poisson.cdf(int(threshold), lambda_param)
    
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
    
    def _calculate_corner_handicap_confidence(self, corners_diff: float, handicap: float) -> float:
        """Calcula confiança para handicap de cantos"""
        distance = abs(corners_diff - handicap)
        
        if distance <= 1.0:
            return 0.7
        elif distance <= 2.0:
            return 0.5
        else:
            return 0.3
    
    def _calculate_corners_confidence(self, lambda_param: float, threshold: float) -> float:
        """Calcula confiança para cantos"""
        distance = abs(lambda_param - threshold)
        
        if distance <= 1.0:
            return 0.8
        elif distance <= 2.0:
            return 0.6
        elif distance <= 3.0:
            return 0.4
        else:
            return 0.2
    
    def _calculate_corner_race_probability(self, home_corners: float, away_corners: float, 
                                         race: int) -> float:
        """Calcula probabilidade de corrida de cantos"""
        # Simplificação: baseado na proporção de cantos
        total_corners = home_corners + away_corners
        if total_corners == 0:
            return 0.5
        
        home_ratio = home_corners / total_corners
        return home_ratio
    
    def _calculate_corner_race_confidence(self, home_corners: float, away_corners: float, 
                                        race: int) -> float:
        """Calcula confiança para corrida de cantos"""
        total_corners = home_corners + away_corners
        if total_corners == 0:
            return 0.3
        
        # Confiança baseada na diferença relativa
        diff_ratio = abs(home_corners - away_corners) / total_corners
        return min(diff_ratio * 2, 0.8)
    
    def get_corners_statistics(self, match_data: Dict[str, Any]) -> Dict[str, float]:
        """Retorna estatísticas de cantos para a partida"""
        home_corners_avg = match_data.get('home_corners_avg', 5.5)
        away_corners_avg = match_data.get('away_corners_avg', 5.0)
        total_corners_avg = home_corners_avg + away_corners_avg
        
        return {
            'total_corners_avg': total_corners_avg,
            'home_corners_avg': home_corners_avg,
            'away_corners_avg': away_corners_avg,
            'corners_difference': home_corners_avg - away_corners_avg,
            'over_105_corners_prob': self._calculate_over_probability(total_corners_avg, 10.5),
            'over_115_corners_prob': self._calculate_over_probability(total_corners_avg, 11.5),
            'first_corner_home_prob': home_corners_avg / total_corners_avg if total_corners_avg > 0 else 0.5
        }

if __name__ == "__main__":
    # Demo do mercado de cantos
    print("📐 MERCADO DE CANTOS - MARABET AI")
    print("=" * 40)
    
    corners_market = CornersMarket()
    
    # Dados de exemplo
    match_data = {
        'home_corners_avg': 6.2,
        'away_corners_avg': 4.8,
        'total_corners_avg': 11.0,
        'possession_factor': 1.1,  # Casa com mais posse
        'style_factor': 1.2,  # Estilo ofensivo
        'weather_factor': 1.0,
        'importance_factor': 1.0
    }
    
    # Estatísticas
    stats = corners_market.get_corners_statistics(match_data)
    print("📊 ESTATÍSTICAS DE CANTOS:")
    for key, value in stats.items():
        print(f"  {key}: {value:.3f}")
    
    print(f"\n📐 PREDIÇÕES TOTAL CANTOS:")
    total_predictions = corners_market.predict_total_corners(match_data)
    for pred in total_predictions[:6]:  # Primeiras 6
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n⚖️ PREDIÇÕES HANDICAP CANTOS:")
    handicap_predictions = corners_market.predict_corner_handicap(match_data)
    for pred in handicap_predictions[:6]:  # Primeiras 6
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n🏁 PREDIÇÕES PRIMEIRO CANTO:")
    first_predictions = corners_market.predict_first_corner(match_data)
    for pred in first_predictions:
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n🏃 PREDIÇÕES CORRIDA CANTOS:")
    race_predictions = corners_market.predict_corner_race(match_data)
    for pred in race_predictions[:4]:  # Primeiras 4
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print("\n✅ Mercado de cantos implementado com sucesso!")
