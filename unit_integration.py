"""
Integração do Sistema de Gestão de Unidades - MaraBet AI
Conecta o gerenciador de unidades com o framework completo
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import json

from unit_management import (
    UnitManager, UnitConfig, ConfidenceLevel, 
    UnitRecommendation, UnitPerformance
)
from bankroll_integration import AdvancedBankrollSystem
from value_integration import AdvancedValueSystem
from probability_integration import AdvancedProbabilitySystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedUnitSystem:
    """
    Sistema Avançado de Gestão de Unidades
    Integra gestão de unidades com todo o framework
    """
    
    def __init__(self, unit_config: Optional[UnitConfig] = None):
        self.bankroll_system = AdvancedBankrollSystem()
        self.value_system = AdvancedValueSystem()
        self.probability_system = AdvancedProbabilitySystem()
        self.unit_manager = UnitManager(unit_config)
        self.unit_history = []
        self.performance_metrics = {}
        
    def analyze_bet_with_units(self, home_team: str, away_team: str, 
                             match_date: str) -> Dict:
        """
        Analisa oportunidade de aposta com gestão de unidades
        """
        logger.info(f"Analisando aposta com unidades: {home_team} vs {away_team}")
        
        try:
            # Análise de valor da partida
            value_analysis = self.value_system.analyze_match_value(
                home_team, away_team, match_date
            )
            
            if not value_analysis:
                return None
            
            # Análise de probabilidades
            prob_analysis = self.probability_system.calculate_match_probabilities(
                home_team, away_team, match_date
            )
            
            if not prob_analysis:
                return None
            
            # Encontra melhor oportunidade de valor
            best_opportunity = value_analysis['value_analysis']['best_opportunity']
            
            if not best_opportunity or best_opportunity['expected_value'] <= 0:
                return {
                    'recommendation': 'NO_VALUE',
                    'reason': 'Nenhuma oportunidade de valor identificada',
                    'value_analysis': value_analysis,
                    'probability_analysis': prob_analysis
                }
            
            # Calcula confiança combinada
            combined_confidence = self._calculate_combined_confidence(
                value_analysis, prob_analysis
            )
            
            # Calcula performance recente
            recent_performance = self._calculate_recent_performance()
            
            # Calcula sequência atual
            current_streak = self._calculate_current_streak()
            
            # Calcula unidades recomendadas
            unit_recommendation = self.unit_manager.calculate_recommended_units(
                confidence=combined_confidence,
                expected_value=best_opportunity['expected_value'],
                bankroll_percentage=self._calculate_bankroll_percentage(),
                recent_performance=recent_performance,
                current_streak=current_streak
            )
            
            # Análise de viabilidade da aposta
            feasibility = self._analyze_unit_feasibility(
                unit_recommendation, best_opportunity, value_analysis
            )
            
            # Recomendação final
            final_recommendation = self._determine_unit_recommendation(
                unit_recommendation, feasibility, value_analysis
            )
            
            # Análise de risco por unidades
            risk_analysis = self._analyze_unit_risk(unit_recommendation, value_analysis)
            
            result = {
                'match_info': {
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': match_date
                },
                'value_analysis': value_analysis,
                'probability_analysis': prob_analysis,
                'unit_recommendation': {
                    'confidence_level': unit_recommendation.confidence_level.value,
                    'confidence_percentage': unit_recommendation.confidence_percentage,
                    'recommended_units': unit_recommendation.recommended_units,
                    'unit_value': unit_recommendation.unit_value,
                    'total_stake': unit_recommendation.total_stake,
                    'adjustment_factors': unit_recommendation.adjustment_factors,
                    'reasoning': unit_recommendation.reasoning
                },
                'feasibility': feasibility,
                'risk_analysis': risk_analysis,
                'final_recommendation': final_recommendation,
                'combined_confidence': combined_confidence,
                'recent_performance': recent_performance,
                'current_streak': current_streak
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise de aposta com unidades: {e}")
            return None
    
    def execute_bet_with_units(self, home_team: str, away_team: str, 
                             match_date: str, bet_outcome: str,
                             actual_result: str, odds: float) -> Dict:
        """
        Executa aposta usando sistema de unidades
        """
        logger.info(f"Executando aposta com unidades: {home_team} vs {away_team}")
        
        try:
            # Analisa oportunidade com unidades
            opportunity = self.analyze_bet_with_units(
                home_team, away_team, match_date
            )
            
            if not opportunity or opportunity['final_recommendation']['action'] == 'AVOID':
                return {
                    'success': False,
                    'reason': 'Aposta não recomendada',
                    'opportunity': opportunity
                }
            
            # Executa aposta com unidades
            unit_rec = opportunity['unit_recommendation']
            unit_recommendation = UnitRecommendation(
                confidence_level=ConfidenceLevel(unit_rec['confidence_level']),
                confidence_percentage=unit_rec['confidence_percentage'],
                recommended_units=unit_rec['recommended_units'],
                unit_value=unit_rec['unit_value'],
                total_stake=unit_rec['total_stake'],
                adjustment_factors=unit_rec['adjustment_factors'],
                reasoning=unit_rec['reasoning'],
                timestamp=datetime.now()
            )
            
            bet_result = self.unit_manager.execute_unit_bet(
                unit_recommendation, bet_outcome, actual_result, odds
            )
            
            if not bet_result['success']:
                return {
                    'success': False,
                    'reason': 'Erro na execução da aposta',
                    'error': bet_result['error']
                }
            
            # Atualiza histórico
            self.unit_history.append({
                'timestamp': datetime.now(),
                'match': f"{home_team} vs {away_team}",
                'bet_outcome': bet_outcome,
                'actual_result': actual_result,
                'unit_recommendation': unit_recommendation,
                'bet_result': bet_result,
                'odds': odds
            })
            
            # Atualiza métricas
            self._update_performance_metrics()
            
            return {
                'success': True,
                'bet_result': bet_result,
                'unit_recommendation': unit_recommendation,
                'opportunity': opportunity
            }
            
        except Exception as e:
            logger.error(f"Erro na execução da aposta com unidades: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_unit_backtesting(self, historical_matches: List[Dict], 
                           initial_capital: float = 1000) -> Dict:
        """
        Executa backtesting com gestão de unidades
        """
        logger.info("Executando backtesting com gestão de unidades")
        
        try:
            # Reseta sistema de unidades
            self.unit_manager = UnitManager()
            self.unit_manager.current_bankroll = initial_capital
            
            portfolio = []
            total_opportunities = 0
            executed_bets = 0
            
            for match in historical_matches[:50]:  # Limita para performance
                try:
                    # Analisa oportunidade com unidades
                    opportunity = self.analyze_bet_with_units(
                        match['home_team'],
                        match['away_team'],
                        match['date']
                    )
                    
                    if not opportunity:
                        continue
                    
                    total_opportunities += 1
                    
                    # Verifica se deve executar a aposta
                    if opportunity['final_recommendation']['action'] in ['BET', 'STRONG_BET']:
                        # Simula resultado
                        actual_result = self._simulate_match_result(match)
                        
                        # Executa aposta com unidades
                        bet_result = self.execute_bet_with_units(
                            match['home_team'],
                            match['away_team'],
                            match['date'],
                            opportunity['value_analysis']['best_opportunity']['outcome'],
                            actual_result,
                            match.get('home_odds', 2.0)
                        )
                        
                        if bet_result['success']:
                            executed_bets += 1
                            portfolio.append({
                                'match_id': match.get('id', f'match_{len(portfolio)}'),
                                'date': match['date'],
                                'home_team': match['home_team'],
                                'away_team': match['away_team'],
                                'bet_outcome': opportunity['value_analysis']['best_opportunity']['outcome'],
                                'unit_recommendation': bet_result['unit_recommendation'],
                                'bet_result': bet_result['bet_result']
                            })
                    
                except Exception as e:
                    logger.error(f"Erro ao processar partida no backtesting: {e}")
                    continue
            
            # Calcula métricas finais
            unit_analytics = self.unit_manager.get_unit_analytics()
            performance_by_level = self.unit_manager.get_unit_performance_by_level()
            
            # Análise de performance
            performance_analysis = self._analyze_unit_backtesting_performance(portfolio)
            
            return {
                'success': True,
                'portfolio': portfolio,
                'unit_analytics': unit_analytics,
                'performance_by_level': performance_by_level,
                'performance_analysis': performance_analysis,
                'summary': {
                    'total_opportunities': total_opportunities,
                    'executed_bets': executed_bets,
                    'execution_rate': executed_bets / total_opportunities if total_opportunities > 0 else 0,
                    'initial_capital': initial_capital,
                    'final_capital': unit_analytics['current_bankroll'],
                    'total_profit': unit_analytics['current_bankroll'] - initial_capital,
                    'profit_percentage': (unit_analytics['current_bankroll'] - initial_capital) / initial_capital * 100,
                    'total_units_staked': unit_analytics['total_units_staked'],
                    'total_units_profit': unit_analytics['total_units_profit'],
                    'average_units_per_bet': unit_analytics['average_units_per_bet']
                }
            }
            
        except Exception as e:
            logger.error(f"Erro no backtesting de unidades: {e}")
            return {'success': False, 'error': str(e)}
    
    def optimize_unit_strategy(self, historical_matches: List[Dict], 
                             initial_capital: float = 1000) -> Dict:
        """
        Otimiza estratégia de unidades baseado em dados históricos
        """
        logger.info("Otimizando estratégia de unidades")
        
        try:
            # Testa diferentes configurações de unidades
            test_configs = {
                'conservative': UnitConfig(
                    high_confidence_units=(1.5, 2.5),
                    medium_high_confidence_units=(1.0, 1.8),
                    medium_confidence_units=(0.8, 1.3),
                    low_confidence_units=(0.3, 0.8)
                ),
                'moderate': UnitConfig(
                    high_confidence_units=(2.0, 3.0),
                    medium_high_confidence_units=(1.5, 2.0),
                    medium_confidence_units=(1.0, 1.5),
                    low_confidence_units=(0.5, 1.0)
                ),
                'aggressive': UnitConfig(
                    high_confidence_units=(2.5, 3.5),
                    medium_high_confidence_units=(1.8, 2.5),
                    medium_confidence_units=(1.3, 1.8),
                    low_confidence_units=(0.8, 1.3)
                )
            }
            
            results = {}
            
            for strategy_name, config in test_configs.items():
                # Executa backtesting com esta configuração
                self.unit_manager = UnitManager(config)
                self.unit_manager.current_bankroll = initial_capital
                
                backtest_result = self.run_unit_backtesting(historical_matches, initial_capital)
                
                if backtest_result['success']:
                    summary = backtest_result['summary']
                    results[strategy_name] = {
                        'profit_percentage': summary['profit_percentage'],
                        'total_units_staked': summary['total_units_staked'],
                        'total_units_profit': summary['total_units_profit'],
                        'average_units_per_bet': summary['average_units_per_bet'],
                        'execution_rate': summary['execution_rate'],
                        'final_capital': summary['final_capital']
                    }
            
            # Encontra melhor estratégia
            best_strategy = max(results.keys(), 
                              key=lambda k: results[k]['profit_percentage'])
            
            return {
                'success': True,
                'results': results,
                'best_strategy': best_strategy,
                'best_performance': results[best_strategy],
                'recommendation': self._get_unit_strategy_recommendation(results, best_strategy)
            }
            
        except Exception as e:
            logger.error(f"Erro na otimização de estratégia de unidades: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_unit_analytics(self) -> Dict:
        """
        Retorna analytics completos do sistema de unidades
        """
        unit_analytics = self.unit_manager.get_unit_analytics()
        performance_by_level = self.unit_manager.get_unit_performance_by_level()
        
        # Análise de tendências
        trends = self._analyze_unit_trends()
        
        # Recomendações estratégicas
        strategic_recommendations = self._generate_unit_recommendations(
            unit_analytics, performance_by_level
        )
        
        return {
            'unit_analytics': unit_analytics,
            'performance_by_level': performance_by_level,
            'trends': trends,
            'strategic_recommendations': strategic_recommendations,
            'performance_metrics': self.performance_metrics
        }
    
    def _calculate_combined_confidence(self, value_analysis: Dict, 
                                     prob_analysis: Dict) -> float:
        """Calcula confiança combinada de valor e probabilidades"""
        value_confidence = value_analysis['confidence']
        prob_confidence = prob_analysis['confidence']
        
        # Combina confianças com pesos
        combined = (value_confidence * 0.6 + prob_confidence * 0.4)
        
        return min(max(combined, 0.0), 1.0)
    
    def _calculate_recent_performance(self) -> float:
        """Calcula performance recente"""
        if not self.unit_history:
            return 0.0
        
        # Últimas 10 apostas
        recent_bets = self.unit_history[-10:]
        if not recent_bets:
            return 0.0
        
        total_profit = sum([bet['bet_result']['profit'] for bet in recent_bets])
        total_staked = sum([bet['unit_recommendation'].total_stake for bet in recent_bets])
        
        return (total_profit / total_staked) if total_staked > 0 else 0.0
    
    def _calculate_current_streak(self) -> int:
        """Calcula sequência atual de vitórias/derrotas"""
        if not self.unit_history:
            return 0
        
        # Últimas apostas
        recent_results = [bet['bet_result']['is_winner'] for bet in self.unit_history[-10:]]
        if not recent_results:
            return 0
        
        # Calcula sequência atual
        current_streak = 0
        last_result = recent_results[-1]
        
        for result in reversed(recent_results):
            if result == last_result:
                current_streak += 1
            else:
                break
        
        return current_streak if last_result else -current_streak
    
    def _calculate_bankroll_percentage(self) -> float:
        """Calcula percentual de crescimento do capital"""
        if not self.unit_history:
            return 0.0
        
        initial_capital = 1000.0  # Assumindo capital inicial
        current_capital = self.unit_manager.current_bankroll
        
        return (current_capital - initial_capital) / initial_capital
    
    def _analyze_unit_feasibility(self, unit_recommendation: UnitRecommendation,
                                 best_opportunity: Dict, value_analysis: Dict) -> Dict:
        """Analisa viabilidade da aposta com unidades"""
        feasibility = {
            'is_feasible': True,
            'reasons': [],
            'warnings': [],
            'score': 100
        }
        
        # Verifica se há capital suficiente
        if unit_recommendation.total_stake > self.unit_manager.current_bankroll * 0.1:
            feasibility['warnings'].append('Aposta com alta concentração de capital')
            feasibility['score'] -= 20
        
        # Verifica nível de confiança
        if unit_recommendation.confidence_percentage < 0.70:
            feasibility['warnings'].append('Baixa confiança para unidades recomendadas')
            feasibility['score'] -= 15
        
        # Verifica unidades recomendadas
        if unit_recommendation.recommended_units > 3.0:
            feasibility['warnings'].append('Muitas unidades recomendadas')
            feasibility['score'] -= 10
        
        # Verifica EV
        if best_opportunity['expected_value'] < 0.05:
            feasibility['warnings'].append('Valor esperado baixo')
            feasibility['score'] -= 15
        
        feasibility['score'] = max(0, feasibility['score'])
        
        return feasibility
    
    def _determine_unit_recommendation(self, unit_recommendation: UnitRecommendation,
                                     feasibility: Dict, value_analysis: Dict) -> Dict:
        """Determina recomendação final da aposta com unidades"""
        if not feasibility['is_feasible']:
            return {
                'action': 'AVOID',
                'reason': 'Aposta não viável',
                'details': feasibility['reasons']
            }
        
        if unit_recommendation.recommended_units <= 0:
            return {
                'action': 'AVOID',
                'reason': 'Nenhuma unidade recomendada',
                'details': ['Confiança insuficiente ou fatores de risco']
            }
        
        if feasibility['score'] >= 80:
            return {
                'action': 'STRONG_BET',
                'reason': 'Excelente oportunidade com unidades adequadas',
                'details': ['Alta confiança', 'Bom valor esperado', 'Unidades apropriadas']
            }
        elif feasibility['score'] >= 60:
            return {
                'action': 'BET',
                'reason': 'Boa oportunidade com unidades moderadas',
                'details': ['Confiança adequada', 'Valor esperado positivo']
            }
        elif feasibility['score'] >= 40:
            return {
                'action': 'CONSIDER',
                'reason': 'Oportunidade questionável',
                'details': feasibility['warnings']
            }
        else:
            return {
                'action': 'AVOID',
                'reason': 'Risco muito alto',
                'details': feasibility['warnings']
            }
    
    def _analyze_unit_risk(self, unit_recommendation: UnitRecommendation,
                          value_analysis: Dict) -> Dict:
        """Analisa riscos específicos da gestão de unidades"""
        risks = []
        risk_score = 0
        
        # Risco de concentração de unidades
        if unit_recommendation.recommended_units > 2.5:
            risks.append({
                'type': 'HIGH_UNIT_CONCENTRATION',
                'level': 'MEDIUM',
                'message': f'Alto número de unidades: {unit_recommendation.recommended_units:.1f}'
            })
            risk_score += 2
        
        # Risco de confiança
        if unit_recommendation.confidence_percentage < 0.75:
            risks.append({
                'type': 'LOW_CONFIDENCE',
                'level': 'MEDIUM',
                'message': f'Confiança baixa: {unit_recommendation.confidence_percentage:.1%}'
            })
            risk_score += 2
        
        # Risco de capital
        capital_risk = (unit_recommendation.total_stake / self.unit_manager.current_bankroll) * 100
        if capital_risk > 5:
            risks.append({
                'type': 'HIGH_CAPITAL_RISK',
                'level': 'HIGH',
                'message': f'Alto risco de capital: {capital_risk:.1f}%'
            })
            risk_score += 3
        
        # Classifica nível de risco
        if risk_score >= 5:
            risk_level = 'HIGH'
        elif risk_score >= 3:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risks': risks,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'capital_risk_percentage': capital_risk
        }
    
    def _simulate_match_result(self, match: Dict) -> str:
        """Simula resultado de uma partida"""
        import random
        
        # Simula resultado baseado nas odds
        home_odds = match.get('home_odds', 2.0)
        draw_odds = match.get('draw_odds', 3.0)
        away_odds = match.get('away_odds', 2.5)
        
        # Calcula probabilidades implícitas
        home_prob = 1 / home_odds
        draw_prob = 1 / draw_odds
        away_prob = 1 / away_odds
        
        # Normaliza probabilidades
        total_prob = home_prob + draw_prob + away_prob
        home_prob /= total_prob
        draw_prob /= total_prob
        away_prob /= total_prob
        
        # Simula resultado
        rand = random.random()
        
        if rand < home_prob:
            return 'home_win'
        elif rand < home_prob + draw_prob:
            return 'draw'
        else:
            return 'away_win'
    
    def _update_performance_metrics(self):
        """Atualiza métricas de performance"""
        unit_analytics = self.unit_manager.get_unit_analytics()
        
        self.performance_metrics = {
            'total_bets': unit_analytics['total_bets'],
            'win_rate': unit_analytics['win_rate'],
            'total_units_staked': unit_analytics['total_units_staked'],
            'total_units_profit': unit_analytics['total_units_profit'],
            'average_units_per_bet': unit_analytics['average_units_per_bet'],
            'current_bankroll': unit_analytics['current_bankroll'],
            'last_updated': datetime.now().isoformat()
        }
    
    def _analyze_unit_backtesting_performance(self, portfolio: List[Dict]) -> Dict:
        """Analisa performance do backtesting de unidades"""
        if not portfolio:
            return {}
        
        # Análise de retorno por unidades
        total_units_staked = sum([bet['unit_recommendation'].recommended_units for bet in portfolio])
        total_units_profit = sum([bet['bet_result']['profit_units'] for bet in portfolio])
        unit_roi = (total_units_profit / total_units_staked * 100) if total_units_staked > 0 else 0
        
        # Análise por nível de confiança
        confidence_performance = {}
        for bet in portfolio:
            level = bet['unit_recommendation'].confidence_level.value
            if level not in confidence_performance:
                confidence_performance[level] = {'units': 0, 'profit': 0, 'bets': 0}
            
            confidence_performance[level]['units'] += bet['unit_recommendation'].recommended_units
            confidence_performance[level]['profit'] += bet['bet_result']['profit_units']
            confidence_performance[level]['bets'] += 1
        
        # Calcula ROI por nível
        for level in confidence_performance:
            data = confidence_performance[level]
            data['roi'] = (data['profit'] / data['units'] * 100) if data['units'] > 0 else 0
            data['avg_units'] = data['units'] / data['bets'] if data['bets'] > 0 else 0
        
        return {
            'total_units_staked': total_units_staked,
            'total_units_profit': total_units_profit,
            'unit_roi': unit_roi,
            'confidence_performance': confidence_performance,
            'best_performing_level': max(confidence_performance.keys(), 
                                       key=lambda k: confidence_performance[k]['roi']) if confidence_performance else None
        }
    
    def _analyze_unit_trends(self) -> Dict:
        """Analisa tendências do sistema de unidades"""
        if not self.unit_history:
            return {}
        
        # Análise de tendência de unidades
        recent_bets = self.unit_history[-10:] if len(self.unit_history) >= 10 else self.unit_history
        
        if not recent_bets:
            return {}
        
        recent_units = np.mean([bet['unit_recommendation'].recommended_units for bet in recent_bets])
        overall_units = np.mean([bet['unit_recommendation'].recommended_units for bet in self.unit_history])
        
        unit_trend = 'INCREASING' if recent_units > overall_units else 'DECREASING'
        
        # Análise de performance recente
        recent_profit = sum([bet['bet_result']['profit'] for bet in recent_bets])
        overall_profit = sum([bet['bet_result']['profit'] for bet in self.unit_history])
        
        return {
            'unit_trend': unit_trend,
            'recent_units_avg': recent_units,
            'overall_units_avg': overall_units,
            'recent_profit': recent_profit,
            'overall_profit': overall_profit
        }
    
    def _generate_unit_recommendations(self, unit_analytics: Dict, 
                                     performance_by_level: Dict) -> List[Dict]:
        """Gera recomendações estratégicas para unidades"""
        recommendations = []
        
        # Recomendação baseada na performance geral
        if unit_analytics['win_rate'] < 0.4:
            recommendations.append({
                'type': 'LOW_WIN_RATE',
                'priority': 'HIGH',
                'message': f'Taxa de acerto baixa: {unit_analytics["win_rate"]:.1%}',
                'action': 'Reduzir unidades ou revisar critérios'
            })
        
        # Recomendação baseada no ROI de unidades
        if unit_analytics['total_units_staked'] > 0:
            unit_roi = (unit_analytics['total_units_profit'] / unit_analytics['total_units_staked']) * 100
            if unit_roi < 0:
                recommendations.append({
                    'type': 'NEGATIVE_UNIT_ROI',
                    'priority': 'HIGH',
                    'message': f'ROI negativo em unidades: {unit_roi:.1f}%',
                    'action': 'Pausar apostas e revisar estratégia'
                })
        
        # Recomendação baseada na performance por nível
        best_level = None
        best_roi = -float('inf')
        
        for level, perf in performance_by_level.items():
            if perf.total_bets > 0 and perf.roi > best_roi:
                best_roi = perf.roi
                best_level = level
        
        if best_level and best_roi > 10:
            recommendations.append({
                'type': 'BEST_PERFORMING_LEVEL',
                'priority': 'MEDIUM',
                'message': f'Melhor nível: {best_level} (ROI: {best_roi:.1f}%)',
                'action': 'Focar mais apostas neste nível de confiança'
            })
        
        return recommendations
    
    def _get_unit_strategy_recommendation(self, results: Dict, best_strategy: str) -> Dict:
        """Gera recomendação de estratégia de unidades"""
        best_performance = results[best_strategy]
        
        if best_performance['profit_percentage'] > 20:
            return {
                'recommendation': best_strategy.upper(),
                'confidence': 'HIGH',
                'reasoning': 'Excelente performance histórica com unidades'
            }
        elif best_performance['profit_percentage'] > 10:
            return {
                'recommendation': best_strategy.upper(),
                'confidence': 'MEDIUM',
                'reasoning': 'Boa performance histórica com unidades'
            }
        else:
            return {
                'recommendation': 'CONSERVATIVE',
                'confidence': 'LOW',
                'reasoning': 'Performance baixa em todas as estratégias de unidades'
            }

if __name__ == "__main__":
    # Teste do sistema de unidades
    system = AdvancedUnitSystem()
    
    print("=== TESTE DO SISTEMA DE GESTÃO DE UNIDADES ===")
    
    # Testa análise de aposta com unidades
    opportunity = system.analyze_bet_with_units('Flamengo', 'Palmeiras', '2024-01-15')
    
    if opportunity:
        print(f"\nAnálise de Aposta com Unidades:")
        print(f"  Partida: {opportunity['match_info']['home_team']} vs {opportunity['match_info']['away_team']}")
        
        unit_rec = opportunity['unit_recommendation']
        print(f"  Nível de confiança: {unit_rec['confidence_level']}")
        print(f"  Confiança: {unit_rec['confidence_percentage']:.1%}")
        print(f"  Unidades recomendadas: {unit_rec['recommended_units']:.1f}")
        print(f"  Valor da unidade: R$ {unit_rec['unit_value']:.2f}")
        print(f"  Stake total: R$ {unit_rec['total_stake']:.2f}")
        print(f"  Fatores de ajuste: {unit_rec['adjustment_factors']}")
        print(f"  Motivos: {', '.join(unit_rec['reasoning'])}")
        
        final_rec = opportunity['final_recommendation']
        print(f"  Recomendação final: {final_rec['action']}")
        print(f"  Motivo: {final_rec['reason']}")
        
        risk = opportunity['risk_analysis']
        print(f"  Nível de risco: {risk['risk_level']}")
        print(f"  Score de risco: {risk['risk_score']}")
    
    print("Teste concluído!")
