# 🐳 DOCKER COMPOSE - GUIA DE USO

**Aplicação**: MaraBet AI  
**Ambiente**: Produção Angoweb (Luanda, Angola)  
**Arquivo**: docker-compose.production.yml

---

## 📋 SERVIÇOS

### **1. web** - Aplicação Principal
- Porta: 8000
- Workers: 4 Gunicorn workers
- Health check: /health endpoint
- Restart: always

### **2. celery** - Worker Assíncrono
- Tarefas em background
- Concurrency: 4
- Conecta ao Redis

### **3. celery-beat** - Agendador
- Tarefas agendadas (cron)
- Scheduler: Database
- Executa tarefas periódicas

---

## 🚀 COMANDOS BÁSICOS

### **Iniciar Tudo:**

```bash
# Primeira vez (build + start)
docker-compose -f docker-compose.production.yml up -d --build

# Próximas vezes (start apenas)
docker-compose -f docker-compose.production.yml up -d
```

### **Parar Tudo:**

```bash
docker-compose -f docker-compose.production.yml down
```

### **Restart:**

```bash
# Restart todos os serviços
docker-compose -f docker-compose.production.yml restart

# Restart serviço específico
docker-compose -f docker-compose.production.yml restart web
```

---

## 📊 MONITORAMENTO

### **Ver Logs:**

```bash
# Todos os serviços
docker-compose -f docker-compose.production.yml logs -f

# Serviço específico
docker-compose -f docker-compose.production.yml logs -f web
docker-compose -f docker-compose.production.yml logs -f celery

# Últimas 100 linhas
docker-compose -f docker-compose.production.yml logs --tail=100 web
```

### **Status dos Containers:**

```bash
# Ver status
docker-compose -f docker-compose.production.yml ps

# Ver recursos (CPU, RAM)
docker stats

# Health check
docker-compose -f docker-compose.production.yml ps
```

---

## 🔧 COMANDOS ÚTEIS

### **Executar Comandos no Container:**

```bash
# Shell interativo
docker-compose -f docker-compose.production.yml exec web bash

# Comando único
docker-compose -f docker-compose.production.yml exec web python manage.py migrate

# Como root (se necessário)
docker-compose -f docker-compose.production.yml exec --user root web bash
```

### **Rebuild:**

```bash
# Rebuild todos
docker-compose -f docker-compose.production.yml build

# Rebuild e restart
docker-compose -f docker-compose.production.yml up -d --build

# Rebuild sem cache
docker-compose -f docker-compose.production.yml build --no-cache
```

---

## 📝 MIGRAÇÕES E SETUP

### **Executar Migrações:**

```bash
# Django
docker-compose -f docker-compose.production.yml exec web python manage.py migrate

# Alembic
docker-compose -f docker-compose.production.yml exec web alembic upgrade head

# Custom
docker-compose -f docker-compose.production.yml exec web python migrate.py --migrate
```

### **Criar Superuser:**

```bash
docker-compose -f docker-compose.production.yml exec web python manage.py createsuperuser
```

### **Collectstatic:**

```bash
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput
```

---

## 🔄 ATUALIZAÇÃO E DEPLOY

### **Deploy de Nova Versão:**

```bash
# 1. Atualizar código
cd /opt/marabet
git pull origin main

# 2. Rebuild e restart
docker-compose -f docker-compose.production.yml up -d --build

# 3. Executar migrações (se houver)
docker-compose -f docker-compose.production.yml exec web python manage.py migrate

# 4. Collectstatic (se houver mudanças)
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput

# 5. Verificar logs
docker-compose -f docker-compose.production.yml logs -f --tail=50
```

---

## 🧹 LIMPEZA

### **Remover Containers Parados:**

```bash
docker-compose -f docker-compose.production.yml down --remove-orphans
```

### **Limpar Tudo (Cuidado!):**

```bash
# Remove containers, networks, volumes
docker-compose -f docker-compose.production.yml down -v

# Limpar imagens não usadas
docker image prune -a
```

---

## 📊 TROUBLESHOOTING

### **Container não inicia:**

```bash
# Ver logs detalhados
docker-compose -f docker-compose.production.yml logs web

# Ver eventos
docker events --filter container=marabet-web

# Inspecionar container
docker inspect marabet-web
```

### **Erro de conexão ao PostgreSQL/Redis local:**

```bash
# Testar do container
docker-compose -f docker-compose.production.yml exec web bash

# Dentro do container
# PostgreSQL (localhost)
nc -zv localhost 5432
psql -h localhost -U marabet_user -d marabet_production

# Redis (localhost)
nc -zv localhost 6379
redis-cli ping
```

### **Health check falha:**

```bash
# Ver health status
docker inspect marabet-web | jq '.[0].State.Health'

# Testar health endpoint
curl http://localhost:8000/health
```

---

## ✅ CHECKLIST

- [ ] docker-compose.production.yml criado
- [ ] .env configurado
- [ ] Build executado: `docker-compose build`
- [ ] Containers iniciados: `docker-compose up -d`
- [ ] Web container: healthy
- [ ] Celery worker: running
- [ ] Celery beat: running
- [ ] Logs sem erros
- [ ] Health check OK
- [ ] Aplicação acessível na porta 8000

---

**🐳 Docker Compose Configurado!**  
**✅ 3 Serviços Rodando**  
**🚀 MaraBet AI em Produção**

