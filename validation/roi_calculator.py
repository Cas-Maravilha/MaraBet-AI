"""
Calculador de ROI - MaraBet AI
Cálculos avançados de ROI e métricas financeiras
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class ROIMetrics:
    """Métricas de ROI calculadas"""
    total_roi: float
    monthly_roi: Dict[str, float]
    weekly_roi: Dict[str, float]
    daily_roi: Dict[str, float]
    compound_roi: float
    annualized_roi: float
    rolling_roi: Dict[str, float]
    risk_adjusted_roi: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float

class ROICalculator:
    """
    Calculador avançado de ROI para MaraBet AI
    Calcula métricas financeiras detalhadas e comparativas
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        """
        Inicializa o calculador de ROI
        
        Args:
            initial_capital: Capital inicial para cálculos
        """
        self.initial_capital = initial_capital
        self.df = None
        
        logger.info(f"ROICalculator inicializado - Capital inicial: R$ {initial_capital:,.2f}")
    
    def load_data(self, bet_records: List[Any]) -> bool:
        """
        Carrega dados de apostas para cálculo
        
        Args:
            bet_records: Lista de registros de apostas
            
        Returns:
            True se carregado com sucesso
        """
        try:
            data = []
            for bet in bet_records:
                data.append({
                    'date': bet.date,
                    'profit_loss': bet.profit_loss,
                    'stake': bet.stake,
                    'roi': bet.roi
                })
            
            self.df = pd.DataFrame(data)
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df['month'] = self.df['date'].dt.to_period('M')
            self.df['week'] = self.df['date'].dt.to_period('W')
            self.df['day'] = self.df['date'].dt.date
            
            logger.info(f"✅ Dados carregados: {len(self.df)} registros")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def calculate_comprehensive_roi(self) -> ROIMetrics:
        """
        Calcula ROI abrangente com todas as métricas
        
        Returns:
            Métricas completas de ROI
        """
        try:
            if self.df is None or self.df.empty:
                logger.error("❌ Dados não carregados")
                return self._empty_metrics()
            
            # ROI básico
            total_roi = self._calculate_total_roi()
            
            # ROI por período
            monthly_roi = self._calculate_monthly_roi()
            weekly_roi = self._calculate_weekly_roi()
            daily_roi = self._calculate_daily_roi()
            
            # ROI composto
            compound_roi = self._calculate_compound_roi()
            
            # ROI anualizado
            annualized_roi = self._calculate_annualized_roi()
            
            # ROI móvel
            rolling_roi = self._calculate_rolling_roi()
            
            # ROI ajustado ao risco
            risk_adjusted_roi = self._calculate_risk_adjusted_roi()
            
            # Ratios de performance
            sharpe_ratio = self._calculate_sharpe_ratio()
            sortino_ratio = self._calculate_sortino_ratio()
            calmar_ratio = self._calculate_calmar_ratio()
            
            return ROIMetrics(
                total_roi=total_roi,
                monthly_roi=monthly_roi,
                weekly_roi=weekly_roi,
                daily_roi=daily_roi,
                compound_roi=compound_roi,
                annualized_roi=annualized_roi,
                rolling_roi=rolling_roi,
                risk_adjusted_roi=risk_adjusted_roi,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular ROI abrangente: {e}")
            return self._empty_metrics()
    
    def _calculate_total_roi(self) -> float:
        """Calcula ROI total"""
        try:
            total_stake = self.df['stake'].sum()
            total_profit = self.df['profit_loss'].sum()
            
            if total_stake == 0:
                return 0.0
            
            return (total_profit / total_stake) * 100
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular ROI total: {e}")
            return 0.0
    
    def _calculate_monthly_roi(self) -> Dict[str, float]:
        """Calcula ROI mensal"""
        try:
            monthly_data = self.df.groupby('month').agg({
                'stake': 'sum',
                'profit_loss': 'sum'
            })
            
            monthly_roi = {}
            for month, row in monthly_data.iterrows():
                if row['stake'] > 0:
                    roi = (row['profit_loss'] / row['stake']) * 100
                    monthly_roi[str(month)] = round(roi, 2)
                else:
                    monthly_roi[str(month)] = 0.0
            
            return monthly_roi
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular ROI mensal: {e}")
            return {}
    
    def _calculate_weekly_roi(self) -> Dict[str, float]:
        """Calcula ROI semanal"""
        try:
            weekly_data = self.df.groupby('week').agg({
                'stake': 'sum',
                'profit_loss': 'sum'
            })
            
            weekly_roi = {}
            for week, row in weekly_data.iterrows():
                if row['stake'] > 0:
                    roi = (row['profit_loss'] / row['stake']) * 100
                    weekly_roi[str(week)] = round(roi, 2)
                else:
                    weekly_roi[str(week)] = 0.0
            
            return weekly_roi
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular ROI semanal: {e}")
            return {}
    
    def _calculate_daily_roi(self) -> Dict[str, float]:
        """Calcula ROI diário"""
        try:
            daily_data = self.df.groupby('day').agg({
                'stake': 'sum',
                'profit_loss': 'sum'
            })
            
            daily_roi = {}
            for day, row in daily_data.iterrows():
                if row['stake'] > 0:
                    roi = (row['profit_loss'] / row['stake']) * 100
                    daily_roi[str(day)] = round(roi, 2)
                else:
                    daily_roi[str(day)] = 0.0
            
            return daily_roi
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular ROI diário: {e}")
            return {}
    
    def _calculate_compound_roi(self) -> float:
        """Calcula ROI composto"""
        try:
            if self.df.empty:
                return 0.0
            
            # Calcular retorno composto
            total_profit = self.df['profit_loss'].sum()
            final_value = self.initial_capital + total_profit
            
            # ROI composto = (Valor Final / Valor Inicial)^(1/n) - 1
            periods = len(self.df['date'].dt.to_period('M').unique())
            if periods == 0:
                return 0.0
            
            compound_roi = ((final_value / self.initial_capital) ** (1 / periods) - 1) * 100
            return round(compound_roi, 2)
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular ROI composto: {e}")
            return 0.0
    
    def _calculate_annualized_roi(self) -> float:
        """Calcula ROI anualizado"""
        try:
            if self.df.empty:
                return 0.0
            
            # Calcular período em anos
            start_date = self.df['date'].min()
            end_date = self.df['date'].max()
            days = (end_date - start_date).days
            years = days / 365.25
            
            if years == 0:
                return 0.0
            
            # ROI anualizado
            total_profit = self.df['profit_loss'].sum()
            annualized_roi = ((1 + total_profit / self.initial_capital) ** (1 / years) - 1) * 100
            
            return round(annualized_roi, 2)
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular ROI anualizado: {e}")
            return 0.0
    
    def _calculate_rolling_roi(self, window: int = 30) -> Dict[str, float]:
        """Calcula ROI móvel"""
        try:
            if self.df.empty:
                return {}
            
            # Ordenar por data
            df_sorted = self.df.sort_values('date')
            
            # Calcular ROI móvel
            rolling_stake = df_sorted['stake'].rolling(window=window, min_periods=1).sum()
            rolling_profit = df_sorted['profit_loss'].rolling(window=window, min_periods=1).sum()
            
            rolling_roi = {}
            for i, (date, stake, profit) in enumerate(zip(df_sorted['date'], rolling_stake, rolling_profit)):
                if stake > 0:
                    roi = (profit / stake) * 100
                    rolling_roi[date.strftime('%Y-%m-%d')] = round(roi, 2)
                else:
                    rolling_roi[date.strftime('%Y-%m-%d')] = 0.0
            
            return rolling_roi
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular ROI móvel: {e}")
            return {}
    
    def _calculate_risk_adjusted_roi(self) -> float:
        """Calcula ROI ajustado ao risco"""
        try:
            if self.df.empty:
                return 0.0
            
            # Calcular retorno médio
            mean_return = self.df['profit_loss'].mean()
            
            # Calcular volatilidade
            volatility = self.df['profit_loss'].std()
            
            if volatility == 0:
                return 0.0
            
            # ROI ajustado ao risco = Retorno Médio / Volatilidade
            risk_adjusted_roi = (mean_return / volatility) * 100
            
            return round(risk_adjusted_roi, 2)
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular ROI ajustado ao risco: {e}")
            return 0.0
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calcula Sharpe Ratio"""
        try:
            if self.df.empty:
                return 0.0
            
            # Calcular retorno médio
            mean_return = self.df['profit_loss'].mean()
            
            # Calcular volatilidade
            volatility = self.df['profit_loss'].std()
            
            if volatility == 0:
                return 0.0
            
            # Assumir risk-free rate de 0.5% ao mês
            risk_free_rate = 0.005 * 30  # 0.5% ao mês convertido para período
            
            # Sharpe Ratio = (Retorno Médio - Risk Free Rate) / Volatilidade
            sharpe_ratio = (mean_return - risk_free_rate) / volatility
            
            return round(sharpe_ratio, 3)
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular Sharpe Ratio: {e}")
            return 0.0
    
    def _calculate_sortino_ratio(self) -> float:
        """Calcula Sortino Ratio"""
        try:
            if self.df.empty:
                return 0.0
            
            # Calcular retorno médio
            mean_return = self.df['profit_loss'].mean()
            
            # Calcular downside deviation (apenas retornos negativos)
            negative_returns = self.df[self.df['profit_loss'] < 0]['profit_loss']
            if len(negative_returns) == 0:
                return float('inf')  # Sem retornos negativos
            
            downside_deviation = negative_returns.std()
            
            if downside_deviation == 0:
                return 0.0
            
            # Assumir risk-free rate de 0.5% ao mês
            risk_free_rate = 0.005 * 30
            
            # Sortino Ratio = (Retorno Médio - Risk Free Rate) / Downside Deviation
            sortino_ratio = (mean_return - risk_free_rate) / downside_deviation
            
            return round(sortino_ratio, 3)
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular Sortino Ratio: {e}")
            return 0.0
    
    def _calculate_calmar_ratio(self) -> float:
        """Calcula Calmar Ratio"""
        try:
            if self.df.empty:
                return 0.0
            
            # Calcular retorno anualizado
            annualized_return = self._calculate_annualized_roi()
            
            # Calcular maximum drawdown
            max_drawdown = self._calculate_maximum_drawdown()
            
            if max_drawdown == 0:
                return 0.0
            
            # Calmar Ratio = Retorno Anualizado / Maximum Drawdown
            calmar_ratio = annualized_return / max_drawdown
            
            return round(calmar_ratio, 3)
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular Calmar Ratio: {e}")
            return 0.0
    
    def _calculate_maximum_drawdown(self) -> float:
        """Calcula Maximum Drawdown"""
        try:
            if self.df.empty:
                return 0.0
            
            # Calcular valor acumulado
            cumulative_profit = self.df['profit_loss'].cumsum()
            cumulative_value = self.initial_capital + cumulative_profit
            
            # Calcular running maximum
            running_max = cumulative_value.expanding().max()
            
            # Calcular drawdown
            drawdown = (running_max - cumulative_value) / running_max * 100
            
            # Maximum drawdown
            max_drawdown = drawdown.max()
            
            return round(max_drawdown, 2)
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular Maximum Drawdown: {e}")
            return 0.0
    
    def calculate_benchmark_comparison(self, benchmark_roi: float = 5.0) -> Dict[str, Any]:
        """
        Compara performance com benchmark
        
        Args:
            benchmark_roi: ROI de benchmark (padrão: 5% ao ano)
            
        Returns:
            Comparação com benchmark
        """
        try:
            if self.df.empty:
                return {}
            
            # Calcular ROI anualizado
            annualized_roi = self._calculate_annualized_roi()
            
            # Calcular excess return
            excess_return = annualized_roi - benchmark_roi
            
            # Calcular tracking error
            daily_returns = self.df['profit_loss'] / self.df['stake'] * 100
            benchmark_daily = benchmark_roi / 365.25  # ROI diário do benchmark
            excess_returns = daily_returns - benchmark_daily
            tracking_error = excess_returns.std()
            
            # Calcular information ratio
            information_ratio = excess_return / tracking_error if tracking_error > 0 else 0
            
            # Calcular beta (simplificado)
            beta = 1.0  # Assumir beta de 1 para simplificação
            
            # Calcular alpha
            alpha = annualized_roi - (benchmark_roi * beta)
            
            return {
                'benchmark_roi': benchmark_roi,
                'actual_roi': annualized_roi,
                'excess_return': round(excess_return, 2),
                'tracking_error': round(tracking_error, 2),
                'information_ratio': round(information_ratio, 3),
                'alpha': round(alpha, 2),
                'beta': beta,
                'outperformance': excess_return > 0,
                'outperformance_percentage': round((excess_return / benchmark_roi) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular comparação com benchmark: {e}")
            return {}
    
    def calculate_roi_by_confidence(self) -> Dict[str, float]:
        """Calcula ROI por faixa de confiança"""
        try:
            if self.df.empty or 'confidence' not in self.df.columns:
                return {}
            
            # Definir faixas de confiança
            confidence_ranges = {
                '60-70%': (0.6, 0.7),
                '70-80%': (0.7, 0.8),
                '80-90%': (0.8, 0.9),
                '90-95%': (0.9, 0.95)
            }
            
            roi_by_confidence = {}
            
            for range_name, (min_conf, max_conf) in confidence_ranges.items():
                mask = (self.df['confidence'] >= min_conf) & (self.df['confidence'] < max_conf)
                range_data = self.df[mask]
                
                if not range_data.empty:
                    total_stake = range_data['stake'].sum()
                    total_profit = range_data['profit_loss'].sum()
                    
                    if total_stake > 0:
                        roi = (total_profit / total_stake) * 100
                        roi_by_confidence[range_name] = round(roi, 2)
                    else:
                        roi_by_confidence[range_name] = 0.0
                else:
                    roi_by_confidence[range_name] = 0.0
            
            return roi_by_confidence
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular ROI por confiança: {e}")
            return {}
    
    def calculate_roi_by_league(self) -> Dict[str, float]:
        """Calcula ROI por liga"""
        try:
            if self.df.empty or 'league' not in self.df.columns:
                return {}
            
            league_data = self.df.groupby('league').agg({
                'stake': 'sum',
                'profit_loss': 'sum'
            })
            
            roi_by_league = {}
            for league, row in league_data.iterrows():
                if row['stake'] > 0:
                    roi = (row['profit_loss'] / row['stake']) * 100
                    roi_by_league[league] = round(roi, 2)
                else:
                    roi_by_league[league] = 0.0
            
            return roi_by_league
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular ROI por liga: {e}")
            return {}
    
    def generate_roi_report(self) -> Dict[str, Any]:
        """Gera relatório completo de ROI"""
        try:
            metrics = self.calculate_comprehensive_roi()
            benchmark_comparison = self.calculate_benchmark_comparison()
            roi_by_confidence = self.calculate_roi_by_confidence()
            roi_by_league = self.calculate_roi_by_league()
            
            return {
                'basic_metrics': {
                    'total_roi': metrics.total_roi,
                    'compound_roi': metrics.compound_roi,
                    'annualized_roi': metrics.annualized_roi,
                    'risk_adjusted_roi': metrics.risk_adjusted_roi
                },
                'performance_ratios': {
                    'sharpe_ratio': metrics.sharpe_ratio,
                    'sortino_ratio': metrics.sortino_ratio,
                    'calmar_ratio': metrics.calmar_ratio
                },
                'period_analysis': {
                    'monthly_roi': metrics.monthly_roi,
                    'weekly_roi': metrics.weekly_roi,
                    'daily_roi': metrics.daily_roi
                },
                'benchmark_comparison': benchmark_comparison,
                'roi_by_confidence': roi_by_confidence,
                'roi_by_league': roi_by_league,
                'summary': self._generate_roi_summary(metrics, benchmark_comparison)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório de ROI: {e}")
            return {}
    
    def _generate_roi_summary(self, metrics: ROIMetrics, benchmark_comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo do ROI"""
        try:
            # Classificar performance
            if metrics.annualized_roi > 20:
                performance_rating = "EXCELENTE"
            elif metrics.annualized_roi > 10:
                performance_rating = "MUITO BOM"
            elif metrics.annualized_roi > 5:
                performance_rating = "BOM"
            elif metrics.annualized_roi > 0:
                performance_rating = "REGULAR"
            else:
                performance_rating = "NECESSITA MELHORIAS"
            
            # Análise de risco
            if metrics.sharpe_ratio > 1.5:
                risk_rating = "BAIXO RISCO"
            elif metrics.sharpe_ratio > 1.0:
                risk_rating = "RISCO MODERADO"
            elif metrics.sharpe_ratio > 0.5:
                risk_rating = "RISCO ALTO"
            else:
                risk_rating = "RISCO MUITO ALTO"
            
            return {
                'performance_rating': performance_rating,
                'risk_rating': risk_rating,
                'outperforms_benchmark': benchmark_comparison.get('outperformance', False),
                'excess_return': benchmark_comparison.get('excess_return', 0),
                'key_insights': self._generate_roi_insights(metrics, benchmark_comparison)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo de ROI: {e}")
            return {}
    
    def _generate_roi_insights(self, metrics: ROIMetrics, benchmark_comparison: Dict[str, Any]) -> List[str]:
        """Gera insights sobre ROI"""
        try:
            insights = []
            
            # Insight sobre ROI anualizado
            if metrics.annualized_roi > 15:
                insights.append(f"🎯 ROI anualizado excepcional de {metrics.annualized_roi:.1f}%")
            elif metrics.annualized_roi > 10:
                insights.append(f"📈 ROI anualizado sólido de {metrics.annualized_roi:.1f}%")
            elif metrics.annualized_roi > 5:
                insights.append(f"📊 ROI anualizado positivo de {metrics.annualized_roi:.1f}%")
            else:
                insights.append(f"⚠️ ROI anualizado de {metrics.annualized_roi:.1f}% precisa melhorar")
            
            # Insight sobre Sharpe Ratio
            if metrics.sharpe_ratio > 1.5:
                insights.append(f"⚡ Sharpe Ratio excelente de {metrics.sharpe_ratio:.2f}")
            elif metrics.sharpe_ratio > 1.0:
                insights.append(f"📊 Sharpe Ratio bom de {metrics.sharpe_ratio:.2f}")
            else:
                insights.append(f"⚠️ Sharpe Ratio de {metrics.sharpe_ratio:.2f} indica alto risco")
            
            # Insight sobre benchmark
            if benchmark_comparison.get('outperformance', False):
                excess = benchmark_comparison.get('excess_return', 0)
                insights.append(f"🏆 Supera benchmark em {excess:.1f} pontos percentuais")
            else:
                excess = benchmark_comparison.get('excess_return', 0)
                insights.append(f"📉 Fica {abs(excess):.1f} pontos percentuais abaixo do benchmark")
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar insights de ROI: {e}")
            return []
    
    def _empty_metrics(self) -> ROIMetrics:
        """Retorna métricas vazias"""
        return ROIMetrics(
            total_roi=0.0,
            monthly_roi={},
            weekly_roi={},
            daily_roi={},
            compound_roi=0.0,
            annualized_roi=0.0,
            rolling_roi={},
            risk_adjusted_roi=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0
        )
    
    def export_roi_report(self, output_file: str) -> bool:
        """
        Exporta relatório de ROI
        
        Args:
            output_file: Arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            report = self.generate_roi_report()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ Relatório de ROI exportado para {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar relatório de ROI: {e}")
            return False
