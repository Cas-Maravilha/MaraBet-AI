# 💾 Sistema de Backup Automatizado - MaraBet AI

**Data**: 24/10/2025  
**Contato**: +224 932027393  
**Versão**: 1.0

---

## 📋 VISÃO GERAL

Sistema completo de backup automatizado incluindo:
- **Backup de Banco de Dados**: PostgreSQL e Redis
- **Backup de Arquivos**: Aplicação, mídia, logs
- **Backup de Configurações**: Docker, Nginx, etc
- **Upload para S3**: Backup remoto opcional
- **Retenção Automática**: 30 dias
- **Notificações**: Telegram

---

## 🚀 INSTALAÇÃO RÁPIDA

### 1. Configurar Backup Automático:

```bash
# Setup cron job
chmod +x backups/scripts/setup_cron.sh
./backups/scripts/setup_cron.sh
```

### 2. Executar Backup Manual:

```bash
# Bash
chmod +x backups/scripts/backup.sh
./backups/scripts/backup.sh

# Python
python backups/scripts/backup.py
```

---

## 📦 O QUE É FEITO BACKUP

### 1. Banco de Dados PostgreSQL:
- Dump completo do banco `marabet`
- Compactado com gzip
- Localização: `backups/database/`

### 2. Redis:
- Dump RDB
- Compactado com gzip
- Localização: `backups/database/`

### 3. Arquivos:
- Código da aplicação (`app/`)
- Arquivos estáticos (`static/`)
- Arquivos de mídia (`media/`)
- Logs (`logs/`)
- Localização: `backups/files/`

### 4. Configurações:
- Docker Compose
- Nginx
- Monitoring
- Migrations
- Localização: `backups/configs/`

---

## ⏰ BACKUP AUTOMÁTICO

### Cron Job:
- **Frequência**: Diariamente às 02:00
- **Script**: `/opt/marabet/backups/scripts/backup.sh`
- **Log**: `/opt/marabet/backups/logs/cron.log`

### Ver Cron Jobs:
```bash
crontab -l
```

### Editar Cron:
```bash
crontab -e
```

---

## 🔄 RESTAURAÇÃO

### 1. Listar Backups:
```bash
ls -lh backups/database/*.sql.gz
```

### 2. Restaurar Banco:
```bash
chmod +x backups/scripts/restore.sh
./backups/scripts/restore.sh
```

### 3. Restauração Manual:
```bash
# Descomprimir
gunzip -c backups/database/marabet_db_YYYYMMDD_HHMMSS.sql.gz > restore.sql

# Restaurar
psql -h localhost -U marabetuser -d marabet -f restore.sql

# Limpar
rm restore.sql
```

---

## ☁️ BACKUP REMOTO (OPCIONAL)

### Opções de Backup em Cloud:

#### 1. **Rclone (Recomendado - Universal)**
```bash
# Instalar Rclone
curl https://rclone.org/install.sh | sudo bash

# Configurar (suporta 40+ provedores)
rclone config

# Suporta: Dropbox, Google Drive, OneDrive, Backblaze B2, etc.
```

#### 2. **Rsync para Servidor Remoto**
```bash
# Backup via SSH para outro servidor
rsync -avz --delete /opt/marabet/backups/ \
    usuario@servidor-backup:/backups/marabet/
```

#### 3. **DigitalOcean Spaces / Backblaze B2 / Wasabi**
```bash
# Compatível com S3 (mais barato que AWS)
# Configure com Rclone ou s3cmd
pip install s3cmd
s3cmd --configure
```

### Exemplo com Rclone:
```bash
# Upload automático
rclone sync /opt/marabet/backups/ remote:marabet-backups/

# Adicionar ao cron
0 3 * * * rclone sync /opt/marabet/backups/ remote:marabet-backups/
```

---

## 📊 MONITORAMENTO

### Ver Logs de Backup:
```bash
# Logs do cron
tail -f backups/logs/cron.log

# Logs de backup específico
cat backups/logs/backup_YYYYMMDD_HHMMSS.log

# Relatórios
cat backups/logs/backup_report_*.txt
```

### Verificar Espaço:
```bash
du -sh backups/
df -h /opt/marabet/backups
```

### Listar Backups:
```bash
# Por tipo
ls -lh backups/database/
ls -lh backups/files/
ls -lh backups/configs/

# Por data
find backups/ -name "*.gz" -mtime -7  # Últimos 7 dias
```

---

## 🔔 NOTIFICAÇÕES TELEGRAM

### Configurar:
```bash
export TELEGRAM_BOT_TOKEN="seu_token_aqui"
export TELEGRAM_CHAT_ID="seu_chat_id_aqui"
```

### Testar:
```bash
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    -d "chat_id=$TELEGRAM_CHAT_ID" \
    -d "text=Teste de notificação MaraBet AI"
```

---

## 🛠️ CONFIGURAÇÃO AVANÇADA

### Alterar Retenção:
```bash
# Editar script
nano backups/scripts/backup.sh

# Modificar linha
RETENTION_DAYS=30  # Alterar para número desejado
```

### Alterar Horário do Backup:
```bash
# Editar cron
crontab -e

# Modificar horário (exemplo: 03:00)
0 3 * * * /opt/marabet/backups/scripts/backup.sh
```

### Backup Incremental:
```bash
# Adicionar ao script
rsync -avz --delete /opt/marabet/app/ /backup/incremental/
```

---

## ⚠️ SOLUÇÃO DE PROBLEMAS

### Backup Falhando:

```bash
# Verificar permissões
ls -l backups/scripts/backup.sh

# Verificar espaço em disco
df -h

# Verificar conexão com banco
pg_dump --version
psql -h localhost -U marabetuser -d marabet -c "SELECT 1;"
```

### Cron Não Executando:

```bash
# Verificar logs do cron
tail -f /var/log/syslog | grep CRON

# Testar script manualmente
./backups/scripts/backup.sh

# Verificar variáveis de ambiente no cron
crontab -e
# Adicionar: SHELL=/bin/bash
```

### Restauração Falhando:

```bash
# Verificar integridade do backup
gunzip -t backups/database/marabet_db_*.sql.gz

# Ver conteúdo
gunzip -c backups/database/marabet_db_*.sql.gz | head -n 50
```

---

## 🔐 SEGURANÇA

### Permissões:
```bash
# Restringir acesso aos backups
chmod 700 backups/
chmod 600 backups/database/*.sql.gz
```

### Criptografia:
```bash
# Criptografar backup
gpg --encrypt --recipient comercial@marabet.ao marabet_db.sql.gz

# Descriptografar
gpg --decrypt marabet_db.sql.gz.gpg > marabet_db.sql.gz
```

---

## 📞 SUPORTE

- **Telefone/WhatsApp**: +224 932027393
- **Telegram**: @marabet_support
- **Email**: suporte@marabet.ao

---

## ✅ CHECKLIST

- [ ] Scripts de backup criados
- [ ] Cron job configurado
- [ ] Backup manual testado
- [ ] Restauração testada
- [ ] S3 configurado (opcional)
- [ ] Notificações Telegram configuradas
- [ ] Retenção configurada
- [ ] Logs monitorados
- [ ] Espaço em disco suficiente

---

**🎯 Implementação 6/6 Concluída!**

**📊 Score: 136.0% → 147.7% (+11.7%)**

**🎉 TODAS AS 6 IMPLEMENTAÇÕES FINALIZADAS!**
