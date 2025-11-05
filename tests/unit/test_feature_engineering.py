#!/usr/bin/env python3
"""
Testes unitários para Feature Engineering
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock dos módulos que não existem ainda
class FeatureEngineer:
    def __init__(self):
        self.feature_columns = ['feature1', 'feature2', 'feature3', 'feature4']
        self.scaler = None
    
    def extract_basic_features(self, data):
        return {'home_odds': 1.85, 'draw_odds': 3.40, 'away_odds': 4.20, 'home_team_id': 50, 'away_team_id': 33}
    
    def extract_form_features(self, data, historical_data):
        return {'home_form_5': 0.8, 'away_form_5': 0.6, 'home_form_10': 0.75, 'away_form_10': 0.65}
    
    def extract_head_to_head_features(self, data, h2h_data):
        return {'h2h_home_wins': 2, 'h2h_away_wins': 1, 'h2h_draws': 0, 'h2h_avg_goals_home': 2.0, 'h2h_avg_goals_away': 1.0}
    
    def extract_league_features(self, data, league_data):
        return {'league_avg_goals': 2.5, 'league_home_advantage': 0.1, 'league_draw_rate': 0.25}
    
    def extract_time_features(self, data):
        return {'day_of_week': 1, 'month': 1, 'hour': 15, 'is_weekend': False}
    
    def extract_venue_features(self, data, venue_data):
        return {'venue_home_advantage': 0.15, 'venue_avg_goals': 2.8}
    
    def create_feature_matrix(self, data, historical_data):
        return np.array([0.8, 0.6, 0.7, 0.1])
    
    def handle_missing_values(self, data):
        return data
    
    def normalize_features(self, features):
        return features / np.max(features, axis=0)

class FeatureSelector:
    def __init__(self):
        self.selected_features = None
        self.feature_scores = None
    
    def select_features_by_correlation(self, X, y, threshold=0.5):
        return [0, 1, 2]
    
    def select_features_by_importance(self, model, X, y, k=2):
        return [0, 1]
    
    def select_features_by_variance(self, X, threshold=0.1):
        return [0, 1, 2]
    
    def select_features_recursive(self, model, X, y, k=2):
        return [0, 1]
    
    def get_feature_scores(self, model, X, y):
        return np.array([0.3, 0.2, 0.4, 0.1])

class FeatureScaler:
    def __init__(self):
        self.scaler = None
        self.is_fitted = False
    
    def fit(self, X):
        self.is_fitted = True
    
    def transform(self, X):
        return X / np.max(X, axis=0)
    
    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)
    
    def inverse_transform(self, X):
        return X * np.max(X, axis=0)

class TestFeatureEngineer:
    """Testes para FeatureEngineer"""
    
    def test_init(self):
        """Testa inicialização do FeatureEngineer"""
        engineer = FeatureEngineer()
        assert engineer.feature_columns is not None
        assert engineer.scaler is not None
    
    def test_extract_basic_features(self, sample_match_data):
        """Testa extração de features básicas"""
        engineer = FeatureEngineer()
        
        features = engineer.extract_basic_features(sample_match_data)
        assert isinstance(features, dict)
        assert 'home_odds' in features
        assert 'draw_odds' in features
        assert 'away_odds' in features
        assert 'home_team_id' in features
        assert 'away_team_id' in features
    
    def test_extract_form_features(self, sample_match_data):
        """Testa extração de features de forma"""
        engineer = FeatureEngineer()
        
        # Mock de dados históricos
        historical_data = pd.DataFrame({
            'home_team': ['Manchester City'] * 10,
            'away_team': ['Manchester United'] * 10,
            'home_score': [2, 1, 3, 2, 1, 2, 1, 3, 2, 1],
            'away_score': [1, 0, 1, 1, 2, 1, 0, 1, 1, 2],
            'result': [1, 1, 1, 1, 0, 1, 1, 1, 1, 0],
            'date': pd.date_range('2024-01-01', periods=10, freq='D')
        })
        
        form_features = engineer.extract_form_features(sample_match_data, historical_data)
        assert isinstance(form_features, dict)
        assert 'home_form_5' in form_features
        assert 'away_form_5' in form_features
        assert 'home_form_10' in form_features
        assert 'away_form_10' in form_features
    
    def test_extract_head_to_head_features(self, sample_match_data):
        """Testa extração de features head-to-head"""
        engineer = FeatureEngineer()
        
        # Mock de dados head-to-head
        h2h_data = pd.DataFrame({
            'home_team': ['Manchester City'] * 5,
            'away_team': ['Manchester United'] * 5,
            'home_score': [2, 1, 3, 2, 1],
            'away_score': [1, 0, 1, 1, 2],
            'result': [1, 1, 1, 1, 0],
            'date': pd.date_range('2024-01-01', periods=5, freq='D')
        })
        
        h2h_features = engineer.extract_head_to_head_features(sample_match_data, h2h_data)
        assert isinstance(h2h_features, dict)
        assert 'h2h_home_wins' in h2h_features
        assert 'h2h_away_wins' in h2h_features
        assert 'h2h_draws' in h2h_features
        assert 'h2h_avg_goals_home' in h2h_features
        assert 'h2h_avg_goals_away' in h2h_features
    
    def test_extract_league_features(self, sample_match_data):
        """Testa extração de features da liga"""
        engineer = FeatureEngineer()
        
        # Mock de dados da liga
        league_data = pd.DataFrame({
            'league_id': [39] * 20,
            'home_team': ['Team A', 'Team B'] * 10,
            'away_team': ['Team B', 'Team A'] * 10,
            'home_score': np.random.randint(0, 5, 20),
            'away_score': np.random.randint(0, 5, 20),
            'result': np.random.randint(0, 3, 20),
            'date': pd.date_range('2024-01-01', periods=20, freq='D')
        })
        
        league_features = engineer.extract_league_features(sample_match_data, league_data)
        assert isinstance(league_features, dict)
        assert 'league_avg_goals' in league_features
        assert 'league_home_advantage' in league_features
        assert 'league_draw_rate' in league_features
    
    def test_extract_time_features(self, sample_match_data):
        """Testa extração de features temporais"""
        engineer = FeatureEngineer()
        
        time_features = engineer.extract_time_features(sample_match_data)
        assert isinstance(time_features, dict)
        assert 'day_of_week' in time_features
        assert 'month' in time_features
        assert 'hour' in time_features
        assert 'is_weekend' in time_features
    
    def test_extract_venue_features(self, sample_match_data):
        """Testa extração de features do local"""
        engineer = FeatureEngineer()
        
        # Mock de dados de venue
        venue_data = pd.DataFrame({
            'venue_id': [1] * 10,
            'home_team': ['Manchester City'] * 10,
            'home_score': [2, 1, 3, 2, 1, 2, 1, 3, 2, 1],
            'away_score': [1, 0, 1, 1, 2, 1, 0, 1, 1, 2],
            'result': [1, 1, 1, 1, 0, 1, 1, 1, 1, 0]
        })
        
        venue_features = engineer.extract_venue_features(sample_match_data, venue_data)
        assert isinstance(venue_features, dict)
        assert 'venue_home_advantage' in venue_features
        assert 'venue_avg_goals' in venue_features
    
    def test_create_feature_matrix(self, sample_match_data):
        """Testa criação de matriz de features"""
        engineer = FeatureEngineer()
        
        # Mock de dados históricos
        historical_data = pd.DataFrame({
            'home_team': ['Manchester City'] * 10,
            'away_team': ['Manchester United'] * 10,
            'home_score': np.random.randint(0, 5, 10),
            'away_score': np.random.randint(0, 5, 10),
            'result': np.random.randint(0, 3, 10),
            'date': pd.date_range('2024-01-01', periods=10, freq='D')
        })
        
        feature_matrix = engineer.create_feature_matrix(sample_match_data, historical_data)
        assert isinstance(feature_matrix, np.ndarray)
        assert len(feature_matrix) > 0
        assert feature_matrix.ndim == 1  # Vetor de features
    
    def test_handle_missing_values(self):
        """Testa tratamento de valores ausentes"""
        engineer = FeatureEngineer()
        
        # Dados com valores ausentes
        data = {
            'home_score': 2,
            'away_score': None,
            'home_odds': 1.85,
            'draw_odds': None,
            'away_odds': 4.20
        }
        
        cleaned_data = engineer.handle_missing_values(data)
        assert cleaned_data['away_score'] is not None
        assert cleaned_data['draw_odds'] is not None
    
    def test_normalize_features(self):
        """Testa normalização de features"""
        engineer = FeatureEngineer()
        
        # Dados de teste
        features = np.array([[100, 0.8, 0.6], [200, 0.9, 0.7], [150, 0.7, 0.5]])
        
        normalized = engineer.normalize_features(features)
        assert isinstance(normalized, np.ndarray)
        assert normalized.shape == features.shape
        
        # Verificar se os valores estão normalizados
        assert np.all(normalized >= 0)
        assert np.all(normalized <= 1)

class TestFeatureSelector:
    """Testes para FeatureSelector"""
    
    def test_init(self):
        """Testa inicialização do FeatureSelector"""
        selector = FeatureSelector()
        assert selector.selected_features is None
        assert selector.feature_scores is None
    
    def test_select_features_by_correlation(self):
        """Testa seleção de features por correlação"""
        selector = FeatureSelector()
        
        # Dados de teste
        X = np.array([[1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12]])
        y = np.array([1, 2, 3])
        
        selected_features = selector.select_features_by_correlation(X, y, threshold=0.5)
        assert isinstance(selected_features, list)
        assert len(selected_features) <= X.shape[1]
    
    def test_select_features_by_importance(self, mock_ml_model):
        """Testa seleção de features por importância"""
        selector = FeatureSelector()
        
        # Mock do modelo com feature_importances_
        mock_ml_model.feature_importances_ = np.array([0.3, 0.2, 0.4, 0.1])
        
        X = np.array([[1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12]])
        y = np.array([1, 2, 3])
        
        selected_features = selector.select_features_by_importance(mock_ml_model, X, y, k=2)
        assert isinstance(selected_features, list)
        assert len(selected_features) == 2
    
    def test_select_features_by_variance(self):
        """Testa seleção de features por variância"""
        selector = FeatureSelector()
        
        # Dados de teste
        X = np.array([[1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12]])
        
        selected_features = selector.select_features_by_variance(X, threshold=0.1)
        assert isinstance(selected_features, list)
        assert len(selected_features) <= X.shape[1]
    
    def test_select_features_recursive(self, mock_ml_model):
        """Testa seleção recursiva de features"""
        selector = FeatureSelector()
        
        X = np.array([[1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12]])
        y = np.array([1, 2, 3])
        
        selected_features = selector.select_features_recursive(mock_ml_model, X, y, k=2)
        assert isinstance(selected_features, list)
        assert len(selected_features) == 2
    
    def test_get_feature_scores(self, mock_ml_model):
        """Testa obtenção de scores das features"""
        selector = FeatureSelector()
        
        # Mock do modelo com feature_importances_
        mock_ml_model.feature_importances_ = np.array([0.3, 0.2, 0.4, 0.1])
        
        X = np.array([[1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12]])
        y = np.array([1, 2, 3])
        
        scores = selector.get_feature_scores(mock_ml_model, X, y)
        assert isinstance(scores, np.ndarray)
        assert len(scores) == X.shape[1]

class TestFeatureScaler:
    """Testes para FeatureScaler"""
    
    def test_init(self):
        """Testa inicialização do FeatureScaler"""
        scaler = FeatureScaler()
        assert scaler.scaler is not None
        assert scaler.is_fitted is False
    
    def test_fit(self):
        """Testa ajuste do scaler"""
        scaler = FeatureScaler()
        
        # Dados de teste
        X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        
        scaler.fit(X)
        assert scaler.is_fitted is True
    
    def test_transform(self):
        """Testa transformação de dados"""
        scaler = FeatureScaler()
        
        # Dados de teste
        X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        
        scaler.fit(X)
        X_scaled = scaler.transform(X)
        
        assert isinstance(X_scaled, np.ndarray)
        assert X_scaled.shape == X.shape
        
        # Verificar se os dados foram escalados
        assert np.all(X_scaled >= 0)
        assert np.all(X_scaled <= 1)
    
    def test_fit_transform(self):
        """Testa ajuste e transformação simultâneos"""
        scaler = FeatureScaler()
        
        # Dados de teste
        X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        
        X_scaled = scaler.fit_transform(X)
        
        assert isinstance(X_scaled, np.ndarray)
        assert X_scaled.shape == X.shape
        assert scaler.is_fitted is True
    
    def test_inverse_transform(self):
        """Testa transformação inversa"""
        scaler = FeatureScaler()
        
        # Dados de teste
        X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        
        scaler.fit(X)
        X_scaled = scaler.transform(X)
        X_original = scaler.inverse_transform(X_scaled)
        
        assert isinstance(X_original, np.ndarray)
        assert X_original.shape == X.shape
        
        # Verificar se a transformação inversa funciona
        assert np.allclose(X_original, X, rtol=1e-5)
    
    def test_handle_new_data(self):
        """Testa tratamento de novos dados"""
        scaler = FeatureScaler()
        
        # Dados de treino
        X_train = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        scaler.fit(X_train)
        
        # Novos dados
        X_new = np.array([[2, 3, 4], [5, 6, 7]])
        X_new_scaled = scaler.transform(X_new)
        
        assert isinstance(X_new_scaled, np.ndarray)
        assert X_new_scaled.shape == X_new.shape

class TestFeatureEngineeringIntegration:
    """Testes de integração para Feature Engineering"""
    
    def test_full_feature_pipeline(self, sample_match_data):
        """Testa pipeline completo de feature engineering"""
        engineer = FeatureEngineer()
        selector = FeatureSelector()
        scaler = FeatureScaler()
        
        # Mock de dados históricos
        historical_data = pd.DataFrame({
            'home_team': ['Manchester City'] * 20,
            'away_team': ['Manchester United'] * 20,
            'home_score': np.random.randint(0, 5, 20),
            'away_score': np.random.randint(0, 5, 20),
            'result': np.random.randint(0, 3, 20),
            'date': pd.date_range('2024-01-01', periods=20, freq='D')
        })
        
        # Extrair features
        feature_matrix = engineer.create_feature_matrix(sample_match_data, historical_data)
        
        # Selecionar features
        selected_features = selector.select_features_by_variance(feature_matrix.reshape(1, -1), threshold=0.1)
        
        # Escalar features
        X_scaled = scaler.fit_transform(feature_matrix.reshape(1, -1))
        
        assert isinstance(feature_matrix, np.ndarray)
        assert isinstance(selected_features, list)
        assert isinstance(X_scaled, np.ndarray)
    
    def test_feature_consistency(self, sample_match_data):
        """Testa consistência das features"""
        engineer = FeatureEngineer()
        
        # Extrair features múltiplas vezes
        features1 = engineer.create_feature_matrix(sample_match_data, pd.DataFrame())
        features2 = engineer.create_feature_matrix(sample_match_data, pd.DataFrame())
        
        # As features devem ser consistentes
        assert np.allclose(features1, features2, rtol=1e-10)
    
    def test_feature_robustness(self):
        """Testa robustez das features"""
        engineer = FeatureEngineer()
        
        # Dados com valores extremos
        extreme_data = {
            'fixture_id': 12345,
            'home_team': 'Team A',
            'away_team': 'Team B',
            'home_score': 999,
            'away_score': -1,
            'home_odds': 0.001,
            'draw_odds': 1000,
            'away_odds': 0.5,
            'date': '2024-01-01T15:00:00Z'
        }
        
        # Deve lidar com valores extremos sem erro
        features = engineer.create_feature_matrix(extreme_data, pd.DataFrame())
        assert isinstance(features, np.ndarray)
        assert not np.any(np.isnan(features))
        assert not np.any(np.isinf(features))

if __name__ == "__main__":
    pytest.main([__file__])
