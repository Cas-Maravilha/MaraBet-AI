#!/usr/bin/env python3
"""
Demonstração de Relatório com Análise de Fatores Contextuais - MaraBet AI
Mostra o relatório completo com análise contextual detalhada
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from report_generator import ReportGenerator
from contextual_analysis import ContextualAnalyzer
from datetime import datetime

def main():
    print("🎯 MARABET AI - RELATÓRIO COM ANÁLISE DE FATORES CONTEXTUAIS")
    print("=" * 70)
    print("Demonstração do relatório completo com análise contextual detalhada")
    print("=" * 70)
    
    # Cria gerador de relatórios
    generator = ReportGenerator()
    
    print("\n🎯 GERANDO RELATÓRIO COMPLETO COM ANÁLISE CONTEXTUAL")
    print("=" * 60)
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print("=" * 60)
    
    # Gera relatório com análise contextual
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
        print("📊 RELATÓRIO COMPLETO COM ANÁLISE CONTEXTUAL")
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
        
        # Mostra seção de análise contextual
        if hasattr(analysis, 'contextual_analysis'):
            print(f"\n🎯 ANÁLISE CONTEXTUAL INCLUÍDA:")
            print("=" * 40)
            print("✅ Fatores positivos por time")
            print("✅ Pontos de atenção e desfalques")
            print("✅ Análise de lesões e status dos jogadores")
            print("✅ Fatores motivacionais e táticos")
            print("✅ Insights principais e fatores de risco")
        
        return result
    else:
        print(f"❌ Erro na geração: {result['error']}")
        return None

def show_contextual_features():
    """Mostra características da análise contextual"""
    
    print("\n🔧 CARACTERÍSTICAS DA ANÁLISE CONTEXTUAL")
    print("=" * 50)
    print("""
✅ FATORES POSITIVOS
   • Invicto em casa há X jogos
   • Melhor ataque/defesa da liga
   • Jogadores em grande fase
   • Elenco completo sem lesões
   • Objetivos claros na temporada

✅ PONTOS DE ATENÇÃO
   • Desfalques de jogadores importantes
   • Cansaço por jogos consecutivos
   • Condições climáticas adversas
   • Pressão externa ou interna
   • Fatores táticos desfavoráveis

✅ ANÁLISE DETALHADA
   • Status dos jogadores principais
   • Vantagens táticas específicas
   • Fatores motivacionais
   • Insights principais
   • Fatores de risco identificados

✅ FORMATAÇÃO PROFISSIONAL
   • Emojis para identificação visual
   • Categorização por tipo de fator
   • Impacto quantificado
   • Confiança na análise
   • Detalhes explicativos
""")

def demonstrate_contextual_analyzer():
    """Demonstra o analisador contextual isoladamente"""
    
    print("\n🧮 TESTE DO ANALISADOR CONTEXTUAL ISOLADO")
    print("=" * 50)
    
    analyzer = ContextualAnalyzer()
    
    # Gera análise contextual
    analysis = analyzer.generate_contextual_analysis("Manchester City", "Arsenal", "High")
    
    # Formata relatório
    report = analyzer.format_contextual_report(analysis)
    
    print("🎯 ANÁLISE CONTEXTUAL GERADA:")
    print("-" * 40)
    print(report)
    
    print("\n✅ ANÁLISE CONTEXTUAL CONCLUÍDA!")
    print("=" * 40)

def show_integration_benefits():
    """Mostra benefícios da integração"""
    
    print("\n🚀 BENEFÍCIOS DA INTEGRAÇÃO")
    print("=" * 40)
    print("""
✅ RELATÓRIOS COMPLETOS
   • Análise contextual + análise preditiva
   • Fatores específicos + projeções futuras
   • Contexto detalhado + recomendações
   • Formatação profissional + métricas precisas

✅ DADOS ESPECÍFICOS
   • Fatores positivos por time
   • Pontos de atenção identificados
   • Status dos jogadores principais
   • Análise de desfalques e lesões
   • Fatores motivacionais e táticos

✅ PROFISSIONALISMO
   • Formato padronizado e organizado
   • Emojis para clareza visual
   • Categorização por tipo de fator
   • Impacto quantificado
   • Insights objetivos e justificados

✅ FLEXIBILIDADE
   • Fatores podem ser personalizados
   • Análise adaptável a diferentes ligas
   • Métricas configuráveis
   • Formatação ajustável
""")

def show_example_contextual_analysis():
    """Mostra exemplo de análise contextual"""
    
    print("\n📄 EXEMPLO DE ANÁLISE CONTEXTUAL")
    print("=" * 50)
    print("""
FATORES CONTEXTUAIS
==================================================

✅ FATORES POSITIVOS - Manchester City
----------------------------------------
🏠 Invicto em casa há 12 jogos
⚽ Melhor ataque da liga (2.8 gols/jogo)
📈 Haaland com 15 gols em 10 jogos
💪 Elenco completo, sem lesões importantes
🎯 Buscando liderança isolada

✅ FATORES POSITIVOS - Arsenal
----------------------------------------
🛡️ Melhor defesa visitante (0.6 gols/jogo)
📊 Posse de bola superior (58%)
🔥 Saka em grande fase (4 gols em 5 jogos)
💡 Sistema tático bem definido

❌ PONTOS DE ATENÇÃO
----------------------------------------
Arsenal: Desfalque de Saliba (defensor titular)
Manchester City: Jogo decisivo na Champions midweek (possível cansaço)

📊 ANÁLISE GERAL
----------------------------------------
Manchester City tem vantagem contextual significativa

🔍 INSIGHTS PRINCIPAIS
----------------------------------------
• Manchester City tem 5 fatores positivos importantes
• Arsenal tem 4 fatores positivos importantes
• Arsenal tem 1 desfalques importantes

⚠️ FATORES DE RISCO
----------------------------------------
• Arsenal: Desfalque de Saliba (defensor titular)
• Manchester City: Jogo decisivo na Champions midweek (possível cansaço)
""")

if __name__ == "__main__":
    # Mostra características
    show_contextual_features()
    
    # Mostra exemplo
    show_example_contextual_analysis()
    
    # Demonstra analisador isolado
    demonstrate_contextual_analyzer()
    
    # Mostra benefícios da integração
    show_integration_benefits()
    
    # Gera relatório completo
    result = main()
    
    if result:
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Sistema de análise contextual implementado")
        print("✅ Relatórios com fatores contextuais gerados")
        print("✅ Integração completa com sistema de relatórios")
        print("✅ Formatação profissional e organizada")
        
        print("\n🔧 COMO USAR:")
        print("=" * 20)
        print("python contextual_report_demo.py")
        print("python main.py --mode report")
        print("from contextual_analysis import ContextualAnalyzer")
        
        print("\n📋 VANTAGENS:")
        print("=" * 20)
        print("• Fatores contextuais específicos")
        print("• Análise de desfalques e lesões")
        print("• Fatores motivacionais e táticos")
        print("• Insights principais identificados")
        print("• Integração com relatórios completos")
        print("• Formatação profissional")
        print("• Análise baseada em contexto real")
    else:
        print("\n❌ ERRO NA DEMONSTRAÇÃO")
        print("=" * 30)
