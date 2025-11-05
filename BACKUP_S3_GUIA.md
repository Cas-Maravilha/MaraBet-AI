# 💾 BACKUP S3 - GUIA COMPLETO

**Bucket**: marabet-backups  
**Região**: eu-west-1  
**Frequência**: Diário, Semanal, Mensal

---

## 🎯 CONFIGURAÇÃO

### **1. Criar Bucket S3:**

```bash
chmod +x criar_bucket_backup.sh
./criar_bucket_backup.sh

# Resultado:
# ✅ Bucket criado
# ✅ Versionamento habilitado
# ✅ Encriptação ativa
# ✅ Lifecycle configurada
```

---

### **2. Copiar Script de Backup para EC2:**

```bash
# Do PC para EC2
scp -i marabet-key.pem criar_backup_automatico.sh ubuntu@[ELASTIC_IP]:/tmp/

# Na EC2
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

sudo mv /tmp/criar_backup_automatico.sh /usr/local/bin/marabet-backup.sh
sudo chmod +x /usr/local/bin/marabet-backup.sh
sudo chown marabet:marabet /usr/local/bin/marabet-backup.sh
```

---

### **3. Configurar Cron (Backup Automático):**

```bash
# Editar crontab do usuário marabet
sudo -u marabet crontab -e

# Adicionar:
# Backup diário às 2h da manhã
0 2 * * * /usr/local/bin/marabet-backup.sh >> /var/log/marabet/backup.log 2>&1

# Explicação:
# 0 2 * * *     = Todo dia às 02:00
# Domingo       = Backup semanal (automático pelo script)
# Dia 1 do mês  = Backup mensal (automático pelo script)
```

---

### **4. Testar Backup Manualmente:**

```bash
# Executar script
sudo -u marabet /usr/local/bin/marabet-backup.sh

# Verificar se criou arquivos
ls -lh /opt/marabet/backups/

# Verificar no S3
aws s3 ls s3://marabet-backups/daily/ --human-readable
```

---

## 📊 ESTRUTURA DE BACKUPS

### **No S3:**

```
s3://marabet-backups/
├── daily/                  (Retenção: 30 dias)
│   ├── database_20251027_020000.sql.gz
│   ├── static_media_20251027_020000.tar.gz
│   └── env_20251027_020000.enc
│
├── weekly/                 (Retenção: 90 dias)
│   └── database_20251027_020000.sql.gz
│
├── monthly/                (Retenção: 365 dias → Glacier)
│   └── database_20251001_020000.sql.gz
│
├── database/               (Backups manuais)
├── redis/                  (Snapshots)
└── files/                  (Diversos)
```

---

## 🔄 RESTORE (RECUPERAÇÃO)

### **1. Restaurar Database:**

```bash
# Listar backups disponíveis
aws s3 ls s3://marabet-backups/daily/ --recursive | grep database

# Download backup
aws s3 cp s3://marabet-backups/daily/database_20251027_020000.sql.gz ./

# Descompactar
gunzip database_20251027_020000.sql.gz

# Restaurar no RDS
PGPASSWORD=$DB_PASSWORD pg_restore \
    -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
    -p 5432 \
    -U marabet_admin \
    -d marabet_production \
    -c \
    database_20251027_020000.sql

# Ou se for SQL puro
PGPASSWORD=$DB_PASSWORD psql \
    -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
    -p 5432 \
    -U marabet_admin \
    -d marabet_production \
    < database_20251027_020000.sql
```

### **2. Restaurar Static/Media:**

```bash
# Download
aws s3 cp s3://marabet-backups/daily/static_media_20251027_020000.tar.gz ./

# Extrair
tar -xzf static_media_20251027_020000.tar.gz -C /opt/marabet/

# Ajustar permissões
sudo chown -R marabet:marabet /opt/marabet/static
sudo chown -R marabet:marabet /opt/marabet/media
```

### **3. Restaurar .env:**

```bash
# Download
aws s3 cp s3://marabet-backups/daily/env_20251027_020000.enc ./

# Descriptografar (usar senha do DB)
openssl enc -aes-256-cbc -d \
    -in env_20251027_020000.enc \
    -out .env \
    -pass pass:GuF#Y(!j38Bgw|YyT<r0J5>yxD3n

# Copiar para aplicação
sudo cp .env /opt/marabet/.env
sudo chown marabet:marabet /opt/marabet/.env
sudo chmod 600 /opt/marabet/.env
```

---

## 📊 MONITORAMENTO

### **Ver Logs de Backup:**

```bash
# Logs do cron
sudo tail -f /var/log/marabet/backup.log

# Última execução
sudo tail -20 /var/log/marabet/backup.log
```

### **Listar Backups S3:**

```bash
# Todos os backups
aws s3 ls s3://marabet-backups/ --recursive --human-readable

# Apenas daily
aws s3 ls s3://marabet-backups/daily/ --human-readable

# Com resumo (tamanho total)
aws s3 ls s3://marabet-backups/ --recursive --summarize --human-readable
```

### **Tamanho e Custos:**

```bash
# Ver tamanho total do bucket
aws s3 ls s3://marabet-backups --recursive --summarize --human-readable | grep "Total Size"

# Exemplo de cálculo de custo:
# 100 GB em S3 Standard = $2.30/mês
# 100 GB em Glacier = $0.40/mês
```

---

## ⚠️ DISASTER RECOVERY

### **Cenário: Perda Total do RDS**

```bash
# 1. Criar nova RDS (ou usar existente)
# 2. Baixar último backup
aws s3 cp s3://marabet-backups/daily/database_latest.sql.gz ./

# 3. Restaurar
gunzip database_latest.sql.gz
PGPASSWORD=$DB_PASSWORD psql -h [NOVO_RDS] -U marabet_admin -d postgres < database_latest.sql

# 4. Atualizar .env com novo endpoint
# 5. Restart aplicação
```

### **Cenário: Perda Total da EC2**

```bash
# 1. Lançar nova EC2
./lancar_ec2_completo.sh

# 2. Configurar ambiente (Nginx, SSL, etc.)

# 3. Restaurar .env
aws s3 cp s3://marabet-backups/daily/env_latest.enc ./
openssl enc -d -aes-256-cbc -in env_latest.enc -out .env

# 4. Restaurar static/media
aws s3 cp s3://marabet-backups/daily/static_media_latest.tar.gz ./
tar -xzf static_media_latest.tar.gz

# 5. Deploy aplicação
docker-compose up -d
```

---

## 💰 CUSTOS S3

### **Estimativa para MaraBet:**

| Item | Tamanho | Custo/mês |
|------|---------|-----------|
| **Database backups** | 50GB | $1.15 |
| **Static/Media** | 20GB | $0.46 |
| **Daily (30 dias)** | 70GB | $1.61 |
| **Weekly (90 dias)** | 10GB | $0.23 |
| **Monthly (Glacier)** | 20GB | $0.08 |
| **TOTAL** | ~100GB | **~$2-3/mês** |

---

## ✅ CHECKLIST

- [ ] Bucket S3 criado
- [ ] Versionamento habilitado
- [ ] Encriptação ativa
- [ ] Lifecycle policy configurada
- [ ] Script de backup na EC2
- [ ] Cron configurado (2h da manhã)
- [ ] Backup testado manualmente
- [ ] Backup aparece no S3
- [ ] Restore testado
- [ ] Logs de backup OK

---

## 📞 COMANDOS ÚTEIS

```bash
# Listar backups
aws s3 ls s3://marabet-backups/daily/ --human-readable

# Download backup
aws s3 cp s3://marabet-backups/daily/database_xxx.sql.gz ./

# Upload manual
aws s3 cp backup.sql.gz s3://marabet-backups/manual/

# Sincronizar pasta
aws s3 sync /opt/marabet/backups/ s3://marabet-backups/sync/

# Ver tamanho
aws s3 ls s3://marabet-backups --recursive --summarize --human-readable
```

---

**💾 Backup S3 Configurado!**  
**✅ Automático Diário**  
**🔒 Encriptado + Versionado**  
**☁️ MaraBet.com Protegido**

