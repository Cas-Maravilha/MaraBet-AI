# MaraBet AI - Documentação de Produção

## 🚀 Deploy em Produção

### Pré-requisitos
- AWS CLI configurado
- Docker instalado
- Python 3.11+
- PostgreSQL
- Redis

### Configuração
1. Copie `.env.production` para `.env`
2. Configure as variáveis de ambiente
3. Execute o script de deploy

### Deploy AWS
```bash
./deploy/scripts/deploy_aws.sh
```

### Deploy Docker
```bash
docker-compose -f deploy/docker/docker-compose.production.yml up -d
```

### Monitoramento
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Logs: ./logs/

### Backup
```bash
./deploy/scripts/backup.sh
```

## 🔒 Segurança
- Todas as chaves em variáveis de ambiente
- HTTPS configurado
- Firewall ativo
- Backup automático

## 📊 Monitoramento
- Health checks a cada 60s
- Métricas em tempo real
- Alertas configurados
- Logs centralizados
