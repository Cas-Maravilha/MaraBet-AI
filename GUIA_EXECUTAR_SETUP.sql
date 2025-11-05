# 📋 Guia Rápido - Executar Setup do Banco de Dados

## 🚀 Como Executar o Script SQL

### **Opção 1: Executar Script Completo (Recomendado)**

```bash
# 1. Copiar script para o servidor (se necessário)
scp setup_database.sql usuario@37.27.220.67:/tmp/

# 2. Conectar ao servidor via SSH
ssh usuario@37.27.220.67

# 3. No servidor, executar o script
sudo -u postgres psql -f /tmp/setup_database.sql
```

### **Opção 2: Comandos SQL Diretos**

Se você já está conectado ao PostgreSQL como superusuário:

```sql
-- Executar os comandos diretamente
CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
CREATE DATABASE meu_banco OWNER meu_usuario;
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;

-- Conectar ao database
\c meu_banco

-- Conceder permissões no schema
GRANT ALL ON SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO meu_usuario;
```

### **Opção 3: Via psql Interativo**

```bash
# Conectar ao PostgreSQL
psql -U postgres

# No prompt psql, copiar e colar os comandos do arquivo setup_database.sql
```

---

## ✅ Após Executar o Script

Teste a conexão:

```bash
# Via Python (recomendado)
python testar_conexao.py

# OU via psql (se estiver instalado)
psql -h 37.27.220.67 -U meu_usuario -d meu_banco
```

---

## 📝 Arquivos Criados

1. **`setup_database.sql`** - Script SQL completo e seguro
2. **`GUIA_EXECUTAR_SETUP.sql`** - Este guia (arquivo markdown)
3. **`testar_conexao.py`** - Script para testar conexão após setup

---

**Última atualização:** 2025-01-27

