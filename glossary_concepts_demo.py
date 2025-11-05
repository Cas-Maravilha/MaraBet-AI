#!/usr/bin/env python3
"""
Demonstração de Glossário e Conceitos - MaraBet AI
Mostra o sistema completo de definições técnicas e conceitos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from glossary_concepts import GlossaryGenerator
from datetime import datetime

def main():
    print("🎯 MARABET AI - GLOSSÁRIO E CONCEITOS")
    print("=" * 70)
    print("Demonstração do sistema completo de definições técnicas")
    print("=" * 70)
    
    # Cria gerador de glossário
    generator = GlossaryGenerator()
    
    print("\n🎯 GERANDO GLOSSÁRIO COMPLETO")
    print("=" * 60)
    print("Sistema de definições técnicas e conceitos")
    print("=" * 60)
    
    # Gera glossário completo
    glossary = generator.generate_glossary()
    
    # Formata glossário
    report = generator.format_glossary(glossary)
    
    print("✅ Glossário gerado!")
    print("\n" + "="*80)
    print("📊 GLOSSÁRIO E CONCEITOS COMPLETO")
    print("="*80)
    print(report)
    
    # Mostra métricas específicas
    print("\n📈 MÉTRICAS ESPECÍFICAS DO GLOSSÁRIO")
    print("=" * 50)
    print(f"• Total de Conceitos: {glossary.total_concepts}")
    print(f"• Número de Seções: {len(glossary.sections)}")
    print(f"• Conceitos Matemáticos: {len([c for s in glossary.sections for c in s.concepts if c.category == 'mathematical'])}")
    print(f"• Conceitos Estatísticos: {len([c for s in glossary.sections for c in s.concepts if c.category == 'statistical'])}")
    print(f"• Conceitos de Apostas: {len([c for s in glossary.sections for c in s.concepts if c.category == 'betting'])}")
    print(f"• Conceitos de Análise: {len([c for s in glossary.sections for c in s.concepts if c.category == 'analysis'])}")
    print(f"• Conceitos de Risco: {len([c for s in glossary.sections for c in s.concepts if c.category == 'risk'])}")
    print(f"• Conceitos de Performance: {len([c for s in glossary.sections for c in s.concepts if c.category == 'performance'])}")
    
    # Mostra detalhes por seção
    print(f"\n🔍 DETALHES POR SEÇÃO")
    print("=" * 30)
    for i, section in enumerate(glossary.sections, 1):
        print(f"{i}. {section.title}")
        print(f"   Conceitos: {len(section.concepts)}")
        print(f"   Descrição: {section.description}")
        print()
    
    return glossary

def show_glossary_features():
    """Mostra características do glossário"""
    
    print("\n🔧 CARACTERÍSTICAS DO GLOSSÁRIO")
    print("=" * 50)
    print("""
✅ CONCEITOS MATEMÁTICOS
   • Expected Value (EV)
   • Kelly Criterion
   • Expected Goals (xG)
   • Fórmulas e cálculos

✅ CONCEITOS ESTATÍSTICOS
   • Head to Head (H2H)
   • Sharpe Ratio
   • Drawdown
   • Métricas estatísticas

✅ CONCEITOS DE APOSTAS
   • Return on Investment (ROI)
   • Yield
   • Taxa de Acerto
   • Métricas de lucratividade

✅ CONCEITOS DE ANÁLISE
   • Forma Recente
   • Probabilidade Implícita
   • Over/Under
   • Métodos de análise

✅ CONCEITOS DE RISCO
   • Gestão de Banca
   • Diversificação
   • Stop Loss
   • Controle de risco

✅ CONCEITOS DE PERFORMANCE
   • Backtesting
   • Edge
   • Value Bet
   • Otimização de estratégias
""")

def demonstrate_key_concepts():
    """Demonstra conceitos-chave"""
    
    print("\n🔑 DEMONSTRAÇÃO DOS CONCEITOS-CHAVE")
    print("=" * 50)
    
    print("CONCEITOS FUNDAMENTAIS:")
    print("1. 🔴 EV (Expected Value)")
    print("   Definição: Valor esperado de retorno de uma aposta")
    print("   Fórmula: EV = (Probabilidade × Odd) - 1")
    print("   Exemplo: Se P = 0.68 e Odd = 1.65, então EV = +12.2%")
    print("   Importância: CRÍTICA - Base para identificar apostas com valor")
    print()
    
    print("2. 🔴 Kelly Criterion")
    print("   Definição: Fórmula para otimização do tamanho da aposta")
    print("   Fórmula: Stake % = (f/4) × [(P × O) - 1] / (O - 1)")
    print("   Exemplo: P = 0.68, O = 1.65, f = 0.25 → Stake = 4.7%")
    print("   Importância: CRÍTICA - Maximiza crescimento da banca")
    print()
    
    print("3. 🟡 xG (Expected Goals)")
    print("   Definição: Gols esperados baseados na qualidade das chances")
    print("   Fórmula: xG = Σ(Probabilidade de Gol de cada chance)")
    print("   Exemplo: Chance 20% + Chance 15% = xG = 0.35")
    print("   Importância: ALTA - Métrica avançada de performance")
    print()
    
    print("4. 🟡 H2H (Head to Head)")
    print("   Definição: Confrontos diretos entre duas equipes")
    print("   Fórmula: H2H = Σ(Resultados Históricos) / Número de Confrontos")
    print("   Exemplo: City 5 vitórias, Arsenal 2 vitórias em 10 confrontos")
    print("   Importância: ALTA - Histórico direto é preditor importante")
    print()
    
    print("5. 🔴 ROI (Return on Investment)")
    print("   Definição: Retorno sobre investimento")
    print("   Fórmula: ROI = (Lucro / Investimento) × 100%")
    print("   Exemplo: Investiu R$ 1.000, lucrou R$ 150 → ROI = 15%")
    print("   Importância: CRÍTICA - Principal métrica de lucratividade")
    print()
    
    print("6. 🟡 Yield")
    print("   Definição: Rentabilidade percentual média por aposta")
    print("   Fórmula: Yield = (Lucro Total / Stake Total) × 100%")
    print("   Exemplo: Apostou R$ 5.000, lucrou R$ 300 → Yield = 6%")
    print("   Importância: ALTA - Mede eficiência das apostas")
    print()

def demonstrate_formulas():
    """Demonstra fórmulas matemáticas"""
    
    print("\n🧮 DEMONSTRAÇÃO DAS FÓRMULAS")
    print("=" * 50)
    
    print("FÓRMULAS MATEMÁTICAS PRINCIPAIS:")
    print("1. Expected Value (EV)")
    print("   EV = (Probabilidade × Odd) - 1")
    print("   Exemplo: (0.68 × 1.65) - 1 = +0.122 = +12.2%")
    print()
    
    print("2. Kelly Criterion")
    print("   Stake % = (f/4) × [(P × O) - 1] / (O - 1)")
    print("   Exemplo: (0.25/4) × [(0.68 × 1.65) - 1] / (1.65 - 1) = 4.7%")
    print()
    
    print("3. ROI")
    print("   ROI = (Lucro / Investimento) × 100%")
    print("   Exemplo: (150 / 1000) × 100% = 15%")
    print()
    
    print("4. Yield")
    print("   Yield = (Lucro Total / Stake Total) × 100%")
    print("   Exemplo: (300 / 5000) × 100% = 6%")
    print()
    
    print("5. xG")
    print("   xG = Σ(Probabilidade de Gol de cada chance)")
    print("   Exemplo: 0.20 + 0.15 = 0.35")
    print()
    
    print("6. Sharpe Ratio")
    print("   Sharpe = (ROI - Taxa Livre de Risco) / Volatilidade")
    print("   Exemplo: (12 - 3) / 8 = 1.125")
    print()

def demonstrate_categories():
    """Demonstra categorias de conceitos"""
    
    print("\n📚 DEMONSTRAÇÃO DAS CATEGORIAS")
    print("=" * 50)
    
    print("CATEGORIAS DE CONCEITOS:")
    print("1. 🔢 CONCEITOS MATEMÁTICOS")
    print("   • Expected Value (EV)")
    print("   • Kelly Criterion")
    print("   • Expected Goals (xG)")
    print("   • Fórmulas e cálculos fundamentais")
    print()
    
    print("2. 📊 CONCEITOS ESTATÍSTICOS")
    print("   • Head to Head (H2H)")
    print("   • Sharpe Ratio")
    print("   • Drawdown")
    print("   • Métricas estatísticas avançadas")
    print()
    
    print("3. 🎯 CONCEITOS DE APOSTAS")
    print("   • Return on Investment (ROI)")
    print("   • Yield")
    print("   • Taxa de Acerto")
    print("   • Métricas de lucratividade")
    print()
    
    print("4. 🔍 CONCEITOS DE ANÁLISE")
    print("   • Forma Recente")
    print("   • Probabilidade Implícita")
    print("   • Over/Under")
    print("   • Métodos de análise de partidas")
    print()
    
    print("5. ⚠️ CONCEITOS DE RISCO")
    print("   • Gestão de Banca")
    print("   • Diversificação")
    print("   • Stop Loss")
    print("   • Controle de risco")
    print()
    
    print("6. 📈 CONCEITOS DE PERFORMANCE")
    print("   • Backtesting")
    print("   • Edge")
    print("   • Value Bet")
    print("   • Otimização de estratégias")
    print()

def show_importance_levels():
    """Mostra níveis de importância"""
    
    print("\n🎯 NÍVEIS DE IMPORTÂNCIA")
    print("=" * 30)
    print("""
🔴 CRÍTICA - Conceitos fundamentais
   • Expected Value (EV)
   • Kelly Criterion
   • Return on Investment (ROI)
   • Gestão de Banca
   • Edge
   • Value Bet

🟡 ALTA - Conceitos importantes
   • Expected Goals (xG)
   • Head to Head (H2H)
   • Yield
   • Taxa de Acerto
   • Forma Recente
   • Probabilidade Implícita
   • Diversificação
   • Stop Loss
   • Backtesting

🟢 MÉDIA - Conceitos relevantes
   • Sharpe Ratio
   • Drawdown
   • Over/Under
   • Outros conceitos auxiliares

INTERPRETAÇÃO:
────────────────────────────────────────────────────
• CRÍTICA: Essencial para apostas lucrativas
• ALTA: Muito importante para análise eficaz
• MÉDIA: Relevante para otimização
""")

def show_examples():
    """Mostra exemplos práticos"""
    
    print("\n💡 EXEMPLOS PRÁTICOS")
    print("=" * 30)
    print("""
EXEMPLO 1 - EV (Expected Value):
────────────────────────────────────────────────────
Probabilidade Real: 68%
Odd Oferecida: 1.65
EV = (0.68 × 1.65) - 1 = +0.122 = +12.2%
Interpretação: Aposta com valor positivo

EXEMPLO 2 - Kelly Criterion:
────────────────────────────────────────────────────
Probabilidade: 68%
Odd: 1.65
Kelly Fraction: 0.25
Stake = (0.25/4) × [(0.68 × 1.65) - 1] / (1.65 - 1) = 4.7%
Interpretação: Apostar 4.7% da banca

EXEMPLO 3 - ROI:
────────────────────────────────────────────────────
Investimento: R$ 1.000
Lucro: R$ 150
ROI = (150/1000) × 100% = 15%
Interpretação: Retorno de 15% sobre o investimento

EXEMPLO 4 - xG:
────────────────────────────────────────────────────
Chance 1: 20% de virar gol
Chance 2: 15% de virar gol
xG = 0.20 + 0.15 = 0.35
Interpretação: Espera-se 0.35 gols dessas chances
""")

if __name__ == "__main__":
    # Mostra características
    show_glossary_features()
    
    # Demonstra conceitos-chave
    demonstrate_key_concepts()
    
    # Demonstra fórmulas
    demonstrate_formulas()
    
    # Demonstra categorias
    demonstrate_categories()
    
    # Mostra níveis de importância
    show_importance_levels()
    
    # Mostra exemplos práticos
    show_examples()
    
    # Gera glossário completo
    glossary = main()
    
    if glossary:
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Sistema de glossário e conceitos implementado")
        print("✅ Definições de termos técnicos")
        print("✅ Explicações detalhadas")
        print("✅ Fórmulas matemáticas")
        print("✅ Exemplos práticos")
        print("✅ Categorização por importância")
        
        print("\n🔧 COMO USAR:")
        print("=" * 20)
        print("python glossary_concepts_demo.py")
        print("from glossary_concepts import GlossaryGenerator")
        
        print("\n📋 VANTAGENS:")
        print("=" * 20)
        print("• Definições técnicas completas")
        print("• Fórmulas matemáticas detalhadas")
        print("• Exemplos práticos")
        print("• Categorização por importância")
        print("• Termos relacionados")
        print("• Formatação profissional")
        print("• Conceitos fundamentais")
        print("• Base educativa sólida")
    else:
        print("\n❌ ERRO NA DEMONSTRAÇÃO")
        print("=" * 30)
