# 🇦🇴 MARABET AI - GUIA DE DEPLOY NA ANGOWEB

**Sistema**: MaraBet AI - Análise Desportiva com IA  
**Provedor**: Angoweb (Angola)  
**Localização**: Luanda, Angola  
**Domínio**: marabet.ao  
**Data**: 2025

---

## 📋 ÍNDICE

1. [Requisitos](#-requisitos)
2. [Configuração do Servidor VPS](#-configuração-do-servidor-vps)
3. [Instalação do Software](#-instalação-do-software)
4. [Configuração do Banco de Dados](#-configuração-do-banco-de-dados)
5. [Deploy da Aplicação](#-deploy-da-aplicação)
6. [Configuração SSL/HTTPS](#-configuração-sslhttps)
7. [Configuração DNS](#-configuração-dns)
8. [Monitoramento](#-monitoramento)
9. [Backup e Manutenção](#-backup-e-manutenção)
10. [Troubleshooting](#-troubleshooting)

---

## ⚡ DEPLOY RÁPIDO (TL;DR)

```bash
# 1. Conectar ao servidor
ssh marabet@95.216.143.185

# 2. Enviar script de instalação PostgreSQL
scp install_postgresql_secure.sh marabet@95.216.143.185:/tmp/

# 3. Executar script
ssh marabet@95.216.143.185
sudo /tmp/install_postgresql_secure.sh

# 4. Verificar credenciais geradas
cat /opt/marabet/.env.db

# 5. Enviar código da aplicação
cd /caminho/local/do/marabet
scp -r * marabet@95.216.143.185:/opt/marabet/

# 6. Iniciar aplicação
ssh marabet@95.216.143.185
cd /opt/marabet
docker-compose -f docker-compose.production.yml up -d
```

---

## 🎯 REQUISITOS

### **VPS Angoweb Recomendado:**

| Especificação | Mínimo | Recomendado |
|---------------|--------|-------------|
| **RAM** | 8GB | 16GB |
| **CPU** | 2 vCPUs | 4 vCPUs |
| **Storage** | 50GB SSD | 100GB SSD |
| **OS** | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| **Custo** | ~150.000 AOA/mês | ~200.000 AOA/mês |

### **Software Necessário:**

- ✅ PostgreSQL 15 (incluído na Angoweb)
- ✅ Redis 7 (incluído na Angoweb)
- ✅ Docker 24.x
- ✅ Docker Compose 2.x
- ✅ Nginx
- ✅ Certbot (Let's Encrypt)

---

## 🖥️ CONFIGURAÇÃO DO SERVIDOR VPS

### **1. Servidor Angoweb Configurado**

**Servidor Ativo:**
- **IP**: 95.216.143.185
- **Usuário**: marabet
- **OS**: Linux (Ubuntu/Debian)

### **2. Conectar ao Servidor**

```bash
# SSH para o servidor
ssh marabet@95.216.143.185

# OU com chave SSH (se configurada)
ssh -i ~/.ssh/id_rsa marabet@95.216.143.185
```

---

## 💻 INSTALAÇÃO DO SOFTWARE

### **1. Conectar e Atualizar Sistema**

```bash
# Conectar ao servidor
ssh marabet@95.216.143.185

# Atualizar pacotes
sudo apt update && sudo apt upgrade -y

# Instalar utilitários
sudo apt install -y curl wget git nano htop
```

### **2. Instalar Docker**

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Verificar instalação
docker --version
```

### **3. Instalar Docker Compose**

```bash
# Instalar Docker Compose
sudo apt install -y docker-compose

# Verificar instalação
docker-compose --version
```

### **4. Instalar Nginx e Certbot**

```bash
# Instalar Nginx
sudo apt install -y nginx

# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Habilitar e iniciar Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### **5. Configurar Firewall (UFW)**

```bash
# Habilitar UFW
sudo ufw enable

# Permitir portas essenciais
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Verificar regras
sudo ufw status
```

---

## 🗄️ CONFIGURAÇÃO DO BANCO DE DADOS

### **Opção A: Instalação Automática (Recomendado)**

**Upload e executar script seguro:**

```bash
# 1. Upload do script
scp install_postgresql_secure.sh marabet@95.216.143.185:/tmp/

# 2. Conectar ao servidor
ssh marabet@95.216.143.185

# 3. Executar script (cria usuário, banco e configura segurança)
chmod +x /tmp/install_postgresql_secure.sh
sudo /tmp/install_postgresql_secure.sh
```

**O script irá:**
- ✅ Instalar PostgreSQL 15
- ✅ Criar banco `marabet` e usuário `marabet_user`
- ✅ Gerar senha forte automaticamente
- ✅ Configurar firewall (bloquear porta 5432 externamente)
- ✅ Salvar credenciais em `/opt/marabet/.env.db` (permissões 600)
- ✅ Configurar PostgreSQL para escutar apenas localhost

### **Opção B: Instalação Manual**

```bash
# Acessar servidor via SSH
ssh marabet@95.216.143.185

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar PostgreSQL 15
sudo apt install -y postgresql-15 postgresql-client-15

# Iniciar e habilitar serviço
sudo systemctl enable --now postgresql

# Criar banco e usuário (usando credenciais da Angoweb)
sudo -u postgres psql <<EOF
CREATE DATABASE marabet;
CREATE USER marabeta_marabet WITH ENCRYPTED PASSWORD '"LT/x%6,jb';
GRANT ALL PRIVILEGES ON DATABASE marabet TO marabeta_marabet;
\q
EOF

# Dar permissões adicionais no schema
sudo -u postgres psql -d marabet <<EOF
GRANT ALL ON SCHEMA public TO marabeta_marabet;
\q
EOF

# Verificar criação
sudo -u postgres psql -c "\l"  # Listar bancos
sudo -u postgres psql -c "\du" # Listar usuários
```

### **3. Verificar Redis**

```bash
# Status do Redis
sudo systemctl status redis-server

# Se não estiver instalado
sudo apt install -y redis-server

# Iniciar Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Testar Redis
redis-cli ping
# Deve retornar: PONG
```

---

## 🚀 DEPLOY DA APLICAÇÃO

### **1. Criar Diretório**

```bash
# Criar diretório
sudo mkdir -p /opt/marabet
sudo chown $USER:$USER /opt/marabet
cd /opt/marabet
```

### **2. Upload do Código**

**Opção A - Via SCP (Recomendado):**

```bash
# Do seu computador local
scp -r * marabet@95.216.143.185:/opt/marabet/

# OU enviar arquivos específicos
cd /caminho/para/marabet
scp -r . marabet@95.216.143.185:/opt/marabet/
```

**Opção B - Via Git:**

```bash
# Clonar repositório
git clone https://github.com/seu-repo/marabet.git /opt/marabet
cd /opt/marabet
```

### **3. Configurar Variáveis de Ambiente**

```bash
# Copiar arquivo de exemplo
cp config_production.env .env

# Editar .env
nano .env
```

**Configurações necessárias:**

```bash
# SECURITY
SECRET_KEY=sua_secret_key_aqui
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,marabet.ao,www.marabet.ao

# DATABASE (local - Angoweb)
DATABASE_URL=postgresql://marabeta_marabet:"LT/x%6,jb@localhost:5432/marabet

# REDIS (local - Angoweb)
REDIS_URL=redis://localhost:6379

# API KEYS
API_FOOTBALL_KEY=sua_chave_api_football
TELEGRAM_BOT_TOKEN=seu_token_telegram
TELEGRAM_CHAT_ID=seu_chat_id

# SYSTEM
SYSTEM_IP=SEU_IP_PUBLICO_ANGOWEB
```

### **4. Executar Migrações**

```bash
# Executar migrações
python migrate.py --migrate --seed

# Verificar banco de dados
psql -h localhost -U marabeta_marabet -d marabet_production
```

### **5. Iniciar Aplicação com Docker**

```bash
# Build e iniciar
docker-compose -f docker-compose.production.yml up -d --build

# Ver logs
docker-compose -f docker-compose.production.yml logs -f

# Verificar status
docker-compose -f docker-compose.production.yml ps
```

---

## 🔒 CONFIGURAÇÃO SSL/HTTPS

### **1. Configurar Nginx**

```bash
# Criar configuração Nginx
sudo nano /etc/nginx/sites-available/marabet
```

**Conteúdo:**

```nginx
server {
    listen 80;
    server_name marabet.ao www.marabet.ao;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name marabet.ao www.marabet.ao;
    
    # SSL Configuration (será configurado pelo Certbot)
    ssl_certificate /etc/letsencrypt/live/marabet.ao/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/marabet.ao/privkey.pem;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logs
    access_log /var/log/nginx/marabet_access.log;
    error_log /var/log/nginx/marabet_error.log;
    
    # Proxy to Docker
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Habilitar site
sudo ln -s /etc/nginx/sites-available/marabet /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### **2. Obter Certificado SSL**

```bash
# Obter certificado Let's Encrypt
sudo certbot --nginx -d marabet.ao -d www.marabet.ao

# Renovação automática (já configurado)
sudo certbot renew --dry-run

# Verificar certificado
sudo certbot certificates
```

---

## 🌐 CONFIGURAÇÃO DNS

### **1. Configurar Registros DNS na Angoweb**

1. Acesse painel Angoweb
2. Vá em "Gestão de DNS"
3. Adicione registros:

| Tipo | Nome | Conteúdo | TTL |
|------|------|----------|-----|
| A | @ | IP_DO_SERVIDOR | 3600 |
| A | www | IP_DO_SERVIDOR | 3600 |

### **2. Verificar DNS**

```bash
# Verificar DNS
dig marabet.ao
dig www.marabet.ao

# Ou
nslookup marabet.ao
```

---

## 📊 MONITORAMENTO

### **1. Verificar Logs**

```bash
# Logs da aplicação
docker-compose -f docker-compose.production.yml logs -f

# Logs do Nginx
sudo tail -f /var/log/nginx/marabet_access.log
sudo tail -f /var/log/nginx/marabet_error.log

# Logs do PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### **2. Verificar Recursos**

```bash
# CPU e RAM
htop

# Espaço em disco
df -h

# Uso de disco por diretório
du -sh /*
```

### **3. Health Check**

```bash
# Verificar endpoints
curl http://localhost:8000/health
curl https://marabet.ao/health
```

---

## 💾 BACKUP E MANUTENÇÃO

### **1. Backup Automático**

```bash
# Configurar backup diário
./backups/scripts/setup_cron.sh

# Backup manual
./backups/scripts/backup.sh
```

### **2. Manutenção**

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Limpar Docker
docker system prune -f

# Limpar logs antigos
sudo logrotate -f /etc/logrotate.d/docker
```

---

## 🔧 TROUBLESHOOTING

### **Problema: Aplicação não inicia**

```bash
# Ver logs
docker-compose logs web
docker-compose logs celery

# Verificar banco de dados
psql -h localhost -U marabeta_marabet -d marabet -c "SELECT 1;"

# Verificar Redis
redis-cli ping
```

### **Problema: Erro 502 Bad Gateway**

```bash
# Verificar se containers estão rodando
docker-compose ps

# Verificar se aplicação responde
curl http://localhost:8000/health

# Verificar Nginx
sudo nginx -t
sudo systemctl status nginx
```

### **Problema: SSL não funciona**

```bash
# Verificar certificado
sudo certbot certificates

# Renovar certificado manualmente
sudo certbot renew

# Verificar firewall
sudo ufw status
```

### **Problema: Banda não atualiza**

```bash
# Limpar cache DNS no servidor
sudo systemd-resolve --flush-caches

# Verificar DNS
dig marabet.ao
```

---

## 📞 SUPORTE

### **Angoweb:**

- 📞 **Telefone**: +244 222 638 200
- 📧 **Email**: suporte@angoweb.com
- 🌐 **Website**: https://angoweb.com

### **MaraBet AI:**

- 📞 **Telefone**: +224 932027393
- 📧 **Email**: suporte@marabet.ao
- 🌐 **Website**: https://marabet.ao

---

## ✅ CHECKLIST FINAL

- [ ] Servidor VPS Angoweb criado
- [ ] PostgreSQL instalado e configurado
- [ ] Redis instalado e configurado
- [ ] Docker e Docker Compose instalados
- [ ] Nginx instalado e configurado
- [ ] Certificado SSL ativo
- [ ] DNS configurado
- [ ] Aplicação acessível em https://marabet.ao
- [ ] Monitoramento configurado
- [ ] Backup automático ativo

---

**🎉 Deploy Completo na Angoweb!**

**✅ Sistema MaraBet AI hospedado em Luanda, Angola**  
**🇦🇴 Domínio .ao configurado**  
**🔒 SSL/HTTPS ativo**  
**🚀 Pronto para produção**

