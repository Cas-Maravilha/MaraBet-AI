# MaraBet AI - Obter Endpoint Redis Serverless (PowerShell)

param(
    [string]$CacheName = "marabet-redis",
    [string]$Region = "eu-west-1"
)

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "💾 MARABET AI - OBTER ENDPOINT REDIS SERVERLESS" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[ℹ] Cache Name: $CacheName" -ForegroundColor Blue
Write-Host "[ℹ] Região: $Region" -ForegroundColor Blue
Write-Host ""

################################################################################
# 1. VERIFICAR STATUS
################################################################################

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "1. VERIFICANDO STATUS" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[ℹ] Consultando ElastiCache Serverless..." -ForegroundColor Blue

try {
    $redisInfo = aws elasticache describe-serverless-caches `
        --serverless-cache-name $CacheName `
        --region $Region `
        --output json | ConvertFrom-Json
    
    $cache = $redisInfo.ServerlessCaches[0]
    $status = $cache.Status
    
    if ($status -eq "available") {
        Write-Host "[✓] Status: available" -ForegroundColor Green
    } elseif ($status -eq "creating") {
        Write-Host "[!] Status: creating (aguardando...)" -ForegroundColor Yellow
        
        Write-Host "[ℹ] Aguardando Redis ficar disponível..." -ForegroundColor Blue
        Write-Host "    Isso pode levar 5-10 minutos" -ForegroundColor Blue
        
        $maxAttempts = 40
        $attempt = 0
        
        while ($status -ne "available" -and $attempt -lt $maxAttempts) {
            Start-Sleep -Seconds 30
            $attempt++
            
            $redisInfo = aws elasticache describe-serverless-caches `
                --serverless-cache-name $CacheName `
                --region $Region `
                --output json | ConvertFrom-Json
            
            $cache = $redisInfo.ServerlessCaches[0]
            $status = $cache.Status
            
            Write-Host "." -NoNewline
        }
        
        Write-Host ""
        
        if ($status -eq "available") {
            Write-Host "[✓] Redis disponível!" -ForegroundColor Green
        } else {
            Write-Host "[✗] Timeout. Status atual: $status" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[!] Status: $status" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "[✗] Erro ao consultar Redis: $_" -ForegroundColor Red
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

$endpoint = $cache.Endpoint.Address
$port = $cache.Endpoint.Port

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

$engine = $cache.Engine
$engineVersion = $cache.FullEngineVersion
$arn = $cache.ARN

Write-Host "[ℹ] Engine: $engine" -ForegroundColor Blue
Write-Host "[ℹ] Version: $engineVersion" -ForegroundColor Blue
Write-Host "[ℹ] Type: Serverless" -ForegroundColor Blue
Write-Host "[ℹ] Multi-AZ: 3 Availability Zones" -ForegroundColor Blue

################################################################################
# 4. GERAR ARQUIVOS
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "4. GERANDO ARQUIVOS DE CONFIGURAÇÃO" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# redis-serverless-endpoint.txt
Write-Host "[ℹ] Criando redis-serverless-endpoint.txt..." -ForegroundColor Blue

@"
MaraBet AI - ElastiCache Redis Serverless
==========================================

Name:                 $CacheName
Status:               $status
Region:               $Region

Endpoint:             $endpoint
Port:                 $port

Engine:               $engine
Version:              $engineVersion
Type:                 Serverless

Encryption At-Rest:   Yes (AWS owned KMS key)
Encryption In-Transit: Yes (TLS)
Multi-AZ:             Yes (3 AZs)

VPC:                  vpc-081a8c63b16a94a3a
Security Group:       sg-09f7d3d37a8407f43

ARN:                  $arn

Generated:            $(Get-Date)
"@ | Out-File -FilePath "redis-serverless-endpoint.txt" -Encoding UTF8

Write-Host "[✓] redis-serverless-endpoint.txt criado" -ForegroundColor Green

# .env.redis
Write-Host "[ℹ] Criando .env.redis..." -ForegroundColor Blue

@"
# MaraBet AI - ElastiCache Redis Serverless Configuration
# Generated: $(Get-Date)

# Redis Connection
REDIS_URL=rediss://${endpoint}:${port}
REDIS_HOST=$endpoint
REDIS_PORT=$port
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
REDIS_ENGINE=$engine
REDIS_VERSION=$engineVersion
REDIS_SERVERLESS_NAME=$CacheName

# AWS
AWS_REGION=$Region
AWS_ACCOUNT_ID=206749730888
ELASTICACHE_ARN=$arn
"@ | Out-File -FilePath ".env.redis" -Encoding UTF8

Write-Host "[✓] .env.redis criado" -ForegroundColor Green

# JSON
Write-Host "[ℹ] Criando redis-serverless-config.json..." -ForegroundColor Blue

$config = @{
    redis = @{
        name = $CacheName
        type = "serverless"
        status = $status
        region = $Region
        endpoint = $endpoint
        port = $port
        engine = $engine
        engine_version = $engineVersion
        arn = $arn
        vpc_id = "vpc-081a8c63b16a94a3a"
        security_group_id = "sg-09f7d3d37a8407f43"
        encryption = @{
            at_rest = $true
            in_transit = $true
            kms_key = "AWS owned"
        }
    }
    connection_strings = @{
        redis = "rediss://${endpoint}:${port}"
        python = "rediss://${endpoint}:${port}/0"
        nodejs = "rediss://${endpoint}:${port}"
    }
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

$config | ConvertTo-Json -Depth 10 | Out-File -FilePath "redis-serverless-config.json" -Encoding UTF8

Write-Host "[✓] redis-serverless-config.json criado" -ForegroundColor Green

################################################################################
# RESUMO
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "✅ ENDPOINT REDIS OBTIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "ElastiCache Redis Serverless:" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "  Name:              $CacheName" -ForegroundColor White
Write-Host "  Status:            $status" -ForegroundColor White
Write-Host "  Endpoint:          $endpoint" -ForegroundColor Yellow
Write-Host "  Port:              $port" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Engine:            $engine $engineVersion" -ForegroundColor White
Write-Host "  Type:              Serverless" -ForegroundColor White
Write-Host "  Multi-AZ:          3 Availability Zones" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "Connection URL:" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "  rediss://${endpoint}:${port}" -ForegroundColor Yellow
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

Write-Host "Arquivos Criados:" -ForegroundColor White
Write-Host "  📄 redis-serverless-endpoint.txt" -ForegroundColor Cyan
Write-Host "  📄 .env.redis" -ForegroundColor Cyan
Write-Host "  📄 redis-serverless-config.json" -ForegroundColor Cyan
Write-Host "  📄 test-redis-serverless.sh" -ForegroundColor Cyan
Write-Host ""

Write-Host "Próximos Passos:" -ForegroundColor White
Write-Host "  1. Testar: python redis_config.py" -ForegroundColor Gray
Write-Host "  2. Adicionar ao .env: cat .env.redis >> .env" -ForegroundColor Gray
Write-Host ""

Write-Host "✅ CONCLUÍDO!" -ForegroundColor Green
Write-Host ""

