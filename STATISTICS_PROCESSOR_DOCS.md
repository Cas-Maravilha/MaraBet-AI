# 📊 Processador de Estatísticas - MaraBet AI

## 📋 Visão Geral

O `StatisticsProcessor` é responsável por processar e calcular estatísticas esportivas avançadas, incluindo forma dos times, médias de gols, probabilidades Poisson, expected goals (xG), valor de apostas e critério de Kelly.

## 🏗️ Funcionalidades

### 1. Cálculo de Forma
Calcula a forma recente de um time baseado nos últimos jogos.

```python
from processadores.statistics import StatisticsProcessor

matches = [
    {'result': 'W', 'goals_scored': 2, 'goals_conceded': 1},
    {'result': 'D', 'goals_scored': 1, 'goals_conceded': 1},
    {'result': 'W', 'goals_scored': 3, 'goals_conceded': 0},
    {'result': 'L', 'goals_scored': 0, 'goals_conceded': 2},
    {'result': 'W', 'goals_scored': 1, 'goals_conceded': 0},
]

form = StatisticsProcessor.calculate_form(matches, last_n=5)
# Retorna: {'points': 10, 'wins': 3, 'draws': 1, 'losses': 1, 'win_rate': 0.6, 'points_per_game': 2.0}
```

### 2. Médias de Gols
Calcula estatísticas de gols marcados e sofridos.

```python
goals_stats = StatisticsProcessor.calculate_goals_average(matches)
# Retorna: {'scored_avg': 1.4, 'conceded_avg': 0.8, 'total_avg': 2.2, 'scored_std': 1.02, 'conceded_std': 0.75}
```

### 3. Probabilidades Poisson
Calcula probabilidades de resultados usando distribuição de Poisson.

```python
probs = StatisticsProcessor.calculate_poisson_probability(avg_home=1.5, avg_away=1.2)
# Retorna: {
#   'home_win': 0.4415, 'draw': 0.2548, 'away_win': 0.3037,
#   'over_25': 0.5064, 'under_25': 0.4936,
#   'btts_yes': 0.5429, 'btts_no': 0.4571
# }
```

### 4. Expected Goals (xG)
Calcula expected goals baseado em estatísticas do jogo.

```python
stats = {
    'shots_on_target': 5,
    'possession': 60,
    'dangerous_attacks': 8
}

xg = StatisticsProcessor.calculate_expected_goals(stats)
# Retorna: 1.8
```

### 5. Cálculo de Valor
Calcula valor esperado de uma aposta.

```python
value = StatisticsProcessor.calculate_value(probability=0.6, odd=1.8)
# Retorna: {
#   'probability': 0.6, 'implied_probability': 0.5556, 'edge': 0.0444,
#   'expected_value': 0.08, 'has_value': True, 'value_percentage': 4.44
# }
```

### 6. Critério de Kelly
Calcula o tamanho ideal da aposta usando critério de Kelly.

```python
kelly = StatisticsProcessor.kelly_criterion(probability=0.6, odd=1.8, fraction=0.25)
# Retorna: 0.025 (2.5% da banca)
```

## 🧮 Algoritmos Implementados

### Distribuição de Poisson
- **Uso**: Modelagem de gols em futebol
- **Parâmetros**: Média de gols marcados e sofridos
- **Saída**: Probabilidades de resultados e mercados

### Expected Goals (xG)
- **Fórmula**: `(shots_on_target * 0.1) + (possession * 1.5) + (dangerous_attacks * 0.05)`
- **Uso**: Avaliação de performance ofensiva
- **Limitações**: Modelo simplificado (pode ser expandido)

### Critério de Kelly
- **Fórmula**: `((odd * probability) - 1) / (odd - 1) * fraction`
- **Uso**: Gestão de banca otimizada
- **Limitações**: 0% a 10% da banca, Kelly fracionado

## 📊 Métricas Calculadas

### Forma do Time
- **Pontos**: Total de pontos nos últimos N jogos
- **Vitórias/Empates/Derrotas**: Contagem de resultados
- **Taxa de Vitórias**: Percentual de vitórias
- **Pontos por Jogo**: Média de pontos por partida

### Estatísticas de Gols
- **Média Marcados**: Gols marcados por jogo
- **Média Sofridos**: Gols sofridos por jogo
- **Total**: Soma das médias
- **Desvio Padrão**: Variabilidade dos gols

### Probabilidades de Mercados
- **1X2**: Vitória casa, empate, vitória visitante
- **Over/Under 2.5**: Mais/menos de 2.5 gols
- **BTTS**: Ambas marcam/não marcam

## 🧪 Testes

### Executar Testes
```bash
python test_statistics_processor.py
```

### Testes Incluídos
- ✅ Cálculo de forma
- ✅ Médias de gols
- ✅ Probabilidades Poisson
- ✅ Expected Goals
- ✅ Cálculo de valor
- ✅ Critério de Kelly
- ✅ Casos extremos

## 📈 Exemplos de Uso

### Análise Completa de Time
```python
from processadores.statistics import StatisticsProcessor

# Dados de partidas
matches = [
    {'result': 'W', 'goals_scored': 2, 'goals_conceded': 1},
    {'result': 'D', 'goals_scored': 1, 'goals_conceded': 1},
    {'result': 'W', 'goals_scored': 3, 'goals_conceded': 0},
    {'result': 'L', 'goals_scored': 0, 'goals_conceded': 2},
    {'result': 'W', 'goals_scored': 1, 'goals_conceded': 0},
]

# Calcular estatísticas
form = StatisticsProcessor.calculate_form(matches)
goals = StatisticsProcessor.calculate_goals_average(matches)

print(f"Forma: {form['wins']}V-{form['draws']}E-{form['losses']}D")
print(f"Gols: {goals['scored_avg']:.1f} marcados, {goals['conceded_avg']:.1f} sofridos")
```

### Análise de Aposta
```python
# Calcular probabilidades
probs = StatisticsProcessor.calculate_poisson_probability(1.5, 1.2)

# Calcular valor da aposta
value = StatisticsProcessor.calculate_value(probs['home_win'], 2.0)

# Calcular stake ideal
stake = StatisticsProcessor.kelly_criterion(probs['home_win'], 2.0)

if value['has_value']:
    print(f"✅ Aposta com valor! Stake: {stake:.1%}")
else:
    print("❌ Aposta sem valor")
```

## ⚠️ Limitações e Considerações

### Expected Goals
- **Modelo Simplificado**: Fórmula básica para demonstração
- **Melhorias**: Implementar modelos mais complexos
- **Dados**: Requer estatísticas detalhadas do jogo

### Critério de Kelly
- **Conservador**: Usa Kelly fracionado (25%)
- **Limites**: Máximo 10% da banca
- **Risco**: Pode ser agressivo em alguns casos

### Probabilidades Poisson
- **Assunção**: Gols independentes e aleatórios
- **Realidade**: Futebol tem fatores contextuais
- **Melhorias**: Ajustar por força dos times

## 🔄 Extensibilidade

### Adicionar Novas Métricas
```python
@staticmethod
def calculate_new_metric(data):
    # Implementar nova métrica
    return result
```

### Personalizar xG
```python
@staticmethod
def calculate_advanced_xg(statistics):
    # Implementar modelo mais complexo
    shots = statistics.get('shots', 0)
    shots_on_target = statistics.get('shots_on_target', 0)
    possession = statistics.get('possession', 50) / 100
    
    # Fórmula mais sofisticada
    xg = (shots_on_target * 0.15) + (shots * 0.05) + (possession * 2.0)
    return round(xg, 2)
```

### Adicionar Novos Mercados
```python
@staticmethod
def calculate_custom_probabilities(avg_home, avg_away):
    # Implementar novos mercados
    # Ex: Over/Under 1.5, 3.5, etc.
    pass
```

## 🐛 Solução de Problemas

### Erro: "Division by zero"
- Verificar se lista de partidas não está vazia
- Adicionar validações antes dos cálculos

### Erro: "Invalid probability"
- Verificar se probabilidades estão entre 0 e 1
- Validar entradas antes dos cálculos

### Erro: "Kelly too high"
- Verificar se odd > 1
- Verificar se probabilidade > 0
- Usar Kelly fracionado mais conservador

## 📊 Performance

### Otimizações
- **NumPy**: Cálculos vetorizados
- **Scipy**: Funções estatísticas otimizadas
- **Caching**: Reutilizar cálculos quando possível

### Complexidade
- **Forma**: O(n) onde n = número de partidas
- **Poisson**: O(max_goals²)
- **Kelly**: O(1)
- **xG**: O(1)
