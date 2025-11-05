# 🔍 Guia: Testar Conexão do Banco de Dados

## 📋 Credenciais do Banco de Dados

```
Host: 37.27.220.67
Porta: 5432 (PostgreSQL)
Database: meu_banco
Usuário: meu_usuario
Senha: ctcaddTcMARvioDY4kso
```

**String de conexão:**
```
postgresql://meu_usuario:ctcaddTcMARvioDY4kso@37.27.220.67:5432/meu_banco
```

---

## 🛠️ Testar com Diferentes Ferramentas

### **1. pgAdmin (PostgreSQL)**

1. Abrir pgAdmin
2. Clicar em **Add New Server**
3. Preencher:
   - **Name**: MaraBet DB (ou qualquer nome)
   - **Host**: `37.27.220.67`
   - **Port**: `5432`
   - **Database**: `meu_banco`
   - **Username**: `meu_usuario`
   - **Password**: `ctcaddTcMARvioDY4kso`
4. Clicar em **Save**
5. Se conectar com sucesso, você verá o database na lista

---

### **2. DBeaver (Universal Database Tool)**

1. Abrir DBeaver
2. Clicar em **New Database Connection**
3. Selecionar **PostgreSQL**
4. Preencher:
   - **Host**: `37.27.220.67`
   - **Port**: `5432`
   - **Database**: `meu_banco`
   - **Username**: `meu_usuario`
   - **Password**: `ctcaddTcMARvioDY4kso`
5. Clicar em **Test Connection**
6. Se funcionar, você verá "Connection successful"
7. Clicar em **Finish**

---

### **3. MySQL Workbench (apenas MySQL)**

**Nota:** MySQL Workbench é para MySQL, não PostgreSQL. Para PostgreSQL, use pgAdmin ou DBeaver.

Se você quiser testar MySQL (porta 3306):
1. Abrir MySQL Workbench
2. Clicar em **+** para adicionar nova conexão
3. Preencher:
   - **Connection Name**: MaraBet MySQL
   - **Hostname**: `37.27.220.67`
   - **Port**: `3306`
   - **Username**: seu usuário MySQL
   - **Password**: sua senha MySQL
4. Clicar em **Test Connection**

**⚠️ Nota:** A porta 3306 (MySQL) não está acessível no servidor. Use PostgreSQL (porta 5432).

---

### **4. psql (Linha de Comando)**

Se você tiver `psql` instalado:

```bash
psql -h 37.27.220.67 -p 5432 -U meu_usuario -d meu_banco
```

Quando solicitado, digite a senha: `ctcaddTcMARvioDY4kso`

---

### **5. Python (psycopg2)**

Use o script `testar_conexao.py`:

```bash
python testar_conexao.py
```

Ou use diretamente:

```python
import psycopg2

conn = psycopg2.connect(
    host="37.27.220.67",
    port=5432,
    database="meu_banco",
    user="meu_usuario",
    password="ctcaddTcMARvioDY4kso"
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())
conn.close()
```

---

### **6. Teste Rápido com Python**

Execute o script `testar_conexao_cliente.py`:

```bash
python testar_conexao_cliente.py
```

---

## ✅ Verificação de Conexão

### **Testes Realizados:**

1. ✅ **Ping**: Servidor acessível (latência ~168ms)
2. ✅ **Test-NetConnection**: Porta 5432 acessível
3. ✅ **Teste TCP (Python)**: Conexão TCP bem-sucedida
4. ✅ **Teste psycopg2**: Conexão PostgreSQL estabelecida
5. ✅ **Teste de autenticação**: Usuário e senha corretos

### **Status da Conexão:**

- ✅ **PostgreSQL (porta 5432)**: Funcionando perfeitamente
- ❌ **MySQL (porta 3306)**: Não disponível (porta fechada)

---

## 🔧 Troubleshooting

### **Erro: "password authentication failed"**

- Verifique se a senha está correta: `ctcaddTcMARvioDY4kso` (com "MAR" em maiúsculas)
- Verifique se não há espaços extras na senha

### **Erro: "could not connect to server"**

- Verifique se o servidor está acessível: `ping 37.27.220.67`
- Verifique se a porta está aberta: `Test-NetConnection -ComputerName 37.27.220.67 -Port 5432`

### **Erro: "timeout"**

- Verifique sua conexão de internet
- Verifique se o firewall não está bloqueando a porta 5432

---

## 📊 Resumo das Credenciais

| Campo | Valor |
|-------|-------|
| **Host** | `37.27.220.67` |
| **Porta** | `5432` (PostgreSQL) |
| **Database** | `meu_banco` |
| **Usuário** | `meu_usuario` |
| **Senha** | `ctcaddTcMARvioDY4kso` |
| **Tipo** | PostgreSQL |

---

**Última atualização:** 2025-01-27  
**Status:** ✅ Conexão PostgreSQL funcionando

