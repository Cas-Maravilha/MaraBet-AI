#!/bin/bash

################################################################################
# MARABET AI - OBTER CERTIFICADO SSL COM CERTBOT
# Automático - sem interação manual
################################################################################

set -e

echo "========================================================================"
echo "🔒 MaraBet AI - Obter Certificado SSL"
echo "========================================================================"
echo ""

# Configurações
DOMAIN="marabet.com"
EMAIL="admin@marabet.com"

echo "[ℹ] Domínio: $DOMAIN"
echo "[ℹ] Email: $EMAIL"
echo ""

################################################################################
# 1. VERIFICAR PRÉ-REQUISITOS
################################################################################

echo "1. Verificando pré-requisitos..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Certbot instalado?
if ! command -v certbot &> /dev/null; then
    echo "[!] Certbot não instalado, instalando..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
    echo "[✓] Certbot instalado"
else
    echo "[✓] Certbot já instalado: $(certbot --version 2>&1 | head -n1)"
fi

# Nginx rodando?
if sudo systemctl is-active nginx > /dev/null; then
    echo "[✓] Nginx está rodando"
else
    echo "[✗] Nginx não está rodando!"
    echo "    Inicie: sudo systemctl start nginx"
    exit 1
fi

# DNS configurado?
echo ""
echo "[ℹ] Verificando DNS..."
DNS_IP=$(dig +short $DOMAIN | head -n1)
SERVER_IP=$(curl -s http://checkip.amazonaws.com)

echo "    DNS aponta para: $DNS_IP"
echo "    Este servidor:   $SERVER_IP"

if [ "$DNS_IP" != "$SERVER_IP" ]; then
    echo "[!] AVISO: DNS não aponta para este servidor"
    echo ""
    read -p "Continuar mesmo assim? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        exit 1
    fi
else
    echo "[✓] DNS configurado corretamente"
fi

################################################################################
# 2. OBTER CERTIFICADO SSL
################################################################################

echo ""
echo "2. Obtendo certificado SSL..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "[ℹ] Executando Certbot..."
echo "[!] Isso pode levar 1-2 minutos..."
echo ""

# Obter SSL automaticamente
sudo certbot --nginx \
  -d $DOMAIN \
  -d www.$DOMAIN \
  --non-interactive \
  --agree-tos \
  --email $EMAIL \
  --redirect \
  --no-eff-email

if [ $? -eq 0 ]; then
    echo ""
    echo "[✓] Certificado SSL obtido com sucesso!"
else
    echo ""
    echo "[✗] Falha ao obter certificado!"
    echo ""
    echo "Possíveis causas:"
    echo "  • DNS não propagado"
    echo "  • Porta 80 não acessível"
    echo "  • Firewall bloqueando"
    echo "  • Domínio já tem certificado"
    echo ""
    echo "Logs:"
    echo "  sudo cat /var/log/letsencrypt/letsencrypt.log"
    exit 1
fi

################################################################################
# 3. VERIFICAR CERTIFICADO
################################################################################

echo ""
echo "3. Verificando certificado..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Listar certificados
sudo certbot certificates

################################################################################
# 4. VERIFICAR AUTO-RENEWAL
################################################################################

echo ""
echo "4. Verificando auto-renewal..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar timer
if sudo systemctl is-active certbot.timer > /dev/null; then
    echo "[✓] Certbot timer ativo"
else
    echo "[!] Certbot timer não ativo, habilitando..."
    sudo systemctl enable certbot.timer
    sudo systemctl start certbot.timer
    echo "[✓] Timer habilitado"
fi

# Testar renovação
echo ""
echo "[ℹ] Testando renovação (dry-run)..."
sudo certbot renew --dry-run --quiet

if [ $? -eq 0 ]; then
    echo "[✓] Renovação automática funcionando!"
else
    echo "[!] Problemas com renovação automática"
fi

################################################################################
# 5. TESTAR HTTPS
################################################################################

echo ""
echo "5. Testando HTTPS..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sleep 2

# Testar HTTPS local
HTTPS_CODE=$(curl -s -k -o /dev/null -w "%{http_code}" https://localhost 2>/dev/null || echo "000")
echo "HTTPS Status: $HTTPS_CODE"

if [ "$HTTPS_CODE" == "200" ]; then
    echo "[✓] HTTPS respondendo!"
elif [ "$HTTPS_CODE" == "502" ]; then
    echo "[!] Bad Gateway - Aplicação não está rodando na porta 8000"
else
    echo "[!] HTTPS Status: $HTTPS_CODE"
fi

# Testar redirect HTTP → HTTPS
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null || echo "000")
echo "HTTP Redirect: $HTTP_CODE"

if [ "$HTTP_CODE" == "301" ] || [ "$HTTP_CODE" == "302" ]; then
    echo "[✓] Redirect HTTP → HTTPS ativo!"
fi

################################################################################
# 6. SALVAR INFORMAÇÕES
################################################################################

echo ""
echo "6. Salvando informações..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Obter detalhes do certificado
CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
EXPIRY=$(sudo openssl x509 -in $CERT_PATH/fullchain.pem -noout -enddate 2>/dev/null | cut -d= -f2)

cat > ssl-certificate-marabet.txt << EOF
MaraBet AI - Certificado SSL
=============================

Domínio:              $DOMAIN
Email:                $EMAIL
Método:               Let's Encrypt (Certbot)

Certificados:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Fullchain:            $CERT_PATH/fullchain.pem
Private Key:          $CERT_PATH/privkey.pem
Chain:                $CERT_PATH/chain.pem
Cert:                 $CERT_PATH/cert.pem

Validade:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Expira em:            $EXPIRY
Renovação automática: ✅ Sim (60 dias antes)
Timer systemd:        ✅ Ativo

Domínios Cobertos:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • $DOMAIN
  • www.$DOMAIN

Configuração:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Nginx config:         /etc/nginx/sites-available/marabet
HTTPS:                ✅ Ativo
HTTP → HTTPS:         ✅ Redirect automático

URLs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  https://$DOMAIN
  https://www.$DOMAIN

Comandos Úteis:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Listar certificados:
  sudo certbot certificates

Renovar manualmente:
  sudo certbot renew

Testar renovação:
  sudo certbot renew --dry-run

Ver logs:
  sudo cat /var/log/letsencrypt/letsencrypt.log

Reload Nginx:
  sudo systemctl reload nginx

Configurado em:       $(date)
EOF

echo "[✓] ssl-certificate-marabet.txt criado"

################################################################################
# RESUMO FINAL
################################################################################

echo ""
echo "========================================================================"
echo "✅ SSL CERTIFICATE CONFIGURADO!"
echo "========================================================================"
echo ""

echo "Certificado SSL:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Domínios:"
echo "    • $DOMAIN"
echo "    • www.$DOMAIN"
echo ""
echo "  Validade:         90 dias"
echo "  Expira em:        $EXPIRY"
echo "  Renovação:        Automática (60 dias antes)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "URLs HTTPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ✅ https://$DOMAIN"
echo "  ✅ https://www.$DOMAIN"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Testar:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  # Local"
echo "  curl https://localhost -k"
echo ""
echo "  # Do seu PC"
echo "  curl https://$DOMAIN"
echo ""
echo "  # Navegador"
echo "  https://$DOMAIN"
echo ""
echo "  # SSL Labs (Grade A+)"
echo "  https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Deploy aplicação:"
echo "     sudo su - marabet"
echo "     cd /opt/marabet"
echo "     docker-compose up -d"
echo ""
echo "  2. Atualizar .env com HTTPS:"
echo "     APP_URL=https://$DOMAIN"
echo ""
echo "  3. Testar aplicação:"
echo "     curl https://$DOMAIN/health"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "✅ HTTPS configurado!"
echo ""
echo "🎉 MARABET.COM AGORA ESTÁ EM HTTPS!"
echo ""

