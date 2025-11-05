#!/usr/bin/env python3
"""
Demonstração do Sistema de Competições Internacionais
MaraBet AI - Demo do sistema com cobertura completa de competições internacionais
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InternationalCompetitionsDemo:
    """Demo do sistema de competições internacionais"""
    
    def __init__(self):
        # Competições internacionais completas
        self.international_competitions = [
            # COMPETIÇÕES EUROPEIAS
            {'name': 'Champions League', 'country': 'Europe', 'priority': 1, 'type': 'Club', 'tier': 'Tier 1'},
            {'name': 'Europa League', 'country': 'Europe', 'priority': 1, 'type': 'Club', 'tier': 'Tier 1'},
            {'name': 'Conference League', 'country': 'Europe', 'priority': 1, 'type': 'Club', 'tier': 'Tier 1'},
            {'name': 'Super Cup', 'country': 'Europe', 'priority': 1, 'type': 'Club', 'tier': 'Tier 1'},
            
            # COMPETIÇÕES INTERNACIONAIS
            {'name': 'World Cup', 'country': 'World', 'priority': 1, 'type': 'National', 'tier': 'Tier 1'},
            {'name': 'Copa America', 'country': 'South America', 'priority': 1, 'type': 'National', 'tier': 'Tier 1'},
            {'name': 'African Cup', 'country': 'Africa', 'priority': 1, 'type': 'National', 'tier': 'Tier 1'},
            {'name': 'Euro Championship', 'country': 'Europe', 'priority': 1, 'type': 'National', 'tier': 'Tier 1'},
            {'name': 'Nations League', 'country': 'Europe', 'priority': 2, 'type': 'National', 'tier': 'Tier 2'},
            
            # OUTRAS COMPETIÇÕES IMPORTANTES
            {'name': 'Gold Cup', 'country': 'North America', 'priority': 2, 'type': 'National', 'tier': 'Tier 2'},
            {'name': 'Asian Cup', 'country': 'Asia', 'priority': 2, 'type': 'National', 'tier': 'Tier 2'},
            {'name': 'Oceania Cup', 'country': 'Oceania', 'priority': 3, 'type': 'National', 'tier': 'Tier 3'},
            
            # LIGAS NACIONAIS PRINCIPAIS
            {'name': 'Premier League', 'country': 'England', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            {'name': 'La Liga', 'country': 'Spain', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            {'name': 'Bundesliga', 'country': 'Germany', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            {'name': 'Serie A', 'country': 'Italy', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            {'name': 'Ligue 1', 'country': 'France', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            {'name': 'Serie A', 'country': 'Brazil', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
            {'name': 'Primera División', 'country': 'Argentina', 'priority': 1, 'type': 'League', 'tier': 'Tier 1'},
        ]
        
        # Times famosos por competição
        self.teams_by_competition = {
            'Champions League': ['Real Madrid', 'Barcelona', 'Bayern Munich', 'Manchester City', 'Liverpool', 'PSG', 'Chelsea', 'Arsenal'],
            'Europa League': ['Sevilla', 'Roma', 'Atalanta', 'Villarreal', 'West Ham', 'Leverkusen', 'Brighton', 'Milan'],
            'Conference League': ['Fiorentina', 'West Ham', 'Roma', 'Villarreal', 'AZ Alkmaar', 'Fiorentina', 'Basel', 'Anderlecht'],
            'World Cup': ['Brasil', 'Argentina', 'França', 'Alemanha', 'Espanha', 'Inglaterra', 'Holanda', 'Portugal'],
            'Copa America': ['Brasil', 'Argentina', 'Uruguai', 'Chile', 'Colômbia', 'Peru', 'Equador', 'Paraguai'],
            'African Cup': ['Egito', 'Senegal', 'Nigéria', 'Marrocos', 'Costa do Marfim', 'Gana', 'Camarões', 'Tunísia'],
            'Euro Championship': ['França', 'Alemanha', 'Espanha', 'Inglaterra', 'Itália', 'Holanda', 'Portugal', 'Bélgica'],
            'Premier League': ['Manchester City', 'Arsenal', 'Liverpool', 'Chelsea', 'Manchester United', 'Tottenham', 'Newcastle', 'Brighton'],
            'La Liga': ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Real Sociedad', 'Villarreal', 'Real Betis', 'Sevilla', 'Valencia'],
            'Bundesliga': ['Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Bayer Leverkusen', 'Eintracht Frankfurt', 'Wolfsburg', 'Freiburg', 'Union Berlin'],
            'Serie A': ['Inter Milan', 'AC Milan', 'Juventus', 'Napoli', 'Atalanta', 'Roma', 'Lazio', 'Fiorentina'],
            'Ligue 1': ['PSG', 'Monaco', 'Lyon', 'Marseille', 'Lille', 'Rennes', 'Nice', 'Lens'],
            'Serie A': ['Flamengo', 'Palmeiras', 'São Paulo', 'Santos', 'Corinthians', 'Internacional', 'Grêmio', 'Atlético-MG'],
            'Primera División': ['Boca Juniors', 'River Plate', 'Racing', 'San Lorenzo', 'Independiente', 'Estudiantes', 'Huracán', 'Vélez'],
        }
        
        # Status de partidas
        self.match_statuses = {
            'NS': 'Não Iniciada',
            '1H': '1º Tempo',
            '2H': '2º Tempo', 
            'HT': 'Intervalo',
            'LIVE': 'Ao Vivo',
            'FT': 'Finalizada'
        }
    
    def generate_international_matches(self, num_matches=20):
        """Gera partidas internacionais simuladas"""
        logger.info(f"🌍 GERANDO {num_matches} PARTIDAS INTERNACIONAIS SIMULADAS")
        
        matches = []
        for i in range(num_matches):
            # Selecionar competição aleatória
            competition = np.random.choice(self.international_competitions)
            comp_name = competition['name']
            country = competition['country']
            priority = competition['priority']
            comp_type = competition['type']
            tier = competition['tier']
            
            # Selecionar times da competição
            teams = self.teams_by_competition.get(comp_name, ['Team A', 'Team B'])
            home_team = np.random.choice(teams)
            away_team = np.random.choice([t for t in teams if t != home_team])
            
            # Horários diferentes
            hours = [14, 16, 18, 20, 22]  # 14h, 16h, 18h, 20h, 22h
            match_time = datetime.now().replace(hour=hours[i % len(hours)], minute=0, second=0, microsecond=0)
            
            # Status da partida (priorizar ao vivo e futuras)
            if i < 4:  # Primeiras 4 partidas ao vivo
                status = 'LIVE'
            elif i < 8:  # Próximas 4 partidas em andamento
                status = np.random.choice(['1H', '2H', 'HT'])
            elif i < 12:  # Próximas 4 partidas não iniciadas
                status = 'NS'
            else:  # Resto finalizadas
                status = 'FT'
            
            match = {
                'fixture': {
                    'id': 6000 + i,
                    'date': match_time.isoformat(),
                    'status': {
                        'short': status
                    }
                },
                'teams': {
                    'home': {
                        'id': 100 + i,
                        'name': home_team
                    },
                    'away': {
                        'id': 200 + i,
                        'name': away_team
                    }
                },
                'goals': {
                    'home': np.random.randint(0, 4) if status in ['1H', '2H', 'HT', 'LIVE', 'FT'] else None,
                    'away': np.random.randint(0, 4) if status in ['1H', '2H', 'HT', 'LIVE', 'FT'] else None
                },
                'league': {
                    'id': 100 + i,
                    'name': comp_name,
                    'season': 2024
                },
                'competition_info': {
                    'name': comp_name,
                    'country': country,
                    'priority': priority,
                    'type': comp_type,
                    'tier': tier
                }
            }
            matches.append(match)
        
        logger.info(f"   {len(matches)} partidas internacionais simuladas geradas")
        return matches
    
    def get_team_form_simulated(self, team_name, last_matches=10):
        """Simula forma recente de um time"""
        np.random.seed(hash(team_name) % 2**32)
        
        matches = []
        for i in range(last_matches):
            home_score = np.random.poisson(1.5)
            away_score = np.random.poisson(1.2)
            
            match = {
                'goals': {
                    'home': home_score,
                    'away': away_score
                }
            }
            matches.append(match)
        
        return matches
    
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
            home_score = match['goals']['home']
            away_score = match['goals']['away']
            
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
        match_time = datetime.fromisoformat(match['fixture']['date'])
        status = match['fixture']['status']['short']
        comp_info = match.get('competition_info', {})
        
        logger.info(f"🔮 PREDIZENDO: {home_team} vs {away_team} ({comp_info.get('name', 'Unknown')}) - {match_time.strftime('%H:%M')}")
        
        # Obter forma recente dos times
        home_form = self.get_team_form_simulated(home_team, 10)
        away_form = self.get_team_form_simulated(away_team, 10)
        
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
            'date_formatted': match_time.strftime('%d/%m %H:%M'),
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
        output += f"🤖 Sistema de IA com dados simulados para demonstração\n"
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
        
        output += f"\n⏰ IMPORTANTE: Predições baseadas em dados simulados\n"
        output += f"🌐 COBERTURA: Competições internacionais completas\n"
        output += f"🏆 INCLUI: Champions League, Europa League, Copa do Mundo, Copa América, CAN, Euro\n"
        output += f"📊 DADOS: Simulados para demonstração do conceito\n"
        output += f"⚠️ AVISO: Apostas envolvem risco. Use com responsabilidade.\n"
        output += f"🤖 Powered by MaraBet AI - Sistema de IA para Futebol"
        
        return output
    
    def run_demo(self):
        """Executa demonstração do sistema internacional"""
        print("🌍 DEMONSTRAÇÃO DO SISTEMA DE COMPETIÇÕES INTERNACIONAIS - MARABET AI")
        print("=" * 80)
        
        # 1. Gerar partidas internacionais
        international_matches = self.generate_international_matches(20)
        
        print(f"📊 {len(international_matches)} partidas internacionais simuladas geradas")
        
        # 2. Mostrar distribuição por tipo de competição
        type_counts = {}
        for match in international_matches:
            comp_type = match['competition_info']['type']
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
        
        print("\n📊 DISTRIBUIÇÃO POR TIPO DE COMPETIÇÃO:")
        for comp_type, count in type_counts.items():
            type_name = {'Club': 'Competições de Clubes', 'National': 'Competições Nacionais', 'League': 'Ligas Nacionais'}.get(comp_type, comp_type)
            print(f"   {type_name}: {count} partidas")
        
        # 3. Mostrar distribuição por status
        status_counts = {}
        for match in international_matches:
            status = match['fixture']['status']['short']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("\n📊 DISTRIBUIÇÃO POR STATUS:")
        for status, count in status_counts.items():
            status_name = self.match_statuses.get(status, status)
            print(f"   {status_name}: {count} partidas")
        
        # 4. Gerar predições
        predictions = []
        for match in international_matches:
            try:
                prediction = self.predict_match(match)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"   Erro ao predizer partida: {e}")
                continue
        
        if not predictions:
            print("❌ Nenhuma predição gerada")
            return False
        
        print(f"🔮 {len(predictions)} predições internacionais geradas")
        
        # 5. Mostrar predições
        output = self.format_international_predictions_output(predictions, "INTERNACIONAIS")
        print("\n" + output)
        
        # 6. Salvar predições
        try:
            with open('international_competitions_demo.txt', 'w', encoding='utf-8') as f:
                f.write(output)
            print("\n✅ Predições salvas em: international_competitions_demo.txt")
        except Exception as e:
            print(f"\n❌ Erro ao salvar predições: {e}")
        
        # 7. Mostrar características do sistema
        print("\n🌍 CARACTERÍSTICAS DO SISTEMA INTERNACIONAL:")
        print("=" * 60)
        
        features = [
            "✅ Cobertura completa de competições internacionais",
            "✅ COMPETIÇÕES EUROPEIAS: Champions League, Europa League, Conference League",
            "✅ COMPETIÇÕES INTERNACIONAIS: Copa do Mundo, Copa América, CAN, Euro",
            "✅ LIGAS NACIONAIS: Premier League, La Liga, Bundesliga, Serie A, Ligue 1",
            "✅ Predições para partidas ao vivo e futuras",
            "✅ Análise de forma dos times",
            "✅ Fator casa ajustado por tipo de competição",
            "✅ Cálculo de probabilidades e odds",
            "✅ Identificação de valor nas apostas",
            "✅ Status das partidas em tempo real",
            "✅ Sistema robusto e escalável",
            "✅ Foco em partidas futuras e ao vivo",
            "✅ Cobertura global não limitada ao Brasil"
        ]
        
        for feature in features:
            print(f"   {feature}")
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        return True

def main():
    """Função principal"""
    demo = InternationalCompetitionsDemo()
    return demo.run_demo()

if __name__ == "__main__":
    main()
