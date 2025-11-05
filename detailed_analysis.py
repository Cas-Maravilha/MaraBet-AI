#!/usr/bin/env python3
"""
Sistema de Predições Detalhadas com Análise de Valor Esperado
Inclui mercados favoráveis, valor esperado, chances mínimas/máximas
"""

import json
import os
import math
from datetime import datetime
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DetailedPredictionAnalyzer:
    def __init__(self):
        self.minimum_value_threshold = 0.05  # 5% de valor mínimo
        self.high_confidence_threshold = 0.75  # 75% de confiança alta
        self.medium_confidence_threshold = 0.60  # 60% de confiança média
        
    def calculate_expected_value(self, probability: float, odds: float) -> float:
        """Calcula o valor esperado de uma aposta"""
        if odds <= 0:
            return 0
        return (probability * odds) - 1
    
    def calculate_kelly_criterion(self, probability: float, odds: float) -> float:
        """Calcula o critério de Kelly para gestão de bankroll"""
        if odds <= 0:
            return 0
        return (probability * odds - 1) / (odds - 1)
    
    def get_market_odds(self, market_type: str, bet_type: str) -> float:
        """Simula odds do mercado (em produção viria de API real)"""
        odds_mapping = {
            'goals': {
                'over_0_5': 1.15, 'over_1_5': 1.35, 'over_2_5': 1.85, 'over_3_5': 2.40,
                'under_0_5': 5.50, 'under_1_5': 3.20, 'under_2_5': 1.95, 'under_3_5': 1.55,
                'btts_yes': 1.75, 'btts_no': 2.10, 'exact_0': 8.50, 'exact_1': 4.20,
                'exact_2': 3.40, 'exact_3': 4.80, 'exact_4': 8.20, 'exact_5': 15.00
            },
            'handicap': {
                'asian_handicap_home': 1.90, 'asian_handicap_away': 1.90,
                'european_handicap_home': 1.85, 'european_handicap_away': 1.95,
                'handicap_home_-1': 2.20, 'handicap_home_-2': 3.50,
                'handicap_away_+1': 1.70, 'handicap_away_+2': 1.35
            },
            'cards': {
                'cards_over_1_5': 1.25, 'cards_over_2_5': 1.60, 'cards_over_3_5': 2.10,
                'cards_over_4_5': 2.80, 'cards_over_5_5': 4.20, 'cards_over_6_5': 6.50,
                'yellow_cards_over_1_5': 1.30, 'yellow_cards_over_2_5': 1.75,
                'yellow_cards_over_3_5': 2.40, 'yellow_cards_over_4_5': 3.50,
                'red_cards_yes': 4.50, 'red_cards_no': 1.20
            },
            'corners': {
                'corners_over_8_5': 1.40, 'corners_over_9_5': 1.65, 'corners_over_10_5': 1.95,
                'corners_over_11_5': 2.30, 'corners_over_12_5': 2.80, 'corners_over_13_5': 3.50,
                'corners_first_home': 1.90, 'corners_first_away': 1.90,
                'corners_handicap_home': 1.85, 'corners_handicap_away': 1.95
            },
            'double_chance': {
                'double_chance_1x': 1.35, 'double_chance_x2': 1.40, 'double_chance_12': 1.25,
                'triple_chance_1x2': 1.15, 'win_draw_win_1': 1.85, 'win_draw_win_x': 3.40,
                'win_draw_win_2': 2.20
            },
            'exact_score': {
                'exact_score_1_0': 7.50, 'exact_score_2_0': 12.00, 'exact_score_2_1': 8.50,
                'exact_score_3_0': 25.00, 'exact_score_3_1': 18.00, 'exact_score_3_2': 22.00,
                'exact_score_0_0': 8.50, 'exact_score_1_1': 6.50, 'exact_score_2_2': 12.00,
                'exact_score_3_3': 35.00, 'exact_score_0_1': 7.50, 'exact_score_0_2': 12.00,
                'exact_score_1_2': 8.50, 'exact_score_0_3': 25.00, 'exact_score_1_3': 18.00,
                'exact_score_2_3': 22.00
            },
            'match_winner': {
                'match_winner_1': 1.85, 'match_winner_x': 3.40, 'match_winner_2': 2.20,
                'half_time_winner_1': 2.50, 'half_time_winner_x': 2.10, 'half_time_winner_2': 3.20
            }
        }
        
        return odds_mapping.get(market_type, {}).get(bet_type, 2.00)
    
    def analyze_prediction_detail(self, category: str, bet_type: str, probability: float) -> Dict:
        """Analisa uma predição em detalhes"""
        odds = self.get_market_odds(category, bet_type)
        expected_value = self.calculate_expected_value(probability, odds)
        kelly_percentage = self.calculate_kelly_criterion(probability, odds)
        
        # Determinar nível de confiança
        if probability >= self.high_confidence_threshold:
            confidence_level = "ALTA"
            confidence_emoji = "🟢"
        elif probability >= self.medium_confidence_threshold:
            confidence_level = "MÉDIA"
            confidence_emoji = "🟡"
        else:
            confidence_level = "BAIXA"
            confidence_emoji = "🔴"
        
        # Determinar se é favorável
        is_favorable = expected_value >= self.minimum_value_threshold
        
        # Calcular chances de green
        min_green_chance = max(0, probability - 0.1)  # Margem de erro
        max_green_chance = min(1, probability + 0.1)
        
        # Recomendação de stake baseada no Kelly
        if kelly_percentage > 0.05:  # 5% máximo
            recommended_stake = min(0.05, kelly_percentage)
        elif kelly_percentage > 0.02:  # 2% moderado
            recommended_stake = kelly_percentage
        else:
            recommended_stake = 0.01  # 1% conservador
        
        return {
            'bet_type': bet_type,
            'probability': probability,
            'odds': odds,
            'expected_value': expected_value,
            'kelly_percentage': kelly_percentage,
            'confidence_level': confidence_level,
            'confidence_emoji': confidence_emoji,
            'is_favorable': is_favorable,
            'min_green_chance': min_green_chance,
            'max_green_chance': max_green_chance,
            'recommended_stake': recommended_stake,
            'roi_potential': expected_value * 100
        }
    
    def analyze_all_predictions(self, predictions: Dict) -> Dict:
        """Analisa todas as predições com detalhes"""
        detailed_analysis = {}
        
        for category, preds in predictions.items():
            if isinstance(preds, dict):
                detailed_analysis[category] = {}
                
                for bet_type, probability in preds.items():
                    detailed_analysis[category][bet_type] = self.analyze_prediction_detail(
                        category, bet_type, probability
                    )
        
        return detailed_analysis
    
    def get_top_recommendations(self, detailed_analysis: Dict, limit: int = 10) -> List[Dict]:
        """Obtém as melhores recomendações baseadas no valor esperado"""
        all_predictions = []
        
        for category, preds in detailed_analysis.items():
            for bet_type, analysis in preds.items():
                if analysis['is_favorable']:
                    all_predictions.append({
                        'category': category,
                        'bet_type': bet_type,
                        'analysis': analysis
                    })
        
        # Ordenar por valor esperado
        all_predictions.sort(key=lambda x: x['analysis']['expected_value'], reverse=True)
        
        return all_predictions[:limit]
    
    def format_detailed_message(self, match_data: Dict, detailed_analysis: Dict, top_recommendations: List[Dict]) -> str:
        """Formata mensagem detalhada para Telegram"""
        match = f"{match_data.get('home_team', 'N/A')} vs {match_data.get('away_team', 'N/A')}"
        league = match_data.get('league', 'N/A')
        
        message = f"🎯 *ANÁLISE DETALHADA MARABET AI*\n\n"
        message += f"🏆 *{match}*\n"
        message += f"🏟️ {league}\n"
        message += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        
        # Top recomendações
        message += f"🏆 *TOP {len(top_recommendations)} RECOMENDAÇÕES:*\n\n"
        
        for i, rec in enumerate(top_recommendations, 1):
            analysis = rec['analysis']
            message += f"{i}. {analysis['confidence_emoji']} *{rec['bet_type']}*\n"
            message += f"   📊 Probabilidade: {analysis['probability']:.1%}\n"
            message += f"   💰 Odds: {analysis['odds']:.2f}\n"
            message += f"   📈 Valor Esperado: {analysis['expected_value']:+.1%}\n"
            message += f"   🎯 ROI Potencial: {analysis['roi_potential']:+.1f}%\n"
            message += f"   💵 Stake Recomendado: {analysis['recommended_stake']:.1%}\n"
            message += f"   🟢 Chance Green: {analysis['min_green_chance']:.1%} - {analysis['max_green_chance']:.1%}\n"
            message += f"   📋 Confiança: {analysis['confidence_level']}\n\n"
        
        # Análise por categoria
        message += f"📊 *ANÁLISE POR CATEGORIA:*\n\n"
        
        for category, preds in detailed_analysis.items():
            favorable_count = sum(1 for analysis in preds.values() if analysis['is_favorable'])
            total_count = len(preds)
            
            if favorable_count > 0:
                message += f"*{category.upper()}:*\n"
                message += f"✅ {favorable_count}/{total_count} apostas favoráveis\n"
                
                # Mostrar melhores da categoria
                category_best = sorted(preds.items(), key=lambda x: x[1]['expected_value'], reverse=True)[:2]
                for bet_type, analysis in category_best:
                    if analysis['is_favorable']:
                        message += f"   {analysis['confidence_emoji']} {bet_type}: {analysis['expected_value']:+.1%} EV\n"
                message += "\n"
        
        message += f"⚠️ *AVISOS IMPORTANTES:*\n"
        message += f"• Stake máximo recomendado: 5% do bankroll\n"
        message += f"• Valor mínimo esperado: {self.minimum_value_threshold:.1%}\n"
        message += f"• Gestão de risco é fundamental\n"
        message += f"• Nunca aposte mais do que pode perder\n\n"
        
        message += f"🤖 *Sistema MaraBet AI - Análise Profissional*"
        
        return message

def main():
    analyzer = DetailedPredictionAnalyzer()
    
    print("🎯 MARABET AI - ANÁLISE DETALHADA COM VALOR ESPERADO")
    print("=" * 60)
    
    # Carregar predições existentes
    prediction_files = [f for f in os.listdir('.') if 'predictions' in f and f.endswith('.json')]
    
    if not prediction_files:
        print("❌ Nenhum arquivo de predições encontrado!")
        return
    
    # Processar cada arquivo
    for filename in prediction_files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            match_data = data.get('match_data', {})
            predictions = data.get('predictions', {})
            
            print(f"\n📊 Processando: {match_data.get('home_team', 'N/A')} vs {match_data.get('away_team', 'N/A')}")
            
            # Análise detalhada
            detailed_analysis = analyzer.analyze_all_predictions(predictions)
            
            # Top recomendações
            top_recommendations = analyzer.get_top_recommendations(detailed_analysis)
            
            # Formatar mensagem
            detailed_message = analyzer.format_detailed_message(match_data, detailed_analysis, top_recommendations)
            
            # Salvar análise detalhada
            analysis_filename = f"detailed_analysis_{filename.replace('.json', '')}.txt"
            with open(analysis_filename, 'w', encoding='utf-8') as f:
                f.write(detailed_message)
            
            print(f"✅ Análise detalhada salva: {analysis_filename}")
            print(f"📈 {len(top_recommendations)} recomendações favoráveis encontradas")
            
        except Exception as e:
            print(f"❌ Erro ao processar {filename}: {e}")
    
    print(f"\n🎯 Análise detalhada concluída!")
    print(f"📊 Arquivos gerados com valor esperado, chances de green e recomendações de stake")

if __name__ == "__main__":
    main()
