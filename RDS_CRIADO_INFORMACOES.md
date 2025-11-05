# 🗄️ RDS POSTGRESQL - INFORMAÇÕES COMPLETAS

**Data de Criação**: 25 de Outubro de 2025  
**Região**: eu-west-1 (Irlanda)  
**Status**: ✅ Criado e Disponível

---

## 📋 INFORMAÇÕES DO RDS

### **Identificação:**

```yaml
DB Instance Identifier: database-1
DB Instance ARN: arn:aws:rds:eu-west-1:206749730888:db:database-1
Engine: PostgreSQL
Region: eu-west-1
Account ID: 206749730888
```

### **Credenciais (AWS Secrets Manager):**

```yaml
Secret Name: rds!db-3758a324-12a2-4675-b5ff-b92acdf38483
Secret ARN: arn:aws:secretsmanager:eu-west-1:206749730888:secret:rds!db-3758a324-12a2-4675-b5ff-b92acdf38483-BpTjIS
Secret Description: The secret associated with the primary RDS DB instance
Version ID: c55b9938-e4de-439a-9ccd-59c7a57ed978
Encryption: aws/secretsmanager KMS Key
```

---

## 🔑 OBTER CREDENCIAIS

### **Via AWS CLI:**

```bash
# Obter credenciais completas do Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id rds!db-3758a324-12a2-4675-b5ff-b92acdf38483 \
  --region eu-west-1

# Extrair apenas username e password
aws secretsmanager get-secret-value \
  --secret-id rds!db-3758a324-12a2-4675-b5ff-b92acdf38483 \
  --region eu-west-1 \
  --query 'SecretString' \
  --output text | jq -r '.'

# Salvar em variáveis
SECRET=$(aws secretsmanager get-secret-value \
  --secret-id rds!db-3758a324-12a2-4675-b5ff-b92acdf38483 \
  --region eu-west-1 \
  --query 'SecretString' \
  --output text)

DB_USERNAME=$(echo $SECRET | jq -r '.username')
DB_PASSWORD=$(echo $SECRET | jq -r '.password')
DB_HOST=$(echo $SECRET | jq -r '.host')
DB_PORT=$(echo $SECRET | jq -r '.port')
DB_ENGINE=$(echo $SECRET | jq -r '.engine')

echo "Username: $DB_USERNAME"
echo "Password: $DB_PASSWORD"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "Engine: $DB_ENGINE"
```

### **Via AWS Console:**

```
1. Acesse: AWS Console > Secrets Manager
2. Região: eu-west-1
3. Busque: rds!db-3758a324-12a2-4675-b5ff-b92acdf38483
4. Clique em "Retrieve secret value"
5. Copie username e password
```

---

## 🔗 OBTER ENDPOINT DO RDS

### **Via AWS CLI:**

```bash
# Obter informações completas do RDS
aws rds describe-db-instances \
  --db-instance-identifier database-1 \
  --region eu-west-1

# Obter apenas o endpoint
RDS_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier database-1 \
  --region eu-west-1 \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)

echo "RDS Endpoint: $RDS_ENDPOINT"

# Obter porta
RDS_PORT=$(aws rds describe-db-instances \
  --db-instance-identifier database-1 \
  --region eu-west-1 \
  --query 'DBInstances[0].Endpoint.Port' \
  --output text)

echo "RDS Port: $RDS_PORT"
```

### **Via AWS Console:**

```
1. AWS Console > RDS > Databases
2. Clique em: database-1
3. Tab "Connectivity & security"
4. Copie "Endpoint"
```

---

## 📊 INFORMAÇÕES COMPLETAS DO RDS

### **Via CLI (JSON Completo):**

```bash
# Ver todas as informações
aws rds describe-db-instances \
  --db-instance-identifier database-1 \
  --region eu-west-1 > rds-database-1-info.json

# Ver informações principais
aws rds describe-db-instances \
  --db-instance-identifier database-1 \
  --region eu-west-1 \
  --query 'DBInstances[0].[DBInstanceIdentifier,DBInstanceClass,Engine,EngineVersion,DBInstanceStatus,MultiAZ,StorageEncrypted,AllocatedStorage,Endpoint.Address,Endpoint.Port]' \
  --output table
```

**Resultado Esperado:**
```
---------------------------------------------------------------
| DescribeDBInstances                                          |
+--------------------+----------------------------------------+
| database-1         | db.t3.medium                           |
| postgres           | 15.x                                   |
| available          | True                                   |
| True               | 100                                    |
| database-1.xxxxx.eu-west-1.rds.amazonaws.com               |
| 5432               |                                        |
+--------------------+----------------------------------------+
```

---

## 🔌 TESTAR CONEXÃO

### **1. Instalar PostgreSQL Client:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y postgresql-client

# Amazon Linux 2
sudo yum install -y postgresql

# macOS
brew install postgresql
```

### **2. Obter Credenciais e Conectar:**

```bash
# Obter credenciais do Secrets Manager
SECRET=$(aws secretsmanager get-secret-value \
  --secret-id rds!db-3758a324-12a2-4675-b5ff-b92acdf38483 \
  --region eu-west-1 \
  --query 'SecretString' \
  --output text)

DB_USERNAME=$(echo $SECRET | jq -r '.username')
DB_PASSWORD=$(echo $SECRET | jq -r '.password')
DB_HOST=$(echo $SECRET | jq -r '.host')
DB_PORT=$(echo $SECRET | jq -r '.port')
DB_NAME=$(echo $SECRET | jq -r '.dbname // "postgres"')

# Conectar ao RDS
psql -h $DB_HOST -p $DB_PORT -U $DB_USERNAME -d $DB_NAME

# Quando solicitar senha, colar: $DB_PASSWORD
```

### **3. Testar Dentro do PostgreSQL:**

```sql
-- Ver versão
SELECT version();

-- Listar databases
\l

-- Criar database MaraBet (se não existir)
CREATE DATABASE marabet_production;

-- Conectar ao database
\c marabet_production

-- Criar tabela de teste
CREATE TABLE test (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Inserir dados de teste
INSERT INTO test (name) VALUES ('MaraBet AI Test');

-- Verificar
SELECT * FROM test;

-- Listar tabelas
\dt

-- Sair
\q
```

---

## 🔐 CONNECTION STRING

### **Formato Padrão:**

```bash
# Obter do Secrets Manager
SECRET=$(aws secretsmanager get-secret-value \
  --secret-id rds!db-3758a324-12a2-4675-b5ff-b92acdf38483 \
  --region eu-west-1 \
  --query 'SecretString' \
  --output text)

# Extrair valores
DB_USERNAME=$(echo $SECRET | jq -r '.username')
DB_PASSWORD=$(echo $SECRET | jq -r '.password')
DB_HOST=$(echo $SECRET | jq -r '.host')
DB_PORT=$(echo $SECRET | jq -r '.port')

# Montar connection string
echo "postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/marabet_production"
```

### **Para .env File:**

```bash
# Gerar automaticamente
cat > .env.rds << EOF
# RDS PostgreSQL Configuration
DATABASE_URL=postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/marabet_production
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=marabet_production
DB_USER=${DB_USERNAME}
DB_PASSWORD=${DB_PASSWORD}
DB_SSL_MODE=require

# AWS Secrets Manager
SECRET_ARN=arn:aws:secretsmanager:eu-west-1:206749730888:secret:rds!db-3758a324-12a2-4675-b5ff-b92acdf38483-BpTjIS
SECRET_NAME=rds!db-3758a324-12a2-4675-b5ff-b92acdf38483
AWS_REGION=eu-west-1
EOF

cat .env.rds
```

---

## 🔧 CONFIGURAR NA APLICAÇÃO

### **Opção 1: Usar Secrets Manager Diretamente (Recomendado)**

**Python:**
```python
import boto3
import json

def get_db_credentials():
    secret_name = "rds!db-3758a324-12a2-4675-b5ff-b92acdf38483"
    region_name = "eu-west-1"
    
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])
    
    return {
        'host': secret['host'],
        'port': secret['port'],
        'username': secret['username'],
        'password': secret['password'],
        'database': 'marabet_production'
    }

# Usar
creds = get_db_credentials()
DATABASE_URL = f"postgresql://{creds['username']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['database']}"
```

**Node.js:**
```javascript
const AWS = require('aws-sdk');

async function getDbCredentials() {
    const client = new AWS.SecretsManager({
        region: 'eu-west-1'
    });
    
    const data = await client.getSecretValue({
        SecretId: 'rds!db-3758a324-12a2-4675-b5ff-b92acdf38483'
    }).promise();
    
    const secret = JSON.parse(data.SecretString);
    
    return {
        host: secret.host,
        port: secret.port,
        user: secret.username,
        password: secret.password,
        database: 'marabet_production'
    };
}

// Usar
const creds = await getDbCredentials();
const DATABASE_URL = `postgresql://${creds.user}:${creds.password}@${creds.host}:${creds.port}/${creds.database}`;
```

### **Opção 2: Usar Variáveis de Ambiente**

```bash
# Exportar credenciais
SECRET=$(aws secretsmanager get-secret-value \
  --secret-id rds!db-3758a324-12a2-4675-b5ff-b92acdf38483 \
  --region eu-west-1 \
  --query 'SecretString' \
  --output text)

export DB_HOST=$(echo $SECRET | jq -r '.host')
export DB_PORT=$(echo $SECRET | jq -r '.port')
export DB_USER=$(echo $SECRET | jq -r '.username')
export DB_PASSWORD=$(echo $SECRET | jq -r '.password')
export DB_NAME=marabet_production

# Iniciar aplicação
python app.py
# ou
npm start
```

---

## 📊 MONITORAMENTO

### **Ver Métricas no CloudWatch:**

```bash
# CPU Utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=database-1 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region eu-west-1

# Database Connections
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=database-1 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region eu-west-1

# Free Storage Space
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name FreeStorageSpace \
  --dimensions Name=DBInstanceIdentifier,Value=database-1 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region eu-west-1
```

### **Ver Logs:**

```bash
# Listar arquivos de log
aws rds describe-db-log-files \
  --db-instance-identifier database-1 \
  --region eu-west-1

# Baixar log específico
aws rds download-db-log-file-portion \
  --db-instance-identifier database-1 \
  --log-file-name error/postgresql.log.2025-10-25-12 \
  --region eu-west-1
```

---

## 💾 BACKUP E RESTORE

### **Criar Snapshot Manual:**

```bash
aws rds create-db-snapshot \
  --db-instance-identifier database-1 \
  --db-snapshot-identifier database-1-snapshot-$(date +%Y%m%d-%H%M%S) \
  --region eu-west-1

# Listar snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier database-1 \
  --region eu-west-1
```

### **Restaurar de Snapshot:**

```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier database-1-restored \
  --db-snapshot-identifier database-1-snapshot-YYYYMMDD-HHMMSS \
  --region eu-west-1
```

---

## 🔧 MODIFICAR RDS

### **Alterar Classe da Instância:**

```bash
aws rds modify-db-instance \
  --db-instance-identifier database-1 \
  --db-instance-class db.t3.large \
  --apply-immediately \
  --region eu-west-1
```

### **Aumentar Storage:**

```bash
aws rds modify-db-instance \
  --db-instance-identifier database-1 \
  --allocated-storage 200 \
  --apply-immediately \
  --region eu-west-1
```

### **Alterar Backup Retention:**

```bash
aws rds modify-db-instance \
  --db-instance-identifier database-1 \
  --backup-retention-period 14 \
  --region eu-west-1
```

---

## 📝 SCRIPT COMPLETO DE SETUP

```bash
#!/bin/bash

echo "🗄️ MaraBet AI - RDS PostgreSQL Setup"
echo "======================================"
echo ""

REGION="eu-west-1"
SECRET_ID="rds!db-3758a324-12a2-4675-b5ff-b92acdf38483"
DB_NAME="marabet_production"

# 1. Obter credenciais
echo "1. Obtendo credenciais do Secrets Manager..."
SECRET=$(aws secretsmanager get-secret-value \
  --secret-id $SECRET_ID \
  --region $REGION \
  --query 'SecretString' \
  --output text)

DB_HOST=$(echo $SECRET | jq -r '.host')
DB_PORT=$(echo $SECRET | jq -r '.port')
DB_USER=$(echo $SECRET | jq -r '.username')
DB_PASSWORD=$(echo $SECRET | jq -r '.password')

echo "   Host: $DB_HOST"
echo "   Port: $DB_PORT"
echo "   User: $DB_USER"
echo ""

# 2. Criar database
echo "2. Criando database marabet_production..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"

echo ""
echo "3. Gerando .env file..."
cat > .env.production << EOF
# RDS PostgreSQL
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_SSL_MODE=require

# AWS
AWS_REGION=${REGION}
SECRET_ARN=arn:aws:secretsmanager:${REGION}:206749730888:secret:${SECRET_ID}-BpTjIS
SECRET_NAME=${SECRET_ID}
EOF

echo "   Arquivo .env.production criado"
echo ""

echo "✅ Setup concluído!"
echo ""
echo "Connection String:"
echo "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo ""
echo "Testar conexão:"
echo "psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
echo ""
```

---

## 📞 INFORMAÇÕES DE SUPORTE

### **ARNs:**

```
RDS Instance ARN:
arn:aws:rds:eu-west-1:206749730888:db:database-1

Secret ARN:
arn:aws:secretsmanager:eu-west-1:206749730888:secret:rds!db-3758a324-12a2-4675-b5ff-b92acdf38483-BpTjIS

KMS Key:
aws/secretsmanager
```

### **Comandos Úteis:**

```bash
# Ver status
aws rds describe-db-instances \
  --db-instance-identifier database-1 \
  --region eu-west-1 \
  --query 'DBInstances[0].DBInstanceStatus'

# Ver endpoint
aws rds describe-db-instances \
  --db-instance-identifier database-1 \
  --region eu-west-1 \
  --query 'DBInstances[0].Endpoint'

# Ver credenciais
aws secretsmanager get-secret-value \
  --secret-id rds!db-3758a324-12a2-4675-b5ff-b92acdf38483 \
  --region eu-west-1 \
  --query 'SecretString' \
  --output text | jq '.'
```

---

## ✅ CHECKLIST

- [ ] RDS criado e disponível
- [ ] Credenciais obtidas do Secrets Manager
- [ ] Endpoint anotado
- [ ] Database `marabet_production` criada
- [ ] Conexão testada com psql
- [ ] .env file configurado
- [ ] Aplicação conectada
- [ ] Monitoramento verificado
- [ ] Backup automático confirmado

---

**🗄️ RDS PostgreSQL Configurado!**  
**🔐 Credenciais no AWS Secrets Manager**  
**✅ Pronto para Produção**  
**☁️ MaraBet AI - Powered by AWS RDS**

