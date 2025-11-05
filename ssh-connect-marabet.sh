#!/bin/bash
# ssh-connect-marabet.sh

KEY_FILE="marabet-key.pem"

# Verificar se key existe
if [ ! -f "\" ]; then
    echo "❌ Key file não encontrado: \"
    exit 1
fi

# Verificar permissões (Linux/macOS)
if [ $(uname) != "MINGW64_NT"* ] && [ $(uname) != "MSYS_NT"* ]; then
    chmod 400 \
fi

# IP da EC2 (atualizar após criar)
EC2_IP="<EC2_PUBLIC_IP>"

if [ "\" == "<EC2_PUBLIC_IP>" ]; then
    echo "⚠️  Atualize o EC2_IP no script primeiro!"
    echo ""
    echo "Obter IP:"
    echo "  aws ec2 describe-instances --instance-ids <INSTANCE_ID> --query 'Reservations[0].Instances[0].PublicIpAddress' --output text"
    exit 1
fi

# Conectar
echo "🔐 Conectando ao MaraBet EC2..."
echo "IP: \"
echo ""

ssh -i \ ubuntu@\
