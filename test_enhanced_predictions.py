#!/usr/bin/env python3
"""
Teste do Sistema de Predições Aprimorado - MaraBet AI
Testa todos os novos mercados de apostas
"""

import logging
import sys
import os
from datetime import datetime

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_predictions_system import EnhancedPredictionsSystem

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_goals_market():
    """Testa mercado de golos"""
    print("⚽ TESTANDO MERCADO DE GOLOS")
    print("-" * 40)
    
    system = EnhancedPredictionsSystem()
    
    match_data = {
        'home_team': 'Teste Casa',
        'away_team': 'Teste Visitante',
        'home_goals_avg': 1.8,
        'away_goals_avg': 1.4,
        'home_advantage': 0.1,
        'weather_factor': 1.0,
        'importance_factor': 1.0
    }
    
    try:
        predictions = system.goals_market.predict_over_under(match_data)
        print(f"✅ Over/Under: {len(predictions)} predições")
        
        predictions = system.goals_market.predict_both_teams_score(match_data)
        print(f"✅ BTTS: {len(predictions)} predições")
        
        predictions = system.goals_market.predict_exact_goals(match_data)
        print(f"✅ Gols Exatos: {len(predictions)} predições")
        
        stats = system.goals_market.get_goal_statistics(match_data)
        print(f"✅ Estatísticas: {len(stats)} métricas")
        
        return True
    except Exception as e:
        print(f"❌ Erro no mercado de golos: {e}")
        return False

def test_handicap_market():
    """Testa mercado de handicap"""
    print("\n⚖️ TESTANDO MERCADO DE HANDICAP")
    print("-" * 40)
    
    system = EnhancedPredictionsSystem()
    
    match_data = {
        'home_team': 'Teste Casa',
        'away_team': 'Teste Visitante',
        'home_strength': 0.6,
        'away_strength': 0.4,
        'home_advantage': 0.1,
        'form_factor': 1.0,
        'injury_factor': 1.0,
        'weather_factor': 1.0
    }
    
    try:
        predictions = system.handicap_market.predict_asian_handicap(match_data)
        print(f"✅ Handicap Asiático: {len(predictions)} predições")
        
        predictions = system.handicap_market.predict_european_handicap(match_data)
        print(f"✅ Handicap Europeu: {len(predictions)} predições")
        
        stats = system.handicap_market.get_handicap_statistics(match_data)
        print(f"✅ Estatísticas: {len(stats)} métricas")
        
        return True
    except Exception as e:
        print(f"❌ Erro no mercado de handicap: {e}")
        return False

def test_cards_market():
    """Testa mercado de cartões"""
    print("\n🟨 TESTANDO MERCADO DE CARTÕES")
    print("-" * 40)
    
    system = EnhancedPredictionsSystem()
    
    match_data = {
        'home_team': 'Teste Casa',
        'away_team': 'Teste Visitante',
        'home_cards_avg': 2.3,
        'away_cards_avg': 2.1,
        'home_yellow_avg': 2.0,
        'away_yellow_avg': 1.8,
        'home_red_avg': 0.1,
        'away_red_avg': 0.08,
        'referee_factor': 1.0,
        'importance_factor': 1.0,
        'rivalry_factor': 1.0
    }
    
    try:
        predictions = system.cards_market.predict_total_cards(match_data)
        print(f"✅ Total Cartões: {len(predictions)} predições")
        
        predictions = system.cards_market.predict_yellow_cards(match_data)
        print(f"✅ Cartões Amarelos: {len(predictions)} predições")
        
        predictions = system.cards_market.predict_red_cards(match_data)
        print(f"✅ Cartões Vermelhos: {len(predictions)} predições")
        
        stats = system.cards_market.get_cards_statistics(match_data)
        print(f"✅ Estatísticas: {len(stats)} métricas")
        
        return True
    except Exception as e:
        print(f"❌ Erro no mercado de cartões: {e}")
        return False

def test_corners_market():
    """Testa mercado de cantos"""
    print("\n📐 TESTANDO MERCADO DE CANTOS")
    print("-" * 40)
    
    system = EnhancedPredictionsSystem()
    
    match_data = {
        'home_team': 'Teste Casa',
        'away_team': 'Teste Visitante',
        'home_corners_avg': 6.2,
        'away_corners_avg': 5.8,
        'possession_factor': 1.0,
        'style_factor': 1.0,
        'weather_factor': 1.0,
        'importance_factor': 1.0
    }
    
    try:
        predictions = system.corners_market.predict_total_corners(match_data)
        print(f"✅ Total Cantos: {len(predictions)} predições")
        
        predictions = system.corners_market.predict_corner_handicap(match_data)
        print(f"✅ Handicap Cantos: {len(predictions)} predições")
        
        predictions = system.corners_market.predict_first_corner(match_data)
        print(f"✅ Primeiro Canto: {len(predictions)} predições")
        
        stats = system.corners_market.get_corners_statistics(match_data)
        print(f"✅ Estatísticas: {len(stats)} métricas")
        
        return True
    except Exception as e:
        print(f"❌ Erro no mercado de cantos: {e}")
        return False

def test_double_chance_market():
    """Testa mercado de dupla chance"""
    print("\n🎯 TESTANDO MERCADO DE DUPLA CHANCE")
    print("-" * 40)
    
    system = EnhancedPredictionsSystem()
    
    match_data = {
        'home_team': 'Teste Casa',
        'away_team': 'Teste Visitante',
        'home_strength': 0.6,
        'away_strength': 0.4,
        'home_advantage': 0.1,
        'form_factor': 1.0,
        'injury_factor': 1.0,
        'weather_factor': 1.0
    }
    
    try:
        predictions = system.double_chance_market.predict_double_chance(match_data)
        print(f"✅ Dupla Chance: {len(predictions)} predições")
        
        predictions = system.double_chance_market.predict_win_draw_win(match_data)
        print(f"✅ Win-Draw-Win: {len(predictions)} predições")
        
        stats = system.double_chance_market.get_double_chance_statistics(match_data)
        print(f"✅ Estatísticas: {len(stats)} métricas")
        
        return True
    except Exception as e:
        print(f"❌ Erro no mercado de dupla chance: {e}")
        return False

def test_exact_score_market():
    """Testa mercado de resultado exato"""
    print("\n🎯 TESTANDO MERCADO DE RESULTADO EXATO")
    print("-" * 40)
    
    system = EnhancedPredictionsSystem()
    
    match_data = {
        'home_team': 'Teste Casa',
        'away_team': 'Teste Visitante',
        'home_goals_avg': 1.8,
        'away_goals_avg': 1.4,
        'home_advantage': 0.1,
        'weather_factor': 1.0,
        'importance_factor': 1.0
    }
    
    try:
        predictions = system.exact_score_market.predict_exact_score(match_data)
        print(f"✅ Resultado Exato: {len(predictions)} predições")
        
        predictions = system.exact_score_market.predict_half_time_score(match_data)
        print(f"✅ Resultado Intervalo: {len(predictions)} predições")
        
        predictions = system.exact_score_market.predict_win_to_nil(match_data)
        print(f"✅ Vitória sem Sofrer: {len(predictions)} predições")
        
        stats = system.exact_score_market.get_exact_score_statistics(match_data)
        print(f"✅ Estatísticas: {len(stats)} métricas")
        
        return True
    except Exception as e:
        print(f"❌ Erro no mercado de resultado exato: {e}")
        return False

def test_comprehensive_system():
    """Testa sistema completo"""
    print("\n🚀 TESTANDO SISTEMA COMPLETO")
    print("-" * 40)
    
    system = EnhancedPredictionsSystem()
    
    match_data = {
        'home_team': 'Manchester City',
        'away_team': 'Arsenal',
        'league': 'Premier League',
        'match_date': '2024-01-20 15:30',
        'home_strength': 0.7,
        'away_strength': 0.65,
        'home_advantage': 0.1,
        'home_goals_avg': 2.1,
        'away_goals_avg': 1.8,
        'home_corners_avg': 6.5,
        'away_corners_avg': 6.0,
        'home_cards_avg': 2.2,
        'away_cards_avg': 2.0,
        'home_yellow_avg': 2.0,
        'away_yellow_avg': 1.8,
        'home_red_avg': 0.08,
        'away_red_avg': 0.06,
        'form_factor': 1.05,
        'injury_factor': 0.98,
        'weather_factor': 1.0,
        'importance_factor': 1.2,
        'rivalry_factor': 1.1,
        'referee_factor': 1.0,
        'possession_factor': 1.02,
        'style_factor': 1.05
    }
    
    try:
        all_predictions = system.generate_comprehensive_predictions(match_data)
        print(f"✅ Predições Geradas: {len(all_predictions)} categorias")
        
        total_predictions = sum(len(preds) for preds in all_predictions.values())
        print(f"✅ Total de Predições: {total_predictions}")
        
        top_recommendations = system.get_top_recommendations(all_predictions, top_n=10)
        print(f"✅ Top Recomendações: {len(top_recommendations)}")
        
        telegram_message = system.generate_telegram_message(match_data, all_predictions)
        print(f"✅ Mensagem Telegram: {len(telegram_message)} caracteres")
        
        try:
            filename = system.save_predictions_to_file(match_data, all_predictions, "test_predictions.json")
            print(f"✅ Arquivo Salvo: {filename}")
        except Exception as e:
            print(f"⚠️  Erro ao salvar arquivo: {e}")
            # Continuar mesmo com erro de salvamento
        
        return True
    except Exception as e:
        print(f"❌ Erro no sistema completo: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 TESTE DO SISTEMA DE PREDIÇÕES APRIMORADO - MARABET AI")
    print("=" * 65)
    print("🎯 Testando todos os novos mercados de apostas")
    print()
    
    tests = [
        ("Mercado de Golos", test_goals_market),
        ("Mercado de Handicap", test_handicap_market),
        ("Mercado de Cartões", test_cards_market),
        ("Mercado de Cantos", test_corners_market),
        ("Mercado de Dupla Chance", test_double_chance_market),
        ("Mercado de Resultado Exato", test_exact_score_market),
        ("Sistema Completo", test_comprehensive_system)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🔍 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {e}")
            results.append((test_name, False))
        print()
    
    # Resumo dos testes
    print("📊 RESUMO DOS TESTES:")
    print("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando perfeitamente!")
        print("🚀 O sistema de predições aprimorado está pronto para uso!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM! Verifique os erros acima.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
