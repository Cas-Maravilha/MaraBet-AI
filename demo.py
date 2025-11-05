#!/usr/bin/env python3
"""
Demonstração rápida do MaraBet AI
Executa uma análise básica sem interface web
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector import SportsDataCollector
from feature_engineering import FeatureEngineer
from ml_models import BettingPredictor, BettingAnalyzer

def main():
    print("🏈 MARABET AI - DEMONSTRAÇÃO RÁPIDA")
    print("=" * 40)
    
    # 1. Coleta de dados
    print("\n📊 Coletando dados esportivos...")
    collector = SportsDataCollector()
    matches = collector.get_football_matches('all', 5)
    print(f"   ✓ {len(matches)} partidas coletadas")
    
    # 2. Análise de forma dos times
    print("\n⚽ Analisando forma dos times...")
    teams = ['Flamengo', 'Palmeiras', 'São Paulo']
    for team in teams:
        form = collector.get_team_form(team)
        print(f"   {team}: {form['wins']}V-{form['draws']}E-{form['losses']}D "
              f"(Taxa: {form['win_rate']:.1%})")
    
    # 3. Criação de features
    print("\n🔧 Criando features...")
    engineer = FeatureEngineer()
    
    # Simula dados históricos
    historical_data = {}
    for team in teams:
        historical_data[team] = collector.get_historical_results(team)
    
    # Cria features para primeira partida
    if matches:
        match = matches[0]
        home_features = engineer.create_team_features(
            historical_data.get(match['home_team'], []),
            historical_data.get(match['away_team'], []),
            is_home=True
        )
        print(f"   ✓ {len(home_features)} features criadas para {match['home_team']}")
    
    # 4. Análise de partida
    print("\n🎯 Analisando partida...")
    if matches:
        match = matches[0]
        home_data = historical_data.get(match['home_team'], [])
        away_data = historical_data.get(match['away_team'], [])
        
        features = engineer.create_match_features(home_data, away_data, match)
        match_df = pd.DataFrame([features])
        
        # Inicializa predictor e analyzer
        predictor = BettingPredictor()
        analyzer = BettingAnalyzer(predictor)
        
        # Simula análise (sem treinamento real)
        print(f"   Partida: {match['home_team']} vs {match['away_team']}")
        print(f"   Data: {match['date']}")
        print(f"   Odds: Casa {match['home_odds']:.2f} | Empate {match['draw_odds']:.2f} | Fora {match['away_odds']:.2f}")
        
        # Simula predição
        import random
        home_prob = random.uniform(0.3, 0.6)
        draw_prob = random.uniform(0.2, 0.4)
        away_prob = 1 - home_prob - draw_prob
        
        print(f"\n   📈 Predições simuladas:")
        print(f"   Casa: {home_prob:.1%}")
        print(f"   Empate: {draw_prob:.1%}")
        print(f"   Fora: {away_prob:.1%}")
        
        # Simula recomendação
        home_ev = (home_prob * match['home_odds']) - 1
        draw_ev = (draw_prob * match['draw_odds']) - 1
        away_ev = (away_prob * match['away_odds']) - 1
        
        print(f"\n   💰 Valor Esperado:")
        print(f"   Casa: {home_ev:.1%}")
        print(f"   Empate: {draw_ev:.1%}")
        print(f"   Fora: {away_ev:.1%}")
        
        best_ev = max(home_ev, draw_ev, away_ev)
        if best_ev > 0.1:
            print(f"\n   ✅ Recomendação: APOSTAR (EV: {best_ev:.1%})")
        else:
            print(f"\n   ❌ Recomendação: EVITAR (EV máximo: {best_ev:.1%})")
    
    print("\n" + "=" * 40)
    print("🎉 Demonstração concluída!")
    print("\nPara usar o sistema completo:")
    print("  python main.py --web     # Interface web")
    print("  python main.py --mode full  # Análise completa")
    print("  python run_example.py    # Exemplo detalhado")

if __name__ == "__main__":
    import pandas as pd
    main()
