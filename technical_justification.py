"""
Justificativa Técnica - MaraBet AI
Sistema especializado para análise técnica detalhada com pesos específicos
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
class TechnicalFactor:
    """Fator técnico individual"""
    name: str
    weight: float
    home_value: float
    away_value: float
    combined_value: float
    analysis: str
    conclusion: str
    confidence: float
    supporting_data: List[str]

@dataclass
class TechnicalJustification:
    """Justificativa técnica completa"""
    home_team: str
    away_team: str
    match_date: str
    recommendation: str
    factors: List[TechnicalFactor]
    overall_confidence: float
    technical_summary: str
    key_insights: List[str]
    risk_factors: List[str]
    analysis_timestamp: datetime

class TechnicalJustificationAnalyzer:
    """
    Analisador de Justificativa Técnica
    Sistema completo para análise técnica detalhada com pesos específicos
    """
    
    def __init__(self):
        self.factor_weights = self._load_factor_weights()
        self.analysis_templates = self._load_analysis_templates()
        self.confidence_levels = self._load_confidence_levels()
        
    def _load_factor_weights(self) -> Dict[str, float]:
        """Carrega pesos dos fatores técnicos"""
        return {
            'offensive_power': 0.35,      # Poder Ofensivo Combinado
            'defensive_vulnerability': 0.25,  # Vulnerabilidade Defensiva
            'playing_style': 0.20,        # Estilo de Jogo
            'motivational_context': 0.10, # Contexto Motivacional
            'xg_analysis': 0.10          # Análise xG
        }
    
    def _load_analysis_templates(self) -> Dict[str, Dict]:
        """Carrega templates de análise"""
        return {
            'offensive_power': {
                'description': 'Poder Ofensivo Combinado',
                'metrics': ['gols_por_jogo_casa', 'gols_por_jogo_fora', 'h2h_goals_avg'],
                'thresholds': {'high': 2.5, 'medium': 2.0, 'low': 1.5}
            },
            'defensive_vulnerability': {
                'description': 'Vulnerabilidade Defensiva',
                'metrics': ['gols_sofridos_por_jogo', 'clean_sheets', 'key_players_out'],
                'thresholds': {'high': 1.5, 'medium': 1.0, 'low': 0.5}
            },
            'playing_style': {
                'description': 'Estilo de Jogo',
                'metrics': ['posse_bola', 'intensidade', 'historico_movimentado'],
                'thresholds': {'high': 0.8, 'medium': 0.6, 'low': 0.4}
            },
            'motivational_context': {
                'description': 'Contexto Motivacional',
                'metrics': ['posicao_tabela', 'objetivos', 'rivalidade'],
                'thresholds': {'high': 0.9, 'medium': 0.7, 'low': 0.5}
            },
            'xg_analysis': {
                'description': 'Análise xG',
                'metrics': ['xg_combinado', 'xg_historico', 'xg_tendencia'],
                'thresholds': {'high': 4.0, 'medium': 3.0, 'low': 2.0}
            }
        }
    
    def _load_confidence_levels(self) -> Dict[str, Dict]:
        """Carrega níveis de confiança"""
        return {
            'very_high': {'min': 0.90, 'max': 1.00, 'label': 'MUITO ALTA', 'icon': '🔥'},
            'high': {'min': 0.80, 'max': 0.89, 'label': 'ALTA', 'icon': '⭐'},
            'medium_high': {'min': 0.70, 'max': 0.79, 'label': 'MÉDIA-ALTA', 'icon': '⚡'},
            'medium': {'min': 0.60, 'max': 0.69, 'label': 'MÉDIA', 'icon': '📊'},
            'low': {'min': 0.50, 'max': 0.59, 'label': 'BAIXA', 'icon': '⚠️'},
            'very_low': {'min': 0.00, 'max': 0.49, 'label': 'MUITO BAIXA', 'icon': '❌'}
        }
    
    def analyze_offensive_power(self, home_team: str, away_team: str, 
                              match_data: Dict) -> TechnicalFactor:
        """Analisa poder ofensivo combinado"""
        
        # Dados simulados para demonstração
        home_goals_home = np.random.uniform(2.5, 3.2)  # Manchester City em casa
        away_goals_away = np.random.uniform(1.6, 2.0)  # Arsenal fora
        h2h_goals_avg = np.random.uniform(3.2, 4.0)    # Histórico H2H
        
        combined_value = (home_goals_home + away_goals_away + h2h_goals_avg) / 3
        
        # Análise baseada nos dados
        if combined_value >= 2.8:
            analysis = f"{home_team}: {home_goals_home:.1f} gols/jogo em casa\n{away_team}: {away_goals_away:.1f} gols/jogo fora\nHistórico H2H: Média de {h2h_goals_avg:.1f} gols/jogo"
            conclusion = "Ambas equipes têm capacidade ofensiva comprovada"
            confidence = 0.85
        elif combined_value >= 2.3:
            analysis = f"{home_team}: {home_goals_home:.1f} gols/jogo em casa\n{away_team}: {away_goals_away:.1f} gols/jogo fora\nHistórico H2H: Média de {h2h_goals_avg:.1f} gols/jogo"
            conclusion = "Equipes com boa capacidade ofensiva"
            confidence = 0.75
        else:
            analysis = f"{home_team}: {home_goals_home:.1f} gols/jogo em casa\n{away_team}: {away_goals_away:.1f} gols/jogo fora\nHistórico H2H: Média de {h2h_goals_avg:.1f} gols/jogo"
            conclusion = "Capacidade ofensiva moderada"
            confidence = 0.65
        
        supporting_data = [
            f"Média de gols em casa: {home_goals_home:.1f}",
            f"Média de gols fora: {away_goals_away:.1f}",
            f"Histórico H2H: {h2h_goals_avg:.1f} gols/jogo",
            f"Valor combinado: {combined_value:.1f}"
        ]
        
        return TechnicalFactor(
            name="Poder Ofensivo Combinado",
            weight=self.factor_weights['offensive_power'],
            home_value=home_goals_home,
            away_value=away_goals_away,
            combined_value=combined_value,
            analysis=analysis,
            conclusion=conclusion,
            confidence=confidence,
            supporting_data=supporting_data
        )
    
    def analyze_defensive_vulnerability(self, home_team: str, away_team: str, 
                                      match_data: Dict) -> TechnicalFactor:
        """Analisa vulnerabilidade defensiva"""
        
        # Dados simulados para demonstração
        home_goals_conceded = np.random.uniform(0.8, 1.2)  # City sofreu gols em 60% dos jogos
        away_goals_conceded = np.random.uniform(0.6, 1.0)  # Arsenal sem Saliba
        clean_sheets_home = np.random.uniform(0.3, 0.5)    # 30-50% clean sheets
        clean_sheets_away = np.random.uniform(0.4, 0.6)    # 40-60% clean sheets
        
        # Arsenal sem Saliba (defensor chave)
        key_players_out = 1 if away_team == "Arsenal" else 0
        
        combined_vulnerability = (home_goals_conceded + away_goals_conceded) / 2
        
        # Análise baseada nos dados
        if combined_vulnerability >= 1.0 or key_players_out > 0:
            analysis = f"{away_team} sem Saliba (defensor chave)\n{home_team} sofreu gols em 60% dos últimos jogos\nClean sheets: {clean_sheets_home:.1%} vs {clean_sheets_away:.1%}"
            conclusion = "Defesas não estão em seu melhor momento"
            confidence = 0.80
        elif combined_vulnerability >= 0.8:
            analysis = f"{home_team}: {home_goals_conceded:.1f} gols sofridos/jogo\n{away_team}: {away_goals_conceded:.1f} gols sofridos/jogo"
            conclusion = "Defesas com algumas vulnerabilidades"
            confidence = 0.70
        else:
            analysis = f"{home_team}: {home_goals_conceded:.1f} gols sofridos/jogo\n{away_team}: {away_goals_conceded:.1f} gols sofridos/jogo"
            conclusion = "Defesas relativamente sólidas"
            confidence = 0.60
        
        supporting_data = [
            f"Gols sofridos {home_team}: {home_goals_conceded:.1f}/jogo",
            f"Gols sofridos {away_team}: {away_goals_conceded:.1f}/jogo",
            f"Clean sheets: {clean_sheets_home:.1%} vs {clean_sheets_away:.1%}",
            f"Desfalques importantes: {key_players_out}"
        ]
        
        return TechnicalFactor(
            name="Vulnerabilidade Defensiva",
            weight=self.factor_weights['defensive_vulnerability'],
            home_value=home_goals_conceded,
            away_value=away_goals_conceded,
            combined_value=combined_vulnerability,
            analysis=analysis,
            conclusion=conclusion,
            confidence=confidence,
            supporting_data=supporting_data
        )
    
    def analyze_playing_style(self, home_team: str, away_team: str, 
                            match_data: Dict) -> TechnicalFactor:
        """Analisa estilo de jogo"""
        
        # Dados simulados para demonstração
        home_possession = np.random.uniform(0.55, 0.65)  # City alta posse
        away_possession = np.random.uniform(0.50, 0.60)  # Arsenal boa posse
        intensity = np.random.uniform(0.7, 0.9)          # Alta intensidade
        historical_movement = np.random.uniform(0.75, 0.85)  # Historicamente movimentado
        
        combined_style = (home_possession + away_possession + intensity + historical_movement) / 4
        
        # Análise baseada nos dados
        if combined_style >= 0.75:
            analysis = f"Ambas equipes jogam de forma ofensiva\nAlta posse de bola = mais oportunidades\nConfronto historicamente movimentado"
            conclusion = "Jogo tende a ser aberto"
            confidence = 0.85
        elif combined_style >= 0.65:
            analysis = f"Equipes com estilo ofensivo\nPosse de bola moderada\nConfrontos geralmente movimentados"
            conclusion = "Jogo tende a ser equilibrado"
            confidence = 0.75
        else:
            analysis = f"Estilo de jogo variado\nPosse de bola controlada\nConfrontos mais fechados"
            conclusion = "Jogo pode ser mais fechado"
            confidence = 0.65
        
        supporting_data = [
            f"Posse de bola {home_team}: {home_possession:.1%}",
            f"Posse de bola {away_team}: {away_possession:.1%}",
            f"Intensidade do jogo: {intensity:.1%}",
            f"Histórico movimentado: {historical_movement:.1%}"
        ]
        
        return TechnicalFactor(
            name="Estilo de Jogo",
            weight=self.factor_weights['playing_style'],
            home_value=home_possession,
            away_value=away_possession,
            combined_value=combined_style,
            analysis=analysis,
            conclusion=conclusion,
            confidence=confidence,
            supporting_data=supporting_data
        )
    
    def analyze_motivational_context(self, home_team: str, away_team: str, 
                                   match_data: Dict) -> TechnicalFactor:
        """Analisa contexto motivacional"""
        
        # Dados simulados para demonstração
        home_position = np.random.randint(1, 4)  # City entre 1º e 3º
        away_position = np.random.randint(1, 4)  # Arsenal entre 1º e 3º
        home_objectives = np.random.uniform(0.8, 1.0)  # Objetivos claros
        away_objectives = np.random.uniform(0.8, 1.0)  # Objetivos claros
        rivalry = np.random.uniform(0.7, 0.9)  # Alta rivalidade
        
        combined_motivation = (home_objectives + away_objectives + rivalry) / 3
        
        # Análise baseada nos dados
        if combined_motivation >= 0.85:
            analysis = f"Disputa direta pela liderança\nAmbos precisam vencer\nPosições: {home_team} {home_position}º, {away_team} {away_position}º"
            conclusion = "Jogo de alta intensidade desde o início"
            confidence = 0.90
        elif combined_motivation >= 0.75:
            analysis = f"Ambos com objetivos importantes\nNecessidade de vitória\nPosições próximas na tabela"
            conclusion = "Jogo de alta motivação"
            confidence = 0.80
        else:
            analysis = f"Objetivos moderados\nPressão variável\nPosições diferentes na tabela"
            conclusion = "Motivação moderada"
            confidence = 0.70
        
        supporting_data = [
            f"Posição {home_team}: {home_position}º lugar",
            f"Posição {away_team}: {away_position}º lugar",
            f"Objetivos {home_team}: {home_objectives:.1%}",
            f"Objetivos {away_team}: {away_objectives:.1%}",
            f"Rivalidade: {rivalry:.1%}"
        ]
        
        return TechnicalFactor(
            name="Contexto Motivacional",
            weight=self.factor_weights['motivational_context'],
            home_value=home_objectives,
            away_value=away_objectives,
            combined_value=combined_motivation,
            analysis=analysis,
            conclusion=conclusion,
            confidence=confidence,
            supporting_data=supporting_data
        )
    
    def analyze_xg_analysis(self, home_team: str, away_team: str, 
                          match_data: Dict) -> TechnicalFactor:
        """Analisa xG avançado"""
        
        # Dados simulados para demonstração
        home_xg = np.random.uniform(2.0, 2.8)  # City xG alto
        away_xg = np.random.uniform(1.5, 2.2)  # Arsenal xG bom
        combined_xg = home_xg + away_xg
        historical_xg = np.random.uniform(3.5, 4.5)  # Histórico H2H
        over_3_goals_percentage = np.random.uniform(0.70, 0.85)  # 70-85% dos jogos
        
        # Análise baseada nos dados
        if combined_xg >= 4.0 and over_3_goals_percentage >= 0.75:
            analysis = f"xG combinado médio: {combined_xg:.1f} por jogo\n{over_3_goals_percentage:.0%} dos últimos confrontos tiveram 3+ gols\nHistórico xG: {historical_xg:.1f}"
            conclusion = "Estatísticas avançadas confirmam tendência"
            confidence = 0.88
        elif combined_xg >= 3.5 and over_3_goals_percentage >= 0.65:
            analysis = f"xG combinado: {combined_xg:.1f} por jogo\n{over_3_goals_percentage:.0%} dos confrontos tiveram 3+ gols"
            conclusion = "Estatísticas indicam tendência positiva"
            confidence = 0.78
        else:
            analysis = f"xG combinado: {combined_xg:.1f} por jogo\n{over_3_goals_percentage:.0%} dos confrontos tiveram 3+ gols"
            conclusion = "Estatísticas moderadas"
            confidence = 0.68
        
        supporting_data = [
            f"xG {home_team}: {home_xg:.1f}",
            f"xG {away_team}: {away_xg:.1f}",
            f"xG combinado: {combined_xg:.1f}",
            f"Histórico xG: {historical_xg:.1f}",
            f"Over 3.5 gols: {over_3_goals_percentage:.1%}"
        ]
        
        return TechnicalFactor(
            name="Análise xG",
            weight=self.factor_weights['xg_analysis'],
            home_value=home_xg,
            away_value=away_xg,
            combined_value=combined_xg,
            analysis=analysis,
            conclusion=conclusion,
            confidence=confidence,
            supporting_data=supporting_data
        )
    
    def generate_technical_justification(self, home_team: str, away_team: str, 
                                       match_date: str, recommendation: str,
                                       match_data: Dict) -> TechnicalJustification:
        """Gera justificativa técnica completa"""
        
        logger.info(f"Gerando justificativa técnica: {home_team} vs {away_team}")
        
        try:
            # Analisa cada fator técnico
            factors = []
            
            factors.append(self.analyze_offensive_power(home_team, away_team, match_data))
            factors.append(self.analyze_defensive_vulnerability(home_team, away_team, match_data))
            factors.append(self.analyze_playing_style(home_team, away_team, match_data))
            factors.append(self.analyze_motivational_context(home_team, away_team, match_data))
            factors.append(self.analyze_xg_analysis(home_team, away_team, match_data))
            
            # Calcula confiança geral
            overall_confidence = self._calculate_overall_confidence(factors)
            
            # Gera resumo técnico
            technical_summary = self._generate_technical_summary(factors, recommendation)
            
            # Extrai insights principais
            key_insights = self._extract_key_insights(factors)
            
            # Identifica fatores de risco
            risk_factors = self._identify_risk_factors(factors)
            
            return TechnicalJustification(
                home_team=home_team,
                away_team=away_team,
                match_date=match_date,
                recommendation=recommendation,
                factors=factors,
                overall_confidence=overall_confidence,
                technical_summary=technical_summary,
                key_insights=key_insights,
                risk_factors=risk_factors,
                analysis_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro na geração da justificativa técnica: {e}")
            return self._create_empty_justification(home_team, away_team, match_date)
    
    def _calculate_overall_confidence(self, factors: List[TechnicalFactor]) -> float:
        """Calcula confiança geral baseada nos fatores"""
        if not factors:
            return 0.0
        
        weighted_confidence = sum(factor.confidence * factor.weight for factor in factors)
        return min(1.0, weighted_confidence)
    
    def _generate_technical_summary(self, factors: List[TechnicalFactor], 
                                  recommendation: str) -> str:
        """Gera resumo técnico"""
        return f"Análise técnica detalhada baseada em {len(factors)} fatores principais que justificam a recomendação de {recommendation}. A análise combina dados ofensivos, defensivos, táticos e contextuais para fornecer uma base sólida para a decisão."
    
    def _extract_key_insights(self, factors: List[TechnicalFactor]) -> List[str]:
        """Extrai insights principais"""
        insights = []
        
        for factor in factors:
            if factor.confidence >= 0.8:
                insights.append(f"• {factor.name}: {factor.conclusion}")
        
        return insights
    
    def _identify_risk_factors(self, factors: List[TechnicalFactor]) -> List[str]:
        """Identifica fatores de risco"""
        risks = []
        
        for factor in factors:
            if factor.confidence < 0.7:
                risks.append(f"• {factor.name}: Confiança baixa ({factor.confidence:.1%})")
        
        return risks
    
    def _create_empty_justification(self, home_team: str, away_team: str, 
                                   match_date: str) -> TechnicalJustification:
        """Cria justificativa vazia em caso de erro"""
        return TechnicalJustification(
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            recommendation="N/A",
            factors=[],
            overall_confidence=0.0,
            technical_summary="Análise não disponível",
            key_insights=[],
            risk_factors=["Erro na análise"],
            analysis_timestamp=datetime.now()
        )
    
    def format_technical_justification(self, justification: TechnicalJustification) -> str:
        """Formata justificativa técnica"""
        
        if not justification or not justification.factors:
            return "Justificativa técnica não disponível."
        
        report_parts = []
        
        # Cabeçalho
        report_parts.append("JUSTIFICATIVA TÉCNICA")
        report_parts.append("=" * 60)
        report_parts.append(f"Partida: {justification.home_team} vs {justification.away_team}")
        report_parts.append(f"Data: {justification.match_date}")
        report_parts.append(f"Recomendação: {justification.recommendation}")
        report_parts.append("")
        
        # Fatores principais
        report_parts.append("🔍 PRINCIPAIS FATORES DA RECOMENDAÇÃO")
        report_parts.append("")
        
        for i, factor in enumerate(justification.factors, 1):
            report_parts.append(f"{i}. {factor.name} ({factor.weight:.0%} do peso):")
            report_parts.append("")
            report_parts.append(factor.analysis)
            report_parts.append(f"Conclusão: {factor.conclusion}")
            report_parts.append("")
        
        # Resumo técnico
        report_parts.append("📊 RESUMO TÉCNICO")
        report_parts.append("-" * 40)
        report_parts.append(justification.technical_summary)
        report_parts.append("")
        
        # Insights principais
        if justification.key_insights:
            report_parts.append("💡 INSIGHTS PRINCIPAIS")
            report_parts.append("-" * 40)
            for insight in justification.key_insights:
                report_parts.append(insight)
            report_parts.append("")
        
        # Fatores de risco
        if justification.risk_factors:
            report_parts.append("⚠️ FATORES DE RISCO")
            report_parts.append("-" * 40)
            for risk in justification.risk_factors:
                report_parts.append(risk)
            report_parts.append("")
        
        # Confiança geral
        confidence_level = self._get_confidence_level(justification.overall_confidence)
        report_parts.append("🎯 CONFIANÇA GERAL")
        report_parts.append("-" * 40)
        report_parts.append(f"Confiança: {justification.overall_confidence:.1%} ({confidence_level['label']})")
        report_parts.append(f"Ícone: {confidence_level['icon']}")
        report_parts.append("")
        
        return "\n".join(report_parts)
    
    def _get_confidence_level(self, confidence: float) -> Dict[str, Any]:
        """Obtém nível de confiança"""
        for level, config in self.confidence_levels.items():
            if config['min'] <= confidence <= config['max']:
                return config
        return self.confidence_levels['low']

if __name__ == "__main__":
    # Teste do analisador de justificativa técnica
    analyzer = TechnicalJustificationAnalyzer()
    
    print("=== TESTE DO ANALISADOR DE JUSTIFICATIVA TÉCNICA ===")
    
    # Dados de exemplo
    match_data = {
        'home_form': 0.8,
        'away_form': 0.6,
        'h2h_home': 0.7,
        'h2h_away': 0.3
    }
    
    # Gera justificativa técnica
    justification = analyzer.generate_technical_justification(
        "Manchester City", "Arsenal", "2024-01-15", 
        "OVER 2.5 GOLS", match_data
    )
    
    # Formata justificativa
    report = analyzer.format_technical_justification(justification)
    
    print(report)
    
    print("\nTeste concluído!")
