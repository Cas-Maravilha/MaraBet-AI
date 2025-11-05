# 🔐 Credenciais de Conexão - Banco de Dados PostgreSQL

## 📋 Informações de Conexão

As credenciais de conexão do banco de dados PostgreSQL foram configuradas nos arquivos de configuração do projeto.

### **Credenciais Configuradas:**

```
Host: 37.27.220.67
Port: 5432
Database: meu_banco
Username: meu_usuario
Password: ctcaddTcMaRVioDY4kso
```

### **String de Conexão (para aplicações):**

```
postgresql://meu_usuario:ctcaddTcMaRVioDY4kso@37.27.220.67:5432/meu_banco
```

---

## 📁 Arquivos Atualizados

As credenciais foram configuradas nos seguintes arquivos:

1. **`config_production.env`** - Configuração de produção
   - Linha 25: `DATABASE_URL=postgresql://meu_usuario:ctcaddTcMaRVioDY4kso@37.27.220.67:5432/meu_banco`

2. **`config_personal.env`** - Configuração pessoal
   - Linha 9-11: `DATABASE_URL=postgresql://meu_usuario:ctcaddTcMaRVioDY4kso@37.27.220.67:5432/meu_banco`

---

## 🔧 Como Usar

### **1. Para Produção:**

Copie o arquivo `config_production.env` para `.env`:

```bash
cp config_production.env .env
```

### **2. Para Desenvolvimento Pessoal:**

Copie o arquivo `config_personal.env` para `.env`:

```bash
cp config_personal.env .env
```

### **3. Testar Conexão:**

```bash
# Via Python (psycopg2)
python -c "import psycopg2; conn = psycopg2.connect('postgresql://meu_usuario:ctcaddTcMaRVioDY4kso@37.27.220.67:5432/meu_banco'); print('✅ Conexão bem-sucedida!')"

# Via psql (linha de comando)
psql -h 37.27.220.67 -p 5432 -U meu_usuario -d meu_banco
```

---

## 🔒 Segurança

⚠️ **IMPORTANTE:**
- Este arquivo contém credenciais sensíveis
- **NÃO** faça commit deste arquivo no Git
- Mantenha as credenciais seguras e não compartilhe publicamente
- Considere usar variáveis de ambiente em produção
- Use um gerenciador de secrets (como AWS Secrets Manager ou HashiCorp Vault) para produção

---

## 📝 Notas

- O banco de dados está hospedado remotamente no servidor `37.27.220.67`
- A porta padrão do PostgreSQL (5432) está sendo usada
- Certifique-se de que o firewall permite conexões na porta 5432
- Verifique se o servidor permite conexões remotas (configuração do `pg_hba.conf`)

---

## 🆘 Troubleshooting

### **Erro: "Connection refused"**
- Verifique se o servidor está acessível: `ping 37.27.220.67`
- Verifique se a porta 5432 está aberta: `telnet 37.27.220.67 5432`

### **Erro: "Authentication failed"**
- Verifique se o username e password estão corretos
- Verifique se o usuário tem permissões para acessar o banco

### **Erro: "Database does not exist"**
- Verifique se o nome do banco está correto: `meu_banco`
- Entre em contato com o administrador do banco de dados

---

**Última atualização:** 2025-01-27  
**Configurado por:** Sistema MaraBet AI

