# Script PowerShell para conectar ao PostgreSQL
# MaraBet AI - Conexão com banco de dados

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔍 CONEXÃO POSTGRESQL - MARABET AI" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Credenciais
$host = "37.27.220.67"
$port = "5432"
$database = "meu_banco"
$username = "meu_usuario"
$password = "ctcaddTcMaRVioDY4kso"

Write-Host "📋 Credenciais de Conexão:" -ForegroundColor Yellow
Write-Host "   Host: $host"
Write-Host "   Port: $port"
Write-Host "   Database: $database"
Write-Host "   Username: $username"
Write-Host ""

# Verificar se psql está instalado
Write-Host "🔍 Verificando se psql está instalado..." -ForegroundColor Yellow
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue

if (-not $psqlPath) {
    Write-Host "❌ psql não encontrado no PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Opções:" -ForegroundColor Yellow
    Write-Host "   1. Instalar PostgreSQL client (psql)" -ForegroundColor White
    Write-Host "   2. Usar Python com psycopg2 (já testado)" -ForegroundColor White
    Write-Host "   3. Conectar via SSH ao servidor e usar psql lá" -ForegroundColor White
    Write-Host ""
    Write-Host "📥 Para instalar PostgreSQL client no Windows:" -ForegroundColor Cyan
    Write-Host "   Download: https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host ""
    
    # Tentar usar Python
    Write-Host "🔄 Tentando usar Python para testar conexão..." -ForegroundColor Yellow
    python testar_conexao_detalhado.py
    
    exit
}

Write-Host "✅ psql encontrado: $($psqlPath.Source)" -ForegroundColor Green
Write-Host ""

# Configurar variável de ambiente PGPASSWORD
$env:PGPASSWORD = $password

Write-Host "🔄 Tentando conectar ao PostgreSQL..." -ForegroundColor Yellow
Write-Host ""

# Comando psql
$psqlCommand = "psql -h $host -p $port -U $username -d $database"

Write-Host "📝 Comando: $psqlCommand" -ForegroundColor Cyan
Write-Host ""

# Tentar conectar
try {
    # Executar psql com comandos SQL
    $sqlCommands = @"
SELECT version();
SELECT current_database();
SELECT current_user;
SELECT now();
\dt
"@
    
    $result = $sqlCommands | & psql -h $host -p $port -U $username -d $database
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Conexão estabelecida com sucesso!" -ForegroundColor Green
        Write-Host $result
    } else {
        Write-Host "❌ Erro na conexão (Exit Code: $LASTEXITCODE)" -ForegroundColor Red
        Write-Host $result
    }
    
} catch {
    Write-Host "❌ Erro ao executar psql: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Alternativas:" -ForegroundColor Yellow
    Write-Host "   1. Verifique se o PostgreSQL está acessível" -ForegroundColor White
    Write-Host "   2. Teste com Python: python testar_conexao_detalhado.py" -ForegroundColor White
    Write-Host "   3. Conecte via SSH ao servidor e use psql localmente" -ForegroundColor White
}

# Limpar variável de ambiente
Remove-Item Env:\PGPASSWORD

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

