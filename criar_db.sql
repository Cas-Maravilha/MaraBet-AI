-- Criar usuário e banco de dados para MaraBet
CREATE USER "meu_root$marabet" WITH PASSWORD 'senha_temporaria' CREATEDB;
CREATE DATABASE marabet OWNER "meu_root$marabet";
GRANT ALL PRIVILEGES ON DATABASE marabet TO "meu_root$marabet";

