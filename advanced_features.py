"""
Framework de Análise MaraBet AI
Sistema Avançado de Feature Engineering
Implementa features baseadas no framework de análise completo
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from data_framework import DataProcessor, AdvancedDataCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedFeatureEngineer:
    """Engineer de features avançadas seguindo o framework"""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.collector = AdvancedDataCollector()
        
    def create_comprehensive_features(self, home_team: str, away_team: str, match_date: str) -> Dict:
        """
        Cria features abrangentes seguindo o framework completo
        """
        logger.info(f"Criando features abrangentes para {home_team} vs {away_team}")
        
        # Coleta análise completa
        match_analysis = self.data_processor.process_match_analysis(home_team, away_team, match_date)
        
        # Cria features por categoria
        features = {}
        
        # 1. Features Históricas (10-20 partidas)
        features.update(self._create_historical_features(match_analysis))
        
        # 2. Features de Confronto Direto (H2H)
        features.update(self._create_h2h_features(match_analysis))
        
        # 3. Features de Desempenho Casa/Fora
        features.update(self._create_home_away_features(match_analysis))
        
        # 4. Features de Forma Recente (últimos 5 jogos)
        features.update(self._create_recent_form_features(match_analysis))
        
        # 5. Features de Estatísticas Avançadas
        features.update(self._create_advanced_stats_features(match_analysis))
        
        # 6. Features de Contexto Competitivo
        features.update(self._create_competitive_context_features(match_analysis))
        
        # 7. Features de Fatores Contextuais
        features.update(self._create_contextual_features(match_analysis))
        
        # 8. Features Comparativas
        features.update(self._create_comparative_features(match_analysis))
        
        # 9. Features de Tendências
        features.update(self._create_trend_features(match_analysis))
        
        # 10. Features de Momentum
        features.update(self._create_momentum_features(match_analysis))
        
        return features
    
    def _create_historical_features(self, match_analysis: Dict) -> Dict:
        """Cria features baseadas em estatísticas históricas (10-20 partidas)"""
        home_stats = match_analysis['home_team_analysis']['historical_stats']
        away_stats = match_analysis['away_team_analysis']['historical_stats']
        
        features = {}
        
        # Features básicas do time da casa
        features['home_matches_played'] = home_stats.matches_played
        features['home_win_rate'] = home_stats.wins / home_stats.matches_played if home_stats.matches_played > 0 else 0
        features['home_draw_rate'] = home_stats.draws / home_stats.matches_played if home_stats.matches_played > 0 else 0
        features['home_loss_rate'] = home_stats.losses / home_stats.matches_played if home_stats.matches_played > 0 else 0
        features['home_goals_per_game'] = home_stats.goals_scored
        features['home_goals_conceded_per_game'] = home_stats.goals_conceded
        features['home_goal_difference'] = home_stats.goals_scored - home_stats.goals_conceded
        features['home_xg_per_game'] = home_stats.xg_for
        features['home_xg_against_per_game'] = home_stats.xg_against
        features['home_xg_difference'] = home_stats.xg_for - home_stats.xg_against
        features['home_possession'] = home_stats.possession
        features['home_shots_per_game'] = home_stats.shots
        features['home_shots_on_target_per_game'] = home_stats.shots_on_target
        features['home_shot_accuracy'] = home_stats.shots_on_target / home_stats.shots if home_stats.shots > 0 else 0
        features['home_pass_accuracy'] = home_stats.pass_accuracy
        features['home_clean_sheet_rate'] = home_stats.clean_sheets / home_stats.matches_played if home_stats.matches_played > 0 else 0
        features['home_failed_to_score_rate'] = home_stats.failed_to_score / home_stats.matches_played if home_stats.matches_played > 0 else 0
        
        # Features básicas do time visitante
        features['away_matches_played'] = away_stats.matches_played
        features['away_win_rate'] = away_stats.wins / away_stats.matches_played if away_stats.matches_played > 0 else 0
        features['away_draw_rate'] = away_stats.draws / away_stats.matches_played if away_stats.matches_played > 0 else 0
        features['away_loss_rate'] = away_stats.losses / away_stats.matches_played if away_stats.matches_played > 0 else 0
        features['away_goals_per_game'] = away_stats.goals_scored
        features['away_goals_conceded_per_game'] = away_stats.goals_conceded
        features['away_goal_difference'] = away_stats.goals_scored - away_stats.goals_conceded
        features['away_xg_per_game'] = away_stats.xg_for
        features['away_xg_against_per_game'] = away_stats.xg_against
        features['away_xg_difference'] = away_stats.xg_for - away_stats.xg_against
        features['away_possession'] = away_stats.possession
        features['away_shots_per_game'] = away_stats.shots
        features['away_shots_on_target_per_game'] = away_stats.shots_on_target
        features['away_shot_accuracy'] = away_stats.shots_on_target / away_stats.shots if away_stats.shots > 0 else 0
        features['away_pass_accuracy'] = away_stats.pass_accuracy
        features['away_clean_sheet_rate'] = away_stats.clean_sheets / away_stats.matches_played if away_stats.matches_played > 0 else 0
        features['away_failed_to_score_rate'] = away_stats.failed_to_score / away_stats.matches_played if away_stats.matches_played > 0 else 0
        
        return features
    
    def _create_h2h_features(self, match_analysis: Dict) -> Dict:
        """Cria features de confronto direto (H2H)"""
        h2h = match_analysis['head_to_head']
        
        features = {}
        
        features['h2h_total_matches'] = h2h.get('total_matches', 0)
        features['h2h_home_wins'] = h2h.get('team1_wins', 0)
        features['h2h_away_wins'] = h2h.get('team2_wins', 0)
        features['h2h_draws'] = h2h.get('draws', 0)
        features['h2h_home_win_rate'] = h2h.get('team1_win_rate', 0)
        features['h2h_away_win_rate'] = h2h.get('team2_win_rate', 0)
        features['h2h_draw_rate'] = h2h.get('draw_rate', 0)
        features['h2h_home_goals'] = h2h.get('team1_goals', 0)
        features['h2h_away_goals'] = h2h.get('team2_goals', 0)
        features['h2h_home_avg_goals'] = h2h.get('team1_avg_goals', 0)
        features['h2h_away_avg_goals'] = h2h.get('team2_avg_goals', 0)
        features['h2h_goal_difference'] = h2h.get('team1_avg_goals', 0) - h2h.get('team2_avg_goals', 0)
        
        # Features de tendência H2H
        if h2h.get('last_result') == 'team1_win':
            features['h2h_last_result_home'] = 1
        elif h2h.get('last_result') == 'team2_win':
            features['h2h_last_result_home'] = -1
        else:
            features['h2h_last_result_home'] = 0
        
        return features
    
    def _create_home_away_features(self, match_analysis: Dict) -> Dict:
        """Cria features de desempenho casa/fora"""
        home_home_away = match_analysis['home_team_analysis']['home_away_performance']
        away_home_away = match_analysis['away_team_analysis']['home_away_performance']
        
        features = {}
        
        # Performance em casa do time da casa
        home_home = home_home_away['home']
        features['home_home_matches'] = home_home['matches']
        features['home_home_win_rate'] = home_home['win_rate']
        features['home_home_goals_scored'] = home_home['goals_scored']
        features['home_home_goals_conceded'] = home_home['goals_conceded']
        features['home_home_avg_goals_scored'] = home_home['avg_goals_scored']
        features['home_home_avg_goals_conceded'] = home_home['avg_goals_conceded']
        features['home_home_goal_difference'] = home_home['goal_difference']
        
        # Performance fora do time visitante
        away_away = away_home_away['away']
        features['away_away_matches'] = away_away['matches']
        features['away_away_win_rate'] = away_away['win_rate']
        features['away_away_goals_scored'] = away_away['goals_scored']
        features['away_away_goals_conceded'] = away_away['goals_conceded']
        features['away_away_avg_goals_scored'] = away_away['avg_goals_scored']
        features['away_away_avg_goals_conceded'] = away_away['avg_goals_conceded']
        features['away_away_goal_difference'] = away_away['goal_difference']
        
        # Fator casa
        features['home_advantage'] = home_home_away['home_advantage']
        features['home_away_advantage'] = home_home['win_rate'] - away_away['win_rate']
        
        return features
    
    def _create_recent_form_features(self, match_analysis: Dict) -> Dict:
        """Cria features de forma recente (últimos 5 jogos)"""
        home_form = match_analysis['home_team_analysis']['recent_form']
        away_form = match_analysis['away_team_analysis']['recent_form']
        
        features = {}
        
        # Forma do time da casa
        features['home_recent_matches'] = home_form['matches']
        features['home_recent_wins'] = home_form['wins']
        features['home_recent_draws'] = home_form['draws']
        features['home_recent_losses'] = home_form['losses']
        features['home_recent_points'] = home_form['points']
        features['home_recent_win_rate'] = home_form['win_rate']
        features['home_recent_goals_scored'] = home_form['goals_scored']
        features['home_recent_goals_conceded'] = home_form['goals_conceded']
        features['home_recent_avg_goals_scored'] = home_form['avg_goals_scored']
        features['home_recent_avg_goals_conceded'] = home_form['avg_goals_conceded']
        features['home_recent_form'] = self._encode_form(home_form['form'])
        features['home_recent_trend'] = self._encode_trend(home_form['trend'])
        
        # Forma do time visitante
        features['away_recent_matches'] = away_form['matches']
        features['away_recent_wins'] = away_form['wins']
        features['away_recent_draws'] = away_form['draws']
        features['away_recent_losses'] = away_form['losses']
        features['away_recent_points'] = away_form['points']
        features['away_recent_win_rate'] = away_form['win_rate']
        features['away_recent_goals_scored'] = away_form['goals_scored']
        features['away_recent_goals_conceded'] = away_form['goals_conceded']
        features['away_recent_avg_goals_scored'] = away_form['avg_goals_scored']
        features['away_recent_avg_goals_conceded'] = away_form['avg_goals_conceded']
        features['away_recent_form'] = self._encode_form(away_form['form'])
        features['away_recent_trend'] = self._encode_trend(away_form['trend'])
        
        return features
    
    def _create_advanced_stats_features(self, match_analysis: Dict) -> Dict:
        """Cria features de estatísticas avançadas"""
        home_advanced = match_analysis['home_team_analysis']['advanced_stats']
        away_advanced = match_analysis['away_team_analysis']['advanced_stats']
        
        features = {}
        
        # Estatísticas avançadas do time da casa
        features['home_xg_for'] = home_advanced['xg_for']
        features['home_xg_against'] = home_advanced['xg_against']
        features['home_xg_difference'] = home_advanced['xg_difference']
        features['home_possession_advanced'] = home_advanced['possession']
        features['home_shots_per_game_advanced'] = home_advanced['shots_per_game']
        features['home_shots_on_target_per_game_advanced'] = home_advanced['shots_on_target_per_game']
        features['home_shot_accuracy_advanced'] = home_advanced['shot_accuracy']
        features['home_passes_per_game'] = home_advanced['passes_per_game']
        features['home_pass_accuracy_advanced'] = home_advanced['pass_accuracy']
        features['home_key_passes_per_game'] = home_advanced['key_passes_per_game']
        features['home_crosses_per_game'] = home_advanced['crosses_per_game']
        features['home_cross_accuracy'] = home_advanced['cross_accuracy']
        features['home_aerial_duels_won'] = home_advanced['aerial_duels_won']
        features['home_tackles_per_game'] = home_advanced['tackles_per_game']
        features['home_interceptions_per_game'] = home_advanced['interceptions_per_game']
        features['home_fouls_per_game'] = home_advanced['fouls_per_game']
        features['home_cards_per_game'] = home_advanced['cards_per_game']
        features['home_corners_per_game'] = home_advanced['corners_per_game']
        features['home_offsides_per_game'] = home_advanced['offsides_per_game']
        
        # Estatísticas avançadas do time visitante
        features['away_xg_for'] = away_advanced['xg_for']
        features['away_xg_against'] = away_advanced['xg_against']
        features['away_xg_difference'] = away_advanced['xg_difference']
        features['away_possession_advanced'] = away_advanced['possession']
        features['away_shots_per_game_advanced'] = away_advanced['shots_per_game']
        features['away_shots_on_target_per_game_advanced'] = away_advanced['shots_on_target_per_game']
        features['away_shot_accuracy_advanced'] = away_advanced['shot_accuracy']
        features['away_passes_per_game'] = away_advanced['passes_per_game']
        features['away_pass_accuracy_advanced'] = away_advanced['pass_accuracy']
        features['away_key_passes_per_game'] = away_advanced['key_passes_per_game']
        features['away_crosses_per_game'] = away_advanced['crosses_per_game']
        features['away_cross_accuracy'] = away_advanced['cross_accuracy']
        features['away_aerial_duels_won'] = away_advanced['aerial_duels_won']
        features['away_tackles_per_game'] = away_advanced['tackles_per_game']
        features['away_interceptions_per_game'] = away_advanced['interceptions_per_game']
        features['away_fouls_per_game'] = away_advanced['fouls_per_game']
        features['away_cards_per_game'] = away_advanced['cards_per_game']
        features['away_corners_per_game'] = away_advanced['corners_per_game']
        features['away_offsides_per_game'] = away_advanced['offsides_per_game']
        
        return features
    
    def _create_competitive_context_features(self, match_analysis: Dict) -> Dict:
        """Cria features de contexto competitivo"""
        home_context = match_analysis['home_team_analysis']['competitive_context']
        away_context = match_analysis['away_team_analysis']['competitive_context']
        
        features = {}
        
        # Contexto do time da casa
        features['home_position'] = home_context['position']
        features['home_total_teams'] = home_context['total_teams']
        features['home_points'] = home_context['points']
        features['home_games_played'] = home_context['games_played']
        features['home_points_per_game'] = home_context['points_per_game']
        features['home_objective'] = self._encode_objective(home_context['objective'])
        features['home_pressure_level'] = self._encode_pressure(home_context['pressure_level'])
        features['home_form_importance'] = self._encode_importance(home_context['form_importance'])
        features['home_home_advantage_level'] = self._encode_advantage(home_context['home_advantage'])
        
        # Contexto do time visitante
        features['away_position'] = away_context['position']
        features['away_total_teams'] = away_context['total_teams']
        features['away_points'] = away_context['points']
        features['away_games_played'] = away_context['games_played']
        features['away_points_per_game'] = away_context['points_per_game']
        features['away_objective'] = self._encode_objective(away_context['objective'])
        features['away_pressure_level'] = self._encode_pressure(away_context['pressure_level'])
        features['away_form_importance'] = self._encode_importance(away_context['form_importance'])
        features['away_home_advantage_level'] = self._encode_advantage(away_context['home_advantage'])
        
        # Features comparativas de contexto
        features['position_difference'] = home_context['position'] - away_context['position']
        features['points_difference'] = home_context['points'] - away_context['points']
        features['points_per_game_difference'] = home_context['points_per_game'] - away_context['points_per_game']
        
        return features
    
    def _create_contextual_features(self, match_analysis: Dict) -> Dict:
        """Cria features de fatores contextuais"""
        context = match_analysis['match_context']
        
        features = {}
        
        # Features básicas do contexto
        features['competition'] = self._encode_competition(context.competition)
        features['weather'] = self._encode_weather(context.weather)
        features['referee'] = self._encode_referee(context.referee)
        
        # Features de lesões e suspensões
        features['home_injuries_count'] = len(context.home_team_injuries)
        features['away_injuries_count'] = len(context.away_team_injuries)
        features['home_suspensions_count'] = len(context.home_team_suspensions)
        features['away_suspensions_count'] = len(context.away_team_suspensions)
        features['total_absences_home'] = len(context.home_team_injuries) + len(context.home_team_suspensions)
        features['total_absences_away'] = len(context.away_team_injuries) + len(context.away_team_suspensions)
        features['absence_difference'] = features['total_absences_home'] - features['total_absences_away']
        
        # Features de forma no contexto
        features['home_form_context'] = self._encode_form(context.home_team_form)
        features['away_form_context'] = self._encode_form(context.away_team_form)
        
        return features
    
    def _create_comparative_features(self, match_analysis: Dict) -> Dict:
        """Cria features comparativas entre os times"""
        comp_analysis = match_analysis['comparative_analysis']
        
        features = {}
        
        # Comparação de forma
        features['form_difference'] = self._encode_form(comp_analysis['form_comparison']['home_form']) - \
                                    self._encode_form(comp_analysis['form_comparison']['away_form'])
        features['home_advantage_factor'] = comp_analysis['form_comparison']['home_advantage']
        
        # Comparação estatística
        stats_comp = comp_analysis['statistical_comparison']
        features['goals_scored_difference'] = stats_comp['goals_scored']
        features['goals_conceded_difference'] = stats_comp['goals_conceded']
        features['possession_difference'] = stats_comp['possession']
        features['xg_difference'] = stats_comp['xg_difference']
        
        # Comparação de contexto competitivo
        comp_context = comp_analysis['competitive_context']
        features['position_difference_comp'] = comp_context['home_position'] - comp_context['away_position']
        features['pressure_difference'] = self._encode_pressure(comp_context['home_pressure']) - \
                                        self._encode_pressure(comp_context['away_pressure'])
        
        # Comparação H2H
        h2h_summary = comp_analysis['head_to_head_summary']
        features['h2h_advantage'] = h2h_summary['home_h2h_advantage']
        
        return features
    
    def _create_trend_features(self, match_analysis: Dict) -> Dict:
        """Cria features de tendências"""
        home_form = match_analysis['home_team_analysis']['recent_form']
        away_form = match_analysis['away_team_analysis']['recent_form']
        
        features = {}
        
        # Tendências de forma
        features['home_trend'] = self._encode_trend(home_form['trend'])
        features['away_trend'] = self._encode_trend(away_form['trend'])
        features['trend_difference'] = features['home_trend'] - features['away_trend']
        
        # Tendências de gols
        features['home_goals_trend'] = self._calculate_goals_trend(match_analysis['home_team_analysis'])
        features['away_goals_trend'] = self._calculate_goals_trend(match_analysis['away_team_analysis'])
        
        return features
    
    def _create_momentum_features(self, match_analysis: Dict) -> Dict:
        """Cria features de momentum"""
        home_form = match_analysis['home_team_analysis']['recent_form']
        away_form = match_analysis['away_team_analysis']['recent_form']
        
        features = {}
        
        # Momentum baseado em pontos
        features['home_momentum_points'] = home_form['points']
        features['away_momentum_points'] = away_form['points']
        features['momentum_difference'] = home_form['points'] - away_form['points']
        
        # Momentum baseado em gols
        features['home_momentum_goals'] = home_form['goals_scored'] - home_form['goals_conceded']
        features['away_momentum_goals'] = away_form['goals_scored'] - away_form['goals_conceded']
        features['goals_momentum_difference'] = features['home_momentum_goals'] - features['away_momentum_goals']
        
        return features
    
    # Métodos auxiliares para encoding
    def _encode_form(self, form: str) -> int:
        """Codifica forma em número"""
        form_map = {'excellent': 4, 'good': 3, 'average': 2, 'poor': 1, 'unknown': 0}
        return form_map.get(form, 0)
    
    def _encode_trend(self, trend: str) -> int:
        """Codifica tendência em número"""
        trend_map = {'improving': 1, 'stable': 0, 'declining': -1}
        return trend_map.get(trend, 0)
    
    def _encode_objective(self, objective: str) -> int:
        """Codifica objetivo em número"""
        obj_map = {'libertadores': 4, 'sul_americana': 3, 'mid_table': 2, 'avoid_relegation': 1}
        return obj_map.get(objective, 0)
    
    def _encode_pressure(self, pressure: str) -> int:
        """Codifica pressão em número"""
        pressure_map = {'high': 3, 'medium': 2, 'low': 1}
        return pressure_map.get(pressure, 0)
    
    def _encode_importance(self, importance: str) -> int:
        """Codifica importância em número"""
        importance_map = {'high': 3, 'medium': 2, 'low': 1}
        return importance_map.get(importance, 0)
    
    def _encode_advantage(self, advantage: str) -> int:
        """Codifica vantagem em número"""
        advantage_map = {'high': 3, 'medium': 2, 'low': 1}
        return advantage_map.get(advantage, 0)
    
    def _encode_competition(self, competition: str) -> int:
        """Codifica competição em número"""
        comp_map = {'Brasileirão': 3, 'Copa do Brasil': 2, 'Libertadores': 4, 'Sul-Americana': 1}
        return comp_map.get(competition, 0)
    
    def _encode_weather(self, weather: str) -> int:
        """Codifica clima em número"""
        weather_map = {'Ensolarado': 3, 'Nublado': 2, 'Chuvoso': 1}
        return weather_map.get(weather, 0)
    
    def _encode_referee(self, referee: str) -> int:
        """Codifica árbitro em número (simulado)"""
        return hash(referee) % 10
    
    def _calculate_goals_trend(self, team_analysis: Dict) -> float:
        """Calcula tendência de gols de um time"""
        historical = team_analysis['historical_stats']
        recent = team_analysis['recent_form']
        
        historical_goals = historical.goals_scored
        recent_goals = recent['avg_goals_scored']
        
        return recent_goals - historical_goals

class FeatureSelector:
    """Seletor de features para otimização"""
    
    def __init__(self):
        self.important_features = [
            # Features históricas mais importantes
            'home_win_rate', 'away_win_rate', 'home_goals_per_game', 'away_goals_per_game',
            'home_goals_conceded_per_game', 'away_goals_conceded_per_game',
            'home_xg_difference', 'away_xg_difference',
            
            # Features de forma recente
            'home_recent_win_rate', 'away_recent_win_rate',
            'home_recent_form', 'away_recent_form',
            'home_recent_trend', 'away_recent_trend',
            
            # Features de confronto direto
            'h2h_home_win_rate', 'h2h_away_win_rate', 'h2h_goal_difference',
            
            # Features de desempenho casa/fora
            'home_home_win_rate', 'away_away_win_rate', 'home_advantage',
            
            # Features de contexto competitivo
            'position_difference', 'points_per_game_difference',
            'home_pressure_level', 'away_pressure_level',
            
            # Features comparativas
            'form_difference', 'goals_scored_difference', 'possession_difference',
            'h2h_advantage', 'momentum_difference'
        ]
    
    def select_features(self, features: Dict) -> Dict:
        """Seleciona features mais importantes"""
        selected = {}
        for feature in self.important_features:
            if feature in features:
                selected[feature] = features[feature]
        return selected
    
    def get_feature_importance_ranking(self) -> List[str]:
        """Retorna ranking de importância das features"""
        return self.important_features

if __name__ == "__main__":
    # Teste do sistema de features avançadas
    engineer = AdvancedFeatureEngineer()
    
    # Cria features para uma partida
    features = engineer.create_comprehensive_features('Flamengo', 'Palmeiras', '2024-01-15')
    
    print("=== FEATURES AVANÇADAS CRIADAS ===")
    print(f"Total de features: {len(features)}")
    
    # Mostra algumas features importantes
    important_features = [
        'home_win_rate', 'away_win_rate', 'home_recent_form', 'away_recent_form',
        'h2h_home_win_rate', 'home_advantage', 'form_difference', 'position_difference'
    ]
    
    print("\nFeatures importantes:")
    for feature in important_features:
        if feature in features:
            print(f"{feature}: {features[feature]}")
    
    # Testa seletor de features
    selector = FeatureSelector()
    selected_features = selector.select_features(features)
    print(f"\nFeatures selecionadas: {len(selected_features)}")
