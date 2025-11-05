# 📱 GUIA DE CONFIGURAÇÃO DO TELEGRAM - MARABET AI

## 🎯 **VISÃO GERAL**

Este guia mostra como configurar o envio automático de predições via Telegram para o sistema MaraBet AI.

## 🚀 **PASSO A PASSO COMPLETO**

### **1. CRIAR BOT NO TELEGRAM**

1. **Abra o Telegram** no seu celular ou computador
2. **Procure por @BotFather** na barra de pesquisa
3. **Inicie uma conversa** com o BotFather
4. **Envie o comando:** `/newbot`
5. **Escolha um nome** para o bot (ex: "MaraBet AI Predictions")
6. **Escolha um username** (ex: "marabet_ai_bot")
7. **Copie o TOKEN** que será fornecido (ex: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### **2. CONFIGURAR O BOT**

1. **Envie uma mensagem** para o bot que você criou
2. **Execute o script de configuração:**
   ```bash
   python setup_telegram_bot.py
   ```
3. **Digite o TOKEN** quando solicitado
4. **O script obterá automaticamente** seu Chat ID

### **3. TESTAR O ENVIO**

1. **Execute o script de envio:**
   ```bash
   python send_predictions_telegram.py
   ```
2. **Verifique se recebeu** as predições no Telegram

## 📋 **ARQUIVOS CRIADOS**

- `send_predictions_telegram.py` - Script principal de envio
- `setup_telegram_bot.py` - Script de configuração
- `demo_telegram_predictions.py` - Demonstração com dados reais
- `demo_telegram_with_simulated_data.py` - Demonstração com dados simulados
- `telegram_config.json` - Arquivo de configuração (criado automaticamente)
- `telegram_message_demo.txt` - Exemplo de mensagem formatada

## 🔧 **CONFIGURAÇÃO MANUAL (ALTERNATIVA)**

Se preferir configurar manualmente:

1. **Edite o arquivo `send_predictions_telegram.py`**
2. **Substitua as linhas:**
   ```python
   self.telegram_bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
   self.telegram_chat_id = "YOUR_TELEGRAM_CHAT_ID"
   ```
3. **Por:**
   ```python
   self.telegram_bot_token = "SEU_TOKEN_AQUI"
   self.telegram_chat_id = "SEU_CHAT_ID_AQUI"
   ```

## 📱 **EXEMPLO DE MENSAGEM ENVIADA**

```
⚽ PREDIÇÕES MARABET AI ⚽
📅 21/10/2025 17:59
🤖 Sistema de IA com dados reais da API Football

🏆 Partida 1:
⚔️ Santos vs Vitoria
📅 2025-10-21
🏆 Serie A

🔮 Predição: 🏠 Casa
📊 Confiança: 75.5%

📈 Probabilidades:
🏠 Casa: 75.5%
🤝 Empate: 9.4%
✈️ Fora: 15.1%

💰 Odds Calculadas:
🏠 Casa: 1.32
🤝 Empate: 10.60
✈️ Fora: 6.62

💎 Valor das Apostas:
🏠 Casa: 0.0% ❌
🤝 Empate: 0.0% ❌
✈️ Fora: 0.0% ❌

──────────────────────────────

📊 RESUMO:
🔮 Predições: 1
📈 Confiança média: 75.5%
💎 Apostas com valor: 0/1

⚠️ AVISO: Apostas envolvem risco. Use com responsabilidade.
🤖 Powered by MaraBet AI - Sistema de IA para Futebol
```

## 🎯 **FUNCIONALIDADES**

### **✅ PREDIÇÕES AUTOMÁTICAS**
- Dados reais da API Football
- Análise de forma dos times
- Cálculo de probabilidades
- Odds calculadas automaticamente

### **✅ ANÁLISE DE VALOR**
- Identificação de apostas com valor positivo
- Recomendações baseadas em dados
- Avisos de risco

### **✅ FORMATAÇÃO PROFISSIONAL**
- Mensagens bem estruturadas
- Emojis para melhor visualização
- Informações completas e claras

## 🔄 **AUTOMAÇÃO**

Para enviar predições automaticamente:

1. **Configure um cron job** (Linux/Mac) ou **Agendador de Tarefas** (Windows)
2. **Execute o script** em horários específicos
3. **Exemplo de cron job:**
   ```bash
   # Enviar predições às 9h, 15h e 21h todos os dias
   0 9,15,21 * * * cd /caminho/para/marabet && python send_predictions_telegram.py
   ```

## 🛠️ **TROUBLESHOOTING**

### **❌ Erro: "Token inválido"**
- Verifique se o token está correto
- Certifique-se de que o bot foi criado corretamente

### **❌ Erro: "Chat ID não encontrado"**
- Envie uma mensagem para o bot primeiro
- Execute o script de configuração novamente

### **❌ Erro: "Nenhuma partida encontrada"**
- Verifique se há partidas do Brasileirão hoje
- O sistema usa dados reais da API Football

### **❌ Erro: "Falha na API"**
- Verifique sua conexão com a internet
- Confirme se a API key está válida

## 📊 **ESTATÍSTICAS DO SISTEMA**

- **✅ 5 predições** geradas por execução
- **✅ Dados reais** da API Football
- **✅ Análise de forma** dos últimos 5 jogos
- **✅ Cálculo de odds** automático
- **✅ Identificação de valor** nas apostas
- **✅ Formatação profissional** para Telegram

## 🎉 **CONCLUSÃO**

O sistema MaraBet AI agora está configurado para enviar predições via Telegram automaticamente. As predições são baseadas em dados reais da API Football e incluem análise completa de probabilidades, odds e valor das apostas.

**Status: SISTEMA DE TELEGRAM CONFIGURADO E FUNCIONANDO! 🚀**
