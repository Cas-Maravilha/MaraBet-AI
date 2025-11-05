#!/usr/bin/env python3
"""
Script para testar o Value Finder do MaraBet AI
"""

from análise.value_finder import ValueFinder
from processadores.statistics import StatisticsProcessor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_value_finder_initialization():
    """Testa inicialização do Value Finder"""
    print("🔍 TESTE DE INICIALIZAÇÃO")
    print("=" * 40)
    
    try:
        value_finder = ValueFinder()
        print("✅ Value Finder inicializado com sucesso")
        
        # Verificar componentes
        assert hasattr(value_finder, 'stats_processor'), "Deve ter stats_processor"
        assert hasattr(value_finder, 'db'), "Deve ter conexão com banco"
        assert isinstance(value_finder.stats_processor, StatisticsProcessor), "stats_processor deve ser StatisticsProcessor"
        
        print("✅ Componentes verificados")
        return True
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return False

def test_probability_calculation():
    """Testa cálculo de probabilidades"""
    print("\n📊 TESTE DE CÁLCULO DE PROBABILIDADES")
    print("=" * 40)
    
    try:
        value_finder = ValueFinder()
        
        # Dados de teste
        match_data = {
            'fixture': {'id': 12345},
            'teams': {
                'home': {'name': 'Manchester City'},
                'away': {'name': 'Arsenal'}
            }
        }
        
        probabilities = value_finder._calculate_probabilities(match_data)
        
        print(f"✅ Probabilidades calculadas:")
        print(f"   Vitória da casa: {probabilities['home_win']:.1%}")
        print(f"   Empate: {probabilities['draw']:.1%}")
        print(f"   Vitória visitante: {probabilities['away_win']:.1%}")
        print(f"   Over 2.5: {probabilities['over_25']:.1%}")
        print(f"   Under 2.5: {probabilities['under_25']:.1%}")
        print(f"   BTTS Sim: {probabilities['btts_yes']:.1%}")
        print(f"   BTTS Não: {probabilities['btts_no']:.1%}")
        
        # Verificar se as probabilidades somam 1 para 1X2
        total_1x2 = probabilities['home_win'] + probabilities['draw'] + probabilities['away_win']
        assert abs(total_1x2 - 1.0) < 0.01, f"Probabilidades 1X2 devem somar 1, obtido: {total_1x2}"
        
        # Verificar se over + under = 1
        total_ou = probabilities['over_25'] + probabilities['under_25']
        assert abs(total_ou - 1.0) < 0.01, f"Over + Under deve ser 1, obtido: {total_ou}"
        
        print("✅ Teste de probabilidades aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de probabilidades: {e}")
        return False

def test_selection_mapping():
    """Testa mapeamento de seleções"""
    print("\n🎯 TESTE DE MAPEAMENTO DE SELEÇÕES")
    print("=" * 40)
    
    try:
        value_finder = ValueFinder()
        
        # Testar mapeamentos
        test_cases = [
            ('h2h', 'Home', 'home_win'),
            ('h2h', 'Draw', 'draw'),
            ('h2h', 'Away', 'away_win'),
            ('totals', 'Over', 'over_25'),
            ('totals', 'Under', 'under_25'),
            ('unknown', 'Unknown', ''),
        ]
        
        for market, selection, expected in test_cases:
            result = value_finder._map_selection(market, selection)
            print(f"   {market} - {selection}: {result}")
            assert result == expected, f"Esperado '{expected}', obtido '{result}'"
        
        print("✅ Teste de mapeamento aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de mapeamento: {e}")
        return False

def test_value_calculation():
    """Testa cálculo de valor"""
    print("\n💰 TESTE DE CÁLCULO DE VALOR")
    print("=" * 40)
    
    try:
        value_finder = ValueFinder()
        
        # Dados de teste
        probabilities = {
            'home_win': 0.45,
            'draw': 0.30,
            'away_win': 0.25,
            'over_25': 0.68,
            'under_25': 0.32,
            'btts_yes': 0.58,
            'btts_no': 0.42
        }
        
        odds_data = [
            {
                'bookmakers': [
                    {
                        'markets': [
                            {
                                'key': 'h2h',
                                'outcomes': [
                                    {'name': 'Home', 'price': 2.0},
                                    {'name': 'Draw', 'price': 3.2},
                                    {'name': 'Away', 'price': 4.0}
                                ]
                            },
                            {
                                'key': 'totals',
                                'outcomes': [
                                    {'name': 'Over', 'price': 1.8},
                                    {'name': 'Under', 'price': 2.1}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        
        best_value = value_finder._find_best_value(probabilities, odds_data)
        
        if best_value:
            print(f"✅ Melhor valor encontrado:")
            print(f"   Mercado: {best_value['market']}")
            print(f"   Seleção: {best_value['selection']}")
            print(f"   Probabilidade: {best_value['probability']:.1%}")
            print(f"   Odd: {best_value['odd']:.2f}")
            print(f"   EV: {best_value['ev']:.2%}")
            print(f"   Confiança: {best_value['confidence']:.1%}")
        else:
            print("⚠️  Nenhum valor encontrado")
        
        print("✅ Teste de cálculo de valor aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de valor: {e}")
        return False

def test_criteria_check():
    """Testa verificação de critérios"""
    print("\n✅ TESTE DE VERIFICAÇÃO DE CRITÉRIOS")
    print("=" * 40)
    
    try:
        value_finder = ValueFinder()
        
        # Casos de teste
        test_cases = [
            {'ev': 0.05, 'confidence': 0.75, 'expected': True},   # Atende critérios
            {'ev': 0.02, 'confidence': 0.75, 'expected': False},  # EV muito baixo
            {'ev': 0.05, 'confidence': 0.60, 'expected': False},  # Confiança muito baixa
            {'ev': 0.05, 'confidence': 0.95, 'expected': False},  # Confiança muito alta
        ]
        
        for i, case in enumerate(test_cases, 1):
            result = value_finder._meets_criteria(case)
            print(f"   Caso {i}: EV={case['ev']:.1%}, Conf={case['confidence']:.1%} → {result}")
            assert result == case['expected'], f"Caso {i}: esperado {case['expected']}, obtido {result}"
        
        print("✅ Teste de critérios aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de critérios: {e}")
        return False

def test_stake_calculation():
    """Testa cálculo de stake"""
    print("\n📈 TESTE DE CÁLCULO DE STAKE")
    print("=" * 40)
    
    try:
        value_finder = ValueFinder()
        
        # Casos de teste
        test_cases = [
            {'probability': 0.6, 'odd': 1.8, 'expected_range': (0, 0.1)},
            {'probability': 0.4, 'odd': 2.5, 'expected_range': (0, 0.1)},
            {'probability': 0.8, 'odd': 1.2, 'expected_range': (0, 0.1)},
        ]
        
        for i, case in enumerate(test_cases, 1):
            stake = value_finder._calculate_stake(case)
            print(f"   Caso {i}: Prob={case['probability']:.1%}, Odd={case['odd']:.1f} → Stake={stake:.2%}")
            
            # Verificar se está no range esperado
            assert case['expected_range'][0] <= stake <= case['expected_range'][1], f"Caso {i}: stake fora do range"
        
        print("✅ Teste de stake aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de stake: {e}")
        return False

def test_confidence_calculation():
    """Testa cálculo de confiança"""
    print("\n🎯 TESTE DE CÁLCULO DE CONFIANÇA")
    print("=" * 40)
    
    try:
        value_finder = ValueFinder()
        
        # Casos de teste
        test_cases = [
            {'probability': 0.6, 'ev': 0.05, 'expected_range': (0.6, 0.95)},
            {'probability': 0.4, 'ev': 0.10, 'expected_range': (0.4, 0.95)},
            {'probability': 0.8, 'ev': 0.20, 'expected_range': (0.8, 0.95)},
        ]
        
        for i, case in enumerate(test_cases, 1):
            value = {'probability': case['probability'], 'expected_value': case['ev']}
            probabilities = {'home_win': case['probability']}
            
            confidence = value_finder._calculate_confidence(value, probabilities)
            print(f"   Caso {i}: Prob={case['probability']:.1%}, EV={case['ev']:.1%} → Conf={confidence:.1%}")
            
            # Verificar se está no range esperado
            assert case['expected_range'][0] <= confidence <= case['expected_range'][1], f"Caso {i}: confiança fora do range"
        
        print("✅ Teste de confiança aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de confiança: {e}")
        return False

def test_factors_generation():
    """Testa geração de fatores"""
    print("\n📋 TESTE DE GERAÇÃO DE FATORES")
    print("=" * 40)
    
    try:
        value_finder = ValueFinder()
        
        probabilities = {
            'home_win': 0.45,
            'draw': 0.30,
            'away_win': 0.25
        }
        
        factors = value_finder._get_factors(probabilities, 'home_win')
        
        print(f"✅ Fatores gerados:")
        print(f"   Probabilidade do modelo: {factors['model_probability']:.1%}")
        print(f"   Edge estatístico: {factors['statistical_edge']}")
        print(f"   Timestamp: {factors['timestamp']}")
        
        # Verificar se tem os campos necessários
        assert 'model_probability' in factors, "Deve ter model_probability"
        assert 'statistical_edge' in factors, "Deve ter statistical_edge"
        assert 'timestamp' in factors, "Deve ter timestamp"
        
        print("✅ Teste de fatores aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de fatores: {e}")
        return False

def test_edge_cases():
    """Testa casos extremos"""
    print("\n🔍 TESTE DE CASOS EXTREMOS")
    print("=" * 40)
    
    try:
        value_finder = ValueFinder()
        
        # Lista vazia de odds
        empty_odds = value_finder._find_best_value({'home_win': 0.5}, [])
        assert empty_odds is None, "Lista vazia deve retornar None"
        
        # Probabilidades zeradas
        zero_probs = value_finder._find_best_value({'home_win': 0}, [{'bookmakers': [{'markets': [{'key': 'h2h', 'outcomes': [{'name': 'Home', 'price': 2.0}]}]}]}])
        assert zero_probs is None, "Probabilidades zeradas devem retornar None"
        
        # Mapeamento desconhecido
        unknown_mapping = value_finder._map_selection('unknown', 'unknown')
        assert unknown_mapping == '', "Mapeamento desconhecido deve retornar string vazia"
        
        print("✅ Teste de casos extremos aprovado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de casos extremos: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🔍 MARABET AI - TESTE DO VALUE FINDER")
    print("=" * 60)
    
    # Executar testes
    results = []
    
    results.append(test_value_finder_initialization())
    results.append(test_probability_calculation())
    results.append(test_selection_mapping())
    results.append(test_value_calculation())
    results.append(test_criteria_check())
    results.append(test_stake_calculation())
    results.append(test_confidence_calculation())
    results.append(test_factors_generation())
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
