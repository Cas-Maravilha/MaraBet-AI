# ☁️ MARABET AI - AWS DEPLOYMENT - README COMPLETO

**Sistema**: MaraBet AI v1.0.0  
**Provedor**: Amazon Web Services (AWS)  
**Região**: eu-west-1 (Irlanda)  
**Data**: Outubro 2025

---

## 📋 ÍNDICE

1. [Visão Geral](#-visão-geral)
2. [Infraestrutura Criada](#-infraestrutura-criada)
3. [Guia Rápido de Deploy](#-guia-rápido-de-deploy)
4. [Documentação Completa](#-documentação-completa)
5. [Custos](#-custos)
6. [Suporte](#-suporte)

---

## 🎯 VISÃO GERAL

O **MaraBet AI** está completamente implementado e documentado para deploy profissional na AWS com:

✅ **12.226+ linhas** de código e documentação  
✅ **36+ arquivos** técnicos  
✅ **7 linguagens** suportadas  
✅ **Scripts automáticos** para tudo  
✅ **Infraestrutura enterprise**  

---

## ☁️ INFRAESTRUTURA CRIADA

### **✅ Disponível e Funcionando:**

```yaml
AWS Account:          206749730888
Região:               eu-west-1 (Irlanda)

VPC:
  ID:                 vpc-081a8c63b16a94a3a
  CIDR:               10.0.0.0/16
  Subnets:            3 (Multi-AZ: a, b, c)
  Status:             ✅ Configurada

RDS PostgreSQL:
  Instance:           database-1
  Endpoint:           database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com
  Port:               5432
  Engine:             PostgreSQL 15.10
  Class:              db.m7g.large (2 vCPUs, 8GB RAM)
  Storage:            100GB (Encrypted)
  Username:           marabet_admin
  Password:           YOUR_RDS_PASSWORD
  Database:           marabet_production
  Status:             ✅ Available

ElastiCache Redis:
  Nome:               marabet-redis
  Endpoint:           marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com
  Port:               6379
  Engine:             Valkey 7.2 (Redis-compatible)
  Type:               Serverless (Auto-scaling)
  Multi-AZ:           Yes (3 zones)
  Encryption:         At-rest + In-transit
  Status:             ✅ Available

Security Groups:
  Redis:              sg-09f7d3d37a8407f43
  Status:             ✅ Configurados
```

---

## 🚀 GUIA RÁPIDO DE DEPLOY

### **Passo 1: Configurar AWS CLI (5 min)**

```bash
# Instalar AWS CLI
# Windows:
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Linux/macOS:
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configurar
aws configure
# Access Key ID: YOUR_AWS_ACCESS_KEY_ID
# Secret Key: YOUR_AWS_SECRET_ACCESS_KEY
# Region: eu-west-1
# Output: json
```

### **Passo 2: Criar Key Pair SSH (1 min)**

```bash
# Criar key
aws ec2 create-key-pair \
  --key-name marabet-key \
  --query 'KeyMaterial' \
  --output text > marabet-key.pem

# Windows: Configurar permissões
.\Configurar-KeyPairWindows.ps1

# Linux/macOS:
chmod 400 marabet-key.pem
```

### **Passo 3: Lançar EC2 Instance (5 min)**

```bash
# Executar script automático
chmod +x lancar_ec2_completo.sh
./lancar_ec2_completo.sh

# Resultado:
# - EC2 criada (t3.medium)
# - Software instalado (Docker, Nginx, etc.)
# - IP público obtido
# - Pronta para receber código
```

### **Passo 4: Aguardar Setup Completar (3 min)**

```bash
# Aguardar User Data finalizar
chmod +x wait-user-data.sh
./wait-user-data.sh

# Mostrará quando setup estiver completo
```

### **Passo 5: Obter IP da EC2**

```bash
# Bash
chmod +x obter_ip_ec2.sh
./obter_ip_ec2.sh

# PowerShell
.\Obter-IpEC2.ps1

# Resultado: IP público + arquivos de configuração
```

### **Passo 6: Conectar via SSH**

```bash
./ssh-connect.sh

# OU
ssh -i marabet-key.pem ubuntu@<EC2_PUBLIC_IP>
```

### **Passo 7: Deploy MaraBet (10 min)**

```bash
# Na EC2
cd /opt/marabet

# Upload código (do seu PC)
# rsync -avz -e "ssh -i marabet-key.pem" ./ ubuntu@<EC2_IP>:/opt/marabet/

# Configurar .env
cat > .env << 'EOF'
# RDS PostgreSQL
DATABASE_URL=postgresql://marabet_admin:YOUR_RDS_PASSWORD@database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com:5432/marabet_production?sslmode=require

# Redis
REDIS_URL=rediss://marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com:6379

# API-Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Telegram
TELEGRAM_BOT_TOKEN=<SEU_TOKEN>
TELEGRAM_CHAT_ID=5550091597
EOF

# Criar database
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com -p 5432 -U marabet_admin -d postgres
CREATE DATABASE marabet_production;
\q

# Deploy
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### **Passo 8: Adicionar IP à API-Football**

```
1. Obter IP público da EC2
2. Acessar: https://dashboard.api-football.com/
3. Soccer > Settings > IP Whitelist
4. Adicionar IP: <EC2_PUBLIC_IP>
```

### **Passo 9: Testar**

```bash
# Testar aplicação
curl http://<EC2_PUBLIC_IP>/health

# Se retornar {"status": "ok"}:
# ✅ MaraBet AI rodando na AWS!
```

**Tempo Total**: ~25 minutos

---

## 📚 DOCUMENTAÇÃO COMPLETA

### **Guias Principais (4):**

1. **AWS_DEPLOYMENT_GUIDE.md** (878 linhas)
   - Deploy completo passo a passo
   - Arquitetura detalhada
   - Todos os serviços AWS

2. **AWS_MIGRACAO_DADOS_COMPLETA.md** (799 linhas)
   - Migração de código
   - Migração de database
   - Configuração completa

3. **AWS_IMPLEMENTACAO_RESUMO.md** (308 linhas)
   - Resumo executivo
   - Comparação com alternativas
   - Justificativa técnica

4. **AWS_IMPLEMENTACAO_FINAL.md** (Guia consolidado)
   - Visão geral completa
   - Checklist final
   - Próximas fases

### **Database RDS (3):**

5. **RDS_INTEGRACAO_MULTILINGUAGEM.md** (755 linhas)
   - Integração em 7 linguagens
   - Python, Node.js, Java, PHP, C#, Go, Ruby

6. **CRIAR_RDS_PASSO_A_PASSO.md** (661 linhas)
   - Criação do RDS
   - VPC e Subnets
   - Security Groups

7. **RDS_CRIADO_INFORMACOES.md** (608 linhas)
   - Informações do RDS criado
   - Secrets Manager
   - Connection strings

### **Cache Redis (2):**

8. **CRIAR_REDIS_PASSO_A_PASSO.md** (500 linhas)
   - Criação do ElastiCache
   - Replication Group
   - Configuração

9. **REDIS_SERVERLESS_CRIADO.md** (421 linhas)
   - Redis Serverless
   - Valkey engine
   - Endpoints

### **Servidor EC2 (2):**

10. **CRIAR_EC2_GUIA_COMPLETO.md** (459 linhas)
    - Criação da EC2
    - Security Group
    - Deploy

11. **CRIAR_KEY_PAIR_AWS.md**
    - SSH Key Pair
    - Permissões
    - Troubleshooting

### **Consolidação (4):**

12. **ENDPOINTS_AWS_COMPLETOS.md** (620 linhas)
    - Todos os endpoints
    - Credenciais
    - Connection strings

13. **SECURITY_GROUPS_GUIA.md** (620 linhas)
    - Security Groups
    - Regras de firewall
    - Boas práticas

14. **CONFIGURACAO_AWS_RAPIDA.md** (419 linhas)
    - Configuração rápida
    - Validação
    - Comandos úteis

15. **README_AWS_COMPLETO.md** (Este arquivo)
    - Visão geral
    - Guia rápido
    - Índice completo

---

## 💻 MÓDULOS DE CÓDIGO

### **Python (3 módulos = 1.128 linhas):**

1. **db_config.py** (330 linhas)
   - Conexão RDS via Secrets Manager
   - Suporte Django, Flask, FastAPI
   - Health check

2. **redis_config.py** (347 linhas)
   - Conexão Redis/Valkey
   - Pool de conexões
   - Cache stats

3. **exemplos_uso_db.py** (451 linhas)
   - 11 exemplos práticos
   - Diferentes frameworks
   - Casos de uso reais

### **Outras Linguagens (4 módulos = 950 linhas):**

4. **db-config.js** (280 linhas) - Node.js
5. **DatabaseConfig.java** (220 linhas) - Java
6. **DatabaseConfig.php** (240 linhas) - PHP
7. **DatabaseConfig.cs** (210 linhas) - C#/.NET

---

## 🔧 SCRIPTS AUTOMÁTICOS

### **Bash Scripts (11):**

1. **lancar_ec2_completo.sh** - Lançar EC2 completa
2. **criar_ec2_marabet.sh** - Criar EC2 (alternativo)
3. **criar_redis_completo.sh** - Criar Redis Cluster
4. **criar_rds_completo.sh** - Criar RDS
5. **criar_security_groups.sh** - Security Groups
6. **deploy_aws_completo.sh** - Deploy infraestrutura completa
7. **obter_endpoint_rds.sh** - Obter endpoint RDS
8. **obter_endpoint_redis.sh** - Obter endpoint Redis
9. **obter_ip_ec2.sh** - Obter IP EC2
10. **setup_rds_marabet.sh** - Setup RDS
11. **validar_aws_config.sh** - Validar configuração

### **PowerShell Scripts (3):**

1. **Obter-EndpointRDS.ps1** - Endpoint RDS (Windows)
2. **Obter-EndpointRedis.ps1** - Endpoint Redis (Windows)
3. **Obter-IpEC2.ps1** - IP EC2 (Windows)
4. **Configurar-KeyPairWindows.ps1** - Permissões Key

### **User Data:**

- **user-data.sh** (330+ linhas) - Inicialização EC2 otimizada

---

## 💰 CUSTOS

### **Configuração Atual:**

| Recurso | Especificação | Custo/mês |
|---------|---------------|-----------|
| **RDS PostgreSQL** | db.m7g.large | $140 |
| **Redis Serverless** | Baixo uso | $50 |
| **EC2** | t3.medium | $33 |
| **Storage** | 50GB gp3 | $4 |
| **IP Elástico** | 1 IP | $3.60 |
| **Data Transfer** | 250GB | $23 |
| **SUBTOTAL** | | **~$253/mês** |

### **Próximos Recursos:**

| Recurso | Custo/mês |
|---------|-----------|
| Application Load Balancer | $25 |
| Route 53 Hosted Zone | $0.50 |
| **TOTAL COMPLETO** | **~$279/mês** |

### **Com Reserved Instances (1 ano):**

- RDS: $84/mês (40% off)
- EC2: $20/mês (40% off)
- **TOTAL**: **~$180/mês** (economia $99/mês)

---

## 🔗 CONEXÕES

### **RDS PostgreSQL:**

```bash
# Connection String
postgresql://marabet_admin:YOUR_RDS_PASSWORD@database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com:5432/marabet_production?sslmode=require

# Componentes
Host:     database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com
Port:     5432
User:     marabet_admin
Password: YOUR_RDS_PASSWORD
Database: marabet_production
```

### **Redis Serverless:**

```bash
# Connection URL
rediss://marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com:6379

# Componentes
Host:     marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com
Port:     6379
SSL/TLS:  Required
```

---

## 📖 COMO USAR ESTA DOCUMENTAÇÃO

### **Para Deploy Completo:**
👉 Leia: **AWS_DEPLOYMENT_GUIDE.md** (878 linhas)

### **Para Migração de Dados:**
👉 Leia: **AWS_MIGRACAO_DADOS_COMPLETA.md** (799 linhas)

### **Para Configuração Rápida:**
👉 Leia: **CONFIGURACAO_AWS_RAPIDA.md** (419 linhas)

### **Para Integração com Código:**
👉 Use: **db_config.py** ou **redis_config.py**  
👉 Veja exemplos: **exemplos_uso_db.py**

### **Para Criar EC2:**
👉 Execute: **./lancar_ec2_completo.sh**  
👉 Leia: **CRIAR_EC2_GUIA_COMPLETO.md**

### **Para Obter IPs/Endpoints:**
👉 Execute: **./obter_ip_ec2.sh**  
👉 Execute: **./obter_endpoint_rds.sh**  
👉 Execute: **./obter_endpoint_redis.sh**

---

## 🛠️ FERRAMENTAS CRIADAS

### **Módulos Reutilizáveis:**

```python
# Python - Conexão RDS
from db_config import get_connection_string, get_credentials
DATABASE_URL = get_connection_string()

# Python - Conexão Redis
from redis_config import get_redis_client
redis_client = get_redis_client()
```

```javascript
// Node.js - Conexão RDS
const { getConnectionString } = require('./db-config');
const DATABASE_URL = await getConnectionString();

// Node.js - Redis
const { getPool } = require('./db-config');
const pool = await getPool();
```

### **Scripts de Automação:**

```bash
# Deploy completo
./deploy_aws_completo.sh

# Criar recursos individuais
./criar_rds_completo.sh
./criar_redis_completo.sh
./lancar_ec2_completo.sh

# Obter informações
./obter_endpoint_rds.sh
./obter_endpoint_redis.sh
./obter_ip_ec2.sh
```

---

## 📊 ESTATÍSTICAS

```
Documentação:         7.048 linhas (19 guias)
Código Python:        1.128 linhas (3 módulos)
Código Multilinguagem: 950 linhas (4 linguagens)
Scripts Bash:         ~3.000 linhas (11 scripts)
Scripts PowerShell:   ~600 linhas (4 scripts)
User Data:            330 linhas

TOTAL:                ~12.226 linhas
ARQUIVOS:             36+
```

---

## ✅ CHECKLIST

- [x] AWS CLI configurado
- [x] Credenciais AWS válidas
- [x] VPC criada
- [x] Subnets configuradas
- [x] Security Groups criados
- [x] RDS PostgreSQL disponível
- [x] Redis Serverless disponível
- [x] Endpoints anotados
- [x] Módulos Python criados
- [x] Scripts automáticos prontos
- [x] Documentação completa
- [x] user-data.sh otimizado
- [ ] Key Pair criada
- [ ] EC2 lançada
- [ ] Código deployado
- [ ] Aplicação rodando
- [ ] ALB configurado
- [ ] Route 53 configurado
- [ ] SSL/HTTPS ativo

---

## 📞 SUPORTE

**MaraBet AI:**
- 📧 Técnico: suporte@marabet.ao
- 📧 Comercial: comercial@marabet.ao
- 📞 WhatsApp: +224 932027393
- 💬 Telegram: @marabet_support

**AWS:**
- 📚 Documentação: https://docs.aws.amazon.com
- 💬 Suporte: https://console.aws.amazon.com/support
- 🎓 Treinamento: https://aws.amazon.com/training

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Infraestrutura Core (RDS + Redis) - Completa
2. ⏳ **Lançar EC2** - Execute: `./lancar_ec2_completo.sh`
3. ⏳ Deploy Aplicação - Seguir guia
4. ⏳ Criar ALB - Próxima fase
5. ⏳ Configurar DNS - Route 53
6. ⏳ SSL/HTTPS - Certificate Manager

---

**✅ TUDO PRONTO PARA DEPLOY!**  
**🚀 Execute os Scripts e Coloque o MaraBet no Ar!**  
**☁️ MaraBet AI - Infraestrutura AWS de Nível Mundial**

---

**© 2025 MaraBet AI, Lda.**  
**Luanda, Angola**  
**Powered by Amazon Web Services**

