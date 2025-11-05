"""
Sistema de Intervalos de Predição - MaraBet AI
Implementação de intervalos de predição para previsões de apostas
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
from sklearn.metrics import mean_squared_error
import warnings

logger = logging.getLogger(__name__)

class PredictionIntervalMethod(Enum):
    """Métodos de cálculo de intervalo de predição"""
    NORMAL = "normal"
    QUANTILE = "quantile"
    BOOTSTRAP = "bootstrap"
    CONFORMAL = "conformal"
    BAYESIAN = "bayesian"

@dataclass
class PredictionInterval:
    """Intervalo de predição para uma previsão"""
    prediction: float
    lower_bound: float
    upper_bound: float
    confidence_level: float
    interval_width: float
    method: str
    sample_size: int
    prediction_error: Optional[float] = None
    calibration_score: Optional[float] = None

@dataclass
class PredictionIntervalMetrics:
    """Métricas de qualidade dos intervalos de predição"""
    coverage_rate: float
    average_width: float
    width_std: float
    calibration_score: float
    sharpness_score: float
    reliability_score: float
    total_predictions: int

class PredictionIntervals:
    """
    Sistema de intervalos de predição para MaraBet AI
    Calcula intervalos de predição usando múltiplos métodos
    """
    
    def __init__(self, 
                 default_confidence_level: float = 0.95,
                 bootstrap_samples: int = 1000,
                 random_state: int = 42):
        """
        Inicializa o sistema de intervalos de predição
        
        Args:
            default_confidence_level: Nível de confiança padrão
            bootstrap_samples: Número de amostras para bootstrap
            random_state: Seed para reprodutibilidade
        """
        self.default_confidence_level = default_confidence_level
        self.bootstrap_samples = bootstrap_samples
        self.random_state = random_state
        np.random.seed(random_state)
        
        logger.info(f"PredictionIntervals inicializado - Nível padrão: {default_confidence_level*100:.0f}%")
    
    def calculate_prediction_interval(self,
                                    prediction: float,
                                    historical_errors: Optional[List[float]] = None,
                                    method: PredictionIntervalMethod = PredictionIntervalMethod.NORMAL,
                                    confidence_level: Optional[float] = None,
                                    model_uncertainty: Optional[float] = None) -> PredictionInterval:
        """
        Calcula intervalo de predição para uma previsão
        
        Args:
            prediction: Previsão pontual
            historical_errors: Erros históricos do modelo (opcional)
            method: Método de cálculo
            confidence_level: Nível de confiança
            model_uncertainty: Incerteza do modelo (opcional)
            
        Returns:
            Intervalo de predição calculado
        """
        try:
            if confidence_level is None:
                confidence_level = self.default_confidence_level
            
            if method == PredictionIntervalMethod.NORMAL:
                return self._calculate_normal_prediction_interval(
                    prediction, historical_errors, confidence_level, model_uncertainty
                )
            elif method == PredictionIntervalMethod.QUANTILE:
                return self._calculate_quantile_prediction_interval(
                    prediction, historical_errors, confidence_level
                )
            elif method == PredictionIntervalMethod.BOOTSTRAP:
                return self._calculate_bootstrap_prediction_interval(
                    prediction, historical_errors, confidence_level
                )
            elif method == PredictionIntervalMethod.CONFORMAL:
                return self._calculate_conformal_prediction_interval(
                    prediction, historical_errors, confidence_level
                )
            elif method == PredictionIntervalMethod.BAYESIAN:
                return self._calculate_bayesian_prediction_interval(
                    prediction, historical_errors, confidence_level, model_uncertainty
                )
            else:
                raise ValueError(f"Método não suportado: {method}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao calcular intervalo de predição: {e}")
            return self._empty_prediction_interval()
    
    def _calculate_normal_prediction_interval(self,
                                            prediction: float,
                                            historical_errors: Optional[List[float]],
                                            confidence_level: float,
                                            model_uncertainty: Optional[float]) -> PredictionInterval:
        """Calcula intervalo de predição usando distribuição normal"""
        try:
            if historical_errors is not None and len(historical_errors) > 0:
                # Usar erros históricos para estimar variabilidade
                error_std = np.std(historical_errors)
                sample_size = len(historical_errors)
            elif model_uncertainty is not None:
                # Usar incerteza do modelo fornecida
                error_std = model_uncertainty
                sample_size = 100  # Assumir amostra razoável
            else:
                # Usar incerteza padrão baseada no tipo de previsão
                if prediction <= 1.0:  # Probabilidade
                    error_std = 0.05  # 5% de incerteza padrão
                else:  # Odds ou outros valores
                    error_std = prediction * 0.1  # 10% de incerteza relativa
                sample_size = 50
            
            # Calcular erro padrão da predição
            prediction_std = error_std * np.sqrt(1 + 1/sample_size)
            
            # Calcular margem de erro
            if sample_size < 30:
                df = sample_size - 1
                t_value = stats.t.ppf((1 + confidence_level) / 2, df)
                margin_of_error = t_value * prediction_std
            else:
                z_value = stats.norm.ppf((1 + confidence_level) / 2)
                margin_of_error = z_value * prediction_std
            
            # Calcular limites
            lower_bound = prediction - margin_of_error
            upper_bound = prediction + margin_of_error
            interval_width = upper_bound - lower_bound
            
            return PredictionInterval(
                prediction=prediction,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence_level=confidence_level,
                interval_width=interval_width,
                method="normal",
                sample_size=sample_size
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo normal: {e}")
            return self._empty_prediction_interval()
    
    def _calculate_quantile_prediction_interval(self,
                                              prediction: float,
                                              historical_errors: Optional[List[float]],
                                              confidence_level: float) -> PredictionInterval:
        """Calcula intervalo de predição usando quantis empíricos"""
        try:
            if historical_errors is None or len(historical_errors) == 0:
                # Usar distribuição normal como fallback
                return self._calculate_normal_prediction_interval(
                    prediction, None, confidence_level, None
                )
            
            # Calcular quantis dos erros históricos
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100
            
            lower_error = np.percentile(historical_errors, lower_percentile)
            upper_error = np.percentile(historical_errors, upper_percentile)
            
            # Calcular limites
            lower_bound = prediction + lower_error
            upper_bound = prediction + upper_error
            interval_width = upper_bound - lower_bound
            
            return PredictionInterval(
                prediction=prediction,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence_level=confidence_level,
                interval_width=interval_width,
                method="quantile",
                sample_size=len(historical_errors)
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo quantile: {e}")
            return self._empty_prediction_interval()
    
    def _calculate_bootstrap_prediction_interval(self,
                                               prediction: float,
                                               historical_errors: Optional[List[float]],
                                               confidence_level: float) -> PredictionInterval:
        """Calcula intervalo de predição usando bootstrap"""
        try:
            if historical_errors is None or len(historical_errors) == 0:
                # Usar distribuição normal como fallback
                return self._calculate_normal_prediction_interval(
                    prediction, None, confidence_level, None
                )
            
            # Bootstrap sampling dos erros
            bootstrap_predictions = []
            for _ in range(self.bootstrap_samples):
                bootstrap_errors = np.random.choice(historical_errors, 
                                                  size=len(historical_errors), 
                                                  replace=True)
                bootstrap_prediction = prediction + np.mean(bootstrap_errors)
                bootstrap_predictions.append(bootstrap_prediction)
            
            bootstrap_predictions = np.array(bootstrap_predictions)
            
            # Calcular quantis
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100
            
            lower_bound = np.percentile(bootstrap_predictions, lower_percentile)
            upper_bound = np.percentile(bootstrap_predictions, upper_percentile)
            interval_width = upper_bound - lower_bound
            
            return PredictionInterval(
                prediction=prediction,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence_level=confidence_level,
                interval_width=interval_width,
                method="bootstrap",
                sample_size=len(historical_errors)
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo bootstrap: {e}")
            return self._empty_prediction_interval()
    
    def _calculate_conformal_prediction_interval(self,
                                               prediction: float,
                                               historical_errors: Optional[List[float]],
                                               confidence_level: float) -> PredictionInterval:
        """Calcula intervalo de predição usando conformal prediction"""
        try:
            if historical_errors is None or len(historical_errors) == 0:
                # Usar distribuição normal como fallback
                return self._calculate_normal_prediction_interval(
                    prediction, None, confidence_level, None
                )
            
            # Calcular quantil de conformal prediction
            alpha = 1 - confidence_level
            quantile_level = 1 - alpha
            
            # Usar quantil dos erros absolutos
            abs_errors = np.abs(historical_errors)
            conformal_quantile = np.quantile(abs_errors, quantile_level)
            
            # Calcular limites
            lower_bound = prediction - conformal_quantile
            upper_bound = prediction + conformal_quantile
            interval_width = upper_bound - lower_bound
            
            return PredictionInterval(
                prediction=prediction,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence_level=confidence_level,
                interval_width=interval_width,
                method="conformal",
                sample_size=len(historical_errors)
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo conformal: {e}")
            return self._empty_prediction_interval()
    
    def _calculate_bayesian_prediction_interval(self,
                                              prediction: float,
                                              historical_errors: Optional[List[float]],
                                              confidence_level: float,
                                              model_uncertainty: Optional[float]) -> PredictionInterval:
        """Calcula intervalo de predição usando abordagem bayesiana"""
        try:
            if historical_errors is not None and len(historical_errors) > 0:
                # Usar erros históricos para estimar parâmetros
                error_mean = np.mean(historical_errors)
                error_std = np.std(historical_errors)
                n = len(historical_errors)
            elif model_uncertainty is not None:
                error_mean = 0
                error_std = model_uncertainty
                n = 100
            else:
                error_mean = 0
                error_std = prediction * 0.1
                n = 50
            
            # Distribuição posterior (assumindo normal)
            posterior_std = error_std * np.sqrt(1 + 1/n)
            
            # Calcular intervalo de credibilidade
            alpha = 1 - confidence_level
            z_value = stats.norm.ppf((1 + confidence_level) / 2)
            margin_of_error = z_value * posterior_std
            
            # Calcular limites
            lower_bound = prediction - margin_of_error
            upper_bound = prediction + margin_of_error
            interval_width = upper_bound - lower_bound
            
            return PredictionInterval(
                prediction=prediction,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence_level=confidence_level,
                interval_width=interval_width,
                method="bayesian",
                sample_size=n
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo bayesiano: {e}")
            return self._empty_prediction_interval()
    
    def calculate_multiple_prediction_intervals(self,
                                              predictions: List[float],
                                              historical_errors: Optional[List[List[float]]] = None,
                                              confidence_levels: List[float] = [0.68, 0.80, 0.90, 0.95, 0.99],
                                              method: PredictionIntervalMethod = PredictionIntervalMethod.NORMAL) -> Dict[float, List[PredictionInterval]]:
        """
        Calcula intervalos de predição para múltiplas previsões e níveis
        
        Args:
            predictions: Lista de previsões
            historical_errors: Lista de erros históricos por previsão
            confidence_levels: Lista de níveis de confiança
            method: Método de cálculo
            
        Returns:
            Dicionário com intervalos por nível de confiança
        """
        try:
            results = {}
            
            for level in confidence_levels:
                level_intervals = []
                
                for i, pred in enumerate(predictions):
                    errors = historical_errors[i] if historical_errors and i < len(historical_errors) else None
                    
                    interval = self.calculate_prediction_interval(
                        pred, errors, method, level
                    )
                    level_intervals.append(interval)
                
                results[level] = level_intervals
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular múltiplos intervalos: {e}")
            return {}
    
    def evaluate_prediction_intervals(self,
                                    intervals: List[PredictionInterval],
                                    actual_values: List[float]) -> PredictionIntervalMetrics:
        """
        Avalia qualidade dos intervalos de predição
        
        Args:
            intervals: Lista de intervalos de predição
            actual_values: Valores reais correspondentes
            
        Returns:
            Métricas de qualidade dos intervalos
        """
        try:
            if len(intervals) != len(actual_values):
                raise ValueError("Número de intervalos deve ser igual ao número de valores reais")
            
            # Calcular taxa de cobertura
            covered = 0
            for interval, actual in zip(intervals, actual_values):
                if interval.lower_bound <= actual <= interval.upper_bound:
                    covered += 1
            
            coverage_rate = covered / len(intervals)
            
            # Calcular métricas de largura
            widths = [interval.interval_width for interval in intervals]
            average_width = np.mean(widths)
            width_std = np.std(widths)
            
            # Calcular score de calibração
            calibration_score = self._calculate_calibration_score(intervals, actual_values)
            
            # Calcular score de sharpness (precisão)
            sharpness_score = self._calculate_sharpness_score(intervals)
            
            # Calcular score de confiabilidade
            reliability_score = self._calculate_reliability_score(intervals, actual_values)
            
            return PredictionIntervalMetrics(
                coverage_rate=coverage_rate,
                average_width=average_width,
                width_std=width_std,
                calibration_score=calibration_score,
                sharpness_score=sharpness_score,
                reliability_score=reliability_score,
                total_predictions=len(intervals)
            )
            
        except Exception as e:
            logger.error(f"❌ Erro na avaliação de intervalos: {e}")
            return self._empty_prediction_interval_metrics()
    
    def _calculate_calibration_score(self, 
                                   intervals: List[PredictionInterval],
                                   actual_values: List[float]) -> float:
        """Calcula score de calibração dos intervalos"""
        try:
            if not intervals or not actual_values:
                return 0.0
            
            # Calcular taxa de cobertura para cada nível de confiança
            confidence_levels = list(set(interval.confidence_level for interval in intervals))
            calibration_scores = []
            
            for level in confidence_levels:
                level_intervals = [i for i in intervals if i.confidence_level == level]
                level_actuals = [actual_values[i] for i, interval in enumerate(intervals) 
                               if interval.confidence_level == level]
                
                if not level_intervals:
                    continue
                
                covered = sum(1 for interval, actual in zip(level_intervals, level_actuals)
                            if interval.lower_bound <= actual <= interval.upper_bound)
                
                actual_coverage = covered / len(level_intervals)
                expected_coverage = level
                
                # Score baseado na diferença entre cobertura real e esperada
                calibration_error = abs(actual_coverage - expected_coverage)
                calibration_score = max(0, 100 - (calibration_error * 100))
                calibration_scores.append(calibration_score)
            
            return np.mean(calibration_scores) if calibration_scores else 0.0
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de calibração: {e}")
            return 0.0
    
    def _calculate_sharpness_score(self, intervals: List[PredictionInterval]) -> float:
        """Calcula score de sharpness (precisão) dos intervalos"""
        try:
            if not intervals:
                return 0.0
            
            # Sharpness é inversamente proporcional à largura média dos intervalos
            widths = [interval.interval_width for interval in intervals]
            mean_width = np.mean(widths)
            
            # Normalizar baseado no valor médio das previsões
            mean_prediction = np.mean([interval.prediction for interval in intervals])
            relative_width = mean_width / abs(mean_prediction) if mean_prediction != 0 else mean_width
            
            # Converter para score 0-100 (menor largura = maior sharpness)
            sharpness_score = max(0, 100 - (relative_width * 100))
            
            return min(100, sharpness_score)
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de sharpness: {e}")
            return 0.0
    
    def _calculate_reliability_score(self, 
                                   intervals: List[PredictionInterval],
                                   actual_values: List[float]) -> float:
        """Calcula score de confiabilidade dos intervalos"""
        try:
            if not intervals or not actual_values:
                return 0.0
            
            # Calcular consistência da cobertura
            coverage_rates = []
            confidence_levels = list(set(interval.confidence_level for interval in intervals))
            
            for level in confidence_levels:
                level_intervals = [i for i in intervals if i.confidence_level == level]
                level_actuals = [actual_values[i] for i, interval in enumerate(intervals) 
                               if interval.confidence_level == level]
                
                if not level_intervals:
                    continue
                
                covered = sum(1 for interval, actual in zip(level_intervals, level_actuals)
                            if interval.lower_bound <= actual <= interval.upper_bound)
                
                coverage_rate = covered / len(level_intervals)
                coverage_rates.append(coverage_rate)
            
            if not coverage_rates:
                return 0.0
            
            # Score baseado na consistência das taxas de cobertura
            coverage_std = np.std(coverage_rates)
            reliability_score = max(0, 100 - (coverage_std * 100))
            
            return min(100, reliability_score)
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de confiabilidade: {e}")
            return 0.0
    
    def format_prediction_interval(self, 
                                 interval: PredictionInterval,
                                 decimal_places: int = 1) -> str:
        """
        Formata intervalo de predição para exibição
        
        Args:
            interval: Intervalo de predição
            decimal_places: Número de casas decimais
            
        Returns:
            String formatada (ex: "82% ± 5%")
        """
        try:
            prediction = interval.prediction
            margin = interval.interval_width / 2
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
    
    def _empty_prediction_interval(self) -> PredictionInterval:
        """Retorna intervalo vazio"""
        return PredictionInterval(
            prediction=0.0,
            lower_bound=0.0,
            upper_bound=0.0,
            confidence_level=0.95,
            interval_width=0.0,
            method="none",
            sample_size=0
        )
    
    def _empty_prediction_interval_metrics(self) -> PredictionIntervalMetrics:
        """Retorna métricas vazias"""
        return PredictionIntervalMetrics(
            coverage_rate=0.0,
            average_width=0.0,
            width_std=0.0,
            calibration_score=0.0,
            sharpness_score=0.0,
            reliability_score=0.0,
            total_predictions=0
        )
