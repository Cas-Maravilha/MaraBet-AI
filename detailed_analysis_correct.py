#!/usr/bin/env python3
"""
Sistema de Predições Detalhadas com Análise de Valor Esperado - Formato Correto
Funciona com o formato real das predições (lista de objetos)
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
        self.minimum_value_threshold = 0.02  # 2% de valor mínimo
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
    
    def get_market_odds(self, market_type: str, selection: str) -> float:
        """Simula odds do mercado baseado no tipo e seleção"""
        odds_mapping = {
            'exact_goals': {
                '0': 8.50, '1': 4.20, '2': 3.40, '3': 4.80, '4': 8.20, '5+': 15.00
            },
            'both_teams_score': {
                'Sim': 1.80, 'Não': 2.00
            },
            'over_under_goals': {
                'Over 0.5': 1.12, 'Under 0.5': 6.00,
                'Over 1.5': 1.28, 'Under 1.5': 3.50,
                'Over 2.5': 1.75, 'Under 2.5': 2.10,
                'Over 3.5': 2.25, 'Under 3.5': 1.65,
                'Over 4.5': 3.50, 'Under 4.5': 1.30,
                'Over 5.5': 6.00, 'Under 5.5': 1.15
            },
            'asian_handicap': {
                'Casa -0.5': 1.95, 'Visitante +0.5': 1.95,
                'Casa -1': 2.20, 'Visitante +1': 1.70,
                'Casa -1.5': 2.40, 'Visitante +1.5': 1.60,
                'Casa -2': 3.20, 'Visitante +2': 1.40,
                'Casa -2.5': 4.00, 'Visitante +2.5': 1.25
            },
            'european_handicap': {
                'Casa -1': 1.90, 'Visitante +1': 2.00,
                'Casa -2': 2.60, 'Visitante +2': 1.50,
                'Casa -3': 3.50, 'Visitante +3': 1.30
            },
            'total_cards': {
                'Over 1.5': 1.20, 'Under 1.5': 4.50,
                'Over 2.5': 1.50, 'Under 2.5': 2.50,
                'Over 3.5': 1.95, 'Under 3.5': 1.85,
                'Over 4.5': 2.60, 'Under 4.5': 1.50,
                'Over 5.5': 3.80, 'Under 5.5': 1.25,
                'Over 6.5': 5.50, 'Under 6.5': 1.15
            },
            'yellow_cards': {
                'Over 1.5': 1.25, 'Under 1.5': 3.80,
                'Over 2.5': 1.65, 'Under 2.5': 2.20,
                'Over 3.5': 2.20, 'Under 3.5': 1.65,
                'Over 4.5': 3.20, 'Under 4.5': 1.35
            },
            'red_cards': {
                'Sim': 5.00, 'Não': 1.15
            },
            'total_corners': {
                'Over 8.5': 1.35, 'Under 8.5': 3.00,
                'Over 9.5': 1.55, 'Under 9.5': 2.40,
                'Over 10.5': 1.85, 'Under 10.5': 1.95,
                'Over 11.5': 2.20, 'Under 11.5': 1.65,
                'Over 12.5': 2.70, 'Under 12.5': 1.45,
                'Over 13.5': 3.30, 'Under 13.5': 1.30
            },
            'first_corner': {
                'Casa': 1.95, 'Visitante': 1.95
            },
            'corner_handicap': {
                'Casa -1': 1.90, 'Visitante +1': 2.00,
                'Casa -2': 2.40, 'Visitante +2': 1.60
            },
            'double_chance': {
                '1X': 1.30, 'X2': 1.35, '12': 1.20
            },
            'match_winner': {
                '1': 1.90, 'X': 3.50, '2': 2.30
            },
            'half_time_result': {
                '1': 2.60, 'X': 2.20, '2': 3.40
            },
            'exact_score': {
                '1-0': 8.50, '2-0': 13.00, '2-1': 9.50,
                '3-0': 28.00, '3-1': 20.00, '3-2': 25.00,
                '0-0': 9.50, '1-1': 7.00, '2-2': 13.00,
                '3-3': 40.00, '0-1': 8.50, '0-2': 13.00,
                '1-2': 9.50, '0-3': 28.00, '1-3': 20.00,
                '2-3': 25.00
            }
        }
        
        return odds_mapping.get(market_type, {}).get(selection, 2.00)
    
    def analyze_prediction_detail(self, prediction: Dict) -> Dict:
        """Analisa uma predição em detalhes"""
        market_type = prediction.get('market_type', '')
        selection = prediction.get('selection', '')
        probability = prediction.get('predicted_probability', 0.0)
        confidence = prediction.get('confidence', 0.0)
        
        odds = self.get_market_odds(market_type, selection)
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
            'market_type': market_type,
            'selection': selection,
            'probability': probability,
            'confidence': confidence,
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
            'recommendation_emoji': recommendation_emoji,
            'reasoning': prediction.get('reasoning', 'Análise baseada em dados históricos')
        }
    
    def analyze_all_predictions(self, predictions: List[Dict]) -> List[Dict]:
        """Analisa todas as predições com detalhes"""
        detailed_analyses = []
        
        for prediction in predictions:
            detailed_analysis = self.analyze_prediction_detail(prediction)
            detailed_analyses.append(detailed_analysis)
        
        return detailed_analyses
    
    def get_top_recommendations(self, detailed_analyses: List[Dict], limit: int = 15) -> List[Dict]:
        """Obtém as melhores recomendações baseadas no valor esperado"""
        favorable_predictions = [analysis for analysis in detailed_analyses if analysis['is_favorable']]
        
        # Ordenar por valor esperado
        favorable_predictions.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return favorable_predictions[:limit]
    
    def format_detailed_message(self, match_data: Dict, detailed_analyses: List[Dict], top_recommendations: List[Dict]) -> str:
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
            
            for i, analysis in enumerate(top_recommendations, 1):
                message += f"{i}. {analysis['recommendation_emoji']} *{analysis['selection']}* ({analysis['market_type']})\n"
                message += f"   📊 Probabilidade: {analysis['probability']:.1%}\n"
                message += f"   💰 Odds: {analysis['odds']:.2f}\n"
                message += f"   📈 Valor Esperado: {analysis['expected_value']:+.1%}\n"
                message += f"   🎯 ROI Potencial: {analysis['roi_potential']:+.1f}%\n"
                message += f"   💵 Stake Recomendado: {analysis['recommended_stake']:.1%}\n"
                message += f"   🟢 Chance Green: {analysis['min_green_chance']:.1%} - {analysis['max_green_chance']:.1%}\n"
                message += f"   📋 Confiança: {analysis['confidence_level']}\n"
                message += f"   ⭐ Nível: {analysis['recommendation_level']}\n"
                message += f"   💡 {analysis['reasoning']}\n\n"
        else:
            message += f"⚠️ *NENHUMA RECOMENDAÇÃO FAVORÁVEL ENCONTRADA*\n"
            message += f"Threshold atual: {self.minimum_value_threshold:.1%} EV\n\n"
        
        # Análise por categoria
        categories = {}
        for analysis in detailed_analyses:
            market_type = analysis['market_type']
            if market_type not in categories:
                categories[market_type] = []
            categories[market_type].append(analysis)
        
        message += f"📊 *ANÁLISE POR CATEGORIA:*\n\n"
        
        for category, analyses in categories.items():
            favorable_count = sum(1 for analysis in analyses if analysis['is_favorable'])
            total_count = len(analyses)
            
            if favorable_count > 0:
                message += f"*{category.upper()}:*\n"
                message += f"✅ {favorable_count}/{total_count} apostas favoráveis\n"
                
                # Mostrar melhores da categoria
                category_best = sorted(analyses, key=lambda x: x['expected_value'], reverse=True)[:3]
                for analysis in category_best:
                    if analysis['is_favorable']:
                        message += f"   {analysis['recommendation_emoji']} {analysis['selection']}: {analysis['expected_value']:+.1%} EV\n"
                message += "\n"
        
        # Resumo estatístico
        if detailed_analyses:
            avg_ev = sum(a['expected_value'] for a in detailed_analyses) / len(detailed_analyses)
            max_ev = max(a['expected_value'] for a in detailed_analyses)
            favorable_total = sum(1 for a in detailed_analyses if a['is_favorable'])
            
            message += f"📈 *RESUMO ESTATÍSTICO:*\n"
            message += f"• Valor Esperado Médio: {avg_ev:+.1%}\n"
            message += f"• Melhor Valor Esperado: {max_ev:+.1%}\n"
            message += f"• Apostas Favoráveis: {favorable_total}/{len(detailed_analyses)}\n"
            message += f"• Taxa de Sucesso: {favorable_total/len(detailed_analyses):.1%}\n\n"
        
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
            predictions = data.get('predictions', [])
            
            print(f"\n📊 Processando: {match_data.get('home_team', 'N/A')} vs {match_data.get('away_team', 'N/A')}")
            
            # Análise detalhada
            detailed_analyses = analyzer.analyze_all_predictions(predictions)
            
            # Top recomendações
            top_recommendations = analyzer.get_top_recommendations(detailed_analyses)
            
            # Formatar mensagem
            detailed_message = analyzer.format_detailed_message(match_data, detailed_analyses, top_recommendations)
            
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
