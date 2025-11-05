#!/bin/bash

################################################################################
# MARABET AI - DEPLOY COMPLETO NA AWS
# Script automático de deploy com todos os recursos
################################################################################

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para print colorido
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo ""
    echo "========================================================================"
    echo "$1"
    echo "========================================================================"
    echo ""
}

# Configurações
PROJECT_NAME="marabet"
REGION="eu-west-1"
VPC_CIDR="10.0.0.0/16"
PUBLIC_SUBNET_A_CIDR="10.0.1.0/24"
PRIVATE_SUBNET_A_CIDR="10.0.11.0/24"
PRIVATE_SUBNET_B_CIDR="10.0.12.0/24"

EC2_INSTANCE_TYPE="t3.large"
RDS_INSTANCE_TYPE="db.t3.large"
REDIS_INSTANCE_TYPE="cache.t3.medium"

DB_NAME="marabet"
DB_USER="marabetadmin"
DB_PASSWORD="MaraBet2025#Secure!"

KEY_NAME="${PROJECT_NAME}-key"

print_header "🚀 MARABET AI - DEPLOY COMPLETO NA AWS"

print_info "Projeto: $PROJECT_NAME"
print_info "Região: $REGION"
print_info "Ambiente: Produção"
echo ""

# Verificar AWS CLI
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI não instalado!"
    print_info "Instale: https://aws.amazon.com/cli/"
    exit 1
fi

# Verificar configuração AWS
print_info "Verificando credenciais AWS..."
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "Credenciais AWS não configuradas!"
    print_info "Execute: aws configure"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
print_success "AWS Account: $ACCOUNT_ID"

################################################################################
# 1. CRIAR VPC
################################################################################

print_header "1. CRIANDO VPC"

print_info "Criando VPC $VPC_CIDR..."
VPC_ID=$(aws ec2 create-vpc \
    --region $REGION \
    --cidr-block $VPC_CIDR \
    --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=${PROJECT_NAME}-vpc}]" \
    --query 'Vpc.VpcId' \
    --output text)

print_success "VPC criada: $VPC_ID"

# Habilitar DNS
aws ec2 modify-vpc-attribute --region $REGION --vpc-id $VPC_ID --enable-dns-support
aws ec2 modify-vpc-attribute --region $REGION --vpc-id $VPC_ID --enable-dns-hostnames

################################################################################
# 2. CRIAR SUBNETS
################################################################################

print_header "2. CRIANDO SUBNETS"

# Public Subnet (Zona A)
print_info "Criando Public Subnet (AZ A)..."
SUBNET_PUBLIC_A=$(aws ec2 create-subnet \
    --region $REGION \
    --vpc-id $VPC_ID \
    --cidr-block $PUBLIC_SUBNET_A_CIDR \
    --availability-zone ${REGION}a \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT_NAME}-public-a}]" \
    --query 'Subnet.SubnetId' \
    --output text)

aws ec2 modify-subnet-attribute --region $REGION --subnet-id $SUBNET_PUBLIC_A --map-public-ip-on-launch

print_success "Public Subnet A: $SUBNET_PUBLIC_A"

# Private Subnet A (Database)
print_info "Criando Private Subnet (AZ A)..."
SUBNET_PRIVATE_A=$(aws ec2 create-subnet \
    --region $REGION \
    --vpc-id $VPC_ID \
    --cidr-block $PRIVATE_SUBNET_A_CIDR \
    --availability-zone ${REGION}a \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT_NAME}-private-a}]" \
    --query 'Subnet.SubnetId' \
    --output text)

print_success "Private Subnet A: $SUBNET_PRIVATE_A"

# Private Subnet B (Database Multi-AZ)
print_info "Criando Private Subnet (AZ B)..."
SUBNET_PRIVATE_B=$(aws ec2 create-subnet \
    --region $REGION \
    --vpc-id $VPC_ID \
    --cidr-block $PRIVATE_SUBNET_B_CIDR \
    --availability-zone ${REGION}b \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT_NAME}-private-b}]" \
    --query 'Subnet.SubnetId' \
    --output text)

print_success "Private Subnet B: $SUBNET_PRIVATE_B"

################################################################################
# 3. INTERNET GATEWAY
################################################################################

print_header "3. CONFIGURANDO INTERNET GATEWAY"

print_info "Criando Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway \
    --region $REGION \
    --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=${PROJECT_NAME}-igw}]" \
    --query 'InternetGateway.InternetGatewayId' \
    --output text)

aws ec2 attach-internet-gateway --region $REGION --vpc-id $VPC_ID --internet-gateway-id $IGW_ID

print_success "Internet Gateway: $IGW_ID"

################################################################################
# 4. ROUTE TABLES
################################################################################

print_header "4. CONFIGURANDO ROUTE TABLES"

print_info "Criando Route Table pública..."
ROUTE_TABLE_PUBLIC=$(aws ec2 create-route-table \
    --region $REGION \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${PROJECT_NAME}-public-rt}]" \
    --query 'RouteTable.RouteTableId' \
    --output text)

aws ec2 create-route \
    --region $REGION \
    --route-table-id $ROUTE_TABLE_PUBLIC \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID

aws ec2 associate-route-table \
    --region $REGION \
    --subnet-id $SUBNET_PUBLIC_A \
    --route-table-id $ROUTE_TABLE_PUBLIC

print_success "Route Table: $ROUTE_TABLE_PUBLIC"

################################################################################
# 5. SECURITY GROUPS
################################################################################

print_header "5. CRIANDO SECURITY GROUPS"

# Security Group para EC2 (Web/App)
print_info "Criando Security Group Web..."
SG_WEB=$(aws ec2 create-security-group \
    --region $REGION \
    --group-name ${PROJECT_NAME}-web-sg \
    --description "MaraBet Web/Application Security Group" \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=${PROJECT_NAME}-web-sg}]" \
    --query 'GroupId' \
    --output text)

# Regras Web
aws ec2 authorize-security-group-ingress --region $REGION --group-id $SG_WEB --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --region $REGION --group-id $SG_WEB --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --region $REGION --group-id $SG_WEB --protocol tcp --port 22 --cidr 0.0.0.0/0

print_success "Web Security Group: $SG_WEB"

# Security Group para RDS
print_info "Criando Security Group Database..."
SG_DB=$(aws ec2 create-security-group \
    --region $REGION \
    --group-name ${PROJECT_NAME}-db-sg \
    --description "MaraBet Database Security Group" \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=${PROJECT_NAME}-db-sg}]" \
    --query 'GroupId' \
    --output text)

aws ec2 authorize-security-group-ingress \
    --region $REGION \
    --group-id $SG_DB \
    --protocol tcp \
    --port 5432 \
    --source-group $SG_WEB

print_success "Database Security Group: $SG_DB"

# Security Group para Redis
print_info "Criando Security Group Redis..."
SG_REDIS=$(aws ec2 create-security-group \
    --region $REGION \
    --group-name ${PROJECT_NAME}-redis-sg \
    --description "MaraBet Redis Security Group" \
    --vpc-id $VPC_ID \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=${PROJECT_NAME}-redis-sg}]" \
    --query 'GroupId' \
    --output text)

aws ec2 authorize-security-group-ingress \
    --region $REGION \
    --group-id $SG_REDIS \
    --protocol tcp \
    --port 6379 \
    --source-group $SG_WEB

print_success "Redis Security Group: $SG_REDIS"

################################################################################
# 6. KEY PAIR
################################################################################

print_header "6. CRIANDO KEY PAIR"

print_info "Gerando Key Pair $KEY_NAME..."
if [ -f "${KEY_NAME}.pem" ]; then
    print_warning "Key ${KEY_NAME}.pem já existe, pulando..."
else
    aws ec2 create-key-pair \
        --region $REGION \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text > ${KEY_NAME}.pem
    
    chmod 400 ${KEY_NAME}.pem
    print_success "Key salva: ${KEY_NAME}.pem"
fi

################################################################################
# 7. S3 BUCKETS
################################################################################

print_header "7. CRIANDO S3 BUCKETS"

# Bucket de Backups
print_info "Criando bucket de backups..."
aws s3api create-bucket \
    --region $REGION \
    --bucket ${PROJECT_NAME}-backups-$(date +%s) \
    --create-bucket-configuration LocationConstraint=$REGION \
    2>/dev/null || print_warning "Bucket backups pode já existir"

# Bucket de Static
print_info "Criando bucket de assets..."
aws s3api create-bucket \
    --region $REGION \
    --bucket ${PROJECT_NAME}-static-$(date +%s) \
    --create-bucket-configuration LocationConstraint=$REGION \
    2>/dev/null || print_warning "Bucket static pode já existir"

# Bucket de Logs
print_info "Criando bucket de logs..."
aws s3api create-bucket \
    --region $REGION \
    --bucket ${PROJECT_NAME}-logs-$(date +%s) \
    --create-bucket-configuration LocationConstraint=$REGION \
    2>/dev/null || print_warning "Bucket logs pode já existir"

print_success "S3 Buckets criados"

################################################################################
# 8. RDS POSTGRESQL
################################################################################

print_header "8. CRIANDO RDS POSTGRESQL (Multi-AZ)"

print_info "Criando DB Subnet Group..."
aws rds create-db-subnet-group \
    --region $REGION \
    --db-subnet-group-name ${PROJECT_NAME}-db-subnet-group \
    --db-subnet-group-description "MaraBet Database Subnet Group" \
    --subnet-ids $SUBNET_PRIVATE_A $SUBNET_PRIVATE_B \
    --tags "Key=Name,Value=${PROJECT_NAME}-db-subnet-group" \
    2>/dev/null || print_warning "DB Subnet Group pode já existir"

print_info "Criando RDS PostgreSQL Multi-AZ..."
print_warning "Isso pode levar 10-15 minutos..."

aws rds create-db-instance \
    --region $REGION \
    --db-instance-identifier ${PROJECT_NAME}-db \
    --db-instance-class $RDS_INSTANCE_TYPE \
    --engine postgres \
    --engine-version 15.4 \
    --master-username $DB_USER \
    --master-user-password "$DB_PASSWORD" \
    --allocated-storage 100 \
    --storage-type gp3 \
    --vpc-security-group-ids $SG_DB \
    --db-subnet-group-name ${PROJECT_NAME}-db-subnet-group \
    --backup-retention-period 7 \
    --preferred-backup-window "02:00-03:00" \
    --preferred-maintenance-window "sun:03:00-sun:04:00" \
    --multi-az \
    --no-publicly-accessible \
    --storage-encrypted \
    --tags "Key=Name,Value=${PROJECT_NAME}-db" \
    2>/dev/null || print_warning "RDS pode já existir"

print_success "RDS PostgreSQL criando em background..."

################################################################################
# 9. ELASTICACHE REDIS
################################################################################

print_header "9. CRIANDO ELASTICACHE REDIS"

print_info "Criando Cache Subnet Group..."
aws elasticache create-cache-subnet-group \
    --region $REGION \
    --cache-subnet-group-name ${PROJECT_NAME}-redis-subnet-group \
    --cache-subnet-group-description "MaraBet Redis Subnet Group" \
    --subnet-ids $SUBNET_PRIVATE_A $SUBNET_PRIVATE_B \
    2>/dev/null || print_warning "Cache Subnet Group pode já existir"

print_info "Criando ElastiCache Redis Cluster..."
print_warning "Isso pode levar 10-15 minutos..."

aws elasticache create-replication-group \
    --region $REGION \
    --replication-group-id ${PROJECT_NAME}-redis \
    --replication-group-description "MaraBet Redis Cluster" \
    --engine redis \
    --engine-version 7.0 \
    --cache-node-type $REDIS_INSTANCE_TYPE \
    --num-cache-clusters 2 \
    --automatic-failover-enabled \
    --cache-subnet-group-name ${PROJECT_NAME}-redis-subnet-group \
    --security-group-ids $SG_REDIS \
    --at-rest-encryption-enabled \
    --transit-encryption-enabled \
    --tags "Key=Name,Value=${PROJECT_NAME}-redis" \
    2>/dev/null || print_warning "Redis pode já existir"

print_success "ElastiCache Redis criando em background..."

################################################################################
# 10. EC2 INSTANCE
################################################################################

print_header "10. LANÇANDO EC2 INSTANCE"

# Buscar AMI Ubuntu 22.04 mais recente
print_info "Buscando AMI Ubuntu 22.04..."
AMI_ID=$(aws ec2 describe-images \
    --region $REGION \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text)

print_success "AMI Ubuntu: $AMI_ID"

# User Data
USER_DATA=$(cat << 'USERDATA'
#!/bin/bash
apt-get update
apt-get install -y docker.io docker-compose git nginx postgresql-client redis-tools

systemctl enable docker
systemctl start docker

mkdir -p /opt/marabet
chown ubuntu:ubuntu /opt/marabet

echo "MaraBet server initialized" > /home/ubuntu/ready.txt
USERDATA
)

print_info "Lançando EC2 Instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --region $REGION \
    --image-id $AMI_ID \
    --instance-type $EC2_INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --subnet-id $SUBNET_PUBLIC_A \
    --security-group-ids $SG_WEB \
    --user-data "$USER_DATA" \
    --block-device-mappings "DeviceName=/dev/sda1,Ebs={VolumeSize=100,VolumeType=gp3}" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${PROJECT_NAME}-app}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

print_success "EC2 Instance: $INSTANCE_ID"

# Aguardar instância ficar running
print_info "Aguardando EC2 ficar pronta..."
aws ec2 wait instance-running --region $REGION --instance-ids $INSTANCE_ID

# Obter IP público
INSTANCE_IP=$(aws ec2 describe-instances \
    --region $REGION \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

print_success "EC2 IP Público: $INSTANCE_IP"

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ DEPLOY CONCLUÍDO!"

echo "Recursos criados:"
echo ""
echo "  VPC:                 $VPC_ID"
echo "  Public Subnet:       $SUBNET_PUBLIC_A"
echo "  Private Subnet A:    $SUBNET_PRIVATE_A"
echo "  Private Subnet B:    $SUBNET_PRIVATE_B"
echo "  Internet Gateway:    $IGW_ID"
echo ""
echo "  Security Groups:"
echo "    - Web:             $SG_WEB"
echo "    - Database:        $SG_DB"
echo "    - Redis:           $SG_REDIS"
echo ""
echo "  EC2 Instance:        $INSTANCE_ID"
echo "  EC2 IP Público:      $INSTANCE_IP"
echo "  Key Pair:            ${KEY_NAME}.pem"
echo ""
echo "  RDS PostgreSQL:      ${PROJECT_NAME}-db (criando...)"
echo "  ElastiCache Redis:   ${PROJECT_NAME}-redis (criando...)"
echo ""
echo "  S3 Buckets:          ${PROJECT_NAME}-backups-*"
echo "                       ${PROJECT_NAME}-static-*"
echo "                       ${PROJECT_NAME}-logs-*"
echo ""
echo "========================================================================"
echo ""
print_info "Próximos passos:"
echo ""
echo "  1. Aguardar RDS e Redis ficarem disponíveis (~15 minutos):"
echo "     aws rds describe-db-instances --db-instance-identifier ${PROJECT_NAME}-db"
echo ""
echo "  2. Conectar na EC2:"
echo "     ssh -i ${KEY_NAME}.pem ubuntu@$INSTANCE_IP"
echo ""
echo "  3. Obter endpoints:"
echo "     RDS:   aws rds describe-db-instances --db-instance-identifier ${PROJECT_NAME}-db --query 'DBInstances[0].Endpoint.Address'"
echo "     Redis: aws elasticache describe-replication-groups --replication-group-id ${PROJECT_NAME}-redis --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Address'"
echo ""
echo "  4. Configurar .env na EC2 com os endpoints"
echo ""
echo "  5. Deploy da aplicação (veja: AWS_MIGRACAO_DADOS_COMPLETA.md)"
echo ""
print_success "Deploy de infraestrutura completo!"
echo ""

