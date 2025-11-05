# 🚀 BUILD E DEPLOY EM PRODUÇÃO - MARABET.COM

**Executar na EC2 AWS**  
**Usuário**: marabet  
**Diretório**: /opt/marabet

---

## 📋 SEQUÊNCIA COMPLETA

### **1. Conectar à EC2:**

```bash
# Do seu PC
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Trocar para usuário marabet
sudo su - marabet

# Ir para diretório
cd /opt/marabet
```

---

### **2. Verificar Arquivos:**

```bash
# Verificar se todos os arquivos estão presentes
ls -la

# Arquivos essenciais:
# ✓ Dockerfile
# ✓ docker-compose.yml ou docker-compose.production.yml
# ✓ requirements.txt
# ✓ .env
# ✓ app.py ou manage.py
```

---

### **3. Build da Imagem:**

```bash
# Se usar docker-compose.yml
docker-compose build

# Se usar docker-compose.production.yml
docker-compose -f docker-compose.production.yml build

# Build com output verboso
docker-compose -f docker-compose.production.yml build --progress=plain

# Build sem cache (limpo)
docker-compose -f docker-compose.production.yml build --no-cache
```

**Tempo estimado**: 2-5 minutos

**Resultado esperado:**
```
Building web
[+] Building 145.2s (15/15) FINISHED
 => [internal] load build definition
 => => transferring dockerfile
 => [internal] load .dockerignore
 => [internal] load metadata for docker.io/library/python:3.11-slim
 ...
 => => writing image sha256:xxxxx
 => => naming to docker.io/library/marabet-web:latest
```

---

### **4. Iniciar Serviços:**

```bash
# Iniciar em background (detached)
docker-compose up -d

# Ou com arquivo específico
docker-compose -f docker-compose.production.yml up -d

# Iniciar com build (rebuild + start)
docker-compose up -d --build
```

**Resultado esperado:**
```
Creating network "marabet_marabet-network" ... done
Creating marabet-celery ... done
Creating marabet-celery-beat ... done
Creating marabet-web ... done
```

---

### **5. Verificar Logs:**

```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs apenas do web
docker-compose logs -f web

# Últimas 100 linhas
docker-compose logs --tail=100 web

# Logs sem seguir
docker-compose logs web
```

**Logs esperados (sem erros):**
```
marabet-web | [2025-10-27 12:00:00 +0000] [1] [INFO] Starting gunicorn 20.1.0
marabet-web | [2025-10-27 12:00:00 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
marabet-web | [2025-10-27 12:00:00 +0000] [1] [INFO] Using worker: sync
marabet-web | [2025-10-27 12:00:00 +0000] [8] [INFO] Booting worker with pid: 8
marabet-celery | [2025-10-27 12:00:01 +0000] [INFO] celery@xxx ready
```

---

### **6. Verificar Status:**

```bash
# Status dos containers
docker-compose ps

# Resultado esperado:
# NAME                 COMMAND             STATUS         PORTS
# marabet-web          "gunicorn..."       Up (healthy)   0.0.0.0:8000->8000/tcp
# marabet-celery       "celery -A..."      Up             
# marabet-celery-beat  "celery -A..."      Up
```

```bash
# Status detalhado
docker ps

# Recursos (CPU/RAM)
docker stats
```

---

### **7. Testar Aplicação:**

```bash
# Testar health check
curl http://localhost:8000/health

# Resultado esperado:
# {"status":"ok","timestamp":"2025-10-27T..."}

# Testar endpoint principal
curl http://localhost:8000/

# Testar API
curl http://localhost:8000/api/status
```

---

### **8. Executar Migrações (Se Necessário):**

```bash
# Django
docker-compose exec web python manage.py migrate

# Criar superuser
docker-compose exec web python manage.py createsuperuser

# Collectstatic
docker-compose exec web python manage.py collectstatic --noinput

# Seed data
docker-compose exec web python seed_data.py
```

---

### **9. Verificar Conexões:**

```bash
# Entrar no container
docker-compose exec web bash

# Testar RDS
nc -zv database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com 5432
# Resultado: Connection to database-1... succeeded!

# Testar Redis
nc -zv marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com 6379
# Resultado: Connection to marabet-redis... succeeded!

# Ou via Python
python -c "
from db_config import test_connection
test_connection()
"

# Sair
exit
```

---

### **10. Verificar do PC:**

```bash
# Do seu PC
curl http://[ELASTIC_IP]:8000/health

# Com domínio (após Nginx configurado)
curl http://marabet.com/health

# HTTPS (após SSL)
curl https://marabet.com/health
```

---

## 🔄 COMANDOS OPERACIONAIS

### **Restart:**

```bash
# Restart todos
docker-compose restart

# Restart apenas web
docker-compose restart web

# Restart com rebuild
docker-compose up -d --build
```

### **Stop:**

```bash
# Parar todos
docker-compose stop

# Parar específico
docker-compose stop web
```

### **Start:**

```bash
# Iniciar todos
docker-compose start

# Iniciar específico
docker-compose start web
```

### **Down (Parar e Remover):**

```bash
# Parar e remover containers
docker-compose down

# Parar, remover containers e volumes
docker-compose down -v
```

---

## 📊 MONITORAMENTO

### **Ver Recursos:**

```bash
# CPU, RAM, Network, Disk
docker stats

# Apenas MaraBet containers
docker stats marabet-web marabet-celery marabet-celery-beat
```

### **Inspecionar Container:**

```bash
# Ver configuração completa
docker inspect marabet-web

# Ver apenas health
docker inspect marabet-web | jq '.[0].State.Health'

# Ver volumes
docker inspect marabet-web | jq '.[0].Mounts'
```

---

## 🔧 TROUBLESHOOTING

### **Container não inicia:**

```bash
# Ver logs detalhados
docker-compose logs web

# Ver últimos eventos
docker events --filter container=marabet-web

# Tentar iniciar em foreground
docker-compose up web
```

### **Erro "Port already in use":**

```bash
# Ver o que está usando porta 8000
sudo lsof -i :8000

# Parar processo
sudo kill <PID>

# Ou mudar porta no docker-compose.yml
# ports: - "8001:8000"
```

### **Erro "Build failed":**

```bash
# Build com output completo
docker-compose build --progress=plain

# Build sem cache
docker-compose build --no-cache

# Verificar Dockerfile
cat Dockerfile
```

### **Aplicação não conecta ao RDS/Redis:**

```bash
# Verificar .env
cat .env | grep DATABASE_URL
cat .env | grep REDIS_URL

# Testar do container
docker-compose exec web nc -zv database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com 5432

# Verificar Security Groups
```

---

## 📝 SCRIPT COMPLETO

### **Criar: `deploy-docker.sh`**

```bash
#!/bin/bash

echo "🚀 MaraBet AI - Build e Deploy"
echo "=============================="
echo ""

cd /opt/marabet

# 1. Build
echo "1. Building imagem..."
docker-compose -f docker-compose.production.yml build

# 2. Start
echo ""
echo "2. Iniciando serviços..."
docker-compose -f docker-compose.production.yml up -d

# 3. Aguardar
echo ""
echo "3. Aguardando serviços iniciarem..."
sleep 10

# 4. Status
echo ""
echo "4. Status dos containers:"
docker-compose -f docker-compose.production.yml ps

# 5. Logs
echo ""
echo "5. Últimas linhas dos logs:"
docker-compose -f docker-compose.production.yml logs --tail=20

# 6. Health
echo ""
echo "6. Testando health check..."
curl -s http://localhost:8000/health

echo ""
echo "✅ Deploy completo!"
echo ""
echo "Ver logs: docker-compose -f docker-compose.production.yml logs -f"
```

---

## ✅ CHECKLIST FINAL

- [ ] Código na EC2 (/opt/marabet)
- [ ] .env configurado
- [ ] Dockerfile presente
- [ ] docker-compose.production.yml presente
- [ ] requirements.txt presente
- [ ] Build executado: `docker-compose build`
- [ ] Containers iniciados: `docker-compose up -d`
- [ ] Logs verificados: sem erros
- [ ] Health check: OK
- [ ] Web acessível: localhost:8000
- [ ] RDS conectado
- [ ] Redis conectado
- [ ] Nginx proxy OK
- [ ] HTTPS funcionando
- [ ] Aplicação totalmente funcional

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Build e deploy completos
2. **Testar**: https://marabet.com
3. **Monitorar**: Logs e métricas
4. **Backup**: Configurar backup automático
5. **Monitoramento**: CloudWatch

---

**🐳 Docker Build e Deploy Completo!**  
**✅ MaraBet AI Rodando em Produção**  
**🌐 https://marabet.com**  
**☁️ Powered by AWS + Docker**
