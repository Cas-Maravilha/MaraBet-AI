# 🔧 Completar pg_hba.conf com scram-sha-256

## 📋 Linha a Ser Corrigida

**Linha atual (incompleta):**
```
host    meu_banco    meu_usuario    0.0.0.0/0
```

**Linha corrigida:**
```
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

---

## 🚀 Passo a Passo Manual

### **1. Conectar ao servidor:**

```bash
ssh usuario@37.27.220.67
```

### **2. Localizar arquivo pg_hba.conf:**

```bash
sudo find /etc -name pg_hba.conf
# Geralmente: /etc/postgresql/[versão]/main/pg_hba.conf
```

### **3. Fazer backup:**

```bash
sudo cp /etc/postgresql/*/main/pg_hba.conf /etc/postgresql/*/main/pg_hba.conf.backup
```

### **4. Editar arquivo:**

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
# OU
sudo vi /etc/postgresql/*/main/pg_hba.conf
```

### **5. Encontrar a linha incompleta:**

Procure por:
```
host    meu_banco    meu_usuario    0.0.0.0/0
```

### **6. Completar a linha:**

Substitua:
```
host    meu_banco    meu_usuario    0.0.0.0/0
```

Por:
```
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

### **7. Salvar arquivo:**

- **Nano:** Ctrl+X, Y, Enter
- **Vi:** Esc, :wq, Enter

### **8. Verificar se a linha foi corrigida:**

```bash
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario
```

Deve mostrar:
```
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

### **9. Reiniciar PostgreSQL:**

```bash
sudo systemctl restart postgresql
```

### **10. Verificar se PostgreSQL está rodando:**

```bash
sudo systemctl status postgresql
```

---

## 🤖 Usar Script Automático

### **Opção 1: Executar script localmente no servidor**

```bash
# 1. Copiar script para o servidor
scp completar_pg_hba_scram.sh usuario@37.27.220.67:/tmp/

# 2. Conectar ao servidor
ssh usuario@37.27.220.67

# 3. Dar permissão de execução
chmod +x /tmp/completar_pg_hba_scram.sh

# 4. Executar com sudo
sudo bash /tmp/completar_pg_hba_scram.sh
```

### **Opção 2: Comandos diretos no servidor**

```bash
# Conectar ao servidor
ssh usuario@37.27.220.67

# Localizar arquivo
PG_HBA_FILE=$(sudo find /etc -name pg_hba.conf 2>/dev/null | head -1)

# Fazer backup
sudo cp "$PG_HBA_FILE" "${PG_HBA_FILE}.backup"

# Remover linha incompleta e adicionar linha completa
sudo sed -i '/^host[[:space:]]*meu_banco[[:space:]]*meu_usuario[[:space:]]*0\.0\.0\.0\/0[[:space:]]*$/d' "$PG_HBA_FILE"
echo "host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256" | sudo tee -a "$PG_HBA_FILE"

# Reiniciar PostgreSQL
sudo systemctl restart postgresql

# Verificar
sudo cat "$PG_HBA_FILE" | grep meu_usuario
```

---

## ✅ Verificação Final

### **1. Verificar linha no pg_hba.conf:**

```bash
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario
```

**Deve mostrar:**
```
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

### **2. Verificar se PostgreSQL está rodando:**

```bash
sudo systemctl status postgresql
```

### **3. Testar conexão localmente no servidor:**

```bash
psql -h localhost -U meu_usuario -d meu_banco
```

### **4. Testar conexão remotamente:**

```bash
# De sua máquina
python testar_conexao.py
```

---

## 🔒 Importante: Verificar Senha do Usuário

Se estiver usando `scram-sha-256`, certifique-se de que a senha do usuário está configurada corretamente:

```sql
# Conectar ao PostgreSQL como superusuário
sudo -u postgres psql

# Alterar senha do usuário
ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';

# Verificar usuário
SELECT usename FROM pg_user WHERE usename = 'meu_usuario';
```

---

## 📝 Exemplo Completo do pg_hba.conf

Após a correção, seu arquivo deve ter algo assim:

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     peer

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5

# IPv6 local connections:
host    all             all             ::1/128                  md5

# Conexões remotas - Permitir todas
host    all             all             0.0.0.0/0               scram-sha-256

# Conexões remotas - Permitir apenas meu_usuario no meu_banco
host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256
```

---

## 🆘 Troubleshooting

### **Erro: "password authentication failed" após correção**

- Verifique se a senha do usuário está correta:
  ```sql
  ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
  ```

### **Erro: "invalid authentication method"**

- Verifique se o PostgreSQL suporta `scram-sha-256` (PostgreSQL 10+)
- Se não suportar, use `md5` em vez de `scram-sha-256`

### **Conexão ainda não funciona**

- Verifique se reiniciou o PostgreSQL: `sudo systemctl restart postgresql`
- Verifique logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`
- Verifique se PostgreSQL está rodando: `sudo systemctl status postgresql`

---

**Última atualização:** 2025-01-27

