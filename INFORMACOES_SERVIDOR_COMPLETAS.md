# 🖥️ INFORMAÇÕES COMPLETAS DO SERVIDOR MARABET

**Data**: 28/10/2025  
**Domínio**: marabet.ao  
**Status**: ✅ Running

---

## 📊 ESPECIFICAÇÕES DO SERVIDOR

### **Informações Básicas**
```
Nome do Servidor: marabet.ao
Hostname: marabet.ao
IP Principal: 37.27.220.67
DNS Reverso: static.67.220.27.37.clients.your-server.de
IPv6: 2a01:4f9:c013:b3f1::/64
Status: Running ✅
```

### **Hardware**
```
CPU: 4 cores
RAM: 8 GB
Disco: 80 GB
Sistema: Ubuntu 22.04 LTS
```

### **Acesso**
```
Usuário: root
IP: 37.27.220.67
SSH: ssh root@37.27.220.67
```

### **Recursos**
```
Backups: Disabled (configurar após deploy)
Rede: -
Banda: 0 GB usados
```

---

## ✅ CHECKLIST DE CONFIGURAÇÃO

### **1. IP Whitelist API-Football** ⚠️ CRÍTICO
```
IP para adicionar: 37.27.220.67
Dashboard: https://dashboard.api-football.com/
Description: MaraBet AI - Production Server (marabet.ao)
Status: PENDING ⏳
```

### **2. Configurações de Produção**

#### **.env (Variáveis de Ambiente)**
```bash
# Sistema
ALLOWED_HOSTS=localhost,127.0.0.1,37.27.220.67,marabet.ao,www.marabet.ao
SYSTEM_IP=37.27.220.67
DEBUG=False

# PostgreSQL (configurar após instalação)
DATABASE_URL=postgresql://marabet_user:SENHA@localhost:5432/marabet

# Redis
REDIS_URL=redis://localhost:6379

# API-Football
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045

# Telegram
TELEGRAM_BOT_TOKEN=8227157482:AAFNRXjutCu46t1EMjjNnuvtrcYEYI0ndgg
TELEGRAM_CHAT_ID=5550091597
```

---

## 🚀 PLANO DE DEPLOY

### **Fase 1: Configuração Inicial**
1. ✅ Conectar: `ssh root@37.27.220.67`
2. ✅ Atualizar sistema: `apt update && apt upgrade -y`
3. ✅ Instalar utilitários básicos
4. ✅ Configurar firewall (UFW)

### **Fase 2: Banco de Dados**
5. ✅ Instalar PostgreSQL 15
6. ✅ Criar banco e usuário
7. ✅ Configurar segurança (localhost apenas)

### **Fase 3: Docker**
8. ✅ Instalar Docker
9. ✅ Instalar Docker Compose
10. ✅ Verificar instalação

### **Fase 4: Aplicação**
11. ✅ Enviar código via SCP
12. ✅ Configurar .env
13. ✅ Executar migrações
14. ✅ Iniciar containers

### **Fase 5: Web Server**
15. ✅ Instalar Nginx
16. ✅ Configurar virtual host
17. ✅ Instalar Certbot
18. ✅ Obter SSL

### **Fase 6: DNS**
19. ⏳ Configurar DNS (marabet.ao → 37.27.220.67)
20. ⏳ Aguardar propagação

### **Fase 7: Verificações**
21. ⏳ Testar aplicação
22. ⏳ Configurar backup
23. ⏳ Configurar monitoramento

---

## 🔒 CONFIGURAÇÕES DE SEGURANÇA

### **Firewall (UFW)**
```bash
# Permitir portas essenciais
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# Bloquear PostgreSQL externamente
ufw deny 5432/tcp

# Ativar firewall
ufw enable
```

### **PostgreSQL**
- ✅ Escutar apenas localhost
- ✅ Autenticação md5
- ✅ Firewall bloqueando porta externa

### **SSL/HTTPS**
- ✅ Let's Encrypt (gratuito)
- ✅ Renovação automática
- ✅ TLS 1.3

---

## 📊 MONITORAMENTO

### **Recursos do Servidor**
```
CPU: 4 cores
RAM: 8 GB (suficiente para desenvolvimento e produção inicial)
Disco: 80 GB (expandir conforme necessário)
```

### **Verificações Diárias**
```bash
# Espaço em disco
df -h

# Uso de memória
free -h

# CPU
top

# Containers
docker stats
```

---

## 💾 BACKUP

### **Configurar Backup Automático**
```bash
# PostgreSQL
pg_dump -h localhost -U marabet_user marabet > backup.sql

# Redis
redis-cli save

# Arquivos
tar -czf backup_$(date +%Y%m%d).tar.gz /opt/marabet/
```

### **Backups no Servidor**
- Status atual: Disabled
- Recomendação: Habilitar após deploy
- Frequência: Diário (manutenção 30 dias)

---

## 🌐 DNS - CONFIGURAR DOMÍNIO

### **Registros DNS Necessários**

```
Tipo    Nome           Conteúdo          TTL
A       @              37.27.220.67      3600
A       www            37.27.220.67      3600
CNAME   www            marabet.ao        3600
```

### **Nameservers**
- Atualmente: N/A
- Configurar via provedor do domínio

---

## 📝 COMANDOS ÚTEIS

### **Conectar ao Servidor**
```bash
ssh root@37.27.220.67
```

### **Verificar Status**
```bash
# Sistema
systemctl status

# Docker
docker ps
docker-compose ps

# Nginx
systemctl status nginx

# PostgreSQL
systemctl status postgresql
```

### **Logs**
```bash
# Aplicação
docker-compose logs -f web

# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Sistema
journalctl -xe
```

### **Reiniciar Serviços**
```bash
# Aplicação
docker-compose restart

# Nginx
systemctl restart nginx

# PostgreSQL
systemctl restart postgresql
```

---

## ✅ STATUS ATUAL

| Item | Status | Nota |
|------|--------|------|
| **Servidor** | ✅ Running | Ubuntu 22.04 |
| **IP Configurado** | ✅ 37.27.220.67 | Fixo |
| **Acesso SSH** | ✅ root@37.27.220.67 | Pronto |
| **IP API-Football** | ⏳ Pendente | Adicionar agora |
| **PostgreSQL** | ⏳ Instalar | Script pronto |
| **Docker** | ⏳ Instalar | Guia pronto |
| **Aplicação** | ⏳ Deploy | Pronto para enviar |
| **SSL** | ⏳ Configurar | Após deploy |
| **DNS** | ⏳ Configurar | marabet.ao |

---

## 🎯 PRÓXIMAS AÇÕES IMEDIATAS

### **1. Adicionar IP na API-Football** (URGENTE)
```
Dashboard: https://dashboard.api-football.com/
IP: 37.27.220.67
```

### **2. Conectar e Instalar PostgreSQL**
```bash
ssh root@37.27.220.67
scp install_postgresql_secure.sh root@37.27.220.67:/tmp/
sudo /tmp/install_postgresql_secure.sh
```

### **3. Enviar Código**
```bash
scp -r * root@37.27.220.67:/opt/marabet/
```

---

**📄 Guia Completo**: `DEPLOY_EXECUTAR_AGORA.md`  
**📧 Suporte**: suporte@marabet.ao  
**📞 WhatsApp**: +224 932027393

