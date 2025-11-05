#!/bin/bash

################################################################################
# MARABET AI - CRIAR BUCKET S3 PARA BACKUPS
# Configuração completa com versionamento, encryption e lifecycle
################################################################################

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_header() {
    echo ""
    echo -e "${CYAN}========================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================================================${NC}"
    echo ""
}

print_header "💾 MARABET AI - CRIAR BUCKET S3 BACKUPS"

# Configurações
BUCKET_NAME="marabet-backups"
REGION="eu-west-1"

print_info "Bucket: $BUCKET_NAME"
print_info "Região: $REGION"
echo ""

################################################################################
# 1. CRIAR BUCKET
################################################################################

print_header "1. CRIANDO BUCKET S3"

print_info "Criando bucket $BUCKET_NAME..."

aws s3api create-bucket \
    --bucket $BUCKET_NAME \
    --region $REGION \
    --create-bucket-configuration LocationConstraint=$REGION 2>&1

if [ $? -eq 0 ]; then
    print_success "Bucket criado!"
else
    print_warning "Bucket pode já existir ou nome está em uso"
    
    # Verificar se existe
    if aws s3api head-bucket --bucket $BUCKET_NAME 2>/dev/null; then
        print_success "Bucket já existe: $BUCKET_NAME"
    else
        echo "Erro ao criar bucket. Tente outro nome."
        exit 1
    fi
fi

################################################################################
# 2. ADICIONAR TAGS
################################################################################

print_header "2. ADICIONANDO TAGS"

print_info "Adicionando tags ao bucket..."

aws s3api put-bucket-tagging \
    --bucket $BUCKET_NAME \
    --tagging 'TagSet=[
        {Key=Project,Value=MaraBet},
        {Key=Environment,Value=production},
        {Key=Purpose,Value=backups},
        {Key=Owner,Value=MaraBet-Team}
    ]'

print_success "Tags adicionadas"

################################################################################
# 3. HABILITAR VERSIONAMENTO
################################################################################

print_header "3. HABILITANDO VERSIONAMENTO"

print_info "Habilitando versionamento..."

aws s3api put-bucket-versioning \
    --bucket $BUCKET_NAME \
    --versioning-configuration Status=Enabled

print_success "Versionamento habilitado"
print_info "Benefício: Mantém versões antigas dos backups"

################################################################################
# 4. HABILITAR ENCRIPTAÇÃO
################################################################################

print_header "4. HABILITANDO ENCRIPTAÇÃO"

print_info "Habilitando encriptação AES256..."

aws s3api put-bucket-encryption \
    --bucket $BUCKET_NAME \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            },
            "BucketKeyEnabled": true
        }]
    }'

print_success "Encriptação habilitada"
print_info "Todos os objetos serão encriptados automaticamente"

################################################################################
# 5. CONFIGURAR LIFECYCLE (Retenção)
################################################################################

print_header "5. CONFIGURANDO LIFECYCLE POLICY"

print_info "Configurando política de retenção..."

aws s3api put-bucket-lifecycle-configuration \
    --bucket $BUCKET_NAME \
    --lifecycle-configuration '{
        "Rules": [
            {
                "Id": "Delete old daily backups",
                "Status": "Enabled",
                "Filter": {"Prefix": "daily/"},
                "Expiration": {"Days": 30}
            },
            {
                "Id": "Delete old weekly backups",
                "Status": "Enabled",
                "Filter": {"Prefix": "weekly/"},
                "Expiration": {"Days": 90}
            },
            {
                "Id": "Delete old monthly backups",
                "Status": "Enabled",
                "Filter": {"Prefix": "monthly/"},
                "Expiration": {"Days": 365}
            },
            {
                "Id": "Transition to Glacier",
                "Status": "Enabled",
                "Filter": {"Prefix": "monthly/"},
                "Transitions": [{
                    "Days": 90,
                    "StorageClass": "GLACIER"
                }]
            }
        ]
    }'

print_success "Lifecycle policy configurada"

echo ""
print_info "Políticas de retenção:"
echo "  • Daily backups:   30 dias"
echo "  • Weekly backups:  90 dias"
echo "  • Monthly backups: 365 dias"
echo "  • Glacier:         Após 90 dias (monthly)"

################################################################################
# 6. BLOQUEAR ACESSO PÚBLICO
################################################################################

print_header "6. BLOQUEANDO ACESSO PÚBLICO"

print_info "Bloqueando acesso público ao bucket..."

aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

print_success "Acesso público bloqueado"
print_info "Apenas usuários AWS autorizados podem acessar"

################################################################################
# 7. CRIAR ESTRUTURA DE PASTAS
################################################################################

print_header "7. CRIANDO ESTRUTURA DE PASTAS"

print_info "Criando estrutura de diretórios no S3..."

# Criar "pastas" vazias
echo "" | aws s3 cp - s3://$BUCKET_NAME/daily/.keep
echo "" | aws s3 cp - s3://$BUCKET_NAME/weekly/.keep
echo "" | aws s3 cp - s3://$BUCKET_NAME/monthly/.keep
echo "" | aws s3 cp - s3://$BUCKET_NAME/database/.keep
echo "" | aws s3 cp - s3://$BUCKET_NAME/redis/.keep
echo "" | aws s3 cp - s3://$BUCKET_NAME/files/.keep

print_success "Estrutura criada"

echo ""
print_info "Estrutura:"
echo "  • s3://$BUCKET_NAME/daily/     - Backups diários"
echo "  • s3://$BUCKET_NAME/weekly/    - Backups semanais"
echo "  • s3://$BUCKET_NAME/monthly/   - Backups mensais"
echo "  • s3://$BUCKET_NAME/database/  - Dumps database"
echo "  • s3://$BUCKET_NAME/redis/     - Snapshots Redis"
echo "  • s3://$BUCKET_NAME/files/     - Arquivos diversos"

################################################################################
# 8. CRIAR POLÍTICA IAM (Opcional)
################################################################################

print_header "8. CRIANDO BUCKET POLICY"

print_info "Configurando bucket policy..."

cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowEC2Access",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::206749730888:root"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::$BUCKET_NAME",
                "arn:aws:s3:::$BUCKET_NAME/*"
            ]
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file://bucket-policy.json 2>/dev/null || print_warning "Policy não aplicada (pode já existir)"

print_success "Bucket policy configurada"

################################################################################
# 9. SALVAR INFORMAÇÕES
################################################################################

print_header "9. SALVANDO INFORMAÇÕES"

cat > s3-backup-info.txt << EOF
MaraBet AI - S3 Backup Bucket
==============================

Bucket Name:          $BUCKET_NAME
Region:               $REGION
URL:                  s3://$BUCKET_NAME
Console URL:          https://s3.console.aws.amazon.com/s3/buckets/$BUCKET_NAME

Configurações:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Versionamento:        ✅ Habilitado
Encriptação:          ✅ AES256
Acesso Público:       ❌ Bloqueado
Lifecycle Policy:     ✅ Configurada

Retenção:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Daily:                30 dias
Weekly:               90 dias
Monthly:              365 dias (→ Glacier após 90 dias)

Estrutura:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

s3://$BUCKET_NAME/
├── daily/            Backups diários (30 dias)
├── weekly/           Backups semanais (90 dias)
├── monthly/          Backups mensais (365 dias)
├── database/         Dumps PostgreSQL
├── redis/            Snapshots Redis
└── files/            Arquivos diversos

Comandos Úteis:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Listar backups:
  aws s3 ls s3://$BUCKET_NAME/ --recursive --human-readable

Upload backup:
  aws s3 cp backup.sql.gz s3://$BUCKET_NAME/daily/backup-\$(date +%Y%m%d).sql.gz

Download backup:
  aws s3 cp s3://$BUCKET_NAME/daily/backup-20251027.sql.gz ./

Sincronizar pasta:
  aws s3 sync /opt/marabet/backups/ s3://$BUCKET_NAME/daily/

Ver tamanho total:
  aws s3 ls s3://$BUCKET_NAME --recursive --summarize --human-readable

Custos:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

S3 Standard:          \$0.023 por GB/mês
S3 Glacier:           \$0.004 por GB/mês
Requests PUT:         \$0.005 por 1.000
Requests GET:         \$0.0004 por 1.000

Estimativa (100GB backups):
  Primeiros 3 meses:  ~\$2.30/mês (S3 Standard)
  Após 3 meses:       ~\$0.70/mês (Glacier)

Criado em:            $(date)
EOF

print_success "s3-backup-info.txt criado"

################################################################################
# RESUMO
################################################################################

print_header "✅ BUCKET S3 CONFIGURADO!"

echo ""
echo "Bucket S3:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Nome:              ${GREEN}$BUCKET_NAME${NC}"
echo "  Região:            $REGION"
echo "  URL:               s3://$BUCKET_NAME"
echo ""
echo "  Versionamento:     ✅ Habilitado"
echo "  Encriptação:       ✅ AES256"
echo "  Acesso Público:    ❌ Bloqueado"
echo "  Lifecycle:         ✅ 30/90/365 dias"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Próximos Passos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. Criar script de backup:"
echo "     ${GREEN}Ver: criar_backup_automatico.sh${NC}"
echo ""
echo "  2. Testar upload:"
echo "     ${GREEN}echo 'test' > test.txt${NC}"
echo "     ${GREEN}aws s3 cp test.txt s3://$BUCKET_NAME/test/test.txt${NC}"
echo ""
echo "  3. Verificar:"
echo "     ${GREEN}aws s3 ls s3://$BUCKET_NAME/${NC}"
echo ""
echo "  4. Configurar cron para backup automático"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_success "Informações salvas em: s3-backup-info.txt"

echo ""
print_header "✅ CONCLUÍDO!"
echo ""

