# 📋 Instruções para Criar Usuário e Database no PostgreSQL

## ❌ Problema Atual

A conexão está falhando porque o usuário `meu_usuario` não existe no servidor PostgreSQL ou a senha está incorreta.

**Erro:** `password authentication failed for user "meu_usuario"`

---

## ✅ Solução: Criar Usuário e Database no Servidor

### **Opção 1: Executar Script SQL (Recomendado)**

1. **Conecte-se ao servidor PostgreSQL como superusuário:**

   ```bash
   # Via SSH ao servidor
   ssh usuario@37.27.220.67
   
   # No servidor, conectar ao PostgreSQL
   sudo -u postgres psql
   # OU
   psql -U postgres -h localhost
   ```

2. **Execute o script SQL:**

   ```bash
   # Copiar script para o servidor (se necessário)
   scp criar_usuario_database.sql usuario@37.27.220.67:/tmp/
   
   # No servidor, executar
   sudo -u postgres psql -f /tmp/criar_usuario_database.sql
   ```

   **OU execute os comandos diretamente:**

   ```sql
   -- Criar usuário
   CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
   
   -- Criar database
   CREATE DATABASE meu_banco OWNER meu_usuario;
   
   -- Conceder permissões
   GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;
   
   -- Conectar ao database
   \c meu_banco
   
   -- Conceder permissões no schema
   GRANT ALL ON SCHEMA public TO meu_usuario;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO meu_usuario;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO meu_usuario;
   ```

---

### **Opção 2: Comandos SQL Diretos**

Se você tem acesso ao servidor PostgreSQL, execute estes comandos:

```sql
-- 1. Criar usuário
CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';

-- 2. Criar database
CREATE DATABASE meu_banco OWNER meu_usuario;

-- 3. Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;

-- 4. Conectar ao database
\c meu_banco

-- 5. Conceder permissões no schema public
GRANT ALL ON SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO meu_usuario;
```

---

### **Opção 3: Se o Usuário Já Existe**

Se o usuário já existe mas a senha está errada:

```sql
-- Alterar senha do usuário existente
ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';

-- Verificar se o database existe
SELECT datname FROM pg_database WHERE datname = 'meu_banco';

-- Se não existir, criar
CREATE DATABASE meu_banco OWNER meu_usuario;

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;
```

---

## 🔧 Verificar Configuração do PostgreSQL

### **1. Verificar pg_hba.conf (Permitir Conexões Remotas)**

O arquivo `pg_hba.conf` deve permitir conexões remotas:

```bash
# Localizar arquivo
sudo find /etc -name pg_hba.conf

# Editar arquivo
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

**Adicionar linha:**

```conf
# Permitir conexões remotas
host    meu_banco    meu_usuario    0.0.0.0/0    md5
# OU permitir todas
host    all          all            0.0.0.0/0    md5
```

**Reiniciar PostgreSQL:**

```bash
sudo systemctl restart postgresql
# OU
sudo service postgresql restart
```

### **2. Verificar postgresql.conf (Listen Addresses)**

```bash
# Localizar arquivo
sudo find /etc -name postgresql.conf

# Verificar configuração
sudo grep -E "listen_addresses|port" /etc/postgresql/*/main/postgresql.conf
```

**Deve ter:**

```conf
listen_addresses = '*'  # ou IP específico
port = 5432
```

**Reiniciar PostgreSQL:**

```bash
sudo systemctl restart postgresql
```

---

## ✅ Testar Após Criar Usuário

Após criar o usuário e database, teste a conexão:

```bash
# No servidor
psql -h localhost -U meu_usuario -d meu_banco

# De sua máquina (se psql estiver instalado)
psql -h 37.27.220.67 -U meu_usuario -d meu_banco

# OU via Python
python testar_conexao.py
```

---

## 📝 Arquivos Úteis

1. **`criar_usuario_database.sql`** - Script SQL completo
2. **`testar_conexao.py`** - Script Python para testar conexão
3. **`database_connection.py`** - Módulo de conexão

---

## 🆘 Troubleshooting

### **Erro: "role does not exist"**
- Usuário não foi criado: Execute `CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';`

### **Erro: "database does not exist"**
- Database não foi criado: Execute `CREATE DATABASE meu_banco OWNER meu_usuario;`

### **Erro: "password authentication failed"**
- Senha incorreta: Execute `ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';`

### **Erro: "Connection refused"**
- PostgreSQL não está rodando: `sudo systemctl start postgresql`
- Porta não está aberta no firewall
- `listen_addresses` não está configurado corretamente

### **Erro: "permission denied"**
- Usuário não tem permissões: Execute os comandos GRANT

---

**Última atualização:** 2025-01-27

