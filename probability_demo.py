#!/usr/bin/env python3
"""
Demonstração do Sistema de Cálculo de Probabilidades - MaraBet AI
Mostra a estrutura de pesos específica para cálculo de probabilidades
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from probability_calculator import ProbabilityCalculator, ProbabilityWeights
from probability_integration import AdvancedProbabilitySystem
import numpy as np

def main():
    print("📊 MARABET AI - SISTEMA DE CÁLCULO DE PROBABILIDADES")
    print("=" * 60)
    print("ETAPA 3: CÁLCULO DE PROBABILIDADES")
    print("=" * 60)
    
    print("\n🎯 ESTRUTURA DE PESOS IMPLEMENTADA:")
    print("-" * 40)
    print("Probabilidade Real = (")
    print("  40% Histórico Recente +")
    print("  25% Confrontos Diretos +")
    print("  15% Estatísticas Avançadas +")
    print("  10% Fatores Contextuais +")
    print("  10% Análise de Momentum")
    print(")")
    
    # Testa com pesos padrão
    print("\n📈 TESTE COM PESOS PADRÃO")
    print("-" * 40)
    
    calculator = ProbabilityCalculator()
    
    # Dados de teste
    match_data = {
        'home_team': 'Flamengo',
        'away_team': 'Palmeiras',
        'date': '2024-01-15'
    }
    
    # Calcula probabilidades
    result = calculator.calculate_probabilities(match_data)
    
    print(f"\nProbabilidades Finais:")
    print(f"  Casa: {result.home_win:.3f} ({result.home_win*100:.1f}%)")
    print(f"  Empate: {result.draw:.3f} ({result.draw*100:.1f}%)")
    print(f"  Fora: {result.away_win:.3f} ({result.away_win*100:.1f}%)")
    print(f"  Confiança: {result.confidence:.3f}")
    
    print(f"\nBreakdown Detalhado por Componente:")
    for component, data in result.breakdown.items():
        print(f"\n  {component.upper().replace('_', ' ')}:")
        print(f"    Peso: {data['weight']:.1%}")
        print(f"    Confiança: {data['confidence']:.3f}")
        print(f"    Probabilidades:")
        print(f"      Casa: {data['probabilities']['home_win']:.3f}")
        print(f"      Empate: {data['probabilities']['draw']:.3f}")
        print(f"      Fora: {data['probabilities']['away_win']:.3f}")
        print(f"    Contribuição Final:")
        print(f"      Casa: {data['contribution']['home_win']:.3f}")
        print(f"      Empate: {data['contribution']['draw']:.3f}")
        print(f"      Fora: {data['contribution']['away_win']:.3f}")
    
    # Testa com pesos customizados
    print("\n🔧 TESTE COM PESOS CUSTOMIZADOS")
    print("-" * 40)
    print("Pesos customizados: 50% Histórico, 30% H2H, 20% Outros")
    
    custom_weights = ProbabilityWeights(
        historico_recente=0.50,      # 50%
        confrontos_diretos=0.30,     # 30%
        estatisticas_avancadas=0.10, # 10%
        fatores_contextuais=0.05,    # 5%
        analise_momentum=0.05        # 5%
    )
    
    custom_calculator = ProbabilityCalculator(custom_weights)
    custom_result = custom_calculator.calculate_probabilities(match_data)
    
    print(f"\nProbabilidades com Pesos Customizados:")
    print(f"  Casa: {custom_result.home_win:.3f} ({custom_result.home_win*100:.1f}%)")
    print(f"  Empate: {custom_result.draw:.3f} ({custom_result.draw*100:.1f}%)")
    print(f"  Fora: {custom_result.away_win:.3f} ({custom_result.away_win*100:.1f}%)")
    print(f"  Confiança: {custom_result.confidence:.3f}")
    
    # Comparação de resultados
    print(f"\n📊 COMPARAÇÃO DE RESULTADOS:")
    print(f"  Diferença Casa: {(custom_result.home_win - result.home_win)*100:+.1f}%")
    print(f"  Diferença Empate: {(custom_result.draw - result.draw)*100:+.1f}%")
    print(f"  Diferença Fora: {(custom_result.away_win - result.away_win)*100:+.1f}%")
    
    # Testa sistema integrado
    print("\n🔬 SISTEMA INTEGRADO DE PROBABILIDADES")
    print("-" * 40)
    
    system = AdvancedProbabilitySystem()
    
    # Calcula probabilidades com sistema integrado
    integrated_result = system.calculate_match_probabilities('Flamengo', 'Palmeiras', '2024-01-15')
    
    if integrated_result:
        print(f"\nAnálise Integrada:")
        print(f"  Probabilidades:")
        print(f"    Casa: {integrated_result['probabilities']['home_win']:.3f}")
        print(f"    Empate: {integrated_result['probabilities']['draw']:.3f}")
        print(f"    Fora: {integrated_result['probabilities']['away_win']:.3f}")
        print(f"  Confiança: {integrated_result['confidence']:.3f}")
        
        print(f"\n  Odds Calculadas:")
        odds = integrated_result['odds']
        print(f"    Casa: {odds['calculated_odds']['home']:.2f}")
        print(f"    Empate: {odds['calculated_odds']['draw']:.2f}")
        print(f"    Fora: {odds['calculated_odds']['away']:.2f}")
        
        print(f"\n  Análise de Apostas:")
        betting = integrated_result['betting_analysis']
        print(f"    Melhor valor: {betting['best_value_bet']['outcome']}")
        print(f"    Valor esperado: {betting['best_value_bet']['expected_value']:.1%}")
        print(f"    Kelly: {betting['best_value_bet']['kelly_percentage']:.1%}")
        print(f"    Rating: {betting['best_value_bet']['value_rating']}")
        
        print(f"\n  Análise de Confiança:")
        confidence = integrated_result['confidence_analysis']
        print(f"    Nível: {confidence['confidence_level']}")
        print(f"    Incerteza: {confidence['uncertainty']:.3f}")
        print(f"    Consistência: {confidence['consistency']:.3f}")
        
        print(f"\n  Recomendações:")
        recommendations = integrated_result['recommendations']
        for i, rec in enumerate(recommendations['recommendations'][:3], 1):
            print(f"    {i}. {rec['outcome']}: {rec['recommendation']} (EV: {rec['expected_value']:.1%})")
        
        print(f"\n  Resumo Executivo:")
        summary = integrated_result['executive_summary']
        print(f"    Predição: {summary['prediction']['most_likely']} ({summary['prediction']['probability']:.1%})")
        print(f"    Fator mais influente: {summary['most_influential_factor']}")
        print(f"    Insights:")
        for insight in summary['insights'][:3]:
            print(f"      • {insight}")
    
    # Testa backtesting
    print("\n📈 BACKTESTING COM SISTEMA DE PROBABILIDADES")
    print("-" * 40)
    
    # Cria dados históricos simulados
    historical_matches = []
    for i in range(50):
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
    
    # Executa backtesting
    backtest_result = system.run_probability_backtesting(historical_matches, 1000)
    
    if backtest_result['success']:
        metrics = backtest_result['metrics']
        print(f"\nResultados do Backtesting:")
        print(f"  Trades: {metrics['total_trades']}")
        print(f"  Taxa de acerto: {metrics['win_rate']:.1%}")
        print(f"  ROI: {metrics['roi']:.2f}%")
        print(f"  Confiança média: {metrics['avg_confidence']:.3f}")
        print(f"  Probabilidade média: {metrics['avg_probability']:.3f}")
        print(f"  Precisão das probabilidades: {metrics['probability_accuracy']:.1%}")
        print(f"  ROI ajustado por confiança: {metrics['confidence_adjusted_roi']:.2f}%")
    else:
        print(f"Falha no backtesting: {backtest_result['error']}")
    
    # Analytics do sistema
    print("\n📊 ANALYTICS DO SISTEMA")
    print("-" * 40)
    
    analytics = system.get_probability_analytics()
    print(f"  Total de cálculos: {analytics['total_calculations']}")
    print(f"  Confiança média: {analytics['average_confidence']:.3f}")
    
    print(f"\n  Distribuição de Probabilidades:")
    dist = analytics['probability_distribution']
    for outcome in ['home_win', 'draw', 'away_win']:
        data = dist[outcome]
        print(f"    {outcome}:")
        print(f"      Média: {data['mean']:.3f}")
        print(f"      Desvio: {data['std']:.3f}")
        print(f"      Min: {data['min']:.3f}")
        print(f"      Max: {data['max']:.3f}")
    
    print(f"\n  Pesos Utilizados:")
    weights = analytics['weights_used']
    for component, weight in weights.items():
        print(f"    {component}: {weight:.1%}")
    
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRAÇÃO DO SISTEMA DE PROBABILIDADES CONCLUÍDA!")
    print("=" * 60)
    
    print(f"\n📋 RESUMO DA IMPLEMENTAÇÃO:")
    print(f"   ✅ Estrutura de pesos específica (40% + 25% + 15% + 10% + 10%)")
    print(f"   ✅ Cálculo de probabilidades por componente")
    print(f"   ✅ Combinação ponderada de resultados")
    print(f"   ✅ Análise de confiança e incerteza")
    print(f"   ✅ Cálculo de odds baseado em probabilidades")
    print(f"   ✅ Análise de valor das apostas")
    print(f"   ✅ Recomendações baseadas em probabilidades")
    print(f"   ✅ Backtesting com métricas específicas")
    print(f"   ✅ Analytics e monitoramento")
    
    print(f"\n🚀 COMO USAR:")
    print(f"   python main.py --mode probabilities")
    print(f"   python probability_demo.py")
    print(f"   python main.py --web")
    
    print(f"\n🔧 VANTAGENS DO SISTEMA:")
    print(f"   • Estrutura de pesos transparente e ajustável")
    print(f"   • Breakdown detalhado por componente")
    print(f"   • Análise de confiança robusta")
    print(f"   • Cálculo preciso de odds")
    print(f"   • Recomendações baseadas em valor esperado")
    print(f"   • Backtesting com métricas específicas")
    print(f"   • Analytics para monitoramento contínuo")

if __name__ == "__main__":
    main()
