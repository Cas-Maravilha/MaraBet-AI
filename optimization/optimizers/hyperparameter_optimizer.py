"""
Sistema de Otimização de Hiperparâmetros Automática
Utiliza Optuna e Ray Tune para otimização avançada
"""

import optuna
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import logging
import joblib
import json
from datetime import datetime
import os
from pathlib import Path

from optimization.validation.time_series_cv import CrossValidationManager, create_time_series_cv

logger = logging.getLogger(__name__)

class HyperparameterOptimizer:
    """
    Otimizador de hiperparâmetros principal usando Optuna
    """
    
    def __init__(
        self,
        study_name: str = "marabet_optimization",
        storage_url: Optional[str] = None,
        direction: str = "maximize",
        n_trials: int = 100,
        timeout: Optional[int] = None,
        cv_strategy: str = "time_series",
        cv_params: Optional[Dict[str, Any]] = None,
        scoring: str = "accuracy",
        random_state: Optional[int] = None
    ):
        """
        Inicializa o otimizador de hiperparâmetros
        
        Args:
            study_name: Nome do estudo Optuna
            storage_url: URL do storage (SQLite, PostgreSQL, etc.)
            direction: Direção da otimização ("maximize" ou "minimize")
            n_trials: Número de tentativas
            timeout: Timeout em segundos
            cv_strategy: Estratégia de validação cruzada
            cv_params: Parâmetros da validação cruzada
            scoring: Métrica de avaliação
            random_state: Seed para reprodutibilidade
        """
        self.study_name = study_name
        self.storage_url = storage_url or f"sqlite:///optimization/{study_name}.db"
        self.direction = direction
        self.n_trials = n_trials
        self.timeout = timeout
        self.scoring = scoring
        self.random_state = random_state
        
        # Configurar validação cruzada
        self.cv_params = cv_params or {}
        self.cv_manager = create_time_series_cv(
            strategy=cv_strategy,
            **self.cv_params
        )
        
        # Inicializar estudo Optuna
        self.study = self._create_study()
        
        # Histórico de otimizações
        self.optimization_history = []
        
    def _create_study(self) -> optuna.Study:
        """Cria o estudo Optuna"""
        sampler = optuna.samplers.TPESampler(seed=self.random_state)
        pruner = optuna.pruners.MedianPruner(
            n_startup_trials=5,
            n_warmup_steps=10,
            interval_steps=1
        )
        
        study = optuna.create_study(
            study_name=self.study_name,
            storage=self.storage_url,
            direction=self.direction,
            sampler=sampler,
            pruner=pruner,
            load_if_exists=True
        )
        
        return study
    
    def optimize_random_forest(
        self,
        X: np.ndarray,
        y: np.ndarray,
        **kwargs
    ) -> optuna.Study:
        """
        Otimiza hiperparâmetros do Random Forest
        
        Args:
            X: Features
            y: Target
            **kwargs: Parâmetros adicionais
            
        Returns:
            Estudo Optuna otimizado
        """
        from sklearn.ensemble import RandomForestClassifier
        
        def objective(trial):
            # Definir espaço de hiperparâmetros
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 20),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
                'bootstrap': trial.suggest_categorical('bootstrap', [True, False]),
                'random_state': self.random_state
            }
            
            # Criar modelo
            model = RandomForestClassifier(**params)
            
            # Validação cruzada
            cv_results = self.cv_manager.cross_validate(
                estimator=model,
                X=X,
                y=y,
                scoring=self.scoring
            )
            
            return cv_results['test_score'].mean()
        
        # Executar otimização
        self.study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout
        )
        
        return self.study
    
    def optimize_xgboost(
        self,
        X: np.ndarray,
        y: np.ndarray,
        **kwargs
    ) -> optuna.Study:
        """
        Otimiza hiperparâmetros do XGBoost
        
        Args:
            X: Features
            y: Target
            **kwargs: Parâmetros adicionais
            
        Returns:
            Estudo Optuna otimizado
        """
        import xgboost as xgb
        
        def objective(trial):
            # Definir espaço de hiperparâmetros
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'reg_alpha': trial.suggest_float('reg_alpha', 0, 10),
                'reg_lambda': trial.suggest_float('reg_lambda', 0, 10),
                'random_state': self.random_state
            }
            
            # Criar modelo
            model = xgb.XGBClassifier(**params)
            
            # Validação cruzada
            cv_results = self.cv_manager.cross_validate(
                estimator=model,
                X=X,
                y=y,
                scoring=self.scoring
            )
            
            return cv_results['test_score'].mean()
        
        # Executar otimização
        self.study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout
        )
        
        return self.study
    
    def optimize_lightgbm(
        self,
        X: np.ndarray,
        y: np.ndarray,
        **kwargs
    ) -> optuna.Study:
        """
        Otimiza hiperparâmetros do LightGBM
        
        Args:
            X: Features
            y: Target
            **kwargs: Parâmetros adicionais
            
        Returns:
            Estudo Optuna otimizado
        """
        import lightgbm as lgb
        
        def objective(trial):
            # Definir espaço de hiperparâmetros
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 15),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'reg_alpha': trial.suggest_float('reg_alpha', 0, 10),
                'reg_lambda': trial.suggest_float('reg_lambda', 0, 10),
                'num_leaves': trial.suggest_int('num_leaves', 10, 100),
                'min_child_samples': trial.suggest_int('min_child_samples', 5, 50),
                'random_state': self.random_state
            }
            
            # Criar modelo
            model = lgb.LGBMClassifier(**params)
            
            # Validação cruzada
            cv_results = self.cv_manager.cross_validate(
                estimator=model,
                X=X,
                y=y,
                scoring=self.scoring
            )
            
            return cv_results['test_score'].mean()
        
        # Executar otimização
        self.study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout
        )
        
        return self.study
    
    def optimize_catboost(
        self,
        X: np.ndarray,
        y: np.ndarray,
        **kwargs
    ) -> optuna.Study:
        """
        Otimiza hiperparâmetros do CatBoost
        
        Args:
            X: Features
            y: Target
            **kwargs: Parâmetros adicionais
            
        Returns:
            Estudo Optuna otimizado
        """
        from catboost import CatBoostClassifier
        
        def objective(trial):
            # Definir espaço de hiperparâmetros
            params = {
                'iterations': trial.suggest_int('iterations', 50, 500),
                'depth': trial.suggest_int('depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1, 10),
                'bootstrap_type': trial.suggest_categorical('bootstrap_type', ['Bayesian', 'Bernoulli']),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'random_seed': self.random_state,
                'verbose': False
            }
            
            # Criar modelo
            model = CatBoostClassifier(**params)
            
            # Validação cruzada
            cv_results = self.cv_manager.cross_validate(
                estimator=model,
                X=X,
                y=y,
                scoring=self.scoring
            )
            
            return cv_results['test_score'].mean()
        
        # Executar otimização
        self.study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout
        )
        
        return self.study
    
    def optimize_logistic_regression(
        self,
        X: np.ndarray,
        y: np.ndarray,
        **kwargs
    ) -> optuna.Study:
        """
        Otimiza hiperparâmetros da Regressão Logística
        
        Args:
            X: Features
            y: Target
            **kwargs: Parâmetros adicionais
            
        Returns:
            Estudo Optuna otimizado
        """
        from sklearn.linear_model import LogisticRegression
        
        def objective(trial):
            # Definir espaço de hiperparâmetros
            params = {
                'C': trial.suggest_float('C', 0.001, 100, log=True),
                'penalty': trial.suggest_categorical('penalty', ['l1', 'l2', 'elasticnet']),
                'solver': trial.suggest_categorical('solver', ['liblinear', 'saga']),
                'max_iter': trial.suggest_int('max_iter', 100, 1000),
                'random_state': self.random_state
            }
            
            # Ajustar solver baseado na penalidade
            if params['penalty'] == 'elasticnet':
                params['l1_ratio'] = trial.suggest_float('l1_ratio', 0, 1)
            elif params['penalty'] == 'l1':
                params['solver'] = 'liblinear'
            
            # Criar modelo
            model = LogisticRegression(**params)
            
            # Validação cruzada
            cv_results = self.cv_manager.cross_validate(
                estimator=model,
                X=X,
                y=y,
                scoring=self.scoring
            )
            
            return cv_results['test_score'].mean()
        
        # Executar otimização
        self.study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout
        )
        
        return self.study
    
    def optimize_bayesian_neural_network(
        self,
        X: np.ndarray,
        y: np.ndarray,
        **kwargs
    ) -> optuna.Study:
        """
        Otimiza hiperparâmetros da Rede Neural Bayesiana
        
        Args:
            X: Features
            y: Target
            **kwargs: Parâmetros adicionais
            
        Returns:
            Estudo Optuna otimizado
        """
        from sklearn.neural_network import MLPClassifier
        
        def objective(trial):
            # Definir espaço de hiperparâmetros
            params = {
                'hidden_layer_sizes': trial.suggest_categorical(
                    'hidden_layer_sizes',
                    [(50,), (100,), (50, 50), (100, 50), (100, 100)]
                ),
                'activation': trial.suggest_categorical('activation', ['relu', 'tanh', 'logistic']),
                'alpha': trial.suggest_float('alpha', 0.0001, 0.1, log=True),
                'learning_rate': trial.suggest_categorical('learning_rate', ['constant', 'adaptive']),
                'learning_rate_init': trial.suggest_float('learning_rate_init', 0.001, 0.1),
                'max_iter': trial.suggest_int('max_iter', 100, 500),
                'random_state': self.random_state
            }
            
            # Criar modelo
            model = MLPClassifier(**params)
            
            # Validação cruzada
            cv_results = self.cv_manager.cross_validate(
                estimator=model,
                X=X,
                y=y,
                scoring=self.scoring
            )
            
            return cv_results['test_score'].mean()
        
        # Executar otimização
        self.study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout
        )
        
        return self.study
    
    def optimize_poisson_model(
        self,
        X: np.ndarray,
        y: np.ndarray,
        **kwargs
    ) -> optuna.Study:
        """
        Otimiza hiperparâmetros do Modelo de Poisson
        
        Args:
            X: Features
            y: Target
            **kwargs: Parâmetros adicionais
            
        Returns:
            Estudo Optuna otimizado
        """
        from sklearn.linear_model import PoissonRegressor
        
        def objective(trial):
            # Definir espaço de hiperparâmetros
            params = {
                'alpha': trial.suggest_float('alpha', 0.001, 10, log=True),
                'max_iter': trial.suggest_int('max_iter', 100, 1000),
                'tol': trial.suggest_float('tol', 1e-6, 1e-3, log=True),
                'warm_start': trial.suggest_categorical('warm_start', [True, False])
            }
            
            # Criar modelo
            model = PoissonRegressor(**params)
            
            # Validação cruzada
            cv_results = self.cv_manager.cross_validate(
                estimator=model,
                X=X,
                y=y,
                scoring=self.scoring
            )
            
            return cv_results['test_score'].mean()
        
        # Executar otimização
        self.study.optimize(
            objective,
            n_trials=self.n_trials,
            timeout=self.timeout
        )
        
        return self.study
    
    def get_best_params(self) -> Dict[str, Any]:
        """Retorna os melhores parâmetros encontrados"""
        return self.study.best_params
    
    def get_best_score(self) -> float:
        """Retorna o melhor score encontrado"""
        return self.study.best_value
    
    def get_best_trial(self) -> optuna.Trial:
        """Retorna o melhor trial"""
        return self.study.best_trial
    
    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Retorna o histórico de otimizações"""
        return [
            {
                'trial_number': trial.number,
                'value': trial.value,
                'params': trial.params,
                'datetime': trial.datetime_start
            }
            for trial in self.study.trials
        ]
    
    def save_study(self, filepath: str) -> None:
        """Salva o estudo em arquivo"""
        joblib.dump(self.study, filepath)
        logger.info(f"Estudo salvo em: {filepath}")
    
    def load_study(self, filepath: str) -> None:
        """Carrega estudo de arquivo"""
        self.study = joblib.load(filepath)
        logger.info(f"Estudo carregado de: {filepath}")
    
    def export_results(self, filepath: str) -> None:
        """Exporta resultados para JSON"""
        results = {
            'study_name': self.study_name,
            'best_params': self.get_best_params(),
            'best_score': self.get_best_score(),
            'n_trials': len(self.study.trials),
            'optimization_history': self.get_optimization_history(),
            'cv_strategy': self.cv_manager.strategy,
            'cv_params': self.cv_params,
            'scoring': self.scoring,
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Resultados exportados para: {filepath}")


class MultiModelOptimizer:
    """
    Otimizador para múltiplos modelos simultaneamente
    """
    
    def __init__(
        self,
        models: List[str],
        study_name: str = "multi_model_optimization",
        **kwargs
    ):
        """
        Inicializa o otimizador multi-modelo
        
        Args:
            models: Lista de modelos para otimizar
            study_name: Nome do estudo
            **kwargs: Parâmetros do otimizador
        """
        self.models = models
        self.optimizers = {}
        
        for model in models:
            self.optimizers[model] = HyperparameterOptimizer(
                study_name=f"{study_name}_{model}",
                **kwargs
            )
    
    def optimize_all(
        self,
        X: np.ndarray,
        y: np.ndarray,
        **kwargs
    ) -> Dict[str, optuna.Study]:
        """
        Otimiza todos os modelos
        
        Args:
            X: Features
            y: Target
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dicionário com estudos otimizados
        """
        results = {}
        
        for model_name, optimizer in self.optimizers.items():
            logger.info(f"Otimizando {model_name}...")
            
            if model_name == "random_forest":
                study = optimizer.optimize_random_forest(X, y, **kwargs)
            elif model_name == "xgboost":
                study = optimizer.optimize_xgboost(X, y, **kwargs)
            elif model_name == "lightgbm":
                study = optimizer.optimize_lightgbm(X, y, **kwargs)
            elif model_name == "catboost":
                study = optimizer.optimize_catboost(X, y, **kwargs)
            elif model_name == "logistic_regression":
                study = optimizer.optimize_logistic_regression(X, y, **kwargs)
            elif model_name == "bayesian_neural_network":
                study = optimizer.optimize_bayesian_neural_network(X, y, **kwargs)
            elif model_name == "poisson_model":
                study = optimizer.optimize_poisson_model(X, y, **kwargs)
            else:
                logger.warning(f"Modelo {model_name} não suportado")
                continue
            
            results[model_name] = study
            logger.info(f"{model_name} otimizado. Melhor score: {study.best_value:.4f}")
        
        return results
    
    def get_best_model(self) -> Tuple[str, Dict[str, Any], float]:
        """
        Retorna o melhor modelo e seus parâmetros
        
        Returns:
            Tupla (nome_do_modelo, melhores_parametros, melhor_score)
        """
        best_model = None
        best_score = float('-inf') if self.optimizers[list(self.optimizers.keys())[0]].direction == "maximize" else float('inf')
        best_params = None
        
        for model_name, optimizer in self.optimizers.items():
            score = optimizer.get_best_score()
            
            if optimizer.direction == "maximize" and score > best_score:
                best_score = score
                best_model = model_name
                best_params = optimizer.get_best_params()
            elif optimizer.direction == "minimize" and score < best_score:
                best_score = score
                best_model = model_name
                best_params = optimizer.get_best_params()
        
        return best_model, best_params, best_score


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 1000
    X = np.random.randn(n_samples, 10)
    y = np.random.randint(0, 3, n_samples)
    
    # Otimizar Random Forest
    optimizer = HyperparameterOptimizer(
        study_name="test_rf",
        n_trials=20,
        cv_strategy="time_series",
        cv_params={"n_splits": 3, "gap": 1}
    )
    
    study = optimizer.optimize_random_forest(X, y)
    
    print(f"Melhor score: {optimizer.get_best_score():.4f}")
    print(f"Melhores parâmetros: {optimizer.get_best_params()}")
    
    # Exportar resultados
    optimizer.export_results("optimization_results.json")
