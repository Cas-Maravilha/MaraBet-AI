#!/usr/bin/env python3
"""
Exemplo de Relatório de Análise Completa - MaraBet AI
Demonstra o formato de relatório profissional
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from report_generator import ReportGenerator
from datetime import datetime

def generate_manchester_city_vs_arsenal_report():
    """Gera relatório específico Manchester City vs Arsenal"""
    
    print("🎯 GERANDO RELATÓRIO DE EXEMPLO")
    print("=" * 60)
    print("Manchester City vs Arsenal - Premier League 2024/25")
    print("=" * 60)
    
    # Cria gerador de relatórios
    generator = ReportGenerator()
    
    # Gera relatório específico
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
        print("📊 RELATÓRIO COMPLETO")
        print("="*80)
        print(result['report'])
        
        return result
    else:
        print(f"❌ Erro na geração: {result['error']}")
        return None

def show_report_structure():
    """Mostra estrutura do relatório"""
    
    print("\n📋 ESTRUTURA DO RELATÓRIO")
    print("=" * 40)
    print("""
🎯 RELATÓRIO DE ANÁLISE PREDITIVA
├── EVENTO ANALISADO
│   ├── 🏟️ Times e Liga
│   ├── 📅 Data e Horário
│   ├── 🌦️ Condições Climáticas
│   ├── 🏟️ Local e Público
│   └── 👨‍⚖️ Árbitro e Importância
│
├── ANÁLISE DE VALOR
│   ├── 📊 Odds de Mercado
│   ├── 🎯 Probabilidades Calculadas
│   ├── 💰 Valores Esperados
│   └── 🏆 Melhor Oportunidade
│
├── ANÁLISE DE PROBABILIDADES
│   ├── 📈 Forma Recente
│   ├── ⚔️ Confrontos Diretos
│   ├── 📊 Estatísticas Avançadas
│   └── 🌍 Fatores Contextuais
│
├── GESTÃO DE UNIDADES
│   ├── 🎯 Recomendação de Unidades
│   └── 💡 Motivos
│
├── GESTÃO DE BANCA
│   ├── 💰 Status da Banca
│   └── ⚖️ Gestão de Risco
│
├── AVALIAÇÃO DE RISCO
│   ├── ⚠️ Análise de Riscos
│   └── 💡 Recomendações
│
├── RECOMENDAÇÃO FINAL
│   ├── 🎯 Decisão
│   ├── 💭 Motivo
│   └── 📊 Métricas
│
└── RESUMO EXECUTIVO
    └── 📈 Conclusão e Recomendação
""")

def demonstrate_report_features():
    """Demonstra características do relatório"""
    
    print("\n🔧 CARACTERÍSTICAS DO RELATÓRIO")
    print("=" * 40)
    print("""
✅ FORMATO PROFISSIONAL
   • Layout estruturado e organizado
   • Emojis para melhor visualização
   • Seções claramente definidas
   • Informações hierarquizadas

✅ ANÁLISE COMPLETA
   • Análise de valor com odds de mercado
   • Cálculo de probabilidades realistas
   • Gestão de unidades por confiança
   • Gestão de banca com Kelly Fracionado
   • Avaliação de risco detalhada

✅ CONTEXTO DETALHADO
   • Informações climáticas
   • Dados do árbitro e público
   • Importância da partida
   • Fatores contextuais

✅ MÉTRICAS DE QUALIDADE
   • Score de confiança
   • Qualidade dos dados
   • Precisão histórica
   • Timestamp da análise

✅ RECOMENDAÇÃO CLARA
   • Decisão final objetiva
   • Justificativa detalhada
   • Métricas de apoio
   • Resumo executivo
""")

def show_example_output():
    """Mostra exemplo de saída do relatório"""
    
    print("\n📄 EXEMPLO DE SAÍDA DO RELATÓRIO")
    print("=" * 50)
    print("""
🎯 RELATÓRIO DE ANÁLISE PREDITIVA
============================================================

EVENTO ANALISADO
🏟️ Manchester City vs Arsenal
📅 Premier League - 2024/25
🕐 2024-01-15 - 15:00h GMT
🌦️ Condições: Céu limpo, 18°C
🏟️ Local: Estádio Manchester City
👨‍⚖️ Árbitro: Michael Oliver
👥 Público: 55,000
⭐ Importância: High

ANÁLISE DE VALOR
------------------------------
📊 Odds de Mercado:
   • Vitória Manchester City: 2.10
   • Empate: 3.20
   • Vitória Arsenal: 3.50

🎯 Probabilidades Calculadas:
   • Vitória Manchester City: 52.3%
   • Empate: 28.1%
   • Vitória Arsenal: 19.6%

💰 Valores Esperados:
   • Vitória Manchester City: +0.098
   • Empate: -0.102
   • Vitória Arsenal: -0.314

🏆 Melhor Oportunidade:
   • Resultado: Home Win
   • Odds: 2.10
   • Probabilidade: 52.3%
   • Valor Esperado: +0.098
   • Classificação: SIGNIFICANT

[... continua com todas as seções ...]

RECOMENDAÇÃO FINAL
------------------------------
🎯 Decisão: BET
💭 Motivo: Boa oportunidade com risco controlado
📊 Score de Confiança: 87.3%
⚠️ Nível de Risco: LOW
💰 Valor Esperado: +0.098
🎯 Unidades: 2.1

RESUMO EXECUTIVO
------------------------------
📈 Esta análise indica uma bet com confiança de 87.3% 
   e valor esperado de +0.098. A recomendação é apostar 
   2.1 unidades no resultado Home Win.
""")

def main():
    """Função principal"""
    
    print("🎯 MARABET AI - EXEMPLO DE RELATÓRIO DE ANÁLISE")
    print("=" * 60)
    print("Demonstração do sistema de relatórios profissionais")
    print("=" * 60)
    
    # Mostra estrutura
    show_report_structure()
    
    # Mostra características
    demonstrate_report_features()
    
    # Mostra exemplo de saída
    show_example_output()
    
    # Gera relatório real
    print("\n🚀 GERANDO RELATÓRIO REAL")
    print("=" * 40)
    
    result = generate_manchester_city_vs_arsenal_report()
    
    if result:
        print("\n✅ RELATÓRIO GERADO COM SUCESSO!")
        print("=" * 40)
        print(f"📁 Arquivo: {result['file_path']}")
        print(f"📊 Confiança: {result['analysis_result'].confidence_score:.1%}")
        print(f"🎯 Recomendação: {result['analysis_result'].final_recommendation['action']}")
        print(f"💰 EV: {result['analysis_result'].value_analysis['best_opportunity']['expected_value']:+.3f}")
        print(f"🎯 Unidades: {result['analysis_result'].unit_recommendation['recommended_units']:.1f}")
        
        print("\n🔧 COMO USAR O SISTEMA:")
        print("=" * 30)
        print("python example_report.py")
        print("python main.py --mode report")
        print("from report_generator import ReportGenerator")
        
        print("\n📋 VANTAGENS DO SISTEMA:")
        print("=" * 30)
        print("• Relatórios profissionais e completos")
        print("• Análise integrada de todos os sistemas")
        print("• Formatação clara e visual")
        print("• Métricas de qualidade")
        print("• Recomendações objetivas")
        print("• Salvamento automático")
        print("• Estrutura padronizada")
    
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
    print("=" * 60)

if __name__ == "__main__":
    main()
