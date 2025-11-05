#!/bin/bash

################################################################################
# MARABET AI - CRIAR ALARMES CLOUDWATCH
# Alarmes para CPU, RAM, Disk, RDS, Redis
################################################################################

set -e

echo "========================================================================"
echo "🚨 MaraBet AI - Criar Alarmes CloudWatch"
echo "========================================================================"
echo ""

# Configurações
REGION="eu-west-1"
SNS_EMAIL="suporte@marabet.com"

# Obter Instance ID
INSTANCE_ID=$(ec2-metadata --instance-id | cut -d " " -f 2 2>/dev/null || echo "i-xxxxxxxxx")

echo "[ℹ] Instance ID: $INSTANCE_ID"
echo "[ℹ] Região: $REGION"
echo "[ℹ] Email notificações: $SNS_EMAIL"
echo ""

################################################################################
# 1. CRIAR SNS TOPIC
################################################################################

echo "1. Criando SNS Topic para notificações..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SNS_TOPIC_ARN=$(aws sns create-topic \
    --name marabet-alerts \
    --region $REGION \
    --query 'TopicArn' \
    --output text 2>&1)

if [[ $SNS_TOPIC_ARN == arn:* ]]; then
    echo "[✓] SNS Topic criado: $SNS_TOPIC_ARN"
else
    echo "[!] SNS Topic pode já existir"
    SNS_TOPIC_ARN=$(aws sns list-topics \
        --region $REGION \
        --query 'Topics[?contains(TopicArn, `marabet-alerts`)].TopicArn' \
        --output text)
    echo "[ℹ] Usando: $SNS_TOPIC_ARN"
fi

# Subscribe email
aws sns subscribe \
    --topic-arn $SNS_TOPIC_ARN \
    --protocol email \
    --notification-endpoint $SNS_EMAIL \
    --region $REGION 2>/dev/null || echo "[!] Email subscription pode já existir"

echo ""
echo "[!] IMPORTANTE: Verifique o email $SNS_EMAIL e confirme a inscrição!"
echo ""

################################################################################
# 2. ALARME: CPU ALTA
################################################################################

echo ""
echo "2. Criando alarme: CPU Alta..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

aws cloudwatch put-metric-alarm \
    --alarm-name marabet-ec2-high-cpu \
    --alarm-description "MaraBet EC2 - CPU acima de 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --dimensions Name=InstanceId,Value=$INSTANCE_ID \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

echo "[✓] Alarme CPU criado"

################################################################################
# 3. ALARME: MEMÓRIA ALTA
################################################################################

echo ""
echo "3. Criando alarme: Memória Alta..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

aws cloudwatch put-metric-alarm \
    --alarm-name marabet-ec2-high-memory \
    --alarm-description "MaraBet EC2 - Memória acima de 85%" \
    --metric-name MEM_USED \
    --namespace MaraBet/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 85 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

echo "[✓] Alarme Memória criado"

################################################################################
# 4. ALARME: DISCO CHEIO
################################################################################

echo ""
echo "4. Criando alarme: Disco Cheio..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

aws cloudwatch put-metric-alarm \
    --alarm-name marabet-ec2-high-disk \
    --alarm-description "MaraBet EC2 - Disco acima de 90%" \
    --metric-name DISK_USED \
    --namespace MaraBet/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 90 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

echo "[✓] Alarme Disco criado"

################################################################################
# 5. ALARME: RDS CPU
################################################################################

echo ""
echo "5. Criando alarme: RDS CPU Alta..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

aws cloudwatch put-metric-alarm \
    --alarm-name marabet-rds-high-cpu \
    --alarm-description "MaraBet RDS - CPU acima de 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --dimensions Name=DBInstanceIdentifier,Value=database-1 \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

echo "[✓] Alarme RDS CPU criado"

################################################################################
# 6. ALARME: RDS CONEXÕES
################################################################################

echo ""
echo "6. Criando alarme: RDS Conexões..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

aws cloudwatch put-metric-alarm \
    --alarm-name marabet-rds-high-connections \
    --alarm-description "MaraBet RDS - Conexões acima de 100" \
    --metric-name DatabaseConnections \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 100 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --dimensions Name=DBInstanceIdentifier,Value=database-1 \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

echo "[✓] Alarme RDS Conexões criado"

################################################################################
# 7. ALARME: RDS STORAGE
################################################################################

echo ""
echo "7. Criando alarme: RDS Storage..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

aws cloudwatch put-metric-alarm \
    --alarm-name marabet-rds-low-storage \
    --alarm-description "MaraBet RDS - Storage livre abaixo de 10GB" \
    --metric-name FreeStorageSpace \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 10000000000 \
    --comparison-operator LessThanThreshold \
    --evaluation-periods 1 \
    --dimensions Name=DBInstanceIdentifier,Value=database-1 \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

echo "[✓] Alarme RDS Storage criado"

################################################################################
# 8. ALARME: REDIS MEMORY
################################################################################

echo ""
echo "8. Criando alarme: Redis Memory..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

aws cloudwatch put-metric-alarm \
    --alarm-name marabet-redis-high-memory \
    --alarm-description "MaraBet Redis - Memória acima de 80%" \
    --metric-name DatabaseMemoryUsagePercentage \
    --namespace AWS/ElastiCache \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION 2>/dev/null || echo "[!] Redis Serverless não suporta esta métrica"

################################################################################
# 9. SALVAR INFORMAÇÕES
################################################################################

echo ""
echo "9. Salvando informações..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > cloudwatch-alarms-info.txt << EOF
MaraBet AI - CloudWatch Alarms
===============================

SNS Topic:            $SNS_TOPIC_ARN
Email:                $SNS_EMAIL
Região:               $REGION

Alarmes Criados:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EC2:
  • marabet-ec2-high-cpu         CPU > 80%
  • marabet-ec2-high-memory      RAM > 85%
  • marabet-ec2-high-disk        Disk > 90%

RDS:
  • marabet-rds-high-cpu         CPU > 80%
  • marabet-rds-high-connections Conexões > 100
  • marabet-rds-low-storage      Storage < 10GB

Notificações:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Email:                $SNS_EMAIL
⚠️  Confirme a inscrição no email!

Ver Alarmes:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Console:
  https://console.aws.amazon.com/cloudwatch/home?region=$REGION#alarmsV2:

CLI:
  aws cloudwatch describe-alarms --region $REGION

Comandos:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Listar alarmes:
  aws cloudwatch describe-alarms --region $REGION

Ver histórico de alarme:
  aws cloudwatch describe-alarm-history --alarm-name marabet-ec2-high-cpu --region $REGION

Deletar alarme:
  aws cloudwatch delete-alarms --alarm-names marabet-ec2-high-cpu --region $REGION

Criado em:            $(date)
EOF

echo "[✓] cloudwatch-alarms-info.txt criado"

################################################################################
# RESUMO
################################################################################

echo ""
echo "========================================================================"
echo "✅ ALARMES CLOUDWATCH CRIADOS!"
echo "========================================================================"
echo ""

echo "Total de alarmes:      7"
echo "SNS Topic:             $SNS_TOPIC_ARN"
echo "Email notificações:    $SNS_EMAIL"
echo ""

echo "⚠️  IMPORTANTE:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Verifique o email $SNS_EMAIL"
echo "  Confirme a inscrição no SNS Topic"
echo "  (Procure email da AWS com assunto: 'Subscription Confirmation')"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "✅ Monitoramento ativo!"
echo ""

