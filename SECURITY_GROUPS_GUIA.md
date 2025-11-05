# 🔒 GUIA COMPLETO - SECURITY GROUPS AWS

**Sistema**: MaraBet AI  
**Região**: eu-west-1 (Irlanda)  
**Componentes**: EC2/Web, RDS PostgreSQL, ElastiCache Redis

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Security Group Web/Application](#1-security-group-webapplication)
3. [Security Group RDS PostgreSQL](#2-security-group-rds-postgresql)
4. [Security Group Redis](#3-security-group-elasticache-redis)
5. [Diagrama de Segurança](#diagrama-de-segurança)
6. [Script Automático](#script-automático)
7. [Verificação](#verificação)

---

## 🎯 VISÃO GERAL

### **Security Groups Necessários:**

| Nome | Propósito | Portas | Origem |
|------|-----------|--------|--------|
| **marabet-web-sg** | EC2/Aplicação | 80, 443, 22, 8000 | Internet (0.0.0.0/0) |
| **marabet-rds-sg** | RDS PostgreSQL | 5432 | Web SG apenas |
| **marabet-redis-sg** | ElastiCache Redis | 6379 | Web SG apenas |

### **Princípio de Segurança:**

```
Internet → Web SG (EC2) → RDS SG (Database)
                       → Redis SG (Cache)

✅ RDS e Redis NÃO são acessíveis da internet
✅ Apenas EC2 pode acessar RDS e Redis
✅ Princípio do menor privilégio
```

---

## 1️⃣ SECURITY GROUP WEB/APPLICATION

### **Criar Security Group:**

```bash
# Obter VPC ID
VPC_ID=$(aws ec2 describe-vpcs \
  --filters "Name=tag:Name,Values=marabet-vpc" \
  --region eu-west-1 \
  --query 'Vpcs[0].VpcId' \
  --output text)

echo "VPC ID: $VPC_ID"

# Criar Web SG
SG_WEB=$(aws ec2 create-security-group \
  --group-name marabet-web-sg \
  --description "Security group for MaraBet Web/Application" \
  --vpc-id $VPC_ID \
  --region eu-west-1 \
  --query 'GroupId' \
  --output text)

echo "Web SG: $SG_WEB"

# Adicionar tags
aws ec2 create-tags \
  --resources $SG_WEB \
  --tags Key=Name,Value=marabet-web-sg Key=Environment,Value=production \
  --region eu-west-1
```

### **Adicionar Regras de Entrada:**

```bash
# HTTP (porta 80)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1

# HTTPS (porta 443)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1

# SSH (porta 22)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1

# Aplicação (porta 8000)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1
```

### **Verificar Regras:**

```bash
aws ec2 describe-security-groups \
  --group-ids $SG_WEB \
  --region eu-west-1 \
  --query 'SecurityGroups[0].IpPermissions[*].[IpProtocol,FromPort,ToPort,IpRanges[0].CidrIp]' \
  --output table
```

**Resultado Esperado:**
```
-----------------------------------
| DescribeSecurityGroups          |
+------+-------+-------+----------+
| tcp  |  22   |  22   | 0.0.0.0/0|
| tcp  |  80   |  80   | 0.0.0.0/0|
| tcp  |  443  |  443  | 0.0.0.0/0|
| tcp  |  8000 |  8000 | 0.0.0.0/0|
+------+-------+-------+----------+
```

---

## 2️⃣ SECURITY GROUP RDS POSTGRESQL

### **Criar Security Group:**

```bash
# Criar RDS SG
SG_RDS=$(aws ec2 create-security-group \
  --group-name marabet-rds-sg \
  --description "Security group for MaraBet RDS PostgreSQL" \
  --vpc-id $VPC_ID \
  --region eu-west-1 \
  --query 'GroupId' \
  --output text)

echo "RDS SG: $SG_RDS"

# Adicionar tags
aws ec2 create-tags \
  --resources $SG_RDS \
  --tags Key=Name,Value=marabet-rds-sg Key=Environment,Value=production Key=Service,Value=RDS \
  --region eu-west-1
```

### **Permitir PostgreSQL apenas do Web SG:**

```bash
# PostgreSQL (porta 5432) apenas do Web SG
aws ec2 authorize-security-group-ingress \
  --group-id $SG_RDS \
  --protocol tcp \
  --port 5432 \
  --source-group $SG_WEB \
  --region eu-west-1
```

### **Verificar Regra:**

```bash
aws ec2 describe-security-groups \
  --group-ids $SG_RDS \
  --region eu-west-1 \
  --query 'SecurityGroups[0].IpPermissions[*].[IpProtocol,FromPort,ToPort,UserIdGroupPairs[0].GroupId]' \
  --output table
```

**Resultado Esperado:**
```
-----------------------------------
| DescribeSecurityGroups          |
+------+------+------+------------+
| tcp  | 5432 | 5432 | sg-xxxxx   |
+------+------+------+------------+
```

---

## 3️⃣ SECURITY GROUP ELASTICACHE REDIS

### **Criar Security Group:**

```bash
# Criar Redis SG
SG_REDIS=$(aws ec2 create-security-group \
  --group-name marabet-redis-sg \
  --description "Security group for MaraBet ElastiCache Redis" \
  --vpc-id $VPC_ID \
  --region eu-west-1 \
  --query 'GroupId' \
  --output text)

echo "Redis SG: $SG_REDIS"

# Adicionar tags
aws ec2 create-tags \
  --resources $SG_REDIS \
  --tags Key=Name,Value=marabet-redis-sg Key=Environment,Value=production Key=Service,Value=Redis \
  --region eu-west-1
```

### **Permitir Redis apenas do Web SG:**

```bash
# Redis (porta 6379) apenas do Web SG
aws ec2 authorize-security-group-ingress \
  --group-id $SG_REDIS \
  --protocol tcp \
  --port 6379 \
  --source-group $SG_WEB \
  --region eu-west-1
```

### **Verificar Regra:**

```bash
aws ec2 describe-security-groups \
  --group-ids $SG_REDIS \
  --region eu-west-1 \
  --query 'SecurityGroups[0].IpPermissions[*].[IpProtocol,FromPort,ToPort,UserIdGroupPairs[0].GroupId]' \
  --output table
```

**Resultado Esperado:**
```
-----------------------------------
| DescribeSecurityGroups          |
+------+------+------+------------+
| tcp  | 6379 | 6379 | sg-xxxxx   |
+------+------+------+------------+
```

---

## 🔐 DIAGRAMA DE SEGURANÇA

```
                        INTERNET
                            │
                            │ HTTP/HTTPS (80, 443)
                            │ SSH (22)
                            │ App (8000)
                            ↓
                ┌───────────────────────┐
                │   marabet-web-sg      │
                │   EC2 Instance        │
                │   (sg-xxxxxxxxx)      │
                └───────────┬───────────┘
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
          │ PostgreSQL (5432)                 │ Redis (6379)
          │                                   │
          ↓                                   ↓
┌─────────────────────┐           ┌─────────────────────┐
│ marabet-rds-sg      │           │ marabet-redis-sg    │
│ RDS PostgreSQL      │           │ ElastiCache Redis   │
│ (sg-yyyyyyyyy)      │           │ (sg-zzzzzzzzz)      │
└─────────────────────┘           └─────────────────────┘
      │                                   │
      │ Privado - Sem acesso internet     │ Privado - Sem acesso internet
      └───────────────────────────────────┘

Legenda:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ RDS e Redis estão em subnets privadas
✅ Apenas EC2 pode acessar RDS e Redis
✅ RDS e Redis NÃO são acessíveis da internet
✅ Princípio do menor privilégio aplicado
```

---

## 🚀 SCRIPT AUTOMÁTICO

### **Executar Script:**

```bash
# Tornar executável
chmod +x criar_security_groups.sh

# Executar com VPC ID
./criar_security_groups.sh vpc-xxxxxxxxx

# Ou obter VPC ID automaticamente
VPC_ID=$(aws ec2 describe-vpcs \
  --filters "Name=tag:Name,Values=marabet-vpc" \
  --region eu-west-1 \
  --query 'Vpcs[0].VpcId' \
  --output text)

./criar_security_groups.sh $VPC_ID
```

### **Resultado do Script:**

```
✅ SECURITY GROUPS CRIADOS COM SUCESSO!

Security Groups:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🌐 Web/Application:
    ID:          sg-0a1b2c3d4e5f67890
    Name:        marabet-web-sg
    Regras:
      • Porta 80   (HTTP)  ← 0.0.0.0/0
      • Porta 443  (HTTPS) ← 0.0.0.0/0
      • Porta 22   (SSH)   ← 0.0.0.0/0
      • Porta 8000 (App)   ← 0.0.0.0/0

  🗄️  RDS PostgreSQL:
    ID:          sg-1b2c3d4e5f6789012
    Name:        marabet-rds-sg
    Regras:
      • Porta 5432 (PostgreSQL) ← sg-0a1b2c3d4e5f67890

  💾 ElastiCache Redis:
    ID:          sg-2c3d4e5f67890123a
    Name:        marabet-redis-sg
    Regras:
      • Porta 6379 (Redis) ← sg-0a1b2c3d4e5f67890
```

**Arquivo Gerado**: `marabet-security-groups.txt`

---

## ✅ VERIFICAÇÃO

### **1. Listar Todos os Security Groups:**

```bash
aws ec2 describe-security-groups \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --region eu-west-1 \
  --query 'SecurityGroups[*].[GroupId,GroupName,Description]' \
  --output table
```

### **2. Ver Regras Detalhadas:**

```bash
# Ver regras do Web SG (formato JSON)
aws ec2 describe-security-groups \
  --group-ids $SG_WEB \
  --region eu-west-1 | jq '.SecurityGroups[0].IpPermissions'

# Ver regras do RDS SG
aws ec2 describe-security-groups \
  --group-ids $SG_RDS \
  --region eu-west-1 | jq '.SecurityGroups[0].IpPermissions'

# Ver regras do Redis SG
aws ec2 describe-security-groups \
  --group-ids $SG_REDIS \
  --region eu-west-1 | jq '.SecurityGroups[0].IpPermissions'
```

### **3. Testar Conectividade (após criar recursos):**

```bash
# Na EC2, testar conexão ao RDS
telnet <RDS_ENDPOINT> 5432
# Ou
nc -zv <RDS_ENDPOINT> 5432

# Testar Redis
telnet <REDIS_ENDPOINT> 6379
# Ou
nc -zv <REDIS_ENDPOINT> 6379
```

---

## 📝 USAR NOS COMANDOS SEGUINTES

### **Criar EC2:**

```bash
aws ec2 run-instances \
  --image-id ami-xxxxxxxxx \
  --instance-type t3.large \
  --key-name marabet-key \
  --security-group-ids $SG_WEB \
  --subnet-id $SUBNET_PUBLIC_A \
  --region eu-west-1
```

### **Criar RDS:**

```bash
aws rds create-db-instance \
  --db-instance-identifier marabet-db \
  --vpc-security-group-ids $SG_RDS \
  --db-subnet-group-name marabet-db-subnet-group \
  --region eu-west-1
```

### **Criar Redis:**

```bash
aws elasticache create-replication-group \
  --replication-group-id marabet-redis \
  --security-group-ids $SG_REDIS \
  --cache-subnet-group-name marabet-redis-subnet-group \
  --region eu-west-1
```

---

## 🔧 MODIFICAR REGRAS (se necessário)

### **Adicionar Regra:**

```bash
# Adicionar nova porta ao Web SG
aws ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 3000 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1
```

### **Remover Regra:**

```bash
# Remover regra
aws ec2 revoke-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1
```

### **Adicionar IP Específico:**

```bash
# Permitir SSH apenas do seu IP
aws ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 22 \
  --cidr SEU_IP/32 \
  --region eu-west-1

# Exemplo: 102.206.57.108/32
```

---

## 🔐 BOAS PRÁTICAS DE SEGURANÇA

### **1. Princípio do Menor Privilégio:**
- ✅ RDS e Redis apenas acessíveis do Web SG
- ✅ Não expostos à internet
- ✅ Subnets privadas

### **2. Restringir SSH:**
```bash
# Em produção, permitir SSH apenas do seu IP
aws ec2 revoke-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1

aws ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 22 \
  --cidr 102.206.57.108/32 \
  --region eu-west-1
```

### **3. Usar Bastion Host:**
```bash
# Para máxima segurança, usar Bastion Host
# SSH → Bastion → EC2 → RDS/Redis
```

### **4. Auditar Regularmente:**
```bash
# Listar todas as regras
aws ec2 describe-security-groups \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --region eu-west-1
```

### **5. Habilitar VPC Flow Logs:**
```bash
# Monitorar tráfego de rede
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids $VPC_ID \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --region eu-west-1
```

---

## 📊 RESUMO

| Security Group | ID | Regras Entrada |
|----------------|----|--------------------|
| **marabet-web-sg** | sg-xxxxxxxxx | 80, 443, 22, 8000 ← 0.0.0.0/0 |
| **marabet-rds-sg** | sg-yyyyyyyyy | 5432 ← Web SG |
| **marabet-redis-sg** | sg-zzzzzzzzz | 6379 ← Web SG |

---

## 📞 PRÓXIMOS PASSOS

1. ✅ Security Groups criados
2. Criar EC2 Instance com Web SG
3. Criar RDS com RDS SG
4. Criar Redis com Redis SG
5. Testar conectividade
6. Deploy da aplicação

---

**🔒 Security Groups Configurados!**  
**✅ Princípio do Menor Privilégio Aplicado**  
**☁️ MaraBet AI - Seguro na AWS**

