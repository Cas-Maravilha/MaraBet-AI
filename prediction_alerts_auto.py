#!/usr/bin/env python3
"""
Sistema de Geração de Previsões com Alertas Automáticos - Execução Automática
Monitora jogos com alto índice de acerto (acima de 80%) e envia alertas automáticos
"""

import json
import os
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PredictionAlertSystem:
    def __init__(self):
        self.config_file = "telegram_config.json"
        self.config = self.load_config()
        self.base_url = f"https://api.telegram.org/bot{self.config.get('telegram_bot_token', '')}"
        
        # Configurações de alertas
        self.high_confidence_threshold = 0.80  # 80% de confiança
        self.excellent_value_threshold = 0.15  # 15% de valor esperado
        self.alert_cooldown = 3600  # 1 hora entre alertas do mesmo jogo
        
        # Cache de alertas enviados
        self.sent_alerts = {}
        
    def load_config(self):
        """Carrega configuração do Telegram"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def send_alert(self, message, parse_mode='Markdown'):
        """Envia alerta para o Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.config.get('telegram_chat_id'),
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info("🚨 Alerta enviado com sucesso!")
                    return True
                else:
                    logger.error(f"❌ Erro ao enviar alerta: {result.get('description', 'Erro desconhecido')}")
            else:
                logger.error(f"❌ Erro HTTP: {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao enviar alerta: {e}")
            return False
    
    def calculate_expected_value(self, probability: float, odds: float) -> float:
        """Calcula o valor esperado de uma aposta"""
        if odds <= 0:
            return 0
        return (probability * odds) - 1
    
    def get_market_odds(self, market_type: str, selection: str) -> float:
        """Simula odds do mercado"""
        odds_mapping = {
            'exact_goals': {
                '0': 8.50, '1': 4.20, '2': 3.40, '3': 4.80, '4': 8.20, '5+': 15.00
            },
            'both_teams_score': {
                'Sim': 1.80, 'Não': 2.00
            },
            'over_under': {
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
            'double_chance': {
                '1X': 1.30, 'X2': 1.35, '12': 1.20
            },
            'match_winner': {
                '1': 1.90, 'X': 3.50, '2': 2.30
            },
            'total_cards': {
                'Over 1.5': 1.20, 'Under 1.5': 4.50,
                'Over 2.5': 1.50, 'Under 2.5': 2.50,
                'Over 3.5': 1.95, 'Under 3.5': 1.85,
                'Over 4.5': 2.60, 'Under 4.5': 1.50,
                'Over 5.5': 3.80, 'Under 5.5': 1.25,
                'Over 6.5': 5.50, 'Under 6.5': 1.15
            },
            'total_corners': {
                'Over 8.5': 1.35, 'Under 8.5': 3.00,
                'Over 9.5': 1.55, 'Under 9.5': 2.40,
                'Over 10.5': 1.85, 'Under 10.5': 1.95,
                'Over 11.5': 2.20, 'Under 11.5': 1.65,
                'Over 12.5': 2.70, 'Under 12.5': 1.45,
                'Over 13.5': 3.30, 'Under 13.5': 1.30
            }
        }
        
        return odds_mapping.get(market_type, {}).get(selection, 2.00)
    
    def analyze_prediction_for_alerts(self, prediction: Dict) -> Dict:
        """Analisa uma predição para alertas"""
        market_type = prediction.get('market_type', '')
        selection = prediction.get('selection', '')
        probability = prediction.get('predicted_probability', 0.0)
        confidence = prediction.get('confidence', 0.0)
        
        odds = self.get_market_odds(market_type, selection)
        expected_value = self.calculate_expected_value(probability, odds)
        
        # Determinar se é um alerta de alta confiança
        is_high_confidence = probability >= self.high_confidence_threshold
        is_excellent_value = expected_value >= self.excellent_value_threshold
        
        # Calcular chances de green
        min_green_chance = max(0, probability - 0.10)  # Margem de erro 10%
        max_green_chance = min(1, probability + 0.05)  # Margem positiva 5%
        
        # Determinar nível de alerta
        if is_high_confidence and is_excellent_value:
            alert_level = "CRÍTICO"
            alert_emoji = "🚨"
        elif is_high_confidence:
            alert_level = "ALTO"
            alert_emoji = "🔥"
        elif is_excellent_value:
            alert_level = "MÉDIO"
            alert_emoji = "⚡"
        else:
            alert_level = "BAIXO"
            alert_emoji = "📊"
        
        return {
            'market_type': market_type,
            'selection': selection,
            'probability': probability,
            'confidence': confidence,
            'odds': odds,
            'expected_value': expected_value,
            'is_high_confidence': is_high_confidence,
            'is_excellent_value': is_excellent_value,
            'min_green_chance': min_green_chance,
            'max_green_chance': max_green_chance,
            'alert_level': alert_level,
            'alert_emoji': alert_emoji,
            'reasoning': prediction.get('reasoning', 'Análise baseada em dados históricos')
        }
    
    def scan_predictions_for_alerts(self) -> List[Dict]:
        """Escaneia predições em busca de alertas"""
        prediction_files = [f for f in os.listdir('.') if 'predictions' in f and f.endswith('.json')]
        alerts = []
        
        for filename in prediction_files:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                match_data = data.get('match_data', {})
                predictions = data.get('predictions', {})
                
                match_key = f"{match_data.get('home_team', 'N/A')} vs {match_data.get('away_team', 'N/A')}"
                
                # Verificar se já enviamos alerta recentemente
                if match_key in self.sent_alerts:
                    last_alert_time = self.sent_alerts[match_key]
                    if time.time() - last_alert_time < self.alert_cooldown:
                        continue
                
                # Analisar predições
                for category, pred_list in predictions.items():
                    if isinstance(pred_list, list):
                        for prediction in pred_list:
                            analysis = self.analyze_prediction_for_alerts(prediction)
                            
                            # Adicionar alerta se atender critérios
                            if analysis['is_high_confidence'] or analysis['is_excellent_value']:
                                alert = {
                                    'match': match_key,
                                    'league': match_data.get('league', 'N/A'),
                                    'category': category,
                                    'analysis': analysis,
                                    'match_data': match_data
                                }
                                alerts.append(alert)
                
            except Exception as e:
                logger.error(f"Erro ao processar {filename}: {e}")
        
        return alerts
    
    def format_alert_message(self, alert: Dict) -> str:
        """Formata mensagem de alerta"""
        match = alert['match']
        league = alert['league']
        analysis = alert['analysis']
        
        message = f"{analysis['alert_emoji']} *ALERTA {analysis['alert_level']} MARABET AI*\n\n"
        message += f"🏆 *{match}*\n"
        message += f"🏟️ {league}\n"
        message += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        
        message += f"🎯 *OPORTUNIDADE IDENTIFICADA:*\n"
        message += f"• Mercado: {analysis['market_type']}\n"
        message += f"• Seleção: {analysis['selection']}\n"
        message += f"• Probabilidade: {analysis['probability']:.1%}\n"
        message += f"• Confiança: {analysis['confidence']:.1%}\n"
        message += f"• Odds: {analysis['odds']:.2f}\n"
        message += f"• Valor Esperado: {analysis['expected_value']:+.1%}\n\n"
        
        message += f"🟢 *CHANCES DE GREEN:*\n"
        message += f"• Mínima: {analysis['min_green_chance']:.1%}\n"
        message += f"• Máxima: {analysis['max_green_chance']:.1%}\n"
        message += f"• Média: {analysis['probability']:.1%}\n\n"
        
        message += f"💡 *ANÁLISE:*\n"
        message += f"{analysis['reasoning']}\n\n"
        
        if analysis['is_high_confidence']:
            message += f"🔥 *ALTA CONFIANÇA* - Probabilidade acima de {self.high_confidence_threshold:.0%}\n"
        
        if analysis['is_excellent_value']:
            message += f"⭐ *EXCELENTE VALOR* - EV acima de {self.excellent_value_threshold:.0%}\n"
        
        message += f"\n⚠️ *AÇÃO RECOMENDADA:*\n"
        if analysis['alert_level'] == "CRÍTICO":
            message += f"🚨 APOSTA RECOMENDADA - Oportunidade excepcional!\n"
        elif analysis['alert_level'] == "ALTO":
            message += f"🔥 CONSIDERE APOSTAR - Alta probabilidade de sucesso\n"
        else:
            message += f"📊 MONITORE - Oportunidade interessante\n"
        
        message += f"\n🤖 *Sistema MaraBet AI - Monitoramento Automático*"
        
        return message
    
    def send_high_confidence_alerts(self):
        """Envia alertas para oportunidades de alta confiança"""
        alerts = self.scan_predictions_for_alerts()
        
        if not alerts:
            logger.info("📊 Nenhum alerta de alta confiança encontrado")
            return
        
        # Filtrar apenas alertas críticos e altos
        critical_alerts = [alert for alert in alerts if alert['analysis']['alert_level'] in ['CRÍTICO', 'ALTO']]
        
        if not critical_alerts:
            logger.info("📊 Nenhum alerta crítico/alto encontrado")
            return
        
        logger.info(f"🚨 Encontrados {len(critical_alerts)} alertas críticos/altos")
        
        # Enviar alertas
        sent_count = 0
        for alert in critical_alerts:
            message = self.format_alert_message(alert)
            
            if self.send_alert(message):
                sent_count += 1
                # Registrar que enviamos alerta para este jogo
                self.sent_alerts[alert['match']] = time.time()
                time.sleep(2)  # Pausa entre alertas
        
        logger.info(f"✅ {sent_count} alertas críticos/altos enviados!")
    
    def send_daily_summary(self):
        """Envia resumo diário de oportunidades"""
        alerts = self.scan_predictions_for_alerts()
        
        if not alerts:
            return
        
        # Agrupar por nível de alerta
        critical_count = len([a for a in alerts if a['analysis']['alert_level'] == 'CRÍTICO'])
        high_count = len([a for a in alerts if a['analysis']['alert_level'] == 'ALTO'])
        medium_count = len([a for a in alerts if a['analysis']['alert_level'] == 'MÉDIO'])
        
        summary = f"📊 *RESUMO DIÁRIO MARABET AI*\n\n"
        summary += f"📅 {datetime.now().strftime('%d/%m/%Y')}\n\n"
        
        summary += f"🚨 *ALERTAS IDENTIFICADOS:*\n"
        summary += f"• Críticos: {critical_count}\n"
        summary += f"• Altos: {high_count}\n"
        summary += f"• Médios: {medium_count}\n"
        summary += f"• Total: {len(alerts)}\n\n"
        
        summary += f"🎯 *CRITÉRIOS DE ALERTA:*\n"
        summary += f"• Alta Confiança: {self.high_confidence_threshold:.0%}+\n"
        summary += f"• Excelente Valor: {self.excellent_value_threshold:.0%}+ EV\n"
        summary += f"• Cooldown: {self.alert_cooldown//3600}h entre alertas\n\n"
        
        if critical_count > 0:
            summary += f"🚨 *ATENÇÃO:* {critical_count} oportunidades críticas identificadas!\n\n"
        
        summary += f"🤖 *Sistema MaraBet AI - Monitoramento 24/7*"
        
        self.send_alert(summary)
    
    def test_alert_system(self):
        """Testa o sistema de alertas"""
        logger.info("🧪 Testando sistema de alertas...")
        
        alerts = self.scan_predictions_for_alerts()
        
        logger.info(f"📊 {len(alerts)} alertas encontrados")
        
        # Mostrar estatísticas
        critical_count = len([a for a in alerts if a['analysis']['alert_level'] == 'CRÍTICO'])
        high_count = len([a for a in alerts if a['analysis']['alert_level'] == 'ALTO'])
        medium_count = len([a for a in alerts if a['analysis']['alert_level'] == 'MÉDIO'])
        low_count = len([a for a in alerts if a['analysis']['alert_level'] == 'BAIXO'])
        
        logger.info(f"🚨 Críticos: {critical_count}")
        logger.info(f"🔥 Altos: {high_count}")
        logger.info(f"⚡ Médios: {medium_count}")
        logger.info(f"📊 Baixos: {low_count}")
        
        # Mostrar exemplos
        if alerts:
            logger.info("\n📋 Exemplos de alertas:")
            for i, alert in enumerate(alerts[:3], 1):
                logger.info(f"{i}. {alert['match']}: {alert['analysis']['alert_level']} - {alert['analysis']['selection']} ({alert['analysis']['probability']:.1%})")

def main():
    alert_system = PredictionAlertSystem()
    
    print("🎯 MARABET AI - SISTEMA DE ALERTAS AUTOMÁTICOS")
    print("=" * 60)
    
    # Executar automaticamente
    print("\n🧪 Testando sistema de alertas...")
    alert_system.test_alert_system()
    
    print("\n🚨 Enviando alertas imediatos...")
    alert_system.send_high_confidence_alerts()
    
    print("\n📊 Enviando resumo diário...")
    alert_system.send_daily_summary()
    
    print("\n✅ Sistema de alertas executado com sucesso!")

if __name__ == "__main__":
    main()
