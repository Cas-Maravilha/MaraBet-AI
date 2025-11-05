# 🗄️ Schema do Banco de Dados - MaraBet AI

## 📊 Estrutura das Tabelas

### 1. **matches** - Partidas
Armazena informações sobre as partidas de futebol.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer | Chave primária |
| `fixture_id` | Integer | ID único da partida (API) |
| `league_id` | Integer | ID da liga |
| `league_name` | String | Nome da liga |
| `date` | DateTime | Data e hora da partida |
| `home_team_id` | Integer | ID do time da casa |
| `home_team_name` | String | Nome do time da casa |
| `away_team_id` | Integer | ID do time visitante |
| `away_team_name` | String | Nome do time visitante |
| `status` | String | Status da partida (NS, 1H, 2H, FT, etc.) |
| `elapsed_time` | Integer | Tempo decorrido (minutos) |
| `home_score` | Integer | Gols do time da casa |
| `away_score` | Integer | Gols do time visitante |
| `statistics` | JSON | Estatísticas da partida |
| `events` | JSON | Eventos da partida |
| `created_at` | DateTime | Data de criação |
| `updated_at` | DateTime | Data de atualização |

### 2. **odds** - Odds de Apostas
Armazena as odds de apostas de diferentes casas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer | Chave primária |
| `fixture_id` | Integer | ID da partida |
| `bookmaker` | String | Casa de apostas |
| `market` | String | Mercado (Match Winner, Over/Under, etc.) |
| `selection` | String | Seleção (Home, Away, Draw, etc.) |
| `odd` | Float | Valor da odd |
| `timestamp` | DateTime | Data/hora da coleta |

### 3. **predictions** - Predições
Armazena as predições geradas pelo sistema.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer | Chave primária |
| `fixture_id` | Integer | ID da partida |
| `market` | String | Mercado da predição |
| `selection` | String | Seleção predita |
| `predicted_probability` | Float | Probabilidade predita |
| `implied_probability` | Float | Probabilidade implícita da odd |
| `recommended_odd` | Float | Odd recomendada |
| `current_odd` | Float | Odd atual |
| `expected_value` | Float | Valor esperado (EV) |
| `confidence` | Float | Nível de confiança |
| `stake_percentage` | Float | Percentual da banca |
| `recommended` | Boolean | Se é recomendada |
| `factors` | JSON | Fatores de justificativa |
| `created_at` | DateTime | Data de criação |

### 4. **betting_history** - Histórico de Apostas
Armazena o histórico de apostas realizadas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer | Chave primária |
| `prediction_id` | Integer | ID da predição |
| `fixture_id` | Integer | ID da partida |
| `stake` | Float | Valor apostado |
| `odd` | Float | Odd da aposta |
| `potential_return` | Float | Retorno potencial |
| `result` | String | Resultado (win, loss, pending) |
| `profit_loss` | Float | Lucro/Prejuízo |
| `placed_at` | DateTime | Data da aposta |
| `settled_at` | DateTime | Data da liquidação |

## 🔧 Funcionalidades

### Inserção de Dados
```python
from armazenamento.banco_de_dados import *

# Criar sessão
db = SessionLocal()

# Inserir partida
match = Match(
    fixture_id=12345,
    league_id=39,
    league_name="Premier League",
    date=datetime.now(),
    home_team_name="Manchester City",
    away_team_name="Arsenal"
)
db.add(match)
db.commit()
```

### Consultas
```python
# Buscar partidas por liga
matches = db.query(Match).filter(Match.league_id == 39).all()

# Buscar predições recomendadas
recommendations = db.query(Prediction).filter(Prediction.recommended == True).all()

# Buscar histórico de apostas
bets = db.query(BettingHistory).filter(BettingHistory.result == "win").all()
```

### Atualizações
```python
# Atualizar resultado da partida
match = db.query(Match).filter(Match.fixture_id == 12345).first()
match.home_score = 2
match.away_score = 1
match.status = "FT"
db.commit()
```

## 📈 Índices

O banco possui índices otimizados para:
- `fixture_id` (partidas e odds)
- `league_id` (filtros por liga)
- `date` (filtros temporais)
- `timestamp` (odds por data)
- `recommended` (predições recomendadas)

## 🚀 Teste do Banco

Execute o script de teste:
```bash
python test_database.py
```

## 📊 Estatísticas

Para verificar estatísticas do banco:
```python
from armazenamento.banco_de_dados import *

db = SessionLocal()
matches_count = db.query(Match).count()
odds_count = db.query(Odds).count()
predictions_count = db.query(Prediction).count()
betting_count = db.query(BettingHistory).count()
db.close()
```

## 🔄 Backup e Restauração

O banco SQLite é armazenado em:
```
data/sports_data.db
```

Para backup:
```bash
cp data/sports_data.db backup/sports_data_backup.db
```

Para restaurar:
```bash
cp backup/sports_data_backup.db data/sports_data.db
```
