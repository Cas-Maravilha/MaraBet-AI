#!/bin/bash

################################################################################
# MARABET AI - CONFIGURAR REGISTROS DNS COMPLETOS
# Cria todos os registros DNS necessários para marabet.com
################################################################################

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
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

print_header "🌐 MARABET AI - CONFIGURAR DNS COMPLETO"

# Configurações
DOMAIN="marabet.com"

print_info "Domínio: $DOMAIN"
echo ""

################################################################################
# 1. OBTER HOSTED ZONE ID
################################################################################

print_header "1. OBTENDO HOSTED ZONE ID"

print_info "Buscando Hosted Zone para $DOMAIN..."

ZONE_ID=$(aws route53 list-hosted-zones \
    --query "HostedZones[?Name=='${DOMAIN}.'].Id" \
    --output text | cut -d'/' -f3 2>&1)

if [ -z "$ZONE_ID" ] || [ "$ZONE_ID" == "None" ]; then
    print_error "Hosted Zone não encontrada!"
    echo ""
    print_info "Crie a Hosted Zone primeiro:"
    echo "  ./criar_hosted_zone.sh"
    echo ""
    print_info "Ou via AWS CLI:"
    echo "  aws route53 create-hosted-zone --name $DOMAIN --caller-reference \$(date +%s)"
    exit 1
fi

print_success "Hosted Zone ID: $ZONE_ID"

################################################################################
# 2. OBTER ELASTIC IP
################################################################################

print_header "2. OBTENDO ELASTIC IP"

print_info "Buscando Elastic IP..."

# Tentar obter de arquivo
if [ -f "elastic-ip-info.txt" ]; then
    ELASTIC_IP=$(grep "Elastic IP:" elastic-ip-info.txt | awk '{print $3}')
    print_success "Elastic IP encontrado: $ELASTIC_IP"
elif [ -f "elastic-ip-info.json" ]; then
    ELASTIC_IP=$(jq -r '.elastic_ip.public_ip' elastic-ip-info.json)
    print_success "Elastic IP encontrado: $ELASTIC_IP"
else
    # Tentar obter da EC2
    print_info "Tentando obter IP da EC2..."
    
    ELASTIC_IP=$(aws ec2 describe-addresses \
        --filters "Name=tag:Name,Values=marabet-elastic-ip" \
        --query 'Addresses[0].PublicIp' \
        --output text 2>/dev/null)
    
    if [ -z "$ELASTIC_IP" ] || [ "$ELASTIC_IP" == "None" ]; then
        print_warning "Elastic IP não encontrado automaticamente"
        echo ""
        read -p "Digite o Elastic IP da EC2: " ELASTIC_IP
    else
        print_success "Elastic IP da AWS: $ELASTIC_IP"
    fi
fi

if [ -z "$ELASTIC_IP" ]; then
    print_error "Elastic IP necessário!"
    exit 1
fi

print_info "Usando Elastic IP: $ELASTIC_IP"

################################################################################
# 3. CRIAR ARQUIVO CHANGE-BATCH
################################################################################

print_header "3. PREPARANDO REGISTROS DNS"

print_info "Criando change-batch.json..."

cat > change-batch.json <<EOF
{
  "Comment": "MaraBet AI - Registros DNS iniciais",
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "$DOMAIN",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [
          {"Value": "$ELASTIC_IP"}
        ]
      }
    },
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "www.$DOMAIN",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [
          {"Value": "$ELASTIC_IP"}
        ]
      }
    },
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.$DOMAIN",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [
          {"Value": "$ELASTIC_IP"}
        ]
      }
    }
  ]
}
EOF

print_success "change-batch.json criado"

echo ""
print_info "Registros DNS a criar:"
echo "  • $DOMAIN → $ELASTIC_IP"
echo "  • www.$DOMAIN → $ELASTIC_IP"
echo "  • api.$DOMAIN → $ELASTIC_IP"
echo ""

################################################################################
# 4. APLICAR MUDANÇAS
################################################################################

print_header "4. APLICANDO REGISTROS DNS"

print_info "Aplicando mudanças no Route 53..."

CHANGE_INFO=$(aws route53 change-resource-record-sets \
    --hosted-zone-id $ZONE_ID \
    --change-batch file://change-batch.json 2>&1)

if [ $? -ne 0 ]; then
    print_error "Falha ao aplicar mudanças!"
    echo "$CHANGE_INFO"
    
    if echo "$CHANGE_INFO" | grep -q "already exists"; then
        print_warning "Registros podem já existir"
        print_info "Use UPSERT em vez de CREATE para atualizar"
    fi
    
    exit 1
fi

CHANGE_ID=$(echo "$CHANGE_INFO" | jq -r '.ChangeInfo.Id' | cut -d'/' -f3)
CHANGE_STATUS=$(echo "$CHANGE_INFO" | jq -r '.ChangeInfo.Status')

print_success "Mudanças aplicadas!"
print_success "Change ID: $CHANGE_ID"
print_info "Status: $CHANGE_STATUS"

################################################################################
# 5. AGUARDAR PROPAGAÇÃO
################################################################################

print_header "5. AGUARDANDO PROPAGAÇÃO"

if [ "$CHANGE_STATUS" == "PENDING" ]; then
    print_info "Aguardando mudanças propagarem..."
    
    aws route53 wait resource-record-sets-changed \
        --id $CHANGE_ID
    
    print_success "Mudanças propagadas!"
else
    print_success "Mudanças já sincronizadas!"
fi

################################################################################
# 6. VERIFICAR REGISTROS
################################################################################

print_header "6. VERIFICANDO REGISTROS DNS"

print_info "Listando registros criados..."

aws route53 list-resource-record-sets \
    --hosted-zone-id $ZONE_ID \
    --query "ResourceRecordSets[?Type=='A'].[Name,Type,TTL,ResourceRecords[0].Value]" \
    --output table

################################################################################
# 7. SALVAR INFORMAÇÕES
################################################################################

print_header "7. SALVANDO INFORMAÇÕES"

cat > dns-config-info.txt << EOF
MaraBet AI - Configuração DNS
==============================

Domínio:              $DOMAIN
Hosted Zone ID:       $ZONE_ID
Elastic IP:           $ELASTIC_IP
Change ID:            $CHANGE_ID

Registros DNS Criados:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A Record:
  $DOMAIN → $ELASTIC_IP (TTL: 300s)

A Record:
  www.$DOMAIN → $ELASTIC_IP (TTL: 300s)

A Record:
  api.$DOMAIN → $ELASTIC_IP (TTL: 300s)

URLs Resultantes:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Site Principal:       http://$DOMAIN
WWW:                  http://www.$DOMAIN
API:                  http://api.$DOMAIN

Com HTTPS (após SSL):
  https://$DOMAIN
  https://www.$DOMAIN
  https://api.$DOMAIN

Próximos Passos:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Aguardar propagação DNS (5-30 minutos)
   Testar: dig $DOMAIN
           nslookup $DOMAIN

2. Solicitar SSL Certificate:
   aws acm request-certificate \\
     --domain-name $DOMAIN \\
     --subject-alternative-names www.$DOMAIN api.$DOMAIN \\
     --validation-method DNS \\
     --region eu-west-1

3. Validar SSL via DNS (automático)

4. Configurar ALB com SSL (opcional)

5. Testar:
   curl http://$DOMAIN
   curl https://$DOMAIN (após SSL)

Configurado em:       $(date)
EOF

print_success "dns-config-info.txt criado"

# JSON
cat > dns-config-info.json << EOF
{
  "domain": "$DOMAIN",
  "hosted_zone_id": "$ZONE_ID",
  "elastic_ip": "$ELASTIC_IP",
  "change_id": "$CHANGE_ID",
  "records": [
    {
      "name": "$DOMAIN",
      "type": "A",
      "value": "$ELASTIC_IP",
      "ttl": 300
    },
    {
      "name": "www.$DOMAIN",
      "type": "A",
      "value": "$ELASTIC_IP",
      "ttl": 300
    },
    {
      "name": "api.$DOMAIN",
      "type": "A",
      "value": "$ELASTIC_IP",
      "ttl": 300
    }
  ],
  "urls": {
    "main": "http://$DOMAIN",
    "www": "http://www.$DOMAIN",
    "api": "http://api.$DOMAIN",
    "main_https": "https://$DOMAIN",
    "www_https": "https://www.$DOMAIN",
    "api_https": "https://api.$DOMAIN"
  },
  "configured_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

print_success "dns-config-info.json criado"

################################################################################
# 8. TESTAR DNS
################################################################################

print_header "8. TESTANDO RESOLUÇÃO DNS"

print_info "Testando resolução local..."

if command -v dig &> /dev/null; then
    echo ""
    echo "Resultado de: dig $DOMAIN"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    dig $DOMAIN +short
    echo ""
else
    print_warning "comando 'dig' não disponível"
fi

if command -v nslookup &> /dev/null; then
    echo ""
    echo "Resultado de: nslookup $DOMAIN"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    nslookup $DOMAIN 2>&1 | grep -A 2 "Name:"
    echo ""
fi

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ DNS CONFIGURADO COM SUCESSO!"

echo ""
echo -e "${CYAN}Registros DNS:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ${GREEN}$DOMAIN${NC} → $ELASTIC_IP"
echo "  ${GREEN}www.$DOMAIN${NC} → $ELASTIC_IP"
echo "  ${GREEN}api.$DOMAIN${NC} → $ELASTIC_IP"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}URLs de Acesso:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  HTTP:  ${BLUE}http://$DOMAIN${NC}"
echo "  HTTP:  ${BLUE}http://www.$DOMAIN${NC}"
echo "  API:   ${BLUE}http://api.$DOMAIN${NC}"
echo ""
echo "  ${YELLOW}(HTTPS após configurar SSL)${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}⏱️  PROPAGAÇÃO DNS:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  • Route 53 interno: Imediato (1-2 minutos)"
echo "  • DNS global: 5-30 minutos"
echo "  • Completa: Até 48 horas (raro)"
echo ""
echo "  Verificar: https://dnschecker.org/#A/$DOMAIN"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Aguardar propagação DNS (5-30 min)"
echo "     ${GREEN}dig $DOMAIN${NC}"
echo ""
echo "  2. Testar HTTP:"
echo "     ${GREEN}curl http://$DOMAIN${NC}"
echo ""
echo "  3. Solicitar SSL Certificate:"
echo "     ${GREEN}./solicitar_ssl.sh${NC}"
echo ""
echo "  4. Validar SSL via DNS"
echo ""
echo "  5. Configurar HTTPS na aplicação"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_success "Informações salvas em: dns-config-info.txt"
print_success "JSON salvo em: dns-config-info.json"

echo ""
print_header "✅ CONCLUÍDO!"

# Criar script de teste DNS
cat > test-dns.sh << 'EOF'
#!/bin/bash

DOMAIN="marabet.com"

echo "🧪 Testando DNS para $DOMAIN"
echo "=============================="
echo ""

echo "1. Teste com dig:"
dig $DOMAIN +short
dig www.$DOMAIN +short
dig api.$DOMAIN +short

echo ""
echo "2. Teste com nslookup:"
nslookup $DOMAIN

echo ""
echo "3. Teste com curl:"
curl -I http://$DOMAIN 2>/dev/null | head -n 1 || echo "HTTP ainda não respondendo"

echo ""
echo "4. Verificar propagação global:"
echo "   https://dnschecker.org/#A/$DOMAIN"
EOF

chmod +x test-dns.sh
print_success "test-dns.sh criado"

echo ""

