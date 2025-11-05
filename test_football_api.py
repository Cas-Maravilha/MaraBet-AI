#!/usr/bin/env python3
"""
Script para testar a API-Football com a chave fornecida
"""

import requests
import json
from datetime import datetime

# Sua chave da API-Football - CONFIGURE NO ARQUIVO .env
import os
from dotenv import load_dotenv

load_dotenv()
API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY', '')
API_FOOTBALL_HOST = "v3.football.api-sports.io"

def test_api_connection():
    """Testa conexão com a API-Football"""
    print("⚽ MARABET AI - TESTE DA API-FOOTBALL")
    print("=" * 50)
    
    print(f"🔑 Chave: {API_FOOTBALL_KEY[:10]}...")
    print(f"🌐 Host: {API_FOOTBALL_HOST}")
    
    headers = {
        'x-rapidapi-host': API_FOOTBALL_HOST,
        'x-rapidapi-key': API_FOOTBALL_KEY
    }
    
    try:
        # Testar endpoint de status
        print("\n🔍 Testando conexão...")
        url = f"https://{API_FOOTBALL_HOST}/status"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Conexão estabelecida com sucesso!")
            print(f"📊 Status: {data.get('response', {}).get('account', 'N/A')}")
            print(f"📅 Data: {data.get('response', {}).get('requests', 'N/A')}")
        else:
            print(f"❌ Erro na conexão: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    
    return True

def test_leagues():
    """Testa endpoint de ligas"""
    print("\n🏆 Testando endpoint de ligas...")
    
    headers = {
        'x-rapidapi-host': API_FOOTBALL_HOST,
        'x-rapidapi-key': API_FOOTBALL_KEY
    }
    
    try:
        url = f"https://{API_FOOTBALL_HOST}/leagues"
        params = {'country': 'England', 'season': 2024}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            leagues = data.get('response', [])
            print(f"✅ Ligas encontradas: {len(leagues)}")
            
            if leagues:
                print("📋 Exemplos de ligas:")
                for league in leagues[:3]:
                    league_info = league.get('league', {})
                    print(f"  - {league_info.get('name', 'N/A')} (ID: {league_info.get('id', 'N/A')})")
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    return True

def test_fixtures():
    """Testa endpoint de partidas"""
    print("\n⚽ Testando endpoint de partidas...")
    
    headers = {
        'x-rapidapi-host': API_FOOTBALL_HOST,
        'x-rapidapi-key': API_FOOTBALL_KEY
    }
    
    try:
        url = f"https://{API_FOOTBALL_HOST}/fixtures"
        params = {
            'league': 39,  # Premier League
            'season': 2024,
            'date': '2024-10-14'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            fixtures = data.get('response', [])
            print(f"✅ Partidas encontradas: {len(fixtures)}")
            
            if fixtures:
                print("📋 Exemplos de partidas:")
                for fixture in fixtures[:3]:
                    fixture_info = fixture.get('fixture', {})
                    teams = fixture.get('teams', {})
                    home_team = teams.get('home', {}).get('name', 'N/A')
                    away_team = teams.get('away', {}).get('name', 'N/A')
                    date = fixture_info.get('date', 'N/A')
                    print(f"  - {home_team} vs {away_team} ({date})")
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    return True

def test_teams():
    """Testa endpoint de times"""
    print("\n👥 Testando endpoint de times...")
    
    headers = {
        'x-rapidapi-host': API_FOOTBALL_HOST,
        'x-rapidapi-key': API_FOOTBALL_KEY
    }
    
    try:
        url = f"https://{API_FOOTBALL_HOST}/teams"
        params = {
            'league': 39,  # Premier League
            'season': 2024
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            teams = data.get('response', [])
            print(f"✅ Times encontrados: {len(teams)}")
            
            if teams:
                print("📋 Exemplos de times:")
                for team in teams[:5]:
                    team_info = team.get('team', {})
                    print(f"  - {team_info.get('name', 'N/A')} (ID: {team_info.get('id', 'N/A')})")
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    return True

def test_live_matches():
    """Testa partidas ao vivo"""
    print("\n🔴 Testando partidas ao vivo...")
    
    headers = {
        'x-rapidapi-host': API_FOOTBALL_HOST,
        'x-rapidapi-key': API_FOOTBALL_KEY
    }
    
    try:
        url = f"https://{API_FOOTBALL_HOST}/fixtures"
        params = {'live': 'all'}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            live_matches = data.get('response', [])
            print(f"✅ Partidas ao vivo: {len(live_matches)}")
            
            if live_matches:
                print("📋 Partidas ao vivo:")
                for match in live_matches[:3]:
                    fixture_info = match.get('fixture', {})
                    teams = match.get('teams', {})
                    home_team = teams.get('home', {}).get('name', 'N/A')
                    away_team = teams.get('away', {}).get('name', 'N/A')
                    status = fixture_info.get('status', {}).get('short', 'N/A')
                    print(f"  - {home_team} vs {away_team} ({status})")
            else:
                print("ℹ️  Nenhuma partida ao vivo no momento")
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("🔮 MARABET AI - TESTE DA API-FOOTBALL")
    print("=" * 60)
    
    # Testar conexão
    if not test_api_connection():
        print("\n❌ Falha na conexão com a API")
        return
    
    # Testar endpoints
    tests = [
        ("Ligas", test_leagues),
        ("Partidas", test_fixtures),
        ("Times", test_teams),
        ("Partidas ao vivo", test_live_matches)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 30)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ OK" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n📈 Resultado: {success_count}/{len(results)} testes aprovados")
    
    if success_count == len(results):
        print("\n🎉 TODOS OS TESTES APROVADOS!")
        print("✅ API-Football configurada e funcionando perfeitamente")
        print("\n🚀 Próximos passos:")
        print("1. Configure a chave no arquivo .env")
        print("2. Execute: python test_api_keys.py")
        print("3. Inicie o sistema: python run_automated_collector.py")
    else:
        print("\n⚠️  Alguns testes falharam")
        print("💡 Verifique se a chave está correta e se há conexão com a internet")

if __name__ == "__main__":
    main()
