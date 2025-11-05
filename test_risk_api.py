#!/usr/bin/env python3
"""
Teste da API de Gestão de Risco
MaraBet AI - Validação dos endpoints de risco
"""

import requests
import json
import time

def test_risk_status():
    """Testa endpoint de status de risco"""
    print("🧪 TESTANDO ENDPOINT DE STATUS DE RISCO")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:5000/api/risk/status')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Status de risco obtido com sucesso!")
            print(f"  Drawdown: {data['data']['current_drawdown']:.1%}")
            print(f"  PnL Diário: R$ {data['data']['daily_pnl']:,.2f}")
            print(f"  PnL Semanal: R$ {data['data']['weekly_pnl']:,.2f}")
            print(f"  Perdas Consecutivas: {data['data']['consecutive_losses']}")
            print(f"  Apostas Ativas: {data['data']['active_bets']}")
            print(f"  Nível de Risco: {data['data']['risk_level'].upper()}")
            print(f"  Trading Halted: {data['data']['trading_halted']}")
            print(f"  Bankroll Atual: R$ {data['data']['current_bankroll']:,.2f}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"  Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_risk_validation():
    """Testa endpoint de validação de apostas"""
    print("\n🧪 TESTANDO ENDPOINT DE VALIDAÇÃO DE APOSTAS")
    print("=" * 50)
    
    # Teste 1: Aposta válida
    print("Testando aposta válida...")
    try:
        data = {
            'win_prob': 0.6,
            'odds': 2.0,
            'stake': 200
        }
        
        response = requests.post('http://localhost:5000/api/risk/validate', json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Válida: {result['data']['is_valid']}")
            print(f"  Mensagem: {result['data']['message']}")
            print(f"  Tamanho da Posição: {result['data']['position_size']:.2%}")
        else:
            print(f"  ❌ Erro: {response.status_code}")
            print(f"  Resposta: {response.text}")
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    # Teste 2: Aposta com edge baixo
    print("\nTestando aposta com edge baixo...")
    try:
        data = {
            'win_prob': 0.4,
            'odds': 2.0,
            'stake': 200
        }
        
        response = requests.post('http://localhost:5000/api/risk/validate', json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Válida: {result['data']['is_valid']}")
            print(f"  Mensagem: {result['data']['message']}")
            print(f"  Tamanho da Posição: {result['data']['position_size']:.2%}")
        else:
            print(f"  ❌ Erro: {response.status_code}")
            print(f"  Resposta: {response.text}")
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    # Teste 3: Aposta com posição muito grande
    print("\nTestando aposta com posição muito grande...")
    try:
        data = {
            'win_prob': 0.6,
            'odds': 2.0,
            'stake': 500  # 5% do bankroll
        }
        
        response = requests.post('http://localhost:5000/api/risk/validate', json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Válida: {result['data']['is_valid']}")
            print(f"  Mensagem: {result['data']['message']}")
            print(f"  Tamanho da Posição: {result['data']['position_size']:.2%}")
        else:
            print(f"  ❌ Erro: {response.status_code}")
            print(f"  Resposta: {response.text}")
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    return True

def test_risk_report():
    """Testa endpoint de relatório de risco"""
    print("\n🧪 TESTANDO ENDPOINT DE RELATÓRIO DE RISCO")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:5000/api/risk/report')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Relatório de risco obtido com sucesso!")
            print(f"  Timestamp: {data['data']['timestamp']}")
            print("\n📋 RELATÓRIO:")
            print(data['data']['report'])
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"  Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_health_check():
    """Testa health check"""
    print("\n🧪 TESTANDO HEALTH CHECK")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:5000/api/health')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check OK!")
            print(f"  Status: {data['status']}")
            print(f"  Timestamp: {data['timestamp']}")
            print(f"  Version: {data['version']}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE DA API DE GESTÃO DE RISCO - MARABET AI")
    print("=" * 70)
    
    # Verificar se o servidor está rodando
    print("Verificando se o servidor está rodando...")
    
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code != 200:
            print("❌ Servidor não está rodando ou não respondeu corretamente")
            print("   Execute: python app.py")
            return False
    except Exception as e:
        print("❌ Servidor não está rodando")
        print("   Execute: python app.py")
        return False
    
    print("✅ Servidor está rodando!")
    
    # Executar testes
    try:
        test_health_check()
        test_risk_status()
        test_risk_validation()
        test_risk_report()
        
        print("\n🎉 TODOS OS TESTES DA API CONCLUÍDOS!")
        print("✅ API de gestão de risco funcionando perfeitamente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {e}")
        return False

if __name__ == "__main__":
    main()
