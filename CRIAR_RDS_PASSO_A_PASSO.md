# 🗄️ CRIAR RDS POSTGRESQL - PASSO A PASSO

**Sistema**: MaraBet AI  
**Região**: eu-west-1 (Irlanda)  
**Database**: PostgreSQL 15 Multi-AZ

---

## 📋 ÍNDICE

1. [Criar VPC](#1-criar-vpc)
2. [Criar Subnets](#2-criar-subnets)
3. [Configurar Internet Gateway](#3-configurar-internet-gateway)
4. [Configurar Route Tables](#4-configurar-route-tables)
5. [Criar Security Groups](#5-criar-security-groups)
6. [Criar RDS PostgreSQL](#6-criar-rds-postgresql)
7. [Verificar e Testar](#7-verificar-e-testar)

---

## 1️⃣ CRIAR VPC

### **Comando:**

```bash
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=marabet-vpc}]' \
  --region eu-west-1
```

### **Salvar VPC ID:**

```bash
# O comando retornará algo como:
# {
#     "Vpc": {
#         "VpcId": "vpc-0a1b2c3d4e5f67890",
#         ...
#     }
# }

# Salvar em variável
export VPC_ID=vpc-0a1b2c3d4e5f67890  # ← SUBSTITUIR pelo ID retornado

# Verificar
echo $VPC_ID
```

### **Habilitar DNS:**

```bash
aws ec2 modify-vpc-attribute \
  --vpc-id $VPC_ID \
  --enable-dns-support \
  --region eu-west-1

aws ec2 modify-vpc-attribute \
  --vpc-id $VPC_ID \
  --enable-dns-hostnames \
  --region eu-west-1
```

✅ **Checkpoint**: VPC criada com DNS habilitado

---

## 2️⃣ CRIAR SUBNETS

### **A. Subnet Pública (Zona A) - Para EC2:**

```bash
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone eu-west-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=marabet-public-a}]' \
  --region eu-west-1
```

**Salvar ID:**
```bash
export SUBNET_PUBLIC_A=subnet-xxxxxxxxx  # ← SUBSTITUIR
```

**Habilitar IP público automático:**
```bash
aws ec2 modify-subnet-attribute \
  --subnet-id $SUBNET_PUBLIC_A \
  --map-public-ip-on-launch \
  --region eu-west-1
```

### **B. Subnet Privada A (Zona A) - Para RDS Primary:**

```bash
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone eu-west-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=marabet-private-a}]' \
  --region eu-west-1
```

**Salvar ID:**
```bash
export SUBNET_PRIVATE_A=subnet-yyyyyyyyy  # ← SUBSTITUIR
```

### **C. Subnet Privada B (Zona B) - Para RDS Standby:**

```bash
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.3.0/24 \
  --availability-zone eu-west-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=marabet-private-b}]' \
  --region eu-west-1
```

**Salvar ID:**
```bash
export SUBNET_PRIVATE_B=subnet-zzzzzzzzz  # ← SUBSTITUIR
```

✅ **Checkpoint**: 3 subnets criadas (1 pública, 2 privadas)

---

## 3️⃣ CONFIGURAR INTERNET GATEWAY

### **Criar IGW:**

```bash
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=marabet-igw}]' \
  --region eu-west-1
```

**Salvar ID:**
```bash
export IGW_ID=igw-xxxxxxxxxxxxx  # ← SUBSTITUIR
```

### **Anexar à VPC:**

```bash
aws ec2 attach-internet-gateway \
  --internet-gateway-id $IGW_ID \
  --vpc-id $VPC_ID \
  --region eu-west-1
```

✅ **Checkpoint**: Internet Gateway criado e anexado

---

## 4️⃣ CONFIGURAR ROUTE TABLES

### **Criar Route Table Pública:**

```bash
aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=marabet-public-rt}]' \
  --region eu-west-1
```

**Salvar ID:**
```bash
export RTB_PUBLIC=rtb-xxxxxxxxxxxxx  # ← SUBSTITUIR
```

### **Adicionar Rota para Internet:**

```bash
aws ec2 create-route \
  --route-table-id $RTB_PUBLIC \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID \
  --region eu-west-1
```

### **Associar Subnet Pública:**

```bash
aws ec2 associate-route-table \
  --route-table-id $RTB_PUBLIC \
  --subnet-id $SUBNET_PUBLIC_A \
  --region eu-west-1
```

✅ **Checkpoint**: Route Table configurada com acesso à internet

---

## 5️⃣ CRIAR SECURITY GROUPS

### **A. Security Group para EC2 (Web/App):**

```bash
aws ec2 create-security-group \
  --group-name marabet-web-sg \
  --description "MaraBet Web/Application Security Group" \
  --vpc-id $VPC_ID \
  --region eu-west-1
```

**Salvar ID:**
```bash
export SG_WEB=sg-xxxxxxxxxxxxx  # ← SUBSTITUIR
```

**Adicionar Regras:**
```bash
# HTTP
aws ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1

# HTTPS
aws ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1

# SSH
aws ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1
```

### **B. Security Group para RDS:**

```bash
aws ec2 create-security-group \
  --group-name marabet-rds-sg \
  --description "MaraBet RDS PostgreSQL Security Group" \
  --vpc-id $VPC_ID \
  --region eu-west-1
```

**Salvar ID:**
```bash
export SG_RDS=sg-yyyyyyyyyyyyy  # ← SUBSTITUIR
```

**Permitir PostgreSQL apenas do Web SG:**
```bash
aws ec2 authorize-security-group-ingress \
  --group-id $SG_RDS \
  --protocol tcp \
  --port 5432 \
  --source-group $SG_WEB \
  --region eu-west-1
```

✅ **Checkpoint**: Security Groups criados e configurados

---

## 6️⃣ CRIAR RDS POSTGRESQL

### **A. Criar DB Subnet Group:**

```bash
aws rds create-db-subnet-group \
  --db-subnet-group-name marabet-db-subnet-group \
  --db-subnet-group-description "MaraBet RDS Subnet Group" \
  --subnet-ids $SUBNET_PRIVATE_A $SUBNET_PRIVATE_B \
  --tags "Key=Name,Value=marabet-db-subnet-group" \
  --region eu-west-1
```

### **B. Criar RDS PostgreSQL Multi-AZ:**

```bash
aws rds create-db-instance \
  --db-instance-identifier marabet-db \
  --db-instance-class db.t3.large \
  --engine postgres \
  --engine-version 15.4 \
  --master-username marabetadmin \
  --master-user-password 'MaraBet2025#Secure!' \
  --allocated-storage 100 \
  --storage-type gp3 \
  --vpc-security-group-ids $SG_RDS \
  --db-subnet-group-name marabet-db-subnet-group \
  --backup-retention-period 7 \
  --preferred-backup-window "02:00-03:00" \
  --preferred-maintenance-window "sun:03:00-sun:04:00" \
  --multi-az \
  --no-publicly-accessible \
  --storage-encrypted \
  --enable-cloudwatch-logs-exports '["postgresql"]' \
  --deletion-protection \
  --tags "Key=Name,Value=marabet-db" "Key=Environment,Value=production" \
  --region eu-west-1
```

### **⏰ Aguardar Criação:**

```bash
# O RDS leva ~10-15 minutos para ficar disponível
echo "Aguardando RDS ficar disponível..."
aws rds wait db-instance-available \
  --db-instance-identifier marabet-db \
  --region eu-west-1

echo "✅ RDS disponível!"
```

### **C. Obter Endpoint do RDS:**

```bash
export RDS_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier marabet-db \
  --region eu-west-1 \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

echo "RDS Endpoint: $RDS_ENDPOINT"
```

✅ **Checkpoint**: RDS PostgreSQL Multi-AZ criado e disponível

---

## 7️⃣ VERIFICAR E TESTAR

### **A. Verificar Status do RDS:**

```bash
aws rds describe-db-instances \
  --db-instance-identifier marabet-db \
  --region eu-west-1 \
  --query 'DBInstances[0].[DBInstanceIdentifier,DBInstanceStatus,Engine,EngineVersion,MultiAZ,StorageEncrypted,Endpoint.Address]' \
  --output table
```

**Resultado esperado:**
```
----------------------------------------------------------
| DescribeDBInstances                                     |
+--------------------+-----------------------------------+
| marabet-db         | available                         |
| postgres           | 15.4                              |
| True               | True                              |
| marabet-db.xxxxx.eu-west-1.rds.amazonaws.com          |
+--------------------+-----------------------------------+
```

### **B. Testar Conexão (após criar EC2):**

```bash
# Instalar PostgreSQL client (se não tiver)
sudo apt install -y postgresql-client

# Testar conexão
psql -h $RDS_ENDPOINT -U marabetadmin -d postgres

# Quando solicitar senha: MaraBet2025#Secure!

# Se conectar, criar database:
CREATE DATABASE marabet;

# Listar databases
\l

# Sair
\q
```

### **C. Ver Informações Completas:**

```bash
aws rds describe-db-instances \
  --db-instance-identifier marabet-db \
  --region eu-west-1 > rds-info.json

# Ver endpoint
cat rds-info.json | jq -r '.DBInstances[0].Endpoint.Address'

# Ver porta
cat rds-info.json | jq -r '.DBInstances[0].Endpoint.Port'

# Ver Multi-AZ
cat rds-info.json | jq -r '.DBInstances[0].MultiAZ'

# Ver status
cat rds-info.json | jq -r '.DBInstances[0].DBInstanceStatus'
```

---

## 📝 RESUMO DOS RECURSOS CRIADOS

### **VPC e Rede:**
```
VPC:                  $VPC_ID (10.0.0.0/16)
Subnet Pública A:     $SUBNET_PUBLIC_A (10.0.1.0/24) - eu-west-1a
Subnet Privada A:     $SUBNET_PRIVATE_A (10.0.2.0/24) - eu-west-1a
Subnet Privada B:     $SUBNET_PRIVATE_B (10.0.3.0/24) - eu-west-1b
Internet Gateway:     $IGW_ID
Route Table Pública:  $RTB_PUBLIC
```

### **Security Groups:**
```
Web/App SG:           $SG_WEB (80, 443, 22)
RDS SG:               $SG_RDS (5432 apenas de $SG_WEB)
```

### **Database:**
```
RDS Instance:         marabet-db
Engine:               PostgreSQL 15.4
Class:                db.t3.large (2 vCPUs, 8GB RAM)
Storage:              100GB gp3 (encrypted)
Multi-AZ:             Yes
Endpoint:             $RDS_ENDPOINT
Port:                 5432
Username:             marabetadmin
Password:             MaraBet2025#Secure!
Database:             postgres (criar 'marabet')
Backup:               7 dias (02:00-03:00 UTC)
Maintenance:          Domingos 03:00-04:00 UTC
```

---

## 🔐 CREDENCIAIS DO DATABASE

```bash
# Endpoint
echo $RDS_ENDPOINT

# Connection String
echo "postgresql://marabetadmin:MaraBet2025#Secure!@$RDS_ENDPOINT:5432/marabet"

# Para usar no .env:
DATABASE_URL=postgresql://marabetadmin:MaraBet2025#Secure!@$RDS_ENDPOINT:5432/marabet
DB_HOST=$RDS_ENDPOINT
DB_PORT=5432
DB_NAME=marabet
DB_USER=marabetadmin
DB_PASSWORD=MaraBet2025#Secure!
```

---

## 🚀 SCRIPT COMPLETO (EXECUTAR TUDO DE UMA VEZ)

### **Salvar como: `criar_rds_completo.sh`**

```bash
#!/bin/bash

set -e

echo "🚀 Criando RDS PostgreSQL para MaraBet AI"
echo "=========================================="
echo ""

REGION="eu-west-1"

# 1. VPC
echo "1. Criando VPC..."
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=marabet-vpc}]' \
  --region $REGION \
  --query 'Vpc.VpcId' \
  --output text)
echo "   VPC: $VPC_ID"

aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support --region $REGION
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames --region $REGION

# 2. Subnets
echo "2. Criando Subnets..."
SUBNET_PUBLIC_A=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ${REGION}a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=marabet-public-a}]' \
  --region $REGION \
  --query 'Subnet.SubnetId' \
  --output text)
echo "   Public A: $SUBNET_PUBLIC_A"

aws ec2 modify-subnet-attribute --subnet-id $SUBNET_PUBLIC_A --map-public-ip-on-launch --region $REGION

SUBNET_PRIVATE_A=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone ${REGION}a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=marabet-private-a}]' \
  --region $REGION \
  --query 'Subnet.SubnetId' \
  --output text)
echo "   Private A: $SUBNET_PRIVATE_A"

SUBNET_PRIVATE_B=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.3.0/24 \
  --availability-zone ${REGION}b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=marabet-private-b}]' \
  --region $REGION \
  --query 'Subnet.SubnetId' \
  --output text)
echo "   Private B: $SUBNET_PRIVATE_B"

# 3. Internet Gateway
echo "3. Criando Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=marabet-igw}]' \
  --region $REGION \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)
echo "   IGW: $IGW_ID"

aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID --region $REGION

# 4. Route Table
echo "4. Configurando Route Table..."
RTB_PUBLIC=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=marabet-public-rt}]' \
  --region $REGION \
  --query 'RouteTable.RouteTableId' \
  --output text)
echo "   Route Table: $RTB_PUBLIC"

aws ec2 create-route --route-table-id $RTB_PUBLIC --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID --region $REGION
aws ec2 associate-route-table --route-table-id $RTB_PUBLIC --subnet-id $SUBNET_PUBLIC_A --region $REGION

# 5. Security Groups
echo "5. Criando Security Groups..."
SG_WEB=$(aws ec2 create-security-group \
  --group-name marabet-web-sg \
  --description "MaraBet Web Security Group" \
  --vpc-id $VPC_ID \
  --region $REGION \
  --query 'GroupId' \
  --output text)
echo "   Web SG: $SG_WEB"

aws ec2 authorize-security-group-ingress --group-id $SG_WEB --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $REGION
aws ec2 authorize-security-group-ingress --group-id $SG_WEB --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $REGION
aws ec2 authorize-security-group-ingress --group-id $SG_WEB --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $REGION

SG_RDS=$(aws ec2 create-security-group \
  --group-name marabet-rds-sg \
  --description "MaraBet RDS Security Group" \
  --vpc-id $VPC_ID \
  --region $REGION \
  --query 'GroupId' \
  --output text)
echo "   RDS SG: $SG_RDS"

aws ec2 authorize-security-group-ingress --group-id $SG_RDS --protocol tcp --port 5432 --source-group $SG_WEB --region $REGION

# 6. RDS
echo "6. Criando RDS PostgreSQL Multi-AZ..."
echo "   (Isso pode levar 10-15 minutos)"

aws rds create-db-subnet-group \
  --db-subnet-group-name marabet-db-subnet-group \
  --db-subnet-group-description "MaraBet RDS Subnet Group" \
  --subnet-ids $SUBNET_PRIVATE_A $SUBNET_PRIVATE_B \
  --region $REGION

aws rds create-db-instance \
  --db-instance-identifier marabet-db \
  --db-instance-class db.t3.large \
  --engine postgres \
  --engine-version 15.4 \
  --master-username marabetadmin \
  --master-user-password 'MaraBet2025#Secure!' \
  --allocated-storage 100 \
  --storage-type gp3 \
  --vpc-security-group-ids $SG_RDS \
  --db-subnet-group-name marabet-db-subnet-group \
  --backup-retention-period 7 \
  --multi-az \
  --no-publicly-accessible \
  --storage-encrypted \
  --region $REGION

echo ""
echo "Aguardando RDS ficar disponível..."
aws rds wait db-instance-available --db-instance-identifier marabet-db --region $REGION

RDS_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier marabet-db \
  --region $REGION \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

echo ""
echo "=========================================="
echo "✅ RDS CRIADO COM SUCESSO!"
echo "=========================================="
echo ""
echo "Recursos:"
echo "  VPC:              $VPC_ID"
echo "  Subnet Pública:   $SUBNET_PUBLIC_A"
echo "  Subnet Privada A: $SUBNET_PRIVATE_A"
echo "  Subnet Privada B: $SUBNET_PRIVATE_B"
echo "  Web SG:           $SG_WEB"
echo "  RDS SG:           $SG_RDS"
echo ""
echo "RDS PostgreSQL:"
echo "  Instance:         marabet-db"
echo "  Endpoint:         $RDS_ENDPOINT"
echo "  Port:             5432"
echo "  Username:         marabetadmin"
echo "  Password:         MaraBet2025#Secure!"
echo "  Database:         postgres"
echo ""
echo "Connection String:"
echo "  postgresql://marabetadmin:MaraBet2025#Secure!@$RDS_ENDPOINT:5432/marabet"
echo ""
```

---

## 💰 CUSTOS

### **RDS db.t3.large Multi-AZ:**
- **Instância**: ~$260/mês
- **Storage**: 100GB gp3 (~$13/mês)
- **Backup**: 7 dias incluído
- **Total**: ~$273/mês

---

## 📞 PRÓXIMOS PASSOS

1. ✅ RDS criado
2. Criar EC2 Instance
3. Conectar EC2 ao RDS
4. Deploy da aplicação
5. Executar migrações

---

**✅ BANCO DE DADOS RDS PRONTO PARA USO!**  
**🗄️ PostgreSQL 15.4 Multi-AZ**  
**🔒 Encrypted + Backups Automáticos**  
**☁️ MaraBet AI - Powered by AWS**

