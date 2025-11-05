#!/usr/bin/env python3
"""
Execução Automática com Telegram - Competições Internacionais
MaraBet AI - Executa predições e envia automaticamente para Telegram
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime, timedelta
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_telegram_message(bot_token, chat_id, message, parse_mode='HTML'):
    """Envia mensagem para o Telegram"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ Mensagem enviada para Telegram com sucesso")
            return True
        else:
            logger.error(f"❌ Erro ao enviar para Telegram: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao enviar para Telegram: {e}")
        return False

def format_telegram_message(predictions, category="INTERNACIONAIS"):
    """Formata mensagem para Telegram"""
    if not predictions:
        return f"❌ Nenhuma partida {category.lower()} encontrada."
    
    # Emoji para o tipo de competição
    emoji_map = {
        'Club': '🏆',
        'National': '🌍',
        'League': '⚽'
    }
    
    message = f"🌍 <b>PREDIÇÕES {category} - MARABET AI</b> 🌍\n"
    message += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    message += f"🤖 Sistema de IA com dados reais da API Football\n"
    message += f"🌐 Cobertura: Competições internacionais completas\n\n"
    
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
            type_name = {
                'Club': 'COMPETIÇÕES DE CLUBES', 
                'National': 'COMPETIÇÕES NACIONAIS', 
                'League': 'LIGAS NACIONAIS'
            }.get(comp_type, comp_type.upper())
            
            emoji = emoji_map.get(comp_type, '⚽')
            message += f"{emoji} <b>{type_name} - {len(type_predictions)} partidas:</b>\n"
            message += "=" * 30 + "\n\n"
            
            for i, prediction in enumerate(type_predictions[:3], 1):  # Limitar a 3 por tipo
                message += f"⚽ <b>Partida {i}:</b>\n"
                message += f"⚔️ {prediction['home_team']} vs {prediction['away_team']}\n"
                message += f"📅 {prediction['date_formatted']}\n"
                message += f"🏆 {prediction['competition']} ({prediction['country']})\n"
                message += f"📊 Status: {prediction['status_name']}\n"
                message += f"🎯 Tier: {prediction['tier']}\n"
                
                if prediction['status'] in ['1H', '2H', 'HT', 'LIVE']:
                    message += f"⚽ Placar: {prediction['home_team']} {prediction['home_score']} x {prediction['away_score']} {prediction['away_team']}\n"
                
                message += "\n"
                
                message += f"🔮 <b>Predição:</b> {prediction['prediction']}\n"
                message += f"📊 <b>Confiança:</b> {prediction['confidence']:.1%}\n"
                message += f"🎯 <b>Confiabilidade:</b> {prediction['reliability']:.1%}\n\n"
                
                message += f"📈 <b>Probabilidades:</b>\n"
                message += f"🏠 Casa: {prediction['probabilities']['home_win']:.1%}\n"
                message += f"🤝 Empate: {prediction['probabilities']['draw']:.1%}\n"
                message += f"✈️ Fora: {prediction['probabilities']['away_win']:.1%}\n\n"
                
                message += f"💰 <b>Odds Calculadas:</b>\n"
                message += f"🏠 Casa: {prediction['odds']['home_win']:.2f}\n"
                message += f"🤝 Empate: {prediction['odds']['draw']:.2f}\n"
                message += f"✈️ Fora: {prediction['odds']['away_win']:.2f}\n\n"
                
                # Análise de valor
                home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
                draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
                away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
                
                message += f"💎 <b>Valor das Apostas:</b>\n"
                message += f"🏠 Casa: {home_value:.1%} {'✅' if home_value > 0.05 else '❌'}\n"
                message += f"🤝 Empate: {draw_value:.1%} {'✅' if draw_value > 0.05 else '❌'}\n"
                message += f"✈️ Fora: {away_value:.1%} {'✅' if away_value > 0.05 else '❌'}\n\n"
                
                message += "─" * 30 + "\n\n"
            
            if len(type_predictions) > 3:
                message += f"... e mais {len(type_predictions) - 3} partidas\n\n"
    
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
    
    message += f"📊 <b>RESUMO DAS PREDIÇÕES {category}:</b>\n"
    message += f"🔮 Predições: {len(predictions)}\n"
    message += f"📈 Confiança média: {avg_confidence:.1%}\n"
    message += f"🎯 Confiabilidade média: {avg_reliability:.1%}\n"
    message += f"💎 Apostas com valor: {positive_value_bets}/{len(predictions)}\n\n"
    
    # Estatísticas por tipo de competição
    types = {}
    for prediction in predictions:
        comp_type = prediction['type']
        types[comp_type] = types.get(comp_type, 0) + 1
    
    message += f"🌍 <b>COBERTURA POR TIPO DE COMPETIÇÃO:</b>\n"
    for comp_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        type_name = {
            'Club': 'Competições de Clubes', 
            'National': 'Competições Nacionais', 
            'League': 'Ligas Nacionais'
        }.get(comp_type, comp_type)
        emoji = emoji_map.get(comp_type, '⚽')
        message += f"   {emoji} {type_name}: {count} partidas\n"
    
    # Estatísticas por país/região
    countries = {}
    for prediction in predictions:
        country = prediction['country']
        countries[country] = countries.get(country, 0) + 1
    
    message += f"\n🌍 <b>COBERTURA POR PAÍS/REGIÃO:</b>\n"
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]:
        message += f"   {country}: {count} partidas\n"
    
    message += f"\n⏰ <b>IMPORTANTE:</b> Predições baseadas em dados reais\n"
    message += f"🌐 <b>COBERTURA:</b> Competições internacionais completas\n"
    message += f"🏆 <b>INCLUI:</b> Champions League, Europa League, Copa do Mundo, Copa América, CAN, Euro\n"
    message += f"⚠️ <b>AVISO:</b> Apostas envolvem risco. Use com responsabilidade.\n"
    message += f"🤖 <b>Powered by MaraBet AI</b> - Sistema de IA para Futebol"
    
    return message

def run_demo_with_telegram():
    """Executa demonstração com envio para Telegram"""
    print("🌍 SISTEMA AUTOMÁTICO COM TELEGRAM - MARABET AI")
    print("=" * 80)
    
    # Configurações do Telegram (exemplo - configure no .env)
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
    
    if not bot_token or not chat_id:
        print("⚠️ Configurações do Telegram não encontradas")
        print("💡 Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env")
        print("🔧 Ou execute: python setup_telegram_international.py")
        
        # Usar configurações de exemplo para demonstração
        print("\n🧪 EXECUTANDO DEMONSTRAÇÃO SEM TELEGRAM...")
        print("=" * 50)
        
        try:
            from demo_international_competitions import InternationalCompetitionsDemo
            demo = InternationalCompetitionsDemo()
            return demo.run_demo()
        except Exception as e:
            print(f"❌ Erro na demonstração: {e}")
            return False
    
    print(f"✅ Bot Token: {bot_token[:10]}...")
    print(f"✅ Chat ID: {chat_id}")
    
    try:
        # Importar o sistema internacional
        from international_competitions_system import InternationalCompetitionsSystem
        
        # Criar instância do sistema
        predictor = InternationalCompetitionsSystem()
        
        print("\n🚀 EXECUTANDO PREDIÇÕES INTERNACIONAIS COM TELEGRAM")
        print("=" * 60)
        
        # 1. Executar predições de hoje
        print("\n📅 EXECUTANDO PREDIÇÕES DE HOJE...")
        print("-" * 40)
        success_today = run_predictions_and_send(predictor, "today", "INTERNACIONAIS DE HOJE", bot_token, chat_id)
        
        # 2. Executar predições ao vivo
        print("\n🔴 EXECUTANDO PREDIÇÕES AO VIVO...")
        print("-" * 40)
        success_live = run_predictions_and_send(predictor, "live", "INTERNACIONAIS AO VIVO", bot_token, chat_id)
        
        # 3. Executar predições futuras
        print("\n🔮 EXECUTANDO PREDIÇÕES FUTURAS...")
        print("-" * 40)
        success_future = run_predictions_and_send(predictor, "future", "INTERNACIONAIS FUTURAS", bot_token, chat_id)
        
        # Resumo final
        print("\n🎯 RESUMO DA EXECUÇÃO COM TELEGRAM:")
        print("=" * 50)
        print(f"📅 Predições de hoje: {'✅ Sucesso' if success_today else '❌ Falhou'}")
        print(f"🔴 Predições ao vivo: {'✅ Sucesso' if success_live else '❌ Falhou'}")
        print(f"🔮 Predições futuras: {'✅ Sucesso' if success_future else '❌ Falhou'}")
        
        total_success = sum([success_today, success_live, success_future])
        print(f"\n📊 Total de execuções bem-sucedidas: {total_success}/3")
        
        if total_success > 0:
            print("\n🎉 SISTEMA AUTOMÁTICO COM TELEGRAM EXECUTADO COM SUCESSO!")
            print("🌍 Predições enviadas automaticamente para Telegram!")
        else:
            print("\n❌ Nenhuma execução foi bem-sucedida")
            print("🔍 Verifique a configuração da API e conexão com internet")
        
        return total_success > 0
        
    except ImportError as e:
        print(f"❌ Erro ao importar sistema internacional: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        return False

def run_predictions_and_send(predictor, mode, category, bot_token, chat_id):
    """Executa predições e envia para Telegram"""
    try:
        # Executar predições
        if mode == "today":
            matches = predictor.get_international_matches_today()
        elif mode == "live":
            matches = predictor.get_international_live_matches()
        elif mode == "future":
            matches = predictor.get_international_future_matches()
        else:
            return False
        
        if not matches:
            print(f"❌ Nenhuma partida {category.lower()} encontrada")
            return False
        
        print(f"📊 {len(matches)} partidas {category.lower()} encontradas")
        
        # Ordenar por prioridade da competição
        matches.sort(key=lambda x: x.get('competition_info', {}).get('priority', 3))
        
        # Gerar predições (limitado para não sobrecarregar)
        predictions = []
        for match in matches[:10]:  # Limitar a 10 partidas
            try:
                prediction = predictor.predict_match(match)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"   Erro ao predizer partida: {e}")
                continue
        
        if not predictions:
            print("❌ Nenhuma predição gerada")
            return False
        
        print(f"🔮 {len(predictions)} predições {category.lower()} geradas")
        
        # Formatar e enviar para Telegram
        message = format_telegram_message(predictions, category)
        
        # Dividir mensagem se muito longa (limite do Telegram: 4096 caracteres)
        if len(message) > 4000:
            # Enviar mensagem de cabeçalho
            header = f"🌍 <b>PREDIÇÕES {category} - MARABET AI</b> 🌍\n"
            header += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            header += f"🤖 Sistema de IA com dados reais da API Football\n"
            header += f"🌐 Cobertura: Competições internacionais completas\n\n"
            send_telegram_message(bot_token, chat_id, header)
            
            # Enviar resumo
            summary = f"📊 <b>RESUMO DAS PREDIÇÕES {category}:</b>\n"
            summary += f"🔮 Predições: {len(predictions)}\n"
            avg_confidence = sum(p['confidence'] for p in predictions) / len(predictions)
            summary += f"📈 Confiança média: {avg_confidence:.1%}\n"
            summary += f"🌍 Cobertura: Competições internacionais completas\n"
            summary += f"🏆 INCLUI: Champions League, Europa League, Copa do Mundo, Copa América, CAN, Euro\n"
            summary += f"🤖 <b>Powered by MaraBet AI</b> - Sistema de IA para Futebol"
            send_telegram_message(bot_token, chat_id, summary)
        else:
            send_telegram_message(bot_token, chat_id, message)
        
        print("📱 Predições enviadas para Telegram")
        return True
        
    except Exception as e:
        logger.error(f"   Erro ao executar predições {mode}: {e}")
        return False

def main():
    """Função principal"""
    return run_demo_with_telegram()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
