# Script PowerShell para testar conectividade com servidor PostgreSQL remoto

Write-Host "🔍 Testando conectividade com servidor PostgreSQL remoto..." -ForegroundColor Cyan
Write-Host ""

$server = "37.27.220.67"
$port = 5432

# Teste 1: Ping
Write-Host "📡 Teste 1: Ping ao servidor..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $server -Count 1 -Quiet
if ($ping) {
    Write-Host "✅ Servidor está online e respondendo ao ping" -ForegroundColor Green
} else {
    Write-Host "❌ Servidor não está respondendo ao ping" -ForegroundColor Red
}

Write-Host ""

# Teste 2: Porta TCP
Write-Host "🔌 Teste 2: Conectividade na porta $port..." -ForegroundColor Yellow
$tcpTest = Test-NetConnection -ComputerName $server -Port $port -InformationLevel Quiet
if ($tcpTest) {
    Write-Host "✅ Porta $port está aberta e acessível!" -ForegroundColor Green
} else {
    Write-Host "❌ Porta $port está bloqueada ou não está acessível" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Possíveis causas:" -ForegroundColor Yellow
    Write-Host "   1. Firewall bloqueando a porta $port"
    Write-Host "   2. PostgreSQL não está escutando externamente"
    Write-Host "   3. PostgreSQL não está em execução no servidor"
    Write-Host "   4. PostgreSQL configurado apenas para localhost"
    Write-Host ""
    Write-Host "📋 Execute as verificações no servidor remoto (veja VERIFICACOES_SERVIDOR_REMOTO.md)" -ForegroundColor Cyan
}

Write-Host ""

# Teste 3: Informações detalhadas
Write-Host "📊 Teste 3: Informações detalhadas..." -ForegroundColor Yellow
$detailed = Test-NetConnection -ComputerName $server -Port $port
Write-Host "   ComputerName: $($detailed.ComputerName)"
Write-Host "   RemoteAddress: $($detailed.RemoteAddress)"
Write-Host "   RemotePort: $($detailed.RemotePort)"
Write-Host "   TcpTestSucceeded: $($detailed.TcpTestSucceeded)"
Write-Host "   PingSucceeded: $($detailed.PingSucceeded)"
if ($detailed.PingReplyDetails) {
    Write-Host "   RTT: $($detailed.PingReplyDetails.RoundtripTime) ms"
}

