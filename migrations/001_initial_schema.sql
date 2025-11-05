-- Migração Inicial - MaraBet AI
-- Data: 2025-10-24
-- Versão: 001

-- ============================================================================
-- TABELAS DE USUÁRIOS E AUTENTICAÇÃO
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    country VARCHAR(2) DEFAULT 'AO',
    language VARCHAR(5) DEFAULT 'pt',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- ============================================================================
-- TABELAS DE PREVISÕES
-- ============================================================================

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL,
    user_id INTEGER REFERENCES users(id),
    league VARCHAR(100),
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    match_date TIMESTAMP NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    predicted_result VARCHAR(100),
    confidence_score DECIMAL(5,2),
    probability DECIMAL(5,2),
    odds DECIMAL(10,2),
    expected_value DECIMAL(10,2),
    risk_level VARCHAR(20),
    actual_result VARCHAR(100),
    is_correct BOOLEAN,
    profit_loss DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_match_id ON predictions(match_id);
CREATE INDEX idx_predictions_user_id ON predictions(user_id);
CREATE INDEX idx_predictions_match_date ON predictions(match_date);
CREATE INDEX idx_predictions_league ON predictions(league);

-- ============================================================================
-- TABELAS DE APOSTAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS bets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    prediction_id INTEGER REFERENCES predictions(id),
    bookmaker VARCHAR(50),
    bet_type VARCHAR(50) NOT NULL,
    stake DECIMAL(10,2) NOT NULL,
    odds DECIMAL(10,2) NOT NULL,
    potential_return DECIMAL(10,2),
    actual_return DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending',
    placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settled_at TIMESTAMP
);

CREATE INDEX idx_bets_user_id ON bets(user_id);
CREATE INDEX idx_bets_prediction_id ON bets(prediction_id);
CREATE INDEX idx_bets_status ON bets(status);

-- ============================================================================
-- TABELAS DE BANKROLL
-- ============================================================================

CREATE TABLE IF NOT EXISTS bankroll (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    total_balance DECIMAL(15,2) DEFAULT 0,
    available_balance DECIMAL(15,2) DEFAULT 0,
    locked_balance DECIMAL(15,2) DEFAULT 0,
    total_profit DECIMAL(15,2) DEFAULT 0,
    total_loss DECIMAL(15,2) DEFAULT 0,
    roi DECIMAL(5,2) DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0,
    total_bets INTEGER DEFAULT 0,
    winning_bets INTEGER DEFAULT 0,
    losing_bets INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bankroll_user_id ON bankroll(user_id);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    bet_id INTEGER REFERENCES bets(id),
    type VARCHAR(20) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    balance_before DECIMAL(15,2),
    balance_after DECIMAL(15,2),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_bet_id ON transactions(bet_id);
CREATE INDEX idx_transactions_type ON transactions(type);

-- ============================================================================
-- TABELAS DE ESTATÍSTICAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS teams_stats (
    id SERIAL PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    league VARCHAR(100),
    season VARCHAR(20),
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    goals_scored INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    clean_sheets INTEGER DEFAULT 0,
    avg_possession DECIMAL(5,2),
    avg_shots DECIMAL(5,2),
    form VARCHAR(20),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_teams_stats_team_name ON teams_stats(team_name);
CREATE INDEX idx_teams_stats_league ON teams_stats(league);

CREATE TABLE IF NOT EXISTS matches_history (
    id SERIAL PRIMARY KEY,
    match_id INTEGER UNIQUE NOT NULL,
    league VARCHAR(100),
    season VARCHAR(20),
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    match_date TIMESTAMP,
    home_score INTEGER,
    away_score INTEGER,
    home_odds DECIMAL(10,2),
    draw_odds DECIMAL(10,2),
    away_odds DECIMAL(10,2),
    result VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_matches_history_match_id ON matches_history(match_id);
CREATE INDEX idx_matches_history_home_team ON matches_history(home_team);
CREATE INDEX idx_matches_history_away_team ON matches_history(away_team);
CREATE INDEX idx_matches_history_match_date ON matches_history(match_date);

-- ============================================================================
-- TABELAS DE CONFIGURAÇÃO
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_config_key ON system_config(key);

CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    service VARCHAR(50) NOT NULL,
    key_name VARCHAR(100) NOT NULL,
    key_value TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER,
    requests_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_api_keys_service ON api_keys(service);

-- ============================================================================
-- TABELAS DE LOGS E AUDITORIA
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- ============================================================================
-- TRIGGERS PARA UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_predictions_updated_at BEFORE UPDATE ON predictions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bankroll_updated_at BEFORE UPDATE ON bankroll
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_stats_updated_at BEFORE UPDATE ON teams_stats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

CREATE OR REPLACE VIEW v_user_stats AS
SELECT 
    u.id,
    u.username,
    u.email,
    b.total_balance,
    b.total_profit,
    b.roi,
    b.win_rate,
    b.total_bets,
    b.winning_bets,
    b.losing_bets
FROM users u
LEFT JOIN bankroll b ON u.id = b.user_id;

CREATE OR REPLACE VIEW v_recent_predictions AS
SELECT 
    p.*,
    u.username,
    CASE 
        WHEN p.is_correct = TRUE THEN 'WIN'
        WHEN p.is_correct = FALSE THEN 'LOSS'
        ELSE 'PENDING'
    END as status
FROM predictions p
LEFT JOIN users u ON p.user_id = u.id
ORDER BY p.created_at DESC
LIMIT 100;

-- ============================================================================
-- DADOS INICIAIS
-- ============================================================================

-- Configurações do sistema
INSERT INTO system_config (key, value, description) VALUES
('app_version', '1.0.0', 'Versão do aplicativo'),
('min_stake', '10', 'Stake mínimo permitido'),
('max_stake', '10000', 'Stake máximo permitido'),
('default_currency', 'AOA', 'Moeda padrão (Kwanza Angolano)'),
('min_confidence', '70', 'Confiança mínima para previsões'),
('max_risk', 'medium', 'Nível de risco máximo padrão')
ON CONFLICT (key) DO NOTHING;

-- ============================================================================
-- SCHEMA VERSION
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_migrations (version, description) VALUES
('001', 'Migração inicial - estrutura completa do banco de dados')
ON CONFLICT (version) DO NOTHING;

-- ============================================================================
-- PERMISSÕES (Opcional - ajustar conforme necessário)
-- ============================================================================

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO marabetuser;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO marabetuser;

-- ============================================================================
-- FIM DA MIGRAÇÃO 001
-- ============================================================================
