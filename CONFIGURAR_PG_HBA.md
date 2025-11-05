# 🔧 Configurar pg_hba.conf para Conexões Remotas

## 📋 Linha a Adicionar no pg_hba.conf

```conf
host    meu_banco    meu_usuario    0.0.0.0/0    md5
```

---

## 🚀 Passo a Passo

### **1. Localizar o arquivo pg_hba.conf:**

```bash
# Conectar ao servidor
ssh usuario@37.27.220.67

# Localizar arquivo
sudo find /etc -name pg_hba.conf

# Geralmente está em:
# /etc/postgresql/[versão]/main/pg_hba.conf
# Exemplo: /etc/postgresql/15/main/pg_hba.conf
```

### **2. Fazer backup do arquivo:**

```bash
sudo cp /etc/postgresql/*/main/pg_hba.conf /etc/postgresql/*/main/pg_hba.conf.backup
```

### **3. Editar o arquivo:**

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
# OU
sudo vi /etc/postgresql/*/main/pg_hba.conf
```

### **4. Adicionar a linha no final do arquivo:**

```conf
# Permitir conexões remotas para meu_usuario
host    meu_banco    meu_usuario    0.0.0.0/0    md5
```

**OU para permitir de qualquer database:**

```conf
# Permitir conexões remotas para meu_usuario em qualquer database
host    all    meu_usuario    0.0.0.0/0    md5
```

### **5. Verificar se a linha foi adicionada:**

```bash
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario
```

Deve mostrar:
```
host    meu_banco    meu_usuario    0.0.0.0/0    md5
```

### **6. Reiniciar PostgreSQL:**

```bash
sudo systemctl restart postgresql
# OU
sudo service postgresql restart
```

### **7. Verificar se PostgreSQL está rodando:**

```bash
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
# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     peer
host    replication     all             127.0.0.1/32            md5
host    replication     all             ::1/128                  md5

# ADICIONE ESTA LINHA PARA CONEXÕES REMOTAS:
host    meu_banco    meu_usuario    0.0.0.0/0    md5
```

---

## 🔒 Opções de Segurança

### **Opção 1: Permitir apenas de IP específico (Mais Seguro)**

```conf
# Permitir apenas de um IP específico
host    meu_banco    meu_usuario    192.168.1.100/32    md5

# OU permitir de uma rede local
host    meu_banco    meu_usuario    192.168.1.0/24    md5
```

### **Opção 2: Permitir de qualquer IP (Menos Seguro, mas Funcional)**

```conf
# Permitir de qualquer IP
host    meu_banco    meu_usuario    0.0.0.0/0    md5
```

### **Opção 3: Permitir para qualquer database (Menos Seguro)**

```conf
# Permitir para qualquer database
host    all    meu_usuario    0.0.0.0/0    md5
```

---

## ✅ Verificar Configuração

### **1. Verificar se a linha existe:**

```bash
sudo grep meu_usuario /etc/postgresql/*/main/pg_hba.conf
```

### **2. Verificar sintaxe do arquivo:**

```bash
sudo -u postgres psql -c "SHOW hba_file"
```

### **3. Testar conexão localmente no servidor:**

```bash
# Deve funcionar
psql -h localhost -U meu_usuario -d meu_banco
```

### **4. Testar conexão remotamente:**

```bash
# De sua máquina
python testar_conexao.py
```

---

## 🆘 Troubleshooting

### **Erro: "pg_hba.conf: line X: syntax error"**

- Verifique se não há espaços extras ou caracteres especiais
- Verifique se a linha está no formato correto
- Certifique-se de que não há linhas duplicadas

### **Erro: "Connection refused" após reiniciar**

- Verifique se PostgreSQL está rodando: `sudo systemctl status postgresql`
- Verifique logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`

### **Erro: "Password authentication failed" mesmo após configuração**

- Verifique se a senha do usuário está correta: `ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';`
- Verifique se o usuário existe: `SELECT usename FROM pg_user WHERE usename = 'meu_usuario';`
- Verifique se reiniciou o PostgreSQL após alterações

### **Conexão local funciona mas remota não**

- Verifique `listen_addresses` no `postgresql.conf`: deve ser `'*'` ou o IP do servidor
- Verifique firewall: `sudo ufw status` ou `sudo iptables -L`
- Verifique se a porta 5432 está aberta: `sudo netstat -tlnp | grep 5432`

---

## 📋 Checklist Final

- [ ] Backup do `pg_hba.conf` criado
- [ ] Linha adicionada no `pg_hba.conf`
- [ ] Sintaxe verificada
- [ ] PostgreSQL reiniciado
- [ ] PostgreSQL está rodando
- [ ] Conexão local testada (funciona)
- [ ] Conexão remota testada (funciona)

---

**Última atualização:** 2025-01-27

