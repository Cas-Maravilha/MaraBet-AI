"""
Otimizadores específicos para cada modelo ML
Implementa espaços de hiperparâmetros otimizados para cada algoritmo
"""

import optuna
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.base import BaseEstimator
import logging

logger = logging.getLogger(__name__)

class RandomForestOptimizer:
    """Otimizador específico para Random Forest"""
    
    @staticmethod
    def suggest_hyperparameters(trial: optuna.Trial, **kwargs) -> Dict[str, Any]:
        """
        Sugere hiperparâmetros para Random Forest
        
        Args:
            trial: Trial do Optuna
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dicionário com hiperparâmetros sugeridos
        """
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 1000),
            'max_depth': trial.suggest_int('max_depth', 3, 30),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
            'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
            'bootstrap': trial.suggest_categorical('bootstrap', [True, False]),
            'criterion': trial.suggest_categorical('criterion', ['gini', 'entropy']),
            'max_leaf_nodes': trial.suggest_int('max_leaf_nodes', 10, 1000),
            'min_impurity_decrease': trial.suggest_float('min_impurity_decrease', 0.0, 0.1),
            'ccp_alpha': trial.suggest_float('ccp_alpha', 0.0, 0.1),
            'random_state': kwargs.get('random_state', 42)
        }
        
        return params
    
    @staticmethod
    def get_default_params() -> Dict[str, Any]:
        """Retorna parâmetros padrão para Random Forest"""
        return {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 2,
            'min_samples_leaf': 1,
            'max_features': 'sqrt',
            'bootstrap': True,
            'criterion': 'gini',
            'random_state': 42
        }


class XGBoostOptimizer:
    """Otimizador específico para XGBoost"""
    
    @staticmethod
    def suggest_hyperparameters(trial: optuna.Trial, **kwargs) -> Dict[str, Any]:
        """
        Sugere hiperparâmetros para XGBoost
        
        Args:
            trial: Trial do Optuna
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dicionário com hiperparâmetros sugeridos
        """
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 1000),
            'max_depth': trial.suggest_int('max_depth', 3, 15),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'colsample_bylevel': trial.suggest_float('colsample_bylevel', 0.6, 1.0),
            'colsample_bynode': trial.suggest_float('colsample_bynode', 0.6, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 0, 10),
            'reg_lambda': trial.suggest_float('reg_lambda', 0, 10),
            'gamma': trial.suggest_float('gamma', 0, 5),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
            'max_delta_step': trial.suggest_int('max_delta_step', 0, 10),
            'random_state': kwargs.get('random_state', 42),
            'n_jobs': kwargs.get('n_jobs', -1)
        }
        
        return params
    
    @staticmethod
    def get_default_params() -> Dict[str, Any]:
        """Retorna parâmetros padrão para XGBoost"""
        return {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'reg_alpha': 0,
            'reg_lambda': 1,
            'random_state': 42
        }


class LightGBMOptimizer:
    """Otimizador específico para LightGBM"""
    
    @staticmethod
    def suggest_hyperparameters(trial: optuna.Trial, **kwargs) -> Dict[str, Any]:
        """
        Sugere hiperparâmetros para LightGBM
        
        Args:
            trial: Trial do Optuna
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dicionário com hiperparâmetros sugeridos
        """
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 1000),
            'max_depth': trial.suggest_int('max_depth', 3, 15),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 0, 10),
            'reg_lambda': trial.suggest_float('reg_lambda', 0, 10),
            'num_leaves': trial.suggest_int('num_leaves', 10, 300),
            'min_child_samples': trial.suggest_int('min_child_samples', 5, 100),
            'min_child_weight': trial.suggest_float('min_child_weight', 0.001, 10),
            'min_split_gain': trial.suggest_float('min_split_gain', 0, 1),
            'feature_fraction': trial.suggest_float('feature_fraction', 0.5, 1.0),
            'bagging_fraction': trial.suggest_float('bagging_fraction', 0.5, 1.0),
            'bagging_freq': trial.suggest_int('bagging_freq', 1, 10),
            'random_state': kwargs.get('random_state', 42),
            'n_jobs': kwargs.get('n_jobs', -1),
            'verbose': -1
        }
        
        return params
    
    @staticmethod
    def get_default_params() -> Dict[str, Any]:
        """Retorna parâmetros padrão para LightGBM"""
        return {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'num_leaves': 31,
            'min_child_samples': 20,
            'reg_alpha': 0,
            'reg_lambda': 0,
            'random_state': 42,
            'verbose': -1
        }


class CatBoostOptimizer:
    """Otimizador específico para CatBoost"""
    
    @staticmethod
    def suggest_hyperparameters(trial: optuna.Trial, **kwargs) -> Dict[str, Any]:
        """
        Sugere hiperparâmetros para CatBoost
        
        Args:
            trial: Trial do Optuna
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dicionário com hiperparâmetros sugeridos
        """
        params = {
            'iterations': trial.suggest_int('iterations', 50, 1000),
            'depth': trial.suggest_int('depth', 3, 12),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
            'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1, 10),
            'bootstrap_type': trial.suggest_categorical('bootstrap_type', ['Bayesian', 'Bernoulli']),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bylevel': trial.suggest_float('colsample_bylevel', 0.6, 1.0),
            'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 1, 20),
            'max_leaves': trial.suggest_int('max_leaves', 16, 64),
            'grow_policy': trial.suggest_categorical('grow_policy', ['SymmetricTree', 'Depthwise', 'Lossguide']),
            'random_seed': kwargs.get('random_state', 42),
            'verbose': False
        }
        
        return params
    
    @staticmethod
    def get_default_params() -> Dict[str, Any]:
        """Retorna parâmetros padrão para CatBoost"""
        return {
            'iterations': 100,
            'depth': 6,
            'learning_rate': 0.1,
            'l2_leaf_reg': 3,
            'bootstrap_type': 'Bayesian',
            'subsample': 0.8,
            'random_seed': 42,
            'verbose': False
        }


class LogisticRegressionOptimizer:
    """Otimizador específico para Regressão Logística"""
    
    @staticmethod
    def suggest_hyperparameters(trial: optuna.Trial, **kwargs) -> Dict[str, Any]:
        """
        Sugere hiperparâmetros para Regressão Logística
        
        Args:
            trial: Trial do Optuna
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dicionário com hiperparâmetros sugeridos
        """
        penalty = trial.suggest_categorical('penalty', ['l1', 'l2', 'elasticnet'])
        
        params = {
            'C': trial.suggest_float('C', 0.001, 100, log=True),
            'penalty': penalty,
            'solver': trial.suggest_categorical('solver', ['liblinear', 'saga']),
            'max_iter': trial.suggest_int('max_iter', 100, 2000),
            'tol': trial.suggest_float('tol', 1e-6, 1e-3, log=True),
            'random_state': kwargs.get('random_state', 42)
        }
        
        # Ajustar solver baseado na penalidade
        if penalty == 'elasticnet':
            params['l1_ratio'] = trial.suggest_float('l1_ratio', 0, 1)
        elif penalty == 'l1':
            params['solver'] = 'liblinear'
        
        return params
    
    @staticmethod
    def get_default_params() -> Dict[str, Any]:
        """Retorna parâmetros padrão para Regressão Logística"""
        return {
            'C': 1.0,
            'penalty': 'l2',
            'solver': 'liblinear',
            'max_iter': 1000,
            'random_state': 42
        }


class NeuralNetworkOptimizer:
    """Otimizador específico para Redes Neurais"""
    
    @staticmethod
    def suggest_hyperparameters(trial: optuna.Trial, **kwargs) -> Dict[str, Any]:
        """
        Sugere hiperparâmetros para Redes Neurais
        
        Args:
            trial: Trial do Optuna
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dicionário com hiperparâmetros sugeridos
        """
        # Definir arquitetura da rede
        n_layers = trial.suggest_int('n_layers', 1, 4)
        hidden_layers = []
        
        for i in range(n_layers):
            layer_size = trial.suggest_int(f'layer_{i}_size', 10, 200)
            hidden_layers.append(layer_size)
        
        params = {
            'hidden_layer_sizes': tuple(hidden_layers),
            'activation': trial.suggest_categorical('activation', ['relu', 'tanh', 'logistic']),
            'alpha': trial.suggest_float('alpha', 0.0001, 0.1, log=True),
            'learning_rate': trial.suggest_categorical('learning_rate', ['constant', 'adaptive']),
            'learning_rate_init': trial.suggest_float('learning_rate_init', 0.001, 0.1),
            'max_iter': trial.suggest_int('max_iter', 100, 1000),
            'early_stopping': trial.suggest_categorical('early_stopping', [True, False]),
            'validation_fraction': trial.suggest_float('validation_fraction', 0.1, 0.3),
            'n_iter_no_change': trial.suggest_int('n_iter_no_change', 5, 20),
            'random_state': kwargs.get('random_state', 42)
        }
        
        return params
    
    @staticmethod
    def get_default_params() -> Dict[str, Any]:
        """Retorna parâmetros padrão para Redes Neurais"""
        return {
            'hidden_layer_sizes': (100,),
            'activation': 'relu',
            'alpha': 0.0001,
            'learning_rate': 'constant',
            'learning_rate_init': 0.001,
            'max_iter': 500,
            'random_state': 42
        }


class PoissonModelOptimizer:
    """Otimizador específico para Modelo de Poisson"""
    
    @staticmethod
    def suggest_hyperparameters(trial: optuna.Trial, **kwargs) -> Dict[str, Any]:
        """
        Sugere hiperparâmetros para Modelo de Poisson
        
        Args:
            trial: Trial do Optuna
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dicionário com hiperparâmetros sugeridos
        """
        params = {
            'alpha': trial.suggest_float('alpha', 0.001, 10, log=True),
            'max_iter': trial.suggest_int('max_iter', 100, 2000),
            'tol': trial.suggest_float('tol', 1e-6, 1e-3, log=True),
            'warm_start': trial.suggest_categorical('warm_start', [True, False]),
            'fit_intercept': trial.suggest_categorical('fit_intercept', [True, False])
        }
        
        return params
    
    @staticmethod
    def get_default_params() -> Dict[str, Any]:
        """Retorna parâmetros padrão para Modelo de Poisson"""
        return {
            'alpha': 1.0,
            'max_iter': 1000,
            'tol': 1e-4,
            'warm_start': False,
            'fit_intercept': True
        }


class ModelOptimizerFactory:
    """Factory para criar otimizadores específicos"""
    
    _optimizers = {
        'random_forest': RandomForestOptimizer,
        'xgboost': XGBoostOptimizer,
        'lightgbm': LightGBMOptimizer,
        'catboost': CatBoostOptimizer,
        'logistic_regression': LogisticRegressionOptimizer,
        'neural_network': NeuralNetworkOptimizer,
        'poisson_model': PoissonModelOptimizer
    }
    
    @classmethod
    def get_optimizer(cls, model_name: str):
        """
        Retorna o otimizador para o modelo especificado
        
        Args:
            model_name: Nome do modelo
            
        Returns:
            Classe do otimizador
        """
        if model_name not in cls._optimizers:
            raise ValueError(f"Otimizador para {model_name} não encontrado")
        
        return cls._optimizers[model_name]
    
    @classmethod
    def get_supported_models(cls) -> List[str]:
        """Retorna lista de modelos suportados"""
        return list(cls._optimizers.keys())
    
    @classmethod
    def suggest_hyperparameters(cls, model_name: str, trial: optuna.Trial, **kwargs) -> Dict[str, Any]:
        """
        Sugere hiperparâmetros para o modelo especificado
        
        Args:
            model_name: Nome do modelo
            trial: Trial do Optuna
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dicionário com hiperparâmetros sugeridos
        """
        optimizer = cls.get_optimizer(model_name)
        return optimizer.suggest_hyperparameters(trial, **kwargs)
    
    @classmethod
    def get_default_params(cls, model_name: str) -> Dict[str, Any]:
        """
        Retorna parâmetros padrão para o modelo especificado
        
        Args:
            model_name: Nome do modelo
            
        Returns:
            Dicionário com parâmetros padrão
        """
        optimizer = cls.get_optimizer(model_name)
        return optimizer.get_default_params()


# Exemplo de uso
if __name__ == "__main__":
    # Testar otimizadores
    import optuna
    
    def objective(trial):
        # Usar otimizador do Random Forest
        params = ModelOptimizerFactory.suggest_hyperparameters(
            'random_forest', trial, random_state=42
        )
        
        # Simular score (em uso real, treinar modelo e avaliar)
        score = np.random.random()
        return score
    
    # Criar estudo
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=10)
    
    print(f"Melhor score: {study.best_value:.4f}")
    print(f"Melhores parâmetros: {study.best_params}")
    
    # Testar parâmetros padrão
    default_params = ModelOptimizerFactory.get_default_params('random_forest')
    print(f"Parâmetros padrão Random Forest: {default_params}")
