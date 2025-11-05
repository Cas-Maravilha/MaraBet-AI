#!/usr/bin/env python3
"""
Demonstração de Cenários e Probabilidades - MaraBet AI
Mostra o sistema completo de distribuição probabilística de gols
"""

import sys
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scenarios_probabilities import ScenariosProbabilityAnalyzer
from datetime import datetime

def main():
    print("🎯 MARABET AI - CENÁRIOS E PROBABILIDADES")
    print("=" * 70)
    print("Demonstração do sistema completo de distribuição probabilística")
    print("=" * 70)
    
    # Cria analisador de cenários e probabilidades
    analyzer = ScenariosProbabilityAnalyzer()
    
    print("\n🎯 GERANDO DISTRIBUIÇÃO DE PROBABILIDADES")
    print("=" * 60)
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print("=" * 60)
    
    # Dados de exemplo
    match_data = {
        'home_form': 0.8,
        'away_form': 0.6,
        'h2h_goals_avg': 3.0
    }
    
    # Gera distribuição de probabilidades
    distribution = analyzer.generate_probability_distribution(
        "Manchester City", "Arsenal", "2024-01-15", match_data
    )
    
    # Formata distribuição
    report = analyzer.format_probability_distribution(distribution)
    
    print("✅ Distribuição de probabilidades gerada!")
    print("\n" + "="*80)
    print("📊 DISTRIBUIÇÃO DE PROBABILIDADES COMPLETA")
    print("="*80)
    print(report)
    
    # Mostra métricas específicas
    print("\n📈 MÉTRICAS ESPECÍFICAS DA DISTRIBUIÇÃO")
    print("=" * 50)
    print(f"• Over 2.5: {distribution.over_2_5_probability:.1%}")
    print(f"• Under 2.5: {distribution.under_2_5_probability:.1%}")
    print(f"• Razão de Probabilidades: {distribution.probability_ratio:.2f}")
    print(f"• Cenário Mais Provável: {distribution.most_likely_scenario.goals}")
    print(f"• Confiança: {distribution.confidence_level:.1%}")
    
    # Mostra detalhes dos cenários
    print(f"\n🔍 DETALHES DOS CENÁRIOS")
    print("=" * 30)
    for i, scenario in enumerate(distribution.scenarios, 1):
        print(f"{i}. {scenario.goals}: {scenario.probability:.1%}")
        print(f"   Barra: {scenario.bar_visual}")
        print(f"   Descrição: {scenario.description}")
        print()
    
    return distribution

def show_scenarios_features():
    """Mostra características dos cenários e probabilidades"""
    
    print("\n🔧 CARACTERÍSTICAS DOS CENÁRIOS E PROBABILIDADES")
    print("=" * 50)
    print("""
✅ DISTRIBUIÇÃO PROBABILÍSTICA DE GOLS
   • 0-1 gols: Jogo de poucos gols
   • 2 gols: Jogo equilibrado
   • 3 gols: Jogo movimentado
   • 4 gols: Jogo de muitos gols
   • 5+ gols: Jogo de muitos gols

✅ VISUALIZAÇÃO EM BARRAS ASCII
   • Barras proporcionais à probabilidade
   • Caracteres █ para preenchimento
   • Caracteres ░ para espaços vazios
   • Indicação do cenário mais provável

✅ CÁLCULO DE PROBABILIDADES OVER/UNDER
   • Over 2.5: Soma de 3, 4 e 5+ gols
   • Under 2.5: Soma de 0-1 e 2 gols
   • Razão de probabilidades
   • Interpretação automática

✅ MODELO POISSON
   • Fórmula: P(X=k) = (λ^k * e^(-λ)) / k!
   • Parâmetro λ baseado em forma dos times
   • Histórico H2H considerado
   • Ajuste por contexto da partida

✅ ANÁLISE DE CONFIANÇA
   • Baseada na concentração de probabilidade
   • Cenário dominante = alta confiança
   • Distribuição equilibrada = baixa confiança
   • Interpretação automática
""")

def demonstrate_probability_calculation():
    """Demonstra cálculo de probabilidades"""
    
    print("\n🧮 DEMONSTRAÇÃO DO CÁLCULO DE PROBABILIDADES")
    print("=" * 50)
    
    # Dados do exemplo
    print("Dados do Exemplo:")
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print()
    
    print("MODELO POISSON:")
    print("λ_home = 1.5 + (forma_casa - 0.5) × 1.0")
    print("λ_away = 1.2 + (forma_fora - 0.5) × 0.8")
    print("λ_total = λ_home + λ_away")
    print()
    
    # Simula cálculo
    home_form = 0.8
    away_form = 0.6
    lambda_home = 1.5 + (home_form - 0.5) * 1.0
    lambda_away = 1.2 + (away_form - 0.5) * 0.8
    lambda_total = lambda_home + lambda_away
    
    print(f"Cálculo:")
    print(f"λ_home = 1.5 + ({home_form} - 0.5) × 1.0 = {lambda_home:.2f}")
    print(f"λ_away = 1.2 + ({away_form} - 0.5) × 0.8 = {lambda_away:.2f}")
    print(f"λ_total = {lambda_home:.2f} + {lambda_away:.2f} = {lambda_total:.2f}")
    print()
    
    print("PROBABILIDADES CALCULADAS:")
    print("P(0 gols) = e^(-λ) = e^(-{:.2f}) = {:.3f}".format(lambda_total, np.exp(-lambda_total)))
    print("P(1 gol) = λ × e^(-λ) = {:.2f} × e^(-{:.2f}) = {:.3f}".format(lambda_total, lambda_total, lambda_total * np.exp(-lambda_total)))
    print("P(2 gols) = (λ²/2) × e^(-λ) = {:.3f}".format((lambda_total**2 / 2) * np.exp(-lambda_total)))
    print("P(3 gols) = (λ³/6) × e^(-λ) = {:.3f}".format((lambda_total**3 / 6) * np.exp(-lambda_total)))
    print("P(4 gols) = (λ⁴/24) × e^(-λ) = {:.3f}".format((lambda_total**4 / 24) * np.exp(-lambda_total)))
    print()

def show_visualization_examples():
    """Mostra exemplos de visualização"""
    
    print("\n📊 EXEMPLOS DE VISUALIZAÇÃO")
    print("=" * 40)
    print("""
DISTRIBUIÇÃO PROBABILÍSTICA DE GOLS:
─────────────────────────────────────
0-1 gols:  12% ████
2 gols:    20% ████████
3 gols:    32% █████████████  ← MAIS PROVÁVEL
4 gols:    24% ██████████
5+ gols:   12% ████

INTERPRETAÇÃO:
─────────────────────────────────────
• Cada █ representa ~5% de probabilidade
• Barra mais longa = cenário mais provável
• ← MAIS PROVÁVEL indica o cenário dominante
• Distribuição visual clara e intuitiva

VANTAGENS DA VISUALIZAÇÃO:
─────────────────────────────────────
• Identificação rápida do cenário mais provável
• Comparação visual entre cenários
• Intuição sobre distribuição de probabilidades
• Formatação profissional e clara
""")

def show_probability_analysis():
    """Mostra análise de probabilidades"""
    
    print("\n📈 ANÁLISE DE PROBABILIDADES")
    print("=" * 40)
    print("""
PROBABILIDADES OVER/UNDER:
─────────────────────────────────────
Over 2.5: 68% (3 + 4 + 5+ gols)
Under 2.5: 32% (0-1 + 2 gols)

RAZÃO DE PROBABILIDADES:
─────────────────────────────────────
Razão = Over 2.5 / Under 2.5
Razão = 68% / 32% = 2.13

INTERPRETAÇÃO DA RAZÃO:
─────────────────────────────────────
• Razão > 2.0: Forte favoritismo para Over 2.5
• Razão > 1.5: Moderado favoritismo para Over 2.5
• Razão > 1.0: Leve favoritismo para Over 2.5
• Razão < 1.0: Favoritismo para Under 2.5

CENÁRIO MAIS PROVÁVEL:
─────────────────────────────────────
• 3 gols: 32% ← MAIS PROVÁVEL
• Descrição: Jogo movimentado
• Características: Ataques eficazes, defesas vulneráveis
• Interpretação: Jogo aberto com boa qualidade ofensiva
""")

def show_confidence_analysis():
    """Mostra análise de confiança"""
    
    print("\n🎯 ANÁLISE DE CONFIANÇA")
    print("=" * 30)
    print("""
NÍVEIS DE CONFIANÇA:
─────────────────────────────────────
• Alta (>80%): Cenário claramente dominante
• Moderada (60-80%): Cenário com vantagem clara
• Baixa (<60%): Distribuição equilibrada

FATORES DE CONFIANÇA:
─────────────────────────────────────
• Concentração de probabilidade
• Diferença entre 1º e 2º cenário
• Consistência com dados históricos
• Qualidade dos dados de entrada

INTERPRETAÇÃO:
─────────────────────────────────────
• Alta confiança: Aposta mais segura
• Moderada confiança: Aposta com cuidado
• Baixa confiança: Aposta com muito cuidado
""")

if __name__ == "__main__":
    # Mostra características
    show_scenarios_features()
    
    # Demonstra cálculo de probabilidades
    demonstrate_probability_calculation()
    
    # Mostra exemplos de visualização
    show_visualization_examples()
    
    # Mostra análise de probabilidades
    show_probability_analysis()
    
    # Mostra análise de confiança
    show_confidence_analysis()
    
    # Gera distribuição completa
    distribution = main()
    
    if distribution:
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Sistema de cenários e probabilidades implementado")
        print("✅ Distribuição probabilística de gols")
        print("✅ Visualização em barras ASCII")
        print("✅ Cálculo de probabilidades Over/Under")
        print("✅ Razão de probabilidades")
        print("✅ Análise de confiança")
        
        print("\n🔧 COMO USAR:")
        print("=" * 20)
        print("python scenarios_probabilities_demo.py")
        print("from scenarios_probabilities import ScenariosProbabilityAnalyzer")
        
        print("\n📋 VANTAGENS:")
        print("=" * 20)
        print("• Distribuição probabilística visual")
        print("• Barras ASCII proporcionais")
        print("• Cálculo automático Over/Under")
        print("• Razão de probabilidades")
        print("• Análise de confiança")
        print("• Modelo Poisson implementado")
        print("• Formatação profissional")
        print("• Interpretação automática")
    else:
        print("\n❌ ERRO NA DEMONSTRAÇÃO")
        print("=" * 30)
