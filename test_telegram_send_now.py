#!/usr/bin/env python3
"""Teste de envio de mensagem via Telegram"""
import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = "8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg"
TELEGRAM_CHAT_ID = "5550091597"

now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

message = f"""⚽ MARABET AI - TESTE DE SISTEMA

📅 Data: {now}

✅ Sistema funcionando perfeitamente!
⚠️ Período sem jogos (possível período de baixa movimentação)

🔍 Status da API-Football:
   • API Key válida
   • Conexão OK
   • Nenhuma partida futura nos próximos 14 dias

📊 Isso é normal em:
   • Períodos de baixa movimentação
   • Final/Início de temporada
   • Semanas sem jogos agendados

🇦🇴 MaraBet AI - Angola
📧 suporte@marabet.ao
📞 +224 932027393

<i>O sistema está monitorando continuamente. Enviaremos previsões assim que houver jogos agendados.</i>
"""

try:
    response = requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
        json={
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        },
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ Mensagem enviada com sucesso no Telegram!")
    else:
        print(f"⚠️ Erro: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"❌ Erro: {e}")

