#!/usr/bin/env python3
"""
Sistema de Backtesting Rigoroso para Validação de Modelos
MaraBet AI - Validação com 3+ anos de dados históricos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class ValidationStatus(Enum):
    """Status de validação"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class ValidationMetrics:
    """Métricas de validação"""
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    calmar_ratio: float
    sortino_ratio: float
    var_95: float
    cvar_95: float
    total_return: float
    annual_return: float
    volatility: float
    skewness: float
    kurtosis: float

@dataclass
class BacktestResult:
    """Resultado do backtesting"""
    start_date: datetime
    end_date: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    profit_factor: float
    metrics: ValidationMetrics
    validation_status: ValidationStatus
    warnings: List[str]
    critical_issues: List[str]

class RigorousBacktester:
    """Sistema de backtesting rigoroso"""
    
    def __init__(self, min_years: int = 3, min_trades: int = 100):
        """Inicializa backtester rigoroso"""
        self.min_years = min_years
        self.min_trades = min_trades
        self.validation_thresholds = {
            'sharpe_ratio': 1.5,
            'max_drawdown': 0.20,  # 20%
            'win_rate': 0.55,      # 55%
            'profit_factor': 1.3,
            'calmar_ratio': 1.0,
            'sortino_ratio': 2.0,
            'var_95': -0.05,       # -5%
            'cvar_95': -0.08       # -8%
        }
    
    def validate_data_requirements(self, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida requisitos mínimos de dados"""
        issues = []
        
        # Verificar se há dados suficientes
        if len(data) < self.min_trades:
            issues.append(f"Dados insuficientes: {len(data)} < {self.min_trades} trades mínimos")
        
        # Verificar período temporal
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            date_range = (data['date'].max() - data['date'].min()).days / 365.25
            if date_range < self.min_years:
                issues.append(f"Período insuficiente: {date_range:.1f} anos < {self.min_years} anos mínimos")
        
        # Verificar colunas obrigatórias
        required_columns = ['date', 'prediction', 'actual', 'odds', 'stake']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            issues.append(f"Colunas obrigatórias ausentes: {missing_columns}")
        
        return len(issues) == 0, issues
    
    def calculate_returns(self, data: pd.DataFrame) -> pd.Series:
        """Calcula retornos das apostas"""
        returns = []
        
        for _, row in data.iterrows():
            prediction = row['prediction']
            actual = row['actual']
            odds = row['odds']
            stake = row['stake']
            
            if prediction == actual:
                # Aposta vencedora
                return_val = (odds - 1) * stake
            else:
                # Aposta perdedora
                return_val = -stake
            
            returns.append(return_val)
        
        return pd.Series(returns, index=data.index)
    
    def calculate_metrics(self, returns: pd.Series) -> ValidationMetrics:
        """Calcula métricas de validação"""
        # Métricas básicas
        total_return = returns.sum()
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = returns.std() * np.sqrt(252)
        
        # Sharpe Ratio
        risk_free_rate = 0.02  # 2% ao ano
        sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Sortino Ratio
        downside_returns = returns[returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = (annual_return - risk_free_rate) / downside_volatility if downside_volatility > 0 else 0
        
        # Drawdown
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Calmar Ratio
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Win Rate
        win_rate = (returns > 0).mean()
        
        # Profit Factor
        gross_profit = returns[returns > 0].sum()
        gross_loss = abs(returns[returns < 0].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # VaR e CVaR (95%)
        var_95 = np.percentile(returns, 5)
        cvar_95 = returns[returns <= var_95].mean()
        
        # Skewness e Kurtosis
        skewness = returns.skew()
        kurtosis = returns.kurtosis()
        
        return ValidationMetrics(
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            calmar_ratio=calmar_ratio,
            sortino_ratio=sortino_ratio,
            var_95=var_95,
            cvar_95=cvar_95,
            total_return=total_return,
            annual_return=annual_return,
            volatility=volatility,
            skewness=skewness,
            kurtosis=kurtosis
        )
    
    def validate_metrics(self, metrics: ValidationMetrics) -> Tuple[ValidationStatus, List[str], List[str]]:
        """Valida métricas contra thresholds"""
        warnings = []
        critical_issues = []
        
        # Verificar Sharpe Ratio
        if metrics.sharpe_ratio < self.validation_thresholds['sharpe_ratio']:
            critical_issues.append(f"Sharpe Ratio {metrics.sharpe_ratio:.2f} < {self.validation_thresholds['sharpe_ratio']}")
        elif metrics.sharpe_ratio < 1.0:
            warnings.append(f"Sharpe Ratio baixo: {metrics.sharpe_ratio:.2f}")
        
        # Verificar Max Drawdown
        if abs(metrics.max_drawdown) > self.validation_thresholds['max_drawdown']:
            critical_issues.append(f"Max Drawdown {abs(metrics.max_drawdown):.1%} > {self.validation_thresholds['max_drawdown']:.1%}")
        elif abs(metrics.max_drawdown) > 0.15:
            warnings.append(f"Drawdown alto: {abs(metrics.max_drawdown):.1%}")
        
        # Verificar Win Rate
        if metrics.win_rate < self.validation_thresholds['win_rate']:
            critical_issues.append(f"Win Rate {metrics.win_rate:.1%} < {self.validation_thresholds['win_rate']:.1%}")
        elif metrics.win_rate < 0.50:
            warnings.append(f"Win Rate baixo: {metrics.win_rate:.1%}")
        
        # Verificar Profit Factor
        if metrics.profit_factor < self.validation_thresholds['profit_factor']:
            critical_issues.append(f"Profit Factor {metrics.profit_factor:.2f} < {self.validation_thresholds['profit_factor']}")
        elif metrics.profit_factor < 1.1:
            warnings.append(f"Profit Factor baixo: {metrics.profit_factor:.2f}")
        
        # Verificar Calmar Ratio
        if metrics.calmar_ratio < self.validation_thresholds['calmar_ratio']:
            warnings.append(f"Calmar Ratio baixo: {metrics.calmar_ratio:.2f}")
        
        # Verificar VaR
        if metrics.var_95 < self.validation_thresholds['var_95']:
            warnings.append(f"VaR 95% alto: {metrics.var_95:.1%}")
        
        # Determinar status
        if critical_issues:
            status = ValidationStatus.CRITICAL
        elif warnings:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.PASSED
        
        return status, warnings, critical_issues
    
    def run_backtest(self, data: pd.DataFrame) -> BacktestResult:
        """Executa backtesting rigoroso"""
        logger.info("Iniciando backtesting rigoroso...")
        
        # Validar requisitos de dados
        data_valid, data_issues = self.validate_data_requirements(data)
        if not data_valid:
            return BacktestResult(
                start_date=datetime.min,
                end_date=datetime.min,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                total_return=0,
                annual_return=0,
                max_drawdown=0,
                sharpe_ratio=0,
                win_rate=0,
                profit_factor=0,
                metrics=ValidationMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                validation_status=ValidationStatus.CRITICAL,
                warnings=[],
                critical_issues=data_issues
            )
        
        # Calcular retornos
        returns = self.calculate_returns(data)
        
        # Calcular métricas
        metrics = self.calculate_metrics(returns)
        
        # Validar métricas
        status, warnings, critical_issues = self.validate_metrics(metrics)
        
        # Estatísticas básicas
        total_trades = len(data)
        winning_trades = (returns > 0).sum()
        losing_trades = (returns < 0).sum()
        
        # Período
        start_date = data['date'].min() if 'date' in data.columns else datetime.min
        end_date = data['date'].max() if 'date' in data.columns else datetime.max
        
        return BacktestResult(
            start_date=start_date,
            end_date=end_date,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            total_return=metrics.total_return,
            annual_return=metrics.annual_return,
            max_drawdown=metrics.max_drawdown,
            sharpe_ratio=metrics.sharpe_ratio,
            win_rate=metrics.win_rate,
            profit_factor=metrics.profit_factor,
            metrics=metrics,
            validation_status=status,
            warnings=warnings,
            critical_issues=critical_issues
        )
    
    def generate_report(self, result: BacktestResult) -> str:
        """Gera relatório de validação"""
        report = []
        report.append("=" * 60)
        report.append("RELATÓRIO DE VALIDAÇÃO RIGOROSA - MARABET AI")
        report.append("=" * 60)
        
        # Status geral
        status_emoji = {
            ValidationStatus.PASSED: "✅",
            ValidationStatus.WARNING: "⚠️",
            ValidationStatus.FAILED: "❌",
            ValidationStatus.CRITICAL: "🚨"
        }
        
        report.append(f"\nSTATUS GERAL: {status_emoji[result.validation_status]} {result.validation_status.value.upper()}")
        
        # Período e trades
        report.append(f"\nPERÍODO: {result.start_date.strftime('%Y-%m-%d')} a {result.end_date.strftime('%Y-%m-%d')}")
        report.append(f"TOTAL DE TRADES: {result.total_trades}")
        report.append(f"TRADES VENCEDORES: {result.winning_trades}")
        report.append(f"TRADES PERDEDORES: {result.losing_trades}")
        
        # Métricas principais
        report.append(f"\nMÉTRICAS PRINCIPAIS:")
        report.append(f"  Retorno Total: {result.total_return:.2%}")
        report.append(f"  Retorno Anual: {result.annual_return:.2%}")
        report.append(f"  Volatilidade: {result.metrics.volatility:.2%}")
        report.append(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
        report.append(f"  Max Drawdown: {result.max_drawdown:.2%}")
        report.append(f"  Win Rate: {result.win_rate:.1%}")
        report.append(f"  Profit Factor: {result.profit_factor:.2f}")
        
        # Métricas avançadas
        report.append(f"\nMÉTRICAS AVANÇADAS:")
        report.append(f"  Calmar Ratio: {result.metrics.calmar_ratio:.2f}")
        report.append(f"  Sortino Ratio: {result.metrics.sortino_ratio:.2f}")
        report.append(f"  VaR 95%: {result.metrics.var_95:.2%}")
        report.append(f"  CVaR 95%: {result.metrics.cvar_95:.2%}")
        report.append(f"  Skewness: {result.metrics.skewness:.2f}")
        report.append(f"  Kurtosis: {result.metrics.kurtosis:.2f}")
        
        # Avisos e problemas
        if result.warnings:
            report.append(f"\n⚠️ AVISOS:")
            for warning in result.warnings:
                report.append(f"  - {warning}")
        
        if result.critical_issues:
            report.append(f"\n🚨 PROBLEMAS CRÍTICOS:")
            for issue in result.critical_issues:
                report.append(f"  - {issue}")
        
        # Recomendação
        if result.validation_status == ValidationStatus.PASSED:
            report.append(f"\n✅ RECOMENDAÇÃO: Sistema aprovado para produção")
        elif result.validation_status == ValidationStatus.WARNING:
            report.append(f"\n⚠️ RECOMENDAÇÃO: Revisar antes do deploy")
        else:
            report.append(f"\n🚨 RECOMENDAÇÃO: NÃO APROVADO para produção")
        
        report.append("=" * 60)
        
        return "\n".join(report)

# Instância global
rigorous_backtester = RigorousBacktester()

if __name__ == "__main__":
    # Teste do sistema de backtesting rigoroso
    print("🧪 TESTANDO SISTEMA DE BACKTESTING RIGOROSO")
    print("=" * 50)
    
    # Dados de exemplo (simulados)
    np.random.seed(42)
    dates = pd.date_range('2021-01-01', '2024-01-01', freq='D')
    n_trades = len(dates)
    
    # Simular dados de apostas
    data = pd.DataFrame({
        'date': dates,
        'prediction': np.random.choice(['home_win', 'draw', 'away_win'], n_trades),
        'actual': np.random.choice(['home_win', 'draw', 'away_win'], n_trades),
        'odds': np.random.uniform(1.5, 3.0, n_trades),
        'stake': np.random.uniform(50, 200, n_trades)
    })
    
    # Executar backtesting
    result = rigorous_backtester.run_backtest(data)
    
    # Gerar relatório
    report = rigorous_backtester.generate_report(result)
    print(report)
    
    print("\n🎉 TESTE DE BACKTESTING RIGOROSO CONCLUÍDO!")
