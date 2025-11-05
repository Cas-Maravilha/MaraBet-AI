# 🚀 EXECUTAR DEPLOY AGORA - SERVIDOR 37.27.220.67

**Servidor**: marabet.ao (37.27.220.67)  
**Hostname**: marabet.ao  
**IP**: 37.27.220.67  
**IPv6**: 2a01:4f9:c013:b3f1::/64  
**CPU**: 4 cores | **RAM**: 8 GB | **Disco**: 80 GB  
**OS**: Ubuntu 22.04 LTS  
**Usuário**: root  
**Data**: 28/10/2025  
**Status**: ✅ Running - Pronto para deploy

---

## ⚠️ ANTES DE COMECAR

### **1. Adicionar IP na API-Football**

⚠️ **CRÍTICO**: Execute PRIMEIRO, antes de fazer deploy!

```
1. Acessar: https://dashboard.api-football.com/
2. Login com suas credenciais
3. Ir para "IP Whitelist" ou "Allowed IPs"
4. Adicionar: 37.27.220.67
   - Description: "MaraBet AI - Production Server"
   - Status: Active
5. Salvar e aguardar 2 minutos
```

**Sem isso, a API-Football não funcionará!**

---

## 📋 PASSO A PASSO COMPLETO

### **PASSO 1: Conectar ao Servidor**

```bash
ssh root@37.27.220.67
```

### **PASSO 2: Verificar Sistema**

```bash
# Sistema operacional
cat /etc/os-release

# Espaço e memória
df -h
free -h

# CPU cores
nproc
```

### **PASSO 3: Atualizar Sistema**

```bash
# Ubuntu/Debian
apt update && apt upgrade -y

# Instalar utilitários básicos
apt install -y curl wget git nano htop
```

### **PASSO 4: Instalar PostgreSQL 15**

```bash
# No seu PC, enviar script:
scp install_postgresql_secure.sh root@37.27.220.67:/tmp/

# No servidor, executar:
chmod +x /tmp/install_postgresql_secure.sh
sudo /tmp/install_postgresql_secure.sh

# Ver credenciais geradas:
cat /opt/marabet/.env.db
```

### **PASSO 5: Instalar Docker**

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install -y docker-compose

# Verificar
docker --version
docker-compose --version
```

### **PASSO 6: Enviar Código da Aplicação**

**Do seu PC (no diretório do projeto):**
```bash
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"

# Enviar todos os arquivos
scp -r * root@37.27.220.67:/opt/marabet/
```

### **PASSO 7: Configurar Variáveis de Ambiente**

```bash
# No servidor
cd /opt/marabet

# Copiar configuração
cp config_production.env .env

# Editar
nano .env
```

**Ajustar no .env:**
```bash
# PostgreSQL (usar senha gerada do script)
DATABASE_URL=postgresql://marabet_user:SENHA_GERADA@localhost:5432/marabet

# Redis
REDIS_URL=redis://localhost:6379

# API-Football (adicionar IP primeiro!)
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Telegram
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597

# Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,37.27.220.67,marabet.ao,www.marabet.ao

# Sistema
SYSTEM_IP=37.27.220.67
DEBUG=False
```

### **PASSO 8: Executar Migrações**

```bash
cd /opt/marabet
python migrate.py --migrate --seed
```

### **PASSO 9: Iniciar Aplicação**

```bash
# Build e iniciar containers
docker-compose -f docker-compose.production.yml up -d --build

# Ver status
docker-compose -f docker-compose.production.yml ps

# Ver logs
docker-compose -f docker-compose.production.yml logs -f
```

### **PASSO 10: Testar Aplicação**

```bash
# Health check
curl http://localhost:8000/health

# Verificar PostgreSQL
psql -h localhost -U marabet_user -d marabet -c "SELECT 1;"

# Verificar Redis
redis-cli ping
```

### **PASSO 11: Instalar e Configurar Nginx**

```bash
# Instalar
apt install -y nginx certbot python3-certbot-nginx

# Criar configuração
nano /etc/nginx/sites-available/marabet
```

**Conteúdo do arquivo:**
```nginx
server {
    listen 80;
    server_name marabet.ao www.marabet.ao;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name marabet.ao www.marabet.ao;
    
    ssl_certificate /etc/letsencrypt/live/marabet.ao/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/marabet.ao/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar site
ln -s /etc/nginx/sites-available/marabet /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### **PASSO 12: Obter Certificado SSL**

```bash
certbot --nginx -d marabet.ao -d www.marabet.ao
```

---

## ✅ VERIFICAÇÕES FINAIS

```bash
# 1. Containers rodando
docker-compose ps
# Deve mostrar: web, celery, celery-beat (todos Up)

# 2. Aplicação respondendo
curl http://localhost:8000/health
# Deve retornar: {"status": "ok"}

# 3. PostgreSQL funcionando
psql -h localhost -U marabet_user -d marabet -c "SELECT version();"

# 4. Redis funcionando
redis-cli ping
# Deve retornar: PONG

# 5. Nginx rodando
systemctl status nginx

# 6. SSL funcionando (se configurado)
curl https://marabet.ao
```

---

## 🐛 TROUBLESHOOTING

### **Erro: Container não inicia**
```bash
# Ver logs
docker-compose logs web

# Verificar .env
cat .env

# Verificar PostgreSQL
systemctl status postgresql
```

### **Erro: API-Football não funciona**
```bash
# Verificar se IP foi adicionado
# Acessar: https://dashboard.api-football.com/
# Verificar IP: 37.27.220.67 está na whitelist
```

### **Erro: Migrações falham**
```bash
# Verificar banco
psql -h localhost -U marabet_user -d marabet -c "\l"

# Recriar banco se necessário
dropdb marabet
createdb marabet
python migrate.py --migrate --seed
```

---

## 📊 CHECKLIST FINAL

### **Pré-Deploy**
- [ ] IP 37.27.220.67 adicionado na API-Football
- [ ] Script install_postgresql_secure.sh pronto
- [ ] Código da aplicação pronto para enviar

### **Durante Deploy**
- [ ] Servidor conectado
- [ ] Sistema atualizado
- [ ] PostgreSQL instalado
- [ ] Docker instalado
- [ ] Código enviado
- [ ] .env configurado
- [ ] Migrações executadas
- [ ] Containers iniciados

### **Pós-Deploy**
- [ ] Health check OK
- [ ] PostgreSQL funcionando
- [ ] Redis funcionando
- [ ] Nginx configurado
- [ ] SSL obtido
- [ ] Aplicação acessível

---

## 🎉 APÓS DEPLOY

### **Sistema estará disponível em:**
- **HTTP**: http://37.27.220.67:8000
- **HTTPS**: https://marabet.ao (após configurar DNS)

### **Monitoramento:**
```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver recursos
htop
df -h
```

### **Reiniciar aplicação:**
```bash
cd /opt/marabet
docker-compose restart
```

---

## 📞 SUPORTE

**MaraBet AI:**
- 📧 Email: suporte@marabet.ao
- 📞 WhatsApp: +224 932027393

**Documentação:**
- Guia completo: `ANGOWEB_DEPLOYMENT_GUIDE.md`
- Conexão servidor: `CONECTAR_SERVIDOR_37.27.220.67.md`

---

**✅ Sistema pronto para deploy!**  
**🚀 Execute os passos acima e terá o MaraBet AI rodando em produção!**

