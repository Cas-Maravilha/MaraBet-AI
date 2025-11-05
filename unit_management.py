"""
Sistema de Gestão de Unidades - MaraBet AI
Sistema especializado para gestão de unidades baseado em níveis de confiança
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
from enum import Enum
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Níveis de confiança para gestão de unidades"""
    HIGH = "HIGH"           # 85-90% - 2-3 unidades
    MEDIUM_HIGH = "MEDIUM_HIGH"  # 75-84% - 1.5-2 unidades
    MEDIUM = "MEDIUM"       # 70-74% - 1-1.5 unidades
    LOW = "LOW"             # <70% - 0.5-1 unidades

@dataclass
class UnitConfig:
    """Configuração de gestão de unidades"""
    base_unit_value: float = 100.0  # Valor base de 1 unidade
    max_units_per_bet: float = 3.0  # Máximo de unidades por aposta
    min_units_per_bet: float = 0.5  # Mínimo de unidades por aposta
    
    # Configurações por nível de confiança
    high_confidence_units: Tuple[float, float] = (2.0, 3.0)      # 85-90%
    medium_high_confidence_units: Tuple[float, float] = (1.5, 2.0)  # 75-84%
    medium_confidence_units: Tuple[float, float] = (1.0, 1.5)    # 70-74%
    low_confidence_units: Tuple[float, float] = (0.5, 1.0)       # <70%
    
    # Fatores de ajuste
    bankroll_factor: bool = True      # Ajustar baseado no capital
    performance_factor: bool = True   # Ajustar baseado na performance
    streak_factor: bool = True        # Ajustar baseado em sequências
    volatility_factor: bool = True    # Ajustar baseado na volatilidade

@dataclass
class UnitRecommendation:
    """Recomendação de unidades para uma aposta"""
    confidence_level: ConfidenceLevel
    confidence_percentage: float
    recommended_units: float
    unit_value: float
    total_stake: float
    adjustment_factors: Dict
    reasoning: List[str]
    timestamp: datetime

@dataclass
class UnitPerformance:
    """Performance das unidades por nível de confiança"""
    confidence_level: ConfidenceLevel
    total_bets: int
    winning_bets: int
    win_rate: float
    total_units_staked: float
    total_units_profit: float
    roi: float
    average_units_per_bet: float
    best_streak: int
    worst_streak: int

class UnitManager:
    """
    Gerenciador de Unidades baseado em Confiança
    Implementa sistema de unidades recomendadas por nível de confiança
    """
    
    def __init__(self, config: Optional[UnitConfig] = None):
        self.config = config or UnitConfig()
        self.unit_history = []
        self.performance_by_level = {}
        self.current_bankroll = 1000.0
        self.performance_metrics = {}
        
    def calculate_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """
        Calcula nível de confiança baseado na porcentagem
        """
        if confidence >= 0.85:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.75:
            return ConfidenceLevel.MEDIUM_HIGH
        elif confidence >= 0.70:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def get_unit_range(self, confidence_level: ConfidenceLevel) -> Tuple[float, float]:
        """
        Retorna faixa de unidades recomendadas para o nível de confiança
        """
        unit_ranges = {
            ConfidenceLevel.HIGH: self.config.high_confidence_units,
            ConfidenceLevel.MEDIUM_HIGH: self.config.medium_high_confidence_units,
            ConfidenceLevel.MEDIUM: self.config.medium_confidence_units,
            ConfidenceLevel.LOW: self.config.low_confidence_units
        }
        
        return unit_ranges[confidence_level]
    
    def calculate_recommended_units(self, confidence: float, 
                                  expected_value: float = 0.0,
                                  bankroll_percentage: float = 0.0,
                                  recent_performance: float = 0.0,
                                  current_streak: int = 0) -> UnitRecommendation:
        """
        Calcula unidades recomendadas baseado em múltiplos fatores
        """
        logger.info(f"Calculando unidades recomendadas: confiança={confidence:.1%}")
        
        try:
            # Determina nível de confiança
            confidence_level = self.calculate_confidence_level(confidence)
            
            # Obtém faixa base de unidades
            min_units, max_units = self.get_unit_range(confidence_level)
            
            # Calcula unidades base
            base_units = (min_units + max_units) / 2
            
            # Aplica fatores de ajuste
            adjustment_factors = {}
            reasoning = []
            
            # Fator de valor esperado
            ev_factor = 1.0
            if expected_value > 0.15:
                ev_factor = 1.2
                reasoning.append("Alto valor esperado (+20%)")
            elif expected_value > 0.10:
                ev_factor = 1.1
                reasoning.append("Bom valor esperado (+10%)")
            elif expected_value < 0.05:
                ev_factor = 0.8
                reasoning.append("Baixo valor esperado (-20%)")
            
            adjustment_factors['ev_factor'] = ev_factor
            
            # Fator de performance recente
            performance_factor = 1.0
            if self.config.performance_factor:
                if recent_performance > 0.15:
                    performance_factor = 1.1
                    reasoning.append("Performance recente positiva (+10%)")
                elif recent_performance < -0.10:
                    performance_factor = 0.9
                    reasoning.append("Performance recente negativa (-10%)")
            
            adjustment_factors['performance_factor'] = performance_factor
            
            # Fator de sequência
            streak_factor = 1.0
            if self.config.streak_factor:
                if current_streak > 3:
                    streak_factor = 0.9
                    reasoning.append("Sequência longa - reduzir exposição (-10%)")
                elif current_streak < -3:
                    streak_factor = 1.1
                    reasoning.append("Sequência negativa - oportunidade (+10%)")
            
            adjustment_factors['streak_factor'] = streak_factor
            
            # Fator de volatilidade do banco
            volatility_factor = 1.0
            if self.config.volatility_factor and bankroll_percentage > 0:
                if bankroll_percentage > 0.20:  # Capital cresceu mais de 20%
                    volatility_factor = 1.1
                    reasoning.append("Capital em alta - aumentar exposição (+10%)")
                elif bankroll_percentage < -0.15:  # Capital caiu mais de 15%
                    volatility_factor = 0.8
                    reasoning.append("Capital em baixa - reduzir exposição (-20%)")
            
            adjustment_factors['volatility_factor'] = volatility_factor
            
            # Calcula unidades ajustadas
            adjusted_units = base_units * ev_factor * performance_factor * streak_factor * volatility_factor
            
            # Aplica limites
            adjusted_units = max(self.config.min_units_per_bet, 
                               min(adjusted_units, self.config.max_units_per_bet))
            
            # Calcula valor da unidade e stake total
            unit_value = self.current_bankroll * 0.01  # 1% do capital por unidade
            total_stake = adjusted_units * unit_value
            
            # Adiciona reasoning baseado no nível de confiança
            confidence_reasoning = {
                ConfidenceLevel.HIGH: "Alta confiança - máximo de unidades",
                ConfidenceLevel.MEDIUM_HIGH: "Confiança média-alta - unidades moderadas",
                ConfidenceLevel.MEDIUM: "Confiança média - unidades conservadoras",
                ConfidenceLevel.LOW: "Baixa confiança - unidades mínimas"
            }
            reasoning.append(confidence_reasoning[confidence_level])
            
            return UnitRecommendation(
                confidence_level=confidence_level,
                confidence_percentage=confidence,
                recommended_units=adjusted_units,
                unit_value=unit_value,
                total_stake=total_stake,
                adjustment_factors=adjustment_factors,
                reasoning=reasoning,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro no cálculo de unidades: {e}")
            # Retorna recomendação conservadora em caso de erro
            return UnitRecommendation(
                confidence_level=ConfidenceLevel.LOW,
                confidence_percentage=confidence,
                recommended_units=0.5,
                unit_value=self.current_bankroll * 0.01,
                total_stake=self.current_bankroll * 0.005,
                adjustment_factors={'error': str(e)},
                reasoning=['Erro no cálculo - usar unidades mínimas'],
                timestamp=datetime.now()
            )
    
    def execute_unit_bet(self, unit_recommendation: UnitRecommendation,
                        bet_outcome: str, actual_result: str,
                        odds: float) -> Dict:
        """
        Executa aposta usando sistema de unidades
        """
        logger.info(f"Executando aposta com {unit_recommendation.recommended_units:.1f} unidades")
        
        try:
            # Verifica se a aposta foi vencedora
            is_winner = self._check_bet_result(bet_outcome, actual_result)
            
            # Calcula resultado financeiro
            if is_winner:
                profit = unit_recommendation.total_stake * (odds - 1)
                result = 'WIN'
            else:
                profit = -unit_recommendation.total_stake
                result = 'LOSS'
            
            # Atualiza capital
            self.current_bankroll += profit
            
            # Registra no histórico
            bet_record = {
                'timestamp': unit_recommendation.timestamp,
                'confidence_level': unit_recommendation.confidence_level.value,
                'confidence_percentage': unit_recommendation.confidence_percentage,
                'recommended_units': unit_recommendation.recommended_units,
                'unit_value': unit_recommendation.unit_value,
                'total_stake': unit_recommendation.total_stake,
                'odds': odds,
                'bet_outcome': bet_outcome,
                'actual_result': actual_result,
                'is_winner': is_winner,
                'profit': profit,
                'profit_units': profit / unit_recommendation.unit_value,
                'capital_before': self.current_bankroll - profit,
                'capital_after': self.current_bankroll,
                'result': result,
                'adjustment_factors': unit_recommendation.adjustment_factors
            }
            
            self.unit_history.append(bet_record)
            
            # Atualiza performance por nível
            self._update_performance_by_level(bet_record)
            
            return {
                'success': True,
                'bet_record': bet_record,
                'new_capital': self.current_bankroll,
                'profit': profit,
                'profit_units': profit / unit_recommendation.unit_value,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Erro na execução da aposta: {e}")
            return {
                'success': False,
                'error': str(e),
                'bet_record': None
            }
    
    def get_unit_performance_by_level(self) -> Dict[str, UnitPerformance]:
        """
        Retorna performance das unidades por nível de confiança
        """
        performance = {}
        
        for level in ConfidenceLevel:
            level_bets = [bet for bet in self.unit_history 
                         if bet['confidence_level'] == level.value]
            
            if not level_bets:
                performance[level.value] = UnitPerformance(
                    confidence_level=level,
                    total_bets=0,
                    winning_bets=0,
                    win_rate=0.0,
                    total_units_staked=0.0,
                    total_units_profit=0.0,
                    roi=0.0,
                    average_units_per_bet=0.0,
                    best_streak=0,
                    worst_streak=0
                )
                continue
            
            # Calcula métricas
            total_bets = len(level_bets)
            winning_bets = len([bet for bet in level_bets if bet['is_winner']])
            win_rate = winning_bets / total_bets if total_bets > 0 else 0
            
            total_units_staked = sum([bet['recommended_units'] for bet in level_bets])
            total_units_profit = sum([bet['profit_units'] for bet in level_bets])
            roi = (total_units_profit / total_units_staked * 100) if total_units_staked > 0 else 0
            
            average_units = np.mean([bet['recommended_units'] for bet in level_bets])
            
            # Calcula sequências
            results = [bet['is_winner'] for bet in level_bets]
            best_streak = self._calculate_max_streak(results, True)
            worst_streak = self._calculate_max_streak(results, False)
            
            performance[level.value] = UnitPerformance(
                confidence_level=level,
                total_bets=total_bets,
                winning_bets=winning_bets,
                win_rate=win_rate,
                total_units_staked=total_units_staked,
                total_units_profit=total_units_profit,
                roi=roi,
                average_units_per_bet=average_units,
                best_streak=best_streak,
                worst_streak=worst_streak
            )
        
        return performance
    
    def get_unit_analytics(self) -> Dict:
        """
        Retorna analytics completos do sistema de unidades
        """
        if not self.unit_history:
            return {'total_bets': 0}
        
        # Estatísticas gerais
        total_bets = len(self.unit_history)
        winning_bets = len([bet for bet in self.unit_history if bet['is_winner']])
        win_rate = winning_bets / total_bets if total_bets > 0 else 0
        
        # Estatísticas de unidades
        total_units_staked = sum([bet['recommended_units'] for bet in self.unit_history])
        total_units_profit = sum([bet['profit_units'] for bet in self.unit_history])
        average_units_per_bet = np.mean([bet['recommended_units'] for bet in self.unit_history])
        
        # Performance por nível
        performance_by_level = self.get_unit_performance_by_level()
        
        # Análise de confiança
        confidence_analysis = self._analyze_confidence_performance()
        
        # Tendências
        trends = self._analyze_unit_trends()
        
        return {
            'total_bets': total_bets,
            'winning_bets': winning_bets,
            'win_rate': win_rate,
            'total_units_staked': total_units_staked,
            'total_units_profit': total_units_profit,
            'average_units_per_bet': average_units_per_bet,
            'performance_by_level': performance_by_level,
            'confidence_analysis': confidence_analysis,
            'trends': trends,
            'current_bankroll': self.current_bankroll,
            'unit_value': self.current_bankroll * 0.01
        }
    
    def optimize_unit_ranges(self, historical_data: List[Dict]) -> Dict:
        """
        Otimiza faixas de unidades baseado em dados históricos
        """
        logger.info("Otimizando faixas de unidades")
        
        try:
            # Simula diferentes faixas de unidades
            test_ranges = {
                'conservative': {
                    'high': (1.5, 2.5),
                    'medium_high': (1.0, 1.8),
                    'medium': (0.8, 1.3),
                    'low': (0.3, 0.8)
                },
                'moderate': {
                    'high': (2.0, 3.0),
                    'medium_high': (1.5, 2.0),
                    'medium': (1.0, 1.5),
                    'low': (0.5, 1.0)
                },
                'aggressive': {
                    'high': (2.5, 3.5),
                    'medium_high': (1.8, 2.5),
                    'medium': (1.3, 1.8),
                    'low': (0.8, 1.3)
                }
            }
            
            results = {}
            
            for strategy, ranges in test_ranges.items():
                # Simula performance com essas faixas
                performance = self._simulate_unit_strategy(historical_data, ranges)
                results[strategy] = performance
            
            # Encontra melhor estratégia
            best_strategy = max(results.keys(), key=lambda k: results[k]['total_roi'])
            
            return {
                'success': True,
                'results': results,
                'best_strategy': best_strategy,
                'best_performance': results[best_strategy],
                'recommendation': self._get_strategy_recommendation(results, best_strategy)
            }
            
        except Exception as e:
            logger.error(f"Erro na otimização de unidades: {e}")
            return {'success': False, 'error': str(e)}
    
    def _check_bet_result(self, bet_outcome: str, actual_result: str) -> bool:
        """Verifica se a aposta foi vencedora"""
        return bet_outcome == actual_result
    
    def _update_performance_by_level(self, bet_record: Dict):
        """Atualiza performance por nível de confiança"""
        level = bet_record['confidence_level']
        
        if level not in self.performance_by_level:
            self.performance_by_level[level] = {
                'total_bets': 0,
                'winning_bets': 0,
                'total_units_staked': 0.0,
                'total_units_profit': 0.0
            }
        
        self.performance_by_level[level]['total_bets'] += 1
        if bet_record['is_winner']:
            self.performance_by_level[level]['winning_bets'] += 1
        
        self.performance_by_level[level]['total_units_staked'] += bet_record['recommended_units']
        self.performance_by_level[level]['total_units_profit'] += bet_record['profit_units']
    
    def _calculate_max_streak(self, results: List[bool], is_win: bool) -> int:
        """Calcula sequência máxima de vitórias ou derrotas"""
        current_streak = 0
        max_streak = 0
        
        for result in results:
            if result == is_win:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _analyze_confidence_performance(self) -> Dict:
        """Analisa performance por nível de confiança"""
        if not self.unit_history:
            return {}
        
        df = pd.DataFrame(self.unit_history)
        
        # Agrupa por nível de confiança
        confidence_groups = df.groupby('confidence_level').agg({
            'is_winner': ['count', 'sum', 'mean'],
            'profit_units': ['sum', 'mean'],
            'recommended_units': 'mean'
        }).round(3)
        
        # Calcula ROI por nível
        roi_by_level = {}
        for level in df['confidence_level'].unique():
            level_data = df[df['confidence_level'] == level]
            total_units = level_data['recommended_units'].sum()
            total_profit = level_data['profit_units'].sum()
            roi = (total_profit / total_units * 100) if total_units > 0 else 0
            roi_by_level[level] = roi
        
        return {
            'performance_by_level': confidence_groups.to_dict(),
            'roi_by_level': roi_by_level,
            'best_performing_level': max(roi_by_level.keys(), key=lambda k: roi_by_level[k]) if roi_by_level else None
        }
    
    def _analyze_unit_trends(self) -> Dict:
        """Analisa tendências do sistema de unidades"""
        if not self.unit_history:
            return {}
        
        df = pd.DataFrame(self.unit_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        # Tendência de unidades por período
        recent_data = df.last('7D')
        if not recent_data.empty:
            recent_units = recent_data['recommended_units'].mean()
            overall_units = df['recommended_units'].mean()
            unit_trend = 'INCREASING' if recent_units > overall_units else 'DECREASING'
        else:
            unit_trend = 'STABLE'
        
        # Tendência de performance
        recent_performance = recent_data['profit_units'].sum() if not recent_data.empty else 0
        overall_performance = df['profit_units'].sum()
        
        return {
            'unit_trend': unit_trend,
            'recent_units_avg': recent_units if not recent_data.empty else 0,
            'overall_units_avg': overall_units,
            'recent_performance': recent_performance,
            'overall_performance': overall_performance
        }
    
    def _simulate_unit_strategy(self, historical_data: List[Dict], ranges: Dict) -> Dict:
        """Simula performance de uma estratégia de unidades"""
        # Implementação simplificada para demonstração
        total_roi = 0
        total_bets = 0
        
        for data in historical_data:
            # Simula cálculo de unidades baseado nas faixas
            confidence = data.get('confidence', 0.5)
            if confidence >= 0.85:
                units = np.random.uniform(ranges['high'][0], ranges['high'][1])
            elif confidence >= 0.75:
                units = np.random.uniform(ranges['medium_high'][0], ranges['medium_high'][1])
            elif confidence >= 0.70:
                units = np.random.uniform(ranges['medium'][0], ranges['medium'][1])
            else:
                units = np.random.uniform(ranges['low'][0], ranges['low'][1])
            
            # Simula resultado
            expected_value = data.get('expected_value', 0.1)
            if expected_value > 0:
                total_roi += expected_value * units
                total_bets += 1
        
        return {
            'total_roi': total_roi,
            'total_bets': total_bets,
            'avg_roi_per_bet': total_roi / total_bets if total_bets > 0 else 0
        }
    
    def _get_strategy_recommendation(self, results: Dict, best_strategy: str) -> Dict:
        """Gera recomendação de estratégia"""
        best_performance = results[best_strategy]
        
        if best_performance['total_roi'] > 0.2:
            return {
                'recommendation': best_strategy.upper(),
                'confidence': 'HIGH',
                'reasoning': 'Excelente performance histórica'
            }
        elif best_performance['total_roi'] > 0.1:
            return {
                'recommendation': best_strategy.upper(),
                'confidence': 'MEDIUM',
                'reasoning': 'Boa performance histórica'
            }
        else:
            return {
                'recommendation': 'CONSERVATIVE',
                'confidence': 'LOW',
                'reasoning': 'Performance baixa em todas as estratégias'
            }

if __name__ == "__main__":
    # Teste do gerenciador de unidades
    print("=== TESTE DO GERENCIADOR DE UNIDADES ===")
    
    manager = UnitManager()
    
    # Testa cálculo de unidades
    print("\nTeste de Cálculo de Unidades:")
    test_cases = [
        {'confidence': 0.90, 'expected_value': 0.15, 'description': 'Alta confiança, alto EV'},
        {'confidence': 0.80, 'expected_value': 0.10, 'description': 'Confiança média-alta, bom EV'},
        {'confidence': 0.72, 'expected_value': 0.08, 'description': 'Confiança média, EV moderado'},
        {'confidence': 0.65, 'expected_value': 0.05, 'description': 'Baixa confiança, baixo EV'},
    ]
    
    for case in test_cases:
        recommendation = manager.calculate_recommended_units(
            case['confidence'], 
            case['expected_value']
        )
        
        print(f"\n  {case['description']}:")
        print(f"    Confiança: {recommendation.confidence_percentage:.1%}")
        print(f"    Nível: {recommendation.confidence_level.value}")
        print(f"    Unidades: {recommendation.recommended_units:.1f}")
        print(f"    Valor da unidade: R$ {recommendation.unit_value:.2f}")
        print(f"    Stake total: R$ {recommendation.total_stake:.2f}")
        print(f"    Fatores: {recommendation.adjustment_factors}")
        print(f"    Motivos: {', '.join(recommendation.reasoning)}")
    
    # Testa execução de apostas
    print(f"\nTeste de Execução de Apostas:")
    
    bets = [
        {'confidence': 0.88, 'expected_value': 0.12, 'outcome': 'home_win', 'result': 'home_win', 'odds': 2.20},
        {'confidence': 0.78, 'expected_value': 0.08, 'outcome': 'draw', 'result': 'away_win', 'odds': 3.50},
        {'confidence': 0.71, 'expected_value': 0.06, 'outcome': 'away_win', 'result': 'away_win', 'odds': 4.00},
    ]
    
    for i, bet in enumerate(bets, 1):
        recommendation = manager.calculate_recommended_units(
            bet['confidence'], 
            bet['expected_value']
        )
        result = manager.execute_unit_bet(
            recommendation, 
            bet['outcome'], 
            bet['result'], 
            bet['odds']
        )
        
        print(f"\n  Aposta {i}:")
        print(f"    Unidades: {recommendation.recommended_units:.1f}")
        print(f"    Stake: R$ {recommendation.total_stake:.2f}")
        print(f"    Resultado: {result['result']}")
        print(f"    Lucro: R$ {result['profit']:.2f}")
        print(f"    Lucro em unidades: {result['profit_units']:.1f}")
        print(f"    Capital: R$ {result['new_capital']:.2f}")
    
    # Analytics
    print(f"\nAnalytics do Sistema de Unidades:")
    analytics = manager.get_unit_analytics()
    print(f"  Total de apostas: {analytics['total_bets']}")
    print(f"  Taxa de acerto: {analytics['win_rate']:.1%}")
    print(f"  Unidades apostadas: {analytics['total_units_staked']:.1f}")
    print(f"  Lucro em unidades: {analytics['total_units_profit']:.1f}")
    print(f"  Unidades médias por aposta: {analytics['average_units_per_bet']:.1f}")
    print(f"  Capital atual: R$ {analytics['current_bankroll']:.2f}")
    print(f"  Valor da unidade: R$ {analytics['unit_value']:.2f}")
    
    print(f"\nPerformance por Nível de Confiança:")
    performance = manager.get_unit_performance_by_level()
    for level, perf in performance.items():
        if perf.total_bets > 0:
            print(f"  {level}:")
            print(f"    Apostas: {perf.total_bets}")
            print(f"    Taxa de acerto: {perf.win_rate:.1%}")
            print(f"    ROI: {perf.roi:.1f}%")
            print(f"    Unidades médias: {perf.average_units_per_bet:.1f}")
    
    print("\nTeste concluído!")
