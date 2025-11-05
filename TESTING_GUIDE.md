# 🧪 Guia de Testes - MaraBet AI

> **Sistema completo de testes unitários e de integração para o MaraBet AI**

## 📋 Visão Geral

O MaraBet AI implementa uma suíte abrangente de testes que garante a qualidade, confiabilidade e robustez do sistema. Os testes cobrem desde funções individuais até fluxos completos de integração.

## 🏗️ Estrutura de Testes

### **Organização dos Testes**

```
tests/
├── conftest.py                 # Configuração global e fixtures
├── test_units/                 # Testes unitários
│   ├── test_ml_models.py      # Testes de modelos ML
│   └── test_utilities.py      # Testes de funções utilitárias
├── test_integration/           # Testes de integração
│   ├── test_pipeline.py       # Pipeline completo
│   └── test_auth_integration.py # Autenticação
└── utils/                      # Utilitários de teste
    └── test_helpers.py         # Helpers e fixtures
```

### **Tipos de Testes**

1. **Testes Unitários** (`test_units/`)
   - Lógica de ML e algoritmos
   - Funções de utilidade
   - Validações e cálculos
   - Modelos de dados

2. **Testes de Integração** (`test_integration/`)
   - Pipeline completo de coleta-processamento-predição
   - Integração com APIs externas
   - Fluxos de autenticação
   - Integração com banco de dados

3. **Testes de API** (`test_integration/`)
   - Endpoints REST
   - Validação de dados
   - Controle de acesso
   - Tratamento de erros

## 🚀 Como Executar Testes

### **1. Execução Básica**

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=. --cov-report=html

# Executar testes específicos
pytest tests/test_units/test_ml_models.py

# Executar com marcadores
pytest -m unit
pytest -m integration
pytest -m ml
pytest -m auth
```

### **2. Scripts de Execução**

```bash
# Usar script personalizado
python scripts/run_tests.py all --parallel --coverage

# Executar tipos específicos
python scripts/run_tests.py unit
python scripts/run_tests.py integration
python scripts/run_tests.py ml
python scripts/run_tests.py auth

# Executar no CI
python scripts/ci_tests.py
```

### **3. Execução Paralela**

```bash
# Executar em paralelo (automático)
pytest -n auto

# Executar com número específico de workers
pytest -n 4

# Executar sequencialmente
pytest -n 0
```

## 📊 Cobertura de Testes

### **Threshold de Cobertura**

- **Mínimo**: 80%
- **Meta**: 90%
- **Ideal**: 95%

### **Relatórios de Cobertura**

```bash
# Gerar relatório HTML
pytest --cov=. --cov-report=html:htmlcov

# Gerar relatório XML (para CI)
pytest --cov=. --cov-report=xml:coverage.xml

# Gerar relatório terminal
pytest --cov=. --cov-report=term-missing
```

### **Verificar Cobertura**

```bash
# Verificar se atende ao threshold
coverage report --fail-under=80

# Gerar relatório final
coverage html -d htmlcov/final
```

## 🧪 Testes Unitários

### **Testes de ML**

```python
# Exemplo: Teste de modelo Random Forest
def test_random_forest_training(sample_ml_data):
    model = RandomForestModel()
    model.fit(sample_ml_data['X_train'], sample_ml_data['y_train'])
    
    assert model.is_trained == True
    assert hasattr(model, 'model')

def test_random_forest_prediction(sample_ml_data):
    model = RandomForestModel()
    model.fit(sample_ml_data['X_train'], sample_ml_data['y_train'])
    
    predictions = model.predict(sample_ml_data['X_test'])
    
    assert len(predictions) == len(sample_ml_data['X_test'])
    assert all(pred in [0, 1, 2] for pred in predictions)
```

### **Testes de Utilidades**

```python
# Exemplo: Teste de cálculo de probabilidade
def test_calculate_implied_probability():
    calculator = ProbabilityCalculator()
    
    prob = calculator.calculate_implied_probability(2.0)
    assert abs(prob - 0.5) < 1e-10

def test_calculate_expected_value():
    calculator = ProbabilityCalculator()
    
    ev = calculator.calculate_expected_value(0.6, 2.0)
    expected = 0.6 * 2.0 - 1  # 0.2
    assert abs(ev - expected) < 1e-10
```

## 🔗 Testes de Integração

### **Pipeline Completo**

```python
# Exemplo: Teste de pipeline completo
def test_complete_value_bet_pipeline(test_db, mock_api_football, mock_odds_api):
    # 1. Coletar dados de partidas
    api_collector = APIFootballCollector()
    fixtures_result = api_collector.collect_fixtures(league_id=39, season=2024)
    assert fixtures_result['success'] == True
    
    # 2. Coletar odds
    odds_collector = OddsCollector()
    odds_result = odds_collector.collect_odds(sport="soccer_epl", regions=["uk"])
    assert odds_result['success'] == True
    
    # 3. Processar dados
    processor = DataProcessor()
    processing_result = processor.process_matches()
    assert processing_result['success'] == True
    
    # 4. Treinar modelo ML
    manager = MLModelManager()
    model = manager.create_model('random_forest')
    training_result = manager.train_model(model, X_train, y_train)
    assert training_result is not None
    
    # 5. Fazer predição
    calculator = ProbabilityCalculator()
    probability = calculator.calculate_probability(model, X_test)
    assert 0 <= probability <= 1
    
    # 6. Identificar value bet
    identifier = ValueIdentifier()
    prediction_data = {
        'predicted_probability': probability,
        'current_odd': 2.10,
        'confidence': 0.8,
        'min_ev_threshold': 0.1,
        'min_confidence_threshold': 0.7
    }
    
    is_value_bet = identifier.identify_value_bet(prediction_data)
    assert isinstance(is_value_bet, bool)
```

### **Testes de Autenticação**

```python
# Exemplo: Teste de fluxo de login
def test_user_login_flow(test_client, test_user):
    login_data = {
        "username": test_user.username,
        "password": "testpass123",
        "remember_me": False
    }
    
    response = test_client.post("/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
```

## 🛠️ Fixtures e Helpers

### **Fixtures Principais**

```python
# Banco de dados de teste
@pytest.fixture(scope="function")
def test_db(test_db_engine):
    session = TestingSessionLocal()
    yield session
    session.close()

# Cliente FastAPI
@pytest.fixture(scope="function")
def test_client(test_db):
    def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

# Redis de teste
@pytest.fixture(scope="function")
def test_redis():
    cache = RedisCache(host="localhost", port=6379, db=1)
    cache.clear_all()
    yield cache
    cache.clear_all()
```

### **Helpers de Dados**

```python
# Criar dados de teste
def create_test_match_data(fixture_id=12345, **kwargs):
    default_data = {
        "fixture_id": fixture_id,
        "league_name": "Premier League",
        "home_team_name": "Manchester United",
        "away_team_name": "Liverpool",
        "date": datetime.now() + timedelta(hours=2),
        "status": "NS"
    }
    default_data.update(kwargs)
    return default_data

# Criar dataset de ML
def create_test_ml_dataset(n_samples=100, n_features=10, n_classes=3):
    X = np.random.rand(n_samples, n_features)
    y = np.random.randint(0, n_classes, n_samples)
    
    split_idx = int(n_samples * 0.8)
    return {
        "X_train": X[:split_idx],
        "y_train": y[:split_idx],
        "X_test": X[split_idx:],
        "y_test": y[split_idx:]
    }
```

## 🏷️ Marcadores de Teste

### **Marcadores Disponíveis**

```python
# Marcadores por tipo
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
def test_integration_flow():
    pass

@pytest.mark.ml
def test_ml_model():
    pass

@pytest.mark.auth
def test_authentication():
    pass

@pytest.mark.api
def test_api_endpoint():
    pass

# Marcadores por característica
@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.external
def test_external_api():
    pass

@pytest.mark.database
def test_database_operation():
    pass

@pytest.mark.redis
def test_redis_operation():
    pass

@pytest.mark.celery
def test_celery_task():
    pass
```

### **Executar por Marcadores**

```bash
# Executar apenas testes unitários
pytest -m unit

# Executar apenas testes de integração
pytest -m integration

# Executar apenas testes de ML
pytest -m ml

# Executar apenas testes de autenticação
pytest -m auth

# Executar apenas testes de API
pytest -m api

# Executar apenas testes lentos
pytest -m slow

# Executar apenas testes externos
pytest -m external

# Excluir testes lentos
pytest -m "not slow"

# Excluir testes externos
pytest -m "not external"
```

## 🔧 Configuração de Testes

### **Arquivo pytest.ini**

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

markers =
    unit: marca testes unitários
    integration: marca testes de integração
    slow: marca testes lentos
    ml: marca testes de machine learning
    auth: marca testes de autenticação
    api: marca testes de API

addopts = 
    --cov=.
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-report=xml:coverage.xml
    --cov-fail-under=80
    --strict-markers
    --disable-warnings
    --tb=short
    -v

cov-branch = true
cov-source = .

cov-omit = 
    tests/*
    */migrations/*
    */venv/*
    */env/*
    */__pycache__/*
    */site-packages/*
    setup.py
    conftest.py
```

### **Variáveis de Ambiente**

```bash
# Configurações de teste
export TEST_DATABASE_URL="sqlite:///./test_sports_data.db"
export TEST_REDIS_URL="redis://localhost:6379/1"
export API_FOOTBALL_KEY="test_key"
export THE_ODDS_API_KEY="test_key"
export TELEGRAM_BOT_TOKEN="test_token"
export TELEGRAM_CHAT_ID="test_chat"
```

## 📈 Métricas e Relatórios

### **Relatórios Gerados**

1. **HTML Coverage Report** (`htmlcov/index.html`)
   - Cobertura visual por arquivo
   - Linhas cobertas/não cobertas
   - Métricas detalhadas

2. **XML Coverage Report** (`coverage.xml`)
   - Para integração com CI/CD
   - Compatível com Codecov

3. **JUnit XML** (`test-results.xml`)
   - Resultados de testes
   - Para integração com CI/CD

4. **JSON Report** (`test-report.json`)
   - Dados estruturados
   - Para análise programática

### **Métricas Importantes**

- **Cobertura de Código**: % de linhas executadas
- **Cobertura de Branches**: % de branches testados
- **Tempo de Execução**: Duração dos testes
- **Taxa de Sucesso**: % de testes que passaram
- **Testes por Segundo**: Velocidade de execução

## 🚨 Tratamento de Erros

### **Testes que Falham**

```python
# Verificar exceções específicas
def test_invalid_input():
    with pytest.raises(ValueError, match="Invalid input"):
        process_invalid_data("invalid")

# Verificar múltiplas exceções
def test_multiple_exceptions():
    with pytest.raises((ValueError, TypeError)):
        process_data(None)
```

### **Testes de Timeout**

```python
# Teste com timeout
@pytest.mark.timeout(30)
def test_slow_operation():
    result = slow_operation()
    assert result is not None
```

### **Testes Condicionais**

```python
# Teste condicional
@pytest.mark.skipif(not redis_available(), reason="Redis not available")
def test_redis_operation():
    cache = RedisCache()
    assert cache.ping() == True
```

## 🔄 Integração com CI/CD

### **GitHub Actions**

```yaml
# Exemplo de workflow
- name: Run Tests
  run: |
    pytest tests/ \
      --cov=. \
      --cov-report=xml:coverage.xml \
      --cov-report=html:htmlcov \
      --junitxml=test-results.xml \
      --html=test-report.html \
      --self-contained-html \
      -v
```

### **Execução Paralela no CI**

```yaml
# Executar testes em paralelo
- name: Run Parallel Tests
  run: |
    pytest tests/ -n auto \
      --cov=. \
      --cov-report=xml:coverage.xml \
      --junitxml=test-results.xml \
      -v
```

## 📚 Boas Práticas

### **1. Nomenclatura**

```python
# Nomes descritivos
def test_calculate_expected_value_with_positive_ev():
    pass

def test_user_login_with_valid_credentials():
    pass

def test_api_returns_404_for_invalid_endpoint():
    pass
```

### **2. Organização**

```python
# Agrupar testes relacionados
class TestMLModelManager:
    def test_create_model(self):
        pass
    
    def test_train_model(self):
        pass
    
    def test_predict(self):
        pass
```

### **3. Fixtures**

```python
# Usar fixtures para setup/teardown
@pytest.fixture
def sample_data():
    # Setup
    data = create_test_data()
    yield data
    # Teardown
    cleanup_test_data(data)
```

### **4. Assertions**

```python
# Assertions específicas
def test_calculation():
    result = calculate_value(10, 20)
    assert result == 30
    assert isinstance(result, int)
    assert result > 0
```

### **5. Mocks**

```python
# Usar mocks para dependências externas
@patch('requests.get')
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {"data": "test"}
    
    result = call_external_api()
    
    assert result == {"data": "test"}
    mock_get.assert_called_once()
```

## 🎯 Objetivos de Qualidade

### **Métricas de Qualidade**

- **Cobertura de Código**: ≥ 80%
- **Cobertura de Branches**: ≥ 70%
- **Tempo de Execução**: < 5 minutos
- **Taxa de Sucesso**: ≥ 95%
- **Testes por Arquivo**: ≥ 5

### **Tipos de Testes por Categoria**

- **ML Models**: 20+ testes
- **Utilities**: 30+ testes
- **API Endpoints**: 50+ testes
- **Authentication**: 25+ testes
- **Integration**: 15+ testes

## 🚀 Próximos Passos

### **Melhorias Planejadas**

1. **Testes de Performance**
   - Benchmarks de ML
   - Testes de carga
   - Testes de memória

2. **Testes de Segurança**
   - Testes de vulnerabilidades
   - Testes de autenticação
   - Testes de autorização

3. **Testes de Usabilidade**
   - Testes de interface
   - Testes de experiência do usuário
   - Testes de acessibilidade

4. **Testes de Compatibilidade**
   - Testes de versões Python
   - Testes de sistemas operacionais
   - Testes de navegadores

---

## 🎉 **SISTEMA DE TESTES COMPLETO!**

**Status**: ✅ **PRONTO PARA PRODUÇÃO**

O MaraBet AI agora possui uma suíte completa de testes unitários e de integração, garantindo qualidade, confiabilidade e robustez do sistema!

**🧪 Desenvolvido com ❤️ para qualidade e confiabilidade**
