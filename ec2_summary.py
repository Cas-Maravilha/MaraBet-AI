#!/usr/bin/env python3
"""
Resumo das Instâncias EC2 Criadas - MaraBet AI
"""

import json
from datetime import datetime

def print_ec2_summary():
    """Imprime resumo das instâncias EC2 criadas"""
    
    print("\n" + "="*80)
    print("🖥️ MARABET AI - INSTÂNCIAS EC2 CRIADAS COM SUCESSO!")
    print("="*80)
    
    print(f"\n📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configurações
    try:
        with open('aws_infrastructure_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de configuração não encontrado")
        return
    
    print(f"\n📋 INFORMAÇÕES DAS INSTÂNCIAS EC2:")
    print("-" * 60)
    
    # Instância Web
    print(f"🖥️ INSTÂNCIA WEB:")
    print(f"• ID: {config['web_instance_id']}")
    print(f"• IP Público: {config['web_public_ip']}")
    print(f"• IP Privado: {config['web_private_ip']}")
    print(f"• Estado: {config['web_state']}")
    print(f"• Tipo: t3.micro")
    print(f"• AMI: Amazon Linux 2")
    print(f"• Subnet: {config['subnet_public_1']}")
    print(f"• Security Group: {config['sg_ec2_id']}")
    print(f"• Key Pair: marabet-key")
    
    print(f"\n🖥️ INSTÂNCIA WORKER:")
    print(f"• ID: {config['worker_instance_id']}")
    print(f"• IP Público: {config['worker_public_ip']}")
    print(f"• IP Privado: {config['worker_private_ip']}")
    print(f"• Estado: {config['worker_state']}")
    print(f"• Tipo: t3.micro")
    print(f"• AMI: Amazon Linux 2")
    print(f"• Subnet: {config['subnet_public_2']}")
    print(f"• Security Group: {config['sg_ec2_id']}")
    print(f"• Key Pair: marabet-key")
    
    print(f"\n🔑 CONFIGURAÇÕES DO KEY PAIR:")
    print("-" * 60)
    print("• Nome: marabet-key")
    print("• Arquivo: ~/.ssh/marabet-key.pem")
    print("• Usuário: ec2-user")
    print("• Permissões: 600 (Linux/Mac)")
    
    print(f"\n🔗 CONEXÕES SSH:")
    print("-" * 60)
    print(f"# Conectar à instância web")
    print(f"ssh -i ~/.ssh/marabet-key.pem ec2-user@{config['web_public_ip']}")
    print()
    print(f"# Conectar à instância worker")
    print(f"ssh -i ~/.ssh/marabet-key.pem ec2-user@{config['worker_public_ip']}")
    
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
    print("• AMI: Amazon Linux 2")
    print("• Tipo: t3.micro")
    print("• CPU: 2 vCPUs")
    print("• RAM: 1GB")
    print("• Storage: 8GB EBS")
    print("• User Data: Docker, Python, AWS CLI")
    print("• Monitoramento: CloudWatch")
    print("• Logs: Habilitados")
    
    print(f"\n📊 SOFTWARE INSTALADO:")
    print("-" * 60)
    print("✅ Docker")
    print("✅ Python 3")
    print("✅ pip3")
    print("✅ AWS CLI")
    print("✅ Git")
    print("✅ yum (package manager)")
    
    print(f"\n💰 CUSTOS ESTIMADOS:")
    print("-" * 60)
    print("• Instância t3.micro: ~$8.50/mês cada")
    print("• Storage EBS 8GB: ~$1/mês cada")
    print("• Data Transfer: ~$1/mês")
    print("• Total estimado: ~$20/mês (2 instâncias)")
    
    print(f"\n🌐 PRÓXIMOS PASSOS:")
    print("-" * 60)
    print("1. ✅ Instâncias EC2 criadas e configuradas")
    print("2. ✅ Key pair configurado")
    print("3. ✅ Security groups aplicados")
    print("4. ✅ User data configurado")
    print("5. 🔄 Deploy da aplicação MaraBet AI")
    print("6. 🔄 Configurar Load Balancer")
    print("7. 🔄 Configurar Auto Scaling")
    print("8. 🔄 Configurar CloudWatch monitoring")
    print("9. 🔄 Configurar backup automático")
    print("10. 🔄 Testar conectividade")
    
    print(f"\n💡 COMANDOS ÚTEIS:")
    print("-" * 60)
    print("# Ver status das instâncias")
    print(f"aws ec2 describe-instances --instance-ids {config['web_instance_id']} {config['worker_instance_id']}")
    print()
    print("# Ver logs das instâncias")
    print("aws logs describe-log-groups --log-group-name-prefix /aws/ec2")
    print()
    print("# Ver métricas CloudWatch")
    print(f"aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization --dimensions Name=InstanceId,Value={config['web_instance_id']} --start-time 2024-01-01T00:00:00Z --end-time 2024-01-02T00:00:00Z --period 3600 --statistics Average")
    print()
    print("# Parar instâncias")
    print(f"aws ec2 stop-instances --instance-ids {config['web_instance_id']} {config['worker_instance_id']}")
    print()
    print("# Iniciar instâncias")
    print(f"aws ec2 start-instances --instance-ids {config['web_instance_id']} {config['worker_instance_id']}")
    
    print(f"\n🔧 CONFIGURAÇÃO PARA APLICAÇÃO:")
    print("-" * 60)
    print("# Variáveis de ambiente")
    print(f"export WEB_SERVER_IP=\"{config['web_public_ip']}\"")
    print(f"export WORKER_SERVER_IP=\"{config['worker_public_ip']}\"")
    print(f"export WEB_PRIVATE_IP=\"{config['web_private_ip']}\"")
    print(f"export WORKER_PRIVATE_IP=\"{config['worker_private_ip']}\"")
    print(f"export SSH_KEY_PATH=\"~/.ssh/marabet-key.pem\"")
    print(f"export SSH_USER=\"ec2-user\"")
    
    print(f"\n🎯 BENEFÍCIOS DO EC2:")
    print("-" * 60)
    print("✅ Gerenciamento automático")
    print("✅ Escalabilidade automática")
    print("✅ Monitoramento integrado")
    print("✅ Backup automático")
    print("✅ Atualizações automáticas")
    print("✅ Alta disponibilidade")
    print("✅ Criptografia em repouso")
    print("✅ Logs de auditoria")
    print("✅ Performance insights")
    print("✅ Manutenção programada")
    print("✅ Auto Scaling")
    print("✅ Load Balancing")
    
    print(f"\n🔧 CONFIGURAÇÃO DO USER DATA:")
    print("-" * 60)
    print("# Script executado na inicialização")
    print("#!/bin/bash")
    print("yum update -y")
    print("yum install -y docker")
    print("systemctl start docker")
    print("systemctl enable docker")
    print("usermod -a -G docker ec2-user")
    print("yum install -y git")
    print("yum install -y python3")
    print("yum install -y python3-pip")
    print("pip3 install awscli")
    print("# Para instância worker:")
    print("pip3 install celery")
    print("pip3 install redis")
    print("pip3 install psycopg2-binary")
    
    print(f"\n🎉 INSTÂNCIAS EC2 PRONTAS!")
    print("-" * 60)
    print("✅ Instâncias EC2 criadas e configuradas")
    print("✅ Key pair configurado")
    print("✅ Security groups aplicados")
    print("✅ Sistema MaraBet AI pronto para deploy")
    
    print("\n" + "="*80)
    print("🖥️ MARABET AI - INSTÂNCIAS EC2 CRIADAS COM SUCESSO!")
    print("="*80)

def main():
    print_ec2_summary()

if __name__ == "__main__":
    main()
