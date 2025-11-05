#!/usr/bin/env python3
"""
Sistema de Feature Engineering Simplificado para previsões esportivas
MaraBet AI - Sistema de Apostas Esportivas Inteligentes
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class SimpleFeatureEngineer:
    """Classe simplificada para criação de features"""
    
    def __init__(self):
        self.feature_cache = {}
        self.team_stats = {}
        self.league_stats = {}
    
    def create_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features básicas"""
        logger.info("🔧 Criando features básicas...")
        
        result_df = df.copy()
        
        # Features de gols
        result_df['total_goals'] = result_df['home_score'] + result_df['away_score']
        result_df['goal_difference'] = result_df['home_score'] - result_df['away_score']
        
        # Features de odds
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
        
        # Features temporais
        result_df['date'] = pd.to_datetime(result_df['date'])
        result_df['day_of_week'] = result_df['date'].dt.dayofweek
        result_df['month'] = result_df['date'].dt.month
        result_df['is_weekend'] = result_df['day_of_week'].isin([5, 6]).astype(int)
        
        return result_df
    
    def create_form_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features de forma dos times"""
        logger.info("📈 Criando features de forma...")
        
        result_df = df.copy()
        
        # Forma em casa (últimos 5 jogos)
        home_form = []
        for team_id in result_df['home_team_id'].unique():
            team_matches = result_df[result_df['home_team_id'] == team_id].sort_values('date')
            team_form = team_matches['home_score'].rolling(5, min_periods=1).mean()
            home_form.extend(team_form.values)
        
        result_df['home_form_5'] = home_form
        
        # Forma fora (últimos 5 jogos)
        away_form = []
        for team_id in result_df['away_team_id'].unique():
            team_matches = result_df[result_df['away_team_id'] == team_id].sort_values('date')
            team_form = team_matches['away_score'].rolling(5, min_periods=1).mean()
            away_form.extend(team_matches['away_score'].rolling(5, min_periods=1).mean().values)
        
        result_df['away_form_5'] = away_form
        
        return result_df
    
    def create_goals_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features de gols"""
        logger.info("⚽ Criando features de gols...")
        
        result_df = df.copy()
        
        # Médias de gols por time
        home_goals_avg = []
        away_goals_avg = []
        
        for team_id in result_df['home_team_id'].unique():
            team_matches = result_df[result_df['home_team_id'] == team_id].sort_values('date')
            team_avg = team_matches['home_score'].expanding().mean()
            home_goals_avg.extend(team_avg.values)
        
        for team_id in result_df['away_team_id'].unique():
            team_matches = result_df[result_df['away_team_id'] == team_id].sort_values('date')
            team_avg = team_matches['away_score'].expanding().mean()
            away_goals_avg.extend(team_matches['away_score'].expanding().mean().values)
        
        result_df['home_goals_avg'] = home_goals_avg
        result_df['away_goals_avg'] = away_goals_avg
        
        return result_df
    
    def create_league_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features da liga"""
        logger.info("🏆 Criando features da liga...")
        
        result_df = df.copy()
        
        # Média de gols da liga
        league_goals_avg = []
        for league_id in result_df['league_id'].unique():
            league_matches = result_df[result_df['league_id'] == league_id].sort_values('date')
            league_avg = league_matches['total_goals'].expanding().mean()
            league_goals_avg.extend(league_avg.values)
        
        result_df['league_goals_avg'] = league_goals_avg
        
        return result_df
    
    def create_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cria features avançadas"""
        logger.info("🚀 Criando features avançadas...")
        
        result_df = df.copy()
        
        # Força relativa dos times
        result_df['home_strength'] = result_df['home_goals_avg'] / result_df['league_goals_avg']
        result_df['away_strength'] = result_df['away_goals_avg'] / result_df['league_goals_avg']
        
        # Diferença de força
        result_df['strength_diff'] = result_df['home_strength'] - result_df['away_strength']
        
        # Expectativa de gols
        result_df['expected_home_goals'] = (
            result_df['home_strength'] * result_df['away_strength'] * result_df['league_goals_avg']
        )
        
        result_df['expected_away_goals'] = (
            result_df['away_strength'] * result_df['home_strength'] * result_df['league_goals_avg']
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
        result_df = self.create_basic_features(df)
        result_df = self.create_form_features(result_df)
        result_df = self.create_goals_features(result_df)
        result_df = self.create_league_features(result_df)
        result_df = self.create_advanced_features(result_df)
        
        # Preencher valores faltantes
        result_df = result_df.fillna(0)
        
        logger.info(f"✅ Features criadas: {len(result_df.columns)} colunas")
        return result_df

def main():
    """Função principal para teste"""
    print("🔧 MARABET AI - SIMPLE FEATURE ENGINEERING")
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
    engineer = SimpleFeatureEngineer()
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
