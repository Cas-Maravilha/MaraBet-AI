#!/usr/bin/env python3
"""
Demonstração de Relatório com Recomendação Final - MaraBet AI
Mostra o relatório completo com recomendação final detalhada
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from report_generator import ReportGenerator
from final_recommendation import FinalRecommendationGenerator
from datetime import datetime

def main():
    print("🎯 MARABET AI - RELATÓRIO COM RECOMENDAÇÃO FINAL")
    print("=" * 70)
    print("Demonstração do relatório completo com recomendação final detalhada")
    print("=" * 70)
    
    # Cria gerador de relatórios
    generator = ReportGenerator()
    
    print("\n🎯 GERANDO RELATÓRIO COMPLETO COM RECOMENDAÇÃO FINAL")
    print("=" * 60)
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print("=" * 60)
    
    # Gera relatório com recomendação final
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
        print("📊 RELATÓRIO COMPLETO COM RECOMENDAÇÃO FINAL")
        print("="*80)
        print(result['report'])
        
        # Mostra métricas específicas
        print("\n📈 MÉTRICAS ESPECÍFICAS DO RELATÓRIO")
        print("=" * 50)
        analysis = result['analysis_result']
        print(f"• Confiança da análise: {analysis.confidence_score:.1%}")
        if hasattr(analysis, 'final_recommendation') and analysis.final_recommendation:
            print(f"• Recomendação: {analysis.final_recommendation.primary_recommendation.market if analysis.final_recommendation.primary_recommendation else 'N/A'}")
        else:
            print("• Recomendação: N/A")
        print(f"• Valor esperado: {analysis.value_analysis['best_opportunity']['expected_value']:+.3f}")
        print(f"• Unidades recomendadas: {analysis.unit_recommendation['recommended_units']:.1f}")
        print(f"• Nível de risco: {analysis.risk_assessment['overall_risk']}")
        
        # Mostra seção de recomendação final
        if hasattr(analysis, 'final_recommendation'):
            print(f"\n🎯 RECOMENDAÇÃO FINAL INCLUÍDA:")
            print("=" * 40)
            print("✅ Aposta recomendada identificada")
            print("✅ Classificação de confiança")
            print("✅ Análise de range alvo")
            print("✅ Recomendações alternativas")
            print("✅ Fatores-chave e avisos")
        
        return result
    else:
        print(f"❌ Erro na geração: {result['error']}")
        return None

def show_final_recommendation_features():
    """Mostra características da recomendação final"""
    
    print("\n🔧 CARACTERÍSTICAS DA RECOMENDAÇÃO FINAL")
    print("=" * 50)
    print("""
✅ APOSTA RECOMENDADA
   • Identificação da melhor oportunidade
   • ODD e probabilidade estimada
   • Valor esperado calculado
   • Nível de confiança
   • Classificação de confiança

✅ CLASSIFICAÇÃO DE CONFIANÇA
   • MUITO ALTA (90-100%): 🔥
   • ALTA (80-89%): ⭐
   • MÉDIA-ALTA (70-79%): ⚡
   • MÉDIA (60-69%): 📊
   • BAIXA (50-59%): ⚠️
   • MUITO BAIXA (0-49%): ❌

✅ ANÁLISE DE RANGE ALVO
   • DENTRO DO RANGE ALVO: 70-90%
   • PRÓXIMO DO RANGE ALVO: 60-70%
   • ABAIXO DO RANGE ALVO: <60%

✅ RECOMENDAÇÕES ALTERNATIVAS
   • Segunda melhor opção
   • Terceira melhor opção
   • Comparação de valores
   • Diversificação de apostas

✅ FORMATAÇÃO PROFISSIONAL
   • Emojis para identificação visual
   • Formatação ASCII clara
   • Informações organizadas
   • Avisos importantes
   • Resumo executivo
""")

def demonstrate_final_recommendation_generator():
    """Demonstra o gerador de recomendação final isoladamente"""
    
    print("\n🧮 TESTE DO GERADOR DE RECOMENDAÇÃO FINAL ISOLADO")
    print("=" * 50)
    
    generator = FinalRecommendationGenerator()
    
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
    
    print("🎯 RECOMENDAÇÃO FINAL GERADA:")
    print("-" * 40)
    print(report)
    
    print("\n✅ RECOMENDAÇÃO FINAL CONCLUÍDA!")
    print("=" * 40)

def show_integration_benefits():
    """Mostra benefícios da integração"""
    
    print("\n🚀 BENEFÍCIOS DA INTEGRAÇÃO")
    print("=" * 40)
    print("""
✅ RELATÓRIOS COMPLETOS
   • Recomendação final + análise de valor esperado
   • Aposta recomendada + múltiplas oportunidades
   • Classificação de confiança + fatores contextuais
   • Formatação profissional + métricas precisas

✅ DADOS ESPECÍFICOS
   • Aposta recomendada identificada
   • Classificação de confiança
   • Análise de range alvo
   • Recomendações alternativas
   • Fatores-chave e avisos

✅ PROFISSIONALISMO
   • Formato padronizado e organizado
   • Emojis para clareza visual
   • Formatação ASCII clara
   • Informações organizadas
   • Resumo executivo

✅ FLEXIBILIDADE
   • Mercados podem ser personalizados
   • Análise adaptável a diferentes ligas
   • Classificações configuráveis
   • Formatação ajustável
""")

def show_example_final_recommendation():
    """Mostra exemplo de recomendação final"""
    
    print("\n📄 EXEMPLO DE RECOMENDAÇÃO FINAL")
    print("=" * 50)
    print("""
RECOMENDAÇÃO FINAL
==================================================

🏆 APOSTA RECOMENDADA
═══════════════════════════════════════════
         OVER 2.5 GOLS (Mais de 2.5)
═══════════════════════════════════════════

🎲 ODD: 1.65
📈 PROBABILIDADE ESTIMADA: 68%
💰 VALOR ESPERADO: +12.2%
🎯 NÍVEL DE CONFIANÇA: 74%
⚡ CLASSIFICAÇÃO: MÉDIA-ALTA

✅ DENTRO DO RANGE ALVO: 70-90%

🔄 RECOMENDAÇÕES ALTERNATIVAS
──────────────────────────────────────────────────
1. AMBAS MARCAM - SIM
   ODD: 1.80 | EV: +8.5% | Confiança: 71%

2. MANCHESTER CITY VENCE
   ODD: 2.20 | EV: +6.3% | Confiança: 68%

📊 ANÁLISE DE MERCADO
──────────────────────────────────────────────────
Análise de mercado para Manchester City vs Arsenal baseada em forma recente, confrontos diretos e fatores contextuais.

🔑 FATORES-CHAVE
──────────────────────────────────────────────────
• Forma recente dos times
• Confrontos diretos históricos
• Fatores contextuais (lesões, motivação)
• Qualidade ofensiva e defensiva
• Vantagem de casa/fora

⚠️ AVISOS IMPORTANTES
──────────────────────────────────────────────────
• Sempre aposte com responsabilidade
• Considere diversificar suas apostas

📈 RESUMO EXECUTIVO
──────────────────────────────────────────────────
• Confiança Geral: 74.0%
• Nível de Risco: MÉDIO
• Stake Recomendado: 2.1 unidades
• Razão: Alta probabilidade baseada em forma ofensiva dos times
""")

if __name__ == "__main__":
    # Mostra características
    show_final_recommendation_features()
    
    # Mostra exemplo
    show_example_final_recommendation()
    
    # Demonstra gerador isolado
    demonstrate_final_recommendation_generator()
    
    # Mostra benefícios da integração
    show_integration_benefits()
    
    # Gera relatório completo
    result = main()
    
    if result:
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Sistema de recomendação final implementado")
        print("✅ Relatórios com recomendação final gerados")
        print("✅ Integração completa com sistema de relatórios")
        print("✅ Formatação profissional e organizada")
        
        print("\n🔧 COMO USAR:")
        print("=" * 20)
        print("python final_recommendation_demo.py")
        print("python main.py --mode report")
        print("from final_recommendation import FinalRecommendationGenerator")
        
        print("\n📋 VANTAGENS:")
        print("=" * 20)
        print("• Aposta recomendada identificada")
        print("• Classificação de confiança")
        print("• Análise de range alvo")
        print("• Recomendações alternativas")
        print("• Integração com relatórios completos")
        print("• Formatação profissional")
        print("• Fatores-chave e avisos")
    else:
        print("\n❌ ERRO NA DEMONSTRAÇÃO")
        print("=" * 30)
