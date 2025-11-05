# 🖥️ CRIAR EC2 INSTANCE - GUIA COMPLETO

**Sistema**: MaraBet AI  
**Região**: eu-west-1 (Irlanda)  
**Instance Type**: t3.large

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Criar Security Group](#1-criar-security-group-ec2)
3. [Criar Key Pair](#2-criar-key-pair)
4. [Lançar EC2 Instance](#3-lançar-ec2-instance)
5. [Configurar na EC2](#4-configurar-na-ec2)
6. [Deploy Aplicação](#5-deploy-aplicação)
7. [Testar Conexões](#6-testar-conexões)

---

## 🎯 VISÃO GERAL

### **EC2 Instance para MaraBet:**

```yaml
Finalidade:           Servidor de Aplicação
Instance Type:        t3.large (2 vCPUs, 8GB RAM)
OS:                   Ubuntu 22.04 LTS
Storage:              100GB gp3 SSD (3000 IOPS)
Network:              VPC pública (com IP público)

Software a Instalar:
├── Docker + Docker Compose
├── Nginx (proxy reverso)
├── PostgreSQL Client
├── Redis Tools (redis-cli)
├── AWS CLI
├── Git
└── Python 3
```

---

## 1️⃣ CRIAR SECURITY GROUP EC2

### **Criar Security Group:**

```bash
# Obter VPC ID
VPC_ID="vpc-081a8c63b16a94a3a"

# Criar SG
aws ec2 create-security-group \
  --group-name marabet-ec2-sg \
  --description "Security group for MaraBet EC2 Application Server" \
  --vpc-id $VPC_ID \
  --region eu-west-1
```

**Anotar Security Group ID retornado**: `sg-xxxxxxxxxxxxx`

```bash
export SG_EC2=sg-xxxxxxxxxxxxx
```

### **Adicionar Regras de Firewall:**

```bash
# SSH - APENAS seu IP (segurança!)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_EC2 \
  --protocol tcp \
  --port 22 \
  --cidr 102.206.57.108/32 \
  --region eu-west-1

# HTTP (porta 80)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_EC2 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1

# HTTPS (porta 443)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_EC2 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1

# Aplicação (porta 8000 - opcional, para testes)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_EC2 \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0 \
  --region eu-west-1
```

### **Verificar Regras:**

```bash
aws ec2 describe-security-groups \
  --group-ids $SG_EC2 \
  --region eu-west-1 \
  --query 'SecurityGroups[0].IpPermissions[*].[IpProtocol,FromPort,ToPort,IpRanges[0].CidrIp]' \
  --output table
```

---

## 2️⃣ CRIAR KEY PAIR

### **Criar Nova Key:**

```bash
aws ec2 create-key-pair \
  --key-name marabet-key \
  --query 'KeyMaterial' \
  --output text \
  --region eu-west-1 > marabet-key.pem

# Proteger chave
chmod 400 marabet-key.pem
```

⚠️ **IMPORTANTE**: Guarde `marabet-key.pem` em local seguro! Sem ela, não poderá acessar a EC2 via SSH.

---

## 3️⃣ LANÇAR EC2 INSTANCE

### **Obter AMI Ubuntu 22.04:**

```bash
AMI_ID=$(aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text \
  --region eu-west-1)

echo "AMI ID: $AMI_ID"
```

### **Obter Subnet Pública:**

```bash
SUBNET_PUBLIC=$(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --region eu-west-1 \
  --query 'Subnets[0].SubnetId' \
  --output text)

echo "Subnet: $SUBNET_PUBLIC"
```

### **Lançar Instance:**

```bash
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.large \
  --key-name marabet-key \
  --subnet-id $SUBNET_PUBLIC \
  --security-group-ids $SG_EC2 \
  --associate-public-ip-address \
  --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=100,VolumeType=gp3,Iops=3000,DeleteOnTermination=true}' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=marabet-app},{Key=Environment,Value=production}]' \
  --monitoring Enabled=true \
  --region eu-west-1
```

**Anotar Instance ID retornado**: `i-xxxxxxxxxxxxx`

### **Aguardar Instance Iniciar:**

```bash
INSTANCE_ID=i-xxxxxxxxxxxxx

# Aguardar running
aws ec2 wait instance-running \
  --instance-ids $INSTANCE_ID \
  --region eu-west-1

# Aguardar status checks
aws ec2 wait instance-status-ok \
  --instance-ids $INSTANCE_ID \
  --region eu-west-1

echo "✅ EC2 Instance disponível!"
```

### **Obter IP Público:**

```bash
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --region eu-west-1 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "IP Público: $PUBLIC_IP"
```

---

## 4️⃣ CONFIGURAR NA EC2

### **Conectar via SSH:**

```bash
ssh -i marabet-key.pem ubuntu@$PUBLIC_IP
```

### **Instalar Software Essencial:**

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar outras ferramentas
sudo apt install -y \
    git \
    nginx \
    postgresql-client \
    redis-tools \
    python3 \
    python3-pip \
    python3-venv

# Instalar AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verificar instalações
docker --version
docker-compose --version
nginx -v
psql --version
redis-cli --version
aws --version
python3 --version
```

### **Criar Estrutura de Diretórios:**

```bash
sudo mkdir -p /opt/marabet
sudo mkdir -p /var/log/marabet
sudo mkdir -p /opt/marabet/backups

sudo chown -R ubuntu:ubuntu /opt/marabet
sudo chown -R ubuntu:ubuntu /var/log/marabet
```

---

## 5️⃣ DEPLOY APLICAÇÃO

### **Upload do Código:**

#### **Opção 1: Via rsync (do seu PC):**

```bash
# No seu PC Windows (Git Bash ou WSL)
rsync -avz --progress \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude 'venv' \
    -e "ssh -i marabet-key.pem" \
    "D:/Usuario/Maravilha/Desktop/MaraBet AI/" \
    ubuntu@$PUBLIC_IP:/opt/marabet/
```

#### **Opção 2: Via Git:**

```bash
# Na EC2
cd /opt/marabet
git clone https://github.com/seu-repo/marabet-ai.git .
```

#### **Opção 3: Via S3:**

```bash
# No PC, upload para S3
aws s3 sync "D:\Usuario\Maravilha\Desktop\MaraBet AI" s3://marabet-deploy-temp/code/

# Na EC2, download
cd /opt/marabet
aws s3 sync s3://marabet-deploy-temp/code/ .
```

### **Configurar .env na EC2:**

```bash
cd /opt/marabet

# Criar .env
cat > .env << 'EOF'
# MaraBet AI - Production Environment

# RDS PostgreSQL
DATABASE_URL=postgresql://marabet_admin:GuF#Y(!j38Bgw|YyT<r0J5>yxD3n@database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com:5432/marabet_production?sslmode=require
DB_HOST=database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=marabet_production
DB_USER=marabet_admin
DB_PASSWORD=GuF#Y(!j38Bgw|YyT<r0J5>yxD3n

# ElastiCache Redis
REDIS_URL=rediss://marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com:6379
REDIS_HOST=marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_SSL=true

# API-Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Telegram
TELEGRAM_BOT_TOKEN=<SEU_TOKEN>
TELEGRAM_CHAT_ID=5550091597

# AWS
AWS_REGION=eu-west-1

# App
APP_ENV=production
DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)
EOF

chmod 600 .env
```

### **Iniciar Aplicação:**

```bash
# Build e start
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Verificar containers
docker-compose ps
```

---

## 6️⃣ TESTAR CONEXÕES

### **Testar RDS:**

```bash
# Na EC2
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d postgres

# Criar database
CREATE DATABASE marabet_production;
\l
\q
```

### **Testar Redis:**

```bash
redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com \
          -p 6379 \
          --tls \
          --insecure

# Comandos
PING
SET test_marabet "OK"
GET test_marabet
```

### **Testar Aplicação:**

```bash
# Dentro da EC2
curl http://localhost/health

# Do seu PC
curl http://<EC2_PUBLIC_IP>/health
```

---

## 💰 CUSTOS

### **EC2 t3.large:**

| Item | Custo/mês |
|------|-----------|
| **Instância t3.large** | $67.07 |
| **Storage 100GB gp3** | $8.00 |
| **IP Público (Elastic)** | $3.60 |
| **Data Transfer 500GB** | $45.00 |
| **TOTAL** | **~$124/mês** |

### **Com Reserved Instance (1 ano):**
- **$40/mês** (economia 40%)

---

## ✅ CHECKLIST

- [ ] Security Group EC2 criado
- [ ] Regras de firewall configuradas (22, 80, 443)
- [ ] Key Pair criada e salva (.pem)
- [ ] AMI Ubuntu 22.04 selecionada
- [ ] Subnet pública identificada
- [ ] EC2 Instance lançada
- [ ] Instance em status running
- [ ] IP público obtido
- [ ] SSH testado
- [ ] Software instalado (Docker, Nginx, etc.)
- [ ] Código deployado
- [ ] .env configurado
- [ ] RDS acessível da EC2
- [ ] Redis acessível da EC2
- [ ] Aplicação rodando
- [ ] Health check respondendo

---

## 📞 SUPORTE

**MaraBet AI:**
- 📧 suporte@marabet.ao
- 📞 +224 932027393

**AWS:**
- 📚 https://docs.aws.amazon.com/ec2/

---

**🖥️ EC2 Instance Pronta para Criação!**  
**✅ Script Automático Disponível**  
**☁️ MaraBet AI - Powered by AWS EC2**

