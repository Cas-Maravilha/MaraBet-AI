#!/bin/bash

################################################################################
# MARABET AI - EC2 USER DATA SCRIPT
# Instalação automática de todo software necessário
################################################################################

set -e

# Redirecionar output para log
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "========================================================================"
echo "🚀 MaraBet AI - EC2 Initialization"
echo "========================================================================"
echo "Started: $(date)"
echo ""

################################################################################
# 1. ATUALIZAR SISTEMA
################################################################################

echo "1. Atualizando sistema..."
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
echo "   ✓ Sistema atualizado"

################################################################################
# 1.5 INSTALAR DEPENDÊNCIAS BASE
################################################################################

echo ""
echo "1.5. Instalando dependências base..."
apt-get install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  git \
  python3-pip \
  python3-venv \
  python3-dev \
  build-essential \
  ufw \
  fail2ban
echo "   ✓ Dependências base instaladas"

################################################################################
# 2. INSTALAR DOCKER (Método Oficial)
################################################################################

echo ""
echo "2. Instalando Docker (método oficial)..."

# Adicionar repositório Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Adicionar usuário ao grupo docker
usermod -aG docker ubuntu

# Habilitar e iniciar
systemctl enable docker
systemctl start docker

echo "   ✓ Docker instalado: $(docker --version)"

################################################################################
# 3. INSTALAR DOCKER COMPOSE
################################################################################

echo ""
echo "3. Instalando Docker Compose..."
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d '"' -f 4)
curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
echo "   ✓ Docker Compose instalado: $(docker-compose --version)"

################################################################################
# 4. INSTALAR NGINX
################################################################################

echo ""
echo "4. Instalando Nginx..."
apt-get install -y nginx
systemctl enable nginx
systemctl start nginx
echo "   ✓ Nginx instalado: $(nginx -v 2>&1)"

################################################################################
# 5. INSTALAR POSTGRESQL CLIENT
################################################################################

echo ""
echo "5. Instalando PostgreSQL Client..."
apt-get install -y postgresql-client
echo "   ✓ PostgreSQL Client: $(psql --version)"

################################################################################
# 6. INSTALAR REDIS TOOLS
################################################################################

echo ""
echo "6. Instalando Redis Tools..."
apt-get install -y redis-tools
echo "   ✓ Redis Tools: $(redis-cli --version)"

################################################################################
# 7. INSTALAR AWS CLI
################################################################################

echo ""
echo "7. Instalando AWS CLI..."
apt-get install -y unzip
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip
echo "   ✓ AWS CLI: $(aws --version)"

################################################################################
# 8. INSTALAR PYTHON E FERRAMENTAS
################################################################################

echo ""
echo "8. Instalando Python e ferramentas..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential
    
# Atualizar pip
python3 -m pip install --upgrade pip

# Instalar dependências comuns
pip3 install \
    boto3 \
    psycopg2-binary \
    redis \
    python-dotenv \
    requests

echo "   ✓ Python: $(python3 --version)"
echo "   ✓ pip: $(pip3 --version)"

################################################################################
# 9. INSTALAR GIT E FERRAMENTAS
################################################################################

echo ""
echo "9. Instalando ferramentas adicionais..."
apt-get install -y \
    git \
    curl \
    wget \
    htop \
    vim \
    nano \
    jq \
    net-tools \
    certbot \
    python3-certbot-nginx

echo "   ✓ Git: $(git --version)"

################################################################################
# 10. CONFIGURAR TIMEZONE
################################################################################

echo ""
echo "10. Configurando timezone..."
timedatectl set-timezone Africa/Luanda
echo "   ✓ Timezone: $(timedatectl | grep 'Time zone')"

################################################################################
# 11. CRIAR ESTRUTURA DE DIRETÓRIOS
################################################################################

echo ""
echo "11. Criando estrutura de diretórios..."
mkdir -p /opt/marabet
mkdir -p /opt/marabet/backups
mkdir -p /opt/marabet/logs
mkdir -p /opt/marabet/static
mkdir -p /opt/marabet/media
mkdir -p /var/log/marabet

chown -R ubuntu:ubuntu /opt/marabet
chown -R ubuntu:ubuntu /var/log/marabet

echo "   ✓ Diretórios criados"

################################################################################
# 12. CONFIGURAR NGINX INICIAL
################################################################################

echo ""
echo "12. Configurando Nginx..."

# Remover default
rm -f /etc/nginx/sites-enabled/default

# Criar configuração básica
cat > /etc/nginx/sites-available/marabet << 'NGINXCONF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }

    location /static/ {
        alias /opt/marabet/static/;
        expires 30d;
    }
}
NGINXCONF

ln -sf /etc/nginx/sites-available/marabet /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "   ✓ Nginx configurado"

################################################################################
# 13. CONFIGURAR FIREWALL UFW
################################################################################

echo ""
echo "13. Configurando firewall..."
ufw --force enable
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw status

echo "   ✓ Firewall UFW configurado"

################################################################################
# 13.5 CONFIGURAR FAIL2BAN
################################################################################

echo ""
echo "13.5. Configurando Fail2Ban..."

# Configurar Fail2Ban para SSH
cat > /etc/fail2ban/jail.local << 'F2BCONF'
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
F2BCONF

systemctl enable fail2ban
systemctl start fail2ban

echo "   ✓ Fail2Ban configurado"

################################################################################
# 13.6 CRIAR USUÁRIO MARABET
################################################################################

echo ""
echo "13.6. Criando usuário marabet..."

# Criar usuário dedicado
useradd -m -s /bin/bash marabet
usermod -aG docker marabet
usermod -aG sudo marabet

# Configurar sudo sem senha para operações Docker
echo "marabet ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/local/bin/docker-compose" >> /etc/sudoers.d/marabet

chown -R marabet:marabet /opt/marabet

echo "   ✓ Usuário marabet criado"

################################################################################
# 14. OTIMIZAÇÕES DO SISTEMA
################################################################################

echo ""
echo "14. Aplicando otimizações..."

# Aumentar limites de arquivo
cat >> /etc/security/limits.conf << EOF
* soft nofile 65536
* hard nofile 65536
ubuntu soft nofile 65536
ubuntu hard nofile 65536
EOF

# Otimizações de rede
cat >> /etc/sysctl.conf << EOF
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.ip_local_port_range = 10000 65000
EOF

sysctl -p

echo "   ✓ Otimizações aplicadas"

################################################################################
# 15. CRIAR ARQUIVO DE STATUS
################################################################################

echo ""
echo "15. Finalizando setup..."

# Informações do sistema
INSTANCE_ID=$(ec2-metadata --instance-id | cut -d " " -f 2 2>/dev/null || echo "unknown")
INSTANCE_TYPE=$(ec2-metadata --instance-type | cut -d " " -f 2 2>/dev/null || echo "unknown")
LOCAL_IPV4=$(ec2-metadata --local-ipv4 | cut -d " " -f 2 2>/dev/null || hostname -I | awk '{print $1}')
PUBLIC_IPV4=$(ec2-metadata --public-ipv4 | cut -d " " -f 2 2>/dev/null || curl -s http://checkip.amazonaws.com)
AZ=$(ec2-metadata --availability-zone | cut -d " " -f 2 2>/dev/null || echo "unknown")

cat > /home/ubuntu/setup-complete.txt << EOF
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        ✅ MARABET AI - EC2 SETUP COMPLETO                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

Data de Setup:        $(date)
Hostname:             $(hostname)
Instance ID:          $INSTANCE_ID
Instance Type:        $INSTANCE_TYPE
Availability Zone:    $AZ

IP Privado:           $LOCAL_IPV4
IP Público:           $PUBLIC_IPV4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOFTWARE INSTALADO:

✓ Docker:             $(docker --version)
✓ Docker Compose:     $(docker-compose --version)
✓ Nginx:              $(nginx -v 2>&1)
✓ PostgreSQL Client:  $(psql --version | head -n1)
✓ Redis Tools:        $(redis-cli --version)
✓ AWS CLI:            $(aws --version | cut -d' ' -f1)
✓ Python:             $(python3 --version)
✓ Git:                $(git --version)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DIRETÓRIOS CRIADOS:

/opt/marabet/         - Aplicação principal
/opt/marabet/backups/ - Backups
/opt/marabet/logs/    - Logs da aplicação
/var/log/marabet/     - Logs do sistema

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SERVIÇOS ATIVOS:

$(systemctl is-active docker)     Docker
$(systemctl is-active nginx)      Nginx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRÓXIMOS PASSOS:

1. Conectar via SSH:
   ssh -i marabet-key.pem ubuntu@$PUBLIC_IPV4

2. Fazer upload do código:
   rsync -avz -e "ssh -i marabet-key.pem" ./ ubuntu@$PUBLIC_IPV4:/opt/marabet/

3. Configurar .env:
   cd /opt/marabet
   nano .env

4. Deploy com Docker:
   docker-compose up -d

5. Ver logs:
   docker-compose logs -f

6. Testar:
   curl http://localhost/health
   curl http://$PUBLIC_IPV4/health

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TESTAR CONECTIVIDADE:

RDS PostgreSQL:
  psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com -p 5432 -U marabet_admin -d postgres

Redis Serverless:
  redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com -p 6379 --tls --insecure

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ EC2 PRONTA PARA RECEBER O MARABET AI!

EOF

chown ubuntu:ubuntu /home/ubuntu/setup-complete.txt

# Criar motd (Message of the Day)
cat > /etc/update-motd.d/99-marabet << 'EOF'
#!/bin/bash
cat << 'MOTD'

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║              🚀 MARABET AI - EC2 SERVER                       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

Diretório da aplicação: /opt/marabet
Logs: /var/log/marabet
Status: cat /home/ubuntu/setup-complete.txt

MOTD
EOF

chmod +x /etc/update-motd.d/99-marabet

################################################################################
# FINALIZAÇÃO
################################################################################

echo ""
echo "========================================================================"
echo "✅ MARABET AI - EC2 SETUP COMPLETO!"
echo "========================================================================"
echo ""
echo "Completed: $(date)"
echo "Instance ready for MaraBet AI deployment!"
echo ""
echo "Log file: /var/log/user-data.log"
echo "Status: /home/ubuntu/setup-complete.txt"
echo ""

