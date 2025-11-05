# 🔔 Sistema de Notificações - MaraBet AI

## 📋 Visão Geral

O sistema de notificações do MaraBet AI permite receber alertas em tempo real sobre predições, status do sistema, erros e relatórios através de Telegram e Email. O sistema é inteligente, com filtros de qualidade e cooldown para evitar spam.

## 🏗️ Arquitetura

### Componentes Principais
- **NotificationManager**: Gerenciador principal de notificações
- **NotificationIntegrator**: Integrador com o sistema MaraBet AI
- **Notification**: Estrutura de dados para notificações
- **Canais**: Telegram e Email

### Tipos de Notificação
- **PREDICTION**: Alertas sobre predições com valor
- **SYSTEM_STATUS**: Mudanças no status do sistema
- **ERROR**: Alertas de erro críticos
- **PERFORMANCE**: Relatórios de performance
- **DAILY_REPORT**: Relatórios diários

## 🚀 Funcionalidades

### 1. Notificações de Predições
- **Filtros Inteligentes**: EV ≥ 5%, confiança ≥ 70%
- **Detalhes Completos**: Mercado, seleção, EV, confiança, stake
- **Informações da Partida**: Times, liga, data
- **Cooldown**: Evita spam de notificações similares

### 2. Notificações de Sistema
- **Status de Execução**: Início/parada do sistema
- **Métricas**: Partidas, odds, predições
- **Próximas Execuções**: Agendamento de tarefas
- **Alertas de Erro**: Problemas críticos

### 3. Relatórios Diários
- **Resumo do Dia**: Estatísticas consolidadas
- **Performance**: Métricas de sucesso
- **Atividade**: Requisições e coleta de dados
- **Recomendações**: Melhores predições do dia

### 4. Sistema de Cooldown
- **Prevenção de Spam**: 5 minutos entre notificações similares
- **Cache Inteligente**: Rastreamento por tipo e chave
- **Configurável**: Tempo de cooldown ajustável

## 🔧 Configuração

### 1. Telegram Bot

#### Criar Bot
1. Acesse [@BotFather](https://t.me/BotFather) no Telegram
2. Envie `/newbot`
3. Escolha um nome e username para o bot
4. Copie o token fornecido

#### Obter Chat ID
1. Envie uma mensagem para seu bot
2. Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
3. Copie o `chat.id` da resposta

#### Configurar no .env
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### 2. Email (Gmail)

#### Configurar App Password
1. Acesse [Conta Google](https://myaccount.google.com/)
2. Segurança → Verificação em duas etapas (ativar)
3. Segurança → Senhas de app
4. Gerar senha para "MaraBet AI"

#### Configurar no .env
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seuemail@gmail.com
SMTP_PASSWORD=sua_senha_de_app
NOTIFICATION_EMAIL=notifications@seuemail.com
ADMIN_EMAIL=admin@seuemail.com
```

### 3. Outros Provedores de Email

#### Outlook/Hotmail
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

#### Yahoo
```bash
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

## 📱 Exemplos de Notificações

### Predição via Telegram
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

### Status via Email
```html
🔮 MaraBet AI
🤖 Status do Sistema

O sistema está executando normalmente.

Tipo: system_status
Prioridade: normal
Timestamp: 14/10/2025 18:30:00

🤖 Status do Sistema
Status: 🟢 Executando
Partidas: 150
Predições: 25
Recomendadas: 8
```

### Relatório Diário
```
📈 Relatório Diário
🟢 DAILY_REPORT

Resumo das atividades do dia

📊 Métricas de Performance
Total de Predições: 25
EV Médio: 6.00%
Confiança Média: 78.0%
Taxa de Sucesso: 68.0%

⏰ 14/10/2025 08:00:00
```

## 🧪 Testes

### Executar Testes
```bash
python test_notifications.py
```

### Testes Incluídos
- ✅ Inicialização do sistema
- ✅ Notificações individuais
- ✅ Sistema de cooldown
- ✅ Critérios de notificação
- ✅ Canais específicos
- ✅ Estatísticas do sistema

### Teste Manual
```python
from notifications.notification_integrator import test_notifications

# Testar todos os canais
result = await test_notifications()

# Testar apenas Telegram
result = await test_notifications(['telegram'])

# Testar apenas Email
result = await test_notifications(['email'])
```

## 🔌 Integração

### Com Value Finder
```python
from notifications.notification_integrator import notify_prediction

# Notificar predição
prediction_data = {
    'market': 'h2h',
    'selection': 'Home',
    'expected_value': 0.08,
    'confidence': 0.75,
    'stake_percentage': 0.03,
    'recommended': True,
    'match': {
        'home_team': 'Manchester City',
        'away_team': 'Arsenal',
        'league': 'Premier League'
    }
}

await notify_prediction(prediction_data)
```

### Com Sistema Automatizado
```python
from notifications.notification_integrator import (
    notify_system_status, notify_error, notify_daily_report
)

# Notificar status
status_data = {
    'running': True,
    'total_matches': 150,
    'total_predictions': 25
}
await notify_system_status(status_data)

# Notificar erro
await notify_error("Erro na coleta de dados", {"error_type": "collection"})

# Notificar relatório diário
report_data = {
    'date': '2025-10-14',
    'total_predictions': 25,
    'success_rate': 0.68
}
await notify_daily_report(report_data)
```

## ⚙️ Configurações Avançadas

### Critérios de Notificação
```python
# settings/settings.py
NOTIFICATION_PREDICTION_THRESHOLD = 0.05  # 5% EV mínimo
NOTIFICATION_CONFIDENCE_THRESHOLD = 0.70  # 70% confiança mínima
NOTIFICATION_COOLDOWN = 300  # 5 minutos entre notificações
```

### Personalizar Formatação
```python
# Personalizar mensagem do Telegram
def _format_telegram_message(self, notification):
    # Implementar formatação customizada
    pass

# Personalizar email HTML
def _format_email_content(self, notification):
    # Implementar template customizado
    pass
```

### Adicionar Novos Canais
```python
class DiscordNotification:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    async def send(self, notification):
        # Implementar envio para Discord
        pass
```

## 📊 Monitoramento

### Estatísticas
```python
from notifications.notification_integrator import get_notification_stats

stats = get_notification_stats()
print(f"Sistema ativado: {stats['enabled']}")
print(f"Predições enviadas: {stats['prediction_count']}")
print(f"Erros notificados: {stats['error_count']}")
```

### Logs
```python
import logging

# Configurar logging para notificações
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('notifications')

# Logs incluem:
# - Envio de notificações
# - Erros de envio
# - Status dos canais
# - Estatísticas de uso
```

## 🐛 Solução de Problemas

### Erro: "Telegram não configurado"
- Verificar se `TELEGRAM_BOT_TOKEN` está correto
- Verificar se `TELEGRAM_CHAT_ID` está correto
- Testar bot manualmente no Telegram

### Erro: "Email não configurado"
- Verificar credenciais SMTP
- Usar senha de app para Gmail
- Verificar configurações de firewall

### Erro: "Notificação não enviada"
- Verificar se atende critérios (EV, confiança)
- Verificar se não está em cooldown
- Verificar logs de erro

### Erro: "Rate limit excedido"
- Ajustar `NOTIFICATION_COOLDOWN`
- Implementar rate limiting por canal
- Usar filas de notificação

## 🔒 Segurança

### Proteção de Credenciais
- Armazenar em `.env` (não versionar)
- Usar variáveis de ambiente em produção
- Rotacionar tokens periodicamente

### Validação de Dados
- Sanitizar dados antes do envio
- Validar tipos de notificação
- Limitar tamanho das mensagens

### Rate Limiting
- Cooldown entre notificações
- Limite de notificações por hora
- Blacklist de usuários

## 📈 Performance

### Otimizações
- Envio assíncrono de notificações
- Cache de configurações
- Pool de conexões SMTP
- Compressão de mensagens

### Métricas
- Taxa de entrega por canal
- Tempo de resposta
- Erro rate
- Throughput

## 🔄 Extensibilidade

### Adicionar Novo Tipo
```python
class NotificationType(Enum):
    PREDICTION = "prediction"
    SYSTEM_STATUS = "system_status"
    ERROR = "error"
    PERFORMANCE = "performance"
    DAILY_REPORT = "daily_report"
    CUSTOM = "custom"  # Novo tipo
```

### Adicionar Novo Canal
```python
class SlackNotification:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    async def send(self, notification):
        # Implementar envio para Slack
        pass
```

### Personalizar Filtros
```python
def custom_prediction_filter(prediction_data):
    # Filtros customizados
    return prediction_data['expected_value'] > 0.10
```

## 📚 Recursos Adicionais

### Documentação da API
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **SMTP Python**: https://docs.python.org/3/library/smtplib.html

### Exemplos de Uso
- **Notificações Básicas**: `examples/basic_notifications.py`
- **Integração Completa**: `examples/full_integration.py`
- **Webhooks**: `examples/webhook_notifications.py`

### Comunidade
- **GitHub Issues**: Para reportar bugs
- **Discord**: Para discussões
- **Documentation**: Wiki do projeto
