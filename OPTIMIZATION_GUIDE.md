# 🎯 Guia de Otimização de Hiperparâmetros - MaraBet AI

> **Sistema completo de otimização automática de hiperparâmetros com Optuna e validação cruzada temporal**

## 📋 Visão Geral

O MaraBet AI implementa um sistema avançado de otimização de hiperparâmetros que utiliza **Optuna** e **Ray Tune** para encontrar automaticamente as melhores configurações para todos os modelos de machine learning. O sistema inclui técnicas avançadas de validação cruzada temporal para séries de dados financeiros.

## 🏗️ Arquitetura do Sistema

### **Componentes Principais**

```
optimization/
├── optimizers/                    # Otimizadores de hiperparâmetros
│   ├── hyperparameter_optimizer.py    # Otimizador principal
│   └── model_optimizers.py            # Otimizadores específicos por modelo
├── validation/                    # Validação cruzada temporal
│   └── time_series_cv.py              # Implementações de CV temporal
├── api/                          # API endpoints
│   └── optimization_endpoints.py      # Endpoints FastAPI
├── dashboard/                    # Interface web
│   └── optimization_dashboard.html    # Dashboard de otimização
└── tests/                        # Testes
    └── test_hyperparameter_optimizer.py
```

### **Tecnologias Utilizadas**

- **Optuna**: Otimização bayesiana de hiperparâmetros
- **Ray Tune**: Otimização distribuída e paralela
- **Time Series CV**: Validação cruzada temporal avançada
- **Celery**: Execução assíncrona de otimizações
- **FastAPI**: API REST para controle
- **Bootstrap 5**: Interface web responsiva

## 🚀 Funcionalidades Principais

### **1. Otimização de Hiperparâmetros**

#### **Modelos Suportados**
- **Random Forest**: 10+ parâmetros otimizáveis
- **XGBoost**: 12+ parâmetros otimizáveis
- **LightGBM**: 15+ parâmetros otimizáveis
- **CatBoost**: 10+ parâmetros otimizáveis
- **Regressão Logística**: 6+ parâmetros otimizáveis
- **Rede Neural Bayesiana**: 8+ parâmetros otimizáveis
- **Modelo de Poisson**: 5+ parâmetros otimizáveis

#### **Estratégias de Otimização**
- **TPE Sampler**: Tree-structured Parzen Estimator
- **Median Pruner**: Poda de tentativas ineficientes
- **Multi-objective**: Otimização de múltiplas métricas
- **Pruning**: Interrupção precoce de tentativas ruins

### **2. Validação Cruzada Temporal**

#### **Time Series Cross-Validation**
```python
# Janela deslizante
cv = TimeSeriesSplit(
    n_splits=5,
    test_size=20,
    gap=1,  # Evita data leakage
    expanding_window=False
)

# Janela expansiva
cv = TimeSeriesSplit(
    n_splits=5,
    test_size=20,
    expanding_window=True
)
```

#### **Purged Cross-Validation**
```python
# Para dados financeiros
cv = PurgedCrossValidation(
    n_splits=5,
    test_size=20,
    purge_days=1,    # Período de purga
    embargo_days=1   # Período de embargo
)
```

#### **Walk-Forward Analysis**
```python
# Para estratégias de trading
cv = WalkForwardAnalysis(
    initial_train_size=100,
    step_size=10,
    min_train_size=50
)
```

#### **Monte Carlo Cross-Validation**
```python
# Validação robusta
cv = MonteCarloCrossValidation(
    n_splits=100,
    test_size=0.2,
    random_state=42
)
```

### **3. Execução Assíncrona**

#### **Tarefas Celery**
- **Otimização única**: `optimize_single_model`
- **Otimização multi-modelo**: `optimize_multiple_models`
- **Otimização customizada**: `optimize_with_custom_objective`
- **Retomar otimização**: `resume_optimization`
- **Exportar resultados**: `export_optimization_results`
- **Limpeza**: `cleanup_old_studies`

#### **Filas de Trabalho**
- **ML Queue**: Otimizações de modelos (2 workers)
- **Data Queue**: Processamento de dados (3 workers)
- **Export Queue**: Exportação de resultados (1 worker)

## 🛠️ Como Usar

### **1. Interface Web**

#### **Acessar Dashboard**
```
http://localhost:8000/optimization
```

#### **Funcionalidades do Dashboard**
- **Iniciar otimizações** (única ou multi-modelo)
- **Monitorar progresso** em tempo real
- **Visualizar resultados** com gráficos
- **Exportar dados** em múltiplos formatos
- **Gerenciar estudos** existentes

### **2. API REST**

#### **Iniciar Otimização Única**
```bash
curl -X POST "http://localhost:8000/optimization/start-single" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "model_name": "random_forest",
    "study_name": "rf_optimization_1",
    "n_trials": 100,
    "timeout": 3600,
    "cv_strategy": "time_series",
    "scoring": "accuracy"
  }'
```

#### **Iniciar Otimização Multi-Modelo**
```bash
curl -X POST "http://localhost:8000/optimization/start-multi" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "model_names": ["random_forest", "xgboost", "lightgbm"],
    "study_name": "multi_model_optimization",
    "n_trials": 50,
    "cv_strategy": "purged",
    "scoring": "f1"
  }'
```

#### **Verificar Status**
```bash
curl -X GET "http://localhost:8000/optimization/status/TASK_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### **Exportar Resultados**
```bash
curl -X POST "http://localhost:8000/optimization/export" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "study_name": "rf_optimization_1",
    "model_name": "random_forest",
    "export_format": "json"
  }'
```

### **3. Linha de Comando**

#### **Script de Gerenciamento**
```bash
# Listar modelos suportados
python scripts/optimization_manager.py list-models

# Listar estratégias de validação cruzada
python scripts/optimization_manager.py list-cv-strategies

# Listar estudos existentes
python scripts/optimization_manager.py list-studies

# Mostrar detalhes de um estudo
python scripts/optimization_manager.py show-study rf_optimization_1

# Iniciar otimização única
python scripts/optimization_manager.py optimize random_forest rf_opt_1 --n-trials 100 --async

# Iniciar otimização multi-modelo
python scripts/optimization_manager.py optimize-multi random_forest xgboost lightgbm multi_opt_1 --n-trials 50

# Exportar resultados
python scripts/optimization_manager.py export rf_opt_1 random_forest --format json

# Limpar estudos antigos
python scripts/optimization_manager.py cleanup --days 30

# Modo interativo
python scripts/optimization_manager.py interactive
```

### **4. Uso Programático**

#### **Otimização Básica**
```python
from optimization.optimizers.hyperparameter_optimizer import HyperparameterOptimizer
import numpy as np

# Criar dados
X = np.random.randn(1000, 10)
y = np.random.randint(0, 3, 1000)

# Criar otimizador
optimizer = HyperparameterOptimizer(
    study_name="my_optimization",
    n_trials=100,
    cv_strategy="time_series",
    cv_params={"n_splits": 5, "gap": 1},
    scoring="accuracy"
)

# Otimizar Random Forest
study = optimizer.optimize_random_forest(X, y)

# Obter resultados
print(f"Melhor score: {optimizer.get_best_score():.4f}")
print(f"Melhores parâmetros: {optimizer.get_best_params()}")
```

#### **Otimização Multi-Modelo**
```python
from optimization.optimizers.hyperparameter_optimizer import MultiModelOptimizer

# Criar otimizador multi-modelo
multi_optimizer = MultiModelOptimizer(
    models=['random_forest', 'xgboost', 'lightgbm'],
    study_name="multi_optimization",
    n_trials=50
)

# Otimizar todos os modelos
results = multi_optimizer.optimize_all(X, y)

# Obter melhor modelo
best_model, best_params, best_score = multi_optimizer.get_best_model()
print(f"Melhor modelo: {best_model} ({best_score:.4f})")
```

#### **Validação Cruzada Customizada**
```python
from optimization.validation.time_series_cv import create_time_series_cv

# Criar validação cruzada personalizada
cv_manager = create_time_series_cv(
    strategy="purged",
    n_splits=5,
    test_size=50,
    purge_days=2,
    embargo_days=1
)

# Usar com otimizador
optimizer = HyperparameterOptimizer(
    study_name="custom_cv_optimization",
    cv_strategy="purged",
    cv_params={"n_splits": 5, "purge_days": 2, "embargo_days": 1}
)
```

## 📊 Métricas e Monitoramento

### **Métricas de Otimização**

#### **Score de Validação**
- **Accuracy**: Taxa de acerto
- **Precision**: Precisão por classe
- **Recall**: Sensibilidade por classe
- **F1-Score**: Média harmônica
- **AUC-ROC**: Área sob a curva ROC
- **Log Loss**: Perda logarítmica

#### **Métricas Temporais**
- **Time Series Accuracy**: Acurácia temporal
- **Walk-Forward Return**: Retorno walk-forward
- **Sharpe Ratio**: Razão de Sharpe
- **Maximum Drawdown**: Máximo drawdown

### **Monitoramento em Tempo Real**

#### **Dashboard Web**
- **Progresso**: Barra de progresso em tempo real
- **Gráficos**: Evolução do score ao longo das tentativas
- **Logs**: Log de atividades e erros
- **Status**: Status de cada otimização

#### **API de Status**
```python
# Verificar status de uma tarefa
response = requests.get(f"/optimization/status/{task_id}")
status = response.json()

print(f"Status: {status['status']}")
print(f"Progresso: {status['info']}")
```

## 🔧 Configuração Avançada

### **Espaços de Hiperparâmetros**

#### **Random Forest**
```python
# Parâmetros otimizáveis
{
    'n_estimators': (50, 1000),
    'max_depth': (3, 30),
    'min_samples_split': (2, 20),
    'min_samples_leaf': (1, 10),
    'max_features': ['sqrt', 'log2', None],
    'bootstrap': [True, False],
    'criterion': ['gini', 'entropy']
}
```

#### **XGBoost**
```python
# Parâmetros otimizáveis
{
    'n_estimators': (50, 1000),
    'max_depth': (3, 15),
    'learning_rate': (0.01, 0.3),
    'subsample': (0.6, 1.0),
    'colsample_bytree': (0.6, 1.0),
    'reg_alpha': (0, 10),
    'reg_lambda': (0, 10),
    'gamma': (0, 5)
}
```

#### **LightGBM**
```python
# Parâmetros otimizáveis
{
    'n_estimators': (50, 1000),
    'max_depth': (3, 15),
    'learning_rate': (0.01, 0.3),
    'num_leaves': (10, 300),
    'min_child_samples': (5, 100),
    'subsample': (0.6, 1.0),
    'colsample_bytree': (0.6, 1.0),
    'reg_alpha': (0, 10),
    'reg_lambda': (0, 10)
}
```

### **Configuração de Validação Cruzada**

#### **Time Series Split**
```python
# Configuração para dados temporais
cv_params = {
    'n_splits': 5,           # Número de splits
    'test_size': 50,         # Tamanho do teste
    'gap': 1,                # Gap entre treino e teste
    'expanding_window': False, # Janela deslizante
    'min_train_size': 100,   # Tamanho mínimo do treino
    'max_train_size': 500    # Tamanho máximo do treino
}
```

#### **Purged Cross-Validation**
```python
# Configuração para dados financeiros
cv_params = {
    'n_splits': 5,           # Número de splits
    'test_size': 50,         # Tamanho do teste
    'purge_days': 2,         # Dias de purga
    'embargo_days': 1        # Dias de embargo
}
```

### **Configuração de Otimização**

#### **Optuna Sampler**
```python
# TPE Sampler (padrão)
sampler = optuna.samplers.TPESampler(
    seed=42,
    n_startup_trials=10,
    n_ei_candidates=24
)

# Grid Sampler
sampler = optuna.samplers.GridSampler(
    search_space={
        'n_estimators': [100, 200, 300],
        'max_depth': [5, 10, 15]
    }
)
```

#### **Pruning**
```python
# Median Pruner (padrão)
pruner = optuna.pruners.MedianPruner(
    n_startup_trials=5,
    n_warmup_steps=10,
    interval_steps=1
)

# Successive Halving Pruner
pruner = optuna.pruners.SuccessiveHalvingPruner(
    min_resource=1,
    reduction_factor=4,
    min_early_stopping_rate=0
)
```

## 📈 Exemplos Práticos

### **1. Otimização para Dados Temporais**

```python
# Configuração para séries temporais
optimizer = HyperparameterOptimizer(
    study_name="temporal_optimization",
    n_trials=200,
    cv_strategy="time_series",
    cv_params={
        "n_splits": 5,
        "test_size": 100,
        "gap": 2,
        "expanding_window": False
    },
    scoring="accuracy"
)

# Otimizar XGBoost
study = optimizer.optimize_xgboost(X, y)
```

### **2. Otimização para Dados Financeiros**

```python
# Configuração para dados financeiros
optimizer = HyperparameterOptimizer(
    study_name="financial_optimization",
    n_trials=300,
    cv_strategy="purged",
    cv_params={
        "n_splits": 5,
        "test_size": 50,
        "purge_days": 3,
        "embargo_days": 2
    },
    scoring="f1"
)

# Otimizar LightGBM
study = optimizer.optimize_lightgbm(X, y)
```

### **3. Otimização Multi-Objetivo**

```python
# Configuração multi-objetivo
def multi_objective(trial):
    # Definir hiperparâmetros
    params = ModelOptimizerFactory.suggest_hyperparameters(
        'random_forest', trial
    )
    
    # Criar modelo
    model = RandomForestClassifier(**params)
    
    # Validação cruzada
    cv_results = cv_manager.cross_validate(model, X, y)
    
    # Retornar múltiplas métricas
    return cv_results['test_score'].mean(), -cv_results['test_score'].std()

# Criar estudo multi-objetivo
study = optuna.create_study(
    directions=['maximize', 'maximize'],
    sampler=optuna.samplers.TPESampler()
)

study.optimize(multi_objective, n_trials=100)
```

### **4. Otimização com Callbacks**

```python
# Callback para monitoramento
def callback(study, trial):
    if trial.number % 10 == 0:
        print(f"Trial {trial.number}: {trial.value:.4f}")
    
    # Salvar checkpoint
    if trial.number % 50 == 0:
        optimizer.save_study(f"checkpoint_{trial.number}.pkl")

# Otimizar com callback
study = optimizer.optimize_random_forest(X, y, callback=callback)
```

## 🧪 Testes e Validação

### **Executar Testes**

```bash
# Testes unitários
pytest optimization/tests/test_hyperparameter_optimizer.py -v

# Testes com cobertura
pytest optimization/tests/ --cov=optimization --cov-report=html

# Testes específicos
pytest optimization/tests/ -m optimization -v
```

### **Testes de Integração**

```python
# Teste de otimização completa
def test_end_to_end_optimization():
    X, y = create_test_data()
    
    optimizer = HyperparameterOptimizer(
        study_name="integration_test",
        n_trials=10
    )
    
    study = optimizer.optimize_random_forest(X, y)
    
    assert study is not None
    assert len(study.trials) == 10
    assert optimizer.get_best_score() > 0
```

## 🚀 Deploy e Produção

### **Configuração de Produção**

#### **Docker Compose**
```yaml
# Adicionar ao docker-compose.yml
services:
  optimization-worker:
    build: .
    command: celery -A tasks.celery_app worker -l info -Q optimization
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/1
    volumes:
      - ./optimization:/app/optimization
```

#### **Variáveis de Ambiente**
```bash
# Configuração de otimização
OPTIMIZATION_STORAGE_URL=postgresql://user:pass@localhost/optimization
OPTIMIZATION_N_TRIALS=100
OPTIMIZATION_TIMEOUT=3600
OPTIMIZATION_CV_STRATEGY=time_series
```

### **Monitoramento de Produção**

#### **Métricas Importantes**
- **Taxa de conclusão**: % de otimizações concluídas
- **Tempo médio**: Tempo médio por otimização
- **Melhor score**: Melhor score encontrado
- **Uso de recursos**: CPU, memória, disco

#### **Alertas**
- **Falhas de otimização**: > 10% de falhas
- **Tempo excessivo**: > 2 horas por otimização
- **Uso de disco**: > 80% de uso
- **Erros de validação**: > 5% de erros

## 📚 Referências e Recursos

### **Documentação Oficial**
- [Optuna Documentation](https://optuna.readthedocs.io/)
- [Ray Tune Documentation](https://docs.ray.io/en/latest/tune/)
- [Scikit-learn Cross-Validation](https://scikit-learn.org/stable/modules/cross_validation.html)

### **Artigos Científicos**
- "Optuna: A Next-generation Hyperparameter Optimization Framework" (2019)
- "Time Series Cross-Validation for Machine Learning" (2020)
- "Purged Cross-Validation for Financial Data" (2018)

### **Tutoriais**
- [Hyperparameter Optimization with Optuna](https://optuna.readthedocs.io/en/stable/tutorial/)
- [Time Series Cross-Validation](https://scikit-learn.org/stable/modules/cross_validation.html#time-series-split)

---

## 🎉 **SISTEMA DE OTIMIZAÇÃO COMPLETO!**

**Status**: ✅ **PRONTO PARA PRODUÇÃO**

O MaraBet AI agora possui um sistema completo de otimização de hiperparâmetros que:

- **Automatiza** a busca pelos melhores parâmetros
- **Utiliza** técnicas avançadas de validação cruzada temporal
- **Suporta** todos os modelos de ML do sistema
- **Executa** otimizações de forma assíncrona
- **Monitora** progresso em tempo real
- **Exporta** resultados em múltiplos formatos

**🎯 Desenvolvido com ❤️ para máxima performance e precisão**
