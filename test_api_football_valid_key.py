#!/usr/bin/env python3
"""
Teste da API Football com Chave Válida
MaraBet AI - Validação da integração com chave válida
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

class APIFootballValidTester:
    """Testador da API Football com chave válida"""
    
    def __init__(self):
        self.api_key = "71b2b62386f2d1275cd3201a73e1e045"
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        self.test_results = {
            'api_connected': False,
            'leagues_available': 0,
            'teams_available': 0,
            'fixtures_available': 0,
            'odds_available': 0,
            'response_times': [],
            'error_count': 0,
            'success_rate': 0.0,
            'data_collected': False
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
                
                # Verificar se há erros de token
                if 'errors' in data and 'token' in data['errors']:
                    logger.error(f"   Erro de token: {data['errors']['token']}")
                    return False
                
                self.test_results['api_connected'] = True
                logger.info("   ✅ Conexão com API funcionando")
                return True
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                logger.error(f"   Resposta: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"   Erro de conexão: {e}")
            return False
    
    def test_countries_endpoint(self) -> Dict[str, Any]:
        """Testa endpoint de países"""
        logger.info("🌍 TESTANDO ENDPOINT DE PAÍSES")
        print("=" * 60)
        
        results = {
            'success': False,
            'countries_count': 0,
            'response_time': 0,
            'countries_data': []
        }
        
        try:
            start_time = time.time()
            
            response = requests.get(
                f"{self.base_url}/countries",
                headers=self.headers,
                timeout=10
            )
            
            results['response_time'] = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if 'errors' in data and 'token' in data['errors']:
                    logger.error(f"   Erro de token: {data['errors']['token']}")
                    return results
                
                countries = data.get('response', [])
                results['countries_count'] = len(countries)
                results['countries_data'] = countries[:10]  # Primeiros 10 países
                results['success'] = True
                
                logger.info(f"   Países encontrados: {len(countries)}")
                for country in countries[:5]:
                    country_name = country.get('name', 'N/A')
                    country_code = country.get('code', 'N/A')
                    logger.info(f"   - {country_name} ({country_code})")
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                logger.error(f"   Resposta: {response.text}")
                
        except Exception as e:
            logger.error(f"   Erro ao buscar países: {e}")
            results['error_count'] += 1
        
        return results
    
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
                
                if 'errors' in data and 'token' in data['errors']:
                    logger.error(f"   Erro de token: {data['errors']['token']}")
                    return results
                
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
            results['error_count'] += 1
        
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
                
                if 'errors' in data and 'token' in data['errors']:
                    logger.error(f"   Erro de token: {data['errors']['token']}")
                    return results
                
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
            results['error_count'] += 1
        
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
                
                if 'errors' in data and 'token' in data['errors']:
                    logger.error(f"   Erro de token: {data['errors']['token']}")
                    return results
                
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
            results['error_count'] += 1
        
        return results
    
    def test_odds_endpoint(self) -> Dict[str, Any]:
        """Testa endpoint de odds"""
        logger.info("💰 TESTANDO ENDPOINT DE ODDS")
        print("=" * 60)
        
        results = {
            'success': False,
            'odds_count': 0,
            'response_time': 0,
            'odds_data': []
        }
        
        try:
            start_time = time.time()
            
            # Buscar odds de partidas
            response = requests.get(
                f"{self.base_url}/odds",
                headers=self.headers,
                params={
                    'league': 71,  # Brasileirão
                    'season': 2024,
                    'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                },
                timeout=10
            )
            
            results['response_time'] = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if 'errors' in data and 'token' in data['errors']:
                    logger.error(f"   Erro de token: {data['errors']['token']}")
                    return results
                
                odds = data.get('response', [])
                results['odds_count'] = len(odds)
                results['odds_data'] = odds[:3]  # Primeiras 3 odds
                results['success'] = True
                
                logger.info(f"   Odds encontradas: {len(odds)}")
                for odd in odds[:2]:
                    fixture = odd.get('fixture', {})
                    teams = odd.get('teams', {})
                    home_team = teams.get('home', {}).get('name', 'N/A')
                    away_team = teams.get('away', {}).get('name', 'N/A')
                    logger.info(f"   - {home_team} vs {away_team}")
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                logger.error(f"   Resposta: {response.text}")
                
        except Exception as e:
            logger.error(f"   Erro ao buscar odds: {e}")
            results['error_count'] += 1
        
        return results
    
    def collect_real_data(self) -> Dict[str, Any]:
        """Coleta dados reais para treinamento"""
        logger.info("📊 COLETANDO DADOS REAIS PARA TREINAMENTO")
        print("=" * 60)
        
        results = {
            'leagues_collected': 0,
            'teams_collected': 0,
            'fixtures_collected': 0,
            'odds_collected': 0,
            'data_saved': False
        }
        
        try:
            # Coletar dados de ligas
            leagues_response = requests.get(
                f"{self.base_url}/leagues",
                headers=self.headers,
                params={'season': 2024, 'country': 'Brazil'},
                timeout=10
            )
            
            if leagues_response.status_code == 200:
                leagues_data = leagues_response.json()
                if 'errors' not in leagues_data or 'token' not in leagues_data['errors']:
                    results['leagues_collected'] = len(leagues_data.get('response', []))
                    logger.info(f"   Ligas coletadas: {results['leagues_collected']}")
            
            # Coletar dados de times
            teams_response = requests.get(
                f"{self.base_url}/teams",
                headers=self.headers,
                params={'country': 'Brazil', 'season': 2024},
                timeout=10
            )
            
            if teams_response.status_code == 200:
                teams_data = teams_response.json()
                if 'errors' not in teams_data or 'token' not in teams_data['errors']:
                    results['teams_collected'] = len(teams_data.get('response', []))
                    logger.info(f"   Times coletados: {results['teams_collected']}")
            
            # Coletar dados de partidas
            fixtures_response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={
                    'league': 71,
                    'season': 2024,
                    'from': '2024-01-01',
                    'to': '2024-12-31'
                },
                timeout=10
            )
            
            if fixtures_response.status_code == 200:
                fixtures_data = fixtures_response.json()
                if 'errors' not in fixtures_data or 'token' not in fixtures_data['errors']:
                    results['fixtures_collected'] = len(fixtures_data.get('response', []))
                    logger.info(f"   Partidas coletadas: {results['fixtures_collected']}")
            
            # Salvar dados coletados
            collected_data = {
                'leagues': leagues_data.get('response', []) if 'leagues_data' in locals() else [],
                'teams': teams_data.get('response', []) if 'teams_data' in locals() else [],
                'fixtures': fixtures_data.get('response', []) if 'fixtures_data' in locals() else [],
                'collected_at': datetime.now().isoformat(),
                'api_key': self.api_key
            }
            
            # Salvar em arquivo
            with open('real_football_data_valid.json', 'w', encoding='utf-8') as f:
                json.dump(collected_data, f, indent=2, ensure_ascii=False)
            
            results['data_saved'] = True
            logger.info("   Dados salvos em: real_football_data_valid.json")
            
        except Exception as e:
            logger.error(f"   Erro ao coletar dados: {e}")
        
        return results
    
    def generate_report(self, connection_result: bool, countries_result: Dict, leagues_result: Dict, 
                       teams_result: Dict, fixtures_result: Dict, odds_result: Dict, 
                       data_collection_result: Dict) -> str:
        """Gera relatório de teste"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE TESTE DA API FOOTBALL COM CHAVE VÁLIDA - MARABET AI")
        report.append("=" * 80)
        
        # Resumo geral
        report.append(f"\n📊 RESUMO GERAL:")
        report.append(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"  API Key: {self.api_key[:10]}...")
        report.append(f"  Conexão: {'✅ Funcionando' if connection_result else '❌ Falhou'}")
        report.append(f"  Países: {countries_result['countries_count']}")
        report.append(f"  Ligas: {leagues_result['leagues_count']}")
        report.append(f"  Times: {teams_result['teams_count']}")
        report.append(f"  Partidas: {fixtures_result['fixtures_count']}")
        report.append(f"  Odds: {odds_result['odds_count']}")
        
        # Resultados de conexão
        report.append(f"\n🔌 RESULTADOS DE CONEXÃO:")
        report.append(f"  API Conectada: {connection_result}")
        report.append(f"  Base URL: {self.base_url}")
        report.append(f"  Headers: Configurados")
        
        # Resultados de endpoints
        report.append(f"\n🌍 RESULTADOS DE ENDPOINTS:")
        report.append(f"  Países:")
        report.append(f"    Sucesso: {countries_result['success']}")
        report.append(f"    Quantidade: {countries_result['countries_count']}")
        report.append(f"    Tempo de resposta: {countries_result['response_time']:.2f}s")
        
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
        
        report.append(f"  Odds:")
        report.append(f"    Sucesso: {odds_result['success']}")
        report.append(f"    Quantidade: {odds_result['odds_count']}")
        report.append(f"    Tempo de resposta: {odds_result['response_time']:.2f}s")
        
        # Resultados de coleta de dados
        report.append(f"\n📊 RESULTADOS DE COLETA DE DADOS:")
        report.append(f"  Ligas coletadas: {data_collection_result['leagues_collected']}")
        report.append(f"  Times coletados: {data_collection_result['teams_collected']}")
        report.append(f"  Partidas coletadas: {data_collection_result['fixtures_collected']}")
        report.append(f"  Odds coletadas: {data_collection_result['odds_collected']}")
        report.append(f"  Dados salvos: {'✅' if data_collection_result['data_saved'] else '❌'}")
        
        # Validação de objetivos
        report.append(f"\n🎯 VALIDAÇÃO DE OBJETIVOS:")
        
        if connection_result:
            report.append(f"  ✅ API conectada")
        else:
            report.append(f"  ❌ API não conectada")
        
        if countries_result['success'] and countries_result['countries_count'] > 0:
            report.append(f"  ✅ Países disponíveis")
        else:
            report.append(f"  ❌ Países não disponíveis")
        
        if leagues_result['success'] and leagues_result['leagues_count'] > 0:
            report.append(f"  ✅ Ligas disponíveis")
        else:
            report.append(f"  ❌ Ligas não disponíveis")
        
        if teams_result['success'] and teams_result['teams_count'] > 0:
            report.append(f"  ✅ Times disponíveis")
        else:
            report.append(f"  ❌ Times não disponíveis")
        
        if fixtures_result['success'] and fixtures_result['fixtures_count'] > 0:
            report.append(f"  ✅ Partidas disponíveis")
        else:
            report.append(f"  ❌ Partidas não disponíveis")
        
        if odds_result['success'] and odds_result['odds_count'] > 0:
            report.append(f"  ✅ Odds disponíveis")
        else:
            report.append(f"  ❌ Odds não disponíveis")
        
        if data_collection_result['data_saved']:
            report.append(f"  ✅ Dados coletados e salvos")
        else:
            report.append(f"  ❌ Dados não coletados")
        
        # Recomendações
        report.append(f"\n💡 RECOMENDAÇÕES:")
        
        if not connection_result:
            report.append(f"  ⚠️ Verificar chave da API")
        
        if not countries_result['success']:
            report.append(f"  ⚠️ Verificar endpoint de países")
        
        if not leagues_result['success']:
            report.append(f"  ⚠️ Verificar endpoint de ligas")
        
        if not teams_result['success']:
            report.append(f"  ⚠️ Verificar endpoint de times")
        
        if not fixtures_result['success']:
            report.append(f"  ⚠️ Verificar endpoint de partidas")
        
        if not odds_result['success']:
            report.append(f"  ⚠️ Verificar endpoint de odds")
        
        report.append(f"  🔄 Executar coleta de dados regularmente")
        report.append(f"  📊 Monitorar limites da API")
        report.append(f"  🔐 Manter chave da API segura")
        
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Função principal"""
    print("⚽ TESTE DA API FOOTBALL COM CHAVE VÁLIDA - MARABET AI")
    print("=" * 80)
    
    tester = APIFootballValidTester()
    
    try:
        # 1. Testar conexão
        connection_result = tester.test_api_connection()
        
        if not connection_result:
            print("\n❌ Falha na conexão com API. Verifique a chave.")
            return False
        
        # 2. Testar endpoints
        countries_result = tester.test_countries_endpoint()
        leagues_result = tester.test_leagues_endpoint()
        teams_result = tester.test_teams_endpoint()
        fixtures_result = tester.test_fixtures_endpoint()
        odds_result = tester.test_odds_endpoint()
        
        # 3. Coletar dados reais
        data_collection_result = tester.collect_real_data()
        
        # 4. Gerar relatório
        report = tester.generate_report(
            connection_result, countries_result, leagues_result, teams_result,
            fixtures_result, odds_result, data_collection_result
        )
        print(f"\n{report}")
        
        # 5. Salvar relatório
        with open("api_football_valid_key_test_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("\n🎉 TESTE DA API FOOTBALL COM CHAVE VÁLIDA CONCLUÍDO!")
        print("📄 Relatório salvo em: api_football_valid_key_test_report.txt")
        print("📊 Dados reais salvos em: real_football_data_valid.json")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        return False

if __name__ == "__main__":
    main()
