# 🔧 MANUTENÇÃO DIÁRIA - MARABET.COM

**Sistema**: MaraBet AI  
**Ambiente**: Produção AWS  
**Frequência**: Diária/Semanal/Mensal

---

## 📋 CHECKLIST DIÁRIO (5-10 MINUTOS)

### **1. Verificar Status dos Serviços:**

```bash
# SSH na EC2
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Trocar para marabet
sudo su - marabet
cd /opt/marabet

# Status dos containers
docker-compose ps

# Resultado esperado:
# NAME                 STATUS         PORTS
# marabet-web          Up (healthy)   0.0.0.0:8000->8000/tcp
# marabet-celery       Up             
# marabet-celery-beat  Up

# Se algum está "Exit" ou "Restarting":
docker-compose logs [container_name]
docker-compose restart [container_name]
```

---

### **2. Verificar Logs:**

```bash
# Últimas 50 linhas de todos os serviços
docker-compose logs --tail=50

# Apenas erros
docker-compose logs --tail=100 | grep -i "error\|exception\|critical"

# Logs específicos
docker-compose logs --tail=50 web
docker-compose logs --tail=50 celery

# Logs do Nginx (como root)
exit  # Sair do usuário marabet
sudo tail -50 /var/log/nginx/marabet-error.log
sudo tail -50 /var/log/nginx/marabet-access.log | tail -20
```

---

### **3. Verificar Recursos do Sistema:**

```bash
# CPU, RAM, Processos
htop

# Uso de disco
df -h

# Resultado importante:
# /dev/xvda1    50G   15G   35G   30% /    ← Deve estar < 80%

# Memória
free -h

# Resultado:
#               total        used        free
# Mem:           3.8Gi       2.1Gi       1.0Gi    ← Used < 85%

# Docker stats
docker stats --no-stream
```

---

### **4. Health Check da Aplicação:**

```bash
# Testar endpoint
curl http://localhost:8000/health

# Resultado esperado:
# {"status":"ok","timestamp":"...","database":"connected","redis":"connected"}

# Testar HTTPS
curl https://marabet.com/health

# Testar API
curl https://api.marabet.com/status
```

---

### **5. Verificar Backups:**

```bash
# Último backup local
ls -lth /opt/marabet/backups/ | head -5

# Backups no S3
aws s3 ls s3://marabet-backups/daily/ --human-readable | tail -5

# Log de backup
tail -20 /var/log/marabet/backup.log
```

---

### **6. CloudWatch (Via Console AWS):**

```
1. Acessar: https://console.aws.amazon.com/cloudwatch/
2. Região: eu-west-1
3. Verificar:
   • Dashboards > MaraBet (se criou)
   • Alarms > Ver se algum está em ALARM
   • Log groups > /marabet/* > Ver erros recentes
```

---

## 📅 CHECKLIST SEMANAL (15-20 MINUTOS)

### **1. Atualizar Sistema:**

```bash
# Atualizar packages
sudo apt-get update
sudo apt-get upgrade -y

# Verificar se precisa restart
sudo needrestart -r l
```

---

### **2. Verificar Certificado SSL:**

```bash
# Ver quando expira
sudo certbot certificates

# Testar renovação
sudo certbot renew --dry-run

# Ver logs de renovação
sudo cat /var/log/letsencrypt/letsencrypt.log | tail -50
```

---

### **3. Revisar Logs de Segurança:**

```bash
# Fail2Ban - Ver bloqueios
sudo fail2ban-client status sshd

# UFW - Ver regras
sudo ufw status verbose

# Logins SSH suspeitos
sudo grep "Failed password" /var/log/auth.log | tail -20

# Conexões ativas
sudo netstat -tunlp | grep ESTABLISHED | wc -l
```

---

### **4. Verificar Snapshots RDS:**

```bash
# Listar snapshots RDS
aws rds describe-db-snapshots \
    --db-instance-identifier database-1 \
    --region eu-west-1 \
    --query 'DBSnapshots[*].[DBSnapshotIdentifier,SnapshotCreateTime,Status]' \
    --output table

# Deletar snapshots antigos (>30 dias)
# (Feito automaticamente pelo script de backup)
```

---

### **5. Revisar Custos AWS:**

```bash
# Ver custo do mês atual (CLI)
aws ce get-cost-and-usage \
    --time-period Start=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --region us-east-1

# Ou via Console:
# AWS Console > Billing > Cost Explorer
```

---

## 📆 CHECKLIST MENSAL (30-45 MINUTOS)

### **1. Análise de Performance:**

```bash
# CloudWatch Insights - Top queries lentas
# RDS Performance Insights (Console)
# Identificar queries problemáticas

# Verificar índices do database
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d marabet_production \
     -c "SELECT schemaname, tablename, indexname FROM pg_indexes WHERE schemaname = 'public';"

# Tamanho das tabelas
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d marabet_production \
     -c "SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"
```

---

### **2. Otimização:**

```bash
# Limpar logs antigos
sudo find /var/log -name "*.log" -mtime +30 -delete
sudo journalctl --vacuum-time=30d

# Limpar Docker
docker system prune -a -f
docker volume prune -f

# Limpar APT cache
sudo apt-get clean
sudo apt-get autoclean
```

---

### **3. Revisar Alarmes:**

```bash
# Ver alarmes disparados no mês
aws cloudwatch describe-alarm-history \
    --alarm-name marabet-ec2-high-cpu \
    --start-date $(date -d "30 days ago" +%Y-%m-%d) \
    --region eu-west-1

# Ajustar thresholds se necessário
```

---

### **4. Testar Disaster Recovery:**

```bash
# Testar restore de um backup antigo (em ambiente de teste)
# NÃO executar em produção!

# 1. Baixar backup de 7 dias atrás
# 2. Restaurar em database de teste
# 3. Verificar integridade
# 4. Documentar tempo de recovery
```

---

## 🚨 TROUBLESHOOTING COMUM

### **Container Reiniciando:**

```bash
# Ver logs
docker-compose logs [container]

# Verificar health
docker inspect marabet-web | jq '.[0].State.Health'

# Restart
docker-compose restart [container]
```

### **Disk Cheio:**

```bash
# Ver uso
df -h

# Limpar
sudo docker system prune -a -f
sudo journalctl --vacuum-time=7d
sudo find /var/log -name "*.log" -mtime +7 -delete
```

### **High CPU/RAM:**

```bash
# Ver processos
htop

# Ver Docker stats
docker stats

# Se necessário, restart
docker-compose restart
```

### **SSL Expirado:**

```bash
# Renovar manualmente
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

---

## 📊 SCRIPT DE VERIFICAÇÃO DIÁRIA

### **Criar: `/usr/local/bin/check-marabet.sh`**

```bash
#!/bin/bash

echo "🔍 MaraBet AI - Verificação Diária"
echo "=================================="
echo "$(date)"
echo ""

# 1. Containers
echo "1. Containers:"
docker-compose -f /opt/marabet/docker-compose.yml ps 2>/dev/null | grep -q "Up" && echo "  ✅ Rodando" || echo "  ❌ Problemas"

# 2. Disco
echo ""
echo "2. Disco:"
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "  ✅ $DISK_USAGE% usado"
else
    echo "  ⚠️  $DISK_USAGE% usado (alto!)"
fi

# 3. Memória
echo ""
echo "3. Memória:"
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ "$MEM_USAGE" -lt 85 ]; then
    echo "  ✅ $MEM_USAGE% usado"
else
    echo "  ⚠️  $MEM_USAGE% usado (alto!)"
fi

# 4. HTTPS
echo ""
echo "4. HTTPS:"
curl -s -o /dev/null -w "%{http_code}" https://marabet.com/health | grep -q 200 && echo "  ✅ Funcionando" || echo "  ❌ Não responde"

# 5. SSL Expiry
echo ""
echo "5. SSL Certificate:"
DAYS_LEFT=$((($(date -d "$(openssl s_client -connect marabet.com:443 -servername marabet.com < /dev/null 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)" +%s) - $(date +%s)) / 86400))
if [ "$DAYS_LEFT" -gt 30 ]; then
    echo "  ✅ Expira em $DAYS_LEFT dias"
else
    echo "  ⚠️  Expira em $DAYS_LEFT dias (renovar!)"
fi

# 6. Último Backup
echo ""
echo "6. Último Backup:"
LAST_BACKUP=$(aws s3 ls s3://marabet-backups/daily/ | tail -1 | awk '{print $1, $2}')
echo "  ℹ️  $LAST_BACKUP"

echo ""
echo "✅ Verificação completa!"
```

**Adicionar ao cron:**
```bash
# Executar todo dia às 9h
0 9 * * * /usr/local/bin/check-marabet.sh | mail -s "MaraBet Daily Check" admin@marabet.com
```

---

## ✅ **MANUTENÇÃO CONFIGURADA**

- Verificação diária automatizada
- Backup automático S3
- Monitoramento CloudWatch 24/7
- Alarmes configurados
- Logs centralizados

---

**🔧 Manutenção Enterprise Configurada!**  
**✅ marabet.com Monitorado 24/7**  
**☁️ AWS Production Ready**  
**🎉 SISTEMA COMPLETO! 🚀**
