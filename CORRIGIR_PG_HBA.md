# 🔧 Corrigir pg_hba.conf - Configuração Correta

## 📋 Linhas Atuais no pg_hba.conf

Você tem duas linhas:

1. **Linha incompleta:**
   ```
   host    meu_banco    meu_usuario    0.0.0.0/0
   ```
   ❌ **Problema:** Falta o método de autenticação

2. **Linha existente:**
   ```
   host    all             all             0.0.0.0.0/0               scram-sha-256
   ```
   ✅ Esta linha está correta e permite conexões remotas para todos

---

## ✅ Soluções

### **Opção 1: Completar a primeira linha (Recomendado - Mais Seguro)**

Edite o arquivo `pg_hba.conf` e complete a linha:

```conf
# Linha corrigida - permite apenas meu_usuario no meu_banco
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

**OU se preferir md5 (compatível com versões antigas):**

```conf
host    meu_banco    meu_usuario    0.0.0.0/0    md5
```

### **Opção 2: Usar a linha existente (Já Funciona)**

A linha `host    all             all             0.0.0.0/0               scram-sha-256` já permite conexões remotas para todos os usuários e databases.

**⚠️ Nota:** Esta linha é menos segura pois permite conexões de qualquer usuário, mas já deve funcionar para seu caso.

### **Opção 3: Linha Específica com scram-sha-256 (Mais Seguro)**

Se você quer usar `scram-sha-256` (método mais seguro), adicione:

```conf
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

**⚠️ IMPORTANTE:** Se usar `scram-sha-256`, o usuário precisa ter senha configurada com esse método:

```sql
-- No PostgreSQL, alterar senha para usar scram-sha-256
ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
```

---

## 🔧 Como Corrigir

### **1. Editar o arquivo pg_hba.conf:**

```bash
# Conectar ao servidor
ssh usuario@37.27.220.67

# Editar arquivo
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

### **2. Encontrar a linha incompleta:**

Procure por:
```
host    meu_banco    meu_usuario    0.0.0.0/0
```

### **3. Completar a linha:**

**Opção A - Usar md5 (compatível):**
```conf
host    meu_banco    meu_usuario    0.0.0.0/0    md5
```

**Opção B - Usar scram-sha-256 (mais seguro):**
```conf
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

### **4. Salvar e reiniciar PostgreSQL:**

```bash
# Salvar arquivo (Ctrl+X, Y, Enter no nano)

# Reiniciar PostgreSQL
sudo systemctl restart postgresql

# Verificar se está rodando
sudo systemctl status postgresql
```

---

## 📝 Exemplo Completo do pg_hba.conf

Seu arquivo `pg_hba.conf` deve ter algo assim:

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     peer

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5

# IPv6 local connections:
host    all             all             ::1/128                  md5

# Conexões remotas - Permitir todas (menos seguro)
host    all             all             0.0.0.0/0               scram-sha-256

# Conexões remotas - Permitir apenas meu_usuario no meu_banco (mais seguro)
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

---

## 🔒 Diferenças entre md5 e scram-sha-256

### **md5:**
- ✅ Compatível com versões antigas do PostgreSQL
- ✅ Funciona com a maioria dos clientes
- ⚠️ Menos seguro que scram-sha-256

### **scram-sha-256:**
- ✅ Mais seguro (criptografia mais forte)
- ✅ Recomendado para PostgreSQL 10+
- ⚠️ Pode não funcionar com clientes muito antigos

---

## ✅ Verificação

### **1. Verificar se a linha está correta:**

```bash
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario
```

Deve mostrar:
```
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

### **2. Verificar sintaxe:**

```bash
sudo -u postgres psql -c "SELECT 1"
```

Se não der erro, a sintaxe está correta.

### **3. Testar conexão:**

```bash
# No servidor
psql -h localhost -U meu_usuario -d meu_banco

# De sua máquina
python testar_conexao.py
```

---

## 🆘 Troubleshooting

### **Erro: "password authentication failed" com scram-sha-256**

- Verifique se a senha do usuário está configurada corretamente:
  ```sql
  ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
  ```

### **Erro: "invalid authentication method"**

- Use `md5` em vez de `scram-sha-256` se seu cliente não suportar:
  ```conf
  host    meu_banco    meu_usuario    0.0.0.0/0    md5
  ```

### **Conexão ainda não funciona após correção**

- Verifique se reiniciou o PostgreSQL: `sudo systemctl restart postgresql`
- Verifique se PostgreSQL está rodando: `sudo systemctl status postgresql`
- Verifique logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`

---

## 💡 Recomendação

**Para máxima compatibilidade, use:**

```conf
host    meu_banco    meu_usuario    0.0.0.0/0    md5
```

**Para máxima segurança, use:**

```conf
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

**Última atualização:** 2025-01-27

