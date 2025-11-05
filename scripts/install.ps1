# Script de instalação para Windows - MaraBet AI
# PowerShell script para instalação e configuração do Docker

Write-Host "🔧 MARABET AI - INSTALAÇÃO WINDOWS" -ForegroundColor Blue
Write-Host "===================================" -ForegroundColor Blue

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

# Verificar se é Windows
if ($env:OS -ne "Windows_NT") {
    Write-Log "Este script é apenas para Windows" "ERROR"
    exit 1
}

# Verificar se está executando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Log "Execute como Administrador" "ERROR"
    Write-Host "Clique com botão direito no PowerShell e selecione 'Executar como administrador'" -ForegroundColor Yellow
    exit 1
}

# Verificar se Docker Desktop está instalado
Write-Log "Verificando Docker Desktop..."
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Log "Docker Desktop encontrado: $dockerVersion" "SUCCESS"
    } else {
        throw "Docker não encontrado"
    }
} catch {
    Write-Log "Docker Desktop não encontrado" "ERROR"
    Write-Log "Instale o Docker Desktop para Windows:" "WARNING"
    Write-Host "1. Acesse: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Write-Host "2. Baixe e instale o Docker Desktop" -ForegroundColor Yellow
    Write-Host "3. Reinicie o computador" -ForegroundColor Yellow
    Write-Host "4. Execute este script novamente" -ForegroundColor Yellow
    exit 1
}

# Verificar se Docker está rodando
Write-Log "Verificando se Docker está rodando..."
try {
    docker info | Out-Null
    Write-Log "Docker está rodando" "SUCCESS"
} catch {
    Write-Log "Docker não está rodando" "ERROR"
    Write-Log "Inicie o Docker Desktop e tente novamente" "WARNING"
    exit 1
}

# Verificar se Docker Compose está disponível
Write-Log "Verificando Docker Compose..."
try {
    $composeVersion = docker-compose --version 2>$null
    if ($composeVersion) {
        Write-Log "Docker Compose encontrado: $composeVersion" "SUCCESS"
    } else {
        throw "Docker Compose não encontrado"
    }
} catch {
    Write-Log "Docker Compose não encontrado" "ERROR"
    Write-Log "Docker Compose deve vir com o Docker Desktop" "WARNING"
    exit 1
}

# Criar diretórios necessários
Write-Log "Criando diretórios necessários..."
$directories = @("data", "logs", "reports", "nginx\ssl", "scripts", "backups")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Log "Diretório criado: $dir" "SUCCESS"
    } else {
        Write-Log "Diretório já existe: $dir" "WARNING"
    }
}

# Configurar arquivo .env
Write-Log "Configurando arquivo .env..."
$envContent = @"
# Configurações do MaraBet AI
# Gerado automaticamente em $(Get-Date)

# API Keys
API_FOOTBALL_KEY=747d6e19a2d3a435fdb7a419007a45fa
THE_ODDS_API_KEY=your_the_odds_api_key_here

# Telegram
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597

# Email
SMTP_USERNAME=kilamu_10@yahoo.com.br
SMTP_PASSWORD=your_yahoo_app_password_here
NOTIFICATION_EMAIL=kilamu_10@yahoo.com.br
ADMIN_EMAIL=kilamu_10@yahoo.com.br

# Banco de dados
DATABASE_URL=sqlite:///data/sports_data.db

# Redis
REDIS_URL=redis://redis:6379

# Aplicação
SECRET_KEY=$([System.Web.Security.Membership]::GeneratePassword(32, 0))
DEBUG=False
HOST=0.0.0.0
PORT=5000
"@

if (Test-Path ".env") {
    Copy-Item ".env" ".env.backup" -Force
    Write-Log "Backup do .env criado" "WARNING"
}

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Log "Arquivo .env criado com suas chaves configuradas" "SUCCESS"

# Gerar certificados SSL
Write-Log "Gerando certificados SSL..."
$certPath = "nginx\ssl\cert.pem"
$keyPath = "nginx\ssl\key.pem"

if (-not (Test-Path $certPath) -or -not (Test-Path $keyPath)) {
    try {
        # Usar OpenSSL se disponível
        $opensslPath = Get-Command openssl -ErrorAction SilentlyContinue
        if ($opensslPath) {
            $opensslCmd = "openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout `"$keyPath`" -out `"$certPath`" -subj `/C=BR/ST=SP/L=SaoPaulo/O=MaraBetAI/CN=localhost`"
            Invoke-Expression $opensslCmd
            Write-Log "Certificados SSL gerados" "SUCCESS"
        } else {
            Write-Log "OpenSSL não encontrado. Certificados SSL não gerados" "WARNING"
            Write-Log "Configure certificados SSL manualmente se necessário" "WARNING"
        }
    } catch {
        Write-Log "Erro ao gerar certificados SSL: $($_.Exception.Message)" "WARNING"
    }
} else {
    Write-Log "Certificados SSL já existem" "SUCCESS"
}

# Configurar firewall do Windows
Write-Log "Configurando firewall do Windows..."
try {
    # Permitir portas necessárias
    $ports = @(80, 443, 5000, 8000)
    foreach ($port in $ports) {
        try {
            New-NetFirewallRule -DisplayName "MaraBet AI Port $port" -Direction Inbound -Protocol TCP -LocalPort $port -Action Allow -ErrorAction SilentlyContinue | Out-Null
            Write-Log "Porta $port configurada no firewall" "SUCCESS"
        } catch {
            Write-Log "Erro ao configurar porta $port no firewall" "WARNING"
        }
    }
} catch {
    Write-Log "Erro ao configurar firewall: $($_.Exception.Message)" "WARNING"
}

# Testar instalação
Write-Log "Testando instalação..."
try {
    # Testar Docker
    docker --version | Out-Null
    Write-Log "Docker funcionando" "SUCCESS"
    
    # Testar Docker Compose
    docker-compose --version | Out-Null
    Write-Log "Docker Compose funcionando" "SUCCESS"
    
    # Testar se os arquivos necessários existem
    if ((Test-Path "docker-compose.yml") -and (Test-Path "Dockerfile")) {
        Write-Log "Arquivos de configuração encontrados" "SUCCESS"
    } else {
        throw "Arquivos de configuração não encontrados"
    }
} catch {
    Write-Log "Erro no teste: $($_.Exception.Message)" "ERROR"
    exit 1
}

# Mostrar próximos passos
Write-Host ""
Write-Log "Instalação concluída com sucesso!" "SUCCESS"
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Configure a senha de app do Yahoo no arquivo .env (opcional)" -ForegroundColor White
Write-Host "2. Execute: docker-compose up -d" -ForegroundColor White
Write-Host "3. Acesse: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "Comandos úteis:" -ForegroundColor Yellow
Write-Host "- Deploy: docker-compose up -d" -ForegroundColor White
Write-Host "- Logs: docker-compose logs -f" -ForegroundColor White
Write-Host "- Parar: docker-compose down" -ForegroundColor White
Write-Host "- Rebuild: docker-compose up --build -d" -ForegroundColor White
Write-Host ""
Write-Host "Arquivos importantes:" -ForegroundColor Yellow
Write-Host "- Configuração: .env" -ForegroundColor White
Write-Host "- Docker: docker-compose.yml" -ForegroundColor White
Write-Host "- Nginx: nginx\nginx.conf" -ForegroundColor White
Write-Host "- Scripts: scripts\" -ForegroundColor White
Write-Host ""
Write-Log "Sistema MaraBet AI pronto para uso!" "SUCCESS"
