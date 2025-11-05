# 🔐 GUIA DE CONFIGURAÇÃO SEGURA - MARABET AI

## ⚠️ ALERTA CRÍTICO DE SEGURANÇA

**SUAS CHAVES DE API FORAM EXPOSTAS PUBLICAMENTE!**

### 🚨 AÇÕES IMEDIATAS NECESSÁRIAS:

#### 1. **REVOGAR CHAVES EXPOSTAS (URGENTE)**
- [ ] **API Football**: Acesse [API-Football](https://www.api-football.com/) e revogue a chave `747d6e19a2d3a435fdb7a419007a45fa`
- [ ] **Telegram Bot**: Acesse [@BotFather](https://t.me/botfather) e revogue o token `8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg`
- [ ] **Yahoo Email**: Altere a senha da conta `kilamu_10@yahoo.com.br`

#### 2. **GERAR NOVAS CHAVES SEGURAS**
- [ ] **API Football**: Gere nova chave em [API-Football](https://www.api-football.com/)
- [ ] **Telegram Bot**: Crie novo bot com [@BotFather](https://t.me/botfather)
- [ ] **Yahoo Email**: Configure senha de app específica

#### 3. **CONFIGURAR VARIÁVEIS DE AMBIENTE**

1. **Copie o arquivo de exemplo:**
   ```bash
   cp config_personal.env .env
   ```

2. **Edite o arquivo `.env` com suas novas credenciais:**
   ```env
   # Configurações da API
   API_FOOTBALL_KEY=sua_nova_chave_aqui
   THE_ODDS_API_KEY=sua_chave_the_odds_aqui
   
   # Telegram
   TELEGRAM_BOT_TOKEN=seu_novo_token_aqui
   TELEGRAM_CHAT_ID=seu_chat_id_aqui
   
   # Email
   SMTP_USERNAME=seu_email_aqui
   SMTP_PASSWORD=sua_senha_de_app_aqui
   NOTIFICATION_EMAIL=seu_email_aqui
   ADMIN_EMAIL=seu_email_aqui
   ```

3. **NUNCA commite o arquivo `.env`!**

#### 4. **VERIFICAR SEGURANÇA**

Execute o teste de segurança:
```bash
python test_api_keys.py
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
- [ ] Credenciais removidas do código
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
