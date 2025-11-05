"""
Analisador de Performance - MaraBet AI
Análise detalhada de performance e métricas de validação
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
from pathlib import Path

from .backtesting_engine import BacktestResults, BetRecord

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """
    Analisador de performance para resultados de backtesting
    Gera análises detalhadas e visualizações
    """
    
    def __init__(self, results: BacktestResults, bet_records: List[BetRecord]):
        """
        Inicializa o analisador
        
        Args:
            results: Resultados do backtesting
            bet_records: Registros individuais de apostas
        """
        self.results = results
        self.bet_records = bet_records
        self.df = self._create_dataframe()
        
        logger.info("PerformanceAnalyzer inicializado")
    
    def _create_dataframe(self) -> pd.DataFrame:
        """Cria DataFrame dos registros de apostas"""
        try:
            data = []
            for bet in self.bet_records:
                data.append({
                    'date': bet.date,
                    'league': bet.league,
                    'home_team': bet.home_team,
                    'away_team': bet.away_team,
                    'bet_type': bet.bet_type,
                    'prediction': bet.prediction,
                    'odds': bet.odds,
                    'stake': bet.stake,
                    'confidence': bet.confidence,
                    'actual_result': bet.actual_result,
                    'bet_result': bet.bet_result.value if bet.bet_result else None,
                    'profit_loss': bet.profit_loss,
                    'roi': bet.roi
                })
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.to_period('M')
            df['week'] = df['date'].dt.to_period('W')
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar DataFrame: {e}")
            return pd.DataFrame()
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Gera relatório completo de performance
        
        Returns:
            Dicionário com relatório detalhado
        """
        try:
            report = {
                'summary': self._generate_summary(),
                'monthly_analysis': self._generate_monthly_analysis(),
                'league_analysis': self._generate_league_analysis(),
                'bet_type_analysis': self._generate_bet_type_analysis(),
                'confidence_analysis': self._generate_confidence_analysis(),
                'risk_metrics': self._generate_risk_metrics(),
                'trend_analysis': self._generate_trend_analysis(),
                'recommendations': self._generate_recommendations()
            }
            
            logger.info("✅ Relatório de performance gerado")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório de performance: {e}")
            return {}
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Gera resumo executivo"""
        try:
            total_days = (self.results.end_date - self.results.start_date).days
            avg_daily_bets = self.results.total_bets / total_days if total_days > 0 else 0
            
            return {
                'period': {
                    'start_date': self.results.start_date.strftime('%Y-%m-%d'),
                    'end_date': self.results.end_date.strftime('%Y-%m-%d'),
                    'total_days': total_days
                },
                'bets': {
                    'total_bets': self.results.total_bets,
                    'winning_bets': self.results.winning_bets,
                    'losing_bets': self.results.losing_bets,
                    'push_bets': self.results.push_bets,
                    'win_rate': round(self.results.win_rate, 2),
                    'avg_daily_bets': round(avg_daily_bets, 1)
                },
                'financial': {
                    'initial_capital': 10000.0,  # Assumindo capital inicial
                    'final_capital': 10000.0 + self.results.total_profit,
                    'total_stake': round(self.results.total_stake, 2),
                    'total_profit': round(self.results.total_profit, 2),
                    'total_roi': round(self.results.total_roi, 2),
                    'average_odds': round(self.results.average_odds, 2)
                },
                'performance': {
                    'sharpe_ratio': round(self.results.sharpe_ratio, 3),
                    'max_drawdown': round(self.results.max_drawdown, 2),
                    'profit_factor': round(self.results.profit_factor, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo: {e}")
            return {}
    
    def _generate_monthly_analysis(self) -> Dict[str, Any]:
        """Gera análise mensal detalhada"""
        try:
            monthly_data = []
            
            for month, roi in self.results.monthly_roi.items():
                month_df = self.df[self.df['month'] == month]
                
                if not month_df.empty:
                    monthly_data.append({
                        'month': month,
                        'roi': round(roi, 2),
                        'bets': len(month_df),
                        'wins': len(month_df[month_df['bet_result'] == 'win']),
                        'win_rate': round(len(month_df[month_df['bet_result'] == 'win']) / len(month_df) * 100, 2),
                        'total_stake': round(month_df['stake'].sum(), 2),
                        'total_profit': round(month_df['profit_loss'].sum(), 2),
                        'avg_confidence': round(month_df['confidence'].mean(), 3),
                        'avg_odds': round(month_df['odds'].mean(), 2)
                    })
            
            # Ordenar por mês
            monthly_data.sort(key=lambda x: x['month'])
            
            return {
                'monthly_breakdown': monthly_data,
                'best_month': {
                    'month': self.results.best_month,
                    'roi': round(self.results.monthly_roi.get(self.results.best_month, 0), 2)
                },
                'worst_month': {
                    'month': self.results.worst_month,
                    'roi': round(self.results.monthly_roi.get(self.results.worst_month, 0), 2)
                },
                'monthly_roi_avg': round(np.mean(list(self.results.monthly_roi.values())), 2),
                'monthly_roi_std': round(np.std(list(self.results.monthly_roi.values())), 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar análise mensal: {e}")
            return {}
    
    def _generate_league_analysis(self) -> Dict[str, Any]:
        """Gera análise por liga"""
        try:
            league_data = []
            
            for league, perf in self.results.league_performance.items():
                league_data.append({
                    'league': league,
                    'bets': perf['bets'],
                    'wins': perf['wins'],
                    'win_rate': round(perf['win_rate'], 2),
                    'stake': round(perf['stake'], 2),
                    'profit': round(perf['profit'], 2),
                    'roi': round(perf['roi'], 2)
                })
            
            # Ordenar por ROI
            league_data.sort(key=lambda x: x['roi'], reverse=True)
            
            return {
                'league_breakdown': league_data,
                'best_league': {
                    'league': self.results.best_league,
                    'roi': round(self.results.league_performance.get(self.results.best_league, {}).get('roi', 0), 2)
                },
                'worst_league': {
                    'league': self.results.worst_league,
                    'roi': round(self.results.league_performance.get(self.results.worst_league, {}).get('roi', 0), 2)
                },
                'total_leagues': len(league_data),
                'profitable_leagues': len([l for l in league_data if l['roi'] > 0])
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar análise por liga: {e}")
            return {}
    
    def _generate_bet_type_analysis(self) -> Dict[str, Any]:
        """Gera análise por tipo de aposta"""
        try:
            bet_type_data = []
            
            for bet_type, perf in self.results.bet_type_performance.items():
                bet_type_data.append({
                    'bet_type': bet_type,
                    'bets': perf['bets'],
                    'wins': perf['wins'],
                    'win_rate': round(perf['win_rate'], 2),
                    'stake': round(perf['stake'], 2),
                    'profit': round(perf['profit'], 2),
                    'roi': round(perf['roi'], 2)
                })
            
            # Ordenar por ROI
            bet_type_data.sort(key=lambda x: x['roi'], reverse=True)
            
            return {
                'bet_type_breakdown': bet_type_data,
                'most_profitable_type': max(bet_type_data, key=lambda x: x['roi'])['bet_type'] if bet_type_data else None,
                'least_profitable_type': min(bet_type_data, key=lambda x: x['roi'])['bet_type'] if bet_type_data else None
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar análise por tipo de aposta: {e}")
            return {}
    
    def _generate_confidence_analysis(self) -> Dict[str, Any]:
        """Gera análise de confiança"""
        try:
            confidence_data = []
            
            for range_name, analysis in self.results.confidence_analysis.items():
                confidence_data.append({
                    'confidence_range': range_name,
                    'bets': analysis['bets'],
                    'win_rate': round(analysis['win_rate'], 2),
                    'roi': round(analysis['roi'], 2)
                })
            
            # Análise de correlação confiança vs performance
            correlation = self.df['confidence'].corr(self.df['roi']) if not self.df.empty else 0
            
            return {
                'confidence_breakdown': confidence_data,
                'confidence_correlation': round(correlation, 3),
                'avg_confidence': round(self.df['confidence'].mean(), 3) if not self.df.empty else 0,
                'confidence_std': round(self.df['confidence'].std(), 3) if not self.df.empty else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar análise de confiança: {e}")
            return {}
    
    def _generate_risk_metrics(self) -> Dict[str, Any]:
        """Gera métricas de risco"""
        try:
            if self.df.empty:
                return {}
            
            # Calcular drawdowns
            cumulative_profit = self.df['profit_loss'].cumsum()
            running_max = cumulative_profit.expanding().max()
            drawdown = running_max - cumulative_profit
            
            # Calcular VaR (Value at Risk) 95%
            var_95 = np.percentile(self.df['profit_loss'], 5)
            
            # Calcular CVaR (Conditional Value at Risk)
            cvar_95 = self.df[self.df['profit_loss'] <= var_95]['profit_loss'].mean()
            
            # Calcular volatilidade
            volatility = self.df['profit_loss'].std()
            
            # Calcular skewness e kurtosis
            skewness = self.df['profit_loss'].skew()
            kurtosis = self.df['profit_loss'].kurtosis()
            
            return {
                'max_drawdown': round(self.results.max_drawdown, 2),
                'current_drawdown': round(drawdown.iloc[-1] if not drawdown.empty else 0, 2),
                'var_95': round(var_95, 2),
                'cvar_95': round(cvar_95, 2),
                'volatility': round(volatility, 2),
                'skewness': round(skewness, 3),
                'kurtosis': round(kurtosis, 3),
                'sharpe_ratio': round(self.results.sharpe_ratio, 3),
                'profit_factor': round(self.results.profit_factor, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar métricas de risco: {e}")
            return {}
    
    def _generate_trend_analysis(self) -> Dict[str, Any]:
        """Gera análise de tendências"""
        try:
            if self.df.empty:
                return {}
            
            # Análise semanal
            weekly_data = self.df.groupby('week').agg({
                'profit_loss': 'sum',
                'stake': 'sum',
                'bet_result': lambda x: (x == 'win').sum() / len(x) * 100,
                'confidence': 'mean',
                'odds': 'mean'
            }).reset_index()
            
            weekly_data['roi'] = (weekly_data['profit_loss'] / weekly_data['stake']) * 100
            
            # Calcular tendências
            roi_trend = np.polyfit(range(len(weekly_data)), weekly_data['roi'], 1)[0]
            win_rate_trend = np.polyfit(range(len(weekly_data)), weekly_data['bet_result'], 1)[0]
            confidence_trend = np.polyfit(range(len(weekly_data)), weekly_data['confidence'], 1)[0]
            
            return {
                'weekly_performance': weekly_data.to_dict('records'),
                'trends': {
                    'roi_trend': round(roi_trend, 3),
                    'win_rate_trend': round(win_rate_trend, 3),
                    'confidence_trend': round(confidence_trend, 3)
                },
                'recent_performance': {
                    'last_4_weeks_roi': round(weekly_data['roi'].tail(4).mean(), 2),
                    'last_4_weeks_win_rate': round(weekly_data['bet_result'].tail(4).mean(), 2)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar análise de tendências: {e}")
            return {}
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas na análise"""
        try:
            recommendations = []
            
            # Análise de ROI
            if self.results.total_roi > 10:
                recommendations.append("✅ Excelente performance! ROI acima de 10%")
            elif self.results.total_roi > 5:
                recommendations.append("👍 Boa performance! ROI acima de 5%")
            elif self.results.total_roi > 0:
                recommendations.append("⚠️ Performance positiva, mas há espaço para melhorias")
            else:
                recommendations.append("❌ Performance negativa. Revisar estratégia urgentemente")
            
            # Análise de win rate
            if self.results.win_rate > 60:
                recommendations.append("🎯 Alta taxa de acerto! Manter estratégia atual")
            elif self.results.win_rate > 50:
                recommendations.append("📈 Taxa de acerto boa, mas pode melhorar")
            else:
                recommendations.append("🔍 Taxa de acerto baixa. Revisar critérios de seleção")
            
            # Análise de ligas
            profitable_leagues = [l for l in self.results.league_performance.values() if l['roi'] > 0]
            if len(profitable_leagues) > len(self.results.league_performance) * 0.7:
                recommendations.append("🏆 Maioria das ligas é lucrativa. Estratégia sólida")
            else:
                recommendations.append("⚠️ Muitas ligas com performance negativa. Focar nas mais lucrativas")
            
            # Análise de confiança
            high_conf_bets = [b for b in self.bet_records if b.confidence > 0.8]
            if high_conf_bets:
                high_conf_roi = sum(b.profit_loss for b in high_conf_bets) / sum(b.stake for b in high_conf_bets) * 100
                if high_conf_roi > self.results.total_roi:
                    recommendations.append("🎯 Apostas de alta confiança são mais lucrativas. Aumentar threshold")
                else:
                    recommendations.append("📊 Apostas de alta confiança não são mais lucrativas. Revisar modelo")
            
            # Análise de drawdown
            if self.results.max_drawdown > self.results.total_stake * 0.2:
                recommendations.append("⚠️ Drawdown alto detectado. Reduzir tamanho das apostas")
            
            # Análise de Sharpe Ratio
            if self.results.sharpe_ratio > 1:
                recommendations.append("📈 Excelente Sharpe Ratio! Estratégia bem balanceada")
            elif self.results.sharpe_ratio > 0.5:
                recommendations.append("👍 Sharpe Ratio bom, mas pode melhorar")
            else:
                recommendations.append("⚠️ Sharpe Ratio baixo. Revisar gestão de risco")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar recomendações: {e}")
            return []
    
    def create_visualizations(self, output_dir: str = "validation/charts") -> bool:
        """
        Cria visualizações dos resultados
        
        Args:
            output_dir: Diretório para salvar gráficos
            
        Returns:
            True se criado com sucesso
        """
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Configurar estilo
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            # 1. ROI Mensal
            self._plot_monthly_roi(output_dir)
            
            # 2. Performance por Liga
            self._plot_league_performance(output_dir)
            
            # 3. Análise de Confiança
            self._plot_confidence_analysis(output_dir)
            
            # 4. Evolução do Capital
            self._plot_capital_evolution(output_dir)
            
            # 5. Distribuição de Lucros/Prejuízos
            self._plot_profit_distribution(output_dir)
            
            # 6. Heatmap de Performance
            self._plot_performance_heatmap(output_dir)
            
            logger.info(f"✅ Visualizações criadas em {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar visualizações: {e}")
            return False
    
    def _plot_monthly_roi(self, output_dir: str):
        """Cria gráfico de ROI mensal"""
        try:
            months = list(self.results.monthly_roi.keys())
            rois = list(self.results.monthly_roi.values())
            
            plt.figure(figsize=(12, 6))
            bars = plt.bar(months, rois, color=['green' if roi > 0 else 'red' for roi in rois])
            plt.title('ROI Mensal - MaraBet AI', fontsize=16, fontweight='bold')
            plt.xlabel('Mês', fontsize=12)
            plt.ylabel('ROI (%)', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Adicionar valores nas barras
            for bar, roi in zip(bars, rois):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                        f'{roi:.1f}%', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/monthly_roi.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico de ROI mensal: {e}")
    
    def _plot_league_performance(self, output_dir: str):
        """Cria gráfico de performance por liga"""
        try:
            leagues = list(self.results.league_performance.keys())
            rois = [perf['roi'] for perf in self.results.league_performance.values()]
            
            # Ordenar por ROI
            sorted_data = sorted(zip(leagues, rois), key=lambda x: x[1], reverse=True)
            leagues, rois = zip(*sorted_data)
            
            plt.figure(figsize=(14, 8))
            bars = plt.barh(leagues, rois, color=['green' if roi > 0 else 'red' for roi in rois])
            plt.title('Performance por Liga - MaraBet AI', fontsize=16, fontweight='bold')
            plt.xlabel('ROI (%)', fontsize=12)
            plt.ylabel('Liga', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Adicionar valores nas barras
            for bar, roi in zip(bars, rois):
                plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                        f'{roi:.1f}%', ha='left', va='center')
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/league_performance.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico de performance por liga: {e}")
    
    def _plot_confidence_analysis(self, output_dir: str):
        """Cria gráfico de análise de confiança"""
        try:
            ranges = list(self.results.confidence_analysis.keys())
            win_rates = [analysis['win_rate'] for analysis in self.results.confidence_analysis.values()]
            rois = [analysis['roi'] for analysis in self.results.confidence_analysis.values()]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Taxa de acerto por faixa de confiança
            bars1 = ax1.bar(ranges, win_rates, color='skyblue')
            ax1.set_title('Taxa de Acerto por Faixa de Confiança', fontweight='bold')
            ax1.set_xlabel('Faixa de Confiança')
            ax1.set_ylabel('Taxa de Acerto (%)')
            ax1.grid(True, alpha=0.3)
            
            for bar, rate in zip(bars1, win_rates):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                        f'{rate:.1f}%', ha='center', va='bottom')
            
            # ROI por faixa de confiança
            bars2 = ax2.bar(ranges, rois, color=['green' if roi > 0 else 'red' for roi in rois])
            ax2.set_title('ROI por Faixa de Confiança', fontweight='bold')
            ax2.set_xlabel('Faixa de Confiança')
            ax2.set_ylabel('ROI (%)')
            ax2.grid(True, alpha=0.3)
            
            for bar, roi in zip(bars2, rois):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                        f'{roi:.1f}%', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/confidence_analysis.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico de análise de confiança: {e}")
    
    def _plot_capital_evolution(self, output_dir: str):
        """Cria gráfico de evolução do capital"""
        try:
            if self.df.empty:
                return
            
            cumulative_profit = self.df['profit_loss'].cumsum()
            capital_evolution = 10000 + cumulative_profit  # Assumindo capital inicial de 10k
            
            plt.figure(figsize=(14, 8))
            plt.plot(self.df['date'], capital_evolution, linewidth=2, color='blue')
            plt.title('Evolução do Capital - MaraBet AI', fontsize=16, fontweight='bold')
            plt.xlabel('Data', fontsize=12)
            plt.ylabel('Capital (R$)', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Adicionar linha do capital inicial
            plt.axhline(y=10000, color='red', linestyle='--', alpha=0.7, label='Capital Inicial')
            
            # Adicionar anotações
            final_capital = capital_evolution.iloc[-1]
            total_return = ((final_capital - 10000) / 10000) * 100
            plt.annotate(f'Retorno Total: {total_return:.1f}%', 
                        xy=(self.df['date'].iloc[-1], final_capital),
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
            
            plt.legend()
            plt.tight_layout()
            plt.savefig(f"{output_dir}/capital_evolution.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico de evolução do capital: {e}")
    
    def _plot_profit_distribution(self, output_dir: str):
        """Cria gráfico de distribuição de lucros/prejuízos"""
        try:
            if self.df.empty:
                return
            
            plt.figure(figsize=(12, 8))
            
            # Histograma de lucros/prejuízos
            plt.hist(self.df['profit_loss'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Break-even')
            plt.axvline(x=self.df['profit_loss'].mean(), color='green', linestyle='-', linewidth=2, 
                       label=f'Média: R$ {self.df["profit_loss"].mean():.2f}')
            
            plt.title('Distribuição de Lucros/Prejuízos - MaraBet AI', fontsize=16, fontweight='bold')
            plt.xlabel('Lucro/Prejuízo (R$)', fontsize=12)
            plt.ylabel('Frequência', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/profit_distribution.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar gráfico de distribuição: {e}")
    
    def _plot_performance_heatmap(self, output_dir: str):
        """Cria heatmap de performance"""
        try:
            if self.df.empty:
                return
            
            # Criar pivot table: Liga x Mês
            pivot_data = self.df.groupby(['league', self.df['date'].dt.to_period('M')])['roi'].mean().unstack(fill_value=0)
            
            plt.figure(figsize=(16, 10))
            sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='RdYlGn', center=0,
                       cbar_kws={'label': 'ROI (%)'})
            plt.title('Heatmap de Performance: Liga x Mês - MaraBet AI', fontsize=16, fontweight='bold')
            plt.xlabel('Mês', fontsize=12)
            plt.ylabel('Liga', fontsize=12)
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/performance_heatmap.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar heatmap de performance: {e}")
    
    def export_report(self, output_file: str) -> bool:
        """
        Exporta relatório completo
        
        Args:
            output_file: Arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            report = self.generate_performance_report()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ Relatório exportado para {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar relatório: {e}")
            return False
