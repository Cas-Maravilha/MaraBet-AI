# 🌐 REGISTRAR DOMÍNIO marabet.com VIA AWS

**Domínio**: marabet.com  
**Registrador**: AWS Route 53 Domains  
**Duração**: 1 ano (renovação automática)

---

## 📋 ÍNDICE

1. [Informações Necessárias](#informações-necessárias)
2. [Registrar Domínio](#1-registrar-domínio)
3. [Verificar Registro](#2-verificar-registro)
4. [Configurar DNS](#3-configurar-dns)
5. [Custos](#4-custos)

---

## 📝 INFORMAÇÕES NECESSÁRIAS

### **Dados do Proprietário:**

```yaml
Nome Completo:        Claudio dos Santos
Tipo de Contato:      PERSON (Pessoa Física)
Email:                admin@marabet.com
Telefone:             +244932027393

Endereço:
  Linha 1:            Rua da Missão, Bairro Alvalade
  Cidade:             Luanda
  País:               AO (Angola)
  CEP:                00000
```

**⚠️ IMPORTANTE**: 
- Use um **email válido** que você tenha acesso
- O email receberá confirmação de registro
- Telefone precisa ser válido (+244 é código de Angola)

---

## 1️⃣ REGISTRAR DOMÍNIO

### **Via AWS CLI:**

```bash
# Registrar marabet.com
aws route53domains register-domain \
  --region us-east-1 \
  --domain-name marabet.com \
  --duration-in-years 1 \
  --auto-renew \
  --admin-contact \
    FirstName=Claudio,\
LastName=dos\ Santos,\
ContactType=PERSON,\
AddressLine1=Rua\ da\ Missão\ Bairro\ Alvalade,\
City=Luanda,\
CountryCode=AO,\
ZipCode=00000,\
PhoneNumber=+244.932027393,\
Email=admin@marabet.com \
  --registrant-contact \
    FirstName=Claudio,\
LastName=dos\ Santos,\
ContactType=PERSON,\
AddressLine1=Rua\ da\ Missão\ Bairro\ Alvalade,\
City=Luanda,\
CountryCode=AO,\
ZipCode=00000,\
PhoneNumber=+244.932027393,\
Email=admin@marabet.com \
  --tech-contact \
    FirstName=Claudio,\
LastName=dos\ Santos,\
ContactType=PERSON,\
AddressLine1=Rua\ da\ Missão\ Bairro\ Alvalade,\
City=Luanda,\
CountryCode=AO,\
ZipCode=00000,\
PhoneNumber=+244.932027393,\
Email=suporte@marabet.com \
  --privacy-protect-admin-contact \
  --privacy-protect-registrant-contact \
  --privacy-protect-tech-contact
```

**⚠️ NOTA IMPORTANTE:**
- Route 53 Domains opera **apenas em us-east-1**
- Use `--region us-east-1` mesmo que sua infraestrutura esteja em eu-west-1

### **Via AWS Console (Mais Fácil):**

```
1. AWS Console > Route 53
2. "Register Domain"
3. Buscar: marabet.com
4. Adicionar ao carrinho
5. Preencher informações de contato:
   - Nome: Claudio dos Santos
   - Email: admin@marabet.com
   - Telefone: +244932027393
   - Endereço: Luanda, Angola
6. Habilitar Privacy Protection (WHOIS privacy)
7. Habilitar Auto-Renew
8. Aceitar termos
9. Finalizar compra

Custo: ~$13/ano para .com
```

---

## 2️⃣ VERIFICAR REGISTRO

### **Ver Status do Registro:**

```bash
# Listar domínios
aws route53domains list-domains \
  --region us-east-1

# Ver detalhes do domínio
aws route53domains get-domain-detail \
  --domain-name marabet.com \
  --region us-east-1
```

### **Verificar Operação:**

```bash
# Listar operações recentes
aws route53domains list-operations \
  --region us-east-1

# Ver detalhes de operação específica
aws route53domains get-operation-detail \
  --operation-id xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx \
  --region us-east-1
```

**Status esperados:**
- `SUBMITTED` - Enviado
- `IN_PROGRESS` - Processando
- `SUCCESSFUL` - Concluído (pode levar até 3 dias)
- `FAILED` - Falhou (verificar motivo)

---

## 3️⃣ CONFIGURAR DNS

### **A. Hosted Zone (Automática):**

Quando você registra via Route 53, uma **Hosted Zone é criada automaticamente** com:

```
Name Servers (já configurados):
  ns-951.awsdns-54.net
  ns-1508.awsdns-60.org
  ns-1868.awsdns-41.co.uk
  ns-470.awsdns-58.com
```

### **B. Criar Registro A (após ter Elastic IP):**

```bash
# Obter Hosted Zone ID
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones \
  --query 'HostedZones[?Name==`marabet.com.`].Id' \
  --output text | cut -d'/' -f3)

# Obter Elastic IP da EC2
ELASTIC_IP=$(cat elastic-ip-info.txt | grep "Elastic IP:" | awk '{print $3}' 2>/dev/null || echo "SEU_ELASTIC_IP")

# Criar registro A para marabet.com
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "marabet.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "'$ELASTIC_IP'"}]
      }
    }]
  }'

# Criar registro A para www.marabet.com
aws route53 change-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "www.marabet.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "'$ELASTIC_IP'"}]
      }
    }]
  }'
```

---

## 4️⃣ CUSTOS

### **Registro de Domínio .com:**

| Item | Custo |
|------|-------|
| **Registro 1º ano** | ~$13 |
| **Renovação anual** | ~$13/ano |
| **Hosted Zone** | $0.50/mês = $6/ano |
| **Queries (1M)** | $0.40 |
| **Privacy Protection** | Incluído (grátis) |
| **Auto-Renew** | Incluído |
| **TOTAL 1º ANO** | **~$20** |
| **TOTAL ANOS SEGUINTES** | **~$20/ano** |

**Comparação:**
- GoDaddy: $12-15/ano + privacy $10/ano = $22-25/ano
- Namecheap: $10/ano + privacy $8/ano = $18/ano
- **AWS Route 53**: $13/ano + $6/ano Hosted Zone = $19/ano ✅

**Vantagem AWS**: Tudo integrado!

---

## 🔒 PRIVACY PROTECTION

### **WHOIS Privacy (Recomendado):**

```bash
# Habilitar privacy protection
aws route53domains enable-domain-privacy \
  --domain-name marabet.com \
  --admin-privacy \
  --registrant-privacy \
  --tech-privacy \
  --region us-east-1

# Verificar status
aws route53domains get-domain-detail \
  --domain-name marabet.com \
  --region us-east-1 \
  --query '[AdminPrivacy,RegistrantPrivacy,TechPrivacy]'
```

**Com Privacy Protection:**
- ❌ Informações pessoais **NÃO aparecem** no WHOIS
- ✅ AWS mascara email, telefone, endereço
- ✅ Proteção contra spam
- ✅ **Grátis** na AWS

---

## 📧 VERIFICAR EMAIL

### **Importante:**

```
1. Verificar inbox de: admin@marabet.com
2. Procurar email da AWS com assunto:
   "Please verify your email address for domain registration"
3. Clicar no link de verificação
4. Prazo: 15 dias para verificar
5. Se não verificar: Domínio será suspenso!
```

---

## 🧪 TESTAR DOMÍNIO

### **Verificar Status:**

```bash
# Status do domínio
aws route53domains get-domain-detail \
  --domain-name marabet.com \
  --region us-east-1 \
  --query 'DomainName,Status,Nameservers'

# Testar resolução DNS
dig marabet.com NS
nslookup marabet.com

# Verificar WHOIS
whois marabet.com
```

### **Online:**
- https://dnschecker.org/
- https://www.whatsmydns.net/
- https://whois.domaintools.com/

---

## 📋 CHECKLIST

- [ ] Domínio marabet.com disponível
- [ ] Comando de registro executado
- [ ] Email de verificação recebido
- [ ] Email verificado (clicar no link)
- [ ] Domínio registrado com sucesso
- [ ] Hosted Zone criada automaticamente
- [ ] Nameservers configurados
- [ ] Privacy Protection habilitada
- [ ] Auto-Renew habilitado
- [ ] Registro A criado (marabet.com → Elastic IP)
- [ ] Registro A criado (www → Elastic IP)
- [ ] DNS testado e funcionando
- [ ] SSL Certificate solicitado
- [ ] SSL validado

---

## ⏱️ TIMELINE

| Atividade | Tempo |
|-----------|-------|
| **Registro do domínio** | Imediato |
| **Email de verificação** | 5-15 minutos |
| **Propagação DNS** | 24-48 horas |
| **Hosted Zone ativa** | Imediato |
| **SSL Certificate** | 5-10 minutos |

---

## 🔧 COMANDOS ÚTEIS

### **Atualizar Contatos:**

```bash
aws route53domains update-domain-contact \
  --domain-name marabet.com \
  --admin-contact Email=comercial@marabet.com \
  --region us-east-1
```

### **Transferir Domínio:**

```bash
# Obter código de transferência (se quiser sair da AWS)
aws route53domains retrieve-domain-auth-code \
  --domain-name marabet.com \
  --region us-east-1
```

### **Renovar Manualmente:**

```bash
aws route53domains renew-domain \
  --domain-name marabet.com \
  --duration-in-years 1 \
  --region us-east-1
```

---

## 📞 SUPORTE

**AWS Route 53:**
- 📚 Docs: https://docs.aws.amazon.com/route53/
- 💬 Suporte: Via Console AWS
- 📧 Email: Via Support Case

**MaraBet AI:**
- 📧 Admin: admin@marabet.com
- 📧 Suporte: suporte@marabet.com
- 📧 Comercial: comercial@marabet.com

---

## ✅ VANTAGENS DE REGISTRAR VIA AWS

✅ **Integração Total** - Route 53 Hosted Zone automática  
✅ **Privacy Protection** - Grátis e automática  
✅ **Auto-Renew** - Nunca perde o domínio  
✅ **Email Forwarding** - Com SES (opcional)  
✅ **DNSSEC** - Segurança DNS avançada  
✅ **API Completa** - Automação total  
✅ **Billing Centralizado** - Uma fatura AWS  

---

**🌐 Domínio marabet.com**  
**✅ Registro via AWS Route 53**  
**🔒 Privacy Protection Incluída**  
**☁️ Integração Total com Infraestrutura AWS**

