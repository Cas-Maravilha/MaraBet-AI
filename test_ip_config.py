#!/usr/bin/env python3
"""
MaraBet AI - Teste de IP e APIs
Verifica se o IP está configurado corretamente
"""

import requests
import json

SYSTEM_IP = "102.206.57.108"
API_FOOTBALL_KEY = "71b2b62386f2d1275cd3201a73e1e045"

def test_current_ip():
    """Verifica IP atual"""
    print("\n" + "="*60)
    print("📍 VERIFICANDO IP ATUAL")
    print("="*60)
    
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        current_ip = response.json()['ip']
        
        print(f"\nIP Configurado: {SYSTEM_IP}")
        print(f"IP Detectado:   {current_ip}")
        
        if current_ip == SYSTEM_IP:
            print("\n✅ IP CORRETO!")
        else:
            print(f"\n⚠️  ATENÇÃO: IP diferente!")
            print(f"   Usar {current_ip} na whitelist")
        
        return current_ip
    except Exception as e:
        print(f"\n❌ Erro ao verificar IP: {e}")
        return None

def test_api_football():
    """Testa API-Football"""
    print("\n" + "="*60)
    print("🔵 TESTANDO API-FOOTBALL")
    print("="*60)
    
    try:
        headers = {'x-apisports-key': API_FOOTBALL_KEY}
        response = requests.get(
            'https://v3.football.api-sports.io/status',
            headers=headers,
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ API-FOOTBALL: OK")
            print(f"   Requests Remaining: {data.get('response', {}).get('requests', {}).get('current', 'N/A')}")
        else:
            print(f"\n❌ API-FOOTBALL: ERRO")
            print(f"   Resposta: {response.text}")
            
            if "IP" in response.text or "not allowed" in response.text.lower():
                print("\n⚠️  PROBLEMA DE IP WHITELIST!")
                print("   Ação: Adicionar IP na dashboard")
                print("   URL: https://dashboard.api-football.com/")
        
        return response.status_code == 200
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False

def test_football_data_org():
    """Testa football-data.org"""
    print("\n" + "="*60)
    print("🟢 TESTANDO FOOTBALL-DATA.ORG")
    print("="*60)
    
    try:
        headers = {'X-Auth-Token': '721b0aaec5794327bab715da2abc7a7b'}
        response = requests.get(
            'https://api.football-data.org/v4/competitions/',
            headers=headers,
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ FOOTBALL-DATA.ORG: OK")
            comps = len(data.get('competitions', []))
            print(f"   Competições: {comps}")
        else:
            print(f"\n❌ FOOTBALL-DATA.ORG: ERRO")
            print(f"   Resposta: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🔍 MARABET AI - TESTE DE CONFIGURAÇÃO DE IP")
    print("="*60)
    
    current_ip = test_current_ip()
    api_football_ok = test_api_football()
    football_data_ok = test_football_data_org()
    
    print("\n" + "="*60)
    print("📊 RESUMO")
    print("="*60)
    
    print(f"\nIP Configurado: {SYSTEM_IP}")
    if current_ip:
        print(f"IP Detectado:   {current_ip}")
    
    print(f"\nAPI-Football:       {'✅ OK' if api_football_ok else '❌ BLOQUEADA'}")
    print(f"football-data.org:  {'✅ OK' if football_data_ok else '❌ ERRO'}")
    
    if not api_football_ok:
        print("\n⚠️  AÇÃO NECESSÁRIA:")
        print("   1. Acessar: https://dashboard.api-football.com/")
        print("   2. Adicionar IP na whitelist")
        print("   3. Testar novamente")
        print("\n   Ver: IP_WHITELIST_INSTRUCTIONS.txt")
    
    if api_football_ok and football_data_ok:
        print("\n🎉 TUDO OK! Sistema pronto para usar.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
