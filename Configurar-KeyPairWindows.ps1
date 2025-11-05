# MaraBet AI - Configurar Permissões Key Pair no Windows
# Remove herança e define permissões seguras

param(
    [string]$KeyFile = "marabet-key.pem"
)

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "🔑 CONFIGURAR PERMISSÕES KEY PAIR - WINDOWS" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se arquivo existe
if (-not (Test-Path $KeyFile)) {
    Write-Host "[✗] Arquivo não encontrado: $KeyFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Crie a key pair primeiro:" -ForegroundColor Yellow
    Write-Host "  aws ec2 create-key-pair --key-name marabet-key --query 'KeyMaterial' --output text > marabet-key.pem" -ForegroundColor Gray
    exit 1
}

Write-Host "[ℹ] Arquivo: $KeyFile" -ForegroundColor Blue
Write-Host ""

################################################################################
# 1. REMOVER HERANÇA
################################################################################

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "1. REMOVENDO HERANÇA DE PERMISSÕES" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[ℹ] Obtendo ACL atual..." -ForegroundColor Blue

try {
    $acl = Get-Acl $KeyFile
    
    # Desabilitar herança (preservar permissões atuais primeiro)
    $acl.SetAccessRuleProtection($true, $false)
    Set-Acl $KeyFile $acl
    
    Write-Host "[✓] Herança removida" -ForegroundColor Green
    
} catch {
    Write-Host "[✗] Erro ao remover herança: $_" -ForegroundColor Red
    exit 1
}

################################################################################
# 2. REMOVER TODAS AS PERMISSÕES
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "2. REMOVENDO PERMISSÕES EXISTENTES" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[ℹ] Removendo todas as permissões..." -ForegroundColor Blue

try {
    $acl = Get-Acl $KeyFile
    
    # Remover todas as regras de acesso
    $acl.Access | ForEach-Object {
        $acl.RemoveAccessRule($_) | Out-Null
    }
    
    Set-Acl $KeyFile $acl
    
    Write-Host "[✓] Permissões removidas" -ForegroundColor Green
    
} catch {
    Write-Host "[✗] Erro ao remover permissões: $_" -ForegroundColor Red
}

################################################################################
# 3. ADICIONAR PERMISSÃO APENAS PARA USUÁRIO ATUAL
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "3. ADICIONANDO PERMISSÃO SOMENTE LEITURA" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

try {
    $acl = Get-Acl $KeyFile
    
    # Obter usuário atual
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    Write-Host "[ℹ] Usuário: $currentUser" -ForegroundColor Blue
    
    # Criar regra de acesso (somente leitura)
    $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $currentUser,
        "Read",
        "Allow"
    )
    
    # Adicionar regra
    $acl.SetAccessRule($accessRule)
    Set-Acl $KeyFile $acl
    
    Write-Host "[✓] Permissão de leitura adicionada para $currentUser" -ForegroundColor Green
    
} catch {
    Write-Host "[✗] Erro ao adicionar permissão: $_" -ForegroundColor Red
    exit 1
}

################################################################################
# 4. VERIFICAR PERMISSÕES
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "4. VERIFICANDO PERMISSÕES FINAIS" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[ℹ] Permissões atuais:" -ForegroundColor Blue
Write-Host ""

$acl = Get-Acl $KeyFile

foreach ($access in $acl.Access) {
    Write-Host "  Usuário:     $($access.IdentityReference)" -ForegroundColor White
    Write-Host "  Permissões:  $($access.FileSystemRights)" -ForegroundColor White
    Write-Host "  Tipo:        $($access.AccessControlType)" -ForegroundColor White
    Write-Host ""
}

# Verificar se herança está desabilitada
if ($acl.AreAccessRulesProtected) {
    Write-Host "[✓] Herança desabilitada ✓" -ForegroundColor Green
} else {
    Write-Host "[!] Herança ainda habilitada!" -ForegroundColor Yellow
}

# Contar permissões
$accessCount = ($acl.Access | Measure-Object).Count
Write-Host "[ℹ] Total de regras de acesso: $accessCount" -ForegroundColor Blue

if ($accessCount -eq 1) {
    Write-Host "[✓] Apenas 1 regra (correto) ✓" -ForegroundColor Green
} else {
    Write-Host "[!] Múltiplas regras ($accessCount)" -ForegroundColor Yellow
}

################################################################################
# RESUMO
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "✅ PERMISSÕES CONFIGURADAS COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Arquivo:" -ForegroundColor White
Write-Host "  $KeyFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "Permissões:" -ForegroundColor White
Write-Host "  ✓ Herança desabilitada" -ForegroundColor Green
Write-Host "  ✓ Apenas usuário atual tem acesso" -ForegroundColor Green
Write-Host "  ✓ Somente leitura" -ForegroundColor Green
Write-Host ""
Write-Host "Pronto para usar:" -ForegroundColor White
Write-Host "  ssh -i $KeyFile ubuntu@<EC2_PUBLIC_IP>" -ForegroundColor Yellow
Write-Host ""

################################################################################
# CRIAR SCRIPT DE CONEXÃO
################################################################################

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "CRIANDO SCRIPT DE CONEXÃO" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Criar script bash para Git Bash
@"
#!/bin/bash
# ssh-connect-marabet.sh

KEY_FILE="marabet-key.pem"

# Verificar se key existe
if [ ! -f "\$KEY_FILE" ]; then
    echo "❌ Key file não encontrado: \$KEY_FILE"
    exit 1
fi

# Verificar permissões (Linux/macOS)
if [ `$(uname)` != "MINGW64_NT"* ] && [ `$(uname)` != "MSYS_NT"* ]; then
    chmod 400 \$KEY_FILE
fi

# IP da EC2 (atualizar após criar)
EC2_IP="<EC2_PUBLIC_IP>"

if [ "\$EC2_IP" == "<EC2_PUBLIC_IP>" ]; then
    echo "⚠️  Atualize o EC2_IP no script primeiro!"
    echo ""
    echo "Obter IP:"
    echo "  aws ec2 describe-instances --instance-ids <INSTANCE_ID> --query 'Reservations[0].Instances[0].PublicIpAddress' --output text"
    exit 1
fi

# Conectar
echo "🔐 Conectando ao MaraBet EC2..."
echo "IP: \$EC2_IP"
echo ""

ssh -i \$KEY_FILE ubuntu@\$EC2_IP
"@ | Out-File -FilePath "ssh-connect-marabet.sh" -Encoding UTF8

Write-Host "[✓] ssh-connect-marabet.sh criado" -ForegroundColor Green
Write-Host ""

Write-Host "Usar com Git Bash:" -ForegroundColor White
Write-Host "  ./ssh-connect-marabet.sh" -ForegroundColor Yellow
Write-Host ""

Write-Host "✅ CONCLUÍDO!" -ForegroundColor Green
Write-Host ""

