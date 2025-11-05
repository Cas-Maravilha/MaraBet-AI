# 📱 Guia de Envio Automático Telegram - MaraBet AI

**Data**: 24/10/2025  
**Versão**: 2.0  
**Contato**: +224 932027393

---

## ✅ CONFIGURAÇÃO ATUAL

### **Telegram Configurado:**
- ✅ Bot Token: `7646701850:AAGuBMODMggvyWt54Uh8AV7Vt4_DGm47va0`
- ✅ Chat ID: `5550091597`
- ✅ Status: Ativo e funcionando

---

## 🚀 USAR O SISTEMA AUTOMÁTICO

### **Método 1: Envio Manual Imediato**

```bash
# Enviar previsões de hoje agora
python send_today_predictions_telegram.py
```

**Resultado:**
- Busca partidas de hoje
- Gera previsões com IA
- Envia para Telegram
- Tempo: ~10 segundos

---

### **Método 2: Agendador Automático** ⭐ (Recomendado)

```bash
# Iniciar agendador (roda em background)
python telegram_auto_scheduler.py
```

**Horários de Envio Automático:**
- 🌅 **08:00** - Previsões matinais
- ☀️ **14:00** - Previsões da tarde  
- 🌙 **20:00** - Previsões da noite

**Funciona:**
- ✅ Envia automaticamente 3x ao dia
- ✅ Busca partidas em tempo real
- ✅ Gera previsões com IA
- ✅ Salva logs em `logs/telegram_scheduler.log`

---

### **Método 3: Sistema de Produção** (Servidor)

No servidor Angoweb, configurar como serviço:

```bash
# Criar arquivo de serviço systemd
sudo nano /etc/systemd/system/marabet-telegram.service
```

```ini
[Unit]
Description=MaraBet AI - Telegram Auto Predictions
After=network.target docker.service

[Service]
Type=simple
User=marabet
WorkingDirectory=/opt/marabet
ExecStart=/usr/bin/python3 /opt/marabet/telegram_auto_scheduler.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/marabet/logs/telegram_service.log
StandardError=append:/opt/marabet/logs/telegram_error.log

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar serviço
sudo systemctl daemon-reload
sudo systemctl enable marabet-telegram
sudo systemctl start marabet-telegram

# Verificar status
sudo systemctl status marabet-telegram

# Ver logs
sudo journalctl -u marabet-telegram -f
```

---

## 📋 SCRIPTS DISPONÍVEIS

### **1. `send_today_predictions_telegram.py`**
**Uso:** Envio manual de previsões de hoje
```bash
python send_today_predictions_telegram.py
```
**Características:**
- ✅ Busca partidas de hoje (8 ligas principais)
- ✅ Gera previsões com IA
- ✅ Envia para Telegram formatado
- ✅ Mostra confiança e odds

### **2. `telegram_auto_scheduler.py`** ⭐
**Uso:** Agendador automático (3x ao dia)
```bash
python telegram_auto_scheduler.py
```
**Características:**
- ✅ Roda continuamente
- ✅ Envia às 08:00, 14:00, 20:00
- ✅ Logs detalhados
- ✅ Reinício automático em caso de erro

### **3. `auto_telegram_predictions.py`**
**Uso:** Sistema avançado com scheduler
```bash
python auto_telegram_predictions.py
```
**Características:**
- ✅ Previsões futuras (7 dias)
- ✅ Verificação a cada 6 horas
- ✅ Limite de 5 previsões por envio
- ✅ Controle de envios duplicados

---

## ⚙️ CONFIGURAÇÃO

### **Arquivo: `telegram_config.json`**

```json
{
  "telegram_bot_token": "7646701850:AAGuBMODMggvyWt54Uh8AV7Vt4_DGm47va0",
  "telegram_chat_id": "5550091597",
  "created_at": "2025-10-22T16:20:00",
  "status": "configured"
}
```

### **Variáveis de Ambiente (.env):**

```bash
# Telegram
TELEGRAM_BOT_TOKEN=7646701850:AAGuBMODMggvyWt54Uh8AV7Vt4_DGm47va0
TELEGRAM_CHAT_ID=5550091597
TELEGRAM_ENABLED=True

# API Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045
```

---

## 📱 FORMATO DA MENSAGEM

### **Exemplo de Mensagem Enviada:**

```
⚽ PREVISÕES DE HOJE - MARABET AI ⚽
📅 24/10/2025 15:21
🤖 Sistema de IA com Dados Reais
========================================

🏆 Partida 1:
⚔️ Flamengo vs Palmeiras
🏆 Brasileirão Série A
⏰ 16:00

🏠 Previsão: Casa
✅ Confiança: 68.5%

📈 Probabilidades:
🏠 Casa: 68.5%
🤝 Empate: 18.2%
✈️ Fora: 13.3%

💰 Odds Calculadas:
🏠 1.46
🤝 5.49
✈️ 7.52

────────────────────────────────────────

📊 RESUMO:
🔮 Previsões: 5
📈 Confiança média: 62.3%

⚠️ IMPORTANTE:
• Análise baseada em dados reais
• Use com responsabilidade
• Apostas envolvem risco

🇦🇴 MaraBet AI - Sistema Profissional
📧 comercial@marabet.ao
📧 suporte@marabet.ao
📞 +224 932027393
```

---

## 🔧 COMANDOS ÚTEIS

### **Ver Configuração Atual:**
```bash
cat telegram_config.json
```

### **Testar Envio:**
```bash
python send_today_predictions_telegram.py
```

### **Iniciar Automático:**
```bash
# Executar em foreground
python telegram_auto_scheduler.py

# Executar em background (Linux)
nohup python telegram_auto_scheduler.py > logs/telegram.log 2>&1 &

# Executar em background (Windows)
start /B python telegram_auto_scheduler.py
```

### **Ver Logs:**
```bash
# Logs do scheduler
tail -f logs/telegram_scheduler.log

# Logs do serviço (se usando systemd)
sudo journalctl -u marabet-telegram -f
```

### **Parar Automático:**
```bash
# Se rodando em foreground
Ctrl+C

# Se rodando como serviço
sudo systemctl stop marabet-telegram

# Se rodando em background
pkill -f telegram_auto_scheduler.py
```

---

## 📊 LIGAS MONITORADAS

### **Ligas Principais (8):**
1. ⚽ Brasileirão Série A (71)
2. 🏆 UEFA Champions League (2)
3. 🏆 UEFA Europa League (3)
4. 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (39)
5. 🇪🇸 La Liga (140)
6. 🇮🇹 Serie A (135)
7. 🇫🇷 Ligue 1 (61)
8. 🇩🇪 Bundesliga (78)

### **Adicionar Mais Ligas:**

Editar `send_today_predictions_telegram.py`:
```python
leagues = [
    71,   # Brasileirão
    2,    # Champions
    # Adicionar IDs de ligas aqui
    # Ver: https://www.api-football.com/documentation-v3#tag/Leagues
]
```

---

## ⚠️ TROUBLESHOOTING

### **Problema: Mensagem não enviada**

```bash
# 1. Verificar config
cat telegram_config.json

# 2. Testar bot
curl "https://api.telegram.org/bot7646701850:AAGuBMODMggvyWt54Uh8AV7Vt4_DGm47va0/getMe"

# 3. Testar envio simples
curl -X POST "https://api.telegram.org/bot7646701850:AAGuBMODMggvyWt54Uh8AV7Vt4_DGm47va0/sendMessage" \
  -d "chat_id=5550091597" \
  -d "text=Teste MaraBet AI"
```

### **Problema: Nenhuma partida encontrada**

```bash
# Normal se não houver jogos no dia
# Sistema enviará mensagem informativa
# Aguardar dias com jogos agendados
```

### **Problema: Bot bloqueado**

```bash
# 1. Abrir chat com o bot no Telegram
# 2. Enviar comando: /start
# 3. Testar novamente
```

---

## 🔄 AUTOMAÇÃO NO SERVIDOR

### **Setup Completo no Angoweb:**

```bash
# 1. Fazer upload do código
scp -r * marabet@servidor:/opt/marabet/

# 2. Instalar dependências
pip install schedule requests

# 3. Criar diretório de logs
mkdir -p /opt/marabet/logs

# 4. Configurar serviço systemd
sudo cp marabet-telegram.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable marabet-telegram
sudo systemctl start marabet-telegram

# 5. Verificar
sudo systemctl status marabet-telegram
```

---

## 📊 MONITORAMENTO

### **Ver Status:**
```bash
# Status do serviço
sudo systemctl status marabet-telegram

# Últimas 50 linhas de log
tail -n 50 logs/telegram_scheduler.log

# Monitorar em tempo real
tail -f logs/telegram_scheduler.log
```

### **Estatísticas:**
```bash
# Contar envios
grep "✅ Previsões enviadas" logs/telegram_scheduler.log | wc -l

# Últimos envios
grep "✅ Previsões enviadas" logs/telegram_scheduler.log | tail -5

# Erros
grep "❌ Erro" logs/telegram_scheduler.log | tail -10
```

---

## 📧 CONTATOS ATUALIZADOS

### **MaraBet AI:**
- 📧 **Comercial**: comercial@marabet.ao
- 📧 **Suporte**: suporte@marabet.ao
- 📞 **WhatsApp**: +224 932027393
- 💬 **Telegram Bot**: @seu_bot_name
- 🌐 **Website**: https://marabet.ao

---

## ✅ CHECKLIST

- [x] Telegram configurado
- [x] Bot Token válido
- [x] Chat ID válido
- [x] Script de envio manual criado
- [x] Agendador automático criado
- [x] Documentação completa
- [ ] Testar envio manual
- [ ] Iniciar agendador
- [ ] Configurar como serviço (servidor)
- [ ] Monitorar logs

---

## 🎯 PRÓXIMOS PASSOS

### **1. Testar Sistema:**
```bash
# Envio manual
python send_today_predictions_telegram.py
```

### **2. Iniciar Automático:**
```bash
# Iniciar agendador
python telegram_auto_scheduler.py

# Deixar rodando em background
```

### **3. No Servidor Angoweb:**
```bash
# Configurar como serviço
sudo systemctl enable marabet-telegram
sudo systemctl start marabet-telegram
```

---

**🎉 Sistema de Envio Automático Configurado!**  
**📱 Previsões serão enviadas automaticamente 3x ao dia!**  
**🇦🇴 MaraBet AI - Telegram Automático Ativo!**

---

**Criado por**: MaraBet AI  
**Última Atualização**: 24/10/2025  
**Arquivo**: TELEGRAM_AUTO_GUIDE.md

