#!/bin/bash

################################################################################
# MARABET AI - CRIAR EC2 INSTANCE
# Script automático completo para servidor de aplicação
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

print_header "🖥️  MARABET AI - CRIAR EC2 INSTANCE"

# Configurações
REGION="eu-west-1"
VPC_ID="vpc-081a8c63b16a94a3a"
INSTANCE_TYPE="t3.large"
INSTANCE_NAME="marabet-app"
KEY_NAME="marabet-key"
SEU_IP="102.206.57.108"  # IP do usuário

print_info "Região: $REGION"
print_info "VPC: $VPC_ID"
print_info "Instance Type: $INSTANCE_TYPE"
print_info "Seu IP: $SEU_IP"
echo ""

################################################################################
# 1. OBTER SUBNET PÚBLICA
################################################################################

print_header "1. OBTENDO SUBNET PÚBLICA"

print_info "Buscando subnet pública..."
SUBNET_PUBLIC=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" "Name=map-public-ip-on-launch,Values=true" \
    --region $REGION \
    --query 'Subnets[0].SubnetId' \
    --output text 2>&1)

if [[ $SUBNET_PUBLIC == subnet-* ]]; then
    print_success "Subnet Pública: $SUBNET_PUBLIC"
else
    print_warning "Subnet pública não encontrada, usando primeira subnet disponível..."
    SUBNET_PUBLIC=$(aws ec2 describe-subnets \
        --filters "Name=vpc-id,Values=$VPC_ID" \
        --region $REGION \
        --query 'Subnets[0].SubnetId' \
        --output text)
    
    print_info "Subnet: $SUBNET_PUBLIC"
fi

################################################################################
# 2. CRIAR SECURITY GROUP EC2
################################################################################

print_header "2. CRIANDO SECURITY GROUP EC2"

print_info "Criando marabet-ec2-sg..."
SG_EC2=$(aws ec2 create-security-group \
    --group-name marabet-ec2-sg \
    --description "Security group for MaraBet EC2 Application Server" \
    --vpc-id $VPC_ID \
    --region $REGION \
    --query 'GroupId' \
    --output text 2>&1)

if [[ $SG_EC2 == sg-* ]]; then
    print_success "EC2 Security Group criado: $SG_EC2"
    
    # Adicionar tags
    aws ec2 create-tags \
        --resources $SG_EC2 \
        --tags Key=Name,Value=marabet-ec2-sg Key=Environment,Value=production \
        --region $REGION
    
    print_info "Adicionando regras de firewall..."
    
    # SSH - Apenas do seu IP
    print_info "Permitindo SSH (22) apenas de $SEU_IP..."
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_EC2 \
        --protocol tcp \
        --port 22 \
        --cidr ${SEU_IP}/32 \
        --region $REGION
    print_success "SSH permitido de $SEU_IP"
    
    # HTTP
    print_info "Permitindo HTTP (80) de qualquer origem..."
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_EC2 \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    print_success "HTTP (80) permitido"
    
    # HTTPS
    print_info "Permitindo HTTPS (443) de qualquer origem..."
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_EC2 \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    print_success "HTTPS (443) permitido"
    
    # Aplicação (porta 8000)
    print_info "Permitindo porta da aplicação (8000)..."
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_EC2 \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    print_success "Porta 8000 permitida"
    
else
    if echo "$SG_EC2" | grep -q "already exists"; then
        print_warning "Security Group já existe, obtendo ID..."
        SG_EC2=$(aws ec2 describe-security-groups \
            --filters "Name=group-name,Values=marabet-ec2-sg" "Name=vpc-id,Values=$VPC_ID" \
            --region $REGION \
            --query 'SecurityGroups[0].GroupId' \
            --output text)
        print_success "EC2 SG existente: $SG_EC2"
    else
        print_error "Erro ao criar EC2 SG: $SG_EC2"
        exit 1
    fi
fi

################################################################################
# 3. CRIAR/OBTER KEY PAIR
################################################################################

print_header "3. CONFIGURANDO KEY PAIR"

if [ -f "${KEY_NAME}.pem" ]; then
    print_warning "Key ${KEY_NAME}.pem já existe localmente"
    print_info "Usando key pair existente"
else
    print_info "Criando Key Pair ${KEY_NAME}..."
    
    # Verificar se key pair existe na AWS
    KEY_EXISTS=$(aws ec2 describe-key-pairs \
        --key-names $KEY_NAME \
        --region $REGION 2>&1 || echo "not_found")
    
    if echo "$KEY_EXISTS" | grep -q "not_found"; then
        # Criar nova key
        aws ec2 create-key-pair \
            --key-name $KEY_NAME \
            --query 'KeyMaterial' \
            --output text \
            --region $REGION > ${KEY_NAME}.pem
        
        chmod 400 ${KEY_NAME}.pem
        print_success "Key Pair criada e salva: ${KEY_NAME}.pem"
    else
        print_warning "Key Pair já existe na AWS mas não está localmente"
        print_error "Você precisará da chave .pem para conectar via SSH"
        print_info "Se perdeu a chave, crie uma nova com nome diferente"
    fi
fi

################################################################################
# 4. OBTER AMI UBUNTU
################################################################################

print_header "4. OBTENDO AMI UBUNTU 22.04"

print_info "Buscando AMI Ubuntu 22.04 LTS mais recente..."
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text \
    --region $REGION)

print_success "AMI Ubuntu: $AMI_ID"

################################################################################
# 5. CRIAR USER DATA SCRIPT
################################################################################

print_header "5. PREPARANDO USER DATA SCRIPT"

print_info "Criando script de inicialização..."

# User Data para instalar tudo automaticamente
USER_DATA=$(cat << 'USERDATA'
#!/bin/bash

# Log do script
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "========================================"
echo "MaraBet AI - EC2 Setup"
echo "========================================"
echo ""

# Atualizar sistema
echo "1. Atualizando sistema..."
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# Instalar Docker
echo "2. Instalando Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Instalar Docker Compose
echo "3. Instalando Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Instalar ferramentas
echo "4. Instalando ferramentas..."
apt-get install -y \
    git \
    nginx \
    postgresql-client \
    redis-tools \
    python3 \
    python3-pip \
    python3-venv \
    jq \
    htop \
    curl \
    wget \
    unzip

# Instalar AWS CLI
echo "5. Instalando AWS CLI..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

# Criar diretórios
echo "6. Criando estrutura de diretórios..."
mkdir -p /opt/marabet
mkdir -p /var/log/marabet
mkdir -p /opt/marabet/backups

chown -R ubuntu:ubuntu /opt/marabet
chown -R ubuntu:ubuntu /var/log/marabet

# Configurar timezone
echo "7. Configurando timezone..."
timedatectl set-timezone Africa/Luanda

# Habilitar serviços
echo "8. Habilitando serviços..."
systemctl enable docker
systemctl enable nginx

# Criar arquivo de conclusão
echo "9. Finalizando..."
cat > /home/ubuntu/setup-complete.txt << EOF
MaraBet AI EC2 Setup Completo
==============================
Data: $(date)
Hostname: $(hostname)
IP Privado: $(hostname -I | awk '{print $1}')

Software Instalado:
- Docker $(docker --version)
- Docker Compose $(docker-compose --version)
- Nginx $(nginx -v 2>&1)
- PostgreSQL Client $(psql --version)
- Redis Tools (redis-cli --version)
- AWS CLI $(aws --version)
- Python $(python3 --version)

Próximos passos:
1. SSH: ssh -i marabet-key.pem ubuntu@<IP_PUBLICO>
2. Clone código: git clone <repo> /opt/marabet
3. Configurar .env
4. Deploy: docker-compose up -d
EOF

chown ubuntu:ubuntu /home/ubuntu/setup-complete.txt

echo ""
echo "✅ MaraBet EC2 Setup Completo!"
echo ""
USERDATA
)

print_success "User Data script preparado"

################################################################################
# 6. LANÇAR EC2 INSTANCE
################################################################################

print_header "6. LANÇANDO EC2 INSTANCE"

print_info "Criando instância $INSTANCE_TYPE..."
print_warning "Isso pode levar 2-3 minutos"

INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --subnet-id $SUBNET_PUBLIC \
    --security-group-ids $SG_EC2 \
    --user-data "$USER_DATA" \
    --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=100,VolumeType=gp3,Iops=3000,DeleteOnTermination=true}' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME},{Key=Environment,Value=production},{Key=Project,Value=MaraBet}]" \
    --monitoring Enabled=true \
    --region $REGION \
    --query 'Instances[0].InstanceId' \
    --output text)

print_success "EC2 Instance criada: $INSTANCE_ID"

################################################################################
# 7. AGUARDAR INSTANCE FICAR RUNNING
################################################################################

print_header "7. AGUARDANDO INSTANCE INICIAR"

print_info "Aguardando instância ficar running..."
aws ec2 wait instance-running \
    --instance-ids $INSTANCE_ID \
    --region $REGION

print_success "Instância running!"

print_info "Aguardando status checks (2/2)..."
aws ec2 wait instance-status-ok \
    --instance-ids $INSTANCE_ID \
    --region $REGION

print_success "Status checks OK!"

################################################################################
# 8. OBTER INFORMAÇÕES DA INSTANCE
################################################################################

print_header "8. OBTENDO INFORMAÇÕES DA INSTANCE"

print_info "Consultando detalhes..."

# Obter IPs
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

PRIVATE_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PrivateIpAddress' \
    --output text)

PUBLIC_DNS=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicDnsName' \
    --output text)

AZ=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].Placement.AvailabilityZone' \
    --output text)

print_success "IP Público: $PUBLIC_IP"
print_success "IP Privado: $PRIVATE_IP"
print_success "DNS Público: $PUBLIC_DNS"
print_success "Availability Zone: $AZ"

################################################################################
# 9. GERAR ARQUIVOS DE CONFIGURAÇÃO
################################################################################

print_header "9. GERANDO ARQUIVOS DE CONFIGURAÇÃO"

# ec2-info.txt
print_info "Criando ec2-info.txt..."
cat > ec2-info.txt << EOF
MaraBet AI - EC2 Instance
=========================

Instance ID:          $INSTANCE_ID
Instance Type:        $INSTANCE_TYPE
AMI:                  $AMI_ID
Region:               $REGION
Availability Zone:    $AZ

IP Público:           $PUBLIC_IP
IP Privado:           $PRIVATE_IP
DNS Público:          $PUBLIC_DNS

VPC:                  $VPC_ID
Subnet:               $SUBNET_PUBLIC
Security Group:       $SG_EC2
Key Pair:             $KEY_NAME

Storage:              100GB gp3 SSD (3000 IOPS)
Monitoring:           Enhanced (CloudWatch)

SSH Command:
ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP

HTTP Test:
curl http://$PUBLIC_IP

Generated:            $(date)
EOF

print_success "ec2-info.txt criado"

# .env.ec2
print_info "Criando .env.ec2..."
cat > .env.ec2 << EOF
# MaraBet AI - EC2 Configuration
# Generated: $(date)

# EC2 Instance
EC2_INSTANCE_ID=$INSTANCE_ID
EC2_PUBLIC_IP=$PUBLIC_IP
EC2_PRIVATE_IP=$PRIVATE_IP
EC2_PUBLIC_DNS=$PUBLIC_DNS
EC2_REGION=$REGION
EC2_AZ=$AZ

# SSH
SSH_USER=ubuntu
SSH_KEY=${KEY_NAME}.pem
SSH_COMMAND=ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP
EOF

print_success ".env.ec2 criado"

# ssh-connect.sh
print_info "Criando ssh-connect.sh..."
cat > ssh-connect.sh << EOF
#!/bin/bash
echo "🔐 Conectando ao MaraBet EC2..."
echo "IP: $PUBLIC_IP"
echo ""
ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP
EOF

chmod +x ssh-connect.sh
print_success "ssh-connect.sh criado"

# deploy-to-ec2.sh
print_info "Criando deploy-to-ec2.sh..."
cat > deploy-to-ec2.sh << 'EOF'
#!/bin/bash

echo "📦 Deploy MaraBet AI para EC2"
echo "=============================="
echo ""

# Carregar variáveis
source .env.ec2

echo "IP EC2: $EC2_PUBLIC_IP"
echo ""

# 1. Fazer upload do código
echo "1. Fazendo upload do código..."
rsync -avz --progress \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude 'node_modules' \
    --exclude 'venv' \
    --exclude '*.pyc' \
    -e "ssh -i $SSH_KEY" \
    ./ ubuntu@$EC2_PUBLIC_IP:/opt/marabet/

echo ""
echo "2. Configurando aplicação na EC2..."

# 2. Executar comandos remotos
ssh -i $SSH_KEY ubuntu@$EC2_PUBLIC_IP << 'REMOTE'
cd /opt/marabet

# Criar .env se não existir
if [ ! -f .env ]; then
    cp .env.example .env 2>/dev/null || touch .env
fi

# Build e start
docker-compose up -d --build

# Ver logs
docker-compose logs -f --tail=50
REMOTE

echo ""
echo "✅ Deploy concluído!"
echo ""
echo "Acessar:"
echo "  http://$EC2_PUBLIC_IP"
echo ""
EOF

chmod +x deploy-to-ec2.sh
print_success "deploy-to-ec2.sh criado"

################################################################################
# 10. ATUALIZAR SECURITY GROUP REDIS E RDS
################################################################################

print_header "10. ATUALIZANDO SECURITY GROUPS RDS E REDIS"

# Permitir RDS do EC2 SG
print_info "Permitindo EC2 acessar RDS..."
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
        --region $REGION 2>/dev/null || print_warning "Regra já existe"
    print_success "EC2 pode acessar RDS"
else
    print_warning "RDS Security Group não encontrado (será criado depois)"
fi

# Permitir Redis do EC2 SG
print_info "Permitindo EC2 acessar Redis..."
SG_REDIS=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=marabet-redis-sg" \
    --region $REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null)

if [[ $SG_REDIS == sg-* ]]; then
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_REDIS \
        --protocol tcp \
        --port 6379 \
        --source-group $SG_EC2 \
        --region $REGION 2>/dev/null || print_warning "Regra já existe"
    print_success "EC2 pode acessar Redis"
else
    # Usar o SG do Redis Serverless
    SG_REDIS_SERVERLESS="sg-09f7d3d37a8407f43"
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_REDIS_SERVERLESS \
        --protocol tcp \
        --port 6379 \
        --source-group $SG_EC2 \
        --region $REGION 2>/dev/null || print_warning "Regra já existe"
    print_success "EC2 pode acessar Redis Serverless"
fi

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ EC2 INSTANCE CRIADA COM SUCESSO!"

echo ""
echo "EC2 Instance:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Instance ID:       $INSTANCE_ID"
echo "  Instance Type:     $INSTANCE_TYPE"
echo "  AMI:               $AMI_ID (Ubuntu 22.04 LTS)"
echo ""
echo "  IP Público:        $PUBLIC_IP"
echo "  IP Privado:        $PRIVATE_IP"
echo "  DNS Público:       $PUBLIC_DNS"
echo ""
echo "  VPC:               $VPC_ID"
echo "  Subnet:            $SUBNET_PUBLIC"
echo "  Security Group:    $SG_EC2"
echo "  Availability Zone: $AZ"
echo ""
echo "  Key Pair:          ${KEY_NAME}.pem"
echo "  SSH User:          ubuntu"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Software Instalado (via User Data):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ✓ Docker + Docker Compose"
echo "  ✓ Nginx"
echo "  ✓ PostgreSQL Client"
echo "  ✓ Redis Tools"
echo "  ✓ AWS CLI"
echo "  ✓ Python 3 + pip"
echo "  ✓ Git"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Conectar via SSH:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ./ssh-connect.sh"
echo ""
echo "  OU"
echo ""
echo "  ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Testar HTTP:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  curl http://$PUBLIC_IP"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Adicionar IP à API-Football Whitelist:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  IP para adicionar: $PUBLIC_IP"
echo "  Dashboard: https://dashboard.api-football.com/"
echo "  Soccer > Settings > IP Whitelist"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Salvar informações
cat >> ec2-history.log << EOF
[$(date)] EC2 criada: $INSTANCE_ID | IP: $PUBLIC_IP | Type: $INSTANCE_TYPE
EOF

print_info "Histórico salvo em: ec2-history.log"

echo ""
print_header "✅ CONCLUÍDO!"

echo ""
print_warning "IMPORTANTE: Aguarde 2-3 minutos para o User Data completar"
print_info "O script instalará Docker, Nginx, etc. automaticamente"
echo ""
print_info "Verificar se setup completou:"
echo "  ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'cat /home/ubuntu/setup-complete.txt'"
echo ""

