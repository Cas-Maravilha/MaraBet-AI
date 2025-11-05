"""
Framework de Análise MaraBet AI
ETAPA 1: COLETA E PROCESSAMENTO DE DADOS
Sistema especializado para coleta e processamento de dados esportivos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import requests
import json
from dataclasses import dataclass
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TeamStats:
    """Estrutura para estatísticas de um time"""
    team_name: str
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_scored: float
    goals_conceded: float
    xg_for: float
    xg_against: float
    possession: float
    shots: float
    shots_on_target: float
    pass_accuracy: float
    fouls: float
    yellow_cards: float
    red_cards: float
    corners: float
    offsides: float
    clean_sheets: int
    failed_to_score: int

@dataclass
class MatchContext:
    """Contexto de uma partida"""
    competition: str
    round: str
    venue: str
    weather: str
    referee: str
    home_team_form: str
    away_team_form: str
    home_team_position: int
    away_team_position: int
    home_team_goals: str
    away_team_goals: str
    home_team_injuries: List[str]
    away_team_injuries: List[str]
    home_team_suspensions: List[str]
    away_team_suspensions: List[str]

class AdvancedDataCollector:
    """Coletor avançado de dados esportivos seguindo o framework"""
    
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_historical_stats(self, team_name: str, matches: int = 15) -> TeamStats:
        """
        Coleta estatísticas históricas dos últimos N jogos
        FONTE: Estatísticas históricas (últimas 10-20 partidas)
        """
        logger.info(f"Coletando estatísticas históricas para {team_name} ({matches} jogos)")
        
        # Simula dados históricos detalhados
        historical_matches = self._simulate_historical_matches(team_name, matches)
        
        # Calcula estatísticas agregadas
        stats = self._calculate_team_stats(team_name, historical_matches)
        
        return stats
    
    def get_head_to_head_stats(self, team1: str, team2: str, matches: int = 8) -> Dict:
        """
        Coleta estatísticas de confrontos diretos
        FONTE: Confrontos diretos (H2H - últimos 5-10 jogos)
        """
        logger.info(f"Coletando H2H entre {team1} vs {team2} ({matches} jogos)")
        
        # Simula confrontos diretos
        h2h_matches = self._simulate_h2h_matches(team1, team2, matches)
        
        # Calcula estatísticas H2H
        h2h_stats = self._calculate_h2h_stats(team1, team2, h2h_matches)
        
        return h2h_stats
    
    def get_home_away_performance(self, team_name: str, matches: int = 10) -> Dict:
        """
        Analisa desempenho em casa e fora
        FONTE: Desempenho casa/fora
        """
        logger.info(f"Analisando desempenho casa/fora para {team_name}")
        
        # Simula dados de casa e fora
        home_matches = self._simulate_venue_matches(team_name, 'home', matches)
        away_matches = self._simulate_venue_matches(team_name, 'away', matches)
        
        # Calcula estatísticas por local
        home_stats = self._calculate_venue_stats(team_name, home_matches, 'home')
        away_stats = self._calculate_venue_stats(team_name, away_matches, 'away')
        
        return {
            'home': home_stats,
            'away': away_stats,
            'home_advantage': home_stats['win_rate'] - away_stats['win_rate']
        }
    
    def get_recent_form_analysis(self, team_name: str, matches: int = 5) -> Dict:
        """
        Análise de forma recente aprimorada
        FONTE: Forma recente (últimos 5 jogos)
        """
        logger.info(f"Analisando forma recente para {team_name} ({matches} jogos)")
        
        # Coleta jogos recentes
        recent_matches = self._simulate_recent_matches(team_name, matches)
        
        # Análise de forma detalhada
        form_analysis = self._analyze_recent_form(team_name, recent_matches)
        
        return form_analysis
    
    def get_advanced_stats(self, team_name: str, matches: int = 10) -> Dict:
        """
        Coleta estatísticas avançadas
        FONTE: Estatísticas avançadas (xG, posse, finalizações)
        """
        logger.info(f"Coletando estatísticas avançadas para {team_name}")
        
        # Simula estatísticas avançadas
        advanced_stats = self._simulate_advanced_stats(team_name, matches)
        
        return advanced_stats
    
    def get_competitive_context(self, team_name: str, competition: str = 'Brasileirão') -> Dict:
        """
        Analisa contexto competitivo
        FONTE: Contexto competitivo (posição, objetivos)
        """
        logger.info(f"Analisando contexto competitivo para {team_name} em {competition}")
        
        # Simula contexto competitivo
        context = self._simulate_competitive_context(team_name, competition)
        
        return context
    
    def get_match_context(self, home_team: str, away_team: str, match_date: str) -> MatchContext:
        """
        Coleta fatores contextuais da partida
        FONTE: Fatores contextuais (lesões, clima, arbitragem)
        """
        logger.info(f"Coletando contexto da partida {home_team} vs {away_team}")
        
        # Simula contexto da partida
        context = self._simulate_match_context(home_team, away_team, match_date)
        
        return context
    
    def _simulate_historical_matches(self, team_name: str, matches: int) -> List[Dict]:
        """Simula jogos históricos com estatísticas detalhadas"""
        import random
        
        historical_matches = []
        base_date = datetime.now() - timedelta(days=matches * 3)
        
        for i in range(matches):
            match_date = base_date + timedelta(days=i * 3)
            
            # Simula resultado e estatísticas
            is_home = random.choice([True, False])
            goals_scored = random.randint(0, 4)
            goals_conceded = random.randint(0, 4)
            
            # Determina resultado
            if goals_scored > goals_conceded:
                result = 'win'
            elif goals_scored < goals_conceded:
                result = 'loss'
            else:
                result = 'draw'
            
            match = {
                'date': match_date.strftime('%Y-%m-%d'),
                'opponent': f"Time_{i}",
                'is_home': is_home,
                'result': result,
                'goals_scored': goals_scored,
                'goals_conceded': goals_conceded,
                'xg_for': round(random.uniform(0.5, 3.5), 2),
                'xg_against': round(random.uniform(0.5, 3.5), 2),
                'possession': round(random.uniform(35, 70), 1),
                'shots': random.randint(5, 20),
                'shots_on_target': random.randint(2, 10),
                'passes': random.randint(200, 600),
                'pass_accuracy': round(random.uniform(70, 95), 1),
                'fouls': random.randint(5, 20),
                'yellow_cards': random.randint(0, 5),
                'red_cards': random.randint(0, 1),
                'corners': random.randint(2, 10),
                'offsides': random.randint(0, 8),
                'clean_sheet': goals_conceded == 0,
                'failed_to_score': goals_scored == 0
            }
            
            historical_matches.append(match)
        
        return historical_matches
    
    def _calculate_team_stats(self, team_name: str, matches: List[Dict]) -> TeamStats:
        """Calcula estatísticas agregadas do time"""
        if not matches:
            return TeamStats(team_name, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        wins = sum(1 for m in matches if m['result'] == 'win')
        draws = sum(1 for m in matches if m['result'] == 'draw')
        losses = sum(1 for m in matches if m['result'] == 'loss')
        
        goals_scored = sum(m['goals_scored'] for m in matches)
        goals_conceded = sum(m['goals_conceded'] for m in matches)
        
        return TeamStats(
            team_name=team_name,
            matches_played=len(matches),
            wins=wins,
            draws=draws,
            losses=losses,
            goals_scored=goals_scored / len(matches),
            goals_conceded=goals_conceded / len(matches),
            xg_for=np.mean([m['xg_for'] for m in matches]),
            xg_against=np.mean([m['xg_against'] for m in matches]),
            possession=np.mean([m['possession'] for m in matches]),
            shots=np.mean([m['shots'] for m in matches]),
            shots_on_target=np.mean([m['shots_on_target'] for m in matches]),
            pass_accuracy=np.mean([m['pass_accuracy'] for m in matches]),
            fouls=np.mean([m['fouls'] for m in matches]),
            yellow_cards=np.mean([m['yellow_cards'] for m in matches]),
            red_cards=np.mean([m['red_cards'] for m in matches]),
            corners=np.mean([m['corners'] for m in matches]),
            offsides=np.mean([m['offsides'] for m in matches]),
            clean_sheets=sum(1 for m in matches if m['clean_sheet']),
            failed_to_score=sum(1 for m in matches if m['failed_to_score'])
        )
    
    def _simulate_h2h_matches(self, team1: str, team2: str, matches: int) -> List[Dict]:
        """Simula confrontos diretos entre dois times"""
        import random
        
        h2h_matches = []
        base_date = datetime.now() - timedelta(days=matches * 30)
        
        for i in range(matches):
            match_date = base_date + timedelta(days=i * 30)
            
            # Simula resultado do confronto
            team1_goals = random.randint(0, 3)
            team2_goals = random.randint(0, 3)
            
            if team1_goals > team2_goals:
                result = 'team1_win'
            elif team1_goals < team2_goals:
                result = 'team2_win'
            else:
                result = 'draw'
            
            match = {
                'date': match_date.strftime('%Y-%m-%d'),
                'team1': team1,
                'team2': team2,
                'team1_goals': team1_goals,
                'team2_goals': team2_goals,
                'result': result,
                'competition': random.choice(['Brasileirão', 'Copa do Brasil', 'Libertadores'])
            }
            
            h2h_matches.append(match)
        
        return h2h_matches
    
    def _calculate_h2h_stats(self, team1: str, team2: str, matches: List[Dict]) -> Dict:
        """Calcula estatísticas de confrontos diretos"""
        if not matches:
            return {'team1_wins': 0, 'team2_wins': 0, 'draws': 0, 'total_matches': 0}
        
        team1_wins = sum(1 for m in matches if m['result'] == 'team1_win')
        team2_wins = sum(1 for m in matches if m['result'] == 'team2_win')
        draws = sum(1 for m in matches if m['result'] == 'draw')
        
        team1_goals = sum(m['team1_goals'] for m in matches)
        team2_goals = sum(m['team2_goals'] for m in matches)
        
        return {
            'team1': team1,
            'team2': team2,
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'draws': draws,
            'total_matches': len(matches),
            'team1_win_rate': team1_wins / len(matches),
            'team2_win_rate': team2_wins / len(matches),
            'draw_rate': draws / len(matches),
            'team1_goals': team1_goals,
            'team2_goals': team2_goals,
            'team1_avg_goals': team1_goals / len(matches),
            'team2_avg_goals': team2_goals / len(matches),
            'last_meeting': matches[-1]['date'] if matches else None,
            'last_result': matches[-1]['result'] if matches else None
        }
    
    def _simulate_venue_matches(self, team_name: str, venue: str, matches: int) -> List[Dict]:
        """Simula jogos em casa ou fora"""
        import random
        
        venue_matches = []
        base_date = datetime.now() - timedelta(days=matches * 4)
        
        for i in range(matches):
            match_date = base_date + timedelta(days=i * 4)
            
            # Ajusta probabilidades baseado no local
            if venue == 'home':
                win_prob = 0.45
                draw_prob = 0.25
                loss_prob = 0.30
            else:
                win_prob = 0.30
                draw_prob = 0.25
                loss_prob = 0.45
            
            rand = random.random()
            if rand < win_prob:
                result = 'win'
                goals_scored = random.randint(1, 3)
                goals_conceded = random.randint(0, 1)
            elif rand < win_prob + draw_prob:
                result = 'draw'
                goals_scored = random.randint(0, 2)
                goals_conceded = goals_scored
            else:
                result = 'loss'
                goals_scored = random.randint(0, 1)
                goals_conceded = random.randint(1, 3)
            
            match = {
                'date': match_date.strftime('%Y-%m-%d'),
                'opponent': f"Time_{i}",
                'venue': venue,
                'result': result,
                'goals_scored': goals_scored,
                'goals_conceded': goals_conceded
            }
            
            venue_matches.append(match)
        
        return venue_matches
    
    def _calculate_venue_stats(self, team_name: str, matches: List[Dict], venue: str) -> Dict:
        """Calcula estatísticas por local"""
        if not matches:
            return {'venue': venue, 'matches': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'win_rate': 0}
        
        wins = sum(1 for m in matches if m['result'] == 'win')
        draws = sum(1 for m in matches if m['result'] == 'draw')
        losses = sum(1 for m in matches if m['result'] == 'loss')
        
        goals_scored = sum(m['goals_scored'] for m in matches)
        goals_conceded = sum(m['goals_conceded'] for m in matches)
        
        return {
            'venue': venue,
            'matches': len(matches),
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'win_rate': wins / len(matches),
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'avg_goals_scored': goals_scored / len(matches),
            'avg_goals_conceded': goals_conceded / len(matches),
            'goal_difference': goals_scored - goals_conceded
        }
    
    def _simulate_recent_matches(self, team_name: str, matches: int) -> List[Dict]:
        """Simula jogos recentes com análise de forma"""
        import random
        
        recent_matches = []
        base_date = datetime.now() - timedelta(days=matches * 2)
        
        for i in range(matches):
            match_date = base_date + timedelta(days=i * 2)
            
            # Simula resultado com tendência de forma
            goals_scored = random.randint(0, 3)
            goals_conceded = random.randint(0, 3)
            
            if goals_scored > goals_conceded:
                result = 'win'
            elif goals_scored < goals_conceded:
                result = 'loss'
            else:
                result = 'draw'
            
            match = {
                'date': match_date.strftime('%Y-%m-%d'),
                'opponent': f"Time_{i}",
                'result': result,
                'goals_scored': goals_scored,
                'goals_conceded': goals_conceded,
                'competition': random.choice(['Brasileirão', 'Copa do Brasil']),
                'venue': random.choice(['home', 'away'])
            }
            
            recent_matches.append(match)
        
        return recent_matches
    
    def _analyze_recent_form(self, team_name: str, matches: List[Dict]) -> Dict:
        """Analisa forma recente detalhada"""
        if not matches:
            return {'form': 'unknown', 'points': 0, 'trend': 'stable'}
        
        # Calcula pontos
        points = sum(3 if m['result'] == 'win' else 1 if m['result'] == 'draw' else 0 for m in matches)
        
        # Analisa tendência
        if len(matches) >= 3:
            recent_3 = matches[-3:]
            earlier_3 = matches[:3] if len(matches) >= 6 else matches[:-3]
            
            recent_points = sum(3 if m['result'] == 'win' else 1 if m['result'] == 'draw' else 0 for m in recent_3)
            earlier_points = sum(3 if m['result'] == 'win' else 1 if m['result'] == 'draw' else 0 for m in earlier_3)
            
            if recent_points > earlier_points:
                trend = 'improving'
            elif recent_points < earlier_points:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        # Determina forma geral
        win_rate = sum(1 for m in matches if m['result'] == 'win') / len(matches)
        
        if win_rate >= 0.6:
            form = 'excellent'
        elif win_rate >= 0.4:
            form = 'good'
        elif win_rate >= 0.2:
            form = 'average'
        else:
            form = 'poor'
        
        return {
            'team': team_name,
            'matches': len(matches),
            'wins': sum(1 for m in matches if m['result'] == 'win'),
            'draws': sum(1 for m in matches if m['result'] == 'draw'),
            'losses': sum(1 for m in matches if m['result'] == 'loss'),
            'points': points,
            'win_rate': win_rate,
            'form': form,
            'trend': trend,
            'goals_scored': sum(m['goals_scored'] for m in matches),
            'goals_conceded': sum(m['goals_conceded'] for m in matches),
            'avg_goals_scored': sum(m['goals_scored'] for m in matches) / len(matches),
            'avg_goals_conceded': sum(m['goals_conceded'] for m in matches) / len(matches)
        }
    
    def _simulate_advanced_stats(self, team_name: str, matches: int) -> Dict:
        """Simula estatísticas avançadas"""
        import random
        
        return {
            'team': team_name,
            'xg_for': round(random.uniform(1.0, 2.5), 2),
            'xg_against': round(random.uniform(0.8, 2.2), 2),
            'xg_difference': round(random.uniform(-0.5, 1.0), 2),
            'possession': round(random.uniform(40, 65), 1),
            'shots_per_game': round(random.uniform(8, 16), 1),
            'shots_on_target_per_game': round(random.uniform(3, 8), 1),
            'shot_accuracy': round(random.uniform(30, 50), 1),
            'passes_per_game': round(random.uniform(300, 600), 1),
            'pass_accuracy': round(random.uniform(75, 90), 1),
            'key_passes_per_game': round(random.uniform(5, 12), 1),
            'crosses_per_game': round(random.uniform(10, 25), 1),
            'cross_accuracy': round(random.uniform(20, 40), 1),
            'aerial_duels_won': round(random.uniform(40, 70), 1),
            'tackles_per_game': round(random.uniform(15, 25), 1),
            'interceptions_per_game': round(random.uniform(8, 15), 1),
            'fouls_per_game': round(random.uniform(8, 18), 1),
            'cards_per_game': round(random.uniform(1.5, 4), 1),
            'corners_per_game': round(random.uniform(3, 8), 1),
            'offsides_per_game': round(random.uniform(1, 5), 1)
        }
    
    def _simulate_competitive_context(self, team_name: str, competition: str) -> Dict:
        """Simula contexto competitivo"""
        import random
        
        # Simula posição na tabela
        position = random.randint(1, 20)
        total_teams = 20
        
        # Determina objetivos baseado na posição
        if position <= 4:
            objective = 'libertadores'
            pressure = 'high'
        elif position <= 8:
            objective = 'sul_americana'
            pressure = 'medium'
        elif position <= 12:
            objective = 'mid_table'
            pressure = 'low'
        else:
            objective = 'avoid_relegation'
            pressure = 'high'
        
        # Simula pontos e jogos
        points = random.randint(10, 60)
        games_played = random.randint(10, 20)
        points_per_game = points / games_played if games_played > 0 else 0
        
        return {
            'team': team_name,
            'competition': competition,
            'position': position,
            'total_teams': total_teams,
            'points': points,
            'games_played': games_played,
            'points_per_game': round(points_per_game, 2),
            'objective': objective,
            'pressure_level': pressure,
            'form_importance': 'high' if position <= 6 or position >= 15 else 'medium',
            'home_advantage': 'high' if position <= 8 else 'medium'
        }
    
    def _simulate_match_context(self, home_team: str, away_team: str, match_date: str) -> MatchContext:
        """Simula contexto da partida"""
        import random
        
        # Simula lesões e suspensões
        home_injuries = random.sample(['Jogador A', 'Jogador B'], random.randint(0, 2))
        away_injuries = random.sample(['Jogador X', 'Jogador Y'], random.randint(0, 2))
        home_suspensions = random.sample(['Jogador C'], random.randint(0, 1))
        away_suspensions = random.sample(['Jogador Z'], random.randint(0, 1))
        
        return MatchContext(
            competition='Brasileirão',
            round=f"Rodada {random.randint(1, 38)}",
            venue='Estádio Principal',
            weather=random.choice(['Ensolarado', 'Nublado', 'Chuvoso']),
            referee=f"Árbitro {random.randint(1, 10)}",
            home_team_form=random.choice(['excellent', 'good', 'average', 'poor']),
            away_team_form=random.choice(['excellent', 'good', 'average', 'poor']),
            home_team_position=random.randint(1, 20),
            away_team_position=random.randint(1, 20),
            home_team_goals=f"{random.randint(15, 45)} gols",
            away_team_goals=f"{random.randint(15, 45)} gols",
            home_team_injuries=home_injuries,
            away_team_injuries=away_injuries,
            home_team_suspensions=home_suspensions,
            away_team_suspensions=away_suspensions
        )

class DataProcessor:
    """Processador de dados do framework"""
    
    def __init__(self):
        self.collector = AdvancedDataCollector()
    
    def process_team_analysis(self, team_name: str) -> Dict:
        """Processa análise completa de um time"""
        logger.info(f"Processando análise completa para {team_name}")
        
        # Coleta todos os dados
        historical_stats = self.collector.get_historical_stats(team_name, 15)
        home_away_perf = self.collector.get_home_away_performance(team_name, 10)
        recent_form = self.collector.get_recent_form_analysis(team_name, 5)
        advanced_stats = self.collector.get_advanced_stats(team_name, 10)
        competitive_context = self.collector.get_competitive_context(team_name)
        
        # Combina todos os dados
        analysis = {
            'team_name': team_name,
            'historical_stats': historical_stats,
            'home_away_performance': home_away_perf,
            'recent_form': recent_form,
            'advanced_stats': advanced_stats,
            'competitive_context': competitive_context,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return analysis
    
    def process_match_analysis(self, home_team: str, away_team: str, match_date: str) -> Dict:
        """Processa análise completa de uma partida"""
        logger.info(f"Processando análise da partida {home_team} vs {away_team}")
        
        # Análise dos times
        home_analysis = self.process_team_analysis(home_team)
        away_analysis = self.process_team_analysis(away_team)
        
        # Confronto direto
        h2h_stats = self.collector.get_head_to_head_stats(home_team, away_team, 8)
        
        # Contexto da partida
        match_context = self.collector.get_match_context(home_team, away_team, match_date)
        
        # Análise comparativa
        comparative_analysis = self._create_comparative_analysis(home_analysis, away_analysis, h2h_stats)
        
        return {
            'match_info': {
                'home_team': home_team,
                'away_team': away_team,
                'date': match_date
            },
            'home_team_analysis': home_analysis,
            'away_team_analysis': away_analysis,
            'head_to_head': h2h_stats,
            'match_context': match_context,
            'comparative_analysis': comparative_analysis,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _create_comparative_analysis(self, home_analysis: Dict, away_analysis: Dict, h2h_stats: Dict) -> Dict:
        """Cria análise comparativa entre os times"""
        home_stats = home_analysis['historical_stats']
        away_stats = away_analysis['historical_stats']
        
        return {
            'form_comparison': {
                'home_form': home_analysis['recent_form']['form'],
                'away_form': away_analysis['recent_form']['form'],
                'home_advantage': home_analysis['home_away_performance']['home_advantage']
            },
            'statistical_comparison': {
                'goals_scored': home_stats.goals_scored - away_stats.goals_scored,
                'goals_conceded': home_stats.goals_conceded - away_stats.goals_conceded,
                'possession': home_stats.possession - away_stats.possession,
                'xg_difference': home_stats.xg_for - away_stats.xg_for
            },
            'competitive_context': {
                'home_position': home_analysis['competitive_context']['position'],
                'away_position': away_analysis['competitive_context']['position'],
                'home_pressure': home_analysis['competitive_context']['pressure_level'],
                'away_pressure': away_analysis['competitive_context']['pressure_level']
            },
            'head_to_head_summary': {
                'home_h2h_advantage': h2h_stats.get('team1_win_rate', 0) - h2h_stats.get('team2_win_rate', 0),
                'last_meeting': h2h_stats.get('last_meeting'),
                'last_result': h2h_stats.get('last_result')
            }
        }

if __name__ == "__main__":
    # Teste do framework
    processor = DataProcessor()
    
    # Teste análise de time
    print("=== TESTE DO FRAMEWORK DE ANÁLISE ===")
    
    team_analysis = processor.process_team_analysis('Flamengo')
    print(f"\nAnálise do Flamengo:")
    print(f"Forma recente: {team_analysis['recent_form']['form']}")
    print(f"Posição: {team_analysis['competitive_context']['position']}")
    print(f"Gols por jogo: {team_analysis['historical_stats'].goals_scored:.2f}")
    
    # Teste análise de partida
    match_analysis = processor.process_match_analysis('Flamengo', 'Palmeiras', '2024-01-15')
    print(f"\nAnálise da partida:")
    print(f"Vantagem H2H: {match_analysis['comparative_analysis']['head_to_head_summary']['home_h2h_advantage']:.2f}")
    print(f"Diferença de gols: {match_analysis['comparative_analysis']['statistical_comparison']['goals_scored']:.2f}")
