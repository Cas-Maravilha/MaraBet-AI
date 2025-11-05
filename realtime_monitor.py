#!/usr/bin/env python3
"""
Sistema de Monitoramento em Tempo Real MaraBet AI
Monitora dados coletados e gera alertas baseados em mudanças significativas
"""

import json
import os
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging
import threading
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTimeMonitor:
    """Monitor em tempo real dos dados coletados"""
    
    def __init__(self):
        self.db_path = "marabet_data.db"
        self.config_file = "telegram_config.json"
        self.config = self.load_config()
        self.base_url = f"https://api.telegram.org/bot{self.config.get('telegram_bot_token', '')}"
        
        # Thresholds para alertas
        self.odds_change_threshold = 0.15  # 15% de mudança nas odds
        self.injury_alert_threshold = 2    # 2+ lesões importantes
        self.weather_alert_threshold = 0.7  # 70% de chance de chuva
        
    def load_config(self):
        """Carrega configuração do Telegram"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def send_alert(self, message, parse_mode='Markdown'):
        """Envia alerta para o Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.config.get('telegram_chat_id'),
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info("🚨 Alerta de monitoramento enviado!")
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao enviar alerta: {e}")
            return False
    
    def monitor_odds_changes(self):
        """Monitora mudanças significativas nas odds"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar odds recentes (últimas 2 horas)
        cursor.execute('''
            SELECT match_id, market_type, odds, timestamp
            FROM odds_history
            WHERE timestamp >= datetime('now', '-2 hours')
            ORDER BY match_id, market_type, timestamp DESC
        ''')
        
        recent_odds = cursor.fetchall()
        conn.close()
        
        # Agrupar por partida e mercado
        odds_by_match = {}
        for match_id, market_type, odds, timestamp in recent_odds:
            if match_id not in odds_by_match:
                odds_by_match[match_id] = {}
            if market_type not in odds_by_match[match_id]:
                odds_by_match[match_id][market_type] = []
            odds_by_match[match_id][market_type].append((odds, timestamp))
        
        # Verificar mudanças significativas
        for match_id, markets in odds_by_match.items():
            for market_type, odds_history in markets.items():
                if len(odds_history) >= 2:
                    current_odds = odds_history[0][0]
                    previous_odds = odds_history[1][0]
                    
                    change_percent = abs(current_odds - previous_odds) / previous_odds
                    
                    if change_percent >= self.odds_change_threshold:
                        self._send_odds_alert(match_id, market_type, current_odds, previous_odds, change_percent)
    
    def monitor_injury_updates(self):
        """Monitora atualizações de lesões importantes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar partidas com lesões recentes
        cursor.execute('''
            SELECT match_id, home_team, away_team, injuries, updated_at
            FROM matches
            WHERE updated_at >= datetime('now', '-1 hour')
            AND injuries != '[]'
        ''')
        
        matches_with_injuries = cursor.fetchall()
        conn.close()
        
        for match_id, home_team, away_team, injuries_json, updated_at in matches_with_injuries:
            injuries = json.loads(injuries_json)
            
            # Contar lesões importantes
            important_injuries = [inj for inj in injuries if inj.get('severity') in ['Moderada', 'Grave']]
            
            if len(important_injuries) >= self.injury_alert_threshold:
                self._send_injury_alert(match_id, home_team, away_team, important_injuries)
    
    def monitor_weather_changes(self):
        """Monitora mudanças meteorológicas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar partidas com clima adverso
        cursor.execute('''
            SELECT match_id, home_team, away_team, weather, match_date
            FROM matches
            WHERE match_date BETWEEN datetime('now') AND datetime('now', '+2 days')
        ''')
        
        upcoming_matches = cursor.fetchall()
        conn.close()
        
        for match_id, home_team, away_team, weather_json, match_date in upcoming_matches:
            weather = json.loads(weather_json)
            
            # Verificar condições adversas
            if weather.get('condition') in ['Chuvoso', 'Tempestade', 'Nevando']:
                self._send_weather_alert(match_id, home_team, away_team, weather, match_date)
    
    def monitor_team_form_changes(self):
        """Monitora mudanças na forma das equipes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar equipes com mudanças recentes
        cursor.execute('''
            SELECT team_id, name, league, form_last_5, last_updated
            FROM teams
            WHERE last_updated >= datetime('now', '-6 hours')
        ''')
        
        teams_updated = cursor.fetchall()
        conn.close()
        
        for team_id, name, league, form_json, last_updated in teams_updated:
            form = json.loads(form_json)
            
            # Verificar forma ruim (3+ derrotas nos últimos 5)
            losses = form.count('L')
            if losses >= 3:
                self._send_form_alert(team_id, name, league, form)
    
    def _send_odds_alert(self, match_id: str, market_type: str, current_odds: float, previous_odds: float, change_percent: float):
        """Envia alerta de mudança nas odds"""
        direction = "📈" if current_odds > previous_odds else "📉"
        
        message = f"⚡ *ALERTA DE ODDS MARABET AI*\n\n"
        message += f"🏆 *Partida:* {match_id}\n"
        message += f"📊 *Mercado:* {market_type}\n"
        message += f"{direction} *Mudança:* {change_percent:.1%}\n"
        message += f"💰 *Odds anterior:* {previous_odds:.2f}\n"
        message += f"💰 *Odds atual:* {current_odds:.2f}\n\n"
        
        if change_percent > 0.20:
            message += f"🚨 *ALERTA CRÍTICO:* Mudança significativa detectada!\n"
        elif change_percent > 0.15:
            message += f"⚠️ *ATENÇÃO:* Mudança importante nas odds\n"
        
        message += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        message += f"🤖 *Sistema MaraBet AI - Monitoramento 24/7*"
        
        self.send_alert(message)
    
    def _send_injury_alert(self, match_id: str, home_team: str, away_team: str, injuries: List[Dict]):
        """Envia alerta de lesões importantes"""
        message = f"🏥 *ALERTA DE LESÕES MARABET AI*\n\n"
        message += f"🏆 *Partida:* {home_team} vs {away_team}\n"
        message += f"⚠️ *Lesões importantes:* {len(injuries)}\n\n"
        
        message += f"📋 *Detalhes das lesões:*\n"
        for injury in injuries[:3]:  # Mostrar apenas as 3 primeiras
            severity_emoji = "🔴" if injury['severity'] == 'Grave' else "🟡" if injury['severity'] == 'Moderada' else "🟢"
            message += f"• {severity_emoji} {injury['player']} ({injury['position']})\n"
            message += f"  Tipo: {injury['injury_type']}\n"
            message += f"  Retorno: {injury['expected_return']} dias\n\n"
        
        if len(injuries) > 3:
            message += f"... e mais {len(injuries) - 3} lesões\n\n"
        
        message += f"💡 *Impacto:* Pode afetar as probabilidades da partida\n"
        message += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        message += f"🤖 *Sistema MaraBet AI - Monitoramento 24/7*"
        
        self.send_alert(message)
    
    def _send_weather_alert(self, match_id: str, home_team: str, away_team: str, weather: Dict, match_date: str):
        """Envia alerta meteorológico"""
        condition_emoji = {
            'Chuvoso': '🌧️',
            'Tempestade': '⛈️',
            'Nevando': '❄️',
            'Nublado': '☁️',
            'Ensolarado': '☀️'
        }
        
        emoji = condition_emoji.get(weather.get('condition', ''), '🌤️')
        
        message = f"{emoji} *ALERTA METEOROLÓGICO MARABET AI*\n\n"
        message += f"🏆 *Partida:* {home_team} vs {away_team}\n"
        message += f"📅 *Data:* {match_date[:10]}\n\n"
        
        message += f"🌤️ *Condições:*\n"
        message += f"• Clima: {weather.get('condition', 'N/A')}\n"
        message += f"• Temperatura: {weather.get('temperature', 'N/A')}°C\n"
        message += f"• Umidade: {weather.get('humidity', 'N/A')}%\n"
        message += f"• Vento: {weather.get('wind_speed', 'N/A')} km/h\n"
        message += f"• Precipitação: {weather.get('precipitation', 'N/A')}%\n\n"
        
        if weather.get('condition') in ['Chuvoso', 'Tempestade']:
            message += f"⚠️ *IMPACTO:* Condições adversas podem afetar:\n"
            message += f"• Qualidade do jogo\n"
            message += f"• Probabilidade de gols\n"
            message += f"• Mercados Over/Under\n\n"
        
        message += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        message += f"🤖 *Sistema MaraBet AI - Monitoramento 24/7*"
        
        self.send_alert(message)
    
    def _send_form_alert(self, team_id: str, name: str, league: str, form: List[str]):
        """Envia alerta de forma ruim"""
        losses = form.count('L')
        wins = form.count('W')
        draws = form.count('D')
        
        message = f"📉 *ALERTA DE FORMA MARABET AI*\n\n"
        message += f"⚽ *Equipe:* {name}\n"
        message += f"🏟️ *Liga:* {league}\n\n"
        
        message += f"📊 *Forma recente:* {' '.join(form)}\n"
        message += f"• Vitórias: {wins}\n"
        message += f"• Empates: {draws}\n"
        message += f"• Derrotas: {losses}\n\n"
        
        if losses >= 4:
            message += f"🚨 *CRÍTICO:* {losses} derrotas consecutivas!\n"
        elif losses >= 3:
            message += f"⚠️ *ATENÇÃO:* Forma preocupante\n"
        
        message += f"💡 *Impacto:* Pode afetar odds e probabilidades\n"
        message += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        message += f"🤖 *Sistema MaraBet AI - Monitoramento 24/7*"
        
        self.send_alert(message)
    
    def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        logger.info("🚀 Iniciando monitoramento em tempo real...")
        
        while True:
            try:
                logger.info("🔍 Executando verificações de monitoramento...")
                
                # Executar verificações
                self.monitor_odds_changes()
                time.sleep(5)
                
                self.monitor_injury_updates()
                time.sleep(5)
                
                self.monitor_weather_changes()
                time.sleep(5)
                
                self.monitor_team_form_changes()
                
                logger.info("✅ Verificações de monitoramento concluídas")
                time.sleep(300)  # Aguardar 5 minutos antes da próxima verificação
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(60)

def main():
    monitor = RealTimeMonitor()
    
    print("🎯 MARABET AI - SISTEMA DE MONITORAMENTO EM TEMPO REAL")
    print("=" * 60)
    
    print("\n📊 Iniciando monitoramento...")
    print("⚠️ Pressione Ctrl+C para parar")
    
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
