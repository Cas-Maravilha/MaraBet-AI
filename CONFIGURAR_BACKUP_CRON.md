# ⏰ CONFIGURAR BACKUP AUTOMÁTICO - CRON

**Script**: backup_to_s3.sh  
**Frequência**: Diário às 2h  
**Retenção**: 30/90/365 dias

---

## 🔧 CONFIGURAÇÃO

### **1. Copiar Script para EC2:**

```bash
# Do PC
scp -i marabet-key.pem backups/scripts/backup_to_s3.sh ubuntu@[ELASTIC_IP]:/tmp/

# Na EC2
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

sudo mkdir -p /opt/marabet/backups/scripts
sudo mv /tmp/backup_to_s3.sh /opt/marabet/backups/scripts/
sudo chmod +x /opt/marabet/backups/scripts/backup_to_s3.sh
sudo chown marabet:marabet /opt/marabet/backups/scripts/backup_to_s3.sh
```

---

### **2. Testar Script Manualmente:**

```bash
# Como usuário marabet
sudo su - marabet

# Executar backup
cd /opt/marabet
./backups/scripts/backup_to_s3.sh

# Verificar logs
cat /var/log/marabet/backup.log

# Verificar S3
aws s3 ls s3://marabet-backups/daily/ --human-readable
```

---

### **3. Configurar Cron:**

```bash
# Editar crontab do usuário marabet
sudo -u marabet crontab -e

# Adicionar linha:
0 2 * * * /opt/marabet/backups/scripts/backup_to_s3.sh >> /var/log/marabet/backup.log 2>&1

# Explicação:
# 0 2 * * *     = Todo dia às 02:00 (horário de Luanda)
# >> ...log     = Append output ao log
# 2>&1          = Redirecionar stderr para stdout
```

### **Salvar e Sair:**
- Nano: `Ctrl+O`, `Enter`, `Ctrl+X`
- Vim: `Esc`, `:wq`, `Enter`

---

### **4. Verificar Cron:**

```bash
# Ver crontab do marabet
sudo -u marabet crontab -l

# Resultado esperado:
# 0 2 * * * /opt/marabet/backups/scripts/backup_to_s3.sh >> /var/log/marabet/backup.log 2>&1
```

---

## 📅 SCHEDULE DE BACKUPS

### **Automático:**

```
Tipo        Quando              Retenção    Storage Class
────────────────────────────────────────────────────────────────
Daily       Todo dia 02:00      30 dias     S3 Standard
Weekly      Domingo 02:00       90 dias     S3 Standard
Monthly     Dia 1 02:00         365 dias    S3 Standard → Glacier (90 dias)
```

### **O Script Detecta Automaticamente:**

- **Domingo** → Salva em `weekly/`
- **Dia 1** → Salva em `monthly/`
- **Outros** → Salva em `daily/`

---

## 💾 O QUE É FEITO BACKUP

### **1. Database (PostgreSQL):**
- Dump completo via `pg_dump`
- Formato: Custom (.dump)
- Compressão: gzip
- Snapshot RDS adicional (AWS)

### **2. Redis:**
- Keys list
- RDB dump (se disponível)
- Serverless: Gerenciado pela AWS

### **3. Arquivos da Aplicação:**
- Código fonte
- Static files
- Media files
- Logs importantes
- Excluídos: venv, __pycache__, .git

### **4. Configurações:**
- .env (encriptado com senha do DB)
- docker-compose.yml
- nginx configs

---

## 🔐 SEGURANÇA

### **Encriptação:**

```
.env:             OpenSSL AES-256-CBC (senha: DB_PASSWORD)
S3:               AES256 server-side
RDS Snapshots:    Encriptados (AWS KMS)
```

### **Descriptografar .env:**

```bash
# Download do S3
aws s3 cp s3://marabet-backups/daily/env_2025-10-27_02-00-00.enc ./

# Descriptografar
openssl enc -aes-256-cbc -d \
    -in env_2025-10-27_02-00-00.enc \
    -out .env \
    -pass pass:"GuF#Y(!j38Bgw|YyT<r0J5>yxD3n"
```

---

## 📊 MONITORAMENTO

### **Ver Logs de Backup:**

```bash
# Últimas execuções
sudo tail -50 /var/log/marabet/backup.log

# Seguir em tempo real
sudo tail -f /var/log/marabet/backup.log

# Filtrar por data
sudo grep "2025-10-27" /var/log/marabet/backup.log
```

### **Verificar Cron Executou:**

```bash
# Ver logs do cron
sudo grep backup /var/log/syslog

# Ver última execução
sudo journalctl -u cron | grep backup | tail -5
```

### **Listar Backups S3:**

```bash
# Todos
aws s3 ls s3://marabet-backups/ --recursive --human-readable

# Por tipo
aws s3 ls s3://marabet-backups/daily/ --human-readable
aws s3 ls s3://marabet-backups/weekly/ --human-readable
aws s3 ls s3://marabet-backups/monthly/ --human-readable

# Tamanho total
aws s3 ls s3://marabet-backups/ --recursive --summarize --human-readable
```

---

## 🔄 RESTORE (RECUPERAÇÃO)

### **Restaurar Database:**

```bash
# 1. Listar backups
aws s3 ls s3://marabet-backups/daily/ | grep database

# 2. Download
aws s3 cp s3://marabet-backups/daily/database_2025-10-27_02-00-00.dump.gz ./

# 3. Descomprimir
gunzip database_2025-10-27_02-00-00.dump.gz

# 4. Restaurar
PGPASSWORD=GuF#Y(!j38Bgw|YyT<r0J5>yxD3n pg_restore \
    -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
    -p 5432 \
    -U marabet_admin \
    -d marabet_production \
    -c \
    database_2025-10-27_02-00-00.dump
```

---

## 💰 CUSTOS

### **Estimativa para MaraBet:**

| Tipo | Tamanho | Retenção | Custo/mês |
|------|---------|----------|-----------|
| **Database daily** | 50GB | 30 dias | $1.15 |
| **App files daily** | 10GB | 30 dias | $0.23 |
| **Weekly** | 60GB | 90 dias | $1.38 |
| **Monthly (Glacier)** | 60GB | 365 dias | $0.24 |
| **RDS Snapshots** | 100GB | 7 dias | $0.95 |
| **TOTAL** | ~280GB | - | **~$4-5/mês** |

---

## ✅ CHECKLIST

- [ ] Bucket S3 criado
- [ ] Script backup_to_s3.sh na EC2
- [ ] Script com permissão de execução
- [ ] Testado manualmente
- [ ] Cron configurado (2h da manhã)
- [ ] Logs criados
- [ ] Backups aparecem no S3
- [ ] Restore testado
- [ ] Notificação Telegram (opcional)
- [ ] CloudWatch alarm (opcional)

---

## 📞 COMANDOS ÚTEIS

```bash
# Executar backup manualmente
sudo -u marabet /opt/marabet/backups/scripts/backup_to_s3.sh

# Ver último backup
aws s3 ls s3://marabet-backups/daily/ --human-readable | tail -5

# Download backup mais recente
aws s3 cp s3://marabet-backups/daily/$(aws s3 ls s3://marabet-backups/daily/ | sort | tail -1 | awk '{print $4}') ./

# Ver cron
sudo -u marabet crontab -l

# Ver logs
sudo tail -f /var/log/marabet/backup.log
```

---

**💾 Backup Automático Configurado!**  
**✅ S3 + RDS Snapshots**  
**🔒 Encriptado**  
**⏰ Diário às 2h**  
**☁️ MaraBet.com Protegido**

