# 🚨 PROBLEMA IDENTIFICADO: IP NÃO AUTORIZADO - API-FOOTBALL

**Data**: 24/10/2025  
**Status**: 🔴 CRÍTICO - BLOQUEIO DE IP  
**Contato**: +224 932027393

---

## 🔍 PROBLEMA DETECTADO

### **Erro da API:**
```json
{
  "errors": {
    "Ip": "This IP is not allowed to call the API, check the list of allowed IPs in the dashboard."
  }
}
```

### **Significado:**
❌ **Seu IP atual NÃO está na lista de IPs permitidos no dashboard da API-Football**

Isso explica por que:
- ❌ Não retorna partidas
- ❌ Não retorna odds
- ❌ Não retorna previsões
- ❌ Sistema não mostra dados reais

---

## ✅ SOLUÇÃO: ADICIONAR IP À WHITELIST

### **Passo 1: Descobrir Seu IP Atual**

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri "https://api.ipify.org").Content

# Linux/Mac
curl https://api.ipify.org

# Ou acesse no navegador:
https://www.whatismyip.com/
```

**Anote seu IP**: _____________________

---

### **Passo 2: Acessar Dashboard API-Football**

1. **Acesse**: https://dashboard.api-football.com/
2. **Login** com suas credenciais
3. **Vá para**: "My Account" ou "API Keys"

---

### **Passo 3: Adicionar IP à Whitelist**

No Dashboard da API-Football:

1. Procure por **"IP Whitelist"** ou **"Allowed IPs"**
2. Clique em **"Add IP"** ou **"+ New IP"**
3. **Cole** seu IP atual
4. **Salve** as alterações
5. **Aguarde** 1-2 minutos para propagar

**Exemplo:**
```
IP Address: 123.45.67.89
Description: MaraBet AI - Development
Status: Active
```

---

### **Passo 4: Testar Novamente**

```bash
# Aguardar 1-2 minutos após adicionar IP

# Testar conexão
python test_api_ultra_plan.py

# Deve retornar dados agora!
```

---

## 🌐 MÚLTIPLOS IPs (Para Produção)

### **IPs que você precisará adicionar:**

1. **IP do seu PC** (desenvolvimento)
   - IP atual: Descobrir com `curl ipify.org`
   - Usar para: Desenvolvimento local

2. **IP do Servidor Angoweb** (produção)
   - IP fornecido pela Angoweb
   - Usar para: Produção
   - Adicionar ANTES do deploy

3. **IP do Servidor de Backup** (opcional)
   - Se usar servidor secundário
   - Para redundância

---

## 📋 CHECKLIST DE CONFIGURAÇÃO

### **No Dashboard API-Football:**

- [ ] Login no dashboard
- [ ] Ir para "API Keys" ou "My Account"
- [ ] Encontrar seção "IP Whitelist"
- [ ] Adicionar IP do PC atual
- [ ] Adicionar IP do servidor Angoweb (quando receber)
- [ ] Salvar alterações
- [ ] Aguardar 1-2 minutos
- [ ] Testar com `python test_api_ultra_plan.py`

---

## ⚠️ IMPORTANTE

### **IPs Dinâmicos:**

Se seu IP muda frequentemente:

**Opção A: Desabilitar Whitelist** (Menos seguro)
```
No dashboard:
• Desmarcar "Enable IP Whitelist"
• Salvar
• API aceitará qualquer IP
```

**Opção B: Usar 0.0.0.0/0** (Aceitar todos)
```
• Adicionar: 0.0.0.0/0
• Permite qualquer IP
• Menos seguro, mas funcional
```

**Opção C: Atualizar IP quando mudar**
```
• Quando IP mudar, atualizar no dashboard
• Recomendado para produção
```

---

## 🔧 CONFIGURAÇÃO PARA ANGOWEB

### **Quando Receber Servidor Angoweb:**

1. **Angoweb fornecerá IP fixo**
2. **Adicionar IP no dashboard API-Football**
3. **Sistema funcionará perfeitamente**

**Exemplo:**
```
IP Angoweb: 197.149.XX.XX (fornecido pela Angoweb)
Adicionar no dashboard API-Football
Aguardar propagação
Deploy funcionará!
```

---

## 🧪 TESTE RÁPIDO

### **Após Adicionar IP:**

```bash
# Teste 1: Status
curl "https://v3.football.api-sports.io/status" \
  -H "x-apisports-key: 71b2b62386f2d1275cd3201a73e1e045"

# Deve retornar dados da conta, não erro de IP

# Teste 2: Jogos ao vivo
curl "https://v3.football.api-sports.io/fixtures?live=all" \
  -H "x-apisports-key: 71b2b62386f2d1275cd3201a73e1e045"

# Deve retornar jogos (ou [] se nenhum ao vivo)

# Teste 3: Próximas partidas
curl "https://v3.football.api-sports.io/fixtures?next=10" \
  -H "x-apisports-key: 71b2b62386f2d1275cd3201a73e1e045"

# Deve retornar lista de partidas futuras
```

---

## 📊 STATUS ATUAL DAS APIs

### **API-Football (api-sports.io):**
- ❌ **Bloqueada por IP** - Precisa adicionar IP
- ✅ Chave válida e ativa
- ✅ Plano Ultra funcionando
- ⏳ Aguardando whitelist de IP

### **football-data.org:**
- ✅ **100% Funcionando**
- ✅ 13 competições
- ✅ 380 partidas
- ✅ Classificações completas
- ✅ Sem restrição de IP

---

## 🎯 SOLUÇÃO TEMPORÁRIA

### **Enquanto não adiciona IP:**

Use **football-data.org** que está funcionando perfeitamente:
- ✅ 380 partidas disponíveis
- ✅ 13 competições
- ✅ Dados em tempo real
- ✅ Sem bloqueio de IP

```bash
# Usar sistema com football-data.org
python final_integrated_football_system.py
```

---

## 📞 SUPORTE API-FOOTBALL

### **Se tiver dúvidas:**

- 🌐 **Dashboard**: https://dashboard.api-football.com/
- 📧 **Suporte**: support@api-football.com
- 📚 **Documentação**: https://www.api-football.com/documentation-v3

---

## ✅ AÇÃO IMEDIATA

### **FAZER AGORA:**

1. **Descobrir seu IP:**
   ```bash
   curl https://api.ipify.org
   ```

2. **Acessar dashboard:**
   ```
   https://dashboard.api-football.com/
   ```

3. **Adicionar IP à whitelist**

4. **Aguardar 2 minutos**

5. **Testar:**
   ```bash
   python test_api_ultra_plan.py
   ```

---

## 🎉 APÓS CORRIGIR

Quando adicionar o IP:
- ✅ API-Football funcionará 100%
- ✅ Odds em tempo real disponíveis
- ✅ Previsões da API acessíveis
- ✅ Jogos ao vivo funcionando
- ✅ Sistema completo operacional

---

**🚨 PROBLEMA: Bloqueio de IP no plano Ultra**  
**✅ SOLUÇÃO: Adicionar IP no dashboard**  
**⏱️ TEMPO: 5 minutos**  

**📧 Suporte**: suporte@marabet.ao  
**📞 WhatsApp**: +224 932027393

