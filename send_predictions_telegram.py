#!/usr/bin/env python3
"""
Envio de Predições via Telegram
MaraBet AI - Envio automático de predições via Telegram
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

class TelegramPredictionsSender:
    """Enviador de predições via Telegram"""
    
    def __init__(self):
        self.api_key = "71b2b62386f2d1275cd3201a73e1e045"
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        
        # Configurações do Telegram (você precisa configurar)
        self.telegram_bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
        self.telegram_chat_id = "YOUR_TELEGRAM_CHAT_ID"
        self.telegram_api_url = f"https://api.telegram.org/bot{self.telegram_bot_token}"
    
    def get_telegram_chat_id(self):
        """Obtém o chat ID do Telegram"""
        logger.info("🔍 OBTENDO CHAT ID DO TELEGRAM")
        print("=" * 60)
        
        try:
            response = requests.get(f"{self.telegram_api_url}/getUpdates")
            if response.status_code == 200:
                data = response.json()
                updates = data.get('result', [])
                
                if updates:
                    chat_id = updates[-1]['message']['chat']['id']
                    logger.info(f"   Chat ID encontrado: {chat_id}")
                    return str(chat_id)
                else:
                    logger.warning("   Nenhuma mensagem encontrada. Envie uma mensagem para o bot primeiro.")
                    return None
            else:
                logger.error(f"   Erro ao obter updates: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"   Erro ao obter chat ID: {e}")
            return None
    
    def send_telegram_message(self, message):
        """Envia mensagem via Telegram"""
        try:
            url = f"{self.telegram_api_url}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data)
            if response.status_code == 200:
                logger.info("   Mensagem enviada com sucesso")
                return True
            else:
                logger.error(f"   Erro ao enviar mensagem: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"   Erro ao enviar mensagem: {e}")
            return False
    
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
    
    def send_predictions(self):
        """Envia predições via Telegram"""
        print("📱 ENVIANDO PREDIÇÕES VIA TELEGRAM - MARABET AI")
        print("=" * 80)
        
        # 1. Verificar configuração do Telegram
        if self.telegram_bot_token == "YOUR_TELEGRAM_BOT_TOKEN":
            print("❌ Token do bot Telegram não configurado!")
            print("   Configure o token do bot no arquivo de configuração")
            return False
        
        if self.telegram_chat_id == "YOUR_TELEGRAM_CHAT_ID":
            print("🔍 Obtendo Chat ID automaticamente...")
            chat_id = self.get_telegram_chat_id()
            if chat_id:
                self.telegram_chat_id = chat_id
            else:
                print("❌ Não foi possível obter o Chat ID")
                print("   Envie uma mensagem para o bot primeiro")
                return False
        
        # 2. Obter partidas
        today_matches = self.get_today_matches()
        upcoming_matches = self.get_upcoming_matches(3)
        
        all_matches = today_matches + upcoming_matches
        
        if not all_matches:
            print("❌ Nenhuma partida encontrada")
            return False
        
        print(f"📊 {len(all_matches)} partidas encontradas")
        
        # 3. Gerar predições
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
        
        # 4. Formatar mensagem
        message = self.format_telegram_message(predictions)
        
        # 5. Enviar via Telegram
        print("📤 Enviando predições via Telegram...")
        success = self.send_telegram_message(message)
        
        if success:
            print("✅ Predições enviadas com sucesso!")
            return True
        else:
            print("❌ Erro ao enviar predições")
            return False

def main():
    """Função principal"""
    sender = TelegramPredictionsSender()
    return sender.send_predictions()

if __name__ == "__main__":
    main()
