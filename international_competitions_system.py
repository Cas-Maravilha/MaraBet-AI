#!/usr/bin/env python3
"""
Sistema de Competições Internacionais - MaraBet AI
Cobertura completa de competições europeias e internacionais
"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InternationalCompetitionsSystem:
    """Sistema de cobertura de competições internacionais"""
    
    def __init__(self):
        self.api_key = "71b2b62386f2d1275cd3201a73e1e045"
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        
        # Competições internacionais completas
        self.international_competitions = {
            # COMPETIÇÕES EUROPEIAS
            'Champions League': {'id': 2, 'country': 'Europe', 'priority': 1, 'type': 'Club', 'tier': 'Tier 1'},
            'Europa League': {'id': 3, 'country': 'Europe', 'priority': 1, 'type': 'Club', 'tier': 'Tier 1'},
            'Conference League': {'id': 848, 'country': 'Europe', 'priority': 1, 'type': 'Club', 'tier': 'Tier 1'},
            'Super Cup': {'id': 667, 'country': 'Europe', 'priority': 1, 'type': 'Club', 'tier': 'Tier 1'},
            
            # COMPETIÇÕES INTERNACIONAIS
            'World Cup': {'id': 1, 'country': 'World', 'priority': 1, 'type': 'National', 'tier': 'Tier 1'},
            'Copa America': {'id': 9, 'country': 'South America', 'priority': 1, 'type': 'National', 'tier': 'Tier 1'},
            'African Cup': {'id': 13, 'country': 'Africa', 'priority': 1, 'type': 'National', 'tier': 'Tier 1'},
            'Euro Championship': {'id': 4, 'country': 'Europe', 'priority': 1, 'type': 'National', 'tier': 'Tier 1'},
            'Nations League': {'id': 5, 'country': 'Europe', 'priority': 2, 'type': 'National', 'tier': 'Tier 2'},
            
            # OUTRAS COMPETIÇÕES IMPORTANTES
            'Gold Cup': {'id': 12, 'country': 'North America', 'priority': 2, 'type': 'National', 'tier': 'Tier 2'},
            'Asian Cup': {'id': 14, 'country': 'Asia', 'priority': 2, 'type': 'National', 'tier': 'Tier 2'},
            'Oceania Cup': {'id': 15, 'country': 'Oceania', 'priority': 3, 'type': 'National', 'tier': 'Tier 3'},
            
            # LIGAS NACIONAIS PRINCIPAIS (TIER 1)
            'Premier League': {'id': 39, 'country': 'England', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            'La Liga': {'id': 140, 'country': 'Spain', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            'Bundesliga': {'id': 78, 'country': 'Germany', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            'Serie A': {'id': 135, 'country': 'Italy', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            'Ligue 1': {'id': 61, 'country': 'France', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            'Serie A': {'id': 71, 'country': 'Brazil', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            'Primera División': {'id': 128, 'country': 'Argentina', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            
            # LIGAS NACIONAIS IMPORTANTES (TIER 2)
            'Eredivisie': {'id': 88, 'country': 'Netherlands', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'Primeira Liga': {'id': 94, 'country': 'Portugal', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'Championship': {'id': 40, 'country': 'England', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'MLS': {'id': 253, 'country': 'USA', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'Liga MX': {'id': 262, 'country': 'Mexico', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'Süper Lig': {'id': 203, 'country': 'Turkey', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'Russian Premier League': {'id': 235, 'country': 'Russia', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'Belgian Pro League': {'id': 144, 'country': 'Belgium', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'Scottish Premiership': {'id': 39, 'country': 'Scotland', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'Austrian Bundesliga': {'id': 218, 'country': 'Austria', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'Swiss Super League': {'id': 169, 'country': 'Switzerland', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'Danish Superliga': {'id': 119, 'country': 'Denmark', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'Norwegian Eliteserien': {'id': 113, 'country': 'Norway', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
            'Swedish Allsvenskan': {'id': 113, 'country': 'Sweden', 'priority': 2, 'type': 'League', 'tier': 'Tier 2'},
        }
        
        # Status de partidas
        self.match_statuses = {
            'NS': 'Não Iniciada',
            '1H': '1º Tempo',
            '2H': '2º Tempo', 
            'HT': 'Intervalo',
            'LIVE': 'Ao Vivo',
            'FT': 'Finalizada',
            'AET': 'Prorrogação',
            'PEN': 'Pênaltis',
            'SUSP': 'Suspensa',
            'CANC': 'Cancelada',
            'ABD': 'Abandonada'
        }
    
    def get_international_competitions_info(self):
        """Obtém informações das competições internacionais"""
        logger.info("🌍 OBTENDO INFORMAÇÕES DAS COMPETIÇÕES INTERNACIONAIS")
        print("=" * 60)
        
        try:
            response = requests.get(
                f"{self.base_url}/leagues",
                headers=self.headers,
                params={'season': 2024},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                leagues = data.get('response', [])
                
                # Filtrar apenas competições internacionais
                international_found = []
                for league in leagues:
                    league_id = league['league']['id']
                    league_name = league['league']['name']
                    country = league['country']['name']
                    
                    # Verificar se é uma competição internacional
                    for comp_name, comp_info in self.international_competitions.items():
                        if comp_info['id'] == league_id:
                            international_found.append({
                                'id': league_id,
                                'name': league_name,
                                'country': country,
                                'priority': comp_info['priority'],
                                'type': comp_info['type'],
                                'tier': comp_info['tier']
                            })
                            break
                
                logger.info(f"   {len(international_found)} competições internacionais encontradas")
                return international_found
            else:
                logger.error(f"   Erro na API: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"   Erro ao buscar competições: {e}")
            return []
    
    def get_international_matches_today(self, max_competitions=15):
        """Obtém partidas de hoje de todas as competições internacionais"""
        logger.info("🌍 OBTENDO PARTIDAS INTERNACIONAIS DE HOJE")
        print("=" * 60)
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            all_matches = []
            
            # Buscar partidas de cada competição internacional
            for comp_name, comp_info in list(self.international_competitions.items())[:max_competitions]:
                try:
                    response = requests.get(
                        f"{self.base_url}/fixtures",
                        headers=self.headers,
                        params={
                            'date': today,
                            'league': comp_info['id'],
                            'season': 2024
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        matches = data.get('response', [])
                        
                        # Adicionar informações da competição
                        for match in matches:
                            match['competition_info'] = comp_info
                        
                        all_matches.extend(matches)
                        if matches:
                            logger.info(f"   {comp_name} ({comp_info['country']}): {len(matches)} partidas")
                        
                except Exception as e:
                    logger.error(f"   Erro ao buscar {comp_name}: {e}")
                    continue
            
            logger.info(f"   Total: {len(all_matches)} partidas internacionais encontradas")
            return all_matches
            
        except Exception as e:
            logger.error(f"   Erro ao buscar partidas internacionais: {e}")
            return []
    
    def get_international_live_matches(self, max_competitions=15):
        """Obtém partidas ao vivo de todas as competições internacionais"""
        logger.info("🔴 OBTENDO PARTIDAS AO VIVO INTERNACIONAIS")
        print("=" * 60)
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            all_live_matches = []
            
            # Buscar partidas ao vivo de cada competição internacional
            for comp_name, comp_info in list(self.international_competitions.items())[:max_competitions]:
                try:
                    response = requests.get(
                        f"{self.base_url}/fixtures",
                        headers=self.headers,
                        params={
                            'date': today,
                            'league': comp_info['id'],
                            'season': 2024,
                            'status': 'LIVE'
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        matches = data.get('response', [])
                        
                        # Adicionar informações da competição
                        for match in matches:
                            match['competition_info'] = comp_info
                        
                        all_live_matches.extend(matches)
                        if matches:
                            logger.info(f"   {comp_name} ({comp_info['country']}): {len(matches)} partidas ao vivo")
                        
                except Exception as e:
                    logger.error(f"   Erro ao buscar {comp_name}: {e}")
                    continue
            
            logger.info(f"   Total: {len(all_live_matches)} partidas ao vivo internacionais")
            return all_live_matches
            
        except Exception as e:
            logger.error(f"   Erro ao buscar partidas ao vivo: {e}")
            return []
    
    def get_international_future_matches(self, days_ahead=7, max_competitions=15):
        """Obtém partidas futuras de todas as competições internacionais"""
        logger.info(f"🔮 OBTENDO PARTIDAS FUTURAS INTERNACIONAIS (PRÓXIMOS {days_ahead} DIAS)")
        print("=" * 60)
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            future_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            all_future_matches = []
            
            # Buscar partidas futuras de cada competição internacional
            for comp_name, comp_info in list(self.international_competitions.items())[:max_competitions]:
                try:
                    response = requests.get(
                        f"{self.base_url}/fixtures",
                        headers=self.headers,
                        params={
                            'from': today,
                            'to': future_date,
                            'league': comp_info['id'],
                            'season': 2024,
                            'status': 'NS'  # Not Started
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        matches = data.get('response', [])
                        
                        # Filtrar apenas partidas futuras
                        future_matches = []
                        for match in matches:
                            match_date = datetime.fromisoformat(match['fixture']['date'].replace('Z', '+00:00'))
                            if match_date > datetime.now():
                                match['competition_info'] = comp_info
                                future_matches.append(match)
                        
                        all_future_matches.extend(future_matches)
                        if future_matches:
                            logger.info(f"   {comp_name} ({comp_info['country']}): {len(future_matches)} partidas futuras")
                        
                except Exception as e:
                    logger.error(f"   Erro ao buscar {comp_name}: {e}")
                    continue
            
            logger.info(f"   Total: {len(all_future_matches)} partidas futuras internacionais")
            return all_future_matches
            
        except Exception as e:
            logger.error(f"   Erro ao buscar partidas futuras: {e}")
            return []
    
    def get_team_form(self, team_id, last_matches=10):
        """Obtém forma recente de um time"""
        try:
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={
                    'team': team_id,
                    'last': last_matches,
                    'status': 'FT'  # FT = Finished
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', [])
            return []
            
        except Exception as e:
            logger.error(f"   Erro ao buscar forma do time {team_id}: {e}")
            return []
    
    def calculate_team_strength(self, team_matches, is_home=True):
        """Calcula força de um time baseada em partidas recentes"""
        if not team_matches:
            return 0.5
        
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        
        for match in team_matches:
            home_score = match['goals']['home'] if match['goals']['home'] is not None else 0
            away_score = match['goals']['away'] if match['goals']['away'] is not None else 0
            
            if is_home:
                goals_for += home_score
                goals_against += away_score
                if home_score > away_score:
                    wins += 1
                elif home_score < away_score:
                    losses += 1
                else:
                    draws += 1
            else:
                goals_for += away_score
                goals_against += home_score
                if away_score > home_score:
                    wins += 1
                elif away_score < home_score:
                    losses += 1
                else:
                    draws += 1
        
        games = len(team_matches)
        if games == 0:
            return 0.5
        
        win_rate = wins / games
        draw_rate = draws / games
        loss_rate = losses / games
        
        avg_goals_for = goals_for / games
        avg_goals_against = goals_against / games
        
        # Calcular força combinada
        strength = (
            win_rate * 0.4 +           # Taxa de vitórias
            draw_rate * 0.1 +          # Taxa de empates
            min(avg_goals_for / 3, 1) * 0.25 +    # Ataque
            max(1 - avg_goals_against / 3, 0) * 0.25  # Defesa
        )
        
        return min(max(strength, 0.1), 0.9)
    
    def predict_match(self, match):
        """Prediz resultado de uma partida"""
        home_team = match['teams']['home']['name']
        away_team = match['teams']['away']['name']
        home_id = match['teams']['home']['id']
        away_id = match['teams']['away']['id']
        match_date = datetime.fromisoformat(match['fixture']['date'].replace('Z', '+00:00'))
        status = match['fixture']['status']['short']
        comp_info = match.get('competition_info', {})
        
        logger.info(f"🔮 PREDIZENDO: {home_team} vs {away_team} ({comp_info.get('name', 'Unknown')}) - {match_date.strftime('%H:%M')}")
        
        # Obter forma recente dos times
        home_form = self.get_team_form(home_id, 10)
        away_form = self.get_team_form(away_id, 10)
        
        # Calcular força dos times
        home_strength = self.calculate_team_strength(home_form, is_home=True)
        away_strength = self.calculate_team_strength(away_form, is_home=False)
        
        # Fator casa (varia por tipo de competição)
        home_advantage = 0.12  # Padrão para ligas nacionais
        
        if comp_info.get('type') == 'Club':
            # Competições de clubes
            if comp_info.get('name') in ['Champions League', 'Europa League', 'Conference League']:
                home_advantage = 0.08  # Menor vantagem em competições europeias
            else:
                home_advantage = 0.12
        elif comp_info.get('type') == 'National':
            # Competições nacionais
            if comp_info.get('name') in ['World Cup', 'Euro Championship', 'Copa America']:
                home_advantage = 0.15  # Maior vantagem em competições nacionais
            else:
                home_advantage = 0.10
        
        # Fator de confiabilidade
        home_reliability = min(len(home_form) / 10, 1.0)
        away_reliability = min(len(away_form) / 10, 1.0)
        avg_reliability = (home_reliability + away_reliability) / 2
        
        # Calcular probabilidades
        home_win_prob = min(0.85, max(0.05, home_strength + home_advantage - away_strength + 0.5))
        away_win_prob = min(0.85, max(0.05, away_strength - home_strength - home_advantage + 0.5))
        draw_prob = max(0.05, 1 - home_win_prob - away_win_prob)
        
        # Normalizar probabilidades
        total_prob = home_win_prob + draw_prob + away_win_prob
        home_win_prob /= total_prob
        draw_prob /= total_prob
        away_win_prob /= total_prob
        
        # Ajustar confiança
        confidence_multiplier = 0.5 + (avg_reliability * 0.5)
        
        # Calcular odds
        home_odds = 1 / home_win_prob if home_win_prob > 0 else 20
        draw_odds = 1 / draw_prob if draw_prob > 0 else 20
        away_odds = 1 / away_win_prob if away_win_prob > 0 else 20
        
        # Determinar predição
        if home_win_prob > draw_prob and home_win_prob > away_win_prob:
            prediction = "🏠 Casa"
            confidence = home_win_prob * confidence_multiplier
        elif away_win_prob > draw_prob and away_win_prob > home_win_prob:
            prediction = "✈️ Fora"
            confidence = away_win_prob * confidence_multiplier
        else:
            prediction = "🤝 Empate"
            confidence = draw_prob * confidence_multiplier
        
        return {
            'match_id': match['fixture']['id'],
            'home_team': home_team,
            'away_team': away_team,
            'date': match['fixture']['date'],
            'date_formatted': match_date.strftime('%d/%m %H:%M'),
            'status': status,
            'status_name': self.match_statuses.get(status, status),
            'competition': comp_info.get('name', 'Unknown'),
            'country': comp_info.get('country', 'Unknown'),
            'type': comp_info.get('type', 'Unknown'),
            'tier': comp_info.get('tier', 'Tier 3'),
            'priority': comp_info.get('priority', 3),
            'home_score': match['goals']['home'] if match['goals']['home'] is not None else 0,
            'away_score': match['goals']['away'] if match['goals']['away'] is not None else 0,
            'prediction': prediction,
            'confidence': confidence,
            'reliability': avg_reliability,
            'probabilities': {
                'home_win': home_win_prob,
                'draw': draw_prob,
                'away_win': away_win_prob
            },
            'odds': {
                'home_win': home_odds,
                'draw': draw_odds,
                'away_win': away_odds
            },
            'team_strengths': {
                'home': home_strength,
                'away': away_strength
            },
            'form_data': {
                'home_games': len(home_form),
                'away_games': len(away_form)
            }
        }
    
    def format_international_predictions_output(self, predictions, category="INTERNACIONAIS"):
        """Formata saída das predições internacionais"""
        if not predictions:
            return f"❌ Nenhuma partida {category.lower()} encontrada."
        
        output = f"🌍 PREDIÇÕES {category} - MARABET AI 🌍\n"
        output += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        output += f"🤖 Sistema de IA com dados reais da API Football\n"
        output += f"🌐 Cobertura: Competições internacionais completas\n\n"
        
        # Agrupar por tipo de competição
        predictions_by_type = {}
        for prediction in predictions:
            comp_type = prediction['type']
            if comp_type not in predictions_by_type:
                predictions_by_type[comp_type] = []
            predictions_by_type[comp_type].append(prediction)
        
        # Ordenar por tipo
        type_order = ['Club', 'National', 'League']
        for comp_type in type_order:
            if comp_type in predictions_by_type:
                type_predictions = predictions_by_type[comp_type]
                type_name = {'Club': 'COMPETIÇÕES DE CLUBES', 'National': 'COMPETIÇÕES NACIONAIS', 'League': 'LIGAS NACIONAIS'}.get(comp_type, comp_type.upper())
                
                output += f"🏆 {type_name} - {len(type_predictions)} partidas:\n"
                output += "=" * 50 + "\n\n"
                
                for i, prediction in enumerate(type_predictions, 1):
                    output += f"⚽ Partida {i}:\n"
                    output += f"⚔️ {prediction['home_team']} vs {prediction['away_team']}\n"
                    output += f"📅 {prediction['date_formatted']}\n"
                    output += f"🏆 {prediction['competition']} ({prediction['country']})\n"
                    output += f"📊 Status: {prediction['status_name']}\n"
                    output += f"🎯 Tier: {prediction['tier']}\n"
                    
                    if prediction['status'] in ['1H', '2H', 'HT', 'LIVE']:
                        output += f"⚽ Placar: {prediction['home_team']} {prediction['home_score']} x {prediction['away_score']} {prediction['away_team']}\n"
                    
                    output += "\n"
                    
                    output += f"🔮 Predição: {prediction['prediction']}\n"
                    output += f"📊 Confiança: {prediction['confidence']:.1%}\n"
                    output += f"🎯 Confiabilidade: {prediction['reliability']:.1%}\n\n"
                    
                    output += f"📈 Probabilidades:\n"
                    output += f"🏠 Casa: {prediction['probabilities']['home_win']:.1%}\n"
                    output += f"🤝 Empate: {prediction['probabilities']['draw']:.1%}\n"
                    output += f"✈️ Fora: {prediction['probabilities']['away_win']:.1%}\n\n"
                    
                    output += f"💰 Odds Calculadas:\n"
                    output += f"🏠 Casa: {prediction['odds']['home_win']:.2f}\n"
                    output += f"🤝 Empate: {prediction['odds']['draw']:.2f}\n"
                    output += f"✈️ Fora: {prediction['odds']['away_win']:.2f}\n\n"
                    
                    # Análise de valor
                    home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
                    draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
                    away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
                    
                    output += f"💎 Valor das Apostas:\n"
                    output += f"🏠 Casa: {home_value:.1%} {'✅' if home_value > 0.05 else '❌'}\n"
                    output += f"🤝 Empate: {draw_value:.1%} {'✅' if draw_value > 0.05 else '❌'}\n"
                    output += f"✈️ Fora: {away_value:.1%} {'✅' if away_value > 0.05 else '❌'}\n\n"
                    
                    # Dados de forma
                    output += f"📊 Dados de Forma:\n"
                    output += f"🏠 {prediction['home_team']}: {prediction['form_data']['home_games']} jogos analisados\n"
                    output += f"✈️ {prediction['away_team']}: {prediction['form_data']['away_games']} jogos analisados\n"
                    output += f"💪 Força: Casa {prediction['team_strengths']['home']:.2f} | Fora {prediction['team_strengths']['away']:.2f}\n\n"
                    
                    output += "─" * 50 + "\n\n"
        
        # Resumo
        avg_confidence = sum(p['confidence'] for p in predictions) / len(predictions)
        avg_reliability = sum(p['reliability'] for p in predictions) / len(predictions)
        positive_value_bets = 0
        
        for prediction in predictions:
            home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
            draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
            away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
            
            if home_value > 0.05 or draw_value > 0.05 or away_value > 0.05:
                positive_value_bets += 1
        
        output += f"📊 RESUMO DAS PREDIÇÕES {category}:\n"
        output += f"🔮 Predições: {len(predictions)}\n"
        output += f"📈 Confiança média: {avg_confidence:.1%}\n"
        output += f"🎯 Confiabilidade média: {avg_reliability:.1%}\n"
        output += f"💎 Apostas com valor: {positive_value_bets}/{len(predictions)}\n\n"
        
        # Estatísticas por tipo de competição
        types = {}
        for prediction in predictions:
            comp_type = prediction['type']
            types[comp_type] = types.get(comp_type, 0) + 1
        
        output += f"🌍 COBERTURA POR TIPO DE COMPETIÇÃO:\n"
        for comp_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            type_name = {'Club': 'Competições de Clubes', 'National': 'Competições Nacionais', 'League': 'Ligas Nacionais'}.get(comp_type, comp_type)
            output += f"   {type_name}: {count} partidas\n"
        
        # Estatísticas por país/região
        countries = {}
        for prediction in predictions:
            country = prediction['country']
            countries[country] = countries.get(country, 0) + 1
        
        output += f"\n🌍 COBERTURA POR PAÍS/REGIÃO:\n"
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
            output += f"   {country}: {count} partidas\n"
        
        output += f"\n⏰ IMPORTANTE: Predições baseadas em dados reais\n"
        output += f"🌐 COBERTURA: Competições internacionais completas\n"
        output += f"🏆 INCLUI: Champions League, Europa League, Copa do Mundo, Copa América, CAN, Euro\n"
        output += f"⚠️ AVISO: Apostas envolvem risco. Use com responsabilidade.\n"
        output += f"🤖 Powered by MaraBet AI - Sistema de IA para Futebol"
        
        return output
    
    def run_international_predictions(self, mode="today"):
        """Executa predições internacionais"""
        print("🌍 SISTEMA DE COMPETIÇÕES INTERNACIONAIS - MARABET AI")
        print("=" * 80)
        
        predictions = []
        
        if mode == "today":
            matches = self.get_international_matches_today()
            category = "INTERNACIONAIS DE HOJE"
        elif mode == "live":
            matches = self.get_international_live_matches()
            category = "INTERNACIONAIS AO VIVO"
        elif mode == "future":
            matches = self.get_international_future_matches()
            category = "INTERNACIONAIS FUTURAS"
        else:
            print("❌ Modo inválido. Use: today, live, ou future")
            return False
        
        if not matches:
            print(f"❌ Nenhuma partida {category.lower()} encontrada")
            return False
        
        print(f"📊 {len(matches)} partidas {category.lower()} encontradas")
        
        # Ordenar por prioridade da competição
        matches.sort(key=lambda x: x.get('competition_info', {}).get('priority', 3))
        
        # Gerar predições (limitado para não sobrecarregar)
        for match in matches[:20]:  # Limitar a 20 partidas
            try:
                prediction = self.predict_match(match)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"   Erro ao predizer partida: {e}")
                continue
        
        if not predictions:
            print("❌ Nenhuma predição gerada")
            return False
        
        print(f"🔮 {len(predictions)} predições {category.lower()} geradas")
        
        # Mostrar predições
        output = self.format_international_predictions_output(predictions, category)
        print("\n" + output)
        
        # Salvar predições
        filename = f"international_{mode}_predictions.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"\n✅ Predições salvas em: {filename}")
        except Exception as e:
            print(f"\n❌ Erro ao salvar predições: {e}")
        
        print(f"\n🎉 PREDIÇÕES {category} CONCLUÍDAS!")
        return True

def main():
    """Função principal"""
    predictor = InternationalCompetitionsSystem()
    
    print("🌍 SISTEMA DE COMPETIÇÕES INTERNACIONAIS - MARABET AI")
    print("=" * 80)
    print("Escolha o modo de predições:")
    print("1. Partidas de hoje")
    print("2. Partidas ao vivo")
    print("3. Partidas futuras")
    
    try:
        choice = input("\nDigite sua escolha (1-3): ").strip()
        
        if choice == "1":
            return predictor.run_international_predictions("today")
        elif choice == "2":
            return predictor.run_international_predictions("live")
        elif choice == "3":
            return predictor.run_international_predictions("future")
        else:
            print("❌ Escolha inválida")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Operação cancelada pelo usuário")
        return False

if __name__ == "__main__":
    main()
