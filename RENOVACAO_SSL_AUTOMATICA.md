# 🔄 RENOVAÇÃO AUTOMÁTICA SSL - GUIA COMPLETO

**Certificado**: Let's Encrypt  
**Validade**: 90 dias  
**Renovação**: Automática (60 dias antes)

---

## 📋 ÍNDICE

1. [Como Funciona](#como-funciona)
2. [Verificar Auto-Renewal](#verificar-auto-renewal)
3. [Testar Renovação](#testar-renovação)
4. [Configurar Manualmente](#configurar-manualmente-se-necessário)
5. [Monitoramento](#monitoramento)

---

## ⚙️ COMO FUNCIONA

### **Let's Encrypt:**

```
Certificado válido por:   90 dias
Renovação automática:     60 dias antes (aos 30 dias restantes)
Método:                   Certbot + systemd timer
Frequência:               2x por dia (verificação)
Downtime:                 Zero (Nginx reload automático)
```

### **Processo Automático:**

```
1. Certbot verifica expiração (2x/dia)
2. Se < 30 dias restantes:
   ├── Solicita novo certificado
   ├── Valida via HTTP/.well-known/
   ├── Atualiza certificados
   └── Recarrega Nginx (sem downtime)
3. Envia notificação (se configurado)
```

---

## 1️⃣ VERIFICAR AUTO-RENEWAL

### **A. Systemd Timer (Método Moderno):**

```bash
# Verificar se timer está ativo
sudo systemctl status certbot.timer

# Resultado esperado:
# ● certbot.timer - Run certbot twice daily
#    Loaded: loaded
#    Active: active (waiting)
```

```bash
# Listar todos os timers
sudo systemctl list-timers | grep certbot

# Resultado:
# NEXT                         LEFT     LAST                         PASSED  UNIT            ACTIVATES
# Tue 2025-10-28 12:00:00 WAT  1h left  Tue 2025-10-27 12:00:00 WAT  12h ago certbot.timer   certbot.service
```

```bash
# Ver configuração do timer
sudo systemctl cat certbot.timer

# Resultado mostra:
# OnCalendar=*-*-* 00,12:00:00  (2x por dia: 00:00 e 12:00)
```

### **B. Cron (Método Tradicional):**

```bash
# Ver crontab do root
sudo crontab -l

# Pode conter:
# 0 12 * * * /usr/bin/certbot renew --quiet
# OU
# 0 0,12 * * * /usr/bin/certbot renew --quiet
```

---

## 2️⃣ TESTAR RENOVAÇÃO

### **Dry-Run (Teste Sem Renovar):**

```bash
# Testar renovação sem efetivamente renovar
sudo certbot renew --dry-run

# Resultado esperado:
# Processing /etc/letsencrypt/renewal/marabet.com.conf
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Cert not due for renewal, but simulating renewal for dry run
# Renewing an existing certificate for marabet.com and www.marabet.com
# 
# Successfully received certificate.
# Certificate not yet due for renewal
# 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Congratulations, all simulated renewals succeeded:
#   /etc/letsencrypt/live/marabet.com/fullchain.pem (success)
```

✅ Se ver "Congratulations" = Auto-renewal está funcionando!

### **Forçar Renovação (Teste Real):**

```bash
# ⚠️ Só use se certificado estiver expirando ou para teste

# Renovar mesmo que não esteja próximo de expirar
sudo certbot renew --force-renewal

# Verificar
sudo certbot certificates
```

---

## 3️⃣ CONFIGURAR MANUALMENTE (Se Necessário)

### **A. Habilitar Systemd Timer:**

```bash
# Habilitar timer
sudo systemctl enable certbot.timer

# Iniciar timer
sudo systemctl start certbot.timer

# Verificar
sudo systemctl status certbot.timer
```

### **B. Configurar Cron (Alternativa):**

```bash
# Editar crontab do root
sudo crontab -e

# Adicionar (se não existir):
0 0,12 * * * /usr/bin/certbot renew --quiet --deploy-hook "systemctl reload nginx"

# Explicação:
# 0 0,12 * * *     = À meia-noite e ao meio-dia, todos os dias
# certbot renew    = Renova certificados que precisam
# --quiet          = Modo silencioso (sem output)
# --deploy-hook    = Executa após renovação bem-sucedida
```

### **C. Script Personalizado:**

```bash
# Criar script de renovação
sudo tee /usr/local/bin/renew-marabet-ssl.sh > /dev/null << 'EOF'
#!/bin/bash

# Renovar certificados
certbot renew --quiet

# Se houve renovação, recarregar Nginx
if [ $? -eq 0 ]; then
    systemctl reload nginx
    
    # Opcional: Enviar notificação
    curl -s "https://api.telegram.org/bot<TOKEN>/sendMessage" \
        -d "chat_id=<CHAT_ID>" \
        -d "text=🔒 SSL renovado em marabet.com" > /dev/null
fi
EOF

sudo chmod +x /usr/local/bin/renew-marabet-ssl.sh

# Adicionar ao cron
sudo crontab -e
# Adicionar: 0 2 * * * /usr/local/bin/renew-marabet-ssl.sh
```

---

## 4️⃣ MONITORAMENTO

### **A. Ver Quando Expira:**

```bash
# Listar todos os certificados
sudo certbot certificates

# Resultado mostra:
# Certificate Name: marabet.com
#   Domains: marabet.com www.marabet.com
#   Expiry Date: 2026-01-25 12:00:00+00:00 (VALID: 89 days)
#   Certificate Path: /etc/letsencrypt/live/marabet.com/fullchain.pem
#   Private Key Path: /etc/letsencrypt/live/marabet.com/privkey.pem

# Ou via OpenSSL
sudo openssl x509 -in /etc/letsencrypt/live/marabet.com/fullchain.pem -noout -dates

# Resultado:
# notBefore=Oct 27 12:00:00 2025 GMT
# notAfter=Jan 25 12:00:00 2026 GMT
```

### **B. Ver Logs de Renovação:**

```bash
# Logs do Certbot
sudo cat /var/log/letsencrypt/letsencrypt.log

# Últimas 50 linhas
sudo tail -50 /var/log/letsencrypt/letsencrypt.log

# Filtrar apenas renovações
sudo grep "renew" /var/log/letsencrypt/letsencrypt.log
```

### **C. Histórico de Renovações:**

```bash
# Ver quando foi renovado pela última vez
sudo ls -la /etc/letsencrypt/live/marabet.com/

# Ver data de criação dos certificados
sudo stat /etc/letsencrypt/live/marabet.com/fullchain.pem
```

---

## 5️⃣ NOTIFICAÇÕES DE EXPIRAÇÃO

### **A. Email Automático:**

Let's Encrypt envia emails automáticos quando:
- Faltam 20 dias para expirar
- Faltam 10 dias para expirar
- Faltam 1 dia para expirar

Para o email: `admin@marabet.com` (configurado no Certbot)

### **B. Alarme CloudWatch (AWS):**

```bash
# Criar alarme para expiração de SSL
# (Requer métrica personalizada)

# Script para enviar métrica
cat > /usr/local/bin/ssl-expiry-metric.sh << 'EOF'
#!/bin/bash

EXPIRY=$(openssl x509 -in /etc/letsencrypt/live/marabet.com/fullchain.pem -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

aws cloudwatch put-metric-data \
    --namespace MaraBet \
    --metric-name SSLDaysToExpiry \
    --value $DAYS_LEFT \
    --region eu-west-1
EOF

chmod +x /usr/local/bin/ssl-expiry-metric.sh

# Adicionar ao cron (diário)
# 0 6 * * * /usr/local/bin/ssl-expiry-metric.sh
```

---

## 🧪 COMANDOS DE TESTE

### **Verificação Completa:**

```bash
#!/bin/bash
# verificar-ssl.sh

echo "🔒 Verificação SSL/HTTPS MaraBet"
echo "================================="
echo ""

# 1. Certbot timer
echo "1. Auto-Renewal Timer:"
sudo systemctl is-active certbot.timer && echo "  ✅ Ativo" || echo "  ❌ Inativo"

# 2. Certificados
echo ""
echo "2. Certificados:"
sudo certbot certificates 2>/dev/null | grep -A 5 "Certificate Name: marabet.com" | grep "Expiry Date"

# 3. Próxima verificação
echo ""
echo "3. Próxima verificação automática:"
sudo systemctl list-timers certbot.timer --no-pager | grep certbot

# 4. Teste de renovação
echo ""
echo "4. Teste de renovação (dry-run):"
echo "   Executando..."
sudo certbot renew --dry-run --quiet 2>&1 | tail -1

# 5. HTTPS funcionando
echo ""
echo "5. HTTPS Status:"
curl -s -o /dev/null -w "%{http_code}" https://localhost -k
echo "   Código: $(curl -s -o /dev/null -w "%{http_code}" https://localhost -k 2>/dev/null)"

echo ""
echo "✅ Verificação completa!"
```

---

## ⚠️ TROUBLESHOOTING

### **Timer não está ativo:**

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### **Renovação falhou:**

```bash
# Ver logs de erro
sudo cat /var/log/letsencrypt/letsencrypt.log | grep -i error

# Renovar manualmente
sudo certbot renew --verbose

# Verificar problemas
sudo certbot renew --dry-run --verbose
```

### **Nginx não recarrega após renovação:**

```bash
# Adicionar deploy-hook
sudo certbot renew --deploy-hook "systemctl reload nginx"

# Ou configurar no renewal config
sudo nano /etc/letsencrypt/renewal/marabet.com.conf

# Adicionar:
# renew_hook = systemctl reload nginx
```

---

## 📊 CRONOGRAMA DE RENOVAÇÃO

```
Dia 0:      Certificado obtido (válido por 90 dias)
Dia 30:     Primeiro aviso de renovação (60 dias restantes)
Dia 60:     Renovação automática executada
Dia 70:     Email de aviso (20 dias restantes)
Dia 80:     Email urgente (10 dias restantes)
Dia 89:     Email crítico (1 dia restante)
Dia 90:     Expiração (se não renovar)
```

**Com auto-renewal**: Renova no dia 60, sempre!

---

## ✅ CHECKLIST

- [ ] Certbot instalado
- [ ] Certificado obtido
- [ ] Systemd timer ativo
- [ ] Ou cron configurado
- [ ] Dry-run testado e passou
- [ ] Email de notificação configurado
- [ ] Deploy-hook configurado (reload nginx)
- [ ] Logs monitorados
- [ ] Alarmes CloudWatch (opcional)
- [ ] Documentação de recovery

---

## 📞 COMANDOS RÁPIDOS

```bash
# Status
sudo systemctl status certbot.timer

# Testar
sudo certbot renew --dry-run

# Renovar agora
sudo certbot renew

# Ver certificados
sudo certbot certificates

# Logs
sudo tail -50 /var/log/letsencrypt/letsencrypt.log
```

---

**🔄 Renovação Automática Ativa!**  
**✅ Zero Manutenção Necessária**  
**🔒 SSL Sempre Válido**  
**🌐 marabet.com Seguro 24/7**

