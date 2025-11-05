# MaraBet AI - Obter Endpoint RDS (PowerShell)
# Obtém e salva todas as informações do RDS PostgreSQL

param(
    [string]$DBInstanceId = "database-1",
    [string]$Region = "eu-west-1",
    [string]$SecretId = "rds!db-3758a324-12a2-4675-b5ff-b92acdf38483"
)

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "🗄️  MARABET AI - OBTER ENDPOINT RDS" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[ℹ] RDS Instance: $DBInstanceId" -ForegroundColor Blue
Write-Host "[ℹ] Região: $Region" -ForegroundColor Blue
Write-Host ""

################################################################################
# 1. VERIFICAR RDS
################################################################################

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "1. VERIFICANDO RDS" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[ℹ] Consultando RDS Instance..." -ForegroundColor Blue

try {
    $rdsInfo = aws rds describe-db-instances `
        --db-instance-identifier $DBInstanceId `
        --region $Region `
        --output json | ConvertFrom-Json
    
    $db = $rdsInfo.DBInstances[0]
    $status = $db.DBInstanceStatus
    
    if ($status -eq "available") {
        Write-Host "[✓] RDS Status: available" -ForegroundColor Green
    } elseif ($status -eq "creating") {
        Write-Host "[!] RDS Status: creating (aguardando...)" -ForegroundColor Yellow
        
        Write-Host "[ℹ] Aguardando RDS ficar disponível..." -ForegroundColor Blue
        aws rds wait db-instance-available `
            --db-instance-identifier $DBInstanceId `
            --region $Region
        
        Write-Host "[✓] RDS agora disponível!" -ForegroundColor Green
    } else {
        Write-Host "[!] RDS Status: $status" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "[✗] Erro ao consultar RDS: $_" -ForegroundColor Red
    exit 1
}

################################################################################
# 2. OBTER ENDPOINT
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "2. OBTENDO ENDPOINT" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

$endpoint = $db.Endpoint.Address
$port = $db.Endpoint.Port

if ([string]::IsNullOrEmpty($endpoint)) {
    Write-Host "[✗] Endpoint não disponível!" -ForegroundColor Red
    exit 1
}

Write-Host "[✓] Endpoint: $endpoint" -ForegroundColor Green
Write-Host "[✓] Porta: $port" -ForegroundColor Green

################################################################################
# 3. INFORMAÇÕES COMPLETAS
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "3. INFORMAÇÕES COMPLETAS" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

$engine = $db.Engine
$engineVersion = $db.EngineVersion
$instanceClass = $db.DBInstanceClass
$storage = $db.AllocatedStorage
$multiAZ = $db.MultiAZ
$encrypted = $db.StorageEncrypted
$backupRetention = $db.BackupRetentionPeriod
$az = $db.AvailabilityZone

Write-Host "[ℹ] Engine: $engine $engineVersion" -ForegroundColor Blue
Write-Host "[ℹ] Instance Class: $instanceClass" -ForegroundColor Blue
Write-Host "[ℹ] Storage: $storage GB" -ForegroundColor Blue
Write-Host "[ℹ] Multi-AZ: $multiAZ" -ForegroundColor Blue
Write-Host "[ℹ] Encrypted: $encrypted" -ForegroundColor Blue
Write-Host "[ℹ] Backup Retention: $backupRetention dias" -ForegroundColor Blue
Write-Host "[ℹ] Availability Zone: $az" -ForegroundColor Blue

################################################################################
# 4. OBTER CREDENCIAIS
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "4. OBTENDO CREDENCIAIS DO SECRETS MANAGER" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

try {
    $secretValue = aws secretsmanager get-secret-value `
        --secret-id $SecretId `
        --region $Region `
        --query 'SecretString' `
        --output text
    
    $secret = $secretValue | ConvertFrom-Json
    
    $dbUser = $secret.username
    $dbPassword = $secret.password
    
    Write-Host "[✓] Credenciais obtidas do Secrets Manager" -ForegroundColor Green
    Write-Host "[ℹ] Username: $dbUser" -ForegroundColor Blue
    Write-Host "[ℹ] Password: $('*' * $dbPassword.Length)" -ForegroundColor Blue
    
} catch {
    Write-Host "[!] Não foi possível obter credenciais do Secrets Manager" -ForegroundColor Yellow
    $dbUser = "admin"
    $dbPassword = "[SENHA_DO_RDS]"
}

################################################################################
# 5. GERAR ARQUIVOS
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "5. GERANDO ARQUIVOS DE CONFIGURAÇÃO" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# rds-endpoint.txt
Write-Host "[ℹ] Criando rds-endpoint.txt..." -ForegroundColor Blue

@"
MaraBet AI - RDS PostgreSQL Endpoint
=====================================

RDS Instance ID:    $DBInstanceId
Status:             $status
Region:             $Region
Availability Zone:  $az

Endpoint:           $endpoint
Port:               $port

Engine:             $engine $engineVersion
Instance Class:     $instanceClass
Storage:            $storage GB
Multi-AZ:           $multiAZ
Encrypted:          $encrypted
Backup Retention:   $backupRetention dias

Database:           marabet_production
Username:           $dbUser
Password:           $dbPassword

ARN:                arn:aws:rds:${Region}:206749730888:db:${DBInstanceId}
Secret ARN:         arn:aws:secretsmanager:${Region}:206749730888:secret:${SecretId}-BpTjIS

Generated:          $(Get-Date)
"@ | Out-File -FilePath "rds-endpoint.txt" -Encoding UTF8

Write-Host "[✓] rds-endpoint.txt criado" -ForegroundColor Green

# .env.rds
Write-Host "[ℹ] Criando .env.rds..." -ForegroundColor Blue

@"
# MaraBet AI - RDS PostgreSQL Configuration
# Generated: $(Get-Date)

# Database Connection
DATABASE_URL=postgresql://${dbUser}:${dbPassword}@${endpoint}:${port}/marabet_production?sslmode=require
DB_HOST=$endpoint
DB_PORT=$port
DB_NAME=marabet_production
DB_USER=$dbUser
DB_PASSWORD=$dbPassword
DB_SSL_MODE=require

# RDS Instance Info
RDS_INSTANCE_ID=$DBInstanceId
RDS_ENDPOINT=$endpoint
RDS_ENGINE=$engine
RDS_VERSION=$engineVersion
RDS_CLASS=$instanceClass
RDS_MULTI_AZ=$multiAZ

# AWS Configuration
AWS_REGION=$Region
AWS_ACCOUNT_ID=206749730888

# Secrets Manager
SECRET_ID=$SecretId
SECRET_ARN=arn:aws:secretsmanager:${Region}:206749730888:secret:${SecretId}-BpTjIS
"@ | Out-File -FilePath ".env.rds" -Encoding UTF8

Write-Host "[✓] .env.rds criado" -ForegroundColor Green

# rds-config.json
Write-Host "[ℹ] Criando rds-config.json..." -ForegroundColor Blue

$config = @{
    rds = @{
        instance_id = $DBInstanceId
        status = $status
        region = $Region
        availability_zone = $az
        endpoint = $endpoint
        port = $port
        engine = $engine
        engine_version = $engineVersion
        instance_class = $instanceClass
        allocated_storage_gb = $storage
        multi_az = $multiAZ
        storage_encrypted = $encrypted
        backup_retention_days = $backupRetention
        arn = "arn:aws:rds:${Region}:206749730888:db:${DBInstanceId}"
    }
    database = @{
        name = "marabet_production"
        username = $dbUser
        password = $dbPassword
    }
    secrets_manager = @{
        secret_id = $SecretId
        secret_arn = "arn:aws:secretsmanager:${Region}:206749730888:secret:${SecretId}-BpTjIS"
        version_id = "c55b9938-e4de-439a-9ccd-59c7a57ed978"
    }
    connection_strings = @{
        postgresql = "postgresql://${dbUser}:${dbPassword}@${endpoint}:${port}/marabet_production?sslmode=require"
        jdbc = "jdbc:postgresql://${endpoint}:${port}/marabet_production?sslmode=require"
        django = "postgres://${dbUser}:${dbPassword}@${endpoint}:${port}/marabet_production"
        rails = "postgresql://${dbUser}:${dbPassword}@${endpoint}:${port}/marabet_production"
    }
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

$config | ConvertTo-Json -Depth 10 | Out-File -FilePath "rds-config.json" -Encoding UTF8

Write-Host "[✓] rds-config.json criado" -ForegroundColor Green

################################################################################
# RESUMO
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "✅ ENDPOINT RDS OBTIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "RDS PostgreSQL:" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "  Instance ID:       $DBInstanceId" -ForegroundColor White
Write-Host "  Status:            $status" -ForegroundColor White
Write-Host "  Endpoint:          $endpoint" -ForegroundColor Yellow
Write-Host "  Port:              $port" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Engine:            $engine $engineVersion" -ForegroundColor White
Write-Host "  Class:             $instanceClass" -ForegroundColor White
Write-Host "  Storage:           $storage GB" -ForegroundColor White
Write-Host "  Multi-AZ:          $multiAZ" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "Connection String:" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "  postgresql://${dbUser}:${dbPassword}@${endpoint}:${port}/marabet_production?sslmode=require" -ForegroundColor Yellow
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

Write-Host "Arquivos Criados:" -ForegroundColor White
Write-Host "  📄 rds-endpoint.txt" -ForegroundColor Cyan
Write-Host "  📄 .env.rds" -ForegroundColor Cyan
Write-Host "  📄 rds-config.json" -ForegroundColor Cyan
Write-Host "  📄 export-rds-vars.sh" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ CONCLUÍDO!" -ForegroundColor Green
Write-Host ""

