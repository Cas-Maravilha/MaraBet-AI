#!/bin/bash

# MaraBet AI - SSH Connect Script
# EC2 Instance: i-0458fc5e3b1715084

echo "🔐 Conectando ao MaraBet EC2..."
echo "Instance ID: i-0458fc5e3b1715084"
echo "Nome: marabet-production"
echo "IP Público: 34.254.241.89"
echo "DNS Público: ec2-34-254-241-89.eu-west-1.compute.amazonaws.com"
echo ""

if [ ! -f "marabet-key.pem" ]; then
    echo "❌ marabet-key.pem não encontrado!"
    echo ""
    echo "Certifique-se de estar no diretório correto:"
    echo "  cd 'D:\Usuario\Maravilha\Desktop\MaraBet AI'"
    exit 1
fi

# Garantir permissões corretas
chmod 400 marabet-key.pem 2>/dev/null || true

# Conectar
ssh -i "marabet-key.pem" ubuntu@ec2-34-254-241-89.eu-west-1.compute.amazonaws.com

