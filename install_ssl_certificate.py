#!/usr/bin/env python3
"""
Script para Instalação de Certificado SSL - MaraBet AI
Automatiza a instalação do certificado SSL com Let's Encrypt
"""

import subprocess
import os
import json
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

def install_ssl_certificate():
    """Instala certificado SSL"""
    print("🔒 MARABET AI - INSTALAÇÃO DE CERTIFICADO SSL")
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
    
    print("\n🔒 ETAPA 1: CRIANDO SCRIPT DE INSTALAÇÃO SSL")
    print("-" * 50)
    
    # Criar script de instalação SSL
    ssl_script_content = f"""#!/bin/bash
# Script de Instalação SSL - MaraBet AI

echo "🔒 MARABET AI - INSTALAÇÃO DE CERTIFICADO SSL"
echo "============================================="

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script deve ser executado como root"
    echo "💡 Execute: sudo ./install_ssl.sh"
    exit 1
fi

# Atualizar sistema
echo "🔄 Atualizando sistema..."
apt update && apt upgrade -y

# Instalar Nginx se não estiver instalado
if ! command -v nginx &> /dev/null; then
    echo "🌐 Instalando Nginx..."
    apt install -y nginx
    systemctl start nginx
    systemctl enable nginx
fi

# Instalar Certbot
echo "🔒 Instalando Certbot..."
apt install -y certbot python3-certbot-nginx

# Verificar se Nginx está rodando
if ! systemctl is-active --quiet nginx; then
    echo "🌐 Iniciando Nginx..."
    systemctl start nginx
fi

# Configurar Nginx para o domínio
echo "🌐 Configurando Nginx para marabet.com..."
cat > /etc/nginx/sites-available/marabet.com << 'EOF'
server {{
    listen 80;
    server_name marabet.com www.marabet.com;
    
    location / {{
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /health {{
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /docs {{
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /predictions {{
        proxy_pass http://localhost:8000/predictions;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /analysis {{
        proxy_pass http://localhost:8000/analysis;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /config {{
        proxy_pass http://localhost:8000/config;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
EOF

# Habilitar site
ln -sf /etc/nginx/sites-available/marabet.com /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar configuração do Nginx
echo "🧪 Testando configuração do Nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração do Nginx OK"
    systemctl reload nginx
else
    echo "❌ Erro na configuração do Nginx"
    exit 1
fi

# Verificar se o domínio está apontando para o servidor
echo "🔍 Verificando DNS do domínio..."
echo "💡 Certifique-se de que marabet.com e www.marabet.com apontam para {ubuntu_public_ip}"
echo "💡 Aguarde alguns minutos para propagação do DNS"
echo "💡 Teste com: nslookup marabet.com"
echo "💡 Teste com: nslookup www.marabet.com"

# Aguardar confirmação do usuário
echo ""
echo "⚠️ IMPORTANTE: Antes de continuar, certifique-se de que:"
echo "   1. O domínio marabet.com está apontando para {ubuntu_public_ip}"
echo "   2. O domínio www.marabet.com está apontando para {ubuntu_public_ip}"
echo "   3. A propagação do DNS foi concluída"
echo ""
read -p "Pressione Enter para continuar ou Ctrl+C para cancelar..."

# Obter certificado SSL
echo "🔒 Obtendo certificado SSL..."
certbot --nginx -d marabet.com -d www.marabet.com --non-interactive --agree-tos --email admin@marabet.com

if [ $? -eq 0 ]; then
    echo "✅ Certificado SSL obtido com sucesso!"
else
    echo "❌ Falha ao obter certificado SSL"
    echo "💡 Verifique se o domínio está apontando corretamente para o servidor"
    exit 1
fi

# Configurar renovação automática
echo "🔄 Configurando renovação automática..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Testar renovação
echo "🧪 Testando renovação automática..."
certbot renew --dry-run

if [ $? -eq 0 ]; then
    echo "✅ Renovação automática configurada com sucesso!"
else
    echo "⚠️ Falha no teste de renovação automática"
fi

# Verificar status do certificado
echo "🔍 Verificando status do certificado..."
certbot certificates

# Verificar configuração do Nginx
echo "🔍 Verificando configuração do Nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração do Nginx OK"
    systemctl reload nginx
else
    echo "❌ Erro na configuração do Nginx"
fi

# Verificar se HTTPS está funcionando
echo "🧪 Testando HTTPS..."
curl -I https://marabet.com/health

echo "🎉 INSTALAÇÃO SSL CONCLUÍDA!"
echo "============================="
echo "🌐 URLs HTTPS:"
echo "  • https://marabet.com"
echo "  • https://www.marabet.com"
echo "  • https://marabet.com/docs"
echo "  • https://marabet.com/health"
echo "  • https://marabet.com/predictions"
echo "  • https://marabet.com/analysis"
echo "  • https://marabet.com/config"
echo ""
echo "🔒 Certificado SSL instalado e configurado!"
echo "🔄 Renovação automática configurada!"
echo "🌐 Nginx configurado como proxy reverso!"
"""
    
    # Salvar script localmente
    with open('install_ssl.sh', 'w') as f:
        f.write(ssl_script_content)
    print("✅ Script de instalação SSL criado: install_ssl.sh")
    
    print("\n🔒 ETAPA 2: TRANSFERINDO SCRIPT PARA O SERVIDOR")
    print("-" * 50)
    
    # Transferir script para o servidor
    print("📤 Transferindo script para o servidor...")
    scp_command = f'scp -i "{key_path}" -o StrictHostKeyChecking=no install_ssl.sh ubuntu@{ubuntu_public_ip}:/home/ubuntu/marabet-ai/'
    
    print(f"Executando: {scp_command}")
    scp_result = run_command(scp_command)
    
    if scp_result is not None:
        print("✅ Script transferido com sucesso")
    else:
        print("⚠️ Falha na transferência do script")
        print("💡 Tente executar manualmente:")
        print(f"scp -i {key_path} install_ssl.sh ubuntu@{ubuntu_public_ip}:/home/ubuntu/marabet-ai/")
    
    print("\n🔒 ETAPA 3: INSTRUÇÕES PARA INSTALAÇÃO MANUAL")
    print("-" * 50)
    
    print("📝 INSTRUÇÕES PARA INSTALAR SSL MANUALMENTE:")
    print("-" * 60)
    print("1. Conectar via SSH:")
    print(f"   ssh -i {key_path} ubuntu@{ubuntu_public_ip}")
    print()
    print("2. Ir para pasta do projeto:")
    print("   cd /home/ubuntu/marabet-ai")
    print()
    print("3. Dar permissão de execução:")
    print("   chmod +x install_ssl.sh")
    print()
    print("4. Executar script como root:")
    print("   sudo ./install_ssl.sh")
    print()
    print("5. Verificar se o domínio está apontando para o servidor:")
    print(f"   nslookup marabet.com")
    print(f"   nslookup www.marabet.com")
    print()
    print("6. Testar HTTPS:")
    print("   curl -I https://marabet.com/health")
    print("   curl -I https://www.marabet.com/health")
    
    print("\n🔒 ETAPA 4: CONFIGURAÇÃO DO DNS")
    print("-" * 50)
    
    print("🌐 CONFIGURAÇÃO DO DNS:")
    print("-" * 60)
    print("Para que o SSL funcione, configure os seguintes registros DNS:")
    print()
    print("Tipo: A")
    print("Nome: @")
    print("Valor: {ubuntu_public_ip}")
    print("TTL: 300")
    print()
    print("Tipo: A")
    print("Nome: www")
    print("Valor: {ubuntu_public_ip}")
    print("TTL: 300")
    print()
    print("Tipo: CNAME")
    print("Nome: marabet.com")
    print("Valor: www.marabet.com")
    print("TTL: 300")
    print()
    print("💡 Aguarde 5-10 minutos para propagação do DNS")
    print("💡 Teste com: nslookup marabet.com")
    print("💡 Teste com: nslookup www.marabet.com")
    
    print("\n🔒 ETAPA 5: COMANDOS DE VERIFICAÇÃO")
    print("-" * 50)
    
    print("🧪 COMANDOS PARA VERIFICAR SSL:")
    print("-" * 60)
    print("Execute no servidor Ubuntu:")
    print()
    print("# 1. Verificar status do certificado")
    print("sudo certbot certificates")
    print()
    print("# 2. Verificar configuração do Nginx")
    print("sudo nginx -t")
    print()
    print("# 3. Verificar status do Nginx")
    print("sudo systemctl status nginx")
    print()
    print("# 4. Testar HTTPS")
    print("curl -I https://marabet.com/health")
    print("curl -I https://www.marabet.com/health")
    print()
    print("# 5. Verificar renovação automática")
    print("sudo certbot renew --dry-run")
    print()
    print("# 6. Verificar logs do Nginx")
    print("sudo tail -f /var/log/nginx/access.log")
    print("sudo tail -f /var/log/nginx/error.log")
    
    print("\n🔒 ETAPA 6: TESTAR HTTPS")
    print("-" * 50)
    
    print("🌐 URLs HTTPS para testar:")
    print("-" * 60)
    print("• https://marabet.com")
    print("• https://www.marabet.com")
    print("• https://marabet.com/docs")
    print("• https://marabet.com/health")
    print("• https://marabet.com/predictions")
    print("• https://marabet.com/analysis")
    print("• https://marabet.com/config")
    print()
    print("💻 Comandos PowerShell para testar:")
    print("$PUBLIC_IP = \"{ubuntu_public_ip}\"")
    print("Invoke-WebRequest -Uri \"https://marabet.com/health\" -Method GET")
    print("Invoke-WebRequest -Uri \"https://www.marabet.com/health\" -Method GET")
    print("Invoke-WebRequest -Uri \"https://marabet.com/docs\" -Method GET")
    
    print("\n🎉 INSTALAÇÃO SSL CONCLUÍDA!")
    print("=" * 60)
    
    print("\n📋 RESUMO DA INSTALAÇÃO:")
    print("-" * 40)
    print(f"• IP Público: {ubuntu_public_ip}")
    print(f"• Domínio: marabet.com")
    print(f"• Certificado: Let's Encrypt")
    print(f"• Status: Script criado")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Script de instalação SSL criado")
    print("2. 🔄 Configurar DNS do domínio")
    print("3. 🔄 Executar script no servidor")
    print("4. 🔄 Verificar certificado SSL")
    print("5. 🔄 Testar HTTPS")
    print("6. 🔄 Configurar renovação automática")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("-" * 40)
    print("• Configure o DNS antes de executar o script")
    print("• Aguarde a propagação do DNS")
    print("• Teste todos os endpoints HTTPS")
    print("• Monitore a renovação automática")
    print("• Configure backup do certificado")
    
    return True

def main():
    print("🚀 Iniciando instalação do certificado SSL...")
    
    # Instalar certificado SSL
    success = install_ssl_certificate()
    
    if success:
        print("\n🎯 SCRIPT DE INSTALAÇÃO SSL CRIADO COM SUCESSO!")
        print("Siga as instruções acima para instalar o certificado SSL!")
    else:
        print("\n❌ Falha na criação do script de instalação SSL")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
