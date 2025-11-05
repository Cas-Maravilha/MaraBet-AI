#!/bin/bash

################################################################################
# MARABET AI - OBTER ENDPOINT REDIS SERVERLESS
# Obtém e salva endpoint do ElastiCache Serverless
################################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo ""
    echo "========================================================================"
    echo "$1"
    echo "========================================================================"
    echo ""
}

print_header "💾 MARABET AI - OBTER ENDPOINT REDIS"

# Configurações
REGION="eu-west-1"
CACHE_NAME="marabet-redis"

print_info "Cache Name: $CACHE_NAME"
print_info "Região: $REGION"
echo ""

################################################################################
# 1. VERIFICAR STATUS
################################################################################

print_header "1. VERIFICANDO STATUS DO REDIS"

print_info "Consultando ElastiCache Serverless..."

STATUS=$(aws elasticache describe-serverless-caches \
    --serverless-cache-name $CACHE_NAME \
    --region $REGION \
    --query 'ServerlessCaches[0].Status' \
    --output text 2>&1)

if [ $? -ne 0 ]; then
    print_error "Redis Serverless não encontrado!"
    echo ""
    print_info "Verifique se o nome está correto: $CACHE_NAME"
    print_info "Liste os caches disponíveis:"
    echo "  aws elasticache describe-serverless-caches --region $REGION"
    exit 1
fi

if [ "$STATUS" == "available" ]; then
    print_success "Status: available ✓"
elif [ "$STATUS" == "creating" ]; then
    print_warning "Status: creating (aguarde 5-10 minutos)"
    print_info "Aguardando Redis ficar disponível..."
    
    # Aguardar em loop (máximo 20 minutos)
    MAX_ATTEMPTS=40
    ATTEMPT=0
    
    while [ "$STATUS" != "available" ] && [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        sleep 30
        ((ATTEMPT++))
        
        STATUS=$(aws elasticache describe-serverless-caches \
            --serverless-cache-name $CACHE_NAME \
            --region $REGION \
            --query 'ServerlessCaches[0].Status' \
            --output text)
        
        echo -n "."
    done
    
    echo ""
    
    if [ "$STATUS" == "available" ]; then
        print_success "Redis agora disponível!"
    else
        print_error "Timeout aguardando Redis. Status atual: $STATUS"
        exit 1
    fi
else
    print_warning "Status: $STATUS"
fi

################################################################################
# 2. OBTER ENDPOINT
################################################################################

print_header "2. OBTENDO ENDPOINT"

print_info "Consultando endpoint..."

REDIS_ENDPOINT=$(aws elasticache describe-serverless-caches \
    --serverless-cache-name $CACHE_NAME \
    --region $REGION \
    --query 'ServerlessCaches[0].Endpoint.Address' \
    --output text)

if [ -z "$REDIS_ENDPOINT" ] || [ "$REDIS_ENDPOINT" == "None" ]; then
    print_error "Endpoint não disponível ainda!"
    exit 1
fi

print_success "Endpoint: $REDIS_ENDPOINT"

REDIS_PORT=$(aws elasticache describe-serverless-caches \
    --serverless-cache-name $CACHE_NAME \
    --region $REGION \
    --query 'ServerlessCaches[0].Endpoint.Port' \
    --output text)

print_success "Porta: $REDIS_PORT"

################################################################################
# 3. OBTER INFORMAÇÕES COMPLETAS
################################################################################

print_header "3. OBTENDO INFORMAÇÕES COMPLETAS"

print_info "Consultando detalhes..."

REDIS_INFO=$(aws elasticache describe-serverless-caches \
    --serverless-cache-name $CACHE_NAME \
    --region $REGION)

# Extrair informações
ENGINE=$(echo "$REDIS_INFO" | jq -r '.ServerlessCaches[0].Engine')
FULL_ENGINE_VERSION=$(echo "$REDIS_INFO" | jq -r '.ServerlessCaches[0].FullEngineVersion')
ARN=$(echo "$REDIS_INFO" | jq -r '.ServerlessCaches[0].ARN')
VPC_ID=$(echo "$REDIS_INFO" | jq -r '.ServerlessCaches[0].SecurityGroupIds[0]' | xargs aws ec2 describe-security-groups --group-ids --region $REGION --query 'SecurityGroups[0].VpcId' --output text 2>/dev/null || echo "N/A")

print_info "Engine: $ENGINE"
print_info "Version: $FULL_ENGINE_VERSION"
print_info "ARN: $ARN"

################################################################################
# 4. GERAR ARQUIVOS DE CONFIGURAÇÃO
################################################################################

print_header "4. GERANDO ARQUIVOS DE CONFIGURAÇÃO"

# redis-serverless-endpoint.txt
print_info "Criando redis-serverless-endpoint.txt..."
cat > redis-serverless-endpoint.txt << EOF
MaraBet AI - ElastiCache Redis Serverless
==========================================

Name:                 $CACHE_NAME
Status:               $STATUS
Region:               $REGION

Endpoint:             $REDIS_ENDPOINT
Port:                 $REDIS_PORT

Engine:               $ENGINE
Version:              $FULL_ENGINE_VERSION
Type:                 Serverless

Encryption At-Rest:   Yes (AWS owned KMS key)
Encryption In-Transit: Yes (TLS)
Multi-AZ:             Yes (3 AZs: eu-west-1a, eu-west-1b, eu-west-1c)

VPC:                  vpc-081a8c63b16a94a3a
Security Group:       sg-09f7d3d37a8407f43
Subnets:
  - subnet-061544d7c4c85bd82 (eu-west-1b)
  - subnet-0f4df2ddacfc070bc (eu-west-1c)
  - subnet-0575567cf09ae0e02 (eu-west-1a)

ARN:                  $ARN

Generated:            $(date)
EOF

print_success "redis-serverless-endpoint.txt criado"

# .env.redis
print_info "Criando .env.redis..."
cat > .env.redis << EOF
# MaraBet AI - ElastiCache Redis Serverless Configuration
# Generated: $(date)

# Redis Connection
REDIS_URL=rediss://$REDIS_ENDPOINT:$REDIS_PORT
REDIS_HOST=$REDIS_ENDPOINT
REDIS_PORT=$REDIS_PORT
REDIS_SSL=true
REDIS_TLS=true
REDIS_DB=0

# Redis Configuration
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_RETRY_ON_TIMEOUT=true
REDIS_DECODE_RESPONSES=true

# Serverless Info
REDIS_TYPE=serverless
REDIS_ENGINE=$ENGINE
REDIS_VERSION=$FULL_ENGINE_VERSION
REDIS_SERVERLESS_NAME=$CACHE_NAME

# AWS
AWS_REGION=$REGION
AWS_ACCOUNT_ID=206749730888
ELASTICACHE_ARN=$ARN
EOF

print_success ".env.redis criado"

# redis-serverless-config.json
print_info "Criando redis-serverless-config.json..."
cat > redis-serverless-config.json << EOF
{
  "redis": {
    "name": "$CACHE_NAME",
    "type": "serverless",
    "status": "$STATUS",
    "region": "$REGION",
    "endpoint": "$REDIS_ENDPOINT",
    "port": $REDIS_PORT,
    "engine": "$ENGINE",
    "engine_version": "$FULL_ENGINE_VERSION",
    "arn": "$ARN",
    "vpc_id": "vpc-081a8c63b16a94a3a",
    "security_group_id": "sg-09f7d3d37a8407f43",
    "subnets": [
      "subnet-061544d7c4c85bd82",
      "subnet-0f4df2ddacfc070bc",
      "subnet-0575567cf09ae0e02"
    ],
    "availability_zones": [
      "eu-west-1a",
      "eu-west-1b",
      "eu-west-1c"
    ],
    "encryption": {
      "at_rest": true,
      "in_transit": true,
      "kms_key": "AWS owned"
    }
  },
  "connection_strings": {
    "redis": "rediss://$REDIS_ENDPOINT:$REDIS_PORT",
    "python": "rediss://$REDIS_ENDPOINT:$REDIS_PORT/0",
    "nodejs": "rediss://$REDIS_ENDPOINT:$REDIS_PORT"
  },
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

print_success "redis-serverless-config.json criado"

# Script de teste
print_info "Criando test-redis-serverless.sh..."
cat > test-redis-serverless.sh << 'EOF'
#!/bin/bash
source .env.redis

echo "🔌 Testando conexão com Redis Serverless..."
echo "Endpoint: $REDIS_HOST"
echo "Port: $REDIS_PORT"
echo ""

# Testar com redis-cli
if command -v redis-cli &> /dev/null; then
    echo "Testando PING..."
    redis-cli -h $REDIS_HOST -p $REDIS_PORT --tls --insecure PING
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Conexão bem-sucedida!"
        echo ""
        echo "Testando comandos básicos:"
        redis-cli -h $REDIS_HOST -p $REDIS_PORT --tls --insecure SET marabet_test "OK"
        redis-cli -h $REDIS_HOST -p $REDIS_PORT --tls --insecure GET marabet_test
        redis-cli -h $REDIS_HOST -p $REDIS_PORT --tls --insecure DEL marabet_test
    else
        echo ""
        echo "❌ Falha na conexão"
        echo "Verifique Security Group e conectividade"
    fi
else
    echo "⚠️  redis-cli não instalado"
    echo "Instale: sudo apt install redis-tools"
    echo ""
    echo "Ou teste com Python:"
    echo "  python redis_config.py"
fi
EOF

chmod +x test-redis-serverless.sh
print_success "test-redis-serverless.sh criado"

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ ENDPOINT REDIS OBTIDO COM SUCESSO!"

echo ""
echo "ElastiCache Redis Serverless:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Name:              $CACHE_NAME"
echo "  Status:            $STATUS"
echo "  Endpoint:          $REDIS_ENDPOINT"
echo "  Port:              $REDIS_PORT"
echo ""
echo "  Engine:            $ENGINE $FULL_ENGINE_VERSION"
echo "  Type:              Serverless"
echo "  Multi-AZ:          3 Availability Zones"
echo "  Encryption:        At-rest ✓ | In-transit ✓"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Connection URL:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  rediss://$REDIS_ENDPOINT:$REDIS_PORT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Arquivos Criados:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📄 redis-serverless-endpoint.txt  - Informações completas"
echo "  📄 .env.redis                     - Variáveis de ambiente"
echo "  📄 redis-serverless-config.json   - Configuração JSON"
echo "  📄 test-redis-serverless.sh       - Script de teste"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Testar conexão:"
echo "     ./test-redis-serverless.sh"
echo ""
echo "  2. Ou testar com Python:"
echo "     python redis_config.py"
echo ""
echo "  3. Adicionar ao .env principal:"
echo "     cat .env.redis >> .env"
echo ""
echo "  4. Usar na aplicação:"
echo "     from redis_config import get_redis_client"
echo "     redis_client = get_redis_client()"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_header "✅ CONCLUÍDO!"

# Salvar no histórico
cat >> redis-history.log << EOF
[$(date)] Redis Serverless endpoint obtido: $REDIS_ENDPOINT (Status: $STATUS)
EOF

print_info "Histórico salvo em: redis-history.log"
echo ""

