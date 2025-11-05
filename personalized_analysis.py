"""
Análise Personalizada - MaraBet AI
Sistema especializado para análise customizada baseada em dados específicos do usuário
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """Perfil do usuário"""
    name: str
    risk_profile: str  # conservador, moderado, agressivo
    bankroll: float
    currency: str
    experience_level: str  # iniciante, intermediario, avancado
    preferred_leagues: List[str]
    preferred_markets: List[str]
    max_stake_percent: float
    stop_loss_percent: float
    target_roi: float

@dataclass
class MatchRequest:
    """Solicitação de análise de partida"""
    home_team: str
    away_team: str
    league: str
    match_date: str
    current_odds: Dict[str, float]
    user_profile: UserProfile
    additional_info: Dict[str, Any]

@dataclass
class PersonalizedAnalysis:
    """Análise personalizada"""
    match_request: MatchRequest
    recommended_markets: List[Dict[str, Any]]
    stake_recommendations: Dict[str, float]
    risk_assessment: Dict[str, Any]
    confidence_levels: Dict[str, float]
    expected_values: Dict[str, float]
    kelly_recommendations: Dict[str, float]
    warnings: List[str]
    opportunities: List[str]
    analysis_timestamp: datetime

class PersonalizedAnalysisGenerator:
    """
    Gerador de Análise Personalizada
    Sistema completo para análise customizada baseada em perfil do usuário
    """
    
    def __init__(self):
        self.risk_profiles = self._load_risk_profiles()
        self.league_analysis = self._load_league_analysis()
        self.market_analysis = self._load_market_analysis()
        self.stake_calculator = self._load_stake_calculator()
        
    def _load_risk_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Carrega perfis de risco"""
        return {
            'conservador': {
                'max_stake_percent': 0.02,  # 2%
                'kelly_fraction': 0.125,    # 1/8
                'stop_loss_percent': 0.10,  # 10%
                'min_confidence': 0.80,     # 80%
                'min_ev': 0.10,             # 10%
                'max_drawdown': 0.15,       # 15%
                'description': 'Perfil conservador - Foco na preservação do capital'
            },
            'moderado': {
                'max_stake_percent': 0.05,  # 5%
                'kelly_fraction': 0.25,     # 1/4
                'stop_loss_percent': 0.20,  # 20%
                'min_confidence': 0.70,     # 70%
                'min_ev': 0.05,             # 5%
                'max_drawdown': 0.25,       # 25%
                'description': 'Perfil moderado - Equilíbrio entre risco e retorno'
            },
            'agressivo': {
                'max_stake_percent': 0.10,  # 10%
                'kelly_fraction': 0.50,     # 1/2
                'stop_loss_percent': 0.30,  # 30%
                'min_confidence': 0.60,     # 60%
                'min_ev': 0.03,             # 3%
                'max_drawdown': 0.40,       # 40%
                'description': 'Perfil agressivo - Busca por retornos elevados'
            }
        }
    
    def _load_league_analysis(self) -> Dict[str, Dict[str, Any]]:
        """Carrega análise por liga"""
        return {
            'Premier League': {
                'difficulty': 'alta',
                'volatility': 'media',
                'data_quality': 'excelente',
                'recommended_markets': ['Over/Under 2.5', 'Ambas Marcam', 'Resultado'],
                'confidence_multiplier': 1.0
            },
            'La Liga': {
                'difficulty': 'alta',
                'volatility': 'baixa',
                'data_quality': 'excelente',
                'recommended_markets': ['Over/Under 2.5', 'Ambas Marcam', 'Resultado'],
                'confidence_multiplier': 1.0
            },
            'Serie A': {
                'difficulty': 'media',
                'volatility': 'media',
                'data_quality': 'boa',
                'recommended_markets': ['Over/Under 2.5', 'Ambas Marcam', 'Resultado'],
                'confidence_multiplier': 0.95
            },
            'Bundesliga': {
                'difficulty': 'media',
                'volatility': 'alta',
                'data_quality': 'boa',
                'recommended_markets': ['Over/Under 2.5', 'Ambas Marcam', 'Resultado'],
                'confidence_multiplier': 0.90
            },
            'Ligue 1': {
                'difficulty': 'baixa',
                'volatility': 'alta',
                'data_quality': 'media',
                'recommended_markets': ['Over/Under 2.5', 'Ambas Marcam', 'Resultado'],
                'confidence_multiplier': 0.85
            },
            'Champions League': {
                'difficulty': 'muito_alta',
                'volatility': 'baixa',
                'data_quality': 'excelente',
                'recommended_markets': ['Over/Under 2.5', 'Ambas Marcam', 'Resultado'],
                'confidence_multiplier': 1.1
            }
        }
    
    def _load_market_analysis(self) -> Dict[str, Dict[str, Any]]:
        """Carrega análise por mercado"""
        return {
            'Over/Under 2.5': {
                'difficulty': 'baixa',
                'volatility': 'media',
                'data_availability': 'excelente',
                'recommended_for': ['iniciante', 'intermediario', 'avancado'],
                'confidence_multiplier': 1.0
            },
            'Ambas Marcam': {
                'difficulty': 'media',
                'volatility': 'baixa',
                'data_availability': 'boa',
                'recommended_for': ['intermediario', 'avancado'],
                'confidence_multiplier': 0.95
            },
            'Resultado': {
                'difficulty': 'alta',
                'volatility': 'alta',
                'data_availability': 'excelente',
                'recommended_for': ['avancado'],
                'confidence_multiplier': 0.90
            },
            'Over/Under 1.5': {
                'difficulty': 'baixa',
                'volatility': 'baixa',
                'data_availability': 'excelente',
                'recommended_for': ['iniciante', 'intermediario'],
                'confidence_multiplier': 1.05
            },
            'Over/Under 3.5': {
                'difficulty': 'media',
                'volatility': 'alta',
                'data_availability': 'boa',
                'recommended_for': ['intermediario', 'avancado'],
                'confidence_multiplier': 0.90
            }
        }
    
    def _load_stake_calculator(self) -> Dict[str, Any]:
        """Carrega calculadora de stake"""
        return {
            'base_formula': 'Stake = (Kelly Fraction × EV × Bankroll) / (Odd - 1)',
            'risk_adjustment': 'Stake = Base Stake × Risk Profile Multiplier',
            'max_stake_formula': 'Max Stake = Bankroll × Max Stake Percent',
            'min_stake_formula': 'Min Stake = Bankroll × 0.001'  # 0.1%
        }
    
    def create_user_profile(self, name: str, risk_profile: str, bankroll: float, 
                          currency: str = "BRL", experience_level: str = "intermediario",
                          preferred_leagues: List[str] = None, 
                          preferred_markets: List[str] = None) -> UserProfile:
        """Cria perfil do usuário"""
        
        if preferred_leagues is None:
            preferred_leagues = ["Premier League", "La Liga", "Serie A"]
        
        if preferred_markets is None:
            preferred_markets = ["Over/Under 2.5", "Ambas Marcam"]
        
        # Obtém configurações do perfil de risco
        risk_config = self.risk_profiles.get(risk_profile, self.risk_profiles['moderado'])
        
        return UserProfile(
            name=name,
            risk_profile=risk_profile,
            bankroll=bankroll,
            currency=currency,
            experience_level=experience_level,
            preferred_leagues=preferred_leagues,
            preferred_markets=preferred_markets,
            max_stake_percent=risk_config['max_stake_percent'],
            stop_loss_percent=risk_config['stop_loss_percent'],
            target_roi=risk_config.get('target_roi', 0.15)  # 15% padrão
        )
    
    def create_match_request(self, home_team: str, away_team: str, league: str,
                           match_date: str, current_odds: Dict[str, float],
                           user_profile: UserProfile, 
                           additional_info: Dict[str, Any] = None) -> MatchRequest:
        """Cria solicitação de análise de partida"""
        
        if additional_info is None:
            additional_info = {}
        
        return MatchRequest(
            home_team=home_team,
            away_team=away_team,
            league=league,
            match_date=match_date,
            current_odds=current_odds,
            user_profile=user_profile,
            additional_info=additional_info
        )
    
    def analyze_recommended_markets(self, match_request: MatchRequest) -> List[Dict[str, Any]]:
        """Analisa mercados recomendados"""
        
        recommended_markets = []
        
        # Obtém configurações da liga
        league_config = self.league_analysis.get(match_request.league, 
                                                self.league_analysis['Premier League'])
        
        # Analisa cada mercado
        for market in match_request.user_profile.preferred_markets:
            if market in match_request.current_odds:
                market_config = self.market_analysis.get(market, 
                                                       self.market_analysis['Over/Under 2.5'])
                
                # Simula análise (em produção, integraria com modelos reais)
                confidence = self._calculate_market_confidence(market, match_request)
                expected_value = self._calculate_expected_value(market, match_request)
                probability = self._calculate_market_probability(market, match_request)
                
                # Aplica multiplicadores
                confidence *= league_config['confidence_multiplier']
                confidence *= market_config['confidence_multiplier']
                
                recommended_markets.append({
                    'market': market,
                    'odd': match_request.current_odds[market],
                    'probability': probability,
                    'expected_value': expected_value,
                    'confidence': confidence,
                    'recommended': confidence >= match_request.user_profile.max_stake_percent,
                    'difficulty': market_config['difficulty'],
                    'volatility': market_config['volatility'],
                    'data_availability': market_config['data_availability']
                })
        
        # Ordena por valor esperado
        recommended_markets.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return recommended_markets
    
    def calculate_stake_recommendations(self, match_request: MatchRequest, 
                                      recommended_markets: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcula recomendações de stake"""
        
        stake_recommendations = {}
        risk_config = self.risk_profiles[match_request.user_profile.risk_profile]
        
        for market_data in recommended_markets:
            if market_data['recommended']:
                market = market_data['market']
                odd = market_data['odd']
                probability = market_data['probability']
                expected_value = market_data['expected_value']
                confidence = market_data['confidence']
                
                # Calcula Kelly Criterion
                kelly_fraction = risk_config['kelly_fraction']
                kelly_stake = self._calculate_kelly_stake(
                    probability, odd, kelly_fraction, match_request.user_profile.bankroll
                )
                
                # Aplica limites do perfil de risco
                max_stake = match_request.user_profile.bankroll * match_request.user_profile.max_stake_percent
                min_stake = match_request.user_profile.bankroll * 0.001  # 0.1%
                
                # Ajusta stake baseado na confiança
                confidence_multiplier = min(confidence / 0.8, 1.0)  # Normaliza para 0.8
                adjusted_stake = kelly_stake * confidence_multiplier
                
                # Aplica limites
                final_stake = max(min_stake, min(adjusted_stake, max_stake))
                
                stake_recommendations[market] = {
                    'stake_amount': final_stake,
                    'stake_percent': (final_stake / match_request.user_profile.bankroll) * 100,
                    'kelly_stake': kelly_stake,
                    'confidence_multiplier': confidence_multiplier,
                    'max_stake': max_stake,
                    'min_stake': min_stake
                }
        
        return stake_recommendations
    
    def _calculate_kelly_stake(self, probability: float, odd: float, 
                             kelly_fraction: float, bankroll: float) -> float:
        """Calcula stake usando Kelly Criterion"""
        if odd <= 1.0:
            return 0.0
        
        kelly_percent = (probability * odd - 1) / (odd - 1)
        kelly_percent = max(0, kelly_percent)  # Não pode ser negativo
        kelly_percent *= kelly_fraction  # Aplica fração conservadora
        
        return kelly_percent * bankroll
    
    def _calculate_market_confidence(self, market: str, match_request: MatchRequest) -> float:
        """Calcula confiança para um mercado"""
        # Simula cálculo de confiança (em produção, usaria modelos reais)
        base_confidence = np.random.uniform(0.6, 0.9)
        
        # Ajusta baseado no perfil de risco
        risk_config = self.risk_profiles[match_request.user_profile.risk_profile]
        if base_confidence < risk_config['min_confidence']:
            base_confidence = risk_config['min_confidence']
        
        return base_confidence
    
    def _calculate_expected_value(self, market: str, match_request: MatchRequest) -> float:
        """Calcula valor esperado para um mercado"""
        # Simula cálculo de EV (em produção, usaria modelos reais)
        odd = match_request.current_odds[market]
        probability = np.random.uniform(0.5, 0.8)
        
        return (probability * odd) - 1
    
    def _calculate_market_probability(self, market: str, match_request: MatchRequest) -> float:
        """Calcula probabilidade para um mercado"""
        # Simula cálculo de probabilidade (em produção, usaria modelos reais)
        return np.random.uniform(0.5, 0.8)
    
    def assess_risk(self, match_request: MatchRequest, 
                   recommended_markets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Avalia risco da análise"""
        
        risk_config = self.risk_profiles[match_request.user_profile.risk_profile]
        
        # Calcula métricas de risco
        total_stake_percent = sum(
            market_data.get('stake_percent', 0) for market_data in recommended_markets
        )
        
        avg_confidence = np.mean([market['confidence'] for market in recommended_markets])
        avg_ev = np.mean([market['expected_value'] for market in recommended_markets])
        
        # Determina nível de risco
        if total_stake_percent > risk_config['max_stake_percent'] * 2:
            risk_level = "ALTO"
        elif total_stake_percent > risk_config['max_stake_percent']:
            risk_level = "MÉDIO"
        else:
            risk_level = "BAIXO"
        
        # Gera alertas
        warnings = []
        if total_stake_percent > risk_config['max_stake_percent']:
            warnings.append(f"Stake total ({total_stake_percent:.1%}) excede limite do perfil")
        
        if avg_confidence < risk_config['min_confidence']:
            warnings.append(f"Confiança média ({avg_confidence:.1%}) abaixo do mínimo")
        
        if avg_ev < risk_config['min_ev']:
            warnings.append(f"EV médio ({avg_ev:.1%}) abaixo do mínimo")
        
        return {
            'risk_level': risk_level,
            'total_stake_percent': total_stake_percent,
            'avg_confidence': avg_confidence,
            'avg_expected_value': avg_ev,
            'warnings': warnings,
            'risk_tolerance': risk_config['max_drawdown'],
            'stop_loss_trigger': match_request.user_profile.bankroll * risk_config['stop_loss_percent']
        }
    
    def generate_opportunities(self, match_request: MatchRequest, 
                             recommended_markets: List[Dict[str, Any]]) -> List[str]:
        """Gera oportunidades identificadas"""
        
        opportunities = []
        
        for market_data in recommended_markets:
            if market_data['recommended']:
                market = market_data['market']
                ev = market_data['expected_value']
                confidence = market_data['confidence']
                
                if ev > 0.10:  # EV > 10%
                    opportunities.append(f"{market}: Valor excelente (EV: {ev:.1%})")
                elif ev > 0.05:  # EV > 5%
                    opportunities.append(f"{market}: Valor positivo (EV: {ev:.1%})")
                
                if confidence > 0.85:  # Confiança > 85%
                    opportunities.append(f"{market}: Alta confiança ({confidence:.1%})")
        
        return opportunities
    
    def generate_personalized_analysis(self, match_request: MatchRequest) -> PersonalizedAnalysis:
        """Gera análise personalizada completa"""
        
        logger.info(f"Gerando análise personalizada: {match_request.home_team} vs {match_request.away_team}")
        
        try:
            # Analisa mercados recomendados
            recommended_markets = self.analyze_recommended_markets(match_request)
            
            # Calcula recomendações de stake
            stake_recommendations = self.calculate_stake_recommendations(match_request, recommended_markets)
            
            # Avalia risco
            risk_assessment = self.assess_risk(match_request, recommended_markets)
            
            # Calcula níveis de confiança
            confidence_levels = {market['market']: market['confidence'] for market in recommended_markets}
            
            # Calcula valores esperados
            expected_values = {market['market']: market['expected_value'] for market in recommended_markets}
            
            # Calcula recomendações Kelly
            kelly_recommendations = {market: data['kelly_stake'] for market, data in stake_recommendations.items()}
            
            # Gera oportunidades
            opportunities = self.generate_opportunities(match_request, recommended_markets)
            
            return PersonalizedAnalysis(
                match_request=match_request,
                recommended_markets=recommended_markets,
                stake_recommendations=stake_recommendations,
                risk_assessment=risk_assessment,
                confidence_levels=confidence_levels,
                expected_values=expected_values,
                kelly_recommendations=kelly_recommendations,
                warnings=risk_assessment['warnings'],
                opportunities=opportunities,
                analysis_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro na geração da análise personalizada: {e}")
            return self._create_empty_analysis(match_request)
    
    def _create_empty_analysis(self, match_request: MatchRequest) -> PersonalizedAnalysis:
        """Cria análise vazia em caso de erro"""
        return PersonalizedAnalysis(
            match_request=match_request,
            recommended_markets=[],
            stake_recommendations={},
            risk_assessment={'risk_level': 'DESCONHECIDO', 'warnings': ['Erro na análise']},
            confidence_levels={},
            expected_values={},
            kelly_recommendations={},
            warnings=['Erro na análise'],
            opportunities=[],
            analysis_timestamp=datetime.now()
        )
    
    def format_personalized_analysis(self, analysis: PersonalizedAnalysis) -> str:
        """Formata análise personalizada"""
        
        if not analysis or not analysis.recommended_markets:
            return "Análise personalizada não disponível."
        
        report_parts = []
        
        # Cabeçalho
        report_parts.append("ANÁLISE PERSONALIZADA")
        report_parts.append("=" * 60)
        report_parts.append(f"Partida: {analysis.match_request.home_team} vs {analysis.match_request.away_team}")
        report_parts.append(f"Liga: {analysis.match_request.league}")
        report_parts.append(f"Data: {analysis.match_request.match_date}")
        report_parts.append(f"Usuário: {analysis.match_request.user_profile.name}")
        report_parts.append(f"Perfil de Risco: {analysis.match_request.user_profile.risk_profile.upper()}")
        report_parts.append(f"Banca: {analysis.match_request.user_profile.bankroll:,.2f} {analysis.match_request.user_profile.currency}")
        report_parts.append("")
        
        # Mercados recomendados
        report_parts.append("MERCADOS RECOMENDADOS")
        report_parts.append("-" * 40)
        for market_data in analysis.recommended_markets:
            if market_data['recommended']:
                report_parts.append(f"✅ {market_data['market']}")
                report_parts.append(f"   Odd: {market_data['odd']:.2f}")
                report_parts.append(f"   Probabilidade: {market_data['probability']:.1%}")
                report_parts.append(f"   EV: {market_data['expected_value']:.1%}")
                report_parts.append(f"   Confiança: {market_data['confidence']:.1%}")
                report_parts.append(f"   Dificuldade: {market_data['difficulty']}")
                report_parts.append("")
        
        # Recomendações de stake
        if analysis.stake_recommendations:
            report_parts.append("RECOMENDAÇÕES DE STAKE")
            report_parts.append("-" * 40)
            for market, stake_data in analysis.stake_recommendations.items():
                report_parts.append(f"💰 {market}")
                report_parts.append(f"   Stake: {stake_data['stake_amount']:,.2f} {analysis.match_request.user_profile.currency}")
                report_parts.append(f"   Percentual: {stake_data['stake_percent']:.2f}%")
                report_parts.append(f"   Kelly: {stake_data['kelly_stake']:,.2f} {analysis.match_request.user_profile.currency}")
                report_parts.append(f"   Multiplicador: {stake_data['confidence_multiplier']:.2f}")
                report_parts.append("")
        
        # Avaliação de risco
        risk = analysis.risk_assessment
        report_parts.append("AVALIAÇÃO DE RISCO")
        report_parts.append("-" * 40)
        report_parts.append(f"Nível de Risco: {risk['risk_level']}")
        report_parts.append(f"Stake Total: {risk['total_stake_percent']:.2f}%")
        report_parts.append(f"Confiança Média: {risk['avg_confidence']:.1%}")
        report_parts.append(f"EV Médio: {risk['avg_expected_value']:.1%}")
        report_parts.append(f"Tolerância: {risk['risk_tolerance']:.1%}")
        report_parts.append("")
        
        # Alertas
        if analysis.warnings:
            report_parts.append("⚠️ ALERTAS")
            report_parts.append("-" * 40)
            for warning in analysis.warnings:
                report_parts.append(f"• {warning}")
            report_parts.append("")
        
        # Oportunidades
        if analysis.opportunities:
            report_parts.append("🎯 OPORTUNIDADES")
            report_parts.append("-" * 40)
            for opportunity in analysis.opportunities:
                report_parts.append(f"• {opportunity}")
            report_parts.append("")
        
        # Timestamp
        report_parts.append("📅 Análise Gerada")
        report_parts.append("-" * 40)
        report_parts.append(f"Data/Hora: {analysis.analysis_timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
        
        return "\n".join(report_parts)

if __name__ == "__main__":
    # Teste do gerador de análise personalizada
    generator = PersonalizedAnalysisGenerator()
    
    print("=== TESTE DO GERADOR DE ANÁLISE PERSONALIZADA ===")
    
    # Cria perfil do usuário
    user_profile = generator.create_user_profile(
        name="João Silva",
        risk_profile="moderado",
        bankroll=1000.0,
        currency="BRL",
        experience_level="intermediario",
        preferred_leagues=["Premier League", "La Liga"],
        preferred_markets=["Over/Under 2.5", "Ambas Marcam"]
    )
    
    # Cria solicitação de análise
    match_request = generator.create_match_request(
        home_team="Manchester City",
        away_team="Arsenal",
        league="Premier League",
        match_date="2024-01-15",
        current_odds={
            "Over/Under 2.5": 1.65,
            "Ambas Marcam": 1.45,
            "Resultado": 2.10
        },
        user_profile=user_profile
    )
    
    # Gera análise personalizada
    analysis = generator.generate_personalized_analysis(match_request)
    
    # Formata análise
    report = generator.format_personalized_analysis(analysis)
    
    print(report)
    
    print("\nTeste concluído!")
