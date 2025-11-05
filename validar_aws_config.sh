#!/bin/bash

################################################################################
# MARABET AI - VALIDAÇÃO DE CONFIGURAÇÃO AWS
# Testa se as credenciais AWS estão corretas e funcionando
################################################################################

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo "========================================================================"
    echo "$1"
    echo "========================================================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

ERRORS=0
WARNINGS=0

print_header "🔍 MARABET AI - VALIDAÇÃO AWS"

################################################################################
# 1. VERIFICAR AWS CLI
################################################################################

print_header "1. VERIFICANDO AWS CLI"

if ! command -v aws &> /dev/null; then
    print_error "AWS CLI não encontrado!"
    print_info "Instale: https://aws.amazon.com/cli/"
    exit 1
fi

AWS_VERSION=$(aws --version 2>&1)
print_success "AWS CLI instalado: $AWS_VERSION"

################################################################################
# 2. VERIFICAR CONFIGURAÇÃO
################################################################################

print_header "2. VERIFICANDO CONFIGURAÇÃO"

# Access Key
ACCESS_KEY=$(aws configure get aws_access_key_id 2>/dev/null)
if [ -z "$ACCESS_KEY" ]; then
    print_error "Access Key não configurada!"
    ((ERRORS++))
else
    print_success "Access Key: ${ACCESS_KEY:0:10}..."
fi

# Secret Key
SECRET_KEY=$(aws configure get aws_secret_access_key 2>/dev/null)
if [ -z "$SECRET_KEY" ]; then
    print_error "Secret Key não configurada!"
    ((ERRORS++))
else
    print_success "Secret Key: ********** (configurada)"
fi

# Region
REGION=$(aws configure get region 2>/dev/null)
if [ -z "$REGION" ]; then
    print_error "Região não configurada!"
    ((ERRORS++))
else
    print_success "Região: $REGION"
    if [ "$REGION" != "eu-west-1" ]; then
        print_warning "Região não é eu-west-1 (Irlanda)"
        ((WARNINGS++))
    fi
fi

# Output Format
OUTPUT=$(aws configure get output 2>/dev/null)
if [ -z "$OUTPUT" ]; then
    print_warning "Output format não configurado (será text por padrão)"
    ((WARNINGS++))
else
    print_success "Output format: $OUTPUT"
fi

################################################################################
# 3. VERIFICAR IDENTIDADE
################################################################################

print_header "3. VERIFICANDO IDENTIDADE AWS"

print_info "Consultando STS GetCallerIdentity..."

IDENTITY=$(aws sts get-caller-identity 2>&1)
if [ $? -eq 0 ]; then
    print_success "Credenciais válidas!"
    
    USER_ID=$(echo "$IDENTITY" | jq -r '.UserId' 2>/dev/null)
    ACCOUNT=$(echo "$IDENTITY" | jq -r '.Account' 2>/dev/null)
    ARN=$(echo "$IDENTITY" | jq -r '.Arn' 2>/dev/null)
    
    echo ""
    print_info "User ID: $USER_ID"
    print_info "Account: $ACCOUNT"
    print_info "ARN: $ARN"
else
    print_error "Falha ao verificar identidade!"
    print_error "Resposta: $IDENTITY"
    ((ERRORS++))
    
    if echo "$IDENTITY" | grep -q "InvalidClientTokenId"; then
        print_error "Access Key inválida ou expirada"
    elif echo "$IDENTITY" | grep -q "SignatureDoesNotMatch"; then
        print_error "Secret Key incorreta"
    fi
fi

################################################################################
# 4. TESTAR ACESSO AOS SERVIÇOS
################################################################################

print_header "4. TESTANDO ACESSO AOS SERVIÇOS"

# EC2
print_info "Testando EC2..."
if aws ec2 describe-regions --region eu-west-1 &> /dev/null; then
    print_success "EC2: Acesso OK"
else
    print_error "EC2: Sem acesso"
    ((ERRORS++))
fi

# VPC
print_info "Testando VPC..."
if aws ec2 describe-vpcs --region eu-west-1 &> /dev/null; then
    VPC_COUNT=$(aws ec2 describe-vpcs --region eu-west-1 --query 'Vpcs | length(@)' --output text)
    print_success "VPC: Acesso OK ($VPC_COUNT VPCs existentes)"
else
    print_error "VPC: Sem acesso"
    ((ERRORS++))
fi

# S3
print_info "Testando S3..."
if aws s3 ls &> /dev/null; then
    BUCKET_COUNT=$(aws s3 ls 2>/dev/null | wc -l)
    print_success "S3: Acesso OK ($BUCKET_COUNT buckets existentes)"
else
    print_error "S3: Sem acesso"
    ((ERRORS++))
fi

# RDS
print_info "Testando RDS..."
if aws rds describe-db-instances --region eu-west-1 &> /dev/null; then
    RDS_COUNT=$(aws rds describe-db-instances --region eu-west-1 --query 'DBInstances | length(@)' --output text)
    print_success "RDS: Acesso OK ($RDS_COUNT instâncias existentes)"
else
    print_error "RDS: Sem acesso"
    ((ERRORS++))
fi

# ElastiCache
print_info "Testando ElastiCache..."
if aws elasticache describe-cache-clusters --region eu-west-1 &> /dev/null; then
    CACHE_COUNT=$(aws elasticache describe-cache-clusters --region eu-west-1 --query 'CacheClusters | length(@)' --output text)
    print_success "ElastiCache: Acesso OK ($CACHE_COUNT clusters existentes)"
else
    print_error "ElastiCache: Sem acesso"
    ((ERRORS++))
fi

################################################################################
# 5. VERIFICAR LIMITES DA CONTA
################################################################################

print_header "5. VERIFICANDO LIMITES DA CONTA"

print_info "Consultando limites de serviço..."

# EC2 Instances
EC2_LIMIT=$(aws service-quotas get-service-quota \
    --service-code ec2 \
    --quota-code L-1216C47A \
    --region eu-west-1 \
    --query 'Quota.Value' \
    --output text 2>/dev/null)

if [ ! -z "$EC2_LIMIT" ]; then
    print_success "Limite EC2 On-Demand: $EC2_LIMIT instâncias"
else
    print_warning "Não foi possível verificar limite de EC2"
    ((WARNINGS++))
fi

# RDS Instances
RDS_LIMIT=$(aws service-quotas get-service-quota \
    --service-code rds \
    --quota-code L-7B6409FD \
    --region eu-west-1 \
    --query 'Quota.Value' \
    --output text 2>/dev/null)

if [ ! -z "$RDS_LIMIT" ]; then
    print_success "Limite RDS Instances: $RDS_LIMIT instâncias"
else
    print_warning "Não foi possível verificar limite de RDS"
    ((WARNINGS++))
fi

################################################################################
# 6. VERIFICAR CUSTOS ATUAIS
################################################################################

print_header "6. VERIFICANDO CUSTOS"

print_info "Consultando custos do mês atual..."

CURRENT_MONTH=$(date -u +%Y-%m-01)
TODAY=$(date -u +%Y-%m-%d)

COST_RESULT=$(aws ce get-cost-and-usage \
    --time-period Start=$CURRENT_MONTH,End=$TODAY \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --region us-east-1 2>&1)

if [ $? -eq 0 ]; then
    COST=$(echo "$COST_RESULT" | jq -r '.ResultsByTime[0].Total.BlendedCost.Amount' 2>/dev/null)
    if [ ! -z "$COST" ] && [ "$COST" != "null" ]; then
        print_success "Custo acumulado este mês: \$$COST USD"
    else
        print_info "Custo: \$0.00 USD (conta nova ou sem uso)"
    fi
else
    print_warning "Não foi possível consultar custos"
    print_info "Pode ser necessário habilitar Cost Explorer no console AWS"
    ((WARNINGS++))
fi

################################################################################
# 7. VERIFICAR RECURSOS EXISTENTES
################################################################################

print_header "7. VERIFICANDO RECURSOS EXISTENTES NA REGIÃO"

print_info "Consultando recursos em eu-west-1..."

# EC2 Instances
EC2_RUNNING=$(aws ec2 describe-instances \
    --region eu-west-1 \
    --filters "Name=instance-state-name,Values=running" \
    --query 'Reservations[].Instances[].[InstanceId,InstanceType,Tags[?Key==`Name`].Value|[0]]' \
    --output text 2>/dev/null | wc -l)

if [ $EC2_RUNNING -gt 0 ]; then
    print_warning "EC2: $EC2_RUNNING instâncias rodando"
    aws ec2 describe-instances \
        --region eu-west-1 \
        --filters "Name=instance-state-name,Values=running" \
        --query 'Reservations[].Instances[].[InstanceId,InstanceType,Tags[?Key==`Name`].Value|[0]]' \
        --output table 2>/dev/null
else
    print_info "EC2: Nenhuma instância rodando"
fi

# RDS Instances
RDS_RUNNING=$(aws rds describe-db-instances \
    --region eu-west-1 \
    --query 'DBInstances[].[DBInstanceIdentifier,DBInstanceClass,DBInstanceStatus]' \
    --output text 2>/dev/null | wc -l)

if [ $RDS_RUNNING -gt 0 ]; then
    print_warning "RDS: $RDS_RUNNING instâncias ativas"
    aws rds describe-db-instances \
        --region eu-west-1 \
        --query 'DBInstances[].[DBInstanceIdentifier,DBInstanceClass,DBInstanceStatus]' \
        --output table 2>/dev/null
else
    print_info "RDS: Nenhuma instância ativa"
fi

################################################################################
# RESUMO FINAL
################################################################################

print_header "📊 RESUMO DA VALIDAÇÃO"

echo ""
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    print_success "TUDO OK! Configuração AWS válida e funcional"
    echo ""
    print_info "Você está pronto para fazer o deploy!"
    print_info "Execute: ./deploy_aws_completo.sh"
elif [ $ERRORS -eq 0 ]; then
    print_success "Configuração válida com $WARNINGS avisos"
    echo ""
    print_warning "Revise os avisos acima antes de prosseguir"
    print_info "Você pode fazer o deploy: ./deploy_aws_completo.sh"
else
    print_error "Encontrados $ERRORS erros e $WARNINGS avisos"
    echo ""
    print_error "CORRIJA OS ERROS antes de fazer deploy!"
    echo ""
    print_info "Passos para corrigir:"
    print_info "1. aws configure"
    print_info "2. Insira Access Key: YOUR_AWS_ACCESS_KEY_ID"
    print_info "3. Insira Secret Key: (sua secret key)"
    print_info "4. Region: eu-west-1"
    print_info "5. Execute este script novamente"
fi

echo ""
print_header "✅ VALIDAÇÃO CONCLUÍDA"

exit $ERRORS

