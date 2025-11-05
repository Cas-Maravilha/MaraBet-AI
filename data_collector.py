import requests
import pandas as pd
import time
import json
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SportsDataCollector:
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def setup_selenium_driver(self):
        """Configura o driver do Selenium para scraping dinâmico"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def get_football_matches(self, league='all', days_ahead=7):
        """
        Coleta dados de partidas de futebol
        """
        try:
            # Simulação de dados - em produção, integrar com APIs reais
            matches = self._simulate_football_data(league, days_ahead)
            return matches
        except Exception as e:
            logger.error(f"Erro ao coletar dados de futebol: {e}")
            return []
    
    def _simulate_football_data(self, league, days_ahead):
        """Simula dados de futebol para demonstração"""
        import random
        
        teams = [
            'Flamengo', 'Palmeiras', 'São Paulo', 'Santos', 'Corinthians',
            'Internacional', 'Grêmio', 'Atlético-MG', 'Cruzeiro', 'Botafogo',
            'Vasco', 'Fluminense', 'Bragantino', 'Fortaleza', 'Ceará',
            'Bahia', 'Sport', 'Vitória', 'Náutico', 'Santa Cruz'
        ]
        
        matches = []
        start_date = datetime.now()
        
        for i in range(days_ahead * 3):  # 3 jogos por dia em média
            match_date = start_date + timedelta(days=i//3, hours=(i%3)*8)
            
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            
            # Simula estatísticas dos times
            home_stats = self._generate_team_stats()
            away_stats = self._generate_team_stats()
            
            match = {
                'id': f"match_{i}_{int(match_date.timestamp())}",
                'league': league,
                'home_team': home_team,
                'away_team': away_team,
                'date': match_date.strftime('%Y-%m-%d %H:%M'),
                'home_odds': round(random.uniform(1.5, 4.0), 2),
                'draw_odds': round(random.uniform(2.8, 3.5), 2),
                'away_odds': round(random.uniform(1.8, 5.0), 2),
                'home_stats': home_stats,
                'away_stats': away_stats,
                'status': 'scheduled'
            }
            
            matches.append(match)
            
        return matches
    
    def _generate_team_stats(self):
        """Gera estatísticas simuladas para um time"""
        return {
            'goals_scored': round(random.uniform(1.0, 2.5), 1),
            'goals_conceded': round(random.uniform(0.8, 2.0), 1),
            'shots': round(random.uniform(8, 15), 1),
            'shots_on_target': round(random.uniform(3, 8), 1),
            'possession': round(random.uniform(40, 65), 1),
            'passes': round(random.uniform(300, 600), 1),
            'pass_accuracy': round(random.uniform(75, 90), 1),
            'fouls': round(random.uniform(8, 18), 1),
            'yellow_cards': round(random.uniform(1, 4), 1),
            'red_cards': round(random.uniform(0, 0.3), 1),
            'corners': round(random.uniform(3, 8), 1),
            'offsides': round(random.uniform(1, 5), 1)
        }
    
    def get_historical_results(self, team, days_back=90):
        """
        Coleta resultados históricos de um time
        """
        try:
            # Simulação de dados históricos
            results = self._simulate_historical_data(team, days_back)
            return results
        except Exception as e:
            logger.error(f"Erro ao coletar dados históricos para {team}: {e}")
            return []
    
    def _simulate_historical_data(self, team, days_back):
        """Simula dados históricos de um time"""
        import random
        
        results = []
        start_date = datetime.now() - timedelta(days=days_back)
        
        for i in range(days_back // 3):  # Jogo a cada 3 dias em média
            match_date = start_date + timedelta(days=i*3)
            
            # Simula resultado do jogo
            home_goals = random.randint(0, 4)
            away_goals = random.randint(0, 4)
            
            result = {
                'team': team,
                'opponent': f"Time_{i}",
                'date': match_date.strftime('%Y-%m-%d'),
                'home_goals': home_goals,
                'away_goals': away_goals,
                'is_home': random.choice([True, False]),
                'result': 'win' if (home_goals > away_goals and random.choice([True, False])) else 
                         'loss' if (home_goals < away_goals and random.choice([True, False])) else 'draw',
                'goals_scored': home_goals if random.choice([True, False]) else away_goals,
                'goals_conceded': away_goals if random.choice([True, False]) else home_goals
            }
            
            results.append(result)
            
        return results
    
    def get_team_form(self, team, matches=5):
        """
        Calcula a forma atual de um time baseada nos últimos jogos
        """
        historical_data = self.get_historical_results(team, days_back=30)
        
        if len(historical_data) < matches:
            matches = len(historical_data)
        
        recent_matches = historical_data[-matches:] if historical_data else []
        
        form_data = {
            'team': team,
            'matches_analyzed': len(recent_matches),
            'wins': sum(1 for match in recent_matches if match['result'] == 'win'),
            'draws': sum(1 for match in recent_matches if match['result'] == 'draw'),
            'losses': sum(1 for match in recent_matches if match['result'] == 'loss'),
            'goals_scored': sum(match['goals_scored'] for match in recent_matches),
            'goals_conceded': sum(match['goals_conceded'] for match in recent_matches),
            'points': sum(3 if match['result'] == 'win' else 1 if match['result'] == 'draw' else 0 
                         for match in recent_matches)
        }
        
        if form_data['matches_analyzed'] > 0:
            form_data['win_rate'] = form_data['wins'] / form_data['matches_analyzed']
            form_data['points_per_game'] = form_data['points'] / form_data['matches_analyzed']
            form_data['goals_per_game'] = form_data['goals_scored'] / form_data['matches_analyzed']
            form_data['goals_conceded_per_game'] = form_data['goals_conceded'] / form_data['matches_analyzed']
        else:
            form_data.update({
                'win_rate': 0,
                'points_per_game': 0,
                'goals_per_game': 0,
                'goals_conceded_per_game': 0
            })
        
        return form_data
    
    def save_data_to_csv(self, data, filename):
        """Salva dados em arquivo CSV"""
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Dados salvos em {filename}")
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")

if __name__ == "__main__":
    collector = SportsDataCollector()
    
    # Teste de coleta de dados
    print("Coletando dados de futebol...")
    matches = collector.get_football_matches()
    print(f"Coletados {len(matches)} jogos")
    
    # Teste de forma do time
    print("\nAnalisando forma do Flamengo...")
    form = collector.get_team_form('Flamengo')
    print(f"Forma do Flamengo: {form}")
    
    # Salvar dados
    collector.save_data_to_csv(matches, 'matches.csv')
