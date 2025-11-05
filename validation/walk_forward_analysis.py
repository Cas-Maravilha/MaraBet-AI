#!/usr/bin/env python3
"""
Walk-Forward Analysis para Validação Temporal
MaraBet AI - Análise com janelas temporais deslizantes
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

@dataclass
class WalkForwardWindow:
    """Janela temporal do walk-forward"""
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    train_size: int
    test_size: int

@dataclass
class WalkForwardResult:
    """Resultado do walk-forward analysis"""
    windows: List[WalkForwardWindow]
    train_metrics: List[Dict[str, float]]
    test_metrics: List[Dict[str, float]]
    overall_metrics: Dict[str, float]
    stability_score: float
    overfitting_detected: bool
    performance_degradation: bool

class WalkForwardAnalyzer:
    """Analisador de walk-forward"""
    
    def __init__(self, 
                 train_months: int = 12,
                 test_months: int = 3,
                 step_months: int = 1,
                 min_train_trades: int = 50,
                 min_test_trades: int = 20):
        """Inicializa analisador walk-forward"""
        self.train_months = train_months
        self.test_months = test_months
        self.step_months = step_months
        self.min_train_trades = min_train_trades
        self.min_test_trades = min_test_trades
    
    def create_windows(self, data: pd.DataFrame) -> List[WalkForwardWindow]:
        """Cria janelas temporais deslizantes"""
        if 'date' not in data.columns:
            raise ValueError("Coluna 'date' não encontrada nos dados")
        
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date').reset_index(drop=True)
        
        start_date = data['date'].min()
        end_date = data['date'].max()
        
        windows = []
        current_date = start_date
        
        while current_date + timedelta(days=30 * (self.train_months + self.test_months)) <= end_date:
            train_start = current_date
            train_end = current_date + timedelta(days=30 * self.train_months)
            test_start = train_end
            test_end = test_start + timedelta(days=30 * self.test_months)
            
            # Verificar se há dados suficientes
            train_data = data[(data['date'] >= train_start) & (data['date'] < train_end)]
            test_data = data[(data['date'] >= test_start) & (data['date'] < test_end)]
            
            if len(train_data) >= self.min_train_trades and len(test_data) >= self.min_test_trades:
                windows.append(WalkForwardWindow(
                    train_start=train_start,
                    train_end=train_end,
                    test_start=test_start,
                    test_end=test_end,
                    train_size=len(train_data),
                    test_size=len(test_data)
                ))
            
            current_date += timedelta(days=30 * self.step_months)
        
        return windows
    
    def calculate_window_metrics(self, data: pd.DataFrame, window: WalkForwardWindow) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Calcula métricas para uma janela específica"""
        # Dados de treino
        train_data = data[(data['date'] >= window.train_start) & (data['date'] < window.train_end)]
        train_returns = self._calculate_returns(train_data)
        
        # Dados de teste
        test_data = data[(data['date'] >= window.test_start) & (data['date'] < window.test_end)]
        test_returns = self._calculate_returns(test_data)
        
        # Métricas de treino
        train_metrics = self._calculate_metrics(train_returns)
        
        # Métricas de teste
        test_metrics = self._calculate_metrics(test_returns)
        
        return train_metrics, test_metrics
    
    def _calculate_returns(self, data: pd.DataFrame) -> pd.Series:
        """Calcula retornos das apostas"""
        returns = []
        
        for _, row in data.iterrows():
            prediction = row['prediction']
            actual = row['actual']
            odds = row['odds']
            stake = row['stake']
            
            if prediction == actual:
                return_val = (odds - 1) * stake
            else:
                return_val = -stake
            
            returns.append(return_val)
        
        return pd.Series(returns, index=data.index)
    
    def _calculate_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """Calcula métricas de performance"""
        if len(returns) == 0:
            return {
                'total_return': 0,
                'annual_return': 0,
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'calmar_ratio': 0,
                'sortino_ratio': 0
            }
        
        # Métricas básicas
        total_return = returns.sum()
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = returns.std() * np.sqrt(252)
        
        # Sharpe Ratio
        risk_free_rate = 0.02
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
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'calmar_ratio': calmar_ratio,
            'sortino_ratio': sortino_ratio
        }
    
    def analyze_stability(self, train_metrics: List[Dict[str, float]], 
                         test_metrics: List[Dict[str, float]]) -> Tuple[float, bool, bool]:
        """Analisa estabilidade e overfitting"""
        if len(train_metrics) < 2 or len(test_metrics) < 2:
            return 0.0, False, False
        
        # Calcular coeficientes de variação
        train_sharpe = [m['sharpe_ratio'] for m in train_metrics]
        test_sharpe = [m['sharpe_ratio'] for m in test_metrics]
        
        train_cv = np.std(train_sharpe) / np.mean(train_sharpe) if np.mean(train_sharpe) != 0 else 0
        test_cv = np.std(test_sharpe) / np.mean(test_sharpe) if np.mean(test_sharpe) != 0 else 0
        
        # Score de estabilidade (0-1, onde 1 é mais estável)
        stability_score = 1 - (train_cv + test_cv) / 2
        
        # Detectar overfitting
        avg_train_sharpe = np.mean(train_sharpe)
        avg_test_sharpe = np.mean(test_sharpe)
        overfitting_detected = avg_train_sharpe > avg_test_sharpe * 1.5
        
        # Detectar degradação de performance
        if len(test_sharpe) >= 3:
            recent_sharpe = np.mean(test_sharpe[-3:])
            early_sharpe = np.mean(test_sharpe[:3])
            performance_degradation = recent_sharpe < early_sharpe * 0.7
        else:
            performance_degradation = False
        
        return stability_score, overfitting_detected, performance_degradation
    
    def run_analysis(self, data: pd.DataFrame) -> WalkForwardResult:
        """Executa análise walk-forward completa"""
        logger.info("Iniciando walk-forward analysis...")
        
        # Criar janelas temporais
        windows = self.create_windows(data)
        
        if len(windows) == 0:
            raise ValueError("Não foi possível criar janelas temporais válidas")
        
        logger.info(f"Criadas {len(windows)} janelas temporais")
        
        # Calcular métricas para cada janela
        train_metrics = []
        test_metrics = []
        
        for i, window in enumerate(windows):
            logger.info(f"Processando janela {i+1}/{len(windows)}: {window.train_start.date()} - {window.test_end.date()}")
            
            try:
                train_m, test_m = self.calculate_window_metrics(data, window)
                train_metrics.append(train_m)
                test_metrics.append(test_m)
            except Exception as e:
                logger.error(f"Erro na janela {i+1}: {e}")
                continue
        
        # Calcular métricas gerais
        overall_metrics = self._calculate_overall_metrics(test_metrics)
        
        # Analisar estabilidade
        stability_score, overfitting_detected, performance_degradation = self.analyze_stability(
            train_metrics, test_metrics
        )
        
        return WalkForwardResult(
            windows=windows,
            train_metrics=train_metrics,
            test_metrics=test_metrics,
            overall_metrics=overall_metrics,
            stability_score=stability_score,
            overfitting_detected=overfitting_detected,
            performance_degradation=performance_degradation
        )
    
    def _calculate_overall_metrics(self, test_metrics: List[Dict[str, float]]) -> Dict[str, float]:
        """Calcula métricas gerais de todas as janelas de teste"""
        if not test_metrics:
            return {}
        
        # Médias das métricas
        overall = {}
        for key in test_metrics[0].keys():
            values = [m[key] for m in test_metrics if not np.isnan(m[key]) and not np.isinf(m[key])]
            if values:
                overall[key] = np.mean(values)
            else:
                overall[key] = 0.0
        
        return overall
    
    def generate_report(self, result: WalkForwardResult) -> str:
        """Gera relatório de walk-forward analysis"""
        report = []
        report.append("=" * 60)
        report.append("WALK-FORWARD ANALYSIS - MARABET AI")
        report.append("=" * 60)
        
        # Resumo geral
        report.append(f"\nRESUMO GERAL:")
        report.append(f"  Janelas Analisadas: {len(result.windows)}")
        report.append(f"  Score de Estabilidade: {result.stability_score:.2f}")
        report.append(f"  Overfitting Detectado: {'Sim' if result.overfitting_detected else 'Não'}")
        report.append(f"  Degradação de Performance: {'Sim' if result.performance_degradation else 'Não'}")
        
        # Métricas gerais
        if result.overall_metrics:
            report.append(f"\nMÉTRICAS GERAIS (TESTE):")
            for key, value in result.overall_metrics.items():
                if key in ['total_return', 'annual_return', 'volatility', 'max_drawdown', 'win_rate']:
                    report.append(f"  {key.replace('_', ' ').title()}: {value:.2%}")
                else:
                    report.append(f"  {key.replace('_', ' ').title()}: {value:.2f}")
        
        # Análise por janela
        report.append(f"\nANÁLISE POR JANELA:")
        for i, (window, train_m, test_m) in enumerate(zip(result.windows, result.train_metrics, result.test_metrics)):
            report.append(f"\n  Janela {i+1}: {window.train_start.date()} - {window.test_end.date()}")
            report.append(f"    Treino - Sharpe: {train_m['sharpe_ratio']:.2f}, Win Rate: {train_m['win_rate']:.1%}")
            report.append(f"    Teste  - Sharpe: {test_m['sharpe_ratio']:.2f}, Win Rate: {test_m['win_rate']:.1%}")
            
            # Detectar problemas
            if train_m['sharpe_ratio'] > test_m['sharpe_ratio'] * 2:
                report.append(f"    ⚠️ Possível overfitting detectado")
            if test_m['sharpe_ratio'] < 0:
                report.append(f"    ❌ Performance negativa no teste")
        
        # Recomendações
        report.append(f"\nRECOMENDAÇÕES:")
        if result.stability_score < 0.5:
            report.append(f"  ⚠️ Baixa estabilidade - revisar modelo")
        if result.overfitting_detected:
            report.append(f"  ⚠️ Overfitting detectado - reduzir complexidade")
        if result.performance_degradation:
            report.append(f"  ⚠️ Degradação de performance - retreinar modelo")
        
        if result.stability_score > 0.7 and not result.overfitting_detected and not result.performance_degradation:
            report.append(f"  ✅ Modelo estável e robusto")
        
        report.append("=" * 60)
        
        return "\n".join(report)

# Instância global
walk_forward_analyzer = WalkForwardAnalyzer()

if __name__ == "__main__":
    # Teste do walk-forward analysis
    print("🧪 TESTANDO WALK-FORWARD ANALYSIS")
    print("=" * 50)
    
    # Dados de exemplo (simulados)
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2024-01-01', freq='D')
    n_trades = len(dates)
    
    # Simular dados de apostas
    data = pd.DataFrame({
        'date': dates,
        'prediction': np.random.choice(['home_win', 'draw', 'away_win'], n_trades),
        'actual': np.random.choice(['home_win', 'draw', 'away_win'], n_trades),
        'odds': np.random.uniform(1.5, 3.0, n_trades),
        'stake': np.random.uniform(50, 200, n_trades)
    })
    
    # Executar análise
    result = walk_forward_analyzer.run_analysis(data)
    
    # Gerar relatório
    report = walk_forward_analyzer.generate_report(result)
    print(report)
    
    print("\n🎉 TESTE DE WALK-FORWARD ANALYSIS CONCLUÍDO!")
