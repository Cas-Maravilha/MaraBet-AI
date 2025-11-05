#!/usr/bin/env python3
"""
Simulador de Dados Realistas
MaraBet AI - Gera dados simulados realistas quando API não está disponível
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
import sqlite3
import json
import os
from pathlib import Path
import random

logger = logging.getLogger(__name__)

class RealisticDataSimulator:
    """Simulador de dados realistas"""
    
    def __init__(self, db_path: str = "data/simulated_data.db"):
        """Inicializa simulador"""
        self.db_path = db_path
        self.leagues = {
            39: "Premier League",
            140: "La Liga", 
            78: "Bundesliga",
            135: "Serie A",
            61: "Ligue 1"
        }
        
        # Times reais por liga
        self.teams = {
            39: ["Arsenal", "Chelsea", "Liverpool", "Manchester City", "Manchester United", 
                 "Tottenham", "Newcastle", "Brighton", "West Ham", "Aston Villa",
                 "Crystal Palace", "Fulham", "Brentford", "Everton", "Nottingham Forest",
                 "Wolves", "Bournemouth", "Sheffield United", "Burnley", "Luton Town"],
            140: ["Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla", "Real Sociedad",
                  "Villarreal", "Real Betis", "Athletic Bilbao", "Valencia", "Osasuna",
                  "Getafe", "Celta Vigo", "Mallorca", "Las Palmas", "Cadiz",
                  "Rayo Vallecano", "Alaves", "Almeria", "Granada", "Elche"],
            78: ["Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen", "Eintracht Frankfurt",
                 "Freiburg", "Union Berlin", "Wolfsburg", "Mainz", "Borussia Monchengladbach",
                 "Cologne", "Hoffenheim", "Werder Bremen", "Bochum", "Augsburg",
                 "Stuttgart", "Heidenheim", "Darmstadt"],
            135: ["Inter Milan", "AC Milan", "Juventus", "Napoli", "Atalanta",
                  "Roma", "Lazio", "Fiorentina", "Bologna", "Torino",
                  "Monza", "Sassuolo", "Lecce", "Frosinone", "Genoa",
                  "Cagliari", "Verona", "Empoli", "Salernitana", "Udinese"],
            61: ["PSG", "Marseille", "Monaco", "Lille", "Lyon",
                 "Rennes", "Lens", "Nice", "Reims", "Toulouse",
                 "Montpellier", "Strasbourg", "Nantes", "Brest", "Lorient",
                 "Clermont", "Le Havre", "Metz"]
        }
        
        # Inicializar banco de dados
        self._init_database()
    
    def _init_database(self):
        """Inicializa banco de dados"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de partidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER UNIQUE,
                league_id INTEGER,
                season INTEGER,
                date TEXT,
                home_team_id INTEGER,
                home_team_name TEXT,
                away_team_id INTEGER,
                away_team_name TEXT,
                home_score INTEGER,
                away_score INTEGER,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de estatísticas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                team_id INTEGER,
                shots_total INTEGER,
                shots_on_goal INTEGER,
                possession INTEGER,
                passes_total INTEGER,
                passes_accurate INTEGER,
                fouls INTEGER,
                yellow_cards INTEGER,
                red_cards INTEGER,
                FOREIGN KEY (match_id) REFERENCES matches (match_id)
            )
        ''')
        
        # Tabela de odds
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS odds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                bookmaker TEXT,
                home_win REAL,
                draw REAL,
                away_win REAL,
                over_2_5 REAL,
                under_2_5 REAL,
                btts_yes REAL,
                btts_no REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches (match_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados simulado inicializado")
    
    def generate_realistic_matches(self, 
                                 start_date: str = "2021-01-01", 
                                 end_date: str = "2024-01-01",
                                 matches_per_week: int = 10) -> List[Dict]:
        """Gera partidas realistas"""
        logger.info("Gerando partidas realistas...")
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        matches = []
        match_id = 1000
        
        current_date = start
        while current_date <= end:
            # Gerar partidas para cada liga
            for league_id, league_name in self.leagues.items():
                season = current_date.year
                if current_date.month < 8:  # Temporada anterior se antes de agosto
                    season -= 1
                
                # Gerar partidas da semana
                for _ in range(matches_per_week):
                    # Selecionar times aleatórios
                    home_team = random.choice(self.teams[league_id])
                    away_team = random.choice([t for t in self.teams[league_id] if t != home_team])
                    
                    # Gerar data da partida (fim de semana)
                    match_date = current_date + timedelta(days=random.choice([5, 6]))  # Sábado ou domingo
                    match_date = match_date.replace(hour=random.choice([15, 17, 19, 21]), minute=0)
                    
                    # Gerar placar realista
                    home_score, away_score = self._generate_realistic_score()
                    
                    # Determinar status
                    if match_date < datetime.now() - timedelta(hours=2):
                        status = "FT"
                    elif match_date < datetime.now():
                        status = random.choice(["1H", "2H", "HT"])
                    else:
                        status = "NS"
                    
                    match_data = {
                        'match_id': match_id,
                        'league_id': league_id,
                        'season': season,
                        'date': match_date.isoformat(),
                        'home_team_id': hash(home_team) % 10000,
                        'home_team_name': home_team,
                        'away_team_id': hash(away_team) % 10000,
                        'away_team_name': away_team,
                        'home_score': home_score if status == "FT" else None,
                        'away_score': away_score if status == "FT" else None,
                        'status': status
                    }
                    
                    matches.append(match_data)
                    match_id += 1
            
            current_date += timedelta(weeks=1)
        
        logger.info(f"Geradas {len(matches)} partidas realistas")
        return matches
    
    def _generate_realistic_score(self) -> Tuple[int, int]:
        """Gera placar realista baseado em distribuições reais"""
        # Distribuição de gols baseada em dados reais
        home_goals = np.random.poisson(1.5)  # Média de 1.5 gols em casa
        away_goals = np.random.poisson(1.2)  # Média de 1.2 gols fora
        
        # Limitar a valores realistas
        home_goals = min(home_goals, 6)
        away_goals = min(away_goals, 6)
        
        return home_goals, away_goals
    
    def generate_realistic_stats(self, matches: List[Dict]) -> List[Dict]:
        """Gera estatísticas realistas para partidas"""
        logger.info("Gerando estatísticas realistas...")
        
        stats = []
        
        for match in matches:
            if match['status'] != 'FT':
                continue
            
            # Estatísticas do time da casa
            home_stats = self._generate_team_stats(match['home_team_name'], is_home=True)
            home_stats['match_id'] = match['match_id']
            home_stats['team_id'] = match['home_team_id']
            home_stats['team_name'] = match['home_team_name']
            stats.append(home_stats)
            
            # Estatísticas do time visitante
            away_stats = self._generate_team_stats(match['away_team_name'], is_home=False)
            away_stats['match_id'] = match['match_id']
            away_stats['team_id'] = match['away_team_id']
            away_stats['team_name'] = match['away_team_name']
            stats.append(away_stats)
        
        logger.info(f"Geradas {len(stats)} estatísticas realistas")
        return stats
    
    def _generate_team_stats(self, team_name: str, is_home: bool) -> Dict:
        """Gera estatísticas realistas para um time"""
        # Fatores baseados no nome do time (times grandes têm melhor performance)
        is_big_team = any(big_team in team_name.lower() for big_team in 
                         ['manchester', 'liverpool', 'arsenal', 'chelsea', 'real', 'barcelona', 
                          'bayern', 'dortmund', 'juventus', 'milan', 'inter', 'psg'])
        
        # Ajustar estatísticas baseado no time e se é casa
        base_shots = 12 if is_big_team else 8
        base_possession = 55 if is_big_team else 45
        base_passes = 500 if is_big_team else 350
        
        if is_home:
            base_shots += 2
            base_possession += 5
            base_passes += 50
        
        return {
            'shots_total': max(0, int(np.random.normal(base_shots, 3))),
            'shots_on_goal': max(0, int(np.random.normal(base_shots * 0.35, 2))),
            'possession': max(20, min(80, int(np.random.normal(base_possession, 8)))),
            'passes_total': max(100, int(np.random.normal(base_passes, 50))),
            'passes_accurate': max(50, int(np.random.normal(base_passes * 0.85, 30))),
            'fouls': max(0, int(np.random.poisson(12))),
            'yellow_cards': max(0, int(np.random.poisson(2.5))),
            'red_cards': 1 if np.random.random() < 0.05 else 0
        }
    
    def generate_realistic_odds(self, matches: List[Dict]) -> List[Dict]:
        """Gera odds realistas para partidas"""
        logger.info("Gerando odds realistas...")
        
        odds = []
        bookmakers = ["Bet365", "William Hill", "Betfair", "Pinnacle", "Marathonbet"]
        
        for match in matches:
            if match['status'] not in ['NS', '1H', '2H', 'HT']:
                continue
            
            # Calcular probabilidades baseadas nos times
            home_team = match['home_team_name']
            away_team = match['away_team_name']
            
            is_home_big = any(big_team in home_team.lower() for big_team in 
                            ['manchester', 'liverpool', 'arsenal', 'chelsea', 'real', 'barcelona'])
            is_away_big = any(big_team in away_team.lower() for big_team in 
                            ['manchester', 'liverpool', 'arsenal', 'chelsea', 'real', 'barcelona'])
            
            # Ajustar probabilidades
            if is_home_big and not is_away_big:
                home_prob = 0.45
                draw_prob = 0.30
                away_prob = 0.25
            elif not is_home_big and is_away_big:
                home_prob = 0.25
                draw_prob = 0.30
                away_prob = 0.45
            elif is_home_big and is_away_big:
                home_prob = 0.40
                draw_prob = 0.30
                away_prob = 0.30
            else:
                home_prob = 0.35
                draw_prob = 0.30
                away_prob = 0.35
            
            # Adicionar ruído
            home_prob += np.random.normal(0, 0.05)
            draw_prob += np.random.normal(0, 0.05)
            away_prob += np.random.normal(0, 0.05)
            
            # Normalizar
            total = home_prob + draw_prob + away_prob
            home_prob /= total
            draw_prob /= total
            away_prob /= total
            
            # Converter para odds (com margem da casa)
            margin = 1.05  # 5% de margem
            home_odds = 1 / (home_prob * margin)
            draw_odds = 1 / (draw_prob * margin)
            away_odds = 1 / (away_prob * margin)
            
            # Gerar odds para múltiplas casas
            for bookmaker in bookmakers:
                # Adicionar variação entre casas
                variation = np.random.normal(1, 0.02)
                
                bookmaker_odds = {
                    'match_id': match['match_id'],
                    'bookmaker': bookmaker,
                    'home_win': round(home_odds * variation, 2),
                    'draw': round(draw_odds * variation, 2),
                    'away_win': round(away_odds * variation, 2),
                    'over_2_5': round(np.random.uniform(1.8, 2.2), 2),
                    'under_2_5': round(np.random.uniform(1.7, 2.0), 2),
                    'btts_yes': round(np.random.uniform(1.8, 2.5), 2),
                    'btts_no': round(np.random.uniform(1.4, 1.8), 2)
                }
                
                odds.append(bookmaker_odds)
        
        logger.info(f"Geradas {len(odds)} odds realistas")
        return odds
    
    def save_to_database(self, matches: List[Dict], stats: List[Dict] = None, odds: List[Dict] = None):
        """Salva dados no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Salvar partidas
            for match in matches:
                cursor.execute('''
                    INSERT OR REPLACE INTO matches 
                    (match_id, league_id, season, date, home_team_id, home_team_name, 
                     away_team_id, away_team_name, home_score, away_score, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    match['match_id'], match['league_id'], match['season'], match['date'],
                    match['home_team_id'], match['home_team_name'], match['away_team_id'],
                    match['away_team_name'], match['home_score'], match['away_score'], match['status']
                ))
            
            # Salvar estatísticas
            if stats:
                for stat in stats:
                    cursor.execute('''
                        INSERT OR REPLACE INTO match_stats 
                        (match_id, team_id, shots_total, shots_on_goal, possession, 
                         passes_total, passes_accurate, fouls, yellow_cards, red_cards)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        stat['match_id'], stat['team_id'], stat['shots_total'], stat['shots_on_goal'],
                        stat['possession'], stat['passes_total'], stat['passes_accurate'],
                        stat['fouls'], stat['yellow_cards'], stat['red_cards']
                    ))
            
            # Salvar odds
            if odds:
                for odd in odds:
                    cursor.execute('''
                        INSERT OR REPLACE INTO odds 
                        (match_id, bookmaker, home_win, draw, away_win, over_2_5, 
                         under_2_5, btts_yes, btts_no)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        odd['match_id'], odd['bookmaker'], odd['home_win'], odd['draw'],
                        odd['away_win'], odd['over_2_5'], odd['under_2_5'], odd['btts_yes'], odd['btts_no']
                    ))
            
            conn.commit()
            logger.info(f"Salvos {len(matches)} partidas no banco de dados simulado")
            
        except Exception as e:
            logger.error(f"Erro ao salvar no banco de dados: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def generate_complete_dataset(self, 
                                start_date: str = "2021-01-01", 
                                end_date: str = "2024-01-01") -> Dict[str, int]:
        """Gera dataset completo simulado"""
        logger.info("Gerando dataset completo simulado...")
        
        # Gerar partidas
        matches = self.generate_realistic_matches(start_date, end_date)
        
        # Gerar estatísticas
        stats = self.generate_realistic_stats(matches)
        
        # Gerar odds
        odds = self.generate_realistic_odds(matches)
        
        # Salvar no banco
        self.save_to_database(matches, stats, odds)
        
        return {
            'matches': len(matches),
            'stats': len(stats),
            'odds': len(odds)
        }
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Obtém resumo dos dados simulados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM matches")
        matches_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM match_stats")
        stats_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM odds")
        odds_count = cursor.fetchone()[0]
        
        # Período dos dados
        cursor.execute("SELECT MIN(date), MAX(date) FROM matches")
        date_range = cursor.fetchone()
        
        # Ligas cobertas
        cursor.execute("SELECT DISTINCT league_id FROM matches")
        leagues = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'matches': matches_count,
            'stats': stats_count,
            'odds': odds_count,
            'date_range': date_range,
            'leagues': leagues,
            'database_path': self.db_path
        }

# Instância global
realistic_simulator = RealisticDataSimulator()

if __name__ == "__main__":
    # Teste do simulador de dados realistas
    print("🧪 TESTANDO SIMULADOR DE DADOS REALISTAS")
    print("=" * 50)
    
    # Gerar dataset completo
    results = realistic_simulator.generate_complete_dataset()
    
    print(f"\nResultados da geração:")
    print(f"  Partidas: {results['matches']}")
    print(f"  Estatísticas: {results['stats']}")
    print(f"  Odds: {results['odds']}")
    
    # Resumo dos dados
    summary = realistic_simulator.get_data_summary()
    print(f"\nResumo dos dados:")
    print(f"  Período: {summary['date_range'][0]} a {summary['date_range'][1]}")
    print(f"  Ligas: {summary['leagues']}")
    print(f"  Banco: {summary['database_path']}")
    
    print("\n🎉 TESTE DE SIMULADOR DE DADOS REALISTAS CONCLUÍDO!")
