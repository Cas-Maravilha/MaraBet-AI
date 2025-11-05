# 🔍 Coletores de Dados - MaraBet AI

## 📋 Visão Geral

O sistema de coletores permite a coleta automatizada de dados esportivos e odds de apostas de diferentes APIs. Todos os coletores herdam de uma classe base que implementa funcionalidades comuns como rate limiting, retry automático e logging.

## 🏗️ Arquitetura

### BaseCollector (Classe Abstrata)
- **Rate Limiting**: Controla a frequência das requisições
- **Retry Automático**: Tenta novamente em caso de falha
- **Logging**: Registra todas as operações
- **Estatísticas**: Conta requisições realizadas

### Coletores Específicos
- **FootballCollector**: Dados da API-Football
- **OddsCollector**: Odds da The Odds API

## ⚽ FootballCollector

### Funcionalidades
- Coleta de partidas por liga
- Tabelas de classificação
- Estatísticas de times
- Eventos de partidas
- Estatísticas de partidas específicas

### Métodos Principais
```python
from coletores.football_collector import FootballCollector

collector = FootballCollector()

# Coletar partidas de uma liga
matches = collector.collect_matches(league_id=39, season=2024)

# Coletar classificação
standings = collector.collect_league_standings(league_id=39)

# Coletar estatísticas de time
stats = collector.collect_team_statistics(team_id=1)

# Coletar todas as ligas monitoradas
all_matches = collector.collect_all_monitored_leagues(days=7)
```

### Ligas Monitoradas

> **Foco Principal**: As casas de apostas em Angola focam nas principais ligas mundiais (Europa, América do Sul, América do Norte, Ásia e África), não necessariamente nas ligas locais angolanas.

#### 🌍 **Ligas Mundiais Focadas pelas Casas Angolanas**

**Priorização por Região:**
- **🇪🇺 Europa**: Prioridade máxima (Premier League, La Liga, Bundesliga, Serie A, Ligue 1, Champions League)
- **🇧🇷 América do Sul**: Prioridade alta (Brasileirão, Primera División, Copa Libertadores)
- **🇺🇸 América do Norte**: Prioridade média (MLS, Liga MX)
- **🇯🇵 Ásia**: Prioridade média (J League, K League, Chinese Super League)
- **🌍 África**: Prioridade média (Premier Soccer League, CAF Champions League)

**Ligas por Prioridade:**

##### **🥇 Prioridade Máxima (Europa)**

> **Foco Principal**: As casas de apostas em Angola focam nas principais ligas mundiais (Europa, América do Sul, América do Norte, Ásia e África), não necessariamente nas ligas locais angolanas.
- **Premier League** (39) - Inglaterra
- **La Liga** (140) - Espanha
- **Bundesliga** (78) - Alemanha
- **Serie A** (135) - Itália
- **Ligue 1** (61) - França
- **UEFA Champions League** (2) - Europa

##### **🥈 Prioridade Alta (América do Sul)**
- **Brasileirão Série A** (71) - Brasil
- **Primera División** (128) - Argentina
- **Copa Libertadores** (13) - América do Sul
- **Primera A** (239) - Colômbia

##### **🥉 Prioridade Média (América do Norte)**
- **Major League Soccer** (253) - EUA/Canadá
- **Liga MX** (262) - México

##### **🥉 Prioridade Média (Ásia)**
- **J1 League** (98) - Japão
- **K League 1** (292) - Coreia do Sul
- **Chinese Super League** (169) - China

##### **🥉 Prioridade Média (África)**
- **Premier Soccer League** (384) - África do Sul
- **CAF Champions League** (14) - África
- **Egyptian Premier League** (307) - Egito
- **Premier League** (39) - Inglaterra
- **La Liga** (140) - Espanha
- **Bundesliga** (78) - Alemanha
- **Serie A** (135) - Itália
- **Ligue 1** (61) - França
- **UEFA Champions League** (2) - Europa
- **Brasileirão Série A** (71) - Brasil
- **Primera División** (128) - Argentina
- **Copa Libertadores** (13) - América do Sul
- **Major League Soccer** (253) - EUA/Canadá
- **J1 League** (98) - Japão
- **K League 1** (292) - Coreia do Sul
- **Premier Soccer League** (384) - África do Sul
- **CAF Champions League** (14) - África

## 🎯 OddsCollector

### Funcionalidades
- Lista de esportes disponíveis
- Odds em tempo real
- Odds por liga específica
- Odds históricas
- Resultados de partidas

### Métodos Principais
```python
from coletores.odds_collector import OddsCollector

collector = OddsCollector()

# Coletar esportes disponíveis
sports = collector.collect_sports()

# Coletar odds de futebol
odds = collector.collect_odds(sport='soccer')

# Coletar odds de liga específica
epl_odds = collector.collect_odds_by_league(league='soccer_epl')

# Coletar odds históricas
historical = collector.collect_historical_odds(date='2024-01-15')

# Coletar resultados
scores = collector.collect_scores(days_from=1)
```

## 🔧 Configuração

### 1. API Keys
Configure no arquivo `.env`:
```bash
API_FOOTBALL_KEY=sua_chave_api_football
THE_ODDS_API_KEY=sua_chave_the_odds_api
```

### 2. Rate Limiting
Configurado automaticamente:
- **API-Football**: 1 requisição por segundo
- **The Odds API**: 1 requisição por segundo
- **Retry**: 3 tentativas com backoff exponencial

### 3. Timeouts
- **Request Timeout**: 30 segundos
- **Max Retries**: 3 tentativas

## 🚀 Uso Básico

### Exemplo Completo
```python
from coletores.football_collector import FootballCollector
from coletores.odds_collector import OddsCollector

# Coletar dados de futebol
football = FootballCollector()
matches = football.collect(league_id=39, days=7)

# Coletar odds
odds = OddsCollector()
odds_data = odds.collect(sport='soccer')

# Verificar estatísticas
print(f"Requisições futebol: {football.get_stats()['total_requests']}")
print(f"Requisições odds: {odds.get_stats()['total_requests']}")
```

## 🧪 Testes

### Executar Testes
```bash
python test_collectors.py
```

### Testes Incluídos
- ✅ Importação de módulos
- ✅ Herança de classes
- ✅ Implementação de métodos abstratos
- ✅ Coleta de dados (com API keys)
- ✅ Rate limiting
- ✅ Tratamento de erros

## 📊 Monitoramento

### Logs
Todos os coletores geram logs detalhados:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Estatísticas
```python
stats = collector.get_stats()
print(f"Total de requisições: {stats['total_requests']}")
print(f"Tipo de coletor: {stats['collector_type']}")
```

## ⚠️ Limitações

### API-Football
- **Gratuito**: 100 requests/dia
- **Rate Limit**: 1 request/segundo
- **Timeout**: 30 segundos

### The Odds API
- **Gratuito**: 500 requests/mês
- **Rate Limit**: 1 request/segundo
- **Timeout**: 30 segundos

## 🔄 Extensibilidade

### Criar Novo Coletor
```python
from coletores.base_collector import BaseCollector

class MeuColetor(BaseCollector):
    def __init__(self):
        super().__init__(api_key="minha_key", base_url="https://api.exemplo.com")
    
    def collect(self, **kwargs):
        # Implementar lógica de coleta
        return self._make_request('endpoint', params=kwargs)
```

### Adicionar ao Sistema
1. Criar arquivo no diretório `coletores/`
2. Herdar de `BaseCollector`
3. Implementar método `collect()`
4. Adicionar ao `__init__.py`

## 🐛 Solução de Problemas

### Erro: "API Key não configurada"
- Verifique o arquivo `.env`
- Execute `python test_api_keys.py`

### Erro: "Rate limit exceeded"
- Aguarde antes de fazer nova requisição
- Verifique limites da API

### Erro: "Request timeout"
- Verifique conexão com internet
- Aumente `REQUEST_TIMEOUT` se necessário

### Erro: "Max retries exceeded"
- Verifique se a API está funcionando
- Verifique se as credenciais estão corretas
