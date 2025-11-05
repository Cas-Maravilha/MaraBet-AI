# ✅ APÓS VERIFICAR DOCKER - PRÓXIMOS PASSOS

**Status**: Docker instalado ✅  
**Versões verificadas**: `docker --version` e `docker compose version`

---

## ✅ O QUE DEVE TER FUNCIONADO

### **Resultados esperados:**

```bash
docker --version
# Deve mostrar: Docker version 24.x.x ou superior

docker compose version
# Deve mostrar: Docker Compose version v2.x.x

docker ps
# Deve retornar lista vazia (sem erros de permissão)
```

**Se todos retornaram sem erros = ✅ Docker funcionando!**

---

## 📋 PRÓXIMOS PASSOS IMEDIATOS

### **1. Testar Docker Completo**

```bash
# Testar execução de container
docker run hello-world

# Se funcionar, mostrará:
# Hello from Docker!
# ...
```

### **2. Criar e Executar Script PostgreSQL**

**Opção A: Criar manualmente no servidor**

```bash
# Criar arquivo
sudo nano /tmp/install_postgresql_secure.sh

# Copiar conteúdo do arquivo SCRIPT_POSTGRESQL_COPIAR_COLAR.txt
# (do seu PC para o servidor via nano)

# Salvar: Ctrl+O, Enter, Ctrl+X
# Dar permissão:
chmod +x /tmp/install_postgresql_secure.sh
```

**Opção B: Tentar SCP novamente**

```powershell
# Do seu PC
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"
scp install_postgresql_secure.sh marabet@37.27.220.67:/tmp/
```

**Executar:**
```bash
sudo /tmp/install_postgresql_secure.sh

# Ver credenciais geradas
cat /opt/marabet/.env.db
```

### **3. Instalar Redis (se necessário)**

```bash
# Verificar se Redis está instalado
redis-cli ping

# Se não estiver:
sudo apt install -y redis-server

# Iniciar e habilitar
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Testar
redis-cli ping
# Deve retornar: PONG
```

### **4. Instalar Nginx**

```bash
# Instalar Nginx e Certbot
sudo apt install -y nginx certbot python3-certbot-nginx

# Habilitar e iniciar
sudo systemctl enable nginx
sudo systemctl start nginx

# Verificar
sudo systemctl status nginx

# Testar (deve retornar página padrão)
curl http://localhost
```

### **5. Preparar Diretório da Aplicação**

```bash
# Garantir que diretório existe e tem permissão
cd /opt/marabet
sudo chown -R marabet:marabet /opt/marabet

# Criar diretórios necessários
mkdir -p backups logs static media
```

---

## 📤 ENVIAR CÓDIGO DA APLICAÇÃO

**Do seu PC Windows:**

```powershell
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"

# Enviar arquivos essenciais primeiro
scp docker-compose.production.yml marabet@37.27.220.67:/opt/marabet/
scp config_production.env marabet@37.27.220.67:/opt/marabet/
scp app.py marabet@37.27.220.67:/opt/marabet/
scp Dockerfile marabet@37.27.220.67:/opt/marabet/
scp requirements.txt marabet@37.27.220.67:/opt/marabet/  # Se existir

# Enviar diretórios
scp -r api/ marabet@37.27.220.67:/opt/marabet/
scp -r models/ marabet@37.27.220.67:/opt/marabet/
scp -r migrations/ marabet@37.27.220.67:/opt/marabet/
scp -r static/ marabet@37.27.220.67:/opt/marabet/
scp -r templates/ marabet@37.27.220.67:/opt/marabet/
scp -r config/ marabet@37.27.220.67:/opt/marabet/  # Se existir

# OU enviar tudo de uma vez (pode demorar alguns minutos):
scp -r * marabet@37.27.220.67:/opt/marabet/
```

---

## ✅ CHECKLIST DE STATUS

### **Concluído:**
- [x] SSH configurado
- [x] Firewall configurado
- [x] Docker instalado e verificado
- [ ] PostgreSQL instalado
- [ ] Redis instalado
- [ ] Nginx instalado
- [ ] Código enviado
- [ ] .env configurado
- [ ] Migrações executadas
- [ ] Aplicação iniciada

---

## 🚀 ORDEM DE EXECUÇÃO

**Após verificar Docker:**

1. ✅ Docker funcionando
2. ⏳ Criar/executar script PostgreSQL
3. ⏳ Instalar Redis (se necessário)
4. ⏳ Instalar Nginx
5. ⏳ Enviar código do PC
6. ⏳ Configurar .env
7. ⏳ Executar migrações
8. ⏳ Iniciar aplicação

---

## 📝 RESUMO RÁPIDO DOS COMANDOS

```bash
# Testar Docker
docker run hello-world

# Criar script PostgreSQL (manual)
sudo nano /tmp/install_postgresql_secure.sh
# (colar conteúdo)

# Executar PostgreSQL
chmod +x /tmp/install_postgresql_secure.sh
sudo /tmp/install_postgresql_secure.sh

# Instalar Redis
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Instalar Nginx
sudo apt install -y nginx certbot python3-certbot-nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

---

**📄 Guias Relacionados:**
- `DEPLOY_SEQUENCIA_COMPLETA.md` - Sequência completa
- `INSTALAR_DOCKER_OFICIAL.md` - Instalação Docker

**📧 Suporte**: suporte@marabet.ao

