from typing import Dict, List, Optional
from datetime import datetime
import logging
from armazenamento.banco_de_dados import SessionLocal, Match, Odds, Prediction
from processadores.statistics import StatisticsProcessor
from settings.settings import MIN_CONFIDENCE, MAX_CONFIDENCE, MIN_VALUE_EV
from notifications.notification_integrator import notify_prediction

logger = logging.getLogger(__name__)

class ValueFinder:
    """Identifica apostas com valor positivo"""
    
    def __init__(self):
        self.stats_processor = StatisticsProcessor()
        self.db = SessionLocal()
    
    def analyze_match(self, match_data: Dict, odds_data: List[Dict]) -> Optional[Prediction]:
        """Analisa uma partida e busca valor"""
        
        try:
            # 1. Calcular probabilidades
            probabilities = self._calculate_probabilities(match_data)
            
            # 2. Comparar com odds
            best_value = self._find_best_value(probabilities, odds_data)
            
            if not best_value:
                return None
            
            # 3. Verificar se atende critérios
            if not self._meets_criteria(best_value):
                return None
            
            # 4. Calcular stake recomendado
            stake = self._calculate_stake(best_value)
            
            # 5. Criar predição
            prediction = Prediction(
                fixture_id=match_data['fixture']['id'],
                market=best_value['market'],
                selection=best_value['selection'],
                predicted_probability=best_value['probability'],
                implied_probability=best_value['implied_probability'],
                recommended_odd=best_value['odd'],
                current_odd=best_value['odd'],
                expected_value=best_value['ev'],
                confidence=best_value['confidence'],
                stake_percentage=stake,
                recommended=True,
                factors=best_value['factors']
            )
            
            self.db.add(prediction)
            self.db.commit()
            
            logger.info(f"✅ Valor encontrado: {best_value['market']} - EV: {best_value['ev']:.2%}")
            
            # Enviar notificação sobre a predição
            try:
                prediction_data = {
                    'fixture_id': prediction.fixture_id,
                    'market': prediction.market,
                    'selection': prediction.selection,
                    'expected_value': prediction.expected_value,
                    'confidence': prediction.confidence,
                    'stake_percentage': prediction.stake_percentage,
                    'recommended': prediction.recommended,
                    'match': {
                        'home_team': match_data.get('teams', {}).get('home', {}).get('name', 'N/A'),
                        'away_team': match_data.get('teams', {}).get('away', {}).get('name', 'N/A'),
                        'league': 'N/A'  # Pode ser obtido dos dados da partida
                    }
                }
                
                # Enviar notificação de forma assíncrona
                import asyncio
                asyncio.create_task(notify_prediction(prediction_data))
                
            except Exception as e:
                logger.error(f"Erro ao enviar notificação: {e}")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Erro ao analisar partida: {e}")
            self.db.rollback()
            return None
    
    def _calculate_probabilities(self, match_data: Dict) -> Dict:
        """Calcula probabilidades reais do jogo"""
        
        # Aqui você implementaria seu modelo de ML
        # Por enquanto, exemplo simplificado
        
        home_team = match_data['teams']['home']['name']
        away_team = match_data['teams']['away']['name']
        
        # Simulação de cálculo (substitua por modelo real)
        probabilities = {
            'home_win': 0.45,
            'draw': 0.30,
            'away_win': 0.25,
            'over_25': 0.68,
            'under_25': 0.32,
            'btts_yes': 0.58,
            'btts_no': 0.42
        }
        
        return probabilities
    
    def _find_best_value(self, probabilities: Dict, odds_data: List[Dict]) -> Optional[Dict]:
        """Encontra a melhor oportunidade de valor"""
        
        best_value = None
        best_ev = -1
        
        for odds in odds_data:
            for market in odds.get('bookmakers', [{}])[0].get('markets', []):
                market_name = market.get('key')
                
                for outcome in market.get('outcomes', []):
                    selection = outcome.get('name')
                    odd = outcome.get('price')
                    
                    # Mapear seleção para probabilidade
                    prob_key = self._map_selection(market_name, selection)
                    probability = probabilities.get(prob_key, 0)
                    
                    if probability == 0:
                        continue
                    
                    # Calcular valor
                    value = self.stats_processor.calculate_value(probability, odd)
                    
                    if value['expected_value'] > best_ev:
                        best_ev = value['expected_value']
                        best_value = {
                            'market': market_name,
                            'selection': selection,
                            'probability': probability,
                            'implied_probability': value['implied_probability'],
                            'odd': odd,
                            'ev': value['expected_value'],
                            'confidence': self._calculate_confidence(value, probabilities),
                            'factors': self._get_factors(probabilities, market_name)
                        }
        
        return best_value
    
    def _map_selection(self, market: str, selection: str) -> str:
        """Mapeia seleção de mercado para chave de probabilidade"""
        mapping = {
            'h2h': {
                'Home': 'home_win',
                'Draw': 'draw',
                'Away': 'away_win'
            },
            'totals': {
                'Over': 'over_25',
                'Under': 'under_25'
            }
        }
        return mapping.get(market, {}).get(selection, '')
    
    def _meets_criteria(self, value: Dict) -> bool:
        """Verifica se atende aos critérios mínimos"""
        return (
            value['ev'] >= MIN_VALUE_EV and
            MIN_CONFIDENCE <= value['confidence'] <= MAX_CONFIDENCE
        )
    
    def _calculate_stake(self, value: Dict) -> float:
        """Calcula stake recomendado"""
        return self.stats_processor.kelly_criterion(
            value['probability'],
            value['odd'],
            fraction=0.25
        )
    
    def _calculate_confidence(self, value: Dict, probabilities: Dict) -> float:
        """Calcula nível de confiança da previsão"""
        # Implementação simplificada
        # Na prática, usar validação cruzada, backtesting, etc
        
        base_confidence = value['probability']
        ev_boost = min(value['expected_value'] * 0.5, 0.15)
        
        return min(base_confidence + ev_boost, 0.95)
    
    def _get_factors(self, probabilities: Dict, market: str) -> Dict:
        """Retorna fatores que justificam a recomendação"""
        return {
            'model_probability': probabilities.get(market, 0),
            'statistical_edge': 'High value detected',
            'timestamp': datetime.now().isoformat()
        }
    
    def __del__(self):
        self.db.close()
