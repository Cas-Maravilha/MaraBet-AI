#!/bin/bash

################################################################################
# MARABET AI - DEPLOY COMPLETO NA AWS
# Script master que executa todos os passos
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

print_header "🚀 MARABET AI - DEPLOY COMPLETO AWS"

echo "Este script irá:"
echo "  1. Lançar EC2 Instance"
echo "  2. Alocar Elastic IP"
echo "  3. Configurar DNS"
echo "  4. Aguardar propagação"
echo "  5. Configurar SSL"
echo "  6. Deploy aplicação"
echo ""

read -p "Continuar? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    print_warning "Deploy cancelado"
    exit 0
fi

################################################################################
# FASE 1: INFRAESTRUTURA
################################################################################

print_header "FASE 1: INFRAESTRUTURA"

# 1. EC2
if [ -f "ec2-instance-info.txt" ]; then
    print_warning "EC2 parece já existir, pulando..."
else
    print_info "Lançando EC2 Instance..."
    chmod +x lancar_ec2_completo.sh
    ./lancar_ec2_completo.sh
    
    print_success "EC2 criada!"
fi

# 2. Elastic IP
if [ -f "elastic-ip-info.txt" ]; then
    print_warning "Elastic IP parece já existir, pulando..."
    ELASTIC_IP=$(grep "Elastic IP:" elastic-ip-info.txt | awk '{print $3}')
else
    print_info "Alocando Elastic IP..."
    chmod +x alocar_elastic_ip.sh
    ./alocar_elastic_ip.sh
    
    ELASTIC_IP=$(grep "Elastic IP:" elastic-ip-info.txt | awk '{print $3}')
    print_success "Elastic IP: $ELASTIC_IP"
fi

# 3. DNS
print_info "Configurando DNS..."
chmod +x configurar_dns_completo.sh
./configurar_dns_completo.sh

print_success "DNS configurado!"

################################################################################
# FASE 2: AGUARDAR DNS
################################################################################

print_header "FASE 2: AGUARDANDO PROPAGAÇÃO DNS"

print_info "Aguardando DNS propagar (pode levar 5-10 minutos)..."
print_warning "Verificando a cada 30 segundos..."

MAX_ATTEMPTS=20
ATTEMPT=0
DNS_OK=false

while [ $ATTEMPT -lt $MAX_ATTEMPTS ] && [ "$DNS_OK" == "false" ]; do
    ((ATTEMPT++))
    
    DNS_IP=$(dig +short marabet.com | head -n1)
    
    echo -n "Tentativa $ATTEMPT/$MAX_ATTEMPTS: DNS resolve para $DNS_IP... "
    
    if [ "$DNS_IP" == "$ELASTIC_IP" ]; then
        echo "✅"
        DNS_OK=true
    else
        echo "⏳"
        sleep 30
    fi
done

if [ "$DNS_OK" == "true" ]; then
    print_success "DNS propagado!"
else
    print_warning "DNS ainda não propagou completamente"
    print_info "Você pode continuar mesmo assim, mas SSL pode falhar"
    read -p "Continuar? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        exit 1
    fi
fi

################################################################################
# FASE 3: SSH E CONFIGURAÇÃO
################################################################################

print_header "FASE 3: CONFIGURAÇÃO REMOTA"

print_warning "Próximos passos requerem execução manual na EC2"
echo ""
print_info "Comandos para executar:"
echo ""
echo "  # 1. SSH na EC2"
echo "  ./ssh-connect.sh"
echo ""
echo "  # 2. Aguardar User Data completar"
echo "  cat /home/ubuntu/setup-complete.txt"
echo ""
echo "  # 3. Configurar Nginx e SSL"
echo "  sudo ln -s /etc/nginx/sites-available/marabet /etc/nginx/sites-enabled/"
echo "  sudo rm /etc/nginx/sites-enabled/default"
echo "  sudo nginx -t && sudo systemctl restart nginx"
echo ""
echo "  # 4. Obter SSL"
echo "  sudo apt-get install -y certbot python3-certbot-nginx"
echo "  sudo certbot --nginx -d marabet.com -d www.marabet.com --email admin@marabet.com"
echo ""
echo "  # 5. Deploy aplicação"
echo "  sudo su - marabet"
echo "  cd /opt/marabet"
echo "  # Upload código via git/rsync/scp"
echo "  nano .env  # Configurar variáveis"
echo "  docker-compose up -d --build"
echo ""

################################################################################
# RESUMO
################################################################################

print_header "✅ INFRAESTRUTURA CRIADA!"

echo ""
echo "Recursos AWS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ✅ EC2 Instance"
echo "  ✅ Elastic IP: $ELASTIC_IP"
echo "  ✅ DNS: marabet.com → $ELASTIC_IP"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Próximos Passos MANUAIS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. SSH na EC2:"
echo "     ${GREEN}./ssh-connect.sh${NC}"
echo ""
echo "  2. Configurar SSL (na EC2):"
echo "     ${GREEN}chmod +x setup_ssl_ec2.sh && ./setup_ssl_ec2.sh${NC}"
echo ""
echo "  3. Upload código (do PC):"
echo "     Ver: ${BLUE}DEPLOY_APLICACAO_COMPLETO.md${NC}"
echo ""
echo "  4. Deploy app (na EC2):"
echo "     ${GREEN}docker-compose up -d${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Documentação:"
echo "  📖 DEPLOY_MARABET_REFERENCIA_RAPIDA.md"
echo "  📖 DEPLOY_APLICACAO_COMPLETO.md"
echo "  📖 COMANDOS_EC2_COMPLETOS.md"
echo ""

echo "✅ Fase de infraestrutura completa!"
echo ""

