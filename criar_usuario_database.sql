-- Script SQL para criar usuário e database PostgreSQL
-- MaraBet AI - Configuração do banco de dados
-- Execute este script como superusuário (postgres) no servidor PostgreSQL

-- ============================================
-- 1. CRIAR USUÁRIO
-- ============================================

-- Verificar se o usuário já existe
SELECT usename FROM pg_user WHERE usename = 'meu_usuario';

-- Criar usuário (se não existir)
-- Se o usuário já existir, você pode usar: ALTER USER em vez de CREATE USER
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'meu_usuario') THEN
        CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
        RAISE NOTICE 'Usuário meu_usuario criado com sucesso!';
    ELSE
        RAISE NOTICE 'Usuário meu_usuario já existe. Use ALTER USER para alterar a senha.';
    END IF;
END $$;

-- OU simplesmente criar/alterar diretamente:
-- CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
-- OU se já existe:
-- ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';

-- ============================================
-- 2. CRIAR DATABASE
-- ============================================

-- Verificar se o database já existe
SELECT datname FROM pg_database WHERE datname = 'meu_banco';

-- Criar database (se não existir)
-- Se o database já existir, você pode usar: ALTER DATABASE em vez de CREATE DATABASE
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'meu_banco') THEN
        CREATE DATABASE meu_banco OWNER meu_usuario;
        RAISE NOTICE 'Database meu_banco criado com sucesso!';
    ELSE
        RAISE NOTICE 'Database meu_banco já existe.';
    END IF;
END $$;

-- OU simplesmente criar diretamente:
-- CREATE DATABASE meu_banco OWNER meu_usuario;

-- ============================================
-- 3. CONCEDER PERMISSÕES
-- ============================================

-- Conceder permissões no database
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;

-- Conectar ao database para conceder permissões no schema
\c meu_banco

-- Conceder permissões no schema public
GRANT ALL ON SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO meu_usuario;

-- ============================================
-- 4. VERIFICAR CONFIGURAÇÃO
-- ============================================

-- Verificar usuário criado
SELECT usename, usecreatedb, usesuper FROM pg_user WHERE usename = 'meu_usuario';

-- Verificar database criado
SELECT datname, datdba FROM pg_database WHERE datname = 'meu_banco';

-- Verificar permissões
SELECT datname, datacl FROM pg_database WHERE datname = 'meu_banco';

-- ============================================
-- 5. TESTAR CONEXÃO
-- ============================================

-- Testar conexão com o novo usuário (execute em outro terminal)
-- psql -h 37.27.220.67 -U meu_usuario -d meu_banco

-- ============================================
-- NOTAS IMPORTANTES
-- ============================================

-- 1. Execute este script como superusuário (postgres)
-- 2. Se o usuário já existir, use: ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
-- 3. Se o database já existir, você pode alterar o owner:
--    ALTER DATABASE meu_banco OWNER TO meu_usuario;
-- 4. Verifique o arquivo pg_hba.conf para permitir conexões remotas
-- 5. Reinicie o PostgreSQL após alterar pg_hba.conf: sudo systemctl restart postgresql

