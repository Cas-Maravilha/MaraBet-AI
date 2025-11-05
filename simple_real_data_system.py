#!/usr/bin/env python3
"""
Sistema Simplificado MaraBet AI com Dados Reais
Sistema funcional que integra dados reais da Football API
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

class SimpleRealDataSystem:
    """Sistema simplificado com dados reais"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        
    def make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Faz requisição para a API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results', 0) > 0:
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
    
    def get_league_standings(self, league_id: int, season: int = 2024) -> List[Dict]:
        """Obtém classificação da liga"""
        params = {
            'league': league_id,
            'season': season
        }
        
        data = self.make_request('standings', params)
        if data:
            standings = data.get('response', [])
            if standings and len(standings) > 0:
                league_data = standings[0].get('league', {})
                standings_data = league_data.get('standings', [])
                if standings_data and len(standings_data) > 0:
                    logger.info(f"✅ Classificação obtida para liga {league_id}")
                    return standings_data[0]
        return []
    
    def analyze_real_matches(self):
        """Analisa partidas reais"""
        logger.info("🚀 Iniciando análise de partidas reais...")
        
        # Coletar partidas de hoje
        today_matches = self.get_today_matches()
        
        if not today_matches:
            logger.warning("⚠️ Nenhuma partida encontrada para hoje")
            return []
        
        # Analisar as primeiras 10 partidas
        analyzed_matches = []
        for match in today_matches[:10]:
            try:
                analysis = self.analyze_single_match(match)
                if analysis:
                    analyzed_matches.append(analysis)
                    logger.info(f"✅ Partida analisada: {analysis['home_team']} vs {analysis['away_team']}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao analisar partida: {e}")
        
        return analyzed_matches
    
    def analyze_single_match(self, match: Dict) -> Optional[Dict]:
        """Analisa uma única partida"""
        try:
            teams = match['teams']
            league = match['league']
            fixture = match['fixture']
            
            # Obter classificação da liga
            standings = self.get_league_standings(league['id'])
            
            # Calcular força das equipes
            home_strength = self.calculate_team_strength(teams['home']['id'], standings)
            away_strength = self.calculate_team_strength(teams['away']['id'], standings)
            
            # Gerar predições simples
            predictions = self.generate_simple_predictions(home_strength, away_strength, league['name'])
            
            analysis = {
                'match_id': fixture['id'],
                'home_team': teams['home']['name'],
                'away_team': teams['away']['name'],
                'league': league['name'],
                'country': league.get('country', 'Unknown'),
                'date': fixture['date'],
                'venue': fixture.get('venue', {}).get('name', 'Unknown'),
                'home_strength': home_strength,
                'away_strength': away_strength,
                'predictions': predictions,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar partida individual: {e}")
            return None
    
    def calculate_team_strength(self, team_id: int, standings: List[Dict]) -> float:
        """Calcula força da equipe baseada na classificação"""
        try:
            if not standings:
                return 0.5  # Força média se não houver classificação
            
            for team in standings:
                if team['team']['id'] == team_id:
                    position = team['rank']
                    total_teams = len(standings)
                    
                    # Calcular força baseada na posição
                    strength = 1.0 - (position - 1) / (total_teams - 1)
                    return max(0.1, min(1.0, strength))
            
            return 0.5  # Força média se equipe não encontrada
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular força da equipe: {e}")
            return 0.5
    
    def generate_simple_predictions(self, home_strength: float, away_strength: float, league: str) -> Dict:
        """Gera predições simples baseadas na força das equipes"""
        try:
            # Calcular probabilidades básicas
            total_strength = home_strength + away_strength
            
            # Probabilidade de vitória em casa
            home_win_prob = home_strength / total_strength
            
            # Probabilidade de empate (baseada na diferença de força)
            strength_diff = abs(home_strength - away_strength)
            draw_prob = 0.3 - (strength_diff * 0.2)  # Menos empates quando há grande diferença
            
            # Probabilidade de vitória fora
            away_win_prob = 1.0 - home_win_prob - draw_prob
            
            # Ajustar probabilidades para somar 1.0
            total_prob = home_win_prob + draw_prob + away_win_prob
            home_win_prob /= total_prob
            draw_prob /= total_prob
            away_win_prob /= total_prob
            
            # Calcular probabilidade de Over 2.5 gols
            avg_strength = (home_strength + away_strength) / 2
            over_2_5_prob = 0.4 + (avg_strength * 0.4)  # Mais gols com equipes mais fortes
            
            # Calcular probabilidade de BTTS
            btts_prob = 0.5 + (avg_strength * 0.3)  # Mais BTTS com equipes mais fortes
            
            predictions = {
                'home_win_probability': round(home_win_prob, 3),
                'draw_probability': round(draw_prob, 3),
                'away_win_probability': round(away_win_prob, 3),
                'over_2_5_probability': round(over_2_5_prob, 3),
                'under_2_5_probability': round(1 - over_2_5_prob, 3),
                'btts_yes_probability': round(btts_prob, 3),
                'btts_no_probability': round(1 - btts_prob, 3),
                'confidence_level': self.calculate_confidence_level(home_strength, away_strength, league)
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar predições: {e}")
            return {}
    
    def calculate_confidence_level(self, home_strength: float, away_strength: float, league: str) -> str:
        """Calcula nível de confiança da análise"""
        try:
            strength_diff = abs(home_strength - away_strength)
            
            # Ligas principais têm maior confiança
            major_leagues = ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']
            league_confidence = 0.8 if league in major_leagues else 0.6
            
            # Maior diferença de força = maior confiança
            strength_confidence = 0.5 + (strength_diff * 0.5)
            
            # Confiança final
            final_confidence = (league_confidence + strength_confidence) / 2
            
            if final_confidence >= 0.8:
                return 'High'
            elif final_confidence >= 0.6:
                return 'Medium'
            else:
                return 'Low'
                
        except Exception as e:
            logger.error(f"❌ Erro ao calcular confiança: {e}")
            return 'Low'
    
    def save_analysis_to_file(self, analyses: List[Dict], filename: str = None):
        """Salva análises em arquivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"real_match_analysis_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analyses, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Análises salvas em {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Erro ao salvar arquivo: {e}")
            return None
    
    def print_analysis_summary(self, analyses: List[Dict]):
        """Imprime resumo das análises"""
        print("\n📊 RESUMO DAS ANÁLISES:")
        print("=" * 50)
        
        print(f"📅 Partidas analisadas: {len(analyses)}")
        
        if analyses:
            print("\n🏆 ANÁLISES DETALHADAS:")
            for i, analysis in enumerate(analyses, 1):
                print(f"\n{i}. {analysis['home_team']} vs {analysis['away_team']}")
                print(f"   🏟️ {analysis['league']} | 📅 {analysis['date'][:10]}")
                print(f"   💪 Força: Casa {analysis['home_strength']:.2f} | Visitante {analysis['away_strength']:.2f}")
                
                predictions = analysis['predictions']
                print(f"   🎯 Probabilidades:")
                print(f"      • Vitória Casa: {predictions['home_win_probability']:.1%}")
                print(f"      • Empate: {predictions['draw_probability']:.1%}")
                print(f"      • Vitória Visitante: {predictions['away_win_probability']:.1%}")
                print(f"      • Over 2.5: {predictions['over_2_5_probability']:.1%}")
                print(f"      • BTTS: {predictions['btts_yes_probability']:.1%}")
                print(f"   📊 Confiança: {predictions['confidence_level']}")

def main():
    # Chave da API fornecida pelo usuário
    API_KEY = "71b2b62386f2d1275cd3201a73e1e045"
    
    print("🎯 MARABET AI - SISTEMA SIMPLIFICADO COM DADOS REAIS")
    print("=" * 60)
    
    # Inicializar sistema
    system = SimpleRealDataSystem(API_KEY)
    
    print(f"🔑 API Key configurada: {API_KEY[:10]}...")
    print("📊 Iniciando análise com dados reais...")
    
    try:
        # Analisar partidas reais
        analyses = system.analyze_real_matches()
        
        if analyses:
            # Salvar análises
            filename = system.save_analysis_to_file(analyses)
            
            # Imprimir resumo
            system.print_analysis_summary(analyses)
            
            print(f"\n✅ ANÁLISE CONCLUÍDA!")
            if filename:
                print(f"📁 Arquivo salvo: {filename}")
            print("🎯 Sistema integrado com dados reais da Football API!")
        else:
            print("⚠️ Nenhuma partida foi analisada com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {e}")
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
