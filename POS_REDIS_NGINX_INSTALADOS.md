# ✅ APÓS INSTALAR REDIS E NGINX - PRÓXIMOS PASSOS

**Status**: Redis e Nginx instalados ✅  
**Próximo**: Verificar serviços e enviar código da aplicação

---

## ✅ VERIFICAÇÕES IMEDIATAS

### **1. Verificar Redis**

```bash
# Verificar status
sudo systemctl status redis-server
# Deve mostrar: active (running)

# Testar conexão
redis-cli ping
# Deve retornar: PONG

# Ver informações
redis-cli info server
```

### **2. Verificar Nginx**

```bash
# Verificar status
sudo systemctl status nginx
# Deve mostrar: active (running)

# Testar (deve retornar HTML)
curl http://localhost

# Verificar configuração
sudo nginx -t
# Deve mostrar: syntax is ok / test is successful
```

### **3. Verificar Todas as Portas**

```bash
# Ver portas em uso
sudo netstat -tlnp | grep -E '(5432|6379|80|443|8000)'

# Ou usar ss
sudo ss -tlnp | grep -E '(5432|6379|80|443|8000)'

# Deve mostrar:
# PostgreSQL: 5432 (localhost apenas)
# Redis: 6379
# HTTP: 80
# HTTPS: 443 (será usado após SSL)
# Aplicação: 8000 (será usado após iniciar)
```

---

## ✅ STATUS ATUAL DO DEPLOY

### **Concluído:**
- [x] SSH configurado
- [x] Firewall configurado
- [x] Docker instalado
- [x] Redis instalado ✅
- [x] Nginx instalado ✅
- [ ] PostgreSQL instalado (próximo)
- [ ] Código enviado
- [ ] Aplicação configurada
- [ ] SSL configurado

---

## 📋 PRÓXIMOS PASSOS IMEDIATOS

### **1. Instalar PostgreSQL 15**

**Criar script no servidor:**

```bash
# Criar arquivo
sudo nano /tmp/install_postgresql_secure.sh

# Copiar TODO o conteúdo do SCRIPT_POSTGRESQL_COPIAR_COLAR.txt
# (do seu PC, copiar e colar no nano)
# Salvar: Ctrl+O, Enter, Ctrl+X

# Dar permissão
chmod +x /tmp/install_postgresql_secure.sh

# Executar
sudo /tmp/install_postgresql_secure.sh

# Ver credenciais geradas
cat /opt/marabet/.env.db
```

### **2. Preparar Diretório da Aplicação**

```bash
# Garantir permissões
cd /opt/marabet
sudo chown -R marabet:marabet /opt/marabet

# Criar diretórios necessários
mkdir -p backups logs static media

# Verificar
ls -la
```

### **3. Enviar Código da Aplicação**

**Do seu PC Windows:**

```powershell
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"

# Enviar arquivos essenciais
scp docker-compose.production.yml marabet@37.27.220.67:/opt/marabet/
scp config_production.env marabet@37.27.220.67:/opt/marabet/
scp app.py marabet@37.27.220.67:/opt/marabet/
scp Dockerfile marabet@37.27.220.67:/opt/marabet/
scp requirements.txt marabet@37.27.220.67:/opt/marabet/  # Se existir

# Enviar diretórios principais
scp -r api/ marabet@37.27.220.67:/opt/marabet/
scp -r models/ marabet@37.27.220.67:/opt/marabet/
scp -r migrations/ marabet@37.27.220.67:/opt/marabet/
scp -r static/ marabet@37.27.220.67:/opt/marabet/
scp -r templates/ marabet@37.27.220.67:/opt/marabet/
scp -r config/ marabet@37.27.220.67:/opt/marabet/  # Se existir

# OU enviar tudo (pode demorar):
scp -r * marabet@37.27.220.67:/opt/marabet/
```

### **4. Verificar Arquivos Enviados**

**No servidor:**

```bash
cd /opt/marabet
ls -la

# Deve mostrar:
# docker-compose.production.yml
# config_production.env
# app.py
# Dockerfile
# api/
# models/
# migrations/
# static/
# templates/
```

---

## ⚙️ CONFIGURAR APLICAÇÃO

### **1. Configurar .env**

```bash
cd /opt/marabet

# Copiar configuração
cp config_production.env .env

# Ver credenciais PostgreSQL geradas
cat /opt/marabet/.env.db

# Editar .env
nano .env
```

**Importante no .env:**
```bash
# PostgreSQL - COPIAR do /opt/marabet/.env.db
# Exemplo da linha DATABASE_URL gerada:
DATABASE_URL=postgresql://marabet_user:SENHA_GERADA_PELO_SCRIPT@localhost:5432/marabet

# Redis
REDIS_URL=redis://localhost:6379

# API-Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Telegram
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597

# Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,37.27.220.67,marabet.ao,www.marabet.ao

# Sistema
SYSTEM_IP=37.27.220.67
DEBUG=False
SECRET_KEY=gerar_chave_secreta_forte_aqui
```

### **2. Executar Migrações**

```bash
cd /opt/marabet

# Instalar dependências Python se necessário
sudo apt install -y python3-pip
pip3 install sqlalchemy psycopg2-binary

# Executar migrações
python3 migrate.py --migrate --seed

# Verificar tabelas criadas
psql -h localhost -U marabet_user -d marabet -c "\dt"
```

---

## 🚀 INICIAR APLICAÇÃO

### **1. Build e Iniciar**

```bash
cd /opt/marabet

# Build e iniciar containers
docker compose -f docker-compose.production.yml up -d --build

# Ver status
docker compose ps

# Ver logs
docker compose logs -f
```

### **2. Testar Aplicação**

```bash
# Health check
curl http://localhost:8000/health

# Deve retornar: {"status": "ok"} ou similar

# Ver containers rodando
docker compose ps
# Deve mostrar: web, celery, celery-beat (todos Up)
```

---

## 🔧 CONFIGURAR NGINX (Após Aplicação Rodar)

### **1. Criar Configuração Nginx**

```bash
sudo nano /etc/nginx/sites-available/marabet
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
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket support (se necessário)
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

# Remover site padrão (opcional)
sudo rm /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl reload nginx
```

### **2. Obter Certificado SSL**

```bash
# Obter certificado Let's Encrypt
sudo certbot --nginx -d marabet.ao -d www.marabet.ao

# Verificar certificado
sudo certbot certificates

# Verificar renovação automática
sudo certbot renew --dry-run
```

---

## ✅ CHECKLIST COMPLETO

### **Serviços Instalados:**
- [x] Docker
- [x] Docker Compose
- [x] Redis ✅
- [x] Nginx ✅
- [ ] PostgreSQL (próximo)

### **Próximos Passos:**
- [ ] Instalar PostgreSQL
- [ ] Verificar todos os serviços
- [ ] Enviar código da aplicação
- [ ] Configurar .env
- [ ] Executar migrações
- [ ] Iniciar aplicação
- [ ] Configurar Nginx
- [ ] Obter SSL

---

## 📊 RESUMO RÁPIDO

**Status atual:**
```
✅ SSH configurado
✅ Firewall configurado
✅ Docker instalado e testado
✅ Redis instalado e rodando
✅ Nginx instalado e rodando
⏳ PostgreSQL - próximo passo
```

**Próximo passo:**
1. Criar script PostgreSQL via nano
2. Executar instalação PostgreSQL
3. Ver credenciais geradas
4. Enviar código do PC
5. Configurar .env
6. Iniciar aplicação

---

**📄 Guias Relacionados:**
- `DOCKER_FUNCIONANDO_PROXIMOS_PASSOS.md` - Passos completos
- `DEPLOY_SEQUENCIA_COMPLETA.md` - Sequência completa

**📧 Suporte**: suporte@marabet.ao

