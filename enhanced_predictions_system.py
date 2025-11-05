#!/usr/bin/env python3
"""
Sistema de Predições Aprimorado - MaraBet AI
Integra todos os mercados de apostas para predições mais específicas e detalhadas
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np

# Importar mercados expandidos
from betting_markets.expanded_markets import ExpandedBettingMarkets, MarketType, MarketPrediction
from betting_markets.goals_market import GoalsMarket
from betting_markets.handicap_market import HandicapMarket
from betting_markets.cards_market import CardsMarket
from betting_markets.corners_market import CornersMarket
from betting_markets.double_chance_market import DoubleChanceMarket
from betting_markets.exact_score_market import ExactScoreMarket

logger = logging.getLogger(__name__)

class EnhancedPredictionsSystem:
    """Sistema de predições aprimorado com múltiplos mercados"""
    
    def __init__(self):
        self.expanded_markets = ExpandedBettingMarkets()
        self.goals_market = GoalsMarket()
        self.handicap_market = HandicapMarket()
        self.cards_market = CardsMarket()
        self.corners_market = CornersMarket()
        self.double_chance_market = DoubleChanceMarket()
        self.exact_score_market = ExactScoreMarket()
        
        # Configurações
        self.min_confidence = 0.3
        self.max_predictions_per_market = 10
        
    def generate_comprehensive_predictions(self, match_data: Dict[str, Any]) -> Dict[str, List[MarketPrediction]]:
        """Gera predições abrangentes para todos os mercados"""
        logger.info(f"Gerando predições abrangentes para {match_data.get('home_team', 'Casa')} vs {match_data.get('away_team', 'Visitante')}")
        
        all_predictions = {}
        
        try:
            # 1. Mercados de golos
            all_predictions['goals'] = self._generate_goals_predictions(match_data)
            
            # 2. Mercados de handicap
            all_predictions['handicap'] = self._generate_handicap_predictions(match_data)
            
            # 3. Mercados de cartões
            all_predictions['cards'] = self._generate_cards_predictions(match_data)
            
            # 4. Mercados de cantos
            all_predictions['corners'] = self._generate_corners_predictions(match_data)
            
            # 5. Mercados de dupla chance
            all_predictions['double_chance'] = self._generate_double_chance_predictions(match_data)
            
            # 6. Mercados de resultado exato
            all_predictions['exact_score'] = self._generate_exact_score_predictions(match_data)
            
            # 7. Mercados básicos (1X2)
            all_predictions['match_winner'] = self._generate_match_winner_predictions(match_data)
            
            logger.info(f"✅ Predições geradas para {len(all_predictions)} categorias de mercados")
            
        except Exception as e:
            logger.error(f"Erro ao gerar predições: {e}")
            all_predictions = {}
        
        return all_predictions
    
    def _generate_goals_predictions(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Gera predições para mercados de golos"""
        predictions = []
        
        try:
            # Over/Under
            predictions.extend(self.goals_market.predict_over_under(match_data))
            
            # Gols exatos
            predictions.extend(self.goals_market.predict_exact_goals(match_data))
            
            # Ambas marcam
            predictions.extend(self.goals_market.predict_both_teams_score(match_data))
            
            # Primeiro tempo
            predictions.extend(self.goals_market.predict_first_half_goals(match_data))
            
            # Jogo limpo
            predictions.extend(self.goals_market.predict_clean_sheet(match_data))
            
        except Exception as e:
            logger.error(f"Erro ao gerar predições de golos: {e}")
        
        return self._filter_predictions(predictions)
    
    def _generate_handicap_predictions(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Gera predições para mercados de handicap"""
        predictions = []
        
        try:
            # Handicap asiático
            predictions.extend(self.handicap_market.predict_asian_handicap(match_data))
            
            # Handicap europeu
            predictions.extend(self.handicap_market.predict_european_handicap(match_data))
            
            # Handicap de cantos
            predictions.extend(self.handicap_market.predict_corner_handicap(match_data))
            
        except Exception as e:
            logger.error(f"Erro ao gerar predições de handicap: {e}")
        
        return self._filter_predictions(predictions)
    
    def _generate_cards_predictions(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Gera predições para mercados de cartões"""
        predictions = []
        
        try:
            # Total de cartões
            predictions.extend(self.cards_market.predict_total_cards(match_data))
            
            # Cartões amarelos
            predictions.extend(self.cards_market.predict_yellow_cards(match_data))
            
            # Cartões vermelhos
            predictions.extend(self.cards_market.predict_red_cards(match_data))
            
            # Primeiro cartão
            predictions.extend(self.cards_market.predict_first_card(match_data))
            
            # Timing dos cartões
            predictions.extend(self.cards_market.predict_card_timing(match_data))
            
        except Exception as e:
            logger.error(f"Erro ao gerar predições de cartões: {e}")
        
        return self._filter_predictions(predictions)
    
    def _generate_corners_predictions(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Gera predições para mercados de cantos"""
        predictions = []
        
        try:
            # Total de cantos
            predictions.extend(self.corners_market.predict_total_corners(match_data))
            
            # Handicap de cantos
            predictions.extend(self.corners_market.predict_corner_handicap(match_data))
            
            # Primeiro canto
            predictions.extend(self.corners_market.predict_first_corner(match_data))
            
            # Timing dos cantos
            predictions.extend(self.corners_market.predict_corner_timing(match_data))
            
            # Corrida de cantos
            predictions.extend(self.corners_market.predict_corner_race(match_data))
            
        except Exception as e:
            logger.error(f"Erro ao gerar predições de cantos: {e}")
        
        return self._filter_predictions(predictions)
    
    def _generate_double_chance_predictions(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Gera predições para mercados de dupla chance"""
        predictions = []
        
        try:
            # Dupla chance básica
            predictions.extend(self.double_chance_market.predict_double_chance(match_data))
            
            # Tripla chance
            predictions.extend(self.double_chance_market.predict_triple_chance(match_data))
            
            # Win-Draw-Win
            predictions.extend(self.double_chance_market.predict_win_draw_win(match_data))
            
            # Dupla chance alternativa
            predictions.extend(self.double_chance_market.predict_alternative_double_chance(match_data))
            
        except Exception as e:
            logger.error(f"Erro ao gerar predições de dupla chance: {e}")
        
        return self._filter_predictions(predictions)
    
    def _generate_exact_score_predictions(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Gera predições para mercados de resultado exato"""
        predictions = []
        
        try:
            # Resultado exato
            predictions.extend(self.exact_score_market.predict_exact_score(match_data))
            
            # Resultado do intervalo
            predictions.extend(self.exact_score_market.predict_half_time_score(match_data))
            
            # Grupos de resultado
            predictions.extend(self.exact_score_market.predict_correct_score_group(match_data))
            
            # Vitória sem sofrer gols
            predictions.extend(self.exact_score_market.predict_win_to_nil(match_data))
            
            # Intervalos de gols
            predictions.extend(self.exact_score_market.predict_goal_intervals(match_data))
            
        except Exception as e:
            logger.error(f"Erro ao gerar predições de resultado exato: {e}")
        
        return self._filter_predictions(predictions)
    
    def _generate_match_winner_predictions(self, match_data: Dict[str, Any]) -> List[MarketPrediction]:
        """Gera predições para resultado da partida (1X2)"""
        predictions = []
        
        try:
            # Usar o sistema expandido para 1X2
            predictions.extend(self.expanded_markets._predict_match_winner(match_data))
            
        except Exception as e:
            logger.error(f"Erro ao gerar predições de resultado da partida: {e}")
        
        return self._filter_predictions(predictions)
    
    def _filter_predictions(self, predictions: List[MarketPrediction]) -> List[MarketPrediction]:
        """Filtra predições por confiança e limita quantidade"""
        # Filtrar por confiança mínima
        filtered = [p for p in predictions if p.confidence >= self.min_confidence]
        
        # Ordenar por confiança (maior primeiro)
        filtered.sort(key=lambda x: x.confidence, reverse=True)
        
        # Limitar quantidade
        return filtered[:self.max_predictions_per_market]
    
    def get_top_recommendations(self, all_predictions: Dict[str, List[MarketPrediction]], 
                              top_n: int = 20) -> List[MarketPrediction]:
        """Retorna as melhores recomendações de todos os mercados"""
        all_recommendations = []
        
        for category, predictions in all_predictions.items():
            for pred in predictions:
                # Calcular score de recomendação
                recommendation_score = self._calculate_recommendation_score(pred)
                pred.recommended = recommendation_score > 0.6
                
                all_recommendations.append((pred, recommendation_score))
        
        # Ordenar por score de recomendação
        all_recommendations.sort(key=lambda x: x[1], reverse=True)
        
        # Retornar top N
        return [pred for pred, score in all_recommendations[:top_n]]
    
    def _calculate_recommendation_score(self, prediction: MarketPrediction) -> float:
        """Calcula score de recomendação para uma predição"""
        # Fatores para o score
        confidence_factor = prediction.confidence
        probability_factor = prediction.predicted_probability
        
        # Penalizar probabilidades muito baixas ou muito altas
        if probability_factor < 0.1 or probability_factor > 0.9:
            probability_factor *= 0.5
        
        # Score base
        base_score = (confidence_factor * 0.6) + (probability_factor * 0.4)
        
        # Bônus para mercados específicos
        if prediction.market_type in [MarketType.OVER_UNDER, MarketType.BOTH_TEAMS_SCORE]:
            base_score *= 1.1
        elif prediction.market_type in [MarketType.ASIAN_HANDICAP, MarketType.EUROPEAN_HANDICAP]:
            base_score *= 1.05
        
        return min(base_score, 1.0)
    
    def generate_telegram_message(self, match_data: Dict[str, Any], 
                                all_predictions: Dict[str, List[MarketPrediction]]) -> str:
        """Gera mensagem formatada para Telegram"""
        home_team = match_data.get('home_team', 'Casa')
        away_team = match_data.get('away_team', 'Visitante')
        league = match_data.get('league', 'Liga')
        match_date = match_data.get('match_date', datetime.now().strftime('%d/%m/%Y %H:%M'))
        
        message = f"⚽ **PREDIÇÕES DETALHADAS** ⚽\n\n"
        message += f"🏆 **{home_team} vs {away_team}**\n"
        message += f"📅 {match_date}\n"
        message += f"🏟️ {league}\n\n"
        
        # Adicionar predições por categoria
        for category, predictions in all_predictions.items():
            if not predictions:
                continue
                
            category_names = {
                'goals': '⚽ GOLOS',
                'handicap': '⚖️ HANDICAP',
                'cards': '🟨 CARTÕES',
                'corners': '📐 CANTOS',
                'double_chance': '🎯 DUPLA CHANCE',
                'exact_score': '🎯 RESULTADO EXATO',
                'match_winner': '🏆 RESULTADO'
            }
            
            message += f"**{category_names.get(category, category.upper())}:**\n"
            
            for pred in predictions[:5]:  # Top 5 por categoria
                confidence_emoji = "🟢" if pred.confidence > 0.7 else "🟡" if pred.confidence > 0.5 else "🔴"
                message += f"{confidence_emoji} {pred.selection}: {pred.predicted_probability:.1%} (conf: {pred.confidence:.1%})\n"
            
            message += "\n"
        
        # Adicionar estatísticas gerais
        message += "📊 **ESTATÍSTICAS:**\n"
        
        # Estatísticas de golos
        if 'goals' in all_predictions:
            goals_stats = self.goals_market.get_goal_statistics(match_data)
            message += f"• Média de gols: {goals_stats['total_goals_avg']:.1f}\n"
            message += f"• BTTS: {goals_stats['btts_probability']:.1%}\n"
            message += f"• Over 2.5: {goals_stats['over_25_probability']:.1%}\n"
        
        # Estatísticas de cartões
        if 'cards' in all_predictions:
            cards_stats = self.cards_market.get_cards_statistics(match_data)
            message += f"• Média de cartões: {cards_stats['total_cards_avg']:.1f}\n"
            message += f"• Cartão vermelho: {cards_stats['red_card_prob']:.1%}\n"
        
        # Estatísticas de cantos
        if 'corners' in all_predictions:
            corners_stats = self.corners_market.get_corners_statistics(match_data)
            message += f"• Média de cantos: {corners_stats['total_corners_avg']:.1f}\n"
            message += f"• Over 10.5 cantos: {corners_stats['over_105_corners_prob']:.1%}\n"
        
        message += "\n🎯 **Sistema MaraBet AI - Predições Profissionais**"
        
        return message
    
    def save_predictions_to_file(self, match_data: Dict[str, Any], 
                               all_predictions: Dict[str, List[MarketPrediction]], 
                               filename: str = None) -> str:
        """Salva predições em arquivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"predictions_{timestamp}.json"
        
        # Converter predições para formato serializável
        serializable_predictions = {}
        for category, predictions in all_predictions.items():
            serializable_predictions[category] = []
            for pred in predictions:
                serializable_predictions[category].append({
                    'market_type': pred.market_type.value,
                    'selection': pred.selection,
                    'predicted_probability': pred.predicted_probability,
                    'confidence': pred.confidence,
                    'expected_value': pred.expected_value,
                    'kelly_fraction': pred.kelly_fraction,
                    'recommended': pred.recommended,
                    'reasoning': pred.reasoning
                })
        
        # Dados completos
        data = {
            'match_data': match_data,
            'predictions': serializable_predictions,
            'generated_at': datetime.now().isoformat(),
            'total_predictions': sum(len(preds) for preds in all_predictions.values())
        }
        
        # Converter valores não serializáveis para JSON
        def make_json_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_serializable(item) for item in obj]
            elif isinstance(obj, bool):
                return obj  # Boolean é serializável em JSON
            elif isinstance(obj, (int, float, str)):
                return obj
            elif hasattr(obj, '__dict__'):
                return make_json_serializable(obj.__dict__)
            else:
                return str(obj)
        
        data = make_json_serializable(data)
        
        # Salvar arquivo
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Predições salvas em {filename}")
        return filename

if __name__ == "__main__":
    # Demo do sistema aprimorado
    print("🚀 SISTEMA DE PREDIÇÕES APRIMORADO - MARABET AI")
    print("=" * 55)
    
    system = EnhancedPredictionsSystem()
    
    # Dados de exemplo para uma partida
    match_data = {
        'home_team': 'Manchester City',
        'away_team': 'Manchester United',
        'league': 'Premier League',
        'match_date': '2024-01-15 15:30',
        'home_strength': 0.7,
        'away_strength': 0.6,
        'home_advantage': 0.1,
        'home_goals_avg': 2.1,
        'away_goals_avg': 1.8,
        'home_corners_avg': 6.5,
        'away_corners_avg': 5.2,
        'home_cards_avg': 2.3,
        'away_cards_avg': 2.1,
        'home_yellow_avg': 2.0,
        'away_yellow_avg': 1.8,
        'home_red_avg': 0.1,
        'away_red_avg': 0.08,
        'form_factor': 1.1,
        'injury_factor': 0.95,
        'weather_factor': 1.0,
        'importance_factor': 1.2,
        'rivalry_factor': 1.3,
        'referee_factor': 1.0,
        'possession_factor': 1.05,
        'style_factor': 1.1
    }
    
    # Gerar predições abrangentes
    print("🔮 Gerando predições abrangentes...")
    all_predictions = system.generate_comprehensive_predictions(match_data)
    
    # Mostrar resumo
    print(f"\n📊 RESUMO DAS PREDIÇÕES:")
    print("-" * 30)
    for category, predictions in all_predictions.items():
        print(f"{category.upper()}: {len(predictions)} predições")
    
    # Mostrar top recomendações
    print(f"\n🏆 TOP 10 RECOMENDAÇÕES:")
    print("-" * 30)
    top_recommendations = system.get_top_recommendations(all_predictions, top_n=10)
    for i, pred in enumerate(top_recommendations, 1):
        print(f"{i:2d}. {pred.market_type.value}: {pred.selection}")
        print(f"    Prob: {pred.predicted_probability:.1%} | Conf: {pred.confidence:.1%} | Rec: {'✅' if pred.recommended else '❌'}")
    
    # Gerar mensagem para Telegram
    print(f"\n📱 MENSAGEM TELEGRAM:")
    print("-" * 30)
    telegram_message = system.generate_telegram_message(match_data, all_predictions)
    print(telegram_message)
    
    # Salvar predições
    filename = system.save_predictions_to_file(match_data, all_predictions)
    print(f"\n💾 Predições salvas em: {filename}")
    
    print("\n✅ Sistema de predições aprimorado implementado com sucesso!")
    print("🎯 Agora você tem acesso a múltiplos mercados de apostas específicos!")
