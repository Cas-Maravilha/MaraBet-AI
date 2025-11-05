#!/bin/bash

################################################################################
# MARABET AI - GERAR CHAVES SECRETAS
# Gera todas as chaves necessárias para .env
################################################################################

echo "========================================================================"
echo "🔐 MaraBet AI - Gerar Chaves Secretas"
echo "========================================================================"
echo ""

echo "Gerando chaves seguras..."
echo ""

################################################################################
# 1. SECRET_KEY
################################################################################

echo "1. SECRET_KEY (Django/Flask):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Método 1: Python secrets (mais seguro)
if command -v python3 &> /dev/null; then
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    echo "SECRET_KEY=$SECRET_KEY"
else
    # Método 2: OpenSSL (alternativa)
    SECRET_KEY=$(openssl rand -base64 50 | tr -d '\n')
    echo "SECRET_KEY=$SECRET_KEY"
fi

echo ""

################################################################################
# 2. JWT_SECRET_KEY
################################################################################

echo "2. JWT_SECRET_KEY (JSON Web Tokens):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v python3 &> /dev/null; then
    JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    echo "JWT_SECRET_KEY=$JWT_SECRET_KEY"
else
    JWT_SECRET_KEY=$(openssl rand -base64 50 | tr -d '\n')
    echo "JWT_SECRET_KEY=$JWT_SECRET_KEY"
fi

echo ""

################################################################################
# 3. DATABASE ENCRYPTION KEY
################################################################################

echo "3. DATABASE_ENCRYPTION_KEY (opcional):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v python3 &> /dev/null; then
    DB_ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "DATABASE_ENCRYPTION_KEY=$DB_ENCRYPTION_KEY"
else
    DB_ENCRYPTION_KEY=$(openssl rand -base64 32 | tr -d '\n')
    echo "DATABASE_ENCRYPTION_KEY=$DB_ENCRYPTION_KEY"
fi

echo ""

################################################################################
# 4. API KEY INTERNA
################################################################################

echo "4. INTERNAL_API_KEY (para APIs internas):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v python3 &> /dev/null; then
    INTERNAL_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(40))")
    echo "INTERNAL_API_KEY=$INTERNAL_API_KEY"
else
    INTERNAL_API_KEY=$(openssl rand -base64 40 | tr -d '\n')
    echo "INTERNAL_API_KEY=$INTERNAL_API_KEY"
fi

echo ""

################################################################################
# 5. SALVAR EM ARQUIVO
################################################################################

echo "5. Salvando em arquivo..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > chaves-secretas.txt << EOF
MaraBet AI - Chaves Secretas Geradas
=====================================
Data: $(date)

⚠️  IMPORTANTE: Guarde este arquivo em local seguro!
⚠️  NÃO faça commit no Git!
⚠️  NÃO compartilhe estas chaves!

Chaves:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SECRET_KEY=$SECRET_KEY

JWT_SECRET_KEY=$JWT_SECRET_KEY

DATABASE_ENCRYPTION_KEY=$DB_ENCRYPTION_KEY

INTERNAL_API_KEY=$INTERNAL_API_KEY

Uso no .env:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Copie as linhas acima e adicione ao seu arquivo .env

Ou use este comando:
  cat chaves-secretas.txt >> .env

Gerado por: gerar_chaves_secretas.sh
EOF

chmod 600 chaves-secretas.txt

echo "[✓] Chaves salvas em: chaves-secretas.txt (permissões 600)"

################################################################################
# 6. CRIAR .ENV PARCIAL
################################################################################

echo ""
echo "6. Criando .env.secrets (apenas chaves)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > .env.secrets << EOF
# MaraBet AI - Secret Keys
# Gerado: $(date)

SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
DATABASE_ENCRYPTION_KEY=$DB_ENCRYPTION_KEY
INTERNAL_API_KEY=$INTERNAL_API_KEY
EOF

chmod 600 .env.secrets

echo "[✓] .env.secrets criado (permissões 600)"

################################################################################
# RESUMO
################################################################################

echo ""
echo "========================================================================"
echo "✅ CHAVES GERADAS COM SUCESSO!"
echo "========================================================================"
echo ""

echo "Arquivos criados:"
echo "  📄 chaves-secretas.txt    - Todas as chaves (texto)"
echo "  📄 .env.secrets           - Formato .env (apenas chaves)"
echo ""

echo "Usar no .env:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  # Opção 1: Copiar manualmente"
echo "  cat chaves-secretas.txt"
echo ""
echo "  # Opção 2: Append ao .env"
echo "  cat .env.secrets >> .env"
echo ""
echo "  # Opção 3: Source no .env"
echo "  echo 'source .env.secrets' >> .env"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "⚠️  SEGURANÇA:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  • NÃO faça commit destes arquivos no Git"
echo "  • Adicione ao .gitignore:"
echo "    chaves-secretas.txt"
echo "    .env.secrets"
echo "    .env"
echo ""
echo "  • Faça backup seguro"
echo "  • Use AWS Secrets Manager em produção (opcional)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "✅ Chaves prontas para uso!"
echo ""

