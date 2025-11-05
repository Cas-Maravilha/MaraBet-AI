-- Script Rápido para Recriar Usuário e Database
-- Execute no psql como superusuário: sudo -u postgres psql

-- Remover existentes
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'meu_banco' AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS meu_banco;
DROP USER IF EXISTS meu_usuario;

-- Criar do zero
CREATE USER meu_usuario WITH PASSWORD 'ctcaddTcMaRVioDY4kso';
CREATE DATABASE meu_banco OWNER meu_usuario;
GRANT ALL PRIVILEGES ON DATABASE meu_banco TO meu_usuario;

-- Permissões no schema
\c meu_banco
GRANT ALL ON SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO meu_usuario;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO meu_usuario;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO meu_usuario;

-- Verificar
\c postgres
SELECT usename FROM pg_user WHERE usename = 'meu_usuario';
SELECT datname FROM pg_database WHERE datname = 'meu_banco';

-- Testar conexão
\c meu_banco meu_usuario
SELECT current_database(), current_user;

\echo '✅ Usuário e database recriados com sucesso!'

