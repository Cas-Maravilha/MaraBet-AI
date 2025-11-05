# 🚀 MaraBet AI - Guia de Deploy Completo

Este guia contém instruções detalhadas para deploy do sistema MaraBet AI em diferentes ambientes.

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalação Rápida](#instalação-rápida)
3. [Deploy Manual](#deploy-manual)
4. [Configuração Avançada](#configuração-avançada)
5. [Monitoramento](#monitoramento)
6. [Troubleshooting](#troubleshooting)
7. [Produção](#produção)

## 🔧 Pré-requisitos

### Sistema Operacional
- **Linux**: Ubuntu 20.04+, CentOS 8+, Debian 11+
- **macOS**: 10.15+ (Catalina ou superior)
- **Windows**: Windows 10/11 com WSL2 ou Docker Desktop

### Software Necessário
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: Para clonar o repositório
- **Curl**: Para testes de conectividade

### Recursos Mínimos
- **RAM**: 2GB (recomendado: 4GB+)
- **CPU**: 2 cores (recomendado: 4 cores+)
- **Disco**: 10GB (recomendado: 20GB+)
- **Rede**: Conexão estável com internet

## 🚀 Instalação Rápida

### Linux/macOS
```bash
# 1. Clone o repositório
git clone <repository-url>
cd marabet-ai

# 2. Execute o setup automático
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. Configure suas chaves no .env
nano .env

# 4. Deploy rápido
chmod +x scripts/quick-start.sh
./scripts/quick-start.sh
```

### Windows
```powershell
# 1. Clone o repositório
git clone <repository-url>
cd marabet-ai

# 2. Execute o setup automático (como Administrador)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\install.ps1

# 3. Configure suas chaves no .env
notepad .env

# 4. Deploy rápido
.\scripts\quick-start.ps1
```

## 🔧 Deploy Manual

### 1. Preparação do Ambiente

#### Instalar Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# CentOS/RHEL
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# macOS
brew install --cask docker
```

#### Instalar Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Configuração

#### Criar arquivo .env
```bash
cp .env.example .env
nano .env
```

Configurar suas chaves:
```env
# API Keys
API_FOOTBALL_KEY=sua_chave_aqui
THE_ODDS_API_KEY=sua_chave_aqui

# Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui

# Email
SMTP_USERNAME=seu_email@exemplo.com
SMTP_PASSWORD=sua_senha_aqui
NOTIFICATION_EMAIL=seu_email@exemplo.com
ADMIN_EMAIL=admin@exemplo.com
```

#### Criar diretórios necessários
```bash
mkdir -p data logs reports nginx/ssl scripts backups
```

### 3. Deploy

#### Build das imagens
```bash
docker-compose build --no-cache
```

#### Iniciar serviços
```bash
docker-compose up -d
```

#### Verificar status
```bash
docker-compose ps
```

## ⚙️ Configuração Avançada

### Docker Compose Personalizado

#### Desenvolvimento
```bash
# Usar arquivo de desenvolvimento
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

#### Produção
```bash
# Usar arquivo de produção
docker-compose -f docker-compose.prod.yml up -d
```

### Configuração de Rede

#### Criar rede personalizada
```bash
docker network create marabet-network --driver bridge --subnet=172.20.0.0/16
```

#### Configurar DNS
```bash
# Adicionar ao docker-compose.yml
networks:
  marabet-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1
```

### Configuração de Volumes

#### Volume persistente para dados
```bash
# Criar volume
docker volume create marabet-data

# Usar no docker-compose.yml
volumes:
  - marabet-data:/app/data
```

#### Backup automático
```bash
# Adicionar ao crontab
0 2 * * * /path/to/marabet-ai/scripts/backup.sh backup
```

### Configuração de SSL

#### Gerar certificados
```bash
# Certificado auto-assinado
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=BR/ST=SP/L=SaoPaulo/O=MaraBetAI/CN=localhost"

# Certificado Let's Encrypt (produção)
certbot certonly --standalone -d seu-dominio.com
```

#### Configurar Nginx
```bash
# Editar nginx/nginx.conf
# Configurar SSL
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

## 📊 Monitoramento

### Scripts de Monitoramento

#### Status Geral
```bash
./scripts/monitor.sh status
```

#### Recursos do Sistema
```bash
./scripts/monitor.sh resources
```

#### Logs de Erro
```bash
./scripts/monitor.sh logs
```

#### Monitoramento em Tempo Real
```bash
./scripts/monitor.sh realtime
```

### Health Checks

#### Verificação Completa
```bash
./scripts/health.sh
```

#### Verificação de Conectividade
```bash
./scripts/health.sh connectivity
```

### Métricas e Alertas

#### Prometheus (opcional)
```bash
# Iniciar com monitoramento
docker-compose -f docker-compose.prod.yml up -d

# Acessar Prometheus
# http://localhost:9090
```

#### Configurar Alertas
```bash
# Editar monitoring/alerts.yml
# Configurar regras de alerta
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Container não inicia
```bash
# Verificar logs
docker-compose logs container_name

# Verificar configuração
docker-compose config

# Rebuild
docker-compose up --build -d
```

#### 2. Erro de permissão
```bash
# Corrigir permissões
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh
```

#### 3. Porta já em uso
```bash
# Verificar portas em uso
netstat -tulpn | grep :8000

# Parar processo
sudo kill -9 PID
```

#### 4. Problemas de rede
```bash
# Verificar conectividade
docker network ls
docker network inspect marabet-network

# Recriar rede
docker-compose down
docker network prune
docker-compose up -d
```

#### 5. Problemas de memória
```bash
# Verificar uso de memória
docker stats

# Limpar containers parados
docker container prune -f

# Limpar imagens não utilizadas
docker image prune -f
```

### Logs Importantes

#### Aplicação
```bash
# Logs da aplicação
docker-compose logs -f marabet-ai

# Logs do coletor
docker-compose logs -f collector

# Logs do dashboard
docker-compose logs -f dashboard
```

#### Nginx
```bash
# Logs de acesso
docker-compose logs -f nginx

# Logs de erro
docker-compose exec nginx tail -f /var/log/nginx/error.log
```

#### Sistema
```bash
# Logs do sistema
journalctl -u docker

# Logs do Docker
sudo journalctl -u docker.service
```

## 🏭 Produção

### Configuração de Produção

#### Usar arquivo de produção
```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### Configurar domínio
```bash
# Editar nginx/nginx.conf
server_name seu-dominio.com;

# Configurar DNS
# A record: seu-dominio.com -> IP_DO_SERVIDOR
```

#### Configurar SSL
```bash
# Usar Let's Encrypt
certbot certonly --standalone -d seu-dominio.com

# Configurar renovação automática
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### Backup e Restore

#### Backup Automático
```bash
# Adicionar ao crontab
0 2 * * * /path/to/marabet-ai/scripts/backup.sh backup

# Backup manual
./scripts/backup.sh backup
```

#### Restore
```bash
# Listar backups
./scripts/backup.sh list

# Restaurar backup
./scripts/backup.sh restore backup_file.tar.gz
```

### Monitoramento de Produção

#### Configurar alertas
```bash
# Editar monitoring/alerts.yml
# Configurar regras de alerta
```

#### Configurar notificações
```bash
# Configurar Telegram
# Configurar Email
# Configurar Slack (opcional)
```

### Escalabilidade

#### Escalar serviços
```bash
# Escalar coletor
docker-compose up -d --scale collector=3

# Escalar dashboard
docker-compose up -d --scale dashboard=2
```

#### Load Balancer
```bash
# Configurar Nginx como load balancer
# Configurar múltiplas instâncias
```

## 📚 Comandos Úteis

### Docker
```bash
# Listar containers
docker ps -a

# Listar imagens
docker images

# Remover container
docker rm container_name

# Remover imagem
docker rmi image_name

# Ver uso de recursos
docker stats
```

### Docker Compose
```bash
# Ver status
docker-compose ps

# Restart serviço
docker-compose restart service_name

# Escalar serviço
docker-compose up -d --scale service_name=3

# Ver logs de serviço específico
docker-compose logs -f service_name
```

### Sistema
```bash
# Verificar espaço em disco
df -h

# Verificar uso de memória
free -h

# Verificar processos
ps aux | grep docker

# Verificar portas
netstat -tulpn | grep :8000
```

## 🆘 Suporte

### Arquivos de Log
- **Aplicação**: `logs/app.log`
- **Coletor**: `logs/collector.log`
- **Nginx**: `nginx/logs/access.log`, `nginx/logs/error.log`

### Arquivos de Configuração
- **Docker**: `Dockerfile`, `docker-compose.yml`
- **Nginx**: `nginx/nginx.conf`
- **Aplicação**: `.env`, `settings/settings.py`

### Comandos de Diagnóstico
```bash
# Status completo
./scripts/health.sh

# Monitoramento
./scripts/monitor.sh full

# Backup
./scripts/backup.sh backup
```

## 📝 Notas Importantes

1. **Primeira execução**: O sistema pode demorar alguns minutos para inicializar completamente
2. **Recursos**: Recomenda-se pelo menos 2GB de RAM e 10GB de espaço em disco
3. **Rede**: Certifique-se de que as portas 80, 443, 5000 e 8000 estão disponíveis
4. **Backup**: Configure backups regulares dos dados importantes
5. **Logs**: Monitore os logs regularmente para identificar problemas
6. **Atualizações**: Mantenha o sistema atualizado regularmente
7. **Segurança**: Configure SSL/TLS em produção
8. **Monitoramento**: Configure alertas para problemas críticos

---

**🎉 Sistema MaraBet AI pronto para deploy!**
