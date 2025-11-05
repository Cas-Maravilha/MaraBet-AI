# 🖥️ COMANDOS COMPLETOS PARA EC2 - MARABET.COM

**Executar na EC2 via SSH**  
**Usuário**: ubuntu → marabet  
**Domínio**: marabet.com

---

## 📋 SEQUÊNCIA COMPLETA

### **1. Conectar via SSH:**

```bash
# Do seu PC
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]
```

---

### **2. Atualizar Sistema (se necessário):**

```bash
# Como ubuntu
sudo apt-get update
sudo apt-get upgrade -y
```

---

### **3. Instalar Certbot:**

```bash
# Instalar Certbot + plugin Nginx
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Verificar instalação
certbot --version
# Resultado: certbot 1.x.x
```

---

### **4. Verificar Nginx:**

```bash
# Status do Nginx
sudo systemctl status nginx

# Se não estiver rodando
sudo systemctl start nginx
sudo systemctl enable nginx

# Testar configuração
sudo nginx -t
```

---

### **5. Obter Certificado SSL:**

```bash
# Método Automático (Recomendado)
sudo certbot --nginx \
  -d marabet.com \
  -d www.marabet.com \
  -d api.marabet.com \
  --non-interactive \
  --agree-tos \
  --email suporte@marabet.com \
  --redirect

# O que o Certbot faz:
# ✅ Obtém certificado SSL gratuito
# ✅ Configura Nginx automaticamente
# ✅ Ativa redirect HTTP → HTTPS
# ✅ Configura auto-renewal
```

**Resultado Esperado:**
```
Congratulations! You have successfully enabled HTTPS on marabet.com, 
www.marabet.com, and api.marabet.com

IMPORTANT NOTES:
 - Your certificate and chain have been saved at:
   /etc/letsencrypt/live/marabet.com/fullchain.pem
 - Your key file has been saved at:
   /etc/letsencrypt/live/marabet.com/privkey.pem
 - Your certificate will expire on YYYY-MM-DD.
 - Certbot has set up a scheduled task to renew automatically.
```

---

### **6. Verificar Certificado:**

```bash
# Ver certificados instalados
sudo certbot certificates

# Ver detalhes
sudo ls -la /etc/letsencrypt/live/marabet.com/

# Verificar expiração
sudo openssl x509 -in /etc/letsencrypt/live/marabet.com/fullchain.pem -noout -dates
```

---

### **7. Configurar Auto-Renewal:**

```bash
# Verificar timer systemd
sudo systemctl list-timers | grep certbot

# Status do timer
sudo systemctl status certbot.timer

# Testar renovação (dry-run)
sudo certbot renew --dry-run

# Se retornar sucesso:
# ✅ Auto-renewal funcionando!
```

---

### **8. Trocar para Usuário marabet:**

```bash
# Mudar para usuário da aplicação
sudo su - marabet

# Verificar diretório
cd /opt/marabet
pwd
# Resultado: /opt/marabet
```

---

### **9. Configurar .env com HTTPS:**

```bash
# No diretório /opt/marabet
nano .env

# Adicionar/atualizar:
```

```bash
# ================================
# MARABET AI - PRODUCTION
# ================================

# App
APP_URL=https://marabet.com
API_URL=https://api.marabet.com
FORCE_HTTPS=true
DEBUG=false

# Database (RDS PostgreSQL)
DATABASE_URL=postgresql://marabet_admin:GuF#Y(!j38Bgw|YyT<r0J5>yxD3n@database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com:5432/marabet_production?sslmode=require
DB_HOST=database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=marabet_production
DB_USER=marabet_admin
DB_PASSWORD=GuF#Y(!j38Bgw|YyT<r0J5>yxD3n

# Cache (Redis Serverless)
REDIS_URL=rediss://marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com:6379
REDIS_HOST=marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_SSL=true

# API Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Telegram
TELEGRAM_BOT_TOKEN=<SEU_TOKEN>
TELEGRAM_CHAT_ID=5550091597

# Security
SECRET_KEY=$(openssl rand -hex 32)
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
SECURE_SSL_REDIRECT=true

# Domain
ALLOWED_HOSTS=marabet.com,www.marabet.com,api.marabet.com

# AWS
AWS_REGION=eu-west-1
```

**Salvar**: Ctrl+O, Enter, Ctrl+X

---

### **10. Testar Conexões:**

```bash
# A. Testar RDS
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d postgres

# Criar database (se não existir)
CREATE DATABASE marabet_production;
\l
\q

# B. Testar Redis
redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com \
          -p 6379 \
          --tls \
          --insecure

# Comandos
PING
SET test_ssl "OK"
GET test_ssl
exit
```

---

### **11. Deploy com Docker:**

```bash
# No diretório /opt/marabet como usuário marabet

# Verificar se docker-compose.yml existe
ls -la docker-compose.yml

# Build e start
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Verificar containers
docker-compose ps

# Resultado esperado:
# NAME                COMMAND             STATUS
# marabet-app         "gunicorn..."       Up
# (outros containers se tiver)
```

---

### **12. Executar Migrações:**

```bash
# Entrar no container da aplicação
docker-compose exec app bash

# Executar migrações (Django exemplo)
python manage.py migrate

# Ou (Flask com Alembic)
alembic upgrade head

# Ou (custom)
python migrate.py

# Criar superuser (opcional)
python manage.py createsuperuser

# Sair
exit
```

---

### **13. Coletar Static Files:**

```bash
# Django
docker-compose exec app python manage.py collectstatic --noinput

# Flask (copiar manualmente se necessário)
docker-compose exec app cp -r static /opt/marabet/
```

---

### **14. Testar Aplicação:**

```bash
# Voltar para usuário ubuntu
exit

# Testar local
curl http://localhost/health
curl https://localhost/health -k

# Testar com domínio
curl http://marabet.com/health
curl https://marabet.com/health
```

---

### **15. Verificar Logs:**

```bash
# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs da aplicação
sudo -u marabet docker-compose -f /opt/marabet/docker-compose.yml logs -f

# Logs do sistema
sudo journalctl -u nginx -f
```

---

## 🔒 VERIFICAÇÃO FINAL SSL

### **A. Testar do PC:**

```bash
# Curl
curl -I https://marabet.com

# Resultado esperado:
# HTTP/2 200
# server: nginx
# strict-transport-security: max-age=63072000
```

### **B. Navegador:**

```
1. Abrir: https://marabet.com
2. Verificar cadeado 🔒 verde
3. Clicar no cadeado
4. Ver certificado
5. Verificar: Let's Encrypt válido
```

### **C. SSL Labs:**

```
https://www.ssllabs.com/ssltest/analyze.html?d=marabet.com

Objetivo: Grade A ou A+
```

---

## 🔧 COMANDOS ÚTEIS

### **Nginx:**

```bash
# Testar config
sudo nginx -t

# Reload (sem downtime)
sudo systemctl reload nginx

# Restart (com downtime)
sudo systemctl restart nginx

# Status
sudo systemctl status nginx

# Ver configuração ativa
sudo nginx -T | grep server_name
```

### **Certbot:**

```bash
# Listar certificados
sudo certbot certificates

# Renovar (manual)
sudo certbot renew

# Renovar específico
sudo certbot renew --cert-name marabet.com

# Testar renovação
sudo certbot renew --dry-run

# Ver logs
sudo cat /var/log/letsencrypt/letsencrypt.log
```

### **Docker:**

```bash
# Como usuário marabet
cd /opt/marabet

# Ver containers
docker-compose ps

# Logs
docker-compose logs -f app

# Restart app
docker-compose restart app

# Stop all
docker-compose down

# Start all
docker-compose up -d

# Rebuild
docker-compose up -d --build
```

---

## 🔐 SECURITY CHECKLIST

- [ ] SSL/TLS ativo
- [ ] HTTPS funcionando
- [ ] HTTP → HTTPS redirect
- [ ] HSTS header ativo
- [ ] Security headers configurados
- [ ] Auto-renewal testado
- [ ] Firewall UFW ativo
- [ ] Fail2Ban rodando
- [ ] .env com permissões 600
- [ ] Senhas fortes configuradas
- [ ] SSH apenas do seu IP
- [ ] Grade A+ no SSL Labs

---

## 📊 VERIFICAÇÃO COMPLETA

### **Script de Status:**

```bash
#!/bin/bash
# status-marabet.sh

echo "🔍 MaraBet AI - Status do Sistema"
echo "=================================="
echo ""

echo "1. Nginx:"
sudo systemctl is-active nginx && echo "  ✅ Running" || echo "  ❌ Stopped"

echo ""
echo "2. Docker:"
systemctl is-active docker && echo "  ✅ Running" || echo "  ❌ Stopped"

echo ""
echo "3. Aplicação:"
cd /opt/marabet
docker-compose ps

echo ""
echo "4. SSL Certificate:"
sudo certbot certificates | grep -A 3 "marabet.com"

echo ""
echo "5. Conexões:"
echo "  RDS:"
nc -zv database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com 5432 2>&1 | grep -q succeeded && echo "    ✅ Conectado" || echo "    ❌ Falha"

echo "  Redis:"
nc -zv marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com 6379 2>&1 | grep -q succeeded && echo "    ✅ Conectado" || echo "    ❌ Falha"

echo ""
echo "6. HTTPS:"
curl -s -o /dev/null -w "%{http_code}" https://marabet.com 2>/dev/null
if [ $? -eq 0 ]; then
    echo "  ✅ HTTPS respondendo"
else
    echo "  ❌ HTTPS não responde"
fi

echo ""
echo "✅ Verificação completa!"
```

---

## 📞 PRÓXIMOS PASSOS

1. ✅ EC2 criada e configurada
2. ✅ Certbot instalado
3. ✅ SSL obtido
4. ✅ Nginx configurado
5. ✅ Aplicação deployada
6. **Testar**: https://marabet.com
7. **Validar**: SSL Labs
8. **Monitorar**: Logs e métricas

---

**🔒 SSL/HTTPS Configurado!**  
**✅ Let's Encrypt Gratuito**  
**🔄 Renovação Automática a Cada 90 Dias**  
**🌐 https://marabet.com Ativo!**  
**☁️ MaraBet AI - Produção Completa na AWS**

