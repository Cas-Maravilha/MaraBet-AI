#!/usr/bin/env python3
"""
Sistema de Feature Engineering para previsões esportivas
MaraBet AI - Sistema de Apostas Esportivas Inteligentes
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Classe para criação de features avançadas"""
    
    def __init__(self):
        self.feature_cache = {}
        self.team_stats = {}
        self.league_stats = {}
    
    def create_form_features(self, df: pd.DataFrame, team_col: str, score_col: str, 
                           window_sizes: List[int] = [3, 5, 10]) -> pd.DataFrame:
        """Cria features de forma dos times"""
        logger.info(f"🔧 Criando features de forma para {team_col}...")
        
        result_df = df.copy()
        
        for window in window_sizes:
            # Forma em casa
            result_df[f'{team_col}_form_{window}'] = (
                result_df.groupby(team_col)[score_col]
                .rolling(window, min_periods=1)
                .mean()
                .reset_index(0, drop=True)
            )
            
            # Forma recente (últimos 3 jogos)
            result_df[f'{team_col}_form_recent'] = (
                result_df.groupby(team_col)[score_col]
                .rolling(3, min_periods=1)
                .mean()
                .reset_index(0, drop=True)
            )
        
        return result_df
    
    def create_goals_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features relacionadas a gols"""
        logger.info("⚽ Criando features de gols...")
        
        result_df = df.copy()
        
        # Médias de gols
        result_df['home_goals_avg'] = (
            result_df.groupby('home_team_id')['home_score']
            .expanding()
            .mean()
            .reset_index(0, drop=True)
        )
        
        result_df['away_goals_avg'] = (
            result_df.groupby('away_team_id')['away_score']
            .expanding()
            .mean()
            .reset_index(0, drop=True)
        )
        
        # Gols sofridos
        result_df['home_goals_conceded_avg'] = (
            result_df.groupby('home_team_id')['away_score']
            .expanding()
            .mean()
            .reset_index(0, drop=True)
        )
        
        result_df['away_goals_conceded_avg'] = (
            result_df.groupby('away_team_id')['home_score']
            .expanding()
            .mean()
            .reset_index(0, drop=True)
        )
        
        # Total de gols
        result_df['total_goals'] = result_df['home_score'] + result_df['away_score']
        result_df['total_goals_avg'] = (
            result_df.groupby(['home_team_id', 'away_team_id'])['total_goals']
            .expanding()
            .mean()
            .reset_index(level=[0, 1], drop=True)
        )
        
        return result_df
    
    def create_h2h_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features de confronto direto"""
        logger.info("🤝 Criando features de confronto direto...")
        
        result_df = df.copy()
        
        # Vitórias em casa
        result_df['h2h_home_wins'] = (
            result_df.groupby(['home_team_id', 'away_team_id'])['home_win']
            .expanding()
            .sum()
            .reset_index(level=[0, 1], drop=True)
        )
        
        # Vitórias fora
        result_df['h2h_away_wins'] = (
            result_df.groupby(['home_team_id', 'away_team_id'])['away_win']
            .expanding()
            .sum()
            .reset_index(level=[0, 1], drop=True)
        )
        
        # Empates
        result_df['h2h_draws'] = (
            result_df.groupby(['home_team_id', 'away_team_id'])['draw']
            .expanding()
            .sum()
            .reset_index(level=[0, 1], drop=True)
        )
        
        # Total de confrontos
        result_df['h2h_total'] = (
            result_df['h2h_home_wins'] + 
            result_df['h2h_away_wins'] + 
            result_df['h2h_draws']
        )
        
        # Percentual de vitórias
        result_df['h2h_home_win_pct'] = result_df['h2h_home_wins'] / (result_df['h2h_total'] + 1)
        result_df['h2h_away_win_pct'] = result_df['h2h_away_wins'] / (result_df['h2h_total'] + 1)
        result_df['h2h_draw_pct'] = result_df['h2h_draws'] / (result_df['h2h_total'] + 1)
        
        return result_df
    
    def create_odds_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features derivadas das odds"""
        logger.info("💰 Criando features de odds...")
        
        result_df = df.copy()
        
        # Preencher odds faltantes
        result_df['home_odd'] = result_df['home_odd'].fillna(result_df['home_odd'].median())
        result_df['draw_odd'] = result_df['draw_odd'].fillna(result_df['draw_odd'].median())
        result_df['away_odd'] = result_df['away_odd'].fillna(result_df['away_odd'].median())
        
        # Probabilidades implícitas
        result_df['home_prob'] = 1 / result_df['home_odd']
        result_df['draw_prob'] = 1 / result_df['draw_odd']
        result_df['away_prob'] = 1 / result_df['away_odd']
        
        # Normalizar probabilidades
        total_prob = result_df['home_prob'] + result_df['draw_prob'] + result_df['away_prob']
        result_df['home_prob_norm'] = result_df['home_prob'] / total_prob
        result_df['draw_prob_norm'] = result_df['draw_prob'] / total_prob
        result_df['away_prob_norm'] = result_df['away_prob'] / total_prob
        
        # Valor das apostas
        result_df['home_value'] = result_df['home_prob_norm'] - result_df['home_prob_norm'].mean()
        result_df['draw_value'] = result_df['draw_prob_norm'] - result_df['draw_prob_norm'].mean()
        result_df['away_value'] = result_df['away_prob_norm'] - result_df['away_prob_norm'].mean()
        
        # Margem da casa
        result_df['bookmaker_margin'] = total_prob - 1
        
        # Diferença entre odds
        result_df['home_away_odd_diff'] = result_df['home_odd'] - result_df['away_odd']
        result_df['home_draw_odd_diff'] = result_df['home_odd'] - result_df['draw_odd']
        result_df['draw_away_odd_diff'] = result_df['draw_odd'] - result_df['away_odd']
        
        return result_df
    
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features temporais"""
        logger.info("📅 Criando features temporais...")
        
        result_df = df.copy()
        
        # Converter data
        result_df['date'] = pd.to_datetime(result_df['date'])
        
        # Dia da semana
        result_df['day_of_week'] = result_df['date'].dt.dayofweek
        result_df['is_weekend'] = result_df['day_of_week'].isin([5, 6]).astype(int)
        
        # Mês
        result_df['month'] = result_df['date'].dt.month
        result_df['is_winter'] = result_df['month'].isin([12, 1, 2]).astype(int)
        
        # Hora (se disponível)
        if 'time' in result_df.columns:
            result_df['hour'] = pd.to_datetime(result_df['time']).dt.hour
            result_df['is_evening'] = result_df['hour'].between(18, 23).astype(int)
        
        # Dias desde último jogo
        result_df['days_since_last_home'] = (
            result_df.groupby('home_team_id')['date']
            .diff()
            .dt.days
            .fillna(7)
        )
        
        result_df['days_since_last_away'] = (
            result_df.groupby('away_team_id')['date']
            .diff()
            .dt.days
            .fillna(7)
        )
        
        return result_df
    
    def create_league_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features da liga"""
        logger.info("🏆 Criando features da liga...")
        
        result_df = df.copy()
        
        # Média de gols da liga
        result_df['league_goals_avg'] = (
            result_df.groupby('league_id')['total_goals']
            .expanding()
            .mean()
            .reset_index(0, drop=True)
        )
        
        # Média de gols em casa da liga
        result_df['league_home_goals_avg'] = (
            result_df.groupby('league_id')['home_score']
            .expanding()
            .mean()
            .reset_index(0, drop=True)
        )
        
        # Média de gols fora da liga
        result_df['league_away_goals_avg'] = (
            result_df.groupby('league_id')['away_score']
            .expanding()
            .mean()
            .reset_index(0, drop=True)
        )
        
        # Percentual de empates da liga
        result_df['league_draw_pct'] = (
            result_df.groupby('league_id')['draw']
            .expanding()
            .mean()
            .reset_index(0, drop=True)
        )
        
        return result_df
    
    def create_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features de momentum"""
        logger.info("📈 Criando features de momentum...")
        
        result_df = df.copy()
        
        # Momentum de gols
        result_df['home_momentum'] = (
            result_df.groupby('home_team_id')['home_score']
            .diff()
            .rolling(3)
            .mean()
            .reset_index(0, drop=True)
        )
        
        result_df['away_momentum'] = (
            result_df.groupby('away_team_id')['away_score']
            .diff()
            .rolling(3)
            .mean()
            .reset_index(0, drop=True)
        )
        
        # Sequência de vitórias/derrotas
        result_df['home_win_streak'] = (
            result_df.groupby('home_team_id')['home_win']
            .apply(lambda x: x * (x.groupby((x != x.shift()).cumsum()).cumsum()))
            .reset_index(0, drop=True)
        )
        
        result_df['away_win_streak'] = (
            result_df.groupby('away_team_id')['away_win']
            .apply(lambda x: x * (x.groupby((x != x.shift()).cumsum()).cumsum()))
            .reset_index(0, drop=True)
        )
        
        # Sequência de empates
        result_df['home_draw_streak'] = (
            result_df.groupby('home_team_id')['draw']
            .apply(lambda x: x * (x.groupby((x != x.shift()).cumsum()).cumsum()))
            .reset_index(0, drop=True)
        )
        
        result_df['away_draw_streak'] = (
            result_df.groupby('away_team_id')['draw']
            .apply(lambda x: x * (x.groupby((x != x.shift()).cumsum()).cumsum()))
            .reset_index(0, drop=True)
        )
        
        return result_df
    
    def create_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features avançadas"""
        logger.info("🚀 Criando features avançadas...")
        
        result_df = df.copy()
        
        # Força relativa dos times
        result_df['home_strength'] = (
            result_df['home_goals_avg'] / result_df['league_home_goals_avg']
        )
        
        result_df['away_strength'] = (
            result_df['away_goals_avg'] / result_df['league_away_goals_avg']
        )
        
        # Diferença de força
        result_df['strength_diff'] = result_df['home_strength'] - result_df['away_strength']
        
        # Expectativa de gols
        result_df['expected_home_goals'] = (
            result_df['home_strength'] * result_df['away_strength'] * result_df['league_home_goals_avg']
        )
        
        result_df['expected_away_goals'] = (
            result_df['away_strength'] * result_df['home_strength'] * result_df['league_away_goals_avg']
        )
        
        # Probabilidade de over/under
        result_df['over_2_5_prob'] = 1 - (
            np.exp(-result_df['expected_home_goals']) * 
            np.exp(-result_df['expected_away_goals'])
        )
        
        # Probabilidade de ambos marcarem
        result_df['btts_prob'] = (
            1 - (1 - result_df['expected_home_goals']) * (1 - result_df['expected_away_goals'])
        )
        
        return result_df
    
    def create_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria todas as features"""
        logger.info("🔧 Criando todas as features...")
        
        # Aplicar todas as transformações
        result_df = self.create_form_features(df, 'home_team_id', 'home_score')
        result_df = self.create_form_features(result_df, 'away_team_id', 'away_score')
        result_df = self.create_goals_features(result_df)
        result_df = self.create_h2h_features(result_df)
        result_df = self.create_odds_features(result_df)
        result_df = self.create_temporal_features(result_df)
        result_df = self.create_league_features(result_df)
        result_df = self.create_momentum_features(result_df)
        result_df = self.create_advanced_features(result_df)
        
        # Preencher valores faltantes
        result_df = result_df.fillna(0)
        
        logger.info(f"✅ Features criadas: {len(result_df.columns)} colunas")
        return result_df
    
    def get_feature_importance(self, model, feature_names: List[str]) -> Dict[str, float]:
        """Calcula importância das features"""
        if hasattr(model, 'feature_importances_'):
            return dict(zip(feature_names, model.feature_importances_))
        elif hasattr(model, 'coef_'):
            return dict(zip(feature_names, abs(model.coef_[0])))
        else:
            return {}

def main():
    """Função principal para teste"""
    print("🔧 MARABET AI - FEATURE ENGINEERING")
    print("=" * 50)
    
    # Criar dados de exemplo
    np.random.seed(42)
    n_matches = 1000
    
    data = {
        'home_team_id': np.random.randint(1, 21, n_matches),
        'away_team_id': np.random.randint(1, 21, n_matches),
        'home_score': np.random.poisson(1.5, n_matches),
        'away_score': np.random.poisson(1.2, n_matches),
        'home_odd': np.random.uniform(1.5, 4.0, n_matches),
        'draw_odd': np.random.uniform(2.8, 4.5, n_matches),
        'away_odd': np.random.uniform(1.5, 4.0, n_matches),
        'league_id': np.random.randint(1, 6, n_matches),
        'date': pd.date_range('2023-01-01', periods=n_matches, freq='D')
    }
    
    df = pd.DataFrame(data)
    
    # Calcular resultados
    df['home_win'] = (df['home_score'] > df['away_score']).astype(int)
    df['draw'] = (df['home_score'] == df['away_score']).astype(int)
    df['away_win'] = (df['home_score'] < df['away_score']).astype(int)
    
    print(f"📊 Dados originais: {len(df.columns)} colunas")
    
    # Criar features
    engineer = FeatureEngineer()
    features_df = engineer.create_all_features(df)
    
    print(f"✅ Dados com features: {len(features_df.columns)} colunas")
    print(f"📈 Features criadas: {len(features_df.columns) - len(df.columns)}")
    
    # Mostrar algumas features
    print("\n🔍 Exemplos de features criadas:")
    new_features = [col for col in features_df.columns if col not in df.columns]
    for feature in new_features[:10]:
        print(f"  - {feature}")
    
    print("\n🎉 Feature engineering concluído!")

if __name__ == "__main__":
    main()
