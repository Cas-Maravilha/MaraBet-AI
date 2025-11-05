# 🚀 GUIA COMPLETO DE DEPLOY DO MARABET NA AWS

**Sistema**: MaraBet AI v1.0.0  
**Provedor**: Amazon Web Services (AWS)  
**Data**: Outubro 2025

---

## 📋 ÍNDICE

1. [Por que AWS?](#-por-que-aws)
2. [Arquitetura AWS](#-arquitetura-aws)
3. [Pré-requisitos](#-pré-requisitos)
4. [Instalação AWS CLI](#-instalação-aws-cli)
5. [Configuração de Conta](#-configuração-de-conta)
6. [Infraestrutura](#-infraestrutura)
7. [Deploy Completo](#-deploy-completo)
8. [Domínio e DNS](#-domínio-e-dns)
9. [Monitoramento](#-monitoramento)
10. [Custos](#-custos)

---

## 🎯 POR QUE AWS?

A **AWS** é a única plataforma que oferece todas as condições necessárias para hospedar o MaraBet:

### **Vantagens Exclusivas:**

✅ **Infraestrutura Global**
- 30+ regiões ao redor do mundo
- Baixa latência para Angola (região África/Europa)
- 99.99% de uptime garantido por SLA

✅ **Serviços Gerenciados**
- RDS (PostgreSQL gerenciado)
- ElastiCache (Redis gerenciado)
- S3 (Backup automático)
- CloudWatch (Monitoramento 24/7)

✅ **Escalabilidade Automática**
- Auto Scaling para tráfego variável
- Load Balancing distribuído
- CDN global (CloudFront)

✅ **Segurança de Nível Enterprise**
- Certificação ISO 27001
- Criptografia em repouso e trânsito
- WAF (Web Application Firewall)
- DDoS Protection

✅ **Compliance e Certificações**
- GDPR compliant
- SOC 1, 2, 3
- PCI DSS Level 1

✅ **Custo-Benefício**
- Free Tier (12 meses)
- Pay-as-you-go
- Reserved Instances (até 75% desconto)

---

## 🏗️ ARQUITETURA AWS

```
                          ┌─────────────────────────────────┐
                          │     Route 53 (DNS)              │
                          │     marabet.ao                  │
                          └──────────────┬──────────────────┘
                                         │
                          ┌──────────────▼──────────────────┐
                          │  CloudFront (CDN)               │
                          │  SSL/TLS Certificate            │
                          └──────────────┬──────────────────┘
                                         │
                          ┌──────────────▼──────────────────┐
                          │  Application Load Balancer      │
                          │  (ALB)                          │
                          └──────────────┬──────────────────┘
                                         │
                    ┌────────────────────┴─────────────────────┐
                    │                                          │
         ┌──────────▼──────────┐                  ┌───────────▼──────────┐
         │  EC2 Instance 1     │                  │  EC2 Instance 2      │
         │  (Application)      │                  │  (Application)       │
         │  t3.large           │                  │  t3.large            │
         └──────────┬──────────┘                  └───────────┬──────────┘
                    │                                          │
                    └────────────────────┬─────────────────────┘
                                         │
                    ┌────────────────────┴─────────────────────┐
                    │                                          │
         ┌──────────▼──────────┐                  ┌───────────▼──────────┐
         │  RDS PostgreSQL     │                  │  ElastiCache Redis   │
         │  (Multi-AZ)         │                  │  (Cluster Mode)      │
         │  db.t3.large        │                  │  cache.t3.medium     │
         └─────────────────────┘                  └──────────────────────┘
                    │
         ┌──────────▼──────────┐
         │  S3 Buckets         │
         │  - Backups          │
         │  - Static Assets    │
         │  - Logs             │
         └─────────────────────┘
```

---

## ✅ PRÉ-REQUISITOS

1. **Conta AWS** (criar em https://aws.amazon.com)
2. **Cartão de crédito** (para verificação - Free Tier disponível)
3. **Domínio marabet.ao** (registrado)
4. **Acesso administrativo** ao computador local

---

## 💻 INSTALAÇÃO AWS CLI

### **Windows (PowerShell como Admin):**

```powershell
# Baixar e instalar AWS CLI v2
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Verificar instalação
aws --version
# Esperado: aws-cli/2.x.x Python/3.x.x Windows/...
```

### **Linux (Ubuntu/Debian):**

```bash
# Baixar AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Descompactar
unzip awscliv2.zip

# Instalar
sudo ./aws/install

# Verificar
aws --version
```

### **macOS:**

```bash
# Baixar AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"

# Instalar
sudo installer -pkg AWSCLIV2.pkg -target /

# Verificar
aws --version
```

---

## 🔑 CONFIGURAÇÃO DE CONTA

### **1. Criar Access Keys:**

1. Acesse: https://console.aws.amazon.com/iam/
2. Navegue: IAM → Users → Seu usuário → Security credentials
3. Clique: **Create access key**
4. Anote: `Access Key ID` e `Secret Access Key` (não compartilhe!)

### **2. Configurar AWS CLI:**

```bash
aws configure

# Preencher:
AWS Access Key ID [None]: SEU_ACCESS_KEY_ID
AWS Secret Access Key [None]: SEU_SECRET_ACCESS_KEY
Default region name [None]: eu-west-1  # Europa (próximo de Angola)
Default output format [None]: json
```

### **3. Testar Configuração:**

```bash
# Verificar identidade
aws sts get-caller-identity

# Listar regiões disponíveis
aws ec2 describe-regions --output table
```

---

## 🏗️ INFRAESTRUTURA

### **Regiões Recomendadas para Angola:**

| Região | Nome | Latência | Recomendação |
|--------|------|----------|--------------|
| **eu-west-1** | Irlanda | ~80ms | ⭐ Melhor |
| **eu-south-1** | Milão | ~100ms | ⭐ Bom |
| **af-south-1** | Cape Town | ~120ms | ⭐ África |
| **eu-central-1** | Frankfurt | ~90ms | Alternativa |

### **Especificações Recomendadas:**

#### **Produção:**
```yaml
EC2 Application Servers:
  Type: t3.large (2 vCPUs, 8GB RAM)
  Quantity: 2 (Auto Scaling)
  OS: Ubuntu 22.04 LTS
  Storage: 100GB gp3 SSD

RDS PostgreSQL:
  Type: db.t3.large (2 vCPUs, 8GB RAM)
  Engine: PostgreSQL 15
  Storage: 100GB gp3
  Multi-AZ: Yes (alta disponibilidade)
  Backup: Automático (7 dias)

ElastiCache Redis:
  Type: cache.t3.medium (2 vCPUs, 3.09GB RAM)
  Engine: Redis 7.0
  Cluster: Yes
  Multi-AZ: Yes

Load Balancer:
  Type: Application Load Balancer
  SSL: AWS Certificate Manager (gratuito)

S3 Buckets:
  - marabet-backups (backups)
  - marabet-static (assets)
  - marabet-logs (logs)
```

---

## 🚀 DEPLOY COMPLETO

### **Script Automático de Deploy:**

```bash
# Criar script de deploy
cat > deploy_aws.sh << 'EOF'
#!/bin/bash

set -e

echo "🚀 MaraBet AI - Deploy na AWS"
echo "=============================="
echo ""

# Variáveis
REGION="eu-west-1"
PROJECT_NAME="marabet"
KEY_NAME="${PROJECT_NAME}-key"
INSTANCE_TYPE="t3.large"
DB_INSTANCE_TYPE="db.t3.large"
CACHE_INSTANCE_TYPE="cache.t3.medium"

# 1. Criar VPC
echo "1. Criando VPC..."
VPC_ID=$(aws ec2 create-vpc \
  --region $REGION \
  --cidr-block 10.0.0.0/16 \
  --query 'Vpc.VpcId' \
  --output text)
echo "   VPC criada: $VPC_ID"

# Nomear VPC
aws ec2 create-tags \
  --region $REGION \
  --resources $VPC_ID \
  --tags Key=Name,Value=${PROJECT_NAME}-vpc

# 2. Criar Subnets
echo "2. Criando Subnets..."

# Subnet Pública 1 (AZ A)
SUBNET_PUBLIC_1=$(aws ec2 create-subnet \
  --region $REGION \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ${REGION}a \
  --query 'Subnet.SubnetId' \
  --output text)
echo "   Subnet pública 1: $SUBNET_PUBLIC_1"

aws ec2 create-tags \
  --region $REGION \
  --resources $SUBNET_PUBLIC_1 \
  --tags Key=Name,Value=${PROJECT_NAME}-subnet-public-1

# Subnet Pública 2 (AZ B)
SUBNET_PUBLIC_2=$(aws ec2 create-subnet \
  --region $REGION \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone ${REGION}b \
  --query 'Subnet.SubnetId' \
  --output text)
echo "   Subnet pública 2: $SUBNET_PUBLIC_2"

aws ec2 create-tags \
  --region $REGION \
  --resources $SUBNET_PUBLIC_2 \
  --tags Key=Name,Value=${PROJECT_NAME}-subnet-public-2

# Subnet Privada 1 (Database AZ A)
SUBNET_PRIVATE_1=$(aws ec2 create-subnet \
  --region $REGION \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.11.0/24 \
  --availability-zone ${REGION}a \
  --query 'Subnet.SubnetId' \
  --output text)
echo "   Subnet privada 1: $SUBNET_PRIVATE_1"

# Subnet Privada 2 (Database AZ B)
SUBNET_PRIVATE_2=$(aws ec2 create-subnet \
  --region $REGION \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.12.0/24 \
  --availability-zone ${REGION}b \
  --query 'Subnet.SubnetId' \
  --output text)
echo "   Subnet privada 2: $SUBNET_PRIVATE_2"

# 3. Internet Gateway
echo "3. Criando Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway \
  --region $REGION \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)
echo "   IGW criado: $IGW_ID"

aws ec2 attach-internet-gateway \
  --region $REGION \
  --vpc-id $VPC_ID \
  --internet-gateway-id $IGW_ID

# 4. Route Table
echo "4. Configurando Route Table..."
ROUTE_TABLE_ID=$(aws ec2 create-route-table \
  --region $REGION \
  --vpc-id $VPC_ID \
  --query 'RouteTable.RouteTableId' \
  --output text)

aws ec2 create-route \
  --region $REGION \
  --route-table-id $ROUTE_TABLE_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID

aws ec2 associate-route-table \
  --region $REGION \
  --subnet-id $SUBNET_PUBLIC_1 \
  --route-table-id $ROUTE_TABLE_ID

aws ec2 associate-route-table \
  --region $REGION \
  --subnet-id $SUBNET_PUBLIC_2 \
  --route-table-id $ROUTE_TABLE_ID

# 5. Security Groups
echo "5. Criando Security Groups..."

# Security Group para Web
SG_WEB=$(aws ec2 create-security-group \
  --region $REGION \
  --group-name ${PROJECT_NAME}-web-sg \
  --description "MaraBet Web Security Group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)
echo "   Web SG: $SG_WEB"

# Regras Web (HTTP/HTTPS/SSH)
aws ec2 authorize-security-group-ingress \
  --region $REGION \
  --group-id $SG_WEB \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --region $REGION \
  --group-id $SG_WEB \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --region $REGION \
  --group-id $SG_WEB \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

# Security Group para Database
SG_DB=$(aws ec2 create-security-group \
  --region $REGION \
  --group-name ${PROJECT_NAME}-db-sg \
  --description "MaraBet Database Security Group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)
echo "   Database SG: $SG_DB"

# Permitir PostgreSQL apenas do Web SG
aws ec2 authorize-security-group-ingress \
  --region $REGION \
  --group-id $SG_DB \
  --protocol tcp --port 5432 \
  --source-group $SG_WEB

# Security Group para Redis
SG_REDIS=$(aws ec2 create-security-group \
  --region $REGION \
  --group-name ${PROJECT_NAME}-redis-sg \
  --description "MaraBet Redis Security Group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)
echo "   Redis SG: $SG_REDIS"

# Permitir Redis apenas do Web SG
aws ec2 authorize-security-group-ingress \
  --region $REGION \
  --group-id $SG_REDIS \
  --protocol tcp --port 6379 \
  --source-group $SG_WEB

# 6. Criar Key Pair
echo "6. Criando Key Pair..."
aws ec2 create-key-pair \
  --region $REGION \
  --key-name $KEY_NAME \
  --query 'KeyMaterial' \
  --output text > ${KEY_NAME}.pem

chmod 400 ${KEY_NAME}.pem
echo "   Key salva: ${KEY_NAME}.pem"

# 7. RDS PostgreSQL
echo "7. Criando RDS PostgreSQL..."

# Criar DB Subnet Group
aws rds create-db-subnet-group \
  --region $REGION \
  --db-subnet-group-name ${PROJECT_NAME}-db-subnet-group \
  --db-subnet-group-description "MaraBet Database Subnet Group" \
  --subnet-ids $SUBNET_PRIVATE_1 $SUBNET_PRIVATE_2

# Criar RDS Instance
aws rds create-db-instance \
  --region $REGION \
  --db-instance-identifier ${PROJECT_NAME}-db \
  --db-instance-class $DB_INSTANCE_TYPE \
  --engine postgres \
  --engine-version 15.4 \
  --master-username marabetadmin \
  --master-user-password "MaraBet2025#Secure!" \
  --allocated-storage 100 \
  --storage-type gp3 \
  --vpc-security-group-ids $SG_DB \
  --db-subnet-group-name ${PROJECT_NAME}-db-subnet-group \
  --backup-retention-period 7 \
  --multi-az \
  --no-publicly-accessible \
  --storage-encrypted

echo "   RDS PostgreSQL criando (pode demorar 10-15min)..."

# 8. ElastiCache Redis
echo "8. Criando ElastiCache Redis..."

# Criar Cache Subnet Group
aws elasticache create-cache-subnet-group \
  --region $REGION \
  --cache-subnet-group-name ${PROJECT_NAME}-redis-subnet-group \
  --cache-subnet-group-description "MaraBet Redis Subnet Group" \
  --subnet-ids $SUBNET_PRIVATE_1 $SUBNET_PRIVATE_2

# Criar Redis Cluster
aws elasticache create-replication-group \
  --region $REGION \
  --replication-group-id ${PROJECT_NAME}-redis \
  --replication-group-description "MaraBet Redis Cluster" \
  --engine redis \
  --engine-version 7.0 \
  --cache-node-type $CACHE_INSTANCE_TYPE \
  --num-cache-clusters 2 \
  --automatic-failover-enabled \
  --cache-subnet-group-name ${PROJECT_NAME}-redis-subnet-group \
  --security-group-ids $SG_REDIS \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled

echo "   Redis criando (pode demorar 10-15min)..."

# 9. S3 Buckets
echo "9. Criando S3 Buckets..."

# Bucket de Backups
aws s3api create-bucket \
  --region $REGION \
  --bucket ${PROJECT_NAME}-backups \
  --create-bucket-configuration LocationConstraint=$REGION

# Bucket de Assets
aws s3api create-bucket \
  --region $REGION \
  --bucket ${PROJECT_NAME}-static \
  --create-bucket-configuration LocationConstraint=$REGION

# Bucket de Logs
aws s3api create-bucket \
  --region $REGION \
  --bucket ${PROJECT_NAME}-logs \
  --create-bucket-configuration LocationConstraint=$REGION

echo "   Buckets S3 criados"

# 10. EC2 Instances
echo "10. Criando EC2 Instances..."

# Buscar AMI Ubuntu 22.04 mais recente
AMI_ID=$(aws ec2 describe-images \
  --region $REGION \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text)
echo "   AMI Ubuntu 22.04: $AMI_ID"

# User Data Script
USER_DATA=$(cat << 'USERDATA'
#!/bin/bash
apt-get update
apt-get install -y docker.io docker-compose git

# Instalar AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Clone do repositório (substituir)
# git clone https://github.com/seu-repo/marabet.git /opt/marabet

echo "MaraBet server ready!" > /home/ubuntu/setup-complete.txt
USERDATA
)

# Criar EC2 Instance 1
INSTANCE_1=$(aws ec2 run-instances \
  --region $REGION \
  --image-id $AMI_ID \
  --instance-type $INSTANCE_TYPE \
  --key-name $KEY_NAME \
  --subnet-id $SUBNET_PUBLIC_1 \
  --security-group-ids $SG_WEB \
  --user-data "$USER_DATA" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${PROJECT_NAME}-app-1}]" \
  --query 'Instances[0].InstanceId' \
  --output text)
echo "   EC2 Instance 1: $INSTANCE_1"

# Criar EC2 Instance 2
INSTANCE_2=$(aws ec2 run-instances \
  --region $REGION \
  --image-id $AMI_ID \
  --instance-type $INSTANCE_TYPE \
  --key-name $KEY_NAME \
  --subnet-id $SUBNET_PUBLIC_2 \
  --security-group-ids $SG_WEB \
  --user-data "$USER_DATA" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${PROJECT_NAME}-app-2}]" \
  --query 'Instances[0].InstanceId' \
  --output text)
echo "   EC2 Instance 2: $INSTANCE_2"

# 11. Application Load Balancer
echo "11. Criando Application Load Balancer..."

# Criar ALB
ALB_ARN=$(aws elbv2 create-load-balancer \
  --region $REGION \
  --name ${PROJECT_NAME}-alb \
  --subnets $SUBNET_PUBLIC_1 $SUBNET_PUBLIC_2 \
  --security-groups $SG_WEB \
  --scheme internet-facing \
  --type application \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)
echo "   ALB criado: $ALB_ARN"

# Criar Target Group
TG_ARN=$(aws elbv2 create-target-group \
  --region $REGION \
  --name ${PROJECT_NAME}-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --health-check-path /health \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)
echo "   Target Group: $TG_ARN"

# Registrar instâncias no Target Group
aws elbv2 register-targets \
  --region $REGION \
  --target-group-arn $TG_ARN \
  --targets Id=$INSTANCE_1 Id=$INSTANCE_2

# Criar Listener
aws elbv2 create-listener \
  --region $REGION \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN

# Obter DNS do ALB
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --region $REGION \
  --load-balancer-arns $ALB_ARN \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

echo ""
echo "=============================="
echo "✅ DEPLOY CONCLUÍDO!"
echo "=============================="
echo ""
echo "Recursos criados:"
echo "  VPC: $VPC_ID"
echo "  EC2 Instance 1: $INSTANCE_1"
echo "  EC2 Instance 2: $INSTANCE_2"
echo "  RDS PostgreSQL: ${PROJECT_NAME}-db (aguardando criação)"
echo "  ElastiCache Redis: ${PROJECT_NAME}-redis (aguardando criação)"
echo "  Load Balancer: $ALB_DNS"
echo ""
echo "Key Pair: ${KEY_NAME}.pem"
echo ""
echo "Próximos passos:"
echo "  1. Aguardar RDS e Redis ficarem disponíveis (~15min)"
echo "  2. Configurar DNS para apontar para: $ALB_DNS"
echo "  3. Conectar via SSH: ssh -i ${KEY_NAME}.pem ubuntu@<IP_INSTANCIA>"
echo "  4. Configurar aplicação nas instâncias"
echo ""
EOF

chmod +x deploy_aws.sh
```

### **Executar Deploy:**

```bash
# Executar script
./deploy_aws.sh

# Acompanhar logs
tail -f deploy.log
```

---

## 🌐 DOMÍNIO E DNS

### **Configurar Route 53:**

```bash
# 1. Criar Hosted Zone
aws route53 create-hosted-zone \
  --name marabet.ao \
  --caller-reference $(date +%s)

# 2. Obter Name Servers
aws route53 list-hosted-zones-by-name \
  --dns-name marabet.ao

# 3. Configurar registro no registrador do domínio .ao
# Aponte os name servers NS para os fornecidos pela AWS

# 4. Criar registro A para ALB
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "marabet.ao",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z32O12XQLNTSW2",
          "DNSName": "marabet-alb-123456789.eu-west-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

### **Configurar SSL/TLS:**

```bash
# Solicitar certificado SSL gratuito
aws acm request-certificate \
  --domain-name marabet.ao \
  --subject-alternative-names www.marabet.ao api.marabet.ao \
  --validation-method DNS

# Adicionar registros de validação no Route 53
# (Automaticamente validado em ~5 minutos)

# Adicionar certificado ao ALB
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

---

## 📊 MONITORAMENTO

### **CloudWatch Dashboard:**

```bash
# Criar dashboard personalizado
aws cloudwatch put-dashboard \
  --dashboard-name MaraBet-Dashboard \
  --dashboard-body file://dashboard.json
```

### **Alarmes:**

```bash
# Alarme para CPU alta
aws cloudwatch put-metric-alarm \
  --alarm-name marabet-high-cpu \
  --alarm-description "CPU acima de 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# Alarme para Database
aws cloudwatch put-metric-alarm \
  --alarm-name marabet-db-connections \
  --metric-name DatabaseConnections \
  --namespace AWS/RDS \
  --statistic Average \
  --period 60 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold
```

---

## 💰 CUSTOS ESTIMADOS

### **Produção (Mensal):**

| Serviço | Especificação | Custo/mês |
|---------|---------------|-----------|
| **EC2** | 2x t3.large | $135 |
| **RDS PostgreSQL** | db.t3.large Multi-AZ | $260 |
| **ElastiCache Redis** | cache.t3.medium | $85 |
| **ALB** | Load Balancer | $25 |
| **S3** | 100GB armazenamento | $3 |
| **Route 53** | Hosted Zone | $0.50 |
| **CloudWatch** | Monitoramento | $10 |
| **Data Transfer** | ~500GB/mês | $45 |
| **Backups** | RDS Snapshots | $10 |
| **Total** | | **~$573/mês** |

### **Com Reserved Instances (1 ano - 40% desconto):**

| Serviço | Custo/mês |
|---------|-----------|
| **EC2** | $81 |
| **RDS** | $156 |
| **Outros** | $141 |
| **Total** | **~$378/mês** |

### **Free Tier (Primeiros 12 meses):**

- EC2: 750 horas/mês t2.micro (grátis)
- RDS: 750 horas/mês db.t2.micro (grátis)
- S3: 5GB (grátis)
- **Economia**: ~$150/mês no primeiro ano

---

## 🔧 CONFIGURAÇÃO DA APLICAÇÃO

### **Conectar às Instâncias:**

```bash
# Obter IP público
aws ec2 describe-instances \
  --instance-ids i-1234567890abcdef0 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text

# Conectar via SSH
ssh -i marabet-key.pem ubuntu@<IP_PUBLICO>
```

### **Instalar Aplicação:**

```bash
# Na instância EC2
cd /opt
git clone https://github.com/seu-repo/marabet.git
cd marabet

# Configurar variáveis
cp .env.example .env
nano .env

# Editar:
DATABASE_URL=postgresql://marabetadmin:MaraBet2025#Secure!@marabet-db.xxxx.eu-west-1.rds.amazonaws.com:5432/marabet
REDIS_URL=redis://marabet-redis.xxxx.cache.amazonaws.com:6379
S3_BUCKET=marabet-backups
AWS_REGION=eu-west-1

# Iniciar com Docker
docker-compose up -d
```

---

## 🎯 CHECKLIST FINAL

- [ ] AWS CLI instalado e configurado
- [ ] VPC e Subnets criadas
- [ ] Security Groups configurados
- [ ] RDS PostgreSQL Multi-AZ operacional
- [ ] ElastiCache Redis Cluster operacional
- [ ] EC2 Instances rodando
- [ ] Application Load Balancer configurado
- [ ] S3 Buckets criados
- [ ] Route 53 configurado
- [ ] Certificado SSL ativo
- [ ] Aplicação deployada
- [ ] Monitoramento CloudWatch ativo
- [ ] Alarmes configurados
- [ ] Backups automáticos ativos
- [ ] Testes de carga realizados
- [ ] Documentação atualizada

---

## 📞 SUPORTE

Para suporte AWS:
- 📧 **AWS Support**: Via Console
- 📚 **Documentação**: https://docs.aws.amazon.com
- 💬 **Forum**: https://forums.aws.amazon.com

Para suporte MaraBet:
- 📧 **Suporte**: suporte@marabet.ao
- 📧 **Comercial**: comercial@marabet.ao
- 📞 **WhatsApp**: +224 932027393

---

**© 2025 MaraBet AI - Hospedado na AWS**  
**🇦🇴 Angola | 🌍 Global com AWS**  
**✅ Deploy Profissional | ✅ Escalável | ✅ Seguro**

