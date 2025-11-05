#!/bin/bash

################################################################################
# MARABET AI - CRIAR HOSTED ZONE ROUTE 53
# Configuração completa de DNS para marabet.com
################################################################################

set -e

# Cores
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

print_header() {
    echo ""
    echo -e "${CYAN}========================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================================================${NC}"
    echo ""
}

print_header "🌐 MARABET AI - CRIAR HOSTED ZONE"

# Configurações
DOMAIN="marabet.com"
CALLER_REF=$(date +%s)
COMMENT="MaraBet AI production DNS"

print_info "Domínio: $DOMAIN"
print_info "Caller Reference: $CALLER_REF"
echo ""

################################################################################
# 1. VERIFICAR SE JÁ EXISTE
################################################################################

print_header "1. VERIFICANDO HOSTED ZONE EXISTENTE"

print_info "Consultando Hosted Zones..."

EXISTING_ZONE=$(aws route53 list-hosted-zones \
    --query "HostedZones[?Name=='${DOMAIN}.'].Id" \
    --output text 2>&1)

if [ ! -z "$EXISTING_ZONE" ] && [ "$EXISTING_ZONE" != "None" ]; then
    ZONE_ID=$(echo "$EXISTING_ZONE" | cut -d'/' -f3)
    print_warning "Hosted Zone já existe!"
    print_info "Zone ID: $ZONE_ID"
    
    USE_EXISTING="y"
    read -p "Usar Hosted Zone existente? (y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Operação cancelada"
        exit 0
    fi
else
    print_info "Nenhuma Hosted Zone encontrada para $DOMAIN"
    USE_EXISTING="n"
fi

################################################################################
# 2. CRIAR HOSTED ZONE
################################################################################

if [ "$USE_EXISTING" == "n" ]; then
    print_header "2. CRIANDO HOSTED ZONE"
    
    print_info "Criando Hosted Zone para $DOMAIN..."
    
    RESULT=$(aws route53 create-hosted-zone \
        --name $DOMAIN \
        --caller-reference $CALLER_REF \
        --hosted-zone-config Comment="$COMMENT" 2>&1)
    
    if [ $? -ne 0 ]; then
        echo "$RESULT"
        exit 1
    fi
    
    ZONE_ID=$(echo "$RESULT" | jq -r '.HostedZone.Id' | cut -d'/' -f3)
    
    print_success "Hosted Zone criada!"
    print_success "Zone ID: $ZONE_ID"
else
    print_header "2. USANDO HOSTED ZONE EXISTENTE"
    print_info "Zone ID: $ZONE_ID"
fi

################################################################################
# 3. OBTER NAMESERVERS
################################################################################

print_header "3. OBTENDO NAMESERVERS"

print_info "Consultando nameservers..."

NAMESERVERS=$(aws route53 get-hosted-zone \
    --id $ZONE_ID \
    --query 'DelegationSet.NameServers' \
    --output text)

print_success "Nameservers obtidos:"
echo ""
echo "$NAMESERVERS" | tr '\t' '\n' | while read ns; do
    echo "  • $ns"
done
echo ""

################################################################################
# 4. SALVAR INFORMAÇÕES
################################################################################

print_header "4. SALVANDO INFORMAÇÕES"

# Arquivo de texto
print_info "Criando hosted-zone-info.txt..."
cat > hosted-zone-info.txt << EOF
MaraBet AI - Route 53 Hosted Zone
==================================

Domínio:              $DOMAIN
Hosted Zone ID:       $ZONE_ID
Caller Reference:     $CALLER_REF
Comment:              $COMMENT

Nameservers:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

$NAMESERVERS

⚠️  CONFIGURAR NO REGISTRADOR DO DOMÍNIO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Se o domínio está em GoDaddy, Namecheap, etc.:
1. Acessar painel do registrador
2. Encontrar "Nameservers" ou "DNS Settings"
3. Alterar para "Custom Nameservers"
4. Adicionar os nameservers acima
5. Salvar
6. Aguardar propagação (24-48h)

Custo:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hosted Zone:          \$0.50/mês
Queries (primeiros 1M): Incluído
TOTAL:                ~\$6/ano

Criado em:            $(date)
EOF

print_success "hosted-zone-info.txt criado"

# JSON
print_info "Criando hosted-zone-info.json..."
NS_ARRAY=$(echo "$NAMESERVERS" | tr '\t' '\n' | jq -R . | jq -s .)

cat > hosted-zone-info.json << EOF
{
  "hosted_zone": {
    "domain": "$DOMAIN",
    "zone_id": "$ZONE_ID",
    "caller_reference": "$CALLER_REF",
    "comment": "$COMMENT",
    "nameservers": $NS_ARRAY
  },
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

print_success "hosted-zone-info.json criado"

################################################################################
# 5. CRIAR REGISTROS INICIAIS
################################################################################

print_header "5. CONFIGURANDO REGISTROS INICIAIS"

print_info "Você quer criar registros DNS agora? (requer Elastic IP)"
read -p "Criar registro A para marabet.com? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Tentar obter Elastic IP
    if [ -f "elastic-ip-info.txt" ]; then
        ELASTIC_IP=$(grep "Elastic IP:" elastic-ip-info.txt | awk '{print $3}')
        print_info "Elastic IP encontrado: $ELASTIC_IP"
    else
        read -p "Digite o Elastic IP da EC2: " ELASTIC_IP
    fi
    
    if [ ! -z "$ELASTIC_IP" ]; then
        print_info "Criando registro A para $DOMAIN..."
        
        aws route53 change-resource-record-sets \
            --hosted-zone-id $ZONE_ID \
            --change-batch '{
                "Changes": [{
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": "'$DOMAIN'",
                        "Type": "A",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": "'$ELASTIC_IP'"}]
                    }
                }]
            }' 2>/dev/null && print_success "Registro A criado: $DOMAIN → $ELASTIC_IP" || print_warning "Registro A pode já existir"
        
        # www
        print_info "Criando registro A para www.$DOMAIN..."
        aws route53 change-resource-record-sets \
            --hosted-zone-id $ZONE_ID \
            --change-batch '{
                "Changes": [{
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": "www.'$DOMAIN'",
                        "Type": "A",
                        "TTL": 300,
                        "ResourceRecords": [{"Value": "'$ELASTIC_IP'"}]
                    }
                }]
            }' 2>/dev/null && print_success "Registro A criado: www.$DOMAIN → $ELASTIC_IP" || print_warning "Registro pode já existir"
    fi
fi

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ HOSTED ZONE CONFIGURADA!"

echo ""
echo -e "${CYAN}Route 53 Hosted Zone:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Domínio:           ${GREEN}$DOMAIN${NC}"
echo "  Hosted Zone ID:    $ZONE_ID"
echo ""
echo "  Nameservers:"
echo "$NAMESERVERS" | tr '\t' '\n' | while read ns; do
    echo "    • $ns"
done
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}⚠️  AÇÃO NECESSÁRIA:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Configure os nameservers no registrador de $DOMAIN"
echo "  (GoDaddy, Namecheap, etc.)"
echo ""
echo "  Nameservers para configurar:"
echo "$NAMESERVERS" | tr '\t' '\n' | while read ns; do
    echo "    $ns"
done
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Configurar nameservers no registrador"
echo "  2. Aguardar propagação (24-48h)"
echo "  3. Criar Elastic IP: ./alocar_elastic_ip.sh"
echo "  4. Criar registro A: $DOMAIN → Elastic IP"
echo "  5. Solicitar SSL Certificate (ACM)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_success "Informações salvas em: hosted-zone-info.txt"

echo ""
print_header "✅ CONCLUÍDO!"
echo ""

