# 📍 ELASTIC IP - GUIA COMPLETO

**Sistema**: MaraBet AI  
**Região**: eu-west-1  
**Finalidade**: IP fixo para EC2

---

## 📋 ÍNDICE

1. [Por que Elastic IP?](#por-que-elastic-ip)
2. [Alocar Elastic IP](#1-alocar-elastic-ip)
3. [Associar à EC2](#2-associar-à-ec2)
4. [Verificar](#3-verificar)
5. [Gerenciar](#4-gerenciar)
6. [Custos](#5-custos)

---

## 🎯 POR QUE ELASTIC IP?

### **Sem Elastic IP:**
❌ IP muda toda vez que EC2 reinicia  
❌ Precisa reconfigurar DNS  
❌ Precisa atualizar whitelist API-Football  
❌ Conexões SSH quebram  

### **Com Elastic IP:**
✅ IP fixo permanente  
✅ Sobrevive a reinicializações  
✅ Configuração única no DNS  
✅ Whitelist API-Football permanente  
✅ SSH sempre no mesmo IP  

**Recomendação**: ✅ **SEMPRE usar Elastic IP em produção!**

---

## 1️⃣ ALOCAR ELASTIC IP

### **Comando:**

```bash
# Alocar IP fixo
aws ec2 allocate-address \
  --domain vpc \
  --region eu-west-1
```

**Resultado:**
```json
{
    "PublicIp": "54.194.XXX.XXX",
    "AllocationId": "eipalloc-0a1b2c3d4e5f67890",
    "PublicIpv4Pool": "amazon",
    "NetworkBorderGroup": "eu-west-1",
    "Domain": "vpc"
}
```

### **Salvar IDs:**

```bash
export ELASTIC_IP=54.194.XXX.XXX
export ALLOCATION_ID=eipalloc-0a1b2c3d4e5f67890

echo "Elastic IP: $ELASTIC_IP"
echo "Allocation ID: $ALLOCATION_ID"
```

### **Adicionar Tags (Recomendado):**

```bash
aws ec2 create-tags \
  --resources $ALLOCATION_ID \
  --tags Key=Name,Value=marabet-elastic-ip Key=Project,Value=MaraBet Key=Environment,Value=production \
  --region eu-west-1
```

---

## 2️⃣ ASSOCIAR À EC2

### **Obter Instance ID:**

```bash
# Se não souber o Instance ID
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=marabet-ec2" "Name=instance-state-name,Values=running" \
  --region eu-west-1 \
  --query 'Reservations[0].Instances[0].InstanceId' \
  --output text)

echo "Instance ID: $INSTANCE_ID"
```

### **Associar Elastic IP:**

```bash
aws ec2 associate-address \
  --instance-id $INSTANCE_ID \
  --allocation-id $ALLOCATION_ID \
  --region eu-west-1
```

**Resultado:**
```json
{
    "AssociationId": "eipassoc-0a1b2c3d4e5f67890"
}
```

### **Salvar Association ID:**

```bash
export ASSOCIATION_ID=eipassoc-0a1b2c3d4e5f67890
```

---

## 3️⃣ VERIFICAR

### **Ver Elastic IPs:**

```bash
# Listar todos os Elastic IPs
aws ec2 describe-addresses \
  --region eu-west-1 \
  --query 'Addresses[*].[PublicIp,AllocationId,InstanceId,Tags[?Key==`Name`].Value|[0]]' \
  --output table
```

**Resultado:**
```
------------------------------------------------
| DescribeAddresses                             |
+------------------+---------------+------------+
| 54.194.XXX.XXX   | eipalloc-xxx  | i-xxxxx    |
+------------------+---------------+------------+
```

### **Ver Elastic IP Específico:**

```bash
aws ec2 describe-addresses \
  --allocation-ids $ALLOCATION_ID \
  --region eu-west-1
```

### **Ver IP da EC2:**

```bash
# IP público atual da EC2
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --region eu-west-1 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text

# Deve retornar o Elastic IP
```

---

## 4️⃣ GERENCIAR

### **Desassociar Elastic IP (manter alocado):**

```bash
aws ec2 disassociate-address \
  --association-id $ASSOCIATION_ID \
  --region eu-west-1
```

### **Reassociar a Outra EC2:**

```bash
# Associar a nova EC2
aws ec2 associate-address \
  --instance-id i-novainstancia \
  --allocation-id $ALLOCATION_ID \
  --region eu-west-1
```

### **Liberar Elastic IP (deletar):**

```bash
# ⚠️ CUIDADO: Só faça se não precisar mais!

# Primeiro desassociar
aws ec2 disassociate-address \
  --association-id $ASSOCIATION_ID \
  --region eu-west-1

# Depois liberar
aws ec2 release-address \
  --allocation-id $ALLOCATION_ID \
  --region eu-west-1
```

---

## 5️⃣ CUSTOS

### **Elastic IP:**

| Situação | Custo |
|----------|-------|
| **Associado a EC2 running** | Grátis ✅ |
| **Não associado (ocioso)** | $0.005/hora = ~$3.60/mês |
| **Associado a EC2 stopped** | $0.005/hora = ~$3.60/mês |

**Importante:**
- ✅ **Grátis** quando associado a EC2 running
- ⚠️ **Cobra** $3.60/mês se não estiver associado ou EC2 parada
- 💡 **Sempre mantenha associado** a uma EC2 running para evitar custos

### **Limite de Elastic IPs:**

- Padrão: 5 IPs por região
- Para mais: Solicitar aumento de quota via AWS Support

---

## 🔧 SCRIPT AUTOMÁTICO

### **Criar e Associar Elastic IP:**

```bash
#!/bin/bash

REGION="eu-west-1"
INSTANCE_NAME="marabet-ec2"

echo "📍 Alocando Elastic IP..."

# Alocar
ALLOCATION=$(aws ec2 allocate-address --domain vpc --region $REGION)
ELASTIC_IP=$(echo "$ALLOCATION" | jq -r '.PublicIp')
ALLOCATION_ID=$(echo "$ALLOCATION" | jq -r '.AllocationId')

echo "✅ Elastic IP alocado: $ELASTIC_IP"
echo "✅ Allocation ID: $ALLOCATION_ID"

# Adicionar tags
aws ec2 create-tags \
  --resources $ALLOCATION_ID \
  --tags Key=Name,Value=marabet-elastic-ip Key=Environment,Value=production \
  --region $REGION

echo "✅ Tags adicionadas"

# Obter Instance ID
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=$INSTANCE_NAME" "Name=instance-state-name,Values=running" \
  --region $REGION \
  --query 'Reservations[0].Instances[0].InstanceId' \
  --output text)

if [ ! -z "$INSTANCE_ID" ] && [ "$INSTANCE_ID" != "None" ]; then
    echo "✅ Instance encontrada: $INSTANCE_ID"
    
    # Associar
    ASSOCIATION=$(aws ec2 associate-address \
      --instance-id $INSTANCE_ID \
      --allocation-id $ALLOCATION_ID \
      --region $REGION)
    
    ASSOCIATION_ID=$(echo "$ASSOCIATION" | jq -r '.AssociationId')
    
    echo "✅ Elastic IP associado!"
    echo "✅ Association ID: $ASSOCIATION_ID"
    
    # Salvar informações
    cat > elastic-ip-info.txt << EOF
MaraBet AI - Elastic IP
=======================

Elastic IP:        $ELASTIC_IP
Allocation ID:     $ALLOCATION_ID
Association ID:    $ASSOCIATION_ID
Instance ID:       $INSTANCE_ID
Region:            $REGION

Criado em:         $(date)
EOF
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ ELASTIC IP CONFIGURADO!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  IP Fixo:      $ELASTIC_IP"
    echo "  Instance:     $INSTANCE_ID"
    echo ""
    echo "  SSH:          ssh -i marabet-key.pem ubuntu@$ELASTIC_IP"
    echo "  HTTP:         http://$ELASTIC_IP"
    echo ""
    echo "  ⚠️  Adicionar à API-Football: $ELASTIC_IP"
    echo ""
else
    echo "⚠️  Nenhuma EC2 running encontrada"
    echo "   Elastic IP alocado mas não associado"
    echo "   Associe manualmente após criar EC2"
fi
```

Salvar como: `alocar_elastic_ip.sh`

---

## 📝 USAR NO .env

### **Atualizar Configuração:**

```bash
# .env
EC2_ELASTIC_IP=54.194.XXX.XXX
EC2_ALLOCATION_ID=eipalloc-0a1b2c3d4e5f67890
EC2_ASSOCIATION_ID=eipassoc-0a1b2c3d4e5f67890

# URLs públicas
APP_URL=http://54.194.XXX.XXX
API_URL=http://54.194.XXX.XXX/api
```

---

## 🔄 CENÁRIOS COMUNS

### **Cenário 1: Reiniciar EC2**

```bash
# Parar EC2
aws ec2 stop-instances --instance-ids $INSTANCE_ID --region eu-west-1

# Iniciar EC2
aws ec2 start-instances --instance-ids $INSTANCE_ID --region eu-west-1

# ✅ Elastic IP permanece o mesmo!
# ✅ Nenhuma reconfiguração necessária
```

### **Cenário 2: Trocar EC2 (upgrade/downgrade)**

```bash
# 1. Criar nova EC2
NOVA_INSTANCE_ID=i-novainstancia

# 2. Desassociar Elastic IP da antiga
aws ec2 disassociate-address \
  --association-id $ASSOCIATION_ID \
  --region eu-west-1

# 3. Associar à nova EC2
aws ec2 associate-address \
  --instance-id $NOVA_INSTANCE_ID \
  --allocation-id $ALLOCATION_ID \
  --region eu-west-1

# ✅ IP permanece o mesmo
# ✅ DNS não precisa mudar
# ✅ API-Football whitelist permanece válido
```

### **Cenário 3: Disaster Recovery**

```bash
# Se EC2 falhar, criar nova e reassociar IP
# Tempo de recuperação: ~5 minutos
# IP permanece o mesmo: Zero impacto nos usuários
```

---

## ⚠️ BOAS PRÁTICAS

### **1. Sempre Alocar para Produção:**
```bash
# Produção: SEMPRE use Elastic IP
# Desenvolvimento/Staging: IP dinâmico OK
```

### **2. Liberar IPs Não Usados:**
```bash
# Verificar IPs ociosos
aws ec2 describe-addresses \
  --region eu-west-1 \
  --query 'Addresses[?InstanceId==null].[PublicIp,AllocationId]' \
  --output table

# Liberar IPs ociosos (evitar custos)
aws ec2 release-address --allocation-id eipalloc-xxxxx --region eu-west-1
```

### **3. Documentar:**
```bash
# Sempre salvar:
# - Elastic IP
# - Allocation ID
# - Association ID
# - Onde está sendo usado
```

### **4. Tags:**
```bash
# Sempre adicionar tags
aws ec2 create-tags \
  --resources $ALLOCATION_ID \
  --tags \
    Key=Name,Value=marabet-elastic-ip \
    Key=Environment,Value=production \
    Key=Owner,Value=MaraBet-Team \
  --region eu-west-1
```

---

## 🔍 COMANDOS ÚTEIS

### **Listar Todos os Elastic IPs:**

```bash
aws ec2 describe-addresses --region eu-west-1
```

### **Filtrar por Tags:**

```bash
aws ec2 describe-addresses \
  --filters "Name=tag:Project,Values=MaraBet" \
  --region eu-west-1
```

### **Ver IP de uma EC2:**

```bash
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --region eu-west-1 \
  --query 'Reservations[0].Instances[0].[PublicIpAddress,Tags[?Key==`Name`].Value|[0]]' \
  --output table
```

### **Ver Todas as Associações:**

```bash
aws ec2 describe-addresses \
  --region eu-west-1 \
  --query 'Addresses[*].[PublicIp,InstanceId,AllocationId,AssociationId]' \
  --output table
```

---

## 💰 CUSTOS

### **Tabela de Custos:**

| Situação | Custo/hora | Custo/mês |
|----------|------------|-----------|
| **Associado a EC2 running** | $0.00 | **Grátis** ✅ |
| **Não associado** | $0.005 | $3.60 |
| **EC2 stopped** | $0.005 | $3.60 |
| **Múltiplos IPs na mesma EC2** | $0.005 | $3.60/IP extra |

**Conclusão:**
- ✅ Use 1 Elastic IP por EC2 = **Grátis**
- ⚠️ Libere IPs não usados = **Economize $3.60/mês por IP**

---

## 🛡️ PROTEÇÃO

### **Evitar Perda Acidental:**

```bash
# Criar alarme se IP ficar desassociado
aws cloudwatch put-metric-alarm \
  --alarm-name marabet-elastic-ip-unassociated \
  --alarm-description "Alerta se Elastic IP ficar desassociado" \
  --metric-name PublicIp \
  --namespace AWS/EC2 \
  --statistic SampleCount \
  --period 300 \
  --threshold 1 \
  --comparison-operator LessThanThreshold \
  --evaluation-periods 1 \
  --region eu-west-1
```

---

## 📋 CHECKLIST

- [ ] Elastic IP alocado
- [ ] Allocation ID salvo
- [ ] Tags adicionadas
- [ ] Elastic IP associado à EC2
- [ ] Association ID salvo
- [ ] IP testado (SSH, HTTP)
- [ ] IP adicionado ao DNS (Route 53)
- [ ] IP adicionado à API-Football whitelist
- [ ] Informações documentadas
- [ ] Backup dos IDs feito

---

## 🔧 TROUBLESHOOTING

### **Erro: "Address does not belong to you"**

```bash
# Allocation ID incorreto ou de outra conta
# Verificar:
aws ec2 describe-addresses --region eu-west-1
```

### **Erro: "Resource has a public IP address"**

```bash
# EC2 já tem IP público dinâmico
# Solução: Desassociar o IP dinâmico primeiro
# (AWS faz isso automaticamente ao associar Elastic IP)
```

### **Erro: "You have reached the maximum"**

```bash
# Limite de 5 Elastic IPs por região
# Solicitar aumento:
# AWS Console > Service Quotas > EC2 > Elastic IPs
```

---

## 📞 PRÓXIMOS PASSOS

1. ✅ Elastic IP alocado
2. ✅ IP associado à EC2
3. **Adicionar ao DNS** (Route 53)
4. **Adicionar à API-Football** whitelist
5. **Testar** conexão SSH com IP fixo
6. **Documentar** IP no README

---

**📍 Elastic IP Configurado!**  
**✅ IP Fixo Permanente**  
**🔒 Protegido Contra Reinicializações**  
**☁️ MaraBet AI - AWS Production Ready**

