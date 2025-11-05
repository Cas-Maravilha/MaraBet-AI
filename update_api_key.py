#!/usr/bin/env python3
"""
Script para Atualizar API Key
MaraBet AI - Atualização da API key da API-Football
"""

import os
import sys
from pathlib import Path

def update_api_key(new_api_key: str):
    """Atualiza API key no arquivo .env"""
    print("🔧 ATUALIZANDO API KEY DA API-FOOTBALL")
    print("=" * 50)
    
    # Ler arquivo .env atual
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado")
        return False
    
    # Ler conteúdo atual
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Atualizar API key
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('API_FOOTBALL_KEY='):
            updated_lines.append(f'API_FOOTBALL_KEY={new_api_key}')
            print(f"✅ API key atualizada: {new_api_key[:10]}...")
        else:
            updated_lines.append(line)
    
    # Escrever arquivo atualizado
    updated_content = '\n'.join(updated_lines)
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✅ Arquivo .env atualizado com sucesso!")
    return True

def test_new_api_key(api_key: str):
    """Testa nova API key"""
    print("\n🌐 TESTANDO NOVA API KEY")
    print("=" * 50)
    
    try:
        import requests
        
        headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'v3.football.api-sports.io'
        }
        
        # Testar endpoint de ligas
        response = requests.get(
            'https://v3.football.api-sports.io/leagues',
            headers=headers,
            params={'country': 'England'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data and data['errors']:
                print(f"❌ Erro na API: {data['errors']}")
                return False
            else:
                print("✅ Nova API key funcionando!")
                print(f"   Status: {response.status_code}")
                print(f"   Resultados: {data.get('results', 0)}")
                return True
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        return False

def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("Uso: python update_api_key.py <nova_api_key>")
        sys.exit(1)
    
    new_api_key = sys.argv[1]
    
    print("🚀 ATUALIZAÇÃO DA API KEY - MARABET AI")
    print("=" * 60)
    
    # Atualizar API key
    if not update_api_key(new_api_key):
        print("❌ Falha na atualização da API key")
        sys.exit(1)
    
    # Testar nova API key
    if not test_new_api_key(new_api_key):
        print("⚠️ Nova API key não está funcionando, mas foi salva")
        print("   Execute o setup completo para testar com dados simulados")
    else:
        print("🎉 Nova API key configurada e funcionando!")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Execute: python setup_complete_system.py")
    print("2. O sistema usará a nova API key para dados reais")
    print("3. Se a API não funcionar, usará dados simulados como fallback")

if __name__ == "__main__":
    main()
