# 🗄️ EXECUTAR MIGRAÇÕES - GUIA COMPLETO

**Banco de Dados**: RDS PostgreSQL  
**Aplicação**: MaraBet AI  
**Ambiente**: Produção AWS

---

## 📋 MÉTODOS DE MIGRAÇÃO

1. [Com Virtual Environment](#método-1-com-virtual-environment)
2. [Com Docker](#método-2-com-docker-recomendado)
3. [Direto no Sistema](#método-3-direto-no-sistema)

---

## MÉTODO 1: COM VIRTUAL ENVIRONMENT

### **Executar na EC2:**

```bash
# SSH na EC2
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Trocar para usuário marabet
sudo su - marabet

# Ir para diretório
cd /opt/marabet
```

### **1. Criar Virtual Environment:**

```bash
# Criar venv
python3 -m venv venv

# Ativar
source venv/bin/activate

# Verificar
which python
# Resultado: /opt/marabet/venv/bin/python
```

### **2. Instalar Dependências:**

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar requirements
pip install -r requirements.txt

# Verificar instalação
pip list
```

### **3. Executar Migrações:**

```bash
# Se tiver script migrate.py
python migrate.py --migrate --seed

# Ou se for Django
python manage.py migrate

# Ou se for Flask com Alembic
alembic upgrade head

# Ou se for custom
python -m marabet.migrations migrate
```

### **4. Seed Data (Dados Iniciais):**

```bash
# Se tiver script de seed
python migrate.py --seed

# Ou Django
python manage.py loaddata initial_data.json

# Ou custom
python seed_data.py
```

---

## MÉTODO 2: COM DOCKER (Recomendado)

### **Executar na EC2:**

```bash
# SSH na EC2
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Trocar para usuário marabet
sudo su - marabet
cd /opt/marabet
```

### **1. Executar Migrações no Container:**

```bash
# Aplicação já deve estar rodando
docker-compose ps

# Executar migrações dentro do container
docker-compose exec app python migrate.py --migrate --seed

# Ou Django
docker-compose exec app python manage.py migrate

# Ou Alembic
docker-compose exec app alembic upgrade head
```

### **2. Seed Data no Container:**

```bash
# Seed
docker-compose exec app python migrate.py --seed

# Ou
docker-compose exec app python manage.py loaddata initial_data.json

# Ou
docker-compose exec app python seed_data.py
```

### **3. Criar Superuser (Django):**

```bash
docker-compose exec app python manage.py createsuperuser

# Preencher:
# Username: admin
# Email: admin@marabet.com
# Password: [SENHA_FORTE]
```

### **4. Collectstatic (Django):**

```bash
docker-compose exec app python manage.py collectstatic --noinput
```

---

## MÉTODO 3: DIRETO NO SISTEMA

### **Sem Virtual Environment:**

```bash
# Instalar dependências globalmente
sudo pip3 install -r requirements.txt

# Executar migrações
python3 migrate.py --migrate --seed

# Ou
sudo -u marabet python3 /opt/marabet/migrate.py --migrate --seed
```

---

## 🗄️ CRIAR DATABASE (Se Ainda Não Criou)

### **Conectar ao RDS:**

```bash
# Na EC2
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d postgres

# Password: GuF#Y(!j38Bgw|YyT<r0J5>yxD3n
```

### **Criar Database:**

```sql
-- Criar database
CREATE DATABASE marabet_production;

-- Ver databases
\l

-- Conectar
\c marabet_production

-- Verificar que está vazio
\dt

-- Sair
\q
```

---

## 📊 VERIFICAR MIGRAÇÕES

### **A. Ver Tabelas Criadas:**

```bash
# Conectar ao database
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d marabet_production

# Listar tabelas
\dt

# Ver schema de uma tabela
\d users

# Contar registros
SELECT COUNT(*) FROM users;

# Sair
\q
```

### **B. Via Python:**

```bash
# Entrar no shell Python
docker-compose exec app python manage.py shell

# Ou
python -c "
from db_config import get_credentials
import psycopg2

creds = get_credentials()
conn = psycopg2.connect(**creds)
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM pg_tables WHERE schemaname = \'public\'')
print(f'Tabelas criadas: {cursor.fetchone()[0]}')

conn.close()
"
```

---

## 🔧 TROUBLESHOOTING

### **Erro: "Database does not exist"**

```bash
# Criar database
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d postgres \
     -c "CREATE DATABASE marabet_production;"
```

### **Erro: "Permission denied"**

```bash
# Verificar permissões do usuário
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d marabet_production \
     -c "\du"

# Grant permissions se necessário
GRANT ALL PRIVILEGES ON DATABASE marabet_production TO marabet_admin;
```

### **Erro: "Connection refused"**

```bash
# Verificar Security Group permite conexão da EC2
aws ec2 describe-security-groups \
  --group-ids sg-09f7d3d37a8407f43 \
  --region eu-west-1

# Testar conectividade
nc -zv database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com 5432
```

### **Erro: "Module not found"**

```bash
# Verificar se requirements foi instalado
pip list

# Reinstalar
pip install -r requirements.txt

# Ou no Docker
docker-compose exec app pip install -r requirements.txt
```

---

## 📝 SCRIPT DE MIGRAÇÃO COMPLETO

### **Criar: `executar_migracoes.sh`**

```bash
#!/bin/bash

echo "🗄️  MaraBet AI - Executar Migrações"
echo "===================================="
echo ""

cd /opt/marabet

# 1. Criar venv se não existir
if [ ! -d "venv" ]; then
    echo "Criando virtual environment..."
    python3 -m venv venv
fi

# 2. Ativar venv
source venv/bin/activate

# 3. Instalar/atualizar dependências
echo "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Executar migrações
echo ""
echo "Executando migrações..."

if [ -f "migrate.py" ]; then
    python migrate.py --migrate --seed
elif [ -f "manage.py" ]; then
    python manage.py migrate
    python manage.py loaddata initial_data.json 2>/dev/null || true
elif [ -f "alembic.ini" ]; then
    alembic upgrade head
else
    echo "⚠️  Script de migração não encontrado"
fi

# 5. Collectstatic (se Django)
if [ -f "manage.py" ]; then
    echo ""
    echo "Coletando static files..."
    python manage.py collectstatic --noinput
fi

echo ""
echo "✅ Migrações completas!"

# Desativar venv
deactivate
```

---

## ✅ CHECKLIST

- [ ] Database `marabet_production` criada no RDS
- [ ] Conexão ao RDS testada
- [ ] Virtual environment criado
- [ ] requirements.txt instalado
- [ ] Migrações executadas
- [ ] Seed data carregado (se aplicável)
- [ ] Superuser criado (se Django)
- [ ] Static files coletados (se Django)
- [ ] Tabelas verificadas no database
- [ ] Dados de teste inseridos
- [ ] Logs sem erros

---

## 📞 COMANDOS RÁPIDOS

```bash
# Ativar venv
source /opt/marabet/venv/bin/activate

# Migrar
python migrate.py --migrate --seed

# Django
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# Alembic
alembic upgrade head

# Verificar database
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com -p 5432 -U marabet_admin -d marabet_production
\dt
\q
```

---

**🗄️ Migrações Completas!**  
**✅ Database Pronto**  
**🚀 Aplicação Pronta para Rodar**  
**☁️ MaraBet.com na AWS**

