#!/bin/bash

################################################################################
# MARABET AI - ATIVAR NGINX
# Script rápido para ativar configuração Nginx
################################################################################

set -e

echo "========================================================================"
echo "🌐 MaraBet AI - Ativar Nginx"
echo "========================================================================"
echo ""

################################################################################
# 1. VERIFICAR SE CONFIG EXISTE
################################################################################

echo "1. Verificando configuração..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ! -f "/etc/nginx/sites-available/marabet" ]; then
    echo "[✗] Arquivo /etc/nginx/sites-available/marabet não encontrado!"
    echo ""
    echo "Crie o arquivo primeiro:"
    echo "  sudo nano /etc/nginx/sites-available/marabet"
    echo ""
    echo "Ou use:"
    echo "  ./instalar_nginx_completo.sh"
    exit 1
fi

echo "[✓] Configuração encontrada"

################################################################################
# 2. HABILITAR SITE
################################################################################

echo ""
echo "2. Habilitando site..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Criar link simbólico
sudo ln -sf /etc/nginx/sites-available/marabet /etc/nginx/sites-enabled/

echo "[✓] Link simbólico criado"

# Remover default
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    sudo rm /etc/nginx/sites-enabled/default
    echo "[✓] Site default removido"
fi

################################################################################
# 3. TESTAR CONFIGURAÇÃO
################################################################################

echo ""
echo "3. Testando configuração..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sudo nginx -t

if [ $? -eq 0 ]; then
    echo ""
    echo "[✓] Configuração válida!"
else
    echo ""
    echo "[✗] Erro na configuração!"
    echo ""
    echo "Verifique o arquivo:"
    echo "  sudo nano /etc/nginx/sites-available/marabet"
    exit 1
fi

################################################################################
# 4. RESTART NGINX
################################################################################

echo ""
echo "4. Reiniciando Nginx..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sudo systemctl restart nginx

echo "[✓] Nginx reiniciado"

# Verificar status
if sudo systemctl is-active nginx > /dev/null; then
    echo "[✓] Nginx está rodando"
else
    echo "[✗] Nginx não está rodando!"
    echo ""
    echo "Ver logs:"
    echo "  sudo journalctl -u nginx -n 50"
    exit 1
fi

################################################################################
# 5. VERIFICAR SITES ATIVOS
################################################################################

echo ""
echo "5. Verificando sites ativos..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Sites habilitados:"
ls -la /etc/nginx/sites-enabled/

################################################################################
# 6. TESTAR HTTP
################################################################################

echo ""
echo "6. Testando HTTP..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sleep 2

# Testar localhost
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null || echo "000")

echo "HTTP Status Code: $HTTP_CODE"

if [ "$HTTP_CODE" == "200" ]; then
    echo "[✓] HTTP respondendo corretamente!"
elif [ "$HTTP_CODE" == "502" ]; then
    echo "[!] Bad Gateway - Aplicação na porta 8000 não está rodando"
    echo ""
    echo "Inicie a aplicação:"
    echo "  sudo su - marabet"
    echo "  cd /opt/marabet"
    echo "  docker-compose up -d"
elif [ "$HTTP_CODE" == "000" ]; then
    echo "[!] Nginx não está respondendo"
else
    echo "[!] Status inesperado: $HTTP_CODE"
fi

################################################################################
# RESUMO
################################################################################

echo ""
echo "========================================================================"
echo "✅ NGINX ATIVADO!"
echo "========================================================================"
echo ""

echo "Status:"
echo "  • Configuração: /etc/nginx/sites-available/marabet"
echo "  • Link simbólico: /etc/nginx/sites-enabled/marabet"
echo "  • Nginx: $(sudo systemctl is-active nginx)"
echo "  • HTTP Status: $HTTP_CODE"
echo ""

echo "Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Se aplicação não está rodando (502):"
echo "     sudo su - marabet"
echo "     cd /opt/marabet"
echo "     docker-compose up -d"
echo ""
echo "  2. Testar HTTP:"
echo "     curl http://marabet.com"
echo ""
echo "  3. Configurar SSL:"
echo "     sudo apt-get install -y certbot python3-certbot-nginx"
echo "     sudo certbot --nginx -d marabet.com -d www.marabet.com"
echo ""
echo "  4. Testar HTTPS:"
echo "     curl https://marabet.com"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Ver logs:"
echo "  sudo tail -f /var/log/nginx/error.log"
echo ""

echo "✅ Nginx configurado e ativo!"
echo ""

