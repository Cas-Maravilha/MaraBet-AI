# 🚀 DEPLOY APLICAÇÃO MARABET - GUIA COMPLETO

**Servidor**: EC2 AWS  
**Domínio**: marabet.com  
**Diretório**: /opt/marabet

---

## 📋 MÉTODOS DE DEPLOY

1. [Via Git (Recomendado)](#método-1-via-git-recomendado)
2. [Via SCP/Rsync (do PC)](#método-2-via-scprsync)
3. [Via S3](#método-3-via-s3)
4. [Configuração Final](#configuração-final)

---

## MÉTODO 1: VIA GIT (Recomendado)

### **A. Criar Repositório Git:**

#### **GitHub:**

```bash
# No seu PC (Windows)
cd "D:\Usuario\Maravilha\Desktop\MaraBet AI"

# Inicializar Git (se não tiver)
git init

# Criar .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env
.env.*

# Logs
*.log
logs/
mara_bet.log

# Database
*.db
*.sqlite3

# Backups
backups/
*.sql
*.dump

# Cache
.cache/
cache/

# IDE
.vscode/
.idea/

# AWS
*.pem
marabet-key.pem

# Temporary
*.tmp
temp/
EOF

# Adicionar arquivos
git add .

# Commit
git commit -m "MaraBet AI - Production ready"

# Criar repo no GitHub (via web ou CLI)
# https://github.com/new

# Adicionar remote
git remote add origin https://github.com/seu-usuario/marabet-ai.git

# Push
git push -u origin main
```

### **B. Clonar na EC2:**

```bash
# SSH na EC2
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Trocar para usuário marabet
sudo su - marabet

# Ir para diretório
cd /opt/marabet

# Clonar repositório
git clone https://github.com/seu-usuario/marabet-ai.git .

# Ou se o repo for privado
git clone https://seu-token@github.com/seu-usuario/marabet-ai.git .

# Verificar arquivos
ls -la
```

---

## MÉTODO 2: VIA SCP/RSYNC

### **A. Upload via SCP (Simples):**

```bash
# Do seu PC (Git Bash ou PowerShell)
scp -i marabet-key.pem -r \
    "D:\Usuario\Maravilha\Desktop\MaraBet AI\*" \
    ubuntu@[ELASTIC_IP]:/tmp/marabet-upload/

# SSH e mover
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]
sudo mv /tmp/marabet-upload/* /opt/marabet/
sudo chown -R marabet:marabet /opt/marabet/
```

### **B. Upload via Rsync (Recomendado - Incremental):**

```bash
# Do seu PC
rsync -avz --progress \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude 'venv' \
    --exclude '*.pyc' \
    --exclude '.env' \
    --exclude '*.log' \
    --exclude 'backups/' \
    -e "ssh -i marabet-key.pem" \
    "D:/Usuario/Maravilha/Desktop/MaraBet AI/" \
    ubuntu@[ELASTIC_IP]:/tmp/marabet-upload/

# SSH e mover
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]
sudo rsync -a /tmp/marabet-upload/ /opt/marabet/
sudo chown -R marabet:marabet /opt/marabet/
sudo rm -rf /tmp/marabet-upload/
```

### **C. Script de Deploy Automatizado:**

```bash
# No PC, criar: deploy-to-ec2.sh

#!/bin/bash

EC2_IP="[ELASTIC_IP]"
KEY_FILE="marabet-key.pem"

echo "📦 Deploy MaraBet para AWS EC2"
echo "=============================="
echo ""

# Rsync
rsync -avz --progress \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude 'venv' \
    --exclude '*.pyc' \
    --exclude '.env*' \
    --exclude '*.log' \
    -e "ssh -i $KEY_FILE" \
    ./ ubuntu@$EC2_IP:/tmp/marabet-deploy/

# SSH e finalizar
ssh -i $KEY_FILE ubuntu@$EC2_IP << 'REMOTE'
sudo rsync -a /tmp/marabet-deploy/ /opt/marabet/
sudo chown -R marabet:marabet /opt/marabet/
sudo rm -rf /tmp/marabet-deploy/

echo ""
echo "✅ Código enviado!"
echo "Próximo: Configurar .env e iniciar aplicação"
REMOTE

echo ""
echo "✅ Deploy completo!"
```

---

## MÉTODO 3: VIA S3

### **A. Upload para S3:**

```bash
# Do PC
aws s3 mb s3://marabet-deploy --region eu-west-1

aws s3 sync "D:\Usuario\Maravilha\Desktop\MaraBet AI" \
    s3://marabet-deploy/code/ \
    --exclude ".git/*" \
    --exclude "__pycache__/*" \
    --exclude "*.pyc" \
    --exclude "venv/*"
```

### **B. Download na EC2:**

```bash
# SSH na EC2
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Como marabet
sudo su - marabet
cd /opt/marabet

# Download
aws s3 sync s3://marabet-deploy/code/ .

# Verificar
ls -la
```

---

## CONFIGURAÇÃO FINAL

### **1. Criar/Configurar .env:**

```bash
# Na EC2, como usuário marabet
cd /opt/marabet

# Criar .env
nano .env
```

**Conteúdo do .env:**

```bash
# ================================
# MARABET AI - PRODUCTION
# ================================

# Environment
NODE_ENV=production
FLASK_ENV=production
DEBUG=false

# App
APP_NAME=MaraBet AI
APP_URL=https://marabet.com
API_URL=https://api.marabet.com
APP_PORT=8000
FORCE_HTTPS=true

# Database (RDS PostgreSQL)
DATABASE_URL=postgresql://marabet_admin:GuF#Y(!j38Bgw|YyT<r0J5>yxD3n@database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com:5432/marabet_production?sslmode=require
DB_HOST=database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=marabet_production
DB_USER=marabet_admin
DB_PASSWORD=GuF#Y(!j38Bgw|YyT<r0J5>yxD3n
DB_SSL_MODE=require

# Cache (Redis Serverless)
REDIS_URL=rediss://marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com:6379
REDIS_HOST=marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_SSL=true
REDIS_DB=0

# API Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io

# Telegram
TELEGRAM_BOT_TOKEN=<SEU_TOKEN_TELEGRAM>
TELEGRAM_CHAT_ID=5550091597

# Security
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
SECURE_SSL_REDIRECT=true

# Domain & Hosts
DOMAIN=marabet.com
ALLOWED_HOSTS=marabet.com,www.marabet.com,api.marabet.com,localhost

# AWS
AWS_REGION=eu-west-1
AWS_ACCOUNT_ID=206749730888

# Timezone
TZ=Africa/Luanda

# Logs
LOG_LEVEL=INFO
LOG_FILE=/var/log/marabet/app.log
```

**Salvar**: Ctrl+O, Enter, Ctrl+X

```bash
# Proteger .env
chmod 600 .env

# Verificar (sem mostrar senhas)
cat .env | grep -v "PASSWORD\|SECRET\|KEY"
```

---

### **2. Criar Database:**

```bash
# Conectar ao RDS
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d postgres

# Password: GuF#Y(!j38Bgw|YyT<r0J5>yxD3n

# Criar database
CREATE DATABASE marabet_production;

# Verificar
\l

# Conectar ao novo database
\c marabet_production

# Sair
\q
```

---

### **3. Instalar Dependências Python:**

```bash
# Se usar venv (opcional)
python3 -m venv venv
source venv/bin/activate

# Instalar requirements
pip install -r requirements.txt

# Ou se tiver setup.py
pip install -e .
```

---

### **4. Executar Migrações:**

```bash
# Django
python manage.py migrate

# Flask com Alembic
alembic upgrade head

# Ou script custom
python migrate.py

# Criar superuser (Django)
python manage.py createsuperuser
```

---

### **5. Coletar Static Files:**

```bash
# Django
python manage.py collectstatic --noinput

# Verificar
ls -la static/
```

---

### **6. Iniciar com Docker:**

```bash
# Build e start
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Verificar containers
docker-compose ps

# Resultado esperado:
# NAME                COMMAND             STATUS
# marabet-app         "gunicorn..."       Up (healthy)
# marabet-nginx       "nginx -g..."       Up
```

---

### **7. Executar Migrações no Container:**

```bash
# Se usar Docker
docker-compose exec app python manage.py migrate

# Criar superuser
docker-compose exec app python manage.py createsuperuser

# Collectstatic
docker-compose exec app python manage.py collectstatic --noinput
```

---

## ✅ VERIFICAÇÃO FINAL

### **A. Testar Localmente na EC2:**

```bash
# HTTP (deve redirecionar)
curl -I http://localhost

# HTTPS
curl -I https://localhost -k

# Health check
curl https://localhost/health -k

# API
curl https://localhost/api/status -k
```

### **B. Testar do Seu PC:**

```bash
# HTTP (redirect)
curl -I http://marabet.com

# HTTPS
curl -I https://marabet.com

# Health check
curl https://marabet.com/health

# API
curl https://api.marabet.com/status
```

### **C. Navegador:**

```
1. Abrir: https://marabet.com
2. Verificar cadeado verde 🔒
3. Testar login/cadastro
4. Verificar previsões
5. Testar Telegram bot
6. Verificar logs
```

---

## 📊 MONITORAMENTO

### **Ver Logs:**

```bash
# Logs da aplicação
docker-compose logs -f app

# Logs do Nginx
sudo tail -f /var/log/nginx/marabet-access.log
sudo tail -f /var/log/nginx/marabet-error.log

# Logs do sistema
sudo journalctl -u docker -f
```

### **Status dos Serviços:**

```bash
# Nginx
sudo systemctl status nginx

# Docker
sudo systemctl status docker

# Containers
docker-compose ps

# Resources
docker stats
```

---

## 🔄 UPDATES E REDEPLOY

### **A. Atualizar Código:**

```bash
# Via Git
cd /opt/marabet
git pull origin main

# Via rsync (do PC)
rsync -avz -e "ssh -i marabet-key.pem" ./ ubuntu@[IP]:/tmp/update/
ssh -i marabet-key.pem ubuntu@[IP]
sudo rsync -a /tmp/update/ /opt/marabet/
sudo chown -R marabet:marabet /opt/marabet/
```

### **B. Redeploy:**

```bash
# Rebuild e restart
docker-compose up -d --build

# Ou restart apenas
docker-compose restart

# Zero downtime (se tiver múltiplos containers)
docker-compose up -d --no-deps --build app
```

---

## 🔧 TROUBLESHOOTING

### **Erro: "Permission denied"**

```bash
# Ajustar permissões
sudo chown -R marabet:marabet /opt/marabet
sudo chmod -R 755 /opt/marabet
chmod 600 /opt/marabet/.env
```

### **Erro: "Port 8000 already in use"**

```bash
# Ver o que está usando
sudo lsof -i :8000

# Parar processo
sudo kill <PID>

# Ou parar Docker
docker-compose down
```

### **Erro: Database connection**

```bash
# Testar conexão
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d marabet_production

# Verificar .env
cat .env | grep DATABASE_URL

# Verificar Security Group RDS permite conexão da EC2
```

### **Erro: Redis connection**

```bash
# Testar Redis
redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com \
          -p 6379 \
          --tls \
          --insecure

# Verificar .env
cat .env | grep REDIS_URL

# Verificar Security Group Redis
```

---

## ✅ CHECKLIST DEPLOY

- [ ] Código enviado para /opt/marabet
- [ ] .env configurado com todas as variáveis
- [ ] .env com permissões 600
- [ ] Database marabet_production criada
- [ ] Conexão RDS testada
- [ ] Conexão Redis testada
- [ ] requirements.txt instalado
- [ ] Migrações executadas
- [ ] Static files coletados
- [ ] Docker containers rodando
- [ ] Nginx funcionando
- [ ] HTTPS ativo
- [ ] Health check respondendo
- [ ] Logs sem erros
- [ ] Aplicação acessível

---

## 📞 COMANDOS RÁPIDOS

```bash
# Deploy
cd /opt/marabet
git pull
docker-compose up -d --build

# Logs
docker-compose logs -f

# Restart
docker-compose restart app

# Stop
docker-compose down

# Status
docker-compose ps

# Shell no container
docker-compose exec app bash
```

---

**🚀 Aplicação Deployada!**  
**✅ marabet.com Funcionando**  
**🔒 HTTPS Ativo**  
**☁️ AWS Production Ready**

