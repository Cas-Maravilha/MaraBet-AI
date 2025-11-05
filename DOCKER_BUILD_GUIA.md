# 🐳 DOCKER - GUIA DE BUILD E USO

**Aplicação**: MaraBet AI  
**Ambiente**: Produção AWS

---

## 📋 ARQUIVOS DOCKER

### **1. Dockerfile** - Imagem da aplicação
### **2. docker-compose.production.yml** - Orquestração
### **3. .dockerignore** - Excluir arquivos

---

## 🔨 BUILD

### **Build Local (Teste):**

```bash
# Build simples
docker build -t marabet-web:latest .

# Build com tag específica
docker build -t marabet-web:1.0.0 .

# Build sem cache
docker build --no-cache -t marabet-web:latest .

# Ver imagens
docker images | grep marabet
```

### **Build via Docker Compose:**

```bash
# Build todos os serviços
docker-compose -f docker-compose.production.yml build

# Build serviço específico
docker-compose -f docker-compose.production.yml build web

# Build com pull de imagens base atualizadas
docker-compose -f docker-compose.production.yml build --pull
```

---

## 🚀 RUN

### **Iniciar Aplicação:**

```bash
# Iniciar todos os serviços
docker-compose -f docker-compose.production.yml up -d

# Ver logs
docker-compose -f docker-compose.production.yml logs -f

# Verificar status
docker-compose -f docker-compose.production.yml ps
```

### **Resultado Esperado:**

```
NAME                 COMMAND                  SERVICE   STATUS     PORTS
marabet-web          "gunicorn marabet.ws…"   web       running    0.0.0.0:8000->8000/tcp
marabet-celery       "celery -A marabet w…"   celery    running    
marabet-celery-beat  "celery -A marabet b…"   celery-beat running
```

---

## 🧪 TESTAR

### **A. Health Check:**

```bash
# Do host
curl http://localhost:8000/health

# Resultado esperado:
# {"status": "ok", "timestamp": "2025-10-27T..."}
```

### **B. Logs:**

```bash
# Ver logs de todos
docker-compose -f docker-compose.production.yml logs

# Seguir logs em tempo real
docker-compose -f docker-compose.production.yml logs -f web

# Últimas 100 linhas
docker-compose -f docker-compose.production.yml logs --tail=100 web
```

### **C. Shell no Container:**

```bash
# Entrar no container
docker-compose -f docker-compose.production.yml exec web bash

# Dentro do container
pwd
ls -la
python --version
pip list

# Testar conexões
nc -zv database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com 5432
nc -zv marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com 6379

# Sair
exit
```

---

## 🔄 ATUALIZAR

### **Deploy Nova Versão:**

```bash
# 1. Atualizar código
cd /opt/marabet
git pull origin main

# 2. Rebuild (se houver mudanças no Dockerfile/requirements)
docker-compose -f docker-compose.production.yml build

# 3. Restart
docker-compose -f docker-compose.production.yml up -d

# 4. Ver logs
docker-compose -f docker-compose.production.yml logs -f --tail=50
```

### **Restart Sem Rebuild:**

```bash
# Restart todos
docker-compose -f docker-compose.production.yml restart

# Restart apenas web
docker-compose -f docker-compose.production.yml restart web
```

---

## 🗑️ LIMPEZA

### **Parar e Remover:**

```bash
# Parar todos
docker-compose -f docker-compose.production.yml down

# Parar e remover volumes (⚠️ perde dados)
docker-compose -f docker-compose.production.yml down -v

# Remover imagens antigas
docker image prune -a
```

---

## 📊 MONITORAMENTO

### **Recursos:**

```bash
# Ver uso de CPU/RAM
docker stats

# Ver uso de um container
docker stats marabet-web

# Top processes
docker-compose -f docker-compose.production.yml top
```

### **Logs:**

```bash
# Nginx access log (do host)
sudo tail -f /var/log/nginx/marabet-access.log

# Logs da aplicação
docker-compose -f docker-compose.production.yml logs -f web

# Logs do Celery
docker-compose -f docker-compose.production.yml logs -f celery
```

---

## 🔧 COMANDOS ÚTEIS

### **Executar Comandos:**

```bash
# Django migrate
docker-compose -f docker-compose.production.yml exec web python manage.py migrate

# Django createsuperuser
docker-compose -f docker-compose.production.yml exec web python manage.py createsuperuser

# Collectstatic
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput

# Shell Python
docker-compose -f docker-compose.production.yml exec web python manage.py shell

# Qualquer comando
docker-compose -f docker-compose.production.yml exec web python [comando]
```

---

## ✅ CHECKLIST

- [ ] Dockerfile criado
- [ ] docker-compose.production.yml criado
- [ ] .env configurado
- [ ] requirements.txt atualizado
- [ ] Build executado
- [ ] Imagem criada
- [ ] Containers iniciados
- [ ] Health check OK
- [ ] Logs sem erros
- [ ] Aplicação respondendo
- [ ] Conexão RDS OK
- [ ] Conexão Redis OK
- [ ] Nginx proxy funcionando
- [ ] HTTPS ativo

---

**🐳 Docker Pronto!**  
**✅ Produção-Ready**  
**🚀 marabet.com**

