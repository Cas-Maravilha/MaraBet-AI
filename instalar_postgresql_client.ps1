# Script para instalar PostgreSQL Client (psql) no Windows
# MaraBet AI - Instalação do cliente PostgreSQL

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📥 INSTALAÇÃO DO POSTGRESQL CLIENT (psql)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se já está instalado
Write-Host "🔍 Verificando se psql já está instalado..." -ForegroundColor Yellow
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue

if ($psqlPath) {
    Write-Host "✅ psql já está instalado: $($psqlPath.Source)" -ForegroundColor Green
    Write-Host ""
    Write-Host "🧪 Testando conexão..." -ForegroundColor Yellow
    
    # Testar conexão
    $env:PGPASSWORD = "ctcaddTcMaRVioDY4kso"
    $result = echo "SELECT version(); \q" | psql -h 37.27.220.67 -U meu_usuario -d meu_banco 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Conexão estabelecida com sucesso!" -ForegroundColor Green
        Write-Host $result
    } else {
        Write-Host "❌ Erro na conexão:" -ForegroundColor Red
        Write-Host $result
    }
    
    Remove-Item Env:\PGPASSWORD
    exit
}

Write-Host "❌ psql não encontrado" -ForegroundColor Red
Write-Host ""
Write-Host "📥 OPÇÕES DE INSTALAÇÃO:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  INSTALAR VIA CHOCOLATEY (Recomendado)" -ForegroundColor Cyan
Write-Host "    choco install postgresql --params '/Password:senha123'" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  BAIXAR INSTALADOR OFICIAL" -ForegroundColor Cyan
Write-Host "    https://www.postgresql.org/download/windows/" -ForegroundColor White
Write-Host "    - Baixe apenas o 'Command Line Tools'" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣  USAR PYTHON (Já disponível)" -ForegroundColor Cyan
Write-Host "    python testar_conexao_detalhado.py" -ForegroundColor White
Write-Host ""
Write-Host "4️⃣  USAR DOCKER (Se Docker estiver instalado)" -ForegroundColor Cyan
Write-Host "    docker run -it --rm postgres:15 psql -h 37.27.220.67 -U meu_usuario -d meu_banco" -ForegroundColor White
Write-Host ""

# Verificar se Chocolatey está instalado
$chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue

if ($chocoInstalled) {
    Write-Host "✅ Chocolatey encontrado!" -ForegroundColor Green
    Write-Host ""
    $install = Read-Host "Deseja instalar PostgreSQL client via Chocolatey? (S/N)"
    
    if ($install -eq "S" -or $install -eq "s") {
        Write-Host ""
        Write-Host "🔄 Instalando PostgreSQL client..." -ForegroundColor Yellow
        choco install postgresql --params '/Password:PostgreSQL123' -y
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ PostgreSQL client instalado com sucesso!" -ForegroundColor Green
            Write-Host ""
            Write-Host "🔄 Recarregando PATH..." -ForegroundColor Yellow
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            Write-Host "✅ Instalação concluída!" -ForegroundColor Green
            Write-Host ""
            Write-Host "🧪 Teste a conexão com:" -ForegroundColor Yellow
            Write-Host "   psql -h 37.27.220.67 -U meu_usuario -d meu_banco" -ForegroundColor White
        } else {
            Write-Host "❌ Erro na instalação" -ForegroundColor Red
        }
    }
} else {
    Write-Host "⚠️  Chocolatey não está instalado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Para instalar Chocolatey:" -ForegroundColor Cyan
    Write-Host "   Set-ExecutionPolicy Bypass -Scope Process -Force;" -ForegroundColor White
    Write-Host "   [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072;" -ForegroundColor White
    Write-Host "   iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "💡 ALTERNATIVA: Usar Python (já disponível)" -ForegroundColor Yellow
Write-Host "   python testar_conexao_detalhado.py" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan

