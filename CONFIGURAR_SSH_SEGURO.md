# 🔒 CONFIGURAR SSH SEGURO NO SERVIDOR

**Objetivo**: Desabilitar login root e autenticação por senha  
**⚠️ CRÍTICO**: Configurar chave SSH ANTES de desabilitar PasswordAuthentication!

---

## ⚠️ AVISO IMPORTANTE

**NÃO DESABILITE PasswordAuthentication SE:**
- ❌ Ainda não configurou chave SSH
- ❌ Não testou login com chave SSH
- ❌ Não tem acesso físico ao servidor

**Isso pode bloquear seu acesso permanentemente!**

---

## ✅ CHECKLIST ANTES DE CONFIGURAR

### **1. Verificar se já tem chave SSH configurada**

**No servidor:**
```bash
# Verificar se já existe arquivo authorized_keys
ls -la ~/.ssh/authorized_keys

# Se existir, mostrar conteúdo
cat ~/.ssh/authorized_keys
# Deve mostrar sua chave pública SSH
```

**Se NÃO existir**, configure chave SSH PRIMEIRO!

---

## 🔑 PASSO 1: CONFIGURAR CHAVE SSH (SE AINDA NÃO FEZ)

### **No seu PC Windows:**

```powershell
# 1. Verificar se já tem chave SSH
ls $env:USERPROFILE\.ssh\id_rsa.pub

# Se não existir, gerar:
ssh-keygen -t rsa -b 4096 -C "marabet@marabet.ao"
# Pressionar Enter para usar local padrão
# Pressionar Enter para senha vazia (ou definir senha)
```

### **Copiar chave para o servidor:**

```powershell
# Opção 1: Via ssh-copy-id (se disponível)
ssh-copy-id marabet@37.27.220.67

# Opção 2: Manual (recomendado)
# 1. Ver sua chave pública:
type $env:USERPROFILE\.ssh\id_rsa.pub

# 2. Copiar o conteúdo completo

# 3. No servidor, executar:
ssh marabet@37.27.220.67
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
# Colar a chave pública
# Salvar (Ctrl+O, Enter, Ctrl+X)
chmod 600 ~/.ssh/authorized_keys
```

### **Testar login com chave SSH:**

```powershell
# Do seu PC
ssh marabet@37.27.220.67

# Se funcionar SEM pedir senha = ✅ Chave SSH configurada!
# Se ainda pedir senha = ⚠️ Ainda não configurada
```

---

## 🔒 PASSO 2: CONFIGURAR SSH SEGURO

### **⚠️ IMPORTANTE: Testar PRIMEIRO!**

**Manter uma sessão SSH aberta enquanto configura** (em caso de erro, pode usar essa sessão)

### **1. Editar configuração SSH**

```bash
# No servidor
sudo nano /etc/ssh/sshd_config
```

### **2. Localizar e modificar estas linhas:**

```bash
# Procurar por estas linhas (Ctrl+W para buscar):

# PermitRootLogin yes
# Mudar para:
PermitRootLogin no

# PasswordAuthentication yes
# Mudar para (APENAS se chave SSH já funcionar!):
PasswordAuthentication no

# PubkeyAuthentication yes (deve estar descomentada)
# Se estiver comentada (#PubkeyAuthentication), descomentar:
PubkeyAuthentication yes
```

### **3. Verificar outras configurações importantes:**

```bash
# Estas linhas devem estar assim:
Port 22
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no  # APENAS após testar chave SSH!
AuthorizedKeysFile .ssh/authorized_keys
```

### **4. Salvar e testar configuração:**

```bash
# Testar sintaxe do arquivo SSH
sudo sshd -t

# Se retornar sem erros = ✅ Sintaxe OK
# Se retornar erro = ❌ Corrigir antes de continuar
```

### **5. Reiniciar serviço SSH:**

```bash
# Reiniciar SSH
sudo systemctl restart sshd

# Verificar status
sudo systemctl status sshd

# ✅ Serviço deve estar "active (running)"
```

---

## ✅ PASSO 3: TESTAR ACESSO

### **Abrir NOVA sessão SSH (sem fechar a atual!):**

```powershell
# Do seu PC, abrir novo terminal/PowerShell
ssh marabet@37.27.220.67

# Se funcionar sem pedir senha = ✅ Configuração OK!
# Se pedir senha e não aceitar = ⚠️ Problema!
```

### **Se funcionar:**

✅ Você pode fechar a sessão antiga  
✅ Login root está desabilitado  
✅ Autenticação por senha está desabilitada  
✅ Apenas chaves SSH funcionam  

### **Se NÃO funcionar:**

❌ **NÃO FECHE A SESSÃO SSH ATUAL!**  
❌ Use a sessão atual para reverter:

```bash
# Reverter configuração
sudo nano /etc/ssh/sshd_config
# Mudar PasswordAuthentication de volta para yes
sudo systemctl restart sshd
```

---

## 📋 CONFIGURAÇÃO RECOMENDADA COMPLETA

### **Conteúdo do `/etc/ssh/sshd_config`:**

```bash
# Porta SSH (padrão 22)
Port 22

# Desabilitar login root
PermitRootLogin no

# Autenticação por chave pública
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# Autenticação por senha (desabilitar APENAS após testar chave!)
PasswordAuthentication no

# Outras configurações de segurança
MaxAuthTries 3
MaxSessions 10
ClientAliveInterval 300
ClientAliveCountMax 2
```

---

## ✅ CHECKLIST FINAL

### **Antes de desabilitar PasswordAuthentication:**
- [ ] Chave SSH gerada no PC
- [ ] Chave copiada para ~/.ssh/authorized_keys no servidor
- [ ] Permissões corretas (700 em ~/.ssh, 600 em authorized_keys)
- [ ] Login com chave SSH testado e funcionando
- [ ] Pelo menos uma sessão SSH aberta como backup

### **Após configurar:**
- [ ] sshd -t passou sem erros
- [ ] SSH reiniciado (systemctl restart sshd)
- [ ] Nova sessão SSH testada
- [ ] Login funciona sem pedir senha
- [ ] Login root bloqueado (teste: ssh root@37.27.220.67 deve falhar)

---

## 🔄 REVERTER CONFIGURAÇÃO (SE NECESSÁRIO)

```bash
# Se perdeu acesso ou precisa reverter:

# Se ainda tiver uma sessão SSH aberta:
sudo nano /etc/ssh/sshd_config
# Mudar PasswordAuthentication para yes
sudo systemctl restart sshd

# Se perdeu acesso completamente:
# - Acessar via console do provedor (se disponível)
# - Ou contatar suporte do provedor
```

---

## 📝 RESUMO RÁPIDO

### **Ordem de execução:**

1. ✅ **PRIMEIRO**: Configurar chave SSH e testar
2. ✅ **SEGUNDO**: Editar sshd_config
3. ✅ **TERCEIRO**: Testar sintaxe (sshd -t)
4. ✅ **QUARTO**: Reiniciar SSH (systemctl restart sshd)
5. ✅ **QUINTO**: Testar nova conexão
6. ✅ **SEXTO**: Se funcionar, está seguro!

---

## ⚠️ CONFIGURAÇÃO SEGURA RECOMENDADA

**Opção 1: Configuração Gradual (Mais Segura)**
```bash
# Primeiro passo: Apenas desabilitar root
PermitRootLogin no
PasswordAuthentication yes  # Manter ativo por enquanto
# Testar, depois desabilitar PasswordAuthentication
```

**Opção 2: Configuração Completa (Após testar chave)**
```bash
PermitRootLogin no
PasswordAuthentication no  # APENAS se chave SSH funcionar!
```

---

**📄 Guia de Segurança**: Este arquivo  
**📧 Suporte**: suporte@marabet.ao  
**⚠️ IMPORTANTE**: Sempre manter uma sessão SSH aberta enquanto configura!

