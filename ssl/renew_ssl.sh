#!/bin/bash
# MaraBet AI - Script de Renovação SSL
# Renova certificados Let's Encrypt automaticamente

set -e

echo "🔐 MaraBet AI - Renovação de Certificados SSL"
echo "=============================================="
echo ""

# Verificar se certbot está instalado
if ! command -v certbot &> /dev/null; then
    echo "❌ Certbot não instalado!"
    echo "   Instalar: sudo apt install certbot python3-certbot-nginx"
    exit 1
fi

echo "✅ Certbot encontrado"
echo ""

# Renovar certificados
echo "🔄 Renovando certificados..."
sudo certbot renew --quiet

if [ $? -eq 0 ]; then
    echo "✅ Certificados renovados com sucesso!"
    
    # Recarregar Nginx
    echo "🔄 Recarregando Nginx..."
    sudo systemctl reload nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx recarregado!"
    else
        echo "⚠️  Erro ao recarregar Nginx"
    fi
    
    # Log de sucesso
    echo "$(date): SSL renovado com sucesso" >> /var/log/marabet/ssl_renewal.log
    
    echo ""
    echo "✅ Renovação concluída!"
else
    echo "❌ Erro na renovação!"
    echo "$(date): Erro na renovação SSL" >> /var/log/marabet/ssl_renewal.log
    exit 1
fi

echo ""
echo "📅 Próxima renovação: Automática (30 dias antes do vencimento)"
echo "📄 Ver logs: /var/log/marabet/ssl_renewal.log"

