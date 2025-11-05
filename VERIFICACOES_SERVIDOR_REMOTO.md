# Verificações no Servidor Remoto (37.27.220.67)

## 🔍 Diagnóstico do Problema

**Teste de conectividade:**
- ✅ Servidor online (Ping funciona)
- ❌ Porta 5432 bloqueada/não acessível

## 📋 Comandos para executar no servidor remoto (37.27.220.67)

### 1️⃣ Verificar se PostgreSQL está em execução

```bash
sudo systemctl status postgresql
```

### 2️⃣ Verificar se está escutando na porta 5432

```bash
sudo ss -tlnp | grep 5432
# ou
sudo netstat -plnt | grep 5432
```

**Deve mostrar:** `0.0.0.0:5432` (escutando em todas as interfaces)

### 3️⃣ Verificar configuração postgresql.conf

```bash
sudo grep "^listen_addresses" /etc/postgresql/14/main/postgresql.conf
```

**Deve mostrar:** `listen_addresses = '*'`

### 4️⃣ Verificar pg_hba.conf para acesso remoto

```bash
sudo grep -v "^#" /etc/postgresql/14/main/pg_hba.conf | grep -v "^$"
```

**Deve ter regras permitindo conexões remotas**

### 5️⃣ Verificar firewall (UFW)

```bash
sudo ufw status
```

**Se o firewall estiver ativo, permitir porta 5432:**
```bash
sudo ufw allow 5432/tcp
sudo ufw reload
```

### 6️⃣ Verificar firewall do sistema (iptables)

```bash
sudo iptables -L -n | grep 5432
```

**Se necessário, permitir porta:**
```bash
sudo iptables -A INPUT -p tcp --dport 5432 -j ACCEPT
```

### 7️⃣ Verificar se PostgreSQL aceita conexões

```bash
sudo -u postgres psql -c "SHOW listen_addresses;"
```

## ✅ Configuração Completa Necessária

No servidor remoto, você precisa:

1. **postgresql.conf:**
   ```conf
   listen_addresses = '*'
   ```

2. **pg_hba.conf:**
   ```conf
   host    marabet    meu_root$marabet    0.0.0.0/0    scram-sha-256
   ```

3. **Firewall:**
   ```bash
   sudo ufw allow 5432/tcp
   ```

4. **Reiniciar PostgreSQL:**
   ```bash
   sudo systemctl restart postgresql
   ```

## 🔒 Segurança

⚠️ **IMPORTANTE:** Permitir conexões de qualquer IP (`0.0.0.0/0`) é menos seguro.

**Para maior segurança, restrinja a IPs específicos no pg_hba.conf:**
```conf
host    marabet    meu_root$marabet    SEU_IP_ESPECIFICO/32    scram-sha-256
```

