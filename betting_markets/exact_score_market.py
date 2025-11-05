#!/usr/bin/env python3
"""
Mercado de Resultado Exato - MaraBet AI
Implementa predições para resultado exato e mercados relacionados
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
from scipy.stats import poisson
from .expanded_markets import MarketType, MarketPrediction

logger = logging.getLogger(__name__)

class ExactScoreMarket:
    """Mercado especializado em predições de resultado exato"""
    
    def __init__(self):
        self.common_scores = [
            "1-0", "2-0", "2-1", "3-0", "3-1", "3-2",
            "0-0", "1-1", "2-2", "3-3",
            "0-1", "0-2", "1-2", "0-3", "1-3", "2-3"
        ]
        self.half_time_scores = [
            "0-0", "1-0", "0-1", "1-1", "2-0", "0-2", "2-1", "1-2"
        ]
    
    def predict_exact_score(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz resultado exato da partida"""
        predictions = []
        
        # Dados da partida
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        
        # Fatores de ajuste
        home_advantage = match_data.get('home_advantage', 0.1)
        weather_factor = match_data.get('weather_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        
        # Ajustar médias de gols
        adj_home_goals = home_goals_avg * (1 + home_advantage) * weather_factor * importance_factor
        adj_away_goals = away_goals_avg * weather_factor * importance_factor
        
        # Calcular probabilidades para cada resultado
        for score in self.common_scores:
            home_goals, away_goals = map(int, score.split('-'))
            
            # Probabilidade usando Poisson
            home_prob = poisson.pmf(home_goals, adj_home_goals)
            away_prob = poisson.pmf(away_goals, adj_away_goals)
            total_prob = home_prob * away_prob
            
            # Confiança baseada na probabilidade
            confidence = min(total_prob * 10, 0.8)  # Máximo 80% de confiança
            
            predictions.append(MarketPrediction(
                market_type=MarketType.EXACT_SCORE,
                selection=score,
                predicted_probability=total_prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Casa: {adj_home_goals:.1f} gols, Visitante: {adj_away_goals:.1f} gols"
            ))
        
        return predictions
    
    def predict_half_time_score(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz resultado do intervalo"""
        predictions = []
        
        # Dados da partida
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        
        # Fatores de ajuste
        home_advantage = match_data.get('home_advantage', 0.1)
        weather_factor = match_data.get('weather_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        
        # Ajustar médias de gols
        adj_home_goals = home_goals_avg * (1 + home_advantage) * weather_factor * importance_factor
        adj_away_goals = away_goals_avg * weather_factor * importance_factor
        
        # Primeiro tempo geralmente tem menos gols (60% da média total)
        first_half_home = adj_home_goals * 0.6
        first_half_away = adj_away_goals * 0.6
        
        # Calcular probabilidades para cada resultado do intervalo
        for score in self.half_time_scores:
            home_goals, away_goals = map(int, score.split('-'))
            
            # Probabilidade usando Poisson
            home_prob = poisson.pmf(home_goals, first_half_home)
            away_prob = poisson.pmf(away_goals, first_half_away)
            total_prob = home_prob * away_prob
            
            # Confiança baseada na probabilidade
            confidence = min(total_prob * 15, 0.8)  # Máximo 80% de confiança
            
            predictions.append(MarketPrediction(
                market_type=MarketType.HALF_TIME_SCORE,
                selection=score,
                predicted_probability=total_prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"1ª parte - Casa: {first_half_home:.1f} gols, Visitante: {first_half_away:.1f} gols"
            ))
        
        return predictions
    
    def predict_correct_score_group(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz grupos de resultado exato"""
        predictions = []
        
        # Dados da partida
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        
        # Fatores de ajuste
        home_advantage = match_data.get('home_advantage', 0.1)
        weather_factor = match_data.get('weather_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        
        # Ajustar médias de gols
        adj_home_goals = home_goals_avg * (1 + home_advantage) * weather_factor * importance_factor
        adj_away_goals = away_goals_avg * weather_factor * importance_factor
        
        # Grupos de resultado
        score_groups = {
            "0-0": [(0, 0)],
            "1-0": [(1, 0)],
            "2-0": [(2, 0)],
            "2-1": [(2, 1)],
            "3-0": [(3, 0)],
            "3-1": [(3, 1)],
            "3-2": [(3, 2)],
            "1-1": [(1, 1)],
            "2-2": [(2, 2)],
            "3-3": [(3, 3)],
            "Outros": []  # Será calculado como 1 - soma dos outros
        }
        
        # Calcular probabilidades para cada grupo
        group_probs = {}
        total_prob = 0
        
        for group, scores in score_groups.items():
            if group == "Outros":
                continue
                
            group_prob = 0
            for home_goals, away_goals in scores:
                home_prob = poisson.pmf(home_goals, adj_home_goals)
                away_prob = poisson.pmf(away_goals, adj_away_goals)
                group_prob += home_prob * away_prob
            
            group_probs[group] = group_prob
            total_prob += group_prob
        
        # Adicionar "Outros"
        group_probs["Outros"] = max(0, 1 - total_prob)
        
        # Criar predições
        for group, prob in group_probs.items():
            confidence = min(prob * 8, 0.8)
            
            predictions.append(MarketPrediction(
                market_type=MarketType.EXACT_SCORE,
                selection=group,
                predicted_probability=prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Casa: {adj_home_goals:.1f} gols, Visitante: {adj_away_goals:.1f} gols"
            ))
        
        return predictions
    
    def predict_win_to_nil(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz vitória sem sofrer gols"""
        predictions = []
        
        # Dados da partida
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        
        # Fatores de ajuste
        home_advantage = match_data.get('home_advantage', 0.1)
        weather_factor = match_data.get('weather_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        
        # Ajustar médias de gols
        adj_home_goals = home_goals_avg * (1 + home_advantage) * weather_factor * importance_factor
        adj_away_goals = away_goals_avg * weather_factor * importance_factor
        
        # Probabilidades de vitória sem sofrer gols
        home_win_to_nil = (1 - poisson.cdf(0, adj_away_goals)) * (1 - poisson.cdf(0, adj_home_goals))
        away_win_to_nil = (1 - poisson.cdf(0, adj_home_goals)) * (1 - poisson.cdf(0, adj_away_goals))
        no_win_to_nil = 1 - home_win_to_nil - away_win_to_nil
        
        # Normalizar
        total = home_win_to_nil + away_win_to_nil + no_win_to_nil
        home_win_to_nil /= total
        away_win_to_nil /= total
        no_win_to_nil /= total
        
        confidence = min((adj_home_goals + adj_away_goals) / 4, 0.7)
        
        predictions.extend([
            MarketPrediction(
                market_type=MarketType.WIN_TO_NIL,
                selection="Casa",
                predicted_probability=home_win_to_nil,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Casa marca e não sofre: {home_win_to_nil:.1%}"
            ),
            MarketPrediction(
                market_type=MarketType.WIN_TO_NIL,
                selection="Visitante",
                predicted_probability=away_win_to_nil,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Visitante marca e não sofre: {away_win_to_nil:.1%}"
            ),
            MarketPrediction(
                market_type=MarketType.WIN_TO_NIL,
                selection="Nenhum",
                predicted_probability=no_win_to_nil,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning="Ambas marcam ou empate"
            )
        ])
        
        return predictions
    
    def predict_goal_intervals(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Prediz intervalos de gols"""
        predictions = []
        
        # Dados da partida
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        total_goals_avg = home_goals_avg + away_goals_avg
        
        # Fatores de ajuste
        home_advantage = match_data.get('home_advantage', 0.1)
        weather_factor = match_data.get('weather_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        
        # Ajustar média total
        adj_total_goals = total_goals_avg * (1 + home_advantage) * weather_factor * importance_factor
        
        # Intervalos de gols
        goal_intervals = [
            ("0-1 gols", 0, 1),
            ("2-3 gols", 2, 3),
            ("4-5 gols", 4, 5),
            ("6+ gols", 6, 10)
        ]
        
        for interval_name, min_goals, max_goals in goal_intervals:
            if max_goals == 10:  # 6+ gols
                prob = 1 - poisson.cdf(5, adj_total_goals)
            else:
                prob = poisson.cdf(max_goals, adj_total_goals) - poisson.cdf(min_goals - 1, adj_total_goals)
            
            confidence = min(prob * 6, 0.8)
            
            predictions.append(MarketPrediction(
                market_type=MarketType.GOAL_INTERVAL,
                selection=interval_name,
                predicted_probability=prob,
                confidence=confidence,
                expected_value=0.0,
                kelly_fraction=0.0,
                reasoning=f"Média total ajustada: {adj_total_goals:.1f} gols"
            ))
        
        return predictions
    
    def get_exact_score_statistics(self, match_data: Dict[str, Any]) -> Dict[str, float]:
        """Retorna estatísticas de resultado exato para a partida"""
        home_goals_avg = match_data.get('home_goals_avg', 1.5)
        away_goals_avg = match_data.get('away_goals_avg', 1.2)
        total_goals_avg = home_goals_avg + away_goals_avg
        
        # Fatores de ajuste
        home_advantage = match_data.get('home_advantage', 0.1)
        weather_factor = match_data.get('weather_factor', 1.0)
        importance_factor = match_data.get('importance_factor', 1.0)
        
        # Ajustar médias
        adj_home_goals = home_goals_avg * (1 + home_advantage) * weather_factor * importance_factor
        adj_away_goals = away_goals_avg * weather_factor * importance_factor
        adj_total_goals = adj_home_goals + adj_away_goals
        
        # Calcular probabilidades dos resultados mais comuns
        most_likely_scores = {}
        for score in ["1-0", "2-1", "1-1", "2-0", "0-1", "1-2"]:
            home_goals, away_goals = map(int, score.split('-'))
            home_prob = poisson.pmf(home_goals, adj_home_goals)
            away_prob = poisson.pmf(away_goals, adj_away_goals)
            most_likely_scores[score] = home_prob * away_prob
        
        return {
            'home_goals_avg': adj_home_goals,
            'away_goals_avg': adj_away_goals,
            'total_goals_avg': adj_total_goals,
            'most_likely_score': max(most_likely_scores, key=most_likely_scores.get),
            'most_likely_probability': max(most_likely_scores.values()),
            'score_1_0_prob': most_likely_scores.get('1-0', 0),
            'score_2_1_prob': most_likely_scores.get('2-1', 0),
            'score_1_1_prob': most_likely_scores.get('1-1', 0),
            'score_2_0_prob': most_likely_scores.get('2-0', 0),
            'win_to_nil_home_prob': (1 - poisson.cdf(0, adj_away_goals)) * (1 - poisson.cdf(0, adj_home_goals)),
            'win_to_nil_away_prob': (1 - poisson.cdf(0, adj_home_goals)) * (1 - poisson.cdf(0, adj_away_goals))
        }

if __name__ == "__main__":
    # Demo do mercado de resultado exato
    print("🎯 MERCADO DE RESULTADO EXATO - MARABET AI")
    print("=" * 45)
    
    exact_score_market = ExactScoreMarket()
    
    # Dados de exemplo
    match_data = {
        'home_goals_avg': 1.8,
        'away_goals_avg': 1.4,
        'home_advantage': 0.15,
        'weather_factor': 0.9,  # Chuva reduz gols
        'importance_factor': 1.1  # Jogo importante
    }
    
    # Estatísticas
    stats = exact_score_market.get_exact_score_statistics(match_data)
    print("📊 ESTATÍSTICAS DE RESULTADO EXATO:")
    for key, value in stats.items():
        print(f"  {key}: {value:.3f}")
    
    print(f"\n🎯 PREDIÇÕES RESULTADO EXATO:")
    exact_predictions = exact_score_market.predict_exact_score(match_data)
    for pred in exact_predictions[:8]:  # Primeiras 8
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n⏰ PREDIÇÕES RESULTADO INTERVALO:")
    half_time_predictions = exact_score_market.predict_half_time_score(match_data)
    for pred in half_time_predictions:
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n🏆 PREDIÇÕES VITÓRIA SEM SOFRER:")
    win_to_nil_predictions = exact_score_market.predict_win_to_nil(match_data)
    for pred in win_to_nil_predictions:
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print(f"\n📊 PREDIÇÕES GRUPOS DE RESULTADO:")
    group_predictions = exact_score_market.predict_correct_score_group(match_data)
    for pred in group_predictions[:6]:  # Primeiras 6
        print(f"  {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
    
    print("\n✅ Mercado de resultado exato implementado com sucesso!")
