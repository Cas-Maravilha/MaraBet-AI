#!/usr/bin/env python3
"""
Demonstração de Justificativa Técnica - MaraBet AI
Mostra o sistema completo de análise técnica detalhada com pesos específicos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from technical_justification import TechnicalJustificationAnalyzer
from datetime import datetime

def main():
    print("🎯 MARABET AI - JUSTIFICATIVA TÉCNICA")
    print("=" * 70)
    print("Demonstração do sistema completo de análise técnica detalhada")
    print("=" * 70)
    
    # Cria analisador de justificativa técnica
    analyzer = TechnicalJustificationAnalyzer()
    
    print("\n🎯 GERANDO JUSTIFICATIVA TÉCNICA")
    print("=" * 60)
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print("=" * 60)
    
    # Dados de exemplo
    match_data = {
        'home_form': 0.8,
        'away_form': 0.6,
        'h2h_home': 0.7,
        'h2h_away': 0.3,
        'home_goals_home': 2.8,
        'away_goals_away': 1.8,
        'h2h_goals_avg': 3.6
    }
    
    # Gera justificativa técnica
    justification = analyzer.generate_technical_justification(
        "Manchester City", "Arsenal", "2024-01-15", 
        "OVER 2.5 GOLS", match_data
    )
    
    # Formata justificativa
    report = analyzer.format_technical_justification(justification)
    
    print("✅ Justificativa técnica gerada!")
    print("\n" + "="*80)
    print("📊 JUSTIFICATIVA TÉCNICA COMPLETA")
    print("="*80)
    print(report)
    
    # Mostra métricas específicas
    print("\n📈 MÉTRICAS ESPECÍFICAS DA JUSTIFICATIVA")
    print("=" * 50)
    print(f"• Confiança Geral: {justification.overall_confidence:.1%}")
    print(f"• Número de Fatores: {len(justification.factors)}")
    print(f"• Insights Principais: {len(justification.key_insights)}")
    print(f"• Fatores de Risco: {len(justification.risk_factors)}")
    
    # Mostra detalhes dos fatores
    print(f"\n🔍 DETALHES DOS FATORES TÉCNICOS")
    print("=" * 40)
    for i, factor in enumerate(justification.factors, 1):
        print(f"{i}. {factor.name} ({factor.weight:.0%} do peso)")
        print(f"   Confiança: {factor.confidence:.1%}")
        print(f"   Valor Combinado: {factor.combined_value:.2f}")
        print(f"   Conclusão: {factor.conclusion}")
        print()
    
    return justification

def show_technical_justification_features():
    """Mostra características da justificativa técnica"""
    
    print("\n🔧 CARACTERÍSTICAS DA JUSTIFICATIVA TÉCNICA")
    print("=" * 50)
    print("""
✅ PODER OFENSIVO COMBINADO (35% do peso)
   • Gols por jogo em casa vs fora
   • Histórico H2H de gols
   • Capacidade ofensiva comprovada
   • Análise combinada de ataque

✅ VULNERABILIDADE DEFENSIVA (25% do peso)
   • Gols sofridos por jogo
   • Clean sheets e defesas
   • Desfalques de jogadores chave
   • Análise de fragilidades

✅ ESTILO DE JOGO (20% do peso)
   • Posse de bola e intensidade
   • Confrontos historicamente movimentados
   • Tendência a jogos abertos
   • Análise tática

✅ CONTEXTO MOTIVACIONAL (10% do peso)
   • Posição na tabela
   • Objetivos da temporada
   • Rivalidade e pressão
   • Análise motivacional

✅ ANÁLISE xG (10% do peso)
   • xG combinado por jogo
   • Histórico xG dos confrontos
   • Tendência de gols
   • Estatísticas avançadas

✅ FORMATAÇÃO PROFISSIONAL
   • Pesos específicos por fator
   • Análise detalhada
   • Conclusões objetivas
   • Confiança quantificada
""")

def demonstrate_technical_analysis():
    """Demonstra análise técnica detalhada"""
    
    print("\n🧮 DEMONSTRAÇÃO DA ANÁLISE TÉCNICA")
    print("=" * 50)
    
    # Dados do exemplo
    print("Dados do Exemplo:")
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print()
    
    print("1. PODER OFENSIVO COMBINADO (35% do peso):")
    print("   • Manchester City: 2.8 gols/jogo em casa")
    print("   • Arsenal: 1.8 gols/jogo fora")
    print("   • Histórico H2H: Média de 3.6 gols/jogo")
    print("   • Conclusão: Ambas equipes têm capacidade ofensiva comprovada")
    print()
    
    print("2. VULNERABILIDADE DEFENSIVA (25% do peso):")
    print("   • Arsenal sem Saliba (defensor chave)")
    print("   • City sofreu gols em 60% dos últimos jogos")
    print("   • Conclusão: Defesas não estão em seu melhor momento")
    print()
    
    print("3. ESTILO DE JOGO (20% do peso):")
    print("   • Ambas equipes jogam de forma ofensiva")
    print("   • Alta posse de bola = mais oportunidades")
    print("   • Confronto historicamente movimentado")
    print("   • Conclusão: Jogo tende a ser aberto")
    print()
    
    print("4. CONTEXTO MOTIVACIONAL (10% do peso):")
    print("   • Disputa direta pela liderança")
    print("   • Ambos precisam vencer")
    print("   • Conclusão: Jogo de alta intensidade desde o início")
    print()
    
    print("5. ANÁLISE xG (10% do peso):")
    print("   • xG combinado médio: 4.5 por jogo")
    print("   • 78% dos últimos confrontos tiveram 3+ gols")
    print("   • Conclusão: Estatísticas avançadas confirmam tendência")
    print()

def show_weight_distribution():
    """Mostra distribuição de pesos"""
    
    print("\n📊 DISTRIBUIÇÃO DE PESOS DOS FATORES")
    print("=" * 50)
    print("""
FATOR TÉCNICO                    PESO    IMPORTÂNCIA
────────────────────────────────────────────────────
Poder Ofensivo Combinado         35%     ⭐⭐⭐⭐⭐
Vulnerabilidade Defensiva        25%     ⭐⭐⭐⭐
Estilo de Jogo                   20%     ⭐⭐⭐
Contexto Motivacional            10%     ⭐⭐
Análise xG                       10%     ⭐⭐
────────────────────────────────────────────────────
TOTAL                           100%     ⭐⭐⭐⭐⭐

JUSTIFICATIVA:
────────────────────────────────────────────────────
• Poder Ofensivo: Fator mais importante (35%)
  - Dados objetivos de gols
  - Histórico comprovado
  - Capacidade ofensiva

• Vulnerabilidade Defensiva: Segundo mais importante (25%)
  - Desfalques importantes
  - Fragilidades defensivas
  - Clean sheets baixos

• Estilo de Jogo: Terceiro mais importante (20%)
  - Tendência tática
  - Histórico de confrontos
  - Intensidade do jogo

• Contexto Motivacional: Quarto mais importante (10%)
  - Pressão da tabela
  - Objetivos claros
  - Rivalidade

• Análise xG: Quinto mais importante (10%)
  - Estatísticas avançadas
  - Tendência de gols
  - Confirmação de dados
""")

def show_confidence_levels():
    """Mostra níveis de confiança"""
    
    print("\n🎯 NÍVEIS DE CONFIANÇA")
    print("=" * 30)
    print("""
NÍVEL DE CONFIANÇA    ICONE    RANGE    APLICAÇÃO
────────────────────────────────────────────────────
MUITO ALTA            🔥       90-100%  Fatores decisivos
ALTA                  ⭐       80-89%   Fatores importantes
MÉDIA-ALTA            ⚡       70-79%   Fatores relevantes
MÉDIA                 📊       60-69%   Fatores moderados
BAIXA                 ⚠️       50-59%   Fatores incertos
MUITO BAIXA           ❌       0-49%    Fatores duvidosos

CÁLCULO DA CONFIANÇA:
────────────────────────────────────────────────────
Confiança Geral = Σ(Confiança do Fator × Peso do Fator)

Exemplo:
• Poder Ofensivo: 85% × 35% = 29.75%
• Vulnerabilidade: 80% × 25% = 20.00%
• Estilo de Jogo: 85% × 20% = 17.00%
• Contexto: 90% × 10% = 9.00%
• xG: 88% × 10% = 8.80%
────────────────────────────────────────────────────
CONFIANÇA GERAL: 84.55% (ALTA) ⭐
""")

def show_technical_insights():
    """Mostra insights técnicos"""
    
    print("\n💡 INSIGHTS TÉCNICOS PRINCIPAIS")
    print("=" * 40)
    print("""
✅ INSIGHTS OFENSIVOS
   • Ambas equipes têm capacidade ofensiva comprovada
   • Histórico H2H mostra média alta de gols
   • Dados objetivos confirmam tendência

✅ INSIGHTS DEFENSIVOS
   • Defesas não estão em seu melhor momento
   • Desfalques importantes afetam qualidade
   • Vulnerabilidades identificadas

✅ INSIGHTS TÁTICOS
   • Jogo tende a ser aberto
   • Alta intensidade desde o início
   • Confronto historicamente movimentado

✅ INSIGHTS MOTIVACIONAIS
   • Disputa direta pela liderança
   • Ambos precisam vencer
   • Pressão alta na partida

✅ INSIGHTS ESTATÍSTICOS
   • Estatísticas avançadas confirmam tendência
   • xG combinado alto
   • Histórico de confrontos movimentados
""")

if __name__ == "__main__":
    # Mostra características
    show_technical_justification_features()
    
    # Demonstra análise técnica
    demonstrate_technical_analysis()
    
    # Mostra distribuição de pesos
    show_weight_distribution()
    
    # Mostra níveis de confiança
    show_confidence_levels()
    
    # Mostra insights técnicos
    show_technical_insights()
    
    # Gera justificativa completa
    justification = main()
    
    if justification:
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Sistema de justificativa técnica implementado")
        print("✅ Análise de 5 fatores técnicos principais")
        print("✅ Pesos específicos por fator")
        print("✅ Confiança quantificada")
        print("✅ Insights técnicos detalhados")
        
        print("\n🔧 COMO USAR:")
        print("=" * 20)
        print("python technical_justification_demo.py")
        print("from technical_justification import TechnicalJustificationAnalyzer")
        
        print("\n📋 VANTAGENS:")
        print("=" * 20)
        print("• Análise técnica detalhada")
        print("• Pesos específicos por fator")
        print("• Confiança quantificada")
        print("• Insights objetivos")
        print("• Formatação profissional")
        print("• Base científica sólida")
        print("• Justificativa clara")
        print("• Fatores de risco identificados")
    else:
        print("\n❌ ERRO NA DEMONSTRAÇÃO")
        print("=" * 30)
