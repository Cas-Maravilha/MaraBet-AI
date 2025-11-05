# 🔐 GUIA PARA REGENERAR CHAVES SEGURAS

## 🚨 ALERTA CRÍTICO DE SEGURANÇA

**SUAS CHAVES FORAM EXPOSTAS NO README PÚBLICO!**

### ⚠️ AÇÕES IMEDIATAS NECESSÁRIAS:

#### 1. **REVOGAR CHAVES EXPOSTAS (URGENTE)**
- [ ] **API Football**: Acesse [API-Football](https://www.api-football.com/) e revogue a chave `747d6e19a2d3a435fdb7a419007a45fa`
- [ ] **Telegram Bot**: Acesse [@BotFather](https://t.me/botfather) e revogue o token `8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg`
- [ ] **Yahoo Email**: Altere a senha da conta `kilamu_10@yahoo.com.br`

#### 2. **GERAR NOVAS CHAVES SEGURAS**
- [ ] **API Football**: Gere nova chave em [API-Football](https://www.api-football.com/)
- [ ] **Telegram Bot**: Crie novo bot com [@BotFather](https://t.me/botfather)
- [ ] **Yahoo Email**: Configure senha de app específica

#### 3. **CONFIGURAR NOVAS CHAVES NO .env**

1. **Abra o arquivo .env:**
   ```bash
   notepad .env
   ```

2. **Substitua pelas suas novas credenciais:**
   ```env
   # Configurações da API
   API_FOOTBALL_KEY=SUA_NOVA_CHAVE_API_FOOTBALL
   THE_ODDS_API_KEY=SUA_CHAVE_THE_ODDS_API
   
   # Telegram
   TELEGRAM_BOT_TOKEN=SEU_NOVO_TOKEN_TELEGRAM
   TELEGRAM_CHAT_ID=SEU_CHAT_ID_TELEGRAM
   
   # Email
   SMTP_USERNAME=SEU_EMAIL_YAHOO
   SMTP_PASSWORD=SUA_SENHA_APP_YAHOO
   NOTIFICATION_EMAIL=SEU_EMAIL_YAHOO
   ADMIN_EMAIL=SEU_EMAIL_YAHOO
   ```

3. **NUNCA commite o arquivo .env!**

#### 4. **VERIFICAR SEGURANÇA**

Execute o teste de segurança:
```bash
python teste_final_sistema.py
```

### 🛡️ BOAS PRÁTICAS DE SEGURANÇA:

1. **NUNCA** coloque credenciais diretamente no código
2. **SEMPRE** use variáveis de ambiente
3. **SEMPRE** adicione arquivos sensíveis ao `.gitignore`
4. **SEMPRE** use senhas de app para email
5. **SEMPRE** revogue chaves comprometidas imediatamente

### 📋 CHECKLIST DE SEGURANÇA:

- [ ] Chaves antigas revogadas
- [ ] Novas chaves geradas
- [ ] Arquivo `.env` configurado
- [ ] Credenciais removidas do README
- [ ] `.gitignore` atualizado
- [ ] Teste de segurança executado
- [ ] Repositório limpo de credenciais

### 🆘 EM CASO DE COMPROMETIMENTO:

1. **Revogue TODAS as chaves imediatamente**
2. **Altere TODAS as senhas**
3. **Monitore contas para atividade suspeita**
4. **Gere novas credenciais**
5. **Atualize configurações**

---

**⚠️ LEMBRE-SE: Segurança é responsabilidade de todos!**
