#!/usr/bin/env python3
"""
Demonstração do Framework Avançado MaraBet AI
Mostra todas as funcionalidades do framework de análise completo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from framework_integration import MaraBetFramework
from data_framework import DataProcessor
from advanced_features import AdvancedFeatureEngineer
import json

def main():
    print("🏈 MARABET AI - FRAMEWORK AVANÇADO")
    print("=" * 50)
    print("Sistema de Análise Preditiva com Framework Completo")
    print("=" * 50)
    
    # Inicializa o framework
    framework = MaraBetFramework()
    
    print("\n📊 ETAPA 1: COLETA E PROCESSAMENTO DE DADOS")
    print("-" * 40)
    
    # Demonstra coleta de dados
    data_processor = DataProcessor()
    
    print("\n1.1 Estatísticas Históricas (10-20 partidas)")
    home_analysis = data_processor.process_team_analysis('Flamengo')
    print(f"   Flamengo - Forma: {home_analysis['recent_form']['form']}")
    print(f"   Gols por jogo: {home_analysis['historical_stats'].goals_scored:.2f}")
    print(f"   Posse de bola: {home_analysis['historical_stats'].possession:.1f}%")
    
    print("\n1.2 Confrontos Diretos (H2H)")
    h2h_stats = data_processor.collector.get_head_to_head_stats('Flamengo', 'Palmeiras', 8)
    print(f"   Flamengo vs Palmeiras - {h2h_stats['total_matches']} confrontos")
    print(f"   Vantagem Flamengo: {h2h_stats['team1_win_rate']:.1%}")
    
    print("\n1.3 Desempenho Casa/Fora")
    home_away = data_processor.collector.get_home_away_performance('Flamengo', 10)
    print(f"   Flamengo em casa: {home_away['home']['win_rate']:.1%}")
    print(f"   Flamengo fora: {home_away['away']['win_rate']:.1%}")
    print(f"   Fator casa: {home_away['home_advantage']:.2f}")
    
    print("\n1.4 Forma Recente (últimos 5 jogos)")
    recent_form = data_processor.collector.get_recent_form_analysis('Flamengo', 5)
    print(f"   Forma: {recent_form['form']} ({recent_form['trend']})")
    print(f"   Pontos: {recent_form['points']}/{recent_form['matches']*3}")
    
    print("\n1.5 Estatísticas Avançadas")
    advanced_stats = data_processor.collector.get_advanced_stats('Flamengo', 10)
    print(f"   xG por jogo: {advanced_stats['xg_for']:.2f}")
    print(f"   Finalizações: {advanced_stats['shots_per_game']:.1f}")
    print(f"   Precisão: {advanced_stats['shot_accuracy']:.1f}%")
    
    print("\n1.6 Contexto Competitivo")
    competitive_context = data_processor.collector.get_competitive_context('Flamengo')
    print(f"   Posição: {competitive_context['position']}/{competitive_context['total_teams']}")
    print(f"   Objetivo: {competitive_context['objective']}")
    print(f"   Pressão: {competitive_context['pressure_level']}")
    
    print("\n1.7 Fatores Contextuais")
    match_context = data_processor.collector.get_match_context('Flamengo', 'Palmeiras', '2024-01-15')
    print(f"   Clima: {match_context.weather}")
    print(f"   Lesões Flamengo: {len(match_context.home_team_injuries)}")
    print(f"   Lesões Palmeiras: {len(match_context.away_team_injuries)}")
    
    print("\n🔧 ETAPA 2: FEATURE ENGINEERING AVANÇADO")
    print("-" * 40)
    
    # Demonstra criação de features
    feature_engineer = AdvancedFeatureEngineer()
    features = feature_engineer.create_comprehensive_features('Flamengo', 'Palmeiras', '2024-01-15')
    
    print(f"\n2.1 Total de Features Criadas: {len(features)}")
    
    # Mostra features por categoria
    categories = {
        'Históricas': [k for k in features.keys() if 'home_' in k and not any(x in k for x in ['recent', 'home_', 'away_'])],
        'H2H': [k for k in features.keys() if 'h2h_' in k],
        'Casa/Fora': [k for k in features.keys() if any(x in k for x in ['home_home', 'away_away', 'home_advantage'])],
        'Forma Recente': [k for k in features.keys() if 'recent_' in k],
        'Avançadas': [k for k in features.keys() if any(x in k for x in ['xg_', 'possession_', 'shots_', 'passes_'])],
        'Contexto': [k for k in features.keys() if any(x in k for x in ['position', 'pressure', 'objective'])],
        'Comparativas': [k for k in features.keys() if any(x in k for x in ['difference', 'advantage', 'momentum'])]
    }
    
    for category, feature_list in categories.items():
        if feature_list:
            print(f"\n2.2 {category}: {len(feature_list)} features")
            for feature in feature_list[:3]:  # Mostra apenas as primeiras 3
                print(f"   {feature}: {features[feature]:.3f}")
            if len(feature_list) > 3:
                print(f"   ... e mais {len(feature_list) - 3} features")
    
    print("\n🤖 ETAPA 3: ANÁLISE PREDITIVA COMPLETA")
    print("-" * 40)
    
    # Executa análise completa
    analysis = framework.analyze_match_comprehensive('Flamengo', 'Palmeiras', '2024-01-15')
    
    print(f"\n3.1 Informações da Partida")
    print(f"   {analysis['match_info']['home_team']} vs {analysis['match_info']['away_team']}")
    print(f"   Data: {analysis['match_info']['date']}")
    
    print(f"\n3.2 Predição")
    prediction = analysis['prediction']
    print(f"   Resultado: {prediction['predicted_result']}")
    print(f"   Confiança: {prediction['confidence']:.1%}")
    print(f"   Método: {prediction['prediction_method']}")
    
    print(f"\n3.3 Probabilidades")
    probs = prediction['probabilities']
    print(f"   Casa: {probs['home_win']:.1%}")
    print(f"   Empate: {probs['draw']:.1%}")
    print(f"   Fora: {probs['away_win']:.1%}")
    
    print(f"\n3.4 Odds Calculadas")
    odds = prediction['calculated_odds']
    print(f"   Casa: {odds['home']:.2f}")
    print(f"   Empate: {odds['draw']:.2f}")
    print(f"   Fora: {odds['away']:.2f}")
    
    print("\n💰 ETAPA 4: RECOMENDAÇÕES DE APOSTAS")
    print("-" * 40)
    
    betting = analysis['betting_recommendations']
    print(f"\n4.1 Total de Recomendações: {betting['total_recommendations']}")
    print(f"   Apostas Fortes: {betting['strong_bets']}")
    print(f"   Evitar: {betting['avoid_bets']}")
    
    if betting['best_bet']:
        best = betting['best_bet']
        print(f"\n4.2 Melhor Aposta")
        print(f"   Resultado: {best['outcome']}")
        print(f"   Odds: {best['market_odds']:.2f}")
        print(f"   Valor Esperado: {best['expected_value']:.1%}")
        print(f"   Kelly: {best['kelly_percentage']:.1%}")
        print(f"   Recomendação: {best['recommendation']}")
    
    print(f"\n4.3 Todas as Recomendações")
    for i, rec in enumerate(betting['recommendations'], 1):
        print(f"   {i}. {rec['outcome']}: {rec['recommendation']} (EV: {rec['expected_value']:.1%})")
    
    print("\n⚠️ ETAPA 5: ANÁLISE DE RISCO")
    print("-" * 40)
    
    risk = analysis['risk_analysis']
    print(f"\n5.1 Nível de Risco: {risk['risk_level']}")
    print(f"   Score: {risk['risk_score']}/10")
    print(f"   Confiança: {risk['confidence']:.1%}")
    print(f"   Recomendação: {risk['recommendation']}")
    
    if risk['risk_factors']:
        print(f"\n5.2 Fatores de Risco:")
        for factor in risk['risk_factors']:
            print(f"   - {factor}")
    
    print("\n📋 ETAPA 6: RESUMO EXECUTIVO")
    print("-" * 40)
    
    summary = analysis['executive_summary']
    print(f"\n6.1 Partida: {summary['match']}")
    print(f"   Predição: {summary['prediction']['result']} ({summary['prediction']['confidence']})")
    print(f"   Método: {summary['prediction']['method']}")
    
    print(f"\n6.2 Análise dos Times")
    home_team = summary['team_analysis']['home_team']
    away_team = summary['team_analysis']['away_team']
    print(f"   {home_team['form'].title()}: Forma {home_team['form']}, Posição {home_team['position']}")
    print(f"   {away_team['form'].title()}: Forma {away_team['form']}, Posição {away_team['position']}")
    
    print(f"\n6.3 Análise de Apostas")
    betting_analysis = summary['betting_analysis']
    print(f"   Melhor aposta: {betting_analysis['best_bet']}")
    print(f"   Valor esperado: {betting_analysis['expected_value']}")
    print(f"   Recomendação: {betting_analysis['recommendation']}")
    
    print(f"\n6.4 Insights-Chave")
    for insight in summary['key_insights']:
        print(f"   • {insight}")
    
    print("\n" + "=" * 50)
    print("🎉 DEMONSTRAÇÃO DO FRAMEWORK CONCLUÍDA!")
    print("=" * 50)
    
    print(f"\n📊 ESTATÍSTICAS DO FRAMEWORK:")
    print(f"   • Features criadas: {analysis['features']['total_features']}")
    print(f"   • Features selecionadas: {analysis['features']['selected_features']}")
    print(f"   • Categorias de análise: 7")
    print(f"   • Fontes de dados: 7")
    print(f"   • Modelos de ML: 6")
    print(f"   • Métricas de risco: 5")
    
    print(f"\n🚀 PRÓXIMOS PASSOS:")
    print(f"   • python main.py --mode framework")
    print(f"   • python main.py --web")
    print(f"   • Integração com APIs reais")
    print(f"   • Deploy em produção")

if __name__ == "__main__":
    main()
