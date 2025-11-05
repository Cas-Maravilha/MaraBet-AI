# ✅ CHECKLIST APÓS CONECTAR COMO MARABET

**Comando**: `ssh marabet@37.27.220.67`  
**Usuário**: marabet  
**Servidor**: 37.27.220.67

---

## 🔍 VERIFICAÇÕES INICIAIS

### **1. Verificar Usuário e Grupos**

```bash
# Ver usuário atual
whoami
# Deve mostrar: marabet

# Ver grupos
groups
# Deve mostrar: marabet sudo docker (se já adicionou ao docker)

# Se não tiver docker no grupo ainda:
sudo usermod -aG docker marabet
newgrp docker
```

### **2. Verificar Sistema**

```bash
# Versão do sistema
cat /etc/os-release

# Espaço em disco
df -h

# Memória
free -h

# CPU
nproc
```

---

## 📋 COMANDOS A EXECUTAR AGORA

### **1. Adicionar ao Grupo Docker (se ainda não fez)**

```bash
sudo usermod -aG docker marabet
newgrp docker  # Ativar grupo agora
groups  # Verificar se docker aparece
```

### **2. Criar Diretório da Aplicação**

```bash
sudo mkdir -p /opt/marabet
sudo chown marabet:marabet /opt/marabet
cd /opt/marabet
pwd  # Deve mostrar: /opt/marabet
```

### **3. Configurar Firewall**

```bash
sudo ufw --force enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 5432/tcp   # PostgreSQL (bloquear externamente)
sudo ufw status verbose
```

### **4. Verificar/Instalar Docker**

```bash
# Verificar se Docker está instalado
docker --version

# Se não estiver, instalar:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker marabet
newgrp docker

# Testar Docker
docker ps
# Deve retornar lista vazia (sem erros)
```

### **5. Instalar Docker Compose**

```bash
# Verificar se está instalado
docker-compose --version

# Se não estiver:
sudo apt install -y docker-compose

# Ou via pip:
sudo pip3 install docker-compose
```

### **6. Preparar para Receber Código**

```bash
# Garantir que tem permissão no diretório
cd /opt/marabet
ls -la
# Deve mostrar que você é o dono do diretório

# Criar subdiretórios necessários
mkdir -p backups logs static media
```

---

## 📤 ENVIAR CÓDIGO (DO SEU PC)

**Agora volte ao seu PC Windows e execute:**

```powershell
# Navegar para o projeto
cd "d:\Usuario\Maravilha\Desktop\MaraBet AI"

# Enviar arquivos essenciais primeiro
scp install_postgresql_secure.sh marabet@37.27.220.67:/tmp/
scp docker-compose.production.yml marabet@37.27.220.67:/opt/marabet/
scp config_production.env marabet@37.27.220.67:/opt/marabet/
scp app.py marabet@37.27.220.67:/opt/marabet/

# Enviar diretórios
scp -r api/ marabet@37.27.220.67:/opt/marabet/
scp -r models/ marabet@37.27.220.67:/opt/marabet/
scp -r migrations/ marabet@37.27.220.67:/opt/marabet/
scp -r static/ marabet@37.27.220.67:/opt/marabet/
scp -r templates/ marabet@37.27.220.67:/opt/marabet/

# Ou enviar tudo de uma vez (pode demorar):
scp -r * marabet@37.27.220.67:/opt/marabet/
```

---

## 🔄 VOLTAR AO SERVIDOR E CONTINUAR

**Após enviar código, voltar ao servidor:**

```bash
# Verificar se arquivos chegaram
cd /opt/marabet
ls -la

# Deve mostrar:
# - docker-compose.production.yml
# - config_production.env
# - app.py
# - api/
# - models/
# etc.
```

---

## ✅ CHECKLIST RÁPIDO

Execute na ordem:

- [ ] `whoami` → marabet
- [ ] `groups` → inclui sudo e docker
- [ ] `cd /opt/marabet` → diretório existe e tem permissão
- [ ] Firewall configurado (ufw)
- [ ] Docker instalado e funcionando
- [ ] Docker Compose instalado
- [ ] Código enviado do PC
- [ ] Arquivos verificados no servidor

---

## 📝 PRÓXIMOS PASSOS (Após Enviar Código)

1. **Instalar PostgreSQL** (usar script enviado)
2. **Configurar .env** (com credenciais do PostgreSQL)
3. **Instalar Nginx** (proxy reverso)
4. **Executar migrações**
5. **Iniciar aplicação**

Todos estão documentados em `PROXIMOS_PASSOS_POS_INSTALACAO.md`

---

**📄 Guia Completo**: `DEPLOY_EXECUTAR_AGORA.md`  
**📧 Suporte**: suporte@marabet.ao

