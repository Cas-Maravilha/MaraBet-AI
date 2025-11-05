# 🔧 Guia: Recriar Usuário e Database do Zero

## 📋 Objetivo

Recriar completamente o usuário `meu_usuario` e database `meu_banco` no PostgreSQL para resolver problemas de autenticação.

---

## 🚀 Passo a Passo Completo

### **1. Conectar ao PostgreSQL como Superusuário:**

```bash
# No servidor PostgreSQL
sudo -u postgres psql
```

### **2. Executar Script SQL:**

**Opção A: Executar script completo (Recomendado)**

```bash
# Copiar script para o servidor
scp recriar_usuario_database.sql usuario@37.27.220.67:/tmp/

# Conectar ao servidor
ssh usuario@37.27.220.67

# Executar script
sudo -u postgres psql -f /tmp/recriar_usuario_database.sql
```

**Opção B: Executar comandos diretamente no psql**

```sql
-- 1. Remover usuário e database existentes
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'meu_banco' AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS meu_banco;
DROP USER IF EXISTS meu_usuario;

-- 2. Criar usuário do zero
CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';

-- 3. Criar database do zero
CREATE DATABASE meu_banco OWNER meu_usuario;

-- 4. Conceder permissões no database
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;

-- 5. Conectar ao database e conceder permissões no schema
\c meu_banco

GRANT ALL ON SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO meu_usuario;

-- 6. Verificar configuração
\c postgres

SELECT usename FROM pg_user WHERE usename = 'meu_usuario';
SELECT datname FROM pg_database WHERE datname = 'meu_banco';

-- 7. Testar conexão com o novo usuário
\c meu_banco meu_usuario

SELECT current_database(), current_user;
```

### **3. Verificar pg_hba.conf:**

```bash
# No servidor
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario
```

**Deve mostrar:**
```
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

**Se não tiver, adicionar:**
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Adicionar linha:
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256

# Salvar e reiniciar PostgreSQL
sudo systemctl restart postgresql
```

### **4. Reiniciar PostgreSQL:**

```bash
sudo systemctl restart postgresql
sudo systemctl status postgresql
```

### **5. Testar Conexão:**

**No servidor:**
```bash
# Testar localmente
psql -h localhost -U meu_usuario -d meu_banco
```

**De sua máquina:**
```bash
# Testar remotamente
python testar_conexao.py
```

---

## 📝 Script SQL Completo

Veja o arquivo `recriar_usuario_database.sql` para o script completo que faz tudo automaticamente.

---

## ✅ Verificação Final

Após executar o script, verifique:

1. **Usuário foi criado:**
   ```sql
   SELECT usename FROM pg_user WHERE usename = 'meu_usuario';
   ```

2. **Database foi criado:**
   ```sql
   SELECT datname FROM pg_database WHERE datname = 'meu_banco';
   ```

3. **Conexão funciona:**
   ```bash
   psql -h localhost -U meu_usuario -d meu_banco
   ```

4. **pg_hba.conf está configurado:**
   ```bash
   sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario
   ```

---

## 🆘 Troubleshooting

### **Erro: "database is being accessed by other users"**

```sql
-- Desconectar todos os usuários do database
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'meu_banco' AND pid <> pg_backend_pid();

-- Depois remover o database
DROP DATABASE meu_banco;
```

### **Erro: "role is used by other users"**

```sql
-- Primeiro remover o database
DROP DATABASE IF EXISTS meu_banco;

-- Depois remover o usuário
DROP USER meu_usuario;
```

### **Erro: "password authentication failed" após recriar**

1. Verificar se pg_hba.conf está correto
2. Reiniciar PostgreSQL
3. Verificar se a senha foi criada corretamente

---

**Última atualização:** 2025-01-27

