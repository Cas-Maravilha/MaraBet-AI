#!/usr/bin/env python3
"""
Sistema Integrado MaraBet AI com Múltiplas APIs de Futebol
Integra Football API e football-data.org para dados completos
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

class MultiAPIFootballSystem:
    """Sistema integrado com múltiplas APIs de futebol"""
    
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
                    logger.warning(f"⚠️ Football API: Nenhum resultado encontrado para {endpoint}")
                    return None
            else:
                logger.error(f"❌ Football API HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na requisição Football API para {endpoint}: {e}")
            return None
    
    def make_football_data_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Faz requisição para football-data.org"""
        try:
            url = f"{self.football_data_url}/{endpoint}"
            response = requests.get(url, headers=self.football_data_headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ football-data.org: Dados obtidos para {endpoint}")
                return data
            else:
                logger.error(f"❌ football-data.org HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na requisição football-data.org para {endpoint}: {e}")
            return None
    
    def get_football_data_competitions(self) -> List[Dict]:
        """Obtém competições da football-data.org"""
        data = self.make_football_data_request('competitions')
        if data:
            competitions = data.get('competitions', [])
            logger.info(f"✅ {len(competitions)} competições encontradas na football-data.org")
            return competitions
        return []
    
    def get_football_data_teams(self, competition_code: str) -> List[Dict]:
        """Obtém equipes de uma competição específica"""
        endpoint = f'competitions/{competition_code}/teams'
        data = self.make_football_data_request(endpoint)
        if data:
            teams = data.get('teams', [])
            logger.info(f"✅ {len(teams)} equipes encontradas na competição {competition_code}")
            return teams
        return []
    
    def get_football_data_matches(self, competition_code: str = None, date_from: str = None, date_to: str = None) -> List[Dict]:
        """Obtém partidas da football-data.org"""
        endpoint = 'matches'
        params = {}
        
        if competition_code:
            params['competitions'] = competition_code
        if date_from:
            params['dateFrom'] = date_from
        if date_to:
            params['dateTo'] = date_to
            
        data = self.make_football_data_request(endpoint, params)
        if data:
            matches = data.get('matches', [])
            logger.info(f"✅ {len(matches)} partidas encontradas na football-data.org")
            return matches
        return []
    
    def get_football_data_standings(self, competition_code: str) -> List[Dict]:
        """Obtém classificação da football-data.org"""
        endpoint = f'competitions/{competition_code}/standings'
        data = self.make_football_data_request(endpoint)
        if data:
            standings = data.get('standings', [])
            if standings:
                logger.info(f"✅ Classificação obtida para {competition_code}")
                return standings[0].get('table', [])
        return []
    
    def get_football_data_team_matches(self, team_id: int, limit: int = 10) -> List[Dict]:
        """Obtém partidas de uma equipe específica"""
        endpoint = f'teams/{team_id}/matches'
        params = {'limit': limit}
        
        data = self.make_football_data_request(endpoint, params)
        if data:
            matches = data.get('matches', [])
            logger.info(f"✅ {len(matches)} partidas encontradas para equipe {team_id}")
            return matches
        return []
    
    def get_football_data_team_info(self, team_id: int) -> Dict:
        """Obtém informações detalhadas de uma equipe"""
        endpoint = f'teams/{team_id}'
        data = self.make_football_data_request(endpoint)
        if data:
            logger.info(f"✅ Informações obtidas para equipe {team_id}")
            return data
        return {}
    
    def collect_comprehensive_multi_api_data(self):
        """Coleta dados abrangentes de ambas as APIs"""
        logger.info("🚀 Iniciando coleta abrangente de múltiplas APIs...")
        
        all_data = {
            'football_api_data': {},
            'football_data_org_data': {},
            'combined_analysis': {},
            'collection_timestamp': datetime.now().isoformat()
        }
        
        # Coletar dados da Football API
        logger.info("📊 Coletando dados da Football API...")
        try:
            # Partidas de hoje
            today = datetime.now().strftime('%Y-%m-%d')
            football_api_matches = self.make_football_api_request('fixtures', {'date': today})
            if football_api_matches:
                all_data['football_api_data']['today_matches'] = football_api_matches.get('response', [])
            
            # Classificações das ligas principais
            league_ids = [39, 140, 78, 135, 61]  # Premier League, La Liga, Bundesliga, Serie A, Ligue 1
            standings = {}
            for league_id in league_ids:
                standings_data = self.make_football_api_request('standings', {'league': league_id, 'season': 2024})
                if standings_data:
                    standings[league_id] = standings_data.get('response', [])
                time.sleep(1)  # Rate limiting
            
            all_data['football_api_data']['standings'] = standings
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados da Football API: {e}")
        
        # Coletar dados da football-data.org
        logger.info("📊 Coletando dados da football-data.org...")
        try:
            # Competições
            competitions = self.get_football_data_competitions()
            all_data['football_data_org_data']['competitions'] = competitions
            
            # Partidas de hoje
            today_matches = self.get_football_data_matches(date_from=today, date_to=today)
            all_data['football_data_org_data']['today_matches'] = today_matches
            
            # Classificações das competições principais
            main_competitions = ['PL', 'PD', 'BL1', 'SA', 'FL1']  # Premier League, La Liga, Bundesliga, Serie A, Ligue 1
            football_data_standings = {}
            for comp_code in main_competitions:
                standings = self.get_football_data_standings(comp_code)
                if standings:
                    football_data_standings[comp_code] = standings
                time.sleep(1)  # Rate limiting
            
            all_data['football_data_org_data']['standings'] = football_data_standings
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados da football-data.org: {e}")
        
        # Combinar e analisar dados
        logger.info("🔄 Combinando e analisando dados...")
        try:
            combined_analysis = self.combine_and_analyze_data(all_data)
            all_data['combined_analysis'] = combined_analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao combinar dados: {e}")
        
        logger.info("✅ Coleta abrangente de múltiplas APIs concluída!")
        return all_data
    
    def combine_and_analyze_data(self, data: Dict) -> Dict:
        """Combina dados de ambas as APIs e gera análise"""
        analysis = {
            'total_matches_football_api': len(data['football_api_data'].get('today_matches', [])),
            'total_matches_football_data_org': len(data['football_data_org_data'].get('today_matches', [])),
            'competitions_available': len(data['football_data_org_data'].get('competitions', [])),
            'standings_comparison': {},
            'enhanced_matches': []
        }
        
        # Comparar classificações
        football_api_standings = data['football_api_data'].get('standings', {})
        football_data_standings = data['football_data_org_data'].get('standings', {})
        
        # Mapear códigos de competição
        competition_mapping = {
            39: 'PL',    # Premier League
            140: 'PD',   # La Liga
            78: 'BL1',   # Bundesliga
            135: 'SA',   # Serie A
            61: 'FL1'    # Ligue 1
        }
        
        for league_id, comp_code in competition_mapping.items():
            if league_id in football_api_standings and comp_code in football_data_standings:
                analysis['standings_comparison'][league_id] = {
                    'football_api_teams': len(football_api_standings[league_id]),
                    'football_data_org_teams': len(football_data_standings[comp_code]),
                    'data_consistency': 'Available'
                }
        
        # Analisar partidas combinadas
        football_api_matches = data['football_api_data'].get('today_matches', [])
        football_data_matches = data['football_data_org_data'].get('today_matches', [])
        
        # Criar análise combinada das primeiras 5 partidas
        for i in range(min(5, len(football_api_matches))):
            try:
                match = football_api_matches[i]
                enhanced_match = self.enhance_match_with_dual_data(match, football_data_matches)
                if enhanced_match:
                    analysis['enhanced_matches'].append(enhanced_match)
            except Exception as e:
                logger.error(f"❌ Erro ao analisar partida {i}: {e}")
        
        return analysis
    
    def enhance_match_with_dual_data(self, football_api_match: Dict, football_data_matches: List[Dict]) -> Optional[Dict]:
        """Melhora dados da partida combinando informações de ambas as APIs"""
        try:
            teams = football_api_match['teams']
            league = football_api_match['league']
            fixture = football_api_match['fixture']
            
            # Buscar partida correspondente na football-data.org
            corresponding_match = None
            for fd_match in football_data_matches:
                if (fd_match.get('homeTeam', {}).get('name') == teams['home']['name'] and
                    fd_match.get('awayTeam', {}).get('name') == teams['away']['name']):
                    corresponding_match = fd_match
                    break
            
            enhanced_match = {
                'match_id': fixture['id'],
                'home_team': teams['home']['name'],
                'away_team': teams['away']['name'],
                'league': league['name'],
                'country': league.get('country', 'Unknown'),
                'date': fixture['date'],
                'venue': fixture.get('venue', {}).get('name', 'Unknown'),
                'referee': fixture.get('referee', 'Unknown'),
                'football_api_data': {
                    'home_team_id': teams['home']['id'],
                    'away_team_id': teams['away']['id'],
                    'league_id': league['id'],
                    'season': league.get('season', 2024),
                    'round': league.get('round', 'Regular Season')
                },
                'football_data_org_data': corresponding_match,
                'data_source': 'Combined',
                'enhancement_timestamp': datetime.now().isoformat()
            }
            
            return enhanced_match
            
        except Exception as e:
            logger.error(f"❌ Erro ao melhorar dados da partida: {e}")
            return None
    
    def save_multi_api_data(self, data: Dict, filename: str = None):
        """Salva dados combinados em arquivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"multi_api_football_data_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Dados combinados salvos em {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Erro ao salvar arquivo: {e}")
            return None
    
    def print_multi_api_summary(self, data: Dict):
        """Imprime resumo dos dados combinados"""
        print("\n📊 RESUMO DOS DADOS COMBINADOS:")
        print("=" * 60)
        
        # Estatísticas gerais
        football_api_matches = len(data['football_api_data'].get('today_matches', []))
        football_data_matches = len(data['football_data_org_data'].get('today_matches', []))
        competitions = len(data['football_data_org_data'].get('competitions', []))
        
        print(f"📅 Partidas Football API: {football_api_matches}")
        print(f"📅 Partidas football-data.org: {football_data_matches}")
        print(f"🏆 Competições disponíveis: {competitions}")
        
        # Análise combinada
        analysis = data.get('combined_analysis', {})
        print(f"🔄 Partidas analisadas combinadamente: {len(analysis.get('enhanced_matches', []))}")
        
        # Comparação de classificações
        standings_comparison = analysis.get('standings_comparison', {})
        if standings_comparison:
            print("\n📊 COMPARAÇÃO DE CLASSIFICAÇÕES:")
            for league_id, comparison in standings_comparison.items():
                league_names = {39: 'Premier League', 140: 'La Liga', 78: 'Bundesliga', 135: 'Serie A', 61: 'Ligue 1'}
                league_name = league_names.get(league_id, f'League {league_id}')
                print(f"   {league_name}:")
                print(f"      Football API: {comparison['football_api_teams']} equipes")
                print(f"      football-data.org: {comparison['football_data_org_teams']} equipes")
        
        # Partidas melhoradas
        enhanced_matches = analysis.get('enhanced_matches', [])
        if enhanced_matches:
            print("\n🏆 PARTIDAS COM DADOS COMBINADOS:")
            for i, match in enumerate(enhanced_matches, 1):
                print(f"{i}. {match['home_team']} vs {match['away_team']}")
                print(f"   🏟️ {match['league']} | 📅 {match['date'][:10]}")
                print(f"   📊 Fonte: {match['data_source']}")
                if match['football_data_org_data']:
                    print(f"   ✅ Dados complementares disponíveis")
                else:
                    print(f"   ⚠️ Apenas dados Football API")

def main():
    # Chaves das APIs fornecidas pelo usuário
    FOOTBALL_API_KEY = "71b2b62386f2d1275cd3201a73e1e045"
    FOOTBALL_DATA_TOKEN = "721b0aaec5794327bab715da2abc7a7b"
    
    print("🎯 MARABET AI - SISTEMA INTEGRADO COM MÚLTIPLAS APIs")
    print("=" * 60)
    
    # Inicializar sistema multi-API
    system = MultiAPIFootballSystem(FOOTBALL_API_KEY, FOOTBALL_DATA_TOKEN)
    
    print(f"🔑 Football API Key: {FOOTBALL_API_KEY[:10]}...")
    print(f"🔑 football-data.org Token: {FOOTBALL_DATA_TOKEN[:10]}...")
    print("📊 Iniciando coleta de dados de múltiplas APIs...")
    
    try:
        # Coletar dados abrangentes
        data = system.collect_comprehensive_multi_api_data()
        
        # Salvar dados
        filename = system.save_multi_api_data(data)
        
        # Imprimir resumo
        system.print_multi_api_summary(data)
        
        print(f"\n✅ COLETA DE MÚLTIPLAS APIs CONCLUÍDA!")
        if filename:
            print(f"📁 Arquivo salvo: {filename}")
        print("🎯 Sistema integrado com Football API e football-data.org!")
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta de múltiplas APIs: {e}")
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
