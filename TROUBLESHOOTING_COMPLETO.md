# 🔧 TROUBLESHOOTING COMPLETO - MARABET.COM

**Guia de resolução de problemas comuns**

---

## ❌ PROBLEMA: APLICAÇÃO NÃO INICIA

### **Sintomas:**
- Container web não sobe
- Status: Exit(1) ou Restarting

### **Diagnóstico:**

```bash
# 1. Ver logs detalhados
docker-compose logs web

# 2. Ver logs completos (sem truncar)
docker-compose logs --tail=200 web

# 3. Tentar iniciar em foreground (ver erros)
docker-compose up web
```

### **Causas Comuns:**

#### **A. Erro de Conexão Database:**

```bash
# Verificar variáveis
docker-compose exec web env | grep DATABASE

# Resultado esperado:
# DATABASE_URL=postgresql://marabet_admin:...@database-1.c74amy6m4xhz...

# Testar conexão Python
docker-compose exec web python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    print('✅ Conexão OK')
    conn.close()
except Exception as e:
    print(f'❌ Erro: {e}')
"

# Testar conectividade de rede
docker-compose exec web nc -zv database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com 5432
```

**Solução:**
```bash
# Verificar .env tem DATABASE_URL correto
cat .env | grep DATABASE_URL

# Verificar Security Group RDS permite conexão da EC2
```

#### **B. Porta 8000 em Uso:**

```bash
# Ver o que está usando porta 8000
sudo netstat -tlnp | grep :8000
# OU
sudo lsof -i :8000

# Matar processo
sudo kill -9 [PID]

# Ou mudar porta no docker-compose.yml
# ports: - "8001:8000"
```

#### **C. Erro no Código:**

```bash
# Ver stack trace completo
docker-compose logs web | grep -A 20 "Error\|Exception"

# Shell no container para debug
docker-compose run --rm web bash
python -c "import app"  # Testar import
```

**Solução:**
```bash
# Corrigir código
# Rebuild
docker-compose build --no-cache web
docker-compose up -d
```

---

## ❌ PROBLEMA: HTTPS NÃO FUNCIONA

### **Sintomas:**
- https://marabet.com não carrega
- Erro SSL

### **Diagnóstico:**

```bash
# 1. Nginx está rodando?
sudo systemctl status nginx

# 2. Certificado SSL existe?
sudo ls -la /etc/letsencrypt/live/marabet.com/

# 3. Nginx configurado para HTTPS?
sudo nginx -t
sudo cat /etc/nginx/sites-enabled/marabet | grep 443

# 4. Porta 443 aberta?
sudo netstat -tlnp | grep :443

# 5. Testar SSL
openssl s_client -connect marabet.com:443 -servername marabet.com
```

**Solução:**
```bash
# Reobter certificado
sudo certbot --nginx -d marabet.com -d www.marabet.com

# Restart Nginx
sudo systemctl restart nginx
```

---

## ❌ PROBLEMA: DATABASE CONNECTION ERROR

### **Sintomas:**
- "Could not connect to database"
- "Connection refused"

### **Diagnóstico:**

```bash
# 1. Testar de fora do container
nc -zv database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com 5432

# 2. Ver erro específico
docker-compose logs web | grep -i "database\|postgres"

# 3. Verificar .env
cat .env | grep DATABASE_URL

# 4. Testar psql direto
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d marabet_production
```

**Soluções:**

```bash
# A. Security Group
# Verificar se EC2 SG está permitido no RDS SG
aws ec2 describe-security-groups --group-ids sg-09f7d3d37a8407f43 --region eu-west-1

# B. Credenciais erradas
# Verificar .env tem senha correta
# Password: GuF#Y(!j38Bgw|YyT<r0J5>yxD3n

# C. Database não existe
# Criar database
psql -h database-1... -U marabet_admin -d postgres
CREATE DATABASE marabet_production;
\q
```

---

## ❌ PROBLEMA: REDIS CONNECTION ERROR

### **Sintomas:**
- "Redis connection failed"
- "Connection timeout"

### **Diagnóstico:**

```bash
# 1. Testar conectividade
nc -zv marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com 6379

# 2. Testar com redis-cli
redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com \
          -p 6379 \
          --tls \
          --insecure \
          ping

# 3. Verificar .env
cat .env | grep REDIS_URL

# 4. Ver erro no log
docker-compose logs web | grep -i redis
```

**Solução:**
```bash
# Verificar Security Group Redis permite conexão da EC2
# Redis Serverless: sg-09f7d3d37a8407f43
```

---

## ❌ PROBLEMA: ALTO USO DE CPU

### **Sintomas:**
- CPU > 80%
- Aplicação lenta

### **Diagnóstico:**

```bash
# 1. Ver processos
htop

# 2. Ver containers
docker stats

# 3. Ver logs de queries lentas (RDS)
# AWS Console > RDS > database-1 > Monitoring > Performance Insights
```

**Soluções:**

```bash
# A. Escalar verticalmente
# Aumentar EC2 para t3.large
aws ec2 modify-instance-attribute \
  --instance-id [ID] \
  --instance-type t3.large

# B. Otimizar queries
# Adicionar índices no database
# Usar cache Redis mais agressivamente

# C. Adicionar mais workers Gunicorn
# docker-compose.yml:
# command: gunicorn ... --workers 8
```

---

## ❌ PROBLEMA: DISCO CHEIO

### **Sintomas:**
- df -h mostra > 90%
- "No space left on device"

### **Diagnóstico:**

```bash
# Ver uso
df -h

# Ver maiores diretórios
sudo du -h /opt/marabet | sort -rh | head -20

# Ver maiores arquivos de log
sudo find /var/log -type f -size +100M -exec ls -lh {} \;
```

**Soluções:**

```bash
# 1. Limpar logs
sudo journalctl --vacuum-size=100M
sudo find /var/log -name "*.log" -mtime +7 -delete

# 2. Limpar Docker
docker system prune -a -f --volumes

# 3. Limpar backups locais
rm -rf /opt/marabet/backups/*.gz

# 4. Aumentar volume EBS (AWS Console)
# EC2 > Volumes > Modify (aumentar tamanho)
# Depois: sudo resize2fs /dev/xvda1
```

---

## ❌ PROBLEMA: BACKUP FALHOU

### **Sintomas:**
- Backup não aparece no S3
- Erro no log de backup

### **Diagnóstico:**

```bash
# Ver log de backup
tail -100 /var/log/marabet/backup.log

# Testar AWS CLI
aws s3 ls s3://marabet-backups/

# Verificar credenciais AWS
aws sts get-caller-identity
```

**Soluções:**

```bash
# Executar backup manualmente
sudo -u marabet /opt/marabet/backups/scripts/backup_to_s3.sh

# Ver saída completa para debug
```

---

## ❌ PROBLEMA: SSL EXPIRADO

### **Sintomas:**
- Erro de certificado no navegador
- "Certificate expired"

### **Diagnóstico:**

```bash
# Ver certificados
sudo certbot certificates

# Ver data de expiração
sudo openssl x509 -in /etc/letsencrypt/live/marabet.com/fullchain.pem -noout -dates
```

**Solução:**

```bash
# Renovar manualmente
sudo certbot renew --force-renewal

# Reload Nginx
sudo systemctl reload nginx

# Verificar auto-renewal
sudo certbot renew --dry-run
sudo systemctl status certbot.timer
```

---

## ❌ PROBLEMA: SITE LENTO

### **Diagnóstico:**

```bash
# 1. Response time
time curl https://marabet.com

# 2. Ver logs de acesso (slow requests)
sudo grep -E '"[5-9][0-9]{2,} ' /var/log/nginx/marabet-access.log

# 3. Queries lentas no RDS
# Performance Insights no Console AWS

# 4. Cache hit rate
redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com \
          -p 6379 --tls --insecure INFO stats | grep hit_rate
```

**Soluções:**

```bash
# 1. Otimizar database
psql ... -c "VACUUM ANALYZE;"

# 2. Limpar cache antigo
redis-cli ... FLUSHDB  # (cuidado!)

# 3. Aumentar workers
# docker-compose.yml: --workers 8

# 4. Adicionar CDN (CloudFront)
```

---

## 🆘 MATRIZ DE PROBLEMAS

| Problema | Verificar | Solução Rápida |
|----------|-----------|----------------|
| **Container não sobe** | `docker-compose logs` | `docker-compose restart` |
| **HTTPS não funciona** | `sudo nginx -t` | `sudo certbot renew` |
| **DB connection** | `nc -zv database-1... 5432` | Verificar Security Group |
| **Redis connection** | `nc -zv marabet-redis... 6379` | Verificar Security Group |
| **CPU alta** | `htop` | Otimizar código/queries |
| **RAM alta** | `free -h` | Reiniciar containers |
| **Disco cheio** | `df -h` | Limpar logs/Docker |
| **Site lento** | `time curl` | Cache/Otimizar DB |
| **Backup falhou** | `tail backup.log` | Rodar manual |

---

## 📞 SUPORTE

**Verificação Completa:**
```bash
# Execute este script para diagnóstico completo
./scripts/verificar-tudo.sh

# Ou
curl -s https://marabet.com/api/diagnostics
```

**Contatos:**
- 📧 Técnico: suporte@marabet.com
- 📧 Emergência: admin@marabet.com
- 📞 WhatsApp: +224 932027393

---

**🔧 Troubleshooting Completo!**  
**✅ Soluções para Todos os Problemas**  
**🌐 marabet.com Enterprise**

