#!/usr/bin/env python3
"""
Predições em Tempo Real
MaraBet AI - Predições usando dados atuais da API Football
"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LivePredictor:
    """Preditor em tempo real usando API Football"""
    
    def __init__(self):
        self.api_key = "71b2b62386f2d1275cd3201a73e1e045"
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
    
    def get_today_matches(self):
        """Obtém partidas de hoje"""
        logger.info("📅 OBTENDO PARTIDAS DE HOJE")
        print("=" * 60)
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={'date': today},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('response', [])
                logger.info(f"   {len(matches)} partidas encontradas para hoje")
                return matches
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"   Erro ao buscar partidas: {e}")
            return []
    
    def get_upcoming_matches(self, days=3):
        """Obtém partidas próximas"""
        logger.info(f"📅 OBTENDO PARTIDAS DOS PRÓXIMOS {days} DIAS")
        print("=" * 60)
        
        try:
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={
                    'from': start_date,
                    'to': end_date,
                    'league': 71,  # Brasileirão
                    'season': 2024
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('response', [])
                logger.info(f"   {len(matches)} partidas encontradas para os próximos {days} dias")
                return matches
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"   Erro ao buscar partidas: {e}")
            return []
    
    def get_team_form(self, team_id, last_matches=5):
        """Obtém forma recente de um time"""
        try:
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={
                    'team': team_id,
                    'last': last_matches
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', [])
            return []
            
        except Exception as e:
            logger.error(f"   Erro ao buscar forma do time {team_id}: {e}")
            return []
    
    def calculate_team_strength(self, team_matches, is_home=True):
        """Calcula força de um time baseada em partidas recentes"""
        if not team_matches:
            return 0.5  # Força neutra se não há dados
        
        wins = 0
        goals_for = 0
        goals_against = 0
        
        for match in team_matches:
            home_score = match['goals']['home'] if match['goals']['home'] is not None else 0
            away_score = match['goals']['away'] if match['goals']['away'] is not None else 0
            
            if is_home:
                goals_for += home_score
                goals_against += away_score
                if home_score > away_score:
                    wins += 1
            else:
                goals_for += away_score
                goals_against += home_score
                if away_score > home_score:
                    wins += 1
        
        games = len(team_matches)
        if games == 0:
            return 0.5
        
        win_rate = wins / games
        avg_goals_for = goals_for / games
        avg_goals_against = goals_against / games
        
        # Calcular força combinada
        strength = (
            win_rate * 0.4 +
            min(avg_goals_for / 3, 1) * 0.3 +
            max(1 - avg_goals_against / 3, 0) * 0.3
        )
        
        return min(max(strength, 0.1), 0.9)
    
    def predict_match(self, match):
        """Prediz resultado de uma partida"""
        home_team = match['teams']['home']['name']
        away_team = match['teams']['away']['name']
        home_id = match['teams']['home']['id']
        away_id = match['teams']['away']['id']
        
        logger.info(f"🔮 PREDIZENDO: {home_team} vs {away_team}")
        
        # Obter forma recente dos times
        home_form = self.get_team_form(home_id, 5)
        away_form = self.get_team_form(away_id, 5)
        
        # Calcular força dos times
        home_strength = self.calculate_team_strength(home_form, is_home=True)
        away_strength = self.calculate_team_strength(away_form, is_home=False)
        
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
            'match_id': match['fixture']['id'],
            'home_team': home_team,
            'away_team': away_team,
            'date': match['fixture']['date'],
            'league': match['league']['name'],
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
            },
            'form_data': {
                'home_games': len(home_form),
                'away_games': len(away_form)
            }
        }
    
    def run_live_predictions(self):
        """Executa predições em tempo real"""
        print("⚽ PREDIÇÕES EM TEMPO REAL - MARABET AI")
        print("=" * 80)
        
        # 1. Obter partidas de hoje
        today_matches = self.get_today_matches()
        
        # 2. Obter partidas próximas
        upcoming_matches = self.get_upcoming_matches(3)
        
        # 3. Combinar partidas
        all_matches = today_matches + upcoming_matches
        
        if not all_matches:
            print("   ❌ Nenhuma partida encontrada")
            return False
        
        # 4. Filtrar partidas do Brasileirão
        brasileirao_matches = [m for m in all_matches if m['league']['id'] == 71]
        
        if not brasileirao_matches:
            print("   ❌ Nenhuma partida do Brasileirão encontrada")
            return False
        
        print(f"\n📊 PARTIDAS ENCONTRADAS:")
        print("=" * 60)
        print(f"   Total de partidas: {len(all_matches)}")
        print(f"   Partidas do Brasileirão: {len(brasileirao_matches)}")
        print(f"   Partidas de hoje: {len(today_matches)}")
        
        # 5. Executar predições
        predictions = []
        for match in brasileirao_matches[:10]:  # Limitar a 10 partidas
            try:
                prediction = self.predict_match(match)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"   Erro ao predizer partida: {e}")
                continue
        
        if not predictions:
            print("   ❌ Nenhuma predição gerada")
            return False
        
        # 6. Mostrar predições
        print(f"\n🔮 PREDIÇÕES EM TEMPO REAL:")
        print("=" * 60)
        
        for i, prediction in enumerate(predictions, 1):
            print(f"   🏆 Partida {i}: {prediction['home_team']} vs {prediction['away_team']}")
            print(f"      Data: {prediction['date'][:10]}")
            print(f"      Liga: {prediction['league']}")
            print(f"      Predição: {prediction['prediction']} (Confiança: {prediction['confidence']:.2%})")
            print(f"      Probabilidades: Casa {prediction['probabilities']['home_win']:.2%} | Empate {prediction['probabilities']['draw']:.2%} | Fora {prediction['probabilities']['away_win']:.2%}")
            print(f"      Odds: Casa {prediction['odds']['home_win']:.2f} | Empate {prediction['odds']['draw']:.2f} | Fora {prediction['odds']['away_win']:.2f}")
            print(f"      Força dos Times: Casa {prediction['team_strengths']['home']:.2f} | Fora {prediction['team_strengths']['away']:.2f}")
            print(f"      Dados de Forma: Casa {prediction['form_data']['home_games']} jogos | Fora {prediction['form_data']['away_games']} jogos")
            print()
        
        # 7. Análise de valor das apostas
        print("\n💰 ANÁLISE DE VALOR DAS APOSTAS:")
        print("=" * 60)
        
        positive_value_bets = 0
        for prediction in predictions:
            home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
            draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
            away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
            
            print(f"   {prediction['home_team']} vs {prediction['away_team']}:")
            print(f"      Valor Casa: {home_value:.2%} {'✅' if home_value > 0.05 else '❌'}")
            print(f"      Valor Empate: {draw_value:.2%} {'✅' if draw_value > 0.05 else '❌'}")
            print(f"      Valor Fora: {away_value:.2%} {'✅' if away_value > 0.05 else '❌'}")
            
            if home_value > 0.05 or draw_value > 0.05 or away_value > 0.05:
                positive_value_bets += 1
            print()
        
        # 8. Resumo
        print("\n📊 RESUMO DAS PREDIÇÕES EM TEMPO REAL:")
        print("=" * 60)
        print(f"   Partidas analisadas: {len(predictions)}")
        print(f"   Confiança média: {sum(p['confidence'] for p in predictions) / len(predictions):.2%}")
        print(f"   Apostas com valor positivo (>5%): {positive_value_bets}/{len(predictions)}")
        
        # 9. Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        print("=" * 60)
        if positive_value_bets > 0:
            print(f"   ✅ {positive_value_bets} apostas com valor positivo identificadas")
            print(f"   💰 Considere apostar nas opções com valor > 5%")
        else:
            print(f"   ⚠️ Nenhuma aposta com valor positivo identificada")
            print(f"   🔍 Aguarde melhores oportunidades ou ajuste os critérios")
        
        print(f"   📊 Monitore as partidas em tempo real")
        print(f"   🔄 Atualize as predições regularmente")
        
        print("\n🎉 PREDIÇÕES EM TEMPO REAL CONCLUÍDAS!")
        return True

def main():
    """Função principal"""
    predictor = LivePredictor()
    return predictor.run_live_predictions()

if __name__ == "__main__":
    main()
