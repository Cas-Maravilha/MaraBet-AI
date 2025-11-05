#!/usr/bin/env python3
"""
Teste Corrigido da API Football
MaraBet AI - Teste com endpoints corretos da API Football
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIFootballTesterCorrected:
    """Testador corrigido da API Football"""
    
    def __init__(self):
        self.api_key = "6da9495ae09b7477"
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
    
    def test_api_connection(self) -> bool:
        """Testa conexão com a API"""
        logger.info("🔌 TESTANDO CONEXÃO COM API FOOTBALL")
        print("=" * 60)
        
        try:
            # Testar endpoint de status
            response = requests.get(
                f"{self.base_url}/status",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"   Status da API: {data}")
                return True
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                logger.error(f"   Resposta: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"   Erro de conexão: {e}")
            return False
    
    def test_leagues_endpoint(self) -> Dict[str, Any]:
        """Testa endpoint de ligas"""
        logger.info("🏆 TESTANDO ENDPOINT DE LIGAS")
        print("=" * 60)
        
        results = {
            'success': False,
            'leagues_count': 0,
            'response_time': 0,
            'leagues_data': []
        }
        
        try:
            start_time = time.time()
            
            # Buscar ligas do Brasil
            response = requests.get(
                f"{self.base_url}/leagues",
                headers=self.headers,
                params={
                    'season': 2024,
                    'country': 'Brazil'
                },
                timeout=10
            )
            
            results['response_time'] = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"   Resposta completa: {json.dumps(data, indent=2)}")
                
                leagues = data.get('response', [])
                results['leagues_count'] = len(leagues)
                results['leagues_data'] = leagues[:5]  # Primeiras 5 ligas
                results['success'] = True
                
                logger.info(f"   Ligas encontradas: {len(leagues)}")
                for league in leagues[:3]:
                    league_info = league.get('league', {})
                    logger.info(f"   - {league_info.get('name', 'N/A')} (ID: {league_info.get('id', 'N/A')})")
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                logger.error(f"   Resposta: {response.text}")
                
        except Exception as e:
            logger.error(f"   Erro ao buscar ligas: {e}")
        
        return results
    
    def test_teams_endpoint(self) -> Dict[str, Any]:
        """Testa endpoint de times"""
        logger.info("⚽ TESTANDO ENDPOINT DE TIMES")
        print("=" * 60)
        
        results = {
            'success': False,
            'teams_count': 0,
            'response_time': 0,
            'teams_data': []
        }
        
        try:
            start_time = time.time()
            
            # Buscar times do Brasil
            response = requests.get(
                f"{self.base_url}/teams",
                headers=self.headers,
                params={
                    'country': 'Brazil',
                    'season': 2024
                },
                timeout=10
            )
            
            results['response_time'] = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"   Resposta completa: {json.dumps(data, indent=2)}")
                
                teams = data.get('response', [])
                results['teams_count'] = len(teams)
                results['teams_data'] = teams[:10]  # Primeiros 10 times
                results['success'] = True
                
                logger.info(f"   Times encontrados: {len(teams)}")
                for team in teams[:5]:
                    team_info = team.get('team', {})
                    logger.info(f"   - {team_info.get('name', 'N/A')} (ID: {team_info.get('id', 'N/A')})")
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                logger.error(f"   Resposta: {response.text}")
                
        except Exception as e:
            logger.error(f"   Erro ao buscar times: {e}")
        
        return results
    
    def test_fixtures_endpoint(self) -> Dict[str, Any]:
        """Testa endpoint de partidas"""
        logger.info("📅 TESTANDO ENDPOINT DE PARTIDAS")
        print("=" * 60)
        
        results = {
            'success': False,
            'fixtures_count': 0,
            'response_time': 0,
            'fixtures_data': []
        }
        
        try:
            start_time = time.time()
            
            # Buscar partidas recentes
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={
                    'date': yesterday,
                    'league': 71,  # Brasileirão
                    'season': 2024
                },
                timeout=10
            )
            
            results['response_time'] = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"   Resposta completa: {json.dumps(data, indent=2)}")
                
                fixtures = data.get('response', [])
                results['fixtures_count'] = len(fixtures)
                results['fixtures_data'] = fixtures[:5]  # Primeiras 5 partidas
                results['success'] = True
                
                logger.info(f"   Partidas encontradas: {len(fixtures)}")
                for fixture in fixtures[:3]:
                    fixture_info = fixture.get('fixture', {})
                    teams = fixture.get('teams', {})
                    home_team = teams.get('home', {}).get('name', 'N/A')
                    away_team = teams.get('away', {}).get('name', 'N/A')
                    logger.info(f"   - {home_team} vs {away_team}")
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                logger.error(f"   Resposta: {response.text}")
                
        except Exception as e:
            logger.error(f"   Erro ao buscar partidas: {e}")
        
        return results
    
    def test_simple_endpoints(self) -> Dict[str, Any]:
        """Testa endpoints simples"""
        logger.info("🔍 TESTANDO ENDPOINTS SIMPLES")
        print("=" * 60)
        
        results = {
            'countries': 0,
            'leagues_simple': 0,
            'teams_simple': 0,
            'fixtures_simple': 0
        }
        
        # Testar países
        try:
            response = requests.get(
                f"{self.base_url}/countries",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                results['countries'] = len(data.get('response', []))
                logger.info(f"   Países encontrados: {results['countries']}")
        except Exception as e:
            logger.error(f"   Erro ao buscar países: {e}")
        
        # Testar ligas simples
        try:
            response = requests.get(
                f"{self.base_url}/leagues",
                headers=self.headers,
                params={'season': 2024},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                results['leagues_simple'] = len(data.get('response', []))
                logger.info(f"   Ligas encontradas: {results['leagues_simple']}")
        except Exception as e:
            logger.error(f"   Erro ao buscar ligas: {e}")
        
        # Testar times simples
        try:
            response = requests.get(
                f"{self.base_url}/teams",
                headers=self.headers,
                params={'season': 2024},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                results['teams_simple'] = len(data.get('response', []))
                logger.info(f"   Times encontrados: {results['teams_simple']}")
        except Exception as e:
            logger.error(f"   Erro ao buscar times: {e}")
        
        # Testar partidas simples
        try:
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={'date': '2024-10-20'},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                results['fixtures_simple'] = len(data.get('response', []))
                logger.info(f"   Partidas encontradas: {results['fixtures_simple']}")
        except Exception as e:
            logger.error(f"   Erro ao buscar partidas: {e}")
        
        return results
    
    def generate_report(self, connection_result: bool, leagues_result: Dict, teams_result: Dict, 
                       fixtures_result: Dict, simple_result: Dict) -> str:
        """Gera relatório de teste"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE TESTE CORRIGIDO DA API FOOTBALL - MARABET AI")
        report.append("=" * 80)
        
        # Resumo geral
        report.append(f"\n📊 RESUMO GERAL:")
        report.append(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"  API Key: {self.api_key[:10]}...")
        report.append(f"  Conexão: {'✅ Funcionando' if connection_result else '❌ Falhou'}")
        report.append(f"  Ligas: {leagues_result['leagues_count']}")
        report.append(f"  Times: {teams_result['teams_count']}")
        report.append(f"  Partidas: {fixtures_result['fixtures_count']}")
        
        # Resultados de conexão
        report.append(f"\n🔌 RESULTADOS DE CONEXÃO:")
        report.append(f"  API Conectada: {connection_result}")
        report.append(f"  Base URL: {self.base_url}")
        report.append(f"  Headers: Configurados")
        
        # Resultados de endpoints
        report.append(f"\n🏆 RESULTADOS DE ENDPOINTS:")
        report.append(f"  Ligas:")
        report.append(f"    Sucesso: {leagues_result['success']}")
        report.append(f"    Quantidade: {leagues_result['leagues_count']}")
        report.append(f"    Tempo de resposta: {leagues_result['response_time']:.2f}s")
        
        report.append(f"  Times:")
        report.append(f"    Sucesso: {teams_result['success']}")
        report.append(f"    Quantidade: {teams_result['teams_count']}")
        report.append(f"    Tempo de resposta: {teams_result['response_time']:.2f}s")
        
        report.append(f"  Partidas:")
        report.append(f"    Sucesso: {fixtures_result['success']}")
        report.append(f"    Quantidade: {fixtures_result['fixtures_count']}")
        report.append(f"    Tempo de resposta: {fixtures_result['response_time']:.2f}s")
        
        # Resultados de endpoints simples
        report.append(f"\n🔍 RESULTADOS DE ENDPOINTS SIMPLES:")
        report.append(f"  Países: {simple_result['countries']}")
        report.append(f"  Ligas: {simple_result['leagues_simple']}")
        report.append(f"  Times: {simple_result['teams_simple']}")
        report.append(f"  Partidas: {simple_result['fixtures_simple']}")
        
        # Validação de objetivos
        report.append(f"\n🎯 VALIDAÇÃO DE OBJETIVOS:")
        
        if connection_result:
            report.append(f"  ✅ API conectada")
        else:
            report.append(f"  ❌ API não conectada")
        
        if simple_result['countries'] > 0:
            report.append(f"  ✅ Países disponíveis")
        else:
            report.append(f"  ❌ Países não disponíveis")
        
        if simple_result['leagues_simple'] > 0:
            report.append(f"  ✅ Ligas disponíveis")
        else:
            report.append(f"  ❌ Ligas não disponíveis")
        
        if simple_result['teams_simple'] > 0:
            report.append(f"  ✅ Times disponíveis")
        else:
            report.append(f"  ❌ Times não disponíveis")
        
        if simple_result['fixtures_simple'] > 0:
            report.append(f"  ✅ Partidas disponíveis")
        else:
            report.append(f"  ❌ Partidas não disponíveis")
        
        # Recomendações
        report.append(f"\n💡 RECOMENDAÇÕES:")
        
        if not connection_result:
            report.append(f"  ⚠️ Verificar chave da API")
        
        if simple_result['countries'] == 0:
            report.append(f"  ⚠️ Verificar endpoint de países")
        
        if simple_result['leagues_simple'] == 0:
            report.append(f"  ⚠️ Verificar endpoint de ligas")
        
        if simple_result['teams_simple'] == 0:
            report.append(f"  ⚠️ Verificar endpoint de times")
        
        if simple_result['fixtures_simple'] == 0:
            report.append(f"  ⚠️ Verificar endpoint de partidas")
        
        report.append(f"  🔄 Executar coleta de dados regularmente")
        report.append(f"  📊 Monitorar limites da API")
        report.append(f"  🔐 Manter chave da API segura")
        
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Função principal"""
    print("⚽ TESTE CORRIGIDO DA API FOOTBALL - MARABET AI")
    print("=" * 80)
    
    tester = APIFootballTesterCorrected()
    
    try:
        # 1. Testar conexão
        connection_result = tester.test_api_connection()
        
        # 2. Testar endpoints
        leagues_result = tester.test_leagues_endpoint()
        teams_result = tester.test_teams_endpoint()
        fixtures_result = tester.test_fixtures_endpoint()
        
        # 3. Testar endpoints simples
        simple_result = tester.test_simple_endpoints()
        
        # 4. Gerar relatório
        report = tester.generate_report(
            connection_result, leagues_result, teams_result,
            fixtures_result, simple_result
        )
        print(f"\n{report}")
        
        # 5. Salvar relatório
        with open("api_football_corrected_test_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("\n🎉 TESTE CORRIGIDO DA API FOOTBALL CONCLUÍDO!")
        print("📄 Relatório salvo em: api_football_corrected_test_report.txt")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        return False

if __name__ == "__main__":
    main()
