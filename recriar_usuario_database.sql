-- ============================================
-- Script para Recriar Usuário e Database do Zero
-- MaraBet AI - Recriação completa
-- ============================================
-- Execute este script como superusuário (postgres) no servidor PostgreSQL
-- 
-- Como executar:
--   sudo -u postgres psql -f recriar_usuario_database.sql
--   OU
--   sudo -u postgres psql
--   \i recriar_usuario_database.sql
-- ============================================

-- ============================================
-- 1. REMOVER USUÁRIO E DATABASE EXISTENTES
-- ============================================

-- Remover database se existir (precisa desconectar usuários primeiro)
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'meu_banco' AND pid <> pg_backend_pid();

-- Remover database
DROP DATABASE IF EXISTS meu_banco;

-- Remover usuário se existir
DROP USER IF EXISTS meu_usuario;

\echo ''
\echo '============================================'
\echo '✅ Usuário e database removidos (se existiam)'
\echo '============================================'
\echo ''

-- ============================================
-- 2. CRIAR USUÁRIO DO ZERO
-- ============================================

-- Criar usuário com senha explícita
CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';

\echo ''
\echo '✅ Usuário meu_usuario criado'
\echo ''

-- ============================================
-- 3. CRIAR DATABASE DO ZERO
-- ============================================

-- Criar database com owner
CREATE DATABASE meu_banco OWNER meu_usuario;

\echo ''
\echo '✅ Database meu_banco criado'
\echo ''

-- ============================================
-- 4. CONCEDER PERMISSÕES NO DATABASE
-- ============================================

-- Conceder todas as permissões no database
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;

\echo ''
\echo '✅ Permissões concedidas no database'
\echo ''

-- ============================================
-- 5. CONCEDER PERMISSÕES NO SCHEMA PUBLIC
-- ============================================

-- Conectar ao database para conceder permissões no schema
\c meu_banco

-- Conceder permissões no schema public
GRANT ALL ON SCHEMA public TO meu_usuario;

-- Conceder permissões em tabelas existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO meu_usuario;

-- Conceder permissões em sequências existentes
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO meu_usuario;

-- Conceder permissões em tabelas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO meu_usuario;

-- Conceder permissões em sequências futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO meu_usuario;

\echo ''
\echo '✅ Permissões concedidas no schema public'
\echo ''

-- ============================================
-- 6. VERIFICAR CONFIGURAÇÃO
-- ============================================

-- Voltar para database postgres para verificar
\c postgres

-- Verificar usuário criado
SELECT 
    usename as usuario,
    usecreatedb as pode_criar_db,
    usesuper as superusuario,
    usecanlogin as pode_login
FROM pg_user 
WHERE usename = 'meu_usuario';

\echo ''

-- Verificar database criado
SELECT 
    datname as database,
    pg_get_userbyid(datdba) as owner,
    datacl as permissoes
FROM pg_database 
WHERE datname = 'meu_banco';

\echo ''

-- ============================================
-- 7. TESTAR CONEXÃO COM O NOVO USUÁRIO
-- ============================================

-- Testar conexão (conectar como meu_usuario)
\c meu_banco meu_usuario

-- Verificar se conseguiu conectar
SELECT 
    current_database() as database_atual,
    current_user as usuario_atual,
    version() as versao_postgres;

\echo ''

-- ============================================
-- 8. RESUMO FINAL
-- ============================================

\c postgres

\echo ''
\echo '============================================'
\echo '✅ RECRIAÇÃO CONCLUÍDA COM SUCESSO!'
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
\echo '💡 IMPORTANTE:'
\echo '   Verifique se o pg_hba.conf permite conexões remotas:'
\echo '   sudo cat /etc/postgresql/*/main/pg_hba.conf | grep meu_usuario'
\echo '   Deve mostrar: host meu_banco meu_usuario 0.0.0.0/0 scram-sha-256'
\echo ''
\echo '   Se não tiver, adicione:'
\echo '   sudo nano /etc/postgresql/*/main/pg_hba.conf'
\echo '   host    meu_banco    meu_usuario    0.0.0.0/0    scram-sha-256'
\echo ''
\echo '   Depois reinicie PostgreSQL:'
\echo '   sudo systemctl restart postgresql'
\echo ''
\echo '============================================'

