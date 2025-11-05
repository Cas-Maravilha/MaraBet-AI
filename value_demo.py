#!/usr/bin/env python3
"""
Demonstração do Sistema de Identificação de Valor - MaraBet AI
Mostra o sistema de cálculo de EV e identificação de oportunidades
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from value_identification import ValueIdentifier, ValueThresholds, ValueLevel
from value_integration import AdvancedValueSystem
import numpy as np

def main():
    print("💰 MARABET AI - SISTEMA DE IDENTIFICAÇÃO DE VALOR")
    print("=" * 60)
    print("ETAPA 4: IDENTIFICAÇÃO DE VALOR")
    print("=" * 60)
    
    print("\n📊 FÓRMULA DE VALOR ESPERADO (EV):")
    print("-" * 40)
    print("EV = (Probabilidade Real × Odd) - 1")
    print("")
    print("Classificação de Valor:")
    print("  EV > 0    → Valor Positivo")
    print("  EV > 0.05 → Valor Significativo (>5%)")
    print("  EV > 0.10 → Valor Excelente (>10%)")
    
    # Testa calculadora de EV
    print("\n🧮 TESTE DA CALCULADORA DE EV")
    print("-" * 40)
    
    identifier = ValueIdentifier()
    
    # Exemplos de cálculo de EV
    test_cases = [
        {'probability': 0.50, 'odds': 2.00, 'description': 'Probabilidade 50%, Odds 2.00'},
        {'probability': 0.45, 'odds': 2.20, 'description': 'Probabilidade 45%, Odds 2.20 (Valor!)'},
        {'probability': 0.30, 'odds': 3.50, 'description': 'Probabilidade 30%, Odds 3.50'},
        {'probability': 0.25, 'odds': 4.00, 'description': 'Probabilidade 25%, Odds 4.00 (Valor!)'},
        {'probability': 0.60, 'odds': 1.80, 'description': 'Probabilidade 60%, Odds 1.80 (Sem valor)'},
    ]
    
    for case in test_cases:
        ev = identifier.calculate_expected_value(case['probability'], case['odds'])
        value_level = identifier.classify_value_level(ev)
        kelly = identifier.calculate_kelly_criterion(case['probability'], case['odds'])
        
        print(f"\n  {case['description']}:")
        print(f"    EV: {ev:.3f} ({ev*100:.1f}%)")
        print(f"    Nível: {value_level.value}")
        print(f"    Kelly: {kelly:.1%}")
    
    # Testa identificação de oportunidades
    print("\n🎯 TESTE DE IDENTIFICAÇÃO DE OPORTUNIDADES")
    print("-" * 40)
    
    # Dados de teste
    match_data = {
        'id': 'test_match_1',
        'home_team': 'Flamengo',
        'away_team': 'Palmeiras',
        'date': '2024-01-15'
    }
    
    probabilities = {
        'home_win': 0.45,  # Flamengo subestimado pelo mercado
        'draw': 0.30,
        'away_win': 0.25
    }
    
    market_odds = {
        'home_win': 2.20,  # Mercado oferece odds melhores
        'draw': 3.10,
        'away_win': 3.50
    }
    
    # Identifica oportunidades
    opportunities = identifier.identify_value_opportunities(match_data, probabilities, market_odds)
    
    print(f"\nOportunidades Identificadas - {match_data['home_team']} vs {match_data['away_team']}:")
    for i, opp in enumerate(opportunities, 1):
        print(f"\n  {i}. {opp.outcome.upper()}:")
        print(f"     Probabilidade: {opp.probability:.3f}")
        print(f"     Odds do mercado: {opp.market_odds:.2f}")
        print(f"     Odds calculadas: {opp.calculated_odds:.2f}")
        print(f"     EV: {opp.expected_value:.3f} ({opp.expected_value*100:.1f}%)")
        print(f"     Nível: {opp.value_level.value}")
        print(f"     Kelly: {opp.kelly_percentage:.1%}")
        print(f"     Confiança: {opp.confidence:.3f}")
        print(f"     Recomendação: {opp.recommendation}")
        print(f"     Diferença de odds: {opp.additional_metrics['odds_difference']:.2f}")
        print(f"     Score de valor: {opp.additional_metrics['value_score']:.1f}")
    
    # Testa análise completa
    print("\n🔬 TESTE DE ANÁLISE COMPLETA DE VALOR")
    print("-" * 40)
    
    analysis = identifier.create_value_analysis(match_data, probabilities, market_odds)
    
    print(f"\nAnálise Completa:")
    print(f"  Total de oportunidades: {analysis.total_opportunities}")
    print(f"  EV médio: {analysis.average_ev:.3f}")
    print(f"  EV máximo: {analysis.highest_ev:.3f}")
    print(f"  Confiança média: {analysis.confidence_score:.3f}")
    print(f"  Eficiência do mercado: {analysis.market_efficiency:.3f}")
    
    print(f"\nDistribuição de Valor:")
    for level, count in analysis.value_distribution.items():
        print(f"  {level}: {count}")
    
    if analysis.best_opportunity:
        best = analysis.best_opportunity
        print(f"\nMelhor Oportunidade:")
        print(f"  {best.outcome}: EV {best.expected_value:.3f} ({best.expected_value*100:.1f}%)")
        print(f"  Recomendação: {best.recommendation}")
        print(f"  Kelly: {best.kelly_percentage:.1%}")
    
    # Testa alertas
    print(f"\n🚨 TESTE DE ALERTAS DE VALOR")
    print("-" * 40)
    
    alerts = identifier.get_value_alerts([analysis], min_ev=0.05, min_confidence=0.7)
    
    if alerts:
        print(f"Alertas encontrados: {len(alerts)}")
        for i, alert in enumerate(alerts, 1):
            print(f"  {i}. {alert.outcome}: EV {alert.expected_value:.3f} - {alert.recommendation}")
    else:
        print("Nenhum alerta de valor significativo encontrado")
    
    # Testa sistema integrado
    print("\n🎭 SISTEMA INTEGRADO DE IDENTIFICAÇÃO DE VALOR")
    print("-" * 40)
    
    system = AdvancedValueSystem()
    
    # Analisa valor de uma partida
    value_result = system.analyze_match_value('Flamengo', 'Palmeiras', '2024-01-15')
    
    if value_result:
        print(f"\nAnálise Integrada de Valor:")
        print(f"  Partida: {value_result['match_info']['home_team']} vs {value_result['match_info']['away_team']}")
        
        va = value_result['value_analysis']
        print(f"  Oportunidades: {va['total_opportunities']}")
        print(f"  EV médio: {va['average_ev']:.3f}")
        print(f"  EV máximo: {va['highest_ev']:.3f}")
        print(f"  Eficiência do mercado: {va['market_efficiency']:.3f}")
        
        print(f"\n  Oportunidades Identificadas:")
        for i, opp in enumerate(va['opportunities'], 1):
            print(f"    {i}. {opp['outcome']}: EV {opp['expected_value']:.3f} - {opp['recommendation']}")
        
        if va['best_opportunity']:
            best = va['best_opportunity']
            print(f"\n  Melhor Oportunidade:")
            print(f"    {best['outcome']}: EV {best['expected_value']:.3f} - {best['recommendation']}")
        
        print(f"\n  Análise de Portfólio:")
        portfolio = value_result['portfolio_analysis']
        print(f"    Valor total: {portfolio['total_value']:.2f}")
        print(f"    Apostas recomendadas: {len(portfolio['recommended_bets'])}")
        print(f"    ROI esperado: {portfolio['expected_roi']:.1f}%")
        
        print(f"\n  Recomendações Estratégicas:")
        strategic = value_result['strategic_recommendations']
        for i, rec in enumerate(strategic['recommendations'][:3], 1):
            print(f"    {i}. {rec['type']}: {rec.get('message', rec.get('reasoning', ''))}")
        
        print(f"\n  Análise de Risco:")
        risk = value_result['risk_analysis']
        print(f"    Nível: {risk['risk_level']}")
        print(f"    Score: {risk['risk_score']}")
        print(f"    Riscos identificados: {risk['total_risks']}")
        
        print(f"\n  Resumo Executivo:")
        summary = value_result['executive_summary']
        print(f"    Recomendação: {summary['recommendation']}")
        print(f"    Nível de risco: {summary['risk_level']}")
        for insight in summary['insights'][:3]:
            print(f"    • {insight}")
    
    # Testa escaneamento de mercado
    print("\n📈 TESTE DE ESCANEAMENTO DE MERCADO")
    print("-" * 40)
    
    # Cria dados históricos simulados
    historical_matches = []
    for i in range(20):
        match = {
            'id': f'match_{i}',
            'home_team': f'Team_{i%10}',
            'away_team': f'Team_{(i+5)%10}',
            'date': f'2024-01-{i%30+1:02d}',
            'home_odds': np.random.uniform(1.5, 4.0),
            'draw_odds': np.random.uniform(2.8, 3.5),
            'away_odds': np.random.uniform(1.8, 5.0)
        }
        historical_matches.append(match)
    
    # Executa backtesting de valor
    backtest_result = system.run_value_backtesting(historical_matches, 1000)
    
    if backtest_result['success']:
        metrics = backtest_result['metrics']
        print(f"\nResultados do Backtesting de Valor:")
        print(f"  Trades: {metrics['total_trades']}")
        print(f"  Taxa de acerto: {metrics['win_rate']:.1%}")
        print(f"  ROI: {metrics['roi']:.2f}%")
        print(f"  EV médio: {metrics['avg_expected_value']:.3f}")
        print(f"  Confiança média: {metrics['avg_confidence']:.3f}")
        print(f"  Kelly médio: {metrics['avg_kelly_percentage']:.1%}")
        print(f"  Precisão do EV: {metrics['ev_accuracy']:.1%}")
        print(f"  ROI ajustado por valor: {metrics['value_adjusted_roi']:.2f}%")
    else:
        print(f"Falha no backtesting: {backtest_result['error']}")
    
    # Analytics do sistema
    print("\n📊 ANALYTICS DO SISTEMA")
    print("-" * 40)
    
    analytics = system.get_value_analytics()
    print(f"  Total de análises: {analytics['total_analyses']}")
    print(f"  EV médio: {analytics['average_ev']:.3f}")
    print(f"  EV máximo: {analytics['max_ev']:.3f}")
    print(f"  Confiança média: {analytics['average_confidence']:.3f}")
    print(f"  Oportunidades positivas: {analytics['positive_ev_percentage']:.1f}%")
    
    print(f"\n  Distribuição de Níveis de Valor:")
    for level, count in analytics['value_level_distribution'].items():
        print(f"    {level}: {count}")
    
    # Testa com pesos customizados
    print("\n🔧 TESTE COM PESOS CUSTOMIZADOS")
    print("-" * 40)
    
    custom_thresholds = ValueThresholds(
        positive=0.02,    # 2% para valor positivo
        significant=0.08, # 8% para valor significativo
        excellent=0.15    # 15% para valor excelente
    )
    
    custom_identifier = ValueIdentifier(custom_thresholds)
    custom_analysis = custom_identifier.create_value_analysis(match_data, probabilities, market_odds)
    
    print(f"Análise com Limiares Customizados:")
    print(f"  Limiares: Positivo > {custom_thresholds.positive:.1%}, Significativo > {custom_thresholds.significant:.1%}, Excelente > {custom_thresholds.excellent:.1%}")
    print(f"  EV médio: {custom_analysis.average_ev:.3f}")
    print(f"  Distribuição:")
    for level, count in custom_analysis.value_distribution.items():
        print(f"    {level}: {count}")
    
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRAÇÃO DO SISTEMA DE IDENTIFICAÇÃO DE VALOR CONCLUÍDA!")
    print("=" * 60)
    
    print(f"\n📋 RESUMO DA IMPLEMENTAÇÃO:")
    print(f"   ✅ Fórmula de Valor Esperado (EV) implementada")
    print(f"   ✅ Classificação de valor (Positivo, Significativo, Excelente)")
    print(f"   ✅ Sistema de identificação de oportunidades")
    print(f"   ✅ Cálculo de Kelly Criterion para sizing")
    print(f"   ✅ Análise de confiança e risco")
    print(f"   ✅ Sistema de alertas de valor")
    print(f"   ✅ Análise de portfólio")
    print(f"   ✅ Backtesting com métricas específicas")
    print(f"   ✅ Analytics e monitoramento")
    
    print(f"\n🚀 COMO USAR:")
    print(f"   python main.py --mode value")
    print(f"   python value_demo.py")
    print(f"   python main.py --web")
    
    print(f"\n🔧 VANTAGENS DO SISTEMA:")
    print(f"   • Fórmula EV transparente e precisa")
    print(f"   • Classificação automática de valor")
    print(f"   • Kelly Criterion para sizing otimizado")
    print(f"   • Análise de confiança robusta")
    print(f"   • Sistema de alertas inteligente")
    print(f"   • Backtesting com métricas específicas")
    print(f"   • Analytics para monitoramento contínuo")

if __name__ == "__main__":
    main()
