#!/bin/bash

################################################################################
# MARABET AI - OBTER ENDPOINT RDS
# Obtém e salva todas as informações do RDS PostgreSQL
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

print_header "🗄️ MARABET AI - OBTER ENDPOINT RDS"

# Configurações
REGION="eu-west-1"
DB_INSTANCE_ID="database-1"
SECRET_ID="rds!db-3758a324-12a2-4675-b5ff-b92acdf38483"

print_info "RDS Instance: $DB_INSTANCE_ID"
print_info "Região: $REGION"
echo ""

################################################################################
# 1. VERIFICAR SE RDS EXISTE
################################################################################

print_header "1. VERIFICANDO RDS"

print_info "Consultando RDS Instance..."

RDS_STATUS=$(aws rds describe-db-instances \
    --db-instance-identifier $DB_INSTANCE_ID \
    --region $REGION \
    --query 'DBInstances[0].DBInstanceStatus' \
    --output text 2>&1)

if [ $? -ne 0 ]; then
    print_error "RDS Instance não encontrado!"
    echo ""
    print_info "Verifique se o nome está correto: $DB_INSTANCE_ID"
    print_info "Liste os RDS disponíveis:"
    echo "  aws rds describe-db-instances --region $REGION --query 'DBInstances[*].DBInstanceIdentifier'"
    exit 1
fi

if [ "$RDS_STATUS" == "available" ]; then
    print_success "RDS Status: available ✓"
elif [ "$RDS_STATUS" == "creating" ]; then
    print_warning "RDS Status: creating (aguarde alguns minutos)"
    print_info "Aguardando RDS ficar disponível..."
    aws rds wait db-instance-available \
        --db-instance-identifier $DB_INSTANCE_ID \
        --region $REGION
    print_success "RDS agora disponível!"
else
    print_warning "RDS Status: $RDS_STATUS"
fi

################################################################################
# 2. OBTER ENDPOINT
################################################################################

print_header "2. OBTENDO ENDPOINT"

print_info "Consultando endpoint do RDS..."

RDS_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier $DB_INSTANCE_ID \
    --region $REGION \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)

if [ -z "$RDS_ENDPOINT" ] || [ "$RDS_ENDPOINT" == "None" ]; then
    print_error "Endpoint não disponível ainda!"
    print_info "RDS pode estar sendo criado. Status: $RDS_STATUS"
    exit 1
fi

print_success "Endpoint: $RDS_ENDPOINT"

# Obter porta
RDS_PORT=$(aws rds describe-db-instances \
    --db-instance-identifier $DB_INSTANCE_ID \
    --region $REGION \
    --query 'DBInstances[0].Endpoint.Port' \
    --output text)

print_success "Porta: $RDS_PORT"

################################################################################
# 3. OBTER INFORMAÇÕES COMPLETAS
################################################################################

print_header "3. OBTENDO INFORMAÇÕES COMPLETAS"

print_info "Consultando detalhes do RDS..."

# Obter informações em JSON
RDS_INFO=$(aws rds describe-db-instances \
    --db-instance-identifier $DB_INSTANCE_ID \
    --region $REGION)

# Extrair informações principais
ENGINE=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].Engine')
ENGINE_VERSION=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].EngineVersion')
INSTANCE_CLASS=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].DBInstanceClass')
STORAGE=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].AllocatedStorage')
MULTI_AZ=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].MultiAZ')
ENCRYPTED=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].StorageEncrypted')
BACKUP_RETENTION=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].BackupRetentionPeriod')
AZ=$(echo "$RDS_INFO" | jq -r '.DBInstances[0].AvailabilityZone')

print_info "Engine: $ENGINE $ENGINE_VERSION"
print_info "Instance Class: $INSTANCE_CLASS"
print_info "Storage: ${STORAGE}GB"
print_info "Multi-AZ: $MULTI_AZ"
print_info "Encrypted: $ENCRYPTED"
print_info "Backup Retention: $BACKUP_RETENTION dias"
print_info "Availability Zone: $AZ"

################################################################################
# 4. OBTER CREDENCIAIS DO SECRETS MANAGER
################################################################################

print_header "4. OBTENDO CREDENCIAIS DO SECRETS MANAGER"

print_info "Consultando Secrets Manager..."

SECRET=$(aws secretsmanager get-secret-value \
    --secret-id $SECRET_ID \
    --region $REGION \
    --query 'SecretString' \
    --output text 2>&1)

if [ $? -ne 0 ]; then
    print_warning "Não foi possível obter credenciais do Secrets Manager"
    print_info "Você pode precisar criar o secret manualmente"
    DB_USER="admin"
    DB_PASSWORD="[SENHA_DO_RDS]"
else
    print_success "Credenciais obtidas do Secrets Manager"
    
    DB_USER=$(echo "$SECRET" | jq -r '.username')
    DB_PASSWORD=$(echo "$SECRET" | jq -r '.password')
    
    print_info "Username: $DB_USER"
    print_info "Password: $( echo "$DB_PASSWORD" | sed 's/./*/g' )"
fi

################################################################################
# 5. GERAR ARQUIVOS DE CONFIGURAÇÃO
################################################################################

print_header "5. GERANDO ARQUIVOS DE CONFIGURAÇÃO"

# Arquivo de endpoint
print_info "Criando rds-endpoint.txt..."
cat > rds-endpoint.txt << EOF
MaraBet AI - RDS PostgreSQL Endpoint
=====================================

RDS Instance ID:    $DB_INSTANCE_ID
Status:             $RDS_STATUS
Region:             $REGION
Availability Zone:  $AZ

Endpoint:           $RDS_ENDPOINT
Port:               $RDS_PORT

Engine:             $ENGINE $ENGINE_VERSION
Instance Class:     $INSTANCE_CLASS
Storage:            ${STORAGE}GB
Multi-AZ:           $MULTI_AZ
Encrypted:          $ENCRYPTED
Backup Retention:   $BACKUP_RETENTION dias

Database:           marabet_production
Username:           $DB_USER
Password:           $DB_PASSWORD

ARN:                arn:aws:rds:$REGION:206749730888:db:$DB_INSTANCE_ID
Secret ARN:         arn:aws:secretsmanager:$REGION:206749730888:secret:$SECRET_ID-BpTjIS

Generated:          $(date)
EOF

print_success "rds-endpoint.txt criado"

# Arquivo .env
print_info "Criando .env.rds..."
cat > .env.rds << EOF
# MaraBet AI - RDS PostgreSQL Configuration
# Generated: $(date)

# Database Connection
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$RDS_ENDPOINT:$RDS_PORT/marabet_production?sslmode=require
DB_HOST=$RDS_ENDPOINT
DB_PORT=$RDS_PORT
DB_NAME=marabet_production
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_SSL_MODE=require

# RDS Instance Info
RDS_INSTANCE_ID=$DB_INSTANCE_ID
RDS_ENDPOINT=$RDS_ENDPOINT
RDS_ENGINE=$ENGINE
RDS_VERSION=$ENGINE_VERSION
RDS_CLASS=$INSTANCE_CLASS
RDS_MULTI_AZ=$MULTI_AZ

# AWS Configuration
AWS_REGION=$REGION
AWS_ACCOUNT_ID=206749730888

# Secrets Manager
SECRET_ID=$SECRET_ID
SECRET_ARN=arn:aws:secretsmanager:$REGION:206749730888:secret:$SECRET_ID-BpTjIS
EOF

print_success ".env.rds criado"

# Arquivo JSON
print_info "Criando rds-config.json..."
cat > rds-config.json << EOF
{
  "rds": {
    "instance_id": "$DB_INSTANCE_ID",
    "status": "$RDS_STATUS",
    "region": "$REGION",
    "availability_zone": "$AZ",
    "endpoint": "$RDS_ENDPOINT",
    "port": $RDS_PORT,
    "engine": "$ENGINE",
    "engine_version": "$ENGINE_VERSION",
    "instance_class": "$INSTANCE_CLASS",
    "allocated_storage_gb": $STORAGE,
    "multi_az": $MULTI_AZ,
    "storage_encrypted": $ENCRYPTED,
    "backup_retention_days": $BACKUP_RETENTION,
    "arn": "arn:aws:rds:$REGION:206749730888:db:$DB_INSTANCE_ID"
  },
  "database": {
    "name": "marabet_production",
    "username": "$DB_USER",
    "password": "$DB_PASSWORD"
  },
  "secrets_manager": {
    "secret_id": "$SECRET_ID",
    "secret_arn": "arn:aws:secretsmanager:$REGION:206749730888:secret:$SECRET_ID-BpTjIS",
    "version_id": "c55b9938-e4de-439a-9ccd-59c7a57ed978"
  },
  "connection_strings": {
    "postgresql": "postgresql://$DB_USER:$DB_PASSWORD@$RDS_ENDPOINT:$RDS_PORT/marabet_production?sslmode=require",
    "jdbc": "jdbc:postgresql://$RDS_ENDPOINT:$RDS_PORT/marabet_production?sslmode=require",
    "django": "postgres://$DB_USER:$DB_PASSWORD@$RDS_ENDPOINT:$RDS_PORT/marabet_production",
    "rails": "postgresql://$DB_USER:$DB_PASSWORD@$RDS_ENDPOINT:$RDS_PORT/marabet_production"
  },
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

print_success "rds-config.json criado"

# Script de teste de conexão
print_info "Criando test-rds-connection.sh..."
cat > test-rds-connection.sh << 'EOF'
#!/bin/bash
source .env.rds
echo "🔌 Testando conexão com RDS..."
echo "Endpoint: $RDS_ENDPOINT"
echo ""
psql "$DATABASE_URL" -c "SELECT version();"
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Conexão bem-sucedida!"
else
    echo ""
    echo "❌ Falha na conexão"
    echo "Verifique Security Groups e conectividade"
fi
EOF

chmod +x test-rds-connection.sh
print_success "test-rds-connection.sh criado"

################################################################################
# RESUMO FINAL
################################################################################

print_header "✅ ENDPOINT RDS OBTIDO COM SUCESSO!"

echo ""
echo "RDS PostgreSQL:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Instance ID:       $DB_INSTANCE_ID"
echo "  Status:            $RDS_STATUS"
echo "  Endpoint:          $RDS_ENDPOINT"
echo "  Port:              $RDS_PORT"
echo ""
echo "  Engine:            $ENGINE $ENGINE_VERSION"
echo "  Class:             $INSTANCE_CLASS"
echo "  Storage:           ${STORAGE}GB"
echo "  Multi-AZ:          $MULTI_AZ"
echo "  Encrypted:         $ENCRYPTED"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Connection String:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  postgresql://$DB_USER:$DB_PASSWORD@$RDS_ENDPOINT:$RDS_PORT/marabet_production?sslmode=require"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Arquivos Criados:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📄 rds-endpoint.txt        - Informações completas (texto)"
echo "  📄 .env.rds                - Variáveis de ambiente"
echo "  📄 rds-config.json         - Configuração em JSON"
echo "  📄 test-rds-connection.sh  - Script de teste"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Testar conexão:"
echo "     ./test-rds-connection.sh"
echo ""
echo "  2. Usar na aplicação:"
echo "     source .env.rds"
echo "     python app.py"
echo ""
echo "  3. Ver configuração:"
echo "     cat rds-config.json"
echo ""
echo "  4. Conectar manualmente:"
echo "     psql -h $RDS_ENDPOINT -p $RDS_PORT -U $DB_USER -d marabet_production"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Criar atalho para exportar variáveis
cat > export-rds-vars.sh << EOF
#!/bin/bash
# MaraBet AI - Exportar variáveis RDS
export RDS_ENDPOINT="$RDS_ENDPOINT"
export RDS_PORT="$RDS_PORT"
export DB_USER="$DB_USER"
export DB_PASSWORD="$DB_PASSWORD"
export DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$RDS_ENDPOINT:$RDS_PORT/marabet_production?sslmode=require"

echo "✅ Variáveis RDS exportadas!"
echo ""
echo "Usar:"
echo "  source export-rds-vars.sh"
echo "  echo \$RDS_ENDPOINT"
echo "  psql \$DATABASE_URL"
EOF

chmod +x export-rds-vars.sh

print_success "export-rds-vars.sh criado"

echo ""
print_header "✅ CONCLUÍDO!"

# Salvar resumo no histórico
cat >> rds-history.log << EOF
[$(date)] RDS Endpoint obtido: $RDS_ENDPOINT (Status: $RDS_STATUS)
EOF

echo ""
print_info "Histórico salvo em: rds-history.log"
echo ""

