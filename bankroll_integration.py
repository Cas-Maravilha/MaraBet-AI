"""
Integração do Sistema de Gestão de Banca - MaraBet AI
Conecta o gerenciador de banca com o framework completo
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import json

from bankroll_management import (
    BankrollManager, BankrollConfig, RiskLevel, 
    BetSizing, BankrollStatus
)
from value_integration import AdvancedValueSystem
from probability_integration import AdvancedProbabilitySystem
from framework_integration import MaraBetFramework

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedBankrollSystem:
    """
    Sistema Avançado de Gestão de Banca
    Integra gestão de banca com todo o framework
    """
    
    def __init__(self, bankroll_config: Optional[BankrollConfig] = None):
        self.framework = MaraBetFramework()
        self.probability_system = AdvancedProbabilitySystem()
        self.value_system = AdvancedValueSystem()
        self.bankroll_manager = BankrollManager(bankroll_config)
        self.betting_history = []
        self.performance_metrics = {}
        
    def analyze_bet_opportunity(self, home_team: str, away_team: str, 
                              match_date: str, risk_level: Optional[RiskLevel] = None) -> Dict:
        """
        Analisa oportunidade de aposta com gestão de banca
        """
        logger.info(f"Analisando oportunidade: {home_team} vs {away_team}")
        
        try:
            # Análise de valor da partida
            value_analysis = self.value_system.analyze_match_value(
                home_team, away_team, match_date
            )
            
            if not value_analysis:
                return None
            
            # Encontra melhor oportunidade de valor
            best_opportunity = value_analysis['value_analysis']['best_opportunity']
            
            if not best_opportunity or best_opportunity['expected_value'] <= 0:
                return {
                    'recommendation': 'NO_VALUE',
                    'reason': 'Nenhuma oportunidade de valor identificada',
                    'value_analysis': value_analysis
                }
            
            # Calcula sizing usando Kelly Fracionado
            bet_sizing = self.bankroll_manager.calculate_kelly_fractional(
                best_opportunity['probability'],
                best_opportunity['market_odds'],
                risk_level
            )
            
            # Verifica limites de risco
            risk_check = self.bankroll_manager.check_risk_limits()
            
            # Análise de viabilidade da aposta
            feasibility = self._analyze_bet_feasibility(
                bet_sizing, best_opportunity, risk_check
            )
            
            # Recomendação final
            final_recommendation = self._determine_final_recommendation(
                bet_sizing, feasibility, risk_check
            )
            
            # Análise de portfólio
            portfolio_impact = self._analyze_portfolio_impact(bet_sizing)
            
            result = {
                'match_info': {
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': match_date
                },
                'value_analysis': value_analysis,
                'bet_sizing': {
                    'stake_percentage': bet_sizing.stake_percentage,
                    'stake_amount': bet_sizing.stake_amount,
                    'kelly_fraction': bet_sizing.kelly_fraction,
                    'risk_level': bet_sizing.risk_level.value,
                    'probability': bet_sizing.probability,
                    'odds': bet_sizing.odds,
                    'expected_value': bet_sizing.expected_value,
                    'recommendation': bet_sizing.recommendation,
                    'risk_factors': bet_sizing.risk_factors
                },
                'feasibility': feasibility,
                'risk_check': risk_check,
                'portfolio_impact': portfolio_impact,
                'final_recommendation': final_recommendation,
                'bankroll_status': self.bankroll_manager.get_bankroll_status()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise de oportunidade: {e}")
            return None
    
    def execute_bet_with_management(self, home_team: str, away_team: str, 
                                  match_date: str, bet_outcome: str,
                                  actual_result: str, risk_level: Optional[RiskLevel] = None) -> Dict:
        """
        Executa aposta com gestão completa de banca
        """
        logger.info(f"Executando aposta com gestão: {home_team} vs {away_team}")
        
        try:
            # Analisa oportunidade
            opportunity = self.analyze_bet_opportunity(
                home_team, away_team, match_date, risk_level
            )
            
            if not opportunity or opportunity['final_recommendation']['action'] == 'AVOID':
                return {
                    'success': False,
                    'reason': 'Aposta não recomendada',
                    'opportunity': opportunity
                }
            
            # Executa aposta
            bet_sizing = opportunity['bet_sizing']
            bet_result = self.bankroll_manager.execute_bet(
                BetSizing(
                    stake_percentage=bet_sizing['stake_percentage'],
                    stake_amount=bet_sizing['stake_amount'],
                    kelly_fraction=bet_sizing['kelly_fraction'],
                    risk_level=RiskLevel(bet_sizing['risk_level']),
                    probability=bet_sizing['probability'],
                    odds=bet_sizing['odds'],
                    expected_value=bet_sizing['expected_value'],
                    recommendation=bet_sizing['recommendation'],
                    risk_factors=bet_sizing['risk_factors'],
                    timestamp=datetime.now()
                ),
                actual_result,
                bet_outcome
            )
            
            if not bet_result['success']:
                return {
                    'success': False,
                    'reason': 'Erro na execução da aposta',
                    'error': bet_result['error']
                }
            
            # Atualiza histórico
            self.betting_history.append({
                'timestamp': datetime.now(),
                'match': f"{home_team} vs {away_team}",
                'bet_outcome': bet_outcome,
                'actual_result': actual_result,
                'bet_sizing': bet_sizing,
                'bet_result': bet_result,
                'bankroll_status': self.bankroll_manager.get_bankroll_status()
            })
            
            # Atualiza métricas de performance
            self._update_performance_metrics()
            
            return {
                'success': True,
                'bet_result': bet_result,
                'bankroll_status': self.bankroll_manager.get_bankroll_status(),
                'opportunity': opportunity
            }
            
        except Exception as e:
            logger.error(f"Erro na execução da aposta: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_bankroll_backtesting(self, historical_matches: List[Dict], 
                               initial_capital: float = 1000,
                               risk_level: RiskLevel = RiskLevel.CONSERVATIVE) -> Dict:
        """
        Executa backtesting com gestão completa de banca
        """
        logger.info("Executando backtesting com gestão de banca")
        
        try:
            # Reseta banca
            self.bankroll_manager.reset_bankroll(initial_capital)
            
            # Ajusta nível de risco
            self.bankroll_manager.adjust_risk_level(risk_level)
            
            portfolio = []
            total_opportunities = 0
            executed_bets = 0
            
            for match in historical_matches[:50]:  # Limita para performance
                try:
                    # Analisa oportunidade
                    opportunity = self.analyze_bet_opportunity(
                        match['home_team'],
                        match['away_team'],
                        match['date'],
                        risk_level
                    )
                    
                    if not opportunity:
                        continue
                    
                    total_opportunities += 1
                    
                    # Verifica se deve executar a aposta
                    if opportunity['final_recommendation']['action'] in ['BET', 'STRONG_BET']:
                        # Simula resultado
                        actual_result = self._simulate_match_result(match)
                        
                        # Executa aposta
                        bet_result = self.execute_bet_with_management(
                            match['home_team'],
                            match['away_team'],
                            match['date'],
                            opportunity['value_analysis']['best_opportunity']['outcome'],
                            actual_result,
                            risk_level
                        )
                        
                        if bet_result['success']:
                            executed_bets += 1
                            portfolio.append({
                                'match_id': match.get('id', f'match_{len(portfolio)}'),
                                'date': match['date'],
                                'home_team': match['home_team'],
                                'away_team': match['away_team'],
                                'bet_outcome': opportunity['value_analysis']['best_opportunity']['outcome'],
                                'bet_sizing': bet_result['bet_result']['bet_record'],
                                'bankroll_status': bet_result['bankroll_status']
                            })
                    
                except Exception as e:
                    logger.error(f"Erro ao processar partida no backtesting: {e}")
                    continue
            
            # Calcula métricas finais
            final_status = self.bankroll_manager.get_bankroll_status()
            betting_stats = self.bankroll_manager.get_betting_statistics()
            
            # Análise de performance
            performance_analysis = self._analyze_backtesting_performance(portfolio)
            
            return {
                'success': True,
                'portfolio': portfolio,
                'final_bankroll_status': final_status,
                'betting_statistics': betting_stats,
                'performance_analysis': performance_analysis,
                'summary': {
                    'total_opportunities': total_opportunities,
                    'executed_bets': executed_bets,
                    'execution_rate': executed_bets / total_opportunities if total_opportunities > 0 else 0,
                    'initial_capital': initial_capital,
                    'final_capital': final_status.current_capital,
                    'total_profit': final_status.total_profit,
                    'profit_percentage': final_status.profit_percentage,
                    'max_drawdown': final_status.max_drawdown_percentage
                }
            }
            
        except Exception as e:
            logger.error(f"Erro no backtesting de gestão de banca: {e}")
            return {'success': False, 'error': str(e)}
    
    def optimize_risk_level(self, historical_matches: List[Dict], 
                          initial_capital: float = 1000) -> Dict:
        """
        Otimiza nível de risco baseado em dados históricos
        """
        logger.info("Otimizando nível de risco")
        
        try:
            risk_levels = [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, 
                          RiskLevel.AGGRESSIVE, RiskLevel.MAXIMUM]
            
            results = {}
            
            for risk_level in risk_levels:
                # Executa backtesting para cada nível de risco
                backtest_result = self.run_bankroll_backtesting(
                    historical_matches, initial_capital, risk_level
                )
                
                if backtest_result['success']:
                    summary = backtest_result['summary']
                    results[risk_level.value] = {
                        'profit_percentage': summary['profit_percentage'],
                        'max_drawdown': summary['max_drawdown'],
                        'execution_rate': summary['execution_rate'],
                        'final_capital': summary['final_capital'],
                        'risk_return_ratio': summary['profit_percentage'] / max(summary['max_drawdown'], 1)
                    }
            
            # Encontra melhor nível de risco
            best_risk_level = None
            best_score = -float('inf')
            
            for risk_level, metrics in results.items():
                # Score baseado em retorno ajustado por risco
                score = metrics['risk_return_ratio']
                if score > best_score:
                    best_score = score
                    best_risk_level = risk_level
            
            return {
                'success': True,
                'results': results,
                'best_risk_level': best_risk_level,
                'best_score': best_score,
                'recommendation': self._get_risk_recommendation(results, best_risk_level)
            }
            
        except Exception as e:
            logger.error(f"Erro na otimização de risco: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_bankroll_analytics(self) -> Dict:
        """
        Retorna analytics completos da gestão de banca
        """
        bankroll_status = self.bankroll_manager.get_bankroll_status()
        betting_stats = self.bankroll_manager.get_betting_statistics()
        risk_check = self.bankroll_manager.check_risk_limits()
        
        # Análise de tendências
        trends = self._analyze_bankroll_trends()
        
        # Análise de performance por período
        performance_by_period = self._analyze_performance_by_period()
        
        # Recomendações estratégicas
        strategic_recommendations = self._generate_strategic_recommendations(
            bankroll_status, betting_stats, risk_check
        )
        
        return {
            'bankroll_status': {
                'current_capital': bankroll_status.current_capital,
                'initial_capital': bankroll_status.initial_capital,
                'total_profit': bankroll_status.total_profit,
                'profit_percentage': bankroll_status.profit_percentage,
                'drawdown_percentage': bankroll_status.drawdown_percentage,
                'max_drawdown_percentage': bankroll_status.max_drawdown_percentage,
                'status': bankroll_status.status,
                'risk_level': bankroll_status.risk_level.value
            },
            'betting_statistics': betting_stats,
            'risk_alerts': risk_check,
            'trends': trends,
            'performance_by_period': performance_by_period,
            'strategic_recommendations': strategic_recommendations,
            'performance_metrics': self.performance_metrics
        }
    
    def _analyze_bet_feasibility(self, bet_sizing: BetSizing, 
                                best_opportunity: Dict, risk_check: Dict) -> Dict:
        """Analisa viabilidade da aposta"""
        feasibility = {
            'is_feasible': True,
            'reasons': [],
            'warnings': [],
            'score': 100
        }
        
        # Verifica se há alertas críticos
        if risk_check['critical_alerts'] > 0:
            feasibility['is_feasible'] = False
            feasibility['reasons'].append('Alertas críticos de risco ativos')
            feasibility['score'] -= 50
        
        # Verifica tamanho da aposta
        if bet_sizing.stake_percentage > 0.05:
            feasibility['warnings'].append('Aposta com alta concentração de risco')
            feasibility['score'] -= 20
        
        # Verifica EV
        if bet_sizing.expected_value < 0.05:
            feasibility['warnings'].append('Valor esperado baixo')
            feasibility['score'] -= 15
        
        # Verifica probabilidade
        if bet_sizing.probability < 0.3 or bet_sizing.probability > 0.7:
            feasibility['warnings'].append('Probabilidade extrema')
            feasibility['score'] -= 10
        
        # Verifica odds
        if bet_sizing.odds < 1.5 or bet_sizing.odds > 5.0:
            feasibility['warnings'].append('Odds extremas')
            feasibility['score'] -= 10
        
        feasibility['score'] = max(0, feasibility['score'])
        
        return feasibility
    
    def _determine_final_recommendation(self, bet_sizing: BetSizing, 
                                      feasibility: Dict, risk_check: Dict) -> Dict:
        """Determina recomendação final da aposta"""
        if not feasibility['is_feasible']:
            return {
                'action': 'AVOID',
                'reason': 'Aposta não viável',
                'details': feasibility['reasons']
            }
        
        if bet_sizing.stake_percentage <= 0:
            return {
                'action': 'AVOID',
                'reason': 'Kelly Fracionado indica não apostar',
                'details': ['EV insuficiente ou probabilidade muito baixa']
            }
        
        if feasibility['score'] >= 80:
            return {
                'action': 'STRONG_BET',
                'reason': 'Excelente oportunidade',
                'details': ['Alto valor esperado', 'Baixo risco', 'Boa viabilidade']
            }
        elif feasibility['score'] >= 60:
            return {
                'action': 'BET',
                'reason': 'Boa oportunidade',
                'details': ['Valor esperado positivo', 'Risco controlado']
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
    
    def _analyze_portfolio_impact(self, bet_sizing: BetSizing) -> Dict:
        """Analisa impacto da aposta no portfólio"""
        current_status = self.bankroll_manager.get_bankroll_status()
        
        # Calcula impacto percentual
        impact_percentage = bet_sizing.stake_percentage
        
        # Calcula novo capital após aposta (assumindo perda)
        new_capital_if_loss = current_status.current_capital - bet_sizing.stake_amount
        new_capital_percentage = (new_capital_if_loss / current_status.initial_capital) * 100
        
        # Calcula novo capital após aposta (assumindo ganho)
        profit_if_win = bet_sizing.stake_amount * (bet_sizing.odds - 1)
        new_capital_if_win = current_status.current_capital + profit_if_win
        new_capital_percentage_win = (new_capital_if_win / current_status.initial_capital) * 100
        
        return {
            'impact_percentage': impact_percentage,
            'current_capital': current_status.current_capital,
            'new_capital_if_loss': new_capital_if_loss,
            'new_capital_if_win': new_capital_if_win,
            'capital_change_if_loss': new_capital_percentage - current_status.profit_percentage,
            'capital_change_if_win': new_capital_percentage_win - current_status.profit_percentage,
            'risk_level': 'HIGH' if impact_percentage > 0.05 else 'MEDIUM' if impact_percentage > 0.02 else 'LOW'
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
        current_status = self.bankroll_manager.get_bankroll_status()
        
        self.performance_metrics = {
            'current_profit_percentage': current_status.profit_percentage,
            'current_drawdown': current_status.drawdown_percentage,
            'win_rate': current_status.win_rate,
            'total_bets': current_status.total_bets,
            'last_updated': datetime.now().isoformat()
        }
    
    def _analyze_backtesting_performance(self, portfolio: List[Dict]) -> Dict:
        """Analisa performance do backtesting"""
        if not portfolio:
            return {}
        
        df = pd.DataFrame(portfolio)
        
        # Análise de retorno
        initial_capital = df['bankroll_status'].iloc[0]['initial_capital']
        final_capital = df['bankroll_status'].iloc[-1]['current_capital']
        total_return = (final_capital - initial_capital) / initial_capital * 100
        
        # Análise de drawdown
        capitals = [status['current_capital'] for status in df['bankroll_status']]
        max_capital = max(capitals)
        min_capital = min(capitals)
        max_drawdown = (max_capital - min_capital) / max_capital * 100
        
        # Análise de volatilidade
        returns = []
        for i in range(1, len(capitals)):
            ret = (capitals[i] - capitals[i-1]) / capitals[i-1]
            returns.append(ret)
        
        volatility = np.std(returns) * 100 if returns else 0
        
        # Análise de sequências
        bet_results = [bet['bet_sizing']['is_winner'] for bet in portfolio]
        win_streak = self._calculate_max_streak(bet_results, True)
        loss_streak = self._calculate_max_streak(bet_results, False)
        
        return {
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
            'max_win_streak': win_streak,
            'max_loss_streak': loss_streak,
            'sharpe_ratio': total_return / volatility if volatility > 0 else 0
        }
    
    def _analyze_bankroll_trends(self) -> Dict:
        """Analisa tendências da banca"""
        if not self.bankroll_manager.capital_history:
            return {}
        
        df = pd.DataFrame(self.bankroll_manager.capital_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        # Tendência de curto prazo (últimos 7 dias)
        recent_data = df.last('7D')
        if not recent_data.empty:
            recent_trend = 'UP' if recent_data['capital'].iloc[-1] > recent_data['capital'].iloc[0] else 'DOWN'
        else:
            recent_trend = 'STABLE'
        
        # Tendência de longo prazo (todo o período)
        overall_trend = 'UP' if df['capital'].iloc[-1] > df['capital'].iloc[0] else 'DOWN'
        
        return {
            'recent_trend': recent_trend,
            'overall_trend': overall_trend,
            'volatility': df['capital'].std(),
            'growth_rate': (df['capital'].iloc[-1] / df['capital'].iloc[0] - 1) * 100 if len(df) > 1 else 0
        }
    
    def _analyze_performance_by_period(self) -> Dict:
        """Analisa performance por período"""
        if not self.betting_history:
            return {}
        
        df = pd.DataFrame(self.betting_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Agrupa por dia
        daily_performance = df.groupby('date').agg({
            'bet_sizing': lambda x: sum([bet['profit'] for bet in x]),
            'bet_sizing': lambda x: len(x)
        }).rename(columns={'bet_sizing': 'daily_profit'})
        
        return {
            'daily_performance': daily_performance.to_dict(),
            'best_day': daily_performance['daily_profit'].idxmax() if not daily_performance.empty else None,
            'worst_day': daily_performance['daily_profit'].idxmin() if not daily_performance.empty else None
        }
    
    def _generate_strategic_recommendations(self, bankroll_status: BankrollStatus,
                                          betting_stats: Dict, risk_check: Dict) -> List[Dict]:
        """Gera recomendações estratégicas"""
        recommendations = []
        
        # Recomendação baseada no status da banca
        if bankroll_status.status == 'CRITICAL':
            recommendations.append({
                'type': 'RISK_MANAGEMENT',
                'priority': 'HIGH',
                'message': 'Status crítico - considere reduzir exposição',
                'action': 'Reduzir tamanho das apostas ou pausar'
            })
        elif bankroll_status.status == 'DANGER':
            recommendations.append({
                'type': 'RISK_MANAGEMENT',
                'priority': 'MEDIUM',
                'message': 'Status de perigo - monitore de perto',
                'action': 'Ajustar estratégia de apostas'
            })
        
        # Recomendação baseada no drawdown
        if bankroll_status.drawdown_percentage > 15:
            recommendations.append({
                'type': 'DRAWDOWN_WARNING',
                'priority': 'HIGH',
                'message': f'Drawdown alto: {bankroll_status.drawdown_percentage:.1f}%',
                'action': 'Considerar stop loss ou redução de exposição'
            })
        
        # Recomendação baseada na taxa de acerto
        if betting_stats.get('win_rate', 0) < 0.4 and betting_stats.get('total_bets', 0) > 10:
            recommendations.append({
                'type': 'PERFORMANCE_WARNING',
                'priority': 'MEDIUM',
                'message': f'Taxa de acerto baixa: {betting_stats["win_rate"]:.1%}',
                'action': 'Revisar critérios de seleção de apostas'
            })
        
        # Recomendação baseada no ROI
        if betting_stats.get('roi', 0) < 0:
            recommendations.append({
                'type': 'ROI_WARNING',
                'priority': 'HIGH',
                'message': f'ROI negativo: {betting_stats["roi"]:.1f}%',
                'action': 'Pausar apostas e revisar estratégia'
            })
        
        return recommendations
    
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
    
    def _get_risk_recommendation(self, results: Dict, best_risk_level: str) -> Dict:
        """Gera recomendação de nível de risco"""
        if not results or not best_risk_level:
            return {'recommendation': 'CONSERVATIVE', 'reason': 'Dados insuficientes'}
        
        best_metrics = results[best_risk_level]
        
        if best_metrics['profit_percentage'] > 20 and best_metrics['max_drawdown'] < 10:
            return {
                'recommendation': best_risk_level,
                'reason': 'Excelente retorno com baixo risco',
                'confidence': 'HIGH'
            }
        elif best_metrics['profit_percentage'] > 10:
            return {
                'recommendation': best_risk_level,
                'reason': 'Bom retorno com risco controlado',
                'confidence': 'MEDIUM'
            }
        else:
            return {
                'recommendation': 'CONSERVATIVE',
                'reason': 'Retornos baixos em todos os níveis',
                'confidence': 'LOW'
            }

if __name__ == "__main__":
    # Teste do sistema de gestão de banca
    system = AdvancedBankrollSystem()
    
    print("=== TESTE DO SISTEMA DE GESTÃO DE BANCA ===")
    
    # Testa análise de oportunidade
    opportunity = system.analyze_bet_opportunity('Flamengo', 'Palmeiras', '2024-01-15')
    
    if opportunity:
        print(f"\nAnálise de Oportunidade:")
        print(f"  Partida: {opportunity['match_info']['home_team']} vs {opportunity['match_info']['away_team']}")
        print(f"  Stake recomendado: {opportunity['bet_sizing']['stake_percentage']:.1%}")
        print(f"  Valor da aposta: R$ {opportunity['bet_sizing']['stake_amount']:.2f}")
        print(f"  EV: {opportunity['bet_sizing']['expected_value']:.3f}")
        print(f"  Recomendação: {opportunity['final_recommendation']['action']}")
        print(f"  Status da banca: {opportunity['bankroll_status']['status']}")
    
    # Testa execução de aposta
    bet_result = system.execute_bet_with_management(
        'Flamengo', 'Palmeiras', '2024-01-15', 
        'home_win', 'home_win'
    )
    
    if bet_result['success']:
        print(f"\nAposta Executada:")
        print(f"  Resultado: {bet_result['bet_result']['result']}")
        print(f"  Lucro: R$ {bet_result['bet_result']['profit']:.2f}")
        print(f"  Capital: R$ {bet_result['bankroll_status']['current_capital']:.2f}")
    
    # Analytics
    analytics = system.get_bankroll_analytics()
    print(f"\nAnalytics da Banca:")
    print(f"  Capital: R$ {analytics['bankroll_status']['current_capital']:.2f}")
    print(f"  Lucro: {analytics['bankroll_status']['profit_percentage']:.1f}%")
    print(f"  Status: {analytics['bankroll_status']['status']}")
    print(f"  Alertas: {analytics['risk_alerts']['total_alerts']}")
    
    print("Teste concluído!")
