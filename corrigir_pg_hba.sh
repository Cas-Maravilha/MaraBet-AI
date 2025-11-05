#!/bin/bash
# Script para corrigir pg_hba.conf
# MaraBet AI - Corrige linha incompleta no pg_hba.conf

echo "============================================================"
echo "🔧 CORREÇÃO DO PG_HBA.CONF - POSTGRESQL"
echo "============================================================"
echo ""

# Verificar se está executando como root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Este script precisa ser executado como root ou com sudo"
    echo "   Execute: sudo bash corrigir_pg_hba.sh"
    exit 1
fi

# Localizar arquivo pg_hba.conf
PG_HBA_FILE=$(find /etc -name pg_hba.conf 2>/dev/null | head -1)

if [ -z "$PG_HBA_FILE" ]; then
    echo "❌ Arquivo pg_hba.conf não encontrado"
    exit 1
fi

echo "📋 Arquivo encontrado: $PG_HBA_FILE"
echo ""

# Fazer backup
BACKUP_FILE="${PG_HBA_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$PG_HBA_FILE" "$BACKUP_FILE"
echo "✅ Backup criado: $BACKUP_FILE"
echo ""

# Verificar se há linha incompleta
if grep -q "^host[[:space:]]*meu_banco[[:space:]]*meu_usuario[[:space:]]*0\.0\.0\.0/0[[:space:]]*$" "$PG_HBA_FILE"; then
    echo "⚠️  Linha incompleta encontrada (sem método de autenticação)"
    echo ""
    echo "Linha atual:"
    grep "^host[[:space:]]*meu_banco[[:space:]]*meu_usuario" "$PG_HBA_FILE"
    echo ""
    
    # Perguntar qual método usar
    echo "Escolha o método de autenticação:"
    echo "1. md5 (compatível, recomendado)"
    echo "2. scram-sha-256 (mais seguro, PostgreSQL 10+)"
    read -p "Escolha (1 ou 2) [1]: " choice
    choice=${choice:-1}
    
    if [ "$choice" = "2" ]; then
        METHOD="scram-sha-256"
    else
        METHOD="md5"
    fi
    
    # Remover linha incompleta
    sed -i '/^host[[:space:]]*meu_banco[[:space:]]*meu_usuario[[:space:]]*0\.0\.0\.0\/0[[:space:]]*$/d' "$PG_HBA_FILE"
    
    # Adicionar linha completa
    if grep -q "host.*meu_banco.*meu_usuario.*$METHOD" "$PG_HBA_FILE"; then
        echo "⚠️  Linha completa já existe"
    else
        echo "# Conexões remotas para meu_usuario - MaraBet AI" >> "$PG_HBA_FILE"
        echo "host    meu_banco    meu_usuario    0.0.0.0/0    $METHOD" >> "$PG_HBA_FILE"
        echo "✅ Linha corrigida e adicionada"
    fi
    
elif grep -q "^host[[:space:]]*meu_banco[[:space:]]*meu_usuario" "$PG_HBA_FILE"; then
    echo "✅ Linha já existe e está completa"
    echo ""
    echo "Linha encontrada:"
    grep "^host[[:space:]]*meu_banco[[:space:]]*meu_usuario" "$PG_HBA_FILE"
else
    echo "ℹ️  Linha não encontrada, adicionando..."
    echo ""
    read -p "Usar md5 (1) ou scram-sha-256 (2)? [1]: " choice
    choice=${choice:-1}
    
    if [ "$choice" = "2" ]; then
        METHOD="scram-sha-256"
    else
        METHOD="md5"
    fi
    
    echo "# Conexões remotas para meu_usuario - MaraBet AI" >> "$PG_HBA_FILE"
    echo "host    meu_banco    meu_usuario    0.0.0.0/0    $METHOD" >> "$PG_HBA_FILE"
    echo "✅ Linha adicionada"
fi

echo ""
echo "📋 Configuração final:"
grep "^host[[:space:]]*meu_banco[[:space:]]*meu_usuario" "$PG_HBA_FILE" || echo "Linha não encontrada"

echo ""
echo "🔄 Reiniciando PostgreSQL..."
systemctl restart postgresql
sleep 2

# Verificar se está rodando
if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL reiniciado com sucesso"
else
    echo "❌ Erro ao reiniciar PostgreSQL"
    echo "   Verifique logs: sudo tail -f /var/log/postgresql/postgresql-*.log"
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ CORREÇÃO CONCLUÍDA!"
echo "============================================================"
echo ""
echo "📋 Próximos passos:"
echo "   1. Testar conexão localmente:"
echo "      psql -h localhost -U meu_usuario -d meu_banco"
echo ""
echo "   2. Testar conexão remotamente:"
echo "      python testar_conexao.py"
echo ""
echo "============================================================"

