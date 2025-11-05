# 🏈 Sistema Básico de Dados Esportivos - MaraBet AI

Sistema econômico e gratuito para análise de dados esportivos usando SQLite e APIs gratuitas.

## 🎯 Características

- **💰 Econômico**: Usa SQLite e APIs gratuitas
- **🚀 Rápido**: Processamento local sem dependências externas
- **📊 Completo**: Coleta, processamento e análise de dados
- **🤖 ML**: Modelos de machine learning para predições
- **📈 Análise**: Identificação de value bets
- **🔧 Simples**: Fácil de configurar e usar

## 🏗️ Arquitetura

```
sports-data-system/
├── config/                 # Configurações
│   ├── settings.py        # Configurações gerais
│   └── api_keys.py        # Gerenciamento de chaves
├── collectors/            # Coletores de dados
│   ├── base_collector.py  # Classe base
│   ├── football_collector.py  # API-Football
│   └── odds_collector.py  # Odds (simulado)
├── processors/            # Processamento
│   ├── statistics.py      # Estatísticas
│   └── predictions.py     # ML e predições
├── storage/               # Armazenamento
│   ├── database.py        # SQLite manager
│   └── models.py          # Modelos de dados
├── analysis/              # Análise (futuro)
├── utils/                 # Utilitários
│   ├── cache.py          # Sistema de cache
│   └── logger.py         # Logging
├── main.py               # Sistema principal
├── requirements.txt      # Dependências
└── README.md            # Documentação
```

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd sports-data-system
```

### 2. Instale dependências
```bash
pip install -r requirements.txt
```

### 3. Configure chaves de API
```bash
# Copie o arquivo de exemplo
cp config/api_keys.py config/.env

# Edite com suas chaves
nano config/.env
```

### 4. Execute o sistema
```bash
python main.py --home-team "Manchester City" --away-team "Arsenal"
```

## 🔧 Configuração

### Chaves de API

1. **API-Football** (obrigatória):
   - Acesse: https://www.api-sports.io/
   - Crie conta gratuita
   - Obtenha sua chave
   - Adicione em `config/.env`:
     ```
     API_FOOTBALL_KEY=sua_chave_aqui
     ```

2. **The Odds API** (opcional):
   - Acesse: https://the-odds-api.com/
   - Obtenha chave gratuita
   - Adicione em `config/.env`:
     ```
     ODDS_API_KEY=sua_chave_aqui
     ```

### Configurações Avançadas

Edite `config/settings.py` para personalizar:

```python
# Configurações de coleta
DATA_COLLECTION_CONFIG = {
    'leagues': [
        {'id': 39, 'name': 'Premier League', 'country': 'England'},
        # Adicione mais ligas
    ],
    'update_interval': 3600,  # 1 hora
}

# Configurações de ML
ML_CONFIG = {
    'n_estimators': 100,
    'max_depth': 10,
    'random_state': 42
}
```

## 📊 Uso

### Análise Completa
```bash
python main.py --home-team "Manchester City" --away-team "Arsenal" --league "Premier League"
```

### Apenas Coleta de Dados
```bash
python main.py --home-team "Liverpool" --away-team "Chelsea" --collect-only
```

### Apenas Predições
```bash
python main.py --home-team "Barcelona" --away-team "Real Madrid" --predict-only
```

### Uso Programático
```python
from main import SportsDataSystem

# Inicializa sistema
system = SportsDataSystem()

# Executa análise
result = system.run_analysis("Manchester City", "Arsenal")

# Acessa resultados
predictions = result['predictions']
stats = result['system_stats']

# Limpa recursos
system.cleanup()
```

## 📈 Funcionalidades

### 1. Coleta de Dados
- **Partidas**: Fixtures, resultados, estatísticas
- **Times**: Informações, estatísticas, forma
- **Ligas**: Premier League, La Liga, Serie A, etc.
- **Odds**: Simuladas (em produção, APIs reais)
- **H2H**: Confrontos diretos

### 2. Processamento
- **Estatísticas**: Cálculos automáticos
- **Forma**: Análise de últimos jogos
- **Probabilidades**: Cálculo baseado em dados
- **Features**: Engenharia de características

### 3. Machine Learning
- **Modelos**: Random Forest para regressão e classificação
- **Predições**: Resultado, total de gols, ambas marcam
- **Value Bets**: Identificação de apostas com valor
- **Confiança**: Níveis de confiança das predições

### 4. Armazenamento
- **SQLite**: Banco local rápido
- **Modelos**: Persistência de ML
- **Cache**: Sistema de cache inteligente
- **Backup**: Limpeza automática

## 🎯 Exemplos de Saída

### Predições
```json
{
  "match_result": {
    "prediction": "Home Win",
    "confidence": 0.75,
    "probabilities": {
      "home_win": 0.60,
      "draw": 0.25,
      "away_win": 0.15
    }
  },
  "total_goals": {
    "prediction": 2.8,
    "over_2_5": true,
    "over_3_5": false
  },
  "both_teams_score": {
    "prediction": "Yes",
    "confidence": 0.68,
    "probability": 0.68
  }
}
```

### Value Bets
```json
{
  "value_bets": [
    {
      "market": "over_2_5_odd",
      "market_odd": 1.80,
      "fair_odd": 1.65,
      "expected_value": 0.09,
      "value_percentage": 9.1,
      "recommendation": "BET"
    }
  ]
}
```

## 📊 Monitoramento

### Logs
- **Console**: Saída em tempo real
- **Arquivo**: Logs rotativos em `logs/`
- **Níveis**: DEBUG, INFO, WARNING, ERROR

### Estatísticas
```python
stats = system.get_stats()
print(f"Uptime: {stats['uptime_seconds']}s")
print(f"Dados coletados: {stats['data_collected']}")
print(f"Predições: {stats['predictions_made']}")
```

### Banco de Dados
```python
db_stats = system.db.get_database_stats()
print(f"Partidas: {db_stats['matches_count']}")
print(f"Times: {db_stats['teams_count']}")
print(f"Tamanho: {db_stats['database_size_mb']} MB")
```

## 🔧 Manutenção

### Limpeza de Dados
```python
# Remove dados antigos (30 dias)
system.db.cleanup_old_data(days=30)

# Limpa cache
system.cache.clear()
```

### Backup
```python
# Salva cache em disco
system.cache.save_to_disk("backup_cache.json")

# Carrega cache do disco
system.cache.load_from_disk("backup_cache.json")
```

### Monitoramento de Performance
```python
# Estatísticas de cache
cache_stats = system.cache.get_stats()
print(f"Hit rate: {cache_stats['hit_rate']}")

# Estatísticas de banco
db_stats = system.db.get_database_stats()
print(f"Tamanho: {db_stats['database_size_mb']} MB")
```

## 🚨 Limitações

### Plano Gratuito
- **API-Football**: 10 requests/min
- **The Odds API**: 500 requests/mês
- **SQLite**: Banco local (não distribuído)

### Performance
- **Processamento**: Local (limitado por CPU)
- **Armazenamento**: Disco local
- **Concorrência**: Limitada

## 🔮 Roadmap

### Versão 1.1
- [ ] Interface web simples
- [ ] Mais fontes de dados
- [ ] Análise de tendências
- [ ] Alertas automáticos

### Versão 1.2
- [ ] Modelos de ML avançados
- [ ] Análise de sentimentos
- [ ] Integração com Telegram
- [ ] Dashboard em tempo real

### Versão 2.0
- [ ] PostgreSQL/MySQL
- [ ] Redis para cache
- [ ] API REST completa
- [ ] Microserviços

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🆘 Suporte

- **Issues**: Use o sistema de issues do GitHub
- **Documentação**: Consulte este README
- **Logs**: Verifique os arquivos de log em `logs/`

## 📞 Contato

- **Email**: marabet@example.com
- **GitHub**: @marabet-ai
- **Website**: https://marabet.ai

---

**MaraBet AI** - Sistema Básico de Dados Esportivos
*Análise inteligente, resultados precisos* 🎯
