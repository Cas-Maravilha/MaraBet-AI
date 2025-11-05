# 🌐 NGINX - CONFIGURAÇÃO BÁSICA MARABET.COM

**Configuração inicial HTTP (antes do SSL)**

---

## 📝 CONFIGURAÇÃO BÁSICA

### **Arquivo:** `/etc/nginx/sites-available/marabet`

```nginx
server {
    listen 80;
    server_name marabet.com www.marabet.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🚀 PASSOS PARA ATIVAR

### **1. Criar arquivo de configuração:**

```bash
# SSH na EC2
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Criar/editar configuração
sudo nano /etc/nginx/sites-available/marabet
```

**Colar a configuração acima**, depois:
- **Salvar**: `Ctrl+O`, `Enter`
- **Sair**: `Ctrl+X`

---

### **2. Ativar o site:**

```bash
# Criar link simbólico
sudo ln -sf /etc/nginx/sites-available/marabet /etc/nginx/sites-enabled/

# Remover default
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar sites ativos
ls -la /etc/nginx/sites-enabled/
```

---

### **3. Testar configuração:**

```bash
# Testar sintaxe
sudo nginx -t

# Resultado esperado:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

### **4. Reload Nginx:**

```bash
# Reload (sem downtime)
sudo systemctl reload nginx

# Ou restart
sudo systemctl restart nginx

# Verificar status
sudo systemctl status nginx
```

---

### **5. Testar aplicação:**

```bash
# Testar local
curl http://localhost

# Testar com domínio
curl http://marabet.com

# Do seu PC
curl http://marabet.com
```

---

## 📊 O QUE ESTA CONFIGURAÇÃO FAZ

```
Internet → Nginx (porta 80)
              ↓
    Proxy para localhost:8000
              ↓
       Aplicação MaraBet
```

### **Headers Configurados:**
- `Host` - Domínio original
- `X-Real-IP` - IP real do cliente
- `X-Forwarded-For` - Chain de proxies
- `X-Forwarded-Proto` - Protocolo (http/https)

---

## ➕ MELHORIAS OPCIONAIS

### **Adicionar Static Files:**

```nginx
server {
    listen 80;
    server_name marabet.com www.marabet.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /opt/marabet/static/;
        expires 30d;
    }
    
    # Media files
    location /media/ {
        alias /opt/marabet/media/;
        expires 7d;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

---

## 🔒 PRÓXIMO PASSO: SSL

Após configuração básica funcionar:

```bash
# Instalar Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obter SSL (atualiza Nginx automaticamente)
sudo certbot --nginx -d marabet.com -d www.marabet.com --email suporte@marabet.com

# Certbot irá:
# ✅ Obter certificado SSL
# ✅ Atualizar configuração Nginx
# ✅ Adicionar redirect HTTP → HTTPS
# ✅ Configurar auto-renewal
```

---

## 🧪 VERIFICAÇÃO

### **Testar Nginx:**

```bash
# Sintaxe
sudo nginx -t

# Status
sudo systemctl status nginx

# Ver configuração ativa
sudo nginx -T | grep server_name
```

### **Ver Logs:**

```bash
# Access log
sudo tail -f /var/log/nginx/access.log

# Error log
sudo tail -f /var/log/nginx/error.log
```

---

## ✅ CHECKLIST

- [ ] Arquivo criado: /etc/nginx/sites-available/marabet
- [ ] Link simbólico criado: sites-enabled/marabet
- [ ] Default removido
- [ ] Nginx testado: `nginx -t`
- [ ] Nginx recarregado
- [ ] Porta 8000 rodando aplicação
- [ ] HTTP funcionando
- [ ] Domínio resolvendo
- [ ] Logs OK
- [ ] Pronto para SSL

---

**🌐 Nginx Configurado!**  
**✅ HTTP Funcionando**  
**⏭️ Próximo: SSL/HTTPS**  
**☁️ marabet.com**

