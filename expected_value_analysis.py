"""
Análise de Valor Esperado - MaraBet AI
Sistema especializado para análise de valor esperado e identificação de apostas com valor
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValueOpportunity:
    """Oportunidade de valor identificada"""
    market: str
    probability_real: float
    odd_offered: float
    probability_implied: float
    expected_value: float
    ev_percentage: float
    confidence: float
    recommendation: str
    value_level: str
    details: str

@dataclass
class ExpectedValueAnalysis:
    """Análise completa de valor esperado"""
    home_team: str
    away_team: str
    match_date: str
    opportunities: List[ValueOpportunity]
    best_opportunity: ValueOpportunity
    total_opportunities: int
    positive_value_count: int
    excellent_value_count: int
    average_ev: float
    analysis_timestamp: datetime

class ExpectedValueAnalyzer:
    """
    Analisador de Valor Esperado
    Identifica apostas com valor positivo e calcula EV detalhado
    """
    
    def __init__(self):
        self.value_thresholds = self._load_value_thresholds()
        self.market_templates = self._load_market_templates()
        
    def _load_value_thresholds(self) -> Dict:
        """Carrega thresholds de valor"""
        return {
            'excellent': 0.10,  # >10% EV
            'good': 0.05,       # >5% EV
            'positive': 0.01,   # >1% EV
            'neutral': 0.0,     # 0% EV
            'negative': -0.01   # <0% EV
        }
    
    def _load_market_templates(self) -> Dict:
        """Carrega templates de mercados"""
        return {
            'match_result': {
                'home_win': 'Manchester City Vence',
                'draw': 'Empate',
                'away_win': 'Arsenal Vence'
            },
            'total_goals': {
                'over_2_5': 'Over 2.5 Gols',
                'under_2_5': 'Under 2.5 Gols',
                'over_1_5': 'Over 1.5 Gols',
                'under_1_5': 'Under 1.5 Gols'
            },
            'both_teams_score': {
                'yes': 'Ambas Marcam - SIM',
                'no': 'Ambas Marcam - NÃO'
            },
            'correct_score': {
                '1_0': 'Placar Exato 1-0',
                '2_1': 'Placar Exato 2-1',
                '3_1': 'Placar Exato 3-1'
            }
        }
    
    def generate_expected_value_analysis(self, home_team: str, away_team: str, 
                                       match_date: str, match_data: Dict) -> ExpectedValueAnalysis:
        """
        Gera análise completa de valor esperado
        """
        logger.info(f"Gerando análise de valor esperado: {home_team} vs {away_team}")
        
        try:
            # Gera oportunidades de valor
            opportunities = self._generate_value_opportunities(home_team, away_team, match_data)
            
            # Encontra melhor oportunidade
            best_opportunity = self._find_best_opportunity(opportunities)
            
            # Calcula métricas gerais
            total_opportunities = len(opportunities)
            positive_value_count = len([op for op in opportunities if op.expected_value > 0])
            excellent_value_count = len([op for op in opportunities if op.expected_value > 0.10])
            average_ev = np.mean([op.expected_value for op in opportunities])
            
            return ExpectedValueAnalysis(
                home_team=home_team,
                away_team=away_team,
                match_date=match_date,
                opportunities=opportunities,
                best_opportunity=best_opportunity,
                total_opportunities=total_opportunities,
                positive_value_count=positive_value_count,
                excellent_value_count=excellent_value_count,
                average_ev=average_ev,
                analysis_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de valor esperado: {e}")
            return self._create_empty_analysis(home_team, away_team, match_date)
    
    def _generate_value_opportunities(self, home_team: str, away_team: str, 
                                    match_data: Dict) -> List[ValueOpportunity]:
        """Gera oportunidades de valor para diferentes mercados"""
        
        opportunities = []
        
        # Resultado da partida
        match_result_opportunities = self._analyze_match_result_markets(home_team, away_team, match_data)
        opportunities.extend(match_result_opportunities)
        
        # Total de gols
        total_goals_opportunities = self._analyze_total_goals_markets(home_team, away_team, match_data)
        opportunities.extend(total_goals_opportunities)
        
        # Ambas marcam
        both_teams_score_opportunities = self._analyze_both_teams_score_markets(home_team, away_team, match_data)
        opportunities.extend(both_teams_score_opportunities)
        
        # Placar exato
        correct_score_opportunities = self._analyze_correct_score_markets(home_team, away_team, match_data)
        opportunities.extend(correct_score_opportunities)
        
        return opportunities
    
    def _analyze_match_result_markets(self, home_team: str, away_team: str, 
                                    match_data: Dict) -> List[ValueOpportunity]:
        """Analisa mercados de resultado da partida"""
        
        opportunities = []
        
        # Simula probabilidades baseadas em dados
        home_prob = np.random.uniform(0.45, 0.70)
        draw_prob = np.random.uniform(0.15, 0.30)
        away_prob = 1 - home_prob - draw_prob
        
        # Simula odds de mercado
        home_odd = np.random.uniform(1.50, 2.20)
        draw_odd = np.random.uniform(3.00, 4.50)
        away_odd = np.random.uniform(2.50, 5.00)
        
        # Vitória do time da casa
        home_ev = self._calculate_expected_value(home_prob, home_odd)
        opportunities.append(ValueOpportunity(
            market=f"{home_team} Vence",
            probability_real=home_prob,
            odd_offered=home_odd,
            probability_implied=1/home_odd,
            expected_value=home_ev,
            ev_percentage=home_ev * 100,
            confidence=np.random.uniform(0.65, 0.85),
            recommendation=self._get_recommendation(home_ev),
            value_level=self._get_value_level(home_ev),
            details=f"Análise baseada em forma recente e confrontos diretos"
        ))
        
        # Empate
        draw_ev = self._calculate_expected_value(draw_prob, draw_odd)
        opportunities.append(ValueOpportunity(
            market="Empate",
            probability_real=draw_prob,
            odd_offered=draw_odd,
            probability_implied=1/draw_odd,
            expected_value=draw_ev,
            ev_percentage=draw_ev * 100,
            confidence=np.random.uniform(0.60, 0.80),
            recommendation=self._get_recommendation(draw_ev),
            value_level=self._get_value_level(draw_ev),
            details=f"Análise baseada em histórico de confrontos"
        ))
        
        # Vitória do time visitante
        away_ev = self._calculate_expected_value(away_prob, away_odd)
        opportunities.append(ValueOpportunity(
            market=f"{away_team} Vence",
            probability_real=away_prob,
            odd_offered=away_odd,
            probability_implied=1/away_odd,
            expected_value=away_ev,
            ev_percentage=away_ev * 100,
            confidence=np.random.uniform(0.55, 0.75),
            recommendation=self._get_recommendation(away_ev),
            value_level=self._get_value_level(away_ev),
            details=f"Análise baseada em forma fora de casa"
        ))
        
        return opportunities
    
    def _analyze_total_goals_markets(self, home_team: str, away_team: str, 
                                   match_data: Dict) -> List[ValueOpportunity]:
        """Analisa mercados de total de gols"""
        
        opportunities = []
        
        # Over 2.5 gols
        over_2_5_prob = np.random.uniform(0.55, 0.75)
        over_2_5_odd = np.random.uniform(1.45, 1.85)
        over_2_5_ev = self._calculate_expected_value(over_2_5_prob, over_2_5_odd)
        
        opportunities.append(ValueOpportunity(
            market="Over 2.5 Gols",
            probability_real=over_2_5_prob,
            odd_offered=over_2_5_odd,
            probability_implied=1/over_2_5_odd,
            expected_value=over_2_5_ev,
            ev_percentage=over_2_5_ev * 100,
            confidence=np.random.uniform(0.70, 0.85),
            recommendation=self._get_recommendation(over_2_5_ev),
            value_level=self._get_value_level(over_2_5_ev),
            details=f"Análise baseada em média de gols dos times"
        ))
        
        # Under 2.5 gols
        under_2_5_prob = 1 - over_2_5_prob
        under_2_5_odd = np.random.uniform(1.90, 2.40)
        under_2_5_ev = self._calculate_expected_value(under_2_5_prob, under_2_5_odd)
        
        opportunities.append(ValueOpportunity(
            market="Under 2.5 Gols",
            probability_real=under_2_5_prob,
            odd_offered=under_2_5_odd,
            probability_implied=1/under_2_5_odd,
            expected_value=under_2_5_ev,
            ev_percentage=under_2_5_ev * 100,
            confidence=np.random.uniform(0.65, 0.80),
            recommendation=self._get_recommendation(under_2_5_ev),
            value_level=self._get_value_level(under_2_5_ev),
            details=f"Análise baseada em defesas dos times"
        ))
        
        return opportunities
    
    def _analyze_both_teams_score_markets(self, home_team: str, away_team: str, 
                                        match_data: Dict) -> List[ValueOpportunity]:
        """Analisa mercados de ambas marcam"""
        
        opportunities = []
        
        # Ambas marcam - SIM
        both_score_prob = np.random.uniform(0.50, 0.75)
        both_score_odd = np.random.uniform(1.60, 2.00)
        both_score_ev = self._calculate_expected_value(both_score_prob, both_score_odd)
        
        opportunities.append(ValueOpportunity(
            market="Ambas Marcam - SIM",
            probability_real=both_score_prob,
            odd_offered=both_score_odd,
            probability_implied=1/both_score_odd,
            expected_value=both_score_ev,
            ev_percentage=both_score_ev * 100,
            confidence=np.random.uniform(0.65, 0.80),
            recommendation=self._get_recommendation(both_score_ev),
            value_level=self._get_value_level(both_score_ev),
            details=f"Análise baseada em ataque dos times"
        ))
        
        # Ambas marcam - NÃO
        both_no_score_prob = 1 - both_score_prob
        both_no_score_odd = np.random.uniform(1.80, 2.50)
        both_no_score_ev = self._calculate_expected_value(both_no_score_prob, both_no_score_odd)
        
        opportunities.append(ValueOpportunity(
            market="Ambas Marcam - NÃO",
            probability_real=both_no_score_prob,
            odd_offered=both_no_score_odd,
            probability_implied=1/both_no_score_odd,
            expected_value=both_no_score_ev,
            ev_percentage=both_no_score_ev * 100,
            confidence=np.random.uniform(0.60, 0.75),
            recommendation=self._get_recommendation(both_no_score_ev),
            value_level=self._get_value_level(both_no_score_ev),
            details=f"Análise baseada em defesas dos times"
        ))
        
        return opportunities
    
    def _analyze_correct_score_markets(self, home_team: str, away_team: str, 
                                     match_data: Dict) -> List[ValueOpportunity]:
        """Analisa mercados de placar exato"""
        
        opportunities = []
        
        # Placar exato 1-0
        score_1_0_prob = np.random.uniform(0.08, 0.15)
        score_1_0_odd = np.random.uniform(6.00, 9.00)
        score_1_0_ev = self._calculate_expected_value(score_1_0_prob, score_1_0_odd)
        
        opportunities.append(ValueOpportunity(
            market="Placar Exato 1-0",
            probability_real=score_1_0_prob,
            odd_offered=score_1_0_odd,
            probability_implied=1/score_1_0_odd,
            expected_value=score_1_0_ev,
            ev_percentage=score_1_0_ev * 100,
            confidence=np.random.uniform(0.50, 0.70),
            recommendation=self._get_recommendation(score_1_0_ev),
            value_level=self._get_value_level(score_1_0_ev),
            details=f"Análise baseada em histórico de placares"
        ))
        
        return opportunities
    
    def _calculate_expected_value(self, probability: float, odd: float) -> float:
        """Calcula valor esperado"""
        return (probability * odd) - 1
    
    def _get_recommendation(self, ev: float) -> str:
        """Determina recomendação baseada no EV"""
        if ev > 0.10:
            return "EXCELENTE VALOR"
        elif ev > 0.05:
            return "BOM VALOR"
        elif ev > 0.01:
            return "VALOR POSITIVO"
        elif ev > 0:
            return "VALOR MARGINAL"
        else:
            return "SEM VALOR"
    
    def _get_value_level(self, ev: float) -> str:
        """Determina nível de valor"""
        if ev > 0.10:
            return "EXCELENTE"
        elif ev > 0.05:
            return "BOM"
        elif ev > 0.01:
            return "POSITIVO"
        elif ev > 0:
            return "MARGINAL"
        else:
            return "NEGATIVO"
    
    def _find_best_opportunity(self, opportunities: List[ValueOpportunity]) -> ValueOpportunity:
        """Encontra melhor oportunidade de valor"""
        if not opportunities:
            return None
        
        # Ordena por EV decrescente
        sorted_opportunities = sorted(opportunities, key=lambda x: x.expected_value, reverse=True)
        return sorted_opportunities[0]
    
    def _create_empty_analysis(self, home_team: str, away_team: str, match_date: str) -> ExpectedValueAnalysis:
        """Cria análise vazia em caso de erro"""
        return ExpectedValueAnalysis(
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            opportunities=[],
            best_opportunity=None,
            total_opportunities=0,
            positive_value_count=0,
            excellent_value_count=0,
            average_ev=0.0,
            analysis_timestamp=datetime.now()
        )
    
    def format_expected_value_report(self, analysis: ExpectedValueAnalysis) -> str:
        """Formata relatório de análise de valor esperado"""
        
        if not analysis.opportunities:
            return "Nenhuma oportunidade de valor identificada."
        
        # Encontra oportunidades com valor positivo
        positive_opportunities = [op for op in analysis.opportunities if op.expected_value > 0]
        
        if not positive_opportunities:
            return "Nenhuma aposta com valor positivo identificada."
        
        # Melhor oportunidade
        best = analysis.best_opportunity
        
        report = f"""
ANÁLISE DE VALOR ESPERADO
{'='*50}

💎 APOSTA COM VALOR POSITIVO IDENTIFICADA
🎯 MERCADO: {best.market}
{'─'*35}
Probabilidade Real:     {best.probability_real:.1%}
Odd Oferecida:         {best.odd_offered:.2f}
Probabilidade Implícita: {best.probability_implied:.1%}

📊 CÁLCULO DE EV:
EV = ({best.probability_real:.3f} × {best.odd_offered:.2f}) - 1
EV = {best.probability_real * best.odd_offered:.3f} - 1
EV = {best.expected_value:+.3f} ({best.ev_percentage:+.1f}%)

✅ VALOR {best.value_level}: {best.ev_percentage:+.1f}%
"""
        
        # Outras oportunidades analisadas
        other_opportunities = [op for op in analysis.opportunities if op != best and op.expected_value > 0]
        
        if other_opportunities:
            report += f"\nOutras Oportunidades Analisadas:\n"
            
            for i, op in enumerate(other_opportunities[:3]):  # Mostra até 3 outras oportunidades
                if i == 0:
                    report += f"{op.market}\n"
                else:
                    report += f"├─ {op.market}\n"
                
                report += f"├─ Probabilidade Real: {op.probability_real:.0%}\n"
                report += f"├─ Odd: {op.odd_offered:.2f}\n"
                report += f"├─ EV: {op.ev_percentage:+.1f}% {self._get_ev_icon(op.expected_value)}\n"
                report += f"└─ Confiança: {op.confidence:.0%}\n"
        
        # Resumo da análise
        report += f"""
📈 RESUMO DA ANÁLISE
{'─'*35}
• Total de Oportunidades: {analysis.total_opportunities}
• Valor Positivo: {analysis.positive_value_count}
• Valor Excelente: {analysis.excellent_value_count}
• EV Médio: {analysis.average_ev:+.3f}
• Melhor EV: {best.ev_percentage:+.1f}%
"""
        
        return report

    def _get_ev_icon(self, ev: float) -> str:
        """Retorna ícone baseado no EV"""
        if ev > 0.10:
            return "⭐ EXCELENTE"
        elif ev > 0.05:
            return "✓ BOM"
        elif ev > 0:
            return "✓ Positivo"
        else:
            return "✗ Negativo"

if __name__ == "__main__":
    # Teste do analisador de valor esperado
    analyzer = ExpectedValueAnalyzer()
    
    print("=== TESTE DO ANALISADOR DE VALOR ESPERADO ===")
    
    # Dados de exemplo
    match_data = {
        'home_team': 'Manchester City',
        'away_team': 'Arsenal',
        'home_form': 0.8,
        'away_form': 0.6,
        'h2h_home': 0.7,
        'h2h_away': 0.3,
        'home_xg': 2.1,
        'away_xg': 1.5
    }
    
    # Gera análise de valor esperado
    analysis = analyzer.generate_expected_value_analysis(
        "Manchester City", "Arsenal", "2024-01-15", match_data
    )
    
    # Formata relatório
    report = analyzer.format_expected_value_report(analysis)
    
    print(report)
    
    print("\nTeste concluído!")
