#!/usr/bin/env python3
"""
Demo do Sistema de Predições Aprimorado - MaraBet AI
Demonstração completa dos novos mercados de apostas
"""

import logging
from datetime import datetime, timedelta
import json
from enhanced_predictions_system import EnhancedPredictionsSystem

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_match_data():
    """Cria dados de exemplo para uma partida"""
    return {
        'home_team': 'Real Madrid',
        'away_team': 'Barcelona',
        'league': 'La Liga',
        'match_date': '2024-01-20 21:00',
        'home_strength': 0.75,
        'away_strength': 0.72,
        'home_advantage': 0.08,
        'home_goals_avg': 2.3,
        'away_goals_avg': 2.1,
        'home_corners_avg': 7.2,
        'away_corners_avg': 6.8,
        'home_cards_avg': 2.5,
        'away_cards_avg': 2.3,
        'home_yellow_avg': 2.2,
        'away_yellow_avg': 2.0,
        'home_red_avg': 0.12,
        'away_red_avg': 0.10,
        'form_factor': 1.05,
        'injury_factor': 0.98,
        'weather_factor': 1.0,
        'importance_factor': 1.4,  # Clássico
        'rivalry_factor': 1.5,  # Rivalidade alta
        'referee_factor': 1.1,  # Árbitro rigoroso
        'possession_factor': 1.02,
        'style_factor': 1.15  # Estilo ofensivo
    }

def create_angola_match_data():
    """Cria dados de exemplo para uma partida do Girabola"""
    return {
        'home_team': 'Petro de Luanda',
        'away_team': '1º de Agosto',
        'league': 'Girabola',
        'match_date': '2024-01-21 16:00',
        'home_strength': 0.65,
        'away_strength': 0.68,
        'home_advantage': 0.12,
        'home_goals_avg': 1.8,
        'away_goals_avg': 1.6,
        'home_corners_avg': 6.0,
        'away_corners_avg': 5.5,
        'home_cards_avg': 2.8,
        'away_cards_avg': 2.6,
        'home_yellow_avg': 2.5,
        'away_yellow_avg': 2.3,
        'home_red_avg': 0.15,
        'away_red_avg': 0.12,
        'form_factor': 1.08,
        'injury_factor': 0.95,
        'weather_factor': 1.0,
        'importance_factor': 1.3,  # Jogo importante
        'rivalry_factor': 1.4,  # Rivalidade
        'referee_factor': 1.2,  # Árbitro rigoroso
        'possession_factor': 1.0,
        'style_factor': 1.05
    }

def create_premier_league_match_data():
    """Cria dados de exemplo para uma partida da Premier League"""
    return {
        'home_team': 'Arsenal',
        'away_team': 'Chelsea',
        'league': 'Premier League',
        'match_date': '2024-01-22 17:30',
        'home_strength': 0.68,
        'away_strength': 0.62,
        'home_advantage': 0.10,
        'home_goals_avg': 2.0,
        'away_goals_avg': 1.7,
        'home_corners_avg': 6.8,
        'away_corners_avg': 6.2,
        'home_cards_avg': 2.2,
        'away_cards_avg': 2.4,
        'home_yellow_avg': 2.0,
        'away_yellow_avg': 2.1,
        'home_red_avg': 0.08,
        'away_red_avg': 0.10,
        'form_factor': 1.12,
        'injury_factor': 0.97,
        'weather_factor': 0.95,  # Chuva leve
        'importance_factor': 1.2,
        'rivalry_factor': 1.3,
        'referee_factor': 1.05,
        'possession_factor': 1.08,
        'style_factor': 1.1
    }

def display_predictions_summary(all_predictions):
    """Exibe resumo das predições"""
    print("\n📊 RESUMO DAS PREDIÇÕES POR CATEGORIA:")
    print("=" * 50)
    
    total_predictions = 0
    for category, predictions in all_predictions.items():
        if predictions:
            print(f"🔹 {category.upper()}: {len(predictions)} predições")
            total_predictions += len(predictions)
            
            # Mostrar top 3 da categoria
            for i, pred in enumerate(predictions[:3], 1):
                confidence_emoji = "🟢" if pred.confidence > 0.7 else "🟡" if pred.confidence > 0.5 else "🔴"
                print(f"   {i}. {confidence_emoji} {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})")
            print()
    
    print(f"📈 TOTAL: {total_predictions} predições geradas")

def display_top_recommendations(system, all_predictions, top_n=15):
    """Exibe top recomendações"""
    print(f"\n🏆 TOP {top_n} RECOMENDAÇÕES:")
    print("=" * 50)
    
    top_recommendations = system.get_top_recommendations(all_predictions, top_n=top_n)
    
    for i, pred in enumerate(top_recommendations, 1):
        confidence_emoji = "🟢" if pred.confidence > 0.7 else "🟡" if pred.confidence > 0.5 else "🔴"
        recommended_emoji = "✅" if pred.recommended else "❌"
        
        print(f"{i:2d}. {confidence_emoji} {pred.market_type.value}: {pred.selection}")
        print(f"    Probabilidade: {pred.predicted_probability:.1%} | Confiança: {pred.confidence:.1%} | Recomendado: {recommended_emoji}")
        print(f"    Razão: {pred.reasoning}")
        print()

def display_telegram_message(system, match_data, all_predictions):
    """Exibe mensagem formatada para Telegram"""
    print("\n📱 MENSAGEM FORMATADA PARA TELEGRAM:")
    print("=" * 60)
    
    telegram_message = system.generate_telegram_message(match_data, all_predictions)
    print(telegram_message)

def save_demo_results(system, match_data, all_predictions, filename_prefix="demo"):
    """Salva resultados da demonstração"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{filename_prefix}_predictions_{timestamp}.json"
    
    system.save_predictions_to_file(match_data, all_predictions, filename)
    print(f"\n💾 Resultados salvos em: {filename}")
    
    return filename

def main():
    """Função principal da demonstração"""
    print("🚀 DEMO DO SISTEMA DE PREDIÇÕES APRIMORADO - MARABET AI")
    print("=" * 65)
    print("🎯 Demonstração dos novos mercados de apostas específicos")
    print()
    
    # Inicializar sistema
    system = EnhancedPredictionsSystem()
    
    # Demonstração 1: Clássico Espanhol
    print("🇪🇸 DEMONSTRAÇÃO 1: REAL MADRID vs BARCELONA (La Liga)")
    print("-" * 60)
    
    match_data_1 = create_sample_match_data()
    all_predictions_1 = system.generate_comprehensive_predictions(match_data_1)
    
    display_predictions_summary(all_predictions_1)
    display_top_recommendations(system, all_predictions_1, top_n=10)
    display_telegram_message(system, match_data_1, all_predictions_1)
    save_demo_results(system, match_data_1, all_predictions_1, "classico_espanhol")
    
    print("\n" + "="*80 + "\n")
    
    # Demonstração 2: Girabola Angola
    print("🇦🇴 DEMONSTRAÇÃO 2: PETRO vs 1º DE AGOSTO (Girabola)")
    print("-" * 60)
    
    match_data_2 = create_angola_match_data()
    all_predictions_2 = system.generate_comprehensive_predictions(match_data_2)
    
    display_predictions_summary(all_predictions_2)
    display_top_recommendations(system, all_predictions_2, top_n=10)
    display_telegram_message(system, match_data_2, all_predictions_2)
    save_demo_results(system, match_data_2, all_predictions_2, "girabola_angola")
    
    print("\n" + "="*80 + "\n")
    
    # Demonstração 3: Premier League
    print("🏴󠁧󠁢󠁥󠁮󠁧󠁿 DEMONSTRAÇÃO 3: ARSENAL vs CHELSEA (Premier League)")
    print("-" * 60)
    
    match_data_3 = create_premier_league_match_data()
    all_predictions_3 = system.generate_comprehensive_predictions(match_data_3)
    
    display_predictions_summary(all_predictions_3)
    display_top_recommendations(system, all_predictions_3, top_n=10)
    display_telegram_message(system, match_data_3, all_predictions_3)
    save_demo_results(system, match_data_3, all_predictions_3, "premier_league")
    
    print("\n" + "="*80 + "\n")
    
    # Resumo final
    print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 50)
    print("✅ Sistema implementado com sucesso!")
    print("🎯 Agora você tem acesso a:")
    print("   • Mercados de golos (Over/Under, BTTS, gols exatos)")
    print("   • Mercados de handicap (Asiático e Europeu)")
    print("   • Mercados de cartões (Amarelos, vermelhos, total)")
    print("   • Mercados de cantos (Total, handicap, primeiro canto)")
    print("   • Mercados de dupla chance (1X, X2, 12)")
    print("   • Mercados de resultado exato (Placar, intervalo)")
    print("   • E muito mais!")
    print()
    print("🚀 O sistema está pronto para gerar predições específicas e detalhadas!")
    print("📱 Integração com Telegram implementada!")
    print("💾 Sistema de salvamento de predições ativo!")

if __name__ == "__main__":
    main()
