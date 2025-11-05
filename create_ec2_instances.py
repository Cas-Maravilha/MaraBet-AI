#!/usr/bin/env python3
"""
Script para Criar e Configurar EC2 - MaraBet AI
Cria instâncias EC2 com configurações de produção
"""

import subprocess
import json
import os
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

def create_key_pair():
    """Cria Key Pair para EC2"""
    print("🔑 MARABET AI - CRIANDO KEY PAIR")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Criar pasta .ssh se não existir
    ssh_dir = os.path.expanduser("~/.ssh")
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir)
        print(f"✅ Pasta .ssh criada: {ssh_dir}")
    else:
        print(f"✅ Pasta .ssh já existe: {ssh_dir}")
    
    # Verificar se key pair já existe
    check_key_command = "aws ec2 describe-key-pairs --key-names marabet-key"
    check_key_result = run_aws_command(check_key_command)
    
    if check_key_result and 'KeyPairs' in check_key_result:
        print("✅ Key pair já existe")
        return True
    
    # Criar key pair
    print("🔑 Criando key pair...")
    create_key_command = "aws ec2 create-key-pair --key-name marabet-key --query 'KeyMaterial' --output text"
    create_key_result = run_aws_command(create_key_command, return_text=True)
    
    if create_key_result:
        # Salvar chave privada
        key_file_path = os.path.join(ssh_dir, "marabet-key.pem")
        with open(key_file_path, 'w') as f:
            f.write(create_key_result)
        
        # Definir permissões corretas (apenas no Linux/Mac)
        if os.name != 'nt':  # Não é Windows
            os.chmod(key_file_path, 0o600)
        
        print(f"✅ Key pair criado e salvo em: {key_file_path}")
        return True
    else:
        print("❌ Falha ao criar key pair")
        return False

def create_ec2_instances():
    """Cria instâncias EC2"""
    print("\n🖥️ MARABET AI - CRIANDO INSTÂNCIAS EC2")
    print("=" * 60)
    
    # Carregar configuração existente
    try:
        with open('aws_infrastructure_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de configuração não encontrado")
        return False
    
    vpc_id = config['vpc_id']
    subnet_public_1 = config['subnet_public_1']
    subnet_public_2 = config['subnet_public_2']
    ec2_sg_id = config['sg_ec2_id']
    
    print(f"✅ VPC ID: {vpc_id}")
    print(f"✅ Subnet 1: {subnet_public_1}")
    print(f"✅ Subnet 2: {subnet_public_2}")
    print(f"✅ EC2 Security Group: {ec2_sg_id}")
    
    print("\n🖥️ ETAPA 1: CRIANDO INSTÂNCIA WEB")
    print("-" * 50)
    
    # Configurações da instância web
    web_instance_config = {
        "instance_name": "marabet-web",
        "instance_type": "t3.micro",
        "ami_id": "ami-0c02fb55956c7d316",  # Amazon Linux 2 AMI
        "subnet_id": subnet_public_1,
        "security_group": ec2_sg_id,
        "key_name": "marabet-key",
        "user_data": """#!/bin/bash
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user
yum install -y git
yum install -y python3
yum install -y python3-pip
pip3 install awscli
"""
    }
    
    print(f"📋 Configurações da instância web:")
    print(f"  • Nome: {web_instance_config['instance_name']}")
    print(f"  • Tipo: {web_instance_config['instance_type']}")
    print(f"  • AMI: {web_instance_config['ami_id']}")
    print(f"  • Subnet: {web_instance_config['subnet_id']}")
    print(f"  • Security Group: {web_instance_config['security_group']}")
    print(f"  • Key Pair: {web_instance_config['key_name']}")
    
    # Criar instância web
    web_instance_command = f'aws ec2 run-instances --image-id {web_instance_config["ami_id"]} --count 1 --instance-type {web_instance_config["instance_type"]} --key-name {web_instance_config["key_name"]} --security-group-ids {web_instance_config["security_group"]} --subnet-id {web_instance_config["subnet_id"]} --associate-public-ip-address --user-data "{web_instance_config["user_data"]}" --tag-specifications "ResourceType=instance,Tags=[{{Key=Name,Value={web_instance_config["instance_name"]}}},{{Key=Project,Value=MaraBet-AI}},{{Key=Environment,Value=production}},{{Key=Role,Value=web}}]"'
    
    print("🚀 Criando instância web...")
    web_instance_result = run_aws_command(web_instance_command)
    
    if web_instance_result and 'Instances' in web_instance_result:
        web_instance_id = web_instance_result['Instances'][0]['InstanceId']
        print(f"✅ Instância web criada: {web_instance_id}")
        config['web_instance_id'] = web_instance_id
    else:
        print("❌ Falha ao criar instância web")
        return False
    
    print("\n🖥️ ETAPA 2: CRIANDO INSTÂNCIA WORKER")
    print("-" * 50)
    
    # Configurações da instância worker
    worker_instance_config = {
        "instance_name": "marabet-worker",
        "instance_type": "t3.micro",
        "ami_id": "ami-0c02fb55956c7d316",  # Amazon Linux 2 AMI
        "subnet_id": subnet_public_2,
        "security_group": ec2_sg_id,
        "key_name": "marabet-key",
        "user_data": """#!/bin/bash
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user
yum install -y git
yum install -y python3
yum install -y python3-pip
pip3 install awscli
pip3 install celery
pip3 install redis
pip3 install psycopg2-binary
"""
    }
    
    print(f"📋 Configurações da instância worker:")
    print(f"  • Nome: {worker_instance_config['instance_name']}")
    print(f"  • Tipo: {worker_instance_config['instance_type']}")
    print(f"  • AMI: {worker_instance_config['ami_id']}")
    print(f"  • Subnet: {worker_instance_config['subnet_id']}")
    print(f"  • Security Group: {worker_instance_config['security_group']}")
    print(f"  • Key Pair: {worker_instance_config['key_name']}")
    
    # Criar instância worker
    worker_instance_command = f'aws ec2 run-instances --image-id {worker_instance_config["ami_id"]} --count 1 --instance-type {worker_instance_config["instance_type"]} --key-name {worker_instance_config["key_name"]} --security-group-ids {worker_instance_config["security_group"]} --subnet-id {worker_instance_config["subnet_id"]} --associate-public-ip-address --user-data "{worker_instance_config["user_data"]}" --tag-specifications "ResourceType=instance,Tags=[{{Key=Name,Value={worker_instance_config["instance_name"]}}},{{Key=Project,Value=MaraBet-AI}},{{Key=Environment,Value=production}},{{Key=Role,Value=worker}}]"'
    
    print("🚀 Criando instância worker...")
    worker_instance_result = run_aws_command(worker_instance_command)
    
    if worker_instance_result and 'Instances' in worker_instance_result:
        worker_instance_id = worker_instance_result['Instances'][0]['InstanceId']
        print(f"✅ Instância worker criada: {worker_instance_id}")
        config['worker_instance_id'] = worker_instance_id
    else:
        print("❌ Falha ao criar instância worker")
        return False
    
    print("\n🖥️ ETAPA 3: AGUARDANDO INSTÂNCIAS")
    print("-" * 50)
    
    # Aguardar instâncias ficarem disponíveis
    print("⏳ Aguardando instâncias ficarem disponíveis...")
    
    # Aguardar instância web
    web_wait_command = f'aws ec2 wait instance-running --instance-ids {web_instance_id}'
    web_wait_result = run_aws_command(web_wait_command)
    
    if web_wait_result is not None:
        print("✅ Instância web disponível!")
    else:
        print("⚠️ Timeout aguardando instância web")
    
    # Aguardar instância worker
    worker_wait_command = f'aws ec2 wait instance-running --instance-ids {worker_instance_id}'
    worker_wait_result = run_aws_command(worker_wait_command)
    
    if worker_wait_result is not None:
        print("✅ Instância worker disponível!")
    else:
        print("⚠️ Timeout aguardando instância worker")
    
    print("\n🖥️ ETAPA 4: OBTENDO INFORMAÇÕES DAS INSTÂNCIAS")
    print("-" * 50)
    
    # Obter informações da instância web
    web_describe_command = f'aws ec2 describe-instances --instance-ids {web_instance_id}'
    web_describe_result = run_aws_command(web_describe_command)
    
    if web_describe_result and 'Reservations' in web_describe_result:
        web_instance = web_describe_result['Reservations'][0]['Instances'][0]
        web_public_ip = web_instance.get('PublicIpAddress', 'N/A')
        web_private_ip = web_instance.get('PrivateIpAddress', 'N/A')
        web_state = web_instance['State']['Name']
        
        print(f"✅ Instância Web:")
        print(f"  • ID: {web_instance_id}")
        print(f"  • IP Público: {web_public_ip}")
        print(f"  • IP Privado: {web_private_ip}")
        print(f"  • Estado: {web_state}")
        
        config['web_public_ip'] = web_public_ip
        config['web_private_ip'] = web_private_ip
        config['web_state'] = web_state
    
    # Obter informações da instância worker
    worker_describe_command = f'aws ec2 describe-instances --instance-ids {worker_instance_id}'
    worker_describe_result = run_aws_command(worker_describe_command)
    
    if worker_describe_result and 'Reservations' in worker_describe_result:
        worker_instance = worker_describe_result['Reservations'][0]['Instances'][0]
        worker_public_ip = worker_instance.get('PublicIpAddress', 'N/A')
        worker_private_ip = worker_instance.get('PrivateIpAddress', 'N/A')
        worker_state = worker_instance['State']['Name']
        
        print(f"✅ Instância Worker:")
        print(f"  • ID: {worker_instance_id}")
        print(f"  • IP Público: {worker_public_ip}")
        print(f"  • IP Privado: {worker_private_ip}")
        print(f"  • Estado: {worker_state}")
        
        config['worker_public_ip'] = worker_public_ip
        config['worker_private_ip'] = worker_private_ip
        config['worker_state'] = worker_state
    
    print("\n🖥️ ETAPA 5: SALVANDO CONFIGURAÇÕES")
    print("-" * 50)
    
    # Salvar configurações atualizadas
    config['ec2_created_at'] = datetime.now().isoformat()
    config['updated_at'] = datetime.now().isoformat()
    
    with open('aws_infrastructure_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configurações salvas em: aws_infrastructure_config.json")
    
    print("\n🎉 INSTÂNCIAS EC2 CRIADAS COM SUCESSO!")
    print("=" * 60)
    
    print("\n📋 INFORMAÇÕES DAS INSTÂNCIAS:")
    print("-" * 40)
    print(f"• Instância Web: {web_instance_id}")
    print(f"• Instância Worker: {worker_instance_id}")
    print(f"• Key Pair: marabet-key")
    print(f"• Security Group: {ec2_sg_id}")
    
    print("\n🔗 CONEXÕES SSH:")
    print("-" * 40)
    if 'web_public_ip' in config and config['web_public_ip'] != 'N/A':
        print(f"# Conectar à instância web")
        print(f"ssh -i ~/.ssh/marabet-key.pem ec2-user@{config['web_public_ip']}")
    if 'worker_public_ip' in config and config['worker_public_ip'] != 'N/A':
        print(f"# Conectar à instância worker")
        print(f"ssh -i ~/.ssh/marabet-key.pem ec2-user@{config['worker_public_ip']}")
    
    print("\n🌐 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Instâncias EC2 criadas")
    print("2. ✅ Key pair configurado")
    print("3. ✅ Security groups aplicados")
    print("4. ✅ User data configurado")
    print("5. 🔄 Deploy da aplicação MaraBet AI")
    print("6. 🔄 Configurar Load Balancer")
    print("7. 🔄 Configurar Auto Scaling")
    print("8. 🔄 Configurar CloudWatch monitoring")
    
    print("\n💡 COMANDOS ÚTEIS:")
    print("-" * 40)
    print(f"# Ver status das instâncias")
    print(f"aws ec2 describe-instances --instance-ids {web_instance_id} {worker_instance_id}")
    print()
    print(f"# Ver logs das instâncias")
    print(f"aws logs describe-log-groups --log-group-name-prefix /aws/ec2")
    print()
    print(f"# Ver métricas CloudWatch")
    print(f"aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization --dimensions Name=InstanceId,Value={web_instance_id} --start-time 2024-01-01T00:00:00Z --end-time 2024-01-02T00:00:00Z --period 3600 --statistics Average")
    
    print("\n🎯 INSTÂNCIAS EC2 PRONTAS!")
    print("-" * 40)
    print("✅ Instâncias EC2 criadas e configuradas")
    print("✅ Key pair configurado")
    print("✅ Security groups aplicados")
    print("✅ Sistema MaraBet AI pronto para deploy")
    
    return True

def main():
    print("🚀 Iniciando criação das instâncias EC2...")
    
    # Verificar se AWS CLI está configurado
    check_command = "aws sts get-caller-identity"
    check_result = run_aws_command(check_command)
    
    if not check_result:
        print("❌ AWS CLI não configurado ou credenciais inválidas")
        print("💡 Execute: aws configure")
        return False
    
    print("✅ AWS CLI configurado e funcionando")
    
    # Criar Key Pair
    key_success = create_key_pair()
    if not key_success:
        print("❌ Falha na criação do Key Pair")
        return False
    
    # Criar instâncias EC2
    ec2_success = create_ec2_instances()
    
    if ec2_success:
        print("\n🎯 INSTÂNCIAS EC2 CRIADAS COM SUCESSO!")
        print("As instâncias EC2 do MaraBet AI estão prontas para uso!")
    else:
        print("\n❌ Falha na criação das instâncias EC2")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
