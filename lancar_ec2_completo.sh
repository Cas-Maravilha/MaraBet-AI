#!/bin/bash

################################################################################
# MARABET AI - LANÇAR EC2 INSTANCE COMPLETO
# Script otimizado com todas as configurações
################################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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
    echo -e "${CYAN}========================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================================================${NC}"
    echo ""
}

print_header "🖥️  MARABET AI - LANÇAR EC2 INSTANCE"

# Configurações
REGION="eu-west-1"
VPC_ID="vpc-081a8c63b16a94a3a"
INSTANCE_TYPE="t3.medium"  # Otimizado: t3.medium é suficiente e mais barato
INSTANCE_NAME="marabet-ec2"
KEY_NAME="marabet-key"
VOLUME_SIZE=50  # 50GB é suficiente inicialmente
SEU_IP="102.206.57.108"

print_info "Região: $REGION"
print_info "VPC: $VPC_ID"
print_info "Instance Type: $INSTANCE_TYPE"
print_info "Storage: ${VOLUME_SIZE}GB gp3"
print_info "Seu IP (SSH): $SEU_IP"
echo ""

################################################################################
# 1. ENCONTRAR AMI UBUNTU 22.04
################################################################################

print_header "1. BUSCANDO AMI UBUNTU 22.04"

print_info "Consultando AMI mais recente..."
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text \
    --region $REGION)

if [ -z "$AMI_ID" ]; then
    print_error "AMI não encontrada!"
    exit 1
fi

print_success "AMI Ubuntu 22.04: $AMI_ID"

# Obter informações da AMI
AMI_NAME=$(aws ec2 describe-images \
    --image-ids $AMI_ID \
    --region $REGION \
    --query 'Images[0].Name' \
    --output text)

print_info "AMI Name: $AMI_NAME"

################################################################################
# 2. OBTER/CRIAR SUBNET PÚBLICA
################################################################################

print_header "2. OBTENDO SUBNET PÚBLICA"

print_info "Buscando subnet pública..."
SUBNET_PUBLIC=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --region $REGION \
    --query 'Subnets[0].SubnetId' \
    --output text)

if [ -z "$SUBNET_PUBLIC" ] || [ "$SUBNET_PUBLIC" == "None" ]; then
    print_error "Subnet não encontrada na VPC $VPC_ID"
    exit 1
fi

print_success "Subnet Pública: $SUBNET_PUBLIC"

# Obter AZ da subnet
SUBNET_AZ=$(aws ec2 describe-subnets \
    --subnet-ids $SUBNET_PUBLIC \
    --region $REGION \
    --query 'Subnets[0].AvailabilityZone' \
    --output text)

print_info "Availability Zone: $SUBNET_AZ"

################################################################################
# 3. CRIAR SECURITY GROUP EC2
################################################################################

print_header "3. CONFIGURANDO SECURITY GROUP"

# Tentar obter existente
SG_EC2=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=marabet-ec2-sg" "Name=vpc-id,Values=$VPC_ID" \
    --region $REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null)

if [[ $SG_EC2 == sg-* ]]; then
    print_warning "Security Group já existe: $SG_EC2"
else
    print_info "Criando Security Group..."
    SG_EC2=$(aws ec2 create-security-group \
        --group-name marabet-ec2-sg \
        --description "Security group for MaraBet EC2 Application Server" \
        --vpc-id $VPC_ID \
        --region $REGION \
        --query 'GroupId' \
        --output text)
    
    print_success "Security Group criado: $SG_EC2"
    
    # Adicionar tags
    aws ec2 create-tags \
        --resources $SG_EC2 \
        --tags Key=Name,Value=marabet-ec2-sg Key=Environment,Value=production Key=Project,Value=MaraBet \
        --region $REGION
    
    # Adicionar regras
    print_info "Adicionando regras de firewall..."
    
    # SSH - apenas seu IP
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_EC2 \
        --protocol tcp \
        --port 22 \
        --cidr ${SEU_IP}/32 \
        --region $REGION
    print_success "  SSH (22) ← $SEU_IP/32"
    
    # HTTP
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_EC2 \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    print_success "  HTTP (80) ← 0.0.0.0/0"
    
    # HTTPS
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_EC2 \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    print_success "  HTTPS (443) ← 0.0.0.0/0"
    
    # Aplicação (8000)
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_EC2 \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region $REGION 2>/dev/null || true
    print_success "  App (8000) ← 0.0.0.0/0"
fi

################################################################################
# 4. VERIFICAR/CRIAR KEY PAIR
################################################################################

print_header "4. VERIFICANDO KEY PAIR"

# Verificar se key existe
KEY_EXISTS=$(aws ec2 describe-key-pairs \
    --key-names $KEY_NAME \
    --region $REGION 2>&1 || echo "not_found")

if echo "$KEY_EXISTS" | grep -q "not_found"; then
    print_warning "Key Pair não encontrada, criando..."
    
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text \
        --region $REGION > ${KEY_NAME}.pem
    
    chmod 400 ${KEY_NAME}.pem
    print_success "Key Pair criada: ${KEY_NAME}.pem"
else
    print_success "Key Pair existe: $KEY_NAME"
    
    if [ ! -f "${KEY_NAME}.pem" ]; then
        print_warning "Arquivo ${KEY_NAME}.pem não encontrado localmente"
        print_error "Você precisará da chave .pem para SSH"
    else
        chmod 400 ${KEY_NAME}.pem
        print_success "Key Pair local: ${KEY_NAME}.pem"
    fi
fi

################################################################################
# 5. LANÇAR EC2 INSTANCE
################################################################################

print_header "5. LANÇANDO EC2 INSTANCE"

print_info "Criando instância $INSTANCE_TYPE..."
print_warning "Isso levará 2-3 minutos"
echo ""

# Verificar se user-data.sh existe
if [ ! -f "user-data.sh" ]; then
    print_warning "user-data.sh não encontrado, criando versão básica..."
    cat > user-data.sh << 'EOF'
#!/bin/bash
apt-get update
apt-get install -y docker.io docker-compose git nginx postgresql-client redis-tools
systemctl enable docker nginx
echo "MaraBet EC2 ready" > /home/ubuntu/ready.txt
EOF
fi

INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SG_EC2 \
    --subnet-id $SUBNET_PUBLIC \
    --associate-public-ip-address \
    --block-device-mappings "[{\"DeviceName\":\"/dev/sda1\",\"Ebs\":{\"VolumeSize\":$VOLUME_SIZE,\"VolumeType\":\"gp3\",\"Iops\":3000,\"DeleteOnTermination\":true}}]" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME},{Key=Environment,Value=production},{Key=Project,Value=MaraBet},{Key=Owner,Value=MaraBet-Team}]" \
    --monitoring Enabled=true \
    --user-data file://user-data.sh \
    --region $REGION \
    --query 'Instances[0].InstanceId' \
    --output text)

if [ -z "$INSTANCE_ID" ]; then
    print_error "Falha ao criar instância!"
    exit 1
fi

print_success "EC2 Instance criada: $INSTANCE_ID"

################################################################################
# 6. AGUARDAR INSTANCE INICIAR
################################################################################

print_header "6. AGUARDANDO INSTANCE INICIAR"

print_info "Aguardando status: running..."
aws ec2 wait instance-running \
    --instance-ids $INSTANCE_ID \
    --region $REGION

print_success "Instance running!"

print_info "Aguardando status checks (2/2)..."
aws ec2 wait instance-status-ok \
    --instance-ids $INSTANCE_ID \
    --region $REGION

print_success "Status checks OK!"

################################################################################
# 7. OBTER INFORMAÇÕES DA INSTANCE
################################################################################

print_header "7. OBTENDO INFORMAÇÕES"

print_info "Consultando detalhes da instância..."

# Obter informações
INSTANCE_INFO=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0]')

PUBLIC_IP=$(echo "$INSTANCE_INFO" | jq -r '.PublicIpAddress')
PRIVATE_IP=$(echo "$INSTANCE_INFO" | jq -r '.PrivateIpAddress')
PUBLIC_DNS=$(echo "$INSTANCE_INFO" | jq -r '.PublicDnsName')
STATE=$(echo "$INSTANCE_INFO" | jq -r '.State.Name')
AZ=$(echo "$INSTANCE_INFO" | jq -r '.Placement.AvailabilityZone')

print_success "IP Público: $PUBLIC_IP"
print_success "IP Privado: $PRIVATE_IP"
print_success "DNS Público: $PUBLIC_DNS"
print_success "Estado: $STATE"
print_success "AZ: $AZ"

################################################################################
# 8. ATUALIZAR SECURITY GROUPS RDS E REDIS
################################################################################

print_header "8. ATUALIZANDO SECURITY GROUPS"

print_info "Permitindo EC2 acessar RDS e Redis..."

# Redis Serverless SG
SG_REDIS="sg-09f7d3d37a8407f43"
aws ec2 authorize-security-group-ingress \
    --group-id $SG_REDIS \
    --protocol tcp \
    --port 6379 \
    --source-group $SG_EC2 \
    --region $REGION 2>/dev/null && print_success "  EC2 → Redis (6379)" || print_warning "  Regra já existe"

# RDS SG (se existir)
SG_RDS=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=marabet-rds-sg" \
    --region $REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null)

if [[ $SG_RDS == sg-* ]]; then
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_RDS \
        --protocol tcp \
        --port 5432 \
        --source-group $SG_EC2 \
        --region $REGION 2>/dev/null && print_success "  EC2 → RDS (5432)" || print_warning "  Regra já existe"
fi

################################################################################
# 9. ADICIONAR IP À API-FOOTBALL WHITELIST
################################################################################

print_header "9. ATUALIZAR API-FOOTBALL WHITELIST"

print_warning "AÇÃO MANUAL NECESSÁRIA!"
echo ""
print_info "Adicione o IP público da EC2 ao whitelist da API-Football:"
echo ""
echo "  📍 IP para adicionar: $PUBLIC_IP"
echo ""
echo "  🔗 Dashboard: https://dashboard.api-football.com/"
echo "  📂 Soccer > Settings > IP Whitelist"
echo "  ➕ Adicionar IP: $PUBLIC_IP"
echo ""

################################################################################
# 10. GERAR ARQUIVOS DE CONFIGURAÇÃO
################################################################################

print_header "10. GERANDO ARQUIVOS DE CONFIGURAÇÃO"

# ec2-instance-info.txt
print_info "Criando ec2-instance-info.txt..."
cat > ec2-instance-info.txt << EOF
MaraBet AI - EC2 Instance Information
======================================

Instance Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Instance ID:          $INSTANCE_ID
Instance Type:        $INSTANCE_TYPE
State:                $STATE
AMI:                  $AMI_ID
AMI Name:             $AMI_NAME
Region:               $REGION
Availability Zone:    $AZ

Network:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IP Público:           $PUBLIC_IP
IP Privado:           $PRIVATE_IP
DNS Público:          $PUBLIC_DNS

VPC:                  $VPC_ID
Subnet:               $SUBNET_PUBLIC
Security Group:       $SG_EC2

Storage:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Volume Size:          ${VOLUME_SIZE}GB
Volume Type:          gp3 SSD
IOPS:                 3000
Throughput:           125 MB/s

Access:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SSH Key:              ${KEY_NAME}.pem
SSH User:             ubuntu
SSH Command:          ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP

HTTP Test:            curl http://$PUBLIC_IP
HTTPS Test:           curl https://$PUBLIC_IP

Connections to AWS Services:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RDS PostgreSQL:
  Endpoint:           database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com
  Port:               5432
  Test:               psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com -p 5432 -U marabet_admin -d postgres

Redis Serverless:
  Endpoint:           marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com
  Port:               6379
  Test:               redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com -p 6379 --tls --insecure

API-Football:
  ⚠️  ADICIONAR IP AO WHITELIST: $PUBLIC_IP
  Dashboard:          https://dashboard.api-football.com/

Generated:            $(date)
EOF

print_success "ec2-instance-info.txt criado"

# .env.ec2
print_info "Criando .env.ec2..."
cat > .env.ec2 << EOF
# MaraBet AI - EC2 Instance Configuration
# Generated: $(date)

# EC2 Instance
EC2_INSTANCE_ID=$INSTANCE_ID
EC2_INSTANCE_TYPE=$INSTANCE_TYPE
EC2_PUBLIC_IP=$PUBLIC_IP
EC2_PRIVATE_IP=$PRIVATE_IP
EC2_PUBLIC_DNS=$PUBLIC_DNS
EC2_REGION=$REGION
EC2_AZ=$AZ
EC2_STATE=$STATE

# SSH Access
SSH_USER=ubuntu
SSH_KEY=${KEY_NAME}.pem
SSH_COMMAND=ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP

# Security
SECURITY_GROUP_ID=$SG_EC2
VPC_ID=$VPC_ID
SUBNET_ID=$SUBNET_PUBLIC

# Storage
VOLUME_SIZE=${VOLUME_SIZE}
VOLUME_TYPE=gp3

# URLs
HTTP_URL=http://$PUBLIC_IP
HTTPS_URL=https://$PUBLIC_IP
EOF

print_success ".env.ec2 criado"

# ssh-connect.sh
print_info "Criando ssh-connect.sh..."
cat > ssh-connect.sh << EOF
#!/bin/bash
echo "🔐 Conectando ao MaraBet EC2..."
echo "Instance ID: $INSTANCE_ID"
echo "IP Público: $PUBLIC_IP"
echo ""

# Verificar permissões da chave
if [ -f "${KEY_NAME}.pem" ]; then
    chmod 400 ${KEY_NAME}.pem
    ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP
else
    echo "❌ Key file não encontrado: ${KEY_NAME}.pem"
    exit 1
fi
EOF

chmod +x ssh-connect.sh
print_success "ssh-connect.sh criado"

# wait-user-data.sh
print_info "Criando wait-user-data.sh..."
cat > wait-user-data.sh << 'EOF'
#!/bin/bash
echo "⏳ Aguardando User Data completar..."
echo "Conectando à EC2 para verificar..."
echo ""

source .env.ec2

MAX_ATTEMPTS=20
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ((ATTEMPT++))
    echo -n "Tentativa $ATTEMPT/$MAX_ATTEMPTS... "
    
    if ssh -i $SSH_KEY -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@$EC2_PUBLIC_IP "test -f /home/ubuntu/setup-complete.txt" 2>/dev/null; then
        echo "✅"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ USER DATA COMPLETO!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        ssh -i $SSH_KEY ubuntu@$EC2_PUBLIC_IP "cat /home/ubuntu/setup-complete.txt"
        exit 0
    else
        echo "⏳"
        sleep 30
    fi
done

echo ""
echo "⚠️  Timeout aguardando User Data"
echo "Verifique manualmente:"
echo "  ssh -i $SSH_KEY ubuntu@$EC2_PUBLIC_IP 'tail -f /var/log/user-data.log'"
EOF

chmod +x wait-user-data.sh
print_success "wait-user-data.sh criado"

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ EC2 INSTANCE CRIADA COM SUCESSO!"

echo ""
echo -e "${CYAN}EC2 Instance:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Instance ID:       $INSTANCE_ID"
echo "  Instance Type:     $INSTANCE_TYPE"
echo "  AMI:               $AMI_ID"
echo "  State:             $STATE"
echo ""
echo "  IP Público:        ${GREEN}$PUBLIC_IP${NC}"
echo "  IP Privado:        $PRIVATE_IP"
echo "  DNS Público:       $PUBLIC_DNS"
echo ""
echo "  VPC:               $VPC_ID"
echo "  Subnet:            $SUBNET_PUBLIC"
echo "  Security Group:    $SG_EC2"
echo "  Availability Zone: $AZ"
echo ""
echo "  Key Pair:          ${KEY_NAME}.pem"
echo "  Storage:           ${VOLUME_SIZE}GB gp3 SSD"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}Software (instalando via User Data):${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ⏳ Docker + Docker Compose"
echo "  ⏳ Nginx"
echo "  ⏳ PostgreSQL Client"
echo "  ⏳ Redis Tools"
echo "  ⏳ AWS CLI"
echo "  ⏳ Python 3 + pip"
echo "  ⏳ Git"
echo ""
echo "  ${YELLOW}Aguarde 2-3 minutos para completar${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}Próximos Passos:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Aguardar User Data completar:"
echo "     ${GREEN}./wait-user-data.sh${NC}"
echo ""
echo "  2. Conectar via SSH:"
echo "     ${GREEN}./ssh-connect.sh${NC}"
echo "     ${YELLOW}OU${NC}"
echo "     ${GREEN}ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP${NC}"
echo ""
echo "  3. Verificar setup completo:"
echo "     ${GREEN}ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'cat /home/ubuntu/setup-complete.txt'${NC}"
echo ""
echo "  4. Adicionar IP à API-Football:"
echo "     ${YELLOW}IP: $PUBLIC_IP${NC}"
echo "     ${BLUE}https://dashboard.api-football.com/${NC}"
echo ""
echo "  5. Deploy MaraBet:"
echo "     ${GREEN}Seguir: CRIAR_EC2_GUIA_COMPLETO.md${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Salvar no histórico
cat >> ec2-history.log << EOF
[$(date)] EC2 criada: $INSTANCE_ID | IP: $PUBLIC_IP | Type: $INSTANCE_TYPE | AMI: $AMI_ID
EOF

print_success "Histórico salvo em: ec2-history.log"

echo ""
print_header "✅ CONCLUÍDO!"

echo ""
print_info "Arquivos gerados:"
echo "  📄 ec2-instance-info.txt      - Informações completas"
echo "  📄 .env.ec2                   - Variáveis de ambiente"
echo "  📄 ssh-connect.sh             - Script de conexão SSH"
echo "  📄 wait-user-data.sh          - Aguardar setup completar"
echo ""

