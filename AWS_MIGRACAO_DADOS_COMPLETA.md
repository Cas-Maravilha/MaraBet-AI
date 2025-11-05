# 📦 GUIA COMPLETO DE MIGRAÇÃO DE DADOS PARA AWS

**Sistema**: MaraBet AI v1.0.0  
**Destino**: Amazon Web Services (AWS)  
**Data**: Outubro 2025

---

## 📋 ÍNDICE

1. [Dados Necessários](#-dados-necessários)
2. [Arquitetura AWS](#-arquitetura-aws)
3. [Preparação](#-preparação)
4. [Migração do Código](#-migração-do-código)
5. [Migração do Banco de Dados](#-migração-do-banco-de-dados)
6. [Configuração de Credenciais](#-configuração-de-credenciais)
7. [Deploy Completo](#-deploy-completo)
8. [Validação](#-validação)
9. [Checklist Final](#-checklist-final)

---

## 📊 DADOS NECESSÁRIOS

### **1. Código MaraBet AI**
```bash
# Localização atual
D:\Usuario\Maravilha\Desktop\MaraBet AI\

# Arquivos essenciais:
- app.py                      # Aplicação principal
- requirements.txt            # Dependências Python
- docker-compose.yml          # Configuração Docker
- Dockerfile                  # Imagem Docker
- .env.example               # Template de variáveis
- /api/                      # APIs
- /models/                   # Modelos ML
- /templates/                # Templates HTML
- /static/                   # CSS, JS, imagens
```

### **2. Chave API-Football**
```
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045
API_FOOTBALL_PLAN=Ultra
IP_WHITELIST=102.206.57.108 (seu IP atual)

# Nota: Será necessário adicionar IPs das instâncias EC2 AWS
```

### **3. Token Telegram Bot**
```
TELEGRAM_BOT_TOKEN=<seu_token_atual>
TELEGRAM_CHAT_ID=5550091597
```

### **4. Backup Banco de Dados (se existente)**
```bash
# Se já tem dados em produção local:
# PostgreSQL backup
marabet_backup_YYYYMMDD.sql.gz

# Redis backup (opcional)
dump.rdb
```

---

## 🏗️ ARQUITETURA AWS

```
Internet (Usuários)
    │
    ├─── Route 53 (DNS)
    │         │
    │         └─── marabet.ao → CloudFront (CDN)
    │                              │
    │                              └─── ALB (Load Balancer)
    │                                        │
    ├─────────────────────────────────────────┤
    │                 VPC                      │
    │  ┌────────────────────────────────────┐ │
    │  │  Public Subnet (Zona A)            │ │
    │  │  ┌──────────────────────────────┐  │ │
    │  │  │  EC2 (Aplicação)              │  │ │
    │  │  │  - Docker                     │  │ │
    │  │  │  - Nginx                      │  │ │
    │  │  │  - MaraBet AI                 │  │ │
    │  │  └──────────────────────────────┘  │ │
    │  └────────────────────────────────────┘ │
    │                                          │
    │  ┌────────────────────────────────────┐ │
    │  │  Private Subnet (Zonas A + B)      │ │
    │  │  ┌──────────────┐ ┌─────────────┐ │ │
    │  │  │ RDS Primary  │ │ RDS Standby │ │ │
    │  │  │ PostgreSQL   │ │ (Multi-AZ)  │ │ │
    │  │  └──────────────┘ └─────────────┘ │ │
    │  │                                    │ │
    │  │  ┌──────────────────────────────┐ │ │
    │  │  │ ElastiCache Redis            │ │ │
    │  │  └──────────────────────────────┘ │ │
    │  └────────────────────────────────────┘ │
    └──────────────────────────────────────────┘

External Services:
- S3 (Backups, Arquivos estáticos)
- CloudWatch (Logs, Métricas)
- Certificate Manager (SSL)
```

### **Especificações:**
```yaml
VPC: 10.0.0.0/16
Public Subnet A: 10.0.1.0/24 (eu-west-1a)
Private Subnet A: 10.0.11.0/24 (eu-west-1a)
Private Subnet B: 10.0.12.0/24 (eu-west-1b)

EC2: t3.large (2 vCPUs, 8GB RAM) - Ubuntu 22.04
RDS: db.t3.large (2 vCPUs, 8GB RAM) - PostgreSQL 15 Multi-AZ
ElastiCache: cache.t3.medium - Redis 7.0
ALB: Application Load Balancer com SSL
S3: 3 buckets (backups, static, logs)
```

---

## 🛠️ PREPARAÇÃO

### **1. Instalar AWS CLI (se ainda não instalou):**

#### **Windows:**
```powershell
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Verificar
aws --version
```

#### **Linux/macOS:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verificar
aws --version
```

### **2. Configurar AWS CLI:**

```bash
aws configure

# Preencher:
AWS Access Key ID: <SEU_ACCESS_KEY>
AWS Secret Access Key: <SEU_SECRET_KEY>
Default region name: eu-west-1
Default output format: json

# Testar
aws sts get-caller-identity
```

### **3. Preparar Código Local:**

```bash
# No Windows PowerShell
cd "D:\Usuario\Maravilha\Desktop\MaraBet AI"

# Criar backup local
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Compress-Archive -Path * -DestinationPath "marabet_backup_$timestamp.zip"

# Verificar arquivos essenciais
ls app.py, requirements.txt, docker-compose.yml, Dockerfile
```

---

## 📤 MIGRAÇÃO DO CÓDIGO

### **Opção 1: Via S3 (Recomendado)**

```bash
# 1. Criar bucket temporário
aws s3 mb s3://marabet-deploy-temp --region eu-west-1

# 2. Fazer upload do código
aws s3 sync . s3://marabet-deploy-temp/code/ \
  --exclude ".git/*" \
  --exclude "__pycache__/*" \
  --exclude "*.pyc" \
  --exclude "node_modules/*" \
  --exclude "venv/*"

# 3. Verificar upload
aws s3 ls s3://marabet-deploy-temp/code/ --recursive
```

### **Opção 2: Via Git (Produção)**

```bash
# 1. Criar repositório privado no GitHub/GitLab
git init
git add .
git commit -m "Initial commit - MaraBet AI"
git remote add origin https://github.com/seu-usuario/marabet-ai.git
git push -u origin main

# 2. Na EC2, fazer clone
# ssh na instância EC2
git clone https://github.com/seu-usuario/marabet-ai.git /opt/marabet
```

---

## 🗄️ MIGRAÇÃO DO BANCO DE DADOS

### **Cenário 1: Banco de Dados Novo (Fresh Install)**

```bash
# Nada a fazer - RDS será criado vazio
# As migrações serão executadas automaticamente no primeiro deploy
```

### **Cenário 2: Migrar Dados Existentes**

#### **A. Fazer Backup Local:**

```bash
# No servidor atual (se tiver)
# Windows (com PostgreSQL instalado)
pg_dump -h localhost -U postgres -d marabet > marabet_backup.sql

# Comprimir
gzip marabet_backup.sql
# Resultado: marabet_backup.sql.gz
```

#### **B. Enviar para S3:**

```bash
# Upload do backup
aws s3 cp marabet_backup.sql.gz s3://marabet-backups/migrations/

# Verificar
aws s3 ls s3://marabet-backups/migrations/
```

#### **C. Restaurar no RDS:**

```bash
# 1. Obter endpoint do RDS
RDS_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier marabet-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

echo "RDS Endpoint: $RDS_ENDPOINT"

# 2. Baixar backup do S3 na EC2
ssh -i marabet-key.pem ubuntu@<EC2_IP>
aws s3 cp s3://marabet-backups/migrations/marabet_backup.sql.gz .
gunzip marabet_backup.sql.gz

# 3. Restaurar no RDS
psql -h $RDS_ENDPOINT -U marabetadmin -d marabet < marabet_backup.sql

# 4. Verificar
psql -h $RDS_ENDPOINT -U marabetadmin -d marabet -c "\dt"
```

---

## 🔑 CONFIGURAÇÃO DE CREDENCIAIS

### **1. Criar arquivo .env na EC2:**

```bash
# Conectar na EC2
ssh -i marabet-key.pem ubuntu@<EC2_IP>

# Ir para diretório da aplicação
cd /opt/marabet

# Criar .env
cat > .env << 'EOF'
# ================================
# MARABET AI - AWS PRODUCTION
# ================================

# Ambiente
NODE_ENV=production
FLASK_ENV=production
DEBUG=False

# Database (RDS PostgreSQL)
DATABASE_URL=postgresql://marabetadmin:MaraBet2025#Secure!@marabet-db.xxxxx.eu-west-1.rds.amazonaws.com:5432/marabet
DB_HOST=marabet-db.xxxxx.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=marabet
DB_USER=marabetadmin
DB_PASSWORD=MaraBet2025#Secure!

# Redis (ElastiCache)
REDIS_URL=redis://marabet-redis.xxxxx.cache.amazonaws.com:6379
REDIS_HOST=marabet-redis.xxxxx.cache.amazonaws.com
REDIS_PORT=6379

# API-Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io

# Telegram
TELEGRAM_BOT_TOKEN=<SEU_TOKEN_TELEGRAM>
TELEGRAM_CHAT_ID=5550091597

# AWS
AWS_REGION=eu-west-1
AWS_ACCESS_KEY_ID=<SEU_ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<SEU_SECRET_KEY>

# S3 Buckets
S3_BUCKET_BACKUPS=marabet-backups
S3_BUCKET_STATIC=marabet-static
S3_BUCKET_LOGS=marabet-logs

# Segurança
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_HOSTS=marabet.ao,www.marabet.ao

# App
APP_NAME=MaraBet AI
APP_URL=https://marabet.ao
APP_PORT=8000

# Email (opcional)
SMTP_HOST=email-smtp.eu-west-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=<SES_SMTP_USER>
SMTP_PASSWORD=<SES_SMTP_PASSWORD>
FROM_EMAIL=noreply@marabet.ao
SUPPORT_EMAIL=suporte@marabet.ao

# Timezone
TZ=Africa/Luanda

# Logs
LOG_LEVEL=INFO
LOG_FILE=/var/log/marabet/app.log

# Backup
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30

# Monitoramento
SENTRY_DSN=<OPCIONAL_SENTRY_DSN>
NEW_RELIC_LICENSE_KEY=<OPCIONAL_NEW_RELIC_KEY>

EOF

# Proteger arquivo
chmod 600 .env
```

### **2. Obter Endpoints Reais:**

```bash
# RDS Endpoint
aws rds describe-db-instances \
  --db-instance-identifier marabet-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text

# ElastiCache Endpoint
aws elasticache describe-replication-groups \
  --replication-group-id marabet-redis \
  --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Address' \
  --output text

# Atualizar .env com valores reais
nano .env
```

### **3. Atualizar IP Whitelist API-Football:**

```bash
# Obter IP público da EC2
EC2_IP=$(curl -s http://checkip.amazonaws.com)
echo "IP EC2: $EC2_IP"

# Adicionar no dashboard API-Football:
# https://dashboard.api-football.com/
# Soccer > Settings > IP Whitelist
# Adicionar: <EC2_IP>
```

---

## 🚀 DEPLOY COMPLETO

### **1. Preparar EC2:**

```bash
# Conectar na EC2
ssh -i marabet-key.pem ubuntu@<EC2_IP>

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar
docker --version
docker-compose --version

# Instalar AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Instalar Nginx
sudo apt install -y nginx

# Instalar PostgreSQL Client
sudo apt install -y postgresql-client
```

### **2. Baixar Código:**

```bash
# Criar diretório
sudo mkdir -p /opt/marabet
sudo chown ubuntu:ubuntu /opt/marabet
cd /opt/marabet

# Opção A: Via S3
aws s3 sync s3://marabet-deploy-temp/code/ .

# Opção B: Via Git
git clone https://github.com/seu-usuario/marabet-ai.git .

# Verificar arquivos
ls -la
```

### **3. Configurar Variáveis:**

```bash
# Criar .env (conforme seção anterior)
nano .env

# Verificar
cat .env | grep -v "PASSWORD\|SECRET\|KEY"
```

### **4. Iniciar Aplicação:**

```bash
# Build e start
docker-compose up -d --build

# Verificar logs
docker-compose logs -f

# Verificar containers
docker-compose ps

# Resultado esperado:
# NAME                COMMAND             STATUS
# marabet-app         "gunicorn..."       Up
# marabet-nginx       "nginx -g..."       Up
```

### **5. Executar Migrações:**

```bash
# Entrar no container da aplicação
docker-compose exec app bash

# Executar migrações
python manage.py migrate

# Criar superuser (opcional)
python manage.py createsuperuser

# Sair
exit
```

### **6. Configurar Nginx:**

```bash
# Configuração Nginx
sudo tee /etc/nginx/sites-available/marabet << 'EOF'
upstream marabet_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name marabet.ao www.marabet.ao;

    client_max_body_size 100M;

    location / {
        proxy_pass http://marabet_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/marabet/static/;
        expires 30d;
    }

    location /media/ {
        alias /opt/marabet/media/;
        expires 30d;
    }

    location /health {
        proxy_pass http://marabet_app/health;
        access_log off;
    }
}
EOF

# Ativar site
sudo ln -sf /etc/nginx/sites-available/marabet /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx

# Habilitar no boot
sudo systemctl enable nginx
```

### **7. Configurar Systemd Service:**

```bash
# Criar service
sudo tee /etc/systemd/system/marabet.service << 'EOF'
[Unit]
Description=MaraBet AI Application
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/marabet
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ubuntu
Group=ubuntu

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviço
sudo systemctl enable marabet

# Iniciar
sudo systemctl start marabet

# Verificar status
sudo systemctl status marabet
```

---

## ✅ VALIDAÇÃO

### **1. Testar Aplicação Localmente na EC2:**

```bash
# Testar endpoint health
curl http://localhost/health

# Resposta esperada:
# {"status": "ok", "timestamp": "2025-10-25T..."}

# Testar API
curl http://localhost/api/v1/status

# Testar com IP público (sem ALB ainda)
curl http://<EC2_PUBLIC_IP>/health
```

### **2. Testar Database:**

```bash
# Conectar ao RDS
psql -h <RDS_ENDPOINT> -U marabetadmin -d marabet

# Verificar tabelas
\dt

# Contar registros (se migrou dados)
SELECT COUNT(*) FROM matches;

# Sair
\q
```

### **3. Testar Redis:**

```bash
# Instalar redis-cli
sudo apt install -y redis-tools

# Conectar ao ElastiCache
redis-cli -h <REDIS_ENDPOINT>

# Testar
PING
# Resposta: PONG

SET test "MaraBet OK"
GET test
# Resposta: "MaraBet OK"

# Sair
exit
```

### **4. Testar API-Football:**

```bash
# Via aplicação
curl http://localhost/api/v1/test-football-api

# Ou diretamente
curl "https://v3.football.api-sports.io/status" \
  -H "x-apisports-key: 71b2b62386f2d1275cd3201a73e1e045"
```

### **5. Testar Telegram Bot:**

```bash
# Enviar mensagem teste
docker-compose exec app python -c "
from notifications.telegram import send_message
send_message('🚀 MaraBet AI na AWS está funcionando!')
"
```

### **6. Testar S3:**

```bash
# Upload teste
echo "MaraBet Test" > test.txt
aws s3 cp test.txt s3://marabet-backups/test/

# Listar
aws s3 ls s3://marabet-backups/test/

# Download
aws s3 cp s3://marabet-backups/test/test.txt test_download.txt

# Comparar
diff test.txt test_download.txt
```

---

## 🎯 CHECKLIST FINAL

### **Infraestrutura:**
- [ ] VPC criada (10.0.0.0/16)
- [ ] Subnets configuradas (Public + Private)
- [ ] Security Groups configurados
- [ ] Internet Gateway ativo
- [ ] Route Tables configuradas

### **Compute:**
- [ ] EC2 Instance rodando (t3.large)
- [ ] Docker instalado e funcionando
- [ ] Docker Compose instalado
- [ ] Nginx instalado e configurado
- [ ] Systemd service ativo

### **Database:**
- [ ] RDS PostgreSQL Multi-AZ criado
- [ ] ElastiCache Redis Cluster criado
- [ ] Backup automático configurado (7 dias)
- [ ] Dados migrados (se aplicável)
- [ ] Conexões testadas

### **Storage:**
- [ ] S3 bucket backups criado
- [ ] S3 bucket static criado
- [ ] S3 bucket logs criado
- [ ] Políticas de acesso configuradas

### **Networking:**
- [ ] Application Load Balancer criado
- [ ] Target Group configurado
- [ ] EC2 registrada no Target Group
- [ ] Health checks funcionando
- [ ] Route 53 Hosted Zone criada
- [ ] Registro A apontando para ALB

### **Segurança:**
- [ ] SSL Certificate Manager configurado
- [ ] HTTPS funcionando
- [ ] Security Groups ajustados
- [ ] .env com permissões corretas (600)
- [ ] Senhas fortes configuradas

### **Aplicação:**
- [ ] Código deployado em /opt/marabet
- [ ] .env configurado com endpoints corretos
- [ ] Docker containers rodando
- [ ] Migrações executadas
- [ ] Static files coletados
- [ ] Logs funcionando

### **APIs:**
- [ ] API-Football key válida
- [ ] IP EC2 adicionado ao whitelist
- [ ] Telegram bot configurado
- [ ] Notificações funcionando

### **Monitoramento:**
- [ ] CloudWatch Logs configurado
- [ ] CloudWatch Alarms criados
- [ ] Dashboard CloudWatch criado
- [ ] Logs da aplicação sendo enviados

### **Backup:**
- [ ] Backup automático RDS ativo
- [ ] Script de backup S3 configurado
- [ ] Cron job de backup criado
- [ ] Teste de restore realizado

### **Validação:**
- [ ] Health endpoint respondendo
- [ ] Login funcionando
- [ ] Previsões sendo geradas
- [ ] Telegram enviando notificações
- [ ] API-Football retornando dados
- [ ] Database com dados corretos
- [ ] Redis armazenando cache

---

## 📞 SUPORTE

**MaraBet AI:**
- 📧 Técnico: suporte@marabet.ao
- 📧 Comercial: comercial@marabet.ao
- 📞 WhatsApp: +224 932027393

**AWS Support:**
- 📚 Docs: https://docs.aws.amazon.com
- 💬 Console: https://console.aws.amazon.com/support

---

## 🎉 CONCLUSÃO

Com este guia, você tem:

✅ **Arquitetura Clara** - Diagrama visual da infraestrutura  
✅ **Dados Mapeados** - Código, credenciais, backups  
✅ **Migração Completa** - Passo a passo detalhado  
✅ **Configuração AWS** - Todos os serviços  
✅ **Validação** - Testes de cada componente  
✅ **Checklist** - Garantia de nada esquecer  

**Sistema pronto para produção na AWS! 🚀**

---

**© 2025 MaraBet AI - Powered by AWS**  
**☁️ Infraestrutura de Nível Mundial**  
**🇦🇴 Luanda, Angola**

