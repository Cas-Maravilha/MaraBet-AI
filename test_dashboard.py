#!/usr/bin/env python3
"""
Script para testar o dashboard web do MaraBet AI
"""

import sys
import os
import requests
import time
import logging
from datetime import datetime

# Adiciona o diretório pai ao sys.path para permitir importações relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from settings.api_keys import validate_keys

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL base do dashboard
BASE_URL = "http://localhost:8000"

def test_dashboard_availability():
    """Testa se o dashboard está disponível"""
    print("🌐 TESTE DE DISPONIBILIDADE DO DASHBOARD")
    print("=" * 50)
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        
        if response.status_code == 200:
            print("✅ Dashboard acessível")
            print(f"   Status: {response.status_code}")
            print(f"   Tamanho da resposta: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Dashboard retornou status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao dashboard")
        print("   Certifique-se de que o servidor está rodando:")
        print("   python run_dashboard.py")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar dashboard: {e}")
        return False

def test_api_endpoints():
    """Testa os endpoints da API"""
    print("\n🔌 TESTE DE ENDPOINTS DA API")
    print("=" * 50)
    
    endpoints = [
        ("/api/stats", "GET", "Estatísticas do sistema"),
        ("/api/predictions", "GET", "Lista de predições"),
        ("/api/matches", "GET", "Lista de partidas"),
        ("/api/leagues", "GET", "Lista de ligas"),
        ("/api/markets", "GET", "Lista de mercados"),
        ("/api/performance", "GET", "Métricas de performance"),
        ("/api/collector/status", "GET", "Status do coletor"),
    ]
    
    results = []
    
    for endpoint, method, description in endpoints:
        try:
            url = BASE_URL + endpoint
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {description}: {response.status_code}")
                results.append(True)
            else:
                print(f"❌ {description}: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {description}: Erro - {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 Taxa de sucesso: {success_rate:.1f}%")
    
    return success_rate > 80

def test_api_data_quality():
    """Testa a qualidade dos dados retornados pela API"""
    print("\n📊 TESTE DE QUALIDADE DOS DADOS")
    print("=" * 50)
    
    try:
        # Testar endpoint de estatísticas
        response = requests.get(BASE_URL + "/api/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            
            print("✅ Estatísticas recebidas:")
            print(f"   Partidas: {stats.get('total_matches', 0)}")
            print(f"   Odds: {stats.get('total_odds', 0)}")
            print(f"   Predições: {stats.get('total_predictions', 0)}")
            print(f"   Recomendadas: {stats.get('recommended_predictions', 0)}")
            
            # Verificar se as chaves esperadas existem
            expected_keys = ['total_matches', 'total_odds', 'total_predictions', 'recommended_predictions']
            missing_keys = [key for key in expected_keys if key not in stats]
            
            if missing_keys:
                print(f"⚠️  Chaves faltando: {missing_keys}")
                return False
            else:
                print("✅ Todas as chaves esperadas presentes")
                return True
        else:
            print(f"❌ Erro ao obter estatísticas: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de qualidade: {e}")
        return False

def test_predictions_api():
    """Testa a API de predições"""
    print("\n🔮 TESTE DA API DE PREDIÇÕES")
    print("=" * 50)
    
    try:
        # Testar diferentes parâmetros
        test_cases = [
            ("/api/predictions", "Sem parâmetros"),
            ("/api/predictions?limit=10", "Com limite"),
            ("/api/predictions?recommended_only=true", "Apenas recomendadas"),
            ("/api/predictions?limit=5&recommended_only=false", "Com limite e todas"),
        ]
        
        for endpoint, description in test_cases:
            try:
                response = requests.get(BASE_URL + endpoint, timeout=5)
                
                if response.status_code == 200:
                    predictions = response.json()
                    print(f"✅ {description}: {len(predictions)} predições")
                    
                    # Verificar estrutura das predições
                    if predictions:
                        pred = predictions[0]
                        expected_keys = ['id', 'market', 'selection', 'expected_value', 'confidence']
                        missing_keys = [key for key in expected_keys if key not in pred]
                        
                        if missing_keys:
                            print(f"   ⚠️  Chaves faltando: {missing_keys}")
                        else:
                            print(f"   ✅ Estrutura válida")
                else:
                    print(f"❌ {description}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {description}: Erro - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de predições: {e}")
        return False

def test_matches_api():
    """Testa a API de partidas"""
    print("\n⚽ TESTE DA API DE PARTIDAS")
    print("=" * 50)
    
    try:
        # Testar diferentes parâmetros
        test_cases = [
            ("/api/matches", "Sem parâmetros"),
            ("/api/matches?limit=10", "Com limite"),
            ("/api/matches?status=NS", "Apenas não iniciadas"),
            ("/api/matches?league=Premier League", "Por liga"),
        ]
        
        for endpoint, description in test_cases:
            try:
                response = requests.get(BASE_URL + endpoint, timeout=5)
                
                if response.status_code == 200:
                    matches = response.json()
                    print(f"✅ {description}: {len(matches)} partidas")
                    
                    # Verificar estrutura das partidas
                    if matches:
                        match = matches[0]
                        expected_keys = ['fixture_id', 'home_team', 'away_team', 'date', 'status']
                        missing_keys = [key for key in expected_keys if key not in match]
                        
                        if missing_keys:
                            print(f"   ⚠️  Chaves faltando: {missing_keys}")
                        else:
                            print(f"   ✅ Estrutura válida")
                else:
                    print(f"❌ {description}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {description}: Erro - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de partidas: {e}")
        return False

def test_collector_control():
    """Testa o controle do coletor"""
    print("\n🤖 TESTE DE CONTROLE DO COLETOR")
    print("=" * 50)
    
    try:
        # Verificar status inicial
        response = requests.get(BASE_URL + "/api/collector/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Status inicial: {status.get('running', 'N/A')}")
            
            # Testar parada (se estiver rodando)
            if status.get('running', False):
                print("   Testando parada do coletor...")
                stop_response = requests.post(BASE_URL + "/api/collector/stop", timeout=5)
                if stop_response.status_code == 200:
                    print("   ✅ Coletor parado com sucesso")
                else:
                    print(f"   ❌ Erro ao parar coletor: {stop_response.status_code}")
            
            # Testar início
            print("   Testando início do coletor...")
            start_response = requests.post(BASE_URL + "/api/collector/start", timeout=5)
            if start_response.status_code == 200:
                print("   ✅ Coletor iniciado com sucesso")
            else:
                print(f"   ❌ Erro ao iniciar coletor: {start_response.status_code}")
            
            return True
        else:
            print(f"❌ Erro ao obter status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de controle: {e}")
        return False

def test_performance_metrics():
    """Testa as métricas de performance"""
    print("\n📈 TESTE DE MÉTRICAS DE PERFORMANCE")
    print("=" * 50)
    
    try:
        response = requests.get(BASE_URL + "/api/performance", timeout=5)
        
        if response.status_code == 200:
            performance = response.json()
            
            print("✅ Métricas de performance:")
            print(f"   Total de predições: {performance.get('total_predictions', 0)}")
            print(f"   EV médio: {performance.get('average_ev', 0):.2%}")
            print(f"   Confiança média: {performance.get('average_confidence', 0):.2%}")
            print(f"   Taxa de sucesso: {performance.get('success_rate', 0):.2%}")
            
            # Verificar se os valores são razoáveis
            ev = performance.get('average_ev', 0)
            confidence = performance.get('average_confidence', 0)
            success_rate = performance.get('success_rate', 0)
            
            if 0 <= ev <= 1 and 0 <= confidence <= 1 and 0 <= success_rate <= 1:
                print("✅ Valores dentro dos limites esperados")
                return True
            else:
                print("⚠️  Valores fora dos limites esperados")
                return False
        else:
            print(f"❌ Erro ao obter métricas: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 MARABET AI - TESTE DO DASHBOARD")
    print("=" * 60)
    
    # Verificar se o dashboard está rodando
    print("📋 Verificando se o dashboard está rodando...")
    if not test_dashboard_availability():
        print("\n❌ Dashboard não está disponível!")
        print("Para executar o dashboard:")
        print("1. Abra um terminal")
        print("2. Execute: python run_dashboard.py")
        print("3. Aguarde a mensagem 'Uvicorn running on...'")
        print("4. Execute este teste novamente")
        sys.exit(1)
    
    # Executar testes
    results = []
    
    results.append(test_dashboard_availability())
    results.append(test_api_endpoints())
    results.append(test_api_data_quality())
    results.append(test_predictions_api())
    results.append(test_matches_api())
    results.append(test_collector_control())
    results.append(test_performance_metrics())
    
    # Resultado final
    success_count = sum(results)
    total_tests = len(results)
    
    print(f"\n📊 RESULTADO FINAL")
    print("=" * 30)
    print(f"Testes aprovados: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 Todos os testes passaram!")
        print("\n✅ O dashboard está funcionando perfeitamente!")
        print("🌐 Acesse: http://localhost:8000")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
        print("💡 Dicas para resolver problemas:")
        print("   • Verifique se o banco de dados está funcionando")
        print("   • Confirme se todas as dependências estão instaladas")
        print("   • Verifique os logs do servidor para erros")

if __name__ == "__main__":
    main()
