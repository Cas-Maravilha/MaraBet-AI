# 📋 Scripts de Teste de Conexão PostgreSQL Remota

Este conjunto de scripts testa a conexão remota ao PostgreSQL no servidor `37.27.220.67`.

## 🚀 Scripts Disponíveis

### 1️⃣ `testar_conexao_remota.py` (Python)
**O que faz:**
- Testa conexão básica ao PostgreSQL
- Testa operações no banco de dados (criar/ler/escrever)
- Mede performance da conexão
- Exibe informações detalhadas do servidor

**Requisitos:**
```bash
pip install psycopg2-binary
```

**Como executar:**
```bash
python testar_conexao_remota.py
```

**Ou:**
```bash
python3 testar_conexao_remota.py
```

---

### 2️⃣ `testar_conexao_remota.sh` (Bash/Shell)
**O que faz:**
- Testa ping ao servidor
- Testa conectividade na porta 5432
- Testa conexão PostgreSQL via `psql`
- Testa queries simples
- Mede performance

**Requisitos:**
- `psql` instalado
- `nc` (netcat) opcional

**Como executar:**
```bash
bash testar_conexao_remota.sh
```

**Ou:**
```bash
chmod +x testar_conexao_remota.sh
./testar_conexao_remota.sh
```

---

### 3️⃣ `testar_conectividade_rede.ps1` (PowerShell)
**O que faz:**
- Testa ping ao servidor remoto
- Testa conectividade na porta 5432
- Resolve DNS (opcional)
- Exibe informações detalhadas

**Como executar:**
```powershell
.\testar_conectividade_rede.ps1
```

**Ou:**
```powershell
powershell -ExecutionPolicy Bypass -File testar_conectividade_rede.ps1
```

---

### 4️⃣ `testar_conexao_completo.sh` (Bash - Todos os testes)
**O que faz:**
- Executa TODOS os testes em sequência
- Testa conectividade de rede
- Testa via `psql`
- Testa via Python (se disponível)
- Gera relatório completo

**Como executar:**
```bash
bash testar_conexao_completo.sh
```

**Ou:**
```bash
chmod +x testar_conexao_completo.sh
./testar_conexao_completo.sh
```

---

## 📊 Resumo dos Testes

### Teste 1: Conectividade de Rede
- ✅ Ping ao servidor
- ✅ Porta 5432 acessível
- ⏱️ Latência

### Teste 2: Conexão PostgreSQL
- ✅ Conexão estabelecida
- ✅ Autenticação
- ✅ Versão do PostgreSQL
- ✅ Database e usuário

### Teste 3: Operações no Banco
- ✅ Listar tabelas
- ✅ Criar tabela
- ✅ Inserir dados
- ✅ Ler dados
- ✅ Remover tabela de teste

### Teste 4: Performance
- ⏱️ Tempo de conexão
- ⏱️ Tempo de query
- 📊 Avaliação de latência

---

## 🔧 Instalação de Dependências

### Python (psycopg2)
```bash
pip install psycopg2-binary
```

### PostgreSQL Client (psql)
```bash
# Ubuntu/Debian
sudo apt install postgresql-client

# Windows
# Baixar do site oficial do PostgreSQL
```

### Netcat (opcional)
```bash
# Ubuntu/Debian
sudo apt install netcat

# Windows
# Usar Test-NetConnection do PowerShell
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

## 🎯 Como Usar

### Opção 1: Teste Rápido (Python)
```bash
python testar_conexao_remota.py
```

### Opção 2: Teste Rápido (Bash)
```bash
bash testar_conexao_remota.sh
```

### Opção 3: Teste de Rede (PowerShell)
```powershell
.\testar_conectividade_rede.ps1
```

### Opção 4: Teste Completo (Todos os testes)
```bash
bash testar_conexao_completo.sh
```

---

## ✅ Interpretando os Resultados

### ✅ Todos os Testes Passaram
```
✅ Conexão PostgreSQL: FUNCIONANDO
✅ Operações no banco: FUNCIONANDO
✅ Performance: EXCELENTE

🎉 TODOS OS TESTES PASSARAM! Conexão funcionando perfeitamente!
```

**Significa:**
- Servidor está acessível
- PostgreSQL está configurado corretamente
- Conexão está funcionando
- Pronto para uso!

---

### ❌ Alguns Testes Falharam
```
❌ Conexão PostgreSQL: FALHOU
   Erro: connection refused
```

**Possíveis causas:**
1. PostgreSQL não está em execução no servidor remoto
2. Firewall bloqueando a porta 5432
3. `postgresql.conf` não tem `listen_addresses = '*'`
4. `pg_hba.conf` não permite conexões remotas
5. Credenciais incorretas

**Soluções:**
1. Execute no servidor remoto: `sudo bash verificar_configuracao_postgresql.sh`
2. Execute no servidor remoto: `sudo bash configurar_postgresql_remoto.sh`
3. Verifique firewall: `sudo ufw status`
4. Verifique se PostgreSQL está escutando: `sudo ss -tlnp | grep 5432`

---

## 🔍 Troubleshooting

### Erro: "connection refused"
- Verifique se PostgreSQL está rodando: `sudo systemctl status postgresql`
- Verifique firewall: `sudo ufw status`
- Verifique configuração: `grep listen_addresses /etc/postgresql/14/main/postgresql.conf`

### Erro: "password authentication failed"
- Verifique credenciais no script
- Verifique `pg_hba.conf` no servidor remoto
- Execute no servidor: `sudo bash configurar_postgresql_remoto.sh`

### Erro: "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### Erro: "psql: command not found"
```bash
sudo apt install postgresql-client
```

---

## 📝 Exemplos de Saída

### Saída de Sucesso (Python)
```
╔═══════════════════════════════════════════════════════════╗
║     TESTE DE CONEXÃO POSTGRESQL REMOTA                    ║
║     Servidor: 37.27.220.67:5432                           ║
╚═══════════════════════════════════════════════════════════╝

✅ Conexão estabelecida com sucesso!

📊 Informações da conexão:
   PostgreSQL: PostgreSQL 14.19...
   Database: marabet
   User: meu_root$marabet

🎉 TODOS OS TESTES PASSARAM!
```

### Saída de Erro
```
❌ Erro de conexão: connection to server at "37.27.220.67", 
   port 5432 failed: Connection refused

💡 Verificações necessárias:
   1. Servidor PostgreSQL está em execução?
   2. Firewall permite conexões na porta 5432?
   3. postgresql.conf tem listen_addresses = '*'?
   4. pg_hba.conf permite conexões remotas?
```

---

## 🚀 Próximos Passos

Após os testes passarem:

1. **Use a conexão em sua aplicação:**
```python
import psycopg2

conn = psycopg2.connect(
    host="37.27.220.67",
    port="5432",
    database="marabet",
    user="meu_root$marabet",
    password="YOUR_DATABASE_PASSWORD"
)
```

2. **Ou use connection string:**
```
postgresql://meu_root%24marabet:YOUR_DATABASE_PASSWORD@37.27.220.67:5432/marabet
```

---

## 📞 Suporte

Se encontrar problemas:
1. Execute: `bash testar_conexao_completo.sh` (teste completo)
2. Execute no servidor: `sudo bash verificar_configuracao_postgresql.sh`
3. Verifique logs: `sudo tail -f /var/log/postgresql/postgresql-14-main.log`

