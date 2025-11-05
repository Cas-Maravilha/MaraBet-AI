#!/usr/bin/env python3
"""
Predições para Hoje - MaraBet AI
Sistema de predições para partidas de hoje usando dados reais
"""

import requests
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

class TodayPredictions:
    """Sistema de predições para hoje"""
    
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
                params={
                    'date': today,
                    'league': 71,  # Brasileirão
                    'season': 2024
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('response', [])
                
                # Filtrar apenas partidas do Brasileirão
                brasileirao_matches = []
                for match in matches:
                    if match['league']['id'] == 71:  # Brasileirão
                        match_date = datetime.fromisoformat(match['fixture']['date'].replace('Z', '+00:00'))
                        # Incluir partidas de hoje (independente do status)
                        brasileirao_matches.append(match)
                
                logger.info(f"   {len(brasileirao_matches)} partidas do Brasileirão encontradas para hoje")
                return brasileirao_matches
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"   Erro ao buscar partidas de hoje: {e}")
            return []
    
    def get_upcoming_today_matches(self):
        """Obtém partidas que ainda vão acontecer hoje"""
        logger.info("⏰ OBTENDO PARTIDAS QUE AINDA VÃO ACONTECER HOJE")
        print("=" * 60)
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={
                    'date': today,
                    'league': 71,  # Brasileirão
                    'season': 2024,
                    'status': 'NS'  # NS = Not Started
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('response', [])
                
                # Filtrar apenas partidas que ainda não começaram
                upcoming_matches = []
                for match in matches:
                    match_date = datetime.fromisoformat(match['fixture']['date'].replace('Z', '+00:00'))
                    if match_date > datetime.now():
                        upcoming_matches.append(match)
                
                logger.info(f"   {len(upcoming_matches)} partidas ainda vão acontecer hoje")
                return upcoming_matches
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"   Erro ao buscar partidas futuras de hoje: {e}")
            return []
    
    def get_team_form(self, team_id, last_matches=10):
        """Obtém forma recente de um time"""
        try:
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={
                    'team': team_id,
                    'last': last_matches,
                    'status': 'FT'  # FT = Finished
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
            return 0.5
        
        wins = 0
        draws = 0
        losses = 0
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
                elif home_score < away_score:
                    losses += 1
                else:
                    draws += 1
            else:
                goals_for += away_score
                goals_against += home_score
                if away_score > home_score:
                    wins += 1
                elif away_score < home_score:
                    losses += 1
                else:
                    draws += 1
        
        games = len(team_matches)
        if games == 0:
            return 0.5
        
        win_rate = wins / games
        draw_rate = draws / games
        loss_rate = losses / games
        
        avg_goals_for = goals_for / games
        avg_goals_against = goals_against / games
        
        # Calcular força combinada
        strength = (
            win_rate * 0.4 +           # Taxa de vitórias
            draw_rate * 0.1 +          # Taxa de empates
            min(avg_goals_for / 3, 1) * 0.25 +    # Ataque
            max(1 - avg_goals_against / 3, 0) * 0.25  # Defesa
        )
        
        return min(max(strength, 0.1), 0.9)
    
    def predict_match(self, match):
        """Prediz resultado de uma partida"""
        home_team = match['teams']['home']['name']
        away_team = match['teams']['away']['name']
        home_id = match['teams']['home']['id']
        away_id = match['teams']['away']['id']
        match_date = datetime.fromisoformat(match['fixture']['date'].replace('Z', '+00:00'))
        status = match['fixture']['status']['short']
        
        logger.info(f"🔮 PREDIZENDO: {home_team} vs {away_team} ({match_date.strftime('%H:%M')}) - Status: {status}")
        
        # Obter forma recente dos times
        home_form = self.get_team_form(home_id, 10)
        away_form = self.get_team_form(away_id, 10)
        
        # Calcular força dos times
        home_strength = self.calculate_team_strength(home_form, is_home=True)
        away_strength = self.calculate_team_strength(away_form, is_home=False)
        
        # Fator casa
        home_advantage = 0.12
        
        # Fator de confiabilidade
        home_reliability = min(len(home_form) / 10, 1.0)
        away_reliability = min(len(away_form) / 10, 1.0)
        avg_reliability = (home_reliability + away_reliability) / 2
        
        # Calcular probabilidades
        home_win_prob = min(0.85, max(0.05, home_strength + home_advantage - away_strength + 0.5))
        away_win_prob = min(0.85, max(0.05, away_strength - home_strength - home_advantage + 0.5))
        draw_prob = max(0.05, 1 - home_win_prob - away_win_prob)
        
        # Normalizar probabilidades
        total_prob = home_win_prob + draw_prob + away_win_prob
        home_win_prob /= total_prob
        draw_prob /= total_prob
        away_win_prob /= total_prob
        
        # Ajustar confiança
        confidence_multiplier = 0.5 + (avg_reliability * 0.5)
        
        # Calcular odds
        home_odds = 1 / home_win_prob if home_win_prob > 0 else 20
        draw_odds = 1 / draw_prob if draw_prob > 0 else 20
        away_odds = 1 / away_win_prob if away_win_prob > 0 else 20
        
        # Determinar predição
        if home_win_prob > draw_prob and home_win_prob > away_win_prob:
            prediction = "🏠 Casa"
            confidence = home_win_prob * confidence_multiplier
        elif away_win_prob > draw_prob and away_win_prob > home_win_prob:
            prediction = "✈️ Fora"
            confidence = away_win_prob * confidence_multiplier
        else:
            prediction = "🤝 Empate"
            confidence = draw_prob * confidence_multiplier
        
        return {
            'match_id': match['fixture']['id'],
            'home_team': home_team,
            'away_team': away_team,
            'date': match['fixture']['date'],
            'date_formatted': match_date.strftime('%H:%M'),
            'status': status,
            'league': match['league']['name'],
            'prediction': prediction,
            'confidence': confidence,
            'reliability': avg_reliability,
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
    
    def format_predictions_output(self, predictions):
        """Formata saída das predições"""
        if not predictions:
            return "❌ Nenhuma partida encontrada para hoje."
        
        output = f"⚽ PREDIÇÕES PARA HOJE - MARABET AI ⚽\n"
        output += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        output += f"🤖 Sistema de IA com dados reais da API Football\n\n"
        
        for i, prediction in enumerate(predictions, 1):
            output += f"🏆 Partida {i}:\n"
            output += f"⚔️ {prediction['home_team']} vs {prediction['away_team']}\n"
            output += f"📅 {prediction['date_formatted']}\n"
            output += f"🏆 {prediction['league']}\n"
            output += f"📊 Status: {prediction['status']}\n\n"
            
            output += f"🔮 Predição: {prediction['prediction']}\n"
            output += f"📊 Confiança: {prediction['confidence']:.1%}\n"
            output += f"🎯 Confiabilidade: {prediction['reliability']:.1%}\n\n"
            
            output += f"📈 Probabilidades:\n"
            output += f"🏠 Casa: {prediction['probabilities']['home_win']:.1%}\n"
            output += f"🤝 Empate: {prediction['probabilities']['draw']:.1%}\n"
            output += f"✈️ Fora: {prediction['probabilities']['away_win']:.1%}\n\n"
            
            output += f"💰 Odds Calculadas:\n"
            output += f"🏠 Casa: {prediction['odds']['home_win']:.2f}\n"
            output += f"🤝 Empate: {prediction['odds']['draw']:.2f}\n"
            output += f"✈️ Fora: {prediction['odds']['away_win']:.2f}\n\n"
            
            # Análise de valor
            home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
            draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
            away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
            
            output += f"💎 Valor das Apostas:\n"
            output += f"🏠 Casa: {home_value:.1%} {'✅' if home_value > 0.05 else '❌'}\n"
            output += f"🤝 Empate: {draw_value:.1%} {'✅' if draw_value > 0.05 else '❌'}\n"
            output += f"✈️ Fora: {away_value:.1%} {'✅' if away_value > 0.05 else '❌'}\n\n"
            
            # Dados de forma
            output += f"📊 Dados de Forma:\n"
            output += f"🏠 {prediction['home_team']}: {prediction['form_data']['home_games']} jogos analisados\n"
            output += f"✈️ {prediction['away_team']}: {prediction['form_data']['away_games']} jogos analisados\n"
            output += f"💪 Força: Casa {prediction['team_strengths']['home']:.2f} | Fora {prediction['team_strengths']['away']:.2f}\n\n"
            
            output += "─" * 50 + "\n\n"
        
        # Resumo
        avg_confidence = sum(p['confidence'] for p in predictions) / len(predictions)
        avg_reliability = sum(p['reliability'] for p in predictions) / len(predictions)
        positive_value_bets = 0
        
        for prediction in predictions:
            home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
            draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
            away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
            
            if home_value > 0.05 or draw_value > 0.05 or away_value > 0.05:
                positive_value_bets += 1
        
        output += f"📊 RESUMO DAS PREDIÇÕES PARA HOJE:\n"
        output += f"🔮 Predições: {len(predictions)}\n"
        output += f"📈 Confiança média: {avg_confidence:.1%}\n"
        output += f"🎯 Confiabilidade média: {avg_reliability:.1%}\n"
        output += f"💎 Apostas com valor: {positive_value_bets}/{len(predictions)}\n\n"
        
        output += f"⏰ IMPORTANTE: Predições baseadas em dados históricos\n"
        output += f"⚠️ AVISO: Apostas envolvem risco. Use com responsabilidade.\n"
        output += f"🤖 Powered by MaraBet AI - Sistema de IA para Futebol"
        
        return output
    
    def run_today_predictions(self):
        """Executa predições para hoje"""
        print("⚽ PREDIÇÕES PARA HOJE - MARABET AI")
        print("=" * 80)
        
        # 1. Obter partidas de hoje
        today_matches = self.get_today_matches()
        
        if not today_matches:
            print("❌ Nenhuma partida do Brasileirão encontrada para hoje")
            return False
        
        print(f"📊 {len(today_matches)} partidas do Brasileirão encontradas para hoje")
        
        # 2. Obter partidas que ainda vão acontecer hoje
        upcoming_matches = self.get_upcoming_today_matches()
        
        if upcoming_matches:
            print(f"⏰ {len(upcoming_matches)} partidas ainda vão acontecer hoje")
            matches_to_predict = upcoming_matches
        else:
            print("⚠️ Nenhuma partida futura encontrada para hoje")
            print("   Analisando todas as partidas de hoje...")
            matches_to_predict = today_matches
        
        # 3. Gerar predições
        predictions = []
        for match in matches_to_predict[:5]:  # Limitar a 5 partidas
            try:
                prediction = self.predict_match(match)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"   Erro ao predizer partida: {e}")
                continue
        
        if not predictions:
            print("❌ Nenhuma predição gerada")
            return False
        
        print(f"🔮 {len(predictions)} predições geradas para hoje")
        
        # 4. Mostrar predições
        output = self.format_predictions_output(predictions)
        print("\n" + output)
        
        # 5. Salvar predições
        try:
            with open('today_predictions.txt', 'w', encoding='utf-8') as f:
                f.write(output)
            print("\n✅ Predições salvas em: today_predictions.txt")
        except Exception as e:
            print(f"\n❌ Erro ao salvar predições: {e}")
        
        print("\n🎉 PREDIÇÕES PARA HOJE CONCLUÍDAS!")
        return True

def main():
    """Função principal"""
    predictor = TodayPredictions()
    return predictor.run_today_predictions()

if __name__ == "__main__":
    main()
