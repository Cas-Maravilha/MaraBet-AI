"""
Analisador de Incerteza - MaraBet AI
Análise detalhada de incerteza e confiabilidade das previsões
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.calibration import calibration_curve
import warnings

from .confidence_calculator import ConfidenceCalculator, ConfidenceInterval, PredictionUncertainty

logger = logging.getLogger(__name__)

@dataclass
class UncertaintyMetrics:
    """Métricas de incerteza agregadas"""
    mean_uncertainty: float
    uncertainty_std: float
    reliability_score: float
    calibration_score: float
    overconfidence_rate: float
    underconfidence_rate: float
    prediction_accuracy: float
    confidence_accuracy: float

@dataclass
class UncertaintyReport:
    """Relatório completo de incerteza"""
    overall_metrics: UncertaintyMetrics
    method_comparison: Dict[str, Dict[str, float]]
    temporal_analysis: Dict[str, Any]
    league_analysis: Dict[str, UncertaintyMetrics]
    recommendations: List[str]

class UncertaintyAnalyzer:
    """
    Analisador de incerteza para previsões do MaraBet AI
    Avalia qualidade e confiabilidade das incertezas
    """
    
    def __init__(self, confidence_calculator: Optional[ConfidenceCalculator] = None):
        """
        Inicializa o analisador de incerteza
        
        Args:
            confidence_calculator: Calculador de confiança (opcional)
        """
        self.confidence_calculator = confidence_calculator or ConfidenceCalculator()
        self.uncertainty_data: List[PredictionUncertainty] = []
        
        logger.info("UncertaintyAnalyzer inicializado")
    
    def analyze_prediction_uncertainty(self,
                                     predictions: List[float],
                                     actual_values: List[float],
                                     confidence_levels: List[float] = [0.68, 0.80, 0.90, 0.95, 0.99],
                                     method: str = "normal") -> UncertaintyReport:
        """
        Analisa incerteza de um conjunto de previsões
        
        Args:
            predictions: Lista de previsões
            actual_values: Lista de valores reais
            confidence_levels: Níveis de confiança para análise
            method: Método de cálculo
            
        Returns:
            Relatório completo de incerteza
        """
        try:
            logger.info(f"🔍 Analisando incerteza de {len(predictions)} previsões")
            
            # Calcular incerteza para cada previsão
            uncertainties = []
            for i, pred in enumerate(predictions):
                actual = actual_values[i] if i < len(actual_values) else None
                uncertainty = self.confidence_calculator.calculate_prediction_uncertainty(
                    [pred], [actual] if actual is not None else None
                )
                uncertainties.append(uncertainty)
            
            self.uncertainty_data = uncertainties
            
            # Calcular métricas gerais
            overall_metrics = self._calculate_overall_metrics(uncertainties, actual_values)
            
            # Comparar métodos
            method_comparison = self._compare_methods(predictions, actual_values, confidence_levels)
            
            # Análise temporal
            temporal_analysis = self._analyze_temporal_patterns(uncertainties)
            
            # Análise por liga (se disponível)
            league_analysis = self._analyze_by_league(uncertainties)
            
            # Gerar recomendações
            recommendations = self._generate_recommendations(overall_metrics, method_comparison)
            
            return UncertaintyReport(
                overall_metrics=overall_metrics,
                method_comparison=method_comparison,
                temporal_analysis=temporal_analysis,
                league_analysis=league_analysis,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de incerteza: {e}")
            return self._empty_uncertainty_report()
    
    def _calculate_overall_metrics(self, 
                                 uncertainties: List[PredictionUncertainty],
                                 actual_values: List[float]) -> UncertaintyMetrics:
        """Calcula métricas gerais de incerteza"""
        try:
            if not uncertainties:
                return self._empty_uncertainty_metrics()
            
            # Métricas básicas
            uncertainty_scores = [u.uncertainty_score for u in uncertainties]
            reliability_scores = [u.reliability_score for u in uncertainties]
            calibration_scores = [u.calibration_score for u in uncertainties]
            
            mean_uncertainty = np.mean(uncertainty_scores)
            uncertainty_std = np.std(uncertainty_scores)
            reliability_score = np.mean(reliability_scores)
            calibration_score = np.mean(calibration_scores)
            
            # Análise de overconfidence/underconfidence
            overconfidence_rate, underconfidence_rate = self._analyze_confidence_bias(
                uncertainties, actual_values
            )
            
            # Precisão das previsões
            predictions = [u.mean_prediction for u in uncertainties]
            prediction_accuracy = self._calculate_prediction_accuracy(predictions, actual_values)
            
            # Precisão das incertezas
            confidence_accuracy = self._calculate_confidence_accuracy(uncertainties, actual_values)
            
            return UncertaintyMetrics(
                mean_uncertainty=mean_uncertainty,
                uncertainty_std=uncertainty_std,
                reliability_score=reliability_score,
                calibration_score=calibration_score,
                overconfidence_rate=overconfidence_rate,
                underconfidence_rate=underconfidence_rate,
                prediction_accuracy=prediction_accuracy,
                confidence_accuracy=confidence_accuracy
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular métricas gerais: {e}")
            return self._empty_uncertainty_metrics()
    
    def _analyze_confidence_bias(self, 
                               uncertainties: List[PredictionUncertainty],
                               actual_values: List[float]) -> Tuple[float, float]:
        """Analisa viés de confiança (overconfidence/underconfidence)"""
        try:
            if not actual_values or len(uncertainties) != len(actual_values):
                return 0.0, 0.0
            
            overconfident = 0
            underconfident = 0
            total = len(uncertainties)
            
            for uncertainty, actual in zip(uncertainties, actual_values):
                # Usar intervalo de 95% como referência
                if 0.95 in uncertainty.confidence_intervals:
                    interval = uncertainty.confidence_intervals[0.95]
                    
                    if actual < interval.lower_bound or actual > interval.upper_bound:
                        # Valor real fora do intervalo de 95% = overconfident
                        overconfident += 1
                    else:
                        # Verificar se está muito próximo dos limites (underconfident)
                        margin = interval.margin_of_error
                        distance_from_center = abs(actual - interval.prediction)
                        
                        if distance_from_center < margin * 0.3:  # Muito próximo do centro
                            underconfident += 1
            
            overconfidence_rate = (overconfident / total) * 100
            underconfidence_rate = (underconfident / total) * 100
            
            return overconfidence_rate, underconfidence_rate
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de viés: {e}")
            return 0.0, 0.0
    
    def _calculate_prediction_accuracy(self, 
                                     predictions: List[float],
                                     actual_values: List[float]) -> float:
        """Calcula precisão das previsões"""
        try:
            if not actual_values or len(predictions) != len(actual_values):
                return 0.0
            
            # Calcular MAE (Mean Absolute Error)
            mae = mean_absolute_error(actual_values, predictions)
            
            # Calcular RMSE (Root Mean Square Error)
            rmse = np.sqrt(mean_squared_error(actual_values, predictions))
            
            # Calcular MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((np.array(actual_values) - np.array(predictions)) / np.array(actual_values))) * 100
            
            # Score combinado (0-100, maior = melhor)
            accuracy_score = max(0, 100 - (mape + rmse * 10))
            
            return min(100, accuracy_score)
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de precisão: {e}")
            return 0.0
    
    def _calculate_confidence_accuracy(self, 
                                     uncertainties: List[PredictionUncertainty],
                                     actual_values: List[float]) -> float:
        """Calcula precisão das incertezas (calibração)"""
        try:
            if not actual_values or len(uncertainties) != len(actual_values):
                return 0.0
            
            # Verificar quantas previsões estão dentro dos intervalos de confiança
            correct_predictions = 0
            total_predictions = len(uncertainties)
            
            for uncertainty, actual in zip(uncertainties, actual_values):
                if 0.95 in uncertainty.confidence_intervals:
                    interval = uncertainty.confidence_intervals[0.95]
                    if interval.lower_bound <= actual <= interval.upper_bound:
                        correct_predictions += 1
            
            # Calcular taxa de acerto
            accuracy_rate = (correct_predictions / total_predictions) * 100
            
            # Ajustar para 95% (nível de confiança esperado)
            expected_rate = 95.0
            calibration_accuracy = max(0, 100 - abs(accuracy_rate - expected_rate))
            
            return calibration_accuracy
            
        except Exception as e:
            logger.error(f"❌ Erro no cálculo de precisão de confiança: {e}")
            return 0.0
    
    def _compare_methods(self, 
                        predictions: List[float],
                        actual_values: List[float],
                        confidence_levels: List[float]) -> Dict[str, Dict[str, float]]:
        """Compara diferentes métodos de cálculo de confiança"""
        try:
            methods = ["normal", "bootstrap", "quantile", "prediction", "bayesian"]
            comparison = {}
            
            for method in methods:
                method_uncertainties = []
                
                for i, pred in enumerate(predictions):
                    actual = actual_values[i] if i < len(actual_values) else None
                    uncertainty = self.confidence_calculator.calculate_prediction_uncertainty(
                        [pred], [actual] if actual is not None else None
                    )
                    method_uncertainties.append(uncertainty)
                
                # Calcular métricas para este método
                metrics = self._calculate_overall_metrics(method_uncertainties, actual_values)
                
                comparison[method] = {
                    'mean_uncertainty': metrics.mean_uncertainty,
                    'reliability_score': metrics.reliability_score,
                    'calibration_score': metrics.calibration_score,
                    'overconfidence_rate': metrics.overconfidence_rate,
                    'confidence_accuracy': metrics.confidence_accuracy
                }
            
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Erro na comparação de métodos: {e}")
            return {}
    
    def _analyze_temporal_patterns(self, 
                                 uncertainties: List[PredictionUncertainty]) -> Dict[str, Any]:
        """Analisa padrões temporais de incerteza"""
        try:
            if not uncertainties:
                return {}
            
            # Extrair métricas temporais
            uncertainty_scores = [u.uncertainty_score for u in uncertainties]
            reliability_scores = [u.reliability_score for u in uncertainties]
            
            # Análise de tendência
            x = np.arange(len(uncertainty_scores))
            uncertainty_trend = np.polyfit(x, uncertainty_scores, 1)[0]
            reliability_trend = np.polyfit(x, reliability_scores, 1)[0]
            
            # Análise de volatilidade
            uncertainty_volatility = np.std(uncertainty_scores)
            reliability_volatility = np.std(reliability_scores)
            
            # Análise de autocorrelação
            uncertainty_autocorr = np.corrcoef(uncertainty_scores[:-1], uncertainty_scores[1:])[0, 1]
            reliability_autocorr = np.corrcoef(reliability_scores[:-1], reliability_scores[1:])[0, 1]
            
            return {
                'uncertainty_trend': uncertainty_trend,
                'reliability_trend': reliability_trend,
                'uncertainty_volatility': uncertainty_volatility,
                'reliability_volatility': reliability_volatility,
                'uncertainty_autocorrelation': uncertainty_autocorr,
                'reliability_autocorrelation': reliability_autocorr,
                'total_predictions': len(uncertainties)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise temporal: {e}")
            return {}
    
    def _analyze_by_league(self, 
                          uncertainties: List[PredictionUncertainty]) -> Dict[str, UncertaintyMetrics]:
        """Analisa incerteza por liga (se disponível)"""
        try:
            # Por enquanto, retornar análise geral
            # Em implementação completa, agruparia por liga
            if not uncertainties:
                return {}
            
            overall_metrics = self._calculate_overall_metrics(uncertainties, [])
            
            return {
                'overall': overall_metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise por liga: {e}")
            return {}
    
    def _generate_recommendations(self, 
                                overall_metrics: UncertaintyMetrics,
                                method_comparison: Dict[str, Dict[str, float]]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        try:
            recommendations = []
            
            # Recomendações baseadas na incerteza
            if overall_metrics.mean_uncertainty > 70:
                recommendations.append("⚠️ Alta incerteza detectada. Considere aumentar o tamanho da amostra ou melhorar a qualidade dos dados.")
            elif overall_metrics.mean_uncertainty < 30:
                recommendations.append("✅ Baixa incerteza - modelo confiável. Continue com a estratégia atual.")
            else:
                recommendations.append("📊 Incerteza moderada. Monitore a performance e ajuste conforme necessário.")
            
            # Recomendações baseadas na confiabilidade
            if overall_metrics.reliability_score > 80:
                recommendations.append("🎯 Alta confiabilidade detectada. O modelo é consistente e confiável.")
            elif overall_metrics.reliability_score < 50:
                recommendations.append("🔍 Baixa confiabilidade. Revise a consistência do modelo e dos dados.")
            else:
                recommendations.append("📈 Confiabilidade moderada. Há espaço para melhorias na consistência.")
            
            # Recomendações baseadas na calibração
            if overall_metrics.calibration_score > 90:
                recommendations.append("✅ Excelente calibração. As incertezas são precisas e confiáveis.")
            elif overall_metrics.calibration_score < 70:
                recommendations.append("⚠️ Calibração inadequada. As incertezas podem estar subestimadas ou superestimadas.")
            else:
                recommendations.append("📊 Calibração moderada. Monitore a precisão das incertezas.")
            
            # Recomendações baseadas no viés de confiança
            if overall_metrics.overconfidence_rate > 20:
                recommendations.append("🚨 Alto nível de overconfidence detectado. O modelo pode estar superestimando sua precisão.")
            elif overall_metrics.underconfidence_rate > 30:
                recommendations.append("📉 Alto nível de underconfidence detectado. O modelo pode estar sendo muito conservador.")
            else:
                recommendations.append("⚖️ Nível adequado de confiança. O modelo está bem calibrado.")
            
            # Recomendações baseadas na comparação de métodos
            if method_comparison:
                best_method = max(method_comparison.items(), 
                                key=lambda x: x[1]['calibration_score'])
                recommendations.append(f"🏆 Método recomendado: {best_method[0]} (melhor calibração: {best_method[1]['calibration_score']:.1f})")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar recomendações: {e}")
            return []
    
    def create_uncertainty_visualizations(self, 
                                        output_dir: str = "confidence/visualizations") -> bool:
        """Cria visualizações de incerteza"""
        try:
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            if not self.uncertainty_data:
                logger.warning("⚠️ Nenhum dado de incerteza para visualizar")
                return False
            
            # Configurar estilo
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            # 1. Distribuição de incerteza
            self._plot_uncertainty_distribution(output_dir)
            
            # 2. Análise de calibração
            self._plot_calibration_analysis(output_dir)
            
            # 3. Comparação de métodos
            self._plot_method_comparison(output_dir)
            
            # 4. Análise temporal
            self._plot_temporal_analysis(output_dir)
            
            logger.info(f"✅ Visualizações de incerteza criadas em {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar visualizações: {e}")
            return False
    
    def _plot_uncertainty_distribution(self, output_dir: str):
        """Cria gráfico de distribuição de incerteza"""
        try:
            uncertainty_scores = [u.uncertainty_score for u in self.uncertainty_data]
            reliability_scores = [u.reliability_score for u in self.uncertainty_data]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Distribuição de incerteza
            ax1.hist(uncertainty_scores, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax1.axvline(np.mean(uncertainty_scores), color='red', linestyle='--', 
                       label=f'Média: {np.mean(uncertainty_scores):.1f}')
            ax1.set_title('Distribuição de Incerteza', fontweight='bold')
            ax1.set_xlabel('Score de Incerteza')
            ax1.set_ylabel('Frequência')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Distribuição de confiabilidade
            ax2.hist(reliability_scores, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
            ax2.axvline(np.mean(reliability_scores), color='red', linestyle='--', 
                       label=f'Média: {np.mean(reliability_scores):.1f}')
            ax2.set_title('Distribuição de Confiabilidade', fontweight='bold')
            ax2.set_xlabel('Score de Confiabilidade')
            ax2.set_ylabel('Frequência')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/uncertainty_distribution.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico de distribuição: {e}")
    
    def _plot_calibration_analysis(self, output_dir: str):
        """Cria gráfico de análise de calibração"""
        try:
            # Simular dados de calibração
            n_bins = 10
            fraction_of_positives = np.linspace(0, 1, n_bins)
            mean_predicted_value = np.linspace(0, 1, n_bins)
            
            fig, ax = plt.subplots(1, 1, figsize=(8, 8))
            
            # Linha de calibração perfeita
            ax.plot([0, 1], [0, 1], 'k--', label='Calibração Perfeita')
            
            # Linha de calibração atual (simulada)
            ax.plot(mean_predicted_value, fraction_of_positives, 'b-', 
                   label='Calibração Atual', linewidth=2)
            
            ax.set_xlabel('Probabilidade Média Predita')
            ax.set_ylabel('Fração de Positivos')
            ax.set_title('Análise de Calibração', fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/calibration_analysis.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico de calibração: {e}")
    
    def _plot_method_comparison(self, output_dir: str):
        """Cria gráfico de comparação de métodos"""
        try:
            # Dados simulados para demonstração
            methods = ['Normal', 'Bootstrap', 'Quantile', 'Prediction', 'Bayesian']
            calibration_scores = [85, 88, 82, 90, 87]
            reliability_scores = [78, 82, 75, 85, 80]
            
            x = np.arange(len(methods))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            bars1 = ax.bar(x - width/2, calibration_scores, width, label='Calibração', alpha=0.8)
            bars2 = ax.bar(x + width/2, reliability_scores, width, label='Confiabilidade', alpha=0.8)
            
            ax.set_xlabel('Métodos')
            ax.set_ylabel('Score')
            ax.set_title('Comparação de Métodos de Confiança', fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(methods)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Adicionar valores nas barras
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{height:.0f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/method_comparison.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico de comparação: {e}")
    
    def _plot_temporal_analysis(self, output_dir: str):
        """Cria gráfico de análise temporal"""
        try:
            uncertainty_scores = [u.uncertainty_score for u in self.uncertainty_data]
            reliability_scores = [u.reliability_score for u in self.uncertainty_data]
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Evolução da incerteza
            ax1.plot(uncertainty_scores, 'b-', linewidth=2, label='Incerteza')
            ax1.axhline(np.mean(uncertainty_scores), color='red', linestyle='--', 
                       label=f'Média: {np.mean(uncertainty_scores):.1f}')
            ax1.set_title('Evolução da Incerteza ao Longo do Tempo', fontweight='bold')
            ax1.set_ylabel('Score de Incerteza')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Evolução da confiabilidade
            ax2.plot(reliability_scores, 'g-', linewidth=2, label='Confiabilidade')
            ax2.axhline(np.mean(reliability_scores), color='red', linestyle='--', 
                       label=f'Média: {np.mean(reliability_scores):.1f}')
            ax2.set_title('Evolução da Confiabilidade ao Longo do Tempo', fontweight='bold')
            ax2.set_xlabel('Índice da Previsão')
            ax2.set_ylabel('Score de Confiabilidade')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/temporal_analysis.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico temporal: {e}")
    
    def _empty_uncertainty_metrics(self) -> UncertaintyMetrics:
        """Retorna métricas vazias"""
        return UncertaintyMetrics(
            mean_uncertainty=0.0,
            uncertainty_std=0.0,
            reliability_score=0.0,
            calibration_score=0.0,
            overconfidence_rate=0.0,
            underconfidence_rate=0.0,
            prediction_accuracy=0.0,
            confidence_accuracy=0.0
        )
    
    def _empty_uncertainty_report(self) -> UncertaintyReport:
        """Retorna relatório vazio"""
        return UncertaintyReport(
            overall_metrics=self._empty_uncertainty_metrics(),
            method_comparison={},
            temporal_analysis={},
            league_analysis={},
            recommendations=[]
        )
