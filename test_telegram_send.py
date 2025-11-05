#!/usr/bin/env python3
"""
Teste de Envio para Telegram
MaraBet AI - Testa e corrige problemas de envio
"""

import os
import requests
import json
from dotenv import load_dotenv

def load_telegram_config():
    """Carrega configurações do Telegram do .env"""
    load_dotenv()
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("❌ Configurações do Telegram não encontradas no .env")
        return None, None
    
    return token, chat_id

def test_telegram_connection(token, chat_id):
    """Testa conexão com Telegram"""
    try:
        # Testar getMe
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Bot conectado: {bot_info.get('first_name', 'N/A')}")
                print(f"   Username: @{bot_info.get('username', 'N/A')}")
                return True
            else:
                print(f"❌ Erro na API: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def send_simple_message(token, chat_id):
    """Envia mensagem simples para testar"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': "🧪 <b>Teste de Conexão - MaraBet AI</b>\n\n✅ Bot funcionando perfeitamente!\n👤 Usuário: Mara Maravilha\n🌍 Idioma: pt-br\n📅 " + "21/10/2025 19:24",
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print("✅ Mensagem de teste enviada com sucesso!")
                return True
            else:
                print(f"❌ Erro na API: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False

def send_long_message(token, chat_id):
    """Envia mensagem longa para testar limites"""
    try:
        # Mensagem longa simulada
        long_message = "🌍 <b>PREDIÇÕES INTERNACIONAIS - MARABET AI</b> 🌍\n"
        long_message += "📅 21/10/2025 19:24\n"
        long_message += "🤖 Sistema de IA com dados simulados para demonstração\n"
        long_message += "🌐 Cobertura: Competições internacionais completas\n"
        long_message += "👤 Usuário: Mara Maravilha\n"
        long_message += "🌍 Idioma: pt-br\n\n"
        
        # Adicionar partidas simuladas
        for i in range(5):
            long_message += f"⚽ <b>Partida {i+1}:</b>\n"
            long_message += f"⚔️ Time A vs Time B\n"
            long_message += f"📅 21/10 20:00\n"
            long_message += f"🏆 Competição Teste\n"
            long_message += f"📊 Status: Não Iniciada\n"
            long_message += f"🎯 Tier: Tier 1\n\n"
            long_message += f"🔮 <b>Predição:</b> Casa\n"
            long_message += f"📊 <b>Confiança:</b> 75.0%\n"
            long_message += f"🎯 <b>Confiabilidade:</b> 100.0%\n\n"
            long_message += f"📈 <b>Probabilidades:</b>\n"
            long_message += f"🏠 Casa: 75.0%\n"
            long_message += f"🤝 Empate: 15.0%\n"
            long_message += f"✈️ Fora: 10.0%\n\n"
            long_message += f"💰 <b>Odds Calculadas:</b>\n"
            long_message += f"🏠 Casa: 1.33\n"
            long_message += f"🤝 Empate: 6.67\n"
            long_message += f"✈️ Fora: 10.00\n\n"
            long_message += "─" * 50 + "\n\n"
        
        long_message += "📊 <b>RESUMO DAS PREDIÇÕES:</b>\n"
        long_message += "🔮 Predições: 5\n"
        long_message += "📈 Confiança média: 75.0%\n"
        long_message += "🎯 Confiabilidade média: 100.0%\n"
        long_message += "💎 Apostas com valor: 0/5\n\n"
        long_message += "⏰ <b>IMPORTANTE:</b> Predições baseadas em dados simulados\n"
        long_message += "🌐 <b>COBERTURA:</b> Competições internacionais completas\n"
        long_message += "🏆 <b>INCLUI:</b> Champions League, Europa League, Copa do Mundo, Copa América, CAN, Euro\n"
        long_message += "📊 <b>DADOS:</b> Simulados para demonstração do conceito\n"
        long_message += "⚠️ <b>AVISO:</b> Apostas envolvem risco. Use com responsabilidade.\n"
        long_message += "🤖 <b>Powered by MaraBet AI</b> - Sistema de IA para Futebol"
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': long_message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print("✅ Mensagem longa enviada com sucesso!")
                return True
            else:
                print(f"❌ Erro na API: {data.get('description', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem longa: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DE ENVIO PARA TELEGRAM - MARABET AI")
    print("=" * 60)
    
    # Carregar configurações
    token, chat_id = load_telegram_config()
    if not token or not chat_id:
        print("❌ Configurações do Telegram não encontradas")
        return False
    
    print(f"✅ Token: {token[:10]}...")
    print(f"✅ Chat ID: {chat_id}")
    
    # Testar conexão
    print(f"\n🔌 TESTANDO CONEXÃO...")
    print("-" * 30)
    if not test_telegram_connection(token, chat_id):
        print("❌ Falha na conexão")
        return False
    
    # Testar mensagem simples
    print(f"\n📱 TESTANDO MENSAGEM SIMPLES...")
    print("-" * 30)
    if not send_simple_message(token, chat_id):
        print("❌ Falha no envio simples")
        return False
    
    # Testar mensagem longa
    print(f"\n📱 TESTANDO MENSAGEM LONGA...")
    print("-" * 30)
    if not send_long_message(token, chat_id):
        print("❌ Falha no envio longo")
        return False
    
    print(f"\n🎉 TODOS OS TESTES PASSARAM!")
    print("=" * 40)
    print("✅ Conexão funcionando")
    print("✅ Mensagem simples enviada")
    print("✅ Mensagem longa enviada")
    print("📱 Verifique se recebeu as mensagens no Telegram")
    print("🤖 Bot: @MaraBetV2Bot")
    print("👤 Usuário: Mara Maravilha")
    print("🌍 Idioma: pt-br")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
