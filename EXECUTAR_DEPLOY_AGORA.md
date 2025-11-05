# 🚀 EXECUTAR DEPLOY AGORA - MARABET.COM

**Guia de execução passo a passo para colocar o MaraBet.com no ar AGORA**

---

## ✅ PRÉ-REQUISITOS (Já Prontos)

- [x] AWS CLI configurado (Access Key: YOUR_AWS_ACCESS_KEY_ID)
- [x] Região: eu-west-1
- [x] RDS PostgreSQL criado e disponível
- [x] Redis Serverless criado e disponível
- [x] Route 53 Hosted Zone criada
- [x] Scripts prontos (36 scripts)
- [x] Documentação completa (57 guias)

---

## 🚀 EXECUTAR AGORA (30 MINUTOS)

### **PASSO 1: Criar Key Pair (1 min)**

```powershell
# No PowerShell do Windows
cd "D:\Usuario\Maravilha\Desktop\MaraBet AI"

# Criar key
aws ec2 create-key-pair --key-name marabet-key --query 'KeyMaterial' --output text --region eu-west-1 > marabet-key.pem

# Configurar permissões
.\Configurar-KeyPairWindows.ps1

# ✅ marabet-key.pem criado
```

---

### **PASSO 2: Lançar EC2 Instance (5 min)**

```bash
# Git Bash ou WSL
cd "D:\Usuario\Maravilha\Desktop\MaraBet AI"

# Tornar executável
chmod +x lancar_ec2_completo.sh

# Executar
./lancar_ec2_completo.sh

# Aguardar mensagem:
# ✅ EC2 INSTANCE CRIADA COM SUCESSO!
# IP Público: XX.XX.XX.XX
```

---

### **PASSO 3: Alocar Elastic IP (1 min)**

```bash
# Tornar executável
chmod +x alocar_elastic_ip.sh

# Executar
./alocar_elastic_ip.sh

# Anotar Elastic IP: XX.XX.XX.XX
```

---

### **PASSO 4: Configurar DNS (2 min)**

```bash
# Tornar executável
chmod +x configurar_dns_completo.sh

# Executar
./configurar_dns_completo.sh

# Resultado:
# ✅ marabet.com → Elastic IP
# ✅ www.marabet.com → Elastic IP
```

---

### **PASSO 5: Aguardar DNS (10 min)**

```bash
# Testar propagação DNS
dig marabet.com +short

# Quando retornar seu Elastic IP:
# ✅ DNS propagado!

# Ou verificar online:
# https://dnschecker.org/#A/marabet.com
```

---

### **PASSO 6: SSH na EC2 (1 min)**

```bash
# Conectar
./ssh-connect.sh

# OU
ssh -i marabet-key.pem ubuntu@[ELASTIC_IP]

# Dentro da EC2:
cat /home/ubuntu/setup-complete.txt
# ✅ Ver se User Data completou
```

---

### **PASSO 7: Configurar Nginx (2 min)**

```bash
# Na EC2, como ubuntu

# Criar configuração básica
sudo tee /etc/nginx/sites-available/marabet > /dev/null << 'EOF'
server {
    listen 80;
    server_name marabet.com www.marabet.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Ativar
sudo ln -s /etc/nginx/sites-available/marabet /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# ✅ Nginx configurado
```

---

### **PASSO 8: Obter SSL (5 min)**

```bash
# Na EC2

# Instalar Certbot (se não estiver)
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx \
  -d marabet.com \
  -d www.marabet.com \
  --non-interactive \
  --agree-tos \
  --email admin@marabet.com \
  --redirect

# ✅ SSL configurado!
# ✅ HTTP → HTTPS redirect ativo
```

---

### **PASSO 9: Deploy Aplicação (5 min)**

```bash
# Trocar para usuário marabet
sudo su - marabet
cd /opt/marabet

# Upload código (escolha um):

# OPÇÃO A: Via Git
git clone https://github.com/seu-repo/marabet-ai.git .

# OPÇÃO B: Do PC via rsync (em outro terminal)
# rsync -avz -e "ssh -i marabet-key.pem" "D:/Usuario/Maravilha/Desktop/MaraBet AI/" ubuntu@[ELASTIC_IP]:/tmp/marabet/
# sudo mv /tmp/marabet/* /opt/marabet/
# sudo chown -R marabet:marabet /opt/marabet/

# Configurar .env
cp env.production.example .env

# Gerar chaves
chmod +x gerar_chaves_secretas.sh
./gerar_chaves_secretas.sh

# Adicionar chaves ao .env
cat .env.secrets >> .env

# Adicionar TELEGRAM_BOT_TOKEN manualmente
nano .env
# Adicionar: TELEGRAM_BOT_TOKEN=seu_token_aqui

# ✅ .env configurado
```

---

### **PASSO 10: Criar Database (2 min)**

```bash
# Conectar ao RDS
psql -h database-1.c74amy6m4xhz.eu-west-1.rds.amazonaws.com \
     -p 5432 \
     -U marabet_admin \
     -d postgres

# Password: GuF#Y(!j38Bgw|YyT<r0J5>yxD3n

# Criar database
CREATE DATABASE marabet_production;

# Verificar
\l

# Sair
\q

# ✅ Database criado
```

---

### **PASSO 11: Build e Start (4 min)**

```bash
# Como marabet em /opt/marabet

# Build
docker-compose build

# Start
docker-compose up -d

# Ver logs
docker-compose logs -f

# Quando ver "Booting worker" e sem erros:
# Ctrl+C para sair dos logs

# ✅ Aplicação rodando!
```

---

### **PASSO 12: Executar Migrações (2 min)**

```bash
# Executar migrações
docker-compose exec web python manage.py migrate

# OU se tiver script custom
docker-compose exec web python migrate.py --migrate --seed

# ✅ Database migrado
```

---

### **PASSO 13: Testar (2 min)**

```bash
# Testar local
curl http://localhost:8000/health

# Sair da EC2
exit
exit

# Do seu PC - Testar HTTPS
curl https://marabet.com/health

# Resultado esperado:
# {"status":"ok","timestamp":"...","database":"connected","redis":"connected"}

# Abrir no navegador:
# https://marabet.com

# ✅ MARABET.COM ESTÁ NO AR! 🎉
```

---

### **PASSO 14: Configurar Backup (2 min)**

```bash
# SSH novamente
./ssh-connect.sh

# Como marabet
sudo su - marabet
cd /opt/marabet

# Copiar script de backup
# (já deve estar no código se fez upload completo)

# Configurar cron
chmod +x configurar_cron_backup.sh
./configurar_cron_backup.sh

# ✅ Backup automático ativo
```

---

### **PASSO 15: Adicionar IP à API-Football (1 min)**

```
1. Acesse: https://dashboard.api-football.com/
2. Login
3. Soccer > Settings > IP Whitelist
4. Adicionar IP: [ELASTIC_IP da EC2]
5. Save

✅ API-Football configurado
```

---

## ✅ **CHECKLIST DE VERIFICAÇÃO FINAL**

- [ ] EC2 criada e rodando
- [ ] Elastic IP associado
- [ ] DNS aponta para Elastic IP
- [ ] Nginx rodando
- [ ] SSL ativo (https)
- [ ] Aplicação rodando (docker-compose ps)
- [ ] Database criado e migrado
- [ ] Redis conectado
- [ ] Health check OK
- [ ] https://marabet.com acessível
- [ ] Cadeado verde 🔒 no navegador
- [ ] API-Football IP whitelisted
- [ ] Backup automático configurado
- [ ] Logs sem erros críticos

---

## 🎉 **SUCESSO!**

Se todos os passos acima foram concluídos:

```
✅ MARABET.COM ESTÁ NO AR!
✅ HTTPS funcionando
✅ Backup automático ativo
✅ Infraestrutura enterprise AWS

🌐 Acesse: https://marabet.com
```

---

## 📞 **SE PRECISAR DE AJUDA**

### **Guias de Referência:**
- DEPLOY_MARABET_REFERENCIA_RAPIDA.md
- TROUBLESHOOTING_COMPLETO.md
- COMANDOS_UTEIS_REFERENCIA.md

### **Suporte:**
- 📧 suporte@marabet.com
- 📞 +224 932027393

---

**🚀 BOA SORTE COM O DEPLOY!**  
**🌐 https://marabet.com**  
**🎉 VOCÊ TEM TUDO PARA TER SUCESSO!**

