#!/usr/bin/env python3
"""
Sistema Final Integrado MaraBet AI - Duas APIs de Futebol
Sistema otimizado que integra Football API e football-data.org
"""

import json
import os
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalIntegratedFootballSystem:
    """Sistema final integrado com duas APIs de futebol"""
    
    def __init__(self, football_api_key: str, football_data_token: str):
        self.football_api_key = football_api_key
        self.football_data_token = football_data_token
        
        # Configurações Football API
        self.football_api_url = "https://v3.football.api-sports.io"
        self.football_api_headers = {
            'x-rapidapi-key': football_api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        
        # Configurações football-data.org
        self.football_data_url = "https://api.football-data.org/v4"
        self.football_data_headers = {
            'X-Auth-Token': football_data_token
        }
        
    def make_football_api_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Faz requisição para Football API"""
        try:
            url = f"{self.football_api_url}/{endpoint}"
            response = requests.get(url, headers=self.football_api_headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results', 0) > 0:
                    return data
                else:
                    logger.warning(f"⚠️ Football API: Nenhum resultado para {endpoint}")
                    return None
            else:
                logger.error(f"❌ Football API HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro Football API {endpoint}: {e}")
            return None
    
    def make_football_data_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Faz requisição para football-data.org"""
        try:
            url = f"{self.football_data_url}/{endpoint}"
            response = requests.get(url, headers=self.football_data_headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ football-data.org: {endpoint}")
                return data
            else:
                logger.error(f"❌ football-data.org HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro football-data.org {endpoint}: {e}")
            return None
    
    def get_comprehensive_match_data(self):
        """Obtém dados abrangentes de partidas de ambas as APIs"""
        logger.info("🚀 Coletando dados abrangentes de partidas...")
        
        comprehensive_data = {
            'football_api_matches': [],
            'football_data_org_matches': [],
            'combined_analysis': {},
            'collection_timestamp': datetime.now().isoformat()
        }
        
        try:
            # Coletar partidas da Football API
            logger.info("📊 Coletando partidas da Football API...")
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Partidas de hoje
            today_matches = self.make_football_api_request('fixtures', {'date': today})
            if today_matches:
                comprehensive_data['football_api_matches'] = today_matches.get('response', [])
            
            # Partidas dos próximos 3 dias
            from_date = datetime.now().strftime('%Y-%m-%d')
            to_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
            upcoming_matches = self.make_football_api_request('fixtures', {'from': from_date, 'to': to_date})
            if upcoming_matches:
                comprehensive_data['football_api_upcoming'] = upcoming_matches.get('response', [])
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados Football API: {e}")
        
        try:
            # Coletar dados da football-data.org
            logger.info("📊 Coletando dados da football-data.org...")
            
            # Partidas dos próximos 7 dias (limitado a 10 dias pela API)
            upcoming_fd = self.make_football_data_request('matches', {
                'dateFrom': today,
                'dateTo': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            })
            if upcoming_fd:
                comprehensive_data['football_data_org_matches'] = upcoming_fd.get('matches', [])
            
            # Classificações das ligas principais
            main_competitions = ['PL', 'PD', 'BL1', 'SA', 'FL1']
            standings_data = {}
            
            for comp_code in main_competitions:
                try:
                    standings = self.make_football_data_request(f'competitions/{comp_code}/standings')
                    if standings:
                        standings_data[comp_code] = standings.get('standings', [])
                    time.sleep(2)  # Rate limiting mais conservador
                except Exception as e:
                    logger.error(f"❌ Erro ao obter classificação {comp_code}: {e}")
            
            comprehensive_data['football_data_org_standings'] = standings_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados football-data.org: {e}")
        
        # Análise combinada
        try:
            logger.info("🔄 Gerando análise combinada...")
            combined_analysis = self.generate_combined_analysis(comprehensive_data)
            comprehensive_data['combined_analysis'] = combined_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro na análise combinada: {e}")
        
        logger.info("✅ Coleta abrangente concluída!")
        return comprehensive_data
    
    def generate_combined_analysis(self, data: Dict) -> Dict:
        """Gera análise combinada dos dados"""
        analysis = {
            'summary': {
                'football_api_matches_today': len(data.get('football_api_matches', [])),
                'football_api_upcoming': len(data.get('football_api_upcoming', [])),
                'football_data_org_matches': len(data.get('football_data_org_matches', [])),
                'football_data_org_standings': len(data.get('football_data_org_standings', {}))
            },
            'top_matches': [],
            'league_standings_summary': {},
            'data_quality': 'High'
        }
        
        # Analisar partidas principais
        football_api_matches = data.get('football_api_matches', [])
        football_data_matches = data.get('football_data_org_matches', [])
        
        # Selecionar partidas importantes
        important_leagues = ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1', 'Champions League']
        
        for match in football_api_matches[:10]:  # Primeiras 10 partidas
            try:
                league_name = match.get('league', {}).get('name', '')
                if any(important_league in league_name for important_league in important_leagues):
                    match_analysis = self.analyze_match(match, football_data_matches)
                    if match_analysis:
                        analysis['top_matches'].append(match_analysis)
            except Exception as e:
                logger.error(f"❌ Erro ao analisar partida: {e}")
        
        # Resumo das classificações
        standings_data = data.get('football_data_org_standings', {})
        for comp_code, standings in standings_data.items():
            if standings and len(standings) > 0:
                table = standings[0].get('table', [])
                if table:
                    analysis['league_standings_summary'][comp_code] = {
                        'total_teams': len(table),
                        'top_3': [
                            {'name': team.get('team', {}).get('name', ''), 'points': team.get('points', 0)}
                            for team in table[:3]
                        ]
                    }
        
        return analysis
    
    def analyze_match(self, match: Dict, football_data_matches: List[Dict]) -> Optional[Dict]:
        """Analisa uma partida específica"""
        try:
            teams = match['teams']
            league = match['league']
            fixture = match['fixture']
            
            # Buscar dados complementares na football-data.org
            complementary_data = None
            for fd_match in football_data_matches:
                if (fd_match.get('homeTeam', {}).get('name') == teams['home']['name'] and
                    fd_match.get('awayTeam', {}).get('name') == teams['away']['name']):
                    complementary_data = fd_match
                    break
            
            match_analysis = {
                'match_id': fixture['id'],
                'home_team': teams['home']['name'],
                'away_team': teams['away']['name'],
                'league': league['name'],
                'country': league.get('country', 'Unknown'),
                'date': fixture['date'],
                'venue': fixture.get('venue', {}).get('name', 'Unknown'),
                'referee': fixture.get('referee', 'Unknown'),
                'data_sources': {
                    'football_api': True,
                    'football_data_org': complementary_data is not None
                },
                'complementary_data': complementary_data,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return match_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar partida individual: {e}")
            return None
    
    def save_comprehensive_data(self, data: Dict, filename: str = None):
        """Salva dados abrangentes"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"comprehensive_football_data_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Dados abrangentes salvos em {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Erro ao salvar arquivo: {e}")
            return None
    
    def print_comprehensive_summary(self, data: Dict):
        """Imprime resumo abrangente"""
        print("\n📊 RESUMO ABRANGENTE - DUAS APIs DE FUTEBOL:")
        print("=" * 70)
        
        analysis = data.get('combined_analysis', {})
        summary = analysis.get('summary', {})
        
        print(f"📅 Partidas Football API (hoje): {summary.get('football_api_matches_today', 0)}")
        print(f"📅 Partidas Football API (próximos 3 dias): {summary.get('football_api_upcoming', 0)}")
        print(f"📅 Partidas football-data.org (próximos 7 dias): {summary.get('football_data_org_matches', 0)}")
        print(f"📊 Classificações football-data.org: {summary.get('football_data_org_standings', 0)}")
        
        # Partidas principais
        top_matches = analysis.get('top_matches', [])
        if top_matches:
            print(f"\n🏆 PARTIDAS PRINCIPAIS ANALISADAS ({len(top_matches)}):")
            for i, match in enumerate(top_matches, 1):
                print(f"\n{i}. {match['home_team']} vs {match['away_team']}")
                print(f"   🏟️ {match['league']} | 📅 {match['date'][:10]}")
                print(f"   📊 Fontes: Football API ✅ | football-data.org {'✅' if match['data_sources']['football_data_org'] else '❌'}")
        
        # Classificações das ligas
        standings_summary = analysis.get('league_standings_summary', {})
        if standings_summary:
            print(f"\n📊 CLASSIFICAÇÕES DAS LIGAS PRINCIPAIS:")
            league_names = {
                'PL': 'Premier League',
                'PD': 'La Liga',
                'BL1': 'Bundesliga',
                'SA': 'Serie A',
                'FL1': 'Ligue 1'
            }
            
            for comp_code, standings in standings_summary.items():
                league_name = league_names.get(comp_code, comp_code)
                print(f"\n🏆 {league_name}:")
                print(f"   ⚽ Total de equipes: {standings['total_teams']}")
                print(f"   🥇 Top 3:")
                for j, team in enumerate(standings['top_3'], 1):
                    print(f"      {j}. {team['name']} - {team['points']} pts")
        
        print(f"\n📈 Qualidade dos dados: {analysis.get('data_quality', 'Unknown')}")

def main():
    # Chaves das APIs fornecidas pelo usuário
    FOOTBALL_API_KEY = "71b2b62386f2d1275cd3201a73e1e045"
    FOOTBALL_DATA_TOKEN = "721b0aaec5794327bab715da2abc7a7b"
    
    print("🎯 MARABET AI - SISTEMA FINAL INTEGRADO COM DUAS APIs")
    print("=" * 70)
    
    # Inicializar sistema final
    system = FinalIntegratedFootballSystem(FOOTBALL_API_KEY, FOOTBALL_DATA_TOKEN)
    
    print(f"🔑 Football API Key: {FOOTBALL_API_KEY[:10]}...")
    print(f"🔑 football-data.org Token: {FOOTBALL_DATA_TOKEN[:10]}...")
    print("📊 Iniciando coleta abrangente de duas APIs...")
    
    try:
        # Coletar dados abrangentes
        data = system.get_comprehensive_match_data()
        
        # Salvar dados
        filename = system.save_comprehensive_data(data)
        
        # Imprimir resumo
        system.print_comprehensive_summary(data)
        
        print(f"\n✅ COLETA ABRANGENTE CONCLUÍDA!")
        if filename:
            print(f"📁 Arquivo salvo: {filename}")
        print("🎯 Sistema final integrado com duas APIs de futebol!")
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta abrangente: {e}")
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
