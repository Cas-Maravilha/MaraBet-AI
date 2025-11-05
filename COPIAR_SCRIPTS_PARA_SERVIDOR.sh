#!/bin/bash

# =============================================
# Script: Copiar Scripts para Servidor Remoto
# Ajuda a transferir os scripts via SCP
# =============================================

echo "📋 Scripts disponíveis para copiar:"
echo ""

# Listar scripts
SCRIPTS=(
    "INSTALAR_POSTGRESQL_REMOTO.sh"
    "configurar_postgresql_remoto.sh"
    "verificar_configuracao_postgresql.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo "✅ $script"
    else
        echo "❌ $script (não encontrado)"
    fi
done

echo ""
echo "📤 Para copiar scripts para o servidor remoto, execute:"
echo ""
echo "scp *.sh usuario@37.27.220.67:/home/usuario/"
echo ""
echo "Substitua 'usuario' pelo seu usuário no servidor remoto."
echo ""
echo "Ou use o comando completo:"
echo "scp INSTALAR_POSTGRESQL_REMOTO.sh configurar_postgresql_remoto.sh verificar_configuracao_postgresql.sh usuario@37.27.220.67:~/"
echo ""

