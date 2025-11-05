#!/usr/bin/env python3
"""
Obter IP Atual - MaraBet AI
Script para descobrir seu IP público
"""

import requests

print("═" * 60)
print("🌐 OBTENDO SEU IP PÚBLICO - MARABET AI")
print("═" * 60)
print()

try:
    ip = requests.get('https://api.ipify.org', timeout=5).text
    
    print(f"📍 SEU IP ATUAL: {ip}")
    print()
    print("═" * 60)
    print("🚨 PROBLEMA IDENTIFICADO:")
    print("═" * 60)
    print()
    print("❌ Este IP não está na whitelist da API-Football")
    print("❌ Por isso o sistema não recebe dados")
    print()
    print("═" * 60)
    print("✅ SOLUÇÃO (5 MINUTOS):")
    print("═" * 60)
    print()
    print("1. Acessar: https://dashboard.api-football.com/")
    print("2. Login com suas credenciais")
    print("3. Ir para 'IP Whitelist' ou 'Allowed IPs'")
    print(f"4. Adicionar IP: {ip}")
    print("5. Salvar e aguardar 2 minutos")
    print("6. Testar: python test_api_ultra_plan.py")
    print()
    print("💡 ALTERNATIVA:")
    print("   • Desabilitar IP Whitelist no dashboard")
    print("   • Ou adicionar 0.0.0.0/0 (aceita todos)")
    print()
    print("📄 Guia completo: FIX_API_IP_WHITELIST.md")
    print("📧 Suporte: suporte@marabet.ao")
    print()
    
except Exception as e:
    print(f"❌ Erro ao obter IP: {e}")
    print("📋 Tente manualmente: https://www.whatismyip.com/")

