# 🌐 INFORMAÇÕES DNS REVERSO DO SERVIDOR

**Servidor**: marabet.ao (37.27.220.67)  
**DNS Reverso**: static.67.220.27.37.clients.your-server.de

---

## 📊 INFORMAÇÕES COMPLETAS DO SERVIDOR

### **IPv4 e DNS Reverso**
```
IP Principal: 37.27.220.67
DNS Reverso: static.67.220.27.37.clients.your-server.de
```

### **Verificar DNS Reverso**

```bash
# No servidor ou do seu PC
nslookup 37.27.220.67

# Deve retornar:
# static.67.220.27.37.clients.your-server.de
```

### **Verificar DNS Direto (quando configurar)**

```bash
# Após configurar DNS do domínio marabet.ao
nslookup marabet.ao

# Deve retornar: 37.27.220.67
```

---

## 🔧 CONFIGURAÇÕES QUE PODEM USAR DNS REVERSO

### **1. Email (SMTP)**

Se configurar envio de emails, pode usar o hostname reverso:
```
Hostname: static.67.220.27.37.clients.your-server.de
```

### **2. Verificações de Segurança**

Alguns serviços verificam DNS reverso como medida de segurança.

### **3. Logs e Identificação**

O hostname reverso pode aparecer nos logs do sistema.

---

## ✅ ATUALIZAR CONFIGURAÇÕES

### **Hostname do Sistema (opcional)**

```bash
# Ver hostname atual
hostname

# Configurar hostname (opcional)
sudo hostnamectl set-hostname static.67.220.27.37.clients.your-server.de

# Ou manter simples
sudo hostnamectl set-hostname marabet-server

# Verificar
hostname
hostnamectl
```

### **Verificar em /etc/hosts**

```bash
# Editar /etc/hosts
sudo nano /etc/hosts

# Adicionar linha (se necessário):
37.27.220.67   marabet.ao www.marabet.ao static.67.220.27.37.clients.your-server.de
```

---

## 📋 INFORMAÇÕES COMPLETAS DO SERVIDOR (ATUALIZADAS)

```
Nome: marabet.ao
IP: 37.27.220.67
DNS Reverso: static.67.220.27.37.clients.your-server.de
IPv6: 2a01:4f9:c013:b3f1::/64
Hostname: static.67.220.27.37.clients.your-server.de
```

---

## 🌐 CONFIGURAR DNS DO DOMÍNIO (Próximo Passo)

### **Registros DNS Necessários:**

```
Tipo    Nome           Conteúdo                         TTL
A       @              37.27.220.67                     3600
A       www            37.27.220.67                     3600
CNAME   www            marabet.ao                       3600
```

### **Onde Configurar:**

1. Painel do provedor do domínio marabet.ao
2. Adicionar registros A e CNAME acima
3. Aguardar propagação (1-48 horas)

### **Verificar Propagação:**

```bash
# Após configurar, verificar
nslookup marabet.ao
dig marabet.ao

# Deve retornar: 37.27.220.67
```

---

## 📝 NOTAS

- **DNS Reverso**: Configurado automaticamente pelo provedor
- **DNS Direto**: Você precisa configurar no painel do domínio
- **Hostname**: Pode usar DNS reverso ou configuração customizada

---

**📄 Documentação Relacionada:**
- `INFORMACOES_SERVIDOR_COMPLETAS.md` - Informações do servidor
- `DEPLOY_SEQUENCIA_COMPLETA.md` - Deploy completo

**📧 Suporte**: suporte@marabet.ao

