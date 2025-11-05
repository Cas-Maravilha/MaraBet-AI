# ✅ VERIFICAR APLICAÇÃO - CHECKLIST COMPLETO

**Aplicação**: MaraBet AI  
**Ambiente**: Produção AWS  
**Domínio**: marabet.com

---

## 📋 CHECKLIST DE VERIFICAÇÃO

### **1. CONTAINERS (Na EC2)**

```bash
# Status dos containers
docker-compose ps

# Resultado esperado:
# NAME                 STATUS         PORTS
# marabet-web          Up (healthy)   0.0.0.0:8000->8000/tcp
# marabet-celery       Up             
# marabet-celery-beat  Up

# Se algum não estiver "Up":
docker-compose logs [nome-do-container]
```

---

### **2. HEALTH CHECK LOCAL (Na EC2)**

```bash
# Testar endpoint local
curl http://localhost:8000/health

# Resultado esperado:
# {"status":"ok","timestamp":"2025-10-27T12:34:56Z","database":"connected","redis":"connected"}

# Se retornar erro 502:
# - Verificar se container está rodando
# - Ver logs: docker-compose logs web

# Se retornar erro de conexão:
# - Verificar porta 8000: sudo lsof -i :8000
```

---

### **3. TESTE VIA IP PÚBLICO (Do PC)**

```bash
# Testar com IP público
curl http://[ELASTIC_IP]:8000/health

# Resultado esperado:
# {"status":"ok",...}

# Se não funcionar:
# - Verificar Security Group permite porta 8000
# - Verificar UFW: sudo ufw status
```

---

### **4. TESTE VIA DOMÍNIO HTTP (Do PC)**

```bash
# Testar via domínio (sem SSL)
curl http://marabet.com/health

# Resultado esperado:
# HTTP/1.1 301 Moved Permanently (redirect para HTTPS)
# OU
# {"status":"ok",...}

# Se não funcionar:
# - Verificar DNS: dig marabet.com
# - Verificar Nginx: sudo systemctl status nginx
```

---

### **5. TESTE VIA DOMÍNIO HTTPS (Do PC)**

```bash
# Testar via HTTPS
curl https://marabet.com/health

# Resultado esperado:
# {"status":"ok","timestamp":"...","database":"connected","redis":"connected"}

# Testar com detalhes
curl -I https://marabet.com/health

# Resultado esperado:
# HTTP/2 200
# server: nginx
# content-type: application/json
# strict-transport-security: max-age=63072000
```

---

### **6. TESTE NO NAVEGADOR**

#### **A. Página Principal:**

```
https://marabet.com

Verificar:
✅ Página carrega
✅ Cadeado verde 🔒
✅ CSS/JS carregados
✅ Imagens aparecem
✅ Sem erros no console (F12)
```

#### **B. Health Check:**

```
https://marabet.com/health

Resultado:
{"status":"ok","timestamp":"..."}
```

#### **C. API:**

```
https://api.marabet.com/status

OU

https://marabet.com/api/status
```

---

### **7. TESTAR DATABASE (RDS)**

```bash
# Na EC2, dentro do container
docker-compose exec web bash

# Testar conexão Python
python -c "
from db_config import test_connection
test_connection()
"

# OU via psql
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d marabet_production \
     -c 'SELECT COUNT(*) FROM pg_tables WHERE schemaname = '\''public'\'';'

# Resultado: Número de tabelas criadas
```

---

### **8. TESTAR REDIS (Cache)**

```bash
# Na EC2
redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com \
          -p 6379 \
          --tls \
          --insecure

# Comandos de teste:
PING
# Resultado: PONG

SET test_marabet "OK"
GET test_marabet
# Resultado: "OK"

DEL test_marabet

# Sair
exit
```

---

### **9. TESTAR API-FOOTBALL**

```bash
# Na EC2, dentro do container
docker-compose exec web python -c "
import requests
import os

API_KEY = os.getenv('API_FOOTBALL_KEY')
headers = {'x-apisports-key': API_KEY}

response = requests.get(
    'https://v3.football.api-sports.io/status',
    headers=headers
)

print(f'Status: {response.status_code}')
print(response.json())
"

# Resultado esperado:
# Status: 200
# {'response': {'account': {...}, 'requests': {...}}}
```

---

### **10. TESTAR TELEGRAM BOT**

```bash
# Na EC2, dentro do container
docker-compose exec web python -c "
import requests
import os

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
data = {
    'chat_id': CHAT_ID,
    'text': '🎉 MaraBet AI está rodando em produção na AWS!'
}

response = requests.post(url, json=data)
print(f'Status: {response.status_code}')
print('Mensagem enviada!' if response.status_code == 200 else 'Erro!')
"

# Verificar seu Telegram
```

---

## 🔍 VERIFICAÇÃO SSL/HTTPS

### **A. SSL Labs:**

```
https://www.ssllabs.com/ssltest/analyze.html?d=marabet.com

Objetivo: Grade A ou A+
```

### **B. Verificar Certificado:**

```bash
# Do PC
openssl s_client -connect marabet.com:443 -servername marabet.com < /dev/null 2>/dev/null | openssl x509 -noout -dates

# Resultado:
# notBefore=Oct 27 12:00:00 2025 GMT
# notAfter=Jan 25 12:00:00 2026 GMT
```

### **C. Headers de Segurança:**

```bash
curl -I https://marabet.com

# Verificar:
# ✅ strict-transport-security: max-age=63072000
# ✅ x-content-type-options: nosniff
# ✅ x-frame-options: SAMEORIGIN
```

---

## 📊 VERIFICAÇÃO COMPLETA

### **Script Automatizado:**

```bash
#!/bin/bash
# verificar-tudo.sh

echo "🔍 MaraBet AI - Verificação Completa"
echo "===================================="
echo ""

DOMAIN="marabet.com"

# 1. Containers
echo "1. Docker Containers:"
docker-compose ps | grep -q "Up" && echo "  ✅ Containers rodando" || echo "  ❌ Problemas"

# 2. Health Local
echo ""
echo "2. Health Check Local:"
curl -s http://localhost:8000/health > /dev/null && echo "  ✅ HTTP OK" || echo "  ❌ HTTP Falhou"

# 3. Health HTTPS
echo ""
echo "3. Health Check HTTPS:"
curl -s https://$DOMAIN/health > /dev/null && echo "  ✅ HTTPS OK" || echo "  ❌ HTTPS Falhou"

# 4. SSL Grade
echo ""
echo "4. SSL Certificate:"
openssl s_client -connect $DOMAIN:443 -servername $DOMAIN < /dev/null 2>/dev/null | grep -q "Verify return code: 0" && echo "  ✅ SSL Válido" || echo "  ⚠️  Verificar SSL"

# 5. Database
echo ""
echo "5. Database (RDS):"
docker-compose exec -T web nc -zv database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com 5432 2>&1 | grep -q "succeeded" && echo "  ✅ RDS Conectado" || echo "  ❌ RDS Não Conecta"

# 6. Redis
echo ""
echo "6. Cache (Redis):"
docker-compose exec -T web nc -zv marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com 6379 2>&1 | grep -q "succeeded" && echo "  ✅ Redis Conectado" || echo "  ❌ Redis Não Conecta"

# 7. Nginx
echo ""
echo "7. Nginx:"
sudo systemctl is-active nginx > /dev/null && echo "  ✅ Nginx Ativo" || echo "  ❌ Nginx Parado"

# 8. SSL Renewal
echo ""
echo "8. SSL Auto-Renewal:"
sudo systemctl is-active certbot.timer > /dev/null && echo "  ✅ Timer Ativo" || echo "  ⚠️  Timer Inativo"

echo ""
echo "✅ Verificação completa!"
echo ""
echo "Acessar: https://$DOMAIN"
```

---

## ✅ CHECKLIST FINAL

### **Infraestrutura:**
- [x] RDS PostgreSQL funcionando
- [x] Redis Serverless funcionando
- [x] VPC + Subnets configuradas
- [x] Security Groups corretos
- [x] Route 53 configurado

### **Aplicação:**
- [ ] Docker containers rodando
- [ ] Health check respondendo
- [ ] Database conectado
- [ ] Redis conectado
- [ ] Logs sem erros

### **Web:**
- [ ] Nginx funcionando
- [ ] SSL ativo
- [ ] HTTPS funcionando
- [ ] Redirect HTTP → HTTPS
- [ ] marabet.com acessível

### **Segurança:**
- [ ] SSL Grade A+
- [ ] Security headers ativos
- [ ] HSTS configurado
- [ ] Fail2Ban ativo
- [ ] UFW configurado

---

## 🎯 SE TUDO PASSOU

```bash
# Testar aplicação completa
curl https://marabet.com/health

# Resultado:
# {"status":"ok","timestamp":"2025-10-27T...","database":"connected","redis":"connected"}

# 🎉 MARABET.COM ESTÁ NO AR!
```

---

**✅ Aplicação Verificada e Funcionando!**  
**🌐 https://marabet.com**  
**☁️ AWS Production**  
**🎉 MARABET.COM NO AR! 🚀**
