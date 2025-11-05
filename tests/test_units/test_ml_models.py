"""
Testes unitários para modelos de Machine Learning
Testa lógica de ML, treinamento, predição e avaliação
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from ml.ml_models import MLModelManager, RandomForestModel, XGBoostModel, LightGBMModel, CatBoostModel, LogisticRegressionModel, BayesianNeuralNetworkModel, PoissonModel
from probability_calculator import ProbabilityCalculator
from value_identification import ValueIdentifier

class TestMLModelManager:
    """Testes para MLModelManager"""
    
    def test_init(self):
        """Testa inicialização do MLModelManager"""
        manager = MLModelManager()
        assert manager is not None
        assert hasattr(manager, 'models')
        assert hasattr(manager, 'trained_models')
    
    def test_create_model_random_forest(self):
        """Testa criação de modelo Random Forest"""
        manager = MLModelManager()
        model = manager.create_model('random_forest')
        assert isinstance(model, RandomForestModel)
        assert model.model_type == 'random_forest'
    
    def test_create_model_xgboost(self):
        """Testa criação de modelo XGBoost"""
        manager = MLModelManager()
        model = manager.create_model('xgboost')
        assert isinstance(model, XGBoostModel)
        assert model.model_type == 'xgboost'
    
    def test_create_model_lightgbm(self):
        """Testa criação de modelo LightGBM"""
        manager = MLModelManager()
        model = manager.create_model('lightgbm')
        assert isinstance(model, LightGBMModel)
        assert model.model_type == 'lightgbm'
    
    def test_create_model_catboost(self):
        """Testa criação de modelo CatBoost"""
        manager = MLModelManager()
        model = manager.create_model('catboost')
        assert isinstance(model, CatBoostModel)
        assert model.model_type == 'catboost'
    
    def test_create_model_logistic_regression(self):
        """Testa criação de modelo Logistic Regression"""
        manager = MLModelManager()
        model = manager.create_model('logistic_regression')
        assert isinstance(model, LogisticRegressionModel)
        assert model.model_type == 'logistic_regression'
    
    def test_create_model_bayesian_neural_network(self):
        """Testa criação de modelo Bayesian Neural Network"""
        manager = MLModelManager()
        model = manager.create_model('bayesian_neural_network')
        assert isinstance(model, BayesianNeuralNetworkModel)
        assert model.model_type == 'bayesian_neural_network'
    
    def test_create_model_poisson(self):
        """Testa criação de modelo Poisson"""
        manager = MLModelManager()
        model = manager.create_model('poisson')
        assert isinstance(model, PoissonModel)
        assert model.model_type == 'poisson'
    
    def test_create_model_invalid(self):
        """Testa criação de modelo inválido"""
        manager = MLModelManager()
        with pytest.raises(ValueError):
            manager.create_model('invalid_model')
    
    def test_train_model(self, sample_ml_data):
        """Testa treinamento de modelo"""
        manager = MLModelManager()
        model = manager.create_model('random_forest')
        
        # Mock do método fit
        model.fit = Mock()
        model.fit.return_value = None
        
        result = manager.train_model(model, sample_ml_data['X_train'], sample_ml_data['y_train'])
        
        assert result is not None
        model.fit.assert_called_once_with(sample_ml_data['X_train'], sample_ml_data['y_train'])
    
    def test_predict(self, sample_ml_data):
        """Testa predição com modelo"""
        manager = MLModelManager()
        model = manager.create_model('random_forest')
        
        # Mock do método predict
        model.predict = Mock()
        model.predict.return_value = np.array([0, 1, 2])
        
        predictions = manager.predict(model, sample_ml_data['X_test'])
        
        assert predictions is not None
        assert len(predictions) == len(sample_ml_data['X_test'])
        model.predict.assert_called_once_with(sample_ml_data['X_test'])
    
    def test_evaluate_model(self, sample_ml_data):
        """Testa avaliação de modelo"""
        manager = MLModelManager()
        model = manager.create_model('random_forest')
        
        # Mock dos métodos predict e score
        model.predict = Mock()
        model.predict.return_value = np.array([0, 1, 2, 0, 1])
        model.score = Mock()
        model.score.return_value = 0.85
        
        metrics = manager.evaluate_model(model, sample_ml_data['X_test'], sample_ml_data['y_test'])
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        assert metrics['accuracy'] == 0.85

class TestRandomForestModel:
    """Testes para RandomForestModel"""
    
    def test_init(self):
        """Testa inicialização do RandomForestModel"""
        model = RandomForestModel()
        assert model.model_type == 'random_forest'
        assert hasattr(model, 'model')
        assert hasattr(model, 'is_trained')
        assert model.is_trained == False
    
    def test_fit(self, sample_ml_data):
        """Testa treinamento do modelo"""
        model = RandomForestModel()
        model.fit(sample_ml_data['X_train'], sample_ml_data['y_train'])
        
        assert model.is_trained == True
        assert hasattr(model, 'model')
    
    def test_predict(self, sample_ml_data):
        """Testa predição do modelo"""
        model = RandomForestModel()
        model.fit(sample_ml_data['X_train'], sample_ml_data['y_train'])
        
        predictions = model.predict(sample_ml_data['X_test'])
        
        assert predictions is not None
        assert len(predictions) == len(sample_ml_data['X_test'])
        assert all(pred in [0, 1, 2] for pred in predictions)
    
    def test_predict_proba(self, sample_ml_data):
        """Testa predição de probabilidades"""
        model = RandomForestModel()
        model.fit(sample_ml_data['X_train'], sample_ml_data['y_train'])
        
        probabilities = model.predict_proba(sample_ml_data['X_test'])
        
        assert probabilities is not None
        assert probabilities.shape[0] == len(sample_ml_data['X_test'])
        assert probabilities.shape[1] == 3  # 3 classes
        assert np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-10)
    
    def test_score(self, sample_ml_data):
        """Testa score do modelo"""
        model = RandomForestModel()
        model.fit(sample_ml_data['X_train'], sample_ml_data['y_train'])
        
        score = model.score(sample_ml_data['X_test'], sample_ml_data['y_test'])
        
        assert 0 <= score <= 1
        assert isinstance(score, float)
    
    def test_predict_untrained(self, sample_ml_data):
        """Testa predição com modelo não treinado"""
        model = RandomForestModel()
        
        with pytest.raises(ValueError, match="Model must be trained before making predictions"):
            model.predict(sample_ml_data['X_test'])

class TestXGBoostModel:
    """Testes para XGBoostModel"""
    
    def test_init(self):
        """Testa inicialização do XGBoostModel"""
        model = XGBoostModel()
        assert model.model_type == 'xgboost'
        assert hasattr(model, 'model')
        assert hasattr(model, 'is_trained')
        assert model.is_trained == False
    
    def test_fit(self, sample_ml_data):
        """Testa treinamento do modelo"""
        model = XGBoostModel()
        model.fit(sample_ml_data['X_train'], sample_ml_data['y_train'])
        
        assert model.is_trained == True
        assert hasattr(model, 'model')
    
    def test_predict(self, sample_ml_data):
        """Testa predição do modelo"""
        model = XGBoostModel()
        model.fit(sample_ml_data['X_train'], sample_ml_data['y_train'])
        
        predictions = model.predict(sample_ml_data['X_test'])
        
        assert predictions is not None
        assert len(predictions) == len(sample_ml_data['X_test'])
        assert all(pred in [0, 1, 2] for pred in predictions)
    
    def test_predict_proba(self, sample_ml_data):
        """Testa predição de probabilidades"""
        model = XGBoostModel()
        model.fit(sample_ml_data['X_train'], sample_ml_data['y_train'])
        
        probabilities = model.predict_proba(sample_ml_data['X_test'])
        
        assert probabilities is not None
        assert probabilities.shape[0] == len(sample_ml_data['X_test'])
        assert probabilities.shape[1] == 3  # 3 classes
        assert np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-10)

class TestProbabilityCalculator:
    """Testes para ProbabilityCalculator"""
    
    def test_init(self):
        """Testa inicialização do ProbabilityCalculator"""
        calculator = ProbabilityCalculator()
        assert calculator is not None
        assert hasattr(calculator, 'models')
    
    def test_calculate_probability_single_model(self, sample_ml_data):
        """Testa cálculo de probabilidade com modelo único"""
        calculator = ProbabilityCalculator()
        
        # Mock do modelo
        mock_model = Mock()
        mock_model.predict_proba.return_value = np.array([[0.3, 0.4, 0.3]])
        mock_model.is_trained = True
        
        probability = calculator.calculate_probability(mock_model, sample_ml_data['X_test'][:1])
        
        assert probability is not None
        assert 0 <= probability <= 1
        mock_model.predict_proba.assert_called_once()
    
    def test_calculate_probability_ensemble(self, sample_ml_data):
        """Testa cálculo de probabilidade com ensemble"""
        calculator = ProbabilityCalculator()
        
        # Mock de múltiplos modelos
        mock_models = []
        for i in range(3):
            mock_model = Mock()
            mock_model.predict_proba.return_value = np.array([[0.2, 0.3, 0.5]])
            mock_model.is_trained = True
            mock_models.append(mock_model)
        
        probability = calculator.calculate_probability(mock_models, sample_ml_data['X_test'][:1])
        
        assert probability is not None
        assert 0 <= probability <= 1
        # Verifica se todos os modelos foram chamados
        for model in mock_models:
            model.predict_proba.assert_called_once()
    
    def test_calculate_probability_untrained_model(self, sample_ml_data):
        """Testa cálculo com modelo não treinado"""
        calculator = ProbabilityCalculator()
        
        mock_model = Mock()
        mock_model.is_trained = False
        
        with pytest.raises(ValueError, match="Model must be trained"):
            calculator.calculate_probability(mock_model, sample_ml_data['X_test'][:1])
    
    def test_calculate_implied_probability(self):
        """Testa cálculo de probabilidade implícita"""
        calculator = ProbabilityCalculator()
        
        # Teste com odds de 2.0 (probabilidade implícita de 0.5)
        implied_prob = calculator.calculate_implied_probability(2.0)
        assert abs(implied_prob - 0.5) < 1e-10
        
        # Teste com odds de 3.0 (probabilidade implícita de 0.333...)
        implied_prob = calculator.calculate_implied_probability(3.0)
        assert abs(implied_prob - 1/3) < 1e-10
    
    def test_calculate_expected_value(self):
        """Testa cálculo de expected value"""
        calculator = ProbabilityCalculator()
        
        # Teste com probabilidade de 0.6 e odds de 2.0
        ev = calculator.calculate_expected_value(0.6, 2.0)
        expected = 0.6 * 2.0 - 1  # 0.2
        assert abs(ev - expected) < 1e-10
        
        # Teste com probabilidade de 0.4 e odds de 3.0
        ev = calculator.calculate_expected_value(0.4, 3.0)
        expected = 0.4 * 3.0 - 1  # 0.2
        assert abs(ev - expected) < 1e-10

class TestValueIdentifier:
    """Testes para ValueIdentifier"""
    
    def test_init(self):
        """Testa inicialização do ValueIdentifier"""
        identifier = ValueIdentifier()
        assert identifier is not None
        assert hasattr(identifier, 'min_ev_threshold')
        assert hasattr(identifier, 'min_confidence_threshold')
    
    def test_identify_value_bet_positive_ev(self):
        """Testa identificação de value bet com EV positivo"""
        identifier = ValueIdentifier()
        
        # Mock de dados de predição
        prediction_data = {
            'predicted_probability': 0.6,
            'current_odd': 2.0,
            'confidence': 0.8,
            'min_ev_threshold': 0.1,
            'min_confidence_threshold': 0.7
        }
        
        is_value_bet = identifier.identify_value_bet(prediction_data)
        
        assert is_value_bet == True
    
    def test_identify_value_bet_negative_ev(self):
        """Testa identificação de value bet com EV negativo"""
        identifier = ValueIdentifier()
        
        # Mock de dados de predição
        prediction_data = {
            'predicted_probability': 0.4,
            'current_odd': 2.0,
            'confidence': 0.8,
            'min_ev_threshold': 0.1,
            'min_confidence_threshold': 0.7
        }
        
        is_value_bet = identifier.identify_value_bet(prediction_data)
        
        assert is_value_bet == False
    
    def test_identify_value_bet_low_confidence(self):
        """Testa identificação de value bet com confiança baixa"""
        identifier = ValueIdentifier()
        
        # Mock de dados de predição
        prediction_data = {
            'predicted_probability': 0.6,
            'current_odd': 2.0,
            'confidence': 0.5,  # Baixa confiança
            'min_ev_threshold': 0.1,
            'min_confidence_threshold': 0.7
        }
        
        is_value_bet = identifier.identify_value_bet(prediction_data)
        
        assert is_value_bet == False
    
    def test_calculate_kelly_criterion(self):
        """Testa cálculo do Kelly Criterion"""
        identifier = ValueIdentifier()
        
        # Teste com EV positivo
        kelly = identifier.calculate_kelly_criterion(0.6, 2.0)
        expected = (0.6 * 2.0 - 1) / (2.0 - 1)  # 0.2
        assert abs(kelly - expected) < 1e-10
        
        # Teste com EV negativo
        kelly = identifier.calculate_kelly_criterion(0.4, 2.0)
        assert kelly == 0  # Kelly deve ser 0 para EV negativo
    
    def test_calculate_stake_percentage(self):
        """Testa cálculo de percentual de stake"""
        identifier = ValueIdentifier()
        
        # Teste com Kelly Criterion
        stake = identifier.calculate_stake_percentage(0.6, 2.0, method='kelly')
        kelly = identifier.calculate_kelly_criterion(0.6, 2.0)
        assert abs(stake - kelly) < 1e-10
        
        # Teste com método fixo
        stake = identifier.calculate_stake_percentage(0.6, 2.0, method='fixed', fixed_percentage=0.02)
        assert stake == 0.02

class TestFeatureEngineering:
    """Testes para feature engineering"""
    
    def test_create_team_features(self, sample_team_stats):
        """Testa criação de features de time"""
        from feature_engineering import FeatureEngineer
        
        engineer = FeatureEngineer()
        features = engineer.create_team_features(sample_team_stats)
        
        assert isinstance(features, dict)
        assert 'goals_scored' in features
        assert 'goals_conceded' in features
        assert 'form' in features
        assert 'home_form' in features
        assert 'away_form' in features
    
    def test_create_match_features(self, sample_match_data, sample_team_stats):
        """Testa criação de features de partida"""
        from feature_engineering import FeatureEngineer
        
        engineer = FeatureEngineer()
        home_stats = sample_team_stats.copy()
        away_stats = sample_team_stats.copy()
        
        features = engineer.create_match_features(sample_match_data, home_stats, away_stats)
        
        assert isinstance(features, dict)
        assert 'home_goals_avg' in features
        assert 'away_goals_avg' in features
        assert 'home_form' in features
        assert 'away_form' in features
    
    def test_create_odds_features(self, sample_odds_data):
        """Testa criação de features de odds"""
        from feature_engineering import FeatureEngineer
        
        engineer = FeatureEngineer()
        features = engineer.create_odds_features(sample_odds_data)
        
        assert isinstance(features, dict)
        assert 'home_odd' in features
        assert 'draw_odd' in features
        assert 'away_odd' in features
        assert 'total_probability' in features

@pytest.mark.ml
class TestMLIntegration:
    """Testes de integração para ML"""
    
    def test_full_ml_pipeline(self, sample_ml_data):
        """Testa pipeline completo de ML"""
        manager = MLModelManager()
        
        # Criar e treinar modelo
        model = manager.create_model('random_forest')
        manager.train_model(model, sample_ml_data['X_train'], sample_ml_data['y_train'])
        
        # Fazer predições
        predictions = manager.predict(model, sample_ml_data['X_test'])
        probabilities = model.predict_proba(sample_ml_data['X_test'])
        
        # Avaliar modelo
        metrics = manager.evaluate_model(model, sample_ml_data['X_test'], sample_ml_data['y_test'])
        
        # Verificações
        assert len(predictions) == len(sample_ml_data['X_test'])
        assert probabilities.shape[0] == len(sample_ml_data['X_test'])
        assert 'accuracy' in metrics
        assert metrics['accuracy'] > 0
    
    def test_ensemble_prediction(self, sample_ml_data):
        """Testa predição com ensemble de modelos"""
        manager = MLModelManager()
        calculator = ProbabilityCalculator()
        
        # Criar múltiplos modelos
        models = []
        for model_type in ['random_forest', 'xgboost', 'lightgbm']:
            model = manager.create_model(model_type)
            manager.train_model(model, sample_ml_data['X_train'], sample_ml_data['y_train'])
            models.append(model)
        
        # Fazer predição com ensemble
        probability = calculator.calculate_probability(models, sample_ml_data['X_test'][:1])
        
        assert probability is not None
        assert 0 <= probability <= 1
    
    def test_value_bet_identification_pipeline(self, sample_ml_data):
        """Testa pipeline completo de identificação de value bets"""
        manager = MLModelManager()
        calculator = ProbabilityCalculator()
        identifier = ValueIdentifier()
        
        # Treinar modelo
        model = manager.create_model('random_forest')
        manager.train_model(model, sample_ml_data['X_train'], sample_ml_data['y_train'])
        
        # Calcular probabilidade
        probability = calculator.calculate_probability(model, sample_ml_data['X_test'][:1])
        
        # Identificar value bet
        prediction_data = {
            'predicted_probability': probability,
            'current_odd': 2.0,
            'confidence': 0.8,
            'min_ev_threshold': 0.1,
            'min_confidence_threshold': 0.7
        }
        
        is_value_bet = identifier.identify_value_bet(prediction_data)
        
        assert isinstance(is_value_bet, bool)
