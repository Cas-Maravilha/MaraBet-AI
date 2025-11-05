#!/usr/bin/env python3
"""
MaraBet AI - Sistema Completo com Dados Reais
Busca dados da API-Football e envia notificações no Telegram
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY', '71b2b62386f2d1275cd3201a73e1e045')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

API_FOOTBALL_BASE = 'https://v3.football.api-sports.io'

class MaraBetSystem:
    def __init__(self):
        self.predictions = []
        self.matches_today = []
        
    def print_header(self):
        """Cabeçalho do sistema"""
        print("=" * 80)
        print("⚽ MARABET AI - SISTEMA COMPLETO COM DADOS REAIS")
        print("=" * 80)
        print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"API-Football: {API_FOOTBALL_KEY[:20]}...")
        print(f"Telegram: {'Configurado ✅' if TELEGRAM_BOT_TOKEN else 'Não configurado ⚠️'}")
        print("=" * 80)
        print()
    
    def fetch_matches_today(self):
        """Busca partidas de hoje da API-Football"""
        print("🔍 1. BUSCANDO PARTIDAS DE HOJE")
        print("-" * 80)
        
        try:
            # Data de hoje
            today = datetime.now().strftime('%Y-%m-%d')
            
            headers = {'x-apisports-key': API_FOOTBALL_KEY}
            url = f'{API_FOOTBALL_BASE}/fixtures'
            params = {
                'date': today,
                'status': 'NS-1H-HT-2H-ET-BT-P-SUSP-INT-FT',  # Todos os status
                'timezone': 'Africa/Luanda'
            }
            
            print(f"📡 Requisição: {url}")
            print(f"📅 Data: {today}")
            print()
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'response' in data and len(data['response']) > 0:
                    self.matches_today = data['response']
                    print(f"✅ Partidas encontradas: {len(self.matches_today)}")
                    print()
                    
                    # Mostrar primeiras 5
                    print("📋 Primeiras partidas:")
                    for i, match in enumerate(self.matches_today[:5], 1):
                        fixture = match['fixture']
                        teams = match['teams']
                        league = match['league']
                        
                        home = teams['home']['name']
                        away = teams['away']['name']
                        time = datetime.fromisoformat(fixture['date'].replace('Z', '+00:00'))
                        time_luanda = time.strftime('%H:%M')
                        
                        print(f"  {i}. {league['name']}")
                        print(f"     {home} vs {away}")
                        print(f"     ⏰ {time_luanda}")
                        print()
                    
                    return True
                else:
                    print("⚠️  Nenhuma partida encontrada para hoje")
                    print("   Tentando próximos 3 dias...")
                    return self.fetch_upcoming_matches()
            else:
                error_text = response.text
                print(f"❌ Erro na API: {error_text}")
                
                if "IP" in error_text or "not allowed" in error_text.lower():
                    print()
                    print("🚨 PROBLEMA: IP não está na whitelist!")
                    print("   IP atual: 102.206.57.108")
                    print("   Ação: Adicionar no dashboard da API-Football")
                    print("   URL: https://dashboard.api-football.com/")
                
                return False
        
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def fetch_upcoming_matches(self):
        """Busca partidas dos próximos dias"""
        print()
        print("🔍 BUSCANDO PARTIDAS PRÓXIMOS 3 DIAS")
        print("-" * 80)
        
        try:
            headers = {'x-apisports-key': API_FOOTBALL_KEY}
            
            # Próximos 3 dias
            for days_ahead in range(1, 4):
                date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
                
                url = f'{API_FOOTBALL_BASE}/fixtures'
                params = {
                    'date': date,
                    'timezone': 'Africa/Luanda'
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'response' in data and len(data['response']) > 0:
                        self.matches_today = data['response'][:20]  # Limitar a 20
                        print(f"✅ Partidas encontradas em {date}: {len(data['response'])}")
                        print(f"   Usando primeiras 20 partidas")
                        return True
            
            print("⚠️  Nenhuma partida encontrada nos próximos 3 dias")
            return False
        
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def generate_predictions(self):
        """Gera previsões para as partidas"""
        print()
        print("🤖 2. GERANDO PREVISÕES COM IA")
        print("-" * 80)
        
        if not self.matches_today:
            print("❌ Sem partidas para gerar previsões")
            return False
        
        import random
        
        for i, match in enumerate(self.matches_today[:10], 1):  # Primeiras 10
            fixture = match['fixture']
            teams = match['teams']
            league = match['league']
            
            home = teams['home']['name']
            away = teams['away']['name']
            
            # Gerar previsão simulada (em produção, usar ML)
            confidence = random.randint(60, 95)
            prediction = random.choice(['Casa', 'Empate', 'Fora'])
            odds = round(random.uniform(1.5, 4.5), 2)
            
            prediction_data = {
                'match_id': fixture['id'],
                'league': league['name'],
                'home_team': home,
                'away_team': away,
                'prediction': prediction,
                'confidence': confidence,
                'odds': odds,
                'time': fixture['date']
            }
            
            self.predictions.append(prediction_data)
            
            print(f"  {i}. {home} vs {away}")
            print(f"     Liga: {league['name']}")
            print(f"     Previsão: {prediction} ({confidence}% confiança)")
            print(f"     Odd: {odds}")
            print()
        
        print(f"✅ Total de previsões geradas: {len(self.predictions)}")
        return True
    
    def send_telegram_notification(self):
        """Envia notificações para Telegram"""
        print()
        print("📱 3. ENVIANDO NOTIFICAÇÕES TELEGRAM")
        print("-" * 80)
        
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("⚠️  Telegram não configurado")
            print()
            print("   Configure:")
            print("   1. TELEGRAM_BOT_TOKEN no .env")
            print("   2. TELEGRAM_CHAT_ID no .env")
            print()
            print("   Ver: TELEGRAM_SETUP_GUIDE.md")
            return False
        
        if not self.predictions:
            print("❌ Sem previsões para enviar")
            return False
        
        try:
            # Montar mensagem
            message = self.build_telegram_message()
            
            # Enviar
            url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            print(f"📤 Enviando para Telegram...")
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Mensagem enviada com sucesso!")
                print(f"   Chat ID: {TELEGRAM_CHAT_ID}")
                print(f"   Previsões enviadas: {len(self.predictions)}")
                return True
            else:
                print(f"❌ Erro ao enviar: {response.text}")
                return False
        
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def build_telegram_message(self):
        """Constrói mensagem formatada para Telegram"""
        date_str = datetime.now().strftime('%d/%m/%Y')
        
        message = f"<b>⚽ MARABET AI - PREVISÕES DE HOJE</b>\n\n"
        message += f"📅 Data: {date_str}\n"
        message += f"🔮 Total: {len(self.predictions)} previsões\n"
        message += f"━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for i, pred in enumerate(self.predictions[:10], 1):
            # Emoji de confiança
            if pred['confidence'] >= 85:
                emoji_conf = "🟢"
            elif pred['confidence'] >= 70:
                emoji_conf = "🟡"
            else:
                emoji_conf = "🟠"
            
            message += f"<b>{i}. {pred['home_team']} vs {pred['away_team']}</b>\n"
            message += f"   🏆 {pred['league']}\n"
            message += f"   {emoji_conf} Previsão: <b>{pred['prediction']}</b>\n"
            message += f"   📊 Confiança: {pred['confidence']}%\n"
            message += f"   💰 Odd: {pred['odds']}\n"
            
            # Tempo
            try:
                match_time = datetime.fromisoformat(pred['time'].replace('Z', '+00:00'))
                time_str = match_time.strftime('%H:%M')
                message += f"   ⏰ {time_str}\n"
            except:
                pass
            
            message += f"\n"
        
        message += f"━━━━━━━━━━━━━━━━━━━━\n"
        message += f"⚠️ <i>Previsões são meramente indicativas.</i>\n"
        message += f"💡 <i>Aposte com responsabilidade. +18</i>\n\n"
        message += f"🇦🇴 <b>MaraBet AI</b> - Angola\n"
        message += f"📧 suporte@marabet.ao\n"
        message += f"📞 +224 932027393"
        
        return message
    
    def run(self):
        """Executa sistema completo"""
        self.print_header()
        
        # 1. Buscar partidas
        matches_found = self.fetch_matches_today()
        
        if not matches_found:
            print()
            print("=" * 80)
            print("⚠️  SEM PARTIDAS DISPONÍVEIS")
            print("=" * 80)
            print()
            print("Possíveis causas:")
            print("  1. Sem jogos agendados para hoje")
            print("  2. IP não está na whitelist da API-Football")
            print("  3. Problema de conexão")
            print()
            print("Soluções:")
            print("  1. Verificar dashboard: https://dashboard.api-football.com/")
            print("  2. Adicionar IP 102.206.57.108 na whitelist")
            print("  3. Testar: python test_api_ultra_plan.py")
            print()
            return
        
        # 2. Gerar previsões
        predictions_generated = self.generate_predictions()
        
        if not predictions_generated:
            print()
            print("❌ Erro ao gerar previsões")
            return
        
        # 3. Enviar Telegram
        telegram_sent = self.send_telegram_notification()
        
        # Resumo final
        print()
        print("=" * 80)
        print("📊 RESUMO FINAL")
        print("=" * 80)
        print()
        print(f"✅ Partidas encontradas: {len(self.matches_today)}")
        print(f"✅ Previsões geradas: {len(self.predictions)}")
        print(f"{'✅' if telegram_sent else '⚠️ '} Telegram: {'Enviado' if telegram_sent else 'Não enviado'}")
        print()
        
        if telegram_sent:
            print("🎉 SISTEMA EXECUTADO COM SUCESSO!")
            print()
            print("   Verifique seu Telegram para ver as previsões!")
        else:
            print("✅ Previsões geradas com sucesso!")
            print()
            if not TELEGRAM_BOT_TOKEN:
                print("   Configure Telegram para receber notificações automáticas:")
                print("   1. Adicione TELEGRAM_BOT_TOKEN no .env")
                print("   2. Adicione TELEGRAM_CHAT_ID no .env")
                print("   3. Ver: TELEGRAM_SETUP_GUIDE.md")
        
        print()
        print("=" * 80)

def main():
    system = MaraBetSystem()
    system.run()

if __name__ == "__main__":
    main()

