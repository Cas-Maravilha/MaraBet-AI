#!/bin/bash

################################################################################
# MARABET AI - CRIAR SECURITY GROUPS
# RDS PostgreSQL + ElastiCache Redis
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

print_header "🔒 MARABET AI - CRIAR SECURITY GROUPS"

REGION="eu-west-1"

# Verificar se VPC ID foi fornecido
if [ -z "$1" ]; then
    print_error "VPC ID não fornecido!"
    echo ""
    echo "Uso: $0 <VPC_ID>"
    echo ""
    echo "Exemplo: $0 vpc-0a1b2c3d4e5f67890"
    echo ""
    echo "Para obter VPC ID:"
    echo "  aws ec2 describe-vpcs --region $REGION --query 'Vpcs[?Tags[?Key==\`Name\`&&Value==\`marabet-vpc\`]].VpcId' --output text"
    echo ""
    exit 1
fi

VPC_ID=$1
print_info "VPC ID: $VPC_ID"
echo ""

################################################################################
# 1. SECURITY GROUP EC2/WEB
################################################################################

print_header "1. CRIANDO SECURITY GROUP EC2/WEB"

print_info "Criando marabet-web-sg..."
SG_WEB=$(aws ec2 create-security-group \
    --group-name marabet-web-sg \
    --description "Security group for MaraBet Web/Application" \
    --vpc-id $VPC_ID \
    --region $REGION \
    --query 'GroupId' \
    --output text 2>&1)

if [[ $SG_WEB == sg-* ]]; then
    print_success "Web SG criado: $SG_WEB"
    
    # Adicionar tags
    aws ec2 create-tags \
        --resources $SG_WEB \
        --tags Key=Name,Value=marabet-web-sg Key=Environment,Value=production \
        --region $REGION
    
    print_info "Adicionando regras de entrada..."
    
    # HTTP
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_WEB \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null || print_warning "Regra HTTP já existe"
    print_success "Porta 80 (HTTP) permitida"
    
    # HTTPS
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_WEB \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null || print_warning "Regra HTTPS já existe"
    print_success "Porta 443 (HTTPS) permitida"
    
    # SSH
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_WEB \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null || print_warning "Regra SSH já existe"
    print_success "Porta 22 (SSH) permitida"
    
    # Aplicação (porta 8000)
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_WEB \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null || print_warning "Regra 8000 já existe"
    print_success "Porta 8000 (App) permitida"
    
else
    if echo "$SG_WEB" | grep -q "already exists"; then
        print_warning "Security Group já existe, obtendo ID..."
        SG_WEB=$(aws ec2 describe-security-groups \
            --filters "Name=group-name,Values=marabet-web-sg" "Name=vpc-id,Values=$VPC_ID" \
            --region $REGION \
            --query 'SecurityGroups[0].GroupId' \
            --output text)
        print_success "Web SG existente: $SG_WEB"
    else
        print_error "Erro ao criar Web SG: $SG_WEB"
        exit 1
    fi
fi

################################################################################
# 2. SECURITY GROUP RDS
################################################################################

print_header "2. CRIANDO SECURITY GROUP RDS"

print_info "Criando marabet-rds-sg..."
SG_RDS=$(aws ec2 create-security-group \
    --group-name marabet-rds-sg \
    --description "Security group for MaraBet RDS PostgreSQL" \
    --vpc-id $VPC_ID \
    --region $REGION \
    --query 'GroupId' \
    --output text 2>&1)

if [[ $SG_RDS == sg-* ]]; then
    print_success "RDS SG criado: $SG_RDS"
    
    # Adicionar tags
    aws ec2 create-tags \
        --resources $SG_RDS \
        --tags Key=Name,Value=marabet-rds-sg Key=Environment,Value=production Key=Service,Value=RDS \
        --region $REGION
    
    print_info "Permitindo PostgreSQL (5432) apenas do Web SG..."
    
    # PostgreSQL do Web SG
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_RDS \
        --protocol tcp \
        --port 5432 \
        --source-group $SG_WEB \
        --region $REGION 2>/dev/null || print_warning "Regra PostgreSQL já existe"
    
    print_success "PostgreSQL (5432) permitido de $SG_WEB"
    
else
    if echo "$SG_RDS" | grep -q "already exists"; then
        print_warning "Security Group já existe, obtendo ID..."
        SG_RDS=$(aws ec2 describe-security-groups \
            --filters "Name=group-name,Values=marabet-rds-sg" "Name=vpc-id,Values=$VPC_ID" \
            --region $REGION \
            --query 'SecurityGroups[0].GroupId' \
            --output text)
        print_success "RDS SG existente: $SG_RDS"
    else
        print_error "Erro ao criar RDS SG: $SG_RDS"
        exit 1
    fi
fi

################################################################################
# 3. SECURITY GROUP REDIS
################################################################################

print_header "3. CRIANDO SECURITY GROUP REDIS"

print_info "Criando marabet-redis-sg..."
SG_REDIS=$(aws ec2 create-security-group \
    --group-name marabet-redis-sg \
    --description "Security group for MaraBet ElastiCache Redis" \
    --vpc-id $VPC_ID \
    --region $REGION \
    --query 'GroupId' \
    --output text 2>&1)

if [[ $SG_REDIS == sg-* ]]; then
    print_success "Redis SG criado: $SG_REDIS"
    
    # Adicionar tags
    aws ec2 create-tags \
        --resources $SG_REDIS \
        --tags Key=Name,Value=marabet-redis-sg Key=Environment,Value=production Key=Service,Value=Redis \
        --region $REGION
    
    print_info "Permitindo Redis (6379) apenas do Web SG..."
    
    # Redis do Web SG
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_REDIS \
        --protocol tcp \
        --port 6379 \
        --source-group $SG_WEB \
        --region $REGION 2>/dev/null || print_warning "Regra Redis já existe"
    
    print_success "Redis (6379) permitido de $SG_WEB"
    
else
    if echo "$SG_REDIS" | grep -q "already exists"; then
        print_warning "Security Group já existe, obtendo ID..."
        SG_REDIS=$(aws ec2 describe-security-groups \
            --filters "Name=group-name,Values=marabet-redis-sg" "Name=vpc-id,Values=$VPC_ID" \
            --region $REGION \
            --query 'SecurityGroups[0].GroupId' \
            --output text)
        print_success "Redis SG existente: $SG_REDIS"
    else
        print_error "Erro ao criar Redis SG: $SG_REDIS"
        exit 1
    fi
fi

################################################################################
# 4. RESUMO E VERIFICAÇÃO
################################################################################

print_header "4. VERIFICANDO SECURITY GROUPS"

print_info "Listando regras do Web SG..."
aws ec2 describe-security-groups \
    --group-ids $SG_WEB \
    --region $REGION \
    --query 'SecurityGroups[0].IpPermissions[*].[IpProtocol,FromPort,ToPort,join(`,`,IpRanges[*].CidrIp),join(`,`,UserIdGroupPairs[*].GroupId)]' \
    --output table

echo ""
print_info "Listando regras do RDS SG..."
aws ec2 describe-security-groups \
    --group-ids $SG_RDS \
    --region $REGION \
    --query 'SecurityGroups[0].IpPermissions[*].[IpProtocol,FromPort,ToPort,join(`,`,IpRanges[*].CidrIp),join(`,`,UserIdGroupPairs[*].GroupId)]' \
    --output table

echo ""
print_info "Listando regras do Redis SG..."
aws ec2 describe-security-groups \
    --group-ids $SG_REDIS \
    --region $REGION \
    --query 'SecurityGroups[0].IpPermissions[*].[IpProtocol,FromPort,ToPort,join(`,`,IpRanges[*].CidrIp),join(`,`,UserIdGroupPairs[*].GroupId)]' \
    --output table

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ SECURITY GROUPS CRIADOS COM SUCESSO!"

echo ""
echo "Security Groups:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🌐 Web/Application:"
echo "    ID:          $SG_WEB"
echo "    Name:        marabet-web-sg"
echo "    Regras:"
echo "      • Porta 80   (HTTP)  ← 0.0.0.0/0"
echo "      • Porta 443  (HTTPS) ← 0.0.0.0/0"
echo "      • Porta 22   (SSH)   ← 0.0.0.0/0"
echo "      • Porta 8000 (App)   ← 0.0.0.0/0"
echo ""
echo "  🗄️  RDS PostgreSQL:"
echo "    ID:          $SG_RDS"
echo "    Name:        marabet-rds-sg"
echo "    Regras:"
echo "      • Porta 5432 (PostgreSQL) ← $SG_WEB"
echo ""
echo "  💾 ElastiCache Redis:"
echo "    ID:          $SG_REDIS"
echo "    Name:        marabet-redis-sg"
echo "    Regras:"
echo "      • Porta 6379 (Redis) ← $SG_WEB"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Usar nos comandos seguintes:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  # Criar EC2 com Web SG"
echo "  aws ec2 run-instances --security-group-ids $SG_WEB ..."
echo ""
echo "  # Criar RDS com RDS SG"
echo "  aws rds create-db-instance --vpc-security-group-ids $SG_RDS ..."
echo ""
echo "  # Criar Redis com Redis SG"
echo "  aws elasticache create-replication-group --security-group-ids $SG_REDIS ..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Salvar IDs em arquivo
cat > marabet-security-groups.txt << EOF
MaraBet AI - Security Groups
=============================

VPC ID:              $VPC_ID
Region:              $REGION

Web/Application SG:  $SG_WEB (marabet-web-sg)
RDS PostgreSQL SG:   $SG_RDS (marabet-rds-sg)
Redis SG:            $SG_REDIS (marabet-redis-sg)

Comandos para usar:
-------------------

# EC2 Instance
aws ec2 run-instances \\
  --security-group-ids $SG_WEB \\
  --region $REGION

# RDS PostgreSQL
aws rds create-db-instance \\
  --vpc-security-group-ids $SG_RDS \\
  --region $REGION

# ElastiCache Redis
aws elasticache create-replication-group \\
  --security-group-ids $SG_REDIS \\
  --region $REGION

Variáveis de Ambiente:
----------------------
export VPC_ID=$VPC_ID
export SG_WEB=$SG_WEB
export SG_RDS=$SG_RDS
export SG_REDIS=$SG_REDIS
export REGION=$REGION
EOF

print_success "Informações salvas em: marabet-security-groups.txt"

echo ""
print_info "Para exportar as variáveis:"
echo ""
echo "  export VPC_ID=$VPC_ID"
echo "  export SG_WEB=$SG_WEB"
echo "  export SG_RDS=$SG_RDS"
echo "  export SG_REDIS=$SG_REDIS"
echo "  export REGION=$REGION"
echo ""

print_header "✅ CONCLUÍDO!"

