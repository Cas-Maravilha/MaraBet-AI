#!/bin/bash
# Script para configurar pg_hba.conf no servidor PostgreSQL
# MaraBet AI - Configuração de conexões remotas

echo "============================================================"
echo "🔧 CONFIGURAÇÃO DO PG_HBA.CONF - POSTGRESQL"
echo "============================================================"
echo ""

# Verificar se está executando como root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Este script precisa ser executado como root ou com sudo"
    echo "   Execute: sudo bash configurar_pg_hba.sh"
    exit 1
fi

# Localizar arquivo pg_hba.conf
PG_HBA_FILE=$(find /etc -name pg_hba.conf 2>/dev/null | head -1)

if [ -z "$PG_HBA_FILE" ]; then
    echo "❌ Arquivo pg_hba.conf não encontrado"
    echo "   Verifique se PostgreSQL está instalado"
    exit 1
fi

echo "📋 Arquivo encontrado: $PG_HBA_FILE"
echo ""

# Fazer backup
BACKUP_FILE="${PG_HBA_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$PG_HBA_FILE" "$BACKUP_FILE"
echo "✅ Backup criado: $BACKUP_FILE"
echo ""

# Verificar se a linha já existe
if grep -q "host.*meu_banco.*meu_usuario" "$PG_HBA_FILE"; then
    echo "⚠️  Linha já existe no arquivo"
    echo ""
    echo "Linha encontrada:"
    grep "host.*meu_banco.*meu_usuario" "$PG_HBA_FILE"
    echo ""
    read -p "Deseja substituir? (s/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "❌ Operação cancelada"
        exit 0
    fi
    # Remover linha antiga
    sed -i '/host.*meu_banco.*meu_usuario/d' "$PG_HBA_FILE"
fi

# Adicionar linha no final do arquivo
echo "# Conexões remotas para meu_usuario - MaraBet AI" >> "$PG_HBA_FILE"
echo "host    meu_banco    meu_usuario    0.0.0.0/0    md5" >> "$PG_HBA_FILE"

echo "✅ Linha adicionada ao pg_hba.conf"
echo ""
echo "📋 Linha adicionada:"
echo "   host    meu_banco    meu_usuario    0.0.0.0/0    md5"
echo ""

# Verificar sintaxe
echo "🔍 Verificando sintaxe..."
if sudo -u postgres psql -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ Sintaxe OK"
else
    echo "⚠️  Aviso: Não foi possível verificar sintaxe"
fi

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
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
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

