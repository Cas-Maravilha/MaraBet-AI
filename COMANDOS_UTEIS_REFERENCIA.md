# ⚡ COMANDOS ÚTEIS - REFERÊNCIA RÁPIDA

**Sistema**: MaraBet AI  
**Ambiente**: Produção AWS  
**Acesso rápido**: marabet.com

---

## 🔐 ACESSO

```bash
# SSH na EC2
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Ou use script
./ssh-connect.sh

# Trocar para usuário marabet
sudo su - marabet
cd /opt/marabet
```

---

## 🐳 DOCKER - OPERAÇÕES

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONTAINERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Status
docker-compose ps

# Logs (seguir)
docker-compose logs -f

# Logs (últimas 100 linhas)
docker-compose logs --tail=100

# Logs de serviço específico
docker-compose logs -f web

# Restart todos
docker-compose restart

# Restart específico
docker-compose restart web

# Stop
docker-compose stop

# Start
docker-compose start

# Down (parar e remover)
docker-compose down

# Up (iniciar)
docker-compose up -d

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BUILD E DEPLOY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Rebuild
docker-compose build

# Rebuild e restart
docker-compose up -d --build

# Rebuild sem cache
docker-compose build --no-cache

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MONITORAMENTO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# CPU/RAM por container
docker stats

# CPU/RAM (apenas MaraBet)
docker stats marabet-web marabet-celery

# Processos dentro do container
docker-compose top

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LIMPEZA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Limpar tudo (containers parados, imagens, volumes)
docker system prune -a

# Limpar volumes não usados
docker volume prune

# Limpar networks não usadas
docker network prune
```

---

## 🗄️ DATABASE - RDS

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONEXÃO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Conectar ao RDS
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d marabet_production

# Password: GuF#Y(!j38Bgw|YyT<r0J5>yxD3n

# Testar conectividade
nc -zv database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com 5432

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# QUERIES ÚTEIS (no psql)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Listar databases
\l

# Listar tabelas
\dt

# Descrever tabela
\d users

# Ver tamanho do database
SELECT pg_size_pretty(pg_database_size('marabet_production'));

# Ver conexões ativas
SELECT count(*) FROM pg_stat_activity;

# Vacuum
VACUUM ANALYZE;

# Sair
\q

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MIGRAÇÕES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Django
docker-compose exec web python manage.py migrate

# Alembic
docker-compose exec web alembic upgrade head

# Custom
docker-compose exec web python migrate.py
```

---

## 💾 REDIS - CACHE

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONEXÃO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Conectar ao Redis
redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com \
          -p 6379 \
          --tls \
          --insecure

# Testar conectividade
nc -zv marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com 6379

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMANDOS REDIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Ping
PING

# Ver todas as chaves
KEYS *

# Obter valor
GET [key]

# Setar valor
SET [key] [value]

# Deletar chave
DEL [key]

# Limpar tudo (CUIDADO!)
FLUSHDB

# Info do servidor
INFO server

# Info de memória
INFO memory

# Sair
exit
```

---

## 🌐 NGINX

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONTROLE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Status
sudo systemctl status nginx

# Testar config
sudo nginx -t

# Reload (sem downtime)
sudo systemctl reload nginx

# Restart (com downtime)
sudo systemctl restart nginx

# Stop
sudo systemctl stop nginx

# Start
sudo systemctl start nginx

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Access log
sudo tail -f /var/log/nginx/marabet-access.log

# Error log
sudo tail -f /var/log/nginx/marabet-error.log

# Últimos 100 erros
sudo tail -100 /var/log/nginx/marabet-error.log
```

---

## 🔒 SSL/HTTPS

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CERTBOT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Listar certificados
sudo certbot certificates

# Renovar (manual)
sudo certbot renew

# Renovar forçado
sudo certbot renew --force-renewal

# Testar renovação (dry-run)
sudo certbot renew --dry-run

# Ver logs
sudo cat /var/log/letsencrypt/letsencrypt.log

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VERIFICAÇÃO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Ver quando expira
sudo openssl x509 -in /etc/letsencrypt/live/marabet.com/fullchain.pem -noout -dates

# Testar HTTPS
curl -I https://marabet.com

# SSL Labs
# https://www.ssllabs.com/ssltest/analyze.html?d=marabet.com
```

---

## 🔄 DEPLOY E ATUALIZAÇÃO

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ATUALIZAR CÓDIGO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Via Git
cd /opt/marabet
git pull origin main

# Via rsync (do PC)
rsync -avz -e "ssh -i marabet-key.pem" ./ ubuntu@[IP]:/opt/marabet/

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REDEPLOY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Rebuild e restart
docker-compose build
docker-compose up -d

# Ou em um comando
docker-compose up -d --build

# Ver logs durante deploy
docker-compose logs -f

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MIGRAÇÕES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Django
docker-compose exec web python manage.py migrate

# Alembic
docker-compose exec web alembic upgrade head

# Custom
docker-compose exec web python migrate.py --migrate

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DJANGO COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Criar superuser
docker-compose exec web python manage.py createsuperuser

# Collectstatic
docker-compose exec web python manage.py collectstatic --noinput

# Shell
docker-compose exec web python manage.py shell

# Flush cache
docker-compose exec web python manage.py flush_cache
```

---

## 📊 MONITORAMENTO

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RECURSOS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# CPU/RAM/Processos interativo
htop

# CPU/RAM por container
docker stats

# Disco
df -h

# Memória
free -h

# Processos Docker
docker ps

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# App logs
tail -f /opt/marabet/logs/app.log
tail -f -n 100 /opt/marabet/logs/app.log

# Nginx access
sudo tail -f /var/log/nginx/marabet-access.log

# Nginx error
sudo tail -f /var/log/nginx/marabet-error.log

# Backup log
tail -f /var/log/marabet/backup.log

# Docker logs
docker-compose logs -f web
```

---

## 🔌 CONECTIVIDADE

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTAR RDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Testar porta
nc -zv database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com 5432

# Conectar
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d marabet_production

# Do container
docker-compose exec web nc -zv database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com 5432

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTAR REDIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Testar porta
nc -zv marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com 6379

# Ping
redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com \
          -p 6379 \
          --tls \
          --insecure \
          ping

# Conectar
redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com \
          -p 6379 \
          --tls \
          --insecure
```

---

## 💾 BACKUP

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUTAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Backup manual
/opt/marabet/backups/scripts/backup_to_s3.sh

# Ver log
tail -50 /var/log/marabet/backup.log

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LISTAR BACKUPS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Backups diários
aws s3 ls s3://marabet-backups/daily/ --human-readable

# Backups semanais
aws s3 ls s3://marabet-backups/weekly/ --human-readable

# Todos os backups
aws s3 ls s3://marabet-backups/ --recursive --human-readable

# Tamanho total
aws s3 ls s3://marabet-backups/ --recursive --summarize --human-readable

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESTORE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Restaurar
/opt/marabet/backups/scripts/restore_from_s3.sh [TIMESTAMP]

# Exemplo
/opt/marabet/backups/scripts/restore_from_s3.sh 2025-10-27_02-00-00
```

---

## 🔍 DEBUG

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHELL NO CONTAINER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Bash
docker-compose exec web bash

# Python shell
docker-compose exec web python

# Django shell
docker-compose exec web python manage.py shell

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VARIÁVEIS DE AMBIENTE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Ver .env (sem senhas)
cat .env | grep -v "PASSWORD\|SECRET\|KEY"

# Testar variável
docker-compose exec web env | grep DATABASE_URL

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NETWORK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Portas abertas
sudo lsof -i -P -n | grep LISTEN

# Conexões estabelecidas
sudo netstat -tunlp | grep ESTABLISHED

# Ver porta específica
sudo lsof -i :8000
```

---

## 🧪 TESTES

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEALTH CHECKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Local
curl http://localhost:8000/health

# Domínio
curl https://marabet.com/health

# API
curl https://api.marabet.com/status

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PERFORMANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Response time
time curl https://marabet.com

# Com detalhes
curl -w "\nTime: %{time_total}s\nSize: %{size_download} bytes\n" \
     -o /dev/null \
     -s https://marabet.com
```

---

## 🔧 SISTEMA

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ATUALIZAÇÃO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Atualizar packages
sudo apt-get update
sudo apt-get upgrade -y

# Limpar cache APT
sudo apt-get clean
sudo apt-get autoclean

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LIMPEZA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Limpar logs antigos
sudo journalctl --vacuum-time=30d
sudo find /var/log -name "*.log" -mtime +30 -delete

# Limpar Docker
docker system prune -a -f

# Limpar backups locais
find /opt/marabet/backups -name "*.gz" -mtime +7 -delete
```

---

## ☁️ AWS CLI

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EC2
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Ver info da EC2
aws ec2 describe-instances --instance-ids [ID] --region eu-west-1

# Ver IP público
aws ec2 describe-instances \
  --instance-ids [ID] \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Ver info do RDS
aws rds describe-db-instances \
  --db-instance-identifier database-1 \
  --region eu-west-1

# Ver snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier database-1 \
  --region eu-west-1

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# S3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Listar buckets
aws s3 ls

# Listar arquivos
aws s3 ls s3://marabet-backups/daily/

# Upload
aws s3 cp file.txt s3://marabet-backups/manual/

# Download
aws s3 cp s3://marabet-backups/daily/backup.gz ./

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLOUDWATCH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Listar alarmes
aws cloudwatch describe-alarms --region eu-west-1

# Ver métricas
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=[ID] \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region eu-west-1
```

---

## ⚡ ATALHOS ÚTEIS

### **Criar aliases no ~/.bashrc:**

```bash
# Adicionar ao ~/.bashrc do usuário marabet
alias mb-logs='docker-compose -f /opt/marabet/docker-compose.yml logs -f'
alias mb-ps='docker-compose -f /opt/marabet/docker-compose.yml ps'
alias mb-restart='docker-compose -f /opt/marabet/docker-compose.yml restart'
alias mb-health='curl http://localhost:8000/health'
alias mb-stats='docker stats'
alias mb-backup='/opt/marabet/backups/scripts/backup_to_s3.sh'

# Aplicar
source ~/.bashrc

# Usar
mb-logs
mb-ps
mb-health
```

---

## 📞 COMANDOS DE EMERGÊNCIA

```bash
# Restart completo (último recurso)
sudo reboot

# Parar tudo
docker-compose down
sudo systemctl stop nginx

# Ver o que está consumindo recursos
sudo htop

# Matar processo específico
sudo kill -9 [PID]

# Verificar integridade do filesystem
sudo fsck -f /dev/xvda1
```

---

**⚡ Referência Rápida Criada!**  
**✅ Todos os Comandos Essenciais**  
**🔧 Operações Enterprise**  
**🌐 marabet.com**

