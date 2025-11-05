# 🇦🇴 RESUMO DA MIGRAÇÃO PARA ANGOWEB

**Data**: 2025  
**Servidor**: Angoweb (95.216.143.185)  
**Domínio**: marabet.ao  

---

## ✅ ALTERAÇÕES REALIZADAS

### **1. README.md - Atualizado para Angoweb**
- ❌ Removidas todas referências à AWS
- ✅ Adicionadas configurações da Angoweb
- ✅ PostgreSQL e Redis hospedados localmente
- ✅ Domínio .ao (marabet.ao)
- ✅ Suporte local: +244 222 638 200
- ✅ Guia de deploy atualizado

### **2. config_production.env - Configurado**
```bash
# Conexão local PostgreSQL
DATABASE_URL=postgresql://marabeta_marabet:"LT/x%6,jb@localhost:5432/marabet

# Conexão local Redis
REDIS_URL=redis://localhost:6379

# Hosts permitidos
ALLOWED_HOSTS=localhost,127.0.0.1,marabet.ao,www.marabet.ao
```

### **3. docker-compose.production.yml - Atualizado**
- ✅ Comentários atualizados para "Angoweb Deployment"
- ✅ Configuração mantida (funciona local)

### **4. DOCKER_COMPOSE_GUIA.md - Atualizado**
- ✅ Ambiente alterado para "Produção Angoweb (Luanda, Angola)"
- ✅ Troubleshooting com conexões locais

### **5. ANGOWEB_DEPLOYMENT_GUIDE.md - Criado**
- ✅ Guia completo de 500+ linhas
- ✅ Deploy rápido (TL;DR)
- ✅ 10 seções detalhadas
- ✅ Duas opções de instalação (automática e manual)

### **6. install_postgresql_secure.sh - Criado**
- ✅ Script de instalação automática do PostgreSQL 15
- ✅ Configuração de segurança
- ✅ Geração automática de senha forte
- ✅ Firewall configurado
- ✅ Credenciais salvas em `/opt/marabet/.env.db`

### **7. COMANDOS_SERVIDOR.txt - Criado**
- ✅ Lista completa de comandos para executar no servidor
- ✅ 12 passos detalhados
- ✅ Verificações finais

---

## 🚀 DEPLOY NA ANGOWEB

### **Servidor Configurado:**
```
IP: 95.216.143.185
Usuário: marabet
OS: Linux (Ubuntu/Debian)
```

### **Deploy Rápido:**

**1. Enviar Script de Instalação:**
```bash
scp install_postgresql_secure.sh marabet@95.216.143.185:/tmp/
```

**2. Conectar e Instalar PostgreSQL:**
```bash
ssh marabet@95.216.143.185
sudo /tmp/install_postgresql_secure.sh
```

**3. Ver Credenciais:**
```bash
cat /opt/marabet/.env.db
```

**4. Enviar Código da Aplicação:**
```bash
# Do seu PC
scp -r * marabet@95.216.143.185:/opt/marabet/
```

**5. Configurar e Iniciar:**
```bash
# No servidor
cd /opt/marabet
cp config_production.env .env
nano .env  # Ajustar DATABASE_URL com credenciais geradas
python migrate.py --migrate --seed
docker-compose -f docker-compose.production.yml up -d
```

**6. Configurar SSL:**
```bash
sudo certbot --nginx -d marabet.ao -d www.marabet.ao
```

---

## 📊 DIFERENÇAS: ANTES vs AGORA

| Aspecto | ANTES (AWS) | AGORA (Angoweb) |
|--------|-------------|-----------------|
| **Banco de Dados** | RDS AWS remoto | PostgreSQL local |
| **Cache** | ElastiCache AWS remoto | Redis local |
| **Hospedagem** | AWS (Irlanda) | Angoweb (Luanda) |
| **Domínio** | .com | .ao |
| **Suporte** | AWS Support | Local Angola |
| **Custo** | ~$326/mês | ~150.000 AOA/mês |
| **Latência** | Média | Mínima (Angola) |
| **Pagamento** | USD | Kwanzas (AOA) |

---

## 🔒 SEGURANÇA IMPLEMENTADA

### **PostgreSQL:**
- ✅ Escuta apenas em localhost (não exposto à internet)
- ✅ Firewall bloqueia porta 5432 externamente
- ✅ Senha forte gerada automaticamente
- ✅ Permissões limitadas por usuário
- ✅ Limite de conexões (20)

### **Credenciais:**
- ✅ Salvas em `/opt/marabet/.env.db`
- ✅ Permissões 600 (apenas proprietário lê)
- ✅ Usuário `marabeta_marabet` criado

---

## 📁 ARQUIVOS CRIADOS/ATUALIZADOS

### **Criados:**
1. ✅ `ANGOWEB_DEPLOYMENT_GUIDE.md` - Guia completo
2. ✅ `install_postgresql_secure.sh` - Script de instalação
3. ✅ `COMANDOS_SERVIDOR.txt` - Comandos para o servidor
4. ✅ `RESUMO_MIGRACAO_ANGOWEB.md` - Este arquivo

### **Atualizados:**
1. ✅ `README.md` - Removidas referências AWS
2. ✅ `config_production.env` - Configurações locais
3. ✅ `docker-compose.production.yml` - Comentários Angoweb
4. ✅ `DOCKER_COMPOSE_GUIA.md` - Ambiente Angoweb

---

## 🎯 PRÓXIMOS PASSOS

### **Imediato:**
1. Conectar ao servidor: `ssh marabet@95.216.143.185`
2. Executar script de instalação PostgreSQL
3. Enviar código da aplicação
4. Configurar aplicação
5. Iniciar containers Docker
6. Configurar SSL/HTTPS

### **Médio Prazo:**
1. Configurar DNS (marabet.ao)
2. Configurar backup automático
3. Configurar monitoramento
4. Testar aplicação completa

### **Longo Prazo:**
1. Otimizar performance
2. Configurar CDN (se necessário)
3. Escalar conforme necessidade

---

## 📞 SUPORTE

### **Angoweb:**
- 📞 Telefone: +244 222 638 200
- 📧 Email: suporte@angoweb.com
- 🌐 Website: https://angoweb.com

### **MaraBet AI:**
- 📞 Telefone: +224 932027393
- 📧 Email: suporte@marabet.ao
- 🌐 Website: https://marabet.ao

---

## ✅ CHECKLIST FINAL

### **Pré-Deploy:**
- [x] README atualizado (sem AWS)
- [x] Configurações locais criadas
- [x] Script de instalação criado
- [x] Guia completo documentado
- [x] Comandos para servidor preparados

### **Deploy:**
- [ ] Conectar ao servidor
- [ ] Instalar PostgreSQL 15
- [ ] Enviar código da aplicação
- [ ] Configurar variáveis de ambiente
- [ ] Executar migrações
- [ ] Iniciar containers Docker
- [ ] Configurar SSL/HTTPS
- [ ] Configurar DNS

### **Pós-Deploy:**
- [ ] Testar aplicação
- [ ] Configurar backup
- [ ] Configurar monitoramento
- [ ] Documentar incidentes conhecidos

---

**🎉 Migração para Angoweb Concluída!**

Sistema configurado para hospedagem local em Angola com:
- 🇦🇴 Infraestrutura local (PostgreSQL + Redis)
- 🌐 Domínio .ao (marabet.ao)
- 🔒 Segurança implementada
- 💰 Pagamento em Kwanzas
- 📞 Suporte local

