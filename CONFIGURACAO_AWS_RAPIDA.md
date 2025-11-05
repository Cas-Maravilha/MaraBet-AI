# ⚡ CONFIGURAÇÃO RÁPIDA AWS - MARABET AI

**Data**: 25 de Outubro de 2025  
**Região**: eu-west-1 (Irlanda)  
**Status**: Credenciais Configuradas ✅

---

## 🔑 CONFIGURAÇÃO AWS CLI

### **1. Instalar AWS CLI (se ainda não instalou):**

#### **Windows (PowerShell como Admin):**
```powershell
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

#### **Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### **2. Configurar Credenciais:**

```bash
aws configure

# Inserir quando solicitado:
AWS Access Key ID [None]: YOUR_AWS_ACCESS_KEY_ID
AWS Secret Access Key [None]: YOUR_AWS_SECRET_ACCESS_KEY
Default region name [None]: eu-west-1
Default output format [None]: json
```

### **3. Verificar Configuração:**

```bash
# Verificar versão
aws --version

# Verificar identidade
aws sts get-caller-identity

# Resultado esperado:
# {
#     "UserId": "AIDAXXXXXXXXXXXXXXXX",
#     "Account": "XXXXXXXXXXXX",
#     "Arn": "arn:aws:iam::XXXXXXXXXXXX:user/nome-usuario"
# }
```

---

## 🧪 TESTES DE VALIDAÇÃO

### **1. Testar Acesso às Regiões:**

```bash
# Listar regiões disponíveis
aws ec2 describe-regions --output table

# Verificar região configurada
aws configure get region
# Esperado: eu-west-1
```

### **2. Testar Acesso aos Serviços:**

```bash
# EC2
aws ec2 describe-instances --region eu-west-1

# RDS
aws rds describe-db-instances --region eu-west-1

# S3
aws s3 ls

# VPC
aws ec2 describe-vpcs --region eu-west-1

# ElastiCache
aws elasticache describe-cache-clusters --region eu-west-1
```

### **3. Verificar Limites da Conta:**

```bash
# Verificar limites de EC2
aws service-quotas list-service-quotas \
    --service-code ec2 \
    --region eu-west-1 \
    --query 'Quotas[?QuotaName==`Running On-Demand Standard (A, C, D, H, I, M, R, T, Z) instances`]'

# Verificar limites de RDS
aws service-quotas list-service-quotas \
    --service-code rds \
    --region eu-west-1 \
    --query 'Quotas[?QuotaName==`DB instances`]'
```

---

## 🚀 PRÓXIMOS PASSOS

### **Agora que as credenciais estão configuradas:**

#### **1. Deploy Automático (Recomendado):**

```bash
# Executar script de deploy completo
chmod +x deploy_aws_completo.sh
./deploy_aws_completo.sh

# Tempo estimado: 20 minutos
# O script criará automaticamente:
# - VPC e Subnets
# - Security Groups
# - EC2 Instance (t3.large)
# - RDS PostgreSQL Multi-AZ
# - ElastiCache Redis Cluster
# - S3 Buckets
# - Application Load Balancer
```

#### **2. Verificar Custos Estimados:**

```bash
# Usar AWS Cost Explorer (via Console)
# Ou CLI:
aws ce get-cost-and-usage \
    --time-period Start=2025-10-01,End=2025-10-31 \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --group-by Type=SERVICE

# Configurar alerta de custo (recomendado)
aws budgets create-budget \
    --account-id $(aws sts get-caller-identity --query Account --output text) \
    --budget file://budget-config.json
```

#### **3. Configurar Budget Alert:**

Criar arquivo `budget-config.json`:
```json
{
  "BudgetName": "MaraBet-Monthly-Budget",
  "BudgetLimit": {
    "Amount": "600",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {},
  "CostTypes": {
    "IncludeTax": true,
    "IncludeSubscription": true,
    "UseBlended": false
  },
  "NotificationsWithSubscribers": [
    {
      "Notification": {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 80,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
        {
          "SubscriptionType": "EMAIL",
          "Address": "suporte@marabet.ao"
        }
      ]
    }
  ]
}
```

---

## 🔒 SEGURANÇA DAS CREDENCIAIS

### **Importantes Práticas de Segurança:**

1. **Não compartilhar credenciais**
   - As keys acima são sensíveis
   - Não fazer commit no Git
   - Não compartilhar em mensagens/emails

2. **Rotacionar chaves regularmente**
   ```bash
   # A cada 90 dias, criar novas keys no IAM:
   # Console AWS > IAM > Users > Security Credentials > Create Access Key
   ```

3. **Usar AWS Secrets Manager para aplicação**
   ```bash
   # Armazenar secrets sensíveis
   aws secretsmanager create-secret \
       --name marabet/production/db-password \
       --secret-string "MaraBet2025#Secure!" \
       --region eu-west-1
   ```

4. **Habilitar MFA (Multi-Factor Authentication)**
   ```bash
   # No Console AWS:
   # IAM > Users > Seu usuário > Security credentials > MFA
   # Recomendado: Google Authenticator ou Authy
   ```

5. **Configurar CloudTrail para auditoria**
   ```bash
   aws cloudtrail create-trail \
       --name marabet-audit-trail \
       --s3-bucket-name marabet-cloudtrail-logs \
       --is-multi-region-trail \
       --enable-log-file-validation
   ```

---

## 📍 REGIÃO: EU-WEST-1 (IRLANDA)

### **Por que Irlanda?**

✅ **Latência para Angola**: ~80-100ms (melhor da Europa)  
✅ **Custos**: Competitivos comparado a outras regiões europeias  
✅ **Disponibilidade**: 3 Availability Zones (a, b, c)  
✅ **Serviços**: Todos os serviços AWS disponíveis  
✅ **GDPR**: Compliance europeu de proteção de dados  
✅ **Conectividade**: Excelente infraestrutura de rede  

### **Availability Zones:**
- **eu-west-1a** - Primary (Application + Database Primary)
- **eu-west-1b** - Secondary (Database Standby)
- **eu-west-1c** - Backup (Failover)

---

## 🧰 COMANDOS ÚTEIS

### **Configuração:**

```bash
# Ver configuração atual
aws configure list

# Ver todas as configurações
cat ~/.aws/config
cat ~/.aws/credentials

# Adicionar profile adicional (opcional)
aws configure --profile marabet-prod

# Usar profile específico
aws s3 ls --profile marabet-prod
```

### **Diagnóstico:**

```bash
# Verificar região ativa
aws configure get region

# Listar recursos na região
aws resourcegroupstaggingapi get-resources \
    --region eu-west-1 \
    --output table

# Verificar custos do mês atual
aws ce get-cost-and-usage \
    --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
    --granularity DAILY \
    --metrics BlendedCost \
    --output json | jq '.ResultsByTime[] | {Date: .TimePeriod.Start, Cost: .Total.BlendedCost.Amount}'
```

### **Limpeza (se necessário):**

```bash
# Listar EC2 instances
aws ec2 describe-instances \
    --region eu-west-1 \
    --query 'Reservations[].Instances[].{ID:InstanceId,State:State.Name,Name:Tags[?Key==`Name`].Value|[0]}'

# Terminar instância específica
# aws ec2 terminate-instances --instance-ids i-xxxxxxxxx --region eu-west-1

# Deletar RDS (criar snapshot antes)
# aws rds delete-db-instance \
#     --db-instance-identifier marabet-db \
#     --final-db-snapshot-identifier marabet-db-final-snapshot-$(date +%Y%m%d) \
#     --region eu-west-1
```

---

## 📊 MONITORAMENTO DE CUSTOS

### **Configurar Alertas:**

```bash
# Ver custo atual
aws ce get-cost-and-usage \
    --time-period Start=$(date -d "1 month ago" +%Y-%m-01),End=$(date +%Y-%m-%d) \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --region eu-west-1

# Configurar alerta de orçamento
aws budgets create-budget \
    --account-id $(aws sts get-caller-identity --query Account --output text) \
    --budget '{
      "BudgetName": "MaraBet-Alert-$600",
      "BudgetLimit": {"Amount": "600", "Unit": "USD"},
      "TimeUnit": "MONTHLY",
      "BudgetType": "COST"
    }' \
    --notifications-with-subscribers '[
      {
        "Notification": {
          "NotificationType": "ACTUAL",
          "ComparisonOperator": "GREATER_THAN",
          "Threshold": 80
        },
        "Subscribers": [{
          "SubscriptionType": "EMAIL",
          "Address": "suporte@marabet.ao"
        }]
      }
    ]'
```

---

## ✅ CHECKLIST DE CONFIGURAÇÃO

- [x] AWS CLI instalado
- [x] Credenciais configuradas
- [x] Região definida (eu-west-1)
- [x] Access Key ID: YOUR_AWS_ACCESS_KEY_ID
- [x] Secret configurado
- [ ] Identidade verificada (`aws sts get-caller-identity`)
- [ ] Acesso aos serviços testado
- [ ] Budget alert configurado (opcional mas recomendado)
- [ ] MFA habilitado (recomendado)
- [ ] CloudTrail ativo (auditoria)
- [ ] Pronto para deploy!

---

## 🚀 EXECUTAR DEPLOY AGORA

```bash
# Com as credenciais configuradas, você pode:

# 1. Deploy automático completo
./deploy_aws_completo.sh

# OU

# 2. Criar recursos manualmente
# VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --region eu-west-1

# EC2
aws ec2 run-instances \
    --image-id ami-0c1c30571d2dae5c9 \
    --instance-type t3.large \
    --region eu-west-1

# RDS
aws rds create-db-instance \
    --db-instance-identifier marabet-db \
    --engine postgres \
    --region eu-west-1

# Etc... (veja AWS_DEPLOYMENT_GUIDE.md para detalhes)
```

---

## 📞 SUPORTE

**MaraBet AI:**
- 📧 Técnico: suporte@marabet.ao
- 📧 Comercial: comercial@marabet.ao
- 📞 WhatsApp: +224 932027393

**AWS:**
- 📚 Documentação: https://docs.aws.amazon.com
- 💬 Suporte: https://console.aws.amazon.com/support
- 📞 Support Plans: https://aws.amazon.com/premiumsupport

---

## 🎯 PRÓXIMO PASSO

**Execute o deploy automático:**

```bash
chmod +x deploy_aws_completo.sh
./deploy_aws_completo.sh
```

**Ou siga o guia completo:**
- `AWS_DEPLOYMENT_GUIDE.md` (878 linhas)
- `AWS_MIGRACAO_DADOS_COMPLETA.md` (799 linhas)

---

**✅ CONFIGURAÇÃO AWS CONCLUÍDA**  
**🚀 PRONTO PARA DEPLOY NO EU-WEST-1**  
**☁️ MaraBet AI - Powered by AWS**

