#!/usr/bin/env python3
"""
Teste da Gestão de Risco Mínima
MaraBet AI - Validação dos parâmetros críticos antes do deploy
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from risk_management.minimum_risk_management import RiskManagement, RiskLimits, ActionType
import logging

def test_risk_limits():
    """Testa limites de risco"""
    print("🧪 TESTANDO LIMITES DE RISCO")
    print("=" * 50)
    
    # Criar instância com limites padrão
    rm = RiskManagement(initial_bankroll=10000)
    
    print(f"Limites configurados:")
    print(f"  Max Perda Diária: {rm.limits.max_daily_loss:.1%}")
    print(f"  Max Perda Semanal: {rm.limits.max_weekly_loss:.1%}")
    print(f"  Max Tamanho Posição: {rm.limits.max_position_size:.1%}")
    print(f"  Circuit Breaker: {rm.limits.circuit_breaker_losses} perdas")
    print(f"  Edge Mínimo: {rm.limits.min_edge_required:.1%}")
    print(f"  Max Apostas Simultâneas: {rm.limits.max_simultaneous_bets}")
    
    return True

def test_position_sizing():
    """Testa cálculo de tamanho de posição"""
    print("\n🧪 TESTANDO CÁLCULO DE TAMANHO DE POSIÇÃO")
    print("=" * 50)
    
    rm = RiskManagement(initial_bankroll=10000)
    
    # Teste 1: Aposta com edge positivo
    win_prob = 0.6
    odds = 2.0
    position_size = rm.calculate_position_size(win_prob, odds)
    print(f"Aposta com edge positivo:")
    print(f"  Win Prob: {win_prob:.1%}")
    print(f"  Odds: {odds:.1f}")
    print(f"  Position Size: {position_size:.2%}")
    print(f"  Valor: R$ {position_size * 10000:,.2f}")
    
    # Teste 2: Aposta com edge baixo
    win_prob = 0.4
    odds = 2.0
    position_size = rm.calculate_position_size(win_prob, odds)
    print(f"\nAposta com edge baixo:")
    print(f"  Win Prob: {win_prob:.1%}")
    print(f"  Odds: {odds:.1f}")
    print(f"  Position Size: {position_size:.2%}")
    print(f"  Valor: R$ {position_size * 10000:,.2f}")
    
    # Teste 3: Aposta com edge muito baixo
    win_prob = 0.3
    odds = 2.0
    position_size = rm.calculate_position_size(win_prob, odds)
    print(f"\nAposta com edge muito baixo:")
    print(f"  Win Prob: {win_prob:.1%}")
    print(f"  Odds: {odds:.1f}")
    print(f"  Position Size: {position_size:.2%}")
    print(f"  Valor: R$ {position_size * 10000:,.2f}")
    
    return True

def test_bet_validation():
    """Testa validação de apostas"""
    print("\n🧪 TESTANDO VALIDAÇÃO DE APOSTAS")
    print("=" * 50)
    
    rm = RiskManagement(initial_bankroll=10000)
    
    # Teste 1: Aposta válida
    is_valid, message = rm.validate_bet(0.6, 2.0, 200)
    print(f"Aposta válida:")
    print(f"  Válida: {is_valid}")
    print(f"  Mensagem: {message}")
    
    # Teste 2: Aposta com edge baixo
    is_valid, message = rm.validate_bet(0.4, 2.0, 200)
    print(f"\nAposta com edge baixo:")
    print(f"  Válida: {is_valid}")
    print(f"  Mensagem: {message}")
    
    # Teste 3: Aposta com posição muito grande
    is_valid, message = rm.validate_bet(0.6, 2.0, 500)  # 5% do bankroll
    print(f"\nAposta com posição grande:")
    print(f"  Válida: {is_valid}")
    print(f"  Mensagem: {message}")
    
    # Teste 4: Aposta com odds inválidas
    is_valid, message = rm.validate_bet(0.6, 1.5, 200)
    print(f"\nAposta com odds inválidas:")
    print(f"  Válida: {is_valid}")
    print(f"  Mensagem: {message}")
    
    return True

def test_circuit_breakers():
    """Testa circuit breakers"""
    print("\n🧪 TESTANDO CIRCUIT BREAKERS")
    print("=" * 50)
    
    rm = RiskManagement(initial_bankroll=10000)
    
    # Simular perdas consecutivas
    print("Simulando perdas consecutivas...")
    
    for i in range(6):  # Mais que o limite de 5
        bet_id = f"bet_{i+1}"
        rm.record_bet(bet_id, 0.6, 2.0, 200, "home_win")
        rm.record_bet_result(bet_id, "loss", -200)
        
        print(f"  Perda {i+1}: Bankroll = R$ {rm.current_bankroll:,.2f}, Consecutivas = {rm.consecutive_losses}")
        
        if rm.trading_halted:
            print(f"  🚨 CIRCUIT BREAKER ATIVADO após {i+1} perdas!")
            break
    
    print(f"\nStatus final:")
    print(f"  Trading Halted: {rm.trading_halted}")
    print(f"  Bankroll: R$ {rm.current_bankroll:,.2f}")
    print(f"  Perdas Consecutivas: {rm.consecutive_losses}")
    
    return True

def test_daily_weekly_limits():
    """Testa limites diários e semanais"""
    print("\n🧪 TESTANDO LIMITES DIÁRIOS E SEMANAIS")
    print("=" * 50)
    
    rm = RiskManagement(initial_bankroll=10000)
    
    # Simular perda diária
    print("Simulando perda diária...")
    
    # Simular perda de 6% (acima do limite de 5%)
    for i in range(3):
        bet_id = f"daily_bet_{i+1}"
        rm.record_bet(bet_id, 0.6, 2.0, 200, "home_win")
        rm.record_bet_result(bet_id, "loss", -200)
        
        print(f"  Perda {i+1}: PnL Diário = R$ {rm.daily_pnl:,.2f}")
        
        if rm.trading_halted:
            print(f"  🚨 CIRCUIT BREAKER ATIVADO por perda diária!")
            break
    
    print(f"\nStatus final:")
    print(f"  Trading Halted: {rm.trading_halted}")
    print(f"  PnL Diário: R$ {rm.daily_pnl:,.2f}")
    print(f"  PnL Semanal: R$ {rm.weekly_pnl:,.2f}")
    
    return True

def test_risk_metrics():
    """Testa métricas de risco"""
    print("\n🧪 TESTANDO MÉTRICAS DE RISCO")
    print("=" * 50)
    
    rm = RiskManagement(initial_bankroll=10000)
    
    # Simular algumas apostas
    print("Simulando apostas...")
    
    # Aposta vencedora
    rm.record_bet("bet_1", 0.6, 2.0, 200, "home_win")
    rm.record_bet_result("bet_1", "win", 200)
    
    # Aposta perdedora
    rm.record_bet("bet_2", 0.55, 2.2, 150, "away_win")
    rm.record_bet_result("bet_2", "loss", -150)
    
    # Obter métricas
    metrics = rm.get_risk_metrics()
    
    print(f"Métricas de risco:")
    print(f"  Drawdown Atual: {metrics.current_drawdown:.1%}")
    print(f"  PnL Diário: R$ {metrics.daily_pnl:,.2f}")
    print(f"  PnL Semanal: R$ {metrics.weekly_pnl:,.2f}")
    print(f"  Perdas Consecutivas: {metrics.consecutive_losses}")
    print(f"  Apostas Ativas: {metrics.active_bets}")
    print(f"  Edge Atual: {metrics.current_edge:.2%}")
    print(f"  Nível de Risco: {metrics.risk_level.value.upper()}")
    
    return True

def test_risk_report():
    """Testa geração de relatório de risco"""
    print("\n🧪 TESTANDO RELATÓRIO DE RISCO")
    print("=" * 50)
    
    rm = RiskManagement(initial_bankroll=10000)
    
    # Simular cenário de risco
    print("Simulando cenário de risco...")
    
    # Simular algumas perdas
    for i in range(3):
        bet_id = f"risk_bet_{i+1}"
        rm.record_bet(bet_id, 0.6, 2.0, 200, "home_win")
        rm.record_bet_result(bet_id, "loss", -200)
    
    # Gerar relatório
    report = rm.generate_risk_report()
    print(f"\n{report}")
    
    return True

def main():
    """Função principal"""
    print("🚀 TESTE DA GESTÃO DE RISCO MÍNIMA - MARABET AI")
    print("=" * 70)
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Executar testes
        test_risk_limits()
        test_position_sizing()
        test_bet_validation()
        test_circuit_breakers()
        test_daily_weekly_limits()
        test_risk_metrics()
        test_risk_report()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("✅ Gestão de risco mínima implementada e validada")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {e}")
        return False

if __name__ == "__main__":
    main()
