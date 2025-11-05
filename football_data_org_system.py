#!/usr/bin/env python3
"""
Sistema Especializado football-data.org MaraBet AI
Coleta dados específicos e detalhados da football-data.org
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

class FootballDataOrgSystem:
    """Sistema especializado para football-data.org"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {
            'X-Auth-Token': token
        }
        
    def make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Faz requisição para football-data.org"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
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
    
    def get_all_competitions(self) -> List[Dict]:
        """Obtém todas as competições disponíveis"""
        data = self.make_request('competitions')
        if data:
            competitions = data.get('competitions', [])
            logger.info(f"✅ {len(competitions)} competições encontradas")
            return competitions
        return []
    
    def get_competition_details(self, competition_code: str) -> Dict:
        """Obtém detalhes de uma competição específica"""
        endpoint = f'competitions/{competition_code}'
        data = self.make_request(endpoint)
        if data:
            logger.info(f"✅ Detalhes obtidos para competição {competition_code}")
            return data
        return {}
    
    def get_competition_teams(self, competition_code: str) -> List[Dict]:
        """Obtém equipes de uma competição"""
        endpoint = f'competitions/{competition_code}/teams'
        data = self.make_request(endpoint)
        if data:
            teams = data.get('teams', [])
            logger.info(f"✅ {len(teams)} equipes encontradas na competição {competition_code}")
            return teams
        return []
    
    def get_competition_standings(self, competition_code: str) -> List[Dict]:
        """Obtém classificação de uma competição"""
        endpoint = f'competitions/{competition_code}/standings'
        data = self.make_request(endpoint)
        if data:
            standings = data.get('standings', [])
            if standings:
                table = standings[0].get('table', [])
                logger.info(f"✅ Classificação obtida para {competition_code}: {len(table)} equipes")
                return table
        return []
    
    def get_competition_matches(self, competition_code: str, season: int = None) -> List[Dict]:
        """Obtém partidas de uma competição"""
        endpoint = f'competitions/{competition_code}/matches'
        params = {}
        if season:
            params['season'] = season
            
        data = self.make_request(endpoint, params)
        if data:
            matches = data.get('matches', [])
            logger.info(f"✅ {len(matches)} partidas encontradas na competição {competition_code}")
            return matches
        return []
    
    def get_upcoming_matches(self, competition_codes: List[str] = None, days_ahead: int = 7) -> List[Dict]:
        """Obtém partidas dos próximos dias"""
        endpoint = 'matches'
        
        # Calcular datas
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        
        params = {
            'dateFrom': date_from,
            'dateTo': date_to
        }
        
        if competition_codes:
            params['competitions'] = ','.join(competition_codes)
        
        data = self.make_request(endpoint, params)
        if data:
            matches = data.get('matches', [])
            logger.info(f"✅ {len(matches)} partidas encontradas para os próximos {days_ahead} dias")
            return matches
        return []
    
    def get_team_details(self, team_id: int) -> Dict:
        """Obtém detalhes de uma equipe"""
        endpoint = f'teams/{team_id}'
        data = self.make_request(endpoint)
        if data:
            logger.info(f"✅ Detalhes obtidos para equipe {team_id}")
            return data
        return {}
    
    def get_team_matches(self, team_id: int, limit: int = 10) -> List[Dict]:
        """Obtém partidas de uma equipe"""
        endpoint = f'teams/{team_id}/matches'
        params = {'limit': limit}
        
        data = self.make_request(endpoint, params)
        if data:
            matches = data.get('matches', [])
            logger.info(f"✅ {len(matches)} partidas encontradas para equipe {team_id}")
            return matches
        return []
    
    def analyze_competition_data(self, competition_code: str):
        """Analisa dados completos de uma competição"""
        logger.info(f"🔍 Analisando dados da competição {competition_code}...")
        
        analysis = {
            'competition_code': competition_code,
            'competition_details': {},
            'teams': [],
            'standings': [],
            'upcoming_matches': [],
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        try:
            # Obter detalhes da competição
            details = self.get_competition_details(competition_code)
            analysis['competition_details'] = details
            
            # Obter equipes
            teams = self.get_competition_teams(competition_code)
            analysis['teams'] = teams
            
            # Obter classificação
            standings = self.get_competition_standings(competition_code)
            analysis['standings'] = standings
            
            # Obter partidas futuras
            upcoming = self.get_upcoming_matches([competition_code], days_ahead=14)
            analysis['upcoming_matches'] = upcoming
            
            logger.info(f"✅ Análise completa da competição {competition_code}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar competição {competition_code}: {e}")
        
        return analysis
    
    def collect_comprehensive_data(self):
        """Coleta dados abrangentes da football-data.org"""
        logger.info("🚀 Iniciando coleta abrangente da football-data.org...")
        
        all_data = {
            'competitions': [],
            'main_competitions_analysis': {},
            'upcoming_matches': [],
            'collection_timestamp': datetime.now().isoformat()
        }
        
        try:
            # Obter todas as competições
            competitions = self.get_all_competitions()
            all_data['competitions'] = competitions
            
            # Analisar competições principais
            main_competitions = ['PL', 'PD', 'BL1', 'SA', 'FL1', 'CL', 'EL']  # Premier League, La Liga, Bundesliga, Serie A, Ligue 1, Champions League, Europa League
            
            for comp_code in main_competitions:
                try:
                    analysis = self.analyze_competition_data(comp_code)
                    all_data['main_competitions_analysis'][comp_code] = analysis
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    logger.error(f"❌ Erro ao analisar competição {comp_code}: {e}")
            
            # Obter partidas futuras das competições principais
            upcoming = self.get_upcoming_matches(main_competitions, days_ahead=7)
            all_data['upcoming_matches'] = upcoming
            
        except Exception as e:
            logger.error(f"❌ Erro na coleta abrangente: {e}")
        
        logger.info("✅ Coleta abrangente da football-data.org concluída!")
        return all_data
    
    def save_data(self, data: Dict, filename: str = None):
        """Salva dados em arquivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"football_data_org_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Dados salvos em {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Erro ao salvar arquivo: {e}")
            return None
    
    def print_data_summary(self, data: Dict):
        """Imprime resumo dos dados coletados"""
        print("\n📊 RESUMO DOS DADOS FOOTBALL-DATA.ORG:")
        print("=" * 60)
        
        competitions = data.get('competitions', [])
        main_analysis = data.get('main_competitions_analysis', {})
        upcoming_matches = data.get('upcoming_matches', [])
        
        print(f"🏆 Total de competições: {len(competitions)}")
        print(f"📊 Competições principais analisadas: {len(main_analysis)}")
        print(f"📅 Partidas futuras: {len(upcoming_matches)}")
        
        # Mostrar competições principais
        if main_analysis:
            print("\n🏆 COMPETIÇÕES PRINCIPAIS:")
            competition_names = {
                'PL': 'Premier League',
                'PD': 'La Liga',
                'BL1': 'Bundesliga',
                'SA': 'Serie A',
                'FL1': 'Ligue 1',
                'CL': 'Champions League',
                'EL': 'Europa League'
            }
            
            for comp_code, analysis in main_analysis.items():
                comp_name = competition_names.get(comp_code, comp_code)
                teams_count = len(analysis.get('teams', []))
                standings_count = len(analysis.get('standings', []))
                upcoming_count = len(analysis.get('upcoming_matches', []))
                
                print(f"\n📊 {comp_name} ({comp_code}):")
                print(f"   ⚽ Equipes: {teams_count}")
                print(f"   📈 Classificação: {standings_count} posições")
                print(f"   📅 Próximas partidas: {upcoming_count}")
                
                # Mostrar top 3 da classificação
                standings = analysis.get('standings', [])
                if standings:
                    print(f"   🏆 Top 3:")
                    for i, team in enumerate(standings[:3], 1):
                        print(f"      {i}. {team.get('team', {}).get('name', 'N/A')} - {team.get('points', 0)} pts")
        
        # Mostrar algumas partidas futuras
        if upcoming_matches:
            print("\n📅 PRÓXIMAS PARTIDAS:")
            for i, match in enumerate(upcoming_matches[:5], 1):
                home_team = match.get('homeTeam', {}).get('name', 'N/A')
                away_team = match.get('awayTeam', {}).get('name', 'N/A')
                competition = match.get('competition', {}).get('name', 'N/A')
                date = match.get('utcDate', 'N/A')[:10]
                
                print(f"{i}. {home_team} vs {away_team}")
                print(f"   📅 {date} | 🏟️ {competition}")

def main():
    # Token da API fornecido pelo usuário
    TOKEN = "721b0aaec5794327bab715da2abc7a7b"
    
    print("🎯 MARABET AI - SISTEMA ESPECIALIZADO FOOTBALL-DATA.ORG")
    print("=" * 60)
    
    # Inicializar sistema
    system = FootballDataOrgSystem(TOKEN)
    
    print(f"🔑 Token configurado: {TOKEN[:10]}...")
    print("📊 Iniciando coleta de dados da football-data.org...")
    
    try:
        # Coletar dados abrangentes
        data = system.collect_comprehensive_data()
        
        # Salvar dados
        filename = system.save_data(data)
        
        # Imprimir resumo
        system.print_data_summary(data)
        
        print(f"\n✅ COLETA DA FOOTBALL-DATA.ORG CONCLUÍDA!")
        if filename:
            print(f"📁 Arquivo salvo: {filename}")
        print("🎯 Sistema integrado com football-data.org!")
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta: {e}")
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
