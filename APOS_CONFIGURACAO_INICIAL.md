# ✅ APÓS CONFIGURAÇÃO INICIAL - PRÓXIMOS PASSOS

**Status**: Firewall e diretórios configurados ✅  
**Próximo**: Instalar serviços e enviar código

---

## ✅ O QUE JÁ FOI FEITO

```bash
✅ Usuário marabet no grupo docker
✅ Diretório /opt/marabet criado
✅ Firewall configurado (UFW)
✅ Portas permitidas: 22, 80, 443
✅ PostgreSQL bloqueado externamente (porta 5432)
```

---

## 📋 PRÓXIMOS COMANDOS (SEQUÊNCIA)

### **1. Verificar Status Atual**

```bash
# Confirmar que está no diretório correto
pwd
# Deve mostrar: /opt/marabet

# Verificar grupos
groups
# Deve mostrar: marabet sudo docker

# Verificar firewall
sudo ufw status
# Deve mostrar: Status: active e regras configuradas
```

### **2. Instalar PostgreSQL 15**

**Primeiro, enviar script do seu PC:**
```powershell
# Do seu PC Windows
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"
scp install_postgresql_secure.sh marabet@37.27.220.67:/tmp/
```

**No servidor:**
```bash
# Dar permissão de execução
chmod +x /tmp/install_postgresql_secure.sh

# Executar instalação (precisa sudo)
sudo /tmp/install_postgresql_secure.sh

# O script irá:
# - Instalar PostgreSQL 15
# - Criar banco 'marabet' e usuário 'marabet_user'
# - Gerar senha forte
# - Configurar segurança
# - Salvar credenciais em /opt/marabet/.env.db

# Ver credenciais geradas
cat /opt/marabet/.env.db
```

### **3. Verificar/Instalar Docker**

```bash
# Verificar se Docker está instalado
docker --version

# Se não estiver instalado:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verificar que pode usar docker sem sudo
docker ps
# Deve retornar lista vazia (sem erros de permissão)
```

### **4. Instalar Docker Compose**

```bash
# Verificar se está instalado
docker-compose --version

# Se não estiver:
sudo apt install -y docker-compose

# Ou via pip (alternativa):
sudo pip3 install docker-compose
```

### **5. Instalar Nginx e Certbot**

```bash
# Instalar Nginx
sudo apt install -y nginx

# Instalar Certbot para SSL
sudo apt install -y certbot python3-certbot-nginx

# Habilitar e iniciar Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Verificar status
sudo systemctl status nginx

# Testar (deve retornar página padrão)
curl http://localhost
```

### **6. Enviar Código da Aplicação**

**Agora, do seu PC Windows:**

```powershell
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"

# Enviar arquivos essenciais primeiro
scp install_postgresql_secure.sh marabet@37.27.220.67:/tmp/
scp docker-compose.production.yml marabet@37.27.220.67:/opt/marabet/
scp config_production.env marabet@37.27.220.67:/opt/marabet/
scp app.py marabet@37.27.220.67:/opt/marabet/
scp Dockerfile marabet@37.27.220.67:/opt/marabet/
scp requirements.txt marabet@37.27.220.67:/opt/marabet/  # Se houver

# Enviar diretórios importantes
scp -r api/ marabet@37.27.220.67:/opt/marabet/
scp -r models/ marabet@37.27.220.67:/opt/marabet/
scp -r migrations/ marabet@37.27.220.67:/opt/marabet/
scp -r static/ marabet@37.27.220.67:/opt/marabet/
scp -r templates/ marabet@37.27.220.67:/opt/marabet/

# OU enviar tudo de uma vez (pode demorar alguns minutos):
scp -r * marabet@37.27.220.67:/opt/marabet/
```

### **7. Verificar Arquivos Enviados**

**Voltar ao servidor e verificar:**

```bash
cd /opt/marabet
ls -la

# Deve mostrar os arquivos enviados:
# - docker-compose.production.yml
# - config_production.env
# - app.py
# - Dockerfile
# - api/
# - models/
# - migrations/
# - static/
# - templates/
```

### **8. Configurar Variáveis de Ambiente**

```bash
cd /opt/marabet

# Copiar configuração
cp config_production.env .env

# Editar .env
nano .env
# ou
vim .env
```

**Editar o arquivo .env:**

```bash
# PostgreSQL (usar credenciais do /opt/marabet/.env.db)
# Exemplo do conteúdo gerado:
# DATABASE_URL=postgresql://marabet_user:SENHA@localhost:5432/marabet

# Copiar DATABASE_URL do arquivo gerado:
cat /opt/marabet/.env.db
# Copiar a linha DATABASE_URL e colar no .env

# Redis
REDIS_URL=redis://localhost:6379

# API-Football (VERIFICAR se IP foi adicionado no dashboard!)
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

### **9. Instalar Dependências Python (se necessário)**

```bash
cd /opt/marabet

# Se houver requirements.txt:
sudo apt install -y python3-pip
pip3 install -r requirements.txt

# Ou instalar manualmente:
pip3 install fastapi uvicorn sqlalchemy psycopg2-binary redis celery
```

### **10. Executar Migrações**

```bash
cd /opt/marabet

# Executar migrações do banco
python3 migrate.py --migrate --seed

# Verificar se tabelas foram criadas
psql -h localhost -U marabet_user -d marabet -c "\dt"
```

### **11. Iniciar Aplicação**

```bash
cd /opt/marabet

# Build e iniciar containers
docker-compose -f docker-compose.production.yml up -d --build

# Ver status
docker-compose -f docker-compose.production.yml ps

# Ver logs
docker-compose -f docker-compose.production.yml logs -f

# Em outra sessão, testar:
curl http://localhost:8000/health
```

---

## ✅ CHECKLIST DE VERIFICAÇÃO

Execute para verificar tudo:

```bash
# 1. PostgreSQL
sudo systemctl status postgresql
psql -h localhost -U marabet_user -d marabet -c "SELECT 1;"

# 2. Docker
docker ps
docker-compose --version

# 3. Aplicação
curl http://localhost:8000/health
# Deve retornar: {"status": "ok"} ou similar

# 4. Nginx
sudo systemctl status nginx

# 5. Firewall
sudo ufw status
```

---

## 🐛 TROUBLESHOOTING

### **Erro: Docker precisa sudo**
```bash
# Adicionar ao grupo novamente
sudo usermod -aG docker marabet
newgrp docker
# Ou fazer logout e login novamente
```

### **Erro: PostgreSQL não conecta**
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Verificar credenciais
cat /opt/marabet/.env.db

# Testar conexão manual
psql -h localhost -U marabet_user -d marabet
```

### **Erro: Container não inicia**
```bash
# Ver logs
docker-compose logs web

# Verificar .env
cat .env

# Verificar Dockerfile
cat Dockerfile
```

---

## 📝 RESUMO RÁPIDO

**Ordem de execução:**

1. ✅ Firewall configurado (já feito)
2. ⏳ Instalar PostgreSQL
3. ⏳ Instalar Docker (se necessário)
4. ⏳ Instalar Docker Compose (se necessário)
5. ⏳ Instalar Nginx
6. ⏳ Enviar código do PC
7. ⏳ Configurar .env
8. ⏳ Executar migrações
9. ⏳ Iniciar aplicação

---

**📄 Guias Relacionados:**
- `DEPLOY_EXECUTAR_AGORA.md` - Deploy completo
- `PROXIMOS_PASSOS_POS_INSTALACAO.md` - Detalhes

**📧 Suporte**: suporte@marabet.ao

