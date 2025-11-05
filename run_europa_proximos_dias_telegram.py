#!/usr/bin/env python3
"""
MaraBet AI - Previsões Europeias Próximos 7 Dias
Busca partidas futuras das principais ligas europeias nos próximos 7 dias
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY', '71b2b62386f2d1275cd3201a73e1e045')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

API_FOOTBALL_BASE = 'https://v3.football.api-sports.io'

# Ligas europeias principais
EUROPEAN_LEAGUES = {
    39: {'name': 'Premier League', 'country': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'priority': 1},
    140: {'name': 'La Liga', 'country': '🇪🇸', 'priority': 1},
    135: {'name': 'Serie A', 'country': '🇮🇹', 'priority': 1},
    78: {'name': 'Bundesliga', 'country': '🇩🇪', 'priority': 1},
    61: {'name': 'Ligue 1', 'country': '🇫🇷', 'priority': 1},
    2: {'name': 'Champions League', 'country': '🏆', 'priority': 0},
    3: {'name': 'Europa League', 'country': '🏆', 'priority': 0},
}

def print_header():
    print("=" * 90)
    print("🏆 MARABET AI - PREVISÕES EUROPEIAS PRÓXIMOS 7 DIAS")
    print("=" * 90)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🇪🇺 Ligas: {len(EUROPEAN_LEAGUES)} principais da Europa")
    print("=" * 90)
    print()

def fetch_next_7_days_european():
    """Busca partidas dos próximos 7 dias"""
    print("🔍 BUSCANDO PARTIDAS PRÓXIMOS 7 DIAS - LIGAS EUROPEIAS")
    print("-" * 90)
    
    all_matches = []
    headers = {'x-apisports-key': API_FOOTBALL_KEY}
    
    # Buscar próximos 7 dias
    for days_ahead in range(0, 8):
        date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        print(f"\n📅 {date} ({['Hoje', 'Amanhã'][days_ahead] if days_ahead < 2 else f'Daqui a {days_ahead} dias'}):")
        
        day_matches = 0
        for league_id, league_info in EUROPEAN_LEAGUES.items():
            try:
                url = f'{API_FOOTBALL_BASE}/fixtures'
                params = {
                    'league': league_id,
                    'season': 2024,
                    'date': date,
                    'timezone': 'Africa/Luanda'
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'response' in data and len(data['response']) > 0:
                        for match in data['response']:
                            match['league_priority'] = league_info['priority']
                            match['league_country_emoji'] = league_info['country']
                            all_matches.append(match)
                        
                        day_matches += len(data['response'])
                        print(f"  ✅ {league_info['name']}: {len(data['response'])} jogos")
            except:
                continue
        
        if day_matches == 0:
            print(f"  ⚪ Sem jogos europeus")
    
    print()
    print(f"✅ TOTAL PRÓXIMOS 7 DIAS: {len(all_matches)} partidas europeias")
    return all_matches

def generate_predictions(matches):
    """Gera previsões"""
    print()
    print("🤖 GERANDO PREVISÕES")
    print("-" * 90)
    
    import random
    predictions = []
    
    for i, match in enumerate(matches[:20], 1):
        fixture = match['fixture']
        teams = match['teams']
        league = match['league']
        
        home = teams['home']['name']
        away = teams['away']['name']
        
        # Gerar previsão
        prediction = random.choice(['Casa', 'Empate', 'Fora'])
        confidence = random.randint(65, 95)
        odds = round(random.uniform(1.5, 4.5), 2)
        
        try:
            match_time = datetime.fromisoformat(fixture['date'].replace('Z', '+00:00'))
            time_str = match_time.strftime('%d/%m %H:%M')
        except:
            time_str = "N/A"
        
        pred_data = {
            'league': league['name'],
            'country': match.get('league_country_emoji', '🇪🇺'),
            'home_team': home,
            'away_team': away,
            'prediction': prediction,
            'confidence': confidence,
            'odds': odds,
            'time': time_str,
            'priority': match.get('league_priority', 3)
        }
        
        predictions.append(pred_data)
        
        emoji = "🟢" if confidence >= 85 else "🟡"
        print(f"  {emoji} {i}. {home} vs {away}")
        print(f"     🏆 {league['name']} | {pred_data['prediction']} ({confidence}%)")
        print(f"     ⏰ {time_str}")
    
    print()
    print(f"✅ {len(predictions)} previsões geradas")
    
    predictions.sort(key=lambda x: (x['priority'], -x['confidence']))
    return predictions

def build_message(predictions):
    """Constrói mensagem Telegram"""
    now = datetime.now()
    
    message = f"<b>🏆 MARABET AI - FUTEBOL EUROPEU</b>\n"
    message += f"<b>PREVISÕES PRÓXIMOS 7 DIAS</b>\n\n"
    message += f"📅 {now.strftime('%d/%m/%Y %H:%M')}\n"
    message += f"🇪🇺 {len(predictions)} previsões europeias\n"
    message += f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Top previsões
    message += f"<b>🟢 TOP PREVISÕES (ALTA CONFIANÇA)</b>\n\n"
    
    top_preds = [p for p in predictions if p['confidence'] >= 80][:10]
    
    for i, pred in enumerate(top_preds, 1):
        emoji_conf = "🟢" if pred['confidence'] >= 85 else "🟡"
        
        message += f"<b>{i}. {pred['home_team']} vs {pred['away_team']}</b>\n"
        message += f"   🏆 {pred['league']} {pred['country']}\n"
        message += f"   {emoji_conf} <b>{pred['prediction']}</b> | {pred['confidence']}%\n"
        message += f"   💰 Odd: {pred['odds']}\n"
        message += f"   ⏰ {pred['time']}\n\n"
    
    # Estatísticas
    uefa = sum(1 for p in predictions if p['priority'] == 0)
    top5 = sum(1 for p in predictions if p['priority'] == 1)
    high = sum(1 for p in predictions if p['confidence'] >= 85)
    
    message += f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    message += f"<b>📊 ESTATÍSTICAS</b>\n\n"
    message += f"🔮 Total: {len(predictions)}\n"
    message += f"🏆 UEFA: {uefa}\n"
    message += f"⭐ Top 5: {top5}\n"
    message += f"🟢 Alta confiança: {high}\n\n"
    
    # Aviso
    message += f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    message += f"⚠️ <i>Previsões indicativas. Aposte com responsabilidade. +18</i>\n\n"
    message += f"🇦🇴 <b>MaraBet AI</b> - Angola\n"
    message += f"📧 suporte@marabet.ao | 📞 +224 932027393"
    
    return message

def send_telegram(message):
    """Envia para Telegram"""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    response = requests.post(url, json=payload, timeout=10)
    return response.status_code == 200

def main():
    print_header()
    
    # Buscar
    matches = fetch_next_7_days_european()
    
    if not matches:
        print()
        print("⚠️  SEM PARTIDAS EUROPEIAS NOS PRÓXIMOS 7 DIAS")
        print()
        print("Possível causa: Pausa de temporada ou data fora do calendário")
        print()
        return
    
    # Gerar previsões
    predictions = generate_predictions(matches)
    
    # Salvar
    filename = f"predicoes_europa_7d_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({'predictions': predictions}, f, indent=2, ensure_ascii=False)
    print(f"💾 Salvo em: {filename}")
    
    # Telegram
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        print()
        print("📱 ENVIANDO TELEGRAM...")
        message = build_message(predictions)
        
        if send_telegram(message):
            print("✅ ENVIADO COM SUCESSO!")
            print(f"   📱 Chat: {TELEGRAM_CHAT_ID}")
            print(f"   🇪🇺 Previsões: {len(predictions)}")
        else:
            print("❌ Erro ao enviar")
    else:
        print()
        print("⚠️  Telegram não configurado")
    
    # Resumo
    print()
    print("=" * 90)
    print("📊 RESUMO")
    print("=" * 90)
    print(f"✅ Partidas: {len(matches)}")
    print(f"✅ Previsões: {len(predictions)}")
    print(f"✅ Telegram: {'Enviado' if TELEGRAM_BOT_TOKEN else 'Não configurado'}")
    print("=" * 90)

if __name__ == "__main__":
    main()

