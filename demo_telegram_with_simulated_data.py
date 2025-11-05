#!/usr/bin/env python3
"""
Demonstração de Envio via Telegram com Dados Simulados
MaraBet AI - Demo do sistema com dados simulados
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

class TelegramSimulatedDemo:
    """Demo do sistema com dados simulados"""
    
    def __init__(self):
        self.teams = [
            "Flamengo", "Palmeiras", "São Paulo", "Santos", "Corinthians",
            "Internacional", "Grêmio", "Atlético-MG", "Cruzeiro", "Botafogo",
            "Vasco", "Fluminense", "Bahia", "Fortaleza", "Ceará",
            "Athletico-PR", "Chapecoense", "Goiás", "Cuiabá", "Juventude"
        ]
    
    def generate_simulated_matches(self, num_matches=5):
        """Gera partidas simuladas"""
        logger.info(f"🎲 GERANDO {num_matches} PARTIDAS SIMULADAS")
        
        matches = []
        for i in range(num_matches):
            home_team = np.random.choice(self.teams)
            away_team = np.random.choice([t for t in self.teams if t != home_team])
            
            # Data aleatória nos próximos 7 dias
            match_date = datetime.now() + timedelta(days=np.random.randint(0, 7))
            
            match = {
                'fixture': {
                    'id': 1000 + i,
                    'date': match_date.isoformat()
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
        
        logger.info(f"   {len(matches)} partidas simuladas geradas")
        return matches
    
    def get_team_form_simulated(self, team_name, last_matches=5):
        """Simula forma recente de um time"""
        # Simular dados de forma baseados no nome do time
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
        
        # Obter forma recente dos times (simulada)
        home_form = self.get_team_form_simulated(home_team, 5)
        away_form = self.get_team_form_simulated(away_team, 5)
        
        # Calcular força dos times
        home_strength = self.calculate_team_strength(home_form, is_home=True)
        away_strength = self.calculate_team_strength(away_form, is_home=False)
        
        # Fator casa
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
            prediction = "🏠 Casa"
            confidence = home_win_prob
        elif away_win_prob > draw_prob and away_win_prob > home_win_prob:
            prediction = "✈️ Fora"
            confidence = away_win_prob
        else:
            prediction = "🤝 Empate"
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
            }
        }
    
    def format_telegram_message(self, predictions):
        """Formata mensagem para o Telegram"""
        if not predictions:
            return "❌ Nenhuma predição disponível no momento."
        
        message = f"⚽ <b>PREDIÇÕES MARABET AI</b> ⚽\n"
        message += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        message += f"🤖 Sistema de IA com dados simulados para demonstração\n\n"
        
        for i, prediction in enumerate(predictions, 1):
            message += f"🏆 <b>Partida {i}:</b>\n"
            message += f"⚔️ {prediction['home_team']} vs {prediction['away_team']}\n"
            message += f"📅 {prediction['date'][:10]}\n"
            message += f"🏆 {prediction['league']}\n\n"
            
            message += f"🔮 <b>Predição:</b> {prediction['prediction']}\n"
            message += f"📊 <b>Confiança:</b> {prediction['confidence']:.1%}\n\n"
            
            message += f"📈 <b>Probabilidades:</b>\n"
            message += f"🏠 Casa: {prediction['probabilities']['home_win']:.1%}\n"
            message += f"🤝 Empate: {prediction['probabilities']['draw']:.1%}\n"
            message += f"✈️ Fora: {prediction['probabilities']['away_win']:.1%}\n\n"
            
            message += f"💰 <b>Odds Calculadas:</b>\n"
            message += f"🏠 Casa: {prediction['odds']['home_win']:.2f}\n"
            message += f"🤝 Empate: {prediction['odds']['draw']:.2f}\n"
            message += f"✈️ Fora: {prediction['odds']['away_win']:.2f}\n\n"
            
            # Análise de valor
            home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
            draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
            away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
            
            message += f"💎 <b>Valor das Apostas:</b>\n"
            message += f"🏠 Casa: {home_value:.1%} {'✅' if home_value > 0.05 else '❌'}\n"
            message += f"🤝 Empate: {draw_value:.1%} {'✅' if draw_value > 0.05 else '❌'}\n"
            message += f"✈️ Fora: {away_value:.1%} {'✅' if away_value > 0.05 else '❌'}\n\n"
            
            message += "─" * 30 + "\n\n"
        
        # Resumo
        avg_confidence = sum(p['confidence'] for p in predictions) / len(predictions)
        positive_value_bets = 0
        
        for prediction in predictions:
            home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
            draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
            away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
            
            if home_value > 0.05 or draw_value > 0.05 or away_value > 0.05:
                positive_value_bets += 1
        
        message += f"📊 <b>RESUMO:</b>\n"
        message += f"🔮 Predições: {len(predictions)}\n"
        message += f"📈 Confiança média: {avg_confidence:.1%}\n"
        message += f"💎 Apostas com valor: {positive_value_bets}/{len(predictions)}\n\n"
        
        message += f"⚠️ <b>AVISO:</b> Apostas envolvem risco. Use com responsabilidade.\n"
        message += f"🤖 Powered by MaraBet AI - Sistema de IA para Futebol"
        
        return message
    
    def save_message_to_file(self, message, filename="telegram_message_demo.txt"):
        """Salva mensagem em arquivo para demonstração"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(message)
            print(f"✅ Mensagem salva em: {filename}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar mensagem: {e}")
            return False
    
    def run_demo(self):
        """Executa demonstração do sistema"""
        print("📱 DEMONSTRAÇÃO DE ENVIO VIA TELEGRAM - MARABET AI")
        print("=" * 80)
        
        # 1. Gerar partidas simuladas
        matches = self.generate_simulated_matches(5)
        
        print(f"📊 {len(matches)} partidas simuladas geradas")
        
        # 2. Gerar predições
        predictions = []
        for match in matches:
            try:
                prediction = self.predict_match(match)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"   Erro ao predizer partida: {e}")
                continue
        
        if not predictions:
            print("❌ Nenhuma predição gerada")
            return False
        
        print(f"🔮 {len(predictions)} predições geradas")
        
        # 3. Formatar mensagem
        message = self.format_telegram_message(predictions)
        
        # 4. Salvar mensagem em arquivo
        print("💾 Salvando mensagem para demonstração...")
        if self.save_message_to_file(message):
            print("✅ Mensagem formatada e salva!")
        
        # 5. Mostrar preview da mensagem
        print("\n📱 PREVIEW DA MENSAGEM TELEGRAM:")
        print("=" * 80)
        print(message)
        
        # 6. Instruções para configuração
        print("\n🔧 INSTRUÇÕES PARA CONFIGURAR TELEGRAM:")
        print("=" * 80)
        print("1. Crie um bot no Telegram com @BotFather")
        print("2. Obtenha o token do bot")
        print("3. Envie uma mensagem para o bot")
        print("4. Execute: python setup_telegram_bot.py")
        print("5. Configure o token e chat ID")
        print("6. Execute: python send_predictions_telegram.py")
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        return True

def main():
    """Função principal"""
    demo = TelegramSimulatedDemo()
    return demo.run_demo()

if __name__ == "__main__":
    main()
