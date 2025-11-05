"""
Sistema de Bootstrap para Confiança - MaraBet AI
Implementação de bootstrap para cálculo de intervalos de confiança
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import scipy.stats as stats
from sklearn.utils import resample
import warnings

logger = logging.getLogger(__name__)

@dataclass
class BootstrapResult:
    """Resultado do bootstrap"""
    original_statistic: float
    bootstrap_statistics: np.ndarray
    confidence_interval: Tuple[float, float]
    confidence_level: float
    bias: float
    standard_error: float
    bootstrap_samples: int
    method: str

@dataclass
class BootstrapMetrics:
    """Métricas do bootstrap"""
    mean_bias: float
    bias_std: float
    coverage_rate: float
    interval_width: float
    efficiency: float
    stability: float

class BootstrapConfidence:
    """
    Sistema de bootstrap para cálculo de intervalos de confiança
    Implementa múltiplas variantes do bootstrap
    """
    
    def __init__(self, 
                 n_bootstrap: int = 1000,
                 random_state: int = 42,
                 confidence_level: float = 0.95):
        """
        Inicializa o sistema de bootstrap
        
        Args:
            n_bootstrap: Número de amostras bootstrap
            random_state: Seed para reprodutibilidade
            confidence_level: Nível de confiança padrão
        """
        self.n_bootstrap = n_bootstrap
        self.random_state = random_state
        self.confidence_level = confidence_level
        np.random.seed(random_state)
        
        logger.info(f"BootstrapConfidence inicializado - {n_bootstrap} amostras, {confidence_level*100:.0f}% confiança")
    
    def bootstrap_confidence_interval(self,
                                    data: Union[List[float], np.ndarray],
                                    statistic_func: callable = np.mean,
                                    method: str = "percentile",
                                    confidence_level: Optional[float] = None) -> BootstrapResult:
        """
        Calcula intervalo de confiança usando bootstrap
        
        Args:
            data: Dados para bootstrap
            statistic_func: Função estatística a ser calculada
            method: Método de bootstrap ("percentile", "bias_corrected", "studentized")
            confidence_level: Nível de confiança
            
        Returns:
            Resultado do bootstrap
        """
        try:
            if confidence_level is None:
                confidence_level = self.confidence_level
            
            data = np.array(data)
            original_statistic = statistic_func(data)
            
            # Gerar amostras bootstrap
            bootstrap_statistics = self._generate_bootstrap_samples(
                data, statistic_func, self.n_bootstrap
            )
            
            # Calcular intervalo de confiança baseado no método
            if method == "percentile":
                ci_lower, ci_upper = self._percentile_confidence_interval(
                    bootstrap_statistics, confidence_level
                )
            elif method == "bias_corrected":
                ci_lower, ci_upper = self._bias_corrected_confidence_interval(
                    bootstrap_statistics, original_statistic, confidence_level
                )
            elif method == "studentized":
                ci_lower, ci_upper = self._studentized_confidence_interval(
                    data, statistic_func, bootstrap_statistics, confidence_level
                )
            else:
                raise ValueError(f"Método não suportado: {method}")
            
            # Calcular métricas
            bias = np.mean(bootstrap_statistics) - original_statistic
            standard_error = np.std(bootstrap_statistics)
            
            return BootstrapResult(
                original_statistic=original_statistic,
                bootstrap_statistics=bootstrap_statistics,
                confidence_interval=(ci_lower, ci_upper),
                confidence_level=confidence_level,
                bias=bias,
                standard_error=standard_error,
                bootstrap_samples=self.n_bootstrap,
                method=method
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no bootstrap: {e}")
            return self._empty_bootstrap_result()
    
    def _generate_bootstrap_samples(self,
                                  data: np.ndarray,
                                  statistic_func: callable,
                                  n_bootstrap: int) -> np.ndarray:
        """Gera amostras bootstrap"""
        try:
            bootstrap_statistics = []
            
            for _ in range(n_bootstrap):
                # Amostragem com reposição
                bootstrap_sample = resample(data, random_state=self.random_state)
                bootstrap_statistic = statistic_func(bootstrap_sample)
                bootstrap_statistics.append(bootstrap_statistic)
            
            return np.array(bootstrap_statistics)
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de amostras bootstrap: {e}")
            return np.array([])
    
    def _percentile_confidence_interval(self,
                                      bootstrap_statistics: np.ndarray,
                                      confidence_level: float) -> Tuple[float, float]:
        """Calcula intervalo de confiança usando método percentil"""
        try:
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100
            
            ci_lower = np.percentile(bootstrap_statistics, lower_percentile)
            ci_upper = np.percentile(bootstrap_statistics, upper_percentile)
            
            return ci_lower, ci_upper
            
        except Exception as e:
            logger.error(f"❌ Erro no método percentil: {e}")
            return 0.0, 0.0
    
    def _bias_corrected_confidence_interval(self,
                                          bootstrap_statistics: np.ndarray,
                                          original_statistic: float,
                                          confidence_level: float) -> Tuple[float, float]:
        """Calcula intervalo de confiança usando método bias-corrected"""
        try:
            # Calcular viés
            bias = np.mean(bootstrap_statistics) - original_statistic
            
            # Ajustar estatísticas bootstrap
            bias_corrected_statistics = bootstrap_statistics - bias
            
            # Calcular percentis
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100
            
            ci_lower = np.percentile(bias_corrected_statistics, lower_percentile)
            ci_upper = np.percentile(bias_corrected_statistics, upper_percentile)
            
            return ci_lower, ci_upper
            
        except Exception as e:
            logger.error(f"❌ Erro no método bias-corrected: {e}")
            return 0.0, 0.0
    
    def _studentized_confidence_interval(self,
                                       data: np.ndarray,
                                       statistic_func: callable,
                                       bootstrap_statistics: np.ndarray,
                                       confidence_level: float) -> Tuple[float, float]:
        """Calcula intervalo de confiança usando método studentized"""
        try:
            original_statistic = statistic_func(data)
            
            # Calcular erro padrão bootstrap
            bootstrap_se = np.std(bootstrap_statistics)
            
            # Calcular estatísticas t bootstrap
            t_statistics = (bootstrap_statistics - original_statistic) / bootstrap_se
            
            # Calcular percentis das estatísticas t
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100
            
            t_lower = np.percentile(t_statistics, lower_percentile)
            t_upper = np.percentile(t_statistics, upper_percentile)
            
            # Calcular intervalo de confiança
            ci_lower = original_statistic - t_upper * bootstrap_se
            ci_upper = original_statistic - t_lower * bootstrap_se
            
            return ci_lower, ci_upper
            
        except Exception as e:
            logger.error(f"❌ Erro no método studentized: {e}")
            return 0.0, 0.0
    
    def bootstrap_prediction_interval(self,
                                    predictions: List[float],
                                    actual_values: List[float],
                                    confidence_level: Optional[float] = None) -> BootstrapResult:
        """
        Calcula intervalo de predição usando bootstrap
        
        Args:
            predictions: Lista de previsões
            actual_values: Lista de valores reais
            confidence_level: Nível de confiança
            
        Returns:
            Resultado do bootstrap para predição
        """
        try:
            if confidence_level is None:
                confidence_level = self.confidence_level
            
            predictions = np.array(predictions)
            actual_values = np.array(actual_values)
            
            # Calcular erros de predição
            errors = actual_values - predictions
            
            # Bootstrap dos erros
            bootstrap_errors = self._generate_bootstrap_samples(
                errors, np.mean, self.n_bootstrap
            )
            
            # Calcular previsão média
            mean_prediction = np.mean(predictions)
            
            # Calcular intervalo de confiança dos erros
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100
            
            error_lower = np.percentile(bootstrap_errors, lower_percentile)
            error_upper = np.percentile(bootstrap_errors, upper_percentile)
            
            # Calcular intervalo de predição
            pred_lower = mean_prediction + error_lower
            pred_upper = mean_prediction + error_upper
            
            return BootstrapResult(
                original_statistic=mean_prediction,
                bootstrap_statistics=bootstrap_errors,
                confidence_interval=(pred_lower, pred_upper),
                confidence_level=confidence_level,
                bias=np.mean(bootstrap_errors),
                standard_error=np.std(bootstrap_errors),
                bootstrap_samples=self.n_bootstrap,
                method="prediction"
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no bootstrap de predição: {e}")
            return self._empty_bootstrap_result()
    
    def compare_bootstrap_methods(self,
                                data: Union[List[float], np.ndarray],
                                statistic_func: callable = np.mean,
                                confidence_levels: List[float] = [0.68, 0.80, 0.90, 0.95, 0.99]) -> Dict[str, Dict[float, BootstrapResult]]:
        """
        Compara diferentes métodos de bootstrap
        
        Args:
            data: Dados para análise
            statistic_func: Função estatística
            confidence_levels: Níveis de confiança para comparar
            
        Returns:
            Dicionário com resultados por método e nível
        """
        try:
            methods = ["percentile", "bias_corrected", "studentized"]
            results = {}
            
            for method in methods:
                method_results = {}
                
                for level in confidence_levels:
                    result = self.bootstrap_confidence_interval(
                        data, statistic_func, method, level
                    )
                    method_results[level] = result
                
                results[method] = method_results
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro na comparação de métodos: {e}")
            return {}
    
    def evaluate_bootstrap_quality(self,
                                 bootstrap_results: List[BootstrapResult],
                                 true_values: Optional[List[float]] = None) -> BootstrapMetrics:
        """
        Avalia qualidade dos resultados bootstrap
        
        Args:
            bootstrap_results: Lista de resultados bootstrap
            true_values: Valores verdadeiros (opcional)
            
        Returns:
            Métricas de qualidade do bootstrap
        """
        try:
            if not bootstrap_results:
                return self._empty_bootstrap_metrics()
            
            # Calcular métricas de viés
            biases = [result.bias for result in bootstrap_results]
            mean_bias = np.mean(np.abs(biases))
            bias_std = np.std(biases)
            
            # Calcular taxa de cobertura (se valores verdadeiros disponíveis)
            if true_values and len(true_values) == len(bootstrap_results):
                covered = 0
                for result, true_val in zip(bootstrap_results, true_values):
                    ci_lower, ci_upper = result.confidence_interval
                    if ci_lower <= true_val <= ci_upper:
                        covered += 1
                coverage_rate = covered / len(bootstrap_results)
            else:
                coverage_rate = 0.0
            
            # Calcular largura média dos intervalos
            interval_widths = []
            for result in bootstrap_results:
                ci_lower, ci_upper = result.confidence_interval
                width = ci_upper - ci_lower
                interval_widths.append(width)
            
            average_width = np.mean(interval_widths)
            
            # Calcular eficiência (inversamente proporcional à largura)
            efficiency = 100 / (1 + average_width) if average_width > 0 else 0
            
            # Calcular estabilidade (consistência dos resultados)
            standard_errors = [result.standard_error for result in bootstrap_results]
            stability = 100 - (np.std(standard_errors) / np.mean(standard_errors) * 100) if np.mean(standard_errors) > 0 else 0
            
            return BootstrapMetrics(
                mean_bias=mean_bias,
                bias_std=bias_std,
                coverage_rate=coverage_rate,
                interval_width=average_width,
                efficiency=efficiency,
                stability=stability
            )
            
        except Exception as e:
            logger.error(f"❌ Erro na avaliação de qualidade: {e}")
            return self._empty_bootstrap_metrics()
    
    def bootstrap_uncertainty_analysis(self,
                                     predictions: List[float],
                                     actual_values: List[float],
                                     confidence_levels: List[float] = [0.68, 0.80, 0.90, 0.95, 0.99]) -> Dict[str, Any]:
        """
        Análise completa de incerteza usando bootstrap
        
        Args:
            predictions: Lista de previsões
            actual_values: Lista de valores reais
            confidence_levels: Níveis de confiança
            
        Returns:
            Análise completa de incerteza
        """
        try:
            predictions = np.array(predictions)
            actual_values = np.array(actual_values)
            
            # Calcular erros
            errors = actual_values - predictions
            
            # Bootstrap para diferentes níveis de confiança
            bootstrap_results = {}
            for level in confidence_levels:
                result = self.bootstrap_confidence_interval(
                    errors, np.mean, "percentile", level
                )
                bootstrap_results[level] = result
            
            # Avaliar qualidade
            quality_metrics = self.evaluate_bootstrap_quality(
                list(bootstrap_results.values()), actual_values
            )
            
            # Calcular métricas de incerteza
            uncertainty_metrics = {
                'mean_uncertainty': np.mean([abs(e) for e in errors]),
                'uncertainty_std': np.std([abs(e) for e in errors]),
                'prediction_accuracy': 100 - (np.mean([abs(e) for e in errors]) / np.mean(actual_values) * 100),
                'coverage_rates': {
                    level: self._calculate_coverage_rate(result, actual_values)
                    for level, result in bootstrap_results.items()
                }
            }
            
            return {
                'bootstrap_results': bootstrap_results,
                'quality_metrics': quality_metrics,
                'uncertainty_metrics': uncertainty_metrics,
                'recommendations': self._generate_bootstrap_recommendations(quality_metrics, uncertainty_metrics)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de incerteza bootstrap: {e}")
            return {}
    
    def _calculate_coverage_rate(self, 
                               result: BootstrapResult,
                               actual_values: List[float]) -> float:
        """Calcula taxa de cobertura para um resultado bootstrap"""
        try:
            ci_lower, ci_upper = result.confidence_interval
            covered = sum(1 for val in actual_values if ci_lower <= val <= ci_upper)
            return covered / len(actual_values) * 100
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de cobertura: {e}")
            return 0.0
    
    def _generate_bootstrap_recommendations(self,
                                          quality_metrics: BootstrapMetrics,
                                          uncertainty_metrics: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na análise bootstrap"""
        try:
            recommendations = []
            
            # Recomendações baseadas no viés
            if quality_metrics.mean_bias > 0.1:
                recommendations.append("⚠️ Alto viés detectado no bootstrap. Considere aumentar o número de amostras ou verificar a qualidade dos dados.")
            elif quality_metrics.mean_bias < 0.01:
                recommendations.append("✅ Baixo viés - bootstrap bem calibrado.")
            else:
                recommendations.append("📊 Viés moderado - monitore a qualidade do bootstrap.")
            
            # Recomendações baseadas na cobertura
            if quality_metrics.coverage_rate > 0:
                if quality_metrics.coverage_rate > 95:
                    recommendations.append("🎯 Excelente cobertura - intervalos de confiança precisos.")
                elif quality_metrics.coverage_rate > 90:
                    recommendations.append("✅ Boa cobertura - intervalos de confiança adequados.")
                else:
                    recommendations.append("⚠️ Baixa cobertura - intervalos podem estar subestimados.")
            
            # Recomendações baseadas na eficiência
            if quality_metrics.efficiency > 80:
                recommendations.append("⚡ Alta eficiência - intervalos precisos e informativos.")
            elif quality_metrics.efficiency > 60:
                recommendations.append("📊 Eficiência moderada - intervalos adequados.")
            else:
                recommendations.append("🔍 Baixa eficiência - considere otimizar o método de bootstrap.")
            
            # Recomendações baseadas na estabilidade
            if quality_metrics.stability > 90:
                recommendations.append("🛡️ Alta estabilidade - resultados consistentes.")
            elif quality_metrics.stability > 70:
                recommendations.append("📈 Estabilidade moderada - resultados razoavelmente consistentes.")
            else:
                recommendations.append("⚠️ Baixa estabilidade - considere aumentar o número de amostras bootstrap.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar recomendações: {e}")
            return []
    
    def _empty_bootstrap_result(self) -> BootstrapResult:
        """Retorna resultado bootstrap vazio"""
        return BootstrapResult(
            original_statistic=0.0,
            bootstrap_statistics=np.array([]),
            confidence_interval=(0.0, 0.0),
            confidence_level=0.95,
            bias=0.0,
            standard_error=0.0,
            bootstrap_samples=0,
            method="none"
        )
    
    def _empty_bootstrap_metrics(self) -> BootstrapMetrics:
        """Retorna métricas bootstrap vazias"""
        return BootstrapMetrics(
            mean_bias=0.0,
            bias_std=0.0,
            coverage_rate=0.0,
            interval_width=0.0,
            efficiency=0.0,
            stability=0.0
        )
