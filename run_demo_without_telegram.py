#!/usr/bin/env python3
"""
Demonstração sem Telegram
MaraBet AI - Executa predições sem envio para Telegram
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

def format_predictions_output(predictions, category="INTERNACIONAIS"):
    """Formata saída das predições para demonstração"""
    if not predictions:
        return f"❌ Nenhuma partida {category.lower()} encontrada."
    
    # Emoji para o tipo de competição
    emoji_map = {
        'Club': '🏆',
        'National': '🌍',
        'League': '⚽'
    }
    
    output = f"🌍 PREDIÇÕES {category} - MARABET AI 🌍\n"
    output += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    output += f"🤖 Sistema de IA com dados simulados para demonstração\n"
    output += f"🌐 Cobertura: Competições internacionais completas\n"
    output += f"👤 Usuário: Mara Maravilha\n"
    output += f"🌍 Idioma: pt-br\n\n"
    
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
            output += f"{emoji} {type_name} - {len(type_predictions)} partidas:\n"
            output += "=" * 50 + "\n\n"
            
            for i, prediction in enumerate(type_predictions[:3], 1):  # Limitar a 3 por tipo
                output += f"⚽ Partida {i}:\n"
                output += f"⚔️ {prediction['home_team']} vs {prediction['away_team']}\n"
                output += f"📅 {prediction['date_formatted']}\n"
                output += f"🏆 {prediction['competition']} ({prediction['country']})\n"
                output += f"📊 Status: {prediction['status_name']}\n"
                output += f"🎯 Tier: {prediction['tier']}\n"
                
                if prediction['status'] in ['1H', '2H', 'HT', 'LIVE']:
                    output += f"⚽ Placar: {prediction['home_team']} {prediction['home_score']} x {prediction['away_score']} {prediction['away_team']}\n"
                
                output += "\n"
                
                output += f"🔮 Predição: {prediction['prediction']}\n"
                output += f"📊 Confiança: {prediction['confidence']:.1%}\n"
                output += f"🎯 Confiabilidade: {prediction['reliability']:.1%}\n\n"
                
                output += f"📈 Probabilidades:\n"
                output += f"🏠 Casa: {prediction['probabilities']['home_win']:.1%}\n"
                output += f"🤝 Empate: {prediction['probabilities']['draw']:.1%}\n"
                output += f"✈️ Fora: {prediction['probabilities']['away_win']:.1%}\n\n"
                
                output += f"💰 Odds Calculadas:\n"
                output += f"🏠 Casa: {prediction['odds']['home_win']:.2f}\n"
                output += f"🤝 Empate: {prediction['odds']['draw']:.2f}\n"
                output += f"✈️ Fora: {prediction['odds']['away_win']:.2f}\n\n"
                
                # Análise de valor
                home_value = (prediction['probabilities']['home_win'] * prediction['odds']['home_win']) - 1
                draw_value = (prediction['probabilities']['draw'] * prediction['odds']['draw']) - 1
                away_value = (prediction['probabilities']['away_win'] * prediction['odds']['away_win']) - 1
                
                output += f"💎 Valor das Apostas:\n"
                output += f"🏠 Casa: {home_value:.1%} {'✅' if home_value > 0.05 else '❌'}\n"
                output += f"🤝 Empate: {draw_value:.1%} {'✅' if draw_value > 0.05 else '❌'}\n"
                output += f"✈️ Fora: {away_value:.1%} {'✅' if away_value > 0.05 else '❌'}\n\n"
                
                output += "─" * 50 + "\n\n"
            
            if len(type_predictions) > 3:
                output += f"... e mais {len(type_predictions) - 3} partidas\n\n"
    
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
    
    output += f"📊 RESUMO DAS PREDIÇÕES {category}:\n"
    output += f"🔮 Predições: {len(predictions)}\n"
    output += f"📈 Confiança média: {avg_confidence:.1%}\n"
    output += f"🎯 Confiabilidade média: {avg_reliability:.1%}\n"
    output += f"💎 Apostas com valor: {positive_value_bets}/{len(predictions)}\n\n"
    
    # Estatísticas por tipo de competição
    types = {}
    for prediction in predictions:
        comp_type = prediction['type']
        types[comp_type] = types.get(comp_type, 0) + 1
    
    output += f"🌍 COBERTURA POR TIPO DE COMPETIÇÃO:\n"
    for comp_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        type_name = {
            'Club': 'Competições de Clubes', 
            'National': 'Competições Nacionais', 
            'League': 'Ligas Nacionais'
        }.get(comp_type, comp_type)
        emoji = emoji_map.get(comp_type, '⚽')
        output += f"   {emoji} {type_name}: {count} partidas\n"
    
    # Estatísticas por país/região
    countries = {}
    for prediction in predictions:
        country = prediction['country']
        countries[country] = countries.get(country, 0) + 1
    
    output += f"\n🌍 COBERTURA POR PAÍS/REGIÃO:\n"
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]:
        output += f"   {country}: {count} partidas\n"
    
    output += f"\n⏰ IMPORTANTE: Predições baseadas em dados simulados\n"
    output += f"🌐 COBERTURA: Competições internacionais completas\n"
    output += f"🏆 INCLUI: Champions League, Europa League, Copa do Mundo, Copa América, CAN, Euro\n"
    output += f"📊 DADOS: Simulados para demonstração do conceito\n"
    output += f"⚠️ AVISO: Apostas envolvem risco. Use com responsabilidade.\n"
    output += f"🤖 Powered by MaraBet AI - Sistema de IA para Futebol"
    
    return output

def run_demo_without_telegram():
    """Executa demonstração sem Telegram"""
    print("🌍 DEMONSTRAÇÃO SEM TELEGRAM - MARABET AI")
    print("=" * 60)
    print("👤 Usuário: Mara Maravilha")
    print("🌍 Idioma: pt-br")
    print("📅 Data: " + datetime.now().strftime('%d/%m/%Y %H:%M'))
    
    try:
        # Importar o sistema de demonstração
        from demo_international_competitions import InternationalCompetitionsDemo
        
        # Criar instância do sistema
        demo = InternationalCompetitionsDemo()
        
        print("\n🚀 EXECUTANDO PREDIÇÕES INTERNACIONAIS")
        print("=" * 50)
        
        # Gerar partidas internacionais
        international_matches = demo.generate_international_matches(20)
        
        print(f"📊 {len(international_matches)} partidas internacionais simuladas geradas")
        
        # Mostrar distribuição por tipo de competição
        type_counts = {}
        for match in international_matches:
            comp_type = match['competition_info']['type']
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
        
        print("\n📊 DISTRIBUIÇÃO POR TIPO DE COMPETIÇÃO:")
        for comp_type, count in type_counts.items():
            type_name = {'Club': 'Competições de Clubes', 'National': 'Competições Nacionais', 'League': 'Ligas Nacionais'}.get(comp_type, comp_type)
            print(f"   {type_name}: {count} partidas")
        
        # Mostrar distribuição por status
        status_counts = {}
        for match in international_matches:
            status = match['fixture']['status']['short']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("\n📊 DISTRIBUIÇÃO POR STATUS:")
        for status, count in status_counts.items():
            status_name = demo.match_statuses.get(status, status)
            print(f"   {status_name}: {count} partidas")
        
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
        
        # Mostrar predições formatadas
        output = format_predictions_output(predictions, "INTERNACIONAIS")
        print("\n" + output)
        
        # Salvar predições
        try:
            with open('international_predictions_demo.txt', 'w', encoding='utf-8') as f:
                f.write(output)
            print("\n✅ Predições salvas em: international_predictions_demo.txt")
        except Exception as e:
            print(f"\n❌ Erro ao salvar predições: {e}")
        
        # Mostrar características do sistema
        print("\n🌍 CARACTERÍSTICAS DO SISTEMA INTERNACIONAL:")
        print("=" * 60)
        
        features = [
            "✅ Cobertura completa de competições internacionais",
            "✅ COMPETIÇÕES EUROPEIAS: Champions League, Europa League, Conference League",
            "✅ COMPETIÇÕES INTERNACIONAIS: Copa do Mundo, Copa América, CAN, Euro",
            "✅ LIGAS NACIONAIS: Premier League, La Liga, Bundesliga, Serie A, Ligue 1",
            "✅ Predições para partidas ao vivo e futuras",
            "✅ Análise de forma dos times",
            "✅ Fator casa ajustado por tipo de competição",
            "✅ Cálculo de probabilidades e odds",
            "✅ Identificação de valor nas apostas",
            "✅ Status das partidas em tempo real",
            "✅ Sistema robusto e escalável",
            "✅ Foco em partidas futuras e ao vivo",
            "✅ Cobertura global não limitada ao Brasil"
        ]
        
        for feature in features:
            print(f"   {feature}")
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        print("=" * 30)
        print("✅ Sistema funcionando perfeitamente")
        print("✅ Predições geradas com sucesso")
        print("✅ Cobertura global implementada")
        print("\n💡 Para receber no Telegram:")
        print("   1. Configure um bot válido no Telegram")
        print("   2. Execute: python run_telegram_auto.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar sistema: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        return False

def main():
    """Função principal"""
    return run_demo_without_telegram()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
