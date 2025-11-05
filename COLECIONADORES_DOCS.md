# 🔍 Colecionadores de Dados - MaraBet AI

## 📋 Visão Geral

O sistema de colecionadores permite a coleta automatizada de dados esportivos de forma organizada e eficiente. Todos os colecionadores herdam de uma classe base que implementa funcionalidades comuns como rate limiting, retry automático e logging detalhado.

## 🏗️ Arquitetura

### BaseCollector (Classe Abstrata)
- **Rate Limiting**: Controla a frequência das requisições (1 req/s)
- **Retry Automático**: 3 tentativas com backoff exponencial
- **Logging Detalhado**: Registra todas as operações
- **Estatísticas**: Conta requisições realizadas
- **Tratamento de Erros**: Gerencia erros de API e rede

### FootballCollector (Colecionador de Futebol)
- **Partidas ao Vivo**: Coleta partidas em andamento
- **Partidas por Data**: Coleta partidas de um dia específico
- **Partidas por Liga**: Coleta partidas de uma liga específica
- **Estatísticas de Partida**: Coleta estatísticas detalhadas
- **Eventos de Partida**: Coleta gols, cartões, substituições
- **Confrontos Diretos**: Coleta histórico H2H entre times
- **Estatísticas de Time**: Coleta estatísticas de times

## ⚽ FootballCollector

### Funcionalidades Principais

#### 1. Coleta de Partidas
```python
from colecionadores.football_collector import FootballCollector

collector = FootballCollector()

# Partidas ao vivo
live_matches = collector.get_live_matches()

# Partidas de hoje
today_matches = collector.get_fixtures_by_date()

# Partidas de data específica
matches = collector.get_fixtures_by_date('2024-01-15')

# Partidas de uma liga
epl_matches = collector.get_fixtures_by_league(39, 2024)
```

#### 2. Detalhes de Partidas
```python
# Estatísticas de uma partida
stats = collector.get_match_statistics(fixture_id=12345)

# Eventos de uma partida
events = collector.get_match_events(fixture_id=12345)

# Confrontos diretos
h2h = collector.get_h2h(team1_id=1, team2_id=2, last=10)

# Estatísticas de time
team_stats = collector.get_team_statistics(team_id=1, league_id=39, season=2024)
```

#### 3. Modos de Coleta
```python
# Modo live - partidas ao vivo
live = collector.collect(mode='live')

# Modo today - partidas de hoje
today = collector.collect(mode='today')

# Modo date - partidas de data específica
date = collector.collect(mode='date', date='2024-01-15')

# Modo league - partidas de liga específica
league = collector.collect(mode='league', league_id=39, season=2024)
```

## 🔧 Configuração

### 1. API Keys
Configure no arquivo `.env`:
```bash
API_FOOTBALL_KEY=sua_chave_api_football
API_FOOTBALL_HOST=v3.football.api-sports.io
```

### 2. Rate Limiting
- **Intervalo**: 1 requisição por segundo
- **Controle**: Automático via `_rate_limit()`
- **Logs**: Debug de tempo de espera

### 3. Retry e Timeout
- **Max Retries**: 3 tentativas
- **Backoff**: Exponencial (2^attempt)
- **Timeout**: 30 segundos por requisição
- **Rate Limit 429**: Aguarda antes de tentar novamente

## 🚀 Uso Avançado

### Exemplo Completo
```python
from colecionadores.football_collector import FootballCollector
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Criar colecionador
collector = FootballCollector()

# Coletar dados
print("Coletando partidas ao vivo...")
live_matches = collector.collect(mode='live')
print(f"Partidas ao vivo: {len(live_matches)}")

print("Coletando partidas de hoje...")
today_matches = collector.collect(mode='today')
print(f"Partidas de hoje: {len(today_matches)}")

# Verificar estatísticas
stats = collector.get_stats()
print(f"Requisições feitas: {stats['total_requests']}")
```

### Tratamento de Erros
```python
try:
    matches = collector.get_live_matches()
    if matches:
        print(f"Sucesso: {len(matches)} partidas")
    else:
        print("Nenhuma partida encontrada")
except Exception as e:
    print(f"Erro na coleta: {e}")
```

## 🧪 Testes

### Executar Testes
```bash
python test_colecionadores.py
```

### Testes Incluídos
- ✅ Importação de módulos
- ✅ Herança de classes
- ✅ Implementação de métodos abstratos
- ✅ Diferentes modos de coleta
- ✅ Métodos específicos
- ✅ Tratamento de erros
- ✅ Rate limiting
- ✅ Estatísticas

## 📊 Monitoramento

### Logs Detalhados
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Logs incluem:
# - Rate limiting
# - Requisições realizadas
# - Erros e retries
# - Estatísticas de coleta
```

### Estatísticas
```python
stats = collector.get_stats()
print(f"Total de requisições: {stats['total_requests']}")
print(f"Tipo de colecionador: {stats['collector_type']}")
```

## ⚠️ Limitações e Considerações

### API-Football
- **Gratuito**: 100 requests/dia
- **Rate Limit**: 1 request/segundo
- **Timeout**: 30 segundos
- **Erro 403**: API key inválida ou não configurada

### Tratamento de Erros
- **403 Forbidden**: API key inválida
- **429 Too Many Requests**: Rate limit excedido
- **Timeout**: Requisição demorou muito
- **Network Error**: Problema de conexão

## 🔄 Extensibilidade

### Criar Novo Colecionador
```python
from colecionadores.base_collector import BaseCollector

class MeuColecionador(BaseCollector):
    def __init__(self):
        super().__init__(
            api_key="minha_key", 
            base_url="https://api.exemplo.com"
        )
        self.headers = {'Authorization': f'Bearer {self.api_key}'}
    
    def collect(self, **kwargs):
        # Implementar lógica de coleta
        return self._make_request('endpoint', params=kwargs)
```

### Adicionar ao Sistema
1. Criar arquivo no diretório `colecionadores/`
2. Herdar de `BaseCollector`
3. Implementar método `collect()`
4. Adicionar ao `__init__.py`

## 🐛 Solução de Problemas

### Erro: "403 Forbidden"
- Verifique se a API key está correta
- Confirme se a conta está ativa
- Execute `python test_api_keys.py`

### Erro: "429 Too Many Requests"
- O sistema aguarda automaticamente
- Verifique se não há múltiplas instâncias rodando
- Considere aumentar o intervalo de rate limiting

### Erro: "Request timeout"
- Verifique conexão com internet
- Aumente `REQUEST_TIMEOUT` se necessário
- Verifique se a API está funcionando

### Erro: "Max retries exceeded"
- Verifique se a API está funcionando
- Confirme se as credenciais estão corretas
- Verifique se não há problemas de rede

## 📈 Performance

### Otimizações Implementadas
- **Session Reuse**: Reutiliza conexões HTTP
- **Rate Limiting**: Evita bloqueios por API
- **Retry Inteligente**: Backoff exponencial
- **Logging Eficiente**: Apenas quando necessário

### Métricas Recomendadas
- **Requisições/minuto**: Máximo 60
- **Taxa de sucesso**: >95%
- **Tempo médio de resposta**: <5 segundos
- **Retries por requisição**: <1 em média
