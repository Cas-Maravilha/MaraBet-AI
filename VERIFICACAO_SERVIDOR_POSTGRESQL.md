# 🔍 Verificação Final no Servidor PostgreSQL

## ❌ Problema Atual

A conexão está falhando mesmo com o usuário criado no servidor. Erro:
```
password authentication failed for user "meu_usuario"
```

---

## ✅ Verificações Necessárias no Servidor

### **1. Verificar se o usuário existe e a senha está correta:**

```bash
# Conectar ao PostgreSQL como superusuário
sudo -u postgres psql

# Verificar usuário
SELECT usename, usecreatedb, usesuper 
FROM pg_user 
WHERE usename = 'meu_usuario';

# Se o usuário existir mas a senha estiver errada, alterar:
ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';

# Verificar se consegue conectar com o usuário (teste local)
\c meu_banco meu_usuario
```

### **2. Verificar se o database existe:**

```sql
-- Verificar database
SELECT datname, datdba, pg_get_userbyid(datdba) as owner
FROM pg_database 
WHERE datname = 'meu_banco';

-- Se não existir, criar:
CREATE DATABASE meu_banco OWNER meu_usuario;

-- Verificar permissões
SELECT datname, datacl 
FROM pg_database 
WHERE datname = 'meu_banco';
```

### **3. Verificar pg_hba.conf (CRÍTICO para conexões remotas):**

```bash
# Localizar arquivo
sudo find /etc -name pg_hba.conf

# Ver conteúdo
sudo cat /etc/postgresql/*/main/pg_hba.conf

# OU editar diretamente
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

**O arquivo DEVE ter uma linha permitindo conexões remotas:**

```conf
# Permitir conexões remotas para meu_usuario
host    meu_banco    meu_usuario    0.0.0.0/0    md5

# OU permitir todas as conexões remotas
host    all          all            0.0.0.0/0    md5
```

**⚠️ IMPORTANTE:** Após alterar `pg_hba.conf`, REINICIE o PostgreSQL:

```bash
sudo systemctl restart postgresql
# OU
sudo service postgresql restart
```

### **4. Verificar postgresql.conf (listen_addresses):**

```bash
# Localizar arquivo
sudo find /etc -name postgresql.conf

# Verificar configuração
sudo grep -E "listen_addresses|port" /etc/postgresql/*/main/postgresql.conf
```

**Deve ter:**

```conf
listen_addresses = '*'  # ou IP específico como '37.27.220.67'
port = 5432
```

**⚠️ IMPORTANTE:** Após alterar `postgresql.conf`, REINICIE o PostgreSQL:

```bash
sudo systemctl restart postgresql
```

### **5. Verificar firewall (iptables/ufw):**

```bash
# Verificar se a porta 5432 está aberta
sudo ufw status
# OU
sudo iptables -L -n | grep 5432

# Se não estiver aberta, abrir:
sudo ufw allow 5432/tcp
# OU
sudo iptables -A INPUT -p tcp --dport 5432 -j ACCEPT
```

### **6. Testar conexão localmente no servidor:**

```bash
# Testar conexão local (deve funcionar)
psql -h localhost -U meu_usuario -d meu_banco

# Se funcionar localmente mas não remotamente, 
# o problema é no pg_hba.conf ou firewall
```

---

## 🔧 Script SQL Completo para Verificar e Corrigir

Execute no servidor PostgreSQL:

```sql
-- 1. Verificar usuário
SELECT usename FROM pg_user WHERE usename = 'meu_usuario';

-- 2. Recriar usuário com senha correta (se necessário)
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_user WHERE usename = 'meu_usuario') THEN
        ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
        RAISE NOTICE 'Senha do usuário atualizada';
    ELSE
        CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
        RAISE NOTICE 'Usuário criado';
    END IF;
END $$;

-- 3. Verificar database
SELECT datname FROM pg_database WHERE datname = 'meu_banco';

-- 4. Criar database se não existir
CREATE DATABASE meu_banco OWNER meu_usuario;

-- 5. Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;

-- 6. Conectar ao database e conceder permissões no schema
\c meu_banco

GRANT ALL ON SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO meu_usuario;
```

---

## 🔧 Configuração do pg_hba.conf

Edite o arquivo `/etc/postgresql/*/main/pg_hba.conf` e adicione:

```conf
# Permitir conexões remotas para meu_usuario
host    meu_banco    meu_usuario    0.0.0.0/0    md5

# OU permitir todas as conexões remotas (menos seguro)
host    all          all            0.0.0.0/0    md5
```

**Formato da linha:**
```
host    database    user    CIDR    auth-method
```

**Explicação:**
- `host`: tipo de conexão (TCP/IP)
- `meu_banco`: nome do database
- `meu_usuario`: nome do usuário
- `0.0.0.0/0`: permite de qualquer IP (ou use IP específico como `192.168.1.0/24`)
- `md5`: método de autenticação (senha criptografada)

---

## 🔧 Configuração do postgresql.conf

Edite o arquivo `/etc/postgresql/*/main/postgresql.conf` e verifique:

```conf
# Permitir conexões de qualquer IP
listen_addresses = '*'

# OU permitir apenas IP específico
# listen_addresses = '37.27.220.67'

# Porta padrão
port = 5432
```

---

## ✅ Checklist de Verificação

- [ ] Usuário `meu_usuario` existe no servidor
- [ ] Senha do usuário está correta: `ctcaddTcMaRVioDY4kso`
- [ ] Database `meu_banco` existe
- [ ] Database pertence ao usuário `meu_usuario`
- [ ] Usuário tem permissões no database
- [ ] `pg_hba.conf` permite conexões remotas
- [ ] `postgresql.conf` tem `listen_addresses = '*'`
- [ ] Firewall permite porta 5432
- [ ] PostgreSQL foi reiniciado após alterações
- [ ] Conexão local funciona (psql -h localhost -U meu_usuario -d meu_banco)

---

## 🧪 Teste Após Configurações

Depois de fazer todas as verificações e correções:

```bash
# No servidor, testar localmente
psql -h localhost -U meu_usuario -d meu_banco

# De sua máquina, testar remotamente
python testar_conexao.py
```

---

**Última atualização:** 2025-01-27

