#!/usr/bin/env python3
"""
Script para Lançar Instância EC2 Ubuntu - MaraBet AI
Cria instância EC2 com Ubuntu 22.04 e configurações de produção
"""

import subprocess
import json
import time
from datetime import datetime

def run_aws_command(command, return_text=False):
    """Executa comando AWS CLI e retorna resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            if return_text:
                return result.stdout.strip()
            else:
                return json.loads(result.stdout) if result.stdout.strip() else {}
        else:
            print(f"❌ Erro no comando: {command}")
            print(f"Erro: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Exceção no comando: {command}")
        print(f"Erro: {e}")
        return None

def launch_ubuntu_instance():
    """Lança instância EC2 com Ubuntu 22.04"""
    print("🚀 MARABET AI - LANÇANDO INSTÂNCIA EC2 UBUNTU")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configuração existente
    try:
        with open('aws_infrastructure_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de configuração não encontrado")
        return False
    
    vpc_id = config['vpc_id']
    subnet_public_1 = config['subnet_public_1']
    ec2_sg_id = config['sg_ec2_id']
    
    print(f"✅ VPC ID: {vpc_id}")
    print(f"✅ Subnet: {subnet_public_1}")
    print(f"✅ EC2 Security Group: {ec2_sg_id}")
    
    print("\n🚀 ETAPA 1: BUSCANDO AMI DO UBUNTU 22.04")
    print("-" * 50)
    
    # Buscar AMI do Ubuntu 22.04 mais recente
    ami_command = 'aws ec2 describe-images --owners 099720109477 --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" --output text'
    ami_id = run_aws_command(ami_command, return_text=True)
    
    if ami_id:
        print(f"✅ AMI encontrada: {ami_id}")
    else:
        print("❌ Falha ao encontrar AMI do Ubuntu 22.04")
        return False
    
    print("\n🚀 ETAPA 2: LANÇANDO INSTÂNCIA EC2")
    print("-" * 50)
    
    # Configurações da instância
    instance_config = {
        "instance_name": "marabet-server",
        "instance_type": "t3.medium",
        "ami_id": ami_id,
        "subnet_id": subnet_public_1,
        "security_group": ec2_sg_id,
        "key_name": "marabet-key",
        "volume_size": 30,
        "volume_type": "gp3"
    }
    
    print(f"📋 Configurações da instância:")
    print(f"  • Nome: {instance_config['instance_name']}")
    print(f"  • Tipo: {instance_config['instance_type']}")
    print(f"  • AMI: {instance_config['ami_id']}")
    print(f"  • Subnet: {instance_config['subnet_id']}")
    print(f"  • Security Group: {instance_config['security_group']}")
    print(f"  • Key Pair: {instance_config['key_name']}")
    print(f"  • Volume: {instance_config['volume_size']}GB {instance_config['volume_type']}")
    
    # Lançar instância EC2
    launch_command = f'aws ec2 run-instances --image-id {instance_config["ami_id"]} --instance-type {instance_config["instance_type"]} --key-name {instance_config["key_name"]} --security-group-ids {instance_config["security_group"]} --subnet-id {instance_config["subnet_id"]} --associate-public-ip-address --tag-specifications "ResourceType=instance,Tags=[{{Key=Name,Value={instance_config["instance_name"]}}},{{Key=Project,Value=MaraBet-AI}},{{Key=Environment,Value=production}},{{Key=Role,Value=server}}]" --block-device-mappings "DeviceName=/dev/sda1,Ebs={{VolumeSize={instance_config["volume_size"]},VolumeType={instance_config["volume_type"]}}}"'
    
    print("🚀 Lançando instância EC2...")
    launch_result = run_aws_command(launch_command)
    
    if launch_result and 'Instances' in launch_result:
        instance_id = launch_result['Instances'][0]['InstanceId']
        print(f"✅ Instância lançada: {instance_id}")
    else:
        print("❌ Falha ao lançar instância EC2")
        return False
    
    print("\n🚀 ETAPA 3: AGUARDANDO INSTÂNCIA")
    print("-" * 50)
    
    # Aguardar instância estar rodando
    print("⏳ Aguardando instância ficar disponível...")
    wait_command = f'aws ec2 wait instance-running --instance-ids {instance_id}'
    wait_result = run_aws_command(wait_command)
    
    if wait_result is not None:
        print("✅ Instância disponível!")
    else:
        print("⚠️ Timeout aguardando instância, mas continuando...")
    
    print("\n🚀 ETAPA 4: OBTENDO INFORMAÇÕES DA INSTÂNCIA")
    print("-" * 50)
    
    # Obter informações da instância
    describe_command = f'aws ec2 describe-instances --instance-ids {instance_id}'
    describe_result = run_aws_command(describe_command)
    
    if describe_result and 'Reservations' in describe_result:
        instance = describe_result['Reservations'][0]['Instances'][0]
        public_ip = instance.get('PublicIpAddress', 'N/A')
        private_ip = instance.get('PrivateIpAddress', 'N/A')
        state = instance['State']['Name']
        instance_type = instance['InstanceType']
        ami_id = instance['ImageId']
        
        print(f"✅ Instância Ubuntu:")
        print(f"  • ID: {instance_id}")
        print(f"  • IP Público: {public_ip}")
        print(f"  • IP Privado: {private_ip}")
        print(f"  • Estado: {state}")
        print(f"  • Tipo: {instance_type}")
        print(f"  • AMI: {ami_id}")
        
        # Salvar informações na configuração
        config['ubuntu_instance_id'] = instance_id
        config['ubuntu_public_ip'] = public_ip
        config['ubuntu_private_ip'] = private_ip
        config['ubuntu_state'] = state
        config['ubuntu_instance_type'] = instance_type
        config['ubuntu_ami_id'] = ami_id
        config['ubuntu_created_at'] = datetime.now().isoformat()
        
    else:
        print("❌ Falha ao obter informações da instância")
        return False
    
    print("\n🚀 ETAPA 5: SALVANDO CONFIGURAÇÕES")
    print("-" * 50)
    
    # Salvar configurações atualizadas
    config['updated_at'] = datetime.now().isoformat()
    
    with open('aws_infrastructure_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configurações salvas em: aws_infrastructure_config.json")
    
    print("\n🎉 INSTÂNCIA UBUNTU LANÇADA COM SUCESSO!")
    print("=" * 60)
    
    print("\n📋 INFORMAÇÕES DA INSTÂNCIA:")
    print("-" * 40)
    print(f"• ID: {instance_id}")
    print(f"• IP Público: {public_ip}")
    print(f"• IP Privado: {private_ip}")
    print(f"• Estado: {state}")
    print(f"• Tipo: {instance_type}")
    print(f"• AMI: {ami_id}")
    print(f"• Volume: 30GB gp3")
    print(f"• Security Group: {ec2_sg_id}")
    print(f"• Key Pair: marabet-key")
    
    print("\n🔗 CONEXÃO SSH:")
    print("-" * 40)
    if public_ip != 'N/A':
        print(f"# Conectar à instância Ubuntu")
        print(f"ssh -i ~/.ssh/marabet-key.pem ubuntu@{public_ip}")
    else:
        print("⚠️ IP público não disponível ainda")
    
    print("\n🌐 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Instância Ubuntu lançada")
    print("2. ✅ Configurações salvas")
    print("3. ✅ Security groups aplicados")
    print("4. 🔄 Configurar aplicação MaraBet AI")
    print("5. 🔄 Deploy do sistema")
    print("6. 🔄 Configurar Load Balancer")
    print("7. 🔄 Configurar Auto Scaling")
    print("8. 🔄 Configurar CloudWatch monitoring")
    
    print("\n💡 COMANDOS ÚTEIS:")
    print("-" * 40)
    print(f"# Ver status da instância")
    print(f"aws ec2 describe-instances --instance-ids {instance_id}")
    print()
    print(f"# Conectar via SSH")
    if public_ip != 'N/A':
        print(f"ssh -i ~/.ssh/marabet-key.pem ubuntu@{public_ip}")
    print()
    print(f"# Ver logs da instância")
    print(f"aws logs describe-log-groups --log-group-name-prefix /aws/ec2")
    print()
    print(f"# Ver métricas CloudWatch")
    print(f"aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization --dimensions Name=InstanceId,Value={instance_id} --start-time 2024-01-01T00:00:00Z --end-time 2024-01-02T00:00:00Z --period 3600 --statistics Average")
    
    print("\n🎯 INSTÂNCIA UBUNTU PRONTA!")
    print("-" * 40)
    print("✅ Instância Ubuntu criada e configurada")
    print("✅ Security groups aplicados")
    print("✅ Sistema MaraBet AI pronto para deploy")
    
    return True

def main():
    print("🚀 Iniciando lançamento da instância EC2 Ubuntu...")
    
    # Verificar se AWS CLI está configurado
    check_command = "aws sts get-caller-identity"
    check_result = run_aws_command(check_command)
    
    if not check_result:
        print("❌ AWS CLI não configurado ou credenciais inválidas")
        print("💡 Execute: aws configure")
        return False
    
    print("✅ AWS CLI configurado e funcionando")
    
    # Lançar instância Ubuntu
    success = launch_ubuntu_instance()
    
    if success:
        print("\n🎯 INSTÂNCIA UBUNTU LANÇADA COM SUCESSO!")
        print("A instância Ubuntu do MaraBet AI está pronta para uso!")
    else:
        print("\n❌ Falha no lançamento da instância Ubuntu")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
