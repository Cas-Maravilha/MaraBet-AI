#!/bin/bash
# Script de Instalação SSL - MaraBet AI

echo "🔒 MARABET AI - INSTALAÇÃO DE CERTIFICADO SSL"
echo "============================================="

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root"
    echo "💡 Execute: sudo ./install_ssl.sh"
    exit 1
fi

# Atualizar sistema
echo "🔄 Atualizando sistema..."
apt update && apt upgrade -y

# Instalar Nginx se não estiver instalado
if ! command -v nginx &> /dev/null; then
    echo "🌐 Instalando Nginx..."
    apt install -y nginx
    systemctl start nginx
    systemctl enable nginx
fi

# Instalar Certbot
echo "🔒 Instalando Certbot..."
apt install -y certbot python3-certbot-nginx

# Verificar se Nginx está rodando
if ! systemctl is-active --quiet nginx; then
    echo "🌐 Iniciando Nginx..."
    systemctl start nginx
fi

# Configurar Nginx para o domínio
echo "🌐 Configurando Nginx para marabet.com..."
cat > /etc/nginx/sites-available/marabet.com << 'EOF'
server {
    listen 80;
    server_name marabet.com www.marabet.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /predictions {
        proxy_pass http://localhost:8000/predictions;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /analysis {
        proxy_pass http://localhost:8000/analysis;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /config {
        proxy_pass http://localhost:8000/config;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Habilitar site
ln -sf /etc/nginx/sites-available/marabet.com /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar configuração do Nginx
echo "🧪 Testando configuração do Nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração do Nginx OK"
    systemctl reload nginx
else
    echo "❌ Erro na configuração do Nginx"
    exit 1
fi

# Verificar se o domínio está apontando para o servidor
echo "🔍 Verificando DNS do domínio..."
echo "💡 Certifique-se de que marabet.com e www.marabet.com apontam para 3.218.152.100"
echo "💡 Aguarde alguns minutos para propagação do DNS"
echo "💡 Teste com: nslookup marabet.com"
echo "💡 Teste com: nslookup www.marabet.com"

# Aguardar confirmação do usuário
echo ""
echo "⚠️ IMPORTANTE: Antes de continuar, certifique-se de que:"
echo "   1. O domínio marabet.com está apontando para 3.218.152.100"
echo "   2. O domínio www.marabet.com está apontando para 3.218.152.100"
echo "   3. A propagação do DNS foi concluída"
echo ""
read -p "Pressione Enter para continuar ou Ctrl+C para cancelar..."

# Obter certificado SSL
echo "🔒 Obtendo certificado SSL..."
certbot --nginx -d marabet.com -d www.marabet.com --non-interactive --agree-tos --email admin@marabet.com

if [ $? -eq 0 ]; then
    echo "✅ Certificado SSL obtido com sucesso!"
else
    echo "❌ Falha ao obter certificado SSL"
    echo "💡 Verifique se o domínio está apontando corretamente para o servidor"
    exit 1
fi

# Configurar renovação automática
echo "🔄 Configurando renovação automática..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Testar renovação
echo "🧪 Testando renovação automática..."
certbot renew --dry-run

if [ $? -eq 0 ]; then
    echo "✅ Renovação automática configurada com sucesso!"
else
    echo "⚠️ Falha no teste de renovação automática"
fi

# Verificar status do certificado
echo "🔍 Verificando status do certificado..."
certbot certificates

# Verificar configuração do Nginx
echo "🔍 Verificando configuração do Nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração do Nginx OK"
    systemctl reload nginx
else
    echo "❌ Erro na configuração do Nginx"
fi

# Verificar se HTTPS está funcionando
echo "🧪 Testando HTTPS..."
curl -I https://marabet.com/health

echo "🎉 INSTALAÇÃO SSL CONCLUÍDA!"
echo "============================="
echo "🌐 URLs HTTPS:"
echo "  • https://marabet.com"
echo "  • https://www.marabet.com"
echo "  • https://marabet.com/docs"
echo "  • https://marabet.com/health"
echo "  • https://marabet.com/predictions"
echo "  • https://marabet.com/analysis"
echo "  • https://marabet.com/config"
echo ""
echo "🔒 Certificado SSL instalado e configurado!"
echo "🔄 Renovação automática configurada!"
echo "🌐 Nginx configurado como proxy reverso!"
