from typing import Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StatisticsProcessor:
    """Processador de estatísticas esportivas"""
    
    @staticmethod
    def calculate_form(matches: List[Dict], last_n: int = 5) -> Dict:
        """Calcula forma recente do time"""
        if not matches:
            return {'points': 0, 'wins': 0, 'draws': 0, 'losses': 0}
        
        recent = matches[:last_n]
        
        wins = sum(1 for m in recent if m.get('result') == 'W')
        draws = sum(1 for m in recent if m.get('result') == 'D')
        losses = sum(1 for m in recent if m.get('result') == 'L')
        points = wins * 3 + draws
        
        return {
            'points': points,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'win_rate': wins / len(recent) if recent else 0,
            'points_per_game': points / len(recent) if recent else 0
        }
    
    @staticmethod
    def calculate_goals_average(matches: List[Dict]) -> Dict:
        """Calcula médias de gols"""
        if not matches:
            return {'scored': 0, 'conceded': 0, 'total': 0}
        
        scored = [m.get('goals_scored', 0) for m in matches]
        conceded = [m.get('goals_conceded', 0) for m in matches]
        
        return {
            'scored_avg': np.mean(scored),
            'conceded_avg': np.mean(conceded),
            'total_avg': np.mean(scored) + np.mean(conceded),
            'scored_std': np.std(scored),
            'conceded_std': np.std(conceded)
        }
    
    @staticmethod
    def calculate_poisson_probability(avg_home: float, avg_away: float, 
                                     max_goals: int = 10) -> Dict:
        """Calcula probabilidades usando distribuição de Poisson"""
        from scipy.stats import poisson
        
        # Matriz de probabilidades
        prob_matrix = np.zeros((max_goals + 1, max_goals + 1))
        
        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                prob_matrix[home_goals, away_goals] = (
                    poisson.pmf(home_goals, avg_home) * 
                    poisson.pmf(away_goals, avg_away)
                )
        
        # Probabilidades de resultado
        home_win = np.sum(np.tril(prob_matrix, -1))
        draw = np.sum(np.diag(prob_matrix))
        away_win = np.sum(np.triu(prob_matrix, 1))
        
        # Over/Under 2.5
        over_25 = sum([
            prob_matrix[h, a] 
            for h in range(max_goals + 1) 
            for a in range(max_goals + 1) 
            if h + a > 2.5
        ])
        
        # Ambas marcam
        btts_yes = 1 - (
            np.sum(prob_matrix[0, :]) + 
            np.sum(prob_matrix[:, 0]) - 
            prob_matrix[0, 0]
        )
        
        return {
            'home_win': float(home_win),
            'draw': float(draw),
            'away_win': float(away_win),
            'over_25': float(over_25),
            'under_25': float(1 - over_25),
            'btts_yes': float(btts_yes),
            'btts_no': float(1 - btts_yes)
        }
    
    @staticmethod
    def calculate_expected_goals(statistics: Dict) -> float:
        """Calcula xG baseado em estatísticas"""
        # Implementação simplificada
        # Na prática, usar modelos mais complexos
        
        shots = statistics.get('shots_on_target', 0)
        possession = statistics.get('possession', 50) / 100
        attacks = statistics.get('dangerous_attacks', 0)
        
        xg = (shots * 0.1) + (possession * 1.5) + (attacks * 0.05)
        return round(xg, 2)
    
    @staticmethod
    def calculate_value(probability: float, odd: float) -> Dict:
        """Calcula valor esperado de uma aposta"""
        implied_prob = 1 / odd
        edge = probability - implied_prob
        ev = (probability * odd) - 1
        
        return {
            'probability': probability,
            'implied_probability': implied_prob,
            'edge': edge,
            'expected_value': ev,
            'has_value': ev > 0,
            'value_percentage': edge * 100
        }
    
    @staticmethod
    def kelly_criterion(probability: float, odd: float, 
                       fraction: float = 0.25) -> float:
        """Calcula stake ideal usando critério de Kelly"""
        if probability <= 0 or odd <= 1:
            return 0
        
        q = 1 - probability
        kelly = ((odd * probability) - 1) / (odd - 1)
        
        # Kelly fracionado (mais conservador)
        fractional_kelly = kelly * fraction
        
        # Limitar entre 0 e 10% da banca
        return max(0, min(fractional_kelly, 0.10))
