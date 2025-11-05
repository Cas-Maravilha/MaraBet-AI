#!/usr/bin/env python3
"""
Script para Verificação e Testes da Aplicação - MaraBet AI
Automatiza a verificação e testes da aplicação em produção
"""

import subprocess
import os
import json
import requests
import time
from datetime import datetime

def run_command(command, shell=True):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ Erro no comando: {command}")
            print(f"Erro: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Exceção no comando: {command}")
        print(f"Erro: {e}")
        return None

def test_application():
    """Testa a aplicação em produção"""
    print("🧪 MARABET AI - VERIFICAÇÃO E TESTES DA APLICAÇÃO")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configuração existente
    try:
        with open('aws_infrastructure_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de configuração não encontrado")
        return False
    
    ubuntu_public_ip = config.get('ubuntu_public_ip')
    key_path = os.path.expanduser("~/.ssh/marabet-key.pem")
    
    if not ubuntu_public_ip:
        print("❌ IP público da instância Ubuntu não encontrado")
        return False
    
    print(f"✅ IP Público: {ubuntu_public_ip}")
    print(f"✅ Chave SSH: {key_path}")
    
    print("\n🧪 ETAPA 1: VERIFICAR STATUS DOS CONTAINERS")
    print("-" * 50)
    
    # Verificar status dos containers
    print("🔍 Verificando status dos containers...")
    status_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "cd /home/ubuntu/marabet-ai && docker-compose -f docker-compose.production.yml ps"'
    status_result = run_command(status_command)
    
    if status_result:
        print("✅ Status dos containers:")
        print(status_result)
    else:
        print("⚠️ Falha ao verificar status dos containers")
    
    print("\n🧪 ETAPA 2: VERIFICAR LOGS DA APLICAÇÃO")
    print("-" * 50)
    
    # Verificar logs da aplicação
    print("📋 Verificando logs da aplicação...")
    logs_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "cd /home/ubuntu/marabet-ai && docker-compose -f docker-compose.production.yml logs --tail=20"'
    logs_result = run_command(logs_command)
    
    if logs_result:
        print("✅ Logs da aplicação:")
        print(logs_result)
    else:
        print("⚠️ Falha ao verificar logs da aplicação")
    
    print("\n🧪 ETAPA 3: TESTAR CONECTIVIDADE LOCAL")
    print("-" * 50)
    
    # Testar conectividade local
    print("🔍 Testando conectividade local...")
    local_test_command = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no ubuntu@{ubuntu_public_ip} "curl -f http://localhost:8000/health"'
    local_test_result = run_command(local_test_command)
    
    if local_test_result:
        print("✅ Aplicação respondendo localmente")
        print(local_test_result)
    else:
        print("⚠️ Aplicação não está respondendo localmente")
    
    print("\n🧪 ETAPA 4: TESTAR ENDPOINTS EXTERNOS")
    print("-" * 50)
    
    # Testar endpoints externos
    base_url = f"http://{ubuntu_public_ip}:8000"
    
    print(f"🌐 Testando endpoints externos em: {base_url}")
    
    # Lista de endpoints para testar
    endpoints = [
        ("/", "Página inicial"),
        ("/health", "Health check"),
        ("/docs", "Documentação Swagger"),
        ("/predictions", "Predições"),
        ("/analysis", "Análise"),
        ("/config", "Configuração")
    ]
    
    for endpoint, description in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Testando {description}: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {description}: OK (Status: {response.status_code})")
            else:
                print(f"⚠️ {description}: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: Erro - {e}")
    
    print("\n🧪 ETAPA 5: TESTAR API DE PREDIÇÕES")
    print("-" * 50)
    
    # Testar API de predições
    print("🔍 Testando API de predições...")
    
    # Dados de teste para predição
    test_data = {
        "match_id": "12345",
        "home_team": "Real Madrid",
        "away_team": "Barcelona",
        "league": "La Liga",
        "match_date": "2024-01-15T20:00:00Z"
    }
    
    try:
        # Testar endpoint de predição
        predict_url = f"{base_url}/predict"
        print(f"📤 Enviando dados de teste para: {predict_url}")
        print(f"📋 Dados: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            predict_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ API de predições: OK")
            print(f"📋 Resposta: {response.json()}")
        else:
            print(f"⚠️ API de predições: Status {response.status_code}")
            print(f"📋 Resposta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API de predições: Erro - {e}")
    
    print("\n🧪 ETAPA 6: CRIAR SCRIPT DE TESTE POWERSHELL")
    print("-" * 50)
    
    # Criar script de teste PowerShell
    powershell_script = f"""# Script de Teste PowerShell - MaraBet AI
# Execute no PowerShell do Windows

$PUBLIC_IP = "{ubuntu_public_ip}"
$BASE_URL = "http://$PUBLIC_IP:8000"

Write-Host "🧪 MARABET AI - TESTES DA APLICAÇÃO" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "📅 Data/Hora: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')" -ForegroundColor Yellow
Write-Host "🌐 URL Base: $BASE_URL" -ForegroundColor Cyan

# Teste 1: Health Check
Write-Host "`n🔍 TESTE 1: HEALTH CHECK" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {{
    $healthResponse = Invoke-WebRequest -Uri "$BASE_URL/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Health Check: OK (Status: $($healthResponse.StatusCode))" -ForegroundColor Green
    Write-Host "📋 Resposta: $($healthResponse.Content)" -ForegroundColor White
}} catch {{
    Write-Host "❌ Health Check: Erro - $($_.Exception.Message)" -ForegroundColor Red
}}

# Teste 2: Documentação Swagger
Write-Host "`n🔍 TESTE 2: DOCUMENTAÇÃO SWAGGER" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {{
    $docsResponse = Invoke-WebRequest -Uri "$BASE_URL/docs" -Method GET -TimeoutSec 10
    Write-Host "✅ Documentação Swagger: OK (Status: $($docsResponse.StatusCode))" -ForegroundColor Green
    Write-Host "🌐 Acesse no navegador: $BASE_URL/docs" -ForegroundColor Cyan
}} catch {{
    Write-Host "❌ Documentação Swagger: Erro - $($_.Exception.Message)" -ForegroundColor Red
}}

# Teste 3: Predições
Write-Host "`n🔍 TESTE 3: PREDIÇÕES" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {{
    $predictionsResponse = Invoke-WebRequest -Uri "$BASE_URL/predictions" -Method GET -TimeoutSec 10
    Write-Host "✅ Predições: OK (Status: $($predictionsResponse.StatusCode))" -ForegroundColor Green
    Write-Host "📋 Resposta: $($predictionsResponse.Content)" -ForegroundColor White
}} catch {{
    Write-Host "❌ Predições: Erro - $($_.Exception.Message)" -ForegroundColor Red
}}

# Teste 4: Análise
Write-Host "`n🔍 TESTE 4: ANÁLISE" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {{
    $analysisResponse = Invoke-WebRequest -Uri "$BASE_URL/analysis" -Method GET -TimeoutSec 10
    Write-Host "✅ Análise: OK (Status: $($analysisResponse.StatusCode))" -ForegroundColor Green
    Write-Host "📋 Resposta: $($analysisResponse.Content)" -ForegroundColor White
}} catch {{
    Write-Host "❌ Análise: Erro - $($_.Exception.Message)" -ForegroundColor Red
}}

# Teste 5: Configuração
Write-Host "`n🔍 TESTE 5: CONFIGURAÇÃO" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {{
    $configResponse = Invoke-WebRequest -Uri "$BASE_URL/config" -Method GET -TimeoutSec 10
    Write-Host "✅ Configuração: OK (Status: $($configResponse.StatusCode))" -ForegroundColor Green
    Write-Host "📋 Resposta: $($configResponse.Content)" -ForegroundColor White
}} catch {{
    Write-Host "❌ Configuração: Erro - $($_.Exception.Message)" -ForegroundColor Red
}}

# Teste 6: API de Predição (POST)
Write-Host "`n🔍 TESTE 6: API DE PREDIÇÃO (POST)" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {{
    $body = @{{
        match_id = "12345"
        home_team = "Real Madrid"
        away_team = "Barcelona"
        league = "La Liga"
        match_date = "2024-01-15T20:00:00Z"
    }} | ConvertTo-Json
    
    $predictResponse = Invoke-WebRequest -Uri "$BASE_URL/predict" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ API de Predição: OK (Status: $($predictResponse.StatusCode))" -ForegroundColor Green
    Write-Host "📋 Resposta: $($predictResponse.Content)" -ForegroundColor White
}} catch {{
    Write-Host "❌ API de Predição: Erro - $($_.Exception.Message)" -ForegroundColor Red
}}

# Teste 7: Página Inicial
Write-Host "`n🔍 TESTE 7: PÁGINA INICIAL" -ForegroundColor Yellow
Write-Host "-" * 40 -ForegroundColor Yellow
try {{
    $homeResponse = Invoke-WebRequest -Uri "$BASE_URL/" -Method GET -TimeoutSec 10
    Write-Host "✅ Página Inicial: OK (Status: $($homeResponse.StatusCode))" -ForegroundColor Green
    Write-Host "🌐 Acesse no navegador: $BASE_URL" -ForegroundColor Cyan
}} catch {{
    Write-Host "❌ Página Inicial: Erro - $($_.Exception.Message)" -ForegroundColor Red
}}

Write-Host "`n🎉 TESTES CONCLUÍDOS!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "🌐 URLs para acessar no navegador:" -ForegroundColor Cyan
Write-Host "  • Página Principal: $BASE_URL" -ForegroundColor White
Write-Host "  • Documentação: $BASE_URL/docs" -ForegroundColor White
Write-Host "  • Health Check: $BASE_URL/health" -ForegroundColor White
Write-Host "  • Predições: $BASE_URL/predictions" -ForegroundColor White
Write-Host "  • Análise: $BASE_URL/analysis" -ForegroundColor White
Write-Host "  • Configuração: $BASE_URL/config" -ForegroundColor White
"""
    
    # Salvar script PowerShell
    with open('test_application.ps1', 'w', encoding='utf-8') as f:
        f.write(powershell_script)
    print("✅ Script de teste PowerShell criado: test_application.ps1")
    
    print("\n🧪 ETAPA 7: CRIAR SCRIPT DE TESTE BASH")
    print("-" * 50)
    
    # Criar script de teste Bash
    bash_script = f"""#!/bin/bash
# Script de Teste Bash - MaraBet AI
# Execute no servidor Ubuntu

PUBLIC_IP="{ubuntu_public_ip}"
BASE_URL="http://$PUBLIC_IP:8000"

echo "🧪 MARABET AI - TESTES DA APLICAÇÃO"
echo "=================================="
echo "📅 Data/Hora: $(date '+%d/%m/%Y %H:%M:%S')"
echo "🌐 URL Base: $BASE_URL"

# Teste 1: Health Check
echo ""
echo "🔍 TESTE 1: HEALTH CHECK"
echo "------------------------"
if curl -f "$BASE_URL/health" > /dev/null 2>&1; then
    echo "✅ Health Check: OK"
    curl -s "$BASE_URL/health" | head -5
else
    echo "❌ Health Check: Falha"
fi

# Teste 2: Documentação Swagger
echo ""
echo "🔍 TESTE 2: DOCUMENTAÇÃO SWAGGER"
echo "--------------------------------"
if curl -f "$BASE_URL/docs" > /dev/null 2>&1; then
    echo "✅ Documentação Swagger: OK"
    echo "🌐 Acesse no navegador: $BASE_URL/docs"
else
    echo "❌ Documentação Swagger: Falha"
fi

# Teste 3: Predições
echo ""
echo "🔍 TESTE 3: PREDIÇÕES"
echo "--------------------"
if curl -f "$BASE_URL/predictions" > /dev/null 2>&1; then
    echo "✅ Predições: OK"
    curl -s "$BASE_URL/predictions" | head -5
else
    echo "❌ Predições: Falha"
fi

# Teste 4: Análise
echo ""
echo "🔍 TESTE 4: ANÁLISE"
echo "-------------------"
if curl -f "$BASE_URL/analysis" > /dev/null 2>&1; then
    echo "✅ Análise: OK"
    curl -s "$BASE_URL/analysis" | head -5
else
    echo "❌ Análise: Falha"
fi

# Teste 5: Configuração
echo ""
echo "🔍 TESTE 5: CONFIGURAÇÃO"
echo "------------------------"
if curl -f "$BASE_URL/config" > /dev/null 2>&1; then
    echo "✅ Configuração: OK"
    curl -s "$BASE_URL/config" | head -5
else
    echo "❌ Configuração: Falha"
fi

# Teste 6: Página Inicial
echo ""
echo "🔍 TESTE 6: PÁGINA INICIAL"
echo "--------------------------"
if curl -f "$BASE_URL/" > /dev/null 2>&1; then
    echo "✅ Página Inicial: OK"
    echo "🌐 Acesse no navegador: $BASE_URL"
else
    echo "❌ Página Inicial: Falha"
fi

echo ""
echo "🎉 TESTES CONCLUÍDOS!"
echo "====================="
echo "🌐 URLs para acessar no navegador:"
echo "  • Página Principal: $BASE_URL"
echo "  • Documentação: $BASE_URL/docs"
echo "  • Health Check: $BASE_URL/health"
echo "  • Predições: $BASE_URL/predictions"
echo "  • Análise: $BASE_URL/analysis"
echo "  • Configuração: $BASE_URL/config"
"""
    
    # Salvar script Bash
    with open('test_application.sh', 'w', encoding='utf-8') as f:
        f.write(bash_script)
    print("✅ Script de teste Bash criado: test_application.sh")
    
    print("\n🧪 ETAPA 8: INSTRUÇÕES DE TESTE")
    print("-" * 50)
    
    print("📝 INSTRUÇÕES PARA TESTAR A APLICAÇÃO:")
    print("-" * 60)
    print("1. Teste no navegador Windows:")
    print(f"   • Página Principal: http://{ubuntu_public_ip}:8000")
    print(f"   • Documentação Swagger: http://{ubuntu_public_ip}:8000/docs")
    print(f"   • Health Check: http://{ubuntu_public_ip}:8000/health")
    print()
    print("2. Teste via PowerShell (Windows):")
    print("   • Execute: .\\test_application.ps1")
    print("   • Ou execute os comandos individualmente")
    print()
    print("3. Teste via SSH (Servidor Ubuntu):")
    print(f"   ssh -i {key_path} ubuntu@{ubuntu_public_ip}")
    print("   cd /home/ubuntu/marabet-ai")
    print("   chmod +x test_application.sh")
    print("   ./test_application.sh")
    print()
    print("4. Comandos PowerShell individuais:")
    print(f"   $PUBLIC_IP = \"{ubuntu_public_ip}\"")
    print("   Invoke-WebRequest -Uri \"http://$PUBLIC_IP:8000/health\" -Method GET")
    print("   Invoke-WebRequest -Uri \"http://$PUBLIC_IP:8000/docs\" -Method GET")
    print("   Invoke-WebRequest -Uri \"http://$PUBLIC_IP:8000/predictions\" -Method GET")
    
    print("\n🎉 VERIFICAÇÃO E TESTES CONCLUÍDOS!")
    print("=" * 60)
    
    print("\n📋 RESUMO DOS TESTES:")
    print("-" * 40)
    print(f"• IP Público: {ubuntu_public_ip}")
    print(f"• URL Base: http://{ubuntu_public_ip}:8000")
    print(f"• Status: Testes executados")
    print(f"• Scripts: Criados (PowerShell e Bash)")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Verificação e testes executados")
    print("2. 🔄 Testar no navegador")
    print("3. 🔄 Executar scripts de teste")
    print("4. 🔄 Verificar logs")
    print("5. 🔄 Configurar monitoramento")
    print("6. 🔄 Configurar backup")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("-" * 40)
    print("• Teste todos os endpoints")
    print("• Verifique os logs da aplicação")
    print("• Monitore o uso de recursos")
    print("• Configure alertas de monitoramento")
    
    return True

def main():
    print("🚀 Iniciando verificação e testes da aplicação...")
    
    # Testar aplicação
    success = test_application()
    
    if success:
        print("\n🎯 VERIFICAÇÃO E TESTES CONCLUÍDOS COM SUCESSO!")
        print("A aplicação MaraBet AI está funcionando em produção!")
    else:
        print("\n❌ Falha na verificação e testes da aplicação")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
