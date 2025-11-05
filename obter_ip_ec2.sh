#!/bin/bash

################################################################################
# MARABET AI - OBTER IP PÚBLICO DA EC2
# Obtém e salva IP público da instância EC2
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

print_header "📍 MARABET AI - OBTER IP PÚBLICO EC2"

# Configurações
REGION="eu-west-1"
INSTANCE_NAME="marabet-ec2"

################################################################################
# 1. ENCONTRAR INSTANCE ID
################################################################################

print_header "1. ENCONTRANDO EC2 INSTANCE"

# Se foi passado Instance ID como parâmetro
if [ ! -z "$1" ]; then
    INSTANCE_ID=$1
    print_info "Instance ID fornecido: $INSTANCE_ID"
else
    # Buscar por nome
    print_info "Buscando instância com nome: $INSTANCE_NAME..."
    
    INSTANCE_ID=$(aws ec2 describe-instances \
        --filters "Name=tag:Name,Values=$INSTANCE_NAME" "Name=instance-state-name,Values=running,pending,stopping,stopped" \
        --region $REGION \
        --query 'Reservations[0].Instances[0].InstanceId' \
        --output text 2>&1)
    
    if [ -z "$INSTANCE_ID" ] || [ "$INSTANCE_ID" == "None" ]; then
        print_error "Instância não encontrada!"
        echo ""
        print_info "Listar todas as instâncias:"
        aws ec2 describe-instances \
            --region $REGION \
            --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value|[0],State.Name,PublicIpAddress]' \
            --output table
        exit 1
    fi
    
    print_success "Instance ID: $INSTANCE_ID"
fi

################################################################################
# 2. OBTER INFORMAÇÕES DA INSTÂNCIA
################################################################################

print_header "2. OBTENDO INFORMAÇÕES COMPLETAS"

print_info "Consultando instância $INSTANCE_ID..."

INSTANCE_INFO=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0]' 2>&1)

if [ $? -ne 0 ]; then
    print_error "Erro ao consultar instância!"
    echo "$INSTANCE_INFO"
    exit 1
fi

# Extrair informações
PUBLIC_IP=$(echo "$INSTANCE_INFO" | jq -r '.PublicIpAddress // "N/A"')
PRIVATE_IP=$(echo "$INSTANCE_INFO" | jq -r '.PrivateIpAddress // "N/A"')
PUBLIC_DNS=$(echo "$INSTANCE_INFO" | jq -r '.PublicDnsName // "N/A"')
STATE=$(echo "$INSTANCE_INFO" | jq -r '.State.Name')
INSTANCE_TYPE=$(echo "$INSTANCE_INFO" | jq -r '.InstanceType')
AZ=$(echo "$INSTANCE_INFO" | jq -r '.Placement.AvailabilityZone')
VPC_ID=$(echo "$INSTANCE_INFO" | jq -r '.VpcId')
SUBNET_ID=$(echo "$INSTANCE_INFO" | jq -r '.SubnetId')

# Security Groups
SG_IDS=$(echo "$INSTANCE_INFO" | jq -r '.SecurityGroups[].GroupId' | tr '\n' ' ')
SG_NAMES=$(echo "$INSTANCE_INFO" | jq -r '.SecurityGroups[].GroupName' | tr '\n' ', ' | sed 's/,$//')

# Nome da instância
INSTANCE_NAME=$(echo "$INSTANCE_INFO" | jq -r '.Tags[]? | select(.Key=="Name") | .Value // "N/A"')

print_info "Nome: $INSTANCE_NAME"
print_info "Estado: $STATE"
print_info "Tipo: $INSTANCE_TYPE"
print_info "AZ: $AZ"

################################################################################
# 3. MOSTRAR IPs
################################################################################

print_header "3. ENDEREÇOS IP"

if [ "$PUBLIC_IP" != "N/A" ] && [ ! -z "$PUBLIC_IP" ]; then
    print_success "IP Público: $PUBLIC_IP"
else
    print_warning "IP Público: Não disponível"
    print_info "Possíveis causas:"
    echo "  • Instância não tem IP público associado"
    echo "  • Instância está parando/parada"
    echo "  • Subnet não tem auto-assign public IP"
fi

print_info "IP Privado: $PRIVATE_IP"

if [ "$PUBLIC_DNS" != "N/A" ] && [ ! -z "$PUBLIC_DNS" ]; then
    print_info "DNS Público: $PUBLIC_DNS"
fi

################################################################################
# 4. SALVAR INFORMAÇÕES
################################################################################

print_header "4. SALVANDO INFORMAÇÕES"

# Arquivo de texto
print_info "Criando ec2-ip-info.txt..."
cat > ec2-ip-info.txt << EOF
MaraBet AI - EC2 IP Information
================================

Instance Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Instance ID:          $INSTANCE_ID
Instance Name:        $INSTANCE_NAME
Instance Type:        $INSTANCE_TYPE
State:                $STATE
Region:               $REGION
Availability Zone:    $AZ

Network:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IP Público:           $PUBLIC_IP
IP Privado:           $PRIVATE_IP
DNS Público:          $PUBLIC_DNS

VPC:                  $VPC_ID
Subnet:               $SUBNET_ID
Security Groups:      $SG_NAMES

SSH Access:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SSH Command:          ssh -i marabet-key.pem ubuntu@$PUBLIC_IP

URLs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HTTP:                 http://$PUBLIC_IP
HTTPS:                https://$PUBLIC_IP
Health Check:         http://$PUBLIC_IP/health

API-Football Whitelist:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  ADICIONAR ESTE IP AO WHITELIST:
    $PUBLIC_IP

    Dashboard: https://dashboard.api-football.com/
    Soccer > Settings > IP Whitelist > Add IP

Generated:            $(date)
EOF

print_success "ec2-ip-info.txt criado"

# JSON
print_info "Criando ec2-ip-info.json..."
cat > ec2-ip-info.json << EOF
{
  "instance": {
    "instance_id": "$INSTANCE_ID",
    "instance_name": "$INSTANCE_NAME",
    "instance_type": "$INSTANCE_TYPE",
    "state": "$STATE",
    "region": "$REGION",
    "availability_zone": "$AZ"
  },
  "network": {
    "public_ip": "$PUBLIC_IP",
    "private_ip": "$PRIVATE_IP",
    "public_dns": "$PUBLIC_DNS",
    "vpc_id": "$VPC_ID",
    "subnet_id": "$SUBNET_ID",
    "security_groups": "$SG_NAMES"
  },
  "access": {
    "ssh_command": "ssh -i marabet-key.pem ubuntu@$PUBLIC_IP",
    "http_url": "http://$PUBLIC_IP",
    "https_url": "https://$PUBLIC_IP",
    "health_check": "http://$PUBLIC_IP/health"
  },
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

print_success "ec2-ip-info.json criado"

# Exportar variáveis
print_info "Criando export-ec2-vars.sh..."
cat > export-ec2-vars.sh << EOF
#!/bin/bash
# MaraBet AI - Exportar variáveis EC2

export EC2_INSTANCE_ID="$INSTANCE_ID"
export EC2_PUBLIC_IP="$PUBLIC_IP"
export EC2_PRIVATE_IP="$PRIVATE_IP"
export EC2_PUBLIC_DNS="$PUBLIC_DNS"
export EC2_REGION="$REGION"
export EC2_SSH="ssh -i marabet-key.pem ubuntu@$PUBLIC_IP"

echo "✅ Variáveis EC2 exportadas!"
echo ""
echo "Usar:"
echo "  source export-ec2-vars.sh"
echo "  echo \$EC2_PUBLIC_IP"
echo "  \$EC2_SSH"
EOF

chmod +x export-ec2-vars.sh
print_success "export-ec2-vars.sh criado"

# Script de conexão rápida
print_info "Atualizando ssh-connect.sh..."
cat > ssh-connect.sh << EOF
#!/bin/bash
echo "🔐 Conectando ao MaraBet EC2..."
echo "Instance ID: $INSTANCE_ID"
echo "IP Público: $PUBLIC_IP"
echo ""

if [ ! -f "marabet-key.pem" ]; then
    echo "❌ marabet-key.pem não encontrado!"
    exit 1
fi

chmod 400 marabet-key.pem
ssh -i marabet-key.pem ubuntu@$PUBLIC_IP
EOF

chmod +x ssh-connect.sh
print_success "ssh-connect.sh atualizado"

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ IP PÚBLICO OBTIDO COM SUCESSO!"

echo ""
echo -e "${CYAN}EC2 Instance:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Instance ID:       $INSTANCE_ID"
echo "  Nome:              $INSTANCE_NAME"
echo "  Tipo:              $INSTANCE_TYPE"
echo "  Estado:            ${GREEN}$STATE${NC}"
echo ""
echo "  IP Público:        ${GREEN}$PUBLIC_IP${NC}"
echo "  IP Privado:        $PRIVATE_IP"
echo "  DNS Público:       $PUBLIC_DNS"
echo ""
echo "  VPC:               $VPC_ID"
echo "  Subnet:            $SUBNET_ID"
echo "  Security Groups:   $SG_NAMES"
echo "  Availability Zone: $AZ"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}Acesso SSH:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ${GREEN}./ssh-connect.sh${NC}"
echo ""
echo "  ${YELLOW}OU${NC}"
echo ""
echo "  ${GREEN}ssh -i marabet-key.pem ubuntu@$PUBLIC_IP${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}URLs de Acesso:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  HTTP:              ${BLUE}http://$PUBLIC_IP${NC}"
echo "  HTTPS:             ${BLUE}https://$PUBLIC_IP${NC}"
echo "  Health Check:      ${BLUE}http://$PUBLIC_IP/health${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}⚠️  IMPORTANTE - API-Football Whitelist:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Adicione este IP ao whitelist da API-Football:"
echo ""
echo "  ${YELLOW}IP: $PUBLIC_IP${NC}"
echo ""
echo "  🔗 Dashboard: ${BLUE}https://dashboard.api-football.com/${NC}"
echo "  📂 Soccer > Settings > IP Whitelist"
echo "  ➕ Adicionar IP: $PUBLIC_IP"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Arquivos Criados:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📄 ec2-ip-info.txt       - Informações completas (texto)"
echo "  📄 ec2-ip-info.json      - Informações em JSON"
echo "  📄 export-ec2-vars.sh    - Exportar variáveis"
echo "  📄 ssh-connect.sh        - Script de conexão SSH"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Testar conectividade HTTP
if [ "$PUBLIC_IP" != "N/A" ] && [ ! -z "$PUBLIC_IP" ]; then
    print_info "Testando conectividade HTTP..."
    
    if curl -s --connect-timeout 5 http://$PUBLIC_IP > /dev/null 2>&1; then
        print_success "HTTP respondendo!"
    else
        print_warning "HTTP não respondendo ainda (normal se aplicação não foi deployada)"
    fi
fi

echo ""
print_header "✅ CONCLUÍDO!"

# Salvar no histórico
cat >> ec2-history.log << EOF
[$(date)] IP obtido: Instance $INSTANCE_ID | IP Público: $PUBLIC_IP | Estado: $STATE
EOF

echo ""

