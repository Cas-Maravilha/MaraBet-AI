# 🐳 INSTALAÇÃO OFICIAL DO DOCKER - UBUNTU 22.04

**Método**: Repositório oficial Docker  
**Vantagem**: Versão mais recente e atualizações automáticas

---

## ✅ COMANDOS PARA INSTALAR DOCKER

### **1. Preparar Dependências**

```bash
sudo apt install -y ca-certificates gnupg lsb-release
```

### **2. Adicionar Chave GPG do Docker**

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

### **3. Adicionar Repositório Docker**

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### **4. Instalar Docker**

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### **5. Adicionar Usuário ao Grupo Docker**

```bash
# Adicionar usuário marabet ao grupo docker
sudo usermod -aG docker marabet

# Ativar grupo imediatamente
newgrp docker

# OU fazer logout e login novamente
```

---

## ✅ VERIFICAÇÕES

### **Verificar Instalação**

```bash
# Verificar versão do Docker
docker --version
# Deve mostrar: Docker version 24.x.x ou superior

# Verificar Docker Compose Plugin
docker compose version
# Deve mostrar: Docker Compose version v2.x.x

# Testar Docker (sem sudo)
docker ps
# Deve retornar lista vazia (sem erros de permissão)

# Testar Docker Compose
docker compose version
```

### **Verificar Grupos**

```bash
# Ver grupos do usuário
groups
# Deve mostrar: marabet sudo docker

# Verificar que docker funciona sem sudo
docker run hello-world
# Deve baixar e executar imagem de teste
```

---

## 🔧 DOCKER COMPOSE - USO

### **Com Docker Compose Plugin (v2):**

```bash
# Formato novo (recomendado)
docker compose -f docker-compose.production.yml up -d

# Ver status
docker compose ps

# Ver logs
docker compose logs -f
```

### **OU com docker-compose standalone (se instalado separadamente):**

```bash
# Formato antigo (também funciona)
docker-compose -f docker-compose.production.yml up -d

# Ver status
docker-compose ps
```

**Ambos funcionam! Use o que preferir.**

---

## ✅ APÓS INSTALAR DOCKER

### **Próximos Passos:**

1. ✅ Docker instalado
2. ⏳ Verificar instalação
3. ⏳ Testar Docker (docker ps)
4. ⏳ Criar script PostgreSQL (se ainda não fez)
5. ⏳ Instalar PostgreSQL
6. ⏳ Instalar Nginx
7. ⏳ Enviar código da aplicação

---

## 🐛 TROUBLESHOOTING

### **Erro: docker: permission denied**

```bash
# Adicionar ao grupo novamente
sudo usermod -aG docker marabet

# Ativar grupo
newgrp docker

# Ou fazer logout e login
exit
ssh marabet@37.27.220.67
```

### **Erro: Cannot connect to Docker daemon**

```bash
# Verificar se Docker está rodando
sudo systemctl status docker

# Se não estiver, iniciar
sudo systemctl start docker
sudo systemctl enable docker
```

### **Erro: docker compose não encontrado**

```bash
# Verificar se plugin está instalado
docker compose version

# Se não estiver, instalar separadamente:
sudo apt install -y docker-compose

# Ou usar docker-compose (com hífen)
docker-compose --version
```

---

## 📋 RESUMO RÁPIDO

```bash
# Sequência completa:
sudo apt install -y ca-certificates gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker marabet
newgrp docker

# Verificar
docker --version
docker compose version
docker ps
```

---

## ✅ CHECKLIST

- [ ] Dependências instaladas
- [ ] Chave GPG adicionada
- [ ] Repositório Docker adicionado
- [ ] Docker instalado (docker-ce, docker-ce-cli, containerd.io)
- [ ] Docker Compose Plugin instalado
- [ ] Usuário adicionado ao grupo docker
- [ ] Docker funciona sem sudo
- [ ] Docker Compose funciona

---

**📄 Guias Relacionados:**
- `DEPLOY_SEQUENCIA_COMPLETA.md` - Sequência completa
- `APOS_CONFIGURACAO_INICIAL.md` - Próximos passos

**📧 Suporte**: suporte@marabet.ao

