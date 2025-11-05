# ⚡ MARABET.COM - REFERÊNCIA RÁPIDA DE DEPLOY

**Deploy completo do zero ao HTTPS em 30 minutos**

---

## 🚀 COMANDOS SEQUENCIAIS

### **No Seu PC (Windows):**

```powershell
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. CRIAR KEY PAIR SSH (1 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

aws ec2 create-key-pair --key-name marabet-key --query 'KeyMaterial' --output text --region eu-west-1 > marabet-key.pem

.\Configurar-KeyPairWindows.ps1

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. LANÇAR EC2 INSTANCE (5 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

chmod +x lancar_ec2_completo.sh
./lancar_ec2_completo.sh

# Aguardar mensagem: ✅ EC2 INSTANCE CRIADA!

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. ALOCAR ELASTIC IP (1 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

chmod +x alocar_elastic_ip.sh
./alocar_elastic_ip.sh

# Anotar Elastic IP: XX.XX.XX.XX

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. CONFIGURAR DNS (2 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

chmod +x configurar_dns_completo.sh
./configurar_dns_completo.sh

# Resultado:
# ✅ marabet.com → Elastic IP
# ✅ www.marabet.com → Elastic IP
# ✅ api.marabet.com → Elastic IP

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. AGUARDAR PROPAGAÇÃO DNS (5-10 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Testar resolução
dig marabet.com +short
# Deve retornar: XX.XX.XX.XX (seu Elastic IP)

# Ou online
# https://dnschecker.org/#A/marabet.com
```

---

### **Na EC2 (via SSH):**

```bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. CONECTAR VIA SSH (1 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Do PC
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Ou usar script
./ssh-connect.sh

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. INSTALAR NGINX (já instalado se usou user-data.sh)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Verificar
nginx -v

# Se não estiver instalado
sudo apt-get update
sudo apt-get install -y nginx

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. CONFIGURAR NGINX (2 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Editar configuração
sudo nano /etc/nginx/sites-available/marabet

# Colar configuração de: nginx-marabet-config.conf
# Ou executar script:
# chmod +x instalar_nginx_completo.sh
# ./instalar_nginx_completo.sh

# Salvar: Ctrl+O, Enter, Ctrl+X

# Ativar site
sudo ln -sf /etc/nginx/sites-available/marabet /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Testar
sudo nginx -t

# Reload
sudo systemctl reload nginx

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 9. INSTALAR CERTBOT (1 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Verificar
certbot --version

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. OBTER SSL CERTIFICATE (5 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

sudo certbot --nginx \
  -d marabet.com \
  -d www.marabet.com \
  -d api.marabet.com \
  --non-interactive \
  --agree-tos \
  --email suporte@marabet.com \
  --redirect

# Resultado:
# ✅ SSL configurado
# ✅ Nginx atualizado
# ✅ HTTP → HTTPS redirect
# ✅ Auto-renewal ativo

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 11. TROCAR PARA USUÁRIO MARABET
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

sudo su - marabet
cd /opt/marabet

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 12. CONFIGURAR .env (2 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

nano .env

# Adicionar:
APP_URL=https://marabet.com
DATABASE_URL=postgresql://marabet_admin:GuF#Y(!j38Bgw|YyT<r0J5>yxD3n@database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com:5432/marabet_production
REDIS_URL=rediss://marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com:6379
API_FOOTBALL_KEY=71b2b62386f2d1275cd3201a73e1e045
TELEGRAM_BOT_TOKEN=<SEU_TOKEN>
TELEGRAM_CHAT_ID=5550091597

# Salvar: Ctrl+O, Enter, Ctrl+X

# Proteger
chmod 600 .env

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 13. TESTAR CONEXÕES (2 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# RDS
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com -p 5432 -U marabet_admin -d postgres
CREATE DATABASE marabet_production;
\q

# Redis
redis-cli -h marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com -p 6379 --tls --insecure
PING
exit

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 14. DEPLOY APLICAÇÃO (5 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Build e start
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Executar migrações
docker-compose exec app python manage.py migrate

# Coletar static files
docker-compose exec app python manage.py collectstatic --noinput

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 15. TESTAR (1 min)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Local
curl http://localhost/health
curl https://localhost/health -k

# Sair
exit

# Do PC
curl https://marabet.com/health

# Navegador
# https://marabet.com

# ✅ MARABET.COM NO AR!
```

---

## 📋 CHECKLIST RÁPIDO

```
PC:
- [ ] AWS CLI configurado
- [ ] Key Pair criada
- [ ] EC2 lançada
- [ ] Elastic IP alocado
- [ ] DNS configurado

EC2:
- [ ] SSH funcionando
- [ ] Nginx instalado
- [ ] Certbot instalado
- [ ] SSL obtido
- [ ] Usuário marabet ativo
- [ ] .env configurado
- [ ] RDS acessível
- [ ] Redis acessível
- [ ] Docker rodando
- [ ] App deployada

Final:
- [ ] https://marabet.com funcionando
- [ ] SSL Grade A+
- [ ] Logs OK
- [ ] Monitoramento ativo
```

---

## 🔗 ENDPOINTS

```
RDS:    database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com:5432
Redis:  marabet-redis-zxaq7e.serverless.euw1.cache.amazonaws.com:6379
Web:    https://marabet.com
API:    https://api.marabet.com
```

---

## 📞 COMANDOS ÚTEIS

```bash
# SSH
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Logs Nginx
sudo tail -f /var/log/nginx/marabet-error.log

# Logs App
sudo -u marabet docker-compose -f /opt/marabet/docker-compose.yml logs -f

# Restart Nginx
sudo systemctl reload nginx

# Restart App
sudo -u marabet docker-compose -f /opt/marabet/docker-compose.yml restart

# Renovar SSL
sudo certbot renew
```

---

**⚡ Deploy Rápido | ✅ 30 Minutos | 🔒 HTTPS**  
**🌐 marabet.com**

