#!/usr/bin/env python3
"""
Mercado de Golos - MaraBet AI
Implementa predições específicas para mercados relacionados a gols
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
from scipy.stats import poisson
from .expanded_markets import MarketType, MarketPrediction

logger = logging.getLogger(__name__)

class GoalsMarket:
    """Mercado especializado em predições de gols"""
    
    def __init__(self):
        self.goal_thresholds = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
        self.exact_goals = [0, 1, 2, 3, 4, 5]
    
    def predict_over_under(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz over/under para diferentes thresholds de gols"""
        predictions = []
        
        # Dados da partida
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        total_goals_avg = home_goals_avg + away_goals_avg
        
        # Fatores de ajuste
        home_advantage = match_data.get('home_advantage', 0.1)
        weather_factor = match_data.get('weather_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        
        # Ajustar média de gols
        adjusted_goals = total_goals_avg * weather_factor * importance_factor
        
        for threshold in self.goal_thresholds:
            # Probabilidade over
            over_prob = self._calculate_over_probability(adjusted_goals, threshold)
            under_prob = 1 - over_prob
            
            # Confiança baseada na proximidade da média
            confidence = self._calculate_confidence(adjusted_goals, threshold)
            
            predictions.extend([
                MarketPrediction(
                    market_type=MarketType.OVER_UNDER,
                    selection=f"Over {threshold}",
                    predicted_probability=over_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Média ajustada: {adjusted_goals:.1f} gols"
                ),
                MarketPrediction(
                    market_type=MarketType.OVER_UNDER,
                    selection=f"Under {threshold}",
                    predicted_probability=under_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"Média ajustada: {adjusted_goals:.1f} gols"
                )
            ])
        
        return predictions
    
    def predict_exact_goals(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz número exato de gols"""
        predictions = []
        
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        total_goals_avg = home_goals_avg + away_goals_avg
        
        # Fatores de ajuste
        weather_factor = match_data.get('weather_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        adjusted_goals = total_goals_avg * weather_factor * importance_factor
        
        for goals in self.exact_goals:
            if goals == 5:  # 5+ gols
                prob = 1 - sum(poisson.pmf(k, adjusted_goals) for k in range(5))
                selection = "5+"
            else:
                prob = poisson.pmf(goals, adjusted_goals)
                selection = str(goals)
            
            # Confiança baseada na probabilidade
            confidence = min(prob * 3, 0.8)  # Máximo 80% de confiança
            
            predictions.append(MarketPrediction(
                market_type=MarketType.EXACT_GOALS,
                selection=selection,
                predicted_probability=prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Distribuição de Poisson com λ={adjusted_goals:.1f}"
            ))
        
        return predictions
    
    def predict_both_teams_score(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz ambas marcam (BTTS)"""
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        
        # Fatores de ajuste
        home_advantage = match_data.get('home_advantage', 0.1)
        weather_factor = match_data.get('weather_factor', 1.0)
        
        # Ajustar médias
        adj_home_goals = home_goals_avg * (1 + home_advantage) * weather_factor
        adj_away_goals = away_goals_avg * weather_factor
        
        # Probabilidade de ambas marcarem
        home_scores_prob = 1 - poisson.cdf(0, adj_home_goals)
        away_scores_prob = 1 - poisson.cdf(0, adj_away_goals)
        btts_prob = home_scores_prob * away_scores_prob
        
        # Confiança baseada na força dos ataques
        confidence = min((adj_home_goals + adj_away_goals) / 4, 0.8)
        
        return [
            MarketPrediction(
                market_type=MarketType.BOTH_TEAMS_SCORE,
                selection="Sim",
                predicted_probability=btts_prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Probabilidade casa: {home_scores_prob:.1%}, visitante: {away_scores_prob:.1%}"
            ),
            MarketPrediction(
                market_type=MarketType.BOTH_TEAMS_SCORE,
                selection="Não",
                predicted_probability=1 - btts_prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Probabilidade casa: {home_scores_prob:.1%}, visitante: {away_scores_prob:.1%}"
            )
        ]
    
    def predict_first_half_goals(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz gols do primeiro tempo"""
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        total_goals_avg = home_goals_avg + away_goals_avg
        
        # Primeiro tempo geralmente tem menos gols (60% da média total)
        first_half_goals = total_goals_avg * 0.6
        
        # Fatores de ajuste
        weather_factor = match_data.get('weather_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        adjusted_goals = first_half_goals * weather_factor * importance_factor
        
        predictions = []
        for threshold in [0.5, 1.5]:
            over_prob = self._calculate_over_probability(adjusted_goals, threshold)
            under_prob = 1 - over_prob
            
            confidence = self._calculate_confidence(adjusted_goals, threshold)
            
            predictions.extend([
                MarketPrediction(
                    market_type=MarketType.FIRST_HALF_GOALS,
                    selection=f"Over {threshold}",
                    predicted_probability=over_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"1ª parte - média ajustada: {adjusted_goals:.1f} gols"
                ),
                MarketPrediction(
                    market_type=MarketType.FIRST_HALF_GOALS,
                    selection=f"Under {threshold}",
                    predicted_probability=under_prob,
                    confidence=confidence,
                    expected_value=0.0,
                    kelly_fraction=0.0,
                    reasoning=f"1ª parte - média ajustada: {adjusted_goals:.1f} gols"
                )
            ])
        
        return predictions
    
    def predict_clean_sheet(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz jogo limpo (qual equipe não sofre gols)"""
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        
        # Fatores de ajuste
        home_advantage = match_data.get('home_advantage', 0.1)
        weather_factor = match_data.get('weather_factor', 1.0)
        
        # Ajustar médias
        adj_home_goals = home_goals_avg * (1 + home_advantage) * weather_factor
        adj_away_goals = away_goals_avg * weather_factor
        
        # Probabilidades de jogo limpo
        home_clean_sheet = poisson.cdf(0, adj_away_goals)  # Casa não sofre
        away_clean_sheet = poisson.cdf(0, adj_home_goals)  # Visitante não sofre
        no_clean_sheet = 1 - home_clean_sheet - away_clean_sheet
        
        # Normalizar probabilidades
        total = home_clean_sheet + away_clean_sheet + no_clean_sheet
        home_clean_sheet /= total
        away_clean_sheet /= total
        no_clean_sheet /= total
        
        confidence = min((adj_home_goals + adj_away_goals) / 4, 0.7)
        
        return [
            MarketPrediction(
                market_type=MarketType.CLEAN_SHEET,
                selection="Casa",
                predicted_probability=home_clean_sheet,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Visitante marca em média {adj_away_goals:.1f} gols"
            ),
            MarketPrediction(
                market_type=MarketType.CLEAN_SHEET,
                selection="Visitante",
                predicted_probability=away_clean_sheet,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Casa marca em média {adj_home_goals:.1f} gols"
            ),
            MarketPrediction(
                market_type=MarketType.CLEAN_SHEET,
                selection="Nenhum",
                predicted_probability=no_clean_sheet,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning="Ambas as equipes marcam"
            )
        ]
    
    def _calculate_over_probability(self, lambda_param: float, threshold: float) -> float:
        """Calcula probabilidade over usando Poisson"""
        return 1 - poisson.cdf(int(threshold), lambda_param)
    
    def _calculate_confidence(self, lambda_param: float, threshold: float) -> float:
        """Calcula confiança baseada na proximidade da média"""
        distance = abs(lambda_param - threshold)
        if distance <= 0.5:
            return 0.8  # Alta confiança
        elif distance <= 1.0:
            return 0.6  # Média confiança
        else:
            return 0.4  # Baixa confiança
    
    def get_goal_statistics(self, match_data: Dict[str, Any]) -> Dict[str, float]:
        """Retorna estatísticas de gols para a partida"""
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        total_goals_avg = home_goals_avg + away_goals_avg
        
        return {
            'home_goals_avg': home_goals_avg,
            'away_goals_avg': away_goals_avg,
            'total_goals_avg': total_goals_avg,
            'btts_probability': (1 - np.exp(-home_goals_avg)) * (1 - np.exp(-away_goals_avg)),
            'over_25_probability': self._calculate_over_probability(total_goals_avg, 2.5),
            'under_25_probability': 1 - self._calculate_over_probability(total_goals_avg, 2.5)
        }

if __name__ == "__main__":
    # Demo do mercado de gols
    print("⚽ MERCADO DE GOLOS - MARABET AI")
    print("=" * 40)
    
    goals_market = GoalsMarket()
    
    # Dados de exemplo
    match_data = {
        'home_goals_avg': 1.8,
        'away_goals_avg': 1.4,
        'home_advantage': 0.15,
        'weather_factor': 0.9,  # Chuva reduz gols
        'importance_factor': 1.1  # Jogo importante aumenta gols
    }
    
    # Estatísticas
    stats = goals_market.get_goal_statistics(match_data)
    print("📊 ESTATÍSTICAS DE GOLOS:")
    for key, value in stats.items():
        print(f"  {key}: {value:.3f}")
    
    print(f"\n🔮 PREDIÇÕES OVER/UNDER:")
    over_under_predictions = goals_market.predict_over_under(match_data)
    for pred in over_under_predictions[:6]:  # Primeiras 6
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n🎯 PREDIÇÕES GOLS EXATOS:")
    exact_predictions = goals_market.predict_exact_goals(match_data)
    for pred in exact_predictions:
        print(f"  {pred.selection} gols: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n⚽ PREDIÇÕES BTTS:")
    btts_predictions = goals_market.predict_both_teams_score(match_data)
    for pred in btts_predictions:
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print("\n✅ Mercado de gols implementado com sucesso!")
