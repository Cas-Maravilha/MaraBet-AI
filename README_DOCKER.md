# 🐳 MaraBet AI - Deploy com Docker

Este documento contém instruções completas para deploy do sistema MaraBet AI usando Docker e Docker Compose.

## 📋 Pré-requisitos

### Sistema Operacional
- **Linux**: Ubuntu 20.04+, CentOS 8+, ou similar
- **macOS**: 10.15+ (Catalina ou superior)
- **Windows**: Windows 10/11 com WSL2

### Software Necessário
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: Para clonar o repositório
- **Curl**: Para testes de conectividade

## 🚀 Instalação Rápida

### 1. Clone o Repositório
```bash
git clone <repository-url>
cd marabet-ai
```

### 2. Execute o Setup Automático
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. Configure suas Chaves
Edite o arquivo `.env` com suas chaves de API:
```bash
nano .env
```

### 4. Deploy do Sistema
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 🔧 Configuração Manual

### 1. Instalar Docker

#### Ubuntu/Debian
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

#### macOS
```bash
brew install --cask docker
```

### 2. Instalar Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Configurar Variáveis de Ambiente
```bash
cp .env.example .env
nano .env
```

Configure suas chaves:
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

## 🐳 Comandos Docker

### Build da Imagem
```bash
# Build básico
docker build -t marabet-ai .

# Build com tag específica
docker build -t marabet-ai:v1.0.0 .

# Build sem cache
docker build --no-cache -t marabet-ai .
```

### Executar Container
```bash
# Executar em modo interativo
docker run -it --rm marabet-ai

# Executar em background
docker run -d --name marabet-ai-app marabet-ai

# Executar com variáveis de ambiente
docker run -d --name marabet-ai-app \
  -e API_FOOTBALL_KEY=sua_chave \
  -e TELEGRAM_BOT_TOKEN=seu_token \
  marabet-ai
```

## 🚀 Docker Compose

### Desenvolvimento
```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Rebuild e iniciar
docker-compose up --build -d
```

### Produção
```bash
# Usar arquivo de produção
docker-compose -f docker-compose.prod.yml up -d

# Escalar serviços
docker-compose up -d --scale collector=3

# Verificar status
docker-compose ps
```

## 📊 Scripts de Gerenciamento

### Setup Inicial
```bash
./scripts/setup.sh
```
- Instala Docker e Docker Compose
- Configura arquivos necessários
- Cria diretórios e permissões
- Gera certificados SSL

### Deploy
```bash
./scripts/deploy.sh
```
- Para serviços existentes
- Faz build das imagens
- Inicia todos os serviços
- Verifica saúde do sistema

### Monitoramento
```bash
# Status geral
./scripts/monitor.sh status

# Recursos do sistema
./scripts/monitor.sh resources

# Logs de erro
./scripts/monitor.sh logs

# Monitoramento em tempo real
./scripts/monitor.sh realtime
```

### Backup
```bash
# Backup completo
./scripts/backup.sh backup

# Listar backups
./scripts/backup.sh list

# Restaurar backup
./scripts/backup.sh restore backup_file.tar.gz
```

### Health Check
```bash
# Verificação completa
./scripts/health.sh

# Verificar apenas containers
./scripts/health.sh containers

# Verificar conectividade
./scripts/health.sh connectivity
```

## 🌐 Acessos

Após o deploy, os seguintes serviços estarão disponíveis:

- **Dashboard Principal**: http://localhost:8000
- **API Flask**: http://localhost:5000
- **Nginx (Proxy)**: http://localhost:80
- **HTTPS**: https://localhost:443 (se configurado)

### Endpoints de Saúde
- `GET /health` - Status geral do sistema
- `GET /api/health` - Status da API
- `GET /dashboard/health` - Status do dashboard

## 🔍 Troubleshooting

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

### Logs e Debugging

#### Ver logs de todos os serviços
```bash
docker-compose logs -f
```

#### Ver logs de um serviço específico
```bash
docker-compose logs -f marabet-ai
```

#### Entrar no container
```bash
docker-compose exec marabet-ai bash
```

#### Verificar recursos
```bash
docker stats
```

## 📈 Monitoramento e Manutenção

### Limpeza Automática
```bash
# Limpar containers parados
docker container prune -f

# Limpar imagens não utilizadas
docker image prune -f

# Limpeza completa
docker system prune -a -f
```

### Backup Automático
```bash
# Adicionar ao crontab
0 2 * * * /path/to/marabet-ai/scripts/backup.sh backup
```

### Atualizações
```bash
# Atualizar código
git pull origin main

# Rebuild e restart
docker-compose up --build -d
```

## 🔒 Segurança

### SSL/TLS
```bash
# Gerar certificados
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

### Firewall
```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp
sudo ufw allow 8000/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
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

## 🆘 Suporte

### Logs Importantes
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

---

**🎉 Sistema MaraBet AI pronto para deploy com Docker!**
