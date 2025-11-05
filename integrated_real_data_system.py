#!/usr/bin/env python3
"""
Sistema Integrado MaraBet AI com Dados Reais
Combina dados reais da Football API com sistema de predições
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Importar módulos do sistema
from robust_real_data_collector import RobustRealDataCollector
from enhanced_predictions_system import EnhancedPredictionsSystem
from concise_alerts import ConciseAlertSystem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegratedRealDataSystem:
    """Sistema integrado com dados reais"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.data_collector = RobustRealDataCollector(api_key)
        self.prediction_system = EnhancedPredictionsSystem()
        self.alert_system = ConciseAlertSystem()
        
    def collect_and_analyze_real_matches(self):
        """Coleta dados reais e gera análises"""
        logger.info("🚀 Iniciando coleta e análise de dados reais...")
        
        # Coletar dados reais
        real_data = self.data_collector.collect_comprehensive_data()
        
        # Processar partidas de hoje
        today_matches = real_data.get('today_matches', [])
        analyzed_matches = []
        
        logger.info(f"📊 Analisando {len(today_matches)} partidas de hoje...")
        
        for match in today_matches[:10]:  # Analisar apenas as primeiras 10
            try:
                # Extrair dados da partida
                match_data = self.extract_match_data(match)
                
                # Gerar predições
                predictions = self.prediction_system.generate_predictions(match_data)
                
                # Salvar predições
                filename = self.prediction_system.save_predictions_to_file(
                    match_data, predictions, f"real_match_{match['fixture']['id']}_predictions.json"
                )
                
                analyzed_matches.append({
                    'match_data': match_data,
                    'predictions': predictions,
                    'filename': filename
                })
                
                logger.info(f"✅ Partida analisada: {match_data['home_team']} vs {match_data['away_team']}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao analisar partida: {e}")
        
        return analyzed_matches
    
    def extract_match_data(self, match: Dict) -> Dict:
        """Extrai dados da partida para análise"""
        try:
            teams = match['teams']
            league = match['league']
            fixture = match['fixture']
            
            # Obter classificação da liga se disponível
            league_standings = self.get_league_standings_for_teams(league['id'])
            
            # Calcular força das equipes baseada na classificação
            home_strength = self.calculate_team_strength(teams['home']['id'], league_standings)
            away_strength = self.calculate_team_strength(teams['away']['id'], league_standings)
            
            match_data = {
                'home_team': teams['home']['name'],
                'away_team': teams['away']['name'],
                'league': league['name'],
                'country': league.get('country', 'Unknown'),
                'season': league.get('season', 2024),
                'round': league.get('round', 'Regular Season'),
                'date': fixture['date'],
                'venue': fixture.get('venue', {}).get('name', 'Unknown'),
                'referee': fixture.get('referee', 'Unknown'),
                'home_team_strength': home_strength,
                'away_team_strength': away_strength,
                'match_intensity': self.calculate_match_intensity(league['name']),
                'referee_strictness': self.calculate_referee_strictness(fixture.get('referee', 'Unknown')),
                'home_attack_style': self.calculate_attack_style(teams['home']['name']),
                'away_attack_style': self.calculate_attack_style(teams['away']['name']),
                'weather_condition': 'Unknown',  # Seria obtido de API meteorológica
                'importance': self.calculate_match_importance(league['name'], teams['home']['name'], teams['away']['name'])
            }
            
            return match_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados da partida: {e}")
            return {}
    
    def get_league_standings_for_teams(self, league_id: int) -> List[Dict]:
        """Obtém classificação da liga para calcular força das equipes"""
        try:
            params = {
                'league': league_id,
                'season': 2024
            }
            
            data = self.data_collector.make_request('standings', params)
            if data:
                standings = data.get('response', [])
                if standings and len(standings) > 0:
                    league_data = standings[0].get('league', {})
                    standings_data = league_data.get('standings', [])
                    if standings_data and len(standings_data) > 0:
                        return standings_data[0]
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter classificação: {e}")
            return []
    
    def calculate_team_strength(self, team_id: int, standings: List[Dict]) -> float:
        """Calcula força da equipe baseada na classificação"""
        try:
            if not standings:
                return 0.5  # Força média se não houver classificação
            
            for team in standings:
                if team['team']['id'] == team_id:
                    position = team['rank']
                    total_teams = len(standings)
                    
                    # Calcular força baseada na posição (1 = mais forte, último = mais fraco)
                    strength = 1.0 - (position - 1) / (total_teams - 1)
                    return max(0.1, min(1.0, strength))  # Limitar entre 0.1 e 1.0
            
            return 0.5  # Força média se equipe não encontrada
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular força da equipe: {e}")
            return 0.5
    
    def calculate_match_intensity(self, league_name: str) -> float:
        """Calcula intensidade da partida baseada na liga"""
        high_intensity_leagues = ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']
        
        if league_name in high_intensity_leagues:
            return 0.8
        elif 'Champions League' in league_name or 'Europa League' in league_name:
            return 0.9
        else:
            return 0.6
    
    def calculate_referee_strictness(self, referee: str) -> float:
        """Calcula rigor do árbitro"""
        # Simulação baseada no nome do árbitro
        if referee == 'Unknown':
            return 0.5
        
        # Simulação simples baseada no nome
        strict_referees = ['Taylor', 'Oliver', 'Atkinson']
        lenient_referees = ['Friend', 'Moss', 'Pawson']
        
        if any(name in referee for name in strict_referees):
            return 0.8
        elif any(name in referee for name in lenient_referees):
            return 0.3
        else:
            return 0.5
    
    def calculate_attack_style(self, team_name: str) -> float:
        """Calcula estilo ofensivo da equipe"""
        # Simulação baseada no nome da equipe
        attacking_teams = ['Barcelona', 'Manchester City', 'Bayern', 'Real Madrid', 'Arsenal']
        defensive_teams = ['Atletico Madrid', 'Chelsea', 'Juventus', 'Inter']
        
        if any(name in team_name for name in attacking_teams):
            return 0.8
        elif any(name in team_name for name in defensive_teams):
            return 0.3
        else:
            return 0.5
    
    def calculate_match_importance(self, league: str, home_team: str, away_team: str) -> str:
        """Calcula importância da partida"""
        big_matches = [
            ('Real Madrid', 'Barcelona'),
            ('Manchester United', 'Manchester City'),
            ('Arsenal', 'Chelsea'),
            ('Liverpool', 'Manchester City'),
            ('Juventus', 'AC Milan'),
            ('Bayern', 'Borussia Dortmund')
        ]
        
        match_pair = (home_team, away_team)
        reverse_pair = (away_team, home_team)
        
        if match_pair in big_matches or reverse_pair in big_matches:
            return 'high'
        elif league in ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']:
            return 'medium'
        else:
            return 'low'
    
    def send_real_data_alerts(self, analyzed_matches: List[Dict]):
        """Envia alertas baseados em dados reais"""
        logger.info("🚨 Enviando alertas baseados em dados reais...")
        
        for match_info in analyzed_matches:
            try:
                match_data = match_info['match_data']
                predictions = match_info['predictions']
                
                # Verificar se há predições de alta confiança
                has_high_confidence = False
                for category, pred_list in predictions.items():
                    if isinstance(pred_list, list):
                        for prediction in pred_list:
                            if prediction.get('predicted_probability', 0) >= 0.80:
                                has_high_confidence = True
                                break
                    if has_high_confidence:
                        break
                
                if has_high_confidence:
                    # Enviar análise concisa
                    self.alert_system.send_concise_analysis(match_data)
                    logger.info(f"✅ Alerta enviado para: {match_data['home_team']} vs {match_data['away_team']}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao enviar alerta: {e}")
    
    def run_complete_real_data_analysis(self):
        """Executa análise completa com dados reais"""
        print("🎯 MARABET AI - ANÁLISE COMPLETA COM DADOS REAIS")
        print("=" * 60)
        
        try:
            # Coletar e analisar partidas reais
            analyzed_matches = self.collect_and_analyze_real_matches()
            
            # Enviar alertas
            self.send_real_data_alerts(analyzed_matches)
            
            # Resumo final
            print(f"\n✅ ANÁLISE COMPLETA CONCLUÍDA!")
            print(f"📊 Partidas analisadas: {len(analyzed_matches)}")
            print(f"🚨 Alertas enviados: {len(analyzed_matches)}")
            print("🎯 Sistema integrado com dados reais da Football API!")
            
        except Exception as e:
            logger.error(f"❌ Erro na análise completa: {e}")
            print(f"❌ Erro: {e}")

def main():
    # Chave da API fornecida pelo usuário
    API_KEY = "71b2b62386f2d1275cd3201a73e1e045"
    
    print("🎯 MARABET AI - SISTEMA INTEGRADO COM DADOS REAIS")
    print("=" * 60)
    
    # Inicializar sistema integrado
    system = IntegratedRealDataSystem(API_KEY)
    
    print(f"🔑 API Key configurada: {API_KEY[:10]}...")
    print("📊 Iniciando análise completa com dados reais...")
    
    # Executar análise completa
    system.run_complete_real_data_analysis()

if __name__ == "__main__":
    main()
