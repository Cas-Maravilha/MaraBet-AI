#!/bin/bash

################################################################################
# MARABET AI - ALOCAR E ASSOCIAR ELASTIC IP
# IP fixo permanente para EC2
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

print_header "📍 MARABET AI - ALOCAR ELASTIC IP"

# Configurações
REGION="eu-west-1"
INSTANCE_NAME="marabet-ec2"

# Permitir passar Instance ID como parâmetro
if [ ! -z "$1" ]; then
    INSTANCE_ID=$1
    print_info "Instance ID fornecido: $INSTANCE_ID"
else
    INSTANCE_ID=""
fi

################################################################################
# 1. ALOCAR ELASTIC IP
################################################################################

print_header "1. ALOCANDO ELASTIC IP"

print_info "Solicitando novo Elastic IP..."

ALLOCATION=$(aws ec2 allocate-address \
    --domain vpc \
    --region $REGION 2>&1)

if [ $? -ne 0 ]; then
    print_error "Falha ao alocar Elastic IP!"
    echo "$ALLOCATION"
    
    if echo "$ALLOCATION" | grep -q "AddressLimitExceeded"; then
        print_warning "Limite de Elastic IPs atingido (padrão: 5)"
        print_info "Solicite aumento: AWS Console > Service Quotas > EC2 > Elastic IPs"
    fi
    
    exit 1
fi

ELASTIC_IP=$(echo "$ALLOCATION" | jq -r '.PublicIp')
ALLOCATION_ID=$(echo "$ALLOCATION" | jq -r '.AllocationId')

print_success "Elastic IP alocado: $ELASTIC_IP"
print_success "Allocation ID: $ALLOCATION_ID"

################################################################################
# 2. ADICIONAR TAGS
################################################################################

print_header "2. ADICIONANDO TAGS"

print_info "Adicionando tags descritivas..."

aws ec2 create-tags \
    --resources $ALLOCATION_ID \
    --tags \
      Key=Name,Value=marabet-elastic-ip \
      Key=Project,Value=MaraBet \
      Key=Environment,Value=production \
      Key=CreatedBy,Value=MaraBet-Deploy-Script \
    --region $REGION

print_success "Tags adicionadas"

################################################################################
# 3. ENCONTRAR EC2 INSTANCE
################################################################################

print_header "3. ENCONTRANDO EC2 INSTANCE"

if [ -z "$INSTANCE_ID" ]; then
    print_info "Buscando instância com nome: $INSTANCE_NAME..."
    
    INSTANCE_ID=$(aws ec2 describe-instances \
        --filters "Name=tag:Name,Values=$INSTANCE_NAME" "Name=instance-state-name,Values=running,pending" \
        --region $REGION \
        --query 'Reservations[0].Instances[0].InstanceId' \
        --output text 2>&1)
    
    if [ -z "$INSTANCE_ID" ] || [ "$INSTANCE_ID" == "None" ]; then
        print_warning "Nenhuma EC2 running encontrada"
        print_info "Elastic IP alocado mas não associado"
        print_info "Associe manualmente após criar/iniciar EC2:"
        echo ""
        echo "  aws ec2 associate-address \\"
        echo "    --instance-id <INSTANCE_ID> \\"
        echo "    --allocation-id $ALLOCATION_ID \\"
        echo "    --region $REGION"
        echo ""
        
        # Salvar para uso futuro
        cat > elastic-ip-pending.txt << EOF
MaraBet AI - Elastic IP (Pendente Associação)
==============================================

Elastic IP:        $ELASTIC_IP
Allocation ID:     $ALLOCATION_ID
Region:            $REGION
Status:            Alocado, não associado

Para associar a uma EC2:
  aws ec2 associate-address \\
    --instance-id <INSTANCE_ID> \\
    --allocation-id $ALLOCATION_ID \\
    --region $REGION

Criado em:         $(date)
EOF
        
        print_success "Informações salvas em: elastic-ip-pending.txt"
        exit 0
    fi
    
    print_success "EC2 Instance encontrada: $INSTANCE_ID"
fi

################################################################################
# 4. ASSOCIAR À EC2
################################################################################

print_header "4. ASSOCIANDO ELASTIC IP À EC2"

print_info "Associando $ELASTIC_IP à instância $INSTANCE_ID..."

ASSOCIATION=$(aws ec2 associate-address \
    --instance-id $INSTANCE_ID \
    --allocation-id $ALLOCATION_ID \
    --region $REGION 2>&1)

if [ $? -ne 0 ]; then
    print_error "Falha ao associar Elastic IP!"
    echo "$ASSOCIATION"
    exit 1
fi

ASSOCIATION_ID=$(echo "$ASSOCIATION" | jq -r '.AssociationId')

print_success "Elastic IP associado!"
print_success "Association ID: $ASSOCIATION_ID"

################################################################################
# 5. VERIFICAR
################################################################################

print_header "5. VERIFICANDO ASSOCIAÇÃO"

print_info "Consultando status..."

# Verificar IP da EC2
EC2_PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

if [ "$EC2_PUBLIC_IP" == "$ELASTIC_IP" ]; then
    print_success "Elastic IP corretamente associado à EC2!"
else
    print_warning "IP público da EC2 ($EC2_PUBLIC_IP) diferente do Elastic IP ($ELASTIC_IP)"
fi

# Verificar associação
ADDRESS_INFO=$(aws ec2 describe-addresses \
    --allocation-ids $ALLOCATION_ID \
    --region $REGION)

ASSOCIATED_INSTANCE=$(echo "$ADDRESS_INFO" | jq -r '.Addresses[0].InstanceId')

if [ "$ASSOCIATED_INSTANCE" == "$INSTANCE_ID" ]; then
    print_success "Associação verificada!"
else
    print_warning "Associação inconsistente"
fi

################################################################################
# 6. SALVAR INFORMAÇÕES
################################################################################

print_header "6. SALVANDO INFORMAÇÕES"

print_info "Criando elastic-ip-info.txt..."

# Obter nome da instância
INSTANCE_NAME=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].Tags[?Key==`Name`].Value|[0]' \
    --output text)

cat > elastic-ip-info.txt << EOF
MaraBet AI - Elastic IP
=======================

Elastic IP Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Elastic IP:        $ELASTIC_IP
Allocation ID:     $ALLOCATION_ID
Association ID:    $ASSOCIATION_ID
Region:            $REGION

EC2 Instance:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Instance ID:       $INSTANCE_ID
Instance Name:     $INSTANCE_NAME
Public IP:         $EC2_PUBLIC_IP

Access:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SSH Command:       ssh -i marabet-key.pem ubuntu@$ELASTIC_IP
HTTP URL:          http://$ELASTIC_IP
HTTPS URL:         https://$ELASTIC_IP
Health Check:      http://$ELASTIC_IP/health

Important Actions:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  Adicionar à API-Football Whitelist:
    IP: $ELASTIC_IP
    Dashboard: https://dashboard.api-football.com/
    Soccer > Settings > IP Whitelist

⚠️  Configurar no Route 53 (quando criar):
    Type: A
    Name: marabet.ao
    Value: $ELASTIC_IP
    TTL: 300

Benefits:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ IP Fixo Permanente
✅ Sobrevive a reinicializações EC2
✅ Grátis (enquanto associado)
✅ Pode ser transferido entre EC2s
✅ Facilita configuração DNS

Commands Reference:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Desassociar:
  aws ec2 disassociate-address \\
    --association-id $ASSOCIATION_ID \\
    --region $REGION

Reassociar a outra EC2:
  aws ec2 associate-address \\
    --instance-id <NOVA_INSTANCE_ID> \\
    --allocation-id $ALLOCATION_ID \\
    --region $REGION

Liberar (deletar):
  aws ec2 release-address \\
    --allocation-id $ALLOCATION_ID \\
    --region $REGION

Created:           $(date)
EOF

print_success "elastic-ip-info.txt criado"

# JSON
print_info "Criando elastic-ip-info.json..."
cat > elastic-ip-info.json << EOF
{
  "elastic_ip": {
    "public_ip": "$ELASTIC_IP",
    "allocation_id": "$ALLOCATION_ID",
    "association_id": "$ASSOCIATION_ID",
    "region": "$REGION"
  },
  "ec2_instance": {
    "instance_id": "$INSTANCE_ID",
    "instance_name": "$INSTANCE_NAME",
    "public_ip": "$EC2_PUBLIC_IP"
  },
  "access": {
    "ssh": "ssh -i marabet-key.pem ubuntu@$ELASTIC_IP",
    "http": "http://$ELASTIC_IP",
    "https": "https://$ELASTIC_IP"
  },
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

print_success "elastic-ip-info.json criado"

# Atualizar .env.ec2
if [ -f ".env.ec2" ]; then
    print_info "Atualizando .env.ec2..."
    echo "" >> .env.ec2
    echo "# Elastic IP" >> .env.ec2
    echo "ELASTIC_IP=$ELASTIC_IP" >> .env.ec2
    echo "ELASTIC_IP_ALLOCATION_ID=$ALLOCATION_ID" >> .env.ec2
    echo "ELASTIC_IP_ASSOCIATION_ID=$ASSOCIATION_ID" >> .env.ec2
    print_success ".env.ec2 atualizado"
fi

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ ELASTIC IP CONFIGURADO COM SUCESSO!"

echo ""
echo -e "${CYAN}Elastic IP:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  IP Fixo:           ${GREEN}$ELASTIC_IP${NC}"
echo "  Allocation ID:     $ALLOCATION_ID"
echo "  Association ID:    $ASSOCIATION_ID"
echo ""
echo "  Associado a:       $INSTANCE_ID ($INSTANCE_NAME)"
echo "  Região:            $REGION"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}Acesso:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  SSH:               ${GREEN}ssh -i marabet-key.pem ubuntu@$ELASTIC_IP${NC}"
echo "  HTTP:              ${BLUE}http://$ELASTIC_IP${NC}"
echo "  HTTPS:             ${BLUE}https://$ELASTIC_IP${NC}"
echo "  Health Check:      ${BLUE}http://$ELASTIC_IP/health${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}⚠️  AÇÕES NECESSÁRIAS:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Adicionar à API-Football Whitelist:"
echo "     ${YELLOW}IP: $ELASTIC_IP${NC}"
echo "     ${BLUE}https://dashboard.api-football.com/${NC}"
echo ""
echo "  2. Configurar no Route 53 (quando criar):"
echo "     ${YELLOW}A Record: marabet.ao → $ELASTIC_IP${NC}"
echo ""
echo "  3. Testar SSH:"
echo "     ${GREEN}ssh -i marabet-key.pem ubuntu@$ELASTIC_IP${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Arquivos Criados:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📄 elastic-ip-info.txt       - Informações completas"
echo "  📄 elastic-ip-info.json      - Configuração JSON"
echo "  📄 .env.ec2                  - Atualizado com Elastic IP"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ BENEFÍCIOS DO ELASTIC IP:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ✅ IP fixo permanente"
echo "  ✅ Sobrevive a reinicializações"
echo "  ✅ Grátis (enquanto associado a EC2 running)"
echo "  ✅ Configuração DNS única"
echo "  ✅ API-Football whitelist permanente"
echo "  ✅ Pode ser transferido entre EC2s"
echo ""

# Salvar no histórico
cat >> elastic-ip-history.log << EOF
[$(date)] Elastic IP alocado: $ELASTIC_IP | Allocation: $ALLOCATION_ID | Instance: $INSTANCE_ID
EOF

print_info "Histórico salvo em: elastic-ip-history.log"

echo ""
print_header "✅ CONCLUÍDO!"

# Criar script de teste rápido
cat > test-elastic-ip.sh << EOF
#!/bin/bash
echo "🧪 Testando Elastic IP: $ELASTIC_IP"
echo ""

echo "1. Ping..."
ping -c 3 $ELASTIC_IP

echo ""
echo "2. SSH Test..."
ssh -i marabet-key.pem -o ConnectTimeout=5 ubuntu@$ELASTIC_IP "echo '✅ SSH funcionando!'" 2>/dev/null || echo "⚠️  SSH ainda não disponível"

echo ""
echo "3. HTTP Test..."
curl -s --connect-timeout 5 http://$ELASTIC_IP > /dev/null 2>&1 && echo "✅ HTTP respondendo" || echo "⚠️  HTTP ainda não disponível"

echo ""
echo "Elastic IP: $ELASTIC_IP está configurado!"
EOF

chmod +x test-elastic-ip.sh
print_success "test-elastic-ip.sh criado"

echo ""

