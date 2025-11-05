#!/usr/bin/env python3
"""
Demonstração de Envio de Predições via Telegram
MaraBet AI - Demo do sistema de envio via Telegram
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

class TelegramPredictionsDemo:
    """Demo do sistema de predições via Telegram"""
    
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
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={'date': today, 'league': 71},  # Brasileirão
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('response', [])
                logger.info(f"   {len(matches)} partidas do Brasileirão encontradas para hoje")
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
            return 0.5
        
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
        
        # Obter forma recente dos times
        home_form = self.get_team_form(home_id, 5)
        away_form = self.get_team_form(away_id, 5)
        
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
        message += f"🤖 Sistema de IA com dados reais da API Football\n\n"
        
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
    
    def save_message_to_file(self, message, filename="telegram_message.txt"):
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
        
        # 1. Obter partidas
        today_matches = self.get_today_matches()
        upcoming_matches = self.get_upcoming_matches(3)
        
        all_matches = today_matches + upcoming_matches
        
        if not all_matches:
            print("❌ Nenhuma partida encontrada")
            return False
        
        print(f"📊 {len(all_matches)} partidas encontradas")
        
        # 2. Gerar predições
        predictions = []
        for match in all_matches[:5]:  # Limitar a 5 partidas
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
    demo = TelegramPredictionsDemo()
    return demo.run_demo()

if __name__ == "__main__":
    main()
