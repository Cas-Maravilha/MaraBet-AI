#!/usr/bin/env python3
"""
Teste rápido de partidas futuras da API-Football
"""
import requests
from datetime import datetime, timedelta

API_KEY = "71b2b62386f2d1275cd3201a73e1e045"
headers = {'x-apisports-key': API_KEY}
base_url = 'https://v3.football.api-sports.io'

print("🔍 TESTANDO PARTIDAS FUTURAS - PRÓXIMOS 7 DIAS")
print("=" * 80)

for i in range(7):
    date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
    date_str = (datetime.now() + timedelta(days=i)).strftime('%d/%m/%Y')
    
    try:
        response = requests.get(
            f'{base_url}/fixtures',
            headers=headers,
            params={'date': date, 'status': 'NS'},
            timeout=10
        )
        
        if response.status_code == 200:
            matches = response.json().get('response', [])
            count = len(matches)
            
            if count > 0:
                print(f"✅ {date_str} ({date}): {count} partidas futuras")
                
                # Mostrar primeiras 3
                for j, match in enumerate(matches[:3], 1):
                    teams = match['teams']
                    league = match['league']
                    fixture = match['fixture']
                    
                    home = teams['home']['name']
                    away = teams['away']['name']
                    
                    try:
                        match_time = datetime.fromisoformat(fixture['date'].replace('Z', '+00:00'))
                        time_str = match_time.strftime('%H:%M')
                    except:
                        time_str = "N/A"
                    
                    print(f"   {j}. {home} vs {away} - {league['name']} ({time_str})")
                    
                if count > 3:
                    print(f"   ... e mais {count - 3} partidas")
                print()
            else:
                print(f"❌ {date_str}: Nenhuma partida")
        else:
            print(f"⚠️ {date_str}: Erro {response.status_code}")
    
    except Exception as e:
        print(f"❌ {date_str}: Erro - {e}")

print("\n" + "=" * 80)
print("✅ TESTE CONCLUÍDO")

