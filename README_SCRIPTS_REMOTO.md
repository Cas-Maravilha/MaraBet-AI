# 📋 Scripts de Configuração PostgreSQL para Servidor Remoto

Este conjunto de scripts automatiza a configuração completa do PostgreSQL para acesso remoto no servidor `37.27.220.67`.

## 🚀 Scripts Disponíveis

### 1️⃣ `INSTALAR_POSTGRESQL_REMOTO.sh`
**O que faz:**
- Instala PostgreSQL 14
- Configura usuário e banco de dados
- Executa configuração de acesso remoto

**Quando usar:**
- Quando o PostgreSQL ainda não está instalado no servidor remoto
- Para instalação completa do zero

**Como executar:**
```bash
sudo bash INSTALAR_POSTGRESQL_REMOTO.sh
```

---

### 2️⃣ `configurar_postgresql_remoto.sh`
**O que faz:**
- Configura `postgresql.conf` com `listen_addresses = '*'`
- Configura `pg_hba.conf` para permitir acesso remoto
- Cria/atualiza usuário e banco de dados
- Configura firewall (UFW)
- Reinicia PostgreSQL
- Verifica configuração

**Quando usar:**
- Quando PostgreSQL já está instalado
- Para configurar acesso remoto

**Como executar:**
```bash
sudo bash configurar_postgresql_remoto.sh
```

---

### 3️⃣ `verificar_configuracao_postgresql.sh`
**O que faz:**
- Verifica status do serviço PostgreSQL
- Verifica porta 5432
- Verifica configurações de arquivos
- Verifica firewall
- Testa conexão local

**Quando usar:**
- Para verificar se tudo está configurado corretamente
- Para diagnóstico de problemas

**Como executar:**
```bash
sudo bash verificar_configuracao_postgresql.sh
```

---

## 📥 Como Transferir Scripts para o Servidor Remoto

### Opção 1: SCP (via SSH)
```bash
scp *.sh usuario@37.27.220.67:/home/usuario/
```

### Opção 2: Git (se o servidor tiver git)
```bash
# No servidor remoto
git clone [seu-repositorio]
cd MaraBet\ AI
```

### Opção 3: Copiar e colar
1. Abra cada script no editor
2. Copie o conteúdo
3. Cole no servidor remoto via SSH
4. Salve como `.sh`
5. Torne executável: `chmod +x script.sh`

---

## 🔧 Passo a Passo de Instalação no Servidor Remoto

### 1. Conectar ao servidor remoto
```bash
ssh usuario@37.27.220.67
```

### 2. Transferir os scripts
```bash
# Usando scp do seu computador
scp *.sh usuario@37.27.220.67:~/
```

### 3. Tornar scripts executáveis
```bash
chmod +x *.sh
```

### 4. Executar instalação (se necessário)
```bash
sudo bash INSTALAR_POSTGRESQL_REMOTO.sh
```

OU

### 4. Executar apenas configuração (se já instalado)
```bash
sudo bash configurar_postgresql_remoto.sh
```

### 5. Verificar configuração
```bash
sudo bash verificar_configuracao_postgresql.sh
```

---

## ✅ Verificação Final

Após executar os scripts, verifique:

1. **PostgreSQL está escutando externamente:**
   ```bash
   sudo ss -tlnp | grep 5432
   ```
   **Deve mostrar:** `0.0.0.0:5432`

2. **Teste de conectividade do seu computador:**
   ```powershell
   Test-NetConnection -ComputerName 37.27.220.67 -Port 5432
   ```
   **Deve mostrar:** `TcpTestSucceeded: True`

3. **Teste de conexão Python:**
   ```bash
   python testar_conexao_postgres.py
   ```

---

## 🔒 Configurações Aplicadas

### postgresql.conf
```conf
listen_addresses = '*'
```

### pg_hba.conf
```conf
host    marabet    meu_root$marabet    0.0.0.0/0    scram-sha-256
host    marabet    meu_root$marabet    ::/0         scram-sha-256
```

### Firewall (UFW)
```bash
ufw allow 5432/tcp
```

---

## 📋 Dados de Conexão Configurados

```
Host: 37.27.220.67
Porta: 5432
Database: marabet
User: meu_root$marabet
Password: YOUR_DATABASE_PASSWORD
```

---

## ⚠️ Segurança

**IMPORTANTE:**
- Os scripts configuram acesso de qualquer IP (`0.0.0.0/0`)
- Para maior segurança, restrinja por IP específico no `pg_hba.conf`:
  ```conf
  host    marabet    meu_root$marabet    SEU_IP_ESPECIFICO/32    scram-sha-256
  ```

---

## 🐛 Solução de Problemas

### PostgreSQL não inicia
```bash
sudo systemctl status postgresql
sudo journalctl -xe
```

### Porta não acessível
1. Verificar firewall: `sudo ufw status`
2. Verificar se está escutando: `sudo ss -tlnp | grep 5432`
3. Verificar `postgresql.conf`: `grep listen_addresses`

### Conexão recusada
1. Verificar `pg_hba.conf`
2. Verificar se usuário/banco existe
3. Verificar logs: `sudo tail -f /var/log/postgresql/postgresql-14-main.log`

---

## 📞 Suporte

Se encontrar problemas:
1. Execute: `sudo bash verificar_configuracao_postgresql.sh`
2. Verifique os logs do PostgreSQL
3. Verifique firewall e conectividade de rede

