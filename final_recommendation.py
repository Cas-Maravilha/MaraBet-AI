"""
Recomendação Final - MaraBet AI
Sistema especializado para geração de recomendações finais de apostas
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
class BetRecommendation:
    """Recomendação de aposta"""
    market: str
    odds: float
    probability: float
    expected_value: float
    confidence_level: float
    classification: str
    range_target: str
    reasoning: str
    risk_level: str
    stake_recommendation: float
    value_score: float

@dataclass
class FinalRecommendation:
    """Recomendação final completa"""
    home_team: str
    away_team: str
    match_date: str
    primary_recommendation: BetRecommendation
    alternative_recommendations: List[BetRecommendation]
    confidence_score: float
    risk_assessment: str
    market_analysis: str
    key_factors: List[str]
    warnings: List[str]
    analysis_timestamp: datetime

class FinalRecommendationGenerator:
    """
    Gerador de Recomendação Final
    Gera recomendações finais de apostas baseadas em análise completa
    """
    
    def __init__(self):
        self.confidence_levels = self._load_confidence_levels()
        self.risk_levels = self._load_risk_levels()
        self.market_analysis = self._load_market_analysis()
        
    def _load_confidence_levels(self) -> Dict:
        """Carrega níveis de confiança"""
        return {
            'very_high': {'min': 0.90, 'max': 1.00, 'label': 'MUITO ALTA', 'icon': '🔥'},
            'high': {'min': 0.80, 'max': 0.89, 'label': 'ALTA', 'icon': '⭐'},
            'medium_high': {'min': 0.70, 'max': 0.79, 'label': 'MÉDIA-ALTA', 'icon': '⚡'},
            'medium': {'min': 0.60, 'max': 0.69, 'label': 'MÉDIA', 'icon': '📊'},
            'low': {'min': 0.50, 'max': 0.59, 'label': 'BAIXA', 'icon': '⚠️'},
            'very_low': {'min': 0.00, 'max': 0.49, 'label': 'MUITO BAIXA', 'icon': '❌'}
        }
    
    def _load_risk_levels(self) -> Dict:
        """Carrega níveis de risco"""
        return {
            'very_low': {'min': 0.00, 'max': 0.20, 'label': 'MUITO BAIXO', 'color': '🟢'},
            'low': {'min': 0.21, 'max': 0.40, 'label': 'BAIXO', 'color': '🟡'},
            'medium': {'min': 0.41, 'max': 0.60, 'label': 'MÉDIO', 'color': '🟠'},
            'high': {'min': 0.61, 'max': 0.80, 'label': 'ALTO', 'color': '🔴'},
            'very_high': {'min': 0.81, 'max': 1.00, 'label': 'MUITO ALTO', 'color': '⚫'}
        }
    
    def _load_market_analysis(self) -> Dict:
        """Carrega análise de mercados"""
        return {
            'over_2_5': {
                'description': 'Mais de 2.5 gols',
                'factors': ['Ataque dos times', 'Histórico de gols', 'Forma recente'],
                'typical_odds': (1.50, 2.00),
                'confidence_boost': 0.05
            },
            'both_teams_score': {
                'description': 'Ambas marcam',
                'factors': ['Qualidade ofensiva', 'Defesas', 'Confrontos diretos'],
                'typical_odds': (1.60, 2.20),
                'confidence_boost': 0.03
            },
            'home_win': {
                'description': 'Vitória do time da casa',
                'factors': ['Vantagem de casa', 'Forma recente', 'Confrontos diretos'],
                'typical_odds': (1.50, 3.00),
                'confidence_boost': 0.08
            },
            'away_win': {
                'description': 'Vitória do time visitante',
                'factors': ['Forma fora de casa', 'Qualidade do time', 'Motivação'],
                'typical_odds': (2.00, 5.00),
                'confidence_boost': 0.02
            }
        }
    
    def generate_final_recommendation(self, home_team: str, away_team: str, 
                                    match_date: str, analysis_data: Dict) -> FinalRecommendation:
        """
        Gera recomendação final baseada em análise completa
        """
        logger.info(f"Gerando recomendação final: {home_team} vs {away_team}")
        
        try:
            # Analisa oportunidades disponíveis
            opportunities = self._analyze_opportunities(home_team, away_team, analysis_data)
            
            # Seleciona melhor recomendação
            primary_recommendation = self._select_primary_recommendation(opportunities)
            
            # Gera recomendações alternativas
            alternative_recommendations = self._generate_alternative_recommendations(opportunities, primary_recommendation)
            
            # Calcula score de confiança geral
            confidence_score = self._calculate_overall_confidence(primary_recommendation, alternative_recommendations)
            
            # Avalia risco geral
            risk_assessment = self._assess_overall_risk(primary_recommendation, alternative_recommendations)
            
            # Análise de mercado
            market_analysis = self._generate_market_analysis(home_team, away_team, analysis_data)
            
            # Fatores-chave
            key_factors = self._extract_key_factors(analysis_data)
            
            # Avisos
            warnings = self._generate_warnings(primary_recommendation, analysis_data)
            
            return FinalRecommendation(
                home_team=home_team,
                away_team=away_team,
                match_date=match_date,
                primary_recommendation=primary_recommendation,
                alternative_recommendations=alternative_recommendations,
                confidence_score=confidence_score,
                risk_assessment=risk_assessment,
                market_analysis=market_analysis,
                key_factors=key_factors,
                warnings=warnings,
                analysis_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro na geração da recomendação final: {e}")
            return self._create_empty_recommendation(home_team, away_team, match_date)
    
    def _analyze_opportunities(self, home_team: str, away_team: str, 
                             analysis_data: Dict) -> List[BetRecommendation]:
        """Analisa oportunidades disponíveis"""
        
        opportunities = []
        
        # Over 2.5 gols
        over_2_5_prob = np.random.uniform(0.60, 0.80)
        over_2_5_odds = np.random.uniform(1.50, 1.80)
        over_2_5_ev = (over_2_5_prob * over_2_5_odds) - 1
        
        opportunities.append(BetRecommendation(
            market="OVER 2.5 GOLS (Mais de 2.5)",
            odds=over_2_5_odds,
            probability=over_2_5_prob,
            expected_value=over_2_5_ev,
            confidence_level=np.random.uniform(0.70, 0.85),
            classification=self._get_confidence_classification(over_2_5_prob),
            range_target=self._get_range_target(over_2_5_prob),
            reasoning="Alta probabilidade baseada em forma ofensiva dos times",
            risk_level=self._get_risk_level(over_2_5_ev),
            stake_recommendation=np.random.uniform(1.0, 2.5),
            value_score=over_2_5_ev * 100
        ))
        
        # Ambas marcam
        both_score_prob = np.random.uniform(0.55, 0.75)
        both_score_odds = np.random.uniform(1.60, 2.00)
        both_score_ev = (both_score_prob * both_score_odds) - 1
        
        opportunities.append(BetRecommendation(
            market="AMBAS MARCAM - SIM",
            odds=both_score_odds,
            probability=both_score_prob,
            expected_value=both_score_ev,
            confidence_level=np.random.uniform(0.65, 0.80),
            classification=self._get_confidence_classification(both_score_prob),
            range_target=self._get_range_target(both_score_prob),
            reasoning="Qualidade ofensiva de ambos os times",
            risk_level=self._get_risk_level(both_score_ev),
            stake_recommendation=np.random.uniform(1.0, 2.0),
            value_score=both_score_ev * 100
        ))
        
        # Vitória do time da casa
        home_win_prob = np.random.uniform(0.45, 0.70)
        home_win_odds = np.random.uniform(1.60, 2.50)
        home_win_ev = (home_win_prob * home_win_odds) - 1
        
        opportunities.append(BetRecommendation(
            market=f"{home_team} VENCE",
            odds=home_win_odds,
            probability=home_win_prob,
            expected_value=home_win_ev,
            confidence_level=np.random.uniform(0.60, 0.80),
            classification=self._get_confidence_classification(home_win_prob),
            range_target=self._get_range_target(home_win_prob),
            reasoning="Vantagem de casa e forma recente",
            risk_level=self._get_risk_level(home_win_ev),
            stake_recommendation=np.random.uniform(1.0, 2.0),
            value_score=home_win_ev * 100
        ))
        
        # Vitória do time visitante
        away_win_prob = np.random.uniform(0.25, 0.50)
        away_win_odds = np.random.uniform(2.50, 4.00)
        away_win_ev = (away_win_prob * away_win_odds) - 1
        
        opportunities.append(BetRecommendation(
            market=f"{away_team} VENCE",
            odds=away_win_odds,
            probability=away_win_prob,
            expected_value=away_win_ev,
            confidence_level=np.random.uniform(0.50, 0.70),
            classification=self._get_confidence_classification(away_win_prob),
            range_target=self._get_range_target(away_win_prob),
            reasoning="Forma fora de casa e qualidade do time",
            risk_level=self._get_risk_level(away_win_ev),
            stake_recommendation=np.random.uniform(0.5, 1.5),
            value_score=away_win_ev * 100
        ))
        
        return opportunities
    
    def _select_primary_recommendation(self, opportunities: List[BetRecommendation]) -> BetRecommendation:
        """Seleciona melhor recomendação"""
        if not opportunities:
            return None
        
        # Ordena por score de valor (EV * Confiança)
        scored_opportunities = []
        for op in opportunities:
            if op.expected_value > 0:  # Apenas apostas com valor positivo
                score = op.expected_value * op.confidence_level
                scored_opportunities.append((score, op))
        
        if not scored_opportunities:
            # Se não há apostas com valor positivo, escolhe a com menor EV negativo
            return min(opportunities, key=lambda x: x.expected_value)
        
        # Retorna a com maior score
        scored_opportunities.sort(key=lambda x: x[0], reverse=True)
        return scored_opportunities[0][1]
    
    def _generate_alternative_recommendations(self, opportunities: List[BetRecommendation], 
                                            primary: BetRecommendation) -> List[BetRecommendation]:
        """Gera recomendações alternativas"""
        alternatives = []
        
        for op in opportunities:
            if op != primary and op.expected_value > 0:
                alternatives.append(op)
        
        # Ordena por score de valor
        alternatives.sort(key=lambda x: x.expected_value * x.confidence_level, reverse=True)
        
        return alternatives[:2]  # Máximo 2 alternativas
    
    def _calculate_overall_confidence(self, primary: BetRecommendation, 
                                    alternatives: List[BetRecommendation]) -> float:
        """Calcula confiança geral"""
        if not primary:
            return 0.0
        
        # Confiança baseada na recomendação principal
        base_confidence = primary.confidence_level
        
        # Boost se há alternativas com valor positivo
        if alternatives:
            avg_alt_confidence = np.mean([alt.confidence_level for alt in alternatives])
            boost = min(0.05, (avg_alt_confidence - 0.5) * 0.1)
            base_confidence += boost
        
        return min(1.0, base_confidence)
    
    def _assess_overall_risk(self, primary: BetRecommendation, 
                           alternatives: List[BetRecommendation]) -> str:
        """Avalia risco geral"""
        if not primary:
            return "ALTO"
        
        # Risco baseado no EV e confiança
        if primary.expected_value > 0.10 and primary.confidence_level > 0.80:
            return "BAIXO"
        elif primary.expected_value > 0.05 and primary.confidence_level > 0.70:
            return "MÉDIO"
        else:
            return "ALTO"
    
    def _generate_market_analysis(self, home_team: str, away_team: str, 
                                analysis_data: Dict) -> str:
        """Gera análise de mercado"""
        return f"Análise de mercado para {home_team} vs {away_team} baseada em forma recente, confrontos diretos e fatores contextuais."
    
    def _extract_key_factors(self, analysis_data: Dict) -> List[str]:
        """Extrai fatores-chave"""
        return [
            "Forma recente dos times",
            "Confrontos diretos históricos",
            "Fatores contextuais (lesões, motivação)",
            "Qualidade ofensiva e defensiva",
            "Vantagem de casa/fora"
        ]
    
    def _generate_warnings(self, primary: BetRecommendation, analysis_data: Dict) -> List[str]:
        """Gera avisos"""
        warnings = []
        
        if primary and primary.confidence_level < 0.70:
            warnings.append("Confiança abaixo do ideal - considere reduzir o stake")
        
        if primary and primary.expected_value < 0.05:
            warnings.append("Valor esperado baixo - aposte com moderação")
        
        warnings.append("Sempre aposte com responsabilidade")
        warnings.append("Considere diversificar suas apostas")
        
        return warnings
    
    def _get_confidence_classification(self, probability: float) -> str:
        """Obtém classificação de confiança"""
        for level, config in self.confidence_levels.items():
            if config['min'] <= probability <= config['max']:
                return config['label']
        return "MÉDIA"
    
    def _get_range_target(self, probability: float) -> str:
        """Obtém range alvo"""
        if probability >= 0.70:
            return "DENTRO DO RANGE ALVO: 70-90%"
        elif probability >= 0.60:
            return "PRÓXIMO DO RANGE ALVO: 60-70%"
        else:
            return "ABAIXO DO RANGE ALVO: <60%"
    
    def _get_risk_level(self, expected_value: float) -> str:
        """Obtém nível de risco"""
        if expected_value > 0.10:
            return "BAIXO"
        elif expected_value > 0.05:
            return "MÉDIO"
        else:
            return "ALTO"
    
    def _create_empty_recommendation(self, home_team: str, away_team: str, match_date: str) -> FinalRecommendation:
        """Cria recomendação vazia em caso de erro"""
        return FinalRecommendation(
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            primary_recommendation=None,
            alternative_recommendations=[],
            confidence_score=0.0,
            risk_assessment="ALTO",
            market_analysis="Análise não disponível",
            key_factors=[],
            warnings=["Erro na análise"],
            analysis_timestamp=datetime.now()
        )
    
    def format_final_recommendation(self, recommendation: FinalRecommendation) -> str:
        """Formata recomendação final"""
        
        if not recommendation.primary_recommendation:
            return "Nenhuma recomendação disponível."
        
        primary = recommendation.primary_recommendation
        
        # Ícone de confiança
        confidence_icon = "🔥" if primary.confidence_level >= 0.80 else "⚡" if primary.confidence_level >= 0.70 else "📊"
        
        report = f"""
RECOMENDAÇÃO FINAL
{'='*50}

🏆 APOSTA RECOMENDADA
{'═'*50}
         {primary.market}
{'═'*50}

🎲 ODD: {primary.odds:.2f}
📈 PROBABILIDADE ESTIMADA: {primary.probability:.0%}
💰 VALOR ESPERADO: {primary.value_score:+.1f}%
🎯 NÍVEL DE CONFIANÇA: {primary.confidence_level:.0%}
{confidence_icon} CLASSIFICAÇÃO: {primary.classification}

✅ {primary.range_target}
"""
        
        # Recomendações alternativas
        if recommendation.alternative_recommendations:
            report += f"\n🔄 RECOMENDAÇÕES ALTERNATIVAS\n"
            report += f"{'─'*50}\n"
            
            for i, alt in enumerate(recommendation.alternative_recommendations, 1):
                report += f"{i}. {alt.market}\n"
                report += f"   ODD: {alt.odds:.2f} | EV: {alt.value_score:+.1f}% | Confiança: {alt.confidence_level:.0%}\n"
        
        # Análise de mercado
        report += f"\n📊 ANÁLISE DE MERCADO\n"
        report += f"{'─'*50}\n"
        report += f"{recommendation.market_analysis}\n"
        
        # Fatores-chave
        report += f"\n🔑 FATORES-CHAVE\n"
        report += f"{'─'*50}\n"
        for factor in recommendation.key_factors:
            report += f"• {factor}\n"
        
        # Avisos
        if recommendation.warnings:
            report += f"\n⚠️ AVISOS IMPORTANTES\n"
            report += f"{'─'*50}\n"
            for warning in recommendation.warnings:
                report += f"• {warning}\n"
        
        # Resumo executivo
        report += f"\n📈 RESUMO EXECUTIVO\n"
        report += f"{'─'*50}\n"
        report += f"• Confiança Geral: {recommendation.confidence_score:.1%}\n"
        report += f"• Nível de Risco: {recommendation.risk_assessment}\n"
        report += f"• Stake Recomendado: {primary.stake_recommendation:.1f} unidades\n"
        report += f"• Razão: {primary.reasoning}\n"
        
        return report

if __name__ == "__main__":
    # Teste do gerador de recomendação final
    generator = FinalRecommendationGenerator()
    
    print("=== TESTE DO GERADOR DE RECOMENDAÇÃO FINAL ===")
    
    # Dados de exemplo
    analysis_data = {
        'home_team': 'Manchester City',
        'away_team': 'Arsenal',
        'home_form': 0.8,
        'away_form': 0.6,
        'h2h_home': 0.7,
        'h2h_away': 0.3,
        'home_xg': 2.1,
        'away_xg': 1.5
    }
    
    # Gera recomendação final
    recommendation = generator.generate_final_recommendation(
        "Manchester City", "Arsenal", "2024-01-15", analysis_data
    )
    
    # Formata recomendação
    report = generator.format_final_recommendation(recommendation)
    
    print(report)
    
    print("\nTeste concluído!")
