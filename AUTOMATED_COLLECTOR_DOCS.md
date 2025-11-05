# 🤖 Sistema de Coleta Automatizada - MaraBet AI

## 📋 Visão Geral

O sistema de coleta automatizada é o coração operacional do MaraBet AI, responsável por executar todas as tarefas de coleta, processamento e análise de forma autônoma e programada. Ele garante que o sistema funcione 24/7 sem intervenção manual.

## 🏗️ Arquitetura

### Componentes Principais
- **AutomatedCollector**: Classe principal que gerencia todo o sistema
- **Schedule**: Agendador de tarefas baseado em tempo
- **ThreadPoolExecutor**: Execução paralela de tarefas
- **Logging**: Sistema de logs detalhado
- **Database**: Armazenamento persistente de dados

### Fluxo de Operação
1. **Inicialização**: Configuração de tarefas e componentes
2. **Agendamento**: Programação de execuções periódicas
3. **Execução**: Processamento automático das tarefas
4. **Monitoramento**: Acompanhamento de status e performance
5. **Manutenção**: Limpeza e otimização automática

## 🚀 Funcionalidades

### 1. Coleta de Dados de Futebol
- **Frequência**: A cada 30 minutos
- **Fonte**: API-Football
- **Dados**: Partidas, estatísticas, eventos
- **Ligas**: 6 ligas principais monitoradas

### 2. Coleta de Odds
- **Frequência**: A cada 15 minutos
- **Fonte**: The Odds API
- **Dados**: Odds em tempo real
- **Mercados**: H2H, Over/Under, BTTS

### 3. Análise de Valor
- **Frequência**: A cada 10 minutos
- **Processo**: Identificação de apostas com valor
- **Critérios**: EV ≥ 5%, confiança 70-90%
- **Output**: Predições recomendadas

### 4. Limpeza de Dados
- **Frequência**: Diariamente às 2:00
- **Processo**: Remoção de dados antigos
- **Critério**: Dados com mais de 30 dias
- **Preservação**: Mantém dados com predições

### 5. Relatório de Status
- **Frequência**: Diariamente às 8:00
- **Conteúdo**: Estatísticas do sistema
- **Métricas**: Partidas, odds, predições, performance
- **Armazenamento**: Logs e arquivo de relatório

## ⚙️ Configuração

### Tarefas Agendadas
```python
# Coleta de futebol - a cada 30 minutos
schedule.every(30).minutes.do(self._collect_football_data)

# Coleta de odds - a cada 15 minutos
schedule.every(15).minutes.do(self._collect_odds_data)

# Análise de valor - a cada 10 minutos
schedule.every(10).minutes.do(self._analyze_matches)

# Limpeza de dados - diariamente às 2:00
schedule.every().day.at("02:00").do(self._cleanup_old_data)

# Relatório de status - diariamente às 8:00
schedule.every().day.at("08:00").do(self._generate_status_report)
```

### Configurações de Sistema
```python
# settings/settings.py
COLLECTION_INTERVAL = 60  # segundos
MONITORED_LEAGUES = [39, 140, 78, 135, 61, 71]  # IDs das ligas
```

## 🚀 Como Usar

### 1. Executar Sistema
```bash
python run_automated_collector.py
```

### 2. Testar Sistema
```bash
python test_automated_collector.py
```

### 3. Parar Sistema
```bash
# Ctrl+C ou enviar sinal SIGTERM
```

## 📊 Monitoramento

### Logs Detalhados
```python
# logs/automated_collector.log
2025-10-14 18:30:00 - INFO - ⚽ Iniciando coleta de dados de futebol...
2025-10-14 18:30:15 - INFO - ✅ Coleta de dados de futebol concluída!
2025-10-14 18:30:20 - INFO - 🎯 Iniciando coleta de odds...
2025-10-14 18:30:35 - INFO - ✅ Coleta de odds concluída! Total: 150
```

### Status em Tempo Real
```python
status = collector.get_status()
print(f"Executando: {status['running']}")
print(f"Partidas: {status['total_matches']}")
print(f"Odds: {status['total_odds']}")
print(f"Predições: {status['total_predictions']}")
```

### Relatório Diário
```
📊 RELATÓRIO DE STATUS - 2025-10-14 08:00
==================================================
🗄️  BANCO DE DADOS:
   Partidas: 1,250
   Odds: 5,680
   Predições: 45
   Recomendadas: 12

📡 COLETORES:
   Futebol: 1,200 requisições
   Odds: 2,400 requisições

⏰ PRÓXIMAS EXECUÇÕES:
   Futebol: 2025-10-14 08:30:00
   Odds: 2025-10-14 08:15:00
   Análise: 2025-10-14 08:10:00
```

## 🔧 Operações de Banco de Dados

### Salvamento de Partidas
```python
def _save_matches_to_db(self, matches):
    for match_data in matches:
        match = Match(
            fixture_id=fixture.get('id'),
            league_id=match_data.get('league', {}).get('id'),
            home_team_name=teams.get('home', {}).get('name'),
            away_team_name=teams.get('away', {}).get('name'),
            # ... outros campos
        )
        self.db.add(match)
    self.db.commit()
```

### Salvamento de Odds
```python
def _save_odds_to_db(self, odds_list):
    for odds_data in odds_list:
        for bookmaker in odds_data.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                for outcome in market.get('outcomes', []):
                    odd = Odds(
                        fixture_id=fixture_id,
                        bookmaker=bookmaker.get('title'),
                        market=market.get('key'),
                        selection=outcome.get('name'),
                        odd=outcome.get('price')
                    )
                    self.db.add(odd)
    self.db.commit()
```

## 🧪 Testes

### Testes Incluídos
- ✅ Inicialização e componentes
- ✅ Configuração do agendamento
- ✅ Coleta de dados de futebol
- ✅ Coleta de dados de odds
- ✅ Análise de partidas
- ✅ Limpeza de dados
- ✅ Relatório de status
- ✅ Operações de banco
- ✅ Ciclo de vida do agendador

### Executar Testes
```bash
python test_automated_collector.py
```

## ⚠️ Limitações e Considerações

### API Keys
- **Requeridas**: Para coleta de dados reais
- **Limites**: Respeitados automaticamente
- **Fallback**: Sistema funciona sem keys (modo simulado)

### Recursos do Sistema
- **CPU**: Processamento contínuo
- **Memória**: Acúmulo de dados ao longo do tempo
- **Rede**: Requisições frequentes às APIs
- **Disco**: Crescimento do banco de dados

### Manutenção
- **Logs**: Rotação automática
- **Dados**: Limpeza diária
- **Performance**: Monitoramento contínuo

## 🔄 Extensibilidade

### Adicionar Nova Tarefa
```python
def _setup_schedule(self):
    # Tarefa existente
    schedule.every(30).minutes.do(self._collect_football_data)
    
    # Nova tarefa
    schedule.every(5).minutes.do(self._new_task)

def _new_task(self):
    logger.info("Executando nova tarefa...")
    # Implementar lógica da tarefa
```

### Personalizar Frequências
```python
def _setup_schedule(self):
    # Frequências personalizadas
    schedule.every(15).minutes.do(self._collect_football_data)
    schedule.every(5).minutes.do(self._collect_odds_data)
    schedule.every(2).minutes.do(self._analyze_matches)
```

### Adicionar Novos Coletores
```python
def __init__(self):
    self.football_collector = FootballCollector()
    self.odds_collector = OddsCollector()
    self.new_collector = NewCollector()  # Novo coletor
```

## 🐛 Solução de Problemas

### Erro: "API Key não configurada"
- **Causa**: Chaves não configuradas no .env
- **Solução**: Configurar API keys ou usar modo simulado
- **Verificação**: `python test_api_keys.py`

### Erro: "Thread não responde"
- **Causa**: Thread do agendador travada
- **Solução**: Reiniciar sistema
- **Prevenção**: Monitoramento de logs

### Erro: "Banco de dados cheio"
- **Causa**: Dados acumulados sem limpeza
- **Solução**: Executar limpeza manual
- **Prevenção**: Limpeza automática diária

### Erro: "Rate limit excedido"
- **Causa**: Muitas requisições às APIs
- **Solução**: Ajustar frequências
- **Prevenção**: Rate limiting automático

## 📈 Performance

### Métricas Recomendadas
- **Uptime**: >99%
- **Latência**: <5 segundos por tarefa
- **Throughput**: 100+ partidas/hora
- **Precisão**: >95% de dados válidos

### Otimizações
- **Threading**: Execução paralela
- **Caching**: Reutilização de dados
- **Batch Processing**: Processamento em lotes
- **Database Indexing**: Consultas otimizadas

## 🔒 Segurança

### Boas Práticas
- **API Keys**: Armazenadas em .env
- **Logs**: Sem informações sensíveis
- **Database**: Acesso restrito
- **Network**: HTTPS para APIs

### Monitoramento
- **Logs**: Análise de erros
- **Performance**: Métricas de sistema
- **Alerts**: Notificações de falhas
- **Backup**: Dados importantes

## 📚 Exemplos de Uso

### Execução Básica
```bash
# Iniciar sistema
python run_automated_collector.py

# Verificar status
python -c "from scheduler.automated_collector import AutomatedCollector; c = AutomatedCollector(); print(c.get_status())"

# Parar sistema
# Ctrl+C
```

### Execução com Docker
```dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "run_automated_collector.py"]
```

### Execução como Serviço
```bash
# systemd service
[Unit]
Description=MaraBet AI Automated Collector
After=network.target

[Service]
Type=simple
User=mara
WorkingDirectory=/opt/marabet
ExecStart=/usr/bin/python3 run_automated_collector.py
Restart=always

[Install]
WantedBy=multi-user.target
```
