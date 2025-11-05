# 🔐 Conectar ao Servidor PostgreSQL via SSH

## 📋 Informações do Servidor

```
Host: 37.27.220.67
Port: 5432 (PostgreSQL)
SSH Port: 22 (padrão)
```

---

## 🔧 Opção 1: Conectar via SSH e usar psql localmente

Se você tem acesso SSH ao servidor, pode conectar diretamente:

### **1. Conectar via SSH:**

```bash
# Windows (PowerShell)
ssh usuario@37.27.220.67

# Windows (Git Bash)
ssh usuario@37.27.220.67

# Linux/Mac
ssh usuario@37.27.220.67
```

**Substitua `usuario` pelo seu usuário SSH no servidor.**

### **2. No servidor, conectar ao PostgreSQL:**

```bash
# Conectar como superusuário postgres
sudo -u postgres psql

# OU conectar diretamente
psql -U postgres -h localhost

# OU conectar com seu usuário
psql -U meu_usuario -d meu_banco -h localhost
```

### **3. Verificar e criar usuário/database:**

```sql
-- Verificar usuários
SELECT usename FROM pg_user;

-- Verificar se meu_usuario existe
SELECT * FROM pg_user WHERE usename = 'meu_usuario';

-- Criar usuário se não existir
CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';

-- Verificar databases
SELECT datname FROM pg_database;

-- Criar database se não existir
CREATE DATABASE meu_banco OWNER meu_usuario;

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;

-- Conectar ao database
\c meu_banco

-- Conceder permissões no schema public
GRANT ALL ON SCHEMA public TO meu_usuario;
```

---

## 🔧 Opção 2: Usar SSH Tunnel (túnel SSH)

Se você não pode acessar diretamente, mas tem SSH, pode criar um túnel:

### **Windows (PowerShell):**

```powershell
# Criar túnel SSH
ssh -L 5433:localhost:5432 usuario@37.27.220.67 -N

# Em outro terminal, conectar via túnel
psql -h localhost -p 5433 -U meu_usuario -d meu_banco
```

### **Windows (PuTTY):**

1. Abra PuTTY
2. Configurações de conexão:
   - Host: `37.27.220.67`
   - Port: `22`
3. SSH → Tunnels:
   - Source port: `5433`
   - Destination: `localhost:5432`
   - Clique em "Add"
4. Conecte e mantenha a sessão aberta
5. Em outro terminal:
   ```bash
   psql -h localhost -p 5433 -U meu_usuario -d meu_banco
   ```

---

## 🔧 Opção 3: Usar Python via SSH

Se você tem acesso SSH, pode executar scripts Python no servidor:

```bash
# Conectar via SSH
ssh usuario@37.27.220.67

# No servidor, executar script Python
python3 testar_conexao_detalhado.py
```

---

## 📝 Comandos Úteis no PostgreSQL

### **Verificar conexões ativas:**

```sql
SELECT * FROM pg_stat_activity;
```

### **Verificar usuários:**

```sql
SELECT usename, usecreatedb, usesuper FROM pg_user;
```

### **Verificar databases:**

```sql
SELECT datname, datdba, encoding FROM pg_database;
```

### **Verificar permissões:**

```sql
-- Permissões do usuário no database
SELECT datname, datacl FROM pg_database WHERE datname = 'meu_banco';

-- Permissões no schema
SELECT schema_name, schema_owner FROM information_schema.schemata;
```

### **Alterar senha:**

```sql
ALTER USER meu_usuario WITH PASSWORD 'nova_senha';
```

### **Listar tabelas:**

```sql
\dt
```

### **Sair do psql:**

```sql
\q
```

---

## 🔒 Verificar Configuração do PostgreSQL

### **1. Verificar pg_hba.conf:**

```bash
# Localizar arquivo
sudo find /etc -name pg_hba.conf

# Ver conteúdo
sudo cat /etc/postgresql/*/main/pg_hba.conf
```

**Deve ter uma linha permitindo conexões remotas:**

```conf
host    meu_banco    meu_usuario    0.0.0.0/0    md5
# ou
host    all          all            0.0.0.0/0    md5
```

### **2. Verificar postgresql.conf:**

```bash
# Localizar arquivo
sudo find /etc -name postgresql.conf

# Ver configurações de conexão
sudo grep -E "listen_addresses|port" /etc/postgresql/*/main/postgresql.conf
```

**Deve ter:**

```conf
listen_addresses = '*'  # ou IP específico
port = 5432
```

### **3. Reiniciar PostgreSQL:**

```bash
sudo systemctl restart postgresql
# ou
sudo service postgresql restart
```

---

## 🆘 Troubleshooting

### **Erro: "Connection refused"**
- PostgreSQL não está rodando: `sudo systemctl status postgresql`
- Porta não está aberta no firewall
- `listen_addresses` não está configurado corretamente

### **Erro: "Password authentication failed"**
- Usuário não existe
- Senha incorreta
- `pg_hba.conf` não permite conexões remotas

### **Erro: "Database does not exist"**
- Database não foi criado
- Nome do database está incorreto

### **Erro: "Permission denied"**
- Usuário não tem permissões no database
- Precisa conceder permissões: `GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;`

---

**Última atualização:** 2025-01-27

