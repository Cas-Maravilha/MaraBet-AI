#!/bin/bash

################################################################################
# MARABET AI - REGISTRAR DOMÍNIO marabet.com VIA AWS
# Registro automático com Route 53 Domains
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

print_header "🌐 MARABET AI - REGISTRAR DOMÍNIO"

# Configurações
DOMAIN="marabet.com"
YEARS=1
REGION="us-east-1"  # Route 53 Domains sempre usa us-east-1

# Dados de contato
FIRST_NAME="Claudio"
LAST_NAME="dos Santos"
EMAIL="admin@marabet.com"
PHONE="+244.932027393"
ADDRESS="Rua da Missao, Bairro Alvalade"
CITY="Luanda"
COUNTRY="AO"
ZIP="00000"

print_info "Domínio: $DOMAIN"
print_info "Duração: $YEARS ano(s)"
print_info "Email: $EMAIL"
print_warning "Região: $REGION (obrigatório para Route 53 Domains)"
echo ""

################################################################################
# 1. VERIFICAR DISPONIBILIDADE
################################################################################

print_header "1. VERIFICANDO DISPONIBILIDADE"

print_info "Consultando disponibilidade de $DOMAIN..."

AVAILABILITY=$(aws route53domains check-domain-availability \
    --domain-name $DOMAIN \
    --region $REGION 2>&1)

if [ $? -ne 0 ]; then
    echo "$AVAILABILITY"
    exit 1
fi

STATUS=$(echo "$AVAILABILITY" | jq -r '.Availability')

if [ "$STATUS" == "AVAILABLE" ]; then
    print_success "Domínio disponível para registro!"
elif [ "$STATUS" == "UNAVAILABLE" ]; then
    print_warning "Domínio NÃO disponível (já registrado)"
    echo ""
    print_info "Opções:"
    echo "  1. Transferir domínio para AWS (se você é dono)"
    echo "  2. Escolher outro domínio"
    exit 1
elif [ "$STATUS" == "DONT_KNOW" ]; then
    print_warning "Status desconhecido"
    print_info "O domínio pode estar em período de redenção ou reserved"
else
    print_warning "Status: $STATUS"
fi

################################################################################
# 2. VERIFICAR PREÇO
################################################################################

print_header "2. CONSULTANDO PREÇO"

print_info "Obtendo preço de registro..."

PRICE_INFO=$(aws route53domains get-domain-suggestions \
    --domain-name $DOMAIN \
    --suggestion-count 1 \
    --only-available \
    --region $REGION 2>/dev/null || echo "{}")

# Preço típico .com
PRICE="$13.00"

echo ""
print_info "Preço estimado: \$$PRICE USD/ano"
echo ""

################################################################################
# 3. PREPARAR CONTATOS
################################################################################

print_header "3. PREPARANDO INFORMAÇÕES DE CONTATO"

print_info "Criando arquivo de contatos..."

# Criar arquivo JSON com contatos
cat > domain-contacts.json << EOF
{
  "FirstName": "$FIRST_NAME",
  "LastName": "$LAST_NAME",
  "ContactType": "PERSON",
  "AddressLine1": "$ADDRESS",
  "City": "$CITY",
  "CountryCode": "$COUNTRY",
  "ZipCode": "$ZIP",
  "PhoneNumber": "$PHONE",
  "Email": "$EMAIL"
}
EOF

print_success "domain-contacts.json criado"

echo ""
print_info "Dados de contato:"
echo "  Nome: $FIRST_NAME $LAST_NAME"
echo "  Email: $EMAIL"
echo "  Telefone: $PHONE"
echo "  Cidade: $CITY, $COUNTRY"

################################################################################
# 4. REGISTRAR DOMÍNIO
################################################################################

print_header "4. REGISTRANDO DOMÍNIO"

print_warning "Esta operação irá COBRAR ~\$13 no seu cartão AWS!"
echo ""

read -p "Continuar com o registro de $DOMAIN? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    print_warning "Registro cancelado"
    exit 0
fi

echo ""
print_info "Registrando $DOMAIN..."
print_warning "Isso pode levar alguns segundos..."

REGISTRATION=$(aws route53domains register-domain \
    --domain-name $DOMAIN \
    --duration-in-years $YEARS \
    --auto-renew \
    --admin-contact file://domain-contacts.json \
    --registrant-contact file://domain-contacts.json \
    --tech-contact file://domain-contacts.json \
    --privacy-protect-admin-contact \
    --privacy-protect-registrant-contact \
    --privacy-protect-tech-contact \
    --region $REGION 2>&1)

if [ $? -ne 0 ]; then
    echo ""
    print_warning "Erro ao registrar domínio:"
    echo "$REGISTRATION"
    echo ""
    print_info "Possíveis causas:"
    echo "  • Domínio não disponível"
    echo "  • Dados de contato inválidos"
    echo "  • Cartão de crédito inválido"
    echo "  • Email inválido"
    exit 1
fi

OPERATION_ID=$(echo "$REGISTRATION" | jq -r '.OperationId')

print_success "Registro iniciado!"
print_success "Operation ID: $OPERATION_ID"

################################################################################
# 5. SALVAR INFORMAÇÕES
################################################################################

print_header "5. SALVANDO INFORMAÇÕES"

cat > domain-registration-info.txt << EOF
MaraBet AI - Registro de Domínio
=================================

Domínio:              $DOMAIN
Status:               Registrando...
Operation ID:         $OPERATION_ID
Duração:              $YEARS ano(s)
Auto-Renew:           Yes
Privacy Protection:   Yes

Contato:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Nome:                 $FIRST_NAME $LAST_NAME
Email:                $EMAIL
Telefone:             $PHONE
Endereço:             $ADDRESS
Cidade:               $CITY
País:                 $COUNTRY

Custo:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Registro:             ~\$13.00 USD
Hosted Zone:          \$0.50/mês
TOTAL 1º ano:         ~\$19.00 USD

Próximos Passos:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✅ Aguardar email de verificação
   Para: $EMAIL
   Assunto: "Verify email address for domain registration"
   Ação: Clicar no link (prazo: 15 dias)

2. ⏳ Aguardar registro completar (até 3 dias)
   Verificar: aws route53domains get-operation-detail --operation-id $OPERATION_ID

3. 🌐 Hosted Zone criada automaticamente
   Acessar: AWS Console > Route 53 > Hosted Zones

4. 📍 Criar registro A apontando para Elastic IP

5. 🔒 Solicitar SSL Certificate (ACM)

Comandos:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Verificar status:
  aws route53domains get-operation-detail --operation-id $OPERATION_ID --region $REGION

Listar domínios:
  aws route53domains list-domains --region $REGION

Ver detalhes:
  aws route53domains get-domain-detail --domain-name $DOMAIN --region $REGION

Registrado em:        $(date)
EOF

print_success "domain-registration-info.txt criado"

################################################################################
# RESUMO
################################################################################

print_header "✅ REGISTRO INICIADO COM SUCESSO!"

echo ""
echo -e "${CYAN}Domínio:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Nome:              ${GREEN}$DOMAIN${NC}"
echo "  Operation ID:      $OPERATION_ID"
echo "  Status:            Registrando... (pode levar até 3 dias)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}⚠️  AÇÃO IMEDIATA NECESSÁRIA:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Verificar email: ${YELLOW}$EMAIL${NC}"
echo "  2. Procurar email da AWS"
echo "  3. Clicar no link de verificação"
echo "  4. ${GREEN}PRAZO: 15 dias!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Verificar status da operação:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ${GREEN}aws route53domains get-operation-detail \\${NC}"
echo "    ${GREEN}--operation-id $OPERATION_ID \\${NC}"
echo "    ${GREEN}--region $REGION${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_success "Informações salvas em: domain-registration-info.txt"

echo ""
print_header "✅ CONCLUÍDO!"

echo ""
print_info "Próximos passos:"
echo "  1. ✅ Verificar email (URGENTE)"
echo "  2. ⏳ Aguardar registro completar"
echo "  3. 🌐 Configurar registros DNS"
echo "  4. 🔒 Solicitar SSL"
echo ""

