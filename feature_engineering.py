import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureEngineer:
    def __init__(self):
        self.config = Config()
        
    def create_team_features(self, team_data, opponent_data, is_home=True):
        """
        Cria features para um time baseado em dados históricos
        """
        features = {}
        
        # Features básicas
        features['is_home'] = 1 if is_home else 0
        
        # Features de forma recente (últimos 5 jogos)
        recent_form = self._calculate_recent_form(team_data, 5)
        features.update(recent_form)
        
        # Features de forma em casa/fora
        home_away_form = self._calculate_home_away_form(team_data, is_home)
        features.update(home_away_form)
        
        # Features de confronto direto
        h2h_features = self._calculate_head_to_head_features(team_data, opponent_data)
        features.update(h2h_features)
        
        # Features de estatísticas ofensivas e defensivas
        offensive_features = self._calculate_offensive_features(team_data)
        features.update(offensive_features)
        
        defensive_features = self._calculate_defensive_features(team_data)
        features.update(defensive_features)
        
        # Features de tendências
        trend_features = self._calculate_trend_features(team_data)
        features.update(trend_features)
        
        return features
    
    def _calculate_recent_form(self, team_data, matches=5):
        """Calcula forma recente do time"""
        if len(team_data) < matches:
            matches = len(team_data)
        
        recent_matches = team_data[-matches:] if team_data else []
        
        if not recent_matches:
            return {
                f'recent_wins_{matches}': 0,
                f'recent_draws_{matches}': 0,
                f'recent_losses_{matches}': 0,
                f'recent_win_rate_{matches}': 0,
                f'recent_points_{matches}': 0,
                f'recent_goals_scored_{matches}': 0,
                f'recent_goals_conceded_{matches}': 0,
                f'recent_goal_difference_{matches}': 0
            }
        
        wins = sum(1 for match in recent_matches if match['result'] == 'win')
        draws = sum(1 for match in recent_matches if match['result'] == 'draw')
        losses = sum(1 for match in recent_matches if match['result'] == 'loss')
        
        goals_scored = sum(match['goals_scored'] for match in recent_matches)
        goals_conceded = sum(match['goals_conceded'] for match in recent_matches)
        points = wins * 3 + draws
        
        return {
            f'recent_wins_{matches}': wins,
            f'recent_draws_{matches}': draws,
            f'recent_losses_{matches}': losses,
            f'recent_win_rate_{matches}': wins / matches if matches > 0 else 0,
            f'recent_points_{matches}': points,
            f'recent_goals_scored_{matches}': goals_scored,
            f'recent_goals_conceded_{matches}': goals_conceded,
            f'recent_goal_difference_{matches}': goals_scored - goals_conceded
        }
    
    def _calculate_home_away_form(self, team_data, is_home):
        """Calcula forma em casa ou fora"""
        location_matches = [match for match in team_data if match.get('is_home', False) == is_home]
        
        if not location_matches:
            return {
                f'{"home" if is_home else "away"}_wins': 0,
                f'{"home" if is_home else "away"}_draws': 0,
                f'{"home" if is_home else "away"}_losses': 0,
                f'{"home" if is_home else "away"}_win_rate': 0,
                f'{"home" if is_home else "away"}_goals_scored': 0,
                f'{"home" if is_home else "away"}_goals_conceded': 0
            }
        
        wins = sum(1 for match in location_matches if match['result'] == 'win')
        draws = sum(1 for match in location_matches if match['result'] == 'draw')
        losses = sum(1 for match in location_matches if match['result'] == 'loss')
        
        goals_scored = sum(match['goals_scored'] for match in location_matches)
        goals_conceded = sum(match['goals_conceded'] for match in location_matches)
        
        return {
            f'{"home" if is_home else "away"}_wins': wins,
            f'{"home" if is_home else "away"}_draws': draws,
            f'{"home" if is_home else "away"}_losses': losses,
            f'{"home" if is_home else "away"}_win_rate': wins / len(location_matches) if location_matches else 0,
            f'{"home" if is_home else "away"}_goals_scored': goals_scored,
            f'{"home" if is_home else "away"}_goals_conceded': goals_conceded
        }
    
    def _calculate_head_to_head_features(self, team_data, opponent_data):
        """Calcula features de confronto direto"""
        # Simulação de confrontos diretos - em produção, buscar dados reais
        h2h_matches = self._simulate_h2h_matches(team_data, opponent_data)
        
        if not h2h_matches:
            return {
                'h2h_wins': 0,
                'h2h_draws': 0,
                'h2h_losses': 0,
                'h2h_win_rate': 0,
                'h2h_goals_scored': 0,
                'h2h_goals_conceded': 0
            }
        
        wins = sum(1 for match in h2h_matches if match['result'] == 'win')
        draws = sum(1 for match in h2h_matches if match['result'] == 'draw')
        losses = sum(1 for match in h2h_matches if match['result'] == 'loss')
        
        goals_scored = sum(match['goals_scored'] for match in h2h_matches)
        goals_conceded = sum(match['goals_conceded'] for match in h2h_matches)
        
        return {
            'h2h_wins': wins,
            'h2h_draws': draws,
            'h2h_losses': losses,
            'h2h_win_rate': wins / len(h2h_matches) if h2h_matches else 0,
            'h2h_goals_scored': goals_scored,
            'h2h_goals_conceded': goals_conceded
        }
    
    def _simulate_h2h_matches(self, team_data, opponent_data):
        """Simula confrontos diretos entre times"""
        # Em produção, buscar dados reais de confrontos
        import random
        
        h2h_matches = []
        for i in range(min(5, len(team_data))):  # Últimos 5 confrontos
            match = {
                'result': random.choice(['win', 'draw', 'loss']),
                'goals_scored': random.randint(0, 3),
                'goals_conceded': random.randint(0, 3)
            }
            h2h_matches.append(match)
        
        return h2h_matches
    
    def _calculate_offensive_features(self, team_data):
        """Calcula features ofensivas"""
        if not team_data:
            return {
                'avg_goals_scored': 0,
                'goals_scored_consistency': 0,
                'scoring_trend': 0
            }
        
        goals_scored = [match['goals_scored'] for match in team_data]
        avg_goals = np.mean(goals_scored)
        
        # Consistência ofensiva (menor desvio = mais consistente)
        consistency = 1 / (1 + np.std(goals_scored)) if len(goals_scored) > 1 else 0
        
        # Tendência ofensiva (últimos jogos vs primeiros)
        if len(goals_scored) >= 6:
            recent_goals = np.mean(goals_scored[-3:])
            early_goals = np.mean(goals_scored[:3])
            trend = recent_goals - early_goals
        else:
            trend = 0
        
        return {
            'avg_goals_scored': avg_goals,
            'goals_scored_consistency': consistency,
            'scoring_trend': trend
        }
    
    def _calculate_defensive_features(self, team_data):
        """Calcula features defensivas"""
        if not team_data:
            return {
                'avg_goals_conceded': 0,
                'goals_conceded_consistency': 0,
                'defensive_trend': 0
            }
        
        goals_conceded = [match['goals_conceded'] for match in team_data]
        avg_goals = np.mean(goals_conceded)
        
        # Consistência defensiva
        consistency = 1 / (1 + np.std(goals_conceded)) if len(goals_conceded) > 1 else 0
        
        # Tendência defensiva
        if len(goals_conceded) >= 6:
            recent_goals = np.mean(goals_conceded[-3:])
            early_goals = np.mean(goals_conceded[:3])
            trend = early_goals - recent_goals  # Positivo = melhora defensiva
        else:
            trend = 0
        
        return {
            'avg_goals_conceded': avg_goals,
            'goals_conceded_consistency': consistency,
            'defensive_trend': trend
        }
    
    def _calculate_trend_features(self, team_data):
        """Calcula features de tendências"""
        if len(team_data) < 3:
            return {
                'form_trend': 0,
                'momentum': 0
            }
        
        # Tendência de forma (pontos nos últimos jogos)
        recent_points = []
        for match in team_data[-3:]:
            if match['result'] == 'win':
                recent_points.append(3)
            elif match['result'] == 'draw':
                recent_points.append(1)
            else:
                recent_points.append(0)
        
        form_trend = np.mean(recent_points) if recent_points else 0
        
        # Momentum (melhora ou piora recente)
        if len(team_data) >= 6:
            recent_form = np.mean(recent_points)
            earlier_form = np.mean([
                3 if match['result'] == 'win' else 1 if match['result'] == 'draw' else 0
                for match in team_data[-6:-3]
            ])
            momentum = recent_form - earlier_form
        else:
            momentum = 0
        
        return {
            'form_trend': form_trend,
            'momentum': momentum
        }
    
    def create_match_features(self, home_team_data, away_team_data, match_info):
        """
        Cria features para uma partida específica
        """
        # Features do time da casa
        home_features = self.create_team_features(home_team_data, away_team_data, is_home=True)
        
        # Features do time visitante
        away_features = self.create_team_features(away_team_data, home_team_data, is_home=False)
        
        # Features da partida
        match_features = {
            'home_team': match_info.get('home_team', ''),
            'away_team': match_info.get('away_team', ''),
            'league': match_info.get('league', ''),
            'home_odds': match_info.get('home_odds', 0),
            'draw_odds': match_info.get('draw_odds', 0),
            'away_odds': match_info.get('away_odds', 0)
        }
        
        # Features comparativas
        comparative_features = self._create_comparative_features(home_features, away_features)
        
        # Combina todas as features
        all_features = {}
        all_features.update({f'home_{k}': v for k, v in home_features.items()})
        all_features.update({f'away_{k}': v for k, v in away_features.items()})
        all_features.update(match_features)
        all_features.update(comparative_features)
        
        return all_features
    
    def _create_comparative_features(self, home_features, away_features):
        """Cria features comparativas entre os times"""
        comparative = {}
        
        # Comparação de forma recente
        home_recent_points = home_features.get('recent_points_5', 0)
        away_recent_points = away_features.get('recent_points_5', 0)
        comparative['form_difference'] = home_recent_points - away_recent_points
        
        # Comparação de gols
        home_goals = home_features.get('avg_goals_scored', 0)
        away_goals = away_features.get('avg_goals_scored', 0)
        comparative['goals_scored_difference'] = home_goals - away_goals
        
        # Comparação defensiva
        home_conceded = home_features.get('avg_goals_conceded', 0)
        away_conceded = away_features.get('avg_goals_conceded', 0)
        comparative['goals_conceded_difference'] = away_conceded - home_conceded
        
        # Fator casa
        home_advantage = home_features.get('home_win_rate', 0) - away_features.get('away_win_rate', 0)
        comparative['home_advantage'] = home_advantage
        
        return comparative
    
    def prepare_training_data(self, matches_data, historical_data):
        """
        Prepara dados de treinamento para os modelos
        """
        training_data = []
        
        for match in matches_data:
            home_team = match['home_team']
            away_team = match['away_team']
            
            # Busca dados históricos dos times
            home_team_data = historical_data.get(home_team, [])
            away_team_data = historical_data.get(away_team, [])
            
            # Cria features da partida
            features = self.create_match_features(home_team_data, away_team_data, match)
            
            # Adiciona resultado (se disponível)
            if 'result' in match:
                features['result'] = match['result']
                features['home_goals'] = match.get('home_goals', 0)
                features['away_goals'] = match.get('away_goals', 0)
            
            training_data.append(features)
        
        return pd.DataFrame(training_data)

if __name__ == "__main__":
    # Teste do FeatureEngineer
    engineer = FeatureEngineer()
    
    # Dados simulados para teste
    team_data = [
        {'result': 'win', 'goals_scored': 2, 'goals_conceded': 1, 'is_home': True},
        {'result': 'draw', 'goals_scored': 1, 'goals_conceded': 1, 'is_home': False},
        {'result': 'loss', 'goals_scored': 0, 'goals_conceded': 2, 'is_home': True},
        {'result': 'win', 'goals_scored': 3, 'goals_conceded': 0, 'is_home': False},
        {'result': 'win', 'goals_scored': 2, 'goals_conceded': 1, 'is_home': True}
    ]
    
    opponent_data = [
        {'result': 'loss', 'goals_scored': 0, 'goals_conceded': 2, 'is_home': True},
        {'result': 'win', 'goals_scored': 2, 'goals_conceded': 1, 'is_home': False},
        {'result': 'draw', 'goals_scored': 1, 'goals_conceded': 1, 'is_home': True}
    ]
    
    features = engineer.create_team_features(team_data, opponent_data, is_home=True)
    print("Features do time:", features)
