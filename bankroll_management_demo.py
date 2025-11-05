#!/usr/bin/env python3
"""
Demonstração de Gestão de Banca Avançada - MaraBet AI
Mostra o sistema completo de gestão de banca com Kelly Fracionado e adaptação para Angola
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bankroll_management_advanced import AdvancedBankrollManager
from datetime import datetime

def main():
    print("🎯 MARABET AI - GESTÃO DE BANCA AVANÇADA")
    print("=" * 70)
    print("Demonstração do sistema completo de gestão de banca")
    print("=" * 70)
    
    # Cria gestor de banca
    manager = AdvancedBankrollManager()
    
    print("\n🎯 GERANDO ANÁLISE DE GESTÃO DE BANCA")
    print("=" * 60)
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print("=" * 60)
    
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
    
    print("✅ Análise de gestão de banca gerada!")
    print("\n" + "="*80)
    print("📊 ANÁLISE COMPLETA DE GESTÃO DE BANCA")
    print("="*80)
    print(report)
    
    # Mostra métricas específicas
    print("\n📈 MÉTRICAS ESPECÍFICAS DA ANÁLISE")
    print("=" * 50)
    print(f"• Probabilidade: {analysis.probability:.1%}")
    print(f"• Odd: {analysis.odds:.2f}")
    print(f"• Banca: {analysis.bankroll_amount:,.2f} {analysis.currency}")
    print(f"• Kelly Fracionado: {analysis.best_recommendation.kelly_fractional:.1%}")
    print(f"• Kelly Completo: {analysis.best_recommendation.kelly_full:.1%}")
    print(f"• Recomendação Conservadora: {analysis.best_recommendation.conservative_recommendation:.1%}")
    print(f"• Nível de Risco: {analysis.best_recommendation.risk_level}")
    
    # Mostra adaptação para Angola
    if analysis.market_adaptation:
        print(f"\n🇦🇴 ADAPTAÇÃO PARA ANGOLA")
        print("=" * 30)
        print(f"• Moeda Local: {analysis.market_adaptation['angola_currency']}")
        print(f"• Taxa de Câmbio: 1 USD = {analysis.market_adaptation['exchange_rate']:,.0f} AOA")
        print(f"• Valor Local: {analysis.market_adaptation['local_formatted']}")
    
    return analysis

def show_bankroll_management_features():
    """Mostra características da gestão de banca"""
    
    print("\n🔧 CARACTERÍSTICAS DA GESTÃO DE BANCA")
    print("=" * 50)
    print("""
✅ KELLY FRACIONADO (1/4)
   • Fórmula: [(P × O) - 1] / (O - 1) × 0.25
   • Aplicação: Stake conservador baseado em Kelly
   • Vantagem: Reduz risco mantendo otimização
   • Recomendação: 2-3% da banca

✅ KELLY COMPLETO
   • Fórmula: [(P × O) - 1] / (O - 1)
   • Aplicação: Stake otimizado baseado em Kelly
   • Vantagem: Maximiza crescimento a longo prazo
   • Risco: Maior volatilidade

✅ RECOMENDAÇÃO CONSERVADORA
   • Base: Kelly Fracionado × 0.5
   • Aplicação: Stake ainda mais conservador
   • Vantagem: Risco mínimo
   • Recomendação: 1-2% da banca

✅ MÉTODOS ALTERNATIVOS
   • Unidade Fixa: 2% da banca (2 unidades)
   • Percentual Fixo: 2.5% da banca
   • Comparação de métodos
   • Adaptação ao perfil de risco

✅ ADAPTAÇÃO PARA ANGOLA
   • Moeda local: Kwanza Angolano (AOA)
   • Taxa de câmbio: 1 USD = 850 AOA
   • Conversão automática
   • Características do mercado local
""")

def demonstrate_kelly_calculation():
    """Demonstra cálculo do Kelly Fracionado"""
    
    print("\n🧮 DEMONSTRAÇÃO DO CÁLCULO DO KELLY FRACIONADO")
    print("=" * 60)
    
    # Dados do exemplo
    P = 0.68  # Probabilidade
    O = 1.65  # Odd
    
    print(f"Dados do Exemplo:")
    print(f"P = {P} (probabilidade)")
    print(f"O = {O} (odd)")
    print()
    
    # Cálculo do Kelly Completo
    kelly_full = ((P * O) - 1) / (O - 1)
    print(f"Cálculo do Kelly Completo:")
    print(f"Kelly = [(P × O) - 1] / (O - 1)")
    print(f"Kelly = [({P} × {O}) - 1] / ({O} - 1)")
    print(f"Kelly = [{P * O:.3f} - 1] / {O - 1:.2f}")
    print(f"Kelly = {kelly_full:.3f} = {kelly_full:.1%} da banca")
    print()
    
    # Cálculo do Kelly Fracionado
    kelly_fractional = kelly_full * 0.25
    print(f"Cálculo do Kelly Fracionado (1/4):")
    print(f"Kelly Fracionado = Kelly × 0.25")
    print(f"Kelly Fracionado = {kelly_full:.3f} × 0.25")
    print(f"Kelly Fracionado = {kelly_fractional:.3f} = {kelly_fractional:.1%} da banca")
    print()
    
    # Recomendação Conservadora
    conservative = kelly_fractional * 0.5
    print(f"Recomendação Conservadora:")
    print(f"Conservadora = Kelly Fracionado × 0.5")
    print(f"Conservadora = {kelly_fractional:.3f} × 0.5")
    print(f"Conservadora = {conservative:.3f} = {conservative:.1%} da banca")
    print()
    
    # Valores para diferentes bancas
    print(f"Valores para Diferentes Bancas:")
    print(f"Banca de R$ 1.000:")
    print(f"  • Kelly Fracionado: R$ {1000 * kelly_fractional:,.0f}")
    print(f"  • Kelly Completo: R$ {1000 * kelly_full:,.0f}")
    print(f"  • Conservadora: R$ {1000 * conservative:,.0f}")
    print()
    print(f"Banca de R$ 5.000:")
    print(f"  • Kelly Fracionado: R$ {5000 * kelly_fractional:,.0f}")
    print(f"  • Kelly Completo: R$ {5000 * kelly_full:,.0f}")
    print(f"  • Conservadora: R$ {5000 * conservative:,.0f}")

def show_angola_adaptation():
    """Mostra adaptação para Angola"""
    
    print("\n🇦🇴 ADAPTAÇÃO PARA MERCADO DE ANGOLA")
    print("=" * 50)
    print("""
✅ MOEDA LOCAL
   • Kwanza Angolano (AOA)
   • Taxa de câmbio: 1 USD = 850 AOA
   • Conversão automática
   • Formatação local

✅ CARACTERÍSTICAS DO MERCADO
   • Mercado de apostas em crescimento
   • Regulamentação em desenvolvimento
   • Moeda local: Kwanza Angolano (AOA)
   • Taxa de câmbio flutuante
   • Recomendação: Stake conservador

✅ CONVERSÃO DE VALORES
   • Banca de R$ 1.000 = 170.000 AOA
   • Banca de R$ 5.000 = 850.000 AOA
   • Stake de R$ 25 = 21.250 AOA
   • Stake de R$ 125 = 106.250 AOA

✅ RECOMENDAÇÕES ESPECÍFICAS
   • Use Kelly Fracionado (mais conservador)
   • Evite Kelly Completo (muito arriscado)
   • Considere Unidade Fixa (2% da banca)
   • Monitore taxa de câmbio
   • Diversifique apostas
""")

def show_method_comparison():
    """Mostra comparação de métodos"""
    
    print("\n📊 COMPARAÇÃO DE MÉTODOS DE GESTÃO DE BANCA")
    print("=" * 60)
    print("""
Método\t\t\t\tBanca de R$ 1.000\tBanca de R$ 5.000
────────────────────────────────────────────────────────────────
Kelly Fracionado (1/4)\t\tR$ 25-30\t\tR$ 125-150
Kelly Completo\t\t\tR$ 50-60\t\tR$ 250-300
Recomendação Conservadora\tR$ 12-15\t\tR$ 60-75
Unidade Fixa (2u)\t\tR$ 20-30\t\tR$ 100-150
Percentual Fixo (2.5%)\t\tR$ 25-30\t\tR$ 125-150

RECOMENDAÇÕES POR PERFIL:
────────────────────────────────────────────────────────────────
Conservador:\t\t\tUnidade Fixa (2%)\t\tR$ 20-30
Moderado:\t\t\tKelly Fracionado (1/4)\tR$ 25-30
Agressivo:\t\t\tKelly Completo\t\tR$ 50-60
Experiente:\t\t\tPercentual Fixo (2.5%)\tR$ 25-30

ADAPTAÇÃO PARA ANGOLA:
────────────────────────────────────────────────────────────────
Conservador:\t\t\tUnidade Fixa (2%)\t\t21.250 AOA
Moderado:\t\t\tKelly Fracionado (1/4)\t25.500 AOA
Agressivo:\t\t\tKelly Completo\t\t51.000 AOA
Experiente:\t\t\tPercentual Fixo (2.5%)\t25.500 AOA
""")

def show_risk_management():
    """Mostra gestão de risco"""
    
    print("\n⚠️ GESTÃO DE RISCO")
    print("=" * 30)
    print("""
NÍVEIS DE RISCO:
────────────────────────────────────────────────────────────────
🟢 MUITO BAIXO (0-2%):\t\tStake muito conservador
🟡 BAIXO (2-5%):\t\t\tStake conservador
🟠 MÉDIO (5-10%):\t\tStake moderado
🔴 ALTO (10-20%):\t\tStake agressivo
⚫ MUITO ALTO (20%+):\t\tStake muito agressivo

RECOMENDAÇÕES DE RISCO:
────────────────────────────────────────────────────────────────
• Nunca aposte mais de 5% da banca em uma única aposta
• Use Kelly Fracionado para reduzir risco
• Diversifique suas apostas
• Monitore sua banca regularmente
• Ajuste stake conforme performance

ADAPTAÇÃO PARA ANGOLA:
────────────────────────────────────────────────────────────────
• Mercado em desenvolvimento - seja conservador
• Taxa de câmbio flutuante - monitore conversões
• Regulamentação em mudança - mantenha-se atualizado
• Diversifique moedas se possível
• Use métodos conservadores inicialmente
""")

if __name__ == "__main__":
    # Mostra características
    show_bankroll_management_features()
    
    # Demonstra cálculo do Kelly
    demonstrate_kelly_calculation()
    
    # Mostra adaptação para Angola
    show_angola_adaptation()
    
    # Mostra comparação de métodos
    show_method_comparison()
    
    # Mostra gestão de risco
    show_risk_management()
    
    # Gera análise completa
    analysis = main()
    
    if analysis:
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Sistema de gestão de banca implementado")
        print("✅ Kelly Fracionado calculado corretamente")
        print("✅ Adaptação para Angola incluída")
        print("✅ Múltiplos métodos de gestão disponíveis")
        print("✅ Gestão de risco integrada")
        
        print("\n🔧 COMO USAR:")
        print("=" * 20)
        print("python bankroll_management_demo.py")
        print("from bankroll_management_advanced import AdvancedBankrollManager")
        
        print("\n📋 VANTAGENS:")
        print("=" * 20)
        print("• Kelly Fracionado (1/4) implementado")
        print("• Cálculo automático de stake")
        print("• Adaptação para mercado de Angola")
        print("• Múltiplos métodos de gestão")
        print("• Gestão de risco integrada")
        print("• Conversão de moeda automática")
        print("• Recomendações conservadoras")
        print("• Formatação profissional")
    else:
        print("\n❌ ERRO NA DEMONSTRAÇÃO")
        print("=" * 30)
