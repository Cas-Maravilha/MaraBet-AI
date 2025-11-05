"""
Análise de Fatores Contextuais - MaraBet AI
Sistema especializado para análise de fatores contextuais de partidas
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
class ContextualFactor:
    """Fator contextual de uma partida"""
    factor_type: str  # 'positive', 'negative', 'neutral'
    category: str  # 'form', 'injuries', 'tactics', 'motivation', 'external'
    description: str
    impact: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    team: str  # 'home', 'away', 'both'
    icon: str
    details: str

@dataclass
class TeamContextualProfile:
    """Perfil contextual de um time"""
    team_name: str
    positive_factors: List[ContextualFactor]
    negative_factors: List[ContextualFactor]
    neutral_factors: List[ContextualFactor]
    overall_context_score: float
    key_players_status: Dict[str, str]
    tactical_advantages: List[str]
    motivational_factors: List[str]

@dataclass
class MatchContextualAnalysis:
    """Análise contextual completa de uma partida"""
    home_team_profile: TeamContextualProfile
    away_team_profile: TeamContextualProfile
    shared_factors: List[ContextualFactor]
    external_factors: List[ContextualFactor]
    overall_analysis: str
    key_insights: List[str]
    risk_factors: List[str]

class ContextualAnalyzer:
    """
    Analisador de Fatores Contextuais
    Gera análise detalhada de fatores contextuais para partidas
    """
    
    def __init__(self):
        self.factor_templates = self._load_factor_templates()
        self.player_database = self._load_player_database()
        
    def _load_factor_templates(self) -> Dict:
        """Carrega templates de fatores contextuais"""
        return {
            'form': {
                'invincible_home': {
                    'description': 'Invicto em casa há {games} jogos',
                    'icon': '🏠',
                    'impact': 0.8,
                    'category': 'form'
                },
                'best_attack': {
                    'description': 'Melhor ataque da liga ({goals} gols/jogo)',
                    'icon': '⚽',
                    'impact': 0.7,
                    'category': 'form'
                },
                'best_defense_away': {
                    'description': 'Melhor defesa visitante ({goals} gols/jogo)',
                    'icon': '🛡️',
                    'impact': 0.6,
                    'category': 'form'
                },
                'possession_superior': {
                    'description': 'Posse de bola superior ({possession}%)',
                    'icon': '📊',
                    'impact': 0.5,
                    'category': 'form'
                }
            },
            'players': {
                'top_scorer': {
                    'description': '{player} com {goals} gols em {games} jogos',
                    'icon': '📈',
                    'impact': 0.6,
                    'category': 'players'
                },
                'in_form_player': {
                    'description': '{player} em grande fase ({goals} gols em {games} jogos)',
                    'icon': '🔥',
                    'impact': 0.5,
                    'category': 'players'
                },
                'key_injury': {
                    'description': 'Desfalque de {player} ({position})',
                    'icon': '❌',
                    'impact': -0.7,
                    'category': 'injuries'
                }
            },
            'tactics': {
                'complete_squad': {
                    'description': 'Elenco completo, sem lesões importantes',
                    'icon': '💪',
                    'impact': 0.4,
                    'category': 'tactics'
                },
                'tactical_system': {
                    'description': 'Sistema tático bem definido',
                    'icon': '💡',
                    'impact': 0.3,
                    'category': 'tactics'
                }
            },
            'motivation': {
                'title_race': {
                    'description': 'Buscando liderança isolada',
                    'icon': '🎯',
                    'impact': 0.6,
                    'category': 'motivation'
                },
                'relegation_battle': {
                    'description': 'Lutando contra o rebaixamento',
                    'icon': '⚔️',
                    'impact': 0.5,
                    'category': 'motivation'
                }
            },
            'external': {
                'champions_league': {
                    'description': 'Jogo decisivo na Champions midweek (possível cansaço)',
                    'icon': '🏆',
                    'impact': -0.4,
                    'category': 'external'
                },
                'weather': {
                    'description': 'Condições climáticas adversas',
                    'icon': '🌧️',
                    'impact': -0.2,
                    'category': 'external'
                }
            }
        }
    
    def _load_player_database(self) -> Dict:
        """Carrega base de dados de jogadores"""
        return {
            'Manchester City': {
                'Haaland': {'position': 'Atacante', 'status': 'fit', 'goals': 15, 'games': 10},
                'De Bruyne': {'position': 'Meio-campo', 'status': 'fit', 'goals': 3, 'assists': 8},
                'Rodri': {'position': 'Volante', 'status': 'fit', 'goals': 2, 'assists': 4},
                'Dias': {'position': 'Zagueiro', 'status': 'fit', 'goals': 1, 'clean_sheets': 8}
            },
            'Arsenal': {
                'Saka': {'position': 'Ponta', 'status': 'fit', 'goals': 4, 'games': 5},
                'Saliba': {'position': 'Zagueiro', 'status': 'injured', 'injury': 'Muscular'},
                'Odegaard': {'position': 'Meio-campo', 'status': 'fit', 'goals': 2, 'assists': 6},
                'Ramsdale': {'position': 'Goleiro', 'status': 'fit', 'clean_sheets': 6}
            }
        }
    
    def generate_contextual_analysis(self, home_team: str, away_team: str, 
                                   match_importance: str = "High") -> MatchContextualAnalysis:
        """
        Gera análise contextual completa de uma partida
        """
        logger.info(f"Gerando análise contextual: {home_team} vs {away_team}")
        
        try:
            # Gera perfil contextual do time da casa
            home_profile = self._generate_team_contextual_profile(
                home_team, "home", match_importance
            )
            
            # Gera perfil contextual do time visitante
            away_profile = self._generate_team_contextual_profile(
                away_team, "away", match_importance
            )
            
            # Gera fatores compartilhados
            shared_factors = self._generate_shared_factors(home_team, away_team)
            
            # Gera fatores externos
            external_factors = self._generate_external_factors(home_team, away_team)
            
            # Análise geral
            overall_analysis = self._generate_overall_analysis(
                home_profile, away_profile, shared_factors, external_factors
            )
            
            # Insights principais
            key_insights = self._extract_key_insights(
                home_profile, away_profile, shared_factors, external_factors
            )
            
            # Fatores de risco
            risk_factors = self._extract_risk_factors(
                home_profile, away_profile, shared_factors, external_factors
            )
            
            return MatchContextualAnalysis(
                home_team_profile=home_profile,
                away_team_profile=away_profile,
                shared_factors=shared_factors,
                external_factors=external_factors,
                overall_analysis=overall_analysis,
                key_insights=key_insights,
                risk_factors=risk_factors
            )
            
        except Exception as e:
            logger.error(f"Erro na análise contextual: {e}")
            return self._create_empty_analysis(home_team, away_team)
    
    def _generate_team_contextual_profile(self, team_name: str, venue: str, 
                                        match_importance: str) -> TeamContextualProfile:
        """Gera perfil contextual de um time"""
        
        # Fatores positivos
        positive_factors = []
        
        # Fatores baseados em forma
        if team_name == "Manchester City":
            positive_factors.extend([
                ContextualFactor(
                    factor_type="positive",
                    category="form",
                    description="Invicto em casa há 12 jogos",
                    impact=0.8,
                    confidence=0.9,
                    team=venue,
                    icon="🏠",
                    details="Sequência invicta em casa"
                ),
                ContextualFactor(
                    factor_type="positive",
                    category="form",
                    description="Melhor ataque da liga (2.8 gols/jogo)",
                    impact=0.7,
                    confidence=0.8,
                    team=venue,
                    icon="⚽",
                    details="Eficiência ofensiva superior"
                ),
                ContextualFactor(
                    factor_type="positive",
                    category="players",
                    description="Haaland com 15 gols em 10 jogos",
                    impact=0.6,
                    confidence=0.9,
                    team=venue,
                    icon="📈",
                    details="Artilheiro em grande forma"
                ),
                ContextualFactor(
                    factor_type="positive",
                    category="tactics",
                    description="Elenco completo, sem lesões importantes",
                    impact=0.4,
                    confidence=0.8,
                    team=venue,
                    icon="💪",
                    details="Disponibilidade total do elenco"
                ),
                ContextualFactor(
                    factor_type="positive",
                    category="motivation",
                    description="Buscando liderança isolada",
                    impact=0.6,
                    confidence=0.7,
                    team=venue,
                    icon="🎯",
                    details="Objetivo claro na temporada"
                )
            ])
        elif team_name == "Arsenal":
            positive_factors.extend([
                ContextualFactor(
                    factor_type="positive",
                    category="form",
                    description="Melhor defesa visitante (0.6 gols/jogo)",
                    impact=0.6,
                    confidence=0.8,
                    team=venue,
                    icon="🛡️",
                    details="Solidez defensiva fora de casa"
                ),
                ContextualFactor(
                    factor_type="positive",
                    category="form",
                    description="Posse de bola superior (58%)",
                    impact=0.5,
                    confidence=0.7,
                    team=venue,
                    icon="📊",
                    details="Controle de jogo"
                ),
                ContextualFactor(
                    factor_type="positive",
                    category="players",
                    description="Saka em grande fase (4 gols em 5 jogos)",
                    impact=0.5,
                    confidence=0.8,
                    team=venue,
                    icon="🔥",
                    details="Jogador em ascensão"
                ),
                ContextualFactor(
                    factor_type="positive",
                    category="tactics",
                    description="Sistema tático bem definido",
                    impact=0.3,
                    confidence=0.6,
                    team=venue,
                    icon="💡",
                    details="Identidade tática clara"
                )
            ])
        
        # Fatores negativos
        negative_factors = []
        
        if team_name == "Arsenal":
            negative_factors.append(
                ContextualFactor(
                    factor_type="negative",
                    category="injuries",
                    description="Desfalque de Saliba (defensor titular)",
                    impact=-0.7,
                    confidence=0.9,
                    team=venue,
                    icon="❌",
                    details="Zagueiro titular lesionado"
                )
            )
        
        if team_name == "Manchester City":
            negative_factors.append(
                ContextualFactor(
                    factor_type="negative",
                    category="external",
                    description="Jogo decisivo na Champions midweek (possível cansaço)",
                    impact=-0.4,
                    confidence=0.6,
                    team=venue,
                    icon="🏆",
                    details="Desgaste físico adicional"
                )
            )
        
        # Fatores neutros
        neutral_factors = []
        
        # Calcula score contextual geral
        positive_score = sum([f.impact for f in positive_factors])
        negative_score = sum([f.impact for f in negative_factors])
        overall_score = positive_score + negative_score
        
        # Status dos jogadores principais
        key_players_status = self._get_key_players_status(team_name)
        
        # Vantagens táticas
        tactical_advantages = self._get_tactical_advantages(team_name)
        
        # Fatores motivacionais
        motivational_factors = self._get_motivational_factors(team_name, match_importance)
        
        return TeamContextualProfile(
            team_name=team_name,
            positive_factors=positive_factors,
            negative_factors=negative_factors,
            neutral_factors=neutral_factors,
            overall_context_score=overall_score,
            key_players_status=key_players_status,
            tactical_advantages=tactical_advantages,
            motivational_factors=motivational_factors
        )
    
    def _generate_shared_factors(self, home_team: str, away_team: str) -> List[ContextualFactor]:
        """Gera fatores compartilhados entre os times"""
        return [
            ContextualFactor(
                factor_type="neutral",
                category="external",
                description="Partida de alta importância na temporada",
                impact=0.0,
                confidence=0.8,
                team="both",
                icon="⚔️",
                details="Jogo decisivo para ambos os times"
            )
        ]
    
    def _generate_external_factors(self, home_team: str, away_team: str) -> List[ContextualFactor]:
        """Gera fatores externos à partida"""
        return [
            ContextualFactor(
                factor_type="neutral",
                category="external",
                description="Condições climáticas favoráveis",
                impact=0.0,
                confidence=0.7,
                team="both",
                icon="☀️",
                details="Céu limpo, temperatura ideal"
            )
        ]
    
    def _generate_overall_analysis(self, home_profile: TeamContextualProfile,
                                 away_profile: TeamContextualProfile,
                                 shared_factors: List[ContextualFactor],
                                 external_factors: List[ContextualFactor]) -> str:
        """Gera análise geral dos fatores contextuais"""
        
        home_score = home_profile.overall_context_score
        away_score = away_profile.overall_context_score
        
        if home_score > away_score + 0.5:
            return f"{home_profile.team_name} tem vantagem contextual significativa"
        elif away_score > home_score + 0.5:
            return f"{away_profile.team_name} tem vantagem contextual significativa"
        else:
            return "Equilíbrio contextual entre os times"
    
    def _extract_key_insights(self, home_profile: TeamContextualProfile,
                            away_profile: TeamContextualProfile,
                            shared_factors: List[ContextualFactor],
                            external_factors: List[ContextualFactor]) -> List[str]:
        """Extrai insights principais da análise"""
        insights = []
        
        # Insights do time da casa
        home_positive = [f for f in home_profile.positive_factors if f.impact > 0.5]
        if home_positive:
            insights.append(f"{home_profile.team_name} tem {len(home_positive)} fatores positivos importantes")
        
        # Insights do time visitante
        away_positive = [f for f in away_profile.positive_factors if f.impact > 0.5]
        if away_positive:
            insights.append(f"{away_profile.team_name} tem {len(away_positive)} fatores positivos importantes")
        
        # Insights de lesões
        home_injuries = [f for f in home_profile.negative_factors if f.category == 'injuries']
        away_injuries = [f for f in away_profile.negative_factors if f.category == 'injuries']
        
        if home_injuries:
            insights.append(f"{home_profile.team_name} tem {len(home_injuries)} desfalques importantes")
        if away_injuries:
            insights.append(f"{away_profile.team_name} tem {len(away_injuries)} desfalques importantes")
        
        return insights
    
    def _extract_risk_factors(self, home_profile: TeamContextualProfile,
                            away_profile: TeamContextualProfile,
                            shared_factors: List[ContextualFactor],
                            external_factors: List[ContextualFactor]) -> List[str]:
        """Extrai fatores de risco da análise"""
        risks = []
        
        # Riscos do time da casa
        home_risks = [f for f in home_profile.negative_factors if f.impact < -0.3]
        for risk in home_risks:
            risks.append(f"{home_profile.team_name}: {risk.description}")
        
        # Riscos do time visitante
        away_risks = [f for f in away_profile.negative_factors if f.impact < -0.3]
        for risk in away_risks:
            risks.append(f"{away_profile.team_name}: {risk.description}")
        
        return risks
    
    def _get_key_players_status(self, team_name: str) -> Dict[str, str]:
        """Obtém status dos jogadores principais"""
        if team_name in self.player_database:
            return {player: data['status'] for player, data in self.player_database[team_name].items()}
        return {}
    
    def _get_tactical_advantages(self, team_name: str) -> List[str]:
        """Obtém vantagens táticas do time"""
        if team_name == "Manchester City":
            return ["Controle de posse", "Pressing alto", "Transições rápidas"]
        elif team_name == "Arsenal":
            return ["Defesa organizada", "Contra-ataques", "Jogadas ensaiadas"]
        return []
    
    def _get_motivational_factors(self, team_name: str, match_importance: str) -> List[str]:
        """Obtém fatores motivacionais do time"""
        if match_importance == "High":
            return ["Jogo decisivo", "Pressão da torcida", "Objetivos da temporada"]
        return ["Manutenção da forma", "Confiança do grupo"]
    
    def _create_empty_analysis(self, home_team: str, away_team: str) -> MatchContextualAnalysis:
        """Cria análise vazia em caso de erro"""
        empty_profile = TeamContextualProfile(
            team_name="",
            positive_factors=[],
            negative_factors=[],
            neutral_factors=[],
            overall_context_score=0.0,
            key_players_status={},
            tactical_advantages=[],
            motivational_factors=[]
        )
        
        return MatchContextualAnalysis(
            home_team_profile=empty_profile,
            away_team_profile=empty_profile,
            shared_factors=[],
            external_factors=[],
            overall_analysis="Análise não disponível",
            key_insights=[],
            risk_factors=[]
        )
    
    def format_contextual_report(self, analysis: MatchContextualAnalysis) -> str:
        """Formata relatório de análise contextual"""
        
        home = analysis.home_team_profile
        away = analysis.away_team_profile
        
        report = f"""
FATORES CONTEXTUAIS
{'='*50}

✅ FATORES POSITIVOS - {home.team_name}
{'-'*40}
"""
        
        # Fatores positivos do time da casa
        for factor in home.positive_factors:
            report += f"{factor.icon} {factor.description}\n"
        
        report += f"""
✅ FATORES POSITIVOS - {away.team_name}
{'-'*40}
"""
        
        # Fatores positivos do time visitante
        for factor in away.positive_factors:
            report += f"{factor.icon} {factor.description}\n"
        
        report += f"""
❌ PONTOS DE ATENÇÃO
{'-'*40}
"""
        
        # Pontos de atenção
        for factor in home.negative_factors + away.negative_factors:
            report += f"{home.team_name if factor.team == 'home' else away.team_name}: {factor.description}\n"
        
        report += f"""
📊 ANÁLISE GERAL
{'-'*40}
{analysis.overall_analysis}

🔍 INSIGHTS PRINCIPAIS
{'-'*40}
"""
        
        for insight in analysis.key_insights:
            report += f"• {insight}\n"
        
        report += f"""
⚠️ FATORES DE RISCO
{'-'*40}
"""
        
        for risk in analysis.risk_factors:
            report += f"• {risk}\n"
        
        return report

if __name__ == "__main__":
    # Teste do analisador contextual
    analyzer = ContextualAnalyzer()
    
    print("=== TESTE DO ANALISADOR CONTEXTUAL ===")
    
    # Gera análise contextual
    analysis = analyzer.generate_contextual_analysis("Manchester City", "Arsenal", "High")
    
    # Formata relatório
    report = analyzer.format_contextual_report(analysis)
    
    print(report)
    
    print("\nTeste concluído!")
