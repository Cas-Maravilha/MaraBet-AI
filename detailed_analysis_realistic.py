#!/usr/bin/env python3
"""
Sistema de Predições Detalhadas com Análise de Valor Esperado - Versão Realista
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
        self.minimum_value_threshold = 0.02  # 2% de valor mínimo (mais realista)
        self.high_confidence_threshold = 0.70  # 70% de confiança alta
        self.medium_confidence_threshold = 0.55  # 55% de confiança média
        
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
                'over_0_5': 1.12, 'over_1_5': 1.28, 'over_2_5': 1.75, 'over_3_5': 2.25,
                'under_0_5': 6.00, 'under_1_5': 3.50, 'under_2_5': 2.10, 'under_3_5': 1.65,
                'btts_yes': 1.80, 'btts_no': 2.00, 'exact_0': 9.50, 'exact_1': 4.50,
                'exact_2': 3.60, 'exact_3': 5.20, 'exact_4': 9.00, 'exact_5': 18.00
            },
            'handicap': {
                'asian_handicap_home': 1.95, 'asian_handicap_away': 1.95,
                'european_handicap_home': 1.90, 'european_handicap_away': 2.00,
                'handicap_home_-1': 2.40, 'handicap_home_-2': 3.80,
                'handicap_away_+1': 1.80, 'handicap_away_+2': 1.40
            },
            'cards': {
                'cards_over_1_5': 1.20, 'cards_over_2_5': 1.50, 'cards_over_3_5': 1.95,
                'cards_over_4_5': 2.60, 'cards_over_5_5': 3.80, 'cards_over_6_5': 5.50,
                'yellow_cards_over_1_5': 1.25, 'yellow_cards_over_2_5': 1.65,
                'yellow_cards_over_3_5': 2.20, 'yellow_cards_over_4_5': 3.20,
                'red_cards_yes': 5.00, 'red_cards_no': 1.15
            },
            'corners': {
                'corners_over_8_5': 1.35, 'corners_over_9_5': 1.55, 'corners_over_10_5': 1.85,
                'corners_over_11_5': 2.20, 'corners_over_12_5': 2.70, 'corners_over_13_5': 3.30,
                'corners_first_home': 1.95, 'corners_first_away': 1.95,
                'corners_handicap_home': 1.90, 'corners_handicap_away': 2.00
            },
            'double_chance': {
                'double_chance_1x': 1.30, 'double_chance_x2': 1.35, 'double_chance_12': 1.20,
                'triple_chance_1x2': 1.10, 'win_draw_win_1': 1.90, 'win_draw_win_x': 3.50,
                'win_draw_win_2': 2.30
            },
            'exact_score': {
                'exact_score_1_0': 8.50, 'exact_score_2_0': 13.00, 'exact_score_2_1': 9.50,
                'exact_score_3_0': 28.00, 'exact_score_3_1': 20.00, 'exact_score_3_2': 25.00,
                'exact_score_0_0': 9.50, 'exact_score_1_1': 7.00, 'exact_score_2_2': 13.00,
                'exact_score_3_3': 40.00, 'exact_score_0_1': 8.50, 'exact_score_0_2': 13.00,
                'exact_score_1_2': 9.50, 'exact_score_0_3': 28.00, 'exact_score_1_3': 20.00,
                'exact_score_2_3': 25.00
            },
            'match_winner': {
                'match_winner_1': 1.90, 'match_winner_x': 3.50, 'match_winner_2': 2.30,
                'half_time_winner_1': 2.60, 'half_time_winner_x': 2.20, 'half_time_winner_2': 3.40
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
        
        # Determinar se é favorável (threshold mais baixo)
        is_favorable = expected_value >= self.minimum_value_threshold
        
        # Calcular chances de green com margem de erro realista
        min_green_chance = max(0, probability - 0.15)  # Margem de erro 15%
        max_green_chance = min(1, probability + 0.10)  # Margem positiva 10%
        
        # Recomendação de stake baseada no Kelly
        if kelly_percentage > 0.05:  # 5% máximo
            recommended_stake = min(0.05, kelly_percentage)
        elif kelly_percentage > 0.02:  # 2% moderado
            recommended_stake = kelly_percentage
        else:
            recommended_stake = 0.01  # 1% conservador
        
        # Calcular ROI potencial
        roi_potential = expected_value * 100
        
        # Determinar nível de recomendação
        if expected_value > 0.10:  # 10%+ EV
            recommendation_level = "EXCELENTE"
            recommendation_emoji = "⭐"
        elif expected_value > 0.05:  # 5%+ EV
            recommendation_level = "MUITO BOA"
            recommendation_emoji = "🔥"
        elif expected_value > 0.02:  # 2%+ EV
            recommendation_level = "BOA"
            recommendation_emoji = "✅"
        else:
            recommendation_level = "NEUTRA"
            recommendation_emoji = "⚪"
        
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
            'roi_potential': roi_potential,
            'recommendation_level': recommendation_level,
            'recommendation_emoji': recommendation_emoji
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
    
    def get_top_recommendations(self, detailed_analysis: Dict, limit: int = 15) -> List[Dict]:
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
        if top_recommendations:
            message += f"🏆 *TOP {len(top_recommendations)} RECOMENDAÇÕES:*\n\n"
            
            for i, rec in enumerate(top_recommendations, 1):
                analysis = rec['analysis']
                message += f"{i}. {analysis['recommendation_emoji']} *{rec['bet_type']}*\n"
                message += f"   📊 Probabilidade: {analysis['probability']:.1%}\n"
                message += f"   💰 Odds: {analysis['odds']:.2f}\n"
                message += f"   📈 Valor Esperado: {analysis['expected_value']:+.1%}\n"
                message += f"   🎯 ROI Potencial: {analysis['roi_potential']:+.1f}%\n"
                message += f"   💵 Stake Recomendado: {analysis['recommended_stake']:.1%}\n"
                message += f"   🟢 Chance Green: {analysis['min_green_chance']:.1%} - {analysis['max_green_chance']:.1%}\n"
                message += f"   📋 Confiança: {analysis['confidence_level']}\n"
                message += f"   ⭐ Nível: {analysis['recommendation_level']}\n\n"
        else:
            message += f"⚠️ *NENHUMA RECOMENDAÇÃO FAVORÁVEL ENCONTRADA*\n"
            message += f"Threshold atual: {self.minimum_value_threshold:.1%} EV\n\n"
        
        # Análise por categoria
        message += f"📊 *ANÁLISE POR CATEGORIA:*\n\n"
        
        for category, preds in detailed_analysis.items():
            favorable_count = sum(1 for analysis in preds.values() if analysis['is_favorable'])
            total_count = len(preds)
            
            if favorable_count > 0:
                message += f"*{category.upper()}:*\n"
                message += f"✅ {favorable_count}/{total_count} apostas favoráveis\n"
                
                # Mostrar melhores da categoria
                category_best = sorted(preds.items(), key=lambda x: x[1]['expected_value'], reverse=True)[:3]
                for bet_type, analysis in category_best:
                    if analysis['is_favorable']:
                        message += f"   {analysis['recommendation_emoji']} {bet_type}: {analysis['expected_value']:+.1%} EV\n"
                message += "\n"
        
        # Resumo estatístico
        all_analyses = []
        for preds in detailed_analysis.values():
            all_analyses.extend(preds.values())
        
        if all_analyses:
            avg_ev = sum(a['expected_value'] for a in all_analyses) / len(all_analyses)
            max_ev = max(a['expected_value'] for a in all_analyses)
            favorable_total = sum(1 for a in all_analyses if a['is_favorable'])
            
            message += f"📈 *RESUMO ESTATÍSTICO:*\n"
            message += f"• Valor Esperado Médio: {avg_ev:+.1%}\n"
            message += f"• Melhor Valor Esperado: {max_ev:+.1%}\n"
            message += f"• Apostas Favoráveis: {favorable_total}/{len(all_analyses)}\n"
            message += f"• Taxa de Sucesso: {favorable_total/len(all_analyses):.1%}\n\n"
        
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
