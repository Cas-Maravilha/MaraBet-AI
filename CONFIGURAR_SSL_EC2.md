# 🔒 CONFIGURAR SSL/HTTPS NA EC2 - GUIA COMPLETO

**Sistema**: MaraBet AI  
**Domínio**: marabet.com  
**Método**: Let's Encrypt + Certbot

---

## 📋 ÍNDICE

1. [Conectar à EC2](#1-conectar-à-ec2)
2. [Configurar Nginx para SSL](#2-configurar-nginx-para-ssl)
3. [Instalar Certbot](#3-instalar-certbot)
4. [Obter Certificado SSL](#4-obter-certificado-ssl)
5. [Configurar Auto-Renewal](#5-configurar-auto-renewal)
6. [Testar HTTPS](#6-testar-https)

---

## 1️⃣ CONECTAR À EC2

### **SSH na Instância:**

```bash
# Do seu PC (Windows com Git Bash ou PowerShell)
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Exemplo:
ssh -i marabet-key.pem ubuntu@54.194.XXX.XXX
```

### **Trocar para Usuário marabet:**

```bash
# Mudar para usuário dedicado
sudo su - marabet

# Verificar diretório
cd /opt/marabet
pwd
# Resultado: /opt/marabet

# Listar arquivos
ls -la
```

---

## 2️⃣ CONFIGURAR NGINX PARA SSL

### **Criar Configuração Nginx:**

```bash
# Como root/sudo
exit  # Sair do usuário marabet
sudo su

# Criar configuração SSL
cat > /etc/nginx/sites-available/marabet-ssl << 'EOF'
# HTTP - Redirecionar para HTTPS
server {
    listen 80;
    server_name marabet.com www.marabet.com api.marabet.com;
    
    # Let's Encrypt ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirecionar todo o resto para HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS - Aplicação Principal
server {
    listen 443 ssl http2;
    server_name marabet.com www.marabet.com;
    
    # Certificados SSL (serão configurados pelo Certbot)
    ssl_certificate /etc/letsencrypt/live/marabet.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/marabet.com/privkey.pem;
    
    # SSL Configuration (Mozilla Modern)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Client
    client_max_body_size 100M;
    
    # Logs
    access_log /var/log/nginx/marabet-access.log;
    error_log /var/log/nginx/marabet-error.log;
    
    # Proxy para aplicação
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    # Static files
    location /static/ {
        alias /opt/marabet/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /opt/marabet/media/;
        expires 30d;
    }
    
    # Health check (sem logs)
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}

# HTTPS - API Subdomain
server {
    listen 443 ssl http2;
    server_name api.marabet.com;
    
    ssl_certificate /etc/letsencrypt/live/marabet.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/marabet.com/privkey.pem;
    
    # SSL config (mesmo do acima)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    # Proxy para API
    location / {
        proxy_pass http://127.0.0.1:8000/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Ativar configuração (ainda vai dar erro até obter SSL)
ln -sf /etc/nginx/sites-available/marabet-ssl /etc/nginx/sites-enabled/

# Remover configuração antiga
rm -f /etc/nginx/sites-enabled/marabet
rm -f /etc/nginx/sites-enabled/default

echo "✅ Configuração Nginx criada"
```

---

## 3️⃣ INSTALAR CERTBOT

### **Certbot já está instalado (user-data.sh):**

```bash
# Verificar se Certbot está instalado
which certbot
certbot --version

# Se não estiver instalado
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

---

## 4️⃣ OBTER CERTIFICADO SSL

### **Método 1: Automático com Certbot + Nginx:**

```bash
# Certbot configura tudo automaticamente
sudo certbot --nginx \
  -d marabet.com \
  -d www.marabet.com \
  -d api.marabet.com \
  --non-interactive \
  --agree-tos \
  --email suporte@marabet.com \
  --redirect

# Resultado:
# ✅ Certificado obtido
# ✅ Nginx configurado automaticamente
# ✅ HTTP → HTTPS redirect ativado
# ✅ Auto-renewal configurado
```

### **Método 2: Manual (mais controle):**

```bash
# Obter certificado apenas (sem configurar Nginx)
sudo certbot certonly --nginx \
  -d marabet.com \
  -d www.marabet.com \
  -d api.marabet.com \
  --non-interactive \
  --agree-tos \
  --email suporte@marabet.com

# Certificados salvos em:
# /etc/letsencrypt/live/marabet.com/fullchain.pem
# /etc/letsencrypt/live/marabet.com/privkey.pem

# Configurar Nginx manualmente (usar config acima)
sudo nginx -t
sudo systemctl reload nginx
```

### **Método 3: DNS Challenge (se HTTP não funcionar):**

```bash
sudo certbot certonly --manual \
  --preferred-challenges dns \
  -d marabet.com \
  -d www.marabet.com \
  -d api.marabet.com \
  --email suporte@marabet.com \
  --agree-tos

# Seguir instruções para adicionar TXT records no Route 53
```

---

## 5️⃣ CONFIGURAR AUTO-RENEWAL

### **Verificar Timer Systemd:**

```bash
# Certbot cria timer automático
sudo systemctl list-timers | grep certbot

# Verificar status
sudo systemctl status certbot.timer

# Se não estiver ativo, habilitar
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### **Testar Renovação:**

```bash
# Dry-run (teste sem renovar de verdade)
sudo certbot renew --dry-run

# Se retornar sucesso:
# ✅ Auto-renewal está funcionando!
```

### **Cron Manual (alternativa):**

```bash
# Adicionar ao crontab
sudo crontab -e

# Adicionar linha:
0 2 * * * certbot renew --quiet --deploy-hook "systemctl reload nginx"
```

---

## 6️⃣ TESTAR HTTPS

### **A. Verificar Certificado:**

```bash
# Ver detalhes do certificado
sudo certbot certificates

# Listar certificados
sudo ls -la /etc/letsencrypt/live/

# Ver expiração
sudo openssl x509 -in /etc/letsencrypt/live/marabet.com/fullchain.pem -noout -dates
```

### **B. Testar Localmente:**

```bash
# Na EC2
curl -I https://marabet.com
curl -I https://www.marabet.com
curl -I https://api.marabet.com

# Verificar redirect HTTP → HTTPS
curl -I http://marabet.com
# Deve retornar: 301 Moved Permanently
# Location: https://marabet.com
```

### **C. Testar do Seu PC:**

```bash
# Do seu PC
curl -I https://marabet.com

# Browser
# Abrir: https://marabet.com
# Verificar cadeado verde 🔒
```

### **D. Testar Segurança SSL:**

```bash
# Online
# https://www.ssllabs.com/ssltest/analyze.html?d=marabet.com

# Ou via curl
curl -vI https://marabet.com 2>&1 | grep -i "ssl\|tls"
```

---

## 🔧 TROUBLESHOOTING

### **Erro: "Connection refused"**

```bash
# Verificar se Nginx está rodando
sudo systemctl status nginx

# Iniciar se necessário
sudo systemctl start nginx

# Ver logs
sudo tail -f /var/log/nginx/error.log
```

### **Erro: "Certificate not found"**

```bash
# Verificar se certificado foi criado
sudo ls -la /etc/letsencrypt/live/marabet.com/

# Se não existir, executar certbot novamente
sudo certbot --nginx -d marabet.com -d www.marabet.com
```

### **Erro: "DNS validation failed"**

```bash
# Verificar se DNS está propagado
dig marabet.com

# Resultado deve mostrar o Elastic IP
# Se não mostrar, aguardar propagação DNS
```

### **Erro: "Port 80 unavailable"**

```bash
# Ver o que está usando porta 80
sudo lsof -i :80

# Parar processos conflitantes
sudo systemctl stop <serviço>
```

---

## 📊 VERIFICAR CONFIGURAÇÃO FINAL

### **Script de Verificação:**

```bash
#!/bin/bash

echo "🔒 Verificando SSL/HTTPS"
echo "========================"
echo ""

# 1. Nginx
echo "1. Nginx Status:"
sudo systemctl is-active nginx && echo "✅ Running" || echo "❌ Stopped"

# 2. Certificados
echo ""
echo "2. Certificados SSL:"
sudo ls /etc/letsencrypt/live/marabet.com/ 2>/dev/null && echo "✅ Encontrados" || echo "❌ Não encontrados"

# 3. Portas
echo ""
echo "3. Portas Abertas:"
sudo lsof -i :80 | grep LISTEN && echo "✅ Porta 80" || echo "❌ Porta 80"
sudo lsof -i :443 | grep LISTEN && echo "✅ Porta 443" || echo "❌ Porta 443"

# 4. Teste HTTP
echo ""
echo "4. Teste HTTP:"
curl -s -o /dev/null -w "%{http_code}" http://localhost && echo " ✅ HTTP respondendo" || echo " ❌ HTTP não responde"

# 5. Teste HTTPS
echo ""
echo "5. Teste HTTPS:"
curl -s -k -o /dev/null -w "%{http_code}" https://localhost && echo " ✅ HTTPS respondendo" || echo " ❌ HTTPS não responde"

# 6. Auto-renewal
echo ""
echo "6. Auto-renewal:"
sudo systemctl is-active certbot.timer && echo "✅ Timer ativo" || echo "❌ Timer inativo"

echo ""
echo "✅ Verificação completa!"
```

---

## 📝 CONFIGURAÇÃO COMPLETA

### **Arquivo: `/opt/marabet/.env`**

```bash
# Atualizar .env com URLs HTTPS
cat >> /opt/marabet/.env << 'EOF'

# SSL/HTTPS
APP_URL=https://marabet.com
API_URL=https://api.marabet.com
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true

# Domínio
DOMAIN=marabet.com
ALLOWED_HOSTS=marabet.com,www.marabet.com,api.marabet.com
EOF
```

---

## 🔐 SECURITY HEADERS

### **Nginx Headers (já incluídos na config):**

```nginx
# HSTS (Force HTTPS)
add_header Strict-Transport-Security "max-age=63072000" always;

# Prevent clickjacking
add_header X-Frame-Options "SAMEORIGIN" always;

# Prevent MIME sniffing
add_header X-Content-Type-Options "nosniff" always;

# XSS Protection
add_header X-XSS-Protection "1; mode=block" always;

# Referrer Policy
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

## 📊 MONITORAMENTO SSL

### **Ver Logs:**

```bash
# Nginx access log
sudo tail -f /var/log/nginx/marabet-access.log

# Nginx error log
sudo tail -f /var/log/nginx/marabet-error.log

# Certbot renewal logs
sudo cat /var/log/letsencrypt/letsencrypt.log
```

### **Verificar Expiração:**

```bash
# Ver quando certificado expira
sudo certbot certificates

# Ou manualmente
sudo openssl x509 -in /etc/letsencrypt/live/marabet.com/fullchain.pem -noout -dates

# Resultado:
# notBefore=Oct 27 12:00:00 2025 GMT
# notAfter=Jan 25 12:00:00 2026 GMT (90 dias)
```

---

## 🔄 RENOVAÇÃO MANUAL

### **Se precisar renovar manualmente:**

```bash
# Renovar todos os certificados
sudo certbot renew

# Renovar certificado específico
sudo certbot renew --cert-name marabet.com

# Forçar renovação (teste)
sudo certbot renew --force-renewal

# Recarregar Nginx após renovar
sudo systemctl reload nginx
```

---

## ✅ CHECKLIST

- [ ] SSH na EC2 funcionando
- [ ] Usuário marabet configurado
- [ ] Diretório /opt/marabet acessível
- [ ] Nginx instalado e rodando
- [ ] Certbot instalado
- [ ] DNS propagado (marabet.com → Elastic IP)
- [ ] Certificado SSL obtido
- [ ] Nginx configurado para SSL
- [ ] HTTP → HTTPS redirect funcionando
- [ ] HTTPS respondendo (porta 443)
- [ ] Auto-renewal configurado
- [ ] Security headers ativos
- [ ] Testado com navegador
- [ ] Grade A no SSL Labs

---

## 🌐 URLS FINAIS

Após configuração completa:

```
✅ https://marabet.com
✅ https://www.marabet.com
✅ https://api.marabet.com

Redirect automático:
http://marabet.com → https://marabet.com ✅
```

---

## 📞 COMANDOS RÁPIDOS

```bash
# SSH
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Trocar usuário
sudo su - marabet

# Ver logs Nginx
sudo tail -f /var/log/nginx/marabet-error.log

# Renovar SSL
sudo certbot renew

# Reload Nginx
sudo systemctl reload nginx

# Testar config Nginx
sudo nginx -t
```

---

**🔒 SSL/HTTPS Pronto!**  
**✅ Let's Encrypt Gratuito**  
**🔄 Renovação Automática**  
**🌐 https://marabet.com**

