# 💾 ELASTICACHE REDIS SERVERLESS - INFORMAÇÕES

**Data de Criação**: 27 de Outubro de 2025, 12:15:09 (UTC+01:00)  
**Status**: Creating → Available (aguardar 5-10 minutos)  
**Tipo**: Serverless (Valkey)

---

## 📊 INFORMAÇÕES DO CLUSTER

### **Identificação:**

```yaml
Name:                 marabet-redis
ARN:                  arn:aws:elasticache:eu-west-1:206749730888:serverlesscache:marabet-redis
Engine:               Valkey (compatível com Redis)
Status:               Creating → Available
Region:               eu-west-1
Account ID:           206749730888
```

### **Conectividade:**

```yaml
VPC ID:               vpc-081a8c63b16a94a3a
Subnets:
  - subnet-061544d7c4c85bd82 (eu-west-1b)
  - subnet-0f4df2ddacfc070bc (eu-west-1c)
  - subnet-0575567cf09ae0e02 (eu-west-1a)

Availability Zones:
  - eu-west-1a
  - eu-west-1b
  - eu-west-1c

Security Group:       sg-09f7d3d37a8407f43
```

### **Segurança:**

```yaml
Encryption At Rest:   Enabled (AWS owned KMS key)
Encryption In Transit: Enabled
User Group:           None
Automatic Backups:    Off (Desligado)
```

---

## ⚠️ IMPORTANTE - VALKEY vs REDIS

### **O que é Valkey?**

**Valkey** é um fork open-source do Redis 7.2, criado pela Linux Foundation:

✅ **100% compatível** com Redis  
✅ **Mesmos comandos** e protocolos  
✅ **Performance similar** ao Redis  
✅ **Sem custos de licença** Redis Labs  

### **Compatibilidade:**

```python
# Código Python funciona igual
import redis
client = redis.Redis(host='endpoint', port=6379)
client.set('key', 'value')  # ✅ Funciona
client.get('key')           # ✅ Funciona
```

**Todos os clientes Redis funcionam com Valkey!**

---

## 🔗 OBTER ENDPOINT

### **Aguardar Disponibilidade:**

```bash
# O endpoint só ficará disponível quando status = available
# Aguardar ~5-10 minutos

# Verificar status
aws elasticache describe-serverless-caches \
  --serverless-cache-name marabet-redis \
  --region eu-west-1 \
  --query 'ServerlessCaches[0].Status' \
  --output text
```

### **Obter Endpoint (após disponível):**

```bash
# Endpoint
REDIS_ENDPOINT=$(aws elasticache describe-serverless-caches \
  --serverless-cache-name marabet-redis \
  --region eu-west-1 \
  --query 'ServerlessCaches[0].Endpoint.Address' \
  --output text)

echo "Redis Endpoint: $REDIS_ENDPOINT"

# Porta
REDIS_PORT=$(aws elasticache describe-serverless-caches \
  --serverless-cache-name marabet-redis \
  --region eu-west-1 \
  --query 'ServerlessCaches[0].Endpoint.Port' \
  --output text)

echo "Redis Port: $REDIS_PORT"
```

### **Informações Completas:**

```bash
# Ver todas as informações
aws elasticache describe-serverless-caches \
  --serverless-cache-name marabet-redis \
  --region eu-west-1 > redis-serverless-info.json

# Ver resumo
aws elasticache describe-serverless-caches \
  --serverless-cache-name marabet-redis \
  --region eu-west-1 \
  --query 'ServerlessCaches[0].[ServerlessCacheName,Status,Engine,Endpoint.Address,Endpoint.Port]' \
  --output table
```

---

## 💰 CUSTOS - SERVERLESS

### **Modelo de Cobrança Serverless:**

ElastiCache Serverless cobra por:

1. **Armazenamento de Dados** (GB/hora)
   - ~$0.125 por GB/hora
   - Exemplo: 10GB = ~$90/mês

2. **Unidades de Computação ElastiCache (ECPUs)**
   - ~$0.034 por ECPU/hora
   - Auto-scaling baseado na demanda

**Vantagens:**
- ✅ Paga apenas pelo que usa
- ✅ Auto-scaling automático
- ✅ Sem provisionamento de capacidade
- ✅ Ideal para cargas variáveis

**Estimativa para MaraBet:**
- Carga baixa/média: ~$50-100/mês
- Carga alta: ~$150-250/mês
- Picos: Escala automaticamente

---

## 🔌 TESTAR CONEXÃO (após disponível)

### **1. Com redis-cli:**

```bash
# Instalar redis-cli
sudo apt install -y redis-tools

# Conectar (com TLS)
redis-cli -h marabet-redis.xxxxx.serverless.euw1.cache.amazonaws.com \
  -p 6379 \
  --tls \
  --insecure

# Comandos de teste
PING
# Resposta: PONG

SET test_key "MaraBet AI Serverless"
GET test_key
# Resposta: "MaraBet AI Serverless"

INFO server
```

### **2. Com Python:**

```python
import redis

# Conectar
r = redis.Redis(
    host='marabet-redis.xxxxx.serverless.euw1.cache.amazonaws.com',
    port=6379,
    ssl=True,
    ssl_cert_reqs=None,  # Ou 'required' se tiver certificado
    decode_responses=True
)

# Testar
print(r.ping())  # True
r.set('test', 'MaraBet OK')
print(r.get('test'))  # 'MaraBet OK'
```

### **3. Com Node.js:**

```javascript
const redis = require('redis');

const client = redis.createClient({
    socket: {
        host: 'marabet-redis.xxxxx.serverless.euw1.cache.amazonaws.com',
        port: 6379,
        tls: true,
        rejectUnauthorized: false
    }
});

await client.connect();

// Testar
await client.ping(); // 'PONG'
await client.set('test', 'MaraBet OK');
const value = await client.get('test'); // 'MaraBet OK'
```

---

## 📝 CONFIGURAR NA APLICAÇÃO

### **Adicionar ao .env:**

```bash
# ElastiCache Redis Serverless
REDIS_URL=rediss://marabet-redis.xxxxx.serverless.euw1.cache.amazonaws.com:6379
REDIS_HOST=marabet-redis.xxxxx.serverless.euw1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_SSL=true
REDIS_TLS=true
REDIS_DB=0

# Serverless Info
REDIS_TYPE=serverless
REDIS_ENGINE=valkey
REDIS_SERVERLESS_NAME=marabet-redis

# AWS
AWS_REGION=eu-west-1
ELASTICACHE_ARN=arn:aws:elasticache:eu-west-1:206749730888:serverlesscache:marabet-redis
```

### **No código Python (atualizar redis_config.py):**

```python
# redis_config.py já está pronto!
# Apenas configure as variáveis de ambiente

import os
os.environ['REDIS_HOST'] = 'marabet-redis.xxxxx.serverless.euw1.cache.amazonaws.com'
os.environ['REDIS_PORT'] = '6379'
os.environ['REDIS_SSL'] = 'true'

from redis_config import get_redis_client

# Usar
redis_client = get_redis_client()
redis_client.set('key', 'value')
```

---

## 🔍 VERIFICAR STATUS

### **Script de Verificação:**

```bash
#!/bin/bash

echo "🔍 Verificando status do Redis Serverless..."
echo ""

STATUS=$(aws elasticache describe-serverless-caches \
  --serverless-cache-name marabet-redis \
  --region eu-west-1 \
  --query 'ServerlessCaches[0].Status' \
  --output text)

echo "Status: $STATUS"

if [ "$STATUS" == "available" ]; then
    echo "✅ Redis disponível!"
    
    ENDPOINT=$(aws elasticache describe-serverless-caches \
      --serverless-cache-name marabet-redis \
      --region eu-west-1 \
      --query 'ServerlessCaches[0].Endpoint.Address' \
      --output text)
    
    PORT=$(aws elasticache describe-serverless-caches \
      --serverless-cache-name marabet-redis \
      --region eu-west-1 \
      --query 'ServerlessCaches[0].Endpoint.Port' \
      --output text)
    
    echo ""
    echo "Endpoint: $ENDPOINT"
    echo "Port: $PORT"
    echo ""
    echo "Connection URL:"
    echo "rediss://$ENDPOINT:$PORT"
    
elif [ "$STATUS" == "creating" ]; then
    echo "⏳ Redis ainda sendo criado..."
    echo "   Aguarde aproximadamente 5-10 minutos"
    echo ""
    echo "Execute novamente este script em alguns minutos"
else
    echo "⚠️  Status inesperado: $STATUS"
fi
```

---

## 📊 RECURSOS CRIADOS

### **VPC e Rede:**
```
VPC:               vpc-081a8c63b16a94a3a
Subnets (3):
  - subnet-061544d7c4c85bd82 (eu-west-1b)
  - subnet-0f4df2ddacfc070bc (eu-west-1c)
  - subnet-0575567cf09ae0e02 (eu-west-1a)
```

### **Segurança:**
```
Security Group:    sg-09f7d3d37a8407f43
Encryption:
  - At Rest:       AWS owned KMS key
  - In Transit:    Enabled (TLS)
```

### **ElastiCache:**
```
Name:              marabet-redis
ARN:               arn:aws:elasticache:eu-west-1:206749730888:serverlesscache:marabet-redis
Type:              Serverless
Engine:            Valkey (Redis-compatible)
Status:            Creating → Available
Multi-AZ:          Yes (3 AZs)
```

---

## ✅ VANTAGENS SERVERLESS

### **Comparado ao Cluster Tradicional:**

| Aspecto | Serverless | Cluster Tradicional |
|---------|------------|---------------------|
| **Provisionamento** | Automático | Manual |
| **Escalabilidade** | Auto-scaling | Manual ou com políticas |
| **Custo Baixa Carga** | Mais barato | Fixo (mesmo sem uso) |
| **Custo Alta Carga** | Pode ser mais caro | Previsível |
| **Manutenção** | Zero | Patches, upgrades |
| **Complexidade** | Baixa | Média |

**Recomendação**: Serverless é ideal para começar!

---

## 📞 PRÓXIMOS PASSOS

1. ⏳ **Aguardar** status = available (~5-10 minutos)

2. **Obter Endpoint:**
   ```bash
   aws elasticache describe-serverless-caches \
     --serverless-cache-name marabet-redis \
     --region eu-west-1
   ```

3. **Configurar .env:**
   ```bash
   REDIS_HOST=marabet-redis.xxxxx.serverless.euw1.cache.amazonaws.com
   REDIS_PORT=6379
   REDIS_SSL=true
   ```

4. **Testar Conexão:**
   ```bash
   python redis_config.py
   ```

5. **Integrar na Aplicação:**
   ```python
   from redis_config import get_redis_client
   redis_client = get_redis_client()
   ```

---

## 📋 CHECKLIST

- [x] ElastiCache Serverless criado
- [x] Nome: marabet-redis
- [x] VPC e Subnets configurados
- [x] Security Group configurado
- [x] Encryption habilitada
- [ ] Status = available (aguardando)
- [ ] Endpoint obtido
- [ ] Conexão testada
- [ ] .env configurado
- [ ] Aplicação integrada

---

**💾 ElastiCache Redis Serverless Criado!**  
**⏳ Aguardando Disponibilidade (5-10 minutos)**  
**🔒 Encryption Enabled (At-rest + In-transit)**  
**✅ Multi-AZ (3 Zonas)**  
**☁️ MaraBet AI - Powered by AWS ElastiCache Serverless**

