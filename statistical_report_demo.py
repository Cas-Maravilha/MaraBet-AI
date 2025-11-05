#!/usr/bin/env python3
"""
Demonstração de Relatório com Análise Estatística Detalhada - MaraBet AI
Mostra o relatório completo com dados estatísticos específicos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from report_generator import ReportGenerator
from statistical_analysis import StatisticalAnalyzer
from datetime import datetime

def main():
    print("📊 MARABET AI - RELATÓRIO COM ANÁLISE ESTATÍSTICA DETALHADA")
    print("=" * 70)
    print("Demonstração do relatório completo com dados estatísticos específicos")
    print("=" * 70)
    
    # Cria gerador de relatórios
    generator = ReportGenerator()
    
    print("\n🎯 GERANDO RELATÓRIO COMPLETO")
    print("=" * 50)
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print("=" * 50)
    
    # Gera relatório com análise estatística
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
        print("📊 RELATÓRIO COMPLETO COM ANÁLISE ESTATÍSTICA")
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
        
        # Mostra seção de análise estatística
        if hasattr(analysis, 'statistical_analysis'):
            print(f"\n📊 ANÁLISE ESTATÍSTICA INCLUÍDA:")
            print("=" * 40)
            print("✅ Forma recente dos times")
            print("✅ Confrontos diretos históricos")
            print("✅ Métricas avançadas (xG, gols, etc.)")
            print("✅ Tendências recentes")
            print("✅ Análise preditiva baseada em dados")
        
        return result
    else:
        print(f"❌ Erro na geração: {result['error']}")
        return None

def show_statistical_features():
    """Mostra características da análise estatística"""
    
    print("\n🔧 CARACTERÍSTICAS DA ANÁLISE ESTATÍSTICA")
    print("=" * 50)
    print("""
✅ DADOS DETALHADOS
   • Forma recente (últimos 5 jogos)
   • Tabelas com resultados específicos
   • Gols marcados e sofridos por jogo
   • Valores de xG por partida
   • Aproveitamento percentual

✅ CONFRONTOS DIRETOS
   • Histórico de confrontos entre os times
   • Resultados com símbolos visuais (✓, ✗, =)
   • Vantagem de casa calculada
   • Média de gols nos confrontos
   • Tendência recente dos confrontos

✅ MÉTRICAS AVANÇADAS
   • Diferença de xG entre os times
   • Eficiência ofensiva (gols/xG)
   • Performance defensiva
   • Análise de tendências
   • Probabilidades preditivas

✅ FORMATAÇÃO PROFISSIONAL
   • Tabelas organizadas e claras
   • Símbolos visuais para resultados
   • Métricas calculadas automaticamente
   • Análise preditiva integrada
   • Dados históricos contextualizados
""")

def demonstrate_statistical_analyzer():
    """Demonstra o analisador estatístico isoladamente"""
    
    print("\n🧮 TESTE DO ANALISADOR ESTATÍSTICO ISOLADO")
    print("=" * 50)
    
    analyzer = StatisticalAnalyzer()
    analyzer.load_sample_data()
    
    # Gera análise estatística
    report = analyzer.generate_detailed_statistical_report("Manchester City", "Arsenal")
    
    print("📊 ANÁLISE ESTATÍSTICA GERADA:")
    print("-" * 40)
    print(report)
    
    print("\n✅ ANÁLISE ESTATÍSTICA CONCLUÍDA!")
    print("=" * 40)

def show_integration_benefits():
    """Mostra benefícios da integração"""
    
    print("\n🚀 BENEFÍCIOS DA INTEGRAÇÃO")
    print("=" * 40)
    print("""
✅ RELATÓRIOS COMPLETOS
   • Análise estatística + análise preditiva
   • Dados históricos + projeções futuras
   • Contexto detalhado + recomendações
   • Formatação profissional + métricas precisas

✅ DADOS ESPECÍFICOS
   • Tabelas de forma recente detalhadas
   • Confrontos diretos com resultados
   • Métricas calculadas automaticamente
   • Análise preditiva baseada em dados reais

✅ PROFISSIONALISMO
   • Formato padronizado e organizado
   • Símbolos visuais para clareza
   • Métricas de qualidade incluídas
   • Recomendações objetivas e justificadas

✅ FLEXIBILIDADE
   • Dados podem ser carregados de APIs reais
   • Análise adaptável a diferentes ligas
   • Métricas personalizáveis
   • Formatação configurável
""")

if __name__ == "__main__":
    # Mostra características
    show_statistical_features()
    
    # Demonstra analisador isolado
    demonstrate_statistical_analyzer()
    
    # Mostra benefícios da integração
    show_integration_benefits()
    
    # Gera relatório completo
    result = main()
    
    if result:
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Sistema de análise estatística implementado")
        print("✅ Relatórios com dados específicos gerados")
        print("✅ Integração completa com sistema de relatórios")
        print("✅ Formatação profissional e organizada")
        
        print("\n🔧 COMO USAR:")
        print("=" * 20)
        print("python statistical_report_demo.py")
        print("python main.py --mode report")
        print("from statistical_analysis import StatisticalAnalyzer")
        
        print("\n📋 VANTAGENS:")
        print("=" * 20)
        print("• Dados estatísticos detalhados")
        print("• Tabelas de forma recente específicas")
        print("• Análise de confrontos diretos")
        print("• Métricas avançadas calculadas")
        print("• Integração com relatórios completos")
        print("• Formatação profissional")
        print("• Análise preditiva baseada em dados")
    else:
        print("\n❌ ERRO NA DEMONSTRAÇÃO")
        print("=" * 30)
