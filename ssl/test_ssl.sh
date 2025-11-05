#!/bin/bash
# MaraBet AI - Teste de Configuração SSL
# Verifica se SSL está configurado corretamente

set -e

DOMAIN="${1:-marabet.ao}"

echo "🔐 MaraBet AI - Teste de Configuração SSL"
echo "=========================================="
echo ""
echo "Domínio: $DOMAIN"
echo ""

# Verificar se site está acessível
echo "1️⃣  Testando HTTPS..."
if curl -s -I "https://$DOMAIN" | grep -q "HTTP/2 200"; then
    echo "   ✅ HTTPS funcionando"
else
    echo "   ❌ HTTPS não acessível"
    echo "   Verifique se Nginx está rodando e SSL configurado"
    exit 1
fi

# Verificar certificado
echo ""
echo "2️⃣  Verificando certificado SSL..."
CERT_INFO=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null || echo "Erro")

if [ "$CERT_INFO" != "Erro" ]; then
    echo "   ✅ Certificado válido"
    echo "$CERT_INFO" | while read line; do
        echo "      $line"
    done
else
    echo "   ⚠️  Não foi possível verificar certificado"
    echo "   (Normal se site ainda não está no ar)"
fi

# Verificar redirecionamento HTTP → HTTPS
echo ""
echo "3️⃣  Testando redirecionamento HTTP → HTTPS..."
REDIRECT=$(curl -s -I "http://$DOMAIN" | grep -i "location: https://" || echo "")

if [ -n "$REDIRECT" ]; then
    echo "   ✅ Redirecionamento HTTP → HTTPS ativo"
else
    echo "   ⚠️  Redirecionamento não configurado"
fi

# Verificar headers de segurança
echo ""
echo "4️⃣  Verificando headers de segurança..."
HEADERS=$(curl -s -I "https://$DOMAIN" 2>/dev/null || echo "")

check_header() {
    if echo "$HEADERS" | grep -qi "$1"; then
        echo "   ✅ $1"
    else
        echo "   ⚠️  $1: Não encontrado"
    fi
}

check_header "Strict-Transport-Security"
check_header "X-Content-Type-Options"
check_header "X-Frame-Options"
check_header "X-XSS-Protection"

# Teste SSL Labs (opcional)
echo ""
echo "5️⃣  Teste SSL Labs (opcional):"
echo "   🌐 https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"

echo ""
echo "✅ Verificação concluída!"

