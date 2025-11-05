# 📚 Documentação - Módulo de Conexão PostgreSQL

## 🔗 Módulo Criado: `database_connection.py`

Módulo completo e reutilizável para gerenciar conexões PostgreSQL no projeto MaraBet AI.

---

## 📋 Credenciais Configuradas

```
Host: 37.27.220.67
Port: 5432
Database: meu_banco
Username: meu_usuario
Password: ctcaddTcMaRVioDY4kso
```

**String de Conexão:**
```
postgresql://meu_usuario:ctcaddTcMaRVioDY4kso@37.27.220.67:5432/meu_banco
```

---

## 🚀 Como Usar

### **1. Importar o módulo:**

```python
from database_connection import db, get_db_connection, test_db_connection
```

### **2. Testar conexão:**

```python
if test_db_connection():
    print("✅ Conexão OK!")
else:
    print("❌ Erro na conexão")
```

### **3. Usar conexão simples:**

```python
from database_connection import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT version();")
result = cursor.fetchone()
print(result)
cursor.close()
conn.close()
```

### **4. Usar context manager (Recomendado):**

```python
from database_connection import db

with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT current_database(), current_user;")
    result = cursor.fetchone()
    print(f"Database: {result['current_database']}")
    print(f"User: {result['current_user']}")
    cursor.close()
```

### **5. Executar queries (Método helper):**

```python
from database_connection import db

# SELECT
results = db.execute_query("SELECT * FROM minha_tabela LIMIT 10")
for row in results:
    print(row)

# INSERT/UPDATE/DELETE
rows_affected = db.execute_command(
    "INSERT INTO minha_tabela (nome) VALUES (%s)",
    ("João",)
)
print(f"Linhas afetadas: {rows_affected}")
```

### **6. Usar pool de conexões:**

```python
from database_connection import db

# Criar pool
db.create_connection_pool(min_conn=1, max_conn=10)

# Usar pool
with db.get_connection(use_pool=True) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    result = cursor.fetchone()
    print(result)
    cursor.close()

# Fechar pool (ao finalizar aplicação)
db.close_connection_pool()
```

---

## 📁 Arquivos Relacionados

1. **`database_connection.py`** - Módulo principal de conexão
2. **`exemplo_uso_conexao.py`** - Exemplos práticos de uso
3. **`atualizar_env.py`** - Script para atualizar arquivo .env
4. **`config_production.env`** - Configuração de produção
5. **`.env`** - Arquivo de ambiente (criado automaticamente)

---

## 🔧 Configuração

O módulo carrega configuração na seguinte ordem de prioridade:

1. **Variável de ambiente `DATABASE_URL`** (mais alta)
2. **Variáveis individuais** (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`)
3. **Arquivo `.env`** (se `python-dotenv` estiver instalado)
4. **Valores padrão** (hardcoded no módulo)

### **Configurar via variáveis de ambiente:**

```bash
# Windows PowerShell
$env:DATABASE_URL = "postgresql://meu_usuario:ctcaddTcMaRVioDY4kso@37.27.220.67:5432/meu_banco"

# Linux/Mac
export DATABASE_URL="postgresql://meu_usuario:ctcaddTcMaRVioDY4kso@37.27.220.67:5432/meu_banco"
```

### **Configurar via arquivo .env:**

```bash
# Copiar arquivo de produção
cp config_production.env .env

# OU atualizar automaticamente
python atualizar_env.py
```

---

## 📊 Funcionalidades

### **✅ Funcionalidades Implementadas:**

- ✅ Conexão simples ao banco
- ✅ Context manager para gerenciamento automático
- ✅ Pool de conexões para alta performance
- ✅ Métodos helper para queries e comandos
- ✅ Suporte a RealDictCursor (retorna dicts)
- ✅ Logging integrado
- ✅ Tratamento de erros
- ✅ Carregamento de configuração flexível

### **🔍 Métodos Disponíveis:**

- `db.create_connection()` - Cria nova conexão
- `db.get_connection()` - Context manager para conexão
- `db.create_connection_pool()` - Cria pool de conexões
- `db.get_connection_from_pool()` - Obtém conexão do pool
- `db.test_connection()` - Testa conexão
- `db.execute_query()` - Executa SELECT
- `db.execute_command()` - Executa INSERT/UPDATE/DELETE
- `db.get_connection_string()` - Retorna string de conexão

---

## 🧪 Exemplos de Uso

Veja o arquivo `exemplo_uso_conexao.py` para exemplos completos:

```bash
python exemplo_uso_conexao.py
```

---

## ⚠️ Nota Importante

**Status da Conexão:** A conexão ainda está falhando porque o usuário `meu_usuario` não existe no servidor PostgreSQL ou a senha está incorreta.

**Solução:** Conecte-se ao servidor PostgreSQL e execute:

```sql
CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
CREATE DATABASE meu_banco OWNER meu_usuario;
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;
```

---

**Última atualização:** 2025-01-27  
**Módulo:** `database_connection.py`  
**Status:** ✅ Módulo criado e configurado (aguardando criação do usuário no servidor)

