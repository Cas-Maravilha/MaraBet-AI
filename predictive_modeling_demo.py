#!/usr/bin/env python3
"""
Demonstração de Relatório com Modelagem Preditiva - MaraBet AI
Mostra o relatório completo com modelagem preditiva detalhada
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from report_generator import ReportGenerator
from predictive_modeling import PredictiveModeler
from datetime import datetime

def main():
    print("🎯 MARABET AI - RELATÓRIO COM MODELAGEM PREDITIVA")
    print("=" * 70)
    print("Demonstração do relatório completo com modelagem preditiva detalhada")
    print("=" * 70)
    
    # Cria gerador de relatórios
    generator = ReportGenerator()
    
    print("\n🎯 GERANDO RELATÓRIO COMPLETO COM MODELAGEM PREDITIVA")
    print("=" * 60)
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print("=" * 60)
    
    # Gera relatório com modelagem preditiva
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
        print("📊 RELATÓRIO COMPLETO COM MODELAGEM PREDITIVA")
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
        
        # Mostra seção de modelagem preditiva
        if hasattr(analysis, 'predictive_model'):
            print(f"\n🎯 MODELAGEM PREDITIVA INCLUÍDA:")
            print("=" * 40)
            print("✅ Tabela de probabilidades calculadas")
            print("✅ Cálculo de odds justas")
            print("✅ Comparação com odds de mercado")
            print("✅ Análise de valor das apostas")
            print("✅ Métricas do modelo preditivo")
        
        return result
    else:
        print(f"❌ Erro na geração: {result['error']}")
        return None

def show_predictive_modeling_features():
    """Mostra características da modelagem preditiva"""
    
    print("\n🔧 CARACTERÍSTICAS DA MODELAGEM PREDITIVA")
    print("=" * 50)
    print("""
✅ MODELOS PREDITIVOS
   • Modelo Poisson (para esportes com pontuação)
   • Machine Learning Ensemble (Random Forest + XGBoost)
   • Rede Neural Bayesiana (para incertezas)
   • Combinação inteligente de modelos
   • Peso otimizado para cada modelo

✅ CÁLCULO DE PROBABILIDADES
   • Probabilidades reais calculadas
   • Odds justas baseadas em probabilidades
   • Comparação com odds de mercado
   • Análise de valor das apostas
   • Classificação de oportunidades

✅ TABELAS PROFISSIONAIS
   • Formatação ASCII para clareza
   • Probabilidades em percentual
   • Odds com precisão decimal
   • Comparação lado a lado
   • Análise de valor detalhada

✅ MÉTRICAS DO MODELO
   • Precisão do modelo
   • Score de confiança
   • Features utilizadas
   • Timestamp da predição
   • Tipo de modelo aplicado
""")

def demonstrate_predictive_modeler():
    """Demonstra o modelador preditivo isoladamente"""
    
    print("\n🧮 TESTE DO MODELADOR PREDITIVO ISOLADO")
    print("=" * 50)
    
    modeler = PredictiveModeler()
    
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
    
    # Gera modelo preditivo
    model = modeler.generate_predictive_model(
        "Manchester City", "Arsenal", "2024-01-15", match_data
    )
    
    # Formata tabela
    table = modeler.format_predictive_table(model)
    
    print("🎯 MODELAGEM PREDITIVA GERADA:")
    print("-" * 40)
    print(table)
    
    print("\n✅ MODELAGEM PREDITIVA CONCLUÍDA!")
    print("=" * 40)

def show_integration_benefits():
    """Mostra benefícios da integração"""
    
    print("\n🚀 BENEFÍCIOS DA INTEGRAÇÃO")
    print("=" * 40)
    print("""
✅ RELATÓRIOS COMPLETOS
   • Modelagem preditiva + análise contextual
   • Probabilidades calculadas + fatores específicos
   • Odds justas + comparação de mercado
   • Formatação profissional + métricas precisas

✅ DADOS ESPECÍFICOS
   • Tabela de probabilidades calculadas
   • Cálculo de odds justas
   • Comparação com odds de mercado
   • Análise de valor das apostas
   • Métricas do modelo preditivo

✅ PROFISSIONALISMO
   • Formato padronizado e organizado
   • Tabelas ASCII para clareza
   • Probabilidades em percentual
   • Odds com precisão decimal
   • Análise de valor objetiva

✅ FLEXIBILIDADE
   • Modelos podem ser personalizados
   • Análise adaptável a diferentes ligas
   • Métricas configuráveis
   • Formatação ajustável
""")

def show_example_predictive_table():
    """Mostra exemplo de tabela preditiva"""
    
    print("\n📄 EXEMPLO DE MODELAGEM PREDITIVA")
    print("=" * 50)
    print("""
MODELAGEM PREDITIVA
==================================================

Probabilidades Calculadas pelo Sistema
┌─────────────────────────────────────────┐
│  RESULTADO  │  PROB. REAL  │  ODD JUSTA │
├─────────────────────────────────────────┤
│  MCI Vitória │    62.5%     │    1.60    │
│  Empate      │    22.0%     │    4.55    │
│  ARS Vitória │    15.5%     │    6.45    │
└─────────────────────────────────────────┘

Odds Oferecidas pelas Casas (Média)
MCI Vitória: 1.72
Empate: 4.20
ARS Vitória: 5.50

ANÁLISE DE VALOR
------------------------------
MCI Vitória:
  Valor Esperado: +0.075
  Recomendação: BOM VALOR
  Confiança: 75.0%

Empate:
  Valor Esperado: -0.076
  Recomendação: SEM VALOR
  Confiança: 26.4%

ARS Vitória:
  Valor Esperado: -0.147
  Recomendação: SEM VALOR
  Confiança: 18.6%

MODELO PREDITIVO
------------------------------
Tipo: Ensemble (Poisson + ML + Bayesian)
Precisão: 85.2%
Confiança: 73.3%
Features: recent_form, head_to_head, home_advantage, xG_difference, tactical_advantage, motivational_factors, contextual_factors
Atualização: 14/10/2025 15:45
""")

if __name__ == "__main__":
    # Mostra características
    show_predictive_modeling_features()
    
    # Mostra exemplo
    show_example_predictive_table()
    
    # Demonstra modelador isolado
    demonstrate_predictive_modeler()
    
    # Mostra benefícios da integração
    show_integration_benefits()
    
    # Gera relatório completo
    result = main()
    
    if result:
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("✅ Sistema de modelagem preditiva implementado")
        print("✅ Relatórios com tabelas preditivas gerados")
        print("✅ Integração completa com sistema de relatórios")
        print("✅ Formatação profissional e organizada")
        
        print("\n🔧 COMO USAR:")
        print("=" * 20)
        print("python predictive_modeling_demo.py")
        print("python main.py --mode report")
        print("from predictive_modeling import PredictiveModeler")
        
        print("\n📋 VANTAGENS:")
        print("=" * 20)
        print("• Tabelas de probabilidades calculadas")
        print("• Cálculo de odds justas")
        print("• Comparação com odds de mercado")
        print("• Análise de valor das apostas")
        print("• Integração com relatórios completos")
        print("• Formatação profissional")
        print("• Modelos preditivos avançados")
    else:
        print("\n❌ ERRO NA DEMONSTRAÇÃO")
        print("=" * 30)
