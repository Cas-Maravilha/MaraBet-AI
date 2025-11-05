"""
Testes para o sistema de otimização de hiperparâmetros
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from datetime import datetime

from optimization.optimizers.hyperparameter_optimizer import HyperparameterOptimizer, MultiModelOptimizer
from optimization.optimizers.model_optimizers import ModelOptimizerFactory
from optimization.validation.time_series_cv import create_time_series_cv, TimeSeriesSplit, PurgedCrossValidation

class TestHyperparameterOptimizer:
    """Testes para HyperparameterOptimizer"""
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para testes"""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        y = np.random.randint(0, 3, 100)
        return X, y
    
    @pytest.fixture
    def optimizer(self):
        """Otimizador para testes"""
        return HyperparameterOptimizer(
            study_name="test_study",
            n_trials=5,
            cv_strategy="time_series",
            cv_params={"n_splits": 3, "gap": 1},
            random_state=42
        )
    
    def test_optimizer_initialization(self, optimizer):
        """Testa inicialização do otimizador"""
        assert optimizer.study_name == "test_study"
        assert optimizer.n_trials == 5
        assert optimizer.direction == "maximize"
        assert optimizer.scoring == "accuracy"
        assert optimizer.cv_manager is not None
    
    def test_optimize_random_forest(self, optimizer, sample_data):
        """Testa otimização do Random Forest"""
        X, y = sample_data
        
        with patch('sklearn.ensemble.RandomForestClassifier') as mock_rf:
            mock_model = Mock()
            mock_rf.return_value = mock_model
            
            # Mock do cross_validate
            with patch.object(optimizer.cv_manager, 'cross_validate') as mock_cv:
                mock_cv.return_value = {'test_score': np.array([0.8, 0.85, 0.82])}
                
                study = optimizer.optimize_random_forest(X, y)
                
                assert study is not None
                assert len(study.trials) == 5
                mock_rf.assert_called()
                mock_cv.assert_called()
    
    def test_optimize_xgboost(self, optimizer, sample_data):
        """Testa otimização do XGBoost"""
        X, y = sample_data
        
        with patch('xgboost.XGBClassifier') as mock_xgb:
            mock_model = Mock()
            mock_xgb.return_value = mock_model
            
            with patch.object(optimizer.cv_manager, 'cross_validate') as mock_cv:
                mock_cv.return_value = {'test_score': np.array([0.8, 0.85, 0.82])}
                
                study = optimizer.optimize_xgboost(X, y)
                
                assert study is not None
                assert len(study.trials) == 5
                mock_xgb.assert_called()
                mock_cv.assert_called()
    
    def test_optimize_lightgbm(self, optimizer, sample_data):
        """Testa otimização do LightGBM"""
        X, y = sample_data
        
        with patch('lightgbm.LGBMClassifier') as mock_lgb:
            mock_model = Mock()
            mock_lgb.return_value = mock_model
            
            with patch.object(optimizer.cv_manager, 'cross_validate') as mock_cv:
                mock_cv.return_value = {'test_score': np.array([0.8, 0.85, 0.82])}
                
                study = optimizer.optimize_lightgbm(X, y)
                
                assert study is not None
                assert len(study.trials) == 5
                mock_lgb.assert_called()
                mock_cv.assert_called()
    
    def test_optimize_catboost(self, optimizer, sample_data):
        """Testa otimização do CatBoost"""
        X, y = sample_data
        
        with patch('catboost.CatBoostClassifier') as mock_cat:
            mock_model = Mock()
            mock_cat.return_value = mock_model
            
            with patch.object(optimizer.cv_manager, 'cross_validate') as mock_cv:
                mock_cv.return_value = {'test_score': np.array([0.8, 0.85, 0.82])}
                
                study = optimizer.optimize_catboost(X, y)
                
                assert study is not None
                assert len(study.trials) == 5
                mock_cat.assert_called()
                mock_cv.assert_called()
    
    def test_optimize_logistic_regression(self, optimizer, sample_data):
        """Testa otimização da Regressão Logística"""
        X, y = sample_data
        
        with patch('sklearn.linear_model.LogisticRegression') as mock_lr:
            mock_model = Mock()
            mock_lr.return_value = mock_model
            
            with patch.object(optimizer.cv_manager, 'cross_validate') as mock_cv:
                mock_cv.return_value = {'test_score': np.array([0.8, 0.85, 0.82])}
                
                study = optimizer.optimize_logistic_regression(X, y)
                
                assert study is not None
                assert len(study.trials) == 5
                mock_lr.assert_called()
                mock_cv.assert_called()
    
    def test_optimize_bayesian_neural_network(self, optimizer, sample_data):
        """Testa otimização da Rede Neural Bayesiana"""
        X, y = sample_data
        
        with patch('sklearn.neural_network.MLPClassifier') as mock_mlp:
            mock_model = Mock()
            mock_mlp.return_value = mock_model
            
            with patch.object(optimizer.cv_manager, 'cross_validate') as mock_cv:
                mock_cv.return_value = {'test_score': np.array([0.8, 0.85, 0.82])}
                
                study = optimizer.optimize_bayesian_neural_network(X, y)
                
                assert study is not None
                assert len(study.trials) == 5
                mock_mlp.assert_called()
                mock_cv.assert_called()
    
    def test_optimize_poisson_model(self, optimizer, sample_data):
        """Testa otimização do Modelo de Poisson"""
        X, y = sample_data
        
        with patch('sklearn.linear_model.PoissonRegressor') as mock_poisson:
            mock_model = Mock()
            mock_poisson.return_value = mock_model
            
            with patch.object(optimizer.cv_manager, 'cross_validate') as mock_cv:
                mock_cv.return_value = {'test_score': np.array([0.8, 0.85, 0.82])}
                
                study = optimizer.optimize_poisson_model(X, y)
                
                assert study is not None
                assert len(study.trials) == 5
                mock_poisson.assert_called()
                mock_cv.assert_called()
    
    def test_get_best_params(self, optimizer):
        """Testa obtenção dos melhores parâmetros"""
        # Mock do estudo com parâmetros
        mock_trial = Mock()
        mock_trial.params = {'n_estimators': 100, 'max_depth': 10}
        mock_trial.value = 0.85
        
        optimizer.study.best_trial = mock_trial
        
        best_params = optimizer.get_best_params()
        assert best_params == {'n_estimators': 100, 'max_depth': 10}
    
    def test_get_best_score(self, optimizer):
        """Testa obtenção do melhor score"""
        optimizer.study.best_value = 0.85
        
        best_score = optimizer.get_best_score()
        assert best_score == 0.85
    
    def test_export_results(self, optimizer, sample_data):
        """Testa exportação de resultados"""
        X, y = sample_data
        
        with patch.object(optimizer.cv_manager, 'cross_validate') as mock_cv:
            mock_cv.return_value = {'test_score': np.array([0.8, 0.85, 0.82])}
            
            # Executar uma otimização simples
            optimizer.optimize_random_forest(X, y)
            
            # Exportar resultados
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                filepath = f.name
            
            try:
                optimizer.export_results(filepath)
                
                # Verificar se arquivo foi criado
                assert os.path.exists(filepath)
                
                # Verificar conteúdo
                with open(filepath, 'r') as f:
                    data = f.read()
                    assert 'study_name' in data
                    assert 'best_params' in data
                    assert 'best_score' in data
                    
            finally:
                if os.path.exists(filepath):
                    os.unlink(filepath)


class TestMultiModelOptimizer:
    """Testes para MultiModelOptimizer"""
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para testes"""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        y = np.random.randint(0, 3, 100)
        return X, y
    
    @pytest.fixture
    def multi_optimizer(self):
        """Otimizador multi-modelo para testes"""
        return MultiModelOptimizer(
            models=['random_forest', 'xgboost'],
            study_name="test_multi_study",
            n_trials=3,
            cv_strategy="time_series",
            cv_params={"n_splits": 3, "gap": 1},
            random_state=42
        )
    
    def test_multi_optimizer_initialization(self, multi_optimizer):
        """Testa inicialização do otimizador multi-modelo"""
        assert len(multi_optimizer.models) == 2
        assert 'random_forest' in multi_optimizer.models
        assert 'xgboost' in multi_optimizer.models
        assert len(multi_optimizer.optimizers) == 2
    
    def test_optimize_all(self, multi_optimizer, sample_data):
        """Testa otimização de todos os modelos"""
        X, y = sample_data
        
        with patch('sklearn.ensemble.RandomForestClassifier') as mock_rf, \
             patch('xgboost.XGBClassifier') as mock_xgb:
            
            mock_rf_model = Mock()
            mock_xgb_model = Mock()
            mock_rf.return_value = mock_rf_model
            mock_xgb.return_value = mock_xgb_model
            
            # Mock do cross_validate para ambos os otimizadores
            for optimizer in multi_optimizer.optimizers.values():
                with patch.object(optimizer.cv_manager, 'cross_validate') as mock_cv:
                    mock_cv.return_value = {'test_score': np.array([0.8, 0.85, 0.82])}
            
            results = multi_optimizer.optimize_all(X, y)
            
            assert len(results) == 2
            assert 'random_forest' in results
            assert 'xgboost' in results
    
    def test_get_best_model(self, multi_optimizer):
        """Testa obtenção do melhor modelo"""
        # Mock dos scores
        multi_optimizer.optimizers['random_forest'].study.best_value = 0.85
        multi_optimizer.optimizers['random_forest'].study.best_trial.params = {'n_estimators': 100}
        
        multi_optimizer.optimizers['xgboost'].study.best_value = 0.90
        multi_optimizer.optimizers['xgboost'].study.best_trial.params = {'n_estimators': 200}
        
        best_model, best_params, best_score = multi_optimizer.get_best_model()
        
        assert best_model == 'xgboost'
        assert best_score == 0.90
        assert best_params == {'n_estimators': 200}


class TestModelOptimizerFactory:
    """Testes para ModelOptimizerFactory"""
    
    def test_get_supported_models(self):
        """Testa obtenção de modelos suportados"""
        models = ModelOptimizerFactory.get_supported_models()
        
        expected_models = [
            'random_forest', 'xgboost', 'lightgbm', 'catboost',
            'logistic_regression', 'neural_network', 'poisson_model'
        ]
        
        for model in expected_models:
            assert model in models
    
    def test_get_optimizer(self):
        """Testa obtenção de otimizador específico"""
        optimizer_class = ModelOptimizerFactory.get_optimizer('random_forest')
        assert optimizer_class is not None
        assert hasattr(optimizer_class, 'suggest_hyperparameters')
        assert hasattr(optimizer_class, 'get_default_params')
    
    def test_get_optimizer_invalid_model(self):
        """Testa obtenção de otimizador para modelo inválido"""
        with pytest.raises(ValueError):
            ModelOptimizerFactory.get_optimizer('invalid_model')
    
    def test_suggest_hyperparameters(self):
        """Testa sugestão de hiperparâmetros"""
        from unittest.mock import Mock
        
        mock_trial = Mock()
        mock_trial.suggest_int.return_value = 100
        mock_trial.suggest_float.return_value = 0.1
        mock_trial.suggest_categorical.return_value = 'sqrt'
        
        params = ModelOptimizerFactory.suggest_hyperparameters(
            'random_forest', mock_trial, random_state=42
        )
        
        assert isinstance(params, dict)
        assert 'n_estimators' in params
        assert 'max_depth' in params
        assert 'random_state' in params
        assert params['random_state'] == 42
    
    def test_get_default_params(self):
        """Testa obtenção de parâmetros padrão"""
        params = ModelOptimizerFactory.get_default_params('random_forest')
        
        assert isinstance(params, dict)
        assert 'n_estimators' in params
        assert 'max_depth' in params
        assert 'random_state' in params


class TestTimeSeriesCrossValidation:
    """Testes para validação cruzada temporal"""
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para testes"""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        y = np.random.randint(0, 3, 100)
        return X, y
    
    def test_time_series_split(self, sample_data):
        """Testa TimeSeriesSplit"""
        X, y = sample_data
        
        cv = TimeSeriesSplit(n_splits=3, test_size=20, gap=1)
        splits = list(cv.split(X, y))
        
        assert len(splits) == 3
        
        for train_idx, test_idx in splits:
            assert len(train_idx) > 0
            assert len(test_idx) > 0
            assert len(set(train_idx) & set(test_idx)) == 0  # Sem sobreposição
    
    def test_purged_cross_validation(self, sample_data):
        """Testa PurgedCrossValidation"""
        X, y = sample_data
        
        cv = PurgedCrossValidation(n_splits=3, test_size=20, purge_days=1, embargo_days=1)
        splits = list(cv.split(X, y))
        
        assert len(splits) == 3
        
        for train_idx, test_idx in splits:
            assert len(train_idx) > 0
            assert len(test_idx) > 0
            assert len(set(train_idx) & set(test_idx)) == 0  # Sem sobreposição
    
    def test_create_time_series_cv(self, sample_data):
        """Testa função de conveniência"""
        X, y = sample_data
        
        cv_manager = create_time_series_cv(
            strategy="time_series",
            n_splits=3,
            test_size=20,
            gap=1
        )
        
        assert cv_manager.strategy == "time_series"
        assert cv_manager.cv is not None
        
        splits = cv_manager.get_splits(X, y)
        assert len(splits) == 3


class TestOptimizationIntegration:
    """Testes de integração para o sistema de otimização"""
    
    @pytest.fixture
    def sample_data(self):
        """Dados de exemplo para testes"""
        np.random.seed(42)
        X = np.random.randn(200, 10)
        y = np.random.randint(0, 3, 200)
        return X, y
    
    def test_end_to_end_optimization(self, sample_data):
        """Testa otimização completa do início ao fim"""
        X, y = sample_data
        
        optimizer = HyperparameterOptimizer(
            study_name="integration_test",
            n_trials=3,
            cv_strategy="time_series",
            cv_params={"n_splits": 3, "gap": 1},
            random_state=42
        )
        
        with patch('sklearn.ensemble.RandomForestClassifier') as mock_rf:
            mock_model = Mock()
            mock_rf.return_value = mock_model
            
            with patch.object(optimizer.cv_manager, 'cross_validate') as mock_cv:
                mock_cv.return_value = {'test_score': np.array([0.8, 0.85, 0.82])}
                
                # Executar otimização
                study = optimizer.optimize_random_forest(X, y)
                
                # Verificar resultados
                assert study is not None
                assert len(study.trials) == 3
                
                # Verificar se parâmetros foram sugeridos
                for trial in study.trials:
                    assert 'n_estimators' in trial.params
                    assert 'max_depth' in trial.params
                    assert trial.value is not None
    
    def test_optimization_with_different_cv_strategies(self, sample_data):
        """Testa otimização com diferentes estratégias de CV"""
        X, y = sample_data
        
        strategies = ["time_series", "purged", "walk_forward", "monte_carlo"]
        
        for strategy in strategies:
            optimizer = HyperparameterOptimizer(
                study_name=f"test_{strategy}",
                n_trials=2,
                cv_strategy=strategy,
                cv_params={"n_splits": 2},
                random_state=42
            )
            
            with patch('sklearn.ensemble.RandomForestClassifier') as mock_rf:
                mock_model = Mock()
                mock_rf.return_value = mock_model
                
                with patch.object(optimizer.cv_manager, 'cross_validate') as mock_cv:
                    mock_cv.return_value = {'test_score': np.array([0.8, 0.85])}
                    
                    study = optimizer.optimize_random_forest(X, y)
                    
                    assert study is not None
                    assert len(study.trials) == 2


# Marcadores de teste
pytestmark = [
    pytest.mark.unit,
    pytest.mark.optimization,
    pytest.mark.ml
]
