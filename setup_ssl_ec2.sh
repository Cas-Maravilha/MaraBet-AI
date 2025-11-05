#!/bin/bash

################################################################################
# MARABET AI - SETUP SSL/HTTPS NA EC2
# Execut na EC2 via SSH para configurar SSL com Let's Encrypt
################################################################################

set -e

echo "========================================================================"
echo "🔒 MaraBet AI - Setup SSL/HTTPS"
echo "========================================================================"
echo ""

# Configurações
DOMAIN="marabet.com"
EMAIL="suporte@marabet.com"

echo "[ℹ] Domínio: $DOMAIN"
echo "[ℹ] Email: $EMAIL"
echo ""

################################################################################
# 1. VERIFICAR DNS
################################################################################

echo "========================================================================"
echo "1. VERIFICANDO DNS"
echo "========================================================================"
echo ""

echo "[ℹ] Verificando se $DOMAIN aponta para este servidor..."

# Obter IP deste servidor
SERVER_IP=$(curl -s http://checkip.amazonaws.com)
echo "[ℹ] IP deste servidor: $SERVER_IP"

# Resolver DNS
DNS_IP=$(dig +short $DOMAIN | head -n1)
echo "[ℹ] DNS resolve para: $DNS_IP"

if [ "$SERVER_IP" == "$DNS_IP" ]; then
    echo "[✓] DNS está correto!"
else
    echo "[!] AVISO: DNS não aponta para este servidor"
    echo "    Servidor: $SERVER_IP"
    echo "    DNS:      $DNS_IP"
    echo ""
    echo "    Continue apenas se tiver certeza!"
    read -p "Continuar? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        exit 1
    fi
fi

################################################################################
# 2. PARAR NGINX TEMPORARIAMENTE
################################################################################

echo ""
echo "========================================================================"
echo "2. PREPARANDO NGINX"
echo "========================================================================"
echo ""

echo "[ℹ] Parando Nginx temporariamente..."
sudo systemctl stop nginx

################################################################################
# 3. OBTER CERTIFICADO SSL
################################################################################

echo ""
echo "========================================================================"
echo "3. OBTENDO CERTIFICADO SSL (Let's Encrypt)"
echo "========================================================================"
echo ""

echo "[ℹ] Solicitando certificado para:"
echo "    • $DOMAIN"
echo "    • www.$DOMAIN"
echo "    • api.$DOMAIN"
echo ""
echo "[!] Isso pode levar 1-2 minutos..."
echo ""

sudo certbot certonly --standalone \
  -d $DOMAIN \
  -d www.$DOMAIN \
  -d api.$DOMAIN \
  --non-interactive \
  --agree-tos \
  --email $EMAIL \
  --preferred-challenges http

if [ $? -eq 0 ]; then
    echo ""
    echo "[✓] Certificado SSL obtido com sucesso!"
else
    echo ""
    echo "[✗] Falha ao obter certificado!"
    echo ""
    echo "Possíveis causas:"
    echo "  • DNS não está propagado"
    echo "  • Porta 80 não está acessível"
    echo "  • Firewall bloqueando"
    exit 1
fi

################################################################################
# 4. CONFIGURAR NGINX COM SSL
################################################################################

echo ""
echo "========================================================================"
echo "4. CONFIGURANDO NGINX COM SSL"
echo "========================================================================"
echo ""

echo "[ℹ] Criando configuração Nginx com SSL..."

sudo tee /etc/nginx/sites-available/marabet-ssl > /dev/null << 'NGINXCONF'
# HTTP - Redirect to HTTPS
server {
    listen 80;
    server_name marabet.com www.marabet.com api.marabet.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS - Main Site
server {
    listen 443 ssl http2;
    server_name marabet.com www.marabet.com;
    
    ssl_certificate /etc/letsencrypt/live/marabet.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/marabet.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /opt/marabet/static/;
        expires 30d;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}

# HTTPS - API
server {
    listen 443 ssl http2;
    server_name api.marabet.com;
    
    ssl_certificate /etc/letsencrypt/live/marabet.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/marabet.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://127.0.0.1:8000/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXCONF

echo "[✓] Configuração Nginx criada"

# Ativar site
sudo ln -sf /etc/nginx/sites-available/marabet-ssl /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo rm -f /etc/nginx/sites-enabled/marabet

echo "[✓] Site ativado"

# Testar configuração
echo ""
echo "[ℹ] Testando configuração Nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "[✓] Configuração válida!"
else
    echo "[✗] Configuração inválida!"
    exit 1
fi

################################################################################
# 5. INICIAR NGINX
################################################################################

echo ""
echo "========================================================================"
echo "5. INICIANDO NGINX COM SSL"
echo "========================================================================"
echo ""

sudo systemctl start nginx
sudo systemctl enable nginx

echo "[✓] Nginx iniciado com SSL"

################################################################################
# 6. CONFIGURAR AUTO-RENEWAL
################################################################################

echo ""
echo "========================================================================"
echo "6. CONFIGURANDO AUTO-RENEWAL"
echo "========================================================================"
echo ""

sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo "[ℹ] Testando renovação automática (dry-run)..."
sudo certbot renew --dry-run

echo "[✓] Auto-renewal configurado e testado"

################################################################################
# 7. TESTAR HTTPS
################################################################################

echo ""
echo "========================================================================"
echo "7. TESTANDO HTTPS"
echo "========================================================================"
echo ""

sleep 2

echo "[ℹ] Testando HTTP → HTTPS redirect..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost)
echo "    HTTP Status: $HTTP_STATUS"

if [ "$HTTP_STATUS" == "301" ] || [ "$HTTP_STATUS" == "302" ]; then
    echo "[✓] Redirect funcionando!"
fi

echo ""
echo "[ℹ] Testando HTTPS..."
HTTPS_STATUS=$(curl -s -k -o /dev/null -w "%{http_code}" https://localhost)
echo "    HTTPS Status: $HTTPS_STATUS"

if [ "$HTTPS_STATUS" == "200" ]; then
    echo "[✓] HTTPS funcionando!"
else
    echo "[!] HTTPS retornou: $HTTPS_STATUS"
fi

################################################################################
# RESUMO FINAL
################################################################################

echo ""
echo "========================================================================"
echo "✅ SSL/HTTPS CONFIGURADO COM SUCESSO!"
echo "========================================================================"
echo ""

echo "Certificado SSL:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
sudo certbot certificates | grep -A 10 "Certificate Name: $DOMAIN" || true
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "URLs HTTPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ✅ https://$DOMAIN"
echo "  ✅ https://www.$DOMAIN"
echo "  ✅ https://api.$DOMAIN"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Testar do seu PC:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  curl https://$DOMAIN"
echo "  curl https://www.$DOMAIN"
echo "  curl https://api.$DOMAIN"
echo ""
echo "  Ou abrir no navegador:"
echo "  https://$DOMAIN"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Verificar segurança SSL:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "✅ MARABET.COM AGORA ESTÁ EM HTTPS!"
echo ""

