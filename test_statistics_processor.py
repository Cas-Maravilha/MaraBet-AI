#!/usr/bin/env python3
"""
Script para testar o processador de estatísticas do MaraBet AI
"""

from processadores.statistics import StatisticsProcessor
import numpy as np

def test_form_calculation():
    """Testa cálculo de forma"""
    print("📊 TESTE DE CÁLCULO DE FORMA")
    print("=" * 40)
    
    # Dados de teste
    matches = [
        {'result': 'W', 'goals_scored': 2, 'goals_conceded': 1},
        {'result': 'D', 'goals_scored': 1, 'goals_conceded': 1},
        {'result': 'W', 'goals_scored': 3, 'goals_conceded': 0},
        {'result': 'L', 'goals_scored': 0, 'goals_conceded': 2},
        {'result': 'W', 'goals_scored': 1, 'goals_conceded': 0},
    ]
    
    try:
        form = StatisticsProcessor.calculate_form(matches)
        
        print(f"✅ Forma calculada:")
        print(f"   Pontos: {form['points']}")
        print(f"   Vitórias: {form['wins']}")
        print(f"   Empates: {form['draws']}")
        print(f"   Derrotas: {form['losses']}")
        print(f"   Taxa de vitórias: {form['win_rate']:.2%}")
        print(f"   Pontos por jogo: {form['points_per_game']:.2f}")
        
        # Verificar se os cálculos estão corretos
        expected_points = 3 + 1 + 3 + 0 + 3  # 10 pontos
        assert form['points'] == expected_points, f"Pontos esperados: {expected_points}, obtidos: {form['points']}"
        
        print("✅ Teste de forma aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de forma: {e}")
        return False

def test_goals_average():
    """Testa cálculo de médias de gols"""
    print("\n⚽ TESTE DE MÉDIAS DE GOLS")
    print("=" * 40)
    
    matches = [
        {'goals_scored': 2, 'goals_conceded': 1},
        {'goals_scored': 1, 'goals_conceded': 1},
        {'goals_scored': 3, 'goals_conceded': 0},
        {'goals_scored': 0, 'goals_conceded': 2},
        {'goals_scored': 1, 'goals_conceded': 0},
    ]
    
    try:
        goals = StatisticsProcessor.calculate_goals_average(matches)
        
        print(f"✅ Médias de gols calculadas:")
        print(f"   Gols marcados (média): {goals['scored_avg']:.2f}")
        print(f"   Gols sofridos (média): {goals['conceded_avg']:.2f}")
        print(f"   Total (média): {goals['total_avg']:.2f}")
        print(f"   Desvio padrão (marcados): {goals['scored_std']:.2f}")
        print(f"   Desvio padrão (sofridos): {goals['conceded_std']:.2f}")
        
        # Verificar se os cálculos estão corretos
        expected_scored = (2 + 1 + 3 + 0 + 1) / 5  # 1.4
        expected_conceded = (1 + 1 + 0 + 2 + 0) / 5  # 0.8
        
        assert abs(goals['scored_avg'] - expected_scored) < 0.01, f"Gols marcados esperados: {expected_scored}, obtidos: {goals['scored_avg']}"
        assert abs(goals['conceded_avg'] - expected_conceded) < 0.01, f"Gols sofridos esperados: {expected_conceded}, obtidos: {goals['conceded_avg']}"
        
        print("✅ Teste de médias de gols aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de médias: {e}")
        return False

def test_poisson_probability():
    """Testa cálculo de probabilidades Poisson"""
    print("\n🎯 TESTE DE PROBABILIDADES POISSON")
    print("=" * 40)
    
    try:
        # Teste com médias típicas
        avg_home = 1.5
        avg_away = 1.2
        
        probs = StatisticsProcessor.calculate_poisson_probability(avg_home, avg_away)
        
        print(f"✅ Probabilidades Poisson calculadas:")
        print(f"   Vitória da casa: {probs['home_win']:.2%}")
        print(f"   Empate: {probs['draw']:.2%}")
        print(f"   Vitória do visitante: {probs['away_win']:.2%}")
        print(f"   Over 2.5: {probs['over_25']:.2%}")
        print(f"   Under 2.5: {probs['under_25']:.2%}")
        print(f"   Ambas marcam: {probs['btts_yes']:.2%}")
        print(f"   Não marcam ambas: {probs['btts_no']:.2%}")
        
        # Verificar se as probabilidades somam 1
        total_prob = probs['home_win'] + probs['draw'] + probs['away_win']
        assert abs(total_prob - 1.0) < 0.01, f"Probabilidades devem somar 1, obtido: {total_prob}"
        
        # Verificar se over + under = 1
        over_under_total = probs['over_25'] + probs['under_25']
        assert abs(over_under_total - 1.0) < 0.01, f"Over + Under deve ser 1, obtido: {over_under_total}"
        
        print("✅ Teste de probabilidades Poisson aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de Poisson: {e}")
        return False

def test_expected_goals():
    """Testa cálculo de xG"""
    print("\n🎯 TESTE DE EXPECTED GOALS (xG)")
    print("=" * 40)
    
    try:
        # Dados de teste
        stats = {
            'shots_on_target': 5,
            'possession': 60,
            'dangerous_attacks': 8
        }
        
        xg = StatisticsProcessor.calculate_expected_goals(stats)
        
        print(f"✅ xG calculado:")
        print(f"   Estatísticas: {stats}")
        print(f"   xG: {xg}")
        
        # Verificar se o xG é razoável
        assert 0 <= xg <= 10, f"xG deve estar entre 0 e 10, obtido: {xg}"
        
        print("✅ Teste de xG aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de xG: {e}")
        return False

def test_value_calculation():
    """Testa cálculo de valor de aposta"""
    print("\n💰 TESTE DE CÁLCULO DE VALOR")
    print("=" * 40)
    
    try:
        # Teste com probabilidade e odd
        probability = 0.6  # 60%
        odd = 1.8
        
        value = StatisticsProcessor.calculate_value(probability, odd)
        
        print(f"✅ Valor calculado:")
        print(f"   Probabilidade: {value['probability']:.2%}")
        print(f"   Probabilidade implícita: {value['implied_probability']:.2%}")
        print(f"   Edge: {value['edge']:.2%}")
        print(f"   Valor esperado: {value['expected_value']:.2%}")
        print(f"   Tem valor: {value['has_value']}")
        print(f"   Percentual de valor: {value['value_percentage']:.2f}%")
        
        # Verificar se o cálculo está correto
        expected_ev = (probability * odd) - 1
        assert abs(value['expected_value'] - expected_ev) < 0.01, f"EV esperado: {expected_ev}, obtido: {value['expected_value']}"
        
        print("✅ Teste de valor aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de valor: {e}")
        return False

def test_kelly_criterion():
    """Testa critério de Kelly"""
    print("\n📈 TESTE DE CRITÉRIO DE KELLY")
    print("=" * 40)
    
    try:
        # Teste com diferentes cenários
        test_cases = [
            {'prob': 0.6, 'odd': 1.8, 'expected_range': (0, 0.1)},
            {'prob': 0.4, 'odd': 2.5, 'expected_range': (0, 0.1)},
            {'prob': 0.8, 'odd': 1.2, 'expected_range': (0, 0.1)},
            {'prob': 0.3, 'odd': 1.5, 'expected_range': (0, 0.1)},  # Sem valor
        ]
        
        for i, case in enumerate(test_cases, 1):
            kelly = StatisticsProcessor.kelly_criterion(
                case['prob'], 
                case['odd']
            )
            
            print(f"   Caso {i}: Prob={case['prob']:.1%}, Odd={case['odd']:.1f} → Kelly={kelly:.2%}")
            
            # Verificar se está no range esperado
            assert case['expected_range'][0] <= kelly <= case['expected_range'][1], f"Kelly fora do range esperado: {kelly}"
        
        print("✅ Teste de Kelly aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de Kelly: {e}")
        return False

def test_edge_cases():
    """Testa casos extremos"""
    print("\n🔍 TESTE DE CASOS EXTREMOS")
    print("=" * 40)
    
    try:
        # Lista vazia
        empty_form = StatisticsProcessor.calculate_form([])
        assert empty_form['points'] == 0, "Forma com lista vazia deve retornar 0 pontos"
        
        # Lista vazia para gols
        empty_goals = StatisticsProcessor.calculate_goals_average([])
        assert empty_goals['scored'] == 0, "Média com lista vazia deve retornar 0"
        
        # Probabilidade 0 para Kelly
        kelly_zero = StatisticsProcessor.kelly_criterion(0, 2.0)
        assert kelly_zero == 0, "Kelly com probabilidade 0 deve retornar 0"
        
        # Odd 1 para Kelly
        kelly_odd_one = StatisticsProcessor.kelly_criterion(0.5, 1.0)
        assert kelly_odd_one == 0, "Kelly com odd 1 deve retornar 0"
        
        print("✅ Teste de casos extremos aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de casos extremos: {e}")
        return False

def main():
    """Função principal de teste"""
    print("📊 MARABET AI - TESTE DO PROCESSADOR DE ESTATÍSTICAS")
    print("=" * 70)
    
    # Executar testes
    results = []
    
    results.append(test_form_calculation())
    results.append(test_goals_average())
    results.append(test_poisson_probability())
    results.append(test_expected_goals())
    results.append(test_value_calculation())
    results.append(test_kelly_criterion())
    results.append(test_edge_cases())
    
    # Resultado final
    success_count = sum(results)
    total_tests = len(results)
    
    print(f"\n📊 RESULTADO FINAL")
    print("=" * 30)
    print(f"Testes aprovados: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 Todos os testes passaram!")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()
