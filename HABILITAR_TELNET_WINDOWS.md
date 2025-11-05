# 🔧 Como Habilitar Telnet no Windows

## 📋 Método 1: Via Painel de Controle (GUI)

1. Abra o **Painel de Controle**
2. Clique em **Programas**
3. Clique em **Ativar ou desativar recursos do Windows**
4. Procure por **Cliente Telnet** e marque a caixa
5. Clique em **OK**
6. Aguarde a instalação

## 📋 Método 2: Via PowerShell (Administrador)

```powershell
# Execute PowerShell como Administrador
Enable-WindowsOptionalFeature -Online -FeatureName TelnetClient
```

## 📋 Método 3: Via CMD (Administrador)

```cmd
# Execute CMD como Administrador
dism /online /Enable-Feature /FeatureName:TelnetClient
```

## 🔍 Testar Telnet Após Habilitar

Após habilitar o telnet, você pode testar:

```cmd
# Testar PostgreSQL (porta 5432)
telnet 37.27.220.67 5432

# Testar MySQL (porta 3306)
telnet 37.27.220.67 3306
```

**Nota:** Se a conexão for bem-sucedida, você verá uma tela preta. Pressione `Ctrl + ]` e depois digite `quit` para sair.

## 💡 Alternativa: Usar Script Python

Se preferir não habilitar o telnet, use o script Python `testar_telnet.py` que faz o mesmo teste:

```bash
python testar_telnet.py
```

## 📊 Resultado Esperado

### PostgreSQL (porta 5432)
- ✅ **Conexão bem-sucedida**: Porta acessível
- ✅ **Conexão estabelecida**: Você pode conectar ao PostgreSQL

### MySQL (porta 3306)
- ❌ **Conexão falhou**: Porta não acessível ou fechada
- ⚠️ **Serviço não disponível**: MySQL não está rodando ou porta está bloqueada

---

**Última atualização:** 2025-01-27

