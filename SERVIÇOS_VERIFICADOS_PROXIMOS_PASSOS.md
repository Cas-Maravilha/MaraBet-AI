# ✅ SERVIÇOS VERIFICADOS - PRÓXIMOS PASSOS CRÍTICOS

**Status**: Redis e Nginx verificados ✅  
**Próximo**: Instalar PostgreSQL e enviar código

---

## ✅ CONFIRMADO

```
✅ Redis: PONG retornado = funcionando
✅ Nginx: HTML retornado = funcionando
✅ Docker: hello-world executado = funcionando
```

---

## 📋 PRÓXIMOS PASSOS NA ORDEM

### **1. INSTALAR POSTGRESQL 15** ⚠️ CRÍTICO

**Criar script no servidor:**

```bash
# No servidor, criar arquivo
sudo nano /tmp/install_postgresql_secure.sh

# IMPORTANTE: Copiar TODO o conteúdo de:
# SCRIPT_POSTGRESQL_COPIAR_COLAR.txt (do seu PC)
# E colar no nano do servidor

# Salvar: Ctrl+O, Enter, Ctrl+X

# Dar permissão
chmod +x /tmp/install_postgresql_secure.sh

# Executar
sudo /tmp/install_postgresql_secure.sh

# O script irá automaticamente:
# ✅ Instalar PostgreSQL 15
# ✅ Criar banco 'marabet'
# ✅ Criar usuário 'marabet_user'
# ✅ Gerar senha forte
# ✅ Configurar segurança
# ✅ Salvar credenciais em /opt/marabet/.env.db

# Ver credenciais IMPORTANTES:
cat /opt/marabet/.env.db

# Anotar a linha DATABASE_URL (você vai precisar!)
```

### **2. VERIFICAR POSTGRESQL**

```bash
# Verificar status
sudo systemctl status postgresql

# Testar conexão
psql -h localhost -U marabet_user -d marabet -c "SELECT 1;"

# Ver banco
psql -h localhost -U marabet_user -d marabet -c "\l"
```

### **3. PREPARAR DIRETÓRIO**

```bash
# Ir para diretório
cd /opt/marabet

# Garantir permissões
sudo chown -R marabet:marabet /opt/marabet

# Criar diretórios necessários
mkdir -p backups logs static media

# Verificar
pwd
# Deve mostrar: /opt/marabet
```

---

## 📤 ENVIAR CÓDIGO DA APLICAÇÃO

### **Do seu PC Windows:**

```powershell
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"

# Opção 1: Enviar tudo de uma vez (pode demorar alguns minutos)
scp -r * marabet@37.27.220.67:/opt/marabet/

# Opção 2: Enviar arquivo por arquivo se houver problemas
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
scp -r config/ marabet@37.27.220.67:/opt/marabet/  # Se existir
```

### **Verificar no Servidor:**

```bash
# No servidor, verificar arquivos
cd /opt/marabet
ls -la

# Deve mostrar todos os arquivos enviados
```

---

## ⚙️ CONFIGURAR .env

### **1. Copiar e Editar**

```bash
cd /opt/marabet

# Copiar configuração
cp config_production.env .env

# Ver credenciais PostgreSQL geradas
cat /opt/marabet/.env.db

# IMPORTANTE: Copiar a linha DATABASE_URL completa!
# Exemplo:
# DATABASE_URL=postgresql://marabet_user:ABC123XYZ@localhost:5432/marabet

# Editar .env
nano .env
```

### **2. Configurar .env com:**

```bash
# PostgreSQL - COPIAR do /opt/marabet/.env.db
DATABASE_URL=postgresql://marabet_user:SENHA_DA_LINHA_ACIMA@localhost:5432/marabet

# Redis
REDIS_URL=redis://localhost:6379

# API-Football (VERIFICAR: IP 37.27.220.67 adicionado no dashboard?)
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Telegram
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597

# Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,37.27.220.67,marabet.ao,www.marabet.ao

# Sistema
SYSTEM_IP=37.27.220.67
DEBUG=False
SECRET_KEY=gerar_com_openssl_rand_base64_32
```

### **3. Gerar SECRET_KEY (se necessário)**

```bash
# Gerar chave secreta forte
openssl rand -base64 32

# Copiar resultado e colar no .env como SECRET_KEY
```

---

## 🔧 EXECUTAR MIGRAÇÕES

```bash
cd /opt/marabet

# Instalar dependências Python
sudo apt install -y python3-pip
pip3 install sqlalchemy psycopg2-binary

# Executar migrações
python3 migrate.py --migrate --seed

# Verificar tabelas criadas
psql -h localhost -U marabet_user -d marabet -c "\dt"

# Deve mostrar lista de tabelas:
# users
# predictions
# bets
# bankroll
# etc.
```

---

## 🚀 INICIAR APLICAÇÃO

### **1. Build e Iniciar**

```bash
cd /opt/marabet

# Build e iniciar
docker compose -f docker-compose.production.yml up -d --build

# Aguardar alguns minutos para build

# Ver status
docker compose ps

# Deve mostrar:
# NAME                STATUS
# marabet-web         Up
# marabet-celery      Up
# marabet-celery-beat Up
```

### **2. Ver Logs**

```bash
# Ver logs de todos
docker compose logs -f

# Ver logs específicos
docker compose logs -f web
docker compose logs -f celery

# Ver últimas 100 linhas
docker compose logs --tail=100
```

### **3. Testar**

```bash
# Health check
curl http://localhost:8000/health

# Deve retornar JSON: {"status": "ok"} ou similar

# Se não funcionar, ver logs:
docker compose logs web | tail -50
```

---

## ✅ CHECKLIST FINAL ANTES DE INICIAR

- [ ] PostgreSQL instalado
- [ ] Credenciais copiadas do /opt/marabet/.env.db
- [ ] Código enviado para /opt/marabet/
- [ ] .env configurado com DATABASE_URL correto
- [ ] SECRET_KEY gerado
- [ ] Migrações executadas
- [ ] Tabelas criadas (verificado com \dt)
- [ ] IP 37.27.220.67 adicionado na API-Football whitelist

---

## 🎯 RESUMO RÁPIDO - PRÓXIMOS COMANDOS

```bash
# 1. Criar script PostgreSQL
sudo nano /tmp/install_postgresql_secure.sh
# (colar conteúdo do SCRIPT_POSTGRESQL_COPIAR_COLAR.txt)

# 2. Executar PostgreSQL
chmod +x /tmp/install_postgresql_secure.sh
sudo /tmp/install_postgresql_secure.sh
cat /opt/marabet/.env.db

# 3. Preparar diretório
cd /opt/marabet
sudo chown -R marabet:marabet /opt/marabet

# 4. Enviar código (do PC)
# scp -r * marabet@37.27.220.67:/opt/marabet/

# 5. Configurar .env
cp config_production.env .env
nano .env  # Colar DATABASE_URL do .env.db

# 6. Migrações
python3 migrate.py --migrate --seed

# 7. Iniciar aplicação
docker compose -f docker-compose.production.yml up -d --build
```

---

## ⚠️ IMPORTANTE ANTES DE CONTINUAR

### **1. Adicionar IP na API-Football**

⚠️ **CRÍTICO**: Antes de iniciar aplicação, adicionar IP no dashboard:

```
Dashboard: https://dashboard.api-football.com/
IP: 37.27.220.67
Description: MaraBet AI - Production Server
```

### **2. Verificar Credenciais PostgreSQL**

Após executar script, **ANOTAR** a linha DATABASE_URL de `/opt/marabet/.env.db` - você vai precisar no `.env`!

---

**📄 Guias Relacionados:**
- `DOCKER_FUNCIONANDO_PROXIMOS_PASSOS.md` - Passos completos
- `SCRIPT_POSTGRESQL_COPIAR_COLAR.txt` - Script para copiar

**📧 Suporte**: suporte@marabet.ao

