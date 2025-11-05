# 🔍 Diagnóstico de Conexão - Banco de Dados PostgreSQL

## ❌ Problema Identificado

**Erro:** `password authentication failed for user "meu_usuario"`

**Status:** O servidor está acessível, mas a autenticação falha.

---

## ✅ O Que Está Funcionando

1. ✅ **Servidor acessível** - IP `37.27.220.67` responde
2. ✅ **Porta aberta** - Porta `5432` está acessível
3. ✅ **PostgreSQL ativo** - Servidor está respondendo

---

## ❌ O Que NÃO Está Funcionando

1. ❌ **Autenticação** - Usuário ou senha incorretos
2. ❌ **Credenciais** - As credenciais fornecidas não estão funcionando

---

## 🔧 Credenciais Testadas

```
Host: 37.27.220.67
Port: 5432
Database: meu_banco
Username: meu_usuario
Password: ctcaddTcMaRVioDY4kso
```

---

## 📋 Verificações Necessárias no Servidor

### **1. Verificar se o usuário existe:**

Conecte-se ao servidor PostgreSQL (como superusuário) e execute:

```sql
-- Listar todos os usuários
SELECT usename FROM pg_user;

-- Verificar usuário específico
SELECT * FROM pg_user WHERE usename = 'meu_usuario';

-- Criar usuário se não existir
CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
```

### **2. Verificar se o database existe:**

```sql
-- Listar todos os databases
SELECT datname FROM pg_database;

-- Verificar database específico
SELECT * FROM pg_database WHERE datname = 'meu_banco';

-- Criar database se não existir
CREATE DATABASE meu_banco OWNER meu_usuario;
```

### **3. Verificar permissões:**

```sql
-- Conceder permissões ao usuário
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;

-- Conceder permissões no schema public
\c meu_banco
GRANT ALL ON SCHEMA public TO meu_usuario;
```

### **4. Verificar pg_hba.conf:**

O arquivo `pg_hba.conf` deve permitir conexões remotas:

```conf
# Permitir conexões remotas
host    meu_banco    meu_usuario    0.0.0.0/0    md5
# ou
host    all          all            0.0.0.0/0    md5
```

Depois de alterar, reinicie o PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### **5. Verificar postgresql.conf:**

O arquivo `postgresql.conf` deve permitir conexões remotas:

```conf
listen_addresses = '*'  # ou o IP específico
port = 5432
```

---

## 🔄 Soluções Possíveis

### **Opção 1: Recriar usuário e senha**

```sql
-- Conectar como superusuário (postgres)
psql -U postgres -h localhost

-- Remover usuário se existir (cuidado!)
DROP USER IF EXISTS meu_usuario;

-- Criar usuário com senha
CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';

-- Criar database
CREATE DATABASE meu_banco OWNER meu_usuario;

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;

-- Conectar ao database e conceder permissões no schema
\c meu_banco
GRANT ALL ON SCHEMA public TO meu_usuario;
```

### **Opção 2: Alterar senha do usuário existente**

```sql
-- Se o usuário já existe, alterar a senha
ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
```

### **Opção 3: Verificar se há caracteres especiais na senha**

A senha pode ter espaços ou caracteres especiais que não estão visíveis. 

**Teste com senha simples primeiro:**
```sql
ALTER USER meu_usuario WITH PASSWORD 'senha123';
```

E depois teste a conexão com:
```
DATABASE_URL=postgresql://meu_usuario:senha123@37.27.220.67:5432/meu_banco
```

---

## 🧪 Teste Direto no Servidor

Se você tem acesso SSH ao servidor, teste localmente:

```bash
# Conectar diretamente no servidor
psql -U meu_usuario -d meu_banco -h localhost

# Ou testar a senha
psql -U meu_usuario -d meu_banco -h 37.27.220.67
```

---

## 📝 Próximos Passos

1. **Verificar no servidor** se o usuário `meu_usuario` existe
2. **Verificar no servidor** se o database `meu_banco` existe
3. **Recriar ou alterar** a senha do usuário
4. **Verificar** o arquivo `pg_hba.conf` para permitir conexões remotas
5. **Testar** a conexão novamente após as correções

---

## 🔒 Segurança

⚠️ **IMPORTANTE:** 
- Após resolver o problema, verifique as permissões do usuário
- Use senhas fortes em produção
- Limite o acesso remoto apenas a IPs necessários no `pg_hba.conf`
- Considere usar SSL/TLS para conexões remotas

---

**Criado em:** 2025-01-27  
**Status:** Aguardando verificação no servidor PostgreSQL

