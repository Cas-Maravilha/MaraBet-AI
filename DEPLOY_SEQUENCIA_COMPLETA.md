# 🚀 SEQUÊNCIA COMPLETA DE DEPLOY - MARABET AI

**Servidor**: marabet.ao (37.27.220.67)  
**Usuário**: marabet  
**Status**: SSH configurado ✅

---

## ✅ CHECKPOINT ATUAL

- ✅ Servidor configurado
- ✅ Usuário marabet criado
- ✅ Firewall configurado
- ✅ SSH seguro configurado
- ⏳ PostgreSQL - Próximo passo
- ⏳ Docker - Instalar
- ⏳ Aplicação - Enviar código

---

## 📋 SEQUÊNCIA COMPLETA DE COMANDOS

### **1. Após Conectar via SSH**

```bash
# Verificar usuário
whoami
# Deve mostrar: marabet

# Verificar diretório
cd /opt/marabet
pwd
# Deve mostrar: /opt/marabet
```

### **2. Criar Script PostgreSQL no Servidor**

```bash
# Criar arquivo
sudo nano /tmp/install_postgresql_secure.sh

# Colar o conteúdo do arquivo SCRIPT_POSTGRESQL_COPIAR_COLAR.txt
# (Copiar do seu PC e colar no nano)

# Salvar: Ctrl+O, Enter, Ctrl+X
# Dar permissão:
chmod +x /tmp/install_postgresql_secure.sh
```

### **3. Executar Instalação PostgreSQL**

```bash
# Executar script
sudo /tmp/install_postgresql_secure.sh

# Verificar credenciais geradas
cat /opt/marabet/.env.db

# Testar PostgreSQL
sudo systemctl status postgresql
psql -h localhost -U marabet_user -d marabet -c "SELECT 1;"
```

### **4. Instalar Docker (se não estiver)**

```bash
# Verificar se já está instalado
docker --version

# Se não estiver, instalar:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker marabet
newgrp docker

# Verificar
docker ps
```

### **5. Instalar Docker Compose**

```bash
# Verificar
docker-compose --version

# Se não estiver:
sudo apt install -y docker-compose
# ou
sudo pip3 install docker-compose
```

### **6. Instalar Nginx**

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl status nginx
```

### **7. Enviar Código da Aplicação**

**Do seu PC Windows:**

```powershell
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"

# Enviar arquivos essenciais
scp docker-compose.production.yml marabet@37.27.220.67:/opt/marabet/
scp config_production.env marabet@37.27.220.67:/opt/marabet/
scp app.py marabet@37.27.220.67:/opt/marabet/
scp Dockerfile marabet@37.27.220.67:/opt/marabet/
scp requirements.txt marabet@37.27.220.67:/opt/marabet/  # Se houver

# Enviar diretórios
scp -r api/ marabet@37.27.220.67:/opt/marabet/
scp -r models/ marabet@37.27.220.67:/opt/marabet/
scp -r migrations/ marabet@37.27.220.67:/opt/marabet/
scp -r static/ marabet@37.27.220.67:/opt/marabet/
scp -r templates/ marabet@37.27.220.67:/opt/marabet/

# OU enviar tudo de uma vez (pode demorar):
scp -r * marabet@37.27.220.67:/opt/marabet/
```

### **8. Configurar .env**

```bash
# No servidor
cd /opt/marabet

# Copiar configuração
cp config_production.env .env

# Editar
nano .env
```

**Editar com credenciais do PostgreSQL:**
```bash
# PostgreSQL (copiar do /opt/marabet/.env.db)
# Exemplo:
DATABASE_URL=postgresql://marabet_user:SENHA_GERADA@localhost:5432/marabet

# Ver senha gerada:
cat /opt/marabet/.env.db

# Redis
REDIS_URL=redis://localhost:6379

# API-Football (VERIFICAR IP na whitelist!)
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Telegram
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597

# Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,37.27.220.67,marabet.ao,www.marabet.ao

# Sistema
SYSTEM_IP=37.27.220.67
DEBUG=False
SECRET_KEY=gerar_chave_secreta_aqui
```

### **9. Instalar Dependências Python**

```bash
cd /opt/marabet

# Instalar Python pip
sudo apt install -y python3-pip

# Instalar dependências (se houver requirements.txt)
pip3 install -r requirements.txt

# Ou instalar manualmente:
pip3 install fastapi uvicorn sqlalchemy psycopg2-binary redis celery pydantic
```

### **10. Executar Migrações**

```bash
cd /opt/marabet

# Executar migrações
python3 migrate.py --migrate --seed

# Verificar tabelas criadas
psql -h localhost -U marabet_user -d marabet -c "\dt"
```

### **11. Iniciar Aplicação**

```bash
cd /opt/marabet

# Build e iniciar
docker-compose -f docker-compose.production.yml up -d --build

# Ver status
docker-compose -f docker-compose.production.yml ps

# Ver logs
docker-compose -f docker-compose.production.yml logs -f
```

### **12. Testar Aplicação**

```bash
# Health check
curl http://localhost:8000/health

# Deve retornar: {"status": "ok"} ou similar
```

### **13. Configurar Nginx**

```bash
# Criar configuração
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
    }
}
```

```bash
# Habilitar site
sudo ln -s /etc/nginx/sites-available/marabet /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl reload nginx
```

### **14. Obter Certificado SSL**

```bash
# Obter certificado Let's Encrypt
sudo certbot --nginx -d marabet.ao -d www.marabet.ao

# Verificar
sudo certbot certificates
```

---

## ✅ VERIFICAÇÕES FINAIS

```bash
# 1. Containers rodando
docker-compose ps
# Deve mostrar: web, celery, celery-beat (todos Up)

# 2. Aplicação respondendo
curl http://localhost:8000/health

# 3. PostgreSQL funcionando
psql -h localhost -U marabet_user -d marabet -c "SELECT version();"

# 4. Redis funcionando (se instalado)
redis-cli ping

# 5. Nginx rodando
sudo systemctl status nginx

# 6. SSL funcionando (após configurar DNS)
curl https://marabet.ao
```

---

## 🎉 DEPLOY COMPLETO!

Após completar todos os passos:

✅ **Aplicação**: Rodando em http://localhost:8000  
✅ **Nginx**: Configurado como proxy reverso  
✅ **SSL**: Certificado configurado  
✅ **DNS**: Configurar marabet.ao → 37.27.220.67  

**Sistema MaraBet AI estará online!**

---

**📄 Guias Relacionados:**
- `DEPLOY_EXECUTAR_AGORA.md` - Deploy completo
- `PROXIMOS_PASSOS_POS_INSTALACAO.md` - Próximos passos
- `APOS_CONFIGURACAO_INICIAL.md` - Após configuração inicial

**📧 Suporte**: suporte@marabet.ao

