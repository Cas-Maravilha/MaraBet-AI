# 📋 Comandos Úteis do PostgreSQL

Guia de referência rápida para comandos úteis do PostgreSQL quando conectado via `psql`.

## 🔌 Comandos de Conexão

### Conectar ao PostgreSQL
```bash
# Conexão local
psql -U usuario -d banco

# Conexão remota
psql -h host -p porta -U usuario -d banco

# Com password na variável de ambiente
export PGPASSWORD='senha'
psql -h host -p porta -U usuario -d banco
```

### Informações da conexão
```sql
\conninfo    -- Exibe informações da conexão atual
```

---

## 📊 Comandos de Banco de Dados

### Listar e Navegar
```sql
\l          -- Listar todos os bancos de dados
\l+         -- Listar com informações detalhadas (tamanho, etc)
\c banco    -- Conectar a um banco específico
\c          -- Mostrar banco atual
```

### Informações do banco
```sql
SELECT current_database();    -- Nome do banco atual
SELECT version();             -- Versão do PostgreSQL
SELECT now();                 -- Data/hora atual do servidor
```

---

## 👥 Comandos de Usuários

### Listar usuários
```sql
\du         -- Listar todos os usuários (roles)
\du+        -- Listar com informações detalhadas
\duS        -- Listar apenas superusuários
```

### Criar/Modificar usuários
```sql
-- Criar usuário
CREATE USER nome_usuario WITH PASSWORD 'senha';

-- Criar usuário com privilégios
CREATE USER nome_usuario WITH PASSWORD 'senha' CREATEDB;

-- Alterar senha
ALTER USER nome_usuario WITH PASSWORD 'nova_senha';

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE banco TO nome_usuario;

-- Remover usuário
DROP USER nome_usuario;
```

---

## 📋 Comandos de Tabelas

### Listar tabelas
```sql
\dt         -- Listar tabelas do schema atual
\dt+        -- Listar com informações detalhadas (tamanho, etc)
\dt schema  -- Listar tabelas de um schema específico
\d          -- Listar todas as tabelas, views e sequências
\d+         -- Listar com informações detalhadas
```

### Informações de tabela
```sql
\d tabela           -- Descrever estrutura da tabela
\d+ tabela          -- Descrever com informações detalhadas
\dS                 -- Listar sequências
\di                 -- Listar índices
\dv                 -- Listar views
\df                 -- Listar funções
```

### Criar tabela
```sql
CREATE TABLE nome_tabela (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔍 Comandos de Consulta

### Consultas básicas
```sql
SELECT * FROM tabela;                    -- Selecionar tudo
SELECT * FROM tabela LIMIT 10;          -- Limitar resultados
SELECT * FROM tabela WHERE id = 1;      -- Filtrar
SELECT COUNT(*) FROM tabela;            -- Contar registros
```

### Informações do sistema
```sql
-- Estatísticas do banco
SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database;

-- Tamanho de uma tabela
SELECT pg_size_pretty(pg_total_relation_size('tabela')) AS tamanho;

-- Listar conexões ativas
SELECT * FROM pg_stat_activity;
```

---

## 🔧 Comandos Úteis de Sistema

### Sair e ajuda
```sql
\q          -- Sair do psql
\h          -- Ajuda geral
\h COMANDO  -- Ajuda de um comando específico (ex: \h SELECT)
\?          -- Lista todos os comandos do psql
```

### Configurações
```sql
\timing     -- Ativar/desativar exibição de tempo de execução
\x          -- Ativar/desativar modo expandido (saída vertical)
\pset       -- Configurar formatação de saída
\set        -- Definir variável
\unset      -- Remover variável
```

### Histórico e comandos
```sql
\s          -- Mostrar histórico de comandos
\s arquivo  -- Salvar histórico em arquivo
\! comando  -- Executar comando do shell (ex: \! ls)
\copy       -- Copiar dados de/para arquivo
```

---

## 📝 Comandos de Importação/Exportação

### Exportar dados
```sql
-- Exportar query para arquivo
\copy (SELECT * FROM tabela) TO '/caminho/arquivo.csv' CSV HEADER;

-- Exportar tabela completa
\copy tabela TO '/caminho/arquivo.csv' CSV HEADER;
```

### Importar dados
```sql
-- Importar de arquivo CSV
\copy tabela FROM '/caminho/arquivo.csv' CSV HEADER;
```

---

## 🔐 Comandos de Permissões

### Ver permissões
```sql
-- Permissões de uma tabela
\dp tabela

-- Permissões de um schema
\dn+

-- Permissões do banco
\l+
```

### Alterar permissões
```sql
-- Conceder privilégios em tabela
GRANT SELECT, INSERT, UPDATE ON tabela TO usuario;
GRANT ALL PRIVILEGES ON TABLE tabela TO usuario;

-- Revogar privilégios
REVOKE SELECT ON tabela FROM usuario;

-- Conceder privilégios no banco
GRANT ALL PRIVILEGES ON DATABASE banco TO usuario;
```

---

## 🗄️ Comandos de Schema

```sql
\dn         -- Listar schemas
\dn+        -- Listar schemas com informações detalhadas
\dx         -- Listar extensões instaladas
\dx+        -- Listar extensões com informações detalhadas
```

---

## 📊 Estatísticas e Monitoramento

```sql
-- Estatísticas de tabelas
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Estatísticas de índices
SELECT indexname, tablename, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public';

-- Queries em execução
SELECT pid, usename, datname, state, query 
FROM pg_stat_activity 
WHERE state = 'active';

-- Conexões ativas
SELECT count(*) FROM pg_stat_activity;
```

---

## 🔄 Comandos de Backup e Restore

### Via psql
```bash
# Backup de um banco
pg_dump -U usuario -d banco > backup.sql

# Backup completo
pg_dumpall -U postgres > backup_all.sql

# Restaurar
psql -U usuario -d banco < backup.sql
```

### Via \copy (dentro do psql)
```sql
\copy tabela TO '/caminho/backup.csv' CSV HEADER
\copy tabela FROM '/caminho/restore.csv' CSV HEADER
```

---

## 💡 Dicas Rápidas

### Atalhos úteis
- `Up/Down` - Navegar pelo histórico
- `Ctrl+D` ou `\q` - Sair do psql
- `Ctrl+C` - Cancelar query em execução
- `Ctrl+L` - Limpar tela
- `Ctrl+R` - Buscar no histórico

### Configurar prompt
```sql
\set PROMPT1 '%n@%M:%> %# '
\set PROMPT2 '%R%# '
```

### Formatação de saída
```sql
-- Modo expandido (útil para muitas colunas)
\x

-- Configurar formato de saída
\pset format aligned    -- Formato alinhado (padrão)
\pset format wrapped    -- Formato com quebra de linha
\pset border 2          -- Bordas duplas
```

---

## 📋 Comandos Mais Usados (Referência Rápida)

```sql
\l          -- Listar bancos
\du         -- Listar usuários
\dt         -- Listar tabelas
\d tabela   -- Estrutura da tabela
\c banco    -- Conectar ao banco
\conninfo   -- Informações da conexão
\q          -- Sair
\h COMANDO  -- Ajuda
\?          -- Lista comandos
\timing     -- Ativar tempo de execução
\x          -- Modo expandido
```

---

## 🔗 Conexão Remota (Exemplo)

```bash
# Conectar ao servidor remoto
psql -h 37.27.220.67 -p 5432 -U "meu_root\$marabet" -d marabet

# Ou com password na variável
export PGPASSWORD='dudbeeGdNBSxjpEWlop'
psql -h 37.27.220.67 -p 5432 -U "meu_root\$marabet" -d marabet
```

---

## 📚 Recursos Adicionais

- Documentação oficial: https://www.postgresql.org/docs/
- Comandos SQL: `\h COMANDO`
- Comandos psql: `\?`

---

## ⚠️ Comandos Importantes para Administração

```sql
-- Verificar versão
SELECT version();

-- Verificar configurações
SHOW all;                    -- Todas as configurações
SHOW shared_buffers;         -- Configuração específica
SHOW max_connections;

-- Recarregar configuração (sem reiniciar)
SELECT pg_reload_conf();

-- Estatísticas do servidor
SELECT * FROM pg_stat_database;

-- Desconectar conexões
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'banco';
```

---

**💡 Dica:** Para ajuda específica de um comando dentro do psql, use `\h COMANDO` (ex: `\h SELECT`, `\h CREATE TABLE`)

