"""
Processador de Estatísticas - Sistema Básico
Processa e calcula estatísticas de dados esportivos
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)

class StatisticsProcessor:
    """Processador de estatísticas esportivas"""
    
    def __init__(self):
        self.processed_data = {}
        self.statistics_cache = {}
    
    def process_team_statistics(self, team_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processa estatísticas de um time"""
        if not team_data:
            return {}
        
        # Converte para DataFrame para facilitar cálculos
        df = pd.DataFrame(team_data)
        
        # Estatísticas básicas
        stats = {
            'team_id': df.iloc[0].get('team_id') if 'team_id' in df.columns else None,
            'team_name': df.iloc[0].get('name') if 'name' in df.columns else 'Unknown',
            'total_matches': len(df),
            'processed_at': datetime.now().isoformat()
        }
        
        # Processa diferentes tipos de dados
        if 'fixtures' in df.columns:
            stats.update(self._process_fixture_stats(df))
        
        if 'goals' in df.columns:
            stats.update(self._process_goal_stats(df))
        
        if 'form' in df.columns:
            stats.update(self._process_form_stats(df))
        
        return stats
    
    def _process_fixture_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Processa estatísticas de partidas"""
        stats = {}
        
        # Conta vitórias, empates e derrotas
        if 'status' in df.columns:
            status_counts = df['status'].value_counts()
            stats.update({
                'wins': int(status_counts.get('W', 0)),
                'draws': int(status_counts.get('D', 0)),
                'losses': int(status_counts.get('L', 0))
            })
            
            # Calcula percentuais
            total = stats['wins'] + stats['draws'] + stats['losses']
            if total > 0:
                stats.update({
                    'win_percentage': round(stats['wins'] / total * 100, 2),
                    'draw_percentage': round(stats['draws'] / total * 100, 2),
                    'loss_percentage': round(stats['losses'] / total * 100, 2)
                })
        
        return stats
    
    def _process_goal_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Processa estatísticas de gols"""
        stats = {}
        
        # Gols marcados e sofridos
        if 'goals_scored' in df.columns:
            goals_scored = df['goals_scored'].fillna(0)
            stats.update({
                'total_goals_scored': int(goals_scored.sum()),
                'avg_goals_scored': round(goals_scored.mean(), 2),
                'max_goals_scored': int(goals_scored.max()),
                'min_goals_scored': int(goals_scored.min())
            })
        
        if 'goals_conceded' in df.columns:
            goals_conceded = df['goals_conceded'].fillna(0)
            stats.update({
                'total_goals_conceded': int(goals_conceded.sum()),
                'avg_goals_conceded': round(goals_conceded.mean(), 2),
                'max_goals_conceded': int(goals_conceded.max()),
                'min_goals_conceded': int(goals_conceded.min())
            })
        
        # Clean sheets
        if 'goals_conceded' in df.columns:
            clean_sheets = (df['goals_conceded'] == 0).sum()
            stats['clean_sheets'] = int(clean_sheets)
            if len(df) > 0:
                stats['clean_sheet_percentage'] = round(clean_sheets / len(df) * 100, 2)
        
        # Failed to score
        if 'goals_scored' in df.columns:
            failed_to_score = (df['goals_scored'] == 0).sum()
            stats['failed_to_score'] = int(failed_to_score)
            if len(df) > 0:
                stats['failed_to_score_percentage'] = round(failed_to_score / len(df) * 100, 2)
        
        return stats
    
    def _process_form_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Processa estatísticas de forma"""
        stats = {}
        
        if 'form' in df.columns:
            form_string = df['form'].iloc[0] if len(df) > 0 else ''
            if form_string:
                # Conta W, D, L na string de forma
                wins = form_string.count('W')
                draws = form_string.count('D')
                losses = form_string.count('L')
                
                stats.update({
                    'form_wins': wins,
                    'form_draws': draws,
                    'form_losses': losses,
                    'form_string': form_string,
                    'form_points': wins * 3 + draws
                })
        
        return stats
    
    def process_match_statistics(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa estatísticas de uma partida específica"""
        stats = {
            'match_id': match_data.get('id'),
            'home_team': match_data.get('teams', {}).get('home', {}).get('name'),
            'away_team': match_data.get('teams', {}).get('away', {}).get('name'),
            'league': match_data.get('league', {}).get('name'),
            'date': match_data.get('date'),
            'processed_at': datetime.now().isoformat()
        }
        
        # Gols
        goals = match_data.get('goals', {})
        stats.update({
            'home_goals': goals.get('home', 0),
            'away_goals': goals.get('away', 0),
            'total_goals': goals.get('home', 0) + goals.get('away', 0)
        })
        
        # Status da partida
        status = match_data.get('status', {})
        stats.update({
            'status': status.get('short'),
            'status_long': status.get('long'),
            'elapsed_minutes': status.get('elapsed', 0)
        })
        
        # Resultado
        if stats['home_goals'] > stats['away_goals']:
            stats['result'] = 'home_win'
        elif stats['away_goals'] > stats['home_goals']:
            stats['result'] = 'away_win'
        else:
            stats['result'] = 'draw'
        
        # Over/Under
        total_goals = stats['total_goals']
        stats.update({
            'over_1_5': total_goals > 1.5,
            'over_2_5': total_goals > 2.5,
            'over_3_5': total_goals > 3.5,
            'both_teams_score': stats['home_goals'] > 0 and stats['away_goals'] > 0
        })
        
        return stats
    
    def process_head_to_head(self, h2h_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processa confrontos diretos entre dois times"""
        if not h2h_data:
            return {}
        
        df = pd.DataFrame(h2h_data)
        
        # Estatísticas básicas
        stats = {
            'total_matches': len(df),
            'processed_at': datetime.now().isoformat()
        }
        
        # Conta resultados
        if 'goals' in df.columns:
            home_wins = 0
            away_wins = 0
            draws = 0
            total_goals = 0
            both_teams_score = 0
            
            for _, match in df.iterrows():
                goals = match['goals']
                home_goals = goals.get('home', 0)
                away_goals = goals.get('away', 0)
                
                total_goals += home_goals + away_goals
                
                if home_goals > away_goals:
                    home_wins += 1
                elif away_goals > home_goals:
                    away_wins += 1
                else:
                    draws += 1
                
                if home_goals > 0 and away_goals > 0:
                    both_teams_score += 1
            
            stats.update({
                'home_wins': home_wins,
                'away_wins': away_wins,
                'draws': draws,
                'avg_goals_per_match': round(total_goals / len(df), 2) if len(df) > 0 else 0,
                'both_teams_score_matches': both_teams_score,
                'both_teams_score_percentage': round(both_teams_score / len(df) * 100, 2) if len(df) > 0 else 0
            })
        
        return stats
    
    def process_odds_statistics(self, odds_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processa estatísticas de odds"""
        if not odds_data:
            return {}
        
        stats = {
            'total_bookmakers': len(odds_data),
            'processed_at': datetime.now().isoformat()
        }
        
        # Coleta todas as odds
        all_odds = {
            'h2h': {'home_win': [], 'draw': [], 'away_win': []},
            'totals': {'over_2_5': [], 'under_2_5': []},
            'btts': {'yes': [], 'no': []}
        }
        
        for bookmaker_data in odds_data:
            odds = bookmaker_data.get('odds', {})
            
            for market, market_odds in odds.items():
                if market in all_odds:
                    for outcome, odd_value in market_odds.items():
                        if outcome in all_odds[market]:
                            all_odds[market][outcome].append(odd_value)
        
        # Calcula estatísticas
        for market, outcomes in all_odds.items():
            stats[market] = {}
            for outcome, values in outcomes.items():
                if values:
                    stats[market][outcome] = {
                        'min': round(min(values), 2),
                        'max': round(max(values), 2),
                        'avg': round(np.mean(values), 2),
                        'median': round(np.median(values), 2),
                        'std': round(np.std(values), 2)
                    }
        
        return stats
    
    def calculate_team_form(self, recent_matches: List[Dict[str, Any]], 
                           team_id: int, matches: int = 5) -> Dict[str, Any]:
        """Calcula forma recente de um time"""
        if not recent_matches or len(recent_matches) < matches:
            return {}
        
        # Pega os últimos N jogos
        last_matches = recent_matches[-matches:]
        
        form_stats = {
            'matches_analyzed': len(last_matches),
            'period': f"Last {len(last_matches)} matches",
            'processed_at': datetime.now().isoformat()
        }
        
        wins = 0
        draws = 0
        losses = 0
        goals_scored = 0
        goals_conceded = 0
        
        for match in last_matches:
            # Determina se o time jogou em casa ou fora
            home_team_id = match.get('teams', {}).get('home', {}).get('id')
            away_team_id = match.get('teams', {}).get('away', {}).get('id')
            
            if team_id == home_team_id:
                # Time jogou em casa
                team_goals = match.get('goals', {}).get('home', 0)
                opponent_goals = match.get('goals', {}).get('away', 0)
            elif team_id == away_team_id:
                # Time jogou fora
                team_goals = match.get('goals', {}).get('away', 0)
                opponent_goals = match.get('goals', {}).get('home', 0)
            else:
                continue
            
            goals_scored += team_goals
            goals_conceded += opponent_goals
            
            if team_goals > opponent_goals:
                wins += 1
            elif team_goals < opponent_goals:
                losses += 1
            else:
                draws += 1
        
        form_stats.update({
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'points': wins * 3 + draws,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'goal_difference': goals_scored - goals_conceded,
            'win_percentage': round(wins / len(last_matches) * 100, 2),
            'avg_goals_scored': round(goals_scored / len(last_matches), 2),
            'avg_goals_conceded': round(goals_conceded / len(last_matches), 2)
        })
        
        return form_stats
    
    def calculate_probabilities(self, team_stats: Dict[str, Any], 
                               opponent_stats: Dict[str, Any]) -> Dict[str, float]:
        """Calcula probabilidades baseadas em estatísticas"""
        probabilities = {}
        
        # Probabilidades básicas baseadas em forma
        home_form = team_stats.get('win_percentage', 50) / 100
        away_form = opponent_stats.get('win_percentage', 50) / 100
        
        # Ajusta para probabilidades que somam 1
        total_form = home_form + away_form + 0.3  # 30% de chance de empate
        
        probabilities['home_win'] = home_form / total_form
        probabilities['draw'] = 0.3 / total_form
        probabilities['away_win'] = away_form / total_form
        
        # Probabilidades de Over/Under baseadas em gols médios
        home_avg_goals = team_stats.get('avg_goals_scored', 1.5)
        away_avg_goals = opponent_stats.get('avg_goals_scored', 1.5)
        total_avg_goals = home_avg_goals + away_avg_goals
        
        # Usa distribuição de Poisson para calcular probabilidades
        probabilities['over_1_5'] = self._poisson_probability(total_avg_goals, 1.5, 'over')
        probabilities['over_2_5'] = self._poisson_probability(total_avg_goals, 2.5, 'over')
        probabilities['over_3_5'] = self._poisson_probability(total_avg_goals, 3.5, 'over')
        
        # Probabilidade de ambas marcarem
        home_score_prob = 1 - math.exp(-home_avg_goals)
        away_score_prob = 1 - math.exp(-away_avg_goals)
        probabilities['both_teams_score'] = home_score_prob * away_score_prob
        
        return probabilities
    
    def _poisson_probability(self, lambda_val: float, threshold: float, 
                           direction: str) -> float:
        """Calcula probabilidade usando distribuição de Poisson"""
        if direction == 'over':
            # P(X > threshold)
            prob = 0
            for k in range(int(threshold) + 1):
                prob += (lambda_val ** k * math.exp(-lambda_val)) / math.factorial(k)
            return 1 - prob
        else:
            # P(X <= threshold)
            prob = 0
            for k in range(int(threshold) + 1):
                prob += (lambda_val ** k * math.exp(-lambda_val)) / math.factorial(k)
            return prob
    
    def get_processed_data(self, data_type: str) -> Dict[str, Any]:
        """Retorna dados processados por tipo"""
        return self.processed_data.get(data_type, {})
    
    def clear_cache(self):
        """Limpa cache de dados processados"""
        self.processed_data.clear()
        self.statistics_cache.clear()
        logger.info("Cache de estatísticas limpo")
