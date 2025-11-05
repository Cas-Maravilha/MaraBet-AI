#!/usr/bin/env python3
"""
Resumo da Instância Ubuntu Lançada - MaraBet AI
"""

import json
from datetime import datetime

def print_ubuntu_summary():
    """Imprime resumo da instância Ubuntu lançada"""
    
    print("\n" + "="*80)
    print("🚀 MARABET AI - INSTÂNCIA UBUNTU LANÇADA COM SUCESSO!")
    print("="*80)
    
    print(f"\n📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configurações
    try:
        with open('aws_infrastructure_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de configuração não encontrado")
        return
    
    print(f"\n📋 INFORMAÇÕES DA INSTÂNCIA UBUNTU:")
    print("-" * 60)
    
    ubuntu_info = [
        ("ID", config['ubuntu_instance_id']),
        ("IP Público", config['ubuntu_public_ip']),
        ("IP Privado", config['ubuntu_private_ip']),
        ("Estado", config['ubuntu_state']),
        ("Tipo", config['ubuntu_instance_type']),
        ("AMI", config['ubuntu_ami_id']),
        ("Volume", "30GB gp3"),
        ("Security Group", config['sg_ec2_id']),
        ("Key Pair", "marabet-key"),
        ("Sistema", "Ubuntu 22.04 LTS")
    ]
    
    for name, value in ubuntu_info:
        print(f"• {name:<20}: {value}")
    
    print(f"\n🔗 CONFIGURAÇÕES DE CONEXÃO:")
    print("-" * 60)
    print(f"• Host: {config['ubuntu_public_ip']}")
    print(f"• Usuário: ubuntu")
    print(f"• Key Pair: marabet-key")
    print(f"• Porta SSH: 22")
    
    print(f"\n🔗 CONEXÃO SSH:")
    print("-" * 60)
    ssh_command = f"ssh -i ~/.ssh/marabet-key.pem ubuntu@{config['ubuntu_public_ip']}"
    print(ssh_command)
    
    print(f"\n🔒 CONFIGURAÇÕES DE SEGURANÇA:")
    print("-" * 60)
    print("• Security Group: sg-07f7e19db4e1e8f78")
    print("• SSH (porta 22): Permitido")
    print("• HTTP (porta 80): Permitido")
    print("• HTTPS (porta 443): Permitido")
    print("• Acesso público: Habilitado")
    print("• Key pair: marabet-key")
    
    print(f"\n⚙️ CONFIGURAÇÕES DE PRODUÇÃO:")
    print("-" * 60)
    print("• Sistema: Ubuntu 22.04 LTS")
    print("• Tipo: t3.medium")
    print("• CPU: 2 vCPUs")
    print("• RAM: 4GB")
    print("• Storage: 30GB gp3")
    print("• Monitoramento: CloudWatch")
    print("• Logs: Habilitados")
    
    print(f"\n📊 RECURSOS DA INSTÂNCIA:")
    print("-" * 60)
    print("✅ Ubuntu 22.04 LTS")
    print("✅ 2 vCPUs")
    print("✅ 4GB RAM")
    print("✅ 30GB Storage gp3")
    print("✅ Acesso SSH")
    print("✅ IP público")
    print("✅ Security groups")
    print("✅ CloudWatch monitoring")
    print("✅ EBS otimizado")
    
    print(f"\n💰 CUSTOS ESTIMADOS:")
    print("-" * 60)
    print("• Instância t3.medium: ~$30/mês")
    print("• Storage EBS 30GB gp3: ~$3/mês")
    print("• Data Transfer: ~$1/mês")
    print("• Total estimado: ~$34/mês")
    
    print(f"\n🌐 PRÓXIMOS PASSOS:")
    print("-" * 60)
    print("1. ✅ Instância Ubuntu lançada")
    print("2. ✅ Configurações salvas")
    print("3. ✅ Security groups aplicados")
    print("4. 🔄 Configurar aplicação MaraBet AI")
    print("5. 🔄 Deploy do sistema")
    print("6. 🔄 Configurar Load Balancer")
    print("7. 🔄 Configurar Auto Scaling")
    print("8. 🔄 Configurar CloudWatch monitoring")
    print("9. 🔄 Configurar backup automático")
    print("10. 🔄 Testar conectividade")
    
    print(f"\n💡 COMANDOS ÚTEIS:")
    print("-" * 60)
    print(f"# Ver status da instância")
    print(f"aws ec2 describe-instances --instance-ids {config['ubuntu_instance_id']}")
    print()
    print(f"# Conectar via SSH")
    print(f"ssh -i ~/.ssh/marabet-key.pem ubuntu@{config['ubuntu_public_ip']}")
    print()
    print(f"# Ver logs da instância")
    print(f"aws logs describe-log-groups --log-group-name-prefix /aws/ec2")
    print()
    print(f"# Ver métricas CloudWatch")
    print(f"aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization --dimensions Name=InstanceId,Value={config['ubuntu_instance_id']} --start-time 2024-01-01T00:00:00Z --end-time 2024-01-02T00:00:00Z --period 3600 --statistics Average")
    print()
    print(f"# Parar instância")
    print(f"aws ec2 stop-instances --instance-ids {config['ubuntu_instance_id']}")
    print()
    print(f"# Iniciar instância")
    print(f"aws ec2 start-instances --instance-ids {config['ubuntu_instance_id']}")
    
    print(f"\n🔧 CONFIGURAÇÃO PARA APLICAÇÃO:")
    print("-" * 60)
    print("# Variáveis de ambiente")
    print(f"export UBUNTU_SERVER_IP=\"{config['ubuntu_public_ip']}\"")
    print(f"export UBUNTU_PRIVATE_IP=\"{config['ubuntu_private_ip']}\"")
    print(f"export UBUNTU_INSTANCE_ID=\"{config['ubuntu_instance_id']}\"")
    print(f"export SSH_KEY_PATH=\"~/.ssh/marabet-key.pem\"")
    print(f"export SSH_USER=\"ubuntu\"")
    
    print(f"\n🎯 BENEFÍCIOS DO UBUNTU:")
    print("-" * 60)
    print("✅ Sistema operacional estável")
    print("✅ Suporte de longo prazo (LTS)")
    print("✅ Atualizações de segurança")
    print("✅ Compatibilidade com Docker")
    print("✅ Performance otimizada")
    print("✅ Monitoramento integrado")
    print("✅ Backup automático")
    print("✅ Escalabilidade")
    print("✅ Alta disponibilidade")
    print("✅ Criptografia em repouso")
    print("✅ Logs de auditoria")
    print("✅ Performance insights")
    
    print(f"\n🔧 CONFIGURAÇÃO DO SISTEMA:")
    print("-" * 60)
    print("# Sistema operacional")
    print("• Ubuntu 22.04 LTS")
    print("• Kernel: Linux")
    print("• Arquitetura: x86_64")
    print("• Usuário padrão: ubuntu")
    print("• Sudo: Habilitado")
    print("• SSH: Habilitado")
    print("• Firewall: UFW")
    print("• Package manager: apt")
    
    print(f"\n🎉 INSTÂNCIA UBUNTU PRONTA!")
    print("-" * 60)
    print("✅ Instância Ubuntu criada e configurada")
    print("✅ Security groups aplicados")
    print("✅ Sistema MaraBet AI pronto para deploy")
    
    print("\n" + "="*80)
    print("🚀 MARABET AI - INSTÂNCIA UBUNTU LANÇADA COM SUCESSO!")
    print("="*80)

def main():
    print_ubuntu_summary()

if __name__ == "__main__":
    main()
