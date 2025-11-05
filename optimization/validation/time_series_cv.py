"""
Time Series Cross-Validation para otimização de hiperparâmetros
Implementa técnicas avançadas de validação cruzada para séries temporais
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Generator, Optional, Dict, Any
from sklearn.model_selection import BaseCrossValidator
from sklearn.base import BaseEstimator
import warnings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TimeSeriesSplit(BaseCrossValidator):
    """
    Time Series Cross-Validation com configurações avançadas
    """
    
    def __init__(
        self,
        n_splits: int = 5,
        test_size: Optional[int] = None,
        gap: int = 0,
        expanding_window: bool = False,
        min_train_size: Optional[int] = None,
        max_train_size: Optional[int] = None
    ):
        """
        Inicializa o Time Series Split
        
        Args:
            n_splits: Número de splits
            test_size: Tamanho do conjunto de teste (se None, usa 1/n_splits)
            gap: Gap entre treino e teste (evita data leakage)
            expanding_window: Se True, usa janela expansiva; se False, usa janela deslizante
            min_train_size: Tamanho mínimo do conjunto de treino
            max_train_size: Tamanho máximo do conjunto de treino
        """
        self.n_splits = n_splits
        self.test_size = test_size
        self.gap = gap
        self.expanding_window = expanding_window
        self.min_train_size = min_train_size
        self.max_train_size = max_train_size
        
    def split(self, X, y=None, groups=None) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Gera splits para validação cruzada temporal
        """
        n_samples = len(X)
        
        if self.test_size is None:
            test_size = n_samples // (self.n_splits + 1)
        else:
            test_size = self.test_size
            
        if self.min_train_size is None:
            min_train_size = test_size
        else:
            min_train_size = self.min_train_size
            
        if self.max_train_size is None:
            max_train_size = n_samples - test_size - self.gap
        else:
            max_train_size = min(self.max_train_size, n_samples - test_size - self.gap)
        
        # Garantir que temos dados suficientes
        if min_train_size + test_size + self.gap > n_samples:
            raise ValueError(
                f"Not enough samples for {self.n_splits} splits. "
                f"Need at least {min_train_size + test_size + self.gap} samples, got {n_samples}"
            )
        
        for i in range(self.n_splits):
            # Calcular índices de teste
            test_start = n_samples - test_size - (i * test_size)
            test_end = test_start + test_size
            
            if test_start < 0:
                break
                
            # Calcular índices de treino
            if self.expanding_window:
                # Janela expansiva: sempre começa do início
                train_start = 0
                train_end = test_start - self.gap
            else:
                # Janela deslizante: mantém tamanho fixo
                train_end = test_start - self.gap
                train_start = max(0, train_end - max_train_size)
            
            # Ajustar tamanho mínimo
            if train_end - train_start < min_train_size:
                train_start = max(0, train_end - min_train_size)
            
            # Verificar se temos dados suficientes
            if train_end <= train_start or test_end <= test_start:
                break
                
            train_indices = np.arange(train_start, train_end)
            test_indices = np.arange(test_start, test_end)
            
            yield train_indices, test_indices
    
    def get_n_splits(self, X=None, y=None, groups=None) -> int:
        """Retorna o número de splits"""
        return self.n_splits


class PurgedCrossValidation(BaseCrossValidator):
    """
    Purged Cross-Validation para evitar data leakage em dados financeiros
    Remove períodos de purga entre treino e teste
    """
    
    def __init__(
        self,
        n_splits: int = 5,
        test_size: Optional[int] = None,
        purge_days: int = 1,
        embargo_days: int = 1
    ):
        """
        Inicializa o Purged Cross-Validation
        
        Args:
            n_splits: Número de splits
            test_size: Tamanho do conjunto de teste
            purge_days: Dias para purgar entre treino e teste
            embargo_days: Dias de embargo após o teste
        """
        self.n_splits = n_splits
        self.test_size = test_size
        self.purge_days = purge_days
        self.embargo_days = embargo_days
        
    def split(self, X, y=None, groups=None) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Gera splits com purga para evitar data leakage
        """
        n_samples = len(X)
        
        if self.test_size is None:
            test_size = n_samples // (self.n_splits + 1)
        else:
            test_size = self.test_size
        
        # Calcular tamanho total necessário
        total_size = test_size + self.purge_days + self.embargo_days
        if total_size * self.n_splits > n_samples:
            raise ValueError("Not enough samples for purged cross-validation")
        
        for i in range(self.n_splits):
            # Calcular índices de teste
            test_start = n_samples - test_size - (i * total_size)
            test_end = test_start + test_size
            
            if test_start < 0:
                break
            
            # Calcular índices de treino (antes da purga)
            train_end = test_start - self.purge_days
            train_start = 0
            
            # Aplicar embargo (remover dados após o teste)
            embargo_start = test_end + self.embargo_days
            
            # Filtrar índices de treino
            train_indices = np.arange(train_start, train_end)
            
            # Filtrar índices de teste
            test_indices = np.arange(test_start, test_end)
            
            # Remover índices que estão no período de embargo
            if embargo_start < n_samples:
                train_indices = train_indices[train_indices < embargo_start]
            
            if len(train_indices) == 0 or len(test_indices) == 0:
                break
                
            yield train_indices, test_indices
    
    def get_n_splits(self, X=None, y=None, groups=None) -> int:
        """Retorna o número de splits"""
        return self.n_splits


class WalkForwardAnalysis:
    """
    Walk-Forward Analysis para validação de estratégias de trading
    """
    
    def __init__(
        self,
        initial_train_size: int,
        step_size: int,
        min_train_size: Optional[int] = None,
        max_train_size: Optional[int] = None,
        gap: int = 0
    ):
        """
        Inicializa o Walk-Forward Analysis
        
        Args:
            initial_train_size: Tamanho inicial do conjunto de treino
            step_size: Tamanho do passo para avançar
            min_train_size: Tamanho mínimo do conjunto de treino
            max_train_size: Tamanho máximo do conjunto de treino
            gap: Gap entre treino e teste
        """
        self.initial_train_size = initial_train_size
        self.step_size = step_size
        self.min_train_size = min_train_size or initial_train_size
        self.max_train_size = max_train_size
        self.gap = gap
        
    def split(self, X, y=None, groups=None) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Gera splits para walk-forward analysis
        """
        n_samples = len(X)
        current_start = 0
        
        while True:
            # Calcular tamanho do treino
            train_size = min(
                self.initial_train_size + (current_start // self.step_size) * self.step_size,
                self.max_train_size or n_samples
            )
            
            # Calcular índices de treino
            train_end = current_start + train_size
            if train_end >= n_samples:
                break
                
            # Calcular índices de teste
            test_start = train_end + self.gap
            test_end = test_start + self.step_size
            
            if test_end > n_samples:
                test_end = n_samples
                
            if test_start >= n_samples:
                break
                
            train_indices = np.arange(current_start, train_end)
            test_indices = np.arange(test_start, test_end)
            
            if len(train_indices) == 0 or len(test_indices) == 0:
                break
                
            yield train_indices, test_indices
            
            # Avançar para o próximo split
            current_start += self.step_size


class MonteCarloCrossValidation:
    """
    Monte Carlo Cross-Validation para validação robusta
    """
    
    def __init__(
        self,
        n_splits: int = 100,
        test_size: float = 0.2,
        random_state: Optional[int] = None
    ):
        """
        Inicializa o Monte Carlo Cross-Validation
        
        Args:
            n_splits: Número de splits aleatórios
            test_size: Proporção do conjunto de teste
            random_state: Seed para reprodutibilidade
        """
        self.n_splits = n_splits
        self.test_size = test_size
        self.random_state = random_state
        
    def split(self, X, y=None, groups=None) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Gera splits aleatórios para Monte Carlo CV
        """
        n_samples = len(X)
        test_size = int(n_samples * self.test_size)
        
        rng = np.random.RandomState(self.random_state)
        
        for _ in range(self.n_splits):
            # Gerar índices aleatórios
            indices = rng.permutation(n_samples)
            test_indices = indices[:test_size]
            train_indices = indices[test_size:]
            
            yield train_indices, test_indices
    
    def get_n_splits(self, X=None, y=None, groups=None) -> int:
        """Retorna o número de splits"""
        return self.n_splits


class CrossValidationManager:
    """
    Gerenciador de validação cruzada com múltiplas estratégias
    """
    
    def __init__(self, strategy: str = "time_series", **kwargs):
        """
        Inicializa o gerenciador de CV
        
        Args:
            strategy: Estratégia de validação ("time_series", "purged", "walk_forward", "monte_carlo")
            **kwargs: Parâmetros específicos da estratégia
        """
        self.strategy = strategy
        self.kwargs = kwargs
        self.cv = self._create_cv()
        
    def _create_cv(self):
        """Cria o objeto de validação cruzada baseado na estratégia"""
        if self.strategy == "time_series":
            return TimeSeriesSplit(**self.kwargs)
        elif self.strategy == "purged":
            return PurgedCrossValidation(**self.kwargs)
        elif self.strategy == "walk_forward":
            return WalkForwardAnalysis(**self.kwargs)
        elif self.strategy == "monte_carlo":
            return MonteCarloCrossValidation(**self.kwargs)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
    
    def cross_validate(
        self,
        estimator: BaseEstimator,
        X: np.ndarray,
        y: np.ndarray,
        scoring: str = "accuracy",
        return_train_score: bool = False
    ) -> Dict[str, Any]:
        """
        Executa validação cruzada
        
        Args:
            estimator: Modelo para validação
            X: Features
            y: Target
            scoring: Métrica de avaliação
            return_train_score: Se deve retornar scores de treino
            
        Returns:
            Dicionário com resultados da validação
        """
        from sklearn.model_selection import cross_validate
        
        cv_results = cross_validate(
            estimator=estimator,
            X=X,
            y=y,
            cv=self.cv,
            scoring=scoring,
            return_train_score=return_train_score,
            return_estimator=True
        )
        
        return cv_results
    
    def get_splits(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Retorna todos os splits
        
        Args:
            X: Features
            y: Target (opcional)
            
        Returns:
            Lista de tuplas (train_indices, test_indices)
        """
        return list(self.cv.split(X, y))
    
    def get_n_splits(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> int:
        """
        Retorna o número de splits
        
        Args:
            X: Features
            y: Target (opcional)
            
        Returns:
            Número de splits
        """
        return self.cv.get_n_splits(X, y)


def create_time_series_cv(
    strategy: str = "time_series",
    n_splits: int = 5,
    test_size: Optional[int] = None,
    gap: int = 0,
    **kwargs
) -> CrossValidationManager:
    """
    Função de conveniência para criar validação cruzada temporal
    
    Args:
        strategy: Estratégia de validação
        n_splits: Número de splits
        test_size: Tamanho do conjunto de teste
        gap: Gap entre treino e teste
        **kwargs: Parâmetros adicionais
        
    Returns:
        Gerenciador de validação cruzada
    """
    params = {
        "n_splits": n_splits,
        "test_size": test_size,
        "gap": gap,
        **kwargs
    }
    
    return CrossValidationManager(strategy=strategy, **params)


# Exemplo de uso
if __name__ == "__main__":
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 1000
    X = np.random.randn(n_samples, 10)
    y = np.random.randint(0, 3, n_samples)
    
    # Testar diferentes estratégias
    strategies = ["time_series", "purged", "walk_forward", "monte_carlo"]
    
    for strategy in strategies:
        print(f"\n=== {strategy.upper()} ===")
        
        try:
            cv_manager = create_time_series_cv(strategy=strategy, n_splits=3)
            splits = cv_manager.get_splits(X, y)
            
            print(f"Número de splits: {len(splits)}")
            for i, (train_idx, test_idx) in enumerate(splits):
                print(f"Split {i+1}: Train={len(train_idx)}, Test={len(test_idx)}")
                
        except Exception as e:
            print(f"Erro com {strategy}: {e}")
