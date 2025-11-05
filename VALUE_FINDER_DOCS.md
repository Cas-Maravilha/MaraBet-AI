# 🔍 Value Finder - MaraBet AI

## 📋 Visão Geral

O `ValueFinder` é o componente central do sistema MaraBet AI responsável por identificar apostas com valor positivo. Ele analisa partidas de futebol, calcula probabilidades reais, compara com odds disponíveis e identifica oportunidades de apostas lucrativas.

## 🏗️ Arquitetura

### Componentes Principais
- **StatisticsProcessor**: Calcula estatísticas e probabilidades
- **Database**: Armazena predições e dados históricos
- **Settings**: Configurações de critérios mínimos

### Fluxo de Análise
1. **Cálculo de Probabilidades**: Usa modelo de ML para calcular probabilidades reais
2. **Busca de Valor**: Compara probabilidades com odds disponíveis
3. **Verificação de Critérios**: Aplica filtros de qualidade
4. **Cálculo de Stake**: Determina tamanho ideal da aposta
5. **Armazenamento**: Salva predição no banco de dados

## 🚀 Funcionalidades

### 1. Análise de Partidas
```python
from análise.value_finder import ValueFinder

value_finder = ValueFinder()

# Dados da partida
match_data = {
    'fixture': {'id': 12345},
    'teams': {
        'home': {'name': 'Manchester City'},
        'away': {'name': 'Arsenal'}
    }
}

# Dados das odds
odds_data = [
    {
        'bookmakers': [
            {
                'markets': [
                    {
                        'key': 'h2h',
                        'outcomes': [
                            {'name': 'Home', 'price': 2.0},
                            {'name': 'Draw', 'price': 3.2},
                            {'name': 'Away', 'price': 4.0}
                        ]
                    }
                ]
            }
        ]
    }
]

# Analisar partida
prediction = value_finder.analyze_match(match_data, odds_data)
```

### 2. Cálculo de Probabilidades
```python
# Probabilidades calculadas pelo modelo
probabilities = {
    'home_win': 0.45,    # 45% chance de vitória da casa
    'draw': 0.30,        # 30% chance de empate
    'away_win': 0.25,    # 25% chance de vitória visitante
    'over_25': 0.68,     # 68% chance de mais de 2.5 gols
    'under_25': 0.32,    # 32% chance de menos de 2.5 gols
    'btts_yes': 0.58,    # 58% chance de ambas marcarem
    'btts_no': 0.42      # 42% chance de não marcarem ambas
}
```

### 3. Identificação de Valor
```python
# Exemplo de valor encontrado
best_value = {
    'market': 'totals',
    'selection': 'Over',
    'probability': 0.68,           # 68% chance real
    'implied_probability': 0.556,  # 55.6% chance implícita (1/1.8)
    'odd': 1.8,                    # Odd disponível
    'ev': 0.224,                   # 22.4% de valor esperado
    'confidence': 0.792,           # 79.2% de confiança
    'factors': {...}               # Fatores justificativos
}
```

### 4. Critérios de Qualidade
- **Valor Mínimo**: EV ≥ 5% (configurável)
- **Confiança**: Entre 70% e 90% (configurável)
- **Stake**: Calculado via critério de Kelly

## 🧮 Algoritmos Implementados

### Mapeamento de Mercados
```python
mapping = {
    'h2h': {
        'Home': 'home_win',
        'Draw': 'draw', 
        'Away': 'away_win'
    },
    'totals': {
        'Over': 'over_25',
        'Under': 'under_25'
    }
}
```

### Cálculo de Confiança
```python
def _calculate_confidence(self, value, probabilities):
    base_confidence = value['probability']
    ev_boost = min(value['expected_value'] * 0.5, 0.15)
    return min(base_confidence + ev_boost, 0.95)
```

### Critério de Kelly
```python
def _calculate_stake(self, value):
    return self.stats_processor.kelly_criterion(
        value['probability'],
        value['odd'],
        fraction=0.25  # Kelly fracionado
    )
```

## 📊 Métricas Calculadas

### Valor Esperado (EV)
- **Fórmula**: `(probabilidade * odd) - 1`
- **Uso**: Identifica apostas lucrativas
- **Critério**: EV ≥ 5% (configurável)

### Confiança
- **Base**: Probabilidade do modelo
- **Boost**: Aumento baseado no EV
- **Limite**: Máximo 95%

### Stake Recomendado
- **Método**: Critério de Kelly fracionado
- **Fração**: 25% do Kelly completo
- **Limite**: 0% a 10% da banca

## 🧪 Testes

### Executar Testes
```bash
python test_value_finder.py
```

### Testes Incluídos
- ✅ Inicialização e componentes
- ✅ Cálculo de probabilidades
- ✅ Mapeamento de seleções
- ✅ Cálculo de valor
- ✅ Verificação de critérios
- ✅ Cálculo de stake
- ✅ Cálculo de confiança
- ✅ Geração de fatores
- ✅ Casos extremos

## 📈 Exemplos de Uso

### Análise Completa
```python
from análise.value_finder import ValueFinder

# Inicializar
value_finder = ValueFinder()

# Dados de entrada
match_data = {...}
odds_data = [...]

# Analisar
prediction = value_finder.analyze_match(match_data, odds_data)

if prediction:
    print(f"✅ Valor encontrado!")
    print(f"   Mercado: {prediction.market}")
    print(f"   Seleção: {prediction.selection}")
    print(f"   EV: {prediction.expected_value:.2%}")
    print(f"   Stake: {prediction.stake_percentage:.2%}")
else:
    print("❌ Nenhum valor encontrado")
```

### Análise de Múltiplas Partidas
```python
def analyze_multiple_matches(matches_data, odds_data_list):
    predictions = []
    
    for match_data, odds_data in zip(matches_data, odds_data_list):
        prediction = value_finder.analyze_match(match_data, odds_data)
        if prediction:
            predictions.append(prediction)
    
    return predictions
```

## ⚙️ Configuração

### Critérios Mínimos
```python
# settings/settings.py
MIN_CONFIDENCE = 0.70      # 70% confiança mínima
MAX_CONFIDENCE = 0.90      # 90% confiança máxima
MIN_VALUE_EV = 0.05        # 5% EV mínimo
```

### Personalização
```python
class CustomValueFinder(ValueFinder):
    def _calculate_probabilities(self, match_data):
        # Implementar modelo personalizado
        return custom_probabilities
    
    def _meets_criteria(self, value):
        # Critérios personalizados
        return custom_criteria_check
```

## 🔄 Integração

### Com Coletores
```python
from coletores.football_collector import FootballCollector
from coletores.odds_collector import OddsCollector
from análise.value_finder import ValueFinder

# Coletar dados
football = FootballCollector()
odds = OddsCollector()

matches = football.collect(mode='today')
odds_data = odds.collect(sport='soccer_epl')

# Analisar
value_finder = ValueFinder()
for match in matches:
    prediction = value_finder.analyze_match(match, odds_data)
```

### Com Banco de Dados
```python
from armazenamento.banco_de_dados import SessionLocal, Prediction

# Consultar predições
db = SessionLocal()
predictions = db.query(Prediction).filter(Prediction.recommended == True).all()

for pred in predictions:
    print(f"{pred.market} - {pred.selection}: {pred.expected_value:.2%}")
```

## ⚠️ Limitações e Considerações

### Modelo de Probabilidades
- **Atual**: Simulação simplificada
- **Melhoria**: Implementar modelo de ML real
- **Dados**: Requer dados históricos extensos

### Critérios de Qualidade
- **Conservador**: Filtros rígidos para evitar perdas
- **Flexível**: Configurável via settings
- **Adaptativo**: Pode ser ajustado baseado em performance

### Gestão de Risco
- **Kelly Fracionado**: Mais conservador que Kelly completo
- **Limites**: Stake limitado a 10% da banca
- **Diversificação**: Múltiplas apostas simultâneas

## 🐛 Solução de Problemas

### Erro: "Nenhum valor encontrado"
- Verificar se odds estão disponíveis
- Ajustar critérios mínimos
- Verificar qualidade do modelo

### Erro: "Probabilidades inválidas"
- Verificar se modelo está funcionando
- Validar dados de entrada
- Verificar mapeamento de mercados

### Erro: "Stake muito alto"
- Ajustar fração do Kelly
- Verificar limites de stake
- Revisar critérios de qualidade

## 📊 Performance

### Otimizações
- **Caching**: Reutilizar cálculos quando possível
- **Batch Processing**: Analisar múltiplas partidas
- **Database Indexing**: Consultas otimizadas

### Métricas
- **Taxa de Detecção**: % de partidas com valor
- **Precisão**: % de apostas vencedoras
- **ROI**: Retorno sobre investimento
- **Sharpe Ratio**: Risco vs retorno

## 🔄 Extensibilidade

### Adicionar Novos Mercados
```python
def _map_selection(self, market, selection):
    mapping = {
        'h2h': {...},
        'totals': {...},
        'new_market': {  # Novo mercado
            'Selection1': 'prob_key1',
            'Selection2': 'prob_key2'
        }
    }
    return mapping.get(market, {}).get(selection, '')
```

### Personalizar Critérios
```python
def _meets_criteria(self, value):
    # Critérios personalizados
    return (
        value['ev'] >= self.custom_min_ev and
        value['confidence'] >= self.custom_min_confidence and
        value['odd'] >= self.custom_min_odd
    )
```

### Adicionar Novos Fatores
```python
def _get_factors(self, probabilities, market):
    return {
        'model_probability': probabilities.get(market, 0),
        'statistical_edge': 'High value detected',
        'timestamp': datetime.now().isoformat(),
        'custom_factor': self.calculate_custom_factor()  # Novo fator
    }
```
