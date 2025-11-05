#!/usr/bin/env python3
"""
Executar Predições com Dados Reais
MaraBet AI - Predições usando dados reais da API Football
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adicionar diretórios ao path
sys.path.append('.')
sys.path.append('./ml')
sys.path.append('./api')

def load_real_data():
    """Carrega dados reais da API Football"""
    logger.info("📊 CARREGANDO DADOS REAIS DA API FOOTBALL")
    print("=" * 60)
    
    try:
        with open('real_football_data_valid.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"   Dados carregados com sucesso!")
        logger.info(f"   Ligas: {len(data.get('leagues', []))}")
        logger.info(f"   Partidas: {len(data.get('fixtures', []))}")
        logger.info(f"   Coletado em: {data.get('collected_at', 'N/A')}")
        
        return data
    except FileNotFoundError:
        logger.error("   Arquivo de dados não encontrado. Execute primeiro o teste da API.")
        return None
    except Exception as e:
        logger.error(f"   Erro ao carregar dados: {e}")
        return None

def prepare_fixtures_data(fixtures_data):
    """Prepara dados de partidas para análise"""
    logger.info("🔧 PREPARANDO DADOS DE PARTIDAS")
    print("=" * 60)
    
    if not fixtures_data:
        logger.error("   Nenhum dado de partidas disponível")
        return None
    
    matches = []
    for fixture in fixtures_data[:50]:  # Usar primeiras 50 partidas
        try:
            match_data = {
                'match_id': fixture['fixture']['id'],
                'league_id': fixture['league']['id'],
                'league_name': fixture['league']['name'],
                'home_team': fixture['teams']['home']['name'],
                'away_team': fixture['teams']['away']['name'],
                'home_score': fixture['goals']['home'] if fixture['goals']['home'] is not None else 0,
                'away_score': fixture['goals']['away'] if fixture['goals']['away'] is not None else 0,
                'status': fixture['fixture']['status']['short'],
                'date': fixture['fixture']['date'],
                'season': fixture['league']['season']
            }
            matches.append(match_data)
        except Exception as e:
            logger.warning(f"   Erro ao processar partida: {e}")
            continue
    
    logger.info(f"   {len(matches)} partidas processadas")
    return matches

def create_team_stats(matches):
    """Cria estatísticas dos times"""
    logger.info("📈 CRIANDO ESTATÍSTICAS DOS TIMES")
    print("=" * 60)
    
    team_stats = {}
    
    for match in matches:
        home_team = match['home_team']
        away_team = match['away_team']
        home_score = match['home_score']
        away_score = match['away_score']
        
        # Inicializar estatísticas se não existirem
        if home_team not in team_stats:
            team_stats[home_team] = {
                'games_played': 0, 'wins': 0, 'draws': 0, 'losses': 0,
                'goals_for': 0, 'goals_against': 0, 'points': 0
            }
        
        if away_team not in team_stats:
            team_stats[away_team] = {
                'games_played': 0, 'wins': 0, 'draws': 0, 'losses': 0,
                'goals_for': 0, 'goals_against': 0, 'points': 0
            }
        
        # Atualizar estatísticas do time da casa
        team_stats[home_team]['games_played'] += 1
        team_stats[home_team]['goals_for'] += home_score
        team_stats[home_team]['goals_against'] += away_score
        
        # Atualizar estatísticas do time visitante
        team_stats[away_team]['games_played'] += 1
        team_stats[away_team]['goals_for'] += away_score
        team_stats[away_team]['goals_against'] += home_score
        
        # Determinar resultado
        if home_score > away_score:
            team_stats[home_team]['wins'] += 1
            team_stats[home_team]['points'] += 3
            team_stats[away_team]['losses'] += 1
        elif home_score < away_score:
            team_stats[away_team]['wins'] += 1
            team_stats[away_team]['points'] += 3
            team_stats[home_team]['losses'] += 1
        else:
            team_stats[home_team]['draws'] += 1
            team_stats[home_team]['points'] += 1
            team_stats[away_team]['draws'] += 1
            team_stats[away_team]['points'] += 1
    
    # Calcular métricas adicionais
    for team in team_stats:
        stats = team_stats[team]
        if stats['games_played'] > 0:
            stats['win_rate'] = stats['wins'] / stats['games_played']
            stats['avg_goals_for'] = stats['goals_for'] / stats['games_played']
            stats['avg_goals_against'] = stats['goals_against'] / stats['games_played']
            stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
        else:
            stats['win_rate'] = 0
            stats['avg_goals_for'] = 0
            stats['avg_goals_against'] = 0
            stats['goal_difference'] = 0
    
    logger.info(f"   Estatísticas criadas para {len(team_stats)} times")
    return team_stats

def predict_match_outcome(home_team, away_team, team_stats):
    """Prediz o resultado de uma partida"""
    logger.info(f"🔮 PREDIZENDO: {home_team} vs {away_team}")
    
    if home_team not in team_stats or away_team not in team_stats:
        logger.warning(f"   Dados insuficientes para {home_team} ou {away_team}")
        return None
    
    home_stats = team_stats[home_team]
    away_stats = team_stats[away_team]
    
    # Calcular força dos times
    home_strength = (
        home_stats['win_rate'] * 0.4 +
        (home_stats['avg_goals_for'] / 3) * 0.3 +
        (1 - home_stats['avg_goals_against'] / 3) * 0.3
    )
    
    away_strength = (
        away_stats['win_rate'] * 0.4 +
        (away_stats['avg_goals_for'] / 3) * 0.3 +
        (1 - away_stats['avg_goals_against'] / 3) * 0.3
    )
    
    # Fator casa (vantagem do time da casa)
    home_advantage = 0.1
    
    # Calcular probabilidades
    home_win_prob = min(0.8, max(0.1, home_strength + home_advantage - away_strength + 0.5))
    away_win_prob = min(0.8, max(0.1, away_strength - home_strength - home_advantage + 0.5))
    draw_prob = max(0.1, 1 - home_win_prob - away_win_prob)
    
    # Normalizar probabilidades
    total_prob = home_win_prob + draw_prob + away_win_prob
    home_win_prob /= total_prob
    draw_prob /= total_prob
    away_win_prob /= total_prob
    
    # Calcular odds
    home_odds = 1 / home_win_prob if home_win_prob > 0 else 10
    draw_odds = 1 / draw_prob if draw_prob > 0 else 10
    away_odds = 1 / away_win_prob if away_win_prob > 0 else 10
    
    # Determinar predição
    if home_win_prob > draw_prob and home_win_prob > away_win_prob:
        prediction = "Casa"
        confidence = home_win_prob
    elif away_win_prob > draw_prob and away_win_prob > home_win_prob:
        prediction = "Fora"
        confidence = away_win_prob
    else:
        prediction = "Empate"
        confidence = draw_prob
    
    return {
        'home_team': home_team,
        'away_team': away_team,
        'prediction': prediction,
        'confidence': confidence,
        'probabilities': {
            'home_win': home_win_prob,
            'draw': draw_prob,
            'away_win': away_win_prob
        },
        'odds': {
            'home_win': home_odds,
            'draw': draw_odds,
            'away_win': away_odds
        },
        'team_strengths': {
            'home': home_strength,
            'away': away_strength
        }
    }

def run_predictions():
    """Executa predições com dados reais"""
    print("⚽ EXECUTANDO PREDIÇÕES COM DADOS REAIS - MARABET AI")
    print("=" * 80)
    
    # 1. Carregar dados reais
    data = load_real_data()
    if not data:
        return False
    
    # 2. Preparar dados de partidas
    matches = prepare_fixtures_data(data.get('fixtures', []))
    if not matches:
        return False
    
    # 3. Criar estatísticas dos times
    team_stats = create_team_stats(matches)
    
    # 4. Mostrar estatísticas dos times
    print("\n📊 ESTATÍSTICAS DOS TIMES:")
    print("=" * 60)
    for team, stats in sorted(team_stats.items(), key=lambda x: x[1]['points'], reverse=True)[:10]:
        print(f"   {team}:")
        print(f"     Jogos: {stats['games_played']} | Vitórias: {stats['wins']} | Empates: {stats['draws']} | Derrotas: {stats['losses']}")
        print(f"     Pontos: {stats['points']} | Gols Pró: {stats['goals_for']} | Gols Contra: {stats['goals_against']}")
        print(f"     Taxa de Vitória: {stats['win_rate']:.2%} | Força: {stats['win_rate'] * 0.4 + (stats['avg_goals_for'] / 3) * 0.3 + (1 - stats['avg_goals_against'] / 3) * 0.3:.2f}")
        print()
    
    # 5. Executar predições para partidas futuras simuladas
    print("\n🔮 PREDIÇÕES DE PARTIDAS:")
    print("=" * 60)
    
    # Selecionar times para simular partidas
    teams = list(team_stats.keys())
    if len(teams) < 2:
        print("   Dados insuficientes para predições")
        return False
    
    # Simular 5 partidas
    predictions = []
    for i in range(5):
        home_team = teams[i % len(teams)]
        away_team = teams[(i + 1) % len(teams)]
        
        if home_team != away_team:
            prediction = predict_match_outcome(home_team, away_team, team_stats)
            if prediction:
                predictions.append(prediction)
                
                print(f"   🏆 {prediction['home_team']} vs {prediction['away_team']}")
                print(f"      Predição: {prediction['prediction']} (Confiança: {prediction['confidence']:.2%})")
                print(f"      Probabilidades: Casa {prediction['probabilities']['home_win']:.2%} | Empate {prediction['probabilities']['draw']:.2%} | Fora {prediction['probabilities']['away_win']:.2%}")
                print(f"      Odds: Casa {prediction['odds']['home_win']:.2f} | Empate {prediction['odds']['draw']:.2f} | Fora {prediction['odds']['away_win']:.2f}")
                print(f"      Força dos Times: Casa {prediction['team_strengths']['home']:.2f} | Fora {prediction['team_strengths']['away']:.2f}")
                print()
    
    # 6. Análise de valor das apostas
    print("\n💰 ANÁLISE DE VALOR DAS APOSTAS:")
    print("=" * 60)
    
    for prediction in predictions:
        # Calcular valor esperado para cada aposta
        home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
        draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
        away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
        
        print(f"   {prediction['home_team']} vs {prediction['away_team']}:")
        print(f"      Valor Casa: {home_value:.2%} {'✅' if home_value > 0 else '❌'}")
        print(f"      Valor Empate: {draw_value:.2%} {'✅' if draw_value > 0 else '❌'}")
        print(f"      Valor Fora: {away_value:.2%} {'✅' if away_value > 0 else '❌'}")
        print()
    
    # 7. Resumo das predições
    print("\n📊 RESUMO DAS PREDIÇÕES:")
    print("=" * 60)
    print(f"   Total de partidas analisadas: {len(matches)}")
    print(f"   Times analisados: {len(team_stats)}")
    print(f"   Predições geradas: {len(predictions)}")
    
    # Calcular confiança média
    if predictions:
        avg_confidence = sum(p['confidence'] for p in predictions) / len(predictions)
        print(f"   Confiança média: {avg_confidence:.2%}")
    
    # Contar apostas com valor positivo
    positive_value_bets = 0
    for prediction in predictions:
        home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
        draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
        away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
        
        if home_value > 0 or draw_value > 0 or away_value > 0:
            positive_value_bets += 1
    
    print(f"   Apostas com valor positivo: {positive_value_bets}/{len(predictions)}")
    
    print("\n🎉 PREDIÇÕES CONCLUÍDAS COM SUCESSO!")
    return True

if __name__ == "__main__":
    run_predictions()
