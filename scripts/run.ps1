# Script de execução para Windows - MaraBet AI
# PowerShell script para executar comandos do sistema

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    [Parameter(Position=1)]
    [string]$Argument = ""
)

Write-Host "🚀 MARABET AI - EXECUTOR WINDOWS" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor Blue

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

# Verificar se Docker está rodando
function Test-Docker {
    try {
        docker info | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Função para deploy
function Start-Deploy {
    Write-Log "Iniciando deploy do MaraBet AI..."
    
    if (-not (Test-Docker)) {
        Write-Log "Docker não está rodando. Inicie o Docker Desktop primeiro." "ERROR"
        return
    }
    
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
    
    # Verificar status
    Write-Log "Verificando status dos serviços..."
    docker-compose ps
    
    Write-Log "Deploy concluído!" "SUCCESS"
    Write-Host "Acesse: http://localhost:8000" -ForegroundColor Green
}

# Função para parar serviços
function Stop-Services {
    Write-Log "Parando todos os serviços..."
    docker-compose down
    Write-Log "Serviços parados" "SUCCESS"
}

# Função para mostrar logs
function Show-Logs {
    param([string]$Service = "")
    
    if ($Service) {
        Write-Log "Mostrando logs do serviço: $Service"
        docker-compose logs -f $Service
    } else {
        Write-Log "Mostrando logs de todos os serviços..."
        docker-compose logs -f
    }
}

# Função para mostrar status
function Show-Status {
    Write-Log "Status dos serviços:"
    docker-compose ps
    
    Write-Host ""
    Write-Log "Uso de recursos:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Função para verificar saúde
function Test-Health {
    Write-Log "Verificando saúde dos serviços..."
    
    # Verificar containers
    $containers = docker-compose ps --format "{{.Name}}:{{.Status}}"
    foreach ($container in $containers) {
        $name, $status = $container.Split(":")
        if ($status -like "*Up*") {
            Write-Log "$name: $status" "SUCCESS"
        } else {
            Write-Log "$name: $status" "ERROR"
        }
    }
    
    # Verificar endpoints
    Write-Host ""
    Write-Log "Verificando endpoints..."
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10 -ErrorAction Stop
        Write-Log "Dashboard: OK" "SUCCESS"
    } catch {
        Write-Log "Dashboard: FALHOU" "ERROR"
    }
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 10 -ErrorAction Stop
        Write-Log "API: OK" "SUCCESS"
    } catch {
        Write-Log "API: FALHOU" "ERROR"
    }
}

# Função para backup
function Start-Backup {
    Write-Log "Iniciando backup..."
    
    $backupDir = "backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # Backup do banco de dados
    if (Test-Path "data\sports_data.db") {
        Copy-Item "data\sports_data.db" "$backupDir\" -Force
        Write-Log "Banco de dados copiado" "SUCCESS"
    }
    
    # Backup dos logs
    if (Test-Path "logs") {
        Copy-Item "logs" "$backupDir\" -Recurse -Force
        Write-Log "Logs copiados" "SUCCESS"
    }
    
    # Backup da configuração
    if (Test-Path ".env") {
        Copy-Item ".env" "$backupDir\" -Force
        Write-Log "Configuração copiada" "SUCCESS"
    }
    
    Write-Log "Backup criado em: $backupDir" "SUCCESS"
}

# Função para limpeza
function Start-Cleanup {
    Write-Log "Iniciando limpeza..."
    
    # Parar serviços
    docker-compose down
    
    # Limpar containers parados
    docker container prune -f
    
    # Limpar imagens não utilizadas
    docker image prune -f
    
    # Limpar volumes não utilizados
    docker volume prune -f
    
    Write-Log "Limpeza concluída" "SUCCESS"
}

# Função para rebuild
function Start-Rebuild {
    Write-Log "Iniciando rebuild..."
    
    # Parar serviços
    docker-compose down
    
    # Remover imagens antigas
    docker-compose down --rmi all
    
    # Build e iniciar
    docker-compose up --build -d
    
    Write-Log "Rebuild concluído" "SUCCESS"
}

# Função para mostrar ajuda
function Show-Help {
    Write-Host ""
    Write-Host "Comandos disponíveis:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  deploy     - Deploy completo do sistema" -ForegroundColor White
    Write-Host "  stop       - Parar todos os serviços" -ForegroundColor White
    Write-Host "  start      - Iniciar serviços existentes" -ForegroundColor White
    Write-Host "  restart    - Reiniciar todos os serviços" -ForegroundColor White
    Write-Host "  logs       - Mostrar logs (opcional: especificar serviço)" -ForegroundColor White
    Write-Host "  status     - Mostrar status dos serviços" -ForegroundColor White
    Write-Host "  health     - Verificar saúde dos serviços" -ForegroundColor White
    Write-Host "  backup     - Criar backup dos dados" -ForegroundColor White
    Write-Host "  cleanup    - Limpar containers e imagens antigas" -ForegroundColor White
    Write-Host "  rebuild    - Rebuild completo do sistema" -ForegroundColor White
    Write-Host "  help       - Mostrar esta ajuda" -ForegroundColor White
    Write-Host ""
    Write-Host "Exemplos:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 deploy" -ForegroundColor White
    Write-Host "  .\run.ps1 logs marabet-ai" -ForegroundColor White
    Write-Host "  .\run.ps1 health" -ForegroundColor White
    Write-Host ""
}

# Função principal
function Main {
    switch ($Command.ToLower()) {
        "deploy" {
            Start-Deploy
        }
        "stop" {
            Stop-Services
        }
        "start" {
            Write-Log "Iniciando serviços existentes..."
            docker-compose up -d
            Write-Log "Serviços iniciados" "SUCCESS"
        }
        "restart" {
            Write-Log "Reiniciando serviços..."
            docker-compose restart
            Write-Log "Serviços reiniciados" "SUCCESS"
        }
        "logs" {
            Show-Logs -Service $Argument
        }
        "status" {
            Show-Status
        }
        "health" {
            Test-Health
        }
        "backup" {
            Start-Backup
        }
        "cleanup" {
            Start-Cleanup
        }
        "rebuild" {
            Start-Rebuild
        }
        "help" {
            Show-Help
        }
        default {
            Write-Log "Comando não reconhecido: $Command" "ERROR"
            Show-Help
        }
    }
}

# Executar comando
Main
