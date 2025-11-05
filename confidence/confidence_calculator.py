"""
Calculador de Intervalos de Confiança - MaraBet AI
Cálculo estatístico de intervalos de confiança para previsões
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import scipy.stats as stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
import warnings

logger = logging.getLogger(__name__)

class ConfidenceMethod(Enum):
    """Métodos de cálculo de intervalo de confiança"""
    NORMAL = "normal"
    BOOTSTRAP = "bootstrap"
    QUANTILE = "quantile"
    PREDICTION = "prediction"
    BAYESIAN = "bayesian"

@dataclass
class ConfidenceInterval:
    """Intervalo de confiança para uma previsão"""
    prediction: float
    lower_bound: float
    upper_bound: float
    confidence_level: float
    margin_of_error: float
    method: str
    sample_size: int
    standard_error: float
    degrees_of_freedom: Optional[int] = None

@dataclass
class PredictionUncertainty:
    """Incerteza de uma previsão"""
    mean_prediction: float
    confidence_intervals: Dict[float, ConfidenceInterval]  # level -> interval
    uncertainty_score: float
    reliability_score: float
    calibration_score: float
    method_used: str

class ConfidenceCalculator:
    """
    Calculador de intervalos de confiança para previsões do MaraBet AI
    Implementa múltiplos métodos estatísticos
    """
    
    def __init__(self, 
                 default_confidence_level: float = 0.95,
                 bootstrap_samples: int = 1000,
                 random_state: int = 42):
        """
        Inicializa o calculador de confiança
        
        Args:
            default_confidence_level: Nível de confiança padrão (0.95 = 95%)
            bootstrap_samples: Número de amostras para bootstrap
            random_state: Seed para reprodutibilidade
        """
        self.default_confidence_level = default_confidence_level
        self.bootstrap_samples = bootstrap_samples
        self.random_state = random_state
        np.random.seed(random_state)
        
        logger.info(f"ConfidenceCalculator inicializado - Nível padrão: {default_confidence_level*100:.0f}%")
    
    def calculate_confidence_interval(self,
                                    predictions: Union[List[float], np.ndarray],
                                    method: ConfidenceMethod = ConfidenceMethod.NORMAL,
                                    confidence_level: Optional[float] = None,
                                    sample_mean: Optional[float] = None,
                                    sample_std: Optional[float] = None,
                                    sample_size: Optional[int] = None) -> ConfidenceInterval:
        """
        Calcula intervalo de confiança para uma previsão
        
        Args:
            predictions: Lista de previsões ou previsão única
            method: Método de cálculo
            confidence_level: Nível de confiança (padrão: 0.95)
            sample_mean: Média da amostra (opcional)
            sample_std: Desvio padrão da amostra (opcional)
            sample_size: Tamanho da amostra (opcional)
            
        Returns:
            Intervalo de confiança calculado
        """
        try:
            if confidence_level is None:
                confidence_level = self.default_confidence_level
            
            predictions = np.array(predictions)
            
            if method == ConfidenceMethod.NORMAL:
                return self._calculate_normal_confidence(
                    predictions, confidence_level, sample_mean, sample_std, sample_size
                )
            elif method == ConfidenceMethod.BOOTSTRAP:
                return self._calculate_bootstrap_confidence(
                    predictions, confidence_level
                )
            elif method == ConfidenceMethod.QUANTILE:
                return self._calculate_quantile_confidence(
                    predictions, confidence_level
                )
            elif method == ConfidenceMethod.PREDICTION:
                return self._calculate_prediction_confidence(
                    predictions, confidence_level, sample_mean, sample_std, sample_size
                )
            elif method == ConfidenceMethod.BAYESIAN:
                return self._calculate_bayesian_confidence(
                    predictions, confidence_level
                )
            else:
                raise ValueError(f"Método não suportado: {method}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao calcular intervalo de confiança: {e}")
            return self._empty_confidence_interval()
    
    def _calculate_normal_confidence(self,
                                   predictions: np.ndarray,
                                   confidence_level: float,
                                   sample_mean: Optional[float] = None,
                                   sample_std: Optional[float] = None,
                                   sample_size: Optional[int] = None) -> ConfidenceInterval:
        """Calcula intervalo de confiança usando distribuição normal"""
        try:
            if len(predictions) == 1:
                # Previsão única - usar parâmetros fornecidos
                if sample_mean is None or sample_std is None or sample_size is None:
                    raise ValueError("Para previsão única, forneça sample_mean, sample_std e sample_size")
                
                mean = sample_mean
                std = sample_std
                n = sample_size
            else:
                # Múltiplas previsões - calcular estatísticas
                mean = np.mean(predictions)
                std = np.std(predictions, ddof=1)  # Desvio padrão amostral
                n = len(predictions)
            
            # Calcular erro padrão
            standard_error = std / np.sqrt(n)
            
            # Calcular margem de erro (t-distribution para pequenas amostras)
            if n < 30:
                df = n - 1
                t_value = stats.t.ppf((1 + confidence_level) / 2, df)
                margin_of_error = t_value * standard_error
            else:
                z_value = stats.norm.ppf((1 + confidence_level) / 2)
                margin_of_error = z_value * standard_error
                df = None
            
            # Calcular limites
            lower_bound = mean - margin_of_error
            upper_bound = mean + margin_of_error
            
            return ConfidenceInterval(
                prediction=mean,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence_level=confidence_level,
                margin_of_error=margin_of_error,
                method="normal",
                sample_size=n,
                standard_error=standard_error,
                degrees_of_freedom=df
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo normal: {e}")
            return self._empty_confidence_interval()
    
    def _calculate_bootstrap_confidence(self,
                                      predictions: np.ndarray,
                                      confidence_level: float) -> ConfidenceInterval:
        """Calcula intervalo de confiança usando bootstrap"""
        try:
            if len(predictions) == 1:
                # Para previsão única, simular variabilidade
                predictions = np.random.normal(predictions[0], 0.1, 100)
            
            n = len(predictions)
            bootstrap_means = []
            
            # Bootstrap sampling
            for _ in range(self.bootstrap_samples):
                bootstrap_sample = np.random.choice(predictions, size=n, replace=True)
                bootstrap_means.append(np.mean(bootstrap_sample))
            
            bootstrap_means = np.array(bootstrap_means)
            
            # Calcular percentis
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100
            
            lower_bound = np.percentile(bootstrap_means, lower_percentile)
            upper_bound = np.percentile(bootstrap_means, upper_percentile)
            mean = np.mean(bootstrap_means)
            
            margin_of_error = (upper_bound - lower_bound) / 2
            standard_error = np.std(bootstrap_means)
            
            return ConfidenceInterval(
                prediction=mean,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence_level=confidence_level,
                margin_of_error=margin_of_error,
                method="bootstrap",
                sample_size=n,
                standard_error=standard_error
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo bootstrap: {e}")
            return self._empty_confidence_interval()
    
    def _calculate_quantile_confidence(self,
                                     predictions: np.ndarray,
                                     confidence_level: float) -> ConfidenceInterval:
        """Calcula intervalo de confiança usando quantis"""
        try:
            if len(predictions) == 1:
                # Para previsão única, usar distribuição normal
                mean = predictions[0]
                std = 0.1  # Assumir pequena variabilidade
                alpha = 1 - confidence_level
                z_value = stats.norm.ppf((1 + confidence_level) / 2)
                margin_of_error = z_value * std
                lower_bound = mean - margin_of_error
                upper_bound = mean + margin_of_error
            else:
                # Usar quantis empíricos
                alpha = 1 - confidence_level
                lower_percentile = (alpha / 2) * 100
                upper_percentile = (1 - alpha / 2) * 100
                
                lower_bound = np.percentile(predictions, lower_percentile)
                upper_bound = np.percentile(predictions, upper_percentile)
                mean = np.mean(predictions)
                margin_of_error = (upper_bound - lower_bound) / 2
            
            standard_error = np.std(predictions) / np.sqrt(len(predictions)) if len(predictions) > 1 else 0.1
            
            return ConfidenceInterval(
                prediction=mean,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence_level=confidence_level,
                margin_of_error=margin_of_error,
                method="quantile",
                sample_size=len(predictions),
                standard_error=standard_error
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo quantile: {e}")
            return self._empty_confidence_interval()
    
    def _calculate_prediction_confidence(self,
                                       predictions: np.ndarray,
                                       confidence_level: float,
                                       sample_mean: Optional[float] = None,
                                       sample_std: Optional[float] = None,
                                       sample_size: Optional[int] = None) -> ConfidenceInterval:
        """Calcula intervalo de confiança para previsão (mais amplo que confiança)"""
        try:
            if len(predictions) == 1:
                if sample_mean is None or sample_std is None or sample_size is None:
                    raise ValueError("Para previsão única, forneça sample_mean, sample_std e sample_size")
                
                mean = sample_mean
                std = sample_std
                n = sample_size
            else:
                mean = np.mean(predictions)
                std = np.std(predictions, ddof=1)
                n = len(predictions)
            
            # Erro padrão para previsão (inclui variabilidade do modelo)
            standard_error = std * np.sqrt(1 + 1/n)
            
            # Calcular margem de erro
            if n < 30:
                df = n - 1
                t_value = stats.t.ppf((1 + confidence_level) / 2, df)
                margin_of_error = t_value * standard_error
            else:
                z_value = stats.norm.ppf((1 + confidence_level) / 2)
                margin_of_error = z_value * standard_error
                df = None
            
            # Calcular limites
            lower_bound = mean - margin_of_error
            upper_bound = mean + margin_of_error
            
            return ConfidenceInterval(
                prediction=mean,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence_level=confidence_level,
                margin_of_error=margin_of_error,
                method="prediction",
                sample_size=n,
                standard_error=standard_error,
                degrees_of_freedom=df
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de previsão: {e}")
            return self._empty_confidence_interval()
    
    def _calculate_bayesian_confidence(self,
                                     predictions: np.ndarray,
                                     confidence_level: float) -> ConfidenceInterval:
        """Calcula intervalo de confiança usando abordagem bayesiana"""
        try:
            if len(predictions) == 1:
                # Para previsão única, usar distribuição normal
                mean = predictions[0]
                std = 0.1
            else:
                mean = np.mean(predictions)
                std = np.std(predictions, ddof=1)
            
            # Usar distribuição normal para simplicidade
            # Em implementação completa, usaria distribuição posterior
            alpha = 1 - confidence_level
            z_value = stats.norm.ppf((1 + confidence_level) / 2)
            margin_of_error = z_value * std
            
            lower_bound = mean - margin_of_error
            upper_bound = mean + margin_of_error
            standard_error = std / np.sqrt(len(predictions)) if len(predictions) > 1 else std
            
            return ConfidenceInterval(
                prediction=mean,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence_level=confidence_level,
                margin_of_error=margin_of_error,
                method="bayesian",
                sample_size=len(predictions),
                standard_error=standard_error
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo bayesiano: {e}")
            return self._empty_confidence_interval()
    
    def calculate_multiple_confidence_levels(self,
                                           predictions: Union[List[float], np.ndarray],
                                           confidence_levels: List[float] = [0.68, 0.80, 0.90, 0.95, 0.99],
                                           method: ConfidenceMethod = ConfidenceMethod.NORMAL) -> Dict[float, ConfidenceInterval]:
        """
        Calcula intervalos de confiança para múltiplos níveis
        
        Args:
            predictions: Previsões
            confidence_levels: Lista de níveis de confiança
            method: Método de cálculo
            
        Returns:
            Dicionário com intervalos para cada nível
        """
        try:
            intervals = {}
            
            for level in confidence_levels:
                interval = self.calculate_confidence_interval(
                    predictions, method, level
                )
                intervals[level] = interval
            
            return intervals
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular múltiplos níveis: {e}")
            return {}
    
    def calculate_prediction_uncertainty(self,
                                       predictions: Union[List[float], np.ndarray],
                                       actual_values: Optional[Union[List[float], np.ndarray]] = None,
                                       method: ConfidenceMethod = ConfidenceMethod.NORMAL) -> PredictionUncertainty:
        """
        Calcula incerteza completa de uma previsão
        
        Args:
            predictions: Previsões
            actual_values: Valores reais (para calibração)
            method: Método de cálculo
            
        Returns:
            Objeto com incerteza completa
        """
        try:
            predictions = np.array(predictions)
            mean_prediction = np.mean(predictions)
            
            # Calcular intervalos para múltiplos níveis
            confidence_levels = [0.68, 0.80, 0.90, 0.95, 0.99]
            intervals = self.calculate_multiple_confidence_levels(
                predictions, confidence_levels, method
            )
            
            # Calcular scores de incerteza
            uncertainty_score = self._calculate_uncertainty_score(intervals)
            reliability_score = self._calculate_reliability_score(predictions)
            calibration_score = self._calculate_calibration_score(predictions, actual_values)
            
            return PredictionUncertainty(
                mean_prediction=mean_prediction,
                confidence_intervals=intervals,
                uncertainty_score=uncertainty_score,
                reliability_score=reliability_score,
                calibration_score=calibration_score,
                method_used=method.value
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular incerteza: {e}")
            return self._empty_prediction_uncertainty()
    
    def _calculate_uncertainty_score(self, intervals: Dict[float, ConfidenceInterval]) -> float:
        """Calcula score de incerteza baseado nos intervalos"""
        try:
            if not intervals:
                return 0.0
            
            # Usar intervalo de 95% como referência
            if 0.95 in intervals:
                interval_95 = intervals[0.95]
                width = interval_95.upper_bound - interval_95.lower_bound
                # Normalizar pela previsão média
                relative_width = width / abs(interval_95.prediction) if interval_95.prediction != 0 else width
                # Converter para score 0-100 (menor = mais certeza)
                uncertainty_score = min(100, relative_width * 100)
                return uncertainty_score
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"❌ Erro ao calcular score de incerteza: {e}")
            return 0.0
    
    def _calculate_reliability_score(self, predictions: np.ndarray) -> float:
        """Calcula score de confiabilidade baseado na consistência"""
        try:
            if len(predictions) <= 1:
                return 50.0  # Score neutro para previsão única
            
            # Calcular coeficiente de variação
            mean = np.mean(predictions)
            std = np.std(predictions)
            
            if mean == 0:
                return 50.0
            
            cv = std / abs(mean)
            # Converter para score 0-100 (menor CV = maior confiabilidade)
            reliability_score = max(0, 100 - (cv * 100))
            
            return min(100, reliability_score)
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular score de confiabilidade: {e}")
            return 50.0
    
    def _calculate_calibration_score(self, 
                                   predictions: np.ndarray, 
                                   actual_values: Optional[np.ndarray] = None) -> float:
        """Calcula score de calibração (precisão das incertezas)"""
        try:
            if actual_values is None or len(predictions) != len(actual_values):
                return 50.0  # Score neutro se não há valores reais
            
            # Calcular quantas previsões estão dentro dos intervalos
            predictions = np.array(predictions)
            actual_values = np.array(actual_values)
            
            # Usar intervalo de 95% como referência
            std = np.std(predictions)
            mean = np.mean(predictions)
            
            # Calcular quantas estão dentro de 2 desvios padrão
            within_2std = np.sum(np.abs(predictions - actual_values) <= 2 * std)
            calibration_score = (within_2std / len(predictions)) * 100
            
            return calibration_score
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular score de calibração: {e}")
            return 50.0
    
    def format_confidence_interval(self, 
                                 interval: ConfidenceInterval,
                                 decimal_places: int = 1) -> str:
        """
        Formata intervalo de confiança para exibição
        
        Args:
            interval: Intervalo de confiança
            decimal_places: Número de casas decimais
            
        Returns:
            String formatada (ex: "82% ± 5%")
        """
        try:
            prediction = interval.prediction
            margin = interval.margin_of_error
            confidence_pct = interval.confidence_level * 100
            
            # Converter para percentual se apropriado
            if prediction <= 1.0:
                prediction_pct = prediction * 100
                margin_pct = margin * 100
                return f"{prediction_pct:.{decimal_places}f}% ± {margin_pct:.{decimal_places}f}%"
            else:
                return f"{prediction:.{decimal_places}f} ± {margin:.{decimal_places}f}"
                
        except Exception as e:
            logger.error(f"❌ Erro ao formatar intervalo: {e}")
            return "N/A"
    
    def _empty_confidence_interval(self) -> ConfidenceInterval:
        """Retorna intervalo vazio"""
        return ConfidenceInterval(
            prediction=0.0,
            lower_bound=0.0,
            upper_bound=0.0,
            confidence_level=0.95,
            margin_of_error=0.0,
            method="none",
            sample_size=0,
            standard_error=0.0
        )
    
    def _empty_prediction_uncertainty(self) -> PredictionUncertainty:
        """Retorna incerteza vazia"""
        return PredictionUncertainty(
            mean_prediction=0.0,
            confidence_intervals={},
            uncertainty_score=0.0,
            reliability_score=0.0,
            calibration_score=0.0,
            method_used="none"
        )
    
    def validate_confidence_interval(self, interval: ConfidenceInterval) -> bool:
        """
        Valida se um intervalo de confiança é consistente
        
        Args:
            interval: Intervalo a ser validado
            
        Returns:
            True se válido
        """
        try:
            # Verificar se lower_bound <= prediction <= upper_bound
            if not (interval.lower_bound <= interval.prediction <= interval.upper_bound):
                return False
            
            # Verificar se margin_of_error é positivo
            if interval.margin_of_error < 0:
                return False
            
            # Verificar se confidence_level está entre 0 e 1
            if not (0 < interval.confidence_level < 1):
                return False
            
            # Verificar se sample_size é positivo
            if interval.sample_size <= 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na validação: {e}")
            return False
