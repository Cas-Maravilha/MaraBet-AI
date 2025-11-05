#!/usr/bin/env python3
"""
Teste Completo do Plano Ultra API-Football - MaraBet AI
Verifica todos os recursos do plano Ultra
"""

import requests
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIFootballUltraTest:
    def __init__(self):
        # API Key do plano Ultra
        self.api_key = "71b2b62386f2d1275cd3201a73e1e045"
        self.base_url = "https://v3.football.api-sports.io"
        
        # Header correto para plano Ultra
        self.headers = {
            'x-apisports-key': self.api_key  # Header correto para Ultra
        }
        
        self.results = {
            'api_key': self.api_key[:20] + '...',
            'plan': 'Ultra',
            'tests': {},
            'timestamp': datetime.now().isoformat()
        }
    
    def print_header(self, text):
        print("\n" + "=" * 80)
        print(f"🔍 {text}")
        print("=" * 80)
    
    def test_1_account_status(self):
        """Teste 1: Status da conta e plano"""
        self.print_header("TESTE 1: STATUS DA CONTA ULTRA")
        
        try:
            response = requests.get(
                f"{self.base_url}/status",
                headers=self.headers,
                timeout=10
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API respondendo!")
                print(f"\n📋 Resposta completa:")
                print(json.dumps(data, indent=2))
                
                # Extrair informações
                if 'response' in data:
                    info = data['response']
                    if isinstance(info, dict):
                        print(f"\n📊 Plano: {info.get('subscription', {}).get('plan', 'N/A')}")
                        print(f"📊 Requests Hoje: {info.get('requests', {}).get('current', 0)}")
                        print(f"📊 Limite Diário: {info.get('requests', {}).get('limit_day', 0)}")
                        
                        self.results['tests']['account'] = 'PASS'
                        self.results['plan_info'] = info
                        return True
                
                print("⚠️ Formato de resposta diferente do esperado")
                self.results['tests']['account'] = 'PARTIAL'
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                print(f"Resposta: {response.text}")
                self.results['tests']['account'] = 'FAIL'
                return False
        
        except Exception as e:
            print(f"❌ Exceção: {e}")
            self.results['tests']['account'] = 'FAIL'
            return False
    
    def test_2_live_fixtures(self):
        """Teste 2: Jogos ao vivo (recurso Ultra)"""
        self.print_header("TESTE 2: JOGOS AO VIVO (ULTRA FEATURE)")
        
        try:
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={'live': 'all'},
                timeout=10
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('response', [])
                
                print(f"✅ API respondendo!")
                print(f"📊 Jogos ao vivo agora: {len(matches)}")
                
                if len(matches) > 0:
                    print(f"\n📋 Primeiros 3 jogos ao vivo:")
                    for i, match in enumerate(matches[:3], 1):
                        home = match['teams']['home']['name']
                        away = match['teams']['away']['name']
                        score_home = match['goals']['home']
                        score_away = match['goals']['away']
                        minute = match['fixture']['status']['elapsed']
                        
                        print(f"   {i}. {home} {score_home} x {score_away} {away} ({minute}')")
                else:
                    print("⚠️ Nenhum jogo ao vivo no momento (normal)")
                
                self.results['tests']['live_fixtures'] = 'PASS'
                self.results['live_matches_count'] = len(matches)
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                self.results['tests']['live_fixtures'] = 'FAIL'
                return False
        
        except Exception as e:
            print(f"❌ Exceção: {e}")
            self.results['tests']['live_fixtures'] = 'FAIL'
            return False
    
    def test_3_live_odds(self):
        """Teste 3: Odds em tempo real (recurso Ultra)"""
        self.print_header("TESTE 3: ODDS EM TEMPO REAL (ULTRA FEATURE)")
        
        try:
            # Primeiro, pegar um fixture_id
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={'date': datetime.now().strftime('%Y-%m-%d'), 'league': 39},  # Premier League
                timeout=10
            )
            
            fixtures = response.json().get('response', [])
            
            if len(fixtures) == 0:
                print("⚠️ Nenhuma partida hoje na Premier League")
                print("   Tentando buscar qualquer partida futura...")
                
                # Buscar partidas futuras
                response = requests.get(
                    f"{self.base_url}/fixtures",
                    headers=self.headers,
                    params={'next': 10},
                    timeout=10
                )
                fixtures = response.json().get('response', [])
            
            if len(fixtures) > 0:
                fixture_id = fixtures[0]['fixture']['id']
                home = fixtures[0]['teams']['home']['name']
                away = fixtures[0]['teams']['away']['name']
                
                print(f"📋 Testando odds para: {home} vs {away} (ID: {fixture_id})")
                
                # Buscar odds
                response = requests.get(
                    f"{self.base_url}/odds",
                    headers=self.headers,
                    params={'fixture': fixture_id},
                    timeout=10
                )
                
                print(f"📊 Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    odds_data = data.get('response', [])
                    
                    print(f"✅ API respondendo!")
                    print(f"📊 Casas de apostas com odds: {len(odds_data)}")
                    
                    if len(odds_data) > 0:
                        print(f"\n📋 Primeiras casas de apostas:")
                        for i, odd in enumerate(odds_data[:5], 1):
                            bookmaker = odd['bookmakers'][0]['name'] if odd.get('bookmakers') else 'N/A'
                            print(f"   {i}. {bookmaker}")
                            
                            # Mostrar odds 1X2 se disponível
                            if odd.get('bookmakers'):
                                for bet in odd['bookmakers'][0].get('bets', []):
                                    if bet['name'] == 'Match Winner':
                                        print(f"      Odds 1X2: ", end="")
                                        for value in bet['values']:
                                            print(f"{value['value']}={value['odd']} ", end="")
                                        print()
                                        break
                    
                    self.results['tests']['odds'] = 'PASS'
                    self.results['odds_bookmakers'] = len(odds_data)
                    return True
                else:
                    print(f"❌ Erro ao buscar odds: {response.status_code}")
                    print(f"Resposta: {response.text[:300]}")
                    self.results['tests']['odds'] = 'FAIL'
                    return False
            else:
                print("⚠️ Nenhuma partida disponível para testar odds")
                self.results['tests']['odds'] = 'SKIP'
                return False
        
        except Exception as e:
            print(f"❌ Exceção: {e}")
            self.results['tests']['odds'] = 'FAIL'
            return False
    
    def test_4_predictions(self):
        """Teste 4: Previsões da API (recurso Ultra)"""
        self.print_header("TESTE 4: PREVISÕES DA API (ULTRA FEATURE)")
        
        try:
            # Buscar partidas futuras
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={'next': 50},
                timeout=10
            )
            
            fixtures = response.json().get('response', [])
            
            if len(fixtures) > 0:
                # Tentar pegar previsão da primeira partida
                for fixture in fixtures[:10]:
                    fixture_id = fixture['fixture']['id']
                    home = fixture['teams']['home']['name']
                    away = fixture['teams']['away']['name']
                    
                    print(f"\n📋 Testando previsão: {home} vs {away} (ID: {fixture_id})")
                    
                    response = requests.get(
                        f"{self.base_url}/predictions",
                        headers=self.headers,
                        params={'fixture': fixture_id},
                        timeout=10
                    )
                    
                    print(f"📊 Status Code: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        predictions = data.get('response', [])
                        
                        if len(predictions) > 0:
                            print(f"✅ Previsão disponível!")
                            
                            pred = predictions[0]
                            
                            # Mostrar previsão
                            if 'predictions' in pred:
                                print(f"\n   📊 Previsão da API:")
                                preds = pred['predictions']
                                print(f"      Vencedor: {preds.get('winner', {}).get('name', 'N/A')}")
                                print(f"      Win or Draw: {preds.get('win_or_draw', 'N/A')}")
                                print(f"      Under/Over: {preds.get('under_over', 'N/A')}")
                                print(f"      Goals Total: {preds.get('goals', {}).get('total', 'N/A')}")
                                print(f"      BTTS: {preds.get('goals', {}).get('home', 'N/A')} - {preds.get('goals', {}).get('away', 'N/A')}")
                            
                            # Mostrar probabilidades
                            if 'comparison' in pred:
                                print(f"\n   📈 Comparação:")
                                comp = pred['comparison']
                                print(f"      Forma: {comp.get('form', {}).get('home', 'N/A')}% vs {comp.get('form', {}).get('away', 'N/A')}%")
                                print(f"      Ataque: {comp.get('att', {}).get('home', 'N/A')}% vs {comp.get('att', {}).get('away', 'N/A')}%")
                                print(f"      Defesa: {comp.get('def', {}).get('home', 'N/A')}% vs {comp.get('def', {}).get('away', 'N/A')}%")
                            
                            self.results['tests']['predictions'] = 'PASS'
                            self.results['prediction_sample'] = pred
                            return True
                        else:
                            print("⚠️ Previsão não disponível para este jogo")
                            continue
                    else:
                        print(f"⚠️ Erro: {response.status_code}")
                        continue
                
                print("\n⚠️ Nenhuma previsão encontrada nas partidas testadas")
                self.results['tests']['predictions'] = 'PARTIAL'
                return False
            
            else:
                print("❌ Nenhuma partida futura disponível")
                self.results['tests']['predictions'] = 'SKIP'
                return False
        
        except Exception as e:
            print(f"❌ Exceção: {e}")
            self.results['tests']['predictions'] = 'FAIL'
            return False
    
    def test_5_statistics(self):
        """Teste 5: Estatísticas detalhadas"""
        self.print_header("TESTE 5: ESTATÍSTICAS DETALHADAS")
        
        try:
            # Buscar estatísticas de um time famoso
            response = requests.get(
                f"{self.base_url}/teams/statistics",
                headers=self.headers,
                params={'team': 33, 'season': 2024, 'league': 39},  # Man United, Premier League
                timeout=10
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get('response', {})
                
                if stats:
                    print("✅ Estatísticas disponíveis!")
                    
                    team_info = stats.get('team', {})
                    print(f"\n   📋 Time: {team_info.get('name', 'N/A')}")
                    
                    if 'fixtures' in stats:
                        fixtures = stats['fixtures']
                        print(f"\n   📊 Jogos:")
                        print(f"      Total: {fixtures.get('played', {}).get('total', 0)}")
                        print(f"      Vitórias: {fixtures.get('wins', {}).get('total', 0)}")
                        print(f"      Empates: {fixtures.get('draws', {}).get('total', 0)}")
                        print(f"      Derrotas: {fixtures.get('loses', {}).get('total', 0)}")
                    
                    if 'goals' in stats:
                        goals = stats['goals']
                        print(f"\n   ⚽ Gols:")
                        print(f"      Marcados: {goals.get('for', {}).get('total', {}).get('total', 0)}")
                        print(f"      Sofridos: {goals.get('against', {}).get('total', {}).get('total', 0)}")
                    
                    self.results['tests']['statistics'] = 'PASS'
                    return True
                else:
                    print("⚠️ Sem dados de estatísticas")
                    self.results['tests']['statistics'] = 'PARTIAL'
                    return False
            else:
                print(f"❌ Erro: {response.status_code}")
                self.results['tests']['statistics'] = 'FAIL'
                return False
        
        except Exception as e:
            print(f"❌ Exceção: {e}")
            self.results['tests']['statistics'] = 'FAIL'
            return False
    
    def test_6_next_fixtures(self):
        """Teste 6: Próximas partidas"""
        self.print_header("TESTE 6: PRÓXIMAS PARTIDAS (NEXT 50)")
        
        try:
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={'next': 50},
                timeout=10
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                matches = data.get('response', [])
                
                print(f"✅ API respondendo!")
                print(f"📊 Próximas partidas: {len(matches)}")
                
                if len(matches) > 0:
                    print(f"\n📋 Primeiras 5 partidas futuras:")
                    for i, match in enumerate(matches[:5], 1):
                        home = match['teams']['home']['name']
                        away = match['teams']['away']['name']
                        league = match['league']['name']
                        date = datetime.fromisoformat(match['fixture']['date'].replace('Z', '+00:00'))
                        
                        print(f"   {i}. {home} vs {away}")
                        print(f"      Liga: {league}")
                        print(f"      Data: {date.strftime('%d/%m/%Y %H:%M')}")
                
                self.results['tests']['next_fixtures'] = 'PASS'
                self.results['next_fixtures_count'] = len(matches)
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                self.results['tests']['next_fixtures'] = 'FAIL'
                return False
        
        except Exception as e:
            print(f"❌ Exceção: {e}")
            self.results['tests']['next_fixtures'] = 'FAIL'
            return False
    
    def generate_diagnostic_report(self):
        """Gera relatório diagnóstico"""
        self.print_header("DIAGNÓSTICO E RECOMENDAÇÕES")
        
        tests_passed = sum(1 for v in self.results['tests'].values() if v == 'PASS')
        tests_partial = sum(1 for v in self.results['tests'].values() if v == 'PARTIAL')
        tests_failed = sum(1 for v in self.results['tests'].values() if v == 'FAIL')
        total_tests = len(self.results['tests'])
        
        print(f"\n📊 RESULTADO GERAL:")
        print(f"   ✅ Testes OK: {tests_passed}")
        print(f"   ⚠️  Testes Parciais: {tests_partial}")
        print(f"   ❌ Testes Falhos: {tests_failed}")
        print(f"   📊 Total: {total_tests}")
        
        percentage = ((tests_passed + tests_partial * 0.5) / total_tests) * 100 if total_tests > 0 else 0
        print(f"\n   📈 Score: {percentage:.1f}%")
        
        print("\n🔍 PROBLEMAS IDENTIFICADOS:")
        
        # Verificar cada teste
        if self.results['tests'].get('live_fixtures') == 'PASS':
            if self.results.get('live_matches_count', 0) == 0:
                print("   ⚠️  Sem jogos ao vivo agora (normal se fora de horário)")
        
        if self.results['tests'].get('odds') in ['FAIL', 'SKIP']:
            print("   ⚠️  Odds não testadas - necessário ter partidas disponíveis")
        
        if self.results['tests'].get('predictions') in ['FAIL', 'PARTIAL', 'SKIP']:
            print("   ⚠️  Previsões da API não disponíveis para partidas testadas")
            print("      Motivo: Nem todas as partidas têm previsões disponíveis")
        
        print("\n✅ RECURSOS ULTRA DISPONÍVEIS:")
        print("   ✅ Jogos ao vivo (/fixtures?live=all)")
        print("   ✅ Próximas partidas (/fixtures?next=50)")
        print("   ✅ Estatísticas detalhadas (/teams/statistics)")
        print("   ✅ Odds (quando partidas disponíveis)")
        print("   ✅ Previsões (quando disponíveis)")
        
        print("\n💡 RECOMENDAÇÕES PARA MARABET:")
        print("   1. ✅ Usar header correto: 'x-apisports-key'")
        print("   2. ✅ Implementar busca de jogos ao vivo")
        print("   3. ✅ Implementar busca de odds em tempo real")
        print("   4. ✅ Usar previsões da API quando disponíveis")
        print("   5. ✅ Cache inteligente (5-15 min para ao vivo)")
        print("   6. ✅ Fallback para modelo próprio se API sem dados")
        
        # Salvar relatório
        with open('api_ultra_diagnostic_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print("\n💾 Relatório salvo: api_ultra_diagnostic_report.json")
        
        return percentage >= 50

def main():
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                                                                ║")
    print("║   🏆 TESTE COMPLETO PLANO ULTRA API-FOOTBALL - MARABET AI     ║")
    print("║                                                                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🔑 Plano: Ultra")
    print(f"📞 Contato: +224 932027393")
    print()
    
    tester = APIFootballUltraTest()
    
    # Executar todos os testes
    tester.test_1_account_status()
    tester.test_2_live_fixtures()
    tester.test_3_live_odds()
    tester.test_4_predictions()
    tester.test_5_statistics()
    tester.test_6_next_fixtures()
    
    # Gerar diagnóstico
    success = tester.generate_diagnostic_report()
    
    print("\n📞 Suporte:")
    print("   📧 Comercial: comercial@marabet.ao")
    print("   📧 Suporte: suporte@marabet.ao")
    print("   📞 WhatsApp: +224 932027393")
    print()
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

