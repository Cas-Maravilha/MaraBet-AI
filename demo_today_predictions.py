#!/usr/bin/env python3
"""
Demonstração de Predições para Hoje
MaraBet AI - Demo do sistema com dados simulados para hoje
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

class TodayPredictionsDemo:
    """Demo do sistema de predições para hoje"""
    
    def __init__(self):
        self.teams = [
            "Flamengo", "Palmeiras", "São Paulo", "Santos", "Corinthians",
            "Internacional", "Grêmio", "Atlético-MG", "Cruzeiro", "Botafogo",
            "Vasco", "Fluminense", "Bahia", "Fortaleza", "Ceará",
            "Athletico-PR", "Chapecoense", "Goiás", "Cuiabá", "Juventude"
        ]
    
    def generate_today_matches(self, num_matches=3):
        """Gera partidas simuladas para hoje"""
        logger.info(f"🎲 GERANDO {num_matches} PARTIDAS PARA HOJE")
        
        matches = []
        for i in range(num_matches):
            home_team = np.random.choice(self.teams)
            away_team = np.random.choice([t for t in self.teams if t != home_team])
            
            # Horários diferentes para hoje
            hours = [16, 19, 21]  # 16h, 19h, 21h
            match_time = datetime.now().replace(hour=hours[i % len(hours)], minute=0, second=0, microsecond=0)
            
            # Status da partida
            statuses = ['NS', '1H', '2H', 'HT', 'FT']  # Not Started, 1st Half, 2nd Half, Half Time, Finished
            status = np.random.choice(statuses)
            
            match = {
                'fixture': {
                    'id': 3000 + i,
                    'date': match_time.isoformat(),
                    'status': {
                        'short': status
                    }
                },
                'teams': {
                    'home': {
                        'id': 100 + i,
                        'name': home_team
                    },
                    'away': {
                        'id': 200 + i,
                        'name': away_team
                    }
                },
                'league': {
                    'id': 71,
                    'name': 'Serie A',
                    'season': 2024
                }
            }
            matches.append(match)
        
        logger.info(f"   {len(matches)} partidas para hoje geradas")
        return matches
    
    def get_team_form_simulated(self, team_name, last_matches=10):
        """Simula forma recente de um time"""
        np.random.seed(hash(team_name) % 2**32)
        
        matches = []
        for i in range(last_matches):
            home_score = np.random.poisson(1.5)
            away_score = np.random.poisson(1.2)
            
            match = {
                'goals': {
                    'home': home_score,
                    'away': away_score
                }
            }
            matches.append(match)
        
        return matches
    
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
            home_score = match['goals']['home']
            away_score = match['goals']['away']
            
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
        match_time = datetime.fromisoformat(match['fixture']['date'])
        status = match['fixture']['status']['short']
        
        logger.info(f"🔮 PREDIZENDO: {home_team} vs {away_team} ({match_time.strftime('%H:%M')}) - Status: {status}")
        
        # Obter forma recente dos times
        home_form = self.get_team_form_simulated(home_team, 10)
        away_form = self.get_team_form_simulated(away_team, 10)
        
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
            'date_formatted': match_time.strftime('%H:%M'),
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
        output += f"🤖 Sistema de IA com dados simulados para demonstração\n\n"
        
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
        
        output += f"⏰ IMPORTANTE: Predições baseadas em dados simulados\n"
        output += f"📊 DADOS: Simulados para demonstração do conceito\n"
        output += f"⚠️ AVISO: Apostas envolvem risco. Use com responsabilidade.\n"
        output += f"🤖 Powered by MaraBet AI - Sistema de IA para Futebol"
        
        return output
    
    def run_demo(self):
        """Executa demonstração do sistema"""
        print("⚽ DEMONSTRAÇÃO DE PREDIÇÕES PARA HOJE - MARABET AI")
        print("=" * 80)
        
        # 1. Gerar partidas para hoje
        today_matches = self.generate_today_matches(3)
        
        print(f"📊 {len(today_matches)} partidas simuladas para hoje")
        
        # 2. Gerar predições
        predictions = []
        for match in today_matches:
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
        
        # 3. Mostrar predições
        output = self.format_predictions_output(predictions)
        print("\n" + output)
        
        # 4. Salvar predições
        try:
            with open('today_predictions_demo.txt', 'w', encoding='utf-8') as f:
                f.write(output)
            print("\n✅ Predições salvas em: today_predictions_demo.txt")
        except Exception as e:
            print(f"\n❌ Erro ao salvar predições: {e}")
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        return True

def main():
    """Função principal"""
    demo = TodayPredictionsDemo()
    return demo.run_demo()

if __name__ == "__main__":
    main()
