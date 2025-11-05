# 🌐 ROUTE 53 - CONFIGURAÇÃO marabet.com

**Domínio**: marabet.com  
**Região**: eu-west-1  
**Status**: ✅ Hosted Zone Criada

---

## 📋 INFORMAÇÕES DO ROUTE 53

### **Hosted Zone:**

```yaml
Domínio:              marabet.com
Record Type:          NS (Name Servers)
Routing Policy:       Simple
TTL:                  172800 seconds (48 horas)

Name Servers:
  - ns-951.awsdns-54.net
  - ns-1508.awsdns-60.org
  - ns-1868.awsdns-41.co.uk
  - ns-470.awsdns-58.com
```

---

## ✅ NAMESERVERS CONFIGURADOS

### **NS Records:**

```
ns-951.awsdns-54.net.
ns-1508.awsdns-60.org.
ns-1868.awsdns-41.co.uk.
ns-470.awsdns-58.com.
```

### **⚠️ IMPORTANTE:**

Você precisa configurar esses nameservers no **registrador do domínio marabet.com** (GoDaddy, Namecheap, etc.):

1. Acesse o painel do registrador
2. Encontre "Nameservers" ou "DNS Settings"
3. Altere para "Custom Nameservers"
4. Adicione os 4 nameservers acima
5. Salve as alterações
6. Aguarde propagação (pode levar 24-48h)

---

## 🔧 CONFIGURAR REGISTROS DNS

### **1. Criar Registro A (para EC2 ou Elastic IP):**

```bash
# Obter Hosted Zone ID
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones \
  --query 'HostedZones[?Name==`marabet.com.`].Id' \
  --output text | cut -d'/' -f3)

echo "Hosted Zone ID: $HOSTED_ZONE_ID"

# Criar registro A
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "marabet.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "SEU_ELASTIC_IP"}]
      }
    }]
  }'

# Para www.marabet.com
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "www.marabet.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "SEU_ELASTIC_IP"}]
      }
    }]
  }'
```

### **2. Criar Registro CNAME (subdomínios):**

```bash
# api.marabet.com
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.marabet.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "marabet.com"}]
      }
    }]
  }'
```

---

## 🔗 APONTAR PARA ALB (quando criar)

### **Com Application Load Balancer (Recomendado):**

```bash
# Obter DNS do ALB
ALB_DNS="marabet-alb-123456789.eu-west-1.elb.amazonaws.com"
ALB_HOSTED_ZONE_ID="Z32O12XQLNTSW2"  # ID da zona do ELB para eu-west-1

# Criar Alias Record (melhor que A Record)
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "marabet.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "'$ALB_HOSTED_ZONE_ID'",
          "DNSName": "'$ALB_DNS'",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

---

## 🔒 SSL/TLS CERTIFICATE

### **Solicitar Certificado SSL (ACM):**

```bash
# Solicitar certificado para marabet.com e www.marabet.com
aws acm request-certificate \
  --domain-name marabet.com \
  --subject-alternative-names www.marabet.com api.marabet.com \
  --validation-method DNS \
  --region eu-west-1

# Anotar ARN retornado
CERTIFICATE_ARN="arn:aws:acm:eu-west-1:206749730888:certificate/xxxxx"
```

### **Validar Certificado:**

```bash
# Obter registros de validação DNS
aws acm describe-certificate \
  --certificate-arn $CERTIFICATE_ARN \
  --region eu-west-1

# Adicionar registros CNAME ao Route 53 (fornecidos pela AWS)
# A validação é automática, leva ~5 minutos
```

---

## 📧 EMAIL (MX RECORDS)

### **Configurar Email (opcional):**

```bash
# Se quiser email @marabet.com
# Usar: AWS SES, Google Workspace, ou outro provider

# Exemplo com SES:
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "marabet.com",
        "Type": "MX",
        "TTL": 300,
        "ResourceRecords": [
          {"Value": "10 inbound-smtp.eu-west-1.amazonaws.com"}
        ]
      }
    }]
  }'
```

---

## 🧪 TESTAR DNS

### **Verificar Propagação:**

```bash
# Consultar nameservers
dig NS marabet.com

# Consultar registro A
dig A marabet.com

# Consultar com nameserver específico
dig @ns-951.awsdns-54.net marabet.com

# Online: https://dnschecker.org/
```

### **Testar Resolução:**

```bash
# Linux/macOS
nslookup marabet.com
host marabet.com

# Windows
nslookup marabet.com
```

---

## 📊 REGISTROS RECOMENDADOS

### **Configuração Completa:**

| Tipo | Nome | Valor | TTL |
|------|------|-------|-----|
| **NS** | marabet.com | ns-951.awsdns-54.net (x4) | 172800 |
| **A** | marabet.com | <ELASTIC_IP> | 300 |
| **A** | www | <ELASTIC_IP> | 300 |
| **CNAME** | api | marabet.com | 300 |
| **MX** | @ | 10 mail.marabet.com | 300 |
| **TXT** | @ | v=spf1 include:amazonses.com ~all | 300 |

---

## 💰 CUSTOS ROUTE 53

| Item | Custo |
|------|-------|
| **Hosted Zone** | $0.50/mês |
| **Queries (1M)** | $0.40 |
| **TOTAL** | **~$1-2/mês** |

---

## ✅ CHECKLIST

- [x] Hosted Zone criada
- [x] Nameservers obtidos (4)
- [ ] Nameservers configurados no registrador
- [ ] Registro A criado (marabet.com → Elastic IP)
- [ ] Registro A criado (www → Elastic IP)
- [ ] Certificado SSL solicitado
- [ ] Certificado validado
- [ ] DNS testado
- [ ] Propagação verificada (24-48h)
- [ ] HTTPS funcionando

---

## 📞 PRÓXIMOS PASSOS

1. ✅ Route 53 Hosted Zone criada
2. **Configurar nameservers** no registrador de marabet.com
3. **Criar Elastic IP** para EC2
4. **Criar registro A** apontando para Elastic IP
5. **Solicitar SSL** certificate
6. **Validar SSL** via DNS
7. **Testar** https://marabet.com

---

**🌐 Route 53 Configurado!**  
**✅ marabet.com | NS Records Ativos**  
**☁️ MaraBet AI - AWS Route 53**

