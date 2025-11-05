"""
Integração do Sistema de Cálculo de Probabilidades - MaraBet AI
Conecta o calculador de probabilidades com o framework de análise
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple
import json

from probability_calculator import ProbabilityCalculator, ProbabilityWeights, ProbabilityResult
from framework_integration import MaraBetFramework
from data_framework import DataProcessor
from advanced_features import AdvancedFeatureEngineer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedProbabilitySystem:
    """
    Sistema Avançado de Cálculo de Probabilidades
    Integra o calculador de probabilidades com o framework completo
    """
    
    def __init__(self, custom_weights: Optional[ProbabilityWeights] = None):
        self.framework = MaraBetFramework()
        self.data_processor = DataProcessor()
        self.feature_engineer = AdvancedFeatureEngineer()
        self.probability_calculator = ProbabilityCalculator(custom_weights)
        self.calculation_history = []
        
    def calculate_match_probabilities(self, home_team: str, away_team: str, match_date: str) -> Dict:
        """
        Calcula probabilidades completas de uma partida
        """
        logger.info(f"Calculando probabilidades: {home_team} vs {away_team}")
        
        try:
            # Análise completa usando o framework
            match_analysis = self.data_processor.process_match_analysis(home_team, away_team, match_date)
            
            # Prepara dados para cálculo de probabilidades
            match_data = self._prepare_match_data_for_probability_calculation(
                home_team, away_team, match_date, match_analysis
            )
            
            # Calcula probabilidades usando a estrutura de pesos
            probability_result = self.probability_calculator.calculate_probabilities(match_data)
            
            # Calcula odds baseadas nas probabilidades
            odds = self._calculate_odds_from_probabilities(probability_result)
            
            # Análise de valor das apostas
            betting_analysis = self._analyze_betting_value(probability_result, odds)
            
            # Análise de confiança e incerteza
            confidence_analysis = self._analyze_confidence_and_uncertainty(probability_result, match_analysis)
            
            # Recomendações baseadas nas probabilidades
            recommendations = self._create_probability_based_recommendations(
                probability_result, odds, betting_analysis, confidence_analysis
            )
            
            # Resumo executivo
            executive_summary = self._create_probability_executive_summary(
                probability_result, match_analysis, betting_analysis, confidence_analysis
            )
            
            result = {
                'match_info': {
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': match_date,
                    'calculation_timestamp': datetime.now().isoformat()
                },
                'probabilities': {
                    'home_win': probability_result.home_win,
                    'draw': probability_result.draw,
                    'away_win': probability_result.away_win
                },
                'odds': odds,
                'confidence': probability_result.confidence,
                'breakdown': probability_result.breakdown,
                'weights_used': {
                    'historico_recente': probability_result.weights_used.historico_recente,
                    'confrontos_diretos': probability_result.weights_used.confrontos_diretos,
                    'estatisticas_avancadas': probability_result.weights_used.estatisticas_avancadas,
                    'fatores_contextuais': probability_result.weights_used.fatores_contextuais,
                    'analise_momentum': probability_result.weights_used.analise_momentum
                },
                'betting_analysis': betting_analysis,
                'confidence_analysis': confidence_analysis,
                'recommendations': recommendations,
                'executive_summary': executive_summary,
                'data_analysis': match_analysis
            }
            
            # Registra no histórico
            self.calculation_history.append({
                'timestamp': datetime.now(),
                'match': f"{home_team} vs {away_team}",
                'probabilities': result['probabilities'],
                'confidence': result['confidence']
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no cálculo de probabilidades: {e}")
            return None
    
    def _prepare_match_data_for_probability_calculation(self, home_team: str, away_team: str, 
                                                      match_date: str, match_analysis: Dict) -> Dict:
        """
        Prepara dados da partida para cálculo de probabilidades
        """
        # Extrai dados relevantes da análise do framework
        home_analysis = match_analysis['home_team_analysis']
        away_analysis = match_analysis['away_team_analysis']
        h2h_stats = match_analysis['head_to_head']
        match_context = match_analysis['match_context']
        
        # Prepara dados estruturados para o calculador
        match_data = {
            'home_team': home_team,
            'away_team': away_team,
            'date': match_date,
            'home_team_analysis': home_analysis,
            'away_team_analysis': away_analysis,
            'head_to_head': h2h_stats,
            'match_context': match_context,
            'comparative_analysis': match_analysis['comparative_analysis']
        }
        
        return match_data
    
    def _calculate_odds_from_probabilities(self, probability_result: ProbabilityResult) -> Dict:
        """
        Calcula odds baseadas nas probabilidades
        """
        # Adiciona margem da casa (5%)
        margin = 0.05
        adjusted_probs = {
            'home_win': probability_result.home_win * (1 - margin),
            'draw': probability_result.draw * (1 - margin),
            'away_win': probability_result.away_win * (1 - margin)
        }
        
        # Calcula odds
        odds = {
            'home': 1 / adjusted_probs['home_win'] if adjusted_probs['home_win'] > 0 else 1000,
            'draw': 1 / adjusted_probs['draw'] if adjusted_probs['draw'] > 0 else 1000,
            'away': 1 / adjusted_probs['away_win'] if adjusted_probs['away_win'] > 0 else 1000
        }
        
        return {
            'calculated_odds': odds,
            'adjusted_probabilities': adjusted_probs,
            'margin': margin,
            'market_odds': {
                'home': 2.0,  # Simulado - em produção viria de API
                'draw': 3.2,
                'away': 3.5
            }
        }
    
    def _analyze_betting_value(self, probability_result: ProbabilityResult, odds: Dict) -> Dict:
        """
        Analisa valor das apostas baseado nas probabilidades
        """
        market_odds = odds['market_odds']
        calculated_odds = odds['calculated_odds']
        
        betting_values = []
        
        for outcome in ['home_win', 'draw', 'away_win']:
            prob = getattr(probability_result, outcome)
            market_odd = market_odds[outcome]
            calculated_odd = calculated_odds[outcome]
            
            # Valor esperado
            expected_value = (prob * market_odd) - 1
            
            # Kelly Criterion
            kelly = (prob * market_odd - 1) / (market_odd - 1) if market_odd > 1 else 0
            kelly = max(0, min(kelly, 0.25))  # Limita entre 0 e 25%
            
            # Análise de valor
            if expected_value > 0.15:
                value_rating = 'HIGH_VALUE'
            elif expected_value > 0.10:
                value_rating = 'GOOD_VALUE'
            elif expected_value > 0.05:
                value_rating = 'FAIR_VALUE'
            else:
                value_rating = 'LOW_VALUE'
            
            betting_values.append({
                'outcome': outcome,
                'probability': prob,
                'market_odds': market_odd,
                'calculated_odds': calculated_odd,
                'expected_value': expected_value,
                'kelly_percentage': kelly,
                'value_rating': value_rating,
                'odds_difference': calculated_odd - market_odd,
                'value_score': expected_value * 100  # Score de 0-100
            })
        
        # Ordena por valor esperado
        betting_values.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return {
            'betting_values': betting_values,
            'best_value_bet': betting_values[0] if betting_values else None,
            'total_positive_value': len([bv for bv in betting_values if bv['expected_value'] > 0]),
            'average_expected_value': np.mean([bv['expected_value'] for bv in betting_values]),
            'highest_value': max([bv['expected_value'] for bv in betting_values]) if betting_values else 0
        }
    
    def _analyze_confidence_and_uncertainty(self, probability_result: ProbabilityResult, 
                                          match_analysis: Dict) -> Dict:
        """
        Analisa confiança e incerteza das probabilidades
        """
        # Confiança geral
        overall_confidence = probability_result.confidence
        
        # Análise de confiança por componente
        component_confidences = {}
        for component, data in probability_result.breakdown.items():
            component_confidences[component] = {
                'confidence': data['confidence'],
                'weight': data['weight'],
                'weighted_confidence': data['confidence'] * data['weight']
            }
        
        # Confiança ponderada
        weighted_confidence = sum(comp['weighted_confidence'] for comp in component_confidences.values())
        
        # Análise de incerteza
        probabilities = [probability_result.home_win, probability_result.draw, probability_result.away_win]
        max_prob = max(probabilities)
        uncertainty = 1 - max_prob  # Incerteza baseada na clareza da predição
        
        # Análise de consistência entre componentes
        component_probs = []
        for component, data in probability_result.breakdown.items():
            component_probs.append(data['probabilities']['home_win'])
        
        consistency = 1 - np.std(component_probs)  # Consistência baseada no desvio padrão
        
        # Classificação da confiança
        if overall_confidence >= 0.8:
            confidence_level = 'VERY_HIGH'
        elif overall_confidence >= 0.7:
            confidence_level = 'HIGH'
        elif overall_confidence >= 0.6:
            confidence_level = 'MEDIUM'
        elif overall_confidence >= 0.5:
            confidence_level = 'LOW'
        else:
            confidence_level = 'VERY_LOW'
        
        return {
            'overall_confidence': overall_confidence,
            'weighted_confidence': weighted_confidence,
            'uncertainty': uncertainty,
            'consistency': consistency,
            'confidence_level': confidence_level,
            'component_confidences': component_confidences,
            'confidence_factors': {
                'data_quality': np.random.uniform(0.7, 0.9),  # Simulado
                'sample_size': np.random.uniform(0.6, 0.9),   # Simulado
                'recency': np.random.uniform(0.8, 1.0)        # Simulado
            }
        }
    
    def _create_probability_based_recommendations(self, probability_result: ProbabilityResult,
                                                odds: Dict, betting_analysis: Dict,
                                                confidence_analysis: Dict) -> Dict:
        """
        Cria recomendações baseadas nas probabilidades
        """
        recommendations = []
        
        for betting_value in betting_analysis['betting_values']:
            outcome = betting_value['outcome']
            ev = betting_value['expected_value']
            kelly = betting_value['kelly_percentage']
            value_rating = betting_value['value_rating']
            
            # Determina recomendação baseada em múltiplos fatores
            confidence_factor = confidence_analysis['overall_confidence']
            uncertainty_factor = 1 - confidence_analysis['uncertainty']
            
            # Ajusta EV baseado na confiança
            adjusted_ev = ev * confidence_factor * uncertainty_factor
            
            if adjusted_ev > 0.15 and kelly > 0.03 and confidence_factor > 0.7:
                recommendation = 'STRONG_BET'
                confidence = 'HIGH'
            elif adjusted_ev > 0.10 and kelly > 0.02 and confidence_factor > 0.6:
                recommendation = 'BET'
                confidence = 'MEDIUM'
            elif adjusted_ev > 0.05 and confidence_factor > 0.5:
                recommendation = 'CONSIDER'
                confidence = 'LOW'
            else:
                recommendation = 'AVOID'
                confidence = 'VERY_LOW'
            
            recommendations.append({
                'outcome': outcome,
                'recommendation': recommendation,
                'confidence': confidence,
                'expected_value': ev,
                'adjusted_expected_value': adjusted_ev,
                'kelly_percentage': kelly,
                'value_rating': value_rating,
                'probability': getattr(probability_result, outcome),
                'market_odds': betting_value['market_odds'],
                'calculated_odds': betting_value['calculated_odds']
            })
        
        # Ordena por valor esperado ajustado
        recommendations.sort(key=lambda x: x['adjusted_expected_value'], reverse=True)
        
        return {
            'recommendations': recommendations,
            'best_recommendation': recommendations[0] if recommendations else None,
            'strong_bets': len([r for r in recommendations if r['recommendation'] == 'STRONG_BET']),
            'total_recommendations': len(recommendations),
            'average_confidence': np.mean([r['confidence'] for r in recommendations]),
            'recommendation_summary': {
                'strong_bets': len([r for r in recommendations if r['recommendation'] == 'STRONG_BET']),
                'bets': len([r for r in recommendations if r['recommendation'] == 'BET']),
                'consider': len([r for r in recommendations if r['recommendation'] == 'CONSIDER']),
                'avoid': len([r for r in recommendations if r['recommendation'] == 'AVOID'])
            }
        }
    
    def _create_probability_executive_summary(self, probability_result: ProbabilityResult,
                                            match_analysis: Dict, betting_analysis: Dict,
                                            confidence_analysis: Dict) -> Dict:
        """
        Cria resumo executivo baseado nas probabilidades
        """
        home_team = match_analysis['match_info']['home_team']
        away_team = match_analysis['match_info']['away_team']
        
        # Predição mais provável
        probabilities = {
            'home_win': probability_result.home_win,
            'draw': probability_result.draw,
            'away_win': probability_result.away_win
        }
        
        most_likely = max(probabilities, key=probabilities.get)
        most_likely_prob = probabilities[most_likely]
        
        # Análise dos componentes mais influentes
        component_contributions = []
        for component, data in probability_result.breakdown.items():
            contribution = data['weight'] * data['confidence']
            component_contributions.append({
                'component': component,
                'weight': data['weight'],
                'confidence': data['confidence'],
                'contribution': contribution
            })
        
        component_contributions.sort(key=lambda x: x['contribution'], reverse=True)
        most_influential = component_contributions[0]['component'] if component_contributions else 'unknown'
        
        # Insights baseados nas probabilidades
        insights = []
        
        # Insight sobre a predição
        if most_likely_prob > 0.5:
            insights.append(f"Predição clara: {most_likely.replace('_', ' ').title()} ({most_likely_prob:.1%})")
        else:
            insights.append(f"Partida equilibrada: {most_likely.replace('_', ' ').title()} ligeiramente favorito ({most_likely_prob:.1%})")
        
        # Insight sobre confiança
        confidence_level = confidence_analysis['confidence_level']
        if confidence_level in ['VERY_HIGH', 'HIGH']:
            insights.append(f"Alta confiança na predição ({confidence_level})")
        elif confidence_level == 'LOW':
            insights.append(f"Baixa confiança na predição - considere cautela")
        
        # Insight sobre valor das apostas
        best_value = betting_analysis['best_value_bet']
        if best_value and best_value['expected_value'] > 0.1:
            insights.append(f"Boa oportunidade de aposta: {best_value['outcome']} (EV: {best_value['expected_value']:.1%})")
        
        # Insight sobre componente mais influente
        insights.append(f"Fator mais influente: {most_influential.replace('_', ' ').title()}")
        
        return {
            'match': f"{home_team} vs {away_team}",
            'prediction': {
                'most_likely': most_likely,
                'probability': most_likely_prob,
                'confidence': probability_result.confidence
            },
            'probabilities': probabilities,
            'confidence_level': confidence_level,
            'most_influential_factor': most_influential,
            'betting_opportunity': {
                'best_value': best_value['outcome'] if best_value else None,
                'expected_value': best_value['expected_value'] if best_value else 0,
                'recommendation': best_value['value_rating'] if best_value else 'NO_VALUE'
            },
            'insights': insights,
            'component_breakdown': component_contributions[:3]  # Top 3 componentes
        }
    
    def run_probability_backtesting(self, historical_matches: List[Dict], initial_capital: float = 1000) -> Dict:
        """
        Executa backtesting usando o sistema de probabilidades
        """
        logger.info("Executando backtesting com sistema de probabilidades")
        
        try:
            portfolio = []
            current_capital = initial_capital
            bet_size = 0.02  # 2% do capital por aposta
            
            for match in historical_matches[:50]:  # Limita para performance
                try:
                    # Calcula probabilidades
                    prob_result = self.calculate_match_probabilities(
                        match['home_team'],
                        match['away_team'],
                        match['date']
                    )
                    
                    if not prob_result:
                        continue
                    
                    # Encontra melhor aposta baseada nas probabilidades
                    best_bet = None
                    for rec in prob_result['recommendations']['recommendations']:
                        if rec['recommendation'] in ['STRONG_BET', 'BET'] and rec['expected_value'] > 0.1:
                            best_bet = rec
                            break
                    
                    if best_bet:
                        # Calcula tamanho da aposta
                        bet_amount = current_capital * bet_size
                        kelly_bet = current_capital * best_bet['kelly_percentage']
                        final_bet = min(bet_amount, kelly_bet)
                        
                        # Simula resultado
                        actual_result = self._simulate_match_result(match)
                        is_winner = self._check_bet_result(best_bet['outcome'], actual_result)
                        
                        # Calcula lucro/prejuízo
                        if is_winner:
                            profit = final_bet * (best_bet['market_odds'] - 1)
                        else:
                            profit = -final_bet
                        
                        current_capital += profit
                        
                        # Registra trade
                        trade = {
                            'match_id': match.get('id', f'match_{len(portfolio)}'),
                            'date': match['date'],
                            'home_team': match['home_team'],
                            'away_team': match['away_team'],
                            'bet_outcome': best_bet['outcome'],
                            'bet_odds': best_bet['market_odds'],
                            'bet_amount': final_bet,
                            'expected_value': best_bet['expected_value'],
                            'probability': best_bet['probability'],
                            'confidence': prob_result['confidence'],
                            'actual_result': actual_result,
                            'is_winner': is_winner,
                            'profit': profit,
                            'capital_after': current_capital,
                            'roi': (current_capital - initial_capital) / initial_capital * 100
                        }
                        
                        portfolio.append(trade)
                        
                except Exception as e:
                    logger.error(f"Erro ao processar partida no backtesting: {e}")
                    continue
            
            # Calcula métricas
            metrics = self._calculate_probability_metrics(portfolio)
            
            return {
                'success': True,
                'portfolio': portfolio,
                'metrics': metrics,
                'probability_summary': self.probability_calculator.get_calculation_summary()
            }
            
        except Exception as e:
            logger.error(f"Erro no backtesting de probabilidades: {e}")
            return {'success': False, 'error': str(e)}
    
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
    
    def _check_bet_result(self, bet_outcome: str, actual_result: str) -> bool:
        """Verifica se a aposta foi vencedora"""
        return bet_outcome == actual_result
    
    def _calculate_probability_metrics(self, portfolio: List[Dict]) -> Dict:
        """Calcula métricas específicas do backtesting de probabilidades"""
        if not portfolio:
            return {}
        
        df = pd.DataFrame(portfolio)
        
        # Métricas básicas
        total_trades = len(df)
        winning_trades = len(df[df['is_winner'] == True])
        losing_trades = len(df[df['is_winner'] == False])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Métricas financeiras
        total_profit = df['profit'].sum()
        total_bet_amount = df['bet_amount'].sum()
        roi = (total_profit / total_bet_amount * 100) if total_bet_amount > 0 else 0
        
        # Métricas de probabilidades
        avg_probability = df['probability'].mean() if 'probability' in df.columns else 0
        avg_confidence = df['confidence'].mean() if 'confidence' in df.columns else 0
        avg_expected_value = df['expected_value'].mean() if 'expected_value' in df.columns else 0
        
        # Análise de precisão das probabilidades
        high_prob_trades = len(df[df['probability'] > 0.6]) if 'probability' in df.columns else 0
        high_prob_win_rate = len(df[(df['probability'] > 0.6) & (df['is_winner'] == True)]) / high_prob_trades if high_prob_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_bet_amount': total_bet_amount,
            'roi': roi,
            'avg_probability': avg_probability,
            'avg_confidence': avg_confidence,
            'avg_expected_value': avg_expected_value,
            'high_prob_trades': high_prob_trades,
            'high_prob_win_rate': high_prob_win_rate,
            'probability_accuracy': high_prob_win_rate,
            'confidence_adjusted_roi': roi * avg_confidence if avg_confidence > 0 else roi
        }
    
    def get_probability_analytics(self) -> Dict:
        """Retorna analytics do sistema de probabilidades"""
        if not self.calculation_history:
            return {'total_calculations': 0}
        
        recent_calculations = self.calculation_history[-20:]  # Últimas 20
        
        avg_confidence = np.mean([calc['confidence'] for calc in recent_calculations])
        
        # Análise de distribuição de probabilidades
        home_probs = [calc['probabilities']['home_win'] for calc in recent_calculations]
        draw_probs = [calc['probabilities']['draw'] for calc in recent_calculations]
        away_probs = [calc['probabilities']['away_win'] for calc in recent_calculations]
        
        return {
            'total_calculations': len(self.calculation_history),
            'recent_calculations': len(recent_calculations),
            'average_confidence': avg_confidence,
            'probability_distribution': {
                'home_win': {
                    'mean': np.mean(home_probs),
                    'std': np.std(home_probs),
                    'min': np.min(home_probs),
                    'max': np.max(home_probs)
                },
                'draw': {
                    'mean': np.mean(draw_probs),
                    'std': np.std(draw_probs),
                    'min': np.min(draw_probs),
                    'max': np.max(draw_probs)
                },
                'away_win': {
                    'mean': np.mean(away_probs),
                    'std': np.std(away_probs),
                    'min': np.min(away_probs),
                    'max': np.max(away_probs)
                }
            },
            'weights_used': {
                'historico_recente': self.probability_calculator.weights.historico_recente,
                'confrontos_diretos': self.probability_calculator.weights.confrontos_diretos,
                'estatisticas_avancadas': self.probability_calculator.weights.estatisticas_avancadas,
                'fatores_contextuais': self.probability_calculator.weights.fatores_contextuais,
                'analise_momentum': self.probability_calculator.weights.analise_momentum
            }
        }

if __name__ == "__main__":
    # Teste do sistema de probabilidades
    system = AdvancedProbabilitySystem()
    
    print("=== TESTE DO SISTEMA DE PROBABILIDADES ===")
    
    # Testa cálculo de probabilidades
    result = system.calculate_match_probabilities('Flamengo', 'Palmeiras', '2024-01-15')
    
    if result:
        print(f"\nProbabilidades:")
        print(f"  Casa: {result['probabilities']['home_win']:.3f} ({result['probabilities']['home_win']*100:.1f}%)")
        print(f"  Empate: {result['probabilities']['draw']:.3f} ({result['probabilities']['draw']*100:.1f}%)")
        print(f"  Fora: {result['probabilities']['away_win']:.3f} ({result['probabilities']['away_win']*100:.1f}%)")
        print(f"  Confiança: {result['confidence']:.3f}")
        
        print(f"\nBreakdown por Componente:")
        for component, data in result['breakdown'].items():
            print(f"  {component}: {data['weight']:.1%} (Conf: {data['confidence']:.3f})")
        
        print(f"\nAnálise de Apostas:")
        betting = result['betting_analysis']
        print(f"  Melhor valor: {betting['best_value_bet']['outcome']} (EV: {betting['best_value_bet']['expected_value']:.1%})")
        print(f"  Apostas com valor positivo: {betting['total_positive_value']}")
        
        print(f"\nResumo Executivo:")
        summary = result['executive_summary']
        print(f"  Predição: {summary['prediction']['most_likely']} ({summary['prediction']['probability']:.1%})")
        print(f"  Fator mais influente: {summary['most_influential_factor']}")
        for insight in summary['insights'][:3]:
            print(f"  • {insight}")
    
    print("Teste concluído!")
