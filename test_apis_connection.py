#!/usr/bin/env python3
"""
Teste de Conexão com APIs de Futebol - MaraBet AI
Verifica se ambas as APIs estão recebendo dados corretamente
"""

import requests
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIsConnectionTest:
    def __init__(self):
        # API 1: API-Football (api-sports.io)
        self.api_football_key = "71b2b62386f2d1275cd3201a73e1e045"
        self.api_football_url = "https://v3.football.api-sports.io"
        self.api_football_headers = {
            'x-rapidapi-key': self.api_football_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        
        # API 2: football-data.org
        self.football_data_token = "721b0aaec5794327bab715da2abc7a7b"
        self.football_data_url = "https://api.football-data.org/v4"
        self.football_data_headers = {
            'X-Auth-Token': self.football_data_token
        }
        
        self.results = {
            'api_football': {'status': 'unknown', 'tests': {}},
            'football_data': {'status': 'unknown', 'tests': {}}
        }
    
    def print_header(self, text):
        print("\n" + "=" * 80)
        print(f"🔍 {text}")
        print("=" * 80)
    
    def test_api_football(self):
        """Testa API-Football"""
        self.print_header("TESTE 1: API-FOOTBALL (api-sports.io)")
        
        print(f"\n🔑 API Key: {self.api_football_key[:20]}...")
        print(f"🌐 URL: {self.api_football_url}")
        
        # Teste 1: Status da API
        print("\n📊 Teste 1.1: Status da API")
        try:
            response = requests.get(
                f"{self.api_football_url}/status",
                headers=self.api_football_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API respondendo!")
                
                if 'response' in data:
                    account = data['response']
                    print(f"   📊 Account: {account.get('account', {}).get('firstname', 'N/A')}")
                    print(f"   📊 Plano: {account.get('subscription', {}).get('plan', 'N/A')}")
                    print(f"   📊 Requests Hoje: {account.get('requests', {}).get('current', 0)}")
                    print(f"   📊 Limite: {account.get('requests', {}).get('limit_day', 0)}")
                    
                    self.results['api_football']['tests']['status'] = 'PASS'
                    self.results['api_football']['account_info'] = account
                else:
                    print("⚠️  Resposta sem dados de account")
                    self.results['api_football']['tests']['status'] = 'PARTIAL'
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                self.results['api_football']['tests']['status'] = 'FAIL'
        
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            self.results['api_football']['tests']['status'] = 'FAIL'
        
        # Teste 2: Buscar partidas
        print("\n📊 Teste 1.2: Buscar Partidas de Hoje")
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            response = requests.get(
                f"{self.api_football_url}/fixtures",
                headers=self.api_football_headers,
                params={'date': today},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('response', [])
                print(f"✅ API respondendo!")
                print(f"   📊 Partidas hoje: {len(matches)}")
                
                if len(matches) > 0:
                    # Mostrar primeira partida
                    match = matches[0]
                    print(f"\n   📋 Exemplo de partida:")
                    print(f"      {match['teams']['home']['name']} vs {match['teams']['away']['name']}")
                    print(f"      Liga: {match['league']['name']}")
                    print(f"      Data: {match['fixture']['date']}")
                
                self.results['api_football']['tests']['fixtures'] = 'PASS'
                self.results['api_football']['matches_count'] = len(matches)
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                self.results['api_football']['tests']['fixtures'] = 'FAIL'
        
        except Exception as e:
            print(f"❌ Erro ao buscar partidas: {e}")
            self.results['api_football']['tests']['fixtures'] = 'FAIL'
        
        # Teste 3: Buscar ligas
        print("\n📊 Teste 1.3: Listar Ligas Disponíveis")
        try:
            response = requests.get(
                f"{self.api_football_url}/leagues",
                headers=self.api_football_headers,
                params={'current': 'true'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                leagues = data.get('response', [])
                print(f"✅ API respondendo!")
                print(f"   📊 Ligas disponíveis: {len(leagues)}")
                
                # Mostrar primeiras 5 ligas
                print("\n   📋 Exemplos de ligas:")
                for league in leagues[:5]:
                    print(f"      • {league['league']['name']} ({league['country']['name']})")
                
                self.results['api_football']['tests']['leagues'] = 'PASS'
                self.results['api_football']['leagues_count'] = len(leagues)
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                self.results['api_football']['tests']['leagues'] = 'FAIL'
        
        except Exception as e:
            print(f"❌ Erro ao buscar ligas: {e}")
            self.results['api_football']['tests']['leagues'] = 'FAIL'
        
        # Determinar status geral
        tests_passed = sum(1 for v in self.results['api_football']['tests'].values() if v == 'PASS')
        total_tests = len(self.results['api_football']['tests'])
        
        if tests_passed == total_tests:
            self.results['api_football']['status'] = 'PASS'
            print(f"\n✅ API-FOOTBALL: FUNCIONANDO ({tests_passed}/{total_tests} testes)")
        elif tests_passed > 0:
            self.results['api_football']['status'] = 'PARTIAL'
            print(f"\n⚠️  API-FOOTBALL: PARCIAL ({tests_passed}/{total_tests} testes)")
        else:
            self.results['api_football']['status'] = 'FAIL'
            print(f"\n❌ API-FOOTBALL: FALHOU ({tests_passed}/{total_tests} testes)")
    
    def test_football_data_org(self):
        """Testa football-data.org"""
        self.print_header("TESTE 2: FOOTBALL-DATA.ORG")
        
        print(f"\n🔑 Token: {self.football_data_token[:20]}...")
        print(f"🌐 URL: {self.football_data_url}")
        
        # Teste 1: Competições disponíveis
        print("\n📊 Teste 2.1: Listar Competições")
        try:
            response = requests.get(
                f"{self.football_data_url}/competitions",
                headers=self.football_data_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                competitions = data.get('competitions', [])
                print("✅ API respondendo!")
                print(f"   📊 Competições disponíveis: {len(competitions)}")
                
                # Mostrar primeiras 5
                print("\n   📋 Exemplos de competições:")
                for comp in competitions[:5]:
                    print(f"      • {comp.get('name', 'N/A')} ({comp.get('area', {}).get('name', 'N/A')})")
                
                self.results['football_data']['tests']['competitions'] = 'PASS'
                self.results['football_data']['competitions_count'] = len(competitions)
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                self.results['football_data']['tests']['competitions'] = 'FAIL'
        
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            self.results['football_data']['tests']['competitions'] = 'FAIL'
        
        # Teste 2: Partidas de uma competição
        print("\n📊 Teste 2.2: Buscar Partidas (Premier League)")
        try:
            # Premier League code: PL
            response = requests.get(
                f"{self.football_data_url}/competitions/PL/matches",
                headers=self.football_data_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('matches', [])
                print("✅ API respondendo!")
                print(f"   📊 Partidas encontradas: {len(matches)}")
                
                if len(matches) > 0:
                    # Mostrar primeira partida
                    match = matches[0]
                    print(f"\n   📋 Exemplo de partida:")
                    print(f"      {match['homeTeam']['name']} vs {match['awayTeam']['name']}")
                    print(f"      Data: {match.get('utcDate', 'N/A')}")
                    print(f"      Status: {match.get('status', 'N/A')}")
                
                self.results['football_data']['tests']['matches'] = 'PASS'
                self.results['football_data']['matches_count'] = len(matches)
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                self.results['football_data']['tests']['matches'] = 'FAIL'
        
        except Exception as e:
            print(f"❌ Erro ao buscar partidas: {e}")
            self.results['football_data']['tests']['matches'] = 'FAIL'
        
        # Teste 3: Tabela de classificação
        print("\n📊 Teste 2.3: Buscar Classificação (Premier League)")
        try:
            response = requests.get(
                f"{self.football_data_url}/competitions/PL/standings",
                headers=self.football_data_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                standings = data.get('standings', [])
                print("✅ API respondendo!")
                print(f"   📊 Tabelas disponíveis: {len(standings)}")
                
                if len(standings) > 0 and len(standings[0].get('table', [])) > 0:
                    # Mostrar top 3
                    print("\n   📋 Top 3:")
                    for i, team in enumerate(standings[0]['table'][:3], 1):
                        print(f"      {i}. {team['team']['name']} - {team['points']} pts")
                
                self.results['football_data']['tests']['standings'] = 'PASS'
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                self.results['football_data']['tests']['standings'] = 'FAIL'
        
        except Exception as e:
            print(f"❌ Erro ao buscar classificação: {e}")
            self.results['football_data']['tests']['standings'] = 'FAIL'
        
        # Determinar status geral
        tests_passed = sum(1 for v in self.results['football_data']['tests'].values() if v == 'PASS')
        total_tests = len(self.results['football_data']['tests'])
        
        if tests_passed == total_tests:
            self.results['football_data']['status'] = 'PASS'
            print(f"\n✅ FOOTBALL-DATA.ORG: FUNCIONANDO ({tests_passed}/{total_tests} testes)")
        elif tests_passed > 0:
            self.results['football_data']['status'] = 'PARTIAL'
            print(f"\n⚠️  FOOTBALL-DATA.ORG: PARCIAL ({tests_passed}/{total_tests} testes)")
        else:
            self.results['football_data']['status'] = 'FAIL'
            print(f"\n❌ FOOTBALL-DATA.ORG: FALHOU ({tests_passed}/{total_tests} testes)")
    
    def generate_report(self):
        """Gera relatório final"""
        self.print_header("RELATÓRIO FINAL DE CONEXÃO DAS APIS")
        
        print("\n📊 RESUMO DOS TESTES:")
        print("-" * 80)
        
        # API-Football
        api1_status = self.results['api_football']['status']
        api1_icon = "✅" if api1_status == 'PASS' else "⚠️" if api1_status == 'PARTIAL' else "❌"
        
        print(f"\n{api1_icon} API 1: API-FOOTBALL (api-sports.io)")
        print(f"   Status Geral: {api1_status}")
        print(f"   Testes:")
        for test_name, result in self.results['api_football']['tests'].items():
            icon = "✅" if result == 'PASS' else "❌"
            print(f"      {icon} {test_name}: {result}")
        
        if 'matches_count' in self.results['api_football']:
            print(f"   📊 Partidas disponíveis: {self.results['api_football']['matches_count']}")
        if 'leagues_count' in self.results['api_football']:
            print(f"   📊 Ligas disponíveis: {self.results['api_football']['leagues_count']}")
        
        # football-data.org
        api2_status = self.results['football_data']['status']
        api2_icon = "✅" if api2_status == 'PASS' else "⚠️" if api2_status == 'PARTIAL' else "❌"
        
        print(f"\n{api2_icon} API 2: FOOTBALL-DATA.ORG")
        print(f"   Status Geral: {api2_status}")
        print(f"   Testes:")
        for test_name, result in self.results['football_data']['tests'].items():
            icon = "✅" if result == 'PASS' else "❌"
            print(f"      {icon} {test_name}: {result}")
        
        if 'competitions_count' in self.results['football_data']:
            print(f"   📊 Competições disponíveis: {self.results['football_data']['competitions_count']}")
        if 'matches_count' in self.results['football_data']:
            print(f"   📊 Partidas disponíveis: {self.results['football_data']['matches_count']}")
        
        # Conclusão
        print("\n" + "=" * 80)
        
        both_working = (api1_status in ['PASS', 'PARTIAL'] and 
                       api2_status in ['PASS', 'PARTIAL'])
        
        if both_working:
            print("🎉 AMBAS AS APIS ESTÃO FUNCIONANDO!")
            print("\n✅ Sistema pode receber dados de:")
            print("   • API-Football: Partidas, ligas, estatísticas")
            print("   • football-data.org: Competições, classificações")
            print("\n✅ MaraBet AI pronto para gerar previsões com dados reais!")
        else:
            print("⚠️  ATENÇÃO: Problemas detectados nas APIs")
            
            if api1_status == 'FAIL':
                print("\n❌ API-Football não está respondendo")
                print("   Verificar:")
                print("   1. API Key está correta")
                print("   2. Limite de requisições não foi atingido")
                print("   3. Conexão com internet")
            
            if api2_status == 'FAIL':
                print("\n❌ football-data.org não está respondendo")
                print("   Verificar:")
                print("   1. Token está correto")
                print("   2. Plano ativo")
                print("   3. Conexão com internet")
        
        print("=" * 80)
        
        # Salvar relatório JSON
        with open('api_connection_test_report.json', 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': self.results
            }, f, indent=2)
        
        print("\n💾 Relatório salvo: api_connection_test_report.json")
        
        return both_working

def main():
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                                                                ║")
    print("║     🔍 TESTE DE CONEXÃO APIs DE FUTEBOL - MARABET AI          ║")
    print("║                                                                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📞 Contato: +224 932027393")
    print()
    
    tester = APIsConnectionTest()
    
    # Testar ambas as APIs
    tester.test_api_football()
    tester.test_football_data_org()
    
    # Gerar relatório
    success = tester.generate_report()
    
    print("\n📞 Suporte:")
    print("   📧 Comercial: comercial@marabet.ao")
    print("   📧 Suporte: suporte@marabet.ao")
    print("   📞 WhatsApp: +224 932027393")
    print()
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

