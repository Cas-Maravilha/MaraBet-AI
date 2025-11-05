# Instalação Docker Desktop no Windows - MaraBet AI
# Script PowerShell para instalar Docker + Docker Compose

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🐳 MARABET AI - INSTALAÇÃO DOCKER DESKTOP" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "📅 Data/Hora: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor White
Write-Host "📞 Contato: +224 932027393" -ForegroundColor White
Write-Host ""

# Verificar se está rodando como Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  ATENÇÃO: Este script precisa ser executado como ADMINISTRADOR!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Para executar como Administrador:" -ForegroundColor White
    Write-Host "   1. Clique com botão direito no PowerShell" -ForegroundColor White
    Write-Host "   2. Selecione 'Executar como Administrador'" -ForegroundColor White
    Write-Host "   3. Execute novamente: .\install_docker.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ Executando como Administrador!" -ForegroundColor Green
Write-Host ""

# Função para verificar versão do Windows
function Check-WindowsVersion {
    Write-Host "📋 PASSO 1: VERIFICAR VERSÃO DO WINDOWS" -ForegroundColor Cyan
    Write-Host "------------------------------------------------------------" -ForegroundColor Gray
    
    $osInfo = Get-CimInstance Win32_OperatingSystem
    $buildNumber = [System.Environment]::OSVersion.Version.Build
    
    Write-Host "📊 Sistema: $($osInfo.Caption)" -ForegroundColor White
    Write-Host "📊 Versão: $($osInfo.Version)" -ForegroundColor White
    Write-Host "📊 Build: $buildNumber" -ForegroundColor White
    Write-Host ""
    
    if ($buildNumber -lt 19041) {
        Write-Host "❌ Windows muito antigo! Build mínimo: 19041" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✅ Versão do Windows compatível!" -ForegroundColor Green
    return $true
}

# Função para instalar WSL2
function Install-WSL2 {
    Write-Host ""
    Write-Host "📋 PASSO 2: INSTALAR WSL2" -ForegroundColor Cyan
    Write-Host "------------------------------------------------------------" -ForegroundColor Gray
    
    try {
        $wslStatus = wsl --status 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ WSL2 já está instalado!" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "⚠️  WSL2 não encontrado. Instalando..." -ForegroundColor Yellow
    }
    
    try {
        Write-Host "🔧 Habilitando recursos do Windows..." -ForegroundColor White
        
        # Habilitar recursos necessários
        dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
        dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
        
        Write-Host "📥 Instalando WSL2..." -ForegroundColor White
        wsl --install --no-distribution
        
        Write-Host "✅ WSL2 instalado com sucesso!" -ForegroundColor Green
        Write-Host "⚠️  IMPORTANTE: Você precisa REINICIAR o computador!" -ForegroundColor Yellow
        
        return $true
    } catch {
        Write-Host "❌ Erro ao instalar WSL2: $_" -ForegroundColor Red
        return $false
    }
}

# Função para instalar Docker Desktop via winget
function Install-DockerDesktop-Winget {
    Write-Host ""
    Write-Host "📋 PASSO 3: INSTALAR DOCKER DESKTOP (WINGET)" -ForegroundColor Cyan
    Write-Host "------------------------------------------------------------" -ForegroundColor Gray
    
    try {
        $wingetVersion = winget --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ winget não disponível!" -ForegroundColor Red
            return $false
        }
        
        Write-Host "✅ winget versão: $wingetVersion" -ForegroundColor Green
        Write-Host "📥 Instalando Docker Desktop..." -ForegroundColor White
        
        winget install Docker.DockerDesktop --accept-source-agreements --accept-package-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Docker Desktop instalado com sucesso!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Falha ao instalar via winget" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Erro ao instalar via winget: $_" -ForegroundColor Red
        return $false
    }
}

# Função para instalar Docker Desktop via Chocolatey
function Install-DockerDesktop-Chocolatey {
    Write-Host ""
    Write-Host "📋 PASSO 4: INSTALAR DOCKER DESKTOP (CHOCOLATEY)" -ForegroundColor Cyan
    Write-Host "------------------------------------------------------------" -ForegroundColor Gray
    
    try {
        $chocoVersion = choco --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Chocolatey não disponível!" -ForegroundColor Red
            Write-Host "📋 Instale chocolatey de: https://chocolatey.org/install" -ForegroundColor White
            return $false
        }
        
        Write-Host "✅ Chocolatey versão: $chocoVersion" -ForegroundColor Green
        Write-Host "📥 Instalando Docker Desktop..." -ForegroundColor White
        
        choco install docker-desktop -y
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Docker Desktop instalado com sucesso!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Falha ao instalar via Chocolatey" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Erro ao instalar via Chocolatey: $_" -ForegroundColor Red
        return $false
    }
}

# Função para fornecer instruções de download manual
function Show-ManualInstallation {
    Write-Host ""
    Write-Host "📋 PASSO 5: DOWNLOAD MANUAL DO DOCKER DESKTOP" -ForegroundColor Cyan
    Write-Host "------------------------------------------------------------" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📥 Para instalar manualmente:" -ForegroundColor White
    Write-Host ""
    Write-Host "1️⃣  Acesse: https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host "2️⃣  Clique em 'Download for Windows'" -ForegroundColor White
    Write-Host "3️⃣  Execute o instalador 'Docker Desktop Installer.exe'" -ForegroundColor White
    Write-Host "4️⃣  Siga as instruções do instalador" -ForegroundColor White
    Write-Host "5️⃣  Reinicie o computador se solicitado" -ForegroundColor White
    Write-Host ""
    Write-Host "🔗 Link direto:" -ForegroundColor White
    Write-Host "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe" -ForegroundColor Cyan
    Write-Host ""
    
    # Abrir página de download
    $response = Read-Host "Deseja abrir a página de download? (S/N)"
    if ($response -eq "S" -or $response -eq "s") {
        Start-Process "https://www.docker.com/products/docker-desktop"
    }
}

# Função para verificar instalação do Docker
function Verify-DockerInstallation {
    Write-Host ""
    Write-Host "📋 PASSO 6: VERIFICAR INSTALAÇÃO DO DOCKER" -ForegroundColor Cyan
    Write-Host "------------------------------------------------------------" -ForegroundColor Gray
    
    # Aguardar um pouco para o Docker estar disponível
    Start-Sleep -Seconds 5
    
    # Verificar Docker
    Write-Host "🔍 Verificando Docker..." -ForegroundColor White
    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ Docker não encontrado!" -ForegroundColor Red
            Write-Host "⚠️  Você pode precisar:" -ForegroundColor Yellow
            Write-Host "  1. Reiniciar o computador" -ForegroundColor White
            Write-Host "  2. Abrir o Docker Desktop manualmente" -ForegroundColor White
            Write-Host "  3. Aguardar o Docker inicializar" -ForegroundColor White
            return $false
        }
    } catch {
        Write-Host "❌ Docker não encontrado!" -ForegroundColor Red
        return $false
    }
    
    # Verificar Docker Compose
    Write-Host "🔍 Verificando Docker Compose..." -ForegroundColor White
    try {
        $composeVersion = docker-compose --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Docker Compose: $composeVersion" -ForegroundColor Green
        } else {
            # Tentar versão V2
            $composeVersion = docker compose version 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Docker Compose V2: $composeVersion" -ForegroundColor Green
            } else {
                Write-Host "❌ Docker Compose não encontrado!" -ForegroundColor Red
                return $false
            }
        }
    } catch {
        Write-Host "❌ Docker Compose não encontrado!" -ForegroundColor Red
        return $false
    }
    
    # Testar Docker
    Write-Host ""
    Write-Host "🧪 Testando Docker..." -ForegroundColor White
    try {
        docker run --rm hello-world 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Docker está funcionando corretamente!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Falha ao executar container de teste" -ForegroundColor Red
            Write-Host "⚠️  Possíveis causas:" -ForegroundColor Yellow
            Write-Host "  1. Docker Desktop não está rodando" -ForegroundColor White
            Write-Host "  2. WSL2 não está configurado" -ForegroundColor White
            Write-Host "  3. Hyper-V não está habilitado" -ForegroundColor White
            return $false
        }
    } catch {
        Write-Host "❌ Falha ao executar container de teste" -ForegroundColor Red
        return $false
    }
}

# Função para exibir próximos passos
function Show-NextSteps {
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "🎯 PRÓXIMOS PASSOS" -ForegroundColor Cyan
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 DOCKER INSTALADO COM SUCESSO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "1️⃣  VERIFICAR DOCKER DESKTOP:" -ForegroundColor White
    Write-Host "   • Abra o Docker Desktop" -ForegroundColor Gray
    Write-Host "   • Aguarde a inicialização completa" -ForegroundColor Gray
    Write-Host "   • Verifique se está rodando (ícone na bandeja)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2️⃣  CONFIGURAR RECURSOS:" -ForegroundColor White
    Write-Host "   • Docker Desktop → Settings → Resources" -ForegroundColor Gray
    Write-Host "   • CPUs: 4" -ForegroundColor Gray
    Write-Host "   • Memória: 8GB" -ForegroundColor Gray
    Write-Host "   • Disco: 20GB" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3️⃣  TESTAR MARABET AI:" -ForegroundColor White
    Write-Host "   cd 'd:\Usuario\Maravilha\Desktop\MaraBet AI'" -ForegroundColor Gray
    Write-Host "   docker-compose -f docker-compose.production.yml up -d" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4️⃣  VERIFICAR CONTAINERS:" -ForegroundColor White
    Write-Host "   docker ps" -ForegroundColor Gray
    Write-Host "   docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor Gray
    Write-Host ""
    Write-Host "5️⃣  ACESSAR APLICAÇÃO:" -ForegroundColor White
    Write-Host "   • Web: http://localhost:80" -ForegroundColor Gray
    Write-Host "   • API: http://localhost:8000" -ForegroundColor Gray
    Write-Host "   • Dashboard: http://localhost:8501" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📞 SUPORTE:" -ForegroundColor White
    Write-Host "   • Telefone/WhatsApp: +224 932027393" -ForegroundColor Gray
    Write-Host "   • Telegram: @marabet_support" -ForegroundColor Gray
    Write-Host "   • Email: suporte@marabet.ai" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🎉 PARABÉNS! Docker está pronto para uso!" -ForegroundColor Green
    Write-Host ""
}

# MAIN - Executar instalação
Write-Host "🚀 Iniciando instalação do Docker Desktop..." -ForegroundColor White
Write-Host ""

# 1. Verificar Windows
if (-not (Check-WindowsVersion)) {
    Write-Host ""
    Write-Host "❌ Sistema não compatível!" -ForegroundColor Red
    exit 1
}

# 2. Instalar WSL2
$wslInstalled = Install-WSL2
if ($wslInstalled) {
    Write-Host ""
    Write-Host "⚠️  REINICIE o computador antes de continuar!" -ForegroundColor Yellow
    $restart = Read-Host "Deseja continuar a instalação agora? (S/N)"
    if ($restart -ne "S" -and $restart -ne "s") {
        Write-Host "⏸️  Instalação pausada. Execute novamente após reiniciar." -ForegroundColor Yellow
        exit 0
    }
}

# 3. Instalar Docker Desktop
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🔄 MÉTODOS DE INSTALAÇÃO DISPONÍVEIS:" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "1. 🟢 winget (Recomendado)" -ForegroundColor White
Write-Host "2. 🟡 chocolatey (Alternativo)" -ForegroundColor White
Write-Host "3. 🔴 Download manual (Última opção)" -ForegroundColor White
Write-Host ""

$dockerInstalled = $false

# Tentar winget
if (Install-DockerDesktop-Winget) {
    $dockerInstalled = $true
}
# Tentar Chocolatey
elseif (Install-DockerDesktop-Chocolatey) {
    $dockerInstalled = $true
}
# Manual
else {
    Show-ManualInstallation
    Write-Host ""
    Write-Host "📋 Após instalar manualmente, execute este script novamente para verificar." -ForegroundColor White
    exit 0
}

if ($dockerInstalled) {
    Write-Host ""
    Write-Host "⏰ AGUARDE..." -ForegroundColor Yellow
    Write-Host "O Docker Desktop está sendo instalado." -ForegroundColor White
    Write-Host "Este processo pode levar alguns minutos." -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
    Write-Host "• Você precisará REINICIAR o computador" -ForegroundColor White
    Write-Host "• Após reiniciar, abra o Docker Desktop manualmente" -ForegroundColor White
    Write-Host "• Aguarde o Docker inicializar completamente" -ForegroundColor White
    Write-Host ""
    
    Read-Host "🔄 Pressione ENTER após reiniciar e abrir o Docker Desktop"
    
    # Verificar instalação
    if (Verify-DockerInstallation) {
        Write-Host ""
        Write-Host "✅ DOCKER INSTALADO E FUNCIONANDO!" -ForegroundColor Green
        Show-NextSteps
        exit 0
    } else {
        Write-Host ""
        Write-Host "⚠️  Docker instalado mas não está funcionando corretamente." -ForegroundColor Yellow
        Write-Host "📋 Verifique:" -ForegroundColor White
        Write-Host "  1. Docker Desktop está aberto e rodando?" -ForegroundColor White
        Write-Host "  2. WSL2 está instalado?" -ForegroundColor White
        Write-Host "  3. Computador foi reiniciado?" -ForegroundColor White
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "❌ Falha ao instalar Docker Desktop" -ForegroundColor Red
    exit 1
}

