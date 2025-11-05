#!/usr/bin/env python3
"""
Sistema de Coleta de Partidas e Estatísticas Reais MaraBet AI
Coleta dados específicos de partidas e estatísticas usando Football API
"""

import json
import os
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealMatchDataCollector:
    """Coletor de dados reais de partidas"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        self.db_path = "real_football_data.db"
        
    def make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Faz requisição para a API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results') > 0:
                    return data
                else:
                    logger.warning(f"⚠️ Nenhum resultado encontrado para {endpoint}")
                    return None
            else:
                logger.error(f"❌ Erro HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na requisição para {endpoint}: {e}")
            return None
    
    def get_today_matches(self) -> List[Dict]:
        """Obtém partidas de hoje"""
        today = datetime.now().strftime('%Y-%m-%d')
        params = {'date': today}
        
        data = self.make_request('fixtures', params)
        if data:
            matches = data.get('response', [])
            logger.info(f"✅ {len(matches)} partidas encontradas para hoje ({today})")
            return matches
        return []
    
    def get_upcoming_matches(self, league_id: int = None, days: int = 3) -> List[Dict]:
        """Obtém partidas dos próximos dias"""
        from_date = datetime.now().strftime('%Y-%m-%d')
        to_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        params = {
            'from': from_date,
            'to': to_date
        }
        
        if league_id:
            params['league'] = league_id
            
        data = self.make_request('fixtures', params)
        if data:
            matches = data.get('response', [])
            logger.info(f"✅ {len(matches)} partidas encontradas para os próximos {days} dias")
            return matches
        return []
    
    def get_match_statistics(self, fixture_id: int) -> Dict:
        """Obtém estatísticas detalhadas de uma partida"""
        params = {'fixture': fixture_id}
        
        data = self.make_request('fixtures/statistics', params)
        if data:
            stats = data.get('response', [])
            logger.info(f"✅ Estatísticas obtidas para partida {fixture_id}")
            return stats
        return []
    
    def get_team_statistics(self, team_id: int, league_id: int, season: int = 2024) -> Dict:
        """Obtém estatísticas da equipe"""
        params = {
            'team': team_id,
            'league': league_id,
            'season': season
        }
        
        data = self.make_request('teams/statistics', params)
        if data:
            stats = data.get('response', [])
            if stats:
                logger.info(f"✅ Estatísticas obtidas para equipe {team_id}")
                return stats[0]
        return {}
    
    def get_head_to_head(self, team1_id: int, team2_id: int, last: int = 5) -> List[Dict]:
        """Obtém histórico de confrontos diretos"""
        params = {
            'h2h': f"{team1_id}-{team2_id}",
            'last': last
        }
        
        data = self.make_request('fixtures/headtohead', params)
        if data:
            h2h = data.get('response', [])
            logger.info(f"✅ {len(h2h)} confrontos diretos encontrados")
            return h2h
        return []
    
    def get_league_standings(self, league_id: int, season: int = 2024) -> List[Dict]:
        """Obtém classificação da liga"""
        params = {
            'league': league_id,
            'season': season
        }
        
        data = self.make_request('standings', params)
        if data:
            standings = data.get('response', [])
            if standings:
                logger.info(f"✅ Classificação obtida para liga {league_id}")
                return standings[0]['league']['standings'][0]
        return []
    
    def get_team_players(self, team_id: int, season: int = 2024) -> List[Dict]:
        """Obtém jogadores da equipe"""
        params = {
            'team': team_id,
            'season': season
        }
        
        data = self.make_request('players/squads', params)
        if data:
            players = data.get('response', [])
            if players:
                logger.info(f"✅ {len(players[0]['players'])} jogadores encontrados para equipe {team_id}")
                return players[0]['players']
        return []
    
    def get_injuries(self, team_id: int = None, league_id: int = None) -> List[Dict]:
        """Obtém informações sobre lesões"""
        params = {}
        if team_id:
            params['team'] = team_id
        if league_id:
            params['league'] = league_id
            
        data = self.make_request('injuries', params)
        if data:
            injuries = data.get('response', [])
            logger.info(f"✅ {len(injuries)} lesões encontradas")
            return injuries
        return []
    
    def collect_comprehensive_match_data(self, league_ids: List[int] = None):
        """Coleta dados abrangentes de partidas"""
        if not league_ids:
            league_ids = [39, 140, 78, 135, 61]  # Premier League, La Liga, Bundesliga, Serie A, Ligue 1
        
        logger.info("🚀 Iniciando coleta abrangente de dados de partidas...")
        
        all_data = {
            'today_matches': [],
            'upcoming_matches': [],
            'league_standings': {},
            'team_statistics': {},
            'injuries': []
        }
        
        # Coletar partidas de hoje
        logger.info("📅 Coletando partidas de hoje...")
        today_matches = self.get_today_matches()
        all_data['today_matches'] = today_matches
        
        # Coletar partidas dos próximos 3 dias
        logger.info("📅 Coletando partidas dos próximos 3 dias...")
        upcoming_matches = self.get_upcoming_matches(days=3)
        all_data['upcoming_matches'] = upcoming_matches
        
        # Coletar classificação das ligas principais
        logger.info("📊 Coletando classificação das ligas...")
        for league_id in league_ids:
            standings = self.get_league_standings(league_id)
            if standings:
                all_data['league_standings'][league_id] = standings
            time.sleep(1)  # Rate limiting
        
        # Coletar estatísticas de algumas equipes principais
        logger.info("⚽ Coletando estatísticas das equipes...")
        main_teams = [
            (529, 140),  # Real Madrid, La Liga
            (541, 140),  # Barcelona, La Liga
            (33, 39),    # Manchester United, Premier League
            (50, 39),    # Manchester City, Premier League
            (40, 39),    # Liverpool, Premier League
        ]
        
        for team_id, league_id in main_teams:
            stats = self.get_team_statistics(team_id, league_id)
            if stats:
                all_data['team_statistics'][team_id] = stats
            time.sleep(1)
        
        # Coletar informações sobre lesões
        logger.info("🏥 Coletando informações sobre lesões...")
        injuries = self.get_injuries()
        all_data['injuries'] = injuries
        
        logger.info("✅ Coleta abrangente de dados concluída!")
        return all_data
    
    def save_data_to_file(self, data: Dict, filename: str = None):
        """Salva dados em arquivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"real_football_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Dados salvos em {filename}")
        return filename
    
    def print_data_summary(self, data: Dict):
        """Imprime resumo dos dados coletados"""
        print("\n📊 RESUMO DOS DADOS COLETADOS:")
        print("=" * 50)
        
        print(f"📅 Partidas de hoje: {len(data['today_matches'])}")
        print(f"📅 Partidas próximos 3 dias: {len(data['upcoming_matches'])}")
        print(f"📊 Classificações de ligas: {len(data['league_standings'])}")
        print(f"⚽ Estatísticas de equipes: {len(data['team_statistics'])}")
        print(f"🏥 Lesões encontradas: {len(data['injuries'])}")
        
        # Mostrar algumas partidas de hoje
        if data['today_matches']:
            print("\n🏆 PARTIDAS DE HOJE:")
            for i, match in enumerate(data['today_matches'][:5], 1):
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                league = match['league']['name']
                time_str = match['fixture']['date'][11:16]
                
                print(f"{i}. {home_team} vs {away_team}")
                print(f"   🕐 {time_str} | 🏟️ {league}")
        
        # Mostrar algumas partidas próximas
        if data['upcoming_matches']:
            print("\n📅 PRÓXIMAS PARTIDAS:")
            for i, match in enumerate(data['upcoming_matches'][:5], 1):
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                league = match['league']['name']
                date_str = match['fixture']['date'][:10]
                
                print(f"{i}. {home_team} vs {away_team}")
                print(f"   📅 {date_str} | 🏟️ {league}")
        
        # Mostrar classificação de uma liga
        if data['league_standings']:
            print("\n📊 CLASSIFICAÇÃO - PREMIER LEAGUE:")
            standings = data['league_standings'].get(39, [])
            if standings:
                for i, team in enumerate(standings[:5], 1):
                    print(f"{i}. {team['team']['name']} - {team['points']} pts")

def main():
    # Chave da API fornecida pelo usuário
    API_KEY = "71b2b62386f2d1275cd3201a73e1e045"
    
    print("🎯 MARABET AI - COLETA DE DADOS REAIS DE PARTIDAS")
    print("=" * 60)
    
    # Inicializar coletor
    collector = RealMatchDataCollector(API_KEY)
    
    print(f"🔑 API Key configurada: {API_KEY[:10]}...")
    print("📊 Iniciando coleta de dados reais de partidas...")
    
    try:
        # Coletar dados abrangentes
        data = collector.collect_comprehensive_match_data()
        
        # Salvar dados em arquivo
        filename = collector.save_data_to_file(data)
        
        # Imprimir resumo
        collector.print_data_summary(data)
        
        print(f"\n✅ COLETA DE DADOS REAIS CONCLUÍDA!")
        print(f"📁 Arquivo salvo: {filename}")
        print("🎯 Sistema integrado com dados reais da Football API!")
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta de dados: {e}")
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
