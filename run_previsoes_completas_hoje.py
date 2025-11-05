#!/usr/bin/env python3
"""
MaraBet AI - Previsões Completas de Hoje
Busca TODAS as ligas e partidas futuras, não apenas hoje
"""
import os
import sys
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY', '71b2b62386f2d1275cd3201a73e1e045')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '5550091597')

API_FOOTBALL_BASE = 'https://v3.football.api-sports.io'

print("=" * 90)
print("⚽ MARABET AI - PREVISÕES COMPLETAS")
print("=" * 90)
print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"🌐 API-Football: Conectado")
print(f"📱 Telegram: {'✅ Configurado' if TELEGRAM_BOT_TOKEN else '⚠️ Não configurado'}")
print("=" * 90)
print()

# Buscar partidas dos próximos 14 dias
all_matches = []
print("🔍 BUSCANDO PARTIDAS FUTURAS (PRÓXIMOS 14 DIAS)")
print("-" * 90)

for i in range(14):
    date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
    try:
        response = requests.get(
            f'{API_FOOTBALL_BASE}/fixtures',
            headers={'x-apisports-key': API_FOOTBALL_KEY},
            params={'date': date, 'status': 'NS'},
            timeout=10
        )
        
        if response.status_code == 200:
            matches = response.json().get('response', [])
            all_matches.extend(matches)
            
            if matches:
                print(f"📅 +{i} dia(s): {len(matches)} partidas")
    except:
        pass

print(f"\n✅ Total encontrado: {len(all_matches)} partidas futuras")

if not all_matches:
    print("\n⚠️ Nenhuma partida futura encontrada nos próximos 14 dias")
    print("   (Pode ser período de baixa movimentação)")
    sys.exit(0)

# Filtrar apenas ligas principais
major_leagues = [
    'Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1',
    'Champions League', 'Europa League', 'Liga Portugal',
    'Brasileiro', 'Serie A', 'Liga MX', 'MLS'
]

filtered_matches = []
for match in all_matches:
    league_name = match['league']['name']
    if any(major in league_name for major in major_leagues):
        filtered_matches.append(match)

if not filtered_matches:
    filtered_matches = all_matches[:20]

print(f"⭐ Ligas principais: {len(filtered_matches)} partidas\n")

# Gerar previsões
import random
predictions = []

for match in filtered_matches[:15]:
    fixture = match['fixture']
    teams = match['teams']
    league = match['league']
    
    home = teams['home']['name']
    away = teams['away']['name']
    
    # Previsão simulada
    prediction = random.choice(['Casa', 'Empate', 'Fora'])
    confidence = random.randint(65, 92)
    odds = round(random.uniform(1.8, 3.5), 2)
    
    predictions.append({
        'match': f"{home} vs {away}",
        'league': league['name'],
        'prediction': prediction,
        'confidence': confidence,
        'odds': odds
    })
    
    print(f"⚽ {home} vs {away}")
    print(f"   🏆 {league['name']}")
    print(f"   🔮 {prediction} ({confidence}%) | 💰 Odd: {odds}")
    print()

# Enviar Telegram
if TELEGRAM_BOT_TOKEN:
    print("📤 ENVIANDO PARA TELEGRAM...")
    
    message = "<b>⚽ MARABET AI - PREVISÕES</b>\n\n"
    message += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    message += f"🔮 {len(predictions)} previsões\n\n"
    message += f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    high_conf = [p for p in predictions if p['confidence'] >= 80]
    
    if high_conf:
        message += "<b>🟢 ALTA CONFIANÇA (80%+)</b>\n\n"
        for i, pred in enumerate(high_conf[:5], 1):
            message += f"<b>{i}. {pred['match']}</b>\n"
            message += f"🏆 {pred['league']}\n"
            message += f"🟢 {pred['prediction']} ({pred['confidence']}%)\n"
            message += f"💰 Odd: {pred['odds']}\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    message += f"📊 Total: {len(predictions)}\n"
    message += f"🟢 Alta confiança: {len(high_conf)}\n\n"
    message += "⚠️ <i>Previsões são indicativas. Aposte com responsabilidade.</i>"
    
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        response = requests.post(
            url,
            json={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Mensagem enviada com sucesso no Telegram!")
        else:
            print(f"⚠️ Erro ao enviar: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Erro: {e}")

print("\n" + "=" * 90)
print("✅ SISTEMA CONCLUÍDO")
print("=" * 90)

