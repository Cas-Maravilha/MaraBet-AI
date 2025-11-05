#!/usr/bin/env python3
"""
Demonstração do Sistema de Gestão de Unidades - MaraBet AI
Mostra o sistema de unidades recomendadas por nível de confiança
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unit_management import UnitManager, UnitConfig, ConfidenceLevel
from unit_integration import AdvancedUnitSystem
import numpy as np

def main():
    print("🎯 MARABET AI - SISTEMA DE GESTÃO DE UNIDADES")
    print("=" * 60)
    print("SISTEMA DE UNIDADES RECOMENDADAS POR CONFIANÇA")
    print("=" * 60)
    
    print("\n📊 UNIDADES RECOMENDADAS POR NÍVEL DE CONFIANÇA:")
    print("-" * 40)
    print("Alta Confiança (85-90%): 2-3 unidades")
    print("Média-Alta (75-84%): 1.5-2 unidades")
    print("Média (70-74%): 1-1.5 unidades")
    print("Baixa (<70%): 0.5-1 unidades")
    
    # Testa calculadora de unidades
    print("\n🧮 TESTE DA CALCULADORA DE UNIDADES")
    print("-" * 40)
    
    # Configuração de teste
    config = UnitConfig(
        base_unit_value=100.0,
        max_units_per_bet=3.0,
        min_units_per_bet=0.5,
        high_confidence_units=(2.0, 3.0),
        medium_high_confidence_units=(1.5, 2.0),
        medium_confidence_units=(1.0, 1.5),
        low_confidence_units=(0.5, 1.0)
    )
    
    manager = UnitManager(config)
    
    # Exemplos de cálculo de unidades
    test_cases = [
        {'confidence': 0.88, 'expected_value': 0.15, 'description': 'Alta confiança, alto EV'},
        {'confidence': 0.80, 'expected_value': 0.10, 'description': 'Confiança média-alta, bom EV'},
        {'confidence': 0.72, 'expected_value': 0.08, 'description': 'Confiança média, EV moderado'},
        {'confidence': 0.65, 'expected_value': 0.05, 'description': 'Baixa confiança, baixo EV'},
        {'confidence': 0.92, 'expected_value': 0.20, 'description': 'Muito alta confiança, muito alto EV'},
    ]
    
    for case in test_cases:
        recommendation = manager.calculate_recommended_units(
            case['confidence'], 
            case['expected_value']
        )
        
        print(f"\n  {case['description']}:")
        print(f"    Confiança: {recommendation.confidence_percentage:.1%}")
        print(f"    Nível: {recommendation.confidence_level.value}")
        print(f"    Unidades: {recommendation.recommended_units:.1f}")
        print(f"    Valor da unidade: R$ {recommendation.unit_value:.2f}")
        print(f"    Stake total: R$ {recommendation.total_stake:.2f}")
        print(f"    Fatores de ajuste: {recommendation.adjustment_factors}")
        print(f"    Motivos: {', '.join(recommendation.reasoning)}")
    
    # Testa diferentes níveis de confiança
    print("\n🎯 TESTE DE DIFERENTES NÍVEIS DE CONFIANÇA")
    print("-" * 40)
    
    confidence_levels = [
        (0.90, "Alta Confiança"),
        (0.80, "Média-Alta"),
        (0.72, "Média"),
        (0.65, "Baixa")
    ]
    
    for confidence, description in confidence_levels:
        recommendation = manager.calculate_recommended_units(confidence, 0.10)
        
        print(f"\n  {description} ({confidence:.0%}):")
        print(f"    Nível: {recommendation.confidence_level.value}")
        print(f"    Unidades: {recommendation.recommended_units:.1f}")
        print(f"    Stake: R$ {recommendation.total_stake:.2f}")
        print(f"    Recomendação: {recommendation.recommendation}")
    
    # Testa execução de apostas
    print("\n🎲 TESTE DE EXECUÇÃO DE APOSTAS COM UNIDADES")
    print("-" * 40)
    
    # Simula algumas apostas
    bets = [
        {'confidence': 0.88, 'expected_value': 0.12, 'outcome': 'home_win', 'result': 'home_win', 'odds': 2.20},
        {'confidence': 0.78, 'expected_value': 0.08, 'outcome': 'draw', 'result': 'away_win', 'odds': 3.50},
        {'confidence': 0.71, 'expected_value': 0.06, 'outcome': 'away_win', 'result': 'away_win', 'odds': 4.00},
        {'confidence': 0.85, 'expected_value': 0.15, 'outcome': 'home_win', 'result': 'home_win', 'odds': 2.10},
    ]
    
    for i, bet in enumerate(bets, 1):
        recommendation = manager.calculate_recommended_units(
            bet['confidence'], 
            bet['expected_value']
        )
        result = manager.execute_unit_bet(
            recommendation, 
            bet['outcome'], 
            bet['result'], 
            bet['odds']
        )
        
        print(f"\n  Aposta {i} ({bet['confidence']:.0%} confiança):")
        print(f"    Unidades: {recommendation.recommended_units:.1f}")
        print(f"    Stake: R$ {recommendation.total_stake:.2f}")
        print(f"    Resultado: {result['result']}")
        print(f"    Lucro: R$ {result['profit']:.2f}")
        print(f"    Lucro em unidades: {result['profit_units']:.1f}")
        print(f"    Capital: R$ {result['new_capital']:.2f}")
    
    # Analytics do sistema
    print(f"\n📊 ANALYTICS DO SISTEMA DE UNIDADES:")
    print("-" * 40)
    
    analytics = manager.get_unit_analytics()
    print(f"  Total de apostas: {analytics['total_bets']}")
    print(f"  Taxa de acerto: {analytics['win_rate']:.1%}")
    print(f"  Unidades apostadas: {analytics['total_units_staked']:.1f}")
    print(f"  Lucro em unidades: {analytics['total_units_profit']:.1f}")
    print(f"  Unidades médias por aposta: {analytics['average_units_per_bet']:.1f}")
    print(f"  Capital atual: R$ {analytics['current_bankroll']:.2f}")
    print(f"  Valor da unidade: R$ {analytics['unit_value']:.2f}")
    
    print(f"\n  Performance por Nível de Confiança:")
    performance = manager.get_unit_performance_by_level()
    for level, perf in performance.items():
        if perf.total_bets > 0:
            print(f"    {level}:")
            print(f"      Apostas: {perf.total_bets}")
            print(f"      Taxa de acerto: {perf.win_rate:.1%}")
            print(f"      ROI: {perf.roi:.1f}%")
            print(f"      Unidades médias: {perf.average_units_per_bet:.1f}")
            print(f"      Sequência máxima de vitórias: {perf.best_streak}")
            print(f"      Sequência máxima de derrotas: {perf.worst_streak}")
    
    # Testa sistema integrado
    print("\n🎭 SISTEMA INTEGRADO DE GESTÃO DE UNIDADES")
    print("-" * 40)
    
    system = AdvancedUnitSystem()
    
    # Analisa aposta com unidades
    opportunity = system.analyze_bet_with_units('Flamengo', 'Palmeiras', '2024-01-15')
    
    if opportunity:
        print(f"\nAnálise de Aposta com Unidades:")
        print(f"  Partida: {opportunity['match_info']['home_team']} vs {opportunity['match_info']['away_team']}")
        
        unit_rec = opportunity['unit_recommendation']
        print(f"  Nível de confiança: {unit_rec['confidence_level']}")
        print(f"  Confiança: {unit_rec['confidence_percentage']:.1%}")
        print(f"  Unidades recomendadas: {unit_rec['recommended_units']:.1f}")
        print(f"  Valor da unidade: R$ {unit_rec['unit_value']:.2f}")
        print(f"  Stake total: R$ {unit_rec['total_stake']:.2f}")
        print(f"  Fatores de ajuste: {unit_rec['adjustment_factors']}")
        print(f"  Motivos: {', '.join(unit_rec['reasoning'])}")
        
        final_rec = opportunity['final_recommendation']
        print(f"  Recomendação final: {final_rec['action']}")
        print(f"  Motivo: {final_rec['reason']}")
        
        risk = opportunity['risk_analysis']
        print(f"  Nível de risco: {risk['risk_level']}")
        print(f"  Score de risco: {risk['risk_score']}")
        print(f"  Risco de capital: {risk['capital_risk_percentage']:.1f}%")
        
        print(f"\n  Confiança combinada: {opportunity['combined_confidence']:.1%}")
        print(f"  Performance recente: {opportunity['recent_performance']:.1%}")
        print(f"  Sequência atual: {opportunity['current_streak']}")
    
    # Testa backtesting com unidades
    print("\n📈 TESTE DE BACKTESTING COM GESTÃO DE UNIDADES")
    print("-" * 40)
    
    # Cria dados históricos simulados
    historical_matches = []
    for i in range(30):
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
    backtest_result = system.run_unit_backtesting(historical_matches, 1000)
    
    if backtest_result['success']:
        summary = backtest_result['summary']
        print(f"\nResultados do Backtesting:")
        print(f"  Oportunidades analisadas: {summary['total_opportunities']}")
        print(f"  Apostas executadas: {summary['executed_bets']}")
        print(f"  Taxa de execução: {summary['execution_rate']:.1%}")
        print(f"  Capital inicial: R$ {summary['initial_capital']:.2f}")
        print(f"  Capital final: R$ {summary['final_capital']:.2f}")
        print(f"  Lucro total: R$ {summary['total_profit']:.2f}")
        print(f"  ROI: {summary['profit_percentage']:.1f}%")
        print(f"  Unidades apostadas: {summary['total_units_staked']:.1f}")
        print(f"  Lucro em unidades: {summary['total_units_profit']:.1f}")
        print(f"  Unidades médias por aposta: {summary['average_units_per_bet']:.1f}")
        
        print(f"\nPerformance por Nível de Confiança:")
        performance_by_level = backtest_result['performance_by_level']
        for level, perf in performance_by_level.items():
            if perf.total_bets > 0:
                print(f"  {level}:")
                print(f"    Apostas: {perf.total_bets}")
                print(f"    Taxa de acerto: {perf.win_rate:.1%}")
                print(f"    ROI: {perf.roi:.1f}%")
                print(f"    Unidades médias: {perf.average_units_per_bet:.1f}")
    else:
        print(f"Falha no backtesting: {backtest_result['error']}")
    
    # Testa otimização de estratégia
    print("\n🔧 TESTE DE OTIMIZAÇÃO DE ESTRATÉGIA DE UNIDADES")
    print("-" * 40)
    
    optimization_result = system.optimize_unit_strategy(historical_matches, 1000)
    
    if optimization_result['success']:
        print(f"\nResultados da Otimização:")
        for strategy, metrics in optimization_result['results'].items():
            print(f"  {strategy.upper()}:")
            print(f"    ROI: {metrics['profit_percentage']:.1f}%")
            print(f"    Unidades apostadas: {metrics['total_units_staked']:.1f}")
            print(f"    Lucro em unidades: {metrics['total_units_profit']:.1f}")
            print(f"    Unidades médias: {metrics['average_units_per_bet']:.1f}")
            print(f"    Taxa de execução: {metrics['execution_rate']:.1%}")
        
        print(f"\nMelhor estratégia: {optimization_result['best_strategy'].upper()}")
        best_perf = optimization_result['best_performance']
        print(f"ROI: {best_perf['profit_percentage']:.1f}%")
        print(f"Unidades médias: {best_perf['average_units_per_bet']:.1f}")
        
        recommendation = optimization_result['recommendation']
        print(f"Recomendação: {recommendation['recommendation']}")
        print(f"Confiança: {recommendation['confidence']}")
        print(f"Motivo: {recommendation['reasoning']}")
    else:
        print(f"Falha na otimização: {optimization_result['error']}")
    
    # Analytics completos
    print("\n📊 ANALYTICS COMPLETOS DO SISTEMA")
    print("-" * 40)
    
    analytics = system.get_unit_analytics()
    unit_analytics = analytics['unit_analytics']
    trends = analytics['trends']
    strategic = analytics['strategic_recommendations']
    
    print(f"  Estatísticas Gerais:")
    print(f"    Total de apostas: {unit_analytics['total_bets']}")
    print(f"    Taxa de acerto: {unit_analytics['win_rate']:.1%}")
    print(f"    Unidades apostadas: {unit_analytics['total_units_staked']:.1f}")
    print(f"    Lucro em unidades: {unit_analytics['total_units_profit']:.1f}")
    print(f"    Capital atual: R$ {unit_analytics['current_bankroll']:.2f}")
    
    print(f"\n  Tendências:")
    print(f"    Tendência de unidades: {trends.get('unit_trend', 'N/A')}")
    print(f"    Unidades recentes: {trends.get('recent_units_avg', 0):.1f}")
    print(f"    Unidades gerais: {trends.get('overall_units_avg', 0):.1f}")
    
    print(f"\n  Recomendações Estratégicas:")
    for i, rec in enumerate(strategic[:3], 1):
        print(f"    {i}. {rec['type']}: {rec['message']}")
    
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRAÇÃO DO SISTEMA DE GESTÃO DE UNIDADES CONCLUÍDA!")
    print("=" * 60)
    
    print(f"\n📋 RESUMO DA IMPLEMENTAÇÃO:")
    print(f"   ✅ Sistema de unidades por nível de confiança")
    print(f"   ✅ Alta Confiança (85-90%): 2-3 unidades")
    print(f"   ✅ Média-Alta (75-84%): 1.5-2 unidades")
    print(f"   ✅ Média (70-74%): 1-1.5 unidades")
    print(f"   ✅ Baixa (<70%): 0.5-1 unidades")
    print(f"   ✅ Fatores de ajuste dinâmicos")
    print(f"   ✅ Sistema de sizing inteligente")
    print(f"   ✅ Backtesting com métricas específicas")
    print(f"   ✅ Otimização de estratégia")
    print(f"   ✅ Analytics e recomendações")
    
    print(f"\n🚀 COMO USAR:")
    print(f"   python main.py --mode units")
    print(f"   python unit_demo.py")
    print(f"   python main.py --web")
    
    print(f"\n🔧 VANTAGENS DO SISTEMA:")
    print(f"   • Unidades baseadas em confiança real")
    print(f"   • Ajuste dinâmico por múltiplos fatores")
    print(f"   • Gestão de risco por unidades")
    print(f"   • Backtesting com métricas específicas")
    print(f"   • Otimização automática de estratégia")
    print(f"   • Analytics completos para monitoramento")

if __name__ == "__main__":
    main()
