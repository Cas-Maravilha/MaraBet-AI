#!/usr/bin/env python3
"""
Guia de Instalação Docker - MaraBet AI
"""

def print_docker_installation_guide():
    """Imprime guia completo de instalação do Docker"""
    from datetime import datetime
    
    print("\n" + "="*80)
    print("🐳 MARABET AI - GUIA DE INSTALAÇÃO DOCKER")
    print("="*80)
    
    print(f"\n📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    print(f"\n🔍 VERIFICAÇÃO ATUAL:")
    print("-" * 50)
    print("• Docker: ❌ Não instalado")
    print("• Docker Compose: ❌ Não instalado")
    print("• .env.production: ✅ Configurado")
    print("• nginx.conf: ✅ Configurado")
    
    print(f"\n📥 INSTALAÇÃO DO DOCKER DESKTOP:")
    print("-" * 50)
    print("1. Acesse: https://www.docker.com/products/docker-desktop/")
    print("2. Clique em 'Download for Windows'")
    print("3. Execute o instalador Docker Desktop Installer.exe")
    print("4. Siga as instruções do instalador")
    print("5. Reinicie o computador após a instalação")
    print("6. Abra o Docker Desktop")
    print("7. Aguarde a inicialização completa")
    
    print(f"\n⚙️ CONFIGURAÇÃO DO DOCKER:")
    print("-" * 50)
    print("1. Abra o Docker Desktop")
    print("2. Vá em Settings (Configurações)")
    print("3. Configure os recursos:")
    print("   • CPUs: 2-4 cores")
    print("   • Memory: 4-8 GB")
    print("   • Disk: 20+ GB")
    print("4. Ative 'Use WSL 2 based engine'")
    print("5. Clique em 'Apply & Restart'")
    
    print(f"\n🧪 TESTE DA INSTALAÇÃO:")
    print("-" * 50)
    print("Abra o PowerShell e execute:")
    print("docker --version")
    print("docker-compose --version")
    print("docker run hello-world")
    
    print(f"\n📋 COMANDOS DOCKER ÚTEIS:")
    print("-" * 50)
    print("# Verificar versão")
    print("docker --version")
    print("docker-compose --version")
    print("")
    print("# Ver containers em execução")
    print("docker ps")
    print("")
    print("# Ver todas as imagens")
    print("docker images")
    print("")
    print("# Parar todos os containers")
    print("docker stop $(docker ps -q)")
    print("")
    print("# Remover containers parados")
    print("docker container prune")
    print("")
    print("# Remover imagens não utilizadas")
    print("docker image prune")
    
    print(f"\n🚀 DEPLOY DO MARABET AI:")
    print("-" * 50)
    print("Após instalar o Docker, execute:")
    print("python deploy_simplified.py")
    print("")
    print("Ou manualmente:")
    print("docker-compose -f docker-compose.production.yml up --build -d")
    
    print(f"\n🔧 SOLUÇÃO DE PROBLEMAS:")
    print("-" * 50)
    print("❌ 'Docker não encontrado':")
    print("   • Verifique se Docker Desktop está instalado")
    print("   • Reinicie o PowerShell/CMD")
    print("   • Verifique se Docker Desktop está rodando")
    print("")
    print("❌ 'Docker daemon not running':")
    print("   • Abra o Docker Desktop")
    print("   • Aguarde a inicialização completa")
    print("   • Verifique se não há erros na interface")
    print("")
    print("❌ 'Port already in use':")
    print("   • Verifique se as portas 80, 8000, 6379 estão livres")
    print("   • Use: netstat -an | findstr :8000")
    print("   • Pare outros serviços que usam essas portas")
    
    print(f"\n📊 ESTRUTURA DO PROJETO:")
    print("-" * 50)
    print("• docker-compose.production.yml - Configuração principal")
    print("• .env.production - Variáveis de ambiente")
    print("• nginx.conf - Configuração do Nginx")
    print("• Dockerfile - Imagem da aplicação")
    print("• deploy_simplified.py - Script de deploy")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print("-" * 50)
    print("1. ✅ Instalar Docker Desktop")
    print("2. ✅ Configurar recursos do Docker")
    print("3. ✅ Testar instalação")
    print("4. 🔄 Executar deploy do MaraBet AI")
    print("5. 🔍 Verificar funcionamento")
    print("6. 📊 Monitorar logs")
    
    print(f"\n💡 DICAS IMPORTANTES:")
    print("-" * 50)
    print("• Docker Desktop deve estar rodando para usar comandos Docker")
    print("• Primeira execução pode demorar (download de imagens)")
    print("• Use 'docker-compose logs' para ver logs da aplicação")
    print("• Use 'docker-compose down' para parar todos os serviços")
    print("• Mantenha o Docker Desktop atualizado")
    
    print(f"\n🎉 APÓS INSTALAÇÃO:")
    print("-" * 50)
    print("O sistema MaraBet AI estará disponível em:")
    print("• http://localhost:8000 - Aplicação principal")
    print("• http://localhost:80 - Nginx (proxy reverso)")
    print("• localhost:6379 - Redis (cache)")
    
    print("\n" + "="*80)
    print("🐳 DOCKER DESKTOP - INSTALAÇÃO NECESSÁRIA!")
    print("="*80)

def main():
    from datetime import datetime
    print_docker_installation_guide()

if __name__ == "__main__":
    main()
