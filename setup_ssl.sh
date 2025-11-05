#!/bin/bash
# Script de Configuração SSL/HTTPS - MaraBet AI
# Executa no servidor Ubuntu

set -e

echo "🔐 MARABET AI - CONFIGURAÇÃO SSL/HTTPS"
echo "=========================================="
echo "📅 Data/Hora: $(date)"
echo ""

# Variáveis
DOMAIN="${1:-marabet.com}"
EMAIL="${2:-comercial@marabet.ao}"

echo "📋 Configuração:"
echo "Domínio: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# 1. Instalar Certbot
echo "📦 PASSO 1: INSTALAR CERTBOT"
echo "----------------------------------------"
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

echo "✅ Certbot instalado com sucesso!"
echo ""

# 2. Criar diretórios
echo "📁 PASSO 2: CRIAR DIRETÓRIOS"
echo "----------------------------------------"
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p nginx

echo "✅ Diretórios criados!"
echo ""

# 3. Obter certificado SSL
echo "🔐 PASSO 3: OBTER CERTIFICADO SSL"
echo "----------------------------------------"
echo "⚠️  IMPORTANTE: Certifique-se que o domínio aponta para este servidor!"
echo ""

# Usar modo standalone temporariamente
sudo certbot certonly --standalone \
    --preferred-challenges http \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

if [ $? -eq 0 ]; then
    echo "✅ Certificado SSL obtido com sucesso!"
else
    echo "❌ Falha ao obter certificado SSL"
    echo "Verifique:"
    echo "  1. O domínio aponta para este servidor"
    echo "  2. As portas 80 e 443 estão abertas"
    echo "  3. Não há outro serviço usando a porta 80"
    exit 1
fi
echo ""

# 4. Copiar certificados para Docker
echo "📋 PASSO 4: COPIAR CERTIFICADOS"
echo "----------------------------------------"
sudo cp -r /etc/letsencrypt/* certbot/conf/
sudo chown -R $USER:$USER certbot/conf

echo "✅ Certificados copiados!"
echo ""

# 5. Configurar renovação automática
echo "⏰ PASSO 5: CONFIGURAR RENOVAÇÃO AUTOMÁTICA"
echo "----------------------------------------"

# Criar script de renovação
cat > renew_ssl.sh << 'EOF'
#!/bin/bash
# Script de Renovação SSL - MaraBet AI

# Renovar certificados
certbot renew --quiet

# Copiar certificados atualizados
cp -r /etc/letsencrypt/* /opt/marabet/certbot/conf/

# Recarregar Nginx no Docker
docker-compose -f /opt/marabet/docker-compose-ssl.yml exec nginx nginx -s reload

echo "✅ Certificados SSL renovados: $(date)" >> /var/log/marabet-ssl-renewal.log
EOF

chmod +x renew_ssl.sh
sudo mv renew_ssl.sh /opt/marabet/

# Adicionar ao crontab
(crontab -l 2>/dev/null; echo "0 0 * * * /opt/marabet/renew_ssl.sh") | crontab -

echo "✅ Renovação automática configurada!"
echo ""

# 6. Testar configuração Nginx
echo "🧪 PASSO 6: TESTAR CONFIGURAÇÃO NGINX"
echo "----------------------------------------"
docker-compose -f docker-compose-ssl.yml config

if [ $? -eq 0 ]; then
    echo "✅ Configuração Docker Compose válida!"
else
    echo "❌ Erro na configuração Docker Compose"
    exit 1
fi
echo ""

# 7. Iniciar serviços
echo "🚀 PASSO 7: INICIAR SERVIÇOS COM SSL"
echo "----------------------------------------"
docker-compose -f docker-compose-ssl.yml up -d

echo "✅ Serviços iniciados com SSL!"
echo ""

# 8. Verificar SSL
echo "🔍 PASSO 8: VERIFICAR SSL"
echo "----------------------------------------"
sleep 5

# Testar HTTPS
curl -I https://$DOMAIN 2>/dev/null | head -n 1

if [ $? -eq 0 ]; then
    echo "✅ SSL funcionando corretamente!"
else
    echo "⚠️  Aguarde alguns segundos e teste manualmente:"
    echo "   https://$DOMAIN"
fi
echo ""

# 9. Informações finais
echo "🎉 CONFIGURAÇÃO SSL CONCLUÍDA!"
echo "=========================================="
echo ""
echo "📋 INFORMAÇÕES:"
echo "• Domínio: https://$DOMAIN"
echo "• Certificado: Let's Encrypt"
echo "• Validade: 90 dias"
echo "• Renovação: Automática (diariamente às 00:00)"
echo ""
echo "🔍 VERIFICAR:"
echo "• Status: docker-compose -f docker-compose-ssl.yml ps"
echo "• Logs: docker-compose -f docker-compose-ssl.yml logs -f nginx"
echo "• SSL: curl -I https://$DOMAIN"
echo ""
echo "🧪 TESTAR SSL:"
echo "• https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo ""
echo "📞 SUPORTE: +224 932027393"
