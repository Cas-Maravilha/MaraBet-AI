# 🖥️ CONECTAR AO SERVIDOR 37.27.220.67

**Servidor**: 37.27.220.67  
**Usuário**: root  
**Comando**: `ssh root@37.27.220.67`

---

## 📋 CHECKLIST ANTES DE CONECTAR

### **1. IP Whitelist API-Football**
⚠️ **IMPORTANTE**: Adicionar este IP no dashboard da API-Football

**IP para adicionar**: `37.27.220.67`  
**Dashboard**: https://dashboard.api-football.com/  
**Descrição**: "MaraBet AI - Production Server"

### **2. Verificar Conexão SSH**
```bash
# Testar conectividade
ping 37.27.220.67

# Tentar conectar
ssh root@37.27.220.67
```

---

## 🚀 DEPLOY NO SERVIDOR

### **1. Conectar**
```bash
ssh root@37.27.220.67
```

### **2. Verificar Sistema**
```bash
# Sistema operacional
cat /etc/os-release

# Espaço em disco
df -h

# Memória
free -h

# CPU
nproc
```

### **3. Atualizar Sistema**
```bash
# Ubuntu/Debian
apt update && apt upgrade -y

# Ou CentOS/RHEL
yum update -y
```

### **4. Instalar PostgreSQL 15**
```bash
# Enviar script de instalação
# Do seu PC:
scp install_postgresql_secure.sh root@37.27.220.67:/tmp/

# No servidor:
chmod +x /tmp/install_postgresql_secure.sh
sudo /tmp/install_postgresql_secure.sh
```

### **5. Instalar Docker**
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install docker-compose -y
# ou
pip install docker-compose

# Adicionar usuário ao grupo docker
usermod -aG docker root
```

### **6. Enviar Código da Aplicação**
```bash
# Do seu PC
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"

# Enviar arquivos
scp -r * root@37.27.220.67:/opt/marabet/
```

### **7. Configurar Aplicação**
```bash
# No servidor
cd /opt/marabet

# Copiar config
cp config_production.env .env

# Editar .env
nano .env
```

**Ajustar no .env:**
```bash
# PostgreSQL (após instalar)
DATABASE_URL=postgresql://marabet_user:senha_gerada@localhost:5432/marabet

# Redis
REDIS_URL=redis://localhost:6379

# API-Football (adicionar IP 37.27.220.67 no dashboard primeiro!)
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Telegram
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597

# Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,37.27.220.67,marabet.ao,www.marabet.ao

# IP do Sistema
SYSTEM_IP=37.27.220.67
```

### **8. Executar Migrações**
```bash
python migrate.py --migrate --seed
```

### **9. Iniciar Aplicação**
```bash
docker-compose -f docker-compose.production.yml up -d --build
```

### **10. Verificar Status**
```bash
# Ver containers
docker-compose ps

# Ver logs
docker-compose logs -f web

# Testar aplicação
curl http://localhost:8000/health
```

---

## 🔒 CONFIGURAR SSL/HTTPS

### **1. Instalar Nginx e Certbot**
```bash
apt install nginx certbot python3-certbot-nginx -y
```

### **2. Configurar Nginx**
```bash
nano /etc/nginx/sites-available/marabet
```

**Conteúdo:**
```nginx
server {
    listen 80;
    server_name marabet.ao www.marabet.ao;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name marabet.ao www.marabet.ao;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **3. Obter Certificado SSL**
```bash
certbot --nginx -d marabet.ao -d www.marabet.ao
```

---

## ⚠️ IMPORTANTE: API-FOOTBALL

### **Adicionar IP no Dashboard**

**IP**: `37.27.220.67`  
**Dashboard**: https://dashboard.api-football.com/  
**Descrição**: "MaraBet AI - Production Server"

**Sem isso, a API-Football não funcionará!**

---

## 📊 VERIFICAÇÕES PÓS-DEPLOY

```bash
# Aplicação rodando
docker-compose ps

# PostgreSQL
psql -h localhost -U marabet_user -d marabet -c "SELECT 1;"

# Redis
redis-cli ping

# Nginx
systemctl status nginx

# SSL
curl https://marabet.ao

# Logs
tail -f /var/log/nginx/marabet_access.log
```

---

## 📝 RESUMO RÁPIDO

```bash
# 1. Conectar
ssh root@37.27.220.67

# 2. Atualizar
apt update && apt upgrade -y

# 3. Instalar PostgreSQL
scp install_postgresql_secure.sh root@37.27.220.67:/tmp/
sudo /tmp/install_postgresql_secure.sh

# 4. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh

# 5. Enviar código
scp -r * root@37.27.220.67:/opt/marabet/

# 6. Configurar
cd /opt/marabet
cp config_production.env .env
nano .env

# 7. Migrar
python migrate.py --migrate --seed

# 8. Iniciar
docker-compose -f docker-compose.production.yml up -d

# 9. SSL
certbot --nginx -d marabet.ao
```

---

**📄 Guia Completo**: `ANGOWEB_DEPLOYMENT_GUIDE.md`  
**📧 Suporte**: suporte@marabet.ao

