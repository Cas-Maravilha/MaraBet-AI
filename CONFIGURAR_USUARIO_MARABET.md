# 👤 CONFIGURAR USUÁRIO MARABET NO SERVIDOR

**Servidor**: marabet.ao (37.27.220.67)  
**Usuário**: marabet  
**Grupo**: sudo (privilegiado)

---

## ✅ USUÁRIO CRIADO

```bash
✅ Usuário: marabet
✅ Grupo sudo: Ativado
✅ Acesso: Pode executar comandos sudo
```

---

## 🔐 CONFIGURAÇÕES ADICIONAIS

### **1. Configurar Senha (se ainda não configurada)**

```bash
# Definir senha para o usuário marabet
passwd marabet

# Ou permitir login sem senha (menos seguro, usar chave SSH)
```

### **2. Configurar Chave SSH (Recomendado)**

**Do seu PC, gerar chave SSH:**
```powershell
# Gerar chave SSH (se ainda não tiver)
ssh-keygen -t rsa -b 4096 -C "marabet@marabet.ao"

# Copiar chave pública para o servidor
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh root@37.27.220.67 "cat >> /home/marabet/.ssh/authorized_keys"

# Ou manualmente:
# 1. Copiar conteúdo de ~/.ssh/id_rsa.pub
# 2. No servidor: nano /home/marabet/.ssh/authorized_keys
# 3. Colar a chave pública
```

**No servidor:**
```bash
# Criar diretório .ssh
mkdir -p /home/marabet/.ssh
chmod 700 /home/marabet/.ssh

# Editar arquivo authorized_keys
nano /home/marabet/.ssh/authorized_keys
# Colar chave pública SSH do seu PC

# Ajustar permissões
chmod 600 /home/marabet/.ssh/authorized_keys
chown -R marabet:marabet /home/marabet/.ssh
```

### **3. Adicionar ao Grupo Docker (Importante!)**

```bash
# Adicionar usuário marabet ao grupo docker
usermod -aG docker marabet

# Verificar grupos
groups marabet
# Deve mostrar: marabet sudo docker
```

### **4. Configurar Diretório Home**

```bash
# Criar diretório para aplicação
mkdir -p /opt/marabet
chown marabet:marabet /opt/marabet

# Ou usar diretório home
mkdir -p /home/marabet/marabet
```

### **5. Configurar Permissões para PostgreSQL**

```bash
# Criar diretório para backups
mkdir -p /opt/marabet/backups
chown marabet:marabet /opt/marabet/backups

# Dar permissão para executar comandos PostgreSQL (se necessário)
# usuário marabet pode usar 'sudo' para comandos administrativos
```

---

## 🔄 MUDAR DE ROOT PARA USUÁRIO MARABET

### **Opção 1: Fazer Logout e Login Novamente**

```bash
# Fazer logout
exit

# Conectar como usuário marabet
ssh marabet@37.27.220.67

# Ou do seu PC:
ssh marabet@37.27.220.67
```

### **Opção 2: Trocar de Usuário no SSH Atual**

```bash
# Se estiver como root, trocar para marabet
su - marabet

# Ou
su marabet
```

---

## ✅ VERIFICAÇÕES

```bash
# Verificar usuário atual
whoami
# Deve mostrar: marabet

# Verificar grupos
groups
# Deve mostrar: marabet sudo docker

# Testar sudo
sudo whoami
# Deve mostrar: root (pedir senha)

# Testar docker (sem sudo, se configurado)
docker ps
# Deve funcionar sem sudo
```

---

## 📋 COMANDOS ATUALIZADOS COM USUÁRIO MARABET

### **Instalações (precisam de sudo):**

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar pacotes
sudo apt install -y curl wget git ufw fail2ban htop vim

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker marabet

# Instalar Nginx
sudo apt install -y nginx certbot python3-certbot-nginx

# Firewall (precisa sudo)
sudo ufw --force enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### **Comandos sem sudo:**

```bash
# Docker (após adicionar ao grupo)
docker ps
docker-compose up -d

# Git
git clone ...
git pull

# Python/pip
python3 migrate.py
pip3 install package

# Criação de diretórios pessoais
mkdir -p ~/marabet
cd ~/marabet
```

---

## 🔒 SEGURANÇA

### **Desabilitar Login Root (Recomendado após configurar tudo)**

```bash
# Editar SSH config
sudo nano /etc/ssh/sshd_config

# Adicionar ou modificar:
PermitRootLogin no
PasswordAuthentication no  # Se usar chaves SSH

# Reiniciar SSH
sudo systemctl restart sshd

# IMPORTANTE: Testar login como marabet ANTES de fazer isso!
# Caso contrário, pode perder acesso ao servidor!
```

---

## 📝 RESUMO

### **Status Atual:**
```
✅ Usuário: marabet criado
✅ Grupo sudo: Adicionado
⏳ Chave SSH: Configurar (recomendado)
⏳ Grupo docker: Adicionar (usermod -aG docker marabet)
⏳ Diretório: /opt/marabet (dar permissão)
```

### **Próximos Passos:**
1. Adicionar ao grupo docker: `sudo usermod -aG docker marabet`
2. Configurar chave SSH (recomendado)
3. Criar diretórios necessários
4. Continuar com instalação do PostgreSQL e Docker

---

## 🔄 ATUALIZAÇÃO DE COMANDOS

### **Antes (como root):**
```bash
apt install -y docker
docker ps
```

### **Agora (como marabet):**
```bash
sudo apt install -y docker
sudo usermod -aG docker marabet
newgrp docker  # Ou logout/login
docker ps  # Sem sudo!
```

---

**📄 Guias Relacionados:**
- `DEPLOY_EXECUTAR_AGORA.md` - Deploy completo
- `PROXIMOS_PASSOS_POS_INSTALACAO.md` - Próximos passos

**📧 Suporte**: suporte@marabet.ao

