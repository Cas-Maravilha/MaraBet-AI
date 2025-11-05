-- Seeds - Dados de Exemplo para Desenvolvimento
-- MaraBet AI

-- ============================================================================
-- USUÁRIOS DE TESTE
-- ============================================================================

-- Senha para todos: marabet123 (hash bcrypt)
INSERT INTO users (username, email, password_hash, full_name, phone, country, is_verified, is_premium) VALUES
('admin', 'admin@marabet.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILOvsOHXm', 'Administrador', '+224932027393', 'GN', TRUE, TRUE),
('teste', 'teste@marabet.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILOvsOHXm', 'Usuário Teste', '+244900000000', 'AO', TRUE, FALSE),
('demo', 'demo@marabet.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILOvsOHXm', 'Demo User', '+244900000001', 'AO', TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- BANKROLL INICIAL
-- ============================================================================

INSERT INTO bankroll (user_id, total_balance, available_balance, total_profit, roi, win_rate, total_bets, winning_bets)
SELECT id, 10000.00, 10000.00, 2500.00, 25.00, 65.00, 100, 65
FROM users WHERE username = 'admin'
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO bankroll (user_id, total_balance, available_balance, total_profit, roi, win_rate, total_bets, winning_bets)
SELECT id, 5000.00, 5000.00, 0.00, 0.00, 0.00, 0, 0
FROM users WHERE username = 'teste'
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO bankroll (user_id, total_balance, available_balance, total_profit, roi, win_rate, total_bets, winning_bets)
SELECT id, 1000.00, 1000.00, 150.00, 15.00, 60.00, 20, 12
FROM users WHERE username = 'demo'
ON CONFLICT (user_id) DO NOTHING;

-- ============================================================================
-- PREVISÕES DE EXEMPLO
-- ============================================================================

INSERT INTO predictions (match_id, user_id, league, home_team, away_team, match_date, prediction_type, predicted_result, confidence_score, probability, odds, risk_level, is_correct)
SELECT 
    12345,
    u.id,
    'Primeira Liga Angola',
    'Petro de Luanda',
    '1º de Agosto',
    CURRENT_TIMESTAMP + INTERVAL '2 days',
    'Resultado Final',
    'Casa',
    85.50,
    72.30,
    1.95,
    'baixo',
    NULL
FROM users u WHERE u.username = 'admin'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- ESTATÍSTICAS DE TIMES
-- ============================================================================

INSERT INTO teams_stats (team_name, league, season, matches_played, wins, draws, losses, goals_scored, goals_conceded, form) VALUES
('Petro de Luanda', 'Primeira Liga Angola', '2024/2025', 15, 12, 2, 1, 35, 8, 'WWWDW'),
('1º de Agosto', 'Primeira Liga Angola', '2024/2025', 15, 10, 3, 2, 28, 12, 'WDWWL'),
('Sagrada Esperança', 'Primeira Liga Angola', '2024/2025', 15, 9, 4, 2, 26, 15, 'DWWWD'),
('Interclube', 'Primeira Liga Angola', '2024/2025', 15, 8, 3, 4, 22, 16, 'LWWDW')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- FIM DOS SEEDS
-- ============================================================================
