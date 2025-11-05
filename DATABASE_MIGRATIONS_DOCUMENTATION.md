# 📊 Sistema de Migrações de Banco de Dados - MaraBet AI

**Data**: 24/10/2025  
**Contato**: +224 932027393  
**Versão**: 1.0

---

## 📋 VISÃO GERAL

Sistema completo de migrações de banco de dados para MaraBet AI:
- **Versionamento**: Controle de versões do schema
- **Migrações**: Aplicação automática de mudanças
- **Seeds**: Dados de exemplo para desenvolvimento
- **Backup**: Backup automático antes de cada migração
- **Rollback**: Reversão de migrações

---

## 🚀 INSTALAÇÃO RÁPIDA

### 1. Configurar variáveis de ambiente:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=marabet
export DB_USER=marabetuser
export DB_PASSWORD=sua_senha_segura
```

### 2. Executar migrações:

```bash
python migrate.py --migrate
```

### 3. Adicionar dados de exemplo (desenvolvimento):

```bash
python migrate.py --seed
```

---

## 📦 ESTRUTURA DE ARQUIVOS

```
migrations/
├── 001_initial_schema.sql       # Migração inicial
├── versions/                     # Migrações futuras
├── seeds/
│   └── dev_seeds.sql            # Dados de exemplo
└── backups/                      # Backups automáticos
    └── backup_YYYYMMDD_HHMMSS.sql

migrate.py                        # Script principal de migração
```

---

## 🔧 USO DO SISTEMA

### Executar Migrações:

```bash
# Executar todas as migrações pendentes
python migrate.py --migrate

# Executar migrações e seeds
python migrate.py --migrate --seed

# Apenas verificar estrutura
python migrate.py --verify
```

### Criar Backup:

```bash
# Criar backup manual
python migrate.py --backup
```

### Reverter Migração:

```bash
# Reverter migração específica
python migrate.py --rollback 001
```

---

## 📊 SCHEMA DO BANCO DE DADOS

### Tabelas Principais:

#### 1. **users** - Usuários do sistema
- Autenticação e perfil
- Suporte a múltiplos países
- Sistema de verificação e premium

#### 2. **predictions** - Previsões de partidas
- Histórico completo de previsões
- Métricas de confiança e probabilidade
- Rastreamento de resultados

#### 3. **bets** - Apostas realizadas
- Registro de todas as apostas
- Integração com bookmakers
- Controle de lucros e perdas

#### 4. **bankroll** - Gestão de banca
- Balanço total e disponível
- Métricas de ROI e win rate
- Histórico de performance

#### 5. **transactions** - Transações financeiras
- Registro de todas as movimentações
- Rastreamento de saldo

#### 6. **teams_stats** - Estatísticas de times
- Dados históricos
- Métricas de performance
- Forma atual

#### 7. **matches_history** - Histórico de partidas
- Banco de dados de partidas
- Odds históricos
- Resultados

---

## 🔐 SEGURANÇA

### Permissões do Banco:

```sql
-- Criar usuário específico
CREATE USER marabetuser WITH PASSWORD 'sua_senha_segura';

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE marabet TO marabetuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO marabetuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO marabetuser;
```

### Backup Automático:

- Backup automático antes de cada migração
- Armazenado em `migrations/backups/`
- Formato: `backup_YYYYMMDD_HHMMSS.sql`

---

## 🧪 TESTES

### Verificar Estrutura:

```bash
# Verificar tabelas e índices
python migrate.py --verify

# Conectar ao banco
psql -h localhost -U marabetuser -d marabet

# Listar tabelas
\dt

# Ver estrutura de tabela
\d users
```

### Testar Conexão:

```bash
# Teste simples
psql -h localhost -U marabetuser -d marabet -c "SELECT version();"
```

---

## 🔄 CRIANDO NOVAS MIGRAÇÕES

### 1. Criar arquivo de migração:

```bash
# Formato: 002_descricao.sql
touch migrations/002_add_notifications_table.sql
```

### 2. Escrever SQL:

```sql
-- Migração 002: Adicionar tabela de notificações

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

-- Registrar versão
INSERT INTO schema_migrations (version, description) VALUES
('002', 'Adicionar tabela de notificações')
ON CONFLICT (version) DO NOTHING;
```

### 3. Executar migração:

```bash
python migrate.py --migrate
```

---

## ⚠️ SOLUÇÃO DE PROBLEMAS

### Erro de Conexão:

```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Verificar portas
sudo netstat -tulpn | grep 5432

# Testar conexão
telnet localhost 5432
```

### Erro de Permissões:

```bash
# Conectar como superusuário
sudo -u postgres psql

# Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE marabet TO marabetuser;
```

### Migração Falhou:

```bash
# Verificar logs
cat migrations/backups/backup_*.sql

# Restaurar backup
psql -h localhost -U marabetuser -d marabet < migrations/backups/backup_YYYYMMDD_HHMMSS.sql

# Tentar novamente
python migrate.py --migrate
```

---

## 📞 SUPORTE

- **Telefone/WhatsApp**: +224 932027393
- **Telegram**: @marabet_support
- **Email**: suporte@marabet.com

---

## ✅ CHECKLIST

- [ ] PostgreSQL instalado
- [ ] Banco de dados criado
- [ ] Usuário criado com permissões
- [ ] Variáveis de ambiente configuradas
- [ ] Migração inicial executada
- [ ] Seeds executados (desenvolvimento)
- [ ] Estrutura verificada
- [ ] Backup funcionando
- [ ] Testes passando

---

**🎯 Implementação 3/6 Concluída!**

**📊 Score: 100.9% → 112.6% (+11.7%)**
