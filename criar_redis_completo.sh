#!/bin/bash

################################################################################
# MARABET AI - CRIAR ELASTICACHE REDIS
# Script automático completo
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

print_header "💾 MARABET AI - CRIAR ELASTICACHE REDIS"

# Configurações
REGION="eu-west-1"
REPLICATION_GROUP_ID="marabet-redis"
NODE_TYPE="cache.t3.medium"
NUM_NODES=2
AUTH_TOKEN="MaraBetRedis2025SecureToken"

print_info "Região: $REGION"
print_info "Cluster ID: $REPLICATION_GROUP_ID"
print_info "Node Type: $NODE_TYPE"
print_info "Número de Nodes: $NUM_NODES (1 Primary + 1 Replica)"
echo ""

################################################################################
# 1. OBTER VPC E SUBNETS
################################################################################

print_header "1. OBTENDO VPC E SUBNETS"

# Obter VPC
print_info "Obtendo VPC marabet-vpc..."
VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=tag:Name,Values=marabet-vpc" \
    --region $REGION \
    --query 'Vpcs[0].VpcId' \
    --output text 2>&1)

if [[ $VPC_ID == vpc-* ]]; then
    print_success "VPC: $VPC_ID"
else
    print_error "VPC marabet-vpc não encontrada!"
    print_info "Crie a VPC primeiro ou use um VPC ID existente"
    exit 1
fi

# Obter Subnets Privadas
print_info "Obtendo subnets privadas..."
SUBNETS=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=marabet-private-*" \
    --region $REGION \
    --query 'Subnets[*].SubnetId' \
    --output text)

if [ -z "$SUBNETS" ]; then
    print_error "Subnets privadas não encontradas!"
    print_info "Crie as subnets privadas primeiro"
    exit 1
fi

SUBNET_ARRAY=($SUBNETS)
SUBNET_PRIVATE_A=${SUBNET_ARRAY[0]}
SUBNET_PRIVATE_B=${SUBNET_ARRAY[1]}

print_success "Subnet Private A: $SUBNET_PRIVATE_A"
print_success "Subnet Private B: $SUBNET_PRIVATE_B"

################################################################################
# 2. OBTER SECURITY GROUP
################################################################################

print_header "2. OBTENDO SECURITY GROUP"

print_info "Obtendo Security Group Redis..."
SG_REDIS=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=marabet-redis-sg" "Name=vpc-id,Values=$VPC_ID" \
    --region $REGION \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>&1)

if [[ $SG_REDIS == sg-* ]]; then
    print_success "Redis SG: $SG_REDIS"
else
    print_warning "Security Group não encontrado, criando..."
    
    # Obter Web SG
    SG_WEB=$(aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=marabet-web-sg" \
        --region $REGION \
        --query 'SecurityGroups[0].GroupId' \
        --output text)
    
    # Criar Redis SG
    SG_REDIS=$(aws ec2 create-security-group \
        --group-name marabet-redis-sg \
        --description "Security group for MaraBet ElastiCache Redis" \
        --vpc-id $VPC_ID \
        --region $REGION \
        --query 'GroupId' \
        --output text)
    
    print_success "Redis SG criado: $SG_REDIS"
    
    # Adicionar regra
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_REDIS \
        --protocol tcp \
        --port 6379 \
        --source-group $SG_WEB \
        --region $REGION
    
    print_success "Regra adicionada (porta 6379 de $SG_WEB)"
fi

################################################################################
# 3. CRIAR CACHE SUBNET GROUP
################################################################################

print_header "3. CRIANDO CACHE SUBNET GROUP"

print_info "Criando marabet-redis-subnet..."
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name marabet-redis-subnet \
    --cache-subnet-group-description "Subnet group for MaraBet Redis" \
    --subnet-ids $SUBNET_PRIVATE_A $SUBNET_PRIVATE_B \
    --region $REGION 2>/dev/null || print_warning "Cache Subnet Group já existe"

print_success "Cache Subnet Group criado/verificado"

################################################################################
# 4. CRIAR REDIS REPLICATION GROUP
################################################################################

print_header "4. CRIANDO REDIS REPLICATION GROUP"

print_info "Criando Redis cluster..."
print_warning "Isso pode levar 10-15 minutos"
echo ""

aws elasticache create-replication-group \
    --replication-group-id $REPLICATION_GROUP_ID \
    --replication-group-description "MaraBet Redis Cluster" \
    --engine redis \
    --engine-version 7.0 \
    --cache-node-type $NODE_TYPE \
    --num-cache-clusters $NUM_NODES \
    --automatic-failover-enabled \
    --cache-subnet-group-name marabet-redis-subnet \
    --security-group-ids $SG_REDIS \
    --at-rest-encryption-enabled \
    --transit-encryption-enabled \
    --auth-token "$AUTH_TOKEN" \
    --snapshot-retention-limit 5 \
    --snapshot-window "03:00-05:00" \
    --preferred-maintenance-window "sun:05:00-sun:07:00" \
    --tags "Key=Name,Value=marabet-redis" "Key=Environment,Value=production" \
    --region $REGION 2>/dev/null || print_warning "Cluster pode já existir"

print_success "Redis Replication Group iniciando..."

print_info "Aguardando cluster ficar disponível..."
aws elasticache wait replication-group-available \
    --replication-group-id $REPLICATION_GROUP_ID \
    --region $REGION

print_success "Redis cluster disponível!"

################################################################################
# 5. OBTER ENDPOINTS
################################################################################

print_header "5. OBTENDO ENDPOINTS"

print_info "Consultando endpoints..."

# Primary Endpoint (Read/Write)
REDIS_PRIMARY=$(aws elasticache describe-replication-groups \
    --replication-group-id $REPLICATION_GROUP_ID \
    --region $REGION \
    --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Address' \
    --output text)

REDIS_PORT=$(aws elasticache describe-replication-groups \
    --replication-group-id $REPLICATION_GROUP_ID \
    --region $REGION \
    --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Port' \
    --output text)

# Reader Endpoint (Read-Only)
REDIS_READER=$(aws elasticache describe-replication-groups \
    --replication-group-id $REPLICATION_GROUP_ID \
    --region $REGION \
    --query 'ReplicationGroups[0].NodeGroups[0].ReaderEndpoint.Address' \
    --output text)

print_success "Primary Endpoint: $REDIS_PRIMARY:$REDIS_PORT"
print_success "Reader Endpoint: $REDIS_READER:$REDIS_PORT"

# Obter status
REDIS_STATUS=$(aws elasticache describe-replication-groups \
    --replication-group-id $REPLICATION_GROUP_ID \
    --region $REGION \
    --query 'ReplicationGroups[0].Status' \
    --output text)

print_info "Status: $REDIS_STATUS"

################################################################################
# 6. GERAR ARQUIVOS DE CONFIGURAÇÃO
################################################################################

print_header "6. GERANDO ARQUIVOS DE CONFIGURAÇÃO"

# redis-endpoint.txt
print_info "Criando redis-endpoint.txt..."
cat > redis-endpoint.txt << EOF
MaraBet AI - ElastiCache Redis
===============================

Replication Group ID: $REPLICATION_GROUP_ID
Region:               $REGION
Status:               $REDIS_STATUS

Primary Endpoint:     $REDIS_PRIMARY
Reader Endpoint:      $REDIS_READER
Port:                 $REDIS_PORT

Node Type:            $NODE_TYPE
Number of Nodes:      $NUM_NODES
Engine:               Redis 7.0

Auth Token:           $AUTH_TOKEN
Encryption At-Rest:   Yes
Encryption In-Transit: Yes

Snapshot Retention:   5 dias
Snapshot Window:      03:00-05:00 UTC
Maintenance Window:   Domingos 05:00-07:00 UTC

Generated:            $(date)
EOF

print_success "redis-endpoint.txt criado"

# .env.redis
print_info "Criando .env.redis..."
cat > .env.redis << EOF
# MaraBet AI - ElastiCache Redis Configuration
# Generated: $(date)

# Redis Connection (Primary - Read/Write)
REDIS_URL=rediss://:$AUTH_TOKEN@$REDIS_PRIMARY:$REDIS_PORT
REDIS_HOST=$REDIS_PRIMARY
REDIS_PORT=$REDIS_PORT
REDIS_PASSWORD=$AUTH_TOKEN
REDIS_SSL=true
REDIS_TLS=true

# Redis Reader (Read-Only)
REDIS_READER_HOST=$REDIS_READER
REDIS_READER_URL=rediss://:$AUTH_TOKEN@$REDIS_READER:$REDIS_PORT

# Redis Configuration
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
REDIS_RETRY_ON_TIMEOUT=true

# Cluster Info
REDIS_CLUSTER_ID=$REPLICATION_GROUP_ID
REDIS_NODE_TYPE=$NODE_TYPE
REDIS_ENGINE=redis
REDIS_ENGINE_VERSION=7.0

# AWS
AWS_REGION=$REGION
EOF

print_success ".env.redis criado"

# redis-config.json
print_info "Criando redis-config.json..."
cat > redis-config.json << EOF
{
  "redis": {
    "replication_group_id": "$REPLICATION_GROUP_ID",
    "status": "$REDIS_STATUS",
    "region": "$REGION",
    "primary_endpoint": "$REDIS_PRIMARY",
    "reader_endpoint": "$REDIS_READER",
    "port": $REDIS_PORT,
    "node_type": "$NODE_TYPE",
    "num_nodes": $NUM_NODES,
    "engine": "redis",
    "engine_version": "7.0",
    "auth_token": "$AUTH_TOKEN",
    "encryption_at_rest": true,
    "encryption_in_transit": true
  },
  "connection_strings": {
    "primary": "rediss://:$AUTH_TOKEN@$REDIS_PRIMARY:$REDIS_PORT",
    "reader": "rediss://:$AUTH_TOKEN@$REDIS_READER:$REDIS_PORT",
    "python": "rediss://:$AUTH_TOKEN@$REDIS_PRIMARY:$REDIS_PORT/0",
    "nodejs": "rediss://:$AUTH_TOKEN@$REDIS_PRIMARY:$REDIS_PORT"
  },
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

print_success "redis-config.json criado"

# test-redis-connection.sh
print_info "Criando test-redis-connection.sh..."
cat > test-redis-connection.sh << 'EOF'
#!/bin/bash
source .env.redis

echo "🔌 Testando conexão com Redis..."
echo "Endpoint: $REDIS_HOST"
echo ""

# Testar com redis-cli (se disponível)
if command -v redis-cli &> /dev/null; then
    redis-cli -h $REDIS_HOST -p $REDIS_PORT --tls -a "$REDIS_PASSWORD" PING
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Conexão bem-sucedida!"
        echo ""
        echo "Testando comandos:"
        redis-cli -h $REDIS_HOST -p $REDIS_PORT --tls -a "$REDIS_PASSWORD" SET test "MaraBet OK"
        redis-cli -h $REDIS_HOST -p $REDIS_PORT --tls -a "$REDIS_PASSWORD" GET test
    else
        echo ""
        echo "❌ Falha na conexão"
    fi
else
    echo "⚠️  redis-cli não instalado"
    echo "Instale: sudo apt install redis-tools"
    echo ""
    echo "Ou teste com Python:"
    echo "  python -c 'import redis; r=redis.from_url(\"$REDIS_URL\"); print(r.ping())'"
fi
EOF

chmod +x test-redis-connection.sh
print_success "test-redis-connection.sh criado"

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ REDIS CLUSTER CRIADO COM SUCESSO!"

echo ""
echo "ElastiCache Redis:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Replication Group:  $REPLICATION_GROUP_ID"
echo "  Status:             $REDIS_STATUS"
echo ""
echo "  Primary Endpoint:   $REDIS_PRIMARY"
echo "  Reader Endpoint:    $REDIS_READER"
echo "  Port:               $REDIS_PORT"
echo ""
echo "  Node Type:          $NODE_TYPE"
echo "  Number of Nodes:    $NUM_NODES"
echo "  Engine:             Redis 7.0"
echo ""
echo "  Auth Token:         $AUTH_TOKEN"
echo "  Encryption:         At-rest ✓ | In-transit ✓"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Connection String:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  rediss://:$AUTH_TOKEN@$REDIS_PRIMARY:$REDIS_PORT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Arquivos Criados:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📄 redis-endpoint.txt       - Informações completas"
echo "  📄 .env.redis               - Variáveis de ambiente"
echo "  📄 redis-config.json        - Configuração em JSON"
echo "  📄 test-redis-connection.sh - Script de teste"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Testar conexão:"
echo "     ./test-redis-connection.sh"
echo ""
echo "  2. Adicionar ao .env principal:"
echo "     cat .env.redis >> .env"
echo ""
echo "  3. Usar na aplicação:"
echo "     source .env.redis"
echo "     python app.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_header "✅ CONCLUÍDO!"

