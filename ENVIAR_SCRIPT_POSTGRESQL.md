# 📤 ENVIAR SCRIPT POSTGRESQL AO SERVIDOR

**Arquivo**: `install_postgresql_secure.sh`  
**Destino**: `/tmp/` no servidor 37.27.220.67

---

## 🔄 OPÇÕES PARA ENVIAR O ARQUIVO

### **Opção 1: SCP (Recomendado)**

**Do seu PC Windows (PowerShell):**
```powershell
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"

# Enviar script
scp install_postgresql_secure.sh marabet@37.27.220.67:/tmp/

# Se pedir senha, digite a senha do usuário marabet
# Se usar chave SSH, não pedirá senha
```

### **Opção 2: Criar Script no Servidor**

**No servidor (via SSH), criar manualmente:**

```bash
# Criar arquivo
sudo nano /tmp/install_postgresql_secure.sh

# Copiar e colar o conteúdo do arquivo install_postgresql_secure.sh
# (Você pode abrir o arquivo no seu PC e copiar todo o conteúdo)

# Salvar (Ctrl+O, Enter, Ctrl+X)

# Dar permissão
chmod +x /tmp/install_postgresql_secure.sh
```

### **Opção 3: Via Git (se usar Git)**

```bash
# No servidor
cd /tmp
git clone [seu-repositorio] temp_repo
cp temp_repo/install_postgresql_secure.sh /tmp/
chmod +x /tmp/install_postgresql_secure.sh
rm -rf temp_repo
```

### **Opção 4: Via Transferência Manual**

1. Abrir `install_postgresql_secure.sh` no seu PC
2. Copiar todo o conteúdo
3. No servidor, executar:
```bash
sudo nano /tmp/install_postgresql_secure.sh
# Colar o conteúdo
# Salvar (Ctrl+O, Enter, Ctrl+X)
chmod +x /tmp/install_postgresql_secure.sh
```

---

## ✅ APÓS ENVIAR O ARQUIVO

**No servidor, verificar:**

```bash
# Verificar se arquivo existe
ls -la /tmp/install_postgresql_secure.sh

# Verificar permissão
ls -l /tmp/install_postgresql_secure.sh
# Deve mostrar: -rwxr-xr-x (executável)

# Se não tiver permissão de execução:
chmod +x /tmp/install_postgresql_secure.sh
```

---

## 🚀 EXECUTAR INSTALAÇÃO

**No servidor:**

```bash
# Executar script (precisa sudo)
sudo /tmp/install_postgresql_secure.sh

# O script irá:
# ✅ Instalar PostgreSQL 15
# ✅ Criar banco 'marabet'
# ✅ Criar usuário 'marabet_user'
# ✅ Gerar senha forte
# ✅ Configurar segurança
# ✅ Salvar credenciais em /opt/marabet/.env.db

# Ver credenciais geradas
cat /opt/marabet/.env.db

# Verificar PostgreSQL
sudo systemctl status postgresql

# Testar conexão
psql -h localhost -U marabet_user -d marabet -c "SELECT 1;"
```

---

## 🐛 TROUBLESHOOTING

### **Erro: Arquivo não encontrado**
```bash
# Verificar se arquivo existe
ls -la /tmp/install_postgresql_secure.sh

# Se não existir, tentar outra opção acima
```

### **Erro: Permissão negada**
```bash
# Dar permissão de execução
chmod +x /tmp/install_postgresql_secure.sh

# Tentar executar novamente
sudo /tmp/install_postgresql_secure.sh
```

### **Erro SCP: Connection refused**
```bash
# Verificar se SSH está ativo no servidor
# No servidor:
sudo systemctl status sshd

# Verificar firewall
sudo ufw status
# Porta 22 deve estar permitida
```

---

## 📋 RESUMO RÁPIDO

**1. Enviar arquivo (qualquer opção acima)**

**2. No servidor:**
```bash
chmod +x /tmp/install_postgresql_secure.sh
sudo /tmp/install_postgresql_secure.sh
cat /opt/marabet/.env.db
```

**3. Copiar credenciais do PostgreSQL para o arquivo .env**

---

**📄 Script local**: `install_postgresql_secure.sh`  
**📧 Suporte**: suporte@marabet.ao

