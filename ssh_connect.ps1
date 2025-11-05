# Script para conectar SSH automaticamente
$password = "kckmcfHrERVuHnCW3jks"
$hostname = "37.27.220.67"
$username = "root"

# Tentativa de usar expect-like automation via PowerShell
$processInfo = New-Object System.Diagnostics.ProcessStartInfo
$processInfo.FileName = "ssh"
$processInfo.Arguments = "${username}@${hostname}"
$processInfo.UseShellExecute = $false
$processInfo.RedirectStandardInput = $true
$processInfo.RedirectStandardOutput = $true
$processInfo.RedirectStandardError = $true
$processInfo.CreateNoWindow = $true

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $processInfo
$process.Start() | Out-Null

Start-Sleep -Milliseconds 500
$process.StandardInput.WriteLine($password)
$process.StandardInput.Flush()

# Manter conexão
while (-not $process.HasExited) {
    $output = $process.StandardOutput.ReadLine()
    if ($output) { Write-Host $output }
    Start-Sleep -Milliseconds 100
}

