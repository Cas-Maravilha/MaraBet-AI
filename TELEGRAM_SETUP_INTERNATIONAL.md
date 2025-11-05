# 🤖 Guia de Configuração do Telegram - Competições Internacionais

## 📋 **CONFIGURAÇÃO DO TELEGRAM PARA ENVIO AUTOMÁTICO**

Para receber predições automaticamente no Telegram, siga estes passos:

### **1. Criar Bot do Telegram**

1. **Abra o Telegram** no seu celular ou computador
2. **Procure por @BotFather** na barra de pesquisa
3. **Digite /newbot** para criar um novo bot
4. **Escolha um nome** para o bot (ex: "MaraBet AI Predictions")
5. **Escolha um username** para o bot (ex: "marabet_ai_bot")
6. **Copie o TOKEN** que o BotFather fornecer (ex: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### **2. Obter Chat ID**

1. **Envie uma mensagem** para o bot que você criou
2. **Acesse esta URL** no navegador (substitua SEU_TOKEN pelo token do bot):
   ```
   https://api.telegram.org/botSEU_TOKEN/getUpdates
   ```
3. **Procure por** `"chat":{"id": NUMERO}` na resposta
4. **Copie o número** que aparece após `"id":` (ex: `123456789`)

### **3. Configurar no Sistema**

#### **Opção A: Configuração Automática**
```bash
python setup_telegram_international.py
```

#### **Opção B: Configuração Manual**
1. **Abra o arquivo `.env`** no diretório do projeto
2. **Adicione as seguintes linhas**:
   ```
   TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI
   TELEGRAM_CHAT_ID=SEU_CHAT_ID_AQUI
   ```
3. **Salve o arquivo**

### **4. Testar Configuração**

```bash
python run_telegram_auto.py
```

## 🚀 **EXECUÇÃO AUTOMÁTICA COM TELEGRAM**

### **Comando Principal:**
```bash
python run_telegram_auto.py
```

### **O que acontece:**
1. ✅ **Sistema executa** predições internacionais
2. ✅ **Busca partidas** de hoje, ao vivo e futuras
3. ✅ **Gera predições** com IA
4. ✅ **Envia automaticamente** para o Telegram
5. ✅ **Formata mensagens** com emojis e HTML

## 📱 **EXEMPLO DE MENSAGEM NO TELEGRAM**

```
🌍 PREDIÇÕES INTERNACIONAIS - MARABET AI 🌍
📅 21/10/2025 18:52
🤖 Sistema de IA com dados reais da API Football
🌐 Cobertura: Competições internacionais completas

🏆 COMPETIÇÕES DE CLUBES - 4 partidas:
============================================================

⚽ Partida 1:
⚔️ Roma vs Fiorentina
📅 21/10 14:00
🏆 Conference League (Europe)
📊 Status: Ao Vivo
🎯 Tier: Tier 1
⚽ Placar: Roma 0 x 1 Fiorentina

🔮 Predição: 🏠 Casa
📊 Confiança: 77.9%
🎯 Confiabilidade: 100.0%

📈 Probabilidades:
🏠 Casa: 77.9%
🤝 Empate: 4.8%
✈️ Fora: 17.3%

💰 Odds Calculadas:
🏠 Casa: 1.28
🤝 Empate: 21.00
✈️ Fora: 5.78

💎 Valor das Apostas:
🏠 Casa: 0.0% ❌
🤝 Empate: 0.0% ❌
✈️ Fora: 0.0% ❌
```

## 🌍 **COMPETIÇÕES COBERTAS**

### **🏆 Competições Europeias:**
- Champions League
- Europa League
- Conference League
- Super Cup

### **🌍 Competições Internacionais:**
- Copa do Mundo
- Copa América
- Copa Africana (CAN)
- Euro Championship
- Nations League

### **⚽ Ligas Nacionais:**
- Premier League (Inglaterra)
- La Liga (Espanha)
- Bundesliga (Alemanha)
- Serie A (Itália)
- Ligue 1 (França)
- Serie A (Brasil)

## 🔧 **SOLUÇÃO DE PROBLEMAS**

### **❌ "Configurações do Telegram não encontradas"**
- Verifique se o arquivo `.env` existe
- Confirme se `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` estão configurados
- Execute: `python setup_telegram_international.py`

### **❌ "Erro ao enviar para Telegram"**
- Verifique se o token do bot está correto
- Confirme se o chat ID está correto
- Teste enviando uma mensagem manual para o bot

### **❌ "Nenhuma partida encontrada"**
- Verifique a conexão com a internet
- Confirme se a API key está funcionando
- Execute: `python test_api_football_valid_key.py`

## 📊 **FUNCIONALIDADES IMPLEMENTADAS**

### ✅ **Sistema Automático:**
- Execução automática de predições
- Envio automático para Telegram
- Formatação HTML com emojis
- Divisão de mensagens longas

### ✅ **Cobertura Global:**
- Todas as competições internacionais
- Partidas ao vivo e futuras
- Análise de forma dos times
- Cálculo de probabilidades e odds

### ✅ **Integração Telegram:**
- Mensagens formatadas com HTML
- Emojis para melhor visualização
- Resumos estatísticos
- Alertas de valor nas apostas

## 🎯 **PRÓXIMOS PASSOS**

1. **Configure o Telegram** seguindo este guia
2. **Execute o sistema** com `python run_telegram_auto.py`
3. **Receba predições** automaticamente no Telegram
4. **Monitore as predições** em tempo real
5. **Ajuste configurações** conforme necessário

## 📞 **SUPORTE**

Se tiver problemas:
1. Verifique este guia
2. Execute os testes de configuração
3. Consulte os logs de erro
4. Verifique a conexão com a internet

---

**🤖 Powered by MaraBet AI - Sistema de IA para Futebol**
