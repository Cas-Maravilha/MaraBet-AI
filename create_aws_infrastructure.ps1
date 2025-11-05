# Script PowerShell para Criação de Infraestrutura AWS - MaraBet AI
# Execute como administrador se necessário

Write-Host "🏗️ MARABET AI - CRIANDO INFRAESTRUTURA AWS" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "📅 Data/Hora: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor Yellow

# Verificar se AWS CLI está instalado
Write-Host "`n🔍 Verificando AWS CLI..." -ForegroundColor Cyan
try {
    $awsVersion = aws --version
    Write-Host "✅ AWS CLI encontrado: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI não encontrado. Instale primeiro." -ForegroundColor Red
    exit 1
}

# Verificar credenciais AWS
Write-Host "`n🔍 Verificando credenciais AWS..." -ForegroundColor Cyan
try {
    $identity = aws sts get-caller-identity
    Write-Host "✅ Credenciais AWS válidas" -ForegroundColor Green
} catch {
    Write-Host "❌ Credenciais AWS inválidas. Execute: aws configure" -ForegroundColor Red
    exit 1
}

Write-Host "`n🌐 ETAPA 1: CRIANDO VPC" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

# Criar VPC
Write-Host "Criando VPC..." -ForegroundColor Yellow
$vpcResult = aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=marabet-vpc},{Key=Project,Value=MaraBet-AI}]'
$vpcJson = $vpcResult | ConvertFrom-Json
$VPC_ID = $vpcJson.Vpc.VpcId
Write-Host "✅ VPC criada: $VPC_ID" -ForegroundColor Green

Write-Host "`n🌐 ETAPA 2: CRIANDO SUBNETS" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

# Criar Subnet Pública 1
Write-Host "Criando Subnet Pública 1..." -ForegroundColor Yellow
$subnet1Result = aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone us-east-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=marabet-public-1},{Key=Project,Value=MaraBet-AI}]'
$subnet1Json = $subnet1Result | ConvertFrom-Json
$SUBNET_PUBLIC_1 = $subnet1Json.Subnet.SubnetId
Write-Host "✅ Subnet Pública 1 criada: $SUBNET_PUBLIC_1" -ForegroundColor Green

# Criar Subnet Pública 2
Write-Host "Criando Subnet Pública 2..." -ForegroundColor Yellow
$subnet2Result = aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone us-east-1b --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=marabet-public-2},{Key=Project,Value=MaraBet-AI}]'
$subnet2Json = $subnet2Result | ConvertFrom-Json
$SUBNET_PUBLIC_2 = $subnet2Json.Subnet.SubnetId
Write-Host "✅ Subnet Pública 2 criada: $SUBNET_PUBLIC_2" -ForegroundColor Green

Write-Host "`n🌐 ETAPA 3: CRIANDO INTERNET GATEWAY" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

# Criar Internet Gateway
Write-Host "Criando Internet Gateway..." -ForegroundColor Yellow
$igwResult = aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=marabet-igw},{Key=Project,Value=MaraBet-AI}]'
$igwJson = $igwResult | ConvertFrom-Json
$IGW_ID = $igwJson.InternetGateway.InternetGatewayId
Write-Host "✅ Internet Gateway criado: $IGW_ID" -ForegroundColor Green

# Anexar Internet Gateway à VPC
Write-Host "Anexando Internet Gateway à VPC..." -ForegroundColor Yellow
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID
Write-Host "✅ Internet Gateway anexado à VPC" -ForegroundColor Green

Write-Host "`n🌐 ETAPA 4: CRIANDO ROUTE TABLE" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

# Criar Route Table
Write-Host "Criando Route Table..." -ForegroundColor Yellow
$rtResult = aws ec2 create-route-table --vpc-id $VPC_ID --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=marabet-rt},{Key=Project,Value=MaraBet-AI}]'
$rtJson = $rtResult | ConvertFrom-Json
$RT_ID = $rtJson.RouteTable.RouteTableId
Write-Host "✅ Route Table criada: $RT_ID" -ForegroundColor Green

# Criar rota para Internet
Write-Host "Criando rota para Internet..." -ForegroundColor Yellow
aws ec2 create-route --route-table-id $RT_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
Write-Host "✅ Rota para Internet criada" -ForegroundColor Green

# Associar subnets à route table
Write-Host "Associando subnets à Route Table..." -ForegroundColor Yellow
aws ec2 associate-route-table --subnet-id $SUBNET_PUBLIC_1 --route-table-id $RT_ID
aws ec2 associate-route-table --subnet-id $SUBNET_PUBLIC_2 --route-table-id $RT_ID
Write-Host "✅ Subnets associadas à Route Table" -ForegroundColor Green

Write-Host "`n🔒 ETAPA 5: CRIANDO SECURITY GROUPS" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

# Criar Security Group para Web
Write-Host "Criando Security Group para Web..." -ForegroundColor Yellow
$sgWebResult = aws ec2 create-security-group --group-name marabet-web-sg --description "Security Group para aplicação web MaraBet AI" --vpc-id $VPC_ID --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=marabet-web-sg},{Key=Project,Value=MaraBet-AI}]'
$sgWebJson = $sgWebResult | ConvertFrom-Json
$SG_WEB_ID = $sgWebJson.GroupId
Write-Host "✅ Security Group Web criado: $SG_WEB_ID" -ForegroundColor Green

# Adicionar regras ao Security Group Web
Write-Host "Adicionando regras ao Security Group Web..." -ForegroundColor Yellow
aws ec2 authorize-security-group-ingress --group-id $SG_WEB_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_WEB_ID --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_WEB_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_WEB_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
Write-Host "✅ Regras do Security Group Web adicionadas" -ForegroundColor Green

# Criar Security Group para Database
Write-Host "Criando Security Group para Database..." -ForegroundColor Yellow
$sgDbResult = aws ec2 create-security-group --group-name marabet-db-sg --description "Security Group para banco de dados MaraBet AI" --vpc-id $VPC_ID --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=marabet-db-sg},{Key=Project,Value=MaraBet-AI}]'
$sgDbJson = $sgDbResult | ConvertFrom-Json
$SG_DB_ID = $sgDbJson.GroupId
Write-Host "✅ Security Group Database criado: $SG_DB_ID" -ForegroundColor Green

# Adicionar regras ao Security Group Database
Write-Host "Adicionando regras ao Security Group Database..." -ForegroundColor Yellow
aws ec2 authorize-security-group-ingress --group-id $SG_DB_ID --protocol tcp --port 5432 --source-group $SG_WEB_ID
aws ec2 authorize-security-group-ingress --group-id $SG_DB_ID --protocol tcp --port 6379 --source-group $SG_WEB_ID
Write-Host "✅ Regras do Security Group Database adicionadas" -ForegroundColor Green

Write-Host "`n📊 ETAPA 6: SALVANDO CONFIGURAÇÕES" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

# Criar arquivo de configuração
$config = @{
    vpc_id = $VPC_ID
    subnet_public_1 = $SUBNET_PUBLIC_1
    subnet_public_2 = $SUBNET_PUBLIC_2
    igw_id = $IGW_ID
    route_table_id = $RT_ID
    sg_web_id = $SG_WEB_ID
    sg_db_id = $SG_DB_ID
    created_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

$configJson = $config | ConvertTo-Json -Depth 2
$configJson | Out-File -FilePath "aws_infrastructure_config.json" -Encoding UTF8
Write-Host "✅ Configurações salvas em: aws_infrastructure_config.json" -ForegroundColor Green

Write-Host "`n🎉 INFRAESTRUTURA CRIADA COM SUCESSO!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

Write-Host "`n📋 RECURSOS CRIADOS:" -ForegroundColor Yellow
Write-Host "-" * 30 -ForegroundColor Yellow
Write-Host "• VPC ID: $VPC_ID" -ForegroundColor White
Write-Host "• Subnet Pública 1: $SUBNET_PUBLIC_1" -ForegroundColor White
Write-Host "• Subnet Pública 2: $SUBNET_PUBLIC_2" -ForegroundColor White
Write-Host "• Internet Gateway: $IGW_ID" -ForegroundColor White
Write-Host "• Route Table: $RT_ID" -ForegroundColor White
Write-Host "• Security Group Web: $SG_WEB_ID" -ForegroundColor White
Write-Host "• Security Group Database: $SG_DB_ID" -ForegroundColor White

Write-Host "`n🌐 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "-" * 30 -ForegroundColor Yellow
Write-Host "1. ✅ VPC e subnets criadas" -ForegroundColor Green
Write-Host "2. ✅ Internet Gateway configurado" -ForegroundColor Green
Write-Host "3. ✅ Route Tables configuradas" -ForegroundColor Green
Write-Host "4. ✅ Security Groups criados" -ForegroundColor Green
Write-Host "5. 🔄 Criar instâncias EC2" -ForegroundColor Cyan
Write-Host "6. 🔄 Configurar RDS" -ForegroundColor Cyan
Write-Host "7. 🔄 Configurar ElastiCache" -ForegroundColor Cyan
Write-Host "8. 🔄 Deploy da aplicação" -ForegroundColor Cyan

Write-Host "`n💡 COMANDOS ÚTEIS:" -ForegroundColor Yellow
Write-Host "-" * 30 -ForegroundColor Yellow
Write-Host "# Ver VPC" -ForegroundColor White
Write-Host "aws ec2 describe-vpcs --vpc-ids $VPC_ID" -ForegroundColor Gray
Write-Host ""
Write-Host "# Ver subnets" -ForegroundColor White
Write-Host "aws ec2 describe-subnets --filters `"Name=vpc-id,Values=$VPC_ID`"" -ForegroundColor Gray
Write-Host ""
Write-Host "# Ver security groups" -ForegroundColor White
Write-Host "aws ec2 describe-security-groups --filters `"Name=vpc-id,Values=$VPC_ID`"" -ForegroundColor Gray

Write-Host "`n🎯 INFRAESTRUTURA AWS CRIADA COM SUCESSO!" -ForegroundColor Green
Write-Host "O sistema MaraBet AI está pronto para deploy na nuvem!" -ForegroundColor Green
