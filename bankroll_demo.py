#!/usr/bin/env python3
"""
Demonstração do Sistema de Gestão de Banca - MaraBet AI
Mostra o sistema de Kelly Fracionado e gestão de risco
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bankroll_management import BankrollManager, BankrollConfig, RiskLevel
from bankroll_integration import AdvancedBankrollSystem
import numpy as np

def main():
    print("💰 MARABET AI - SISTEMA DE GESTÃO DE BANCA")
    print("=" * 60)
    print("ETAPA 5: GESTÃO DE BANCA")
    print("=" * 60)
    
    print("\n📊 CRITÉRIO DE KELLY FRACIONADO:")
    print("-" * 40)
    print("Stake % = (f/4) × [(P × O) - 1] / (O - 1)")
    print("")
    print("Onde:")
    print("  f = fração conservadora (0.25)")
    print("  P = probabilidade estimada")
    print("  O = odd decimal")
    print("")
    print("Níveis de Risco:")
    print("  CONSERVATIVE: f = 0.25 (25%)")
    print("  MODERATE: f = 0.50 (50%)")
    print("  AGGRESSIVE: f = 0.75 (75%)")
    print("  MAXIMUM: f = 1.00 (100%)")
    
    # Testa calculadora de Kelly Fracionado
    print("\n🧮 TESTE DA CALCULADORA DE KELLY FRACIONADO")
    print("-" * 40)
    
    # Configuração de teste
    config = BankrollConfig(
        initial_capital=1000.0,
        conservative_fraction=0.25,
        max_stake_percentage=0.10,
        risk_level=RiskLevel.CONSERVATIVE
    )
    
    manager = BankrollManager(config)
    
    # Exemplos de cálculo de Kelly Fracionado
    test_cases = [
        {'probability': 0.50, 'odds': 2.00, 'description': 'Probabilidade 50%, Odds 2.00'},
        {'probability': 0.45, 'odds': 2.20, 'description': 'Probabilidade 45%, Odds 2.20'},
        {'probability': 0.30, 'odds': 3.50, 'description': 'Probabilidade 30%, Odds 3.50'},
        {'probability': 0.25, 'odds': 4.00, 'description': 'Probabilidade 25%, Odds 4.00'},
        {'probability': 0.60, 'odds': 1.80, 'description': 'Probabilidade 60%, Odds 1.80 (Sem valor)'},
    ]
    
    for case in test_cases:
        sizing = manager.calculate_kelly_fractional(case['probability'], case['odds'])
        
        print(f"\n  {case['description']}:")
        print(f"    Stake %: {sizing.stake_percentage:.2%}")
        print(f"    Stake Amount: R$ {sizing.stake_amount:.2f}")
        print(f"    EV: {sizing.expected_value:.3f}")
        print(f"    Recomendação: {sizing.recommendation}")
        print(f"    Risco: {sizing.risk_factors['overall_risk']}")
        print(f"    Score de risco: {sizing.risk_factors['risk_score']}")
    
    # Testa diferentes níveis de risco
    print("\n🎯 TESTE DE DIFERENTES NÍVEIS DE RISCO")
    print("-" * 40)
    
    probability = 0.45
    odds = 2.20
    
    for risk_level in [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE, RiskLevel.MAXIMUM]:
        sizing = manager.calculate_kelly_fractional(probability, odds, risk_level)
        
        print(f"\n  {risk_level.value}:")
        print(f"    Fração: {sizing.risk_factors.get('fraction', 'N/A')}")
        print(f"    Stake %: {sizing.stake_percentage:.2%}")
        print(f"    Stake Amount: R$ {sizing.stake_amount:.2f}")
        print(f"    Recomendação: {sizing.recommendation}")
    
    # Testa execução de apostas
    print("\n🎲 TESTE DE EXECUÇÃO DE APOSTAS")
    print("-" * 40)
    
    # Simula algumas apostas
    bets = [
        {'probability': 0.45, 'odds': 2.20, 'outcome': 'home_win', 'result': 'home_win'},
        {'probability': 0.30, 'odds': 3.50, 'outcome': 'draw', 'result': 'away_win'},
        {'probability': 0.25, 'odds': 4.00, 'outcome': 'away_win', 'result': 'away_win'},
        {'probability': 0.40, 'odds': 2.50, 'outcome': 'home_win', 'result': 'home_win'},
    ]
    
    for i, bet in enumerate(bets, 1):
        sizing = manager.calculate_kelly_fractional(bet['probability'], bet['odds'])
        result = manager.execute_bet(sizing, bet['result'], bet['outcome'])
        
        print(f"\n  Aposta {i}:")
        print(f"    Stake: R$ {sizing.stake_amount:.2f} ({sizing.stake_percentage:.1%})")
        print(f"    Resultado: {result['result']}")
        print(f"    Lucro: R$ {result['profit']:.2f}")
        print(f"    Capital: R$ {result['new_capital']:.2f}")
    
    # Status da banca
    print(f"\n📊 STATUS DA BANCA:")
    print("-" * 40)
    
    status = manager.get_bankroll_status()
    print(f"  Capital atual: R$ {status.current_capital:.2f}")
    print(f"  Capital inicial: R$ {status.initial_capital:.2f}")
    print(f"  Lucro total: R$ {status.total_profit:.2f}")
    print(f"  ROI: {status.profit_percentage:.1f}%")
    print(f"  Drawdown: {status.drawdown_percentage:.1f}%")
    print(f"  Drawdown máximo: {status.max_drawdown_percentage:.1f}%")
    print(f"  Taxa de acerto: {status.win_rate:.1%}")
    print(f"  Total de apostas: {status.total_bets}")
    print(f"  Stake médio: R$ {status.average_stake:.2f}")
    print(f"  Status: {status.status}")
    print(f"  Nível de risco: {status.risk_level.value}")
    
    # Verifica limites de risco
    print(f"\n⚠️ VERIFICAÇÃO DE LIMITES DE RISCO:")
    print("-" * 40)
    
    risk_check = manager.check_risk_limits()
    print(f"  Total de alertas: {risk_check['total_alerts']}")
    print(f"  Alertas críticos: {risk_check['critical_alerts']}")
    
    if risk_check['alerts']:
        for alert in risk_check['alerts']:
            print(f"    {alert['level']}: {alert['message']}")
    else:
        print("    Nenhum alerta de risco ativo")
    
    # Estatísticas de apostas
    print(f"\n📈 ESTATÍSTICAS DE APOSTAS:")
    print("-" * 40)
    
    stats = manager.get_betting_statistics()
    print(f"  Total de apostas: {stats['total_bets']}")
    print(f"  Apostas vencedoras: {stats['winning_bets']}")
    print(f"  Apostas perdedoras: {stats['losing_bets']}")
    print(f"  Taxa de acerto: {stats['win_rate']:.1%}")
    print(f"  Total apostado: R$ {stats['total_staked']:.2f}")
    print(f"  Lucro total: R$ {stats['total_profit']:.2f}")
    print(f"  ROI: {stats['roi']:.1f}%")
    print(f"  Stake médio: {stats['avg_stake_percentage']:.1%}")
    print(f"  Stake máximo: {stats['max_stake_percentage']:.1%}")
    print(f"  Odds médias: {stats['avg_odds']:.2f}")
    print(f"  Probabilidade média: {stats['avg_probability']:.3f}")
    print(f"  EV médio: {stats['avg_expected_value']:.3f}")
    print(f"  Sequência máxima de vitórias: {stats['max_win_streak']}")
    print(f"  Sequência máxima de derrotas: {stats['max_loss_streak']}")
    
    # Testa sistema integrado
    print("\n🎭 SISTEMA INTEGRADO DE GESTÃO DE BANCA")
    print("-" * 40)
    
    system = AdvancedBankrollSystem()
    
    # Analisa oportunidade com gestão de banca
    opportunity = system.analyze_bet_opportunity('Flamengo', 'Palmeiras', '2024-01-15')
    
    if opportunity:
        print(f"\nAnálise de Oportunidade com Gestão de Banca:")
        print(f"  Partida: {opportunity['match_info']['home_team']} vs {opportunity['match_info']['away_team']}")
        
        bet_sizing = opportunity['bet_sizing']
        print(f"  Stake recomendado: {bet_sizing['stake_percentage']:.1%}")
        print(f"  Valor da aposta: R$ {bet_sizing['stake_amount']:.2f}")
        print(f"  EV: {bet_sizing['expected_value']:.3f}")
        print(f"  Nível de risco: {bet_sizing['risk_level']}")
        print(f"  Recomendação: {bet_sizing['recommendation']}")
        
        feasibility = opportunity['feasibility']
        print(f"  Viável: {feasibility['is_feasible']}")
        print(f"  Score: {feasibility['score']}")
        if feasibility['warnings']:
            print(f"  Avisos: {', '.join(feasibility['warnings'])}")
        
        final_rec = opportunity['final_recommendation']
        print(f"  Recomendação final: {final_rec['action']}")
        print(f"  Motivo: {final_rec['reason']}")
        
        bankroll_status = opportunity['bankroll_status']
        print(f"  Status da banca: {bankroll_status['status']}")
        print(f"  Capital: R$ {bankroll_status['current_capital']:.2f}")
        print(f"  Lucro: {bankroll_status['profit_percentage']:.1f}%")
    
    # Testa backtesting com gestão de banca
    print("\n📈 TESTE DE BACKTESTING COM GESTÃO DE BANCA")
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
    backtest_result = system.run_bankroll_backtesting(historical_matches, 1000)
    
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
        print(f"  Drawdown máximo: {summary['max_drawdown']:.1f}%")
        
        final_status = backtest_result['final_bankroll_status']
        print(f"\nStatus Final da Banca:")
        print(f"  Capital: R$ {final_status['current_capital']:.2f}")
        print(f"  Lucro: R$ {final_status['total_profit']:.2f}")
        print(f"  ROI: {final_status['profit_percentage']:.1f}%")
        print(f"  Drawdown: {final_status['drawdown_percentage']:.1f}%")
        print(f"  Status: {final_status['status']}")
        
        betting_stats = backtest_result['betting_statistics']
        print(f"\nEstatísticas de Apostas:")
        print(f"  Total: {betting_stats['total_bets']}")
        print(f"  Taxa de acerto: {betting_stats['win_rate']:.1%}")
        print(f"  ROI: {betting_stats['roi']:.1f}%")
        print(f"  Stake médio: {betting_stats['avg_stake_percentage']:.1%}")
        print(f"  EV médio: {betting_stats['avg_expected_value']:.3f}")
    else:
        print(f"Falha no backtesting: {backtest_result['error']}")
    
    # Testa otimização de risco
    print("\n🔧 TESTE DE OTIMIZAÇÃO DE RISCO")
    print("-" * 40)
    
    optimization_result = system.optimize_risk_level(historical_matches, 1000)
    
    if optimization_result['success']:
        print(f"\nResultados da Otimização:")
        for risk_level, metrics in optimization_result['results'].items():
            print(f"  {risk_level}:")
            print(f"    ROI: {metrics['profit_percentage']:.1f}%")
            print(f"    Drawdown: {metrics['max_drawdown']:.1f}%")
            print(f"    Taxa de execução: {metrics['execution_rate']:.1%}")
            print(f"    Score risco/retorno: {metrics['risk_return_ratio']:.2f}")
        
        print(f"\nMelhor nível de risco: {optimization_result['best_risk_level']}")
        print(f"Score: {optimization_result['best_score']:.2f}")
        
        recommendation = optimization_result['recommendation']
        print(f"Recomendação: {recommendation['recommendation']}")
        print(f"Motivo: {recommendation['reason']}")
        print(f"Confiança: {recommendation['confidence']}")
    else:
        print(f"Falha na otimização: {optimization_result['error']}")
    
    # Analytics do sistema
    print("\n📊 ANALYTICS DO SISTEMA")
    print("-" * 40)
    
    analytics = system.get_bankroll_analytics()
    bankroll = analytics['bankroll_status']
    betting = analytics['betting_statistics']
    
    print(f"  Capital: R$ {bankroll['current_capital']:.2f}")
    print(f"  Lucro: {bankroll['profit_percentage']:.1f}%")
    print(f"  Drawdown: {bankroll['drawdown_percentage']:.1f}%")
    print(f"  Status: {bankroll['status']}")
    print(f"  Nível de risco: {bankroll['risk_level']}")
    
    print(f"\n  Estatísticas de Apostas:")
    print(f"    Total: {betting['total_bets']}")
    print(f"    Taxa de acerto: {betting['win_rate']:.1%}")
    print(f"    ROI: {betting['roi']:.1f}%")
    print(f"    Stake médio: {betting['avg_stake_percentage']:.1%}")
    
    print(f"\n  Alertas de Risco:")
    risk_alerts = analytics['risk_alerts']
    print(f"    Total: {risk_alerts['total_alerts']}")
    print(f"    Críticos: {risk_alerts['critical_alerts']}")
    
    print(f"\n  Recomendações Estratégicas:")
    strategic = analytics['strategic_recommendations']
    for i, rec in enumerate(strategic[:3], 1):
        print(f"    {i}. {rec['type']}: {rec['message']}")
    
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRAÇÃO DO SISTEMA DE GESTÃO DE BANCA CONCLUÍDA!")
    print("=" * 60)
    
    print(f"\n📋 RESUMO DA IMPLEMENTAÇÃO:")
    print(f"   ✅ Critério de Kelly Fracionado implementado")
    print(f"   ✅ Fórmula: Stake % = (f/4) × [(P × O) - 1] / (O - 1)")
    print(f"   ✅ Múltiplos níveis de risco (Conservative, Moderate, Aggressive, Maximum)")
    print(f"   ✅ Sistema de sizing de apostas inteligente")
    print(f"   ✅ Gestão de risco e drawdown")
    print(f"   ✅ Monitoramento de banca em tempo real")
    print(f"   ✅ Alertas de gestão de risco")
    print(f"   ✅ Backtesting com métricas específicas")
    print(f"   ✅ Otimização de nível de risco")
    print(f"   ✅ Analytics e recomendações estratégicas")
    
    print(f"\n🚀 COMO USAR:")
    print(f"   python main.py --mode bankroll")
    print(f"   python bankroll_demo.py")
    print(f"   python main.py --web")
    
    print(f"\n🔧 VANTAGENS DO SISTEMA:")
    print(f"   • Kelly Fracionado para sizing otimizado")
    print(f"   • Múltiplos níveis de risco configuráveis")
    print(f"   • Gestão automática de drawdown")
    print(f"   • Alertas de risco em tempo real")
    print(f"   • Backtesting com métricas específicas")
    print(f"   • Otimização automática de nível de risco")
    print(f"   • Analytics completos para monitoramento")

if __name__ == "__main__":
    main()
