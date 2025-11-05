# 🔧 OPERAÇÕES COMPLETAS - MARABET.COM

**Sistema**: MaraBet AI AWS Enterprise  
**Manutenção**: Diária, Semanal, Mensal

---

## 📅 TAREFAS DIÁRIAS (5-10 MIN)

```bash
# 1. Status dos serviços
docker-compose ps

# 2. Logs (últimas 50 linhas)
docker-compose logs --tail=50

# 3. Recursos
htop  # CPU/RAM
df -h # Disco
free -h # Memória

# 4. Health check
curl https://marabet.com/health

# 5. CloudWatch (Console AWS)
# Verificar alarmes e métricas
```

---

## 📅 TAREFAS SEMANAIS (15-20 MIN)

```bash
# 1. Atualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# 2. Verificar backups (últimos 7 dias)
aws s3 ls s3://marabet-backups/daily/ --human-readable | tail -7

# 3. Revisar logs de erro
grep -i "error\|exception" /opt/marabet/logs/*.log | tail -50

# 4. Verificar SSL
sudo certbot certificates

# 5. Limpar Docker
docker system prune -f

# 6. Verificar disco
df -h
# Se > 80%, limpar:
sudo journalctl --vacuum-time=7d
sudo find /var/log -name "*.log" -mtime +7 -delete
```

---

## 📅 TAREFAS MENSAIS (30-45 MIN)

```bash
# 1. Testar restauração de backup
./backups/scripts/restore_from_s3.sh [TIMESTAMP] --test

# 2. Revisar custos AWS
# Console > Billing > Cost Explorer

# 3. Otimizar database
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d marabet_production \
     -c "VACUUM ANALYZE;"

# 4. Revisar alarmes CloudWatch
aws cloudwatch describe-alarm-history --region eu-west-1

# 5. Atualizar documentação de mudanças

# 6. Revisar Security Groups
aws ec2 describe-security-groups --region eu-west-1

# 7. Verificar certificados SSL (expiração)
openssl s_client -connect marabet.com:443 < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

---

## 🚨 PROCEDIMENTOS DE EMERGÊNCIA

### **Aplicação Offline:**

```bash
# 1. Verificar containers
docker-compose ps

# 2. Restart
docker-compose restart

# 3. Se não resolver, rebuild
docker-compose down
docker-compose up -d --build

# 4. Ver logs
docker-compose logs -f
```

### **Database Slow:**

```bash
# Ver conexões ativas
psql -h database-1... -U marabet_admin -d marabet_production \
    -c "SELECT count(*) FROM pg_stat_activity;"

# Ver queries lentas
psql -h database-1... -U marabet_admin -d marabet_production \
    -c "SELECT pid, now() - query_start as duration, query FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC LIMIT 10;"

# Matar query específica (cuidado!)
# SELECT pg_terminate_backend(PID);
```

### **Disk Cheio:**

```bash
# Limpar logs
sudo journalctl --vacuum-size=100M
sudo find /var/log -name "*.log" -mtime +3 -delete

# Limpar Docker
docker system prune -a -f --volumes

# Limpar backups locais
sudo rm -rf /opt/marabet/backups/*.gz

# Se crítico, aumentar volume EBS via AWS Console
```

---

## 📊 DASHBOARD DE MONITORAMENTO

### **Métricas Chave:**

```yaml
Aplicação:
  - Health check: OK/FAIL
  - Response time: < 500ms
  - Error rate 5xx: < 1%
  - Requests/min: Variável

EC2:
  - CPU: < 70%
  - RAM: < 80%
  - Disk: < 75%
  - Network: Estável

RDS:
  - CPU: < 70%
  - Connections: < 100
  - Storage: > 20GB free
  - Replication lag: 0

Redis:
  - Memory: < 80%
  - Connections: Estável
  - Hit rate: > 90%

Backup:
  - Último: < 24h
  - Status: Success
  - Size: Estável
```

---

## ✅ CHECKLIST OPERACIONAL

### **Diário:**
- [ ] Status containers OK
- [ ] Logs sem erros críticos
- [ ] Health check respondendo
- [ ] Recursos < 80%
- [ ] CloudWatch sem alarmes

### **Semanal:**
- [ ] Sistema atualizado
- [ ] Backups verificados
- [ ] SSL válido
- [ ] Logs de segurança OK
- [ ] Docker limpo

### **Mensal:**
- [ ] Restore testado
- [ ] Custos revisados
- [ ] Database otimizado
- [ ] Alarmes ajustados
- [ ] Documentação atualizada

---

## 📞 CONTATOS DE SUPORTE

### **MaraBet:**
- 📧 Técnico: suporte@marabet.com
- 📧 Emergência: admin@marabet.com
- 📞 WhatsApp: +224 932027393

### **AWS:**
- 📚 Docs: https://docs.aws.amazon.com
- 💬 Support: Console AWS
- 📞 Enterprise: 24/7

---

**🔧 Operações Enterprise Configuradas!**  
**✅ Manutenção Documentada**  
**📊 Monitoramento 24/7**  
**🌐 marabet.com Pronto**

