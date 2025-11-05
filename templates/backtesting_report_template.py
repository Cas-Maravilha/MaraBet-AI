#!/usr/bin/env python3
"""
Template de Relatório de Backtesting - MaraBet AI
Gera relatórios profissionais de backtesting para uso comercial
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BacktestingMetrics:
    """Métricas de backtesting"""
    total_bets: int
    winning_bets: int
    losing_bets: int
    win_rate: float
    total_roi: float
    monthly_roi: List[float]
    annualized_roi: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    var_95: float
    cvar_95: float
    consistency_score: float
    profit_factor: float
    average_odds: float
    average_stake: float
    total_stake: float
    total_profit: float

@dataclass
class LeagueAnalysis:
    """Análise por liga"""
    league_name: str
    total_bets: int
    win_rate: float
    roi: float
    profit: float
    best_month: str
    worst_month: str
    confidence_score: float

@dataclass
class BacktestingReport:
    """Relatório completo de backtesting"""
    report_id: str
    generation_date: datetime
    period_start: datetime
    period_end: datetime
    strategy_name: str
    strategy_version: str
    overall_metrics: BacktestingMetrics
    league_analysis: List[LeagueAnalysis]
    monthly_breakdown: Dict[str, Dict[str, float]]
    risk_analysis: Dict[str, float]
    recommendations: List[str]
    disclaimer: str
    methodology: str

class BacktestingReportGenerator:
    """
    Gerador de relatórios de backtesting para MaraBet AI
    Cria relatórios profissionais para uso comercial
    """
    
    def __init__(self, template_dir: str = "templates"):
        """
        Inicializa o gerador de relatórios
        
        Args:
            template_dir: Diretório de templates
        """
        self.template_dir = template_dir
        os.makedirs(template_dir, exist_ok=True)
        
        logger.info("BacktestingReportGenerator inicializado")
    
    def generate_report(self, 
                       backtesting_data: Dict[str, Any],
                       strategy_name: str = "MaraBet AI Strategy",
                       strategy_version: str = "1.0") -> BacktestingReport:
        """
        Gera relatório completo de backtesting
        
        Args:
            backtesting_data: Dados de backtesting
            strategy_name: Nome da estratégia
            strategy_version: Versão da estratégia
            
        Returns:
            Relatório de backtesting
        """
        try:
            logger.info(f"📊 Gerando relatório de backtesting para {strategy_name}")
            
            # Processar dados
            overall_metrics = self._calculate_overall_metrics(backtesting_data)
            league_analysis = self._analyze_leagues(backtesting_data)
            monthly_breakdown = self._calculate_monthly_breakdown(backtesting_data)
            risk_analysis = self._analyze_risk(backtesting_data)
            recommendations = self._generate_recommendations(overall_metrics, league_analysis)
            
            # Criar relatório
            report = BacktestingReport(
                report_id=f"BTR_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                generation_date=datetime.now(),
                period_start=datetime.fromisoformat(backtesting_data.get('period_start', '2024-01-01')),
                period_end=datetime.fromisoformat(backtesting_data.get('period_end', '2024-12-31')),
                strategy_name=strategy_name,
                strategy_version=strategy_version,
                overall_metrics=overall_metrics,
                league_analysis=league_analysis,
                monthly_breakdown=monthly_breakdown,
                risk_analysis=risk_analysis,
                recommendations=recommendations,
                disclaimer=self._get_disclaimer(),
                methodology=self._get_methodology()
            )
            
            # Salvar relatório
            self._save_report(report)
            
            logger.info("✅ Relatório de backtesting gerado com sucesso")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            raise
    
    def _calculate_overall_metrics(self, data: Dict[str, Any]) -> BacktestingMetrics:
        """Calcula métricas gerais de backtesting"""
        try:
            bets = data.get('bets', [])
            if not bets:
                return self._empty_metrics()
            
            df = pd.DataFrame(bets)
            
            # Métricas básicas
            total_bets = len(df)
            winning_bets = len(df[df['result'] == 'win'])
            losing_bets = len(df[df['result'] == 'loss'])
            win_rate = (winning_bets / total_bets) * 100 if total_bets > 0 else 0
            
            # ROI e lucro
            total_stake = df['stake'].sum()
            total_profit = df['profit'].sum()
            total_roi = (total_profit / total_stake) * 100 if total_stake > 0 else 0
            
            # ROI mensal
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.to_period('M')
            monthly_profit = df.groupby('month')['profit'].sum()
            monthly_stake = df.groupby('month')['stake'].sum()
            monthly_roi = (monthly_profit / monthly_stake * 100).tolist()
            
            # ROI anualizado
            days = (df['date'].max() - df['date'].min()).days
            annualized_roi = ((1 + total_roi/100) ** (365/days) - 1) * 100 if days > 0 else 0
            
            # Métricas de risco
            returns = df['profit'] / df['stake']
            sharpe_ratio = self._calculate_sharpe_ratio(returns)
            sortino_ratio = self._calculate_sortino_ratio(returns)
            max_drawdown = self._calculate_max_drawdown(returns)
            
            # VaR e CVaR
            var_95 = np.percentile(returns, 5)
            cvar_95 = returns[returns <= var_95].mean()
            
            # Outras métricas
            calmar_ratio = annualized_roi / abs(max_drawdown) if max_drawdown != 0 else 0
            consistency_score = self._calculate_consistency_score(monthly_roi)
            profit_factor = abs(monthly_profit[monthly_profit > 0].sum() / monthly_profit[monthly_profit < 0].sum()) if monthly_profit[monthly_profit < 0].sum() != 0 else float('inf')
            
            return BacktestingMetrics(
                total_bets=total_bets,
                winning_bets=winning_bets,
                losing_bets=losing_bets,
                win_rate=win_rate,
                total_roi=total_roi,
                monthly_roi=monthly_roi,
                annualized_roi=annualized_roi,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                max_drawdown=max_drawdown,
                var_95=var_95,
                cvar_95=cvar_95,
                consistency_score=consistency_score,
                profit_factor=profit_factor,
                average_odds=df['odds'].mean(),
                average_stake=df['stake'].mean(),
                total_stake=total_stake,
                total_profit=total_profit
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular métricas: {e}")
            return self._empty_metrics()
    
    def _analyze_leagues(self, data: Dict[str, Any]) -> List[LeagueAnalysis]:
        """Analisa performance por liga"""
        try:
            bets = data.get('bets', [])
            if not bets:
                return []
            
            df = pd.DataFrame(bets)
            league_analysis = []
            
            for league in df['league'].unique():
                league_df = df[df['league'] == league]
                
                total_bets = len(league_df)
                win_rate = (len(league_df[league_df['result'] == 'win']) / total_bets) * 100
                total_stake = league_df['stake'].sum()
                total_profit = league_df['profit'].sum()
                roi = (total_profit / total_stake) * 100 if total_stake > 0 else 0
                
                # Melhor e pior mês
                league_df['month'] = pd.to_datetime(league_df['date']).dt.to_period('M')
                monthly_profit = league_df.groupby('month')['profit'].sum()
                best_month = monthly_profit.idxmax().strftime('%Y-%m') if not monthly_profit.empty else "N/A"
                worst_month = monthly_profit.idxmin().strftime('%Y-%m') if not monthly_profit.empty else "N/A"
                
                # Score de confiança
                confidence_score = min(100, max(0, win_rate * (1 + roi/100)))
                
                league_analysis.append(LeagueAnalysis(
                    league_name=league,
                    total_bets=total_bets,
                    win_rate=win_rate,
                    roi=roi,
                    profit=total_profit,
                    best_month=best_month,
                    worst_month=worst_month,
                    confidence_score=confidence_score
                ))
            
            return sorted(league_analysis, key=lambda x: x.roi, reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar ligas: {e}")
            return []
    
    def _calculate_monthly_breakdown(self, data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Calcula breakdown mensal"""
        try:
            bets = data.get('bets', [])
            if not bets:
                return {}
            
            df = pd.DataFrame(bets)
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.to_period('M')
            
            monthly_data = {}
            for month in df['month'].unique():
                month_df = df[df['month'] == month]
                month_str = month.strftime('%Y-%m')
                
                monthly_data[month_str] = {
                    'total_bets': len(month_df),
                    'win_rate': (len(month_df[month_df['result'] == 'win']) / len(month_df)) * 100,
                    'total_stake': month_df['stake'].sum(),
                    'total_profit': month_df['profit'].sum(),
                    'roi': (month_df['profit'].sum() / month_df['stake'].sum()) * 100 if month_df['stake'].sum() > 0 else 0,
                    'average_odds': month_df['odds'].mean(),
                    'sharpe_ratio': self._calculate_sharpe_ratio(month_df['profit'] / month_df['stake'])
                }
            
            return monthly_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular breakdown mensal: {e}")
            return {}
    
    def _analyze_risk(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Analisa métricas de risco"""
        try:
            bets = data.get('bets', [])
            if not bets:
                return {}
            
            df = pd.DataFrame(bets)
            returns = df['profit'] / df['stake']
            
            return {
                'volatility': returns.std() * np.sqrt(252),  # Volatilidade anualizada
                'skewness': returns.skew(),
                'kurtosis': returns.kurtosis(),
                'max_consecutive_losses': self._calculate_max_consecutive_losses(df),
                'max_consecutive_wins': self._calculate_max_consecutive_wins(df),
                'recovery_factor': abs(df['profit'].sum() / df['profit'].min()) if df['profit'].min() < 0 else float('inf'),
                'expectancy': returns.mean(),
                'win_loss_ratio': abs(returns[returns > 0].mean() / returns[returns < 0].mean()) if returns[returns < 0].mean() != 0 else float('inf')
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar risco: {e}")
            return {}
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calcula Sharpe Ratio"""
        try:
            if len(returns) < 2:
                return 0.0
            
            excess_returns = returns.mean() - risk_free_rate/252
            return excess_returns / returns.std() * np.sqrt(252) if returns.std() != 0 else 0.0
        except:
            return 0.0
    
    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calcula Sortino Ratio"""
        try:
            if len(returns) < 2:
                return 0.0
            
            excess_returns = returns.mean() - risk_free_rate/252
            downside_returns = returns[returns < 0]
            downside_std = downside_returns.std() if len(downside_returns) > 1 else 0
            
            return excess_returns / downside_std * np.sqrt(252) if downside_std != 0 else 0.0
        except:
            return 0.0
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calcula Maximum Drawdown"""
        try:
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return drawdown.min() * 100
        except:
            return 0.0
    
    def _calculate_consistency_score(self, monthly_roi: List[float]) -> float:
        """Calcula score de consistência"""
        try:
            if len(monthly_roi) < 2:
                return 0.0
            
            positive_months = sum(1 for roi in monthly_roi if roi > 0)
            return (positive_months / len(monthly_roi)) * 100
        except:
            return 0.0
    
    def _calculate_max_consecutive_losses(self, df: pd.DataFrame) -> int:
        """Calcula máximo de perdas consecutivas"""
        try:
            max_losses = 0
            current_losses = 0
            
            for result in df['result']:
                if result == 'loss':
                    current_losses += 1
                    max_losses = max(max_losses, current_losses)
                else:
                    current_losses = 0
            
            return max_losses
        except:
            return 0
    
    def _calculate_max_consecutive_wins(self, df: pd.DataFrame) -> int:
        """Calcula máximo de vitórias consecutivas"""
        try:
            max_wins = 0
            current_wins = 0
            
            for result in df['result']:
                if result == 'win':
                    current_wins += 1
                    max_wins = max(max_wins, current_wins)
                else:
                    current_wins = 0
            
            return max_wins
        except:
            return 0
    
    def _generate_recommendations(self, metrics: BacktestingMetrics, leagues: List[LeagueAnalysis]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Recomendações baseadas em ROI
        if metrics.total_roi < 5:
            recommendations.append("⚠️ ROI baixo - Revisar estratégia de seleção de apostas")
        elif metrics.total_roi > 20:
            recommendations.append("✅ ROI excelente - Considerar aumentar stake")
        
        # Recomendações baseadas em win rate
        if metrics.win_rate < 50:
            recommendations.append("⚠️ Taxa de acerto baixa - Melhorar critérios de seleção")
        elif metrics.win_rate > 70:
            recommendations.append("✅ Taxa de acerto excelente - Estratégia muito eficaz")
        
        # Recomendações baseadas em Sharpe Ratio
        if metrics.sharpe_ratio < 1:
            recommendations.append("⚠️ Sharpe Ratio baixo - Melhorar relação risco/retorno")
        elif metrics.sharpe_ratio > 2:
            recommendations.append("✅ Sharpe Ratio excelente - Estratégia muito eficiente")
        
        # Recomendações baseadas em drawdown
        if metrics.max_drawdown < -20:
            recommendations.append("🚨 Drawdown alto - Implementar gestão de risco mais conservadora")
        
        # Recomendações baseadas em consistência
        if metrics.consistency_score < 60:
            recommendations.append("⚠️ Baixa consistência - Revisar estabilidade da estratégia")
        
        # Recomendações por liga
        best_league = max(leagues, key=lambda x: x.roi) if leagues else None
        worst_league = min(leagues, key=lambda x: x.roi) if leagues else None
        
        if best_league and best_league.roi > metrics.total_roi * 1.5:
            recommendations.append(f"🎯 Focar mais em {best_league.league_name} - Performance superior")
        
        if worst_league and worst_league.roi < 0:
            recommendations.append(f"⚠️ Revisar estratégia para {worst_league.league_name} - Performance negativa")
        
        return recommendations
    
    def _get_disclaimer(self) -> str:
        """Retorna disclaimer legal"""
        return """
        DISCLAIMER: Este relatório de backtesting é fornecido apenas para fins informativos e educacionais. 
        Os resultados passados não garantem resultados futuros. Apostas esportivas envolvem risco de perda 
        de capital. Nunca aposte mais do que pode perder. Consulte sempre um profissional financeiro 
        antes de tomar decisões de investimento. A Cas Maravilha, proprietária da MaraBet AI, não se 
        responsabiliza por perdas financeiras decorrentes do uso deste sistema.
        """
    
    def _get_methodology(self) -> str:
        """Retorna metodologia do backtesting"""
        return """
        METODOLOGIA: Este backtesting foi realizado usando dados históricos reais de apostas esportivas. 
        A estratégia utiliza algoritmos de machine learning para análise de probabilidades e identificação 
        de value bets. As métricas de performance incluem ROI, Sharpe Ratio, Sortino Ratio, Maximum Drawdown 
        e outras medidas de risco. O período de teste foi selecionado para representar diferentes condições 
        de mercado e sazonalidade.
        """
    
    def _save_report(self, report: BacktestingReport):
        """Salva relatório em arquivo"""
        try:
            filename = f"backtesting_report_{report.report_id}.json"
            filepath = os.path.join(self.template_dir, filename)
            
            # Converter para dicionário
            report_dict = asdict(report)
            
            # Converter datetime para string
            for key, value in report_dict.items():
                if isinstance(value, datetime):
                    report_dict[key] = value.isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Relatório salvo em {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {e}")
    
    def generate_html_report(self, report: BacktestingReport) -> str:
        """Gera relatório HTML"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Backtesting - {report.strategy_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
        }}
        .metric-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border-left: 5px solid #667eea;
        }}
        .metric-card h3 {{
            margin-top: 0;
            color: #667eea;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .league-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .league-table th, .league-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .league-table th {{
            background-color: #667eea;
            color: white;
        }}
        .positive {{
            color: #28a745;
            font-weight: bold;
        }}
        .negative {{
            color: #dc3545;
            font-weight: bold;
        }}
        .recommendations {{
            background: #e8f5e8;
            padding: 30px;
            margin: 20px;
            border-radius: 10px;
            border-left: 5px solid #28a745;
        }}
        .disclaimer {{
            background: #fff3cd;
            padding: 20px;
            margin: 20px;
            border-radius: 10px;
            border-left: 5px solid #ffc107;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Relatório de Backtesting</h1>
            <h2>{report.strategy_name} v{report.strategy_version}</h2>
            <p>Período: {report.period_start.strftime('%d/%m/%Y')} - {report.period_end.strftime('%d/%m/%Y')}</p>
            <p>Gerado em: {report.generation_date.strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Total de Apostas</h3>
                <div class="metric-value">{report.overall_metrics.total_bets}</div>
            </div>
            <div class="metric-card">
                <h3>Taxa de Acerto</h3>
                <div class="metric-value">{report.overall_metrics.win_rate:.1f}%</div>
            </div>
            <div class="metric-card">
                <h3>ROI Total</h3>
                <div class="metric-value {'positive' if report.overall_metrics.total_roi > 0 else 'negative'}">
                    {report.overall_metrics.total_roi:.2f}%
                </div>
            </div>
            <div class="metric-card">
                <h3>ROI Anualizado</h3>
                <div class="metric-value {'positive' if report.overall_metrics.annualized_roi > 0 else 'negative'}">
                    {report.overall_metrics.annualized_roi:.2f}%
                </div>
            </div>
            <div class="metric-card">
                <h3>Sharpe Ratio</h3>
                <div class="metric-value">{report.overall_metrics.sharpe_ratio:.2f}</div>
            </div>
            <div class="metric-card">
                <h3>Max Drawdown</h3>
                <div class="metric-value negative">{report.overall_metrics.max_drawdown:.2f}%</div>
            </div>
            <div class="metric-card">
                <h3>Lucro Total</h3>
                <div class="metric-value {'positive' if report.overall_metrics.total_profit > 0 else 'negative'}">
                    {report.overall_metrics.total_profit:,.2f} AOA
                </div>
            </div>
            <div class="metric-card">
                <h3>Stake Total</h3>
                <div class="metric-value">{report.overall_metrics.total_stake:,.2f} AOA</div>
            </div>
        </div>
        
        <div style="padding: 40px;">
            <h2>Análise por Liga</h2>
            <table class="league-table">
                <thead>
                    <tr>
                        <th>Liga</th>
                        <th>Apostas</th>
                        <th>Taxa de Acerto</th>
                        <th>ROI</th>
                        <th>Lucro</th>
                        <th>Score de Confiança</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_league_table_rows(report.league_analysis)}
                </tbody>
            </table>
        </div>
        
        <div class="recommendations">
            <h3>💡 Recomendações</h3>
            <ul>
                {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
            </ul>
        </div>
        
        <div class="disclaimer">
            <h3>⚠️ Disclaimer</h3>
            <p>{report.disclaimer}</p>
        </div>
    </div>
</body>
</html>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar HTML: {e}")
            return ""
    
    def _generate_league_table_rows(self, leagues: List[LeagueAnalysis]) -> str:
        """Gera linhas da tabela de ligas"""
        html = ""
        for league in leagues:
            html += f"""
            <tr>
                <td>{league.league_name}</td>
                <td>{league.total_bets}</td>
                <td>{league.win_rate:.1f}%</td>
                <td class="{'positive' if league.roi > 0 else 'negative'}">{league.roi:.2f}%</td>
                <td class="{'positive' if league.profit > 0 else 'negative'}">{league.profit:,.2f} AOA</td>
                <td>{league.confidence_score:.1f}</td>
            </tr>
            """
        return html
    
    def _empty_metrics(self) -> BacktestingMetrics:
        """Retorna métricas vazias"""
        return BacktestingMetrics(
            total_bets=0,
            winning_bets=0,
            losing_bets=0,
            win_rate=0.0,
            total_roi=0.0,
            monthly_roi=[],
            annualized_roi=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            max_drawdown=0.0,
            var_95=0.0,
            cvar_95=0.0,
            consistency_score=0.0,
            profit_factor=0.0,
            average_odds=0.0,
            average_stake=0.0,
            total_stake=0.0,
            total_profit=0.0
        )

def main():
    """Função principal para demonstração"""
    # Dados de exemplo
    sample_data = {
        'period_start': '2024-01-01',
        'period_end': '2024-12-31',
        'bets': [
            {
                'date': '2024-01-15',
                'league': 'Premier League',
                'home_team': 'Arsenal',
                'away_team': 'Chelsea',
                'bet_type': '1X2',
                'selection': '1',
                'odds': 2.10,
                'stake': 100.0,
                'result': 'win',
                'profit': 110.0
            },
            {
                'date': '2024-01-16',
                'league': 'La Liga',
                'home_team': 'Real Madrid',
                'away_team': 'Barcelona',
                'bet_type': '1X2',
                'selection': 'X',
                'odds': 3.50,
                'stake': 50.0,
                'result': 'loss',
                'profit': -50.0
            }
            # Adicionar mais apostas conforme necessário
        ]
    }
    
    try:
        # Criar gerador
        generator = BacktestingReportGenerator()
        
        # Gerar relatório
        report = generator.generate_report(sample_data, "MaraBet AI Strategy", "1.0")
        
        # Gerar HTML
        html_content = generator.generate_html_report(report)
        
        # Salvar HTML
        with open("backtesting_report.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Template de relatório de backtesting criado com sucesso!")
        print(f"📊 Relatório ID: {report.report_id}")
        print(f"📈 ROI Total: {report.overall_metrics.total_roi:.2f}%")
        print(f"🎯 Taxa de Acerto: {report.overall_metrics.win_rate:.1f}%")
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
