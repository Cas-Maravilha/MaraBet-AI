# Script de Teste PowerShell - MaraBet AI
# Execute no PowerShell do Windows

$PUBLIC_IP = "3.218.152.100"
$BASE_URL = "http://$PUBLIC_IP:8000"

Write-Host "🧪 MARABET AI - TESTES DA APLICAÇÃO" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "📅 Data/Hora: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor Yellow
Write-Host "🌐 URL Base: $BASE_URL" -ForegroundColor Cyan

# Teste 1: Health Check
Write-Host "`n🔍 TESTE 1: HEALTH CHECK" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "$BASE_URL/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Health Check: OK (Status: $($healthResponse.StatusCode))" -ForegroundColor Green
    Write-Host "📋 Resposta: $($healthResponse.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Health Check: Erro - $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 2: Documentação Swagger
Write-Host "`n🔍 TESTE 2: DOCUMENTAÇÃO SWAGGER" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {
    $docsResponse = Invoke-WebRequest -Uri "$BASE_URL/docs" -Method GET -TimeoutSec 10
    Write-Host "✅ Documentação Swagger: OK (Status: $($docsResponse.StatusCode))" -ForegroundColor Green
    Write-Host "🌐 Acesse no navegador: $BASE_URL/docs" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Documentação Swagger: Erro - $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 3: Predições
Write-Host "`n🔍 TESTE 3: PREDIÇÕES" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {
    $predictionsResponse = Invoke-WebRequest -Uri "$BASE_URL/predictions" -Method GET -TimeoutSec 10
    Write-Host "✅ Predições: OK (Status: $($predictionsResponse.StatusCode))" -ForegroundColor Green
    Write-Host "📋 Resposta: $($predictionsResponse.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Predições: Erro - $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 4: Análise
Write-Host "`n🔍 TESTE 4: ANÁLISE" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {
    $analysisResponse = Invoke-WebRequest -Uri "$BASE_URL/analysis" -Method GET -TimeoutSec 10
    Write-Host "✅ Análise: OK (Status: $($analysisResponse.StatusCode))" -ForegroundColor Green
    Write-Host "📋 Resposta: $($analysisResponse.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Análise: Erro - $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 5: Configuração
Write-Host "`n🔍 TESTE 5: CONFIGURAÇÃO" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {
    $configResponse = Invoke-WebRequest -Uri "$BASE_URL/config" -Method GET -TimeoutSec 10
    Write-Host "✅ Configuração: OK (Status: $($configResponse.StatusCode))" -ForegroundColor Green
    Write-Host "📋 Resposta: $($configResponse.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ Configuração: Erro - $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 6: API de Predição (POST)
Write-Host "`n🔍 TESTE 6: API DE PREDIÇÃO (POST)" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {
    $body = @{
        match_id = "12345"
        home_team = "Real Madrid"
        away_team = "Barcelona"
        league = "La Liga"
        match_date = "2024-01-15T20:00:00Z"
    } | ConvertTo-Json
    
    $predictResponse = Invoke-WebRequest -Uri "$BASE_URL/predict" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ API de Predição: OK (Status: $($predictResponse.StatusCode))" -ForegroundColor Green
    Write-Host "📋 Resposta: $($predictResponse.Content)" -ForegroundColor White
} catch {
    Write-Host "❌ API de Predição: Erro - $($_.Exception.Message)" -ForegroundColor Red
}

# Teste 7: Página Inicial
Write-Host "`n🔍 TESTE 7: PÁGINA INICIAL" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {
    $homeResponse = Invoke-WebRequest -Uri "$BASE_URL/" -Method GET -TimeoutSec 10
    Write-Host "✅ Página Inicial: OK (Status: $($homeResponse.StatusCode))" -ForegroundColor Green
    Write-Host "🌐 Acesse no navegador: $BASE_URL" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Página Inicial: Erro - $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 TESTES CONCLUÍDOS!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "🌐 URLs para acessar no navegador:" -ForegroundColor Cyan
Write-Host "  • Página Principal: $BASE_URL" -ForegroundColor White
Write-Host "  • Documentação: $BASE_URL/docs" -ForegroundColor White
Write-Host "  • Health Check: $BASE_URL/health" -ForegroundColor White
Write-Host "  • Predições: $BASE_URL/predictions" -ForegroundColor White
Write-Host "  • Análise: $BASE_URL/analysis" -ForegroundColor White
Write-Host "  • Configuração: $BASE_URL/config" -ForegroundColor White
