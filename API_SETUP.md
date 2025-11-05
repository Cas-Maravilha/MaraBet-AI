# 🔑 Configuração de API Keys - MaraBet AI

## 📋 APIs Necessárias

### 1. API-Football (Dados Esportivos)
- **Gratuita**: 100 requests/dia
- **Site**: https://www.api-football.com/
- **Registro**: Gratuito
- **Dados**: Estatísticas, resultados, jogadores, times

### 2. The Odds API (Odds de Apostas)
- **Gratuita**: 500 requests/mês
- **Site**: https://the-odds-api.com/
- **Registro**: Gratuito
- **Dados**: Odds de apostas em tempo real

## 🚀 Como Configurar

### Passo 1: Obter API Keys

#### API-Football:
1. Acesse https://www.api-football.com/
2. Clique em "Sign Up" para criar conta gratuita
3. Confirme seu email
4. Faça login e vá em "My Dashboard"
5. Clique em "My Access"
6. Copie sua API Key

#### The Odds API:
1. Acesse https://the-odds-api.com/
2. Clique em "Get Free API Key"
3. Preencha o formulário de registro
4. Confirme seu email
5. Faça login no dashboard
6. Copie sua API Key

### Passo 2: Configurar no Projeto

1. **Edite o arquivo `.env`** na raiz do projeto:
```bash
# API Keys
API_FOOTBALL_KEY=sua_chave_api_football_aqui
THE_ODDS_API_KEY=sua_chave_the_odds_api_aqui

# Outras configurações
REDIS_URL=redis://localhost:6379
SECRET_KEY=sua_chave_secreta_aqui
```

2. **Teste a configuração**:
```bash
python test_api_keys.py
```

### Passo 3: Verificar Funcionamento

Execute o sistema para verificar se as APIs estão funcionando:

```bash
# Demonstração rápida
python demo.py

# Sistema completo
python main.py --mode full --league all --days 7 --capital 1000
```

## 🔧 Configurações Avançadas

### Limites de Rate
- **API-Football**: 100 requests/dia (gratuito)
- **The Odds API**: 500 requests/mês (gratuito)

### Ligas Monitoradas
O sistema está configurado para monitorar:
- Premier League (39)
- La Liga (140)
- Bundesliga (78)
- Serie A (135)
- Ligue 1 (61)
- Brasileirão Série A (71)

### Configurações de Análise
- Confiança mínima: 70%
- Confiança máxima: 90%
- EV mínimo: 5%

## 🚨 Solução de Problemas

### Erro: "API_FOOTBALL_KEY não configurada"
- Verifique se o arquivo `.env` existe
- Confirme se a chave está correta
- Execute `python test_api_keys.py`

### Erro: "Rate limit exceeded"
- Aguarde 24h para API-Football
- Aguarde 1 mês para The Odds API
- Considere upgrade para planos pagos

### Erro: "Invalid API Key"
- Verifique se copiou a chave corretamente
- Confirme se a conta está ativa
- Teste a chave no site da API

## 📞 Suporte

Para dúvidas sobre configuração:
- Consulte a documentação das APIs
- Verifique os logs em `mara_bet.log`
- Execute `python test_api_keys.py` para diagnóstico
