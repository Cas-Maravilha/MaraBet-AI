# 📥 Como Instalar psql no Windows

## ❌ Problema Atual

O comando `psql` não está instalado no Windows. Você precisa instalar o cliente PostgreSQL.

---

## ✅ Opções de Instalação

### **Opção 1: Instalar via Chocolatey (Mais Rápido)**

Se você tem Chocolatey instalado:

```powershell
choco install postgresql --params '/Password:PostgreSQL123'
```

**OU apenas o cliente (sem servidor):**

```powershell
choco install postgresql-client
```

---

### **Opção 2: Baixar Instalador Oficial**

1. **Acesse:** https://www.postgresql.org/download/windows/
2. **Baixe:** PostgreSQL Installer (versão mais recente)
3. **Durante a instalação:**
   - Selecione apenas "Command Line Tools" (não precisa instalar o servidor)
   - Ou instale tudo se quiser ter servidor local também
4. **Adicione ao PATH:** Geralmente fica em `C:\Program Files\PostgreSQL\<versão>\bin`

---

### **Opção 3: Usar Python (Já Disponível)**

Você pode usar Python em vez de `psql`:

```powershell
# Testar conexão
python testar_conexao_interativo.py

# OU diretamente
python -c "import psycopg2; conn = psycopg2.connect('postgresql://meu_usuario:ctcaddTcMaRVioDY4kso@37.27.220.67:5432/meu_banco'); print('✅ Conectado!')"
```

---

### **Opção 4: Usar Docker (Se Docker estiver instalado)**

```powershell
docker run -it --rm postgres:15 psql -h 37.27.220.67 -U meu_usuario -d meu_banco
```

---

## 🔧 Após Instalar psql

### **Testar Instalação:**

```powershell
psql --version
```

### **Conectar ao Banco:**

```powershell
# Definir senha (evita prompt)
$env:PGPASSWORD = "ctcaddTcMaRVioDY4kso"

# Conectar
psql -h 37.27.220.67 -U meu_usuario -d meu_banco

# OU em uma linha
psql -h 37.27.220.67 -U meu_usuario -d meu_banco -W
```

---

## 💡 Alternativa: Usar Python

Como você já tem Python instalado, pode usar Python em vez de `psql`:

### **Script Python para testar conexão:**

```powershell
python testar_conexao_detalhado.py
```

### **Script Python para executar queries:**

```python
import psycopg2

conn = psycopg2.connect(
    host='37.27.220.67',
    port=5432,
    database='meu_banco',
    user='meu_usuario',
    password='ctcaddTcMaRVioDY4kso'
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
```

---

## 🎯 Recomendação

**Para desenvolvimento local:** Use Python (já está instalado)

**Para uso avançado:** Instale `psql` via Chocolatey ou instalador oficial

---

**Última atualização:** 2025-01-27

