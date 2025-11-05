#!/bin/bash

################################################################################
# MARABET AI - SETUP RDS POSTGRESQL
# Obtém credenciais do Secrets Manager e configura database
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

print_header "🗄️ MARABET AI - SETUP RDS POSTGRESQL"

# Configurações
REGION="eu-west-1"
SECRET_ID="rds!db-3758a324-12a2-4675-b5ff-b92acdf38483"
DB_INSTANCE_ID="database-1"
DB_NAME="marabet_production"

print_info "Região: $REGION"
print_info "RDS Instance: $DB_INSTANCE_ID"
print_info "Database: $DB_NAME"
echo ""

################################################################################
# 1. VERIFICAR AWS CLI
################################################################################

print_header "1. VERIFICANDO AMBIENTE"

if ! command -v aws &> /dev/null; then
    print_error "AWS CLI não encontrado!"
    exit 1
fi
print_success "AWS CLI instalado"

if ! command -v jq &> /dev/null; then
    print_warning "jq não encontrado, instalando..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y jq || sudo yum install -y jq
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install jq
    fi
fi
print_success "jq disponível"

if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL client não encontrado"
    print_info "Instale com: sudo apt install postgresql-client"
fi

################################################################################
# 2. OBTER CREDENCIAIS DO SECRETS MANAGER
################################################################################

print_header "2. OBTENDO CREDENCIAIS DO SECRETS MANAGER"

print_info "Buscando secret: $SECRET_ID..."
SECRET=$(aws secretsmanager get-secret-value \
    --secret-id $SECRET_ID \
    --region $REGION \
    --query 'SecretString' \
    --output text 2>&1)

if [ $? -ne 0 ]; then
    print_error "Falha ao obter credenciais!"
    echo "$SECRET"
    exit 1
fi

print_success "Credenciais obtidas"

# Extrair valores
DB_HOST=$(echo $SECRET | jq -r '.host')
DB_PORT=$(echo $SECRET | jq -r '.port')
DB_USER=$(echo $SECRET | jq -r '.username')
DB_PASSWORD=$(echo $SECRET | jq -r '.password')
DB_ENGINE=$(echo $SECRET | jq -r '.engine')

print_info "Host: $DB_HOST"
print_info "Port: $DB_PORT"
print_info "User: $DB_USER"
print_info "Engine: $DB_ENGINE"

################################################################################
# 3. VERIFICAR STATUS DO RDS
################################################################################

print_header "3. VERIFICANDO STATUS DO RDS"

print_info "Consultando RDS Instance..."
RDS_STATUS=$(aws rds describe-db-instances \
    --db-instance-identifier $DB_INSTANCE_ID \
    --region $REGION \
    --query 'DBInstances[0].DBInstanceStatus' \
    --output text 2>&1)

if [[ $RDS_STATUS == "available" ]]; then
    print_success "RDS Status: available"
elif [[ $RDS_STATUS == "creating" ]]; then
    print_warning "RDS Status: creating (aguarde alguns minutos)"
elif [[ $RDS_STATUS == "backing-up" ]]; then
    print_warning "RDS Status: backing-up"
else
    print_error "RDS Status: $RDS_STATUS"
fi

# Obter mais informações
RDS_INFO=$(aws rds describe-db-instances \
    --db-instance-identifier $DB_INSTANCE_ID \
    --region $REGION \
    --query 'DBInstances[0].[DBInstanceClass,Engine,EngineVersion,MultiAZ,StorageEncrypted,AllocatedStorage]' \
    --output text)

read -r CLASS ENGINE VERSION MULTIAZ ENCRYPTED STORAGE <<< "$RDS_INFO"

print_info "Instance Class: $CLASS"
print_info "Engine: $ENGINE $VERSION"
print_info "Multi-AZ: $MULTIAZ"
print_info "Encrypted: $ENCRYPTED"
print_info "Storage: ${STORAGE}GB"

################################################################################
# 4. TESTAR CONECTIVIDADE
################################################################################

print_header "4. TESTANDO CONECTIVIDADE"

if command -v psql &> /dev/null; then
    print_info "Testando conexão com PostgreSQL..."
    
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "SELECT version();" &>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Conexão estabelecida com sucesso!"
    else
        print_error "Falha na conexão!"
        print_info "Verifique Security Groups e Network ACLs"
        print_info "Comando para testar manualmente:"
        echo "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres"
    fi
else
    print_warning "psql não disponível, pulando teste de conexão"
fi

################################################################################
# 5. CRIAR DATABASE MARABET
################################################################################

print_header "5. CRIANDO DATABASE"

if command -v psql &> /dev/null; then
    print_info "Criando database $DB_NAME..."
    
    # Verificar se database já existe
    DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" 2>/dev/null)
    
    if [ "$DB_EXISTS" == "1" ]; then
        print_warning "Database $DB_NAME já existe"
    else
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;" &>/dev/null
        
        if [ $? -eq 0 ]; then
            print_success "Database $DB_NAME criada"
        else
            print_error "Falha ao criar database"
        fi
    fi
else
    print_warning "psql não disponível, pule para criar database manualmente"
fi

################################################################################
# 6. GERAR ARQUIVOS DE CONFIGURAÇÃO
################################################################################

print_header "6. GERANDO ARQUIVOS DE CONFIGURAÇÃO"

# .env.production
print_info "Criando .env.production..."
cat > .env.production << EOF
# MaraBet AI - Production Environment
# Generated: $(date)

# RDS PostgreSQL
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?sslmode=require
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_SSL_MODE=require

# AWS Configuration
AWS_REGION=${REGION}
AWS_ACCOUNT_ID=206749730888

# AWS Secrets Manager
SECRET_ARN=arn:aws:secretsmanager:${REGION}:206749730888:secret:${SECRET_ID}-BpTjIS
SECRET_NAME=${SECRET_ID}

# RDS Instance
RDS_INSTANCE_ID=${DB_INSTANCE_ID}
RDS_INSTANCE_ARN=arn:aws:rds:${REGION}:206749730888:db:${DB_INSTANCE_ID}
EOF

print_success ".env.production criado"

# rds-info.json
print_info "Criando rds-info.json..."
cat > rds-info.json << EOF
{
  "rds": {
    "instance_id": "${DB_INSTANCE_ID}",
    "region": "${REGION}",
    "endpoint": "${DB_HOST}",
    "port": ${DB_PORT},
    "engine": "${DB_ENGINE}",
    "database": "${DB_NAME}",
    "username": "${DB_USER}",
    "instance_class": "${CLASS}",
    "multi_az": ${MULTIAZ},
    "encrypted": ${ENCRYPTED},
    "storage_gb": ${STORAGE}
  },
  "secrets_manager": {
    "secret_id": "${SECRET_ID}",
    "secret_arn": "arn:aws:secretsmanager:${REGION}:206749730888:secret:${SECRET_ID}-BpTjIS",
    "region": "${REGION}"
  },
  "connection_string": "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?sslmode=require"
}
EOF

print_success "rds-info.json criado"

# connection-test.sh
print_info "Criando connection-test.sh..."
cat > connection-test.sh << 'EOF'
#!/bin/bash
source .env.production
echo "Testing RDS Connection..."
psql "$DATABASE_URL" -c "SELECT version();"
echo ""
echo "Listing databases:"
psql "$DATABASE_URL" -c "\l"
EOF

chmod +x connection-test.sh
print_success "connection-test.sh criado"

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ SETUP CONCLUÍDO!"

echo ""
echo "Informações do RDS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  RDS Instance:      $DB_INSTANCE_ID"
echo "  Status:            $RDS_STATUS"
echo "  Endpoint:          $DB_HOST"
echo "  Port:              $DB_PORT"
echo "  Database:          $DB_NAME"
echo "  Username:          $DB_USER"
echo "  Engine:            $DB_ENGINE"
echo ""
echo "  Instance Class:    $CLASS"
echo "  Multi-AZ:          $MULTIAZ"
echo "  Encrypted:         $ENCRYPTED"
echo "  Storage:           ${STORAGE}GB"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Arquivos Criados:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📄 .env.production      - Variáveis de ambiente"
echo "  📄 rds-info.json        - Informações em JSON"
echo "  📄 connection-test.sh   - Script de teste"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Connection String:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?sslmode=require"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Testar conexão:"
echo "     ./connection-test.sh"
echo ""
echo "  2. Conectar manualmente:"
echo "     psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
echo ""
echo "  3. Usar na aplicação:"
echo "     source .env.production"
echo "     python app.py"
echo ""
echo "  4. Ver credenciais novamente:"
echo "     cat .env.production"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Exportar variáveis (opcional)
read -p "Exportar variáveis no shell atual? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?sslmode=require"
    export DB_HOST=$DB_HOST
    export DB_PORT=$DB_PORT
    export DB_NAME=$DB_NAME
    export DB_USER=$DB_USER
    export DB_PASSWORD=$DB_PASSWORD
    
    print_success "Variáveis exportadas!"
    echo ""
    echo "Agora você pode usar:"
    echo "  echo \$DATABASE_URL"
    echo "  psql \$DATABASE_URL"
fi

echo ""
print_header "✅ SETUP COMPLETO!"

