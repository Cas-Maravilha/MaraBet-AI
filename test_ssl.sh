#!/bin/bash
# Script de Teste SSL - MaraBet AI
# Testa configuração SSL/HTTPS

echo "🔍 MARABET AI - TESTE SSL/HTTPS"
echo "=========================================="
echo ""

# Variáveis
DOMAIN="${1:-marabet.com}"

echo "📋 Testando: $DOMAIN"
echo ""

# 1. Testar resolução DNS
echo "1️⃣  TESTE DNS"
echo "----------------------------------------"
nslookup $DOMAIN
echo ""

# 2. Testar conectividade HTTP
echo "2️⃣  TESTE HTTP (porta 80)"
echo "----------------------------------------"
curl -I http://$DOMAIN 2>&1 | head -n 5
echo ""

# 3. Testar conectividade HTTPS
echo "3️⃣  TESTE HTTPS (porta 443)"
echo "----------------------------------------"
curl -I https://$DOMAIN 2>&1 | head -n 5
echo ""

# 4. Testar certificado SSL
echo "4️⃣  TESTE CERTIFICADO SSL"
echo "----------------------------------------"
echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates
echo ""

# 5. Testar redirecionamento HTTP -> HTTPS
echo "5️⃣  TESTE REDIRECIONAMENTO HTTP -> HTTPS"
echo "----------------------------------------"
curl -I -L http://$DOMAIN 2>&1 | grep -E "(HTTP|Location)"
echo ""

# 6. Testar headers de segurança
echo "6️⃣  TESTE HEADERS DE SEGURANÇA"
echo "----------------------------------------"
curl -I https://$DOMAIN 2>&1 | grep -E "(Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options)"
echo ""

# 7. Testar SSL Labs (score)
echo "7️⃣  SSL LABS (Score)"
echo "----------------------------------------"
echo "🌐 Teste completo em:"
echo "   https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo ""

# 8. Testar validade do certificado
echo "8️⃣  VALIDADE DO CERTIFICADO"
echo "----------------------------------------"
echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -text | grep -A 2 "Validity"
echo ""

# 9. Testar TLS versions
echo "9️⃣  TESTE TLS VERSIONS"
echo "----------------------------------------"
echo "TLS 1.2:"
openssl s_client -tls1_2 -connect $DOMAIN:443 </dev/null 2>&1 | grep "Protocol"
echo "TLS 1.3:"
openssl s_client -tls1_3 -connect $DOMAIN:443 </dev/null 2>&1 | grep "Protocol"
echo ""

echo "🎉 TESTES CONCLUÍDOS!"
echo "=========================================="
