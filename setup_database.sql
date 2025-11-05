-- ============================================
-- Script de Setup do Banco de Dados PostgreSQL
-- MaraBet AI - Configuração Completa
-- ============================================
-- Execute este script como superusuário (postgres) no servidor PostgreSQL
-- 
-- Como executar:
--   psql -U postgres -f setup_database.sql
--   OU
--   sudo -u postgres psql -f setup_database.sql
-- ============================================

-- ============================================
-- 1. CRIAR USUÁRIO
-- ============================================

-- Verificar se o usuário já existe
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_user WHERE usename = 'meu_usuario') THEN
        RAISE NOTICE 'Usuário meu_usuario já existe. Alterando senha...';
        ALTER USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
    ELSE
        RAISE NOTICE 'Criando usuário meu_usuario...';
        CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
    END IF;
END $$;

-- ============================================
-- 2. CRIAR DATABASE
-- ============================================

-- Verificar se o database já existe
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_database WHERE datname = 'meu_banco') THEN
        RAISE NOTICE 'Database meu_banco já existe. Alterando owner...';
        ALTER DATABASE meu_banco OWNER TO meu_usuario;
    ELSE
        RAISE NOTICE 'Criando database meu_banco...';
        CREATE DATABASE meu_banco OWNER meu_usuario;
    END IF;
END $$;

-- ============================================
-- 3. CONCEDER PERMISSÕES NO DATABASE
-- ============================================

GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;

-- ============================================
-- 4. CONCEDER PERMISSÕES NO SCHEMA PUBLIC
-- ============================================

-- Conectar ao database para conceder permissões no schema
\c meu_banco

-- Conceder permissões no schema public
GRANT ALL ON SCHEMA public TO meu_usuario;

-- Conceder permissões em todas as tabelas existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO meu_usuario;

-- Conceder permissões em todas as sequências existentes
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO meu_usuario;

-- Conceder permissões em tabelas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO meu_usuario;

-- Conceder permissões em sequências futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO meu_usuario;

-- ============================================
-- 5. VERIFICAR CONFIGURAÇÃO
-- ============================================

-- Voltar para database postgres para verificar
\c postgres

-- Verificar usuário criado
SELECT 
    usename as usuario,
    usecreatedb as pode_criar_db,
    usesuper as superusuario
FROM pg_user 
WHERE usename = 'meu_usuario';

-- Verificar database criado
SELECT 
    datname as database,
    pg_get_userbyid(datdba) as owner
FROM pg_database 
WHERE datname = 'meu_banco';

-- Verificar permissões do database
SELECT 
    datname as database,
    datacl as permissoes
FROM pg_database 
WHERE datname = 'meu_banco';

-- ============================================
-- 6. RESUMO
-- ============================================

\echo ''
\echo '============================================'
\echo '✅ SETUP CONCLUÍDO COM SUCESSO!'
\echo '============================================'
\echo ''
\echo '📋 Credenciais:'
\echo '   Host: 37.27.220.67'
\echo '   Port: 5432'
\echo '   Database: meu_banco'
\echo '   Username: meu_usuario'
\echo '   Password: ctcaddTcMaRVioDY4kso'
\echo ''
\echo '🔗 String de Conexão:'
\echo '   postgresql://meu_usuario:ctcaddTcMaRVioDY4kso@37.27.220.67:5432/meu_banco'
\echo ''
\echo '🧪 Testar conexão:'
\echo '   psql -h 37.27.220.67 -U meu_usuario -d meu_banco'
\echo '   OU'
\echo '   python testar_conexao.py'
\echo ''
\echo '============================================'

