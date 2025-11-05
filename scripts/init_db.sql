-- Script de inicialização do banco de dados PostgreSQL
-- Executado automaticamente na primeira inicialização do container

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Criar schema principal
CREATE SCHEMA IF NOT EXISTS sports_betting;

-- Definir schema padrão
SET search_path TO sports_betting, public;

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'USER' CHECK (role IN ('ADMIN', 'MODERATOR', 'USER', 'VIEWER')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de ligas
CREATE TABLE IF NOT EXISTS leagues (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    type VARCHAR(20) DEFAULT 'league',
    logo VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de times
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    logo VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de jogos
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    league_id INTEGER REFERENCES leagues(id),
    home_team_id INTEGER REFERENCES teams(id),
    away_team_id INTEGER REFERENCES teams(id),
    match_date TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    home_score INTEGER,
    away_score INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de odds
CREATE TABLE IF NOT EXISTS odds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    match_id INTEGER REFERENCES matches(id),
    bookmaker VARCHAR(50) NOT NULL,
    market_type VARCHAR(50) NOT NULL,
    selection VARCHAR(100) NOT NULL,
    odds DECIMAL(10,3) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de estatísticas
CREATE TABLE IF NOT EXISTS statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    match_id INTEGER REFERENCES matches(id),
    team_id INTEGER REFERENCES teams(id),
    stat_type VARCHAR(50) NOT NULL,
    stat_value DECIMAL(10,3) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de previsões
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    match_id INTEGER REFERENCES matches(id),
    model_name VARCHAR(100) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    probability DECIMAL(5,4) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    expected_value DECIMAL(10,4),
    kelly_fraction DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de apostas
CREATE TABLE IF NOT EXISTS bets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    match_id INTEGER REFERENCES matches(id),
    prediction_id UUID REFERENCES predictions(id),
    bookmaker VARCHAR(50) NOT NULL,
    market_type VARCHAR(50) NOT NULL,
    selection VARCHAR(100) NOT NULL,
    odds DECIMAL(10,3) NOT NULL,
    stake DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    result VARCHAR(20),
    profit_loss DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de backtesting
CREATE TABLE IF NOT EXISTS backtesting_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_bets INTEGER NOT NULL,
    winning_bets INTEGER NOT NULL,
    win_rate DECIMAL(5,4) NOT NULL,
    total_profit DECIMAL(10,2) NOT NULL,
    roi DECIMAL(5,4) NOT NULL,
    sharpe_ratio DECIMAL(10,4),
    max_drawdown DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_league ON matches(league_id);
CREATE INDEX IF NOT EXISTS idx_odds_match ON odds(match_id);
CREATE INDEX IF NOT EXISTS idx_odds_bookmaker ON odds(bookmaker);
CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions(match_id);
CREATE INDEX IF NOT EXISTS idx_bets_user ON bets(user_id);
CREATE INDEX IF NOT EXISTS idx_bets_match ON bets(match_id);
CREATE INDEX IF NOT EXISTS idx_statistics_match ON statistics(match_id);
CREATE INDEX IF NOT EXISTS idx_statistics_team ON statistics(team_id);

-- Triggers para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_matches_updated_at BEFORE UPDATE ON matches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bets_updated_at BEFORE UPDATE ON bets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Inserir dados iniciais
INSERT INTO leagues (id, name, country, type) VALUES
(39, 'Premier League', 'England', 'league'),
(140, 'La Liga', 'Spain', 'league'),
(78, 'Bundesliga', 'Germany', 'league'),
(135, 'Serie A', 'Italy', 'league'),
(61, 'Ligue 1', 'France', 'league'),
(71, 'Brasileirão', 'Brazil', 'league')
ON CONFLICT (id) DO NOTHING;

-- Inserir usuário admin padrão
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@marabet.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KzKz2K', 'ADMIN')
ON CONFLICT (email) DO NOTHING;

-- Comentários nas tabelas
COMMENT ON TABLE users IS 'Usuários do sistema';
COMMENT ON TABLE leagues IS 'Ligas esportivas';
COMMENT ON TABLE teams IS 'Times esportivos';
COMMENT ON TABLE matches IS 'Jogos/partidas';
COMMENT ON TABLE odds IS 'Odds das casas de apostas';
COMMENT ON TABLE statistics IS 'Estatísticas dos times';
COMMENT ON TABLE predictions IS 'Previsões dos modelos ML';
COMMENT ON TABLE bets IS 'Apostas dos usuários';
COMMENT ON TABLE backtesting_results IS 'Resultados de backtesting';

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA sports_betting TO sports_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sports_betting TO sports_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sports_betting TO sports_user;