# 📈 Sistema de Monitoramento Grafana + Prometheus - MaraBet AI

**Data**: 24/10/2025  
**Contato**: +224 932027393  
**Versão**: 1.0

---

## 📋 VISÃO GERAL

Sistema completo de monitoramento implementando:
- **Prometheus**: Coleta de métricas
- **Grafana**: Visualização e dashboards
- **Alertmanager**: Gerenciamento de alertas
- **Exporters**: Node, cAdvisor, PostgreSQL, Redis

---

## 🚀 INSTALAÇÃO RÁPIDA

### Método 1: Script Automatizado

```bash
chmod +x monitoring/setup_monitoring.sh
./monitoring/setup_monitoring.sh
```

### Método 2: Manual

```bash
# Iniciar serviços
docker-compose -f docker-compose.monitoring.yml up -d

# Verificar status
docker-compose -f docker-compose.monitoring.yml ps
```

---

## 🔧 CONFIGURAÇÃO

### Acessos:

- **Grafana**: http://localhost:3000
  - Usuário: `admin`
  - Senha: `marabet123`

- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

### Portas:

- `3000`: Grafana
- `9090`: Prometheus
- `9093`: Alertmanager
- `9100`: Node Exporter
- `8080`: cAdvisor
- `9187`: PostgreSQL Exporter
- `9121`: Redis Exporter

---

## 📊 DASHBOARDS DISPONÍVEIS

### 1. Overview Geral
- Status dos serviços
- Requests/segundo
- Tempo de resposta
- Taxa de erro

### 2. Performance da Aplicação
- Latência P50, P95, P99
- Throughput
- Erros HTTP
- Conexões ativas

### 3. Infraestrutura
- CPU, Memória, Disco
- Rede
- Containers Docker
- Processos

### 4. Banco de Dados
- Conexões PostgreSQL
- Queries/segundo
- Tamanho do banco
- Cache hit rate

### 5. Cache Redis
- Memória utilizada
- Hits/Misses
- Comandos/segundo
- Conexões

---

## 🚨 ALERTAS CONFIGURADOS

### Críticos:
- ✅ Serviço down
- ✅ Banco de dados down
- ✅ Alta taxa de erro (>5%)

### Warnings:
- ✅ Tempo de resposta alto (P95 >1s)
- ✅ Redis down
- ✅ Alto uso de CPU (>80%)
- ✅ Alto uso de memória (>85%)
- ✅ Disco cheio (>80%)
- ✅ Muitas conexões no banco

---

## 📈 MÉTRICAS COLETADAS

### Aplicação:
- `http_requests_total`: Total de requisições
- `http_request_duration_seconds`: Tempo de resposta
- `http_requests_in_progress`: Requisições em andamento

### Sistema:
- `node_cpu_seconds_total`: Uso de CPU
- `node_memory_MemAvailable_bytes`: Memória disponível
- `node_filesystem_avail_bytes`: Espaço em disco

### PostgreSQL:
- `pg_stat_database_numbackends`: Conexões ativas
- `pg_stat_database_xact_commit`: Transações
- `pg_database_size_bytes`: Tamanho do banco

### Redis:
- `redis_memory_used_bytes`: Memória usada
- `redis_connected_clients`: Clientes conectados
- `redis_keyspace_hits_total`: Cache hits

---

## 🔍 QUERIES ÚTEIS

### PromQL Examples:

```promql
# Taxa de requisições por segundo
rate(http_requests_total[5m])

# P95 tempo de resposta
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Taxa de erro
rate(http_requests_total{status=~"5.."}[5m])

# Uso de CPU
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Uso de memória
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

---

## 🔧 COMANDOS ÚTEIS

### Docker:

```bash
# Ver logs
docker-compose -f docker-compose.monitoring.yml logs -f

# Reiniciar serviços
docker-compose -f docker-compose.monitoring.yml restart

# Parar serviços
docker-compose -f docker-compose.monitoring.yml down

# Rebuild
docker-compose -f docker-compose.monitoring.yml up -d --build
```

### Prometheus:

```bash
# Recarregar configuração
curl -X POST http://localhost:9090/-/reload

# Verificar health
curl http://localhost:9090/-/healthy

# Ver targets
curl http://localhost:9090/api/v1/targets
```

### Grafana:

```bash
# Resetar senha admin
docker exec -it marabet-grafana grafana-cli admin reset-admin-password marabet123

# Ver configuração
docker exec -it marabet-grafana cat /etc/grafana/grafana.ini
```

---

## ⚠️ SOLUÇÃO DE PROBLEMAS

### Grafana não conecta ao Prometheus:

```bash
# Verificar rede Docker
docker network inspect monitoring

# Testar conectividade
docker exec marabet-grafana curl http://prometheus:9090/-/healthy
```

### Métricas não aparecem:

```bash
# Verificar targets no Prometheus
# http://localhost:9090/targets

# Ver logs do exporter
docker logs marabet-node-exporter
```

### Alertas não enviados:

```bash
# Verificar configuração
docker exec marabet-alertmanager amtool check-config /etc/alertmanager/config.yml

# Ver alertas ativos
curl http://localhost:9093/api/v1/alerts
```

---

## 📞 SUPORTE

- **Telefone/WhatsApp**: +224 932027393
- **Telegram**: @marabet_support
- **Email**: suporte@marabet.ao

---

## ✅ CHECKLIST

- [ ] Docker Compose executando
- [ ] Prometheus coletando métricas
- [ ] Grafana acessível
- [ ] Datasource Prometheus configurado
- [ ] Dashboards criados
- [ ] Alertmanager funcionando
- [ ] Exporters ativos
- [ ] Alertas configurados
- [ ] Notificações testadas

---

**🎯 Implementação 5/6 Concluída!**

**📊 Score: 124.3% → 136.0% (+11.7%)**
