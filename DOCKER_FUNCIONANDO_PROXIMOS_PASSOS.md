# ✅ DOCKER FUNCIONANDO - PRÓXIMOS PASSOS COMPLETOS

**Status**: Docker testado e funcionando ✅  
**Próximo**: Instalar PostgreSQL e serviços necessários

---

## ✅ CONFIRMADO

```
✅ Docker instalado
✅ Docker Compose instalado
✅ Docker funcionando (hello-world executado)
✅ Usuário marabet no grupo docker
```

---

## 📋 SEQUÊNCIA DE INSTALAÇÃO

### **1. Instalar PostgreSQL 15**

**Criar script no servidor:**

```bash
# Criar arquivo
sudo nano /tmp/install_postgresql_secure.sh

# Copiar TODO o conteúdo do arquivo SCRIPT_POSTGRESQL_COPIAR_COLAR.txt
# (do seu PC, copiar e colar no nano)

# Salvar: Ctrl+O, Enter, Ctrl+X
# Dar permissão:
chmod +x /tmp/install_postgresql_secure.sh

# Executar
sudo /tmp/install_postgresql_secure.sh

# O script irá:
# ✅ Instalar PostgreSQL 15
# ✅ Criar banco 'marabet'
# ✅ Criar usuário 'marabet_user'
# ✅ Gerar senha forte automaticamente
# ✅ Configurar segurança
# ✅ Salvar credenciais em /opt/marabet/.env.db

# Ver credenciais geradas
cat /opt/marabet/.env.db
```

### **2. Instalar Redis**

```bash
# Instalar Redis
sudo apt install -y redis-server

# Habilitar e iniciar
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verificar status
sudo systemctl status redis-server

# Testar
redis-cli ping
# Deve retornar: PONG
```

### **3. Instalar Nginx e Certbot**

```bash
# Instalar Nginx
sudo apt install -y nginx

# Instalar Certbot (SSL)
sudo apt install -y certbot python3-certbot-nginx

# Habilitar e iniciar Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Verificar
sudo systemctl status nginx

# Testar (deve retornar HTML do Nginx)
curl http://localhost
```

### **4. Verificar Serviços Instalados**

```bash
# PostgreSQL
sudo systemctl status postgresql
psql -h localhost -U marabet_user -d marabet -c "SELECT 1;"

# Redis
redis-cli ping

# Nginx
sudo systemctl status nginx
curl http://localhost

# Docker
docker ps
docker compose version
```

---

## 📤 ENVIAR CÓDIGO DA APLICAÇÃO

### **Preparar no Servidor:**

```bash
# Garantir permissões
cd /opt/marabet
sudo chown -R marabet:marabet /opt/marabet

# Criar diretórios
mkdir -p backups logs static media
```

### **Do seu PC Windows:**

```powershell
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"

# Opção 1: Enviar tudo de uma vez
scp -r * marabet@37.27.220.67:/opt/marabet/

# Opção 2: Enviar arquivo por arquivo (se houver problemas)
scp docker-compose.production.yml marabet@37.27.220.67:/opt/marabet/
scp config_production.env marabet@37.27.220.67:/opt/marabet/
scp app.py marabet@37.27.220.67:/opt/marabet/
scp Dockerfile marabet@37.27.220.67:/opt/marabet/
scp requirements.txt marabet@37.27.220.67:/opt/marabet/

# Enviar diretórios
scp -r api/ marabet@37.27.220.67:/opt/marabet/
scp -r models/ marabet@37.27.220.67:/opt/marabet/
scp -r migrations/ marabet@37.27.220.67:/opt/marabet/
scp -r static/ marabet@37.27.220.67:/opt/marabet/
scp -r templates/ marabet@37.27.220.67:/opt/marabet/
```

### **Verificar no Servidor:**

```bash
cd /opt/marabet
ls -la

# Deve mostrar:
# - docker-compose.production.yml
# - config_production.env
# - app.py
# - Dockerfile
# - api/
# - models/
# - migrations/
# etc.
```

---

## ⚙️ CONFIGURAR APLICAÇÃO

### **1. Configurar .env**

```bash
cd /opt/marabet

# Copiar configuração
cp config_production.env .env

# Editar
nano .env
```

**Editar .env com:**

```bash
# PostgreSQL (usar credenciais do /opt/marabet/.env.db)
# Copiar a linha DATABASE_URL do arquivo gerado:
cat /opt/marabet/.env.db

# Colar no .env, exemplo:
DATABASE_URL=postgresql://marabet_user:SENHA_GERADA@localhost:5432/marabet

# Redis
REDIS_URL=redis://localhost:6379

# API-Football (VERIFICAR se IP 37.27.220.67 foi adicionado!)
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Telegram
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597

# Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,37.27.220.67,marabet.ao,www.marabet.ao

# Sistema
SYSTEM_IP=37.27.220.67
DEBUG=False
SECRET_KEY=gerar_chave_secreta_forte_aqui_ou_usar_openssl_rand_base64_32
```

### **2. Instalar Dependências Python (se necessário)**

```bash
cd /opt/marabet

# Instalar pip se não tiver
sudo apt install -y python3-pip

# Se houver requirements.txt:
pip3 install -r requirements.txt

# Ou instalar manualmente:
pip3 install fastapi uvicorn sqlalchemy psycopg2-binary redis celery pydantic
```

### **3. Executar Migrações**

```bash
cd /opt/marabet

# Executar migrações do banco
python3 migrate.py --migrate --seed

# Verificar tabelas criadas
psql -h localhost -U marabet_user -d marabet -c "\dt"

# Deve mostrar lista de tabelas
```

---

## 🚀 INICIAR APLICAÇÃO

### **1. Build e Iniciar Containers**

```bash
cd /opt/marabet

# Build e iniciar
docker compose -f docker-compose.production.yml up -d --build

# OU se usar docker-compose standalone:
docker-compose -f docker-compose.production.yml up -d --build

# Ver status
docker compose ps
# OU
docker-compose ps
```

### **2. Ver Logs**

```bash
# Ver logs de todos os serviços
docker compose logs -f

# OU logs específicos
docker compose logs -f web
docker compose logs -f celery

# Ver últimas 100 linhas
docker compose logs --tail=100
```

### **3. Testar Aplicação**

```bash
# Health check
curl http://localhost:8000/health

# Deve retornar: {"status": "ok"} ou similar

# Testar endpoint principal
curl http://localhost:8000/

# Ver containers rodando
docker compose ps
```

---

## ⚠️ SE DER ERRO AO INICIAR

### **Problema: Container não inicia**

```bash
# Ver logs detalhados
docker compose logs web

# Verificar .env
cat .env

# Verificar Dockerfile
cat Dockerfile

# Verificar docker-compose
cat docker-compose.production.yml
```

### **Problema: Erro de conexão ao PostgreSQL**

```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Testar conexão manual
psql -h localhost -U marabet_user -d marabet

# Verificar credenciais
cat /opt/marabet/.env.db
cat .env | grep DATABASE_URL
```

### **Problema: Erro de conexão ao Redis**

```bash
# Verificar Redis
sudo systemctl status redis-server
redis-cli ping

# Verificar URL no .env
cat .env | grep REDIS
```

---

## ✅ CHECKLIST FINAL ANTES DE INICIAR APLICAÇÃO

- [ ] PostgreSQL instalado e funcionando
- [ ] Redis instalado e funcionando
- [ ] Docker funcionando
- [ ] Docker Compose funcionando
- [ ] Código enviado para /opt/marabet/
- [ ] .env configurado com credenciais corretas
- [ ] DATABASE_URL copiado do /opt/marabet/.env.db
- [ ] Migrações executadas
- [ ] IP 37.27.220.67 adicionado na API-Football whitelist

---

## 🎉 APÓS INICIAR APLICAÇÃO COM SUCESSO

### **Status Esperado:**

```bash
docker compose ps

# Deve mostrar:
# NAME                STATUS        PORTS
# marabet-web         Up           0.0.0.0:8000->8000/tcp
# marabet-celery      Up
# marabet-celery-beat Up
```

### **Testar:**

```bash
# Health check
curl http://localhost:8000/health

# Deve retornar JSON com status OK
```

### **Próximos Passos:**

1. ✅ Aplicação rodando
2. ⏳ Configurar Nginx como proxy reverso
3. ⏳ Obter certificado SSL
4. ⏳ Configurar DNS (marabet.ao → 37.27.220.67)

---

## 📊 RESUMO RÁPIDO

**Ordem de execução:**

1. ✅ Docker testado (hello-world)
2. ⏳ Instalar PostgreSQL (script)
3. ⏳ Instalar Redis
4. ⏳ Instalar Nginx
5. ⏳ Enviar código do PC
6. ⏳ Configurar .env
7. ⏳ Executar migrações
8. ⏳ Iniciar aplicação

---

**📄 Guias Relacionados:**
- `DEPLOY_SEQUENCIA_COMPLETA.md` - Sequência completa
- `POS_DOCKER_VERIFICADO.md` - Após Docker
- `SCRIPT_POSTGRESQL_COPIAR_COLAR.txt` - Script PostgreSQL

**📧 Suporte**: suporte@marabet.ao

