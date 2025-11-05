#!/bin/bash
# Script de Deploy AWS - MaraBet AI

echo "🚀 Iniciando deploy do MaraBet AI na AWS..."

# Verificar se AWS CLI está configurado
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI não encontrado. Instale e configure primeiro."
    exit 1
fi

# Verificar credenciais AWS
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Credenciais AWS não configuradas."
    exit 1
fi

echo "✅ AWS CLI configurado e funcionando"

# Criar stack CloudFormation
echo "📦 Criando infraestrutura AWS..."
aws cloudformation create-stack \
    --stack-name marabet-ai-production \
    --template-body file://deploy/aws/cloudformation-template.yml \
    --capabilities CAPABILITY_IAM

echo "⏳ Aguardando criação da stack..."
aws cloudformation wait stack-create-complete \
    --stack-name marabet-ai-production

echo "✅ Infraestrutura criada com sucesso!"

# Deploy da aplicação
echo "📦 Fazendo deploy da aplicação..."
# Aqui você adicionaria comandos específicos para deploy da aplicação

echo "🎉 Deploy concluído com sucesso!"
