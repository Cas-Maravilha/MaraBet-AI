# 🤖 SISTEMA AUTOMÁTICO DE PREDIÇÕES FUTURAS - MARABET AI

## 🎯 **VISÃO GERAL**

Sistema automático que envia predições de partidas futuras via Telegram usando dados reais da API Football, com foco exclusivo em partidas que ainda vão acontecer.

## ✅ **CARACTERÍSTICAS PRINCIPAIS**

### **🔮 PREDIÇÕES FUTURAS:**
- ✅ Apenas partidas que ainda vão acontecer
- ✅ Dados históricos para análise de forma
- ✅ Confiança ajustada pela confiabilidade
- ✅ Probabilidades e odds calculadas

### **🤖 AUTOMAÇÃO:**
- ✅ Verificação automática a cada 6 horas
- ✅ Controle de envios diários (máximo 3)
- ✅ Filtro de partidas não enviadas
- ✅ Logs detalhados

### **📊 DADOS REAIS:**
- ✅ API Football com dados reais
- ✅ Análise de forma dos últimos 10 jogos
- ✅ Cálculo de força dos times
- ✅ Fator casa considerado

## 🚀 **CONFIGURAÇÃO RÁPIDA**

### **1. CONFIGURAR TELEGRAM:**
```bash
python setup_auto_telegram.py
```

### **2. INICIAR SISTEMA:**
```bash
python start_auto_predictions.py
```

### **3. MONITORAR:**
- Logs detalhados no console
- Controle de envios diários
- Verificação de partidas novas

## 📋 **ARQUIVOS DO SISTEMA**

### **Scripts Principais:**
- `auto_telegram_predictions.py` - Sistema automático principal
- `setup_auto_telegram.py` - Configuração automática
- `start_auto_predictions.py` - Script de inicialização
- `demo_auto_system.py` - Demonstração do sistema

### **Configurações:**
- `telegram_config.json` - Configuração do Telegram
- `auto_telegram_config.json` - Configuração do sistema automático

### **Arquivos de Suporte:**
- `start_auto_predictions.bat` - Inicialização no Windows
- `AUTO_TELEGRAM_SYSTEM_GUIDE.md` - Este guia

## ⚙️ **CONFIGURAÇÕES PERSONALIZÁVEIS**

### **Arquivo: `auto_telegram_config.json`**
```json
{
  "check_interval_hours": 6,      // Frequência de verificação
  "days_ahead": 7,                // Dias à frente para buscar partidas
  "max_predictions": 5,           // Máximo de predições por envio
  "max_sends_per_day": 3,         // Máximo de envios por dia
  "enabled": true                 // Sistema ativo/inativo
}
```

### **Parâmetros Explicados:**
- **`check_interval_hours`**: A cada quantas horas verificar partidas (padrão: 6)
- **`days_ahead`**: Quantos dias à frente buscar partidas (padrão: 7)
- **`max_predictions`**: Máximo de predições por envio (padrão: 5)
- **`max_sends_per_day`**: Máximo de envios por dia (padrão: 3)
- **`enabled`**: Ativar/desativar sistema (padrão: true)

## 🔮 **EXEMPLO DE PREDIÇÕES ENVIADAS**

```
🔮 PREDIÇÕES FUTURAS - MARABET AI 🔮
📅 21/10/2025 18:30
⚽ Partidas que ainda vão acontecer
🤖 Sistema automático com dados reais da API Football

🏆 Partida 1:
⚔️ Flamengo vs Palmeiras
📅 25/10/2025 16:00
🏆 Serie A

🔮 Predição: 🏠 Casa
📊 Confiança: 68.5%
🎯 Confiabilidade: 95.0%

📈 Probabilidades:
🏠 Casa: 68.5%
🤝 Empate: 18.2%
✈️ Fora: 13.3%

💰 Odds Calculadas:
🏠 Casa: 1.46
🤝 Empate: 5.49
✈️ Fora: 7.52

💎 Valor das Apostas:
🏠 Casa: 0.0% ❌
🤝 Empate: 0.0% ❌
✈️ Fora: 0.0% ❌

📊 Dados de Forma:
🏠 Flamengo: 10 jogos analisados
✈️ Palmeiras: 10 jogos analisados
💪 Força: Casa 0.65 | Fora 0.58

──────────────────────────────

📊 RESUMO DAS PREDIÇÕES FUTURAS:
🔮 Predições: 3
📈 Confiança média: 72.1%
🎯 Confiabilidade média: 96.7%
💎 Apostas com valor: 0/3

⏰ IMPORTANTE: Estas são predições para partidas FUTURAS
🤖 AUTOMÁTICO: Enviado automaticamente pelo sistema
⚠️ AVISO: Apostas envolvem risco. Use com responsabilidade.
🤖 Powered by MaraBet AI - Sistema de IA para Futebol
```

## 🎯 **FLUXO DE FUNCIONAMENTO**

### **1. VERIFICAÇÃO AUTOMÁTICA:**
- Sistema verifica a cada 6 horas
- Busca partidas futuras do Brasileirão
- Filtra partidas não enviadas anteriormente

### **2. ANÁLISE DE DADOS:**
- Obtém forma recente dos times (últimos 10 jogos)
- Calcula força dos times baseada em resultados
- Aplica fator casa e confiabilidade

### **3. GERAÇÃO DE PREDIÇÕES:**
- Calcula probabilidades normalizadas
- Determina predição mais provável
- Calcula odds para apostas

### **4. ENVIO VIA TELEGRAM:**
- Formata mensagem com HTML
- Inclui análise de valor das apostas
- Envia via bot configurado

### **5. CONTROLE DE ENVIOS:**
- Registra partidas enviadas
- Controla limite diário de envios
- Reset diário do contador

## 📊 **MONITORAMENTO E LOGS**

### **Logs Detalhados:**
```
2025-10-21 18:30:15 - INFO - 🔍 VERIFICANDO PARTIDAS FUTURAS...
2025-10-21 18:30:16 - INFO - 📅 OBTENDO PARTIDAS FUTURAS (PRÓXIMOS 7 DIAS)
2025-10-21 18:30:17 - INFO -    3 partidas futuras encontradas
2025-10-21 18:30:18 - INFO - 🔮 PREDIZENDO: Flamengo vs Palmeiras (25/10/2025 16:00)
2025-10-21 18:30:19 - INFO - 🔮 PREDIZENDO: São Paulo vs Santos (26/10/2025 19:00)
2025-10-21 18:30:20 - INFO - 🔮 PREDIZENDO: Corinthians vs Internacional (27/10/2025 16:00)
2025-10-21 18:30:21 - INFO - 📤 Enviando 3 predições via Telegram...
2025-10-21 18:30:22 - INFO - ✅ Mensagem enviada com sucesso
2025-10-21 18:30:23 - INFO - ✅ Predições enviadas com sucesso! (Envio 1/3)
```

### **Controles de Qualidade:**
- ✅ Verificação de partidas não enviadas
- ✅ Controle de limite diário
- ✅ Validação de dados da API
- ✅ Tratamento de erros

## 🛠️ **TROUBLESHOOTING**

### **❌ "Configuração do Telegram não encontrada"**
**Solução:**
```bash
python setup_auto_telegram.py
```

### **❌ "Nenhuma partida futura encontrada"**
**Explicação:** Normal quando não há partidas do Brasileirão nos próximos dias.

### **❌ "Limite diário atingido"**
**Explicação:** Sistema respeita limite de 3 envios por dia.

### **❌ "Erro na API"**
**Solução:** Verificar conexão com internet e API key.

## 🎉 **VANTAGENS DO SISTEMA AUTOMÁTICO**

### **✅ PREDIÇÕES FUTURAS:**
- Partidas que ainda vão acontecer
- Valor real para apostas
- Baseadas em dados históricos

### **✅ AUTOMAÇÃO COMPLETA:**
- Verificação automática
- Envio automático
- Controle de qualidade

### **✅ DADOS REAIS:**
- API Football oficial
- Análise de forma dos times
- Cálculo de probabilidades

### **✅ CONFIGURAÇÃO FLEXÍVEL:**
- Parâmetros personalizáveis
- Controle de envios
- Logs detalhados

## 🚀 **SISTEMA PRONTO PARA USO**

**O MaraBet AI agora possui:**
- ✅ **Sistema automático** de predições futuras
- ✅ **Envio via Telegram** automático
- ✅ **Dados reais** da API Football
- ✅ **Análise de forma** dos times
- ✅ **Controle de qualidade** integrado
- ✅ **Configuração flexível** e personalizável

**Status: SISTEMA AUTOMÁTICO IMPLEMENTADO E FUNCIONANDO! 🎉**

## ⚠️ **IMPORTANTE**

- **Predições são para partidas FUTURAS**
- **Sistema usa dados reais da API Football**
- **Apostas envolvem risco**
- **Use com responsabilidade**

**O sistema está configurado para enviar automaticamente predições futuras via Telegram sempre que houver partidas disponíveis!**
