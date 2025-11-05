"""
Análise Estatística Detalhada - MaraBet AI
Sistema especializado para análise estatística avançada de partidas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MatchResult:
    """Resultado de uma partida"""
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    home_xg: float
    away_xg: float
    date: str
    venue: str  # 'H' for home, 'A' for away
    result: str  # 'W' for win, 'D' for draw, 'L' for loss

@dataclass
class TeamForm:
    """Forma recente de um time"""
    team_name: str
    matches: List[MatchResult]
    venue: str  # 'Home' or 'Away'
    goals_scored: List[int]
    goals_conceded: List[int]
    xg_values: List[float]
    results: List[str]
    avg_goals_scored: float
    avg_goals_conceded: float
    avg_xg: float
    win_rate: float
    points_per_game: float

@dataclass
class HeadToHead:
    """Confrontos diretos entre dois times"""
    home_team: str
    away_team: str
    matches: List[MatchResult]
    home_wins: int
    away_wins: int
    draws: int
    home_advantage: float
    avg_goals_home: float
    avg_goals_away: float
    recent_trend: str

class StatisticalAnalyzer:
    """
    Analisador Estatístico Detalhado
    Gera análises estatísticas avançadas para partidas
    """
    
    def __init__(self):
        self.match_database = []
        self.team_stats = {}
        
    def add_match_result(self, match: MatchResult):
        """Adiciona resultado de partida ao banco de dados"""
        self.match_database.append(match)
        
        # Atualiza estatísticas dos times
        self._update_team_stats(match)
    
    def generate_team_form_analysis(self, team_name: str, venue: str = "Home", 
                                  last_matches: int = 5) -> TeamForm:
        """
        Gera análise de forma recente de um time
        """
        logger.info(f"Analisando forma recente: {team_name} ({venue})")
        
        try:
            # Filtra partidas do time
            if venue == "Home":
                team_matches = [m for m in self.match_database 
                              if m.home_team == team_name][-last_matches:]
                goals_scored = [m.home_score for m in team_matches]
                goals_conceded = [m.away_score for m in team_matches]
                xg_values = [m.home_xg for m in team_matches]
                results = [m.result for m in team_matches if m.home_team == team_name]
            else:  # Away
                team_matches = [m for m in self.match_database 
                              if m.away_team == team_name][-last_matches:]
                goals_scored = [m.away_score for m in team_matches]
                goals_conceded = [m.home_score for m in team_matches]
                xg_values = [m.away_xg for m in team_matches]
                results = [m.result for m in team_matches if m.away_team == team_name]
            
            # Calcula métricas
            avg_goals_scored = np.mean(goals_scored) if goals_scored else 0
            avg_goals_conceded = np.mean(goals_conceded) if goals_conceded else 0
            avg_xg = np.mean(xg_values) if xg_values else 0
            
            # Calcula taxa de vitórias
            wins = results.count('W')
            win_rate = wins / len(results) if results else 0
            
            # Calcula pontos por jogo
            points = wins * 3 + results.count('D')
            points_per_game = points / len(results) if results else 0
            
            return TeamForm(
                team_name=team_name,
                matches=team_matches,
                venue=venue,
                goals_scored=goals_scored,
                goals_conceded=goals_conceded,
                xg_values=xg_values,
                results=results,
                avg_goals_scored=avg_goals_scored,
                avg_goals_conceded=avg_goals_conceded,
                avg_xg=avg_xg,
                win_rate=win_rate,
                points_per_game=points_per_game
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de forma: {e}")
            return self._create_empty_team_form(team_name, venue)
    
    def generate_head_to_head_analysis(self, home_team: str, away_team: str, 
                                     last_matches: int = 5) -> HeadToHead:
        """
        Gera análise de confrontos diretos entre dois times
        """
        logger.info(f"Analisando confrontos diretos: {home_team} vs {away_team}")
        
        try:
            # Filtra confrontos diretos
            h2h_matches = []
            for match in self.match_database:
                if ((match.home_team == home_team and match.away_team == away_team) or
                    (match.home_team == away_team and match.away_team == home_team)):
                    h2h_matches.append(match)
            
            # Pega os últimos confrontos
            h2h_matches = h2h_matches[-last_matches:]
            
            # Analisa resultados
            home_wins = 0
            away_wins = 0
            draws = 0
            home_goals = []
            away_goals = []
            
            for match in h2h_matches:
                if match.home_team == home_team:
                    # Time da casa jogando em casa
                    home_goals.append(match.home_score)
                    away_goals.append(match.away_score)
                    
                    if match.home_score > match.away_score:
                        home_wins += 1
                    elif match.home_score < match.away_score:
                        away_wins += 1
                    else:
                        draws += 1
                else:
                    # Time da casa jogando fora
                    home_goals.append(match.away_score)
                    away_goals.append(match.home_score)
                    
                    if match.away_score > match.home_score:
                        home_wins += 1
                    elif match.away_score < match.home_score:
                        away_wins += 1
                    else:
                        draws += 1
            
            # Calcula métricas
            total_matches = len(h2h_matches)
            home_advantage = home_wins / total_matches if total_matches > 0 else 0
            avg_goals_home = np.mean(home_goals) if home_goals else 0
            avg_goals_away = np.mean(away_goals) if away_goals else 0
            
            # Determina tendência recente
            if home_wins > away_wins:
                recent_trend = f"Favorável ao {home_team}"
            elif away_wins > home_wins:
                recent_trend = f"Favorável ao {away_team}"
            else:
                recent_trend = "Equilibrado"
            
            return HeadToHead(
                home_team=home_team,
                away_team=away_team,
                matches=h2h_matches,
                home_wins=home_wins,
                away_wins=away_wins,
                draws=draws,
                home_advantage=home_advantage,
                avg_goals_home=avg_goals_home,
                avg_goals_away=avg_goals_away,
                recent_trend=recent_trend
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de confrontos diretos: {e}")
            return self._create_empty_h2h(home_team, away_team)
    
    def generate_detailed_statistical_report(self, home_team: str, away_team: str) -> str:
        """
        Gera relatório estatístico detalhado
        """
        logger.info(f"Gerando relatório estatístico: {home_team} vs {away_team}")
        
        try:
            # Análise de forma recente
            home_form = self.generate_team_form_analysis(home_team, "Home", 5)
            away_form = self.generate_team_form_analysis(away_team, "Away", 5)
            
            # Análise de confrontos diretos
            h2h = self.generate_head_to_head_analysis(home_team, away_team, 5)
            
            # Gera relatório formatado
            report = self._format_statistical_report(home_team, away_team, home_form, away_form, h2h)
            
            return report
            
        except Exception as e:
            logger.error(f"Erro na geração do relatório estatístico: {e}")
            return f"Erro na análise estatística: {e}"
    
    def _format_statistical_report(self, home_team: str, away_team: str, 
                                 home_form: TeamForm, away_form: TeamForm, 
                                 h2h: HeadToHead) -> str:
        """Formata relatório estatístico detalhado"""
        
        # Formata tabela de forma recente - Casa
        home_table = self._format_form_table(home_form, "Casa")
        
        # Formata tabela de forma recente - Fora
        away_table = self._format_form_table(away_form, "Fora")
        
        # Formata tabela de confrontos diretos
        h2h_table = self._format_h2h_table(h2h)
        
        report = f"""
ANÁLISE ESTATÍSTICA DETALHADA
{'='*60}

Forma Recente (Últimos 5 Jogos)
{'-'*40}

{home_team} (Casa):
{home_table}

Média: {home_form.avg_goals_scored:.1f} gols/jogo | xG: {home_form.avg_xg:.2f} | {home_form.win_rate:.0%} aproveitamento

{away_team} (Fora):
{away_table}

Média: {away_form.avg_goals_scored:.1f} gols/jogo | xG: {away_form.avg_xg:.2f} | {away_form.win_rate:.0%} aproveitamento

Confrontos Diretos (Últimos 5)
{'-'*40}
{h2h_table}

Vantagem {home_team}: {h2h.home_advantage:.0%} vitórias em casa

MÉTRICAS AVANÇADAS
{'-'*40}
• Diferença de xG: {home_form.avg_xg - away_form.avg_xg:+.2f}
• Diferença de gols: {home_form.avg_goals_scored - away_form.avg_goals_scored:+.1f}
• Eficiência ofensiva {home_team}: {home_form.avg_goals_scored / home_form.avg_xg:.2f}
• Eficiência ofensiva {away_team}: {away_form.avg_goals_scored / away_form.avg_xg:.2f}
• Defesa {home_team}: {home_form.avg_goals_conceded:.1f} gols/jogo
• Defesa {away_team}: {away_form.avg_goals_conceded:.1f} gols/jogo

TENDÊNCIAS RECENTES
{'-'*40}
• {home_team} em casa: {self._get_form_trend(home_form.results)}
• {away_team} fora: {self._get_form_trend(away_form.results)}
• Confrontos diretos: {h2h.recent_trend}
• Média de gols nos confrontos: {h2h.avg_goals_home:.1f}-{h2h.avg_goals_away:.1f}

ANÁLISE PREDITIVA
{'-'*40}
• Probabilidade de vitória {home_team}: {self._calculate_win_probability(home_form, away_form, h2h, home_team):.1%}
• Probabilidade de empate: {self._calculate_draw_probability(home_form, away_form, h2h):.1%}
• Probabilidade de vitória {away_team}: {self._calculate_win_probability(away_form, home_form, h2h, away_team):.1%}
• Total de gols esperado: {self._calculate_expected_goals(home_form, away_form):.1f}
• Mais de 2.5 gols: {self._calculate_over_25_probability(home_form, away_form):.1%}
"""
        
        return report
    
    def _format_form_table(self, form: TeamForm, venue: str) -> str:
        """Formata tabela de forma recente"""
        if not form.matches:
            return f"Nenhum jogo encontrado para {form.team_name} ({venue})"
        
        table = "Jogo\t\tResultado\tGols Marcados\tGols Sofridos\txG\n"
        table += "-" * 70 + "\n"
        
        for i, match in enumerate(form.matches, 1):
            if form.venue == "Home":
                opponent = match.away_team
                score = f"{match.home_score}-{match.away_score}"
                goals_scored = match.home_score
                goals_conceded = match.away_score
                xg = match.home_xg
            else:
                opponent = match.home_team
                score = f"{match.away_score}-{match.home_score}"
                goals_scored = match.away_score
                goals_conceded = match.home_score
                xg = match.away_xg
            
            result_symbol = "✓" if form.results[i-1] == 'W' else "✗" if form.results[i-1] == 'L' else "="
            
            table += f"{opponent[:3]}\t\t{score}\t{goals_scored}\t\t{goals_conceded}\t\t{xg:.1f}\n"
        
        return table
    
    def _format_h2h_table(self, h2h: HeadToHead) -> str:
        """Formata tabela de confrontos diretos"""
        if not h2h.matches:
            return f"Nenhum confronto direto encontrado entre {h2h.home_team} e {h2h.away_team}"
        
        table = ""
        for match in h2h.matches:
            if match.home_team == h2h.home_team:
                # Time da casa jogando em casa
                venue = "H"
                score = f"{match.home_score}-{match.away_score}"
                result = "✓" if match.home_score > match.away_score else "✗" if match.home_score < match.away_score else "="
            else:
                # Time da casa jogando fora
                venue = "A"
                score = f"{match.away_score}-{match.home_score}"
                result = "✓" if match.away_score > match.home_score else "✗" if match.away_score < match.home_score else "="
            
            table += f"{h2h.home_team[:3]} {score} {h2h.away_team[:3]} ({venue}) {result}\n"
        
        return table
    
    def _get_form_trend(self, results: List[str]) -> str:
        """Determina tendência da forma recente"""
        if not results:
            return "Sem dados"
        
        recent = results[-3:] if len(results) >= 3 else results
        wins = recent.count('W')
        draws = recent.count('D')
        losses = recent.count('L')
        
        if wins > losses:
            return f"Positiva ({wins}V-{draws}E-{losses}D)"
        elif losses > wins:
            return f"Negativa ({wins}V-{draws}E-{losses}D)"
        else:
            return f"Estável ({wins}V-{draws}E-{losses}D)"
    
    def _calculate_win_probability(self, team_form: TeamForm, opponent_form: TeamForm, 
                                 h2h: HeadToHead, team_name: str) -> float:
        """Calcula probabilidade de vitória"""
        # Fatores: forma recente (40%), confrontos diretos (30%), xG (20%), home advantage (10%)
        form_factor = team_form.win_rate * 0.4
        h2h_factor = h2h.home_advantage if team_name == h2h.home_team else (1 - h2h.home_advantage)
        h2h_factor *= 0.3
        xg_factor = (team_form.avg_xg / (team_form.avg_xg + opponent_form.avg_xg)) * 0.2
        home_advantage = 0.1 if team_form.venue == "Home" else 0
        
        return form_factor + h2h_factor + xg_factor + home_advantage
    
    def _calculate_draw_probability(self, home_form: TeamForm, away_form: TeamForm, h2h: HeadToHead) -> float:
        """Calcula probabilidade de empate"""
        # Baseado na diferença de força entre os times
        strength_diff = abs(home_form.win_rate - away_form.win_rate)
        return max(0.2, 0.4 - strength_diff)
    
    def _calculate_expected_goals(self, home_form: TeamForm, away_form: TeamForm) -> float:
        """Calcula total de gols esperado"""
        return home_form.avg_goals_scored + away_form.avg_goals_scored
    
    def _calculate_over_25_probability(self, home_form: TeamForm, away_form: TeamForm) -> float:
        """Calcula probabilidade de mais de 2.5 gols"""
        expected_goals = self._calculate_expected_goals(home_form, away_form)
        # Usa distribuição de Poisson para calcular P(goals > 2.5)
        if expected_goals <= 0:
            return 0.0
        
        # Aproximação simples baseada na média
        if expected_goals >= 3.0:
            return 0.8
        elif expected_goals >= 2.5:
            return 0.6
        elif expected_goals >= 2.0:
            return 0.4
        else:
            return 0.2
    
    def _update_team_stats(self, match: MatchResult):
        """Atualiza estatísticas dos times"""
        # Implementação simplificada - em produção seria mais complexa
        pass
    
    def _create_empty_team_form(self, team_name: str, venue: str) -> TeamForm:
        """Cria TeamForm vazio em caso de erro"""
        return TeamForm(
            team_name=team_name,
            matches=[],
            venue=venue,
            goals_scored=[],
            goals_conceded=[],
            xg_values=[],
            results=[],
            avg_goals_scored=0,
            avg_goals_conceded=0,
            avg_xg=0,
            win_rate=0,
            points_per_game=0
        )
    
    def _create_empty_h2h(self, home_team: str, away_team: str) -> HeadToHead:
        """Cria HeadToHead vazio em caso de erro"""
        return HeadToHead(
            home_team=home_team,
            away_team=away_team,
            matches=[],
            home_wins=0,
            away_wins=0,
            draws=0,
            home_advantage=0,
            avg_goals_home=0,
            avg_goals_away=0,
            recent_trend="Sem dados"
        )
    
    def load_sample_data(self):
        """Carrega dados de exemplo para demonstração"""
        logger.info("Carregando dados de exemplo")
        
        # Dados de exemplo para Manchester City (Casa)
        mci_home_matches = [
            MatchResult("Manchester City", "Chelsea", 3, 1, 2.4, 1.2, "2024-01-10", "H", "W"),
            MatchResult("Manchester City", "Newcastle", 2, 0, 2.8, 0.8, "2024-01-07", "H", "W"),
            MatchResult("Manchester City", "West Ham", 4, 1, 3.2, 1.1, "2024-01-03", "H", "W"),
            MatchResult("Manchester City", "Liverpool", 1, 1, 1.9, 1.5, "2023-12-30", "H", "D"),
            MatchResult("Manchester City", "Brentford", 2, 0, 2.1, 0.9, "2023-12-27", "H", "W"),
        ]
        
        # Dados de exemplo para Arsenal (Fora)
        ars_away_matches = [
            MatchResult("Tottenham", "Arsenal", 2, 3, 1.8, 2.3, "2024-01-09", "A", "W"),
            MatchResult("Aston Villa", "Arsenal", 1, 2, 1.2, 1.8, "2024-01-06", "A", "W"),
            MatchResult("Leicester", "Arsenal", 1, 1, 1.5, 2.0, "2024-01-02", "A", "D"),
            MatchResult("Brighton", "Arsenal", 0, 2, 0.8, 2.4, "2023-12-29", "A", "W"),
            MatchResult("Everton", "Arsenal", 0, 1, 0.9, 1.6, "2023-12-26", "A", "W"),
        ]
        
        # Dados de confrontos diretos
        h2h_matches = [
            MatchResult("Manchester City", "Arsenal", 3, 1, 2.8, 1.2, "2023-10-15", "H", "W"),
            MatchResult("Arsenal", "Manchester City", 0, 0, 1.5, 1.8, "2023-04-26", "A", "D"),
            MatchResult("Manchester City", "Arsenal", 4, 1, 3.1, 0.9, "2023-02-15", "H", "W"),
            MatchResult("Arsenal", "Manchester City", 1, 3, 1.2, 2.5, "2022-11-05", "A", "L"),
            MatchResult("Manchester City", "Arsenal", 3, 0, 2.9, 0.8, "2022-08-13", "H", "W"),
        ]
        
        # Adiciona todos os dados
        for match in mci_home_matches + ars_away_matches + h2h_matches:
            self.add_match_result(match)
        
        logger.info("Dados de exemplo carregados com sucesso")

if __name__ == "__main__":
    # Teste do analisador estatístico
    analyzer = StatisticalAnalyzer()
    
    print("=== TESTE DO ANALISADOR ESTATÍSTICO ===")
    
    # Carrega dados de exemplo
    analyzer.load_sample_data()
    
    # Gera relatório estatístico
    report = analyzer.generate_detailed_statistical_report("Manchester City", "Arsenal")
    
    print(report)
    
    print("\nTeste concluído!")
