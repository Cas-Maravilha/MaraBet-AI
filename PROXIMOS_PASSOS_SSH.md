# ✅ PRÓXIMOS PASSOS APÓS VERIFICAR SSH

**Comando**: `sudo systemctl status sshd`  
**Esperado**: active (running)

---

## ✅ SE SSH ESTÁ ATIVO

### **Status esperado:**
```
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled)
     Active: active (running) since ...
```

**Se mostrar `active (running)` = ✅ SSH funcionando!**

---

## 🧪 TESTE COMPLETO DO SSH SEGURO

### **1. Verificar configuração ativa**

```bash
# Ver configurações aplicadas
sudo sshd -T | grep -E "(permitrootlogin|passwordauthentication|pubkeyauthentication)"

# Deve mostrar:
# permitrootlogin no
# pubkeyauthentication yes
# passwordauthentication no  (se configurou)
```

### **2. Testar nova conexão SSH**

**⚠️ IMPORTANTE: Manter sessão atual aberta!**

**Do seu PC, abrir NOVO terminal:**
```powershell
ssh marabet@37.27.220.67
```

**Resultados:**

#### **✅ Funciona sem pedir senha:**
```
# Conecta diretamente
# Mostra prompt do servidor
```

**Ação:** ✅ Configuração OK! Pode continuar.

#### **⚠️ Ainda pede senha:**
```
# Pedido de senha aparece
# Mas consegue conectar
```

**Ação:** 
- Verificar chave SSH
- Verificar `~/.ssh/authorized_keys`
- Pode continuar, mas otimizar depois

#### **❌ Falha na conexão:**
```
Connection refused
Permission denied
```

**Ação:** 
- ⚠️ NÃO fechar sessão atual
- Reverter configuração (veja abaixo)

---

## 🔄 SE PRECISAR REVERTER

**Na sessão SSH atual (que ainda funciona):**

```bash
# Editar configuração
sudo nano /etc/ssh/sshd_config

# Mudar de volta para:
PermitRootLogin yes
PasswordAuthentication yes

# Salvar e reiniciar
sudo systemctl restart sshd

# Verificar novamente
sudo systemctl status sshd
```

---

## ✅ APÓS CONFIRMAR SSH FUNCIONANDO

### **Continuar com Deploy:**

1. ✅ SSH configurado
2. ⏳ Instalar PostgreSQL
3. ⏳ Instalar Docker
4. ⏳ Enviar código
5. ⏳ Configurar aplicação

---

## 📋 RESUMO RÁPIDO

**Se status mostra `active (running)`:**
```bash
✅ SSH reiniciado com sucesso
✅ Pronto para testar nova conexão
⚠️ Testar antes de fechar sessão atual
```

**Próximo passo:**
```powershell
# Do seu PC - abrir NOVO terminal
ssh marabet@37.27.220.67
```

---

**📄 Guias Relacionados:**
- `VERIFICAR_SSH_APOS_REINICIAR.md` - Verificações completas
- `CONFIGURAR_SSH_SEGURO.md` - Configuração detalhada

**📧 Suporte**: suporte@marabet.ao

