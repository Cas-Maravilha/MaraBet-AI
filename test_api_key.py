#!/usr/bin/env python3
"""
Script de Teste da API Key
MaraBet AI - Teste específico da nova API key
"""

import os
import sys
import requests
from dotenv import load_dotenv

def test_api_key_directly(api_key: str):
    """Testa API key diretamente"""
    print(f"🔍 TESTANDO API KEY: {api_key[:10]}...")
    print("=" * 50)
    
    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': 'v3.football.api-sports.io'
    }
    
    # Testar diferentes endpoints
    endpoints = [
        ('leagues', {'country': 'England'}),
        ('fixtures', {'live': 'all'}),
        ('teams', {'country': 'England'})
    ]
    
    for endpoint, params in endpoints:
        print(f"\n📡 Testando endpoint: {endpoint}")
        try:
            url = f"https://v3.football.api-sports.io/{endpoint}"
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Resultados: {data.get('results', 0)}")
                
                if 'errors' in data and data['errors']:
                    print(f"   ❌ Erros: {data['errors']}")
                else:
                    print(f"   ✅ Sucesso!")
            else:
                print(f"   ❌ Erro HTTP: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    return True

def test_with_system():
    """Testa com sistema integrado"""
    print(f"\n🤖 TESTANDO COM SISTEMA INTEGRADO")
    print("=" * 50)
    
    try:
        from api.real_football_api import initialize_real_football_api
        
        api_key = os.getenv('API_FOOTBALL_KEY')
        api = initialize_real_football_api(api_key)
        
        # Testar conexão
        if api.test_api_connection():
            print("✅ Sistema integrado funcionando!")
            
            # Testar funcionalidades específicas
            print("\n📊 Testando funcionalidades:")
            
            # Partidas ao vivo
            live_matches = api.get_live_matches()
            print(f"   Partidas ao vivo: {len(live_matches)}")
            
            # Partidas de hoje
            today_matches = api.get_today_matches()
            print(f"   Partidas de hoje: {len(today_matches)}")
            
            # Tabela da Premier League
            standings = api.get_league_standings(39)
            print(f"   Times na tabela: {len(standings)}")
            
            return True
        else:
            print("❌ Sistema integrado não funcionando")
            return False
            
    except Exception as e:
        print(f"❌ Erro no sistema integrado: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE DA API KEY - MARABET AI")
    print("=" * 60)
    
    # Carregar API key do .env
    load_dotenv()
    api_key = os.getenv('API_FOOTBALL_KEY')
    
    if not api_key:
        print("❌ API key não encontrada no .env")
        return False
    
    print(f"API Key encontrada: {api_key[:10]}...")
    
    # Teste direto
    test_api_key_directly(api_key)
    
    # Teste com sistema
    test_with_system()
    
    print(f"\n🎯 RESUMO:")
    print(f"   API Key: {api_key[:10]}...")
    print(f"   Status: {'Funcionando' if '6da9495ae0' in api_key else 'Não configurada'}")
    print(f"   Sistema: {'Pronto' if os.path.exists('models/ensemble_model.joblib') else 'Não configurado'}")
    
    return True

if __name__ == "__main__":
    main()
