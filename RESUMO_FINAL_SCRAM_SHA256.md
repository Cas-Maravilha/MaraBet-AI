# 📋 Resumo Final - Configuração com scram-sha-256

## ✅ Status Atual

- ✅ **psycopg2 versão 2.9.11** - Suporta scram-sha-256
- ✅ **Configurações locais** - Todas atualizadas corretamente
- ✅ **Credenciais configuradas** - Senha correta em todos os arquivos
- ❌ **Conexão ainda falha** - Problema no servidor PostgreSQL

---

## 🔧 Verificações Necessárias no Servidor

### **1. Verificar pg_hba.conf**

A linha deve estar completa e correta:

```bash
# Verificar linha no pg_hba.conf
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario
```

**Deve mostrar:**
```
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

**Se mostrar incompleta (sem scram-sha-256):**
```bash
# Editar arquivo
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Completar linha:
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

### **2. Verificar/Alterar Senha do Usuário**

A senha do usuário precisa estar configurada corretamente:

```bash
# Conectar ao PostgreSQL como superusuário
sudo -u postgres psql

# Verificar se usuário existe
SELECT usename FROM pg_user WHERE usename = 'meu_usuario';

# Alterar senha (IMPORTANTE: usar aspas simples)
ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';

# Verificar método de criptografia
SHOW password_encryption;
```

**Deve mostrar:** `scram-sha-256`

### **3. Verificar Database**

```sql
# Verificar se database existe
SELECT datname FROM pg_database WHERE datname = 'meu_banco';

# Se não existir, criar:
CREATE DATABASE meu_banco OWNER meu_usuario;

# Verificar permissões
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;
```

### **4. Reiniciar PostgreSQL**

Após qualquer alteração:

```bash
sudo systemctl restart postgresql
sudo systemctl status postgresql
```

### **5. Verificar postgresql.conf**

```bash
# Verificar listen_addresses
sudo grep listen_addresses /etc/postgresql/*/main/postgresql.conf
```

**Deve mostrar:**
```
listen_addresses = '*'
```

---

## 🚀 Script SQL Completo para Servidor

Execute no servidor PostgreSQL (como superusuário postgres):

```sql
-- 1. Verificar/Alterar senha do usuário
ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';

-- 2. Verificar usuário
SELECT usename, usecreatedb FROM pg_user WHERE usename = 'meu_usuario';

-- 3. Verificar/Alterar método de criptografia
SHOW password_encryption;

-- Se não estiver em scram-sha-256, alterar (opcional):
-- ALTER SYSTEM SET password_encryption = 'scram-sha-256';
-- SELECT pg_reload_conf();

-- 4. Verificar database
SELECT datname, pg_get_userbyid(datdba) as owner 
FROM pg_database 
WHERE datname = 'meu_banco';

-- 5. Criar database se não existir
CREATE DATABASE meu_banco OWNER meu_usuario;

-- 6. Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;

-- 7. Conectar ao database
\c meu_banco

-- 8. Conceder permissões no schema
GRANT ALL ON SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO meu_usuario;
```

---

## 📋 Checklist Final

- [ ] **pg_hba.conf** tem linha completa: `host meu_banco meu_usuario 0.0.0.0/0 scram-sha-256`
- [ ] **PostgreSQL reiniciado** após alterar pg_hba.conf
- [ ] **Senha do usuário** está correta: `ctcaddTcMaRVioDY4kso`
- [ ] **Usuário existe** no servidor: `SELECT usename FROM pg_user WHERE usename = 'meu_usuario';`
- [ ] **Database existe**: `SELECT datname FROM pg_database WHERE datname = 'meu_banco';`
- [ ] **Permissões concedidas** no database
- [ ] **listen_addresses = '*'** no postgresql.conf
- [ ] **PostgreSQL está rodando**: `sudo systemctl status postgresql`
- [ ] **Conexão local funciona**: `psql -h localhost -U meu_usuario -d meu_banco`

---

## 🧪 Teste Após Configurações

### **1. Testar localmente no servidor:**

```bash
psql -h localhost -U meu_usuario -d meu_banco
```

**Se funcionar localmente mas não remotamente:**
- Verifique `listen_addresses` no postgresql.conf
- Verifique firewall (porta 5432)

### **2. Testar remotamente:**

```bash
# De sua máquina
python testar_conexao_scram.py
# OU
python testar_conexao.py
```

---

## 🆘 Troubleshooting

### **Erro: "password authentication failed"**

**Causa mais comum:** Senha do usuário no servidor está diferente

**Solução:**
```sql
ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
```

**Verificar:**
```sql
SELECT usename FROM pg_user WHERE usename = 'meu_usuario';
```

### **Erro: "Connection refused"**

**Causa:** PostgreSQL não está escutando conexões remotas

**Solução:**
1. Verificar `listen_addresses` no postgresql.conf
2. Verificar firewall
3. Reiniciar PostgreSQL

### **Erro: "database does not exist"**

**Solução:**
```sql
CREATE DATABASE meu_banco OWNER meu_usuario;
```

---

## 📝 Comandos Rápidos no Servidor

```bash
# 1. Verificar pg_hba.conf
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario

# 2. Completar linha se necessário
sudo sed -i 's/^host[[:space:]]*meu_banco[[:space:]]*meu_usuario[[:space:]]*0\.0\.0\.0\/0[[:space:]]*$/host    meu_banco    meu_usuario    0.0.0.0\/0    scram-sha-256/' /etc/postgresql/*/main/pg_hba.conf

# 3. Reiniciar PostgreSQL
sudo systemctl restart postgresql

# 4. Verificar senha do usuário
sudo -u postgres psql -c "ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';"

# 5. Testar conexão local
psql -h localhost -U meu_usuario -d meu_banco
```

---

**Última atualização:** 2025-01-27  
**Método de autenticação:** scram-sha-256  
**psycopg2 versão:** 2.9.11 (suporta scram-sha-256)

