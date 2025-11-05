# 🎯 Coletor de Odds - MaraBet AI

## 📋 Visão Geral

O `OddsCollector` é responsável pela coleta de odds de apostas da The Odds API, fornecendo dados em tempo real de múltiplas casas de apostas e ligas de futebol.

## 🏗️ Arquitetura

### Herança
- Herda de `BaseCollector`
- Implementa rate limiting automático
- Retry com backoff exponencial
- Logging detalhado

### Mapeamento de Esportes
```python
sports_map = {
    'soccer_epl': 'Premier League',
    'soccer_spain_la_liga': 'La Liga',
    'soccer_germany_bundesliga': 'Bundesliga',
    'soccer_italy_serie_a': 'Serie A',
    'soccer_france_ligue_one': 'Ligue 1',
    'soccer_brazil_campeonato': 'Brasileirão',
}
```

## 🚀 Funcionalidades

### 1. Lista de Esportes
```python
from coletores.odds_collector import OddsCollector

collector = OddsCollector()

# Obter lista de esportes disponíveis
sports = collector.get_sports()
print(f"Esportes disponíveis: {len(sports)}")
```

### 2. Coleta de Odds por Esporte
```python
# Odds da Premier League
epl_odds = collector.get_odds('soccer_epl')

# Odds da La Liga
laliga_odds = collector.get_odds('soccer_spain_la_liga')

# Odds com regiões específicas
uk_odds = collector.get_odds('soccer_epl', regions='uk')

# Odds com mercados específicos
h2h_odds = collector.get_odds('soccer_epl', markets='h2h')
```

### 3. Coleta de Todas as Ligas
```python
# Coletar odds de todas as ligas de futebol
all_odds = collector.get_all_football_odds()

for league, odds_list in all_odds.items():
    print(f"{league}: {len(odds_list)} jogos")
```

### 4. Método Principal de Coleta
```python
# Usar o método collect() com parâmetros
odds = collector.collect(sport='soccer_epl')
```

## 🔧 Parâmetros de Configuração

### Regiões Suportadas
- `uk`: Reino Unido
- `us`: Estados Unidos
- `eu`: Europa
- `au`: Austrália

### Mercados Disponíveis
- `h2h`: Match Winner (1X2)
- `spreads`: Handicap
- `totals`: Over/Under

### Formato de Odds
- `decimal`: Formato decimal (1.85, 2.50, etc.)

## 📊 Estrutura dos Dados

### Exemplo de Odds Coletadas
```json
{
  "id": "12345",
  "sport_key": "soccer_epl",
  "sport_title": "Soccer",
  "commence_time": "2024-01-15T15:00:00Z",
  "home_team": "Manchester City",
  "away_team": "Arsenal",
  "bookmakers": [
    {
      "key": "bet365",
      "title": "Bet365",
      "markets": [
        {
          "key": "h2h",
          "outcomes": [
            {
              "name": "Manchester City",
              "price": 1.85
            },
            {
              "name": "Arsenal", 
              "price": 3.20
            },
            {
              "name": "Draw",
              "price": 3.50
            }
          ]
        }
      ]
    }
  ]
}
```

## 🧪 Testes

### Executar Testes
```bash
python test_odds_collector.py
```

### Testes Incluídos
- ✅ Importação de módulos
- ✅ Herança de classes
- ✅ Implementação de métodos abstratos
- ✅ Mapeamento de esportes
- ✅ Coleta de esportes disponíveis
- ✅ Coleta de odds por esporte
- ✅ Coleta de todas as ligas
- ✅ Diferentes parâmetros (regiões, mercados)
- ✅ Tratamento de erros

## 📈 Monitoramento

### Logs Detalhados
```python
import logging
logging.basicConfig(level=logging.INFO)

# Logs incluem:
# - Coleta de esportes
# - Coleta de odds por esporte
# - Número de jogos coletados
# - Erros de coleta
```

### Estatísticas
```python
stats = collector.get_stats()
print(f"Total de requisições: {stats['total_requests']}")
print(f"Tipo de coletor: {stats['collector_type']}")
```

## ⚠️ Limitações e Considerações

### The Odds API
- **Gratuito**: 500 requests/mês
- **Rate Limit**: 1 request/segundo
- **Timeout**: 30 segundos
- **Erro 403**: API key inválida ou não configurada

### Tratamento de Erros
- **403 Forbidden**: API key inválida
- **429 Too Many Requests**: Rate limit excedido
- **Timeout**: Requisição demorou muito
- **Network Error**: Problema de conexão

## 🔄 Uso Avançado

### Exemplo Completo
```python
from coletores.odds_collector import OddsCollector
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Criar coletor
collector = OddsCollector()

# Coletar esportes disponíveis
sports = collector.get_sports()
soccer_sports = [s for s in sports if 'soccer' in s.get('key', '')]
print(f"Esportes de futebol: {len(soccer_sports)}")

# Coletar odds da Premier League
epl_odds = collector.get_odds('soccer_epl')
print(f"Odds EPL: {len(epl_odds)}")

# Coletar odds de todas as ligas
all_odds = collector.get_all_football_odds()
for league, odds in all_odds.items():
    print(f"{league}: {len(odds)} jogos")

# Verificar estatísticas
stats = collector.get_stats()
print(f"Requisições: {stats['total_requests']}")
```

### Filtros e Parâmetros
```python
# Apenas odds do Reino Unido
uk_odds = collector.get_odds('soccer_epl', regions='uk')

# Apenas mercado Match Winner
h2h_odds = collector.get_odds('soccer_epl', markets='h2h')

# Múltiplas regiões
multi_region = collector.get_odds('soccer_epl', regions='uk,us,eu')

# Múltiplos mercados
multi_market = collector.get_odds('soccer_epl', markets='h2h,spreads,totals')
```

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

## 📊 Performance

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

## 🔄 Extensibilidade

### Adicionar Nova Liga
```python
# No construtor da classe
self.sports_map['soccer_new_league'] = 'Nova Liga'
```

### Personalizar Parâmetros
```python
# Criar método personalizado
def get_custom_odds(self, sport, custom_params):
    return self._make_request(
        f'sports/{sport}/odds',
        params={
            'apiKey': self.api_key,
            **custom_params
        }
    )
```
