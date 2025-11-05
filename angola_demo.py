#!/usr/bin/env python3
"""
Demonstração do Sistema MaraBet AI - Mercado Angolano
Mostra configuração completa para Kwanza Angolano (AOA)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from angola.currency_converter import AngolaCurrencyConverter
from angola.angola_config import AngolaMarketConfig
import json

def main():
    """Demonstração completa do sistema angolano"""
    print("🇦🇴 MARABET AI - SISTEMA ANGOANO")
    print("=" * 50)
    print()
    
    try:
        # 1. Configuração do Mercado Angolano
        print("📋 1. CONFIGURAÇÃO DO MERCADO ANGOANO")
        print("-" * 40)
        
        market_config = AngolaMarketConfig()
        market_info = market_config.get_market_info()
        
        print(f"País: {market_info.get('country')}")
        print(f"Moeda: {market_info.get('currency')}")
        print(f"Fuso Horário: {market_info.get('timezone')}")
        print(f"Idioma: {market_info.get('language')}")
        print(f"Formato de Data: {market_info.get('date_format')}")
        print()
        
        # 2. Casas de Apostas Angolanas
        print("🏢 2. CASAS DE APOSTAS ANGOANAS")
        print("-" * 40)
        
        bookmakers = market_config.get_active_bookmakers()
        for i, bookmaker in enumerate(bookmakers, 1):
            print(f"{i}. {bookmaker.name} ({bookmaker.code})")
            print(f"   Website: {bookmaker.website}")
            print(f"   Moedas: {', '.join(bookmaker.supported_currencies)}")
            print(f"   Aposta mínima: {market_config.format_currency(bookmaker.min_bet)}")
            print(f"   Aposta máxima: {market_config.format_currency(bookmaker.max_bet)}")
            print(f"   Taxa de comissão: {bookmaker.commission_rate:.1%}")
            print()
        
        # 3. Ligas Prioritárias
        print("⚽ 3. LIGAS PRIORITÁRIAS")
        print("-" * 40)
        
        priority_leagues = market_config.get_priority_leagues(8)
        for i, league in enumerate(priority_leagues, 1):
            print(f"{i}. {league.name} ({league.country}) - Prioridade {league.priority}")
        print()
        
        # 4. Conversão de Moedas
        print("💱 4. SISTEMA DE CONVERSÃO DE MOEDAS")
        print("-" * 40)
        
        currency_converter = AngolaCurrencyConverter()
        
        # Exemplos de conversão
        test_amounts = [100, 500, 1000, 5000]
        currencies = ["USD", "EUR", "GBP", "BRL"]
        
        print("Conversões para Kwanza Angolano (AOA):")
        for currency in currencies:
            print(f"\n{currency} para AOA:")
            for amount in test_amounts:
                aoa_amount = currency_converter.convert_to_aoa(amount, currency)
                if aoa_amount:
                    formatted = currency_converter.format_currency(aoa_amount, "AOA")
                    print(f"  {amount} {currency} = {formatted}")
        print()
        
        # 5. Preços em AOA
        print("💰 5. PREÇOS EM KWANZA ANGOANO")
        print("-" * 40)
        
        pricing = market_config.get_pricing()
        for key, price_info in pricing.items():
            aoa_price = price_info['aoa']
            usd_price = price_info['usd']
            formatted_aoa = market_config.format_currency(aoa_price)
            print(f"• {price_info['description']}: {formatted_aoa} (~${usd_price} USD)")
        print()
        
        # 6. Exemplo de Relatório em AOA
        print("📊 6. EXEMPLO DE RELATÓRIO EM AOA")
        print("-" * 40)
        
        # Dados de exemplo
        sample_data = {
            'period_start': '2024-01-01',
            'period_end': '2024-12-31',
            'bets': [
                {
                    'date': '2024-01-15',
                    'league': 'Premier League',
                    'home_team': 'Arsenal',
                    'away_team': 'Chelsea',
                    'bet_type': '1X2',
                    'selection': '1',
                    'odds': 2.10,
                    'stake': 1000.0,  # 1000 AOA
                    'result': 'win',
                    'profit': 1100.0  # 1100 AOA
                },
                {
                    'date': '2024-01-16',
                    'league': 'La Liga',
                    'home_team': 'Real Madrid',
                    'away_team': 'Barcelona',
                    'bet_type': '1X2',
                    'selection': 'X',
                    'odds': 3.50,
                    'stake': 500.0,  # 500 AOA
                    'result': 'loss',
                    'profit': -500.0  # -500 AOA
                }
            ]
        }
        
        # Calcular métricas
        total_bets = len(sample_data['bets'])
        winning_bets = len([b for b in sample_data['bets'] if b['result'] == 'win'])
        total_stake = sum(b['stake'] for b in sample_data['bets'])
        total_profit = sum(b['profit'] for b in sample_data['bets'])
        win_rate = (winning_bets / total_bets) * 100
        roi = (total_profit / total_stake) * 100 if total_stake > 0 else 0
        
        print(f"Total de apostas: {total_bets}")
        print(f"Taxa de acerto: {win_rate:.1f}%")
        print(f"Stake total: {market_config.format_currency(total_stake)}")
        print(f"Lucro total: {market_config.format_currency(total_profit)}")
        print(f"ROI: {roi:.2f}%")
        print()
        
        # 7. Informações de Contato
        print("📞 7. INFORMAÇÕES DE CONTATO")
        print("-" * 40)
        
        contact_info = market_config.get_contact_info()
        print(f"Empresa: {contact_info.get('company_name')} - Proprietária da MaraBet AI")
        print(f"Endereço: {contact_info.get('address')}")
        print(f"Telemóvel: {contact_info.get('phone')}")
        print(f"Email: {contact_info.get('email')}")
        print(f"Website: {contact_info.get('website')}")
        print(f"WhatsApp: {contact_info.get('whatsapp')}")
        print()
        
        # 8. Resumo do Sistema
        print("🎯 8. RESUMO DO SISTEMA ANGOANO")
        print("-" * 40)
        
        print("✅ Sistema totalmente adaptado para Angola:")
        print("  • Moeda: Kwanza Angolano (AOA)")
        print("  • Casas de apostas: 6 integradas")
        print("  • Ligas: 14 prioritárias")
        print("  • Conversão automática de moedas")
        print("  • Formatação local angolana")
        print("  • Preços em AOA")
        print("  • Suporte local")
        print()
        
        print("🚀 O MaraBet AI está pronto para o mercado angolano!")
        print("   Sistema profissional com foco em Kwanza Angolano")
        print("   Integração completa com casas de apostas locais")
        print("   Preços adaptados para o mercado angolano")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
