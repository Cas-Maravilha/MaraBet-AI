#!/bin/bash

# =============================================
# Script: Instalação Segura do PostgreSQL 15
# Projeto: MaraBet AI
# Servidor: Angoweb (Ubuntu 22.04 LTS)
# =============================================

set -e  # Aborta em caso de erro

echo "🚀 Iniciando instalação segura do PostgreSQL 15..."

# === 1. Atualizar sistema ===
echo "🔄 Atualizando pacotes..."
sudo apt update && sudo apt upgrade -y

# === 2. Instalar PostgreSQL 15 ===
echo "📦 Instalando PostgreSQL 15..."
sudo apt install -y postgresql-15 postgresql-client-15

# === 3. Iniciar e habilitar serviço ===
echo "⚡ Iniciando e habilitando PostgreSQL..."
sudo systemctl enable --now postgresql

# === 4. Gerar senha forte para o usuário marabet_user ===
DB_USER="marabet_user"
DB_NAME="marabet"
DB_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-24)

# === 5. Criar banco e usuário ===
echo "🗄 Criando banco de dados e usuário..."
sudo -u postgres psql <<EOF
CREATE DATABASE ${DB_NAME};
CREATE USER ${DB_USER} WITH ENCRYPTED PASSWORD '${DB_PASS}';
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
ALTER USER ${DB_USER} WITH CONNECTION LIMIT 20;
EOF

# === 6. Configurar postgresql.conf (apenas localhost) ===
echo "🔒 Configurando postgresql.conf para escutar apenas em localhost..."
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/15/main/postgresql.conf

# === 7. Configurar pg_hba.conf (autenticação md5 local) ===
echo "🛡 Configurando pg_hba.conf..."
sudo tee /etc/postgresql/15/main/pg_hba.conf > /dev/null <<EOF
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   ${DB_NAME}      ${DB_USER}                              md5
host    ${DB_NAME}      ${DB_USER}      127.0.0.1/32            md5
host    ${DB_NAME}      ${DB_USER}      ::1/128                 md5
# Rejeitar todas as outras conexões
host    all             all             0.0.0.0/0               reject
host    all             all             ::0/0                   reject
EOF

# === 8. Reiniciar PostgreSQL ===
echo "🔁 Reiniciando PostgreSQL..."
sudo systemctl restart postgresql

# === 9. Configurar firewall (UFW) ===
echo "🧱 Configurando UFW para bloquear acesso externo à porta 5432..."
sudo ufw status | grep -q "Status: active" || sudo ufw --force enable
sudo ufw deny 5432/tcp > /dev/null 2>&1 || true  # Garante que está bloqueada

# === 10. Criar arquivo .env.db com credenciais seguras ===
ENV_FILE="/opt/marabet/.env.db"
sudo mkdir -p /opt/marabet
sudo tee $ENV_FILE > /dev/null <<EOF
# PostgreSQL Credentials - MaraBet AI
DB_HOST=localhost
DB_PORT=5432
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASS=${DB_PASS}
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@localhost:5432/${DB_NAME}
EOF

sudo chmod 600 $ENV_FILE
sudo chown marabet:marabet $ENV_FILE 2>/dev/null || true

echo "✅ Arquivo de credenciais salvo em: $ENV_FILE (permissões 600)"

# === 11. Testar conexão local ===
echo "🔍 Testando conexão local..."
sudo -u postgres psql -d $DB_NAME -U $DB_USER -c "SELECT 'Conexão bem-sucedida ao banco MaraBet!' as status;" -h localhost -p 5432

# === 12. Mensagem final ===
echo ""
echo "🎉 PostgreSQL 15 instalado e protegido com sucesso!"
echo "📝 Credenciais salvas em: $ENV_FILE"
echo "🔒 O PostgreSQL está acessível APENAS via localhost (não exposto à internet)."
echo "💡 Use 'source /opt/marabet/.env.db' em seus scripts para carregar as variáveis."

