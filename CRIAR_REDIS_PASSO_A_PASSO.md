# 💾 CRIAR ELASTICACHE REDIS - PASSO A PASSO

**Sistema**: MaraBet AI  
**Região**: eu-west-1 (Irlanda)  
**Cache**: Redis 7.0 Cluster Mode

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Criar Cache Subnet Group](#1-criar-cache-subnet-group)
3. [Criar Security Group](#2-security-group-redis)
4. [Criar Redis Cluster](#3-criar-redis-cluster)
5. [Obter Endpoint](#4-obter-endpoint)
6. [Testar Conexão](#5-testar-conexão)
7. [Configurar Aplicação](#6-configurar-aplicação)

---

## 🎯 VISÃO GERAL

### **ElastiCache Redis para MaraBet:**

```
VPC: marabet-vpc (10.0.0.0/16)
├── Private Subnet A (10.0.2.0/24 - eu-west-1a)
│   └── Redis Primary Node
└── Private Subnet B (10.0.3.0/24 - eu-west-1b)
    └── Redis Replica Node

Security Group: marabet-redis-sg
├── Porta 6379 ← Apenas de marabet-web-sg
└── Sem acesso público

Especificações:
├── Engine: Redis 7.0
├── Node Type: cache.t3.medium (2 vCPUs, 3.09GB RAM)
├── Cluster Mode: Enabled
├── Replicas: 1 (alta disponibilidade)
└── Encryption: At-rest + In-transit
```

---

## 1️⃣ CRIAR CACHE SUBNET GROUP

### **Obter IDs das Subnets Privadas:**

```bash
# Listar subnets privadas
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=marabet-private-*" \
  --region eu-west-1 \
  --query 'Subnets[*].[SubnetId,Tags[?Key==`Name`].Value|[0],AvailabilityZone,CidrBlock]' \
  --output table

# Salvar IDs
export SUBNET_PRIVATE_A=subnet-xxxxxxxxx  # AZ A
export SUBNET_PRIVATE_B=subnet-yyyyyyyyy  # AZ B
```

### **Criar Cache Subnet Group:**

```bash
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name marabet-redis-subnet \
  --cache-subnet-group-description "Subnet group for MaraBet Redis" \
  --subnet-ids $SUBNET_PRIVATE_A $SUBNET_PRIVATE_B \
  --region eu-west-1
```

**Resultado Esperado:**
```json
{
    "CacheSubnetGroup": {
        "CacheSubnetGroupName": "marabet-redis-subnet",
        "CacheSubnetGroupDescription": "Subnet group for MaraBet Redis",
        "VpcId": "vpc-xxxxxxxxx",
        "Subnets": [
            {
                "SubnetIdentifier": "subnet-xxxxxxxxx",
                "SubnetAvailabilityZone": {
                    "Name": "eu-west-1a"
                }
            },
            {
                "SubnetIdentifier": "subnet-yyyyyyyyy",
                "SubnetAvailabilityZone": {
                    "Name": "eu-west-1b"
                }
            }
        ]
    }
}
```

### **Verificar:**

```bash
aws elasticache describe-cache-subnet-groups \
  --cache-subnet-group-name marabet-redis-subnet \
  --region eu-west-1
```

---

## 2️⃣ SECURITY GROUP REDIS

### **Se ainda não criou o Security Group:**

```bash
# Obter Web Security Group ID
SG_WEB=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=marabet-web-sg" \
  --region eu-west-1 \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

echo "Web SG: $SG_WEB"

# Criar Redis Security Group
SG_REDIS=$(aws ec2 create-security-group \
  --group-name marabet-redis-sg \
  --description "Security group for MaraBet ElastiCache Redis" \
  --vpc-id $VPC_ID \
  --region eu-west-1 \
  --query 'GroupId' \
  --output text)

echo "Redis SG: $SG_REDIS"

# Permitir Redis (6379) apenas do Web SG
aws ec2 authorize-security-group-ingress \
  --group-id $SG_REDIS \
  --protocol tcp \
  --port 6379 \
  --source-group $SG_WEB \
  --region eu-west-1
```

### **Se já criou:**

```bash
# Obter ID do Security Group existente
SG_REDIS=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=marabet-redis-sg" \
  --region eu-west-1 \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

echo "Redis SG: $SG_REDIS"
```

---

## 3️⃣ CRIAR REDIS CLUSTER

### **Opção 1: Replication Group (Recomendado - Alta Disponibilidade)**

```bash
aws elasticache create-replication-group \
  --replication-group-id marabet-redis \
  --replication-group-description "MaraBet Redis Cluster" \
  --engine redis \
  --engine-version 7.0 \
  --cache-node-type cache.t3.medium \
  --num-cache-clusters 2 \
  --automatic-failover-enabled \
  --cache-subnet-group-name marabet-redis-subnet \
  --security-group-ids $SG_REDIS \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled \
  --auth-token-enabled \
  --auth-token "MaraBetRedis2025SecureToken" \
  --snapshot-retention-limit 5 \
  --snapshot-window "03:00-05:00" \
  --preferred-maintenance-window "sun:05:00-sun:07:00" \
  --tags "Key=Name,Value=marabet-redis" "Key=Environment,Value=production" \
  --region eu-west-1
```

**Parâmetros:**
- `--replication-group-id`: Nome do cluster
- `--num-cache-clusters 2`: 1 Primary + 1 Replica
- `--automatic-failover-enabled`: Failover automático
- `--at-rest-encryption-enabled`: Criptografia em disco
- `--transit-encryption-enabled`: Criptografia em trânsito
- `--auth-token`: Senha para conexão (TLS)
- `--snapshot-retention-limit 5`: 5 dias de snapshots

### **Opção 2: Cluster Mode Disabled (Mais simples)**

```bash
aws elasticache create-replication-group \
  --replication-group-id marabet-redis-simple \
  --replication-group-description "MaraBet Redis Simple" \
  --engine redis \
  --engine-version 7.0 \
  --cache-node-type cache.t3.medium \
  --num-cache-clusters 2 \
  --automatic-failover-enabled \
  --cache-subnet-group-name marabet-redis-subnet \
  --security-group-ids $SG_REDIS \
  --region eu-west-1
```

### **⏰ Aguardar Criação:**

```bash
# Aguardar cluster ficar disponível (~10-15 minutos)
echo "Aguardando Redis cluster ficar disponível..."
aws elasticache wait replication-group-available \
  --replication-group-id marabet-redis \
  --region eu-west-1

echo "✅ Redis cluster disponível!"
```

---

## 4️⃣ OBTER ENDPOINT

### **Endpoint Primary (Read/Write):**

```bash
# Obter endpoint primary
REDIS_ENDPOINT=$(aws elasticache describe-replication-groups \
  --replication-group-id marabet-redis \
  --region eu-west-1 \
  --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Address' \
  --output text)

echo "Redis Primary Endpoint: $REDIS_ENDPOINT"

# Obter porta
REDIS_PORT=$(aws elasticache describe-replication-groups \
  --replication-group-id marabet-redis \
  --region eu-west-1 \
  --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Port' \
  --output text)

echo "Redis Port: $REDIS_PORT"
```

### **Endpoint Reader (Read-Only):**

```bash
# Obter endpoint de leitura
REDIS_READER_ENDPOINT=$(aws elasticache describe-replication-groups \
  --replication-group-id marabet-redis \
  --region eu-west-1 \
  --query 'ReplicationGroups[0].NodeGroups[0].ReaderEndpoint.Address' \
  --output text)

echo "Redis Reader Endpoint: $REDIS_READER_ENDPOINT"
```

### **Informações Completas:**

```bash
# Ver todas as informações
aws elasticache describe-replication-groups \
  --replication-group-id marabet-redis \
  --region eu-west-1 > redis-info.json

# Resumo
aws elasticache describe-replication-groups \
  --replication-group-id marabet-redis \
  --region eu-west-1 \
  --query 'ReplicationGroups[0].[ReplicationGroupId,Status,ClusterEnabled,AtRestEncryptionEnabled,TransitEncryptionEnabled,NodeGroups[0].PrimaryEndpoint.Address]' \
  --output table
```

---

## 5️⃣ TESTAR CONEXÃO

### **A. Instalar redis-cli:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y redis-tools

# Amazon Linux 2
sudo yum install -y redis

# macOS
brew install redis
```

### **B. Testar Conexão:**

#### **Com TLS (se --transit-encryption-enabled):**

```bash
# Com autenticação
redis-cli -h $REDIS_ENDPOINT \
  -p $REDIS_PORT \
  --tls \
  --cacert /path/to/ca-cert.pem \
  -a "MaraBetRedis2025SecureToken"

# Testar comandos
PING
# Resposta: PONG

SET test_key "MaraBet AI"
GET test_key
# Resposta: "MaraBet AI"

INFO server
```

#### **Sem TLS (se não habilitou criptografia):**

```bash
redis-cli -h $REDIS_ENDPOINT -p $REDIS_PORT

PING
SET test "MaraBet OK"
GET test
```

### **C. Testar com Python:**

```python
import redis

# Com TLS
r = redis.Redis(
    host='marabet-redis.xxxxx.cache.amazonaws.com',
    port=6379,
    password='MaraBetRedis2025SecureToken',
    ssl=True,
    ssl_cert_reqs='required',
    decode_responses=True
)

# Testar
r.ping()  # True
r.set('test', 'MaraBet AI')
r.get('test')  # 'MaraBet AI'
```

---

## 6️⃣ CONFIGURAR APLICAÇÃO

### **Adicionar ao .env:**

```bash
# Redis Configuration
REDIS_URL=rediss://:MaraBetRedis2025SecureToken@marabet-redis.xxxxx.cache.amazonaws.com:6379
REDIS_HOST=marabet-redis.xxxxx.cache.amazonaws.com
REDIS_PORT=6379
REDIS_PASSWORD=MaraBetRedis2025SecureToken
REDIS_SSL=true
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
```

### **No código Python:**

```python
import redis
import os

# Opção 1: Com URL
redis_client = redis.from_url(
    os.getenv('REDIS_URL'),
    decode_responses=True
)

# Opção 2: Com parâmetros
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    password=os.getenv('REDIS_PASSWORD'),
    ssl=True,
    decode_responses=True
)

# Usar
redis_client.set('key', 'value')
value = redis_client.get('key')
```

---

## 💰 CUSTOS

### **cache.t3.medium (Replication Group 2 nodes):**

| Item | Custo/mês |
|------|-----------|
| **Primary Node** | $42.50 |
| **Replica Node** | $42.50 |
| **Backup (5 dias)** | ~$3 |
| **Data Transfer** | ~$5 |
| **TOTAL** | **~$93/mês** |

---

## 📊 MONITORAMENTO

### **CloudWatch Métricas:**

```bash
# CPU Utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name CPUUtilization \
  --dimensions Name=CacheClusterId,Value=marabet-redis-001 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region eu-west-1

# Memory Usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name DatabaseMemoryUsagePercentage \
  --dimensions Name=CacheClusterId,Value=marabet-redis-001 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region eu-west-1
```

---

## 🔧 COMANDOS ÚTEIS

### **Listar Clusters:**

```bash
aws elasticache describe-replication-groups \
  --region eu-west-1 \
  --query 'ReplicationGroups[*].[ReplicationGroupId,Status,NodeGroups[0].PrimaryEndpoint.Address]' \
  --output table
```

### **Modificar Cluster:**

```bash
# Aumentar para cache.t3.large
aws elasticache modify-replication-group \
  --replication-group-id marabet-redis \
  --cache-node-type cache.t3.large \
  --apply-immediately \
  --region eu-west-1
```

### **Criar Snapshot:**

```bash
aws elasticache create-snapshot \
  --replication-group-id marabet-redis \
  --snapshot-name marabet-redis-snapshot-$(date +%Y%m%d) \
  --region eu-west-1
```

### **Deletar Cluster (cuidado!):**

```bash
# Criar snapshot final antes
aws elasticache delete-replication-group \
  --replication-group-id marabet-redis \
  --final-snapshot-identifier marabet-redis-final-$(date +%Y%m%d) \
  --region eu-west-1
```

---

## ✅ CHECKLIST

- [ ] Subnets privadas criadas
- [ ] Cache Subnet Group criado
- [ ] Security Group Redis criado
- [ ] Redis Replication Group criado
- [ ] Aguardar status = available (~10-15 min)
- [ ] Endpoint obtido
- [ ] Auth token anotado
- [ ] Conexão testada
- [ ] .env configurado
- [ ] Aplicação conectada

---

**💾 ElastiCache Redis Pronto para Criação!**  
**🔒 Criptografia At-rest + In-transit**  
**✅ Alta Disponibilidade com Replica**  
**☁️ MaraBet AI - Powered by AWS ElastiCache**

