# Script de início rápido para Windows - MaraBet AI
# PowerShell script para configuração e deploy rápido

Write-Host "🚀 MARABET AI - INÍCIO RÁPIDO WINDOWS" -ForegroundColor Blue
Write-Host "=====================================" -ForegroundColor Blue

# Função para log
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        default { "Cyan" }
    }
    Write-Host "[$timestamp] $Message" -ForegroundColor $color
}

# Verificar se Docker está instalado
function Test-Docker {
    try {
        docker --version | Out-Null
        docker info | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Verificar se Docker Compose está instalado
function Test-DockerCompose {
    try {
        docker-compose --version | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Verificar arquivo .env
function Test-EnvFile {
    if (Test-Path ".env") {
        Write-Log "Arquivo .env encontrado" "SUCCESS"
        return $true
    } else {
        Write-Log "Arquivo .env não encontrado. Criando..." "WARNING"
        
        $envContent = @"
# Configurações do MaraBet AI
API_FOOTBALL_KEY=747d6e19a2d3a435fdb7a419007a45fa
THE_ODDS_API_KEY=your_the_odds_api_key_here
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597
SMTP_USERNAME=kilamu_10@yahoo.com.br
SMTP_PASSWORD=your_yahoo_app_password_here
NOTIFICATION_EMAIL=kilamu_10@yahoo.com.br
ADMIN_EMAIL=kilamu_10@yahoo.com.br
DATABASE_URL=sqlite:///data/sports_data.db
REDIS_URL=redis://redis:6379
SECRET_KEY=$([System.Web.Security.Membership]::GeneratePassword(32, 0))
DEBUG=False
HOST=0.0.0.0
PORT=5000
"@
        
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Log "Arquivo .env criado com suas chaves" "SUCCESS"
        return $true
    }
}

# Criar diretórios necessários
function New-RequiredDirectories {
    Write-Log "Criando diretórios necessários..."
    
    $directories = @("data", "logs", "reports", "nginx\ssl", "scripts", "backups")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Log "Diretório criado: $dir" "SUCCESS"
        }
    }
}

# Deploy do sistema
function Start-SystemDeploy {
    Write-Log "Iniciando deploy do sistema..."
    
    # Parar serviços existentes
    Write-Log "Parando serviços existentes..."
    docker-compose down 2>$null
    
    # Build das imagens
    Write-Log "Fazendo build das imagens..."
    docker-compose build --no-cache
    
    # Iniciar serviços
    Write-Log "Iniciando serviços..."
    docker-compose up -d
    
    # Aguardar serviços iniciarem
    Write-Log "Aguardando serviços iniciarem..."
    Start-Sleep -Seconds 30
    
    Write-Log "Sistema iniciado" "SUCCESS"
}

# Verificar saúde dos serviços
function Test-SystemHealth {
    Write-Log "Verificando saúde dos serviços..."
    
    # Aguardar um pouco mais
    Start-Sleep -Seconds 10
    
    # Verificar containers
    $containers = docker-compose ps --format "{{.Name}}:{{.Status}}"
    $allUp = $true
    
    foreach ($container in $containers) {
        $name, $status = $container.Split(":")
        if ($status -like "*Up*") {
            Write-Log "$name: $status" "SUCCESS"
        } else {
            Write-Log "$name: $status" "ERROR"
            $allUp = $false
        }
    }
    
    if ($allUp) {
        Write-Log "Todos os containers estão rodando" "SUCCESS"
    } else {
        Write-Log "Alguns containers não estão rodando" "ERROR"
    }
    
    return $allUp
}

# Testar endpoints
function Test-Endpoints {
    Write-Log "Testando endpoints..."
    
    # Aguardar serviços estarem prontos
    Start-Sleep -Seconds 20
    
    # Testar API
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 10 -ErrorAction Stop
        Write-Log "API: OK" "SUCCESS"
    } catch {
        Write-Log "API: Não respondeu (pode estar inicializando)" "WARNING"
    }
    
    # Testar Dashboard
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10 -ErrorAction Stop
        Write-Log "Dashboard: OK" "SUCCESS"
    } catch {
        Write-Log "Dashboard: Não respondeu (pode estar inicializando)" "WARNING"
    }
    
    # Testar Redis
    try {
        docker-compose exec redis redis-cli ping | Out-Null
        Write-Log "Redis: OK" "SUCCESS"
    } catch {
        Write-Log "Redis: Não respondeu (pode estar inicializando)" "WARNING"
    }
}

# Mostrar informações do sistema
function Show-SystemInfo {
    Write-Host ""
    Write-Log "Sistema MaraBet AI iniciado com sucesso!" "SUCCESS"
    Write-Host ""
    Write-Host "Informações do sistema:" -ForegroundColor Yellow
    Write-Host "======================" -ForegroundColor Yellow
    Write-Host "Dashboard: http://localhost:8000" -ForegroundColor White
    Write-Host "API: http://localhost:5000" -ForegroundColor White
    Write-Host "Nginx: http://localhost:80" -ForegroundColor White
    Write-Host ""
    Write-Host "Status dos containers:" -ForegroundColor Yellow
    docker-compose ps
    Write-Host ""
    Write-Host "Comandos úteis:" -ForegroundColor Yellow
    Write-Host "- Ver logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "- Parar: docker-compose down" -ForegroundColor White
    Write-Host "- Restart: docker-compose restart" -ForegroundColor White
    Write-Host "- Status: docker-compose ps" -ForegroundColor White
    Write-Host "- Monitor: .\scripts\run.ps1 status" -ForegroundColor White
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Yellow
    Write-Host "1. Acesse o dashboard: http://localhost:8000" -ForegroundColor White
    Write-Host "2. Configure notificações (opcional)" -ForegroundColor White
    Write-Host "3. Monitore o sistema: .\scripts\run.ps1 status" -ForegroundColor White
    Write-Host ""
    Write-Log "Sistema pronto para uso!" "SUCCESS"
}

# Função principal
function Main {
    Write-Log "Iniciando configuração rápida do MaraBet AI..."
    
    # Verificações básicas
    if (-not (Test-Docker)) {
        Write-Log "Docker não está instalado ou não está rodando" "ERROR"
        Write-Log "Execute: .\scripts\install.ps1" "WARNING"
        exit 1
    }
    
    if (-not (Test-DockerCompose)) {
        Write-Log "Docker Compose não está instalado" "ERROR"
        Write-Log "Execute: .\scripts\install.ps1" "WARNING"
        exit 1
    }
    
    Test-EnvFile
    New-RequiredDirectories
    
    # Deploy
    Start-SystemDeploy
    
    # Verificações pós-deploy
    $healthOk = Test-SystemHealth
    Test-Endpoints
    
    # Mostrar informações
    Show-SystemInfo
    
    if (-not $healthOk) {
        Write-Log "Sistema iniciado com alguns problemas. Verifique os logs." "WARNING"
        Write-Log "Execute: docker-compose logs -f" "WARNING"
    }
}

# Executar
Main
