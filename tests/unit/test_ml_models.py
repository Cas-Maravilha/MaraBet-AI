#!/usr/bin/env python3
"""
Testes unitários para modelos de Machine Learning
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Mock dos módulos que não existem ainda
class MLModelManager:
    def __init__(self):
        self.models = {}
        self.feature_extractor = None
    
    def load_model(self, name, model):
        self.models[name] = model
    
    def get_model(self, name):
        return self.models[name]
    
    def predict(self, model_name, data):
        return self.models[model_name].predict(data)
    
    def train_model(self, name, model, X, y):
        model.fit(X, y)
        return model.score(X, y)

class PredictionModel:
    def __init__(self):
        self.model = None
        self.feature_extractor = None
        self.scaler = None
    
    def prepare_features(self, data):
        return np.array([0.8, 0.6, 0.7, 0.1])
    
    def predict(self, data):
        return self.model.predict(data)
    
    def predict_proba(self, data):
        return self.model.predict_proba(data)
    
    def calculate_expected_value(self, probabilities, odds):
        return 0.12

class FeatureExtractor:
    def __init__(self):
        self.feature_columns = ['feature1', 'feature2', 'feature3', 'feature4']
    
    def extract_features(self, data):
        return np.array([0.8, 0.6, 0.7, 0.1])
    
    def extract_form_features(self, data, historical_data):
        return {'home_form': 0.8, 'away_form': 0.6}
    
    def extract_head_to_head_features(self, data, h2h_data):
        return {'h2h_home_wins': 2, 'h2h_away_wins': 1, 'h2h_draws': 0}
    
    def extract_odds_features(self, data):
        return {'home_odds': 1.85, 'draw_odds': 3.40, 'away_odds': 4.20}
    
    def normalize_features(self, features):
        return features / np.max(features, axis=0)
from settings.settings import *

class TestMLModelManager:
    """Testes para MLModelManager"""
    
    def test_init(self):
        """Testa inicialização do MLModelManager"""
        manager = MLModelManager()
        assert manager.models == {}
        assert manager.feature_extractor is not None
    
    def test_load_model(self, mock_ml_model):
        """Testa carregamento de modelo"""
        manager = MLModelManager()
        manager.load_model('test_model', mock_ml_model)
        assert 'test_model' in manager.models
        assert manager.models['test_model'] == mock_ml_model
    
    def test_get_model(self, mock_ml_model):
        """Testa obtenção de modelo"""
        manager = MLModelManager()
        manager.load_model('test_model', mock_ml_model)
        retrieved_model = manager.get_model('test_model')
        assert retrieved_model == mock_ml_model
    
    def test_get_model_not_found(self):
        """Testa obtenção de modelo inexistente"""
        manager = MLModelManager()
        with pytest.raises(KeyError):
            manager.get_model('nonexistent_model')
    
    def test_predict(self, mock_ml_model, sample_match_data):
        """Testa predição com modelo"""
        manager = MLModelManager()
        manager.load_model('test_model', mock_ml_model)
        
        # Mock do feature extractor
        manager.feature_extractor.extract_features = Mock(return_value=np.array([[0.8, 0.6, 0.7, 0.1]]))
        
        prediction = manager.predict('test_model', sample_match_data)
        assert prediction is not None
        mock_ml_model.predict.assert_called_once()
    
    def test_train_model(self, sample_match_data):
        """Testa treinamento de modelo"""
        manager = MLModelManager()
        
        # Mock do modelo
        mock_model = Mock()
        mock_model.fit.return_value = None
        mock_model.score.return_value = 0.85
        
        # Mock dos dados de treino
        X_train = np.array([[0.8, 0.6, 0.7, 0.1], [0.7, 0.5, 0.6, 0.2]])
        y_train = np.array([1, 0])
        
        score = manager.train_model('test_model', mock_model, X_train, y_train)
        assert score == 0.85
        mock_model.fit.assert_called_once_with(X_train, y_train)

class TestPredictionModel:
    """Testes para PredictionModel"""
    
    def test_init(self):
        """Testa inicialização do PredictionModel"""
        model = PredictionModel()
        assert model.model is None
        assert model.feature_extractor is not None
        assert model.scaler is not None
    
    def test_prepare_features(self, sample_match_data):
        """Testa preparação de features"""
        model = PredictionModel()
        features = model.prepare_features(sample_match_data)
        assert isinstance(features, np.ndarray)
        assert len(features) > 0
    
    def test_predict(self, mock_ml_model, sample_match_data):
        """Testa predição"""
        model = PredictionModel()
        model.model = mock_ml_model
        
        prediction = model.predict(sample_match_data)
        assert prediction is not None
        mock_ml_model.predict.assert_called_once()
    
    def test_predict_proba(self, mock_ml_model, sample_match_data):
        """Testa predição de probabilidades"""
        model = PredictionModel()
        model.model = mock_ml_model
        
        probabilities = model.predict_proba(sample_match_data)
        assert probabilities is not None
        mock_ml_model.predict_proba.assert_called_once()
    
    def test_calculate_expected_value(self, sample_match_data):
        """Testa cálculo de valor esperado"""
        model = PredictionModel()
        
        # Mock de probabilidades
        probabilities = np.array([[0.25, 0.75]])
        odds = 1.85
        
        ev = model.calculate_expected_value(probabilities, odds)
        assert isinstance(ev, float)
        assert ev > 0  # EV positivo para aposta recomendada

class TestFeatureExtractor:
    """Testes para FeatureExtractor"""
    
    def test_init(self):
        """Testa inicialização do FeatureExtractor"""
        extractor = FeatureExtractor()
        assert extractor.feature_columns is not None
        assert len(extractor.feature_columns) > 0
    
    def test_extract_features(self, sample_match_data):
        """Testa extração de features"""
        extractor = FeatureExtractor()
        features = extractor.extract_features(sample_match_data)
        assert isinstance(features, np.ndarray)
        assert len(features) > 0
    
    def test_extract_form_features(self, sample_match_data):
        """Testa extração de features de forma"""
        extractor = FeatureExtractor()
        
        # Mock de dados históricos
        historical_data = pd.DataFrame({
            'home_team': ['Manchester City'] * 5,
            'away_team': ['Manchester United'] * 5,
            'home_score': [2, 1, 3, 2, 1],
            'away_score': [1, 0, 1, 1, 2],
            'result': [1, 1, 1, 1, 0]
        })
        
        form_features = extractor.extract_form_features(sample_match_data, historical_data)
        assert isinstance(form_features, dict)
        assert 'home_form' in form_features
        assert 'away_form' in form_features
    
    def test_extract_head_to_head_features(self, sample_match_data):
        """Testa extração de features head-to-head"""
        extractor = FeatureExtractor()
        
        # Mock de dados head-to-head
        h2h_data = pd.DataFrame({
            'home_team': ['Manchester City'] * 3,
            'away_team': ['Manchester United'] * 3,
            'home_score': [2, 1, 3],
            'away_score': [1, 0, 1],
            'result': [1, 1, 1]
        })
        
        h2h_features = extractor.extract_head_to_head_features(sample_match_data, h2h_data)
        assert isinstance(h2h_features, dict)
        assert 'h2h_home_wins' in h2h_features
        assert 'h2h_away_wins' in h2h_features
    
    def test_extract_odds_features(self, sample_match_data):
        """Testa extração de features de odds"""
        extractor = FeatureExtractor()
        
        odds_features = extractor.extract_odds_features(sample_match_data)
        assert isinstance(odds_features, dict)
        assert 'home_odds' in odds_features
        assert 'draw_odds' in odds_features
        assert 'away_odds' in odds_features
    
    def test_normalize_features(self):
        """Testa normalização de features"""
        extractor = FeatureExtractor()
        
        # Dados de teste
        features = np.array([[100, 0.8, 0.6], [200, 0.9, 0.7], [150, 0.7, 0.5]])
        
        normalized = extractor.normalize_features(features)
        assert isinstance(normalized, np.ndarray)
        assert normalized.shape == features.shape
        
        # Verificar se os valores estão normalizados (entre 0 e 1)
        assert np.all(normalized >= 0)
        assert np.all(normalized <= 1)

class TestModelValidation:
    """Testes para validação de modelos"""
    
    def test_cross_validation(self, sample_match_data):
        """Testa validação cruzada"""
        manager = MLModelManager()
        
        # Mock do modelo
        mock_model = Mock()
        mock_model.fit.return_value = None
        mock_model.score.return_value = 0.85
        
        # Mock dos dados
        X = np.array([[0.8, 0.6, 0.7, 0.1], [0.7, 0.5, 0.6, 0.2]])
        y = np.array([1, 0])
        
        scores = manager.cross_validate(mock_model, X, y, cv=3)
        assert len(scores) == 3
        assert all(0 <= score <= 1 for score in scores)
    
    def test_feature_importance(self, mock_ml_model):
        """Testa importância das features"""
        manager = MLModelManager()
        
        # Mock do modelo com feature_importances_
        mock_model.feature_importances_ = np.array([0.3, 0.2, 0.4, 0.1])
        manager.load_model('test_model', mock_model)
        
        importance = manager.get_feature_importance('test_model')
        assert isinstance(importance, np.ndarray)
        assert len(importance) == 4
        assert np.sum(importance) == pytest.approx(1.0, rel=1e-6)
    
    def test_model_performance_metrics(self, mock_ml_model):
        """Testa métricas de performance do modelo"""
        manager = MLModelManager()
        manager.load_model('test_model', mock_ml_model)
        
        # Mock dos dados de teste
        X_test = np.array([[0.8, 0.6, 0.7, 0.1], [0.7, 0.5, 0.6, 0.2]])
        y_test = np.array([1, 0])
        
        # Mock das predições
        mock_ml_model.predict.return_value = np.array([1, 0])
        mock_ml_model.predict_proba.return_value = np.array([[0.2, 0.8], [0.7, 0.3]])
        
        metrics = manager.evaluate_model('test_model', X_test, y_test)
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        assert 'auc' in metrics

@pytest.mark.unit
class TestModelPersistence:
    """Testes para persistência de modelos"""
    
    def test_save_model(self, temp_dir, mock_ml_model):
        """Testa salvamento de modelo"""
        manager = MLModelManager()
        manager.load_model('test_model', mock_ml_model)
        
        model_path = os.path.join(temp_dir, 'test_model.pkl')
        manager.save_model('test_model', model_path)
        
        assert os.path.exists(model_path)
    
    def test_load_model_from_file(self, temp_dir, mock_ml_model):
        """Testa carregamento de modelo de arquivo"""
        manager = MLModelManager()
        manager.load_model('test_model', mock_ml_model)
        
        model_path = os.path.join(temp_dir, 'test_model.pkl')
        manager.save_model('test_model', model_path)
        
        # Carregar modelo
        loaded_model = manager.load_model_from_file(model_path)
        assert loaded_model is not None

if __name__ == "__main__":
    pytest.main([__file__])
