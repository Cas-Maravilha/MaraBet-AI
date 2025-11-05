#!/bin/bash

################################################################################
# MARABET AI - SOLICITAR SSL CERTIFICATE
# Certificado SSL gratuito via AWS Certificate Manager (ACM)
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

print_header "🔒 MARABET AI - SOLICITAR SSL CERTIFICATE"

# Configurações
DOMAIN="marabet.com"
REGION="eu-west-1"

print_info "Domínio: $DOMAIN"
print_info "Região: $REGION"
print_warning "ACM certificates DEVEM ser solicitados na região onde serão usados"
echo ""

################################################################################
# 1. SOLICITAR CERTIFICADO
################################################################################

print_header "1. SOLICITANDO CERTIFICADO SSL"

print_info "Solicitando certificado para $DOMAIN e subdomínios..."

CERT_ARN=$(aws acm request-certificate \
    --domain-name $DOMAIN \
    --subject-alternative-names www.$DOMAIN api.$DOMAIN \
    --validation-method DNS \
    --region $REGION \
    --query 'CertificateArn' \
    --output text 2>&1)

if [ $? -ne 0 ]; then
    echo "$CERT_ARN"
    exit 1
fi

print_success "Certificado solicitado!"
print_success "Certificate ARN: $CERT_ARN"

################################################################################
# 2. OBTER REGISTROS DE VALIDAÇÃO
################################################################################

print_header "2. OBTENDO REGISTROS DE VALIDAÇÃO DNS"

print_info "Aguardando AWS gerar registros de validação..."
sleep 5

CERT_INFO=$(aws acm describe-certificate \
    --certificate-arn $CERT_ARN \
    --region $REGION)

# Extrair CNAME de validação
VALIDATION_RECORDS=$(echo "$CERT_INFO" | jq -r '.Certificate.DomainValidationOptions[]')

print_success "Registros de validação obtidos"

################################################################################
# 3. CRIAR REGISTROS DE VALIDAÇÃO NO ROUTE 53
################################################################################

print_header "3. CRIANDO REGISTROS DE VALIDAÇÃO"

print_info "Adicionando registros CNAME ao Route 53..."

# Obter Hosted Zone ID
ZONE_ID=$(aws route53 list-hosted-zones \
    --query "HostedZones[?Name=='${DOMAIN}.'].Id" \
    --output text | cut -d'/' -f3)

if [ -z "$ZONE_ID" ]; then
    print_error "Hosted Zone não encontrada!"
    exit 1
fi

# Criar registros de validação
echo "$CERT_INFO" | jq -r '.Certificate.DomainValidationOptions[] | 
    .ResourceRecord | 
    "{\"Action\":\"UPSERT\",\"ResourceRecordSet\":{\"Name\":\"\(.Name)\",\"Type\":\"\(.Type)\",\"TTL\":300,\"ResourceRecords\":[{\"Value\":\"\(.Value)\"}]}}"' | \
while read record; do
    if [ ! -z "$record" ]; then
        aws route53 change-resource-record-sets \
            --hosted-zone-id $ZONE_ID \
            --change-batch "{\"Changes\":[$record]}" 2>/dev/null && \
            print_success "Registro de validação criado" || \
            print_warning "Registro pode já existir"
    fi
done

################################################################################
# 4. AGUARDAR VALIDAÇÃO
################################################################################

print_header "4. AGUARDANDO VALIDAÇÃO"

print_info "Aguardando AWS validar certificado..."
print_warning "Isso pode levar 5-10 minutos"
echo ""

aws acm wait certificate-validated \
    --certificate-arn $CERT_ARN \
    --region $REGION

print_success "Certificado validado e emitido!"

################################################################################
# 5. VERIFICAR CERTIFICADO
################################################################################

print_header "5. VERIFICANDO CERTIFICADO"

CERT_STATUS=$(aws acm describe-certificate \
    --certificate-arn $CERT_ARN \
    --region $REGION \
    --query 'Certificate.Status' \
    --output text)

CERT_DOMAINS=$(aws acm describe-certificate \
    --certificate-arn $CERT_ARN \
    --region $REGION \
    --query 'Certificate.SubjectAlternativeNames' \
    --output text)

print_info "Status: $CERT_STATUS"
print_info "Domínios cobertos:"
echo "$CERT_DOMAINS" | tr '\t' '\n' | while read domain; do
    echo "  • $domain"
done

################################################################################
# 6. SALVAR INFORMAÇÕES
################################################################################

print_header "6. SALVANDO INFORMAÇÕES"

cat > ssl-certificate-info.txt << EOF
MaraBet AI - SSL Certificate
=============================

Domain:               $DOMAIN
Certificate ARN:      $CERT_ARN
Status:               $CERT_STATUS
Region:               $REGION
Validation Method:    DNS

Domains Covered:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

$(echo "$CERT_DOMAINS" | tr '\t' '\n' | while read domain; do echo "  • $domain"; done)

Usage:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Application Load Balancer:
  aws elbv2 create-listener \\
    --load-balancer-arn <ALB_ARN> \\
    --protocol HTTPS \\
    --port 443 \\
    --certificates CertificateArn=$CERT_ARN \\
    --default-actions Type=forward,TargetGroupArn=<TG_ARN>

CloudFront:
  Use Certificate ARN no CloudFront Distribution

API Gateway:
  Custom Domain Names com Certificate ARN

Renewal:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AWS Certificate Manager renova automaticamente!
✅ Renovação automática 60 dias antes da expiração
✅ Zero manutenção necessária

Criado em:            $(date)
EOF

print_success "ssl-certificate-info.txt criado"

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ SSL CERTIFICATE EMITIDO!"

echo ""
echo -e "${CYAN}SSL Certificate:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ARN:               ${GREEN}$CERT_ARN${NC}"
echo "  Status:            ${GREEN}$CERT_STATUS${NC}"
echo "  Região:            $REGION"
echo ""
echo "  Domínios:"
echo "$CERT_DOMAINS" | tr '\t' '\n' | while read domain; do
    echo "    • $domain"
done
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}Recursos que Podem Usar Este Certificado:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ✅ Application Load Balancer (ALB)"
echo "  ✅ CloudFront Distribution"
echo "  ✅ API Gateway Custom Domain"
echo "  ✅ Elastic Beanstalk"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Configurar HTTPS no Nginx (EC2):"
echo "     Copiar certificado ou usar ALB"
echo ""
echo "  2. OU criar Application Load Balancer:"
echo "     Terminar SSL no ALB (recomendado)"
echo ""
echo "  3. Testar HTTPS:"
echo "     ${GREEN}curl https://$DOMAIN${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_info "Informações salvas em: ssl-certificate-info.txt"

echo ""
print_header "✅ CONCLUÍDO!"
echo ""

