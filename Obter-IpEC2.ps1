# MaraBet AI - Obter IP Público da EC2 (PowerShell)

param(
    [string]$InstanceId = "",
    [string]$InstanceName = "marabet-ec2",
    [string]$Region = "eu-west-1"
)

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "📍 MARABET AI - OBTER IP PÚBLICO EC2" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

################################################################################
# 1. ENCONTRAR INSTANCE
################################################################################

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "1. ENCONTRANDO EC2 INSTANCE" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

if ([string]::IsNullOrEmpty($InstanceId)) {
    Write-Host "[ℹ] Buscando instância com nome: $InstanceName..." -ForegroundColor Blue
    
    try {
        $instances = aws ec2 describe-instances `
            --filters "Name=tag:Name,Values=$InstanceName" "Name=instance-state-name,Values=running,pending,stopping,stopped" `
            --region $Region `
            --output json | ConvertFrom-Json
        
        $InstanceId = $instances.Reservations[0].Instances[0].InstanceId
        
        if ([string]::IsNullOrEmpty($InstanceId)) {
            Write-Host "[✗] Instância não encontrada!" -ForegroundColor Red
            Write-Host ""
            Write-Host "Listar todas as instâncias:" -ForegroundColor Yellow
            Write-Host "  aws ec2 describe-instances --region $Region" -ForegroundColor Gray
            exit 1
        }
        
        Write-Host "[✓] Instance ID: $InstanceId" -ForegroundColor Green
        
    } catch {
        Write-Host "[✗] Erro ao buscar instância: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[ℹ] Instance ID fornecido: $InstanceId" -ForegroundColor Blue
}

################################################################################
# 2. OBTER INFORMAÇÕES
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "2. OBTENDO INFORMAÇÕES COMPLETAS" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[ℹ] Consultando instância $InstanceId..." -ForegroundColor Blue

try {
    $instanceInfo = aws ec2 describe-instances `
        --instance-ids $InstanceId `
        --region $Region `
        --output json | ConvertFrom-Json
    
    $instance = $instanceInfo.Reservations[0].Instances[0]
    
    $publicIp = $instance.PublicIpAddress
    $privateIp = $instance.PrivateIpAddress
    $publicDns = $instance.PublicDnsName
    $state = $instance.State.Name
    $instanceType = $instance.InstanceType
    $az = $instance.Placement.AvailabilityZone
    $vpcId = $instance.VpcId
    $subnetId = $instance.SubnetId
    
    # Nome da instância
    $nameTag = $instance.Tags | Where-Object { $_.Key -eq "Name" }
    $instanceName = if ($nameTag) { $nameTag.Value } else { "N/A" }
    
    # Security Groups
    $sgNames = ($instance.SecurityGroups | ForEach-Object { $_.GroupName }) -join ", "
    
    Write-Host "[ℹ] Nome: $instanceName" -ForegroundColor Blue
    Write-Host "[ℹ] Estado: $state" -ForegroundColor Blue
    Write-Host "[ℹ] Tipo: $instanceType" -ForegroundColor Blue
    Write-Host "[ℹ] AZ: $az" -ForegroundColor Blue
    
} catch {
    Write-Host "[✗] Erro ao consultar instância: $_" -ForegroundColor Red
    exit 1
}

################################################################################
# 3. MOSTRAR IPs
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "3. ENDEREÇOS IP" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

if (![string]::IsNullOrEmpty($publicIp)) {
    Write-Host "[✓] IP Público: $publicIp" -ForegroundColor Green
} else {
    Write-Host "[!] IP Público: Não disponível" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Possíveis causas:" -ForegroundColor Yellow
    Write-Host "  • Instância não tem IP público associado"
    Write-Host "  • Instância está parando/parada"
}

Write-Host "[ℹ] IP Privado: $privateIp" -ForegroundColor Blue

if (![string]::IsNullOrEmpty($publicDns)) {
    Write-Host "[ℹ] DNS Público: $publicDns" -ForegroundColor Blue
}

################################################################################
# 4. SALVAR INFORMAÇÕES
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "4. SALVANDO INFORMAÇÕES" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Arquivo de texto
Write-Host "[ℹ] Criando ec2-ip-info.txt..." -ForegroundColor Blue

@"
MaraBet AI - EC2 IP Information
================================

Instance Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Instance ID:          $InstanceId
Instance Name:        $instanceName
Instance Type:        $instanceType
State:                $state
Region:               $Region
Availability Zone:    $az

Network:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IP Público:           $publicIp
IP Privado:           $privateIp
DNS Público:          $publicDns

VPC:                  $vpcId
Subnet:               $subnetId
Security Groups:      $sgNames

SSH Access:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SSH Command:          ssh -i marabet-key.pem ubuntu@$publicIp

URLs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HTTP:                 http://$publicIp
HTTPS:                https://$publicIp
Health Check:         http://$publicIp/health

API-Football Whitelist:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  ADICIONAR ESTE IP AO WHITELIST:
    $publicIp

    Dashboard: https://dashboard.api-football.com/
    Soccer > Settings > IP Whitelist > Add IP

Generated:            $(Get-Date)
"@ | Out-File -FilePath "ec2-ip-info.txt" -Encoding UTF8

Write-Host "[✓] ec2-ip-info.txt criado" -ForegroundColor Green

# JSON
Write-Host "[ℹ] Criando ec2-ip-info.json..." -ForegroundColor Blue

$config = @{
    instance = @{
        instance_id = $InstanceId
        instance_name = $instanceName
        instance_type = $instanceType
        state = $state
        region = $Region
        availability_zone = $az
    }
    network = @{
        public_ip = $publicIp
        private_ip = $privateIp
        public_dns = $publicDns
        vpc_id = $vpcId
        subnet_id = $subnetId
        security_groups = $sgNames
    }
    access = @{
        ssh_command = "ssh -i marabet-key.pem ubuntu@$publicIp"
        http_url = "http://$publicIp"
        https_url = "https://$publicIp"
        health_check = "http://$publicIp/health"
    }
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

$config | ConvertTo-Json -Depth 10 | Out-File -FilePath "ec2-ip-info.json" -Encoding UTF8

Write-Host "[✓] ec2-ip-info.json criado" -ForegroundColor Green

################################################################################
# RESUMO
################################################################################

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "✅ IP PÚBLICO OBTIDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "EC2 Instance:" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "  Instance ID:       $InstanceId" -ForegroundColor White
Write-Host "  Nome:              $instanceName" -ForegroundColor White
Write-Host "  Tipo:              $instanceType" -ForegroundColor White
Write-Host "  Estado:            $state" -ForegroundColor Green
Write-Host ""
Write-Host "  IP Público:        $publicIp" -ForegroundColor Yellow
Write-Host "  IP Privado:        $privateIp" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "SSH Command:" -ForegroundColor White
Write-Host "  ssh -i marabet-key.pem ubuntu@$publicIp" -ForegroundColor Yellow
Write-Host ""
Write-Host "HTTP:" -ForegroundColor White
Write-Host "  http://$publicIp" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  API-Football Whitelist:" -ForegroundColor Yellow
Write-Host "  Adicionar IP: $publicIp" -ForegroundColor Yellow
Write-Host "  Dashboard: https://dashboard.api-football.com/" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ CONCLUÍDO!" -ForegroundColor Green
Write-Host ""

