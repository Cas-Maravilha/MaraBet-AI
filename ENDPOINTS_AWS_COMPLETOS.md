# 🔗 ENDPOINTS AWS - MARABET AI

**Data**: 27 de Outubro de 2025  
**Região**: eu-west-1 (Irlanda)  
**Status**: ✅ Todos Disponíveis

---

## 📊 RESUMO EXECUTIVO

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     ✅ INFRAESTRUTURA AWS CORE CRIADA                         ║
║        RDS PostgreSQL + Redis Serverless                      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🗄️ RDS POSTGRESQL

### **Informações:**

```yaml
Instance ID:          database-1
Status:               available ✅
Endpoint:             database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com
Port:                 5432

Engine:               PostgreSQL 15.10
Instance Class:       db.m7g.large (2 vCPUs, 8GB RAM)
Storage:              100GB (Encrypted)
Multi-AZ:             No (Single AZ)
Availability Zone:    eu-west-1c
```

### **Credenciais:**

```yaml
Username:             marabet_admin
Password:             GuF#Y(!j38Bgw|YyT<r0J5>yxD3n
Database:             marabet_production (criar)

Secret Manager:       rds!db-3758a324-12a2-4675-b5ff-b92acdf38483
Secret ARN:           arn:aws:secretsmanager:eu-west-1:206749730888:secret:rds!db-3758a324-12a2-4675-b5ff-b92acdf38483-BpTjIS
```

### **Connection String:**

```
postgresql://marabet_admin:GuF#Y(!j38Bgw|YyT<r0J5>yxD3n@database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com:5432/marabet_production?sslmode=require
```

---

## 💾 ELASTICACHE REDIS

### **Informações:**

```yaml
Nome:                 marabet-redis
Status:               available ✅
Endpoint:             marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com
Port:                 6379

Engine:               Valkey 7.2 (Redis-compatible)
Type:                 Serverless
Multi-AZ:             Yes (3 AZs)
Availability Zones:   eu-west-1a, eu-west-1b, eu-west-1c
```

### **Segurança:**

```yaml
Encryption At-Rest:   Yes (AWS owned KMS)
Encryption In-Transit: Yes (TLS)
Security Group:       sg-09f7d3d37a8407f43
VPC:                  vpc-081a8c63b16a94a3a
Public Access:        No
```

### **Connection String:**

```
rediss://marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com:6379
```

---

## 📝 VARIÁVEIS DE AMBIENTE (.env)

### **Adicionar ao .env do MaraBet:**

```bash
# ==================================
# AWS INFRASTRUCTURE
# ==================================

# RDS PostgreSQL
DATABASE_URL=postgresql://marabet_admin:GuF#Y(!j38Bgw|YyT<r0J5>yxD3n@database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com:5432/marabet_production?sslmode=require
DB_HOST=database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=marabet_production
DB_USER=marabet_admin
DB_PASSWORD=GuF#Y(!j38Bgw|YyT<r0J5>yxD3n
DB_SSL_MODE=require

# ElastiCache Redis Serverless
REDIS_URL=rediss://marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com:6379
REDIS_HOST=marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_SSL=true
REDIS_TLS=true
REDIS_DB=0

# AWS General
AWS_REGION=eu-west-1
AWS_ACCOUNT_ID=206749730888

# Secrets Manager
DB_SECRET_ARN=arn:aws:secretsmanager:eu-west-1:206749730888:secret:rds!db-3758a324-12a2-4675-b5ff-b92acdf38483-BpTjIS
```

---

## 🐍 USO NO CÓDIGO PYTHON

### **Database (RDS):**

```python
from db_config import get_connection_string, get_credentials

# Opção 1: Connection string
DATABASE_URL = get_connection_string()

# Opção 2: Credenciais individuais
creds = get_credentials()

# Opção 3: SQLAlchemy
from sqlalchemy import create_engine
engine = create_engine(get_connection_string())
```

### **Cache (Redis):**

```python
from redis_config import get_redis_client

# Obter cliente Redis
redis_client = get_redis_client()

# Cache de previsões
import json
predictions = {'matches': [...]}
redis_client.set('predictions:today', json.dumps(predictions), ex=3600)

# Recuperar cache
cached = redis_client.get('predictions:today')
if cached:
    predictions = json.loads(cached)

# Rate limiting
key = f'rate_limit:user:{user_id}'
if redis_client.incr(key) > 100:
    raise Exception("Rate limit exceeded")
redis_client.expire(key, 3600)
```

---

## 🔍 VERIFICAR RECURSOS

### **Status Geral:**

```bash
# RDS
aws rds describe-db-instances \
  --region eu-west-1 \
  --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus,Endpoint.Address]' \
  --output table

# Redis
aws elasticache describe-serverless-caches \
  --region eu-west-1 \
  --query 'ServerlessCaches[*].[ServerlessCacheName,Status,Endpoint.Address]' \
  --output table

# VPC
aws ec2 describe-vpcs \
  --region eu-west-1 \
  --query 'Vpcs[*].[VpcId,CidrBlock,Tags[?Key==`Name`].Value|[0]]' \
  --output table
```

---

## 🏗️ ARQUITETURA ATUAL

```
AWS Account: 206749730888
Region: eu-west-1 (Irlanda)

VPC: vpc-081a8c63b16a94a3a
├── Subnets:
│   ├── subnet-061544d7c4c85bd82 (eu-west-1b)
│   ├── subnet-0f4df2ddacfc070bc (eu-west-1c)
│   └── subnet-0575567cf09ae0e02 (eu-west-1a)
│
├── Security Groups:
│   └── sg-09f7d3d37a8407f43 (Redis)
│
├── RDS PostgreSQL:
│   ├── database-1 (db.m7g.large)
│   ├── PostgreSQL 15.10
│   ├── Endpoint: database-1.c74amy6m4xhz...
│   └── Single AZ (eu-west-1c)
│
└── ElastiCache Redis:
    ├── marabet-redis (Serverless)
    ├── Valkey 7.2
    ├── Endpoint: marabet-redis-zxaq7e.serverless...
    └── Multi-AZ (3 zones)
```

---

## ⏭️ PRÓXIMOS RECURSOS A CRIAR

### **1. EC2 Instance (Aplicação)**

```bash
Especificações:
├── Type: t3.large (2 vCPUs, 8GB RAM)
├── OS: Ubuntu 22.04 LTS
├── Storage: 100GB gp3 SSD
├── Security Group: marabet-web-sg
└── Subnet: Pública

Finalidade:
├── Rodar aplicação MaraBet AI
├── Docker + Docker Compose
├── Nginx como proxy
└── Conectar ao RDS e Redis
```

### **2. Application Load Balancer**

```bash
Finalidade:
├── Distribuir tráfego
├── SSL/TLS termination
├── Health checks
└── Alta disponibilidade
```

### **3. Route 53 (DNS)**

```bash
Domínio: marabet.ao
├── Registro A → ALB
├── SSL Certificate (ACM)
└── Health checks
```

### **4. S3 Buckets**

```bash
Buckets:
├── marabet-backups (backups)
├── marabet-static (assets)
└── marabet-logs (logs)
```

---

## 💰 CUSTOS ATUAIS

| Recurso | Custo/mês |
|---------|-----------|
| **RDS db.m7g.large** | ~$140 |
| **Redis Serverless** | ~$50-120 |
| **TOTAL ATUAL** | **~$190-260/mês** |

### **Custos Adicionais ao Criar EC2:**

| Recurso Adicional | Custo/mês |
|-------------------|-----------|
| **EC2 t3.large** | ~$67 |
| **ALB** | ~$25 |
| **S3 (100GB)** | ~$3 |
| **Route 53** | ~$1 |
| **CloudWatch** | ~$10 |
| **Data Transfer** | ~$30 |
| **TOTAL COMPLETO** | **~$326-396/mês** |

---

## 📋 CHECKLIST

### **Recursos Criados:**
- [x] VPC e Subnets
- [x] Security Groups
- [x] RDS PostgreSQL (available)
- [x] ElastiCache Redis Serverless (available)
- [x] Endpoints anotados
- [x] Credenciais salvas
- [x] Arquivos de configuração gerados

### **Próximos Passos:**
- [ ] Criar EC2 Instance
- [ ] Configurar Nginx na EC2
- [ ] Deploy aplicação na EC2
- [ ] Criar Application Load Balancer
- [ ] Configurar Route 53
- [ ] Solicitar SSL Certificate
- [ ] Criar S3 Buckets
- [ ] Configurar CloudWatch
- [ ] Executar migrações
- [ ] Validar sistema completo

---

## 📞 OBTER ENDPOINTS NOVAMENTE

### **RDS:**
```bash
aws rds describe-db-instances \
  --db-instance-identifier database-1 \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

### **Redis:**
```bash
aws elasticache describe-serverless-caches \
  --serverless-cache-name marabet-redis \
  --query 'ServerlessCaches[0].Endpoint.Address' \
  --output text
```

### **PowerShell:**
```powershell
# RDS
.\Obter-EndpointRDS.ps1

# Redis
.\Obter-EndpointRedis.ps1
```

---

## 📚 DOCUMENTAÇÃO DISPONÍVEL

### **Guias de Deploy:**
1. ✅ AWS_DEPLOYMENT_GUIDE.md (878 linhas)
2. ✅ AWS_MIGRACAO_DADOS_COMPLETA.md (799 linhas)
3. ✅ AWS_IMPLEMENTACAO_RESUMO.md (308 linhas)

### **Database:**
4. ✅ RDS_CRIADO_INFORMACOES.md
5. ✅ RDS_INTEGRACAO_MULTILINGUAGEM.md
6. ✅ CRIAR_RDS_PASSO_A_PASSO.md

### **Redis:**
7. ✅ REDIS_SERVERLESS_CRIADO.md
8. ✅ CRIAR_REDIS_PASSO_A_PASSO.md

### **Módulos de Código:**
9. ✅ db_config.py (330 linhas) - Python RDS
10. ✅ redis_config.py (347 linhas) - Python Redis
11. ✅ db-config.js (280 linhas) - Node.js RDS
12. ✅ DatabaseConfig.java (220 linhas) - Java RDS
13. ✅ DatabaseConfig.php (240 linhas) - PHP RDS
14. ✅ DatabaseConfig.cs (210 linhas) - C# RDS

### **Scripts:**
15. ✅ obter_endpoint_rds.sh
16. ✅ Obter-EndpointRDS.ps1
17. ✅ obter_endpoint_redis.sh
18. ✅ Obter-EndpointRedis.ps1
19. ✅ setup_rds_marabet.sh
20. ✅ criar_redis_completo.sh

**Total**: 20+ arquivos | 4.000+ linhas de código/documentação

---

## ✅ STATUS INFRAESTRUTURA

| Componente | Status | Endpoint | Custo/mês |
|------------|--------|----------|-----------|
| **VPC** | ✅ Ativa | vpc-081a8c63b16a94a3a | Grátis |
| **Subnets** | ✅ 3 criadas | Múltiplas AZs | Grátis |
| **Security Groups** | ✅ Configurados | sg-09f7d3d37a8407f43 | Grátis |
| **RDS PostgreSQL** | ✅ Available | database-1.c74amy6m4xhz... | ~$140 |
| **Redis Serverless** | ✅ Available | marabet-redis-zxaq7e... | ~$50-120 |
| **EC2** | ⏳ A criar | - | ~$67 |
| **ALB** | ⏳ A criar | - | ~$25 |
| **Route 53** | ⏳ A configurar | marabet.ao | ~$1 |

**Total Atual**: ~$190-260/mês  
**Total Projetado**: ~$326-396/mês (após EC2 e ALB)

---

## 🔗 CONNECTION STRINGS COMPLETAS

### **Para .env:**

```bash
# ==================================
# AWS - RDS POSTGRESQL
# ==================================
DATABASE_URL=postgresql://marabet_admin:GuF#Y(!j38Bgw|YyT<r0J5>yxD3n@database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com:5432/marabet_production?sslmode=require
DB_HOST=database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=marabet_production
DB_USER=marabet_admin
DB_PASSWORD=GuF#Y(!j38Bgw|YyT<r0J5>yxD3n
DB_SSL_MODE=require

# ==================================
# AWS - ELASTICACHE REDIS
# ==================================
REDIS_URL=rediss://marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com:6379
REDIS_HOST=marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_SSL=true
REDIS_TLS=true
REDIS_DB=0

# ==================================
# AWS GENERAL
# ==================================
AWS_REGION=eu-west-1
AWS_ACCOUNT_ID=206749730888
```

---

## 🔧 TESTAR CONEXÕES (na EC2)

### **Quando criar a EC2, executar:**

```bash
# 1. Instalar clients
sudo apt update
sudo apt install -y postgresql-client redis-tools

# 2. Testar RDS PostgreSQL
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d postgres

# Password: GuF#Y(!j38Bgw|YyT<r0J5>yxD3n

# Criar database
CREATE DATABASE marabet_production;
\l
\q

# 3. Testar Redis
redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com \
          -p 6379 \
          --tls \
          --insecure

# Comandos
PING
SET test "MaraBet OK"
GET test
INFO server
```

---

## 🎯 PRÓXIMO PASSO: CRIAR EC2

### **Especificações Recomendadas:**

```yaml
Instance Type:        t3.large (2 vCPUs, 8GB RAM)
AMI:                  Ubuntu 22.04 LTS
Storage:              100GB gp3 SSD
Subnet:               Subnet Pública (com auto-assign public IP)
Security Group:       marabet-web-sg (80, 443, 22)
Key Pair:             marabet-key (criar ou usar existente)

Software a Instalar:
├── Docker + Docker Compose
├── Nginx
├── PostgreSQL Client
├── Redis Tools
├── Git
└── AWS CLI
```

### **Comando para Criar EC2:**

```bash
# Obter AMI Ubuntu 22.04 mais recente
AMI_ID=$(aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text \
  --region eu-west-1)

# Criar Key Pair (se não tiver)
aws ec2 create-key-pair \
  --key-name marabet-key \
  --query 'KeyMaterial' \
  --output text \
  --region eu-west-1 > marabet-key.pem

chmod 400 marabet-key.pem

# Lançar EC2
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.large \
  --key-name marabet-key \
  --subnet-id <SUBNET_PUBLICA_ID> \
  --security-group-ids <WEB_SG_ID> \
  --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=100,VolumeType=gp3}' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=marabet-app}]' \
  --region eu-west-1
```

---

## 📊 ARQUITETURA COMPLETA (Atual)

```
Internet
    │
    ↓ (A criar: Route 53 → ALB)
    │
    ↓ (A criar: EC2 Instance)
    │
    ├─────────────────────────────────┐
    │          VPC                     │
    │  vpc-081a8c63b16a94a3a          │
    │                                  │
    │  ✅ RDS PostgreSQL               │
    │     database-1                   │
    │     db.m7g.large                 │
    │     eu-west-1c                   │
    │                                  │
    │  ✅ ElastiCache Redis            │
    │     marabet-redis                │
    │     Serverless Valkey 7.2        │
    │     Multi-AZ (a, b, c)           │
    │                                  │
    └──────────────────────────────────┘
```

---

## ✅ CHECKLIST COMPLETO

### **Infraestrutura Core (Concluída):**
- [x] AWS Account configurada (206749730888)
- [x] AWS CLI configurado
- [x] Região selecionada (eu-west-1)
- [x] VPC criada (vpc-081a8c63b16a94a3a)
- [x] Subnets criadas (3)
- [x] Security Groups configurados
- [x] RDS PostgreSQL criado e disponível
- [x] Redis Serverless criado e disponível
- [x] Endpoints anotados
- [x] Credenciais salvas
- [x] Módulos Python criados
- [x] Documentação completa

### **Próxima Fase (Aplicação):**
- [ ] Criar EC2 Instance
- [ ] Configurar EC2 (Docker, Nginx, etc.)
- [ ] Deploy código MaraBet
- [ ] Testar RDS da EC2
- [ ] Testar Redis da EC2
- [ ] Executar migrações
- [ ] Iniciar aplicação

### **Próxima Fase (Load Balancing):**
- [ ] Criar Application Load Balancer
- [ ] Configurar Target Group
- [ ] Registrar EC2 no Target Group
- [ ] Configurar Health Checks

### **Próxima Fase (DNS e SSL):**
- [ ] Configurar Route 53
- [ ] Solicitar SSL Certificate (ACM)
- [ ] Apontar marabet.ao para ALB
- [ ] Validar HTTPS

---

## 📞 SUPORTE

**MaraBet AI:**
- 📧 Técnico: suporte@marabet.ao
- 📧 Comercial: comercial@marabet.ao
- 📞 WhatsApp: +224 932027393

**AWS:**
- 📚 Documentação: https://docs.aws.amazon.com
- 💬 Suporte: Via Console AWS

---

**✅ Endpoints Anotados e Salvos!**  
**🗄️ RDS: database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com**  
**💾 Redis: marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com**  
**🚀 Próximo Passo: Criar EC2 Instance!**  
**☁️ MaraBet AI - Infraestrutura AWS em Produção**

