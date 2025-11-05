#!/usr/bin/env python3
"""
Script para testar o sistema de notificações do MaraBet AI
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Adiciona o diretório pai ao sys.path para permitir importações relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from notifications.notification_integrator import (
    notification_integrator, test_notifications, get_notification_stats
)
from settings.settings import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SMTP_USERNAME, SMTP_PASSWORD
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_notification_system():
    """Testa o sistema completo de notificações"""
    print("🔔 MARABET AI - TESTE DO SISTEMA DE NOTIFICAÇÕES")
    print("=" * 60)
    
    # Verificar configuração
    print("\n📋 Verificando configuração...")
    
    telegram_configured = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    email_configured = bool(SMTP_USERNAME and SMTP_PASSWORD)
    
    print(f"📱 Telegram: {'✅ Configurado' if telegram_configured else '❌ Não configurado'}")
    print(f"📧 Email: {'✅ Configurado' if email_configured else '❌ Não configurado'}")
    
    if not telegram_configured and not email_configured:
        print("\n⚠️  AVISO: Nenhum canal de notificação configurado!")
        print("Para testar notificações reais:")
        print("1. Configure Telegram ou Email no arquivo .env")
        print("2. Execute este teste novamente")
        print("\nContinuando com testes básicos...")
    
    # Testar inicialização
    print("\n🔧 TESTE DE INICIALIZAÇÃO")
    print("=" * 40)
    
    try:
        stats = get_notification_stats()
        print("✅ Sistema de notificações inicializado")
        print(f"   Ativado: {stats['enabled']}")
        print(f"   Telegram: {stats['telegram_enabled']}")
        print(f"   Email: {stats['email_enabled']}")
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return False
    
    # Testar notificações individuais
    print("\n📤 TESTE DE NOTIFICAÇÕES INDIVIDUAIS")
    print("=" * 40)
    
    # Dados de teste
    test_prediction = {
        'fixture_id': 12345,
        'market': 'h2h',
        'selection': 'Home',
        'expected_value': 0.08,
        'confidence': 0.75,
        'stake_percentage': 0.03,
        'recommended': True,
        'match': {
            'home_team': 'Manchester City',
            'away_team': 'Arsenal',
            'league': 'Premier League'
        }
    }
    
    test_status = {
        'running': True,
        'total_matches': 150,
        'total_predictions': 25,
        'recommended_predictions': 8,
        'next_execution': '2025-10-14 19:00:00'
    }
    
    test_performance = {
        'total_predictions': 25,
        'average_ev': 0.06,
        'average_confidence': 0.78,
        'success_rate': 0.68
    }
    
    # Testar cada tipo de notificação
    results = {}
    
    # Teste de predição
    try:
        print("🔮 Testando notificação de predição...")
        result = await notification_integrator.notify_prediction(test_prediction)
        results['prediction'] = result
        print(f"   Resultado: {'✅ Enviada' if result else '❌ Falhou'}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        results['prediction'] = False
    
    # Teste de status
    try:
        print("🤖 Testando notificação de status...")
        result = await notification_integrator.notify_system_status(test_status)
        results['status'] = result
        print(f"   Resultado: {'✅ Enviada' if result else '❌ Falhou'}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        results['status'] = False
    
    # Teste de performance
    try:
        print("📊 Testando notificação de performance...")
        result = await notification_integrator.notify_performance(test_performance)
        results['performance'] = result
        print(f"   Resultado: {'✅ Enviada' if result else '❌ Falhou'}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        results['performance'] = False
    
    # Teste de erro
    try:
        print("❌ Testando notificação de erro...")
        result = await notification_integrator.notify_error(
            "Teste de erro do sistema",
            {"error_type": "test", "timestamp": datetime.now().isoformat()}
        )
        results['error'] = result
        print(f"   Resultado: {'✅ Enviada' if result else '❌ Falhou'}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        results['error'] = False
    
    # Teste de relatório diário
    try:
        print("📈 Testando relatório diário...")
        report_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_predictions': 25,
            'successful_predictions': 17,
            'total_ev': 1.5,
            'best_prediction': test_prediction
        }
        result = await notification_integrator.notify_daily_report(report_data)
        results['daily_report'] = result
        print(f"   Resultado: {'✅ Enviada' if result else '❌ Falhou'}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        results['daily_report'] = False
    
    # Teste de cooldown
    print("\n⏰ TESTE DE COOLDOWN")
    print("=" * 40)
    
    try:
        # Tentar enviar a mesma predição novamente
        print("🔮 Testando cooldown de predição...")
        result1 = await notification_integrator.notify_prediction(test_prediction)
        result2 = await notification_integrator.notify_prediction(test_prediction)
        
        print(f"   Primeira tentativa: {'✅ Enviada' if result1 else '❌ Falhou'}")
        print(f"   Segunda tentativa: {'✅ Enviada' if result2 else '❌ Bloqueada (cooldown)'}")
        
        if result1 and not result2:
            print("   ✅ Cooldown funcionando corretamente")
        else:
            print("   ⚠️  Cooldown pode não estar funcionando")
    except Exception as e:
        print(f"   ❌ Erro no teste de cooldown: {e}")
    
    # Teste de critérios de notificação
    print("\n🎯 TESTE DE CRITÉRIOS DE NOTIFICAÇÃO")
    print("=" * 40)
    
    try:
        # Predição com EV baixo (não deve notificar)
        low_ev_prediction = test_prediction.copy()
        low_ev_prediction['expected_value'] = 0.02  # 2% EV
        
        print("🔮 Testando predição com EV baixo...")
        result = await notification_integrator.notify_prediction(low_ev_prediction)
        print(f"   Resultado: {'✅ Enviada' if result else '❌ Bloqueada (EV baixo)'}")
        
        # Predição com confiança baixa (não deve notificar)
        low_conf_prediction = test_prediction.copy()
        low_conf_prediction['confidence'] = 0.50  # 50% confiança
        
        print("🔮 Testando predição com confiança baixa...")
        result = await notification_integrator.notify_prediction(low_conf_prediction)
        print(f"   Resultado: {'✅ Enviada' if result else '❌ Bloqueada (confiança baixa)'}")
        
        # Predição não recomendada (não deve notificar)
        not_recommended_prediction = test_prediction.copy()
        not_recommended_prediction['recommended'] = False
        
        print("🔮 Testando predição não recomendada...")
        result = await notification_integrator.notify_prediction(not_recommended_prediction)
        print(f"   Resultado: {'✅ Enviada' if result else '❌ Bloqueada (não recomendada)'}")
        
    except Exception as e:
        print(f"   ❌ Erro no teste de critérios: {e}")
    
    # Teste de canais específicos
    if telegram_configured or email_configured:
        print("\n📡 TESTE DE CANAIS ESPECÍFICOS")
        print("=" * 40)
        
        channels = []
        if telegram_configured:
            channels.append('telegram')
        if email_configured:
            channels.append('email')
        
        try:
            print(f"📤 Testando canais: {', '.join(channels)}")
            result = await test_notifications(channels)
            
            for channel, success in result.items():
                print(f"   {channel}: {'✅ Sucesso' if success else '❌ Falhou'}")
        except Exception as e:
            print(f"   ❌ Erro no teste de canais: {e}")
    
    # Estatísticas finais
    print("\n📊 ESTATÍSTICAS FINAIS")
    print("=" * 40)
    
    try:
        stats = get_notification_stats()
        print(f"✅ Sistema ativado: {stats['enabled']}")
        print(f"📱 Telegram: {stats['telegram_enabled']}")
        print(f"📧 Email: {stats['email_enabled']}")
        print(f"🔮 Predições enviadas: {stats['prediction_count']}")
        print(f"❌ Erros notificados: {stats['error_count']}")
        print(f"⏰ Entradas de cooldown: {stats['cooldown_entries']}")
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
    
    # Resultado final
    success_count = sum(results.values())
    total_tests = len(results)
    
    print(f"\n📊 RESULTADO FINAL")
    print("=" * 30)
    print(f"Testes aprovados: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 Todos os testes passaram!")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
    
    if not telegram_configured and not email_configured:
        print("\n💡 DICAS PARA CONFIGURAR NOTIFICAÇÕES:")
        print("1. Telegram:")
        print("   - Crie um bot com @BotFather")
        print("   - Obtenha o token do bot")
        print("   - Obtenha seu chat_id")
        print("   - Configure no .env")
        print("2. Email:")
        print("   - Configure SMTP (Gmail, Outlook, etc.)")
        print("   - Use senha de app para Gmail")
        print("   - Configure no .env")
    
    return success_count == total_tests

async def main():
    """Função principal"""
    try:
        success = await test_notification_system()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Erro fatal no teste: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
