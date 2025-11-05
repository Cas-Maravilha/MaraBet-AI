"""
ETAPA 4: IDENTIFICAÇÃO DE VALOR - MaraBet AI
Sistema especializado para identificação de valor nas apostas usando EV
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

class ValueLevel(Enum):
    """Níveis de valor das apostas"""
    NEGATIVE = "NEGATIVE"           # EV <= 0
    POSITIVE = "POSITIVE"           # EV > 0
    SIGNIFICANT = "SIGNIFICANT"     # EV > 0.05 (5%)
    EXCELLENT = "EXCELLENT"         # EV > 0.10 (10%)

@dataclass
class ValueThresholds:
    """Limiares para classificação de valor"""
    positive: float = 0.0           # EV > 0
    significant: float = 0.05       # EV > 5%
    excellent: float = 0.10         # EV > 10%
    
    def get_value_level(self, ev: float) -> ValueLevel:
        """Retorna o nível de valor baseado no EV"""
        if ev <= self.positive:
            return ValueLevel.NEGATIVE
        elif ev <= self.significant:
            return ValueLevel.POSITIVE
        elif ev <= self.excellent:
            return ValueLevel.SIGNIFICANT
        else:
            return ValueLevel.EXCELLENT

@dataclass
class ValueOpportunity:
    """Oportunidade de valor identificada"""
    match_id: str
    home_team: str
    away_team: str
    outcome: str
    market_odds: float
    calculated_odds: float
    probability: float
    expected_value: float
    value_level: ValueLevel
    confidence: float
    kelly_percentage: float
    recommendation: str
    timestamp: datetime
    additional_metrics: Dict

@dataclass
class ValueAnalysis:
    """Análise completa de valor"""
    match_info: Dict
    opportunities: List[ValueOpportunity]
    best_opportunity: Optional[ValueOpportunity]
    total_opportunities: int
    value_distribution: Dict[str, int]
    average_ev: float
    highest_ev: float
    confidence_score: float
    market_efficiency: float

class ValueIdentifier:
    """
    Identificador de Valor em Apostas
    Implementa a fórmula: EV = (Probabilidade Real × Odd) - 1
    """
    
    def __init__(self, thresholds: Optional[ValueThresholds] = None):
        self.thresholds = thresholds or ValueThresholds()
        self.opportunities_history = []
        self.market_data = {}
        
    def calculate_expected_value(self, probability: float, odds: float) -> float:
        """
        Calcula o Valor Esperado (EV) usando a fórmula:
        EV = (Probabilidade Real × Odd) - 1
        """
        if probability <= 0 or odds <= 0:
            return 0.0
        
        ev = (probability * odds) - 1
        return round(ev, 4)
    
    def classify_value_level(self, ev: float) -> ValueLevel:
        """Classifica o nível de valor baseado no EV"""
        return self.thresholds.get_value_level(ev)
    
    def calculate_kelly_criterion(self, probability: float, odds: float) -> float:
        """
        Calcula o Kelly Criterion para sizing da aposta
        Kelly = (bp - q) / b
        onde b = odds - 1, p = probabilidade, q = 1 - p
        """
        if probability <= 0 or odds <= 1:
            return 0.0
        
        b = odds - 1
        p = probability
        q = 1 - p
        
        kelly = (b * p - q) / b
        return max(0, min(kelly, 0.25))  # Limita entre 0 e 25%
    
    def identify_value_opportunities(self, match_data: Dict, 
                                   probabilities: Dict[str, float],
                                   market_odds: Dict[str, float]) -> List[ValueOpportunity]:
        """
        Identifica oportunidades de valor em uma partida
        """
        logger.info(f"Identificando oportunidades de valor: {match_data.get('home_team')} vs {match_data.get('away_team')}")
        
        opportunities = []
        
        for outcome in ['home_win', 'draw', 'away_win']:
            if outcome not in probabilities or outcome not in market_odds:
                continue
            
            probability = probabilities[outcome]
            market_odd = market_odds[outcome]
            
            # Calcula EV
            ev = self.calculate_expected_value(probability, market_odd)
            
            # Classifica nível de valor
            value_level = self.classify_value_level(ev)
            
            # Calcula Kelly Criterion
            kelly = self.calculate_kelly_criterion(probability, market_odd)
            
            # Calcula odds calculadas (baseadas na probabilidade)
            calculated_odds = 1 / probability if probability > 0 else 0
            
            # Determina recomendação
            recommendation = self._determine_recommendation(ev, value_level, kelly)
            
            # Calcula confiança baseada em múltiplos fatores
            confidence = self._calculate_confidence(probability, ev, value_level)
            
            # Cria oportunidade de valor
            opportunity = ValueOpportunity(
                match_id=match_data.get('id', f"match_{datetime.now().timestamp()}"),
                home_team=match_data.get('home_team', ''),
                away_team=match_data.get('away_team', ''),
                outcome=outcome,
                market_odds=market_odd,
                calculated_odds=calculated_odds,
                probability=probability,
                expected_value=ev,
                value_level=value_level,
                confidence=confidence,
                kelly_percentage=kelly,
                recommendation=recommendation,
                timestamp=datetime.now(),
                additional_metrics={
                    'odds_difference': calculated_odds - market_odd,
                    'value_score': ev * 100,  # Score de 0-100
                    'edge_percentage': ev * 100,
                    'implied_probability': 1 / market_odd if market_odd > 0 else 0,
                    'probability_edge': probability - (1 / market_odd) if market_odd > 0 else 0
                }
            )
            
            opportunities.append(opportunity)
        
        # Ordena por EV (maior primeiro)
        opportunities.sort(key=lambda x: x.expected_value, reverse=True)
        
        # Registra no histórico
        self.opportunities_history.extend(opportunities)
        
        return opportunities
    
    def analyze_value_distribution(self, opportunities: List[ValueOpportunity]) -> Dict[str, int]:
        """Analisa distribuição de níveis de valor"""
        distribution = {
            'NEGATIVE': 0,
            'POSITIVE': 0,
            'SIGNIFICANT': 0,
            'EXCELLENT': 0
        }
        
        for opp in opportunities:
            distribution[opp.value_level.value] += 1
        
        return distribution
    
    def find_best_opportunity(self, opportunities: List[ValueOpportunity]) -> Optional[ValueOpportunity]:
        """Encontra a melhor oportunidade de valor"""
        if not opportunities:
            return None
        
        # Filtra apenas oportunidades com valor positivo
        positive_opportunities = [opp for opp in opportunities if opp.expected_value > 0]
        
        if not positive_opportunities:
            return None
        
        # Ordena por EV * confiança (valor esperado ponderado pela confiança)
        best_opportunity = max(positive_opportunities, 
                             key=lambda x: x.expected_value * x.confidence)
        
        return best_opportunity
    
    def calculate_market_efficiency(self, opportunities: List[ValueOpportunity]) -> float:
        """
        Calcula eficiência do mercado baseada na distribuição de valor
        Mercado eficiente = poucas oportunidades de valor
        """
        if not opportunities:
            return 1.0
        
        # Conta oportunidades com valor positivo
        positive_count = len([opp for opp in opportunities if opp.expected_value > 0])
        total_count = len(opportunities)
        
        # Eficiência = 1 - (oportunidades positivas / total)
        efficiency = 1 - (positive_count / total_count)
        
        return round(efficiency, 3)
    
    def create_value_analysis(self, match_data: Dict, 
                            probabilities: Dict[str, float],
                            market_odds: Dict[str, float]) -> ValueAnalysis:
        """
        Cria análise completa de valor para uma partida
        """
        # Identifica oportunidades
        opportunities = self.identify_value_opportunities(match_data, probabilities, market_odds)
        
        # Encontra melhor oportunidade
        best_opportunity = self.find_best_opportunity(opportunities)
        
        # Analisa distribuição
        value_distribution = self.analyze_value_distribution(opportunities)
        
        # Calcula métricas
        total_opportunities = len(opportunities)
        average_ev = np.mean([opp.expected_value for opp in opportunities]) if opportunities else 0
        highest_ev = max([opp.expected_value for opp in opportunities]) if opportunities else 0
        confidence_score = np.mean([opp.confidence for opp in opportunities]) if opportunities else 0
        market_efficiency = self.calculate_market_efficiency(opportunities)
        
        return ValueAnalysis(
            match_info=match_data,
            opportunities=opportunities,
            best_opportunity=best_opportunity,
            total_opportunities=total_opportunities,
            value_distribution=value_distribution,
            average_ev=average_ev,
            highest_ev=highest_ev,
            confidence_score=confidence_score,
            market_efficiency=market_efficiency
        )
    
    def scan_multiple_matches(self, matches_data: List[Dict], 
                            probabilities_data: List[Dict],
                            market_odds_data: List[Dict]) -> List[ValueAnalysis]:
        """
        Escaneia múltiplas partidas em busca de oportunidades de valor
        """
        logger.info(f"Escaneando {len(matches_data)} partidas em busca de valor")
        
        analyses = []
        
        for i, match_data in enumerate(matches_data):
            try:
                probabilities = probabilities_data[i] if i < len(probabilities_data) else {}
                market_odds = market_odds_data[i] if i < len(market_odds_data) else {}
                
                analysis = self.create_value_analysis(match_data, probabilities, market_odds)
                analyses.append(analysis)
                
            except Exception as e:
                logger.error(f"Erro ao analisar partida {i}: {e}")
                continue
        
        return analyses
    
    def get_value_alerts(self, analyses: List[ValueAnalysis], 
                        min_ev: float = 0.05,
                        min_confidence: float = 0.7) -> List[ValueOpportunity]:
        """
        Gera alertas de oportunidades de valor significativas
        """
        alerts = []
        
        for analysis in analyses:
            for opportunity in analysis.opportunities:
                if (opportunity.expected_value >= min_ev and 
                    opportunity.confidence >= min_confidence and
                    opportunity.recommendation in ['BET', 'STRONG_BET']):
                    alerts.append(opportunity)
        
        # Ordena por EV
        alerts.sort(key=lambda x: x.expected_value, reverse=True)
        
        return alerts
    
    def calculate_portfolio_value(self, opportunities: List[ValueOpportunity], 
                                capital: float = 1000) -> Dict:
        """
        Calcula valor do portfólio baseado nas oportunidades identificadas
        """
        if not opportunities:
            return {'total_value': 0, 'recommended_bets': []}
        
        # Filtra apenas oportunidades recomendadas
        recommended = [opp for opp in opportunities 
                     if opp.recommendation in ['BET', 'STRONG_BET'] and opp.expected_value > 0]
        
        if not recommended:
            return {'total_value': 0, 'recommended_bets': []}
        
        # Calcula tamanho das apostas usando Kelly Criterion
        bets = []
        total_value = 0
        
        for opp in recommended:
            # Tamanho da aposta baseado no Kelly Criterion
            bet_size = capital * opp.kelly_percentage
            bet_size = min(bet_size, capital * 0.1)  # Limita a 10% do capital por aposta
            
            if bet_size > 0:
                expected_profit = bet_size * opp.expected_value
                total_value += expected_profit
                
                bets.append({
                    'opportunity': opp,
                    'bet_size': bet_size,
                    'expected_profit': expected_profit,
                    'roi': opp.expected_value * 100
                })
        
        return {
            'total_value': total_value,
            'recommended_bets': bets,
            'total_bet_amount': sum([bet['bet_size'] for bet in bets]),
            'expected_roi': (total_value / sum([bet['bet_size'] for bet in bets]) * 100) if bets else 0
        }
    
    def _determine_recommendation(self, ev: float, value_level: ValueLevel, kelly: float) -> str:
        """Determina recomendação baseada em EV, nível de valor e Kelly"""
        if ev <= 0:
            return 'AVOID'
        elif ev < 0.05:
            return 'CONSIDER'
        elif ev < 0.10:
            if kelly > 0.02:
                return 'BET'
            else:
                return 'CONSIDER'
        else:
            if kelly > 0.03:
                return 'STRONG_BET'
            else:
                return 'BET'
    
    def _calculate_confidence(self, probability: float, ev: float, value_level: ValueLevel) -> float:
        """Calcula confiança baseada em múltiplos fatores"""
        # Confiança baseada na probabilidade (mais próxima de 0.5 = menos confiança)
        prob_confidence = 1 - abs(probability - 0.5) * 2
        
        # Confiança baseada no EV (maior EV = maior confiança)
        ev_confidence = min(ev * 5, 1.0)  # EV de 0.2 = confiança máxima
        
        # Confiança baseada no nível de valor
        level_confidence = {
            ValueLevel.NEGATIVE: 0.0,
            ValueLevel.POSITIVE: 0.3,
            ValueLevel.SIGNIFICANT: 0.7,
            ValueLevel.EXCELLENT: 1.0
        }[value_level]
        
        # Combina fatores
        total_confidence = (prob_confidence * 0.3 + ev_confidence * 0.4 + level_confidence * 0.3)
        
        return min(max(total_confidence, 0.0), 1.0)
    
    def get_value_statistics(self) -> Dict:
        """Retorna estatísticas do sistema de identificação de valor"""
        if not self.opportunities_history:
            return {'total_opportunities': 0}
        
        recent_opportunities = self.opportunities_history[-100:]  # Últimas 100
        
        # Estatísticas gerais
        total_opportunities = len(self.opportunities_history)
        recent_count = len(recent_opportunities)
        
        # Distribuição de níveis
        level_distribution = self.analyze_value_distribution(recent_opportunities)
        
        # Métricas de EV
        evs = [opp.expected_value for opp in recent_opportunities]
        avg_ev = np.mean(evs) if evs else 0
        max_ev = max(evs) if evs else 0
        positive_ev_count = len([ev for ev in evs if ev > 0])
        
        # Métricas de confiança
        confidences = [opp.confidence for opp in recent_opportunities]
        avg_confidence = np.mean(confidences) if confidences else 0
        
        return {
            'total_opportunities': total_opportunities,
            'recent_opportunities': recent_count,
            'level_distribution': level_distribution,
            'average_ev': avg_ev,
            'max_ev': max_ev,
            'positive_ev_count': positive_ev_count,
            'positive_ev_percentage': (positive_ev_count / recent_count * 100) if recent_count > 0 else 0,
            'average_confidence': avg_confidence,
            'thresholds_used': {
                'positive': self.thresholds.positive,
                'significant': self.thresholds.significant,
                'excellent': self.thresholds.excellent
            }
        }

if __name__ == "__main__":
    # Teste do identificador de valor
    print("=== TESTE DO IDENTIFICADOR DE VALOR ===")
    
    identifier = ValueIdentifier()
    
    # Dados de teste
    match_data = {
        'id': 'test_match_1',
        'home_team': 'Flamengo',
        'away_team': 'Palmeiras',
        'date': '2024-01-15'
    }
    
    probabilities = {
        'home_win': 0.45,
        'draw': 0.30,
        'away_win': 0.25
    }
    
    market_odds = {
        'home_win': 2.20,  # Mercado subestima Flamengo
        'draw': 3.10,
        'away_win': 3.50
    }
    
    # Cria análise de valor
    analysis = identifier.create_value_analysis(match_data, probabilities, market_odds)
    
    print(f"\nAnálise de Valor - {match_data['home_team']} vs {match_data['away_team']}")
    print(f"Total de oportunidades: {analysis.total_opportunities}")
    print(f"EV médio: {analysis.average_ev:.3f}")
    print(f"EV máximo: {analysis.highest_ev:.3f}")
    print(f"Confiança média: {analysis.confidence_score:.3f}")
    print(f"Eficiência do mercado: {analysis.market_efficiency:.3f}")
    
    print(f"\nDistribuição de Valor:")
    for level, count in analysis.value_distribution.items():
        print(f"  {level}: {count}")
    
    print(f"\nOportunidades Identificadas:")
    for i, opp in enumerate(analysis.opportunities, 1):
        print(f"\n  {i}. {opp.outcome.upper()}:")
        print(f"     Probabilidade: {opp.probability:.3f}")
        print(f"     Odds do mercado: {opp.market_odds:.2f}")
        print(f"     Odds calculadas: {opp.calculated_odds:.2f}")
        print(f"     EV: {opp.expected_value:.3f} ({opp.expected_value*100:.1f}%)")
        print(f"     Nível: {opp.value_level.value}")
        print(f"     Kelly: {opp.kelly_percentage:.1%}")
        print(f"     Confiança: {opp.confidence:.3f}")
        print(f"     Recomendação: {opp.recommendation}")
    
    if analysis.best_opportunity:
        print(f"\nMelhor Oportunidade:")
        best = analysis.best_opportunity
        print(f"  {best.outcome}: EV {best.expected_value:.3f} ({best.expected_value*100:.1f}%)")
        print(f"  Recomendação: {best.recommendation}")
        print(f"  Kelly: {best.kelly_percentage:.1%}")
    
    # Testa alertas
    print(f"\nAlertas de Valor (EV > 5%, Confiança > 70%):")
    alerts = identifier.get_value_alerts([analysis], min_ev=0.05, min_confidence=0.7)
    
    if alerts:
        for alert in alerts:
            print(f"  {alert.outcome}: EV {alert.expected_value:.3f} - {alert.recommendation}")
    else:
        print("  Nenhum alerta de valor significativo encontrado")
    
    # Estatísticas
    print(f"\nEstatísticas do Sistema:")
    stats = identifier.get_value_statistics()
    print(f"  Total de oportunidades: {stats['total_opportunities']}")
    print(f"  EV médio: {stats['average_ev']:.3f}")
    print(f"  Oportunidades positivas: {stats['positive_ev_percentage']:.1f}%")
    print(f"  Confiança média: {stats['average_confidence']:.3f}")
    
    print("\nTeste concluído!")
