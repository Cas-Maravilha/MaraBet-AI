# 🚨 PLANO DE DISASTER RECOVERY - MARABET AI

## 📋 **VISÃO GERAL**

Este documento define o plano de disaster recovery para o sistema MaraBet AI, incluindo procedimentos para recuperação de desastres, RTO (Recovery Time Objective) e RPO (Recovery Point Objective).

## 🎯 **OBJETIVOS DE RECUPERAÇÃO**

### **RTO (Recovery Time Objective)**
- **Crítico**: 4 horas
- **Importante**: 8 horas  
- **Normal**: 24 horas

### **RPO (Recovery Point Objective)**
- **Dados de Apostas**: 15 minutos
- **Métricas de Negócio**: 1 hora
- **Logs do Sistema**: 4 horas
- **Configurações**: 24 horas

## 🏗️ **ARQUITETURA DE RECUPERAÇÃO**

### **1. TIER 1 - DADOS CRÍTICOS**
- **Banco de Dados Principal**: SQLite/PostgreSQL
- **Backup Frequência**: A cada 15 minutos
- **Replicação**: Master-Slave
- **Localização**: Data center principal + backup

### **2. TIER 2 - DADOS IMPORTANTES**
- **Modelos de ML**: Modelos treinados
- **Configurações**: Settings e parâmetros
- **Backup Frequência**: Diário
- **Replicação**: Backup local + remoto

### **3. TIER 3 - DADOS DE SUPORTE**
- **Logs do Sistema**: Logs de aplicação
- **Métricas**: Dados de monitoramento
- **Backup Frequência**: Semanal
- **Replicação**: Backup remoto

## 🔄 **CENÁRIOS DE DESASTRE**

### **CENÁRIO 1: FALHA DO BANCO DE DADOS**
**Probabilidade**: Alta
**Impacto**: Crítico

#### **Procedimentos:**
1. **Detecção** (0-5 min)
   - Monitoramento automático detecta falha
   - Alerta enviado para equipe de suporte

2. **Avaliação** (5-15 min)
   - Verificar status do banco
   - Identificar causa da falha
   - Determinar se é recuperável

3. **Recuperação** (15-60 min)
   - Ativar banco de dados secundário
   - Restaurar dados do backup mais recente
   - Verificar integridade dos dados

4. **Validação** (60-90 min)
   - Testar funcionalidades críticas
   - Verificar consistência dos dados
   - Monitorar performance

#### **RTO**: 1 hora
#### **RPO**: 15 minutos

### **CENÁRIO 2: FALHA DO SERVIDOR PRINCIPAL**
**Probabilidade**: Média
**Impacto**: Crítico

#### **Procedimentos:**
1. **Detecção** (0-5 min)
   - Health checks falham
   - Alerta automático disparado

2. **Failover** (5-15 min)
   - Ativar servidor secundário
   - Redirecionar tráfego
   - Verificar conectividade

3. **Recuperação** (15-60 min)
   - Restaurar aplicação
   - Sincronizar dados
   - Configurar monitoramento

4. **Validação** (60-120 min)
   - Testes de funcionalidade
   - Verificar performance
   - Monitorar estabilidade

#### **RTO**: 2 horas
#### **RPO**: 1 hora

### **CENÁRIO 3: FALHA COMPLETA DO DATA CENTER**
**Probabilidade**: Baixa
**Impacto**: Crítico

#### **Procedimentos:**
1. **Ativação** (0-30 min)
   - Ativar data center secundário
   - Notificar equipe de emergência
   - Iniciar procedimentos de recuperação

2. **Restauração** (30-180 min)
   - Restaurar aplicação completa
   - Restaurar banco de dados
   - Configurar infraestrutura

3. **Sincronização** (180-240 min)
   - Sincronizar dados
   - Verificar integridade
   - Configurar monitoramento

4. **Validação** (240-300 min)
   - Testes completos
   - Verificar funcionalidades
   - Monitorar estabilidade

#### **RTO**: 4 horas
#### **RPO**: 4 horas

## 🛠️ **PROCEDIMENTOS DE RECUPERAÇÃO**

### **1. RECUPERAÇÃO DO BANCO DE DADOS**

#### **SQLite (Desenvolvimento)**
```bash
# 1. Parar aplicação
systemctl stop marabet-ai

# 2. Fazer backup do banco atual
cp mara_bet.db mara_bet.db.broken

# 3. Restaurar do backup
cp backups/latest/database_backup.db mara_bet.db

# 4. Verificar integridade
sqlite3 mara_bet.db "PRAGMA integrity_check;"

# 5. Reiniciar aplicação
systemctl start marabet-ai
```

#### **PostgreSQL (Produção)**
```bash
# 1. Parar aplicação
systemctl stop marabet-ai

# 2. Parar PostgreSQL
systemctl stop postgresql

# 3. Restaurar do backup
pg_restore -d marabet -v backups/latest/database_backup.dump

# 4. Verificar integridade
psql -d marabet -c "SELECT COUNT(*) FROM bets;"

# 5. Reiniciar serviços
systemctl start postgresql
systemctl start marabet-ai
```

### **2. RECUPERAÇÃO DA APLICAÇÃO**

```bash
# 1. Parar aplicação
systemctl stop marabet-ai

# 2. Fazer backup da versão atual
cp -r /opt/marabet /opt/marabet.broken

# 3. Restaurar do backup
tar -xzf backups/latest/application_backup.tar.gz -C /opt/

# 4. Restaurar dependências
cd /opt/marabet
pip install -r requirements.txt

# 5. Configurar permissões
chown -R marabet:marabet /opt/marabet
chmod +x /opt/marabet/*.py

# 6. Reiniciar aplicação
systemctl start marabet-ai
```

### **3. RECUPERAÇÃO DE CONFIGURAÇÕES**

```bash
# 1. Parar aplicação
systemctl stop marabet-ai

# 2. Restaurar configurações
cp backups/latest/config/.env /opt/marabet/
cp -r backups/latest/config/settings/ /opt/marabet/

# 3. Verificar configurações
python /opt/marabet/validate_production.py

# 4. Reiniciar aplicação
systemctl start marabet-ai
```

## 📊 **MONITORAMENTO E ALERTAS**

### **Alertas de Disaster Recovery**
- **Backup Falhou**: Alerta imediato
- **Backup Antigo**: Alerta se backup > 24h
- **Espaço em Disco**: Alerta se < 20%
- **Integridade**: Alerta se checksum inválido

### **Métricas de Recuperação**
- **Tempo de Detecção**: < 5 minutos
- **Tempo de Recuperação**: Conforme RTO
- **Taxa de Sucesso**: > 99%
- **Perda de Dados**: Conforme RPO

## 🧪 **TESTES DE DISASTER RECOVERY**

### **Testes Mensais**
1. **Teste de Backup**
   - Criar backup completo
   - Validar integridade
   - Verificar checksum

2. **Teste de Restauração**
   - Restaurar em ambiente de teste
   - Verificar funcionalidades
   - Validar dados

3. **Teste de Failover**
   - Simular falha do servidor
   - Ativar servidor secundário
   - Verificar funcionalidades

### **Testes Trimestrais**
1. **Teste Completo**
   - Simular falha completa
   - Executar procedimentos completos
   - Validar RTO e RPO

2. **Teste de Equipe**
   - Treinar equipe nos procedimentos
   - Simular cenários reais
   - Documentar lições aprendidas

## 📋 **CHECKLIST DE RECUPERAÇÃO**

### **Pré-Recuperação**
- [ ] Confirmar tipo de desastre
- [ ] Notificar equipe de suporte
- [ ] Verificar disponibilidade de backups
- [ ] Preparar ambiente de recuperação

### **Durante a Recuperação**
- [ ] Parar serviços afetados
- [ ] Fazer backup do estado atual
- [ ] Executar procedimentos de recuperação
- [ ] Verificar integridade dos dados
- [ ] Reiniciar serviços

### **Pós-Recuperação**
- [ ] Validar funcionalidades críticas
- [ ] Verificar performance
- [ ] Monitorar estabilidade
- [ ] Documentar incidente
- [ ] Atualizar procedimentos se necessário

## 📞 **CONTATOS DE EMERGÊNCIA**

### **Equipe Principal**
- **Líder Técnico**: +55 11 99999-0001
- **DBA**: +55 11 99999-0002
- **DevOps**: +55 11 99999-0003

### **Equipe Secundária**
- **Gerente de Projeto**: +55 11 99999-0004
- **Arquiteto**: +55 11 99999-0005

### **Provedores**
- **AWS Support**: support@aws.com
- **Data Center**: +55 11 3333-4444

## 📚 **DOCUMENTAÇÃO RELACIONADA**

- [Manual de Backup](backup_manual.md)
- [Procedimentos de Restauração](restore_procedures.md)
- [Configuração de Monitoramento](monitoring_setup.md)
- [Treinamento da Equipe](team_training.md)

## 🔄 **ATUALIZAÇÕES**

- **Versão**: 1.0
- **Última Atualização**: 2024-01-01
- **Próxima Revisão**: 2024-04-01
- **Responsável**: Equipe de DevOps

---

**⚠️ IMPORTANTE**: Este plano deve ser revisado e testado regularmente para garantir sua eficácia em situações reais de desastre.
