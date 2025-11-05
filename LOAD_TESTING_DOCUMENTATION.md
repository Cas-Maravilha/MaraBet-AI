# 🧪 Sistema de Testes de Carga - MaraBet AI

**Data**: 24/10/2025  
**Contato**: +224 932027393  
**Versão**: 1.0

---

## 📋 VISÃO GERAL

Sistema completo de testes de carga implementando:
- **Locust** (Python): Testes com interface web
- **K6** (JavaScript): Testes de performance avançados
- **Artillery** (Node.js): Testes baseados em cenários

---

## 🚀 INSTALAÇÃO

### Instalar Dependências Python:

```bash
cd load_tests
pip install -r requirements.txt
```

### Instalar K6 (Ubuntu/Debian):

```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### Instalar Artillery (Node.js):

```bash
npm install -g artillery
```

---

## 🧪 EXECUTAR TESTES

### Método 1: Script Automatizado (Recomendado)

```bash
# Executar script interativo
chmod +x load_tests/scripts/run_tests.sh
./load_tests/scripts/run_tests.sh http://localhost:8000
```

### Método 2: Comandos Individuais

#### Locust:

```bash
# Com interface web
cd load_tests/locust
locust -f locustfile.py --host=http://localhost:8000

# Modo headless
locust -f locustfile.py --host=http://localhost:8000 \
    --users=100 --spawn-rate=10 --run-time=5m \
    --html=../reports/locust_report.html --headless
```

#### K6:

```bash
# Executar teste
k6 run load_tests/k6/k6_test.js

# Com variáveis
k6 run --env BASE_URL=http://localhost:8000 load_tests/k6/k6_test.js

# Com relatório
k6 run load_tests/k6/k6_test.js \
    --out json=load_tests/reports/k6_results.json
```

#### Artillery:

```bash
# Executar teste
artillery run load_tests/artillery/artillery.yml

# Com relatório
artillery run load_tests/artillery/artillery.yml \
    --output load_tests/reports/artillery_report.json

artillery report load_tests/reports/artillery_report.json \
    --output load_tests/reports/artillery_report.html
```

---

## 📊 CENÁRIOS DE TESTE

### Locust:
- **Usuários normais**: Navegação e visualização
- **Usuários apostadores**: Criação de apostas
- **Administradores**: Gestão do sistema

### K6:
- **Warm-up**: 20 usuários (30s)
- **Ramp-up**: 50 usuários (1min)
- **Load**: 100 usuários (3min)
- **Peak**: 200 usuários (2min)
- **Ramp-down**: 50 usuários (1min)

### Artillery:
- **Normal User Flow** (70%): Navegação comum
- **Betting User Flow** (20%): Apostas
- **Admin Flow** (10%): Administração

---

## 📈 MÉTRICAS MONITORADAS

### Resposta:
- **p50, p95, p99**: Percentis de tempo de resposta
- **Média**: Tempo médio de resposta
- **Min/Max**: Tempos mínimo e máximo

### Taxa:
- **RPS**: Requisições por segundo
- **Throughput**: Volume de dados
- **Erros**: Taxa de erro

### Performance:
- **CPU**: Uso de processador
- **Memória**: Consumo de RAM
- **Disco**: I/O de disco
- **Rede**: Tráfego de rede

---

## 🎯 OBJETIVOS DE PERFORMANCE

### Tempos de Resposta:
- **p95 < 500ms**: 95% das requisições
- **p99 < 1000ms**: 99% das requisições
- **Média < 300ms**: Tempo médio

### Taxa de Erro:
- **< 1%**: Taxa de erro geral
- **< 0.1%**: Erros críticos

### Capacidade:
- **100 usuários**: Carga normal
- **200 usuários**: Carga de pico
- **500 usuários**: Carga máxima

---

## 📊 RELATÓRIOS

### Locust:
- **HTML**: `load_tests/reports/locust_report.html`
- **CSV**: `load_tests/reports/locust_*.csv`

### K6:
- **JSON**: `load_tests/reports/k6_results.json`
- **Summary**: `load_tests/reports/k6_summary.json`

### Artillery:
- **JSON**: `load_tests/reports/artillery_report.json`
- **HTML**: `load_tests/reports/artillery_report.html`

---

## ⚠️ BOAS PRÁTICAS

1. **Ambiente de Testes**: Use ambiente dedicado
2. **Warm-up**: Sempre faça aquecimento
3. **Incremental**: Aumente carga gradualmente
4. **Monitoramento**: Observe métricas durante testes
5. **Análise**: Revise relatórios após testes
6. **Documentação**: Registre resultados

---

## 🔍 TROUBLESHOOTING

### Erro: "Connection refused"
```bash
# Verificar se aplicação está rodando
docker-compose ps
curl http://localhost:8000/health
```

### Erro: "Too many open files"
```bash
# Aumentar limite de arquivos
ulimit -n 65536
```

### Performance degradada
```bash
# Verificar recursos do sistema
htop
docker stats
```

---

## 📞 SUPORTE

- **Telefone/WhatsApp**: +224 932027393
- **Telegram**: @marabet_support
- **Email**: suporte@marabet.ao

---

**🎯 Implementação 4/6 Concluída!**

**📊 Score: 112.6% → 124.3% (+11.7%)**
