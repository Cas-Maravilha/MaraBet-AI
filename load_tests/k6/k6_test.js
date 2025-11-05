// Testes de Carga com K6 - MaraBet AI
// Testa performance do sistema de previsões

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Métricas customizadas
const errorRate = new Rate('errors');

// Configuração de testes
export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Warm-up: 20 usuários
    { duration: '1m', target: 50 },    // Ramp-up: 50 usuários
    { duration: '3m', target: 100 },   // Load: 100 usuários
    { duration: '2m', target: 200 },   // Peak: 200 usuários
    { duration: '1m', target: 50 },    // Ramp-down: 50 usuários
    { duration: '30s', target: 0 },    // Cool-down: 0 usuários
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% das requisições < 500ms
    errors: ['rate<0.1'],              // Taxa de erro < 10%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export function setup() {
  // Fazer login e obter token
  const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    username: 'teste',
    password: 'marabet123',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  return { token: loginRes.json('token') };
}

export default function (data) {
  const params = {
    headers: {
      'Authorization': `Bearer ${data.token}`,
      'Content-Type': 'application/json',
    },
  };

  // Teste 1: Página inicial
  let res = http.get(`${BASE_URL}/`, params);
  check(res, {
    'home status 200': (r) => r.status === 200,
    'home response time < 500ms': (r) => r.timings.duration < 500,
  }) || errorRate.add(1);

  sleep(1);

  // Teste 2: Previsões de hoje
  res = http.get(`${BASE_URL}/api/predictions/today`, params);
  check(res, {
    'predictions status 200': (r) => r.status === 200,
    'predictions has data': (r) => r.json('predictions') !== undefined,
  }) || errorRate.add(1);

  sleep(2);

  // Teste 3: Previsões ao vivo
  res = http.get(`${BASE_URL}/api/predictions/live`, params);
  check(res, {
    'live predictions status 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // Teste 4: Estatísticas
  res = http.get(`${BASE_URL}/api/statistics`, params);
  check(res, {
    'statistics status 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // Teste 5: Bankroll
  res = http.get(`${BASE_URL}/api/bankroll`, params);
  check(res, {
    'bankroll status 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(2);
}

export function teardown(data) {
  // Cleanup se necessário
  console.log('Teste finalizado');
}

// Executar: k6 run load_tests/k6/k6_test.js
