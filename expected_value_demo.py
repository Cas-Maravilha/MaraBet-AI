#!/usr/bin/env python3
"""
Demonstração de Relatório com Análise de Valor Esperado - MaraBet AI
Mostra o relatório completo com análise de valor esperado detalhada
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from report_generator import ReportGenerator
from expected_value_analysis import ExpectedValueAnalyzer
from datetime import datetime

def main():
    print("🎯 MARABET AI - RELATÓRIO COM ANÁLISE DE VALOR ESPERADO")
    print("=" * 70)
    print("Demonstração do relatório completo com análise de valor esperado detalhada")
    print("=" * 70)
    
    # Cria gerador de relatórios
    generator = ReportGenerator()
    
    print("\n🎯 GERANDO RELATÓRIO COMPLETO COM ANÁLISE DE VALOR ESPERADO")
    print("=" * 60)
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print("=" * 60)
    
    # Gera relatório com análise de valor esperado
    result = generator.generate_complete_analysis_report(
        home_team="Manchester City",
        away_team="Arsenal", 
        match_date="2024-01-15",
        league="Premier League",
        season="2024/25"
    )
    
    if result['success']:
        print("✅ Relatório gerado com sucesso!")
        print(f"📁 Arquivo salvo em: {result['file_path']}")
        
        # Mostra o relatório completo
        print("\n" + "="*80)
        print("📊 RELATÓRIO COMPLETO COM ANÁLISE DE VALOR ESPERADO")
        print("="*80)
        print(result['report'])
        
        # Mostra métricas específicas
        print("\n📈 MÉTRICAS ESPECÍFICAS DO RELATÓRIO")
        print("=" * 50)
        analysis = result['analysis_result']
        print(f"• Confiança da análise: {analysis.confidence_score:.1%}")
        print(f"• Recomendação: {analysis.final_recommendation['action']}")
        print(f"• Valor esperado: {analysis.value_analysis['best_opportunity']['expected_value']:+.3f}")
        print(f"• Unidades recomendadas: {analysis.unit_recommendation['recommended_units']:.1f}")
        print(f"• Nível de risco: {analysis.risk_assessment['overall_risk']}")
        
        # Mostra seção de análise de valor esperado
        if hasattr(analysis, 'expected_value_analysis'):
            print(f"\n🎯 ANÁLISE DE VALOR ESPERADO INCLUÍDA:")
            print("=" * 40)
            print("✅ Identificação de apostas com valor positivo")
            print("✅ Cálculo detalhado de EV")
            print("✅ Análise de múltiplas oportunidades")
            print("✅ Comparação de probabilidades")
            print("✅ Recomendações de valor")
        
        return result
    else:
        print(f"❌ Erro na geração: {result['error']}")
        return None

def show_expected_value_features():
    """Mostra características da análise de valor esperado"""
    
    print("\n🔧 CARACTERÍSTICAS DA ANÁLISE DE VALOR ESPERADO")
    print("=" * 50)
    print("""
✅ IDENTIFICAÇÃO DE VALOR
   • Apostas com valor positivo identificadas
   • Cálculo detalhado de EV
   • Comparação de probabilidades
   • Análise de múltiplas oportunidades
   • Recomendações de valor

✅ CÁLCULO DE EV
   • Fórmula: EV = (Probabilidade Real × Odd) - 1
   • Probabilidade real calculada
   • Odd oferecida pelo mercado
   • Probabilidade implícita
   • Percentual de EV

✅ ANÁLISE DE MERCADOS
   • Resultado da partida
   • Total de gols (Over/Under)
   • Ambas marcam (SIM/NÃO)
   • Placar exato
   • Outros mercados específicos

✅ FORMATAÇÃO PROFISSIONAL
   • Emojis para identificação visual
   • Cálculo passo a passo
   • Comparação lado a lado
   • Recomendações claras
   • Resumo da análise
""")

def demonstrate_expected_value_analyzer():
    """Demonstra o analisador de valor esperado isoladamente"""
    
    print("\n🧮 TESTE DO ANALISADOR DE VALOR ESPERADO ISOLADO")
    print("=" * 50)
    
    analyzer = ExpectedValueAnalyzer()
    
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
    
    print("🎯 ANÁLISE DE VALOR ESPERADO GERADA:")
    print("-" * 40)
    print(report)
    
    print("\n✅ ANÁLISE DE VALOR ESPERADO CONCLUÍDA!")
    print("=" * 40)

def show_integration_benefits():
    """Mostra benefícios da integração"""
    
    print("\n🚀 BENEFÍCIOS DA INTEGRAÇÃO")
    print("=" * 40)
    print("""
✅ RELATÓRIOS COMPLETOS
   • Análise de valor esperado + modelagem preditiva
   • Identificação de valor + probabilidades calculadas
   • Múltiplas oportunidades + análise contextual
   • Formatação profissional + métricas precisas

✅ DADOS ESPECÍFICOS
   • Apostas com valor positivo identificadas
   • Cálculo detalhado de EV
   • Análise de múltiplas oportunidades
   • Comparação de probabilidades
   • Recomendações de valor

✅ PROFISSIONALISMO
   • Formato padronizado e organizado
   • Emojis para clareza visual
   • Cálculo passo a passo
   • Recomendações objetivas
   • Resumo da análise

✅ FLEXIBILIDADE
   • Mercados podem ser personalizados
   • Análise adaptável a diferentes ligas
   • Thresholds configuráveis
   • Formatação ajustável
""")

def show_example_expected_value_analysis():
    """Mostra exemplo de análise de valor esperado"""
    
    print("\n📄 EXEMPLO DE ANÁLISE DE VALOR ESPERADO")
    print("=" * 50)
    print("""
ANÁLISE DE VALOR ESPERADO
==================================================

💎 APOSTA COM VALOR POSITIVO IDENTIFICADA
🎯 MERCADO: Manchester City Vence
───────────────────────────────────
Probabilidade Real:     62.5%
Odd Oferecida:         1.72
Probabilidade Implícita: 58.1%

📊 CÁLCULO DE EV:
EV = (0.625 × 1.72) - 1
EV = 1.075 - 1
EV = +0.075 (+7.5%)

✅ VALOR POSITIVO: 7.5%

Outras Oportunidades Analisadas:
Over 2.5 Gols
├─ Probabilidade Real: 68%
├─ Odd: 1.65
├─ EV: +12.2% ⭐ EXCELENTE
└─ Confiança: 74%

Ambas Marcam - SIM
├─ Probabilidade Real: 58%
├─ Odd: 1.80
├─ EV: +4.4% ✓ Positivo
└─ Confiança: 71%

📈 RESUMO DA ANÁLISE
───────────────────────────────────
• Total de Oportunidades: 8
• Valor Positivo: 3
• Valor Excelente: 1
• EV Médio: +0.023
• Melhor EV: +12.2%
""")

if __name__ == "__main__":
    # Mostra características
    show_expected_value_features()
    
    # Mostra exemplo
    show_example_expected_value_analysis()
    
    # Demonstra analisador isolado
    demonstrate_expected_value_analyzer()
    
    # Mostra benefícios da integração
    show_integration_benefits()
    
    # Gera relatório completo
    result = main()
    
    if result:
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Sistema de análise de valor esperado implementado")
        print("✅ Relatórios com análise de valor gerados")
        print("✅ Integração completa com sistema de relatórios")
        print("✅ Formatação profissional e organizada")
        
        print("\n🔧 COMO USAR:")
        print("=" * 20)
        print("python expected_value_demo.py")
        print("python main.py --mode report")
        print("from expected_value_analysis import ExpectedValueAnalyzer")
        
        print("\n📋 VANTAGENS:")
        print("=" * 20)
        print("• Identificação de apostas com valor positivo")
        print("• Cálculo detalhado de EV")
        print("• Análise de múltiplas oportunidades")
        print("• Comparação de probabilidades")
        print("• Integração com relatórios completos")
        print("• Formatação profissional")
        print("• Recomendações de valor")
    else:
        print("\n❌ ERRO NA DEMONSTRAÇÃO")
        print("=" * 30)
