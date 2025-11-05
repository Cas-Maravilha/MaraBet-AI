#!/bin/bash

################################################################################
# MARABET AI - CRIAR RDS POSTGRESQL MULTI-AZ
# Script automático completo
################################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_header() {
    echo ""
    echo "========================================================================"
    echo "$1"
    echo "========================================================================"
    echo ""
}

print_header "🗄️ MARABET AI - CRIAR RDS POSTGRESQL"

REGION="eu-west-1"
print_info "Região: $REGION"
echo ""

################################################################################
# 1. CRIAR VPC
################################################################################

print_header "1. CRIANDO VPC"

print_info "Criando VPC 10.0.0.0/16..."
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=marabet-vpc}]' \
  --region $REGION \
  --query 'Vpc.VpcId' \
  --output text)

print_success "VPC criada: $VPC_ID"

print_info "Habilitando DNS..."
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support --region $REGION
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames --region $REGION
print_success "DNS habilitado"

################################################################################
# 2. CRIAR SUBNETS
################################################################################

print_header "2. CRIANDO SUBNETS"

# Subnet Pública
print_info "Criando Subnet Pública (10.0.1.0/24 - AZ A)..."
SUBNET_PUBLIC_A=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ${REGION}a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=marabet-public-a}]' \
  --region $REGION \
  --query 'Subnet.SubnetId' \
  --output text)

aws ec2 modify-subnet-attribute \
  --subnet-id $SUBNET_PUBLIC_A \
  --map-public-ip-on-launch \
  --region $REGION

print_success "Subnet Pública: $SUBNET_PUBLIC_A"

# Subnet Privada A
print_info "Criando Subnet Privada A (10.0.2.0/24 - AZ A)..."
SUBNET_PRIVATE_A=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone ${REGION}a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=marabet-private-a}]' \
  --region $REGION \
  --query 'Subnet.SubnetId' \
  --output text)

print_success "Subnet Privada A: $SUBNET_PRIVATE_A"

# Subnet Privada B
print_info "Criando Subnet Privada B (10.0.3.0/24 - AZ B)..."
SUBNET_PRIVATE_B=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.3.0/24 \
  --availability-zone ${REGION}b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=marabet-private-b}]' \
  --region $REGION \
  --query 'Subnet.SubnetId' \
  --output text)

print_success "Subnet Privada B: $SUBNET_PRIVATE_B"

################################################################################
# 3. INTERNET GATEWAY
################################################################################

print_header "3. CONFIGURANDO INTERNET GATEWAY"

print_info "Criando Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=marabet-igw}]' \
  --region $REGION \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)

print_success "Internet Gateway: $IGW_ID"

print_info "Anexando à VPC..."
aws ec2 attach-internet-gateway \
  --internet-gateway-id $IGW_ID \
  --vpc-id $VPC_ID \
  --region $REGION

print_success "Internet Gateway anexado"

################################################################################
# 4. ROUTE TABLE
################################################################################

print_header "4. CONFIGURANDO ROUTE TABLE"

print_info "Criando Route Table pública..."
RTB_PUBLIC=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=marabet-public-rt}]' \
  --region $REGION \
  --query 'RouteTable.RouteTableId' \
  --output text)

print_success "Route Table: $RTB_PUBLIC"

print_info "Adicionando rota para internet..."
aws ec2 create-route \
  --route-table-id $RTB_PUBLIC \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID \
  --region $REGION

print_success "Rota adicionada"

print_info "Associando subnet pública..."
aws ec2 associate-route-table \
  --route-table-id $RTB_PUBLIC \
  --subnet-id $SUBNET_PUBLIC_A \
  --region $REGION

print_success "Subnet associada"

################################################################################
# 5. SECURITY GROUPS
################################################################################

print_header "5. CRIANDO SECURITY GROUPS"

# Security Group Web
print_info "Criando Security Group Web..."
SG_WEB=$(aws ec2 create-security-group \
  --group-name marabet-web-sg \
  --description "MaraBet Web/Application Security Group" \
  --vpc-id $VPC_ID \
  --region $REGION \
  --query 'GroupId' \
  --output text)

print_success "Web SG: $SG_WEB"

print_info "Adicionando regras Web (80, 443, 22)..."
aws ec2 authorize-security-group-ingress --group-id $SG_WEB --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $REGION 2>/dev/null || true
aws ec2 authorize-security-group-ingress --group-id $SG_WEB --protocol tcp --port 443 --cidr 0.0.0.0/0 --region $REGION 2>/dev/null || true
aws ec2 authorize-security-group-ingress --group-id $SG_WEB --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $REGION 2>/dev/null || true

print_success "Regras Web adicionadas"

# Security Group RDS
print_info "Criando Security Group RDS..."
SG_RDS=$(aws ec2 create-security-group \
  --group-name marabet-rds-sg \
  --description "MaraBet RDS PostgreSQL Security Group" \
  --vpc-id $VPC_ID \
  --region $REGION \
  --query 'GroupId' \
  --output text)

print_success "RDS SG: $SG_RDS"

print_info "Permitindo PostgreSQL (5432) apenas do Web SG..."
aws ec2 authorize-security-group-ingress \
  --group-id $SG_RDS \
  --protocol tcp \
  --port 5432 \
  --source-group $SG_WEB \
  --region $REGION 2>/dev/null || true

print_success "Regras RDS adicionadas"

################################################################################
# 6. CRIAR RDS
################################################################################

print_header "6. CRIANDO RDS POSTGRESQL MULTI-AZ"

print_info "Criando DB Subnet Group..."
aws rds create-db-subnet-group \
  --db-subnet-group-name marabet-db-subnet-group \
  --db-subnet-group-description "MaraBet RDS Subnet Group" \
  --subnet-ids $SUBNET_PRIVATE_A $SUBNET_PRIVATE_B \
  --tags "Key=Name,Value=marabet-db-subnet-group" \
  --region $REGION 2>/dev/null || print_warning "DB Subnet Group já existe"

print_success "DB Subnet Group criado"

print_info "Criando RDS PostgreSQL 15.4..."
print_warning "Isso pode levar 10-15 minutos"
echo ""

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
  --region $REGION 2>/dev/null || print_warning "RDS já existe"

print_success "RDS PostgreSQL iniciando..."

print_info "Aguardando RDS ficar disponível..."
print_warning "Isso levará aproximadamente 10-15 minutos"
echo ""

aws rds wait db-instance-available \
  --db-instance-identifier marabet-db \
  --region $REGION

print_success "RDS disponível!"

# Obter endpoint
RDS_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier marabet-db \
  --region $REGION \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ RDS POSTGRESQL CRIADO COM SUCESSO!"

echo ""
echo "Recursos Criados:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  VPC:"
echo "    ID:                $VPC_ID"
echo "    CIDR:              10.0.0.0/16"
echo ""
echo "  Subnets:"
echo "    Pública (AZ A):    $SUBNET_PUBLIC_A (10.0.1.0/24)"
echo "    Privada A (AZ A):  $SUBNET_PRIVATE_A (10.0.2.0/24)"
echo "    Privada B (AZ B):  $SUBNET_PRIVATE_B (10.0.3.0/24)"
echo ""
echo "  Networking:"
echo "    Internet Gateway:  $IGW_ID"
echo "    Route Table:       $RTB_PUBLIC"
echo ""
echo "  Security Groups:"
echo "    Web/App:           $SG_WEB"
echo "    RDS:               $SG_RDS"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🗄️  RDS PostgreSQL:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "    Instance ID:       marabet-db"
echo "    Engine:            PostgreSQL 15.4"
echo "    Class:             db.t3.large (2 vCPUs, 8GB RAM)"
echo "    Storage:           100GB gp3 (encrypted)"
echo "    Multi-AZ:          Yes ✓"
echo "    Endpoint:          $RDS_ENDPOINT"
echo "    Port:              5432"
echo ""
echo "    Master Username:   marabetadmin"
echo "    Master Password:   MaraBet2025#Secure!"
echo "    Initial Database:  postgres"
echo ""
echo "    Backup:            7 dias (02:00-03:00 UTC)"
echo "    Maintenance:       Domingos 03:00-04:00 UTC"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📝 Connection String:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "    postgresql://marabetadmin:MaraBet2025#Secure!@$RDS_ENDPOINT:5432/marabet"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🔧 Para usar no .env:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "    DATABASE_URL=postgresql://marabetadmin:MaraBet2025#Secure!@$RDS_ENDPOINT:5432/marabet"
echo "    DB_HOST=$RDS_ENDPOINT"
echo "    DB_PORT=5432"
echo "    DB_NAME=marabet"
echo "    DB_USER=marabetadmin"
echo "    DB_PASSWORD=MaraBet2025#Secure!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📊 Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "    1. Criar EC2 Instance na subnet pública"
echo "    2. Conectar EC2 ao RDS usando endpoint acima"
echo "    3. Criar database 'marabet':"
echo "       psql -h $RDS_ENDPOINT -U marabetadmin -d postgres"
echo "       CREATE DATABASE marabet;"
echo ""
echo "    4. Deploy da aplicação"
echo "    5. Executar migrações"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Salvar informações em arquivo
cat > marabet-rds-info.txt << EOF
MaraBet AI - RDS PostgreSQL
============================

VPC ID:              $VPC_ID
Subnet Pública:      $SUBNET_PUBLIC_A
Subnet Privada A:    $SUBNET_PRIVATE_A
Subnet Privada B:    $SUBNET_PRIVATE_B
Web Security Group:  $SG_WEB
RDS Security Group:  $SG_RDS

RDS Endpoint:        $RDS_ENDPOINT
RDS Port:            5432
RDS Username:        marabetadmin
RDS Password:        MaraBet2025#Secure!

Connection String:
postgresql://marabetadmin:MaraBet2025#Secure!@$RDS_ENDPOINT:5432/marabet

.env variables:
DATABASE_URL=postgresql://marabetadmin:MaraBet2025#Secure!@$RDS_ENDPOINT:5432/marabet
DB_HOST=$RDS_ENDPOINT
DB_PORT=5432
DB_NAME=marabet
DB_USER=marabetadmin
DB_PASSWORD=MaraBet2025#Secure!
EOF

print_success "Informações salvas em: marabet-rds-info.txt"

echo ""
print_header "✅ CONCLUÍDO!"
echo ""

