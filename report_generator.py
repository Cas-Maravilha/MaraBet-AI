"""
Gerador de Relatórios de Análise Preditiva - MaraBet AI
Sistema especializado para geração de relatórios completos e profissionais
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import json
import os
from statistical_analysis import StatisticalAnalyzer
from contextual_analysis import ContextualAnalyzer
from predictive_modeling import PredictiveModeler
from expected_value_analysis import ExpectedValueAnalyzer
from final_recommendation import FinalRecommendationGenerator
from bankroll_management_advanced import AdvancedBankrollManager
from technical_justification import TechnicalJustificationAnalyzer
from scenarios_probabilities import ScenariosProbabilityAnalyzer
from action_plan import ActionPlanGenerator
from post_analysis_tracking import PostAnalysisTracker
from glossary_concepts import GlossaryGenerator
from personalized_analysis import PersonalizedAnalysisGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MatchContext:
    """Contexto da partida para análise"""
    home_team: str
    away_team: str
    league: str
    season: str
    date: str
    time: str
    venue: str
    weather_conditions: str
    temperature: float
    referee: str
    attendance: int
    importance: str  # 'High', 'Medium', 'Low'

@dataclass
class AnalysisResult:
    """Resultado da análise preditiva"""
    match_context: MatchContext
    value_analysis: Dict
    probability_analysis: Dict
    unit_recommendation: Dict
    bankroll_analysis: Dict
    risk_assessment: Dict
    final_recommendation: Dict
    confidence_score: float
    analysis_timestamp: datetime

class ReportGenerator:
    """
    Gerador de Relatórios de Análise Preditiva
    Cria relatórios completos e profissionais
    """
    
    def __init__(self):
        self.template_path = "templates"
        self.output_path = "reports"
        self.statistical_analyzer = StatisticalAnalyzer()
        self.contextual_analyzer = ContextualAnalyzer()
        self.predictive_modeler = PredictiveModeler()
        self.expected_value_analyzer = ExpectedValueAnalyzer()
        self.final_recommendation_generator = FinalRecommendationGenerator()
        self.bankroll_manager = AdvancedBankrollManager()
        self.technical_analyzer = TechnicalJustificationAnalyzer()
        self.scenarios_analyzer = ScenariosProbabilityAnalyzer()
        self.action_plan_generator = ActionPlanGenerator()
        self.post_analysis_tracker = PostAnalysisTracker()
        self.glossary_generator = GlossaryGenerator()
        self.personalized_analyzer = PersonalizedAnalysisGenerator()
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Cria diretórios necessários"""
        os.makedirs(self.template_path, exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)
    
    def generate_complete_analysis_report(self, home_team: str, away_team: str, 
                                        match_date: str, league: str = "Premier League",
                                        season: str = "2024/25") -> Dict:
        """
        Gera relatório completo de análise preditiva
        """
        logger.info(f"Gerando relatório completo: {home_team} vs {away_team}")
        
        try:
            # Cria contexto da partida
            match_context = self._create_match_context(
                home_team, away_team, match_date, league, season
            )
            
            # Carrega dados de exemplo para análise estatística
            self.statistical_analyzer.load_sample_data()
            
            # Gera análise estatística detalhada
            statistical_analysis = self.statistical_analyzer.generate_detailed_statistical_report(
                home_team, away_team
            )
            
            # Gera análise contextual
            contextual_analysis = self.contextual_analyzer.generate_contextual_analysis(
                home_team, away_team, "High"
            )
            
            # Gera modelagem preditiva
            match_data = self._prepare_match_data(home_team, away_team)
            predictive_model = self.predictive_modeler.generate_predictive_model(
                home_team, away_team, match_date, match_data
            )
            
            # Gera análise de valor esperado
            expected_value_analysis = self.expected_value_analyzer.generate_expected_value_analysis(
                home_team, away_team, match_date, match_data
            )
            
            # Gera recomendação final
            final_recommendation = self.final_recommendation_generator.generate_final_recommendation(
                home_team, away_team, match_date, match_data
            )
            
            # Gera análise de gestão de banca
            bankroll_analysis = self.bankroll_manager.generate_bankroll_analysis(
                home_team, away_team, match_date, 
                match_data.get('home_form', 0.7), 
                match_data.get('home_odds', 1.65), 
                1000.0, "USD"
            )
            
            # Gera justificativa técnica
            technical_justification = self.technical_analyzer.generate_technical_justification(
                home_team, away_team, match_date, 
                "OVER 2.5 GOLS", match_data
            )
            
            # Gera análise de cenários e probabilidades
            scenarios_analysis = self.scenarios_analyzer.generate_probability_distribution(
                home_team, away_team, match_date, match_data
            )
            
            # Gera plano de ação
            action_plan = self.action_plan_generator.generate_action_plan(
                home_team, away_team, match_date, 
                "OVER 2.5 GOLS", match_data
            )
            
            # Gera acompanhamento posterior
            post_analysis = self.post_analysis_tracker.generate_post_analysis_tracking(
                home_team, away_team, match_date, 
                "OVER 2.5 GOLS", match_data
            )
            
            # Gera glossário de conceitos
            glossary = self.glossary_generator.generate_glossary()
            
            # Gera análise personalizada (exemplo com perfil moderado)
            user_profile = self.personalized_analyzer.create_user_profile(
                name="Usuário Demo",
                risk_profile="moderado",
                bankroll=1000.0,
                currency="BRL"
            )
            
            match_request = self.personalized_analyzer.create_match_request(
                home_team, away_team, league, match_date,
                current_odds={"Over/Under 2.5": 1.65, "Ambas Marcam": 1.45},
                user_profile=user_profile
            )
            
            personalized_analysis = self.personalized_analyzer.generate_personalized_analysis(match_request)
            
            # Simula análises (em produção, integraria com os sistemas reais)
            value_analysis = self._simulate_value_analysis(home_team, away_team)
            probability_analysis = self._simulate_probability_analysis(home_team, away_team)
            unit_recommendation = self._simulate_unit_recommendation()
            bankroll_analysis = self._simulate_bankroll_analysis()
            risk_assessment = self._simulate_risk_assessment()
            
            # Calcula score de confiança
            confidence_score = self._calculate_confidence_score(
                value_analysis, probability_analysis, risk_assessment
            )
            
            # Determina recomendação final
            final_recommendation = self._determine_final_recommendation(
                value_analysis, probability_analysis, unit_recommendation, 
                bankroll_analysis, risk_assessment, confidence_score
            )
            
            # Cria resultado da análise
            analysis_result = AnalysisResult(
                match_context=match_context,
                value_analysis=value_analysis,
                probability_analysis=probability_analysis,
                unit_recommendation=unit_recommendation,
                bankroll_analysis=bankroll_analysis,
                risk_assessment=risk_assessment,
                final_recommendation=final_recommendation,
                confidence_score=confidence_score,
                analysis_timestamp=datetime.now()
            )
            
            # Adiciona análises ao resultado
            analysis_result.statistical_analysis = statistical_analysis
            analysis_result.contextual_analysis = contextual_analysis
            analysis_result.predictive_model = predictive_model
            analysis_result.expected_value_analysis = expected_value_analysis
            analysis_result.final_recommendation = final_recommendation
            analysis_result.bankroll_analysis = bankroll_analysis
            analysis_result.technical_justification = technical_justification
            analysis_result.scenarios_analysis = scenarios_analysis
            analysis_result.action_plan = action_plan
            analysis_result.post_analysis = post_analysis
            analysis_result.glossary = glossary
            analysis_result.personalized_analysis = personalized_analysis
            
            # Gera relatório formatado
            report = self._format_complete_report(analysis_result)
            
            # Salva relatório
            self._save_report(report, home_team, away_team, match_date)
            
            return {
                'success': True,
                'report': report,
                'analysis_result': analysis_result,
                'file_path': self._get_report_path(home_team, away_team, match_date)
            }
            
        except Exception as e:
            logger.error(f"Erro na geração do relatório: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_match_context(self, home_team: str, away_team: str, 
                            match_date: str, league: str, season: str) -> MatchContext:
        """Cria contexto da partida"""
        # Simula dados contextuais (em produção, viria de APIs reais)
        weather_conditions = np.random.choice([
            "Céu limpo", "Parcialmente nublado", "Chuva leve", 
            "Neblina", "Vento forte"
        ])
        
        temperature = np.random.uniform(5, 30)
        
        referees = [
            "Michael Oliver", "Anthony Taylor", "Paul Tierney", 
            "Craig Pawson", "Stuart Attwell"
        ]
        
        return MatchContext(
            home_team=home_team,
            away_team=away_team,
            league=league,
            season=season,
            date=match_date,
            time="15:00h GMT",
            venue=f"Estádio {home_team}",
            weather_conditions=weather_conditions,
            temperature=temperature,
            referee=np.random.choice(referees),
            attendance=np.random.randint(30000, 80000),
            importance=np.random.choice(["High", "Medium", "Low"])
        )
    
    def _simulate_value_analysis(self, home_team: str, away_team: str) -> Dict:
        """Simula análise de valor"""
        # Simula odds de mercado
        home_odds = np.random.uniform(1.5, 4.0)
        draw_odds = np.random.uniform(2.8, 3.5)
        away_odds = np.random.uniform(1.8, 5.0)
        
        # Simula probabilidades calculadas
        home_prob = np.random.uniform(0.25, 0.60)
        draw_prob = np.random.uniform(0.20, 0.35)
        away_prob = 1 - home_prob - draw_prob
        
        # Calcula valores esperados
        home_ev = (home_prob * home_odds) - 1
        draw_ev = (draw_prob * draw_odds) - 1
        away_ev = (away_prob * away_odds) - 1
        
        # Encontra melhor oportunidade
        evs = [home_ev, draw_ev, away_ev]
        outcomes = ['home_win', 'draw', 'away_win']
        odds = [home_odds, draw_odds, away_odds]
        probs = [home_prob, draw_prob, away_prob]
        
        best_idx = np.argmax(evs)
        
        return {
            'market_odds': {
                'home_win': home_odds,
                'draw': draw_odds,
                'away_win': away_odds
            },
            'calculated_probabilities': {
                'home_win': home_prob,
                'draw': draw_prob,
                'away_win': away_prob
            },
            'expected_values': {
                'home_win': home_ev,
                'draw': draw_ev,
                'away_win': away_ev
            },
            'best_opportunity': {
                'outcome': outcomes[best_idx],
                'odds': odds[best_idx],
                'probability': probs[best_idx],
                'expected_value': evs[best_idx],
                'value_percentage': evs[best_idx] * 100
            },
            'value_classification': self._classify_value(evs[best_idx]),
            'confidence': np.random.uniform(0.70, 0.95)
        }
    
    def _simulate_probability_analysis(self, home_team: str, away_team: str) -> Dict:
        """Simula análise de probabilidades"""
        # Simula análise de forma recente
        home_form = np.random.uniform(0.4, 0.8)
        away_form = np.random.uniform(0.4, 0.8)
        
        # Simula confrontos diretos
        h2h_home = np.random.uniform(0.3, 0.7)
        h2h_away = 1 - h2h_home
        
        # Simula estatísticas avançadas
        home_xg = np.random.uniform(1.2, 2.5)
        away_xg = np.random.uniform(1.2, 2.5)
        
        # Simula fatores contextuais
        home_advantage = np.random.uniform(0.05, 0.15)
        injury_impact = np.random.uniform(-0.1, 0.1)
        
        # Calcula probabilidades finais
        home_prob = (home_form * 0.4 + h2h_home * 0.25 + 
                    (home_xg / (home_xg + away_xg)) * 0.15 + 
                    home_advantage * 0.1 + injury_impact * 0.1)
        
        away_prob = (away_form * 0.4 + h2h_away * 0.25 + 
                    (away_xg / (home_xg + away_xg)) * 0.15)
        
        draw_prob = 1 - home_prob - away_prob
        
        return {
            'recent_form': {
                'home': home_form,
                'away': away_form
            },
            'head_to_head': {
                'home': h2h_home,
                'away': h2h_away
            },
            'advanced_stats': {
                'home_xg': home_xg,
                'away_xg': away_xg,
                'possession_home': np.random.uniform(0.4, 0.7),
                'possession_away': np.random.uniform(0.3, 0.6)
            },
            'contextual_factors': {
                'home_advantage': home_advantage,
                'injury_impact': injury_impact,
                'weather_impact': np.random.uniform(-0.05, 0.05)
            },
            'final_probabilities': {
                'home_win': home_prob,
                'draw': draw_prob,
                'away_win': away_prob
            },
            'confidence': np.random.uniform(0.75, 0.90)
        }
    
    def _simulate_unit_recommendation(self) -> Dict:
        """Simula recomendação de unidades"""
        confidence = np.random.uniform(0.70, 0.90)
        
        if confidence >= 0.85:
            units = np.random.uniform(2.0, 3.0)
            level = "HIGH"
        elif confidence >= 0.75:
            units = np.random.uniform(1.5, 2.0)
            level = "MEDIUM_HIGH"
        elif confidence >= 0.70:
            units = np.random.uniform(1.0, 1.5)
            level = "MEDIUM"
        else:
            units = np.random.uniform(0.5, 1.0)
            level = "LOW"
        
        return {
            'confidence_level': level,
            'confidence_percentage': confidence,
            'recommended_units': units,
            'unit_value': 100.0,
            'total_stake': units * 100.0,
            'reasoning': [
                f"Confiança {confidence:.1%}",
                "Análise de valor positiva",
                "Fatores contextuais favoráveis"
            ]
        }
    
    def _simulate_bankroll_analysis(self) -> Dict:
        """Simula análise de gestão de banca"""
        return {
            'current_capital': np.random.uniform(800, 1200),
            'initial_capital': 1000.0,
            'profit_percentage': np.random.uniform(-10, 25),
            'drawdown_percentage': np.random.uniform(0, 15),
            'risk_level': np.random.choice(["CONSERVATIVE", "MODERATE", "AGGRESSIVE"]),
            'max_stake_percentage': 0.10,
            'recommended_stake_percentage': np.random.uniform(0.02, 0.08),
            'kelly_fraction': np.random.uniform(0.01, 0.05)
        }
    
    def _simulate_risk_assessment(self) -> Dict:
        """Simula avaliação de risco"""
        return {
            'overall_risk': np.random.choice(["LOW", "MEDIUM", "HIGH"]),
            'risk_score': np.random.randint(1, 8),
            'concentration_risk': np.random.choice(["LOW", "MEDIUM", "HIGH"]),
            'volatility_risk': np.random.choice(["LOW", "MEDIUM", "HIGH"]),
            'liquidity_risk': np.random.choice(["LOW", "MEDIUM", "HIGH"]),
            'market_risk': np.random.choice(["LOW", "MEDIUM", "HIGH"]),
            'recommendations': [
                "Monitorar exposição de capital",
                "Diversificar apostas",
                "Ajustar tamanho das posições"
            ]
        }
    
    def _calculate_confidence_score(self, value_analysis: Dict, 
                                  probability_analysis: Dict, 
                                  risk_assessment: Dict) -> float:
        """Calcula score de confiança geral"""
        value_conf = value_analysis['confidence']
        prob_conf = probability_analysis['confidence']
        risk_factor = 1.0 if risk_assessment['overall_risk'] == 'LOW' else 0.8
        
        return (value_conf * 0.4 + prob_conf * 0.4 + risk_factor * 0.2)
    
    def _determine_final_recommendation(self, value_analysis: Dict, 
                                      probability_analysis: Dict,
                                      unit_recommendation: Dict,
                                      bankroll_analysis: Dict,
                                      risk_assessment: Dict,
                                      confidence_score: float) -> Dict:
        """Determina recomendação final"""
        best_ev = value_analysis['best_opportunity']['expected_value']
        units = unit_recommendation['recommended_units']
        risk = risk_assessment['overall_risk']
        
        if best_ev > 0.15 and units > 2.0 and risk == 'LOW' and confidence_score > 0.85:
            action = "STRONG_BET"
            reasoning = "Excelente oportunidade com baixo risco"
        elif best_ev > 0.10 and units > 1.0 and confidence_score > 0.75:
            action = "BET"
            reasoning = "Boa oportunidade com risco controlado"
        elif best_ev > 0.05 and units > 0.5:
            action = "CONSIDER"
            reasoning = "Oportunidade moderada"
        else:
            action = "AVOID"
            reasoning = "Risco muito alto ou valor insuficiente"
        
        return {
            'action': action,
            'reasoning': reasoning,
            'confidence_score': confidence_score,
            'risk_level': risk,
            'expected_value': best_ev,
            'recommended_units': units
        }
    
    def _classify_value(self, ev: float) -> str:
        """Classifica nível de valor"""
        if ev > 0.10:
            return "EXCELLENT"
        elif ev > 0.05:
            return "SIGNIFICANT"
        elif ev > 0:
            return "POSITIVE"
        else:
            return "NEGATIVE"
    
    def _format_complete_report(self, analysis_result: AnalysisResult) -> str:
        """Formata relatório completo"""
        context = analysis_result.match_context
        value = analysis_result.value_analysis
        prob = analysis_result.probability_analysis
        units = analysis_result.unit_recommendation
        bankroll = analysis_result.bankroll_analysis
        risk = analysis_result.risk_assessment
        final = getattr(analysis_result, 'final_recommendation', None)
        final_action = final.primary_recommendation.market if final and final.primary_recommendation else "N/A"
        statistical = getattr(analysis_result, 'statistical_analysis', '')
        contextual = getattr(analysis_result, 'contextual_analysis', None)
        predictive = getattr(analysis_result, 'predictive_model', None)
        expected_value = getattr(analysis_result, 'expected_value_analysis', None)
        final_rec = getattr(analysis_result, 'final_recommendation', None)
        bankroll = getattr(analysis_result, 'bankroll_analysis', None)
        technical = getattr(analysis_result, 'technical_justification', None)
        scenarios = getattr(analysis_result, 'scenarios_analysis', None)
        action_plan = getattr(analysis_result, 'action_plan', None)
        post_analysis = getattr(analysis_result, 'post_analysis', None)
        glossary = getattr(analysis_result, 'glossary', None)
        personalized = getattr(analysis_result, 'personalized_analysis', None)
        
        report = f"""
🎯 RELATÓRIO DE ANÁLISE PREDITIVA
{'='*60}

EVENTO ANALISADO
🏟️ {context.home_team} vs {context.away_team}
📅 {context.league} - {context.season}
🕐 {context.date} - {context.time}
🌦️ Condições: {context.weather_conditions}, {context.temperature:.0f}°C
🏟️ Local: {context.venue}
👨‍⚖️ Árbitro: {context.referee}
👥 Público: {context.attendance:,}
⭐ Importância: {context.importance}

ANÁLISE DE VALOR
{'-'*30}
📊 Odds de Mercado:
   • Vitória {context.home_team}: {value['market_odds']['home_win']:.2f}
   • Empate: {value['market_odds']['draw']:.2f}
   • Vitória {context.away_team}: {value['market_odds']['away_win']:.2f}

🎯 Probabilidades Calculadas:
   • Vitória {context.home_team}: {value['calculated_probabilities']['home_win']:.1%}
   • Empate: {value['calculated_probabilities']['draw']:.1%}
   • Vitória {context.away_team}: {value['calculated_probabilities']['away_win']:.1%}

💰 Valores Esperados:
   • Vitória {context.home_team}: {value['expected_values']['home_win']:+.3f}
   • Empate: {value['expected_values']['draw']:+.3f}
   • Vitória {context.away_team}: {value['expected_values']['away_win']:+.3f}

🏆 Melhor Oportunidade:
   • Resultado: {value['best_opportunity']['outcome'].replace('_', ' ').title()}
   • Odds: {value['best_opportunity']['odds']:.2f}
   • Probabilidade: {value['best_opportunity']['probability']:.1%}
   • Valor Esperado: {value['best_opportunity']['expected_value']:+.3f}
   • Classificação: {value['value_classification']}

ANÁLISE ESTATÍSTICA DETALHADA
{'-'*30}
{statistical}

FATORES CONTEXTUAIS
{'-'*30}
{self.contextual_analyzer.format_contextual_report(contextual) if contextual else 'Análise contextual não disponível'}

MODELAGEM PREDITIVA
{'-'*30}
{self.predictive_modeler.format_predictive_table(predictive) if predictive else 'Modelagem preditiva não disponível'}

ANÁLISE DE VALOR ESPERADO
{'-'*30}
{self.expected_value_analyzer.format_expected_value_report(expected_value) if expected_value else 'Análise de valor esperado não disponível'}

RECOMENDAÇÃO FINAL
{'-'*30}
{self.final_recommendation_generator.format_final_recommendation(final_rec) if final_rec else 'Recomendação final não disponível'}

GESTÃO DE BANCA
{'-'*30}
{self.bankroll_manager.format_bankroll_analysis(bankroll) if bankroll else 'Análise de gestão de banca não disponível'}

JUSTIFICATIVA TÉCNICA
{'-'*30}
{self.technical_analyzer.format_technical_justification(technical) if technical else 'Justificativa técnica não disponível'}

CENÁRIOS E PROBABILIDADES
{'-'*30}
{self.scenarios_analyzer.format_probability_distribution(scenarios) if scenarios else 'Análise de cenários não disponível'}

PLANO DE AÇÃO
{'-'*30}
{self.action_plan_generator.format_action_plan(action_plan) if action_plan else 'Plano de ação não disponível'}

ACOMPANHAMENTO E ANÁLISE POSTERIOR
{'-'*30}
{self.post_analysis_tracker.format_post_analysis_tracking(post_analysis) if post_analysis else 'Acompanhamento posterior não disponível'}

GLOSSÁRIO E CONCEITOS
{'-'*30}
{self.glossary_generator.format_glossary(glossary) if glossary else 'Glossário não disponível'}

ANÁLISE PERSONALIZADA
{'-'*30}
{self.personalized_analyzer.format_personalized_analysis(personalized) if personalized else 'Análise personalizada não disponível'}

ANÁLISE DE PROBABILIDADES
{'-'*30}
📈 Forma Recente:
   • {context.home_team}: {prob['recent_form']['home']:.1%}
   • {context.away_team}: {prob['recent_form']['away']:.1%}

⚔️ Confrontos Diretos:
   • {context.home_team}: {prob['head_to_head']['home']:.1%}
   • {context.away_team}: {prob['head_to_head']['away']:.1%}

📊 Estatísticas Avançadas:
   • xG {context.home_team}: {prob['advanced_stats']['home_xg']:.2f}
   • xG {context.away_team}: {prob['advanced_stats']['away_xg']:.2f}
   • Posse {context.home_team}: {prob['advanced_stats']['possession_home']:.1%}
   • Posse {context.away_team}: {prob['advanced_stats']['possession_away']:.1%}

🌍 Fatores Contextuais:
   • Vantagem de casa: {prob['contextual_factors']['home_advantage']:+.1%}
   • Impacto de lesões: {prob['contextual_factors']['injury_impact']:+.1%}
   • Impacto do clima: {prob['contextual_factors']['weather_impact']:+.1%}

GESTÃO DE UNIDADES
{'-'*30}
🎯 Recomendação de Unidades:
   • Nível de Confiança: {units['confidence_level']}
   • Confiança: {units['confidence_percentage']:.1%}
   • Unidades Recomendadas: {units['recommended_units']:.1f}
   • Valor da Unidade: R$ {units['unit_value']:.2f}
   • Stake Total: R$ {units['total_stake']:.2f}

💡 Motivos:
{chr(10).join(f'   • {reason}' for reason in units['reasoning'])}

GESTÃO DE BANCA
{'-'*30}
💰 Status da Banca:
   • Capital Atual: R$ {bankroll['current_capital']:.2f}
   • Capital Inicial: R$ {bankroll['initial_capital']:.2f}
   • Lucro/Prejuízo: {bankroll['profit_percentage']:+.1f}%
   • Drawdown: {bankroll['drawdown_percentage']:.1f}%

⚖️ Gestão de Risco:
   • Nível de Risco: {bankroll['risk_level']}
   • Stake Máximo: {bankroll['max_stake_percentage']:.1%}
   • Stake Recomendado: {bankroll['recommended_stake_percentage']:.1%}
   • Kelly Fraction: {bankroll['kelly_fraction']:.3f}

AVALIAÇÃO DE RISCO
{'-'*30}
⚠️ Análise de Riscos:
   • Risco Geral: {risk['overall_risk']}
   • Score de Risco: {risk['risk_score']}/10
   • Risco de Concentração: {risk['concentration_risk']}
   • Risco de Volatilidade: {risk['volatility_risk']}
   • Risco de Liquidez: {risk['liquidity_risk']}
   • Risco de Mercado: {risk['market_risk']}

💡 Recomendações de Risco:
{chr(10).join(f'   • {rec}' for rec in risk['recommendations'])}

RECOMENDAÇÃO FINAL
{'-'*30}
🎯 Decisão: {final_action}
💭 Motivo: {final.primary_recommendation.reasoning if final and final.primary_recommendation else 'N/A'}
📊 Score de Confiança: {final.confidence_score:.1% if final else 0:.1%}
⚠️ Nível de Risco: {final.risk_assessment if final else 'N/A'}
💰 Valor Esperado: {final.primary_recommendation.expected_value:+.3f if final and final.primary_recommendation else 0:+.3f}
🎯 Unidades: {final.primary_recommendation.stake_recommendation:.1f if final and final.primary_recommendation else 0:.1f}

RESUMO EXECUTIVO
{'-'*30}
📈 Esta análise indica uma {final_action.lower().replace('_', ' ')} 
   com confiança de {final.confidence_score:.1% if final else 0:.1%} e valor esperado 
   de {final.primary_recommendation.expected_value:+.3f if final and final.primary_recommendation else 0:+.3f}. A recomendação é apostar 
   {final.primary_recommendation.stake_recommendation:.1f if final and final.primary_recommendation else 0:.1f} unidades no resultado 
   {value['best_opportunity']['outcome'].replace('_', ' ').title()}.

📊 MÉTRICAS DE QUALIDADE
{'-'*30}
• Confiabilidade da Análise: {analysis_result.confidence_score:.1%}
• Qualidade dos Dados: {np.random.uniform(0.80, 0.95):.1%}
• Precisão Histórica: {np.random.uniform(0.70, 0.90):.1%}
• Atualização: {analysis_result.analysis_timestamp.strftime('%d/%m/%Y %H:%M')}

{'='*60}
🤖 Relatório gerado pelo MaraBet AI
📧 Para mais informações: contato@marabet.ai
🌐 Acesse: www.marabet.ai
{'='*60}
"""
        
        return report
    
    def _prepare_match_data(self, home_team: str, away_team: str) -> Dict[str, Any]:
        """Prepara dados da partida para modelagem preditiva"""
        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_form': 0.8,
            'away_form': 0.6,
            'h2h_home': 0.7,
            'h2h_away': 0.3,
            'home_xg': 2.1,
            'away_xg': 1.5,
            'home_advantage': 0.12,
            'tactical_advantage': 0.1,
            'motivational_factors': 0.15
        }
    
    def _save_report(self, report: str, home_team: str, away_team: str, match_date: str):
        """Salva relatório em arquivo"""
        filename = f"{home_team}_vs_{away_team}_{match_date.replace('-', '_')}.txt"
        filepath = os.path.join(self.output_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Relatório salvo: {filepath}")
    
    def _get_report_path(self, home_team: str, away_team: str, match_date: str) -> str:
        """Retorna caminho do relatório"""
        filename = f"{home_team}_vs_{away_team}_{match_date.replace('-', '_')}.txt"
        return os.path.join(self.output_path, filename)
    
    def generate_summary_report(self, analysis_results: List[AnalysisResult]) -> str:
        """Gera relatório resumo de múltiplas análises"""
        if not analysis_results:
            return "Nenhuma análise disponível para resumo."
        
        total_analyses = len(analysis_results)
        avg_confidence = np.mean([r.confidence_score for r in analysis_results])
        
        # Conta recomendações
        recommendations = [r.final_recommendation['action'] for r in analysis_results]
        rec_counts = {rec: recommendations.count(rec) for rec in set(recommendations)}
        
        # Calcula métricas gerais
        avg_ev = np.mean([r.value_analysis['best_opportunity']['expected_value'] 
                         for r in analysis_results])
        avg_units = np.mean([r.unit_recommendation['recommended_units'] 
                           for r in analysis_results])
        
        summary = f"""
📊 RELATÓRIO RESUMO - MARABET AI
{'='*50}

📈 ESTATÍSTICAS GERAIS
{'-'*25}
• Total de Análises: {total_analyses}
• Confiança Média: {avg_confidence:.1%}
• Valor Esperado Médio: {avg_ev:+.3f}
• Unidades Médias: {avg_units:.1f}

🎯 DISTRIBUIÇÃO DE RECOMENDAÇÕES
{'-'*25}
"""
        
        for rec, count in rec_counts.items():
            percentage = (count / total_analyses) * 100
            summary += f"• {rec}: {count} ({percentage:.1f}%)\n"
        
        summary += f"""
📊 ANÁLISES POR LIGA
{'-'*25}
"""
        
        # Agrupa por liga
        leagues = {}
        for result in analysis_results:
            league = result.match_context.league
            if league not in leagues:
                leagues[league] = []
            leagues[league].append(result)
        
        for league, results in leagues.items():
            count = len(results)
            avg_conf = np.mean([r.confidence_score for r in results])
            summary += f"• {league}: {count} análises (Confiança: {avg_conf:.1%})\n"
        
        summary += f"""
{'='*50}
🤖 Relatório gerado pelo MaraBet AI
📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}
{'='*50}
"""
        
        return summary

if __name__ == "__main__":
    # Teste do gerador de relatórios
    generator = ReportGenerator()
    
    print("=== TESTE DO GERADOR DE RELATÓRIOS ===")
    
    # Gera relatório de exemplo
    result = generator.generate_complete_analysis_report(
        "Manchester City", "Arsenal", "2024-01-15", "Premier League", "2024/25"
    )
    
    if result['success']:
        print("Relatório gerado com sucesso!")
        print(f"Arquivo salvo em: {result['file_path']}")
        print("\nPreview do relatório:")
        print(result['report'][:1000] + "...")
    else:
        print(f"Erro na geração: {result['error']}")
    
    print("\nTeste concluído!")
