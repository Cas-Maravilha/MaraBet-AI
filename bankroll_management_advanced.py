"""
Gestão de Banca Avançada - MaraBet AI
Sistema especializado para gestão de banca com Kelly Fracionado e adaptação para Angola
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
class BankrollRecommendation:
    """Recomendação de gestão de banca"""
    method: str
    stake_percentage: float
    stake_amount: float
    kelly_fractional: float
    kelly_full: float
    conservative_recommendation: float
    risk_level: str
    reasoning: str
    currency: str
    local_amount: float

@dataclass
class BankrollAnalysis:
    """Análise completa de gestão de banca"""
    home_team: str
    away_team: str
    match_date: str
    probability: float
    odds: float
    bankroll_amount: float
    currency: str
    recommendations: List[BankrollRecommendation]
    best_recommendation: BankrollRecommendation
    risk_assessment: str
    market_adaptation: Dict[str, Any]
    analysis_timestamp: datetime

class AdvancedBankrollManager:
    """
    Gestor Avançado de Banca
    Sistema completo de gestão de banca com Kelly Fracionado e adaptação para Angola
    """
    
    def __init__(self):
        self.kelly_fraction = 0.25  # Kelly Fracionado (1/4)
        self.conservative_multiplier = 0.5  # Multiplicador conservador
        self.angola_currency = "AOA"  # Kwanza Angolano
        self.exchange_rates = self._load_exchange_rates()
        self.risk_levels = self._load_risk_levels()
        
    def _load_exchange_rates(self) -> Dict[str, float]:
        """Carrega taxas de câmbio para Angola"""
        return {
            "USD_to_AOA": 850.0,  # 1 USD = 850 AOA (aproximado)
            "EUR_to_AOA": 920.0,  # 1 EUR = 920 AOA (aproximado)
            "BRL_to_AOA": 170.0,  # 1 BRL = 170 AOA (aproximado)
        }
    
    def _load_risk_levels(self) -> Dict[str, Dict]:
        """Carrega níveis de risco"""
        return {
            'very_low': {'min': 0.00, 'max': 0.02, 'label': 'MUITO BAIXO', 'color': '🟢'},
            'low': {'min': 0.02, 'max': 0.05, 'label': 'BAIXO', 'color': '🟡'},
            'medium': {'min': 0.05, 'max': 0.10, 'label': 'MÉDIO', 'color': '🟠'},
            'high': {'min': 0.10, 'max': 0.20, 'label': 'ALTO', 'color': '🔴'},
            'very_high': {'min': 0.20, 'max': 1.00, 'label': 'MUITO ALTO', 'color': '⚫'}
        }
    
    def calculate_kelly_fractional(self, probability: float, odds: float) -> float:
        """
        Calcula Kelly Fracionado (1/4)
        Fórmula: [(P × O) - 1] / (O - 1) × 0.25
        """
        if odds <= 1.0 or probability <= 0.0 or probability >= 1.0:
            return 0.0
        
        kelly_full = ((probability * odds) - 1) / (odds - 1)
        kelly_fractional = kelly_full * self.kelly_fraction
        
        # Limita entre 0 e 0.25 (máximo 25% da banca)
        return max(0.0, min(kelly_fractional, 0.25))
    
    def calculate_kelly_full(self, probability: float, odds: float) -> float:
        """
        Calcula Kelly Completo
        Fórmula: [(P × O) - 1] / (O - 1)
        """
        if odds <= 1.0 or probability <= 0.0 or probability >= 1.0:
            return 0.0
        
        kelly_full = ((probability * odds) - 1) / (odds - 1)
        
        # Limita entre 0 e 0.50 (máximo 50% da banca)
        return max(0.0, min(kelly_full, 0.50))
    
    def calculate_conservative_recommendation(self, kelly_fractional: float) -> float:
        """
        Calcula recomendação conservadora
        Aplica multiplicador conservador ao Kelly Fracionado
        """
        return kelly_fractional * self.conservative_multiplier
    
    def convert_to_angola_currency(self, amount_usd: float) -> float:
        """Converte valor em USD para Kwanza Angolano"""
        return amount_usd * self.exchange_rates["USD_to_AOA"]
    
    def format_angola_currency(self, amount: float) -> str:
        """Formata valor em moeda angolana"""
        return f"{amount:,.0f} {self.angola_currency}"
    
    def generate_bankroll_recommendations(self, probability: float, odds: float, 
                                        bankroll_amount: float, 
                                        currency: str = "USD") -> List[BankrollRecommendation]:
        """Gera recomendações de gestão de banca"""
        
        recommendations = []
        
        # Kelly Fracionado
        kelly_fractional = self.calculate_kelly_fractional(probability, odds)
        kelly_fractional_amount = bankroll_amount * kelly_fractional
        
        recommendations.append(BankrollRecommendation(
            method="Kelly Fracionado (1/4)",
            stake_percentage=kelly_fractional * 100,
            stake_amount=kelly_fractional_amount,
            kelly_fractional=kelly_fractional,
            kelly_full=self.calculate_kelly_full(probability, odds),
            conservative_recommendation=self.calculate_conservative_recommendation(kelly_fractional),
            risk_level=self._get_risk_level(kelly_fractional),
            reasoning=f"Kelly Fracionado: {kelly_fractional:.1%} da banca",
            currency=currency,
            local_amount=self.convert_to_angola_currency(kelly_fractional_amount) if currency == "USD" else kelly_fractional_amount
        ))
        
        # Kelly Completo
        kelly_full = self.calculate_kelly_full(probability, odds)
        kelly_full_amount = bankroll_amount * kelly_full
        
        recommendations.append(BankrollRecommendation(
            method="Kelly Completo",
            stake_percentage=kelly_full * 100,
            stake_amount=kelly_full_amount,
            kelly_fractional=kelly_fractional,
            kelly_full=kelly_full,
            conservative_recommendation=self.calculate_conservative_recommendation(kelly_full),
            risk_level=self._get_risk_level(kelly_full),
            reasoning=f"Kelly Completo: {kelly_full:.1%} da banca",
            currency=currency,
            local_amount=self.convert_to_angola_currency(kelly_full_amount) if currency == "USD" else kelly_full_amount
        ))
        
        # Recomendação Conservadora
        conservative = self.calculate_conservative_recommendation(kelly_fractional)
        conservative_amount = bankroll_amount * conservative
        
        recommendations.append(BankrollRecommendation(
            method="Recomendação Conservadora",
            stake_percentage=conservative * 100,
            stake_amount=conservative_amount,
            kelly_fractional=kelly_fractional,
            kelly_full=kelly_full,
            conservative_recommendation=conservative,
            risk_level=self._get_risk_level(conservative),
            reasoning=f"Conservadora: {conservative:.1%} da banca (2-3% recomendado)",
            currency=currency,
            local_amount=self.convert_to_angola_currency(conservative_amount) if currency == "USD" else conservative_amount
        ))
        
        # Unidade Fixa
        unit_fixed = 0.02  # 2% da banca
        unit_fixed_amount = bankroll_amount * unit_fixed
        
        recommendations.append(BankrollRecommendation(
            method="Unidade Fixa (2u)",
            stake_percentage=unit_fixed * 100,
            stake_amount=unit_fixed_amount,
            kelly_fractional=kelly_fractional,
            kelly_full=kelly_full,
            conservative_recommendation=conservative,
            risk_level=self._get_risk_level(unit_fixed),
            reasoning="Unidade fixa: 2% da banca (2 unidades)",
            currency=currency,
            local_amount=self.convert_to_angola_currency(unit_fixed_amount) if currency == "USD" else unit_fixed_amount
        ))
        
        # Percentual Fixo
        percent_fixed = 0.025  # 2.5% da banca
        percent_fixed_amount = bankroll_amount * percent_fixed
        
        recommendations.append(BankrollRecommendation(
            method="Percentual Fixo (2.5%)",
            stake_percentage=percent_fixed * 100,
            stake_amount=percent_fixed_amount,
            kelly_fractional=kelly_fractional,
            kelly_full=kelly_full,
            conservative_recommendation=conservative,
            risk_level=self._get_risk_level(percent_fixed),
            reasoning="Percentual fixo: 2.5% da banca",
            currency=currency,
            local_amount=self.convert_to_angola_currency(percent_fixed_amount) if currency == "USD" else percent_fixed_amount
        ))
        
        return recommendations
    
    def _get_risk_level(self, stake_percentage: float) -> str:
        """Determina nível de risco baseado no percentual"""
        for level, config in self.risk_levels.items():
            if config['min'] <= stake_percentage <= config['max']:
                return config['label']
        return "MUITO ALTO"
    
    def generate_bankroll_analysis(self, home_team: str, away_team: str, 
                                 match_date: str, probability: float, 
                                 odds: float, bankroll_amount: float,
                                 currency: str = "USD") -> BankrollAnalysis:
        """Gera análise completa de gestão de banca"""
        
        logger.info(f"Gerando análise de banca: {home_team} vs {away_team}")
        
        try:
            # Gera recomendações
            recommendations = self.generate_bankroll_recommendations(
                probability, odds, bankroll_amount, currency
            )
            
            # Seleciona melhor recomendação (Kelly Fracionado)
            best_recommendation = recommendations[0]
            
            # Avalia risco geral
            risk_assessment = self._assess_overall_risk(recommendations)
            
            # Adaptação para mercado de Angola
            market_adaptation = self._generate_market_adaptation(bankroll_amount, currency)
            
            return BankrollAnalysis(
                home_team=home_team,
                away_team=away_team,
                match_date=match_date,
                probability=probability,
                odds=odds,
                bankroll_amount=bankroll_amount,
                currency=currency,
                recommendations=recommendations,
                best_recommendation=best_recommendation,
                risk_assessment=risk_assessment,
                market_adaptation=market_adaptation,
                analysis_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de banca: {e}")
            return self._create_empty_analysis(home_team, away_team, match_date)
    
    def _assess_overall_risk(self, recommendations: List[BankrollRecommendation]) -> str:
        """Avalia risco geral baseado nas recomendações"""
        if not recommendations:
            return "ALTO"
        
        # Usa a recomendação conservadora como base
        conservative_rec = next((r for r in recommendations if "Conservadora" in r.method), None)
        if conservative_rec:
            return conservative_rec.risk_level
        
        return "MÉDIO"
    
    def _generate_market_adaptation(self, bankroll_amount: float, currency: str) -> Dict[str, Any]:
        """Gera adaptação para mercado de Angola"""
        return {
            "angola_currency": self.angola_currency,
            "exchange_rate": self.exchange_rates["USD_to_AOA"],
            "local_amount": self.convert_to_angola_currency(bankroll_amount) if currency == "USD" else bankroll_amount,
            "local_formatted": self.format_angola_currency(self.convert_to_angola_currency(bankroll_amount) if currency == "USD" else bankroll_amount),
            "market_characteristics": [
                "Mercado de apostas em crescimento",
                "Regulamentação em desenvolvimento",
                "Moeda local: Kwanza Angolano (AOA)",
                "Taxa de câmbio flutuante",
                "Recomendação: Stake conservador"
            ]
        }
    
    def _create_empty_analysis(self, home_team: str, away_team: str, match_date: str) -> BankrollAnalysis:
        """Cria análise vazia em caso de erro"""
        return BankrollAnalysis(
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            probability=0.0,
            odds=0.0,
            bankroll_amount=0.0,
            currency="USD",
            recommendations=[],
            best_recommendation=None,
            risk_assessment="ALTO",
            market_adaptation={},
            analysis_timestamp=datetime.now()
        )
    
    def format_bankroll_analysis(self, analysis: BankrollAnalysis) -> str:
        """Formata análise de gestão de banca"""
        
        if not analysis or not analysis.recommendations:
            return "Análise de gestão de banca não disponível."
        
        report_parts = []
        
        # Cabeçalho
        report_parts.append("GESTÃO DE BANCA")
        report_parts.append("=" * 60)
        report_parts.append(f"Partida: {analysis.home_team} vs {analysis.away_team}")
        report_parts.append(f"Data: {analysis.match_date}")
        report_parts.append(f"Probabilidade: {analysis.probability:.1%}")
        report_parts.append(f"Odd: {analysis.odds:.2f}")
        report_parts.append(f"Banca: {analysis.bankroll_amount:,.2f} {analysis.currency}")
        report_parts.append("")
        
        # Cálculo do Kelly Fracionado
        kelly_fractional = analysis.best_recommendation.kelly_fractional
        kelly_full = analysis.best_recommendation.kelly_full
        
        report_parts.append("CÁLCULO DO KELLY FRACIONADO")
        report_parts.append("-" * 40)
        report_parts.append(f"P = {analysis.probability:.2f} (probabilidade)")
        report_parts.append(f"O = {analysis.odds:.2f} (odd)")
        report_parts.append(f"Kelly Fracionado (1/4) = [(P × O) - 1] / (O - 1) × 0.25")
        report_parts.append(f"= [({analysis.probability:.2f} × {analysis.odds:.2f}) - 1] / ({analysis.odds:.2f} - 1) × 0.25")
        report_parts.append(f"= [{analysis.probability * analysis.odds:.3f} - 1] / {analysis.odds - 1:.2f} × 0.25")
        report_parts.append(f"= {kelly_full:.3f} × 0.25")
        report_parts.append(f"= {kelly_fractional:.3f} = {kelly_fractional:.1%} da banca")
        report_parts.append("")
        
        # Recomendação Conservadora
        conservative = analysis.best_recommendation.conservative_recommendation
        report_parts.append("RECOMENDAÇÃO CONSERVADORA")
        report_parts.append("-" * 40)
        report_parts.append(f"Kelly Fracionado: {kelly_fractional:.1%} da banca")
        report_parts.append(f"Recomendação Conservadora: {conservative:.1%} da banca")
        report_parts.append(f"Valor: {analysis.best_recommendation.stake_amount:,.2f} {analysis.currency}")
        report_parts.append("")
        
        # Tabela de Métodos
        report_parts.append("MÉTODOS DE GESTÃO DE BANCA")
        report_parts.append("-" * 40)
        report_parts.append("Método\t\t\tBanca de R$ 1.000\tBanca de R$ 5.000")
        report_parts.append("-" * 80)
        
        for rec in analysis.recommendations:
            amount_1k = rec.stake_amount if analysis.bankroll_amount == 1000 else rec.stake_amount * (1000 / analysis.bankroll_amount)
            amount_5k = rec.stake_amount if analysis.bankroll_amount == 5000 else rec.stake_amount * (5000 / analysis.bankroll_amount)
            
            method_name = rec.method[:20] + "..." if len(rec.method) > 20 else rec.method
            report_parts.append(f"{method_name:<20}\tR$ {amount_1k:,.0f}\t\tR$ {amount_5k:,.0f}")
        
        report_parts.append("")
        
        # Adaptação para Angola
        if analysis.market_adaptation:
            report_parts.append("ADAPTAÇÃO PARA MERCADO DE ANGOLA")
            report_parts.append("-" * 40)
            report_parts.append(f"Moeda Local: {analysis.market_adaptation['angola_currency']}")
            report_parts.append(f"Taxa de Câmbio: 1 USD = {analysis.market_adaptation['exchange_rate']:,.0f} AOA")
            report_parts.append(f"Valor Local: {analysis.market_adaptation['local_formatted']}")
            report_parts.append("")
            
            report_parts.append("Características do Mercado:")
            for char in analysis.market_adaptation['market_characteristics']:
                report_parts.append(f"• {char}")
            report_parts.append("")
        
        # Resumo Executivo
        report_parts.append("RESUMO EXECUTIVO")
        report_parts.append("-" * 40)
        report_parts.append(f"• Melhor Método: {analysis.best_recommendation.method}")
        report_parts.append(f"• Stake Recomendado: {analysis.best_recommendation.stake_percentage:.1f}% da banca")
        report_parts.append(f"• Valor: {analysis.best_recommendation.stake_amount:,.2f} {analysis.currency}")
        report_parts.append(f"• Nível de Risco: {analysis.best_recommendation.risk_level}")
        report_parts.append(f"• Razão: {analysis.best_recommendation.reasoning}")
        
        return "\n".join(report_parts)

if __name__ == "__main__":
    # Teste do gestor de banca avançado
    manager = AdvancedBankrollManager()
    
    print("=== TESTE DO GESTOR DE BANCA AVANÇADO ===")
    
    # Dados de exemplo
    probability = 0.68
    odds = 1.65
    bankroll_amount = 1000.0
    currency = "USD"
    
    # Gera análise
    analysis = manager.generate_bankroll_analysis(
        "Manchester City", "Arsenal", "2024-01-15", 
        probability, odds, bankroll_amount, currency
    )
    
    # Formata análise
    report = manager.format_bankroll_analysis(analysis)
    
    print(report)
    
    print("\nTeste concluído!")
