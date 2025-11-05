"""
Integração do Sistema de Identificação de Valor - MaraBet AI
Conecta o identificador de valor com o framework completo
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import json

from value_identification import (
    ValueIdentifier, ValueThresholds, ValueLevel, 
    ValueOpportunity, ValueAnalysis
)
from probability_integration import AdvancedProbabilitySystem
from framework_integration import MaraBetFramework
from data_framework import DataProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedValueSystem:
    """
    Sistema Avançado de Identificação de Valor
    Integra identificação de valor com todo o framework
    """
    
    def __init__(self, custom_thresholds: Optional[ValueThresholds] = None):
        self.framework = MaraBetFramework()
        self.data_processor = DataProcessor()
        self.probability_system = AdvancedProbabilitySystem()
        self.value_identifier = ValueIdentifier(custom_thresholds)
        self.value_history = []
        
    def analyze_match_value(self, home_team: str, away_team: str, match_date: str) -> Dict:
        """
        Analisa valor de uma partida específica
        """
        logger.info(f"Analisando valor: {home_team} vs {away_team}")
        
        try:
            # Análise completa da partida
            match_analysis = self.data_processor.process_match_analysis(home_team, away_team, match_date)
            
            # Cálculo de probabilidades
            prob_result = self.probability_system.calculate_match_probabilities(
                home_team, away_team, match_date
            )
            
            if not prob_result:
                return None
            
            # Prepara dados para identificação de valor
            match_data = {
                'id': f"{home_team}_{away_team}_{match_date}",
                'home_team': home_team,
                'away_team': away_team,
                'date': match_date
            }
            
            probabilities = prob_result['probabilities']
            market_odds = prob_result['odds']['market_odds']
            
            # Identifica oportunidades de valor
            value_analysis = self.value_identifier.create_value_analysis(
                match_data, probabilities, market_odds
            )
            
            # Análise de portfólio
            portfolio_analysis = self._analyze_portfolio_value(value_analysis.opportunities)
            
            # Recomendações estratégicas
            strategic_recommendations = self._create_strategic_recommendations(
                value_analysis, match_analysis, prob_result
            )
            
            # Análise de risco
            risk_analysis = self._analyze_value_risk(value_analysis, match_analysis)
            
            # Resumo executivo
            executive_summary = self._create_value_executive_summary(
                value_analysis, portfolio_analysis, strategic_recommendations, risk_analysis
            )
            
            result = {
                'match_info': match_data,
                'value_analysis': {
                    'opportunities': [
                        {
                            'outcome': opp.outcome,
                            'market_odds': opp.market_odds,
                            'calculated_odds': opp.calculated_odds,
                            'probability': opp.probability,
                            'expected_value': opp.expected_value,
                            'value_level': opp.value_level.value,
                            'confidence': opp.confidence,
                            'kelly_percentage': opp.kelly_percentage,
                            'recommendation': opp.recommendation,
                            'additional_metrics': opp.additional_metrics
                        }
                        for opp in value_analysis.opportunities
                    ],
                    'best_opportunity': {
                        'outcome': value_analysis.best_opportunity.outcome,
                        'expected_value': value_analysis.best_opportunity.expected_value,
                        'recommendation': value_analysis.best_opportunity.recommendation,
                        'kelly_percentage': value_analysis.best_opportunity.kelly_percentage
                    } if value_analysis.best_opportunity else None,
                    'total_opportunities': value_analysis.total_opportunities,
                    'value_distribution': value_analysis.value_distribution,
                    'average_ev': value_analysis.average_ev,
                    'highest_ev': value_analysis.highest_ev,
                    'confidence_score': value_analysis.confidence_score,
                    'market_efficiency': value_analysis.market_efficiency
                },
                'portfolio_analysis': portfolio_analysis,
                'strategic_recommendations': strategic_recommendations,
                'risk_analysis': risk_analysis,
                'executive_summary': executive_summary,
                'probability_analysis': prob_result,
                'match_analysis': match_analysis
            }
            
            # Registra no histórico
            self.value_history.append({
                'timestamp': datetime.now(),
                'match': f"{home_team} vs {away_team}",
                'value_analysis': value_analysis,
                'best_opportunity': value_analysis.best_opportunity
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise de valor: {e}")
            return None
    
    def scan_market_opportunities(self, league: str = 'all', days: int = 7) -> Dict:
        """
        Escaneia o mercado em busca de oportunidades de valor
        """
        logger.info(f"Escaneando mercado: {league}, {days} dias")
        
        try:
            # Coleta dados de partidas
            matches = self.data_processor.collect_historical_data(league, days)
            
            if not matches:
                return {'success': False, 'error': 'Nenhuma partida encontrada'}
            
            # Analisa cada partida
            value_analyses = []
            all_opportunities = []
            
            for match in matches[:20]:  # Limita para performance
                try:
                    analysis = self.analyze_match_value(
                        match['home_team'],
                        match['away_team'],
                        match['date']
                    )
                    
                    if analysis:
                        value_analyses.append(analysis)
                        all_opportunities.extend(analysis['value_analysis']['opportunities'])
                        
                except Exception as e:
                    logger.error(f"Erro ao analisar partida: {e}")
                    continue
            
            # Análise agregada
            market_summary = self._create_market_summary(value_analyses, all_opportunities)
            
            # Alertas de valor
            alerts = self._generate_market_alerts(all_opportunities)
            
            # Top oportunidades
            top_opportunities = self._get_top_opportunities(all_opportunities)
            
            return {
                'success': True,
                'market_summary': market_summary,
                'alerts': alerts,
                'top_opportunities': top_opportunities,
                'total_matches_analyzed': len(value_analyses),
                'total_opportunities_found': len(all_opportunities),
                'value_analyses': value_analyses
            }
            
        except Exception as e:
            logger.error(f"Erro no escaneamento do mercado: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_value_backtesting(self, historical_matches: List[Dict], 
                            initial_capital: float = 1000) -> Dict:
        """
        Executa backtesting focado em identificação de valor
        """
        logger.info("Executando backtesting de valor")
        
        try:
            portfolio = []
            current_capital = initial_capital
            total_bet_amount = 0
            total_profit = 0
            
            for match in historical_matches[:50]:  # Limita para performance
                try:
                    # Analisa valor da partida
                    value_result = self.analyze_match_value(
                        match['home_team'],
                        match['away_team'],
                        match['date']
                    )
                    
                    if not value_result:
                        continue
                    
                    # Encontra melhor oportunidade
                    best_opportunity = value_result['value_analysis']['best_opportunity']
                    
                    if not best_opportunity or best_opportunity['expected_value'] <= 0:
                        continue
                    
                    # Calcula tamanho da aposta
                    kelly_percentage = best_opportunity['kelly_percentage']
                    bet_amount = current_capital * kelly_percentage
                    bet_amount = min(bet_amount, current_capital * 0.1)  # Limita a 10%
                    
                    if bet_amount < 10:  # Aposta mínima
                        continue
                    
                    # Simula resultado
                    actual_result = self._simulate_match_result(match)
                    is_winner = self._check_bet_result(best_opportunity['outcome'], actual_result)
                    
                    # Calcula lucro/prejuízo
                    if is_winner:
                        profit = bet_amount * (best_opportunity['market_odds'] - 1)
                    else:
                        profit = -bet_amount
                    
                    current_capital += profit
                    total_bet_amount += bet_amount
                    total_profit += profit
                    
                    # Registra trade
                    trade = {
                        'match_id': match.get('id', f'match_{len(portfolio)}'),
                        'date': match['date'],
                        'home_team': match['home_team'],
                        'away_team': match['away_team'],
                        'bet_outcome': best_opportunity['outcome'],
                        'bet_odds': best_opportunity['market_odds'],
                        'bet_amount': bet_amount,
                        'expected_value': best_opportunity['expected_value'],
                        'kelly_percentage': kelly_percentage,
                        'confidence': value_result['value_analysis']['confidence_score'],
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
            metrics = self._calculate_value_metrics(portfolio, initial_capital)
            
            return {
                'success': True,
                'portfolio': portfolio,
                'metrics': metrics,
                'value_statistics': self.value_identifier.get_value_statistics()
            }
            
        except Exception as e:
            logger.error(f"Erro no backtesting de valor: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_portfolio_value(self, opportunities: List[ValueOpportunity]) -> Dict:
        """Analisa valor do portfólio baseado nas oportunidades"""
        if not opportunities:
            return {'total_value': 0, 'recommended_bets': []}
        
        # Filtra oportunidades recomendadas
        recommended = [opp for opp in opportunities 
                     if opp.recommendation in ['BET', 'STRONG_BET'] and opp.expected_value > 0]
        
        if not recommended:
            return {'total_value': 0, 'recommended_bets': []}
        
        # Calcula valor do portfólio
        portfolio_value = self.value_identifier.calculate_portfolio_value(recommended)
        
        # Análise de diversificação
        diversification = self._analyze_diversification(recommended)
        
        # Análise de risco do portfólio
        portfolio_risk = self._analyze_portfolio_risk(recommended)
        
        return {
            'total_value': portfolio_value['total_value'],
            'recommended_bets': portfolio_value['recommended_bets'],
            'total_bet_amount': portfolio_value['total_bet_amount'],
            'expected_roi': portfolio_value['expected_roi'],
            'diversification': diversification,
            'portfolio_risk': portfolio_risk
        }
    
    def _create_strategic_recommendations(self, value_analysis: ValueAnalysis,
                                        match_analysis: Dict, prob_result: Dict) -> Dict:
        """Cria recomendações estratégicas baseadas na análise de valor"""
        recommendations = []
        
        # Recomendação baseada na melhor oportunidade
        if value_analysis.best_opportunity:
            best = value_analysis.best_opportunity
            recommendations.append({
                'type': 'BEST_VALUE_BET',
                'outcome': best.outcome,
                'expected_value': best.expected_value,
                'recommendation': best.recommendation,
                'reasoning': f"Melhor oportunidade identificada com EV de {best.expected_value:.1%}"
            })
        
        # Recomendação baseada na eficiência do mercado
        if value_analysis.market_efficiency < 0.5:
            recommendations.append({
                'type': 'MARKET_INEFFICIENCY',
                'message': 'Mercado apresenta ineficiências significativas',
                'opportunities': value_analysis.total_opportunities,
                'reasoning': 'Muitas oportunidades de valor encontradas'
            })
        
        # Recomendação baseada na confiança
        if value_analysis.confidence_score > 0.8:
            recommendations.append({
                'type': 'HIGH_CONFIDENCE',
                'message': 'Alta confiança nas predições',
                'confidence': value_analysis.confidence_score,
                'reasoning': 'Modelos apresentam alta concordância'
            })
        
        # Recomendação baseada no contexto da partida
        context = match_analysis.get('match_context', {})
        if context.get('importance', 'normal') == 'high':
            recommendations.append({
                'type': 'HIGH_STAKES_MATCH',
                'message': 'Partida de alta importância',
                'reasoning': 'Maior volatilidade e potencial de valor'
            })
        
        return {
            'recommendations': recommendations,
            'total_recommendations': len(recommendations),
            'priority_level': self._calculate_priority_level(recommendations)
        }
    
    def _analyze_value_risk(self, value_analysis: ValueAnalysis, match_analysis: Dict) -> Dict:
        """Analisa riscos específicos da identificação de valor"""
        risks = []
        risk_score = 0
        
        # Risco baseado na concentração de valor
        if value_analysis.total_opportunities == 1:
            risks.append({
                'type': 'CONCENTRATION_RISK',
                'level': 'HIGH',
                'message': 'Toda a análise concentrada em uma única oportunidade'
            })
            risk_score += 3
        
        # Risco baseado na confiança
        if value_analysis.confidence_score < 0.6:
            risks.append({
                'type': 'LOW_CONFIDENCE_RISK',
                'level': 'MEDIUM',
                'message': 'Baixa confiança nas predições'
            })
            risk_score += 2
        
        # Risco baseado na eficiência do mercado
        if value_analysis.market_efficiency > 0.8:
            risks.append({
                'type': 'EFFICIENT_MARKET_RISK',
                'level': 'LOW',
                'message': 'Mercado muito eficiente, poucas oportunidades'
            })
            risk_score += 1
        
        # Risco baseado no contexto
        context = match_analysis.get('match_context', {})
        if context.get('volatility', 'normal') == 'high':
            risks.append({
                'type': 'HIGH_VOLATILITY_RISK',
                'level': 'MEDIUM',
                'message': 'Partida com alta volatilidade'
            })
            risk_score += 2
        
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
            'total_risks': len(risks)
        }
    
    def _create_value_executive_summary(self, value_analysis: ValueAnalysis,
                                      portfolio_analysis: Dict, strategic_recommendations: Dict,
                                      risk_analysis: Dict) -> Dict:
        """Cria resumo executivo da análise de valor"""
        home_team = value_analysis.match_info.get('home_team', '')
        away_team = value_analysis.match_info.get('away_team', '')
        
        # Resumo das oportunidades
        opportunities_summary = {
            'total': value_analysis.total_opportunities,
            'positive': value_analysis.value_distribution.get('POSITIVE', 0),
            'significant': value_analysis.value_distribution.get('SIGNIFICANT', 0),
            'excellent': value_analysis.value_distribution.get('EXCELLENT', 0)
        }
        
        # Melhor oportunidade
        best_opp = value_analysis.best_opportunity
        best_opportunity_summary = {
            'outcome': best_opp.outcome if best_opp else None,
            'expected_value': best_opp.expected_value if best_opp else 0,
            'recommendation': best_opp.recommendation if best_opp else 'NO_VALUE'
        }
        
        # Insights principais
        insights = []
        
        if value_analysis.highest_ev > 0.1:
            insights.append(f"Excelente oportunidade identificada (EV: {value_analysis.highest_ev:.1%})")
        
        if value_analysis.market_efficiency < 0.5:
            insights.append("Mercado apresenta ineficiências significativas")
        
        if value_analysis.confidence_score > 0.8:
            insights.append("Alta confiança nas predições do modelo")
        
        if risk_analysis['risk_level'] == 'HIGH':
            insights.append("⚠️ Alto risco identificado - considere cautela")
        
        return {
            'match': f"{home_team} vs {away_team}",
            'opportunities_summary': opportunities_summary,
            'best_opportunity': best_opportunity_summary,
            'market_efficiency': value_analysis.market_efficiency,
            'confidence_score': value_analysis.confidence_score,
            'risk_level': risk_analysis['risk_level'],
            'insights': insights,
            'recommendation': self._get_overall_recommendation(value_analysis, risk_analysis)
        }
    
    def _create_market_summary(self, value_analyses: List[Dict], 
                             all_opportunities: List[Dict]) -> Dict:
        """Cria resumo do mercado baseado nas análises"""
        if not value_analyses:
            return {}
        
        # Métricas agregadas
        total_matches = len(value_analyses)
        total_opportunities = len(all_opportunities)
        
        # Distribuição de valor
        value_distribution = {}
        for opp in all_opportunities:
            level = opp['value_level']
            value_distribution[level] = value_distribution.get(level, 0) + 1
        
        # Métricas de EV
        evs = [opp['expected_value'] for opp in all_opportunities]
        avg_ev = np.mean(evs) if evs else 0
        max_ev = max(evs) if evs else 0
        positive_ev_count = len([ev for ev in evs if ev > 0])
        
        # Eficiência do mercado
        market_efficiencies = [analysis['value_analysis']['market_efficiency'] 
                             for analysis in value_analyses]
        avg_efficiency = np.mean(market_efficiencies) if market_efficiencies else 0
        
        return {
            'total_matches_analyzed': total_matches,
            'total_opportunities_found': total_opportunities,
            'opportunities_per_match': total_opportunities / total_matches if total_matches > 0 else 0,
            'value_distribution': value_distribution,
            'average_ev': avg_ev,
            'max_ev': max_ev,
            'positive_ev_percentage': (positive_ev_count / total_opportunities * 100) if total_opportunities > 0 else 0,
            'average_market_efficiency': avg_efficiency,
            'market_condition': 'INEFFICIENT' if avg_efficiency < 0.5 else 'EFFICIENT'
        }
    
    def _generate_market_alerts(self, all_opportunities: List[Dict]) -> List[Dict]:
        """Gera alertas de mercado baseados nas oportunidades"""
        alerts = []
        
        # Filtra oportunidades significativas
        significant_opportunities = [
            opp for opp in all_opportunities 
            if opp['expected_value'] > 0.05 and opp['confidence'] > 0.7
        ]
        
        for opp in significant_opportunities:
            alert = {
                'type': 'VALUE_OPPORTUNITY',
                'match': f"{opp['home_team']} vs {opp['away_team']}",
                'outcome': opp['outcome'],
                'expected_value': opp['expected_value'],
                'value_level': opp['value_level'],
                'recommendation': opp['recommendation'],
                'urgency': 'HIGH' if opp['expected_value'] > 0.1 else 'MEDIUM'
            }
            alerts.append(alert)
        
        # Ordena por EV
        alerts.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return alerts
    
    def _get_top_opportunities(self, all_opportunities: List[Dict], limit: int = 10) -> List[Dict]:
        """Retorna as melhores oportunidades de valor"""
        # Filtra oportunidades com valor positivo
        positive_opportunities = [
            opp for opp in all_opportunities 
            if opp['expected_value'] > 0
        ]
        
        # Ordena por EV
        positive_opportunities.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return positive_opportunities[:limit]
    
    def _analyze_diversification(self, opportunities: List[ValueOpportunity]) -> Dict:
        """Analisa diversificação do portfólio"""
        if not opportunities:
            return {'diversification_score': 0, 'outcomes': []}
        
        # Conta distribuição por resultado
        outcome_counts = {}
        for opp in opportunities:
            outcome = opp.outcome
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
        
        # Calcula score de diversificação
        total_opportunities = len(opportunities)
        max_concentration = max(outcome_counts.values()) if outcome_counts else 0
        diversification_score = 1 - (max_concentration / total_opportunities)
        
        return {
            'diversification_score': diversification_score,
            'outcomes': outcome_counts,
            'max_concentration': max_concentration,
            'concentration_percentage': (max_concentration / total_opportunities * 100) if total_opportunities > 0 else 0
        }
    
    def _analyze_portfolio_risk(self, opportunities: List[ValueOpportunity]) -> Dict:
        """Analisa risco do portfólio"""
        if not opportunities:
            return {'risk_score': 0, 'risk_level': 'LOW'}
        
        # Calcula métricas de risco
        evs = [opp.expected_value for opp in opportunities]
        confidences = [opp.confidence for opp in opportunities]
        
        # Risco baseado na variância do EV
        ev_variance = np.var(evs) if len(evs) > 1 else 0
        ev_risk = min(ev_variance * 10, 1.0)  # Normaliza entre 0 e 1
        
        # Risco baseado na confiança média
        avg_confidence = np.mean(confidences) if confidences else 0
        confidence_risk = 1 - avg_confidence
        
        # Risco baseado na concentração
        total_ev = sum(evs)
        max_ev = max(evs) if evs else 0
        concentration_risk = max_ev / total_ev if total_ev > 0 else 0
        
        # Score de risco total
        risk_score = (ev_risk * 0.4 + confidence_risk * 0.3 + concentration_risk * 0.3)
        
        # Classifica nível de risco
        if risk_score >= 0.7:
            risk_level = 'HIGH'
        elif risk_score >= 0.4:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'ev_risk': ev_risk,
            'confidence_risk': confidence_risk,
            'concentration_risk': concentration_risk
        }
    
    def _calculate_priority_level(self, recommendations: List[Dict]) -> str:
        """Calcula nível de prioridade das recomendações"""
        if not recommendations:
            return 'LOW'
        
        # Conta tipos de recomendação
        high_priority_types = ['BEST_VALUE_BET', 'HIGH_CONFIDENCE']
        medium_priority_types = ['MARKET_INEFFICIENCY', 'HIGH_STAKES_MATCH']
        
        high_count = len([rec for rec in recommendations if rec['type'] in high_priority_types])
        medium_count = len([rec for rec in recommendations if rec['type'] in medium_priority_types])
        
        if high_count > 0:
            return 'HIGH'
        elif medium_count > 0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_overall_recommendation(self, value_analysis: ValueAnalysis, risk_analysis: Dict) -> str:
        """Determina recomendação geral baseada na análise"""
        if not value_analysis.best_opportunity:
            return 'NO_VALUE'
        
        best_ev = value_analysis.best_opportunity.expected_value
        risk_level = risk_analysis['risk_level']
        
        if best_ev > 0.1 and risk_level == 'LOW':
            return 'STRONG_BUY'
        elif best_ev > 0.05 and risk_level in ['LOW', 'MEDIUM']:
            return 'BUY'
        elif best_ev > 0.02:
            return 'CONSIDER'
        else:
            return 'HOLD'
    
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
    
    def _calculate_value_metrics(self, portfolio: List[Dict], initial_capital: float) -> Dict:
        """Calcula métricas específicas do backtesting de valor"""
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
        
        # Métricas de valor
        avg_ev = df['expected_value'].mean() if 'expected_value' in df.columns else 0
        avg_confidence = df['confidence'].mean() if 'confidence' in df.columns else 0
        avg_kelly = df['kelly_percentage'].mean() if 'kelly_percentage' in df.columns else 0
        
        # Análise de precisão do EV
        high_ev_trades = len(df[df['expected_value'] > 0.05]) if 'expected_value' in df.columns else 0
        high_ev_win_rate = len(df[(df['expected_value'] > 0.05) & (df['is_winner'] == True)]) / high_ev_trades if high_ev_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_bet_amount': total_bet_amount,
            'roi': roi,
            'avg_expected_value': avg_ev,
            'avg_confidence': avg_confidence,
            'avg_kelly_percentage': avg_kelly,
            'high_ev_trades': high_ev_trades,
            'high_ev_win_rate': high_ev_win_rate,
            'ev_accuracy': high_ev_win_rate,
            'value_adjusted_roi': roi * avg_confidence if avg_confidence > 0 else roi
        }
    
    def get_value_analytics(self) -> Dict:
        """Retorna analytics do sistema de identificação de valor"""
        if not self.value_history:
            return {'total_analyses': 0}
        
        recent_analyses = self.value_history[-20:]  # Últimas 20
        
        # Estatísticas gerais
        total_analyses = len(self.value_history)
        recent_count = len(recent_analyses)
        
        # Métricas de valor
        all_evs = []
        all_confidences = []
        value_levels = {'NEGATIVE': 0, 'POSITIVE': 0, 'SIGNIFICANT': 0, 'EXCELLENT': 0}
        
        for analysis in recent_analyses:
            if analysis['value_analysis']:
                for opp in analysis['value_analysis'].opportunities:
                    all_evs.append(opp.expected_value)
                    all_confidences.append(opp.confidence)
                    value_levels[opp.value_level.value] += 1
        
        return {
            'total_analyses': total_analyses,
            'recent_analyses': recent_count,
            'average_ev': np.mean(all_evs) if all_evs else 0,
            'max_ev': max(all_evs) if all_evs else 0,
            'average_confidence': np.mean(all_confidences) if all_confidences else 0,
            'value_level_distribution': value_levels,
            'positive_ev_percentage': (value_levels['POSITIVE'] + value_levels['SIGNIFICANT'] + value_levels['EXCELLENT']) / sum(value_levels.values()) * 100 if sum(value_levels.values()) > 0 else 0
        }

if __name__ == "__main__":
    # Teste do sistema de valor
    system = AdvancedValueSystem()
    
    print("=== TESTE DO SISTEMA DE IDENTIFICAÇÃO DE VALOR ===")
    
    # Testa análise de valor
    result = system.analyze_match_value('Flamengo', 'Palmeiras', '2024-01-15')
    
    if result:
        print(f"\nAnálise de Valor:")
        print(f"  Partida: {result['match_info']['home_team']} vs {result['match_info']['away_team']}")
        print(f"  Oportunidades: {result['value_analysis']['total_opportunities']}")
        print(f"  EV médio: {result['value_analysis']['average_ev']:.3f}")
        print(f"  EV máximo: {result['value_analysis']['highest_ev']:.3f}")
        print(f"  Eficiência do mercado: {result['value_analysis']['market_efficiency']:.3f}")
        
        print(f"\nOportunidades Identificadas:")
        for i, opp in enumerate(result['value_analysis']['opportunities'], 1):
            print(f"  {i}. {opp['outcome']}: EV {opp['expected_value']:.3f} - {opp['recommendation']}")
        
        if result['value_analysis']['best_opportunity']:
            best = result['value_analysis']['best_opportunity']
            print(f"\nMelhor Oportunidade:")
            print(f"  {best['outcome']}: EV {best['expected_value']:.3f} - {best['recommendation']}")
        
        print(f"\nResumo Executivo:")
        summary = result['executive_summary']
        print(f"  Recomendação: {summary['recommendation']}")
        print(f"  Nível de risco: {summary['risk_level']}")
        for insight in summary['insights'][:3]:
            print(f"  • {insight}")
    
    print("Teste concluído!")
