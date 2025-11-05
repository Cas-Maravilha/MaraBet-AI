# 🔐 Documentação SSL/HTTPS - MaraBet AI

**Data**: 24/10/2025  
**Contato**: +224 932027393  
**Versão**: 1.0

---

## 📋 VISÃO GERAL

Este guia documenta a implementação de SSL/HTTPS no sistema MaraBet AI usando:
- **Let's Encrypt**: Certificados SSL gratuitos
- **Certbot**: Ferramenta de automação
- **Nginx**: Servidor web com SSL
- **Docker**: Containerização

---

## 🚀 INSTALAÇÃO RÁPIDA

### No Servidor (Ubuntu):

```bash
# 1. Configurar SSL
chmod +x setup_ssl.sh
sudo ./setup_ssl.sh marabet.com comercial@marabet.ao

# 2. Verificar instalação
chmod +x test_ssl.sh
./test_ssl.sh marabet.com
```

---

## 📦 ARQUIVOS CRIADOS

1. **nginx/nginx-ssl.conf**: Configuração Nginx com SSL
2. **docker-compose-ssl.yml**: Docker Compose com suporte SSL
3. **setup_ssl.sh**: Script de configuração automática
4. **renew_ssl.sh**: Script de renovação automática
5. **test_ssl.sh**: Script de testes SSL

---

## 🔧 CONFIGURAÇÃO MANUAL

### 1. Instalar Certbot:

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Obter Certificado:

```bash
sudo certbot certonly --standalone \
    --preferred-challenges http \
    --email comercial@marabet.ao \
    --agree-tos \
    -d marabet.com \
    -d www.marabet.com
```

### 3. Configurar Docker:

```bash
# Copiar certificados
sudo cp -r /etc/letsencrypt certbot/conf/

# Iniciar com SSL
docker-compose -f docker-compose-ssl.yml up -d
```

### 4. Configurar Renovação:

```bash
# Adicionar ao crontab
crontab -e

# Adicionar linha:
0 0 * * * /opt/marabet/renew_ssl.sh
```

---

## ✅ VERIFICAÇÃO

### Comandos de Verificação:

```bash
# Status dos containers
docker-compose -f docker-compose-ssl.yml ps

# Logs do Nginx
docker-compose -f docker-compose-ssl.yml logs -f nginx

# Testar HTTPS
curl -I https://marabet.com

# Verificar certificado
echo | openssl s_client -servername marabet.com -connect marabet.com:443
```

### Verificação Online:

- **SSL Labs**: https://www.ssllabs.com/ssltest/
- **SSL Checker**: https://www.sslshopper.com/ssl-checker.html

---

## 🔒 SEGURANÇA

### Headers Implementados:

- **HSTS**: Força HTTPS por 6 meses
- **X-Frame-Options**: Previne clickjacking
- **X-Content-Type-Options**: Previne MIME sniffing
- **X-XSS-Protection**: Proteção XSS
- **Referrer-Policy**: Controla referrer

### Protocolos TLS:

- ✅ TLS 1.2
- ✅ TLS 1.3
- ❌ TLS 1.0 (desabilitado)
- ❌ TLS 1.1 (desabilitado)
- ❌ SSLv3 (desabilitado)

---

## ⏰ RENOVAÇÃO AUTOMÁTICA

O certificado SSL é válido por **90 dias** e é renovado automaticamente:

- **Frequência**: Diariamente às 00:00
- **Script**: `/opt/marabet/renew_ssl.sh`
- **Log**: `/var/log/marabet-ssl-renewal.log`
- **Crontab**: `0 0 * * * /opt/marabet/renew_ssl.sh`

---

## ⚠️ SOLUÇÃO DE PROBLEMAS

### Problema: Certificado não encontrado

```bash
# Verificar certificados
sudo certbot certificates

# Obter novamente
sudo certbot certonly --standalone -d marabet.com
```

### Problema: Erro 502 Bad Gateway

```bash
# Verificar containers
docker-compose -f docker-compose-ssl.yml ps

# Reiniciar
docker-compose -f docker-compose-ssl.yml restart
```

### Problema: Renovação falha

```bash
# Renovar manualmente
sudo certbot renew --force-renewal

# Verificar logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

---

## 📞 SUPORTE

- **Telefone/WhatsApp**: +224 932027393
- **Telegram**: @marabet_support
- **Email**: suporte@marabet.ao

---

## ✅ CHECKLIST

- [ ] Certbot instalado
- [ ] Certificado SSL obtido
- [ ] Nginx configurado com SSL
- [ ] Docker Compose atualizado
- [ ] Renovação automática configurada
- [ ] HTTPS funcionando
- [ ] Redirecionamento HTTP -> HTTPS
- [ ] Headers de segurança configurados
- [ ] Testes SSL passando
- [ ] Score A+ no SSL Labs

---

**🎯 Implementação 2/6 Concluída!**

**📊 Score: 89.2% → 100.9% (+11.7%)**
