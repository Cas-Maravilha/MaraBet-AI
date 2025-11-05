# 🚀 PRÓXIMOS PASSOS APÓS INSTALAÇÃO BÁSICA

**Servidor**: marabet.ao (37.27.220.67)  
**Status**: Instalação básica concluída ✅

---

## ✅ O QUE JÁ FOI FEITO

```bash
✅ Sistema atualizado (apt update && apt upgrade -y)
✅ Utilitários instalados:
   - curl (downloads)
   - wget (downloads)
   - git (controle de versão)
   - ufw (firewall)
   - fail2ban (proteção SSH)
   - htop (monitoramento)
   - vim (editor)
```

---

## 📋 PRÓXIMOS COMANDOS (SEQUÊNCIA COMPLETA)

### **1. Configurar Firewall (UFW)**

```bash
# Habilitar firewall
ufw --force enable

# Permitir portas essenciais
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# Bloquear PostgreSQL externamente (importante!)
ufw deny 5432/tcp

# Verificar status
ufw status verbose
```

### **2. Configurar Fail2Ban (Proteção SSH)**

```bash
# Habilitar fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Ver status
systemctl status fail2ban

# Ver logs (se necessário)
fail2ban-client status sshd
```

### **3. Adicionar Usuário ao Grupo Docker**

```bash
# Adicionar usuário marabet ao grupo docker
sudo usermod -aG docker marabet

# Trocar de grupo (ou fazer logout/login)
newgrp docker

# Verificar
groups
# Deve mostrar: marabet sudo docker
```

### **4. Instalar PostgreSQL 15**

**Do seu PC, enviar script:**
```bash
# Do seu PC Windows
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"
scp install_postgresql_secure.sh marabet@37.27.220.67:/tmp/
```

**No servidor, executar:**
```bash
# Dar permissão de execução
chmod +x /tmp/install_postgresql_secure.sh

# Executar instalação (precisa sudo para criar usuário postgres)
sudo /tmp/install_postgresql_secure.sh

# O script irá:
# - Instalar PostgreSQL 15
# - Criar banco 'marabet' e usuário 'marabet_user'
# - Gerar senha forte automaticamente
# - Configurar segurança (localhost apenas)
# - Salvar credenciais em /opt/marabet/.env.db

# Ver credenciais geradas
cat /opt/marabet/.env.db
```

### **4. Instalar Docker**

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Adicionar usuário ao grupo docker (se necessário)
usermod -aG docker root
newgrp docker  # Ou fazer logout e login novamente

# Verificar instalação
docker --version
docker ps  # Deve retornar lista vazia (sem erros)
```

### **5. Instalar Docker Compose**

```bash
# Instalar Docker Compose
apt install -y docker-compose

# Ou via pip (alternativa)
# pip install docker-compose

# Verificar
docker-compose --version
```

### **6. Instalar Nginx e Certbot**

```bash
# Instalar Nginx
apt install -y nginx

# Instalar Certbot para SSL
apt install -y certbot python3-certbot-nginx

# Habilitar e iniciar Nginx
systemctl enable nginx
systemctl start nginx

# Verificar status
systemctl status nginx

# Testar (deve retornar página padrão do Nginx)
curl http://localhost
```

### **7. Enviar Código da Aplicação**

**Do seu PC (PowerShell/CMD):**
```powershell
# Navegar para o diretório do projeto
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"

# Enviar todos os arquivos (pode demorar alguns minutos)
scp -r * root@37.27.220.67:/opt/marabet/

# Ou enviar arquivo por arquivo se houver problemas:
scp config_production.env root@37.27.220.67:/opt/marabet/
scp docker-compose.production.yml root@37.27.220.67:/opt/marabet/
scp app.py root@37.27.220.67:/opt/marabet/
# ... etc
```

### **8. Configurar Variáveis de Ambiente**

```bash
# No servidor
cd /opt/marabet

# Copiar configuração de produção
cp config_production.env .env

# Editar .env
vim .env
# ou
nano .env
```

**Editar o arquivo .env com:**
```bash
# PostgreSQL (usar credenciais do /opt/marabet/.env.db geradas pelo script)
# Exemplo:
DATABASE_URL=postgresql://marabet_user:SENHA_AQUI@localhost:5432/marabet

# Ou copiar do arquivo gerado:
# cat /opt/marabet/.env.db

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
SECRET_KEY=gerar_uma_chave_secreta_forte_aqui
```

### **9. Executar Migrações do Banco**

```bash
cd /opt/marabet

# Instalar Python e dependências (se necessário)
apt install -y python3 python3-pip
pip3 install -r requirements.txt  # Se houver arquivo requirements.txt

# Executar migrações
python3 migrate.py --migrate --seed

# Verificar se criou as tabelas
psql -h localhost -U marabet_user -d marabet -c "\dt"
```

### **10. Iniciar Aplicação com Docker**

```bash
cd /opt/marabet

# Build e iniciar containers
docker-compose -f docker-compose.production.yml up -d --build

# Ver status dos containers
docker-compose -f docker-compose.production.yml ps

# Ver logs
docker-compose -f docker-compose.production.yml logs -f

# Verificar health check
curl http://localhost:8000/health
```

---

## ✅ VERIFICAÇÕES

### **Verificar Serviços:**

```bash
# PostgreSQL
systemctl status postgresql
psql -h localhost -U marabet_user -d marabet -c "SELECT 1;"

# Redis (se instalado)
systemctl status redis-server
redis-cli ping

# Docker
docker ps
docker-compose ps

# Nginx
systemctl status nginx
nginx -t  # Testar configuração

# Firewall
ufw status
```

---

## 📊 RESUMO RÁPIDO DOS COMANDOS

```bash
# Sequência completa (copie e cole):

# 1. Firewall
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 5432/tcp

# 2. Fail2Ban
systemctl enable fail2ban
systemctl start fail2ban

# 3. PostgreSQL (após enviar script)
chmod +x /tmp/install_postgresql_secure.sh
sudo /tmp/install_postgresql_secure.sh
cat /opt/marabet/.env.db

# 4. Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
docker --version

# 5. Docker Compose
apt install -y docker-compose

# 6. Nginx
apt install -y nginx certbot python3-certbot-nginx
systemctl enable nginx
systemctl start nginx

# 7. Enviar código (do seu PC)
# scp -r * root@37.27.220.67:/opt/marabet/

# 8. Configurar .env
cd /opt/marabet
cp config_production.env .env
vim .env

# 9. Migrações
python3 migrate.py --migrate --seed

# 10. Iniciar aplicação
docker-compose -f docker-compose.production.yml up -d --build
```

---

## ⚠️ CHECKLIST ANTES DE CONTINUAR

- [ ] Firewall configurado (UFW)
- [ ] Fail2Ban ativo
- [ ] PostgreSQL instalado e configurado
- [ ] Docker instalado
- [ ] Docker Compose instalado
- [ ] Nginx instalado
- [ ] Código enviado para /opt/marabet/
- [ ] .env configurado
- [ ] Migrações executadas
- [ ] Containers iniciados

---

**📄 Guia Completo**: `DEPLOY_EXECUTAR_AGORA.md`  
**📧 Suporte**: suporte@marabet.ao

