#!/usr/bin/env python3
"""
Envio Automático de Predições Futuras via Telegram
MaraBet AI - Sistema automático com dados reais da API Football
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
import schedule

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoTelegramPredictions:
    """Sistema automático de predições futuras via Telegram"""
    
    def __init__(self):
        self.api_key = "71b2b62386f2d1275cd3201a73e1e045"
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        
        # Configurações do Telegram (configurar via setup)
        self.telegram_bot_token = None
        self.telegram_chat_id = None
        self.telegram_api_url = None
        
        # Configurações do sistema
        self.check_interval_hours = 6  # Verificar a cada 6 horas
        self.days_ahead = 7  # Próximos 7 dias
        self.max_predictions = 5  # Máximo de predições por envio
        
        # Controle de envios
        self.last_sent_matches = set()
        self.sent_today = 0
        self.max_sends_per_day = 3
        
    def load_telegram_config(self):
        """Carrega configuração do Telegram"""
        try:
            if os.path.exists('telegram_config.json'):
                with open('telegram_config.json', 'r') as f:
                    config = json.load(f)
                    self.telegram_bot_token = config.get('telegram_bot_token')
                    self.telegram_chat_id = config.get('telegram_chat_id')
                    self.telegram_api_url = f"https://api.telegram.org/bot{self.telegram_bot_token}"
                    logger.info("✅ Configuração do Telegram carregada")
                    return True
            else:
                logger.error("❌ Arquivo telegram_config.json não encontrado")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configuração: {e}")
            return False
    
    def get_future_matches(self):
        """Obtém partidas FUTURAS do Brasileirão"""
        logger.info(f"📅 OBTENDO PARTIDAS FUTURAS (PRÓXIMOS {self.days_ahead} DIAS)")
        
        try:
            # Data de hoje
            today = datetime.now().strftime('%Y-%m-%d')
            # Data futura
            future_date = (datetime.now() + timedelta(days=self.days_ahead)).strftime('%Y-%m-%d')
            
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={
                    'from': today,
                    'to': future_date,
                    'league': 71,  # Brasileirão
                    'season': 2024,
                    'status': 'NS'  # NS = Not Started (não iniciadas)
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('response', [])
                
                # Filtrar apenas partidas que ainda não começaram
                future_matches = []
                for match in matches:
                    match_date = datetime.fromisoformat(match['fixture']['date'].replace('Z', '+00:00'))
                    if match_date > datetime.now():
                        future_matches.append(match)
                
                logger.info(f"   {len(future_matches)} partidas futuras encontradas")
                return future_matches
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"   Erro ao buscar partidas futuras: {e}")
            return []
    
    def get_team_form(self, team_id, last_matches=10):
        """Obtém forma recente de um time (últimos jogos já finalizados)"""
        try:
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={
                    'team': team_id,
                    'last': last_matches,
                    'status': 'FT'  # FT = Finished (finalizadas)
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
        """Calcula força de um time baseada em partidas já finalizadas"""
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
        
        # Calcular força combinada (mais sofisticada)
        strength = (
            win_rate * 0.4 +           # Taxa de vitórias
            draw_rate * 0.1 +          # Taxa de empates
            min(avg_goals_for / 3, 1) * 0.25 +    # Ataque
            max(1 - avg_goals_against / 3, 0) * 0.25  # Defesa
        )
        
        return min(max(strength, 0.1), 0.9)
    
    def predict_future_match(self, match):
        """Prediz resultado de uma partida FUTURA"""
        home_team = match['teams']['home']['name']
        away_team = match['teams']['away']['name']
        home_id = match['teams']['home']['id']
        away_id = match['teams']['away']['id']
        match_date = datetime.fromisoformat(match['fixture']['date'].replace('Z', '+00:00'))
        
        logger.info(f"🔮 PREDIZENDO: {home_team} vs {away_team} ({match_date.strftime('%d/%m/%Y %H:%M')})")
        
        # Obter forma recente dos times (apenas jogos já finalizados)
        home_form = self.get_team_form(home_id, 10)
        away_form = self.get_team_form(away_id, 10)
        
        # Calcular força dos times
        home_strength = self.calculate_team_strength(home_form, is_home=True)
        away_strength = self.calculate_team_strength(away_form, is_home=False)
        
        # Fator casa (vantagem do time da casa)
        home_advantage = 0.12
        
        # Fator de confiabilidade baseado na quantidade de dados
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
        
        # Ajustar confiança baseada na confiabilidade dos dados
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
            'date_formatted': match_date.strftime('%d/%m/%Y %H:%M'),
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
    
    def format_telegram_message(self, predictions):
        """Formata mensagem para o Telegram"""
        if not predictions:
            return "❌ Nenhuma partida futura encontrada no momento."
        
        message = f"🔮 <b>PREDIÇÕES FUTURAS - MARABET AI</b> 🔮\n"
        message += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        message += f"⚽ Partidas que ainda vão acontecer\n"
        message += f"🤖 Sistema automático com dados reais da API Football\n\n"
        
        for i, prediction in enumerate(predictions, 1):
            message += f"🏆 <b>Partida {i}:</b>\n"
            message += f"⚔️ {prediction['home_team']} vs {prediction['away_team']}\n"
            message += f"📅 {prediction['date_formatted']}\n"
            message += f"🏆 {prediction['league']}\n\n"
            
            message += f"🔮 <b>Predição:</b> {prediction['prediction']}\n"
            message += f"📊 <b>Confiança:</b> {prediction['confidence']:.1%}\n"
            message += f"🎯 <b>Confiabilidade:</b> {prediction['reliability']:.1%}\n\n"
            
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
            
            # Dados de forma
            message += f"📊 <b>Dados de Forma:</b>\n"
            message += f"🏠 {prediction['home_team']}: {prediction['form_data']['home_games']} jogos analisados\n"
            message += f"✈️ {prediction['away_team']}: {prediction['form_data']['away_games']} jogos analisados\n"
            message += f"💪 Força: Casa {prediction['team_strengths']['home']:.2f} | Fora {prediction['team_strengths']['away']:.2f}\n\n"
            
            message += "─" * 30 + "\n\n"
        
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
        
        message += f"📊 <b>RESUMO DAS PREDIÇÕES FUTURAS:</b>\n"
        message += f"🔮 Predições: {len(predictions)}\n"
        message += f"📈 Confiança média: {avg_confidence:.1%}\n"
        message += f"🎯 Confiabilidade média: {avg_reliability:.1%}\n"
        message += f"💎 Apostas com valor: {positive_value_bets}/{len(predictions)}\n\n"
        
        message += f"⏰ <b>IMPORTANTE:</b> Estas são predições para partidas FUTURAS\n"
        message += f"🤖 <b>AUTOMÁTICO:</b> Enviado automaticamente pelo sistema\n"
        message += f"⚠️ <b>AVISO:</b> Apostas envolvem risco. Use com responsabilidade.\n"
        message += f"🤖 Powered by MaraBet AI - Sistema de IA para Futebol"
        
        return message
    
    def send_telegram_message(self, message):
        """Envia mensagem via Telegram"""
        try:
            url = f"{self.telegram_api_url}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Mensagem enviada com sucesso")
                return True
            else:
                logger.error(f"❌ Erro ao enviar mensagem: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}")
            return False
    
    def check_and_send_predictions(self):
        """Verifica e envia predições se houver partidas futuras"""
        logger.info("🔍 VERIFICANDO PARTIDAS FUTURAS...")
        
        # Verificar limite diário
        if self.sent_today >= self.max_sends_per_day:
            logger.info(f"⏰ Limite diário atingido ({self.max_sends_per_day} envios)")
            return
        
        # Obter partidas futuras
        future_matches = self.get_future_matches()
        
        if not future_matches:
            logger.info("❌ Nenhuma partida futura encontrada")
            return
        
        # Filtrar partidas não enviadas
        new_matches = []
        for match in future_matches:
            match_id = match['fixture']['id']
            if match_id not in self.last_sent_matches:
                new_matches.append(match)
        
        if not new_matches:
            logger.info("❌ Nenhuma partida nova para enviar")
            return
        
        # Limitar número de predições
        matches_to_predict = new_matches[:self.max_predictions]
        
        # Gerar predições
        predictions = []
        for match in matches_to_predict:
            try:
                prediction = self.predict_future_match(match)
                predictions.append(prediction)
                self.last_sent_matches.add(match['fixture']['id'])
            except Exception as e:
                logger.error(f"❌ Erro ao predizer partida: {e}")
                continue
        
        if not predictions:
            logger.info("❌ Nenhuma predição gerada")
            return
        
        # Formatar e enviar mensagem
        message = self.format_telegram_message(predictions)
        
        logger.info(f"📤 Enviando {len(predictions)} predições via Telegram...")
        success = self.send_telegram_message(message)
        
        if success:
            self.sent_today += 1
            logger.info(f"✅ Predições enviadas com sucesso! (Envio {self.sent_today}/{self.max_sends_per_day})")
        else:
            logger.error("❌ Erro ao enviar predições")
    
    def reset_daily_counter(self):
        """Reseta contador diário"""
        self.sent_today = 0
        self.last_sent_matches.clear()
        logger.info("🔄 Contador diário resetado")
    
    def start_automation(self):
        """Inicia automação do sistema"""
        print("🤖 SISTEMA AUTOMÁTICO DE PREDIÇÕES FUTURAS - MARABET AI")
        print("=" * 80)
        
        # Carregar configuração do Telegram
        if not self.load_telegram_config():
            print("❌ Configuração do Telegram não encontrada!")
            print("   Execute: python setup_telegram_bot.py")
            return False
        
        print("✅ Configuração do Telegram carregada")
        print(f"📅 Verificando a cada {self.check_interval_hours} horas")
        print(f"📊 Próximos {self.days_ahead} dias")
        print(f"🔢 Máximo {self.max_predictions} predições por envio")
        print(f"📤 Máximo {self.max_sends_per_day} envios por dia")
        
        # Agendar verificações
        schedule.every(self.check_interval_hours).hours.do(self.check_and_send_predictions)
        schedule.every().day.at("00:00").do(self.reset_daily_counter)
        
        # Verificação inicial
        self.check_and_send_predictions()
        
        print("\n🔄 SISTEMA AUTOMÁTICO INICIADO!")
        print("   Pressione Ctrl+C para parar")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        except KeyboardInterrupt:
            print("\n🛑 Sistema automático parado pelo usuário")
            return True

def main():
    """Função principal"""
    auto_system = AutoTelegramPredictions()
    return auto_system.start_automation()

if __name__ == "__main__":
    main()
