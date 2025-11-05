#!/bin/bash

################################################################################
# MARABET AI - INSTALAR E CONFIGURAR NGINX COMPLETO
# Executar na EC2 via SSH
################################################################################

set -e

echo "========================================================================"
echo "🌐 MaraBet AI - Instalar e Configurar Nginx"
echo "========================================================================"
echo ""

# Variáveis
DOMAIN="marabet.com"

################################################################################
# 1. INSTALAR NGINX
################################################################################

echo "1. Instalando Nginx..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sudo apt-get update
sudo apt-get install -y nginx

echo ""
echo "[✓] Nginx instalado: $(nginx -v 2>&1)"

################################################################################
# 2. CRIAR CONFIGURAÇÃO
################################################################################

echo ""
echo "2. Criando configuração do Nginx..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Baixar configuração ou criar inline
if [ -f "nginx-marabet-config.conf" ]; then
    echo "[ℹ] Usando nginx-marabet-config.conf local"
    sudo cp nginx-marabet-config.conf /etc/nginx/sites-available/marabet
else
    echo "[ℹ] Criando configuração inline..."
    
    sudo tee /etc/nginx/sites-available/marabet > /dev/null << 'NGINXCONF'
# MaraBet AI - Nginx Configuration

# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
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
    listen [::]:443 ssl http2;
    server_name marabet.com www.marabet.com;
    
    # SSL (será configurado pelo Certbot)
    ssl_certificate /etc/letsencrypt/live/marabet.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/marabet.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Config
    client_max_body_size 100M;
    
    # Logs
    access_log /var/log/nginx/marabet-access.log;
    error_log /var/log/nginx/marabet-error.log;
    
    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    # Static Files
    location /static/ {
        alias /opt/marabet/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media Files
    location /media/ {
        alias /opt/marabet/media/;
        expires 7d;
    }
    
    # Health Check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}

# HTTPS - API Subdomain
server {
    listen 443 ssl http2;
    server_name api.marabet.com;
    
    ssl_certificate /etc/letsencrypt/live/marabet.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/marabet.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    
    add_header Access-Control-Allow-Origin * always;
    
    location / {
        proxy_pass http://127.0.0.1:8000/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXCONF

fi

echo "[✓] Configuração criada"

################################################################################
# 3. ATIVAR SITE
################################################################################

echo ""
echo "3. Ativando site..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Remover default
sudo rm -f /etc/nginx/sites-enabled/default

# Ativar marabet
sudo ln -sf /etc/nginx/sites-available/marabet /etc/nginx/sites-enabled/

echo "[✓] Site ativado"

################################################################################
# 4. TESTAR CONFIGURAÇÃO
################################################################################

echo ""
echo "4. Testando configuração..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sudo nginx -t

if [ $? -eq 0 ]; then
    echo ""
    echo "[✓] Configuração válida!"
else
    echo ""
    echo "[✗] Erro na configuração!"
    exit 1
fi

################################################################################
# 5. RELOAD NGINX
################################################################################

echo ""
echo "5. Recarregando Nginx..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sudo systemctl reload nginx
sudo systemctl enable nginx

echo "[✓] Nginx recarregado e habilitado no boot"

################################################################################
# 6. VERIFICAR STATUS
################################################################################

echo ""
echo "6. Verificando status..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sudo systemctl status nginx --no-pager | head -n 10

################################################################################
# RESUMO
################################################################################

echo ""
echo "========================================================================"
echo "✅ NGINX INSTALADO E CONFIGURADO!"
echo "========================================================================"
echo ""

echo "Configuração:"
echo "  • /etc/nginx/sites-available/marabet"
echo "  • /etc/nginx/sites-enabled/marabet → ativo"
echo ""

echo "Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Instalar Certbot:"
echo "     sudo apt-get install -y certbot python3-certbot-nginx"
echo ""
echo "  2. Obter SSL:"
echo "     sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo ""
echo "  3. Deploy aplicação:"
echo "     sudo su - marabet"
echo "     cd /opt/marabet"
echo "     docker-compose up -d"
echo ""
echo "  4. Testar:"
echo "     curl http://localhost"
echo "     curl https://$DOMAIN (após SSL)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "✅ Nginx pronto!"
echo ""

