# 🔑 CRIAR KEY PAIR AWS - GUIA COMPLETO

**Sistema**: MaraBet AI  
**Key Name**: marabet-key  
**Região**: eu-west-1

---

## 📋 ÍNDICE

1. [Criar Key Pair](#1-criar-key-pair)
2. [Configurar Permissões](#2-configurar-permissões)
3. [Testar Key](#3-testar-key)
4. [Usar com EC2](#4-usar-com-ec2)
5. [Troubleshooting](#5-troubleshooting)

---

## 1️⃣ CRIAR KEY PAIR

### **Via AWS CLI:**

```bash
# Criar key pair e salvar
aws ec2 create-key-pair \
  --key-name marabet-key \
  --query 'KeyMaterial' \
  --output text \
  --region eu-west-1 > marabet-key.pem

# Verificar se foi criado
ls -lah marabet-key.pem
```

**Resultado Esperado:**
```
-rw-r--r-- 1 user user 1.7K Oct 27 12:30 marabet-key.pem
```

### **Verificar na AWS:**

```bash
# Listar key pairs
aws ec2 describe-key-pairs \
  --key-names marabet-key \
  --region eu-west-1

# Resultado
# {
#     "KeyPairs": [
#         {
#             "KeyPairId": "key-xxxxxxxxxxxxx",
#             "KeyFingerprint": "xx:xx:xx:...",
#             "KeyName": "marabet-key",
#             "KeyType": "rsa",
#             "Tags": []
#         }
#     ]
# }
```

---

## 2️⃣ CONFIGURAR PERMISSÕES

### **A. Linux / macOS:**

```bash
# Definir permissões corretas
chmod 400 marabet-key.pem

# Verificar
ls -l marabet-key.pem
# Resultado: -r-------- 1 user user 1706 Oct 27 12:30 marabet-key.pem

# Testar permissões
stat -c "%a %n" marabet-key.pem
# Resultado: 400 marabet-key.pem
```

### **B. Windows (PowerShell como Admin):**

```powershell
# Método 1: Via PowerShell
$path = ".\marabet-key.pem"

# Remover herança
$acl = Get-Acl $path
$acl.SetAccessRuleProtection($true, $false)
Set-Acl $path $acl

# Remover todos os usuários
$acl = Get-Acl $path
$acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) }

# Adicionar apenas usuário atual
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule($user, "Read", "Allow")
$acl.SetAccessRule($rule)
Set-Acl $path $acl

Write-Host "✅ Permissões configuradas!"
```

### **C. Windows (Interface Gráfica):**

```
1. Clicar com botão direito em marabet-key.pem
2. Propriedades
3. Aba "Segurança"
4. Botão "Avançado"
5. Desabilitar herança
   • Escolher "Remover todas as permissões herdadas"
6. Adicionar permissão apenas para seu usuário
   • Adicionar → Selecionar um principal → Seu usuário
   • Permissões básicas: Leitura ✓
   • OK
7. Aplicar → OK
```

### **Verificar Permissões Windows:**

```powershell
# Ver ACL
Get-Acl marabet-key.pem | Format-List

# Ou
icacls marabet-key.pem
```

---

## 3️⃣ TESTAR KEY

### **Verificar Conteúdo:**

```bash
# Ver início da chave
head -n 5 marabet-key.pem

# Resultado esperado:
# -----BEGIN RSA PRIVATE KEY-----
# MIIEowIBAAKCAQEA...
# ...
```

### **Verificar Fingerprint:**

```bash
# Calcular fingerprint local
ssh-keygen -l -f marabet-key.pem

# Comparar com AWS
aws ec2 describe-key-pairs \
  --key-names marabet-key \
  --region eu-west-1 \
  --query 'KeyPairs[0].KeyFingerprint' \
  --output text
```

---

## 4️⃣ USAR COM EC2

### **Ao Criar EC2:**

```bash
# Especificar key pair
aws ec2 run-instances \
  --key-name marabet-key \
  --image-id ami-xxxxx \
  --instance-type t3.large \
  ...
```

### **Conectar via SSH:**

```bash
# Obter IP público da EC2
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids i-xxxxxxxxxxxxx \
  --region eu-west-1 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

# Conectar
ssh -i marabet-key.pem ubuntu@$PUBLIC_IP

# Se der erro de permissões
chmod 400 marabet-key.pem
ssh -i marabet-key.pem ubuntu@$PUBLIC_IP
```

### **Windows (usar Git Bash ou WSL):**

```bash
# Git Bash
ssh -i marabet-key.pem ubuntu@$PUBLIC_IP

# Ou usar PuTTY:
# 1. Converter .pem para .ppk com PuTTYgen
# 2. Usar .ppk no PuTTY
```

---

## 5️⃣ TROUBLESHOOTING

### **Erro: "Permissions 0644 are too open"**

```bash
# Solução
chmod 400 marabet-key.pem
```

### **Erro: "WARNING: UNPROTECTED PRIVATE KEY FILE!"**

```bash
# Linux/macOS
chmod 400 marabet-key.pem

# Windows (PowerShell como Admin)
icacls marabet-key.pem /inheritance:r
icacls marabet-key.pem /grant:r "$env:USERNAME:(R)"
```

### **Erro: "No supported authentication methods available"**

```bash
# Verifique o usuário correto
# Ubuntu AMI usa 'ubuntu'
ssh -i marabet-key.pem ubuntu@$PUBLIC_IP

# Não use 'root' ou 'ec2-user' para Ubuntu
```

### **Erro: "Connection refused" ou "Connection timed out"**

```bash
# 1. Verificar Security Group permite SSH
aws ec2 describe-security-groups \
  --group-ids $SG_EC2 \
  --region eu-west-1 \
  --query 'SecurityGroups[0].IpPermissions[?FromPort==`22`]'

# 2. Verificar se EC2 está running
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --region eu-west-1 \
  --query 'Reservations[0].Instances[0].State.Name'

# 3. Verificar se IP público existe
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --region eu-west-1 \
  --query 'Reservations[0].Instances[0].PublicIpAddress'
```

### **Perdi a chave marabet-key.pem:**

```bash
# Opção 1: Criar nova key pair com nome diferente
aws ec2 create-key-pair \
  --key-name marabet-key-2 \
  --query 'KeyMaterial' \
  --output text > marabet-key-2.pem

chmod 400 marabet-key-2.pem

# Opção 2: Deletar antiga e criar nova
aws ec2 delete-key-pair --key-name marabet-key --region eu-west-1
aws ec2 create-key-pair --key-name marabet-key --query 'KeyMaterial' --output text > marabet-key.pem
chmod 400 marabet-key.pem

# ⚠️ Atenção: EC2s existentes continuarão usando a chave antiga
# Você não poderá acessar EC2s criadas com a chave perdida
```

---

## 🔒 SEGURANÇA

### **Boas Práticas:**

1. **Nunca compartilhar** marabet-key.pem
2. **Nunca fazer commit** no Git (.gitignore)
3. **Fazer backup** em local seguro
4. **Permissões 400** sempre (somente leitura pelo dono)
5. **Rotacionar** a cada 90 dias
6. **Usar Key diferente** para cada ambiente

### **Backup Seguro:**

```bash
# Fazer backup criptografado
gpg -c marabet-key.pem
# Gera: marabet-key.pem.gpg

# Restaurar
gpg -d marabet-key.pem.gpg > marabet-key.pem
chmod 400 marabet-key.pem
```

---

## 📝 COMANDOS ÚTEIS

### **Listar Key Pairs:**

```bash
aws ec2 describe-key-pairs --region eu-west-1
```

### **Deletar Key Pair:**

```bash
aws ec2 delete-key-pair \
  --key-name marabet-key \
  --region eu-west-1
```

### **Criar Multiple Keys:**

```bash
# Produção
aws ec2 create-key-pair --key-name marabet-prod-key --query 'KeyMaterial' --output text > marabet-prod.pem

# Desenvolvimento
aws ec2 create-key-pair --key-name marabet-dev-key --query 'KeyMaterial' --output text > marabet-dev.pem

# Staging
aws ec2 create-key-pair --key-name marabet-staging-key --query 'KeyMaterial' --output text > marabet-staging.pem
```

---

## 🔧 USAR KEY PAIR

### **Script de Conexão:**

```bash
#!/bin/bash
# ssh-marabet.sh

KEY_FILE="marabet-key.pem"
EC2_IP="<IP_PUBLICO_EC2>"

# Verificar permissões
if [ $(stat -c %a $KEY_FILE 2>/dev/null || stat -f %A $KEY_FILE) != "400" ]; then
    echo "⚠️  Ajustando permissões..."
    chmod 400 $KEY_FILE
fi

# Conectar
echo "🔐 Conectando ao MaraBet EC2..."
echo "IP: $EC2_IP"
echo ""

ssh -i $KEY_FILE ubuntu@$EC2_IP

# Salvar como ssh-marabet.sh
# chmod +x ssh-marabet.sh
# ./ssh-marabet.sh
```

### **Config SSH (~/.ssh/config):**

```bash
# Adicionar ao ~/.ssh/config
Host marabet
    HostName <IP_PUBLICO_EC2>
    User ubuntu
    IdentityFile ~/caminho/para/marabet-key.pem
    ServerAliveInterval 60

# Conectar simplesmente com
ssh marabet
```

---

## ✅ CHECKLIST

- [ ] Key pair criada via AWS CLI
- [ ] Arquivo marabet-key.pem salvo
- [ ] Permissões configuradas (400)
- [ ] Backup da chave feito
- [ ] Key pair verificada na AWS
- [ ] Fingerprint conferido
- [ ] Testada com EC2 (após criar)
- [ ] Adicionada ao .gitignore
- [ ] Backup em local seguro

---

## 📞 PRÓXIMOS PASSOS

1. ✅ Key Pair criada
2. **Criar EC2**: `./criar_ec2_marabet.sh`
3. **SSH na EC2**: `ssh -i marabet-key.pem ubuntu@<IP>`
4. **Deploy**: Aplicação MaraBet

---

**🔑 Key Pair Pronta!**  
**🔒 Permissões Seguras**  
**✅ Pronta para Usar com EC2**  
**☁️ MaraBet AI - AWS SSH Key**

