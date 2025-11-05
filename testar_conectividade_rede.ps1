# =============================================
# Script PowerShell: Teste de Conectividade
# Testa conectividade de rede ao servidor remoto
# =============================================

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TESTE DE CONECTIVIDADE DE REDE                          ║" -ForegroundColor Cyan
Write-Host "║     Servidor: 37.27.220.67                                 ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$server = "37.27.220.67"
$port = 5432

# === TESTE 1: Ping ===
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host "TESTE 1: Ping ao Servidor" -ForegroundColor Blue
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host ""

Write-Host "🔄 Testando ping ao servidor..." -ForegroundColor Yellow

try {
    $ping = Test-Connection -ComputerName $server -Count 1 -ErrorAction Stop
    $rtt = $ping.ResponseTime
    Write-Host "✅ Servidor está online" -ForegroundColor Green
    Write-Host "   Latência: $rtt ms" -ForegroundColor Green
    $pingSuccess = $true
} catch {
    Write-Host "❌ Servidor não está respondendo ao ping" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Verifique se o IP $server está correto" -ForegroundColor Yellow
    $pingSuccess = $false
}

Write-Host ""

# === TESTE 2: Porta TCP ===
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host "TESTE 2: Conectividade na Porta $port" -ForegroundColor Blue
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host ""

Write-Host "🔄 Testando conectividade na porta $port..." -ForegroundColor Yellow

try {
    $tcpTest = Test-NetConnection -ComputerName $server -Port $port -WarningAction SilentlyContinue
    
    Write-Host "📊 Informações da conexão:" -ForegroundColor Cyan
    Write-Host "   ComputerName: $($tcpTest.ComputerName)"
    Write-Host "   RemoteAddress: $($tcpTest.RemoteAddress)"
    Write-Host "   RemotePort: $($tcpTest.RemotePort)"
    Write-Host "   InterfaceAlias: $($tcpTest.InterfaceAlias)"
    Write-Host "   SourceAddress: $($tcpTest.SourceAddress)"
    Write-Host ""
    
    if ($tcpTest.TcpTestSucceeded) {
        Write-Host "✅ Porta $port está aberta e acessível!" -ForegroundColor Green
        $portSuccess = $true
    } else {
        Write-Host "❌ Porta $port está bloqueada ou não está acessível" -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 Possíveis causas:" -ForegroundColor Yellow
        Write-Host "   1. Firewall bloqueando a porta $port"
        Write-Host "   2. PostgreSQL não está em execução"
        Write-Host "   3. PostgreSQL não está escutando externamente"
        Write-Host "   4. PostgreSQL configurado apenas para localhost"
        Write-Host ""
        Write-Host "📋 Execute no servidor remoto:" -ForegroundColor Cyan
        Write-Host "   sudo bash verificar_configuracao_postgresql.sh" -ForegroundColor White
        $portSuccess = $false
    }
    
    if ($tcpTest.PingSucceeded) {
        Write-Host "✅ Ping bem-sucedido: $($tcpTest.PingReplyDetails.RoundtripTime) ms" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Erro ao testar conectividade: $_" -ForegroundColor Red
    $portSuccess = $false
}

Write-Host ""

# === TESTE 3: DNS Lookup (opcional) ===
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host "TESTE 3: Resolução DNS (opcional)" -ForegroundColor Blue
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host ""

try {
    $dns = Resolve-DnsName -Name $server -ErrorAction SilentlyContinue
    if ($dns) {
        Write-Host "✅ Resolução DNS bem-sucedida" -ForegroundColor Green
        Write-Host "   Nome: $($dns[0].Name)"
        Write-Host "   IP: $($dns[0].IPAddress)"
    } else {
        Write-Host "⚠️  Não foi possível resolver DNS (pode ser IP direto)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Teste DNS pulado (normal para IPs diretos)" -ForegroundColor Yellow
}

Write-Host ""

# === RESUMO FINAL ===
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host "RESUMO DOS TESTES" -ForegroundColor Blue
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host ""

$allTests = @()

if ($pingSuccess) {
    Write-Host "✅ Ping: PASSOU" -ForegroundColor Green
    $allTests += $true
} else {
    Write-Host "❌ Ping: FALHOU" -ForegroundColor Red
    $allTests += $false
}

if ($portSuccess) {
    Write-Host "✅ Porta TCP $port: PASSOU" -ForegroundColor Green
    $allTests += $true
} else {
    Write-Host "❌ Porta TCP $port: FALHOU" -ForegroundColor Red
    $allTests += $false
}

$passed = ($allTests | Where-Object { $_ -eq $true }).Count
$total = $allTests.Count

Write-Host ""
Write-Host "📊 Resultado Final: $passed/$total testes passaram" -ForegroundColor Cyan

if ($passed -eq $total) {
    Write-Host ""
    Write-Host "🎉 TODOS OS TESTES DE REDE PASSARAM!" -ForegroundColor Green
    Write-Host "   Você pode prosseguir com o teste de conexão PostgreSQL" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Próximos passos:" -ForegroundColor Yellow
    Write-Host "   1. Execute: python testar_conexao_remota.py" -ForegroundColor White
    Write-Host "   2. Ou execute: bash testar_conexao_remota.sh" -ForegroundColor White
    exit 0
} else {
    Write-Host ""
    Write-Host "⚠️  Alguns testes falharam. Verifique a conectividade de rede." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Ações recomendadas:" -ForegroundColor Yellow
    Write-Host "   1. Verifique se o servidor está online" -ForegroundColor White
    Write-Host "   2. Verifique configurações de firewall" -ForegroundColor White
    Write-Host "   3. Verifique se PostgreSQL está configurado para acesso remoto" -ForegroundColor White
    exit 1
}

