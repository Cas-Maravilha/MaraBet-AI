#!/usr/bin/env python3
"""
Simulação Monte Carlo para Análise de Cenários de Risco
MaraBet AI - Simulação de cenários de perda e stress testing
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

class ScenarioType(Enum):
    """Tipos de cenários"""
    NORMAL = "normal"
    STRESS = "stress"
    CRISIS = "crisis"
    BLACK_SWAN = "black_swan"

@dataclass
class MonteCarloResult:
    """Resultado da simulação Monte Carlo"""
    scenario_type: ScenarioType
    simulations: int
    final_capital: List[float]
    max_drawdown: List[float]
    probability_of_ruin: float
    expected_return: float
    var_95: float
    cvar_95: float
    worst_case: float
    best_case: float
    median_case: float

class MonteCarloSimulator:
    """Simulador Monte Carlo para análise de risco"""
    
    def __init__(self, 
                 initial_capital: float = 10000,
                 simulations: int = 10000,
                 time_horizon: int = 252):  # 1 ano de trading
        """Inicializa simulador Monte Carlo"""
        self.initial_capital = initial_capital
        self.simulations = simulations
        self.time_horizon = time_horizon
        
        # Cenários de mercado
        self.scenarios = {
            ScenarioType.NORMAL: {
                'win_rate': 0.55,
                'avg_odds': 2.0,
                'volatility': 0.15,
                'correlation': 0.1
            },
            ScenarioType.STRESS: {
                'win_rate': 0.45,
                'avg_odds': 1.8,
                'volatility': 0.25,
                'correlation': 0.3
            },
            ScenarioType.CRISIS: {
                'win_rate': 0.35,
                'avg_odds': 1.6,
                'volatility': 0.40,
                'correlation': 0.6
            },
            ScenarioType.BLACK_SWAN: {
                'win_rate': 0.25,
                'avg_odds': 1.4,
                'volatility': 0.60,
                'correlation': 0.8
            }
        }
    
    def simulate_trading_period(self, 
                               scenario: ScenarioType,
                               position_size: float = 0.05,
                               kelly_fraction: float = 0.25) -> List[float]:
        """Simula um período de trading"""
        params = self.scenarios[scenario]
        
        # Gerar retornos diários
        daily_returns = []
        capital = self.initial_capital
        
        for day in range(self.time_horizon):
            # Simular resultado da aposta
            is_winner = np.random.random() < params['win_rate']
            
            # Simular odds (com volatilidade)
            odds = np.random.normal(params['avg_odds'], params['volatility'] * params['avg_odds'])
            odds = max(1.1, odds)  # Odds mínimas
            
            # Calcular tamanho da posição
            if kelly_fraction > 0:
                # Kelly Criterion
                kelly_size = kelly_fraction * position_size * capital
            else:
                # Tamanho fixo
                kelly_size = position_size * capital
            
            # Limitar tamanho da posição
            kelly_size = min(kelly_size, capital * 0.1)  # Máximo 10% do capital
            
            # Calcular retorno
            if is_winner:
                daily_return = (odds - 1) * kelly_size
            else:
                daily_return = -kelly_size
            
            # Aplicar correlação (períodos de perda consecutivos)
            if len(daily_returns) > 0 and daily_returns[-1] < 0:
                if np.random.random() < params['correlation']:
                    daily_return = -abs(daily_return)  # Manter perda
            
            daily_returns.append(daily_return)
            capital += daily_return
            
            # Parar se capital muito baixo
            if capital < self.initial_capital * 0.1:  # 10% do capital inicial
                break
        
        return daily_returns
    
    def run_simulation(self, 
                      scenario: ScenarioType,
                      position_size: float = 0.05,
                      kelly_fraction: float = 0.25) -> MonteCarloResult:
        """Executa simulação Monte Carlo"""
        logger.info(f"Iniciando simulação Monte Carlo - Cenário: {scenario.value}")
        
        all_simulations = []
        final_capitals = []
        max_drawdowns = []
        
        for sim in range(self.simulations):
            if sim % 1000 == 0:
                logger.info(f"Simulação {sim}/{self.simulations}")
            
            # Simular período de trading
            daily_returns = self.simulate_trading_period(scenario, position_size, kelly_fraction)
            
            # Calcular capital final
            final_capital = self.initial_capital + sum(daily_returns)
            final_capitals.append(final_capital)
            
            # Calcular max drawdown
            if daily_returns:
                cumulative = np.cumsum([self.initial_capital] + daily_returns)
                running_max = np.maximum.accumulate(cumulative)
                drawdowns = (cumulative - running_max) / running_max
                max_drawdown = np.min(drawdowns)
                max_drawdowns.append(max_drawdown)
            else:
                max_drawdowns.append(0)
            
            all_simulations.append(daily_returns)
        
        # Calcular estatísticas
        final_capitals = np.array(final_capitals)
        max_drawdowns = np.array(max_drawdowns)
        
        # Probabilidade de ruína (capital < 20% do inicial)
        ruin_threshold = self.initial_capital * 0.2
        probability_of_ruin = np.mean(final_capitals < ruin_threshold)
        
        # VaR e CVaR
        var_95 = np.percentile(final_capitals, 5)
        cvar_95 = np.mean(final_capitals[final_capitals <= var_95])
        
        # Estatísticas gerais
        expected_return = np.mean(final_capitals)
        worst_case = np.min(final_capitals)
        best_case = np.max(final_capitals)
        median_case = np.median(final_capitals)
        
        return MonteCarloResult(
            scenario_type=scenario,
            simulations=self.simulations,
            final_capital=final_capitals.tolist(),
            max_drawdown=max_drawdowns.tolist(),
            probability_of_ruin=probability_of_ruin,
            expected_return=expected_return,
            var_95=var_95,
            cvar_95=cvar_95,
            worst_case=worst_case,
            best_case=best_case,
            median_case=median_case
        )
    
    def run_stress_test(self, 
                       position_sizes: List[float] = [0.01, 0.02, 0.05, 0.10],
                       kelly_fractions: List[float] = [0.0, 0.25, 0.50, 1.0]) -> Dict[str, Any]:
        """Executa stress test com diferentes parâmetros"""
        logger.info("Iniciando stress test...")
        
        results = {}
        
        for scenario in ScenarioType:
            scenario_results = {}
            
            for pos_size in position_sizes:
                for kelly_frac in kelly_fractions:
                    key = f"pos_{pos_size}_kelly_{kelly_frac}"
                    
                    # Executar simulação com menos iterações para stress test
                    original_simulations = self.simulations
                    self.simulations = 1000  # Reduzir para stress test
                    
                    result = self.run_simulation(scenario, pos_size, kelly_frac)
                    
                    scenario_results[key] = {
                        'position_size': pos_size,
                        'kelly_fraction': kelly_frac,
                        'probability_of_ruin': result.probability_of_ruin,
                        'expected_return': result.expected_return,
                        'var_95': result.var_95,
                        'worst_case': result.worst_case,
                        'median_case': result.median_case
                    }
                    
                    self.simulations = original_simulations
            
            results[scenario.value] = scenario_results
        
        return results
    
    def generate_report(self, result: MonteCarloResult) -> str:
        """Gera relatório da simulação"""
        report = []
        report.append("=" * 60)
        report.append("SIMULAÇÃO MONTE CARLO - MARABET AI")
        report.append("=" * 60)
        
        # Informações gerais
        report.append(f"\nCENÁRIO: {result.scenario_type.value.upper()}")
        report.append(f"Simulações: {result.simulations:,}")
        report.append(f"Horizonte Temporal: {self.time_horizon} dias")
        report.append(f"Capital Inicial: R$ {self.initial_capital:,.2f}")
        
        # Resultados principais
        report.append(f"\nRESULTADOS PRINCIPAIS:")
        report.append(f"  Capital Esperado: R$ {result.expected_return:,.2f}")
        report.append(f"  Retorno Esperado: {((result.expected_return / self.initial_capital) - 1) * 100:.1f}%")
        report.append(f"  Melhor Caso: R$ {result.best_case:,.2f}")
        report.append(f"  Pior Caso: R$ {result.worst_case:,.2f}")
        report.append(f"  Caso Mediano: R$ {result.median_case:,.2f}")
        
        # Análise de risco
        report.append(f"\nANÁLISE DE RISCO:")
        report.append(f"  Probabilidade de Ruína: {result.probability_of_ruin:.1%}")
        report.append(f"  VaR 95%: R$ {result.var_95:,.2f}")
        report.append(f"  CVaR 95%: R$ {result.cvar_95:,.2f}")
        
        # Drawdown
        avg_max_drawdown = np.mean(result.max_drawdown)
        worst_drawdown = np.min(result.max_drawdown)
        report.append(f"  Drawdown Médio: {avg_max_drawdown:.1%}")
        report.append(f"  Pior Drawdown: {worst_drawdown:.1%}")
        
        # Distribuição de resultados
        final_capitals = np.array(result.final_capital)
        profitable_sims = np.sum(final_capitals > self.initial_capital)
        report.append(f"\nDISTRIBUIÇÃO:")
        report.append(f"  Simulações Lucrativas: {profitable_sims:,} ({profitable_sims/len(final_capitals)*100:.1f}%)")
        report.append(f"  Simulações com Perda: {len(final_capitals) - profitable_sims:,}")
        
        # Percentis
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        report.append(f"\nPERCENTIS DE CAPITAL FINAL:")
        for p in percentiles:
            value = np.percentile(final_capitals, p)
            report.append(f"  {p:2d}%: R$ {value:,.2f}")
        
        # Recomendações
        report.append(f"\nRECOMENDAÇÕES:")
        if result.probability_of_ruin > 0.1:
            report.append(f"  🚨 ALTA probabilidade de ruína - reduzir tamanho das posições")
        elif result.probability_of_ruin > 0.05:
            report.append(f"  ⚠️ MÉDIA probabilidade de ruína - monitorar de perto")
        else:
            report.append(f"  ✅ BAIXA probabilidade de ruína - parâmetros adequados")
        
        if result.var_95 < self.initial_capital * 0.5:
            report.append(f"  🚨 VaR 95% muito baixo - risco de perda significativa")
        
        if avg_max_drawdown < -0.3:
            report.append(f"  ⚠️ Drawdown médio alto - considerar stop loss mais agressivo")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def generate_stress_report(self, stress_results: Dict[str, Any]) -> str:
        """Gera relatório de stress test"""
        report = []
        report.append("=" * 60)
        report.append("STRESS TEST - MARABET AI")
        report.append("=" * 60)
        
        for scenario, results in stress_results.items():
            report.append(f"\nCENÁRIO: {scenario.upper()}")
            report.append("-" * 40)
            
            # Encontrar melhor e pior configuração
            best_config = None
            worst_config = None
            best_return = -float('inf')
            worst_return = float('inf')
            
            for config, data in results.items():
                if data['expected_return'] > best_return:
                    best_return = data['expected_return']
                    best_config = config
                
                if data['expected_return'] < worst_return:
                    worst_return = data['expected_return']
                    worst_config = config
            
            if best_config:
                best_data = results[best_config]
                report.append(f"  MELHOR CONFIGURAÇÃO: {best_config}")
                report.append(f"    Retorno Esperado: R$ {best_data['expected_return']:,.2f}")
                report.append(f"    Prob. Ruína: {best_data['probability_of_ruin']:.1%}")
                report.append(f"    VaR 95%: R$ {best_data['var_95']:,.2f}")
            
            if worst_config:
                worst_data = results[worst_config]
                report.append(f"  PIOR CONFIGURAÇÃO: {worst_config}")
                report.append(f"    Retorno Esperado: R$ {worst_data['expected_return']:,.2f}")
                report.append(f"    Prob. Ruína: {worst_data['probability_of_ruin']:.1%}")
                report.append(f"    VaR 95%: R$ {worst_data['var_95']:,.2f}")
        
        report.append("=" * 60)
        return "\n".join(report)

# Instância global
monte_carlo_simulator = MonteCarloSimulator()

if __name__ == "__main__":
    # Teste da simulação Monte Carlo
    print("🧪 TESTANDO SIMULAÇÃO MONTE CARLO")
    print("=" * 50)
    
    # Simulação normal
    result = monte_carlo_simulator.run_simulation(ScenarioType.NORMAL)
    report = monte_carlo_simulator.generate_report(result)
    print(report)
    
    # Stress test
    print("\n" + "="*60)
    print("EXECUTANDO STRESS TEST...")
    stress_results = monte_carlo_simulator.run_stress_test()
    stress_report = monte_carlo_simulator.generate_stress_report(stress_results)
    print(stress_report)
    
    print("\n🎉 TESTE DE SIMULAÇÃO MONTE CARLO CONCLUÍDO!")
