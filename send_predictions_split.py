#!/usr/bin/env python3
"""
Envio de Predições Dividido
MaraBet AI - Envia predições em partes menores para evitar limite do Telegram
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_telegram_config():
    """Carrega configurações do Telegram do .env"""
    load_dotenv()
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        logger.error("❌ Configurações do Telegram não encontradas no .env")
        return None, None
    
    return token, chat_id

def send_telegram_message(token, chat_id, message):
    """Envia mensagem para o Telegram"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                logger.info("✅ Mensagem enviada com sucesso!")
                return True
            else:
                logger.error(f"❌ Erro na API: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            logger.error(f"❌ Erro HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem: {e}")
        return False

def split_message(message, max_length=4000):
    """Divide mensagem em partes menores"""
    if len(message) <= max_length:
        return [message]
    
    parts = []
    current_part = ""
    lines = message.split('\n')
    
    for line in lines:
        if len(current_part + line + '\n') <= max_length:
            current_part += line + '\n'
        else:
            if current_part:
                parts.append(current_part.strip())
            current_part = line + '\n'
    
    if current_part:
        parts.append(current_part.strip())
    
    return parts

def format_predictions_for_telegram(predictions, category="INTERNACIONAIS"):
    """Formata predições para envio via Telegram"""
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
    message += f"🤖 Sistema de IA com dados simulados para demonstração\n"
    message += f"🌐 Cobertura: Competições internacionais completas\n"
    message += f"👤 Usuário: Mara Maravilha\n"
    message += f"🌍 Idioma: pt-br\n\n"
    
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
            message += f"{emoji} <b>{type_name}</b> - {len(type_predictions)} partidas:\n"
            message += "=" * 50 + "\n\n"
            
            for i, prediction in enumerate(type_predictions[:2], 1):  # Limitar a 2 por tipo
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
                
                message += "─" * 50 + "\n\n"
            
            if len(type_predictions) > 2:
                message += f"... e mais {len(type_predictions) - 2} partidas\n\n"
    
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
    
    message += f"\n⏰ <b>IMPORTANTE:</b> Predições baseadas em dados simulados\n"
    message += f"🌐 <b>COBERTURA:</b> Competições internacionais completas\n"
    message += f"🏆 <b>INCLUI:</b> Champions League, Europa League, Copa do Mundo, Copa América, CAN, Euro\n"
    message += f"📊 <b>DADOS:</b> Simulados para demonstração do conceito\n"
    message += f"⚠️ <b>AVISO:</b> Apostas envolvem risco. Use com responsabilidade.\n"
    message += f"🤖 <b>Powered by MaraBet AI</b> - Sistema de IA para Futebol"
    
    return message

def run_predictions_telegram_split():
    """Executa envio de predições via Telegram em partes"""
    print("🚀 ENVIO DE PREDIÇÕES VIA TELEGRAM (DIVIDIDO) - MARABET AI")
    print("=" * 70)
    
    # Carregar configurações
    token, chat_id = load_telegram_config()
    if not token or not chat_id:
        print("❌ Configurações do Telegram não encontradas")
        return False
    
    print(f"✅ Token: {token[:10]}...")
    print(f"✅ Chat ID: {chat_id}")
    
    try:
        # Importar o sistema de demonstração
        from demo_international_competitions import InternationalCompetitionsDemo
        
        # Criar instância do sistema
        demo = InternationalCompetitionsDemo()
        
        print("\n🚀 GERANDO PREDIÇÕES INTERNACIONAIS")
        print("=" * 50)
        
        # Gerar partidas internacionais
        international_matches = demo.generate_international_matches(8)
        
        print(f"📊 {len(international_matches)} partidas internacionais simuladas geradas")
        
        # Gerar predições
        predictions = []
        for match in international_matches:
            try:
                prediction = demo.predict_match(match)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"   Erro ao predizer partida: {e}")
                continue
        
        if not predictions:
            print("❌ Nenhuma predição gerada")
            return False
        
        print(f"🔮 {len(predictions)} predições internacionais geradas")
        
        # Formatar para Telegram
        message = format_predictions_for_telegram(predictions, "INTERNACIONAIS")
        
        # Dividir mensagem em partes
        message_parts = split_message(message, max_length=4000)
        
        print(f"\n📱 ENVIANDO PARA TELEGRAM ({len(message_parts)} partes)...")
        print("=" * 50)
        
        # Enviar cada parte
        success_count = 0
        for i, part in enumerate(message_parts, 1):
            print(f"📤 Enviando parte {i}/{len(message_parts)}...")
            success = send_telegram_message(token, chat_id, part)
            if success:
                success_count += 1
                print(f"✅ Parte {i} enviada com sucesso!")
            else:
                print(f"❌ Erro ao enviar parte {i}")
        
        if success_count == len(message_parts):
            print(f"\n🎉 TODAS AS PREDIÇÕES ENVIADAS COM SUCESSO!")
            print("=" * 50)
            print(f"✅ {success_count}/{len(message_parts)} partes enviadas")
            print("📱 Verifique se recebeu as mensagens no Telegram")
            print("🤖 Bot: @MaraBetV2Bot")
            print("👤 Usuário: Mara Maravilha")
            print("🌍 Idioma: pt-br")
            
            # Salvar predições localmente também
            try:
                with open('telegram_predictions_split.txt', 'w', encoding='utf-8') as f:
                    f.write(message)
                print("✅ Predições salvas em: telegram_predictions_split.txt")
            except Exception as e:
                print(f"❌ Erro ao salvar predições: {e}")
            
            return True
        else:
            print(f"\n⚠️ ENVIO PARCIAL: {success_count}/{len(message_parts)} partes enviadas")
            return False
        
    except ImportError as e:
        print(f"❌ Erro ao importar sistema: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        return False

def main():
    """Função principal"""
    return run_predictions_telegram_split()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
