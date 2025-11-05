#!/usr/bin/env python3
"""
Mercado de Cartões - MaraBet AI
Implementa predições para mercados relacionados a cartões
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
from scipy.stats import poisson
from .expanded_markets import MarketType, MarketPrediction

logger = logging.getLogger(__name__)

class CardsMarket:
    """Mercado especializado em predições de cartões"""
    
    def __init__(self):
        self.card_thresholds = [1.5, 2.5, 3.5, 4.5, 5.5, 6.5]
        self.card_types = ['yellow', 'red', 'total']
    
    def predict_total_cards(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz total de cartões na partida"""
        predictions = []
        
        # Dados da partida
        home_cards_avg = match_data.get('home_cards_avg', 2.1)
        away_cards_avg = match_data.get('away_cards_avg', 2.0)
        total_cards_avg = home_cards_avg + away_cards_avg
        
        # Fatores de ajuste
        referee_factor = match_data.get('referee_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        rivalry_factor = match_data.get('rivalry_factor', 1.0)
        weather_factor = match_data.get('weather_factor', 1.0)
        
        # Ajustar média de cartões
        adjusted_cards = total_cards_avg * referee_factor * importance_factor * rivalry_factor * weather_factor
        
        for threshold in self.card_thresholds:
            # Probabilidade over
            over_prob = self._calculate_over_probability(adjusted_cards, threshold)
            under_prob = 1 - over_prob
            
            # Confiança baseada na proximidade da média
            confidence = self._calculate_cards_confidence(adjusted_cards, threshold)
            
            predictions.extend([
                MarketPrediction(
                    market_type=MarketType.TOTAL_CARDS,
                    selection=f"Over {threshold}",
                    predicted_probability=over_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Média ajustada: {adjusted_cards:.1f} cartões"
                ),
                MarketPrediction(
                    market_type=MarketType.TOTAL_CARDS,
                    selection=f"Under {threshold}",
                    predicted_probability=under_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Média ajustada: {adjusted_cards:.1f} cartões"
                )
            ])
        
        return predictions
    
    def predict_yellow_cards(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz cartões amarelos"""
        predictions = []
        
        # Dados da partida
        home_yellow_avg = match_data.get('home_yellow_avg', 1.8)
        away_yellow_avg = match_data.get('away_yellow_avg', 1.7)
        total_yellow_avg = home_yellow_avg + away_yellow_avg
        
        # Fatores de ajuste
        referee_factor = match_data.get('referee_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        rivalry_factor = match_data.get('rivalry_factor', 1.0)
        
        adjusted_yellow = total_yellow_avg * referee_factor * importance_factor * rivalry_factor
        
        for threshold in [1.5, 2.5, 3.5, 4.5]:
            over_prob = self._calculate_over_probability(adjusted_yellow, threshold)
            under_prob = 1 - over_prob
            
            confidence = self._calculate_cards_confidence(adjusted_yellow, threshold)
            
            predictions.extend([
                MarketPrediction(
                    market_type=MarketType.YELLOW_CARDS,
                    selection=f"Over {threshold}",
                    predicted_probability=over_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Média ajustada amarelos: {adjusted_yellow:.1f}"
                ),
                MarketPrediction(
                    market_type=MarketType.YELLOW_CARDS,
                    selection=f"Under {threshold}",
                    predicted_probability=under_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Média ajustada amarelos: {adjusted_yellow:.1f}"
                )
            ])
        
        return predictions
    
    def predict_red_cards(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz cartões vermelhos"""
        predictions = []
        
        # Dados da partida
        home_red_avg = match_data.get('home_red_avg', 0.1)
        away_red_avg = match_data.get('away_red_avg', 0.1)
        total_red_avg = home_red_avg + away_red_avg
        
        # Fatores de ajuste
        referee_factor = match_data.get('referee_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        rivalry_factor = match_data.get('rivalry_factor', 1.0)
        
        adjusted_red = total_red_avg * referee_factor * importance_factor * rivalry_factor
        
        # Mercados de cartões vermelhos
        red_markets = [
            ("0", 0),
            ("1+", 1),
            ("2+", 2)
        ]
        
        for selection, threshold in red_markets:
            if threshold == 0:
                prob = poisson.cdf(0, adjusted_red)
            else:
                prob = 1 - poisson.cdf(threshold - 1, adjusted_red)
            
            confidence = self._calculate_red_cards_confidence(adjusted_red, threshold)
            
            predictions.append(MarketPrediction(
                market_type=MarketType.RED_CARDS,
                selection=selection,
                predicted_probability=prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Média ajustada vermelhos: {adjusted_red:.2f}"
            ))
        
        return predictions
    
    def predict_first_card(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz qual equipe recebe o primeiro cartão"""
        predictions = []
        
        # Dados da partida
        home_cards_avg = match_data.get('home_cards_avg', 2.1)
        away_cards_avg = match_data.get('away_cards_avg', 2.0)
        
        # Fatores de ajuste
        referee_factor = match_data.get('referee_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        rivalry_factor = match_data.get('rivalry_factor', 1.0)
        
        adj_home_cards = home_cards_avg * referee_factor * importance_factor * rivalry_factor
        adj_away_cards = away_cards_avg * referee_factor * importance_factor * rivalry_factor
        
        # Probabilidade de receber primeiro cartão
        total_cards = adj_home_cards + adj_away_cards
        home_first_prob = adj_home_cards / total_cards if total_cards > 0 else 0.5
        away_first_prob = 1 - home_first_prob
        
        # Confiança baseada na diferença
        confidence = min(abs(home_first_prob - away_first_prob) * 2, 0.8)
        
        predictions.extend([
            MarketPrediction(
                market_type=MarketType.FIRST_CARD,
                selection="Casa",
                predicted_probability=home_first_prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Casa: {adj_home_cards:.1f}, Visitante: {adj_away_cards:.1f} cartões"
            ),
            MarketPrediction(
                market_type=MarketType.FIRST_CARD,
                selection="Visitante",
                predicted_probability=away_first_prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Casa: {adj_home_cards:.1f}, Visitante: {adj_away_cards:.1f} cartões"
            )
        ])
        
        return predictions
    
    def predict_card_timing(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz timing dos cartões (primeiro tempo, segundo tempo)"""
        predictions = []
        
        # Dados da partida
        total_cards_avg = match_data.get('total_cards_avg', 4.1)
        
        # Fatores de ajuste
        referee_factor = match_data.get('referee_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        
        adjusted_cards = total_cards_avg * referee_factor * importance_factor
        
        # Distribuição temporal (60% no segundo tempo)
        first_half_cards = adjusted_cards * 0.4
        second_half_cards = adjusted_cards * 0.6
        
        # Mercados de timing
        timing_markets = [
            ("1º Tempo Over 1.5", first_half_cards, 1.5),
            ("1º Tempo Under 1.5", first_half_cards, 1.5),
            ("2º Tempo Over 2.5", second_half_cards, 2.5),
            ("2º Tempo Under 2.5", second_half_cards, 2.5)
        ]
        
        for selection, avg_cards, threshold in timing_markets:
            if "Over" in selection:
                prob = self._calculate_over_probability(avg_cards, threshold)
            else:
                prob = 1 - self._calculate_over_probability(avg_cards, threshold)
            
            confidence = self._calculate_cards_confidence(avg_cards, threshold)
            
            predictions.append(MarketPrediction(
                market_type=MarketType.TOTAL_CARDS,
                selection=selection,
                predicted_probability=prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Média {selection.split()[0]}: {avg_cards:.1f} cartões"
            ))
        
        return predictions
    
    def _calculate_over_probability(self, lambda_param: float, threshold: float) -> float:
        """Calcula probabilidade over usando Poisson"""
        return 1 - poisson.cdf(int(threshold), lambda_param)
    
    def _calculate_cards_confidence(self, lambda_param: float, threshold: float) -> float:
        """Calcula confiança para cartões"""
        distance = abs(lambda_param - threshold)
        
        if distance <= 0.5:
            return 0.8
        elif distance <= 1.0:
            return 0.6
        elif distance <= 1.5:
            return 0.4
        else:
            return 0.2
    
    def _calculate_red_cards_confidence(self, lambda_param: float, threshold: int) -> float:
        """Calcula confiança para cartões vermelhos"""
        if lambda_param < 0.5:
            return 0.3  # Baixa confiança para poucos cartões vermelhos
        elif lambda_param < 1.0:
            return 0.5
        else:
            return 0.7
    
    def get_cards_statistics(self, match_data: Dict[str, Any]) -> Dict[str, float]:
        """Retorna estatísticas de cartões para a partida"""
        home_cards_avg = match_data.get('home_cards_avg', 2.1)
        away_cards_avg = match_data.get('away_cards_avg', 2.0)
        total_cards_avg = home_cards_avg + away_cards_avg
        
        home_yellow_avg = match_data.get('home_yellow_avg', 1.8)
        away_yellow_avg = match_data.get('away_yellow_avg', 1.7)
        total_yellow_avg = home_yellow_avg + away_yellow_avg
        
        home_red_avg = match_data.get('home_red_avg', 0.1)
        away_red_avg = match_data.get('away_red_avg', 0.1)
        total_red_avg = home_red_avg + away_red_avg
        
        return {
            'total_cards_avg': total_cards_avg,
            'yellow_cards_avg': total_yellow_avg,
            'red_cards_avg': total_red_avg,
            'over_35_cards_prob': self._calculate_over_probability(total_cards_avg, 3.5),
            'over_45_cards_prob': self._calculate_over_probability(total_cards_avg, 4.5),
            'red_card_prob': 1 - poisson.cdf(0, total_red_avg),
            'first_card_home_prob': home_cards_avg / total_cards_avg if total_cards_avg > 0 else 0.5
        }

if __name__ == "__main__":
    # Demo do mercado de cartões
    print("🟨 MERCADO DE CARTÕES - MARABET AI")
    print("=" * 40)
    
    cards_market = CardsMarket()
    
    # Dados de exemplo
    match_data = {
        'home_cards_avg': 2.3,
        'away_cards_avg': 2.1,
        'home_yellow_avg': 2.0,
        'away_yellow_avg': 1.8,
        'home_red_avg': 0.15,
        'away_red_avg': 0.12,
        'total_cards_avg': 4.4,
        'referee_factor': 1.2,  # Árbitro rigoroso
        'importance_factor': 1.1,  # Jogo importante
        'rivalry_factor': 1.3,  # Clássico
        'weather_factor': 1.0
    }
    
    # Estatísticas
    stats = cards_market.get_cards_statistics(match_data)
    print("📊 ESTATÍSTICAS DE CARTÕES:")
    for key, value in stats.items():
        print(f"  {key}: {value:.3f}")
    
    print(f"\n🟨 PREDIÇÕES TOTAL CARTÕES:")
    total_predictions = cards_market.predict_total_cards(match_data)
    for pred in total_predictions[:6]:  # Primeiras 6
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n🟡 PREDIÇÕES CARTÕES AMARELOS:")
    yellow_predictions = cards_market.predict_yellow_cards(match_data)
    for pred in yellow_predictions[:4]:  # Primeiras 4
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n🔴 PREDIÇÕES CARTÕES VERMELHOS:")
    red_predictions = cards_market.predict_red_cards(match_data)
    for pred in red_predictions:
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n⏰ PREDIÇÕES TIMING CARTÕES:")
    timing_predictions = cards_market.predict_card_timing(match_data)
    for pred in timing_predictions:
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print("\n✅ Mercado de cartões implementado com sucesso!")
