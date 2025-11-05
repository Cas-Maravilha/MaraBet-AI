# 🔔 Configuração de Notificações - MaraBet AI

## 📋 Suas Credenciais Configuradas

### 🤖 Telegram
- **Bot**: @MaraBetAIBot
- **Token**: `8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg`
- **Status**: ✅ Token configurado
- **Chat ID**: ⚠️ Precisa ser configurado

### 📧 Email Yahoo
- **Email**: `kilamu_10@yahoo.com.br`
- **Servidor**: `smtp.mail.yahoo.com:587`
- **Status**: ✅ Email configurado
- **Senha de App**: ⚠️ Precisa ser configurada

## 🚀 Como Completar a Configuração

### 1. Configurar Chat ID do Telegram

```bash
# Execute este comando:
python get_telegram_chat_id.py
```

**Instruções:**
1. Abra o Telegram
2. Procure por @MaraBetAIBot
3. Inicie uma conversa com o bot
4. Envie qualquer mensagem (ex: /start)
5. Execute o comando acima
6. Copie o Chat ID fornecido

### 2. Configurar Senha de App do Yahoo

```bash
# Execute este comando:
python setup_yahoo_email.py
```

**Instruções:**
1. Acesse: https://login.yahoo.com/
2. Faça login na sua conta Yahoo
3. Vá em 'Account Info' ou 'Gerenciar Conta'
4. Clique em 'Account Security' ou 'Segurança da Conta'
5. Procure por 'App passwords' ou 'Senhas de App'
6. Clique em 'Generate app password' ou 'Gerar senha de app'
7. Digite um nome (ex: 'MaraBet AI')
8. Copie a senha gerada (16 caracteres)
9. Execute o comando acima e cole a senha

### 3. Atualizar Arquivo .env

Após obter o Chat ID e a senha de app, edite o arquivo `.env`:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=SEU_CHAT_ID_AQUI

# Email Yahoo
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=kilamu_10@yahoo.com.br
SMTP_PASSWORD=SUA_SENHA_DE_APP_AQUI
NOTIFICATION_EMAIL=kilamu_10@yahoo.com.br
ADMIN_EMAIL=kilamu_10@yahoo.com.br
```

## 🧪 Testar o Sistema

### Teste Completo
```bash
python test_my_notifications.py
```

### Teste Individual do Telegram
```bash
python get_telegram_chat_id.py
```

### Teste Individual do Email
```bash
python setup_yahoo_email.py
```

## 📱 Exemplos de Notificações

### Telegram
```
🔮 Nova Predição Encontrada!
🟠 PREDICTION

Valor detectado: 8.00% EV

📊 Detalhes da Predição:
🎯 Mercado: h2h
🎲 Seleção: Home
🟢 EV: 8.00%
🎯 Confiança: 75.0%
💰 Stake: 3.0%
⚽ Manchester City vs Arsenal
🏆 Premier League

⏰ 14/10/2025 18:30:00
```

### Email
- Template HTML responsivo
- Cores e estilos personalizados
- Informações estruturadas
- Links e botões interativos

## 🎯 Tipos de Notificação

### 🔮 Predições
- **Quando**: Predições com EV ≥ 5% e confiança ≥ 70%
- **Conteúdo**: Mercado, seleção, EV, confiança, stake, partida
- **Frequência**: Imediata (com cooldown de 5 min)

### 🤖 Status do Sistema
- **Quando**: Início/parada do sistema, mudanças de status
- **Conteúdo**: Status, métricas, próximas execuções
- **Frequência**: Imediata

### ❌ Alertas de Erro
- **Quando**: Erros críticos no sistema
- **Conteúdo**: Tipo de erro, detalhes, timestamp
- **Frequência**: Imediata (com cooldown)

### 📊 Relatórios de Performance
- **Quando**: Métricas de performance
- **Conteúdo**: Total de predições, EV médio, taxa de sucesso
- **Frequência**: Sob demanda

### 📈 Relatórios Diários
- **Quando**: Diariamente às 8:00
- **Conteúdo**: Resumo do dia, estatísticas, melhores predições
- **Frequência**: Diária

## 🚀 Iniciar o Sistema

### Sistema Automatizado
```bash
python run_automated_collector.py
```

### Dashboard Web
```bash
python run_dashboard.py
```

### Teste de API Keys
```bash
python test_api_keys.py
```

## 🔧 Comandos Úteis

### Verificar Configuração
```bash
python -c "from settings.settings import *; print(f'Telegram: {bool(TELEGRAM_BOT_TOKEN)}'); print(f'Email: {bool(SMTP_USERNAME)}')"
```

### Testar Notificações
```bash
python -c "import asyncio; from notifications.notification_integrator import test_notifications; asyncio.run(test_notifications())"
```

### Ver Estatísticas
```bash
python -c "from notifications.notification_integrator import get_notification_stats; print(get_notification_stats())"
```

## 🐛 Solução de Problemas

### Erro: "Chat ID não encontrado"
- Verifique se enviou mensagem para @MaraBetAIBot
- Execute `python get_telegram_chat_id.py` novamente
- Verifique se o token está correto

### Erro: "Email não configurado"
- Verifique se a senha de app tem 16 caracteres
- Use senha de app, não senha normal do Yahoo
- Ative verificação em duas etapas primeiro

### Erro: "Notificação não enviada"
- Verifique se atende critérios (EV ≥ 5%, confiança ≥ 70%)
- Verifique se não está em cooldown
- Verifique logs de erro

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs do sistema
2. Execute os testes individuais
3. Verifique as configurações no .env
4. Consulte a documentação completa

## 🎉 Próximos Passos

Após configurar as notificações:
1. ✅ Configure o Chat ID do Telegram
2. ✅ Configure a senha de app do Yahoo
3. ✅ Teste o sistema de notificações
4. ✅ Inicie o sistema automatizado
5. ✅ Acesse o dashboard web
6. ✅ Monitore as notificações

**Sistema pronto para uso!** 🚀
