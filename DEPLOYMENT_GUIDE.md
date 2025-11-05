# 🚀 Guia de Deployment - MaraBet AI

> **Pipeline Completo de CI/CD com GitHub Actions para Deploy Automático em Staging e Produção**

## 📋 Visão Geral

Este guia detalha o pipeline completo de CI/CD implementado para o MaraBet AI, incluindo testes automatizados, build de imagens Docker e deploy automático em ambientes de Staging e Produção.

## 🏗️ Arquitetura do Pipeline

### **Workflows Implementados**

1. **🧪 CI (Continuous Integration)** - `ci.yml`
2. **🐳 Docker Build & Push** - `docker-build.yml`
3. **🚀 Deploy Staging** - `deploy-staging.yml`
4. **🚀 Deploy Production** - `deploy-production.yml`
5. **🔄 Rollback** - `rollback.yml`
6. **🧹 Cleanup & Maintenance** - `cleanup.yml`
7. **📊 Monitoring & Alerts** - `monitoring.yml`

### **Fluxo de Deploy**

```mermaid
graph TD
    A[Push/PR] --> B[CI Tests]
    B --> C[Build Docker Images]
    C --> D{Environment}
    D -->|develop| E[Deploy Staging]
    D -->|main/tag| F[Deploy Production]
    E --> G[Health Checks]
    F --> H[Health Checks]
    G --> I[Monitoring]
    H --> I
    I --> J[Cleanup & Maintenance]
```

## 🔧 Configuração Inicial

### **1. Secrets do GitHub**

Configure os seguintes secrets no repositório GitHub:

#### **Docker Registry**
```
DOCKER_USERNAME=seu_usuario_docker
DOCKER_PASSWORD=sua_senha_docker
```

#### **Staging Environment**
```
STAGING_HOST=staging.marabet-ai.com
STAGING_USERNAME=deploy
STAGING_SSH_KEY=chave_ssh_privada
STAGING_PORT=22
STAGING_DATABASE_URL=postgresql://user:pass@host:port/db
```

#### **Production Environment**
```
PRODUCTION_HOST=marabet-ai.com
PRODUCTION_USERNAME=deploy
PRODUCTION_SSH_KEY=chave_ssh_privada
PRODUCTION_PORT=22
PRODUCTION_DATABASE_URL=postgresql://user:pass@host:port/db
```

#### **API Keys**
```
API_FOOTBALL_KEY=sua_chave_api_football
THE_ODDS_API_KEY=sua_chave_odds_api
TELEGRAM_BOT_TOKEN=seu_bot_token
TELEGRAM_CHAT_ID=seu_chat_id
```

#### **Monitoring**
```
GRAFANA_ADMIN_PASSWORD=senha_admin_grafana
SLACK_WEBHOOK_URL=webhook_slack_opcional
```

### **2. Configuração dos Servidores**

#### **Staging Server**
```bash
# Instalar Docker e Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Criar usuário deploy
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# Configurar SSH
sudo mkdir -p /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
sudo chown deploy:deploy /home/deploy/.ssh
```

#### **Production Server**
```bash
# Instalar Docker e Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Criar usuário deploy
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# Configurar SSH
sudo mkdir -p /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
sudo chown deploy:deploy /home/deploy/.ssh

# Configurar SSL (Let's Encrypt)
sudo apt install certbot
sudo certbot certonly --standalone -d marabet-ai.com -d www.marabet-ai.com
```

## 🚀 Processo de Deploy

### **Deploy Automático**

#### **Staging (Branch: develop)**
```bash
# Push para develop ativa deploy automático
git checkout develop
git add .
git commit -m "feat: nova funcionalidade"
git push origin develop
```

#### **Production (Branch: main ou Tags)**
```bash
# Deploy via tag (recomendado)
git tag v1.0.0
git push origin v1.0.0

# Ou push para main
git checkout main
git merge develop
git push origin main
```

### **Deploy Manual**

#### **Via GitHub Actions UI**
1. Acesse **Actions** no repositório
2. Selecione o workflow desejado
3. Clique em **Run workflow**
4. Escolha o ambiente e confirme

#### **Via CLI**
```bash
# Deploy staging
gh workflow run deploy-staging.yml -f environment=staging

# Deploy production
gh workflow run deploy-production.yml -f environment=production
```

## 🔄 Rollback

### **Rollback Automático**
```bash
# Via GitHub Actions UI
1. Acesse Actions > Rollback Deployment
2. Escolha o ambiente
3. Especifique a versão (opcional)
4. Execute o workflow
```

### **Rollback Manual**
```bash
# No servidor
cd /opt/marabet-ai/production
docker-compose down
docker pull marabet-ai:v1.0.0  # versão anterior
docker-compose up -d
```

## 📊 Monitoramento

### **Health Checks**
- **Staging**: `http://staging.marabet-ai.com/health`
- **Production**: `https://marabet-ai.com/health`

### **Métricas**
- **Prometheus**: `http://staging.marabet-ai.com:9090`
- **Grafana**: `https://marabet-ai.com:3000`

### **Logs**
```bash
# Ver logs em tempo real
docker logs -f marabet-ai-production

# Ver logs específicos
docker exec marabet-ai-production tail -f /app/logs/mara_bet.log
```

## 🧹 Manutenção

### **Limpeza Automática**
- **Frequência**: Diária às 2:00 AM UTC
- **Ações**: Limpeza de imagens antigas, logs, volumes não utilizados

### **Limpeza Manual**
```bash
# Limpar imagens antigas
docker image prune -f

# Limpar volumes não utilizados
docker volume prune -f

# Limpar cache de build
docker builder prune -f
```

## 🔒 Segurança

### **Scan de Vulnerabilidades**
- **Trivy**: Scan automático de imagens Docker
- **Bandit**: Análise de código Python
- **Safety**: Verificação de dependências

### **Rate Limiting**
- **API**: 10 requests/segundo
- **Dashboard**: 5 requests/segundo

### **SSL/TLS**
- **Certificados**: Let's Encrypt
- **Protocolos**: TLS 1.2 e 1.3
- **Headers**: Security headers configurados

## 🚨 Alertas e Notificações

### **Health Checks**
- **Frequência**: A cada 5 minutos
- **Endpoints**: Health, API, Dashboard
- **Ação**: Notificação automática em caso de falha

### **Logs**
- **Análise**: Automática de erros e warnings
- **Alertas**: Contagem alta de erros/warnings

### **Performance**
- **Métricas**: CPU, memória, disco
- **Alertas**: Uso excessivo de recursos

## 📈 Métricas e KPIs

### **Deploy Metrics**
- **Tempo de Deploy**: < 5 minutos
- **Taxa de Sucesso**: > 95%
- **Tempo de Rollback**: < 2 minutos

### **Performance Metrics**
- **Uptime**: > 99.9%
- **Response Time**: < 200ms
- **Error Rate**: < 0.1%

## 🛠️ Troubleshooting

### **Problemas Comuns**

#### **Deploy Falha**
```bash
# Verificar logs
docker logs marabet-ai-production

# Verificar status dos containers
docker ps -a

# Verificar recursos
docker stats
```

#### **Health Check Falha**
```bash
# Testar endpoint manualmente
curl -f http://localhost:8000/health

# Verificar configuração do nginx
docker exec marabet-nginx-production nginx -t
```

#### **Banco de Dados**
```bash
# Verificar conexão
docker exec marabet-ai-production python -c "
from armazenamento.banco_de_dados import DatabaseManager
db = DatabaseManager()
db.test_connection()
"
```

### **Comandos Úteis**

```bash
# Reiniciar serviços
docker-compose restart

# Ver logs em tempo real
docker-compose logs -f

# Executar comandos no container
docker exec -it marabet-ai-production bash

# Backup do banco
docker exec marabet-ai-production python -c "
from armazenamento.banco_de_dados import DatabaseManager
db = DatabaseManager()
db.backup_database('/app/data/backup.db')
"
```

## 📚 Recursos Adicionais

### **Documentação**
- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker Compose](https://docs.docker.com/compose/)
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)

### **Ferramentas**
- [Docker Hub](https://hub.docker.com/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Trivy](https://trivy.dev/)

---

**MaraBet AI: Pipeline de Deploy Profissional e Confiável!** 🚀💰
