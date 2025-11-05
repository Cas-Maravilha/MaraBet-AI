#!/usr/bin/env python3
"""
Script para Criar Security Groups Adicionais - MaraBet AI
Cria Security Groups específicos para EC2 e RDS
"""

import subprocess
import json
import time
from datetime import datetime

def run_aws_command(command):
    """Executa comando AWS CLI e retorna resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout) if result.stdout.strip() else {}
        else:
            print(f"❌ Erro no comando: {command}")
            print(f"Erro: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Exceção no comando: {command}")
        print(f"Erro: {e}")
        return None

def create_additional_security_groups():
    """Cria Security Groups adicionais para EC2 e RDS"""
    print("🔒 MARABET AI - CRIANDO SECURITY GROUPS ADICIONAIS")
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
    print(f"✅ VPC ID carregado: {vpc_id}")
    
    print("\n🔒 ETAPA 1: CRIANDO SECURITY GROUP PARA EC2")
    print("-" * 50)
    
    # Criar Security Group para EC2
    ec2_sg_command = f'aws ec2 create-security-group --group-name marabet-ec2-sg --description "Security group for MaraBet EC2 instances" --vpc-id {vpc_id} --tag-specifications "ResourceType=security-group,Tags=[{{Key=Name,Value=marabet-ec2-sg}},{{Key=Project,Value=MaraBet-AI}}]"'
    ec2_sg_result = run_aws_command(ec2_sg_command)
    
    if ec2_sg_result and 'GroupId' in ec2_sg_result:
        ec2_sg_id = ec2_sg_result['GroupId']
        config['sg_ec2_id'] = ec2_sg_id
        print(f"✅ Security Group EC2 criado: {ec2_sg_id}")
    else:
        print("❌ Falha ao criar Security Group EC2")
        return False
    
    # Adicionar regras ao Security Group EC2
    print("\n📋 Adicionando regras ao Security Group EC2...")
    
    ec2_rules = [
        (22, "SSH", "0.0.0.0/0"),
        (80, "HTTP", "0.0.0.0/0"),
        (443, "HTTPS", "0.0.0.0/0"),
        (8000, "MaraBet App", "0.0.0.0/0"),
        (3000, "Development", "0.0.0.0/0"),
        (8080, "Alternative App", "0.0.0.0/0")
    ]
    
    for port, description, cidr in ec2_rules:
        rule_command = f'aws ec2 authorize-security-group-ingress --group-id {ec2_sg_id} --protocol tcp --port {port} --cidr {cidr}'
        rule_result = run_aws_command(rule_command)
        
        if rule_result is not None:
            print(f"✅ Regra adicionada: {description} (porta {port})")
        else:
            print(f"❌ Falha ao adicionar regra: {description} (porta {port})")
    
    print("\n🔒 ETAPA 2: CRIANDO SECURITY GROUP PARA RDS")
    print("-" * 50)
    
    # Criar Security Group para RDS
    rds_sg_command = f'aws ec2 create-security-group --group-name marabet-rds-sg --description "Security group for MaraBet RDS database" --vpc-id {vpc_id} --tag-specifications "ResourceType=security-group,Tags=[{{Key=Name,Value=marabet-rds-sg}},{{Key=Project,Value=MaraBet-AI}}]"'
    rds_sg_result = run_aws_command(rds_sg_command)
    
    if rds_sg_result and 'GroupId' in rds_sg_result:
        rds_sg_id = rds_sg_result['GroupId']
        config['sg_rds_id'] = rds_sg_id
        print(f"✅ Security Group RDS criado: {rds_sg_id}")
    else:
        print("❌ Falha ao criar Security Group RDS")
        return False
    
    # Adicionar regras ao Security Group RDS
    print("\n📋 Adicionando regras ao Security Group RDS...")
    
    rds_rules = [
        (5432, "PostgreSQL", ec2_sg_id),
        (3306, "MySQL", ec2_sg_id),
        (6379, "Redis", ec2_sg_id),
        (11211, "Memcached", ec2_sg_id)
    ]
    
    for port, description, source_group in rds_rules:
        rule_command = f'aws ec2 authorize-security-group-ingress --group-id {rds_sg_id} --protocol tcp --port {port} --source-group {source_group}'
        rule_result = run_aws_command(rule_command)
        
        if rule_result is not None:
            print(f"✅ Regra adicionada: {description} (porta {port}) do EC2")
        else:
            print(f"❌ Falha ao adicionar regra: {description} (porta {port})")
    
    print("\n🔒 ETAPA 3: CRIANDO SECURITY GROUP PARA ELASTICACHE")
    print("-" * 50)
    
    # Criar Security Group para ElastiCache
    cache_sg_command = f'aws ec2 create-security-group --group-name marabet-cache-sg --description "Security group for MaraBet ElastiCache" --vpc-id {vpc_id} --tag-specifications "ResourceType=security-group,Tags=[{{Key=Name,Value=marabet-cache-sg}},{{Key=Project,Value=MaraBet-AI}}]"'
    cache_sg_result = run_aws_command(cache_sg_command)
    
    if cache_sg_result and 'GroupId' in cache_sg_result:
        cache_sg_id = cache_sg_result['GroupId']
        config['sg_cache_id'] = cache_sg_id
        print(f"✅ Security Group ElastiCache criado: {cache_sg_id}")
    else:
        print("❌ Falha ao criar Security Group ElastiCache")
        return False
    
    # Adicionar regras ao Security Group ElastiCache
    print("\n📋 Adicionando regras ao Security Group ElastiCache...")
    
    cache_rules = [
        (6379, "Redis", ec2_sg_id),
        (11211, "Memcached", ec2_sg_id)
    ]
    
    for port, description, source_group in cache_rules:
        rule_command = f'aws ec2 authorize-security-group-ingress --group-id {cache_sg_id} --protocol tcp --port {port} --source-group {source_group}'
        rule_result = run_aws_command(rule_command)
        
        if rule_result is not None:
            print(f"✅ Regra adicionada: {description} (porta {port}) do EC2")
        else:
            print(f"❌ Falha ao adicionar regra: {description} (porta {port})")
    
    print("\n🔒 ETAPA 4: CRIANDO SECURITY GROUP PARA LOAD BALANCER")
    print("-" * 50)
    
    # Criar Security Group para Load Balancer
    lb_sg_command = f'aws ec2 create-security-group --group-name marabet-lb-sg --description "Security group for MaraBet Load Balancer" --vpc-id {vpc_id} --tag-specifications "ResourceType=security-group,Tags=[{{Key=Name,Value=marabet-lb-sg}},{{Key=Project,Value=MaraBet-AI}}]"'
    lb_sg_result = run_aws_command(lb_sg_command)
    
    if lb_sg_result and 'GroupId' in lb_sg_result:
        lb_sg_id = lb_sg_result['GroupId']
        config['sg_lb_id'] = lb_sg_id
        print(f"✅ Security Group Load Balancer criado: {lb_sg_id}")
    else:
        print("❌ Falha ao criar Security Group Load Balancer")
        return False
    
    # Adicionar regras ao Security Group Load Balancer
    print("\n📋 Adicionando regras ao Security Group Load Balancer...")
    
    lb_rules = [
        (80, "HTTP", "0.0.0.0/0"),
        (443, "HTTPS", "0.0.0.0/0"),
        (8000, "MaraBet App", "0.0.0.0/0")
    ]
    
    for port, description, cidr in lb_rules:
        rule_command = f'aws ec2 authorize-security-group-ingress --group-id {lb_sg_id} --protocol tcp --port {port} --cidr {cidr}'
        rule_result = run_aws_command(rule_command)
        
        if rule_result is not None:
            print(f"✅ Regra adicionada: {description} (porta {port})")
        else:
            print(f"❌ Falha ao adicionar regra: {description} (porta {port})")
    
    # Adicionar regra para Load Balancer acessar EC2
    lb_to_ec2_command = f'aws ec2 authorize-security-group-ingress --group-id {ec2_sg_id} --protocol tcp --port 8000 --source-group {lb_sg_id}'
    lb_to_ec2_result = run_aws_command(lb_to_ec2_command)
    
    if lb_to_ec2_result is not None:
        print("✅ Regra adicionada: Load Balancer → EC2 (porta 8000)")
    else:
        print("❌ Falha ao adicionar regra: Load Balancer → EC2")
    
    print("\n📊 ETAPA 5: SALVANDO CONFIGURAÇÕES ATUALIZADAS")
    print("-" * 50)
    
    # Salvar configurações atualizadas
    config['updated_at'] = datetime.now().isoformat()
    config['total_security_groups'] = 6
    
    with open('aws_infrastructure_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configurações atualizadas salvas em: aws_infrastructure_config.json")
    
    print("\n🎉 SECURITY GROUPS CRIADOS COM SUCESSO!")
    print("=" * 60)
    
    print("\n📋 SECURITY GROUPS CRIADOS:")
    print("-" * 40)
    print(f"• EC2 Security Group: {config['sg_ec2_id']}")
    print(f"• RDS Security Group: {config['sg_rds_id']}")
    print(f"• ElastiCache Security Group: {config['sg_cache_id']}")
    print(f"• Load Balancer Security Group: {config['sg_lb_id']}")
    print(f"• Web Security Group: {config['sg_web_id']}")
    print(f"• Database Security Group: {config['sg_db_id']}")
    
    print("\n🔒 REGRAS CONFIGURADAS:")
    print("-" * 40)
    print("• EC2: SSH(22), HTTP(80), HTTPS(443), App(8000), Dev(3000), Alt(8080)")
    print("• RDS: PostgreSQL(5432), MySQL(3306), Redis(6379), Memcached(11211)")
    print("• ElastiCache: Redis(6379), Memcached(11211)")
    print("• Load Balancer: HTTP(80), HTTPS(443), App(8000)")
    print("• Web: SSH(22), HTTP(80), HTTPS(443), App(8000)")
    print("• Database: PostgreSQL(5432), Redis(6379)")
    
    print("\n🌐 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ Security Groups criados")
    print("2. ✅ Regras de segurança configuradas")
    print("3. 🔄 Criar instâncias EC2")
    print("4. 🔄 Configurar RDS")
    print("5. 🔄 Configurar ElastiCache")
    print("6. 🔄 Configurar Load Balancer")
    print("7. 🔄 Deploy da aplicação")
    
    print("\n💡 COMANDOS ÚTEIS:")
    print("-" * 40)
    print(f"# Ver todos os Security Groups")
    print(f"aws ec2 describe-security-groups --filters \"Name=vpc-id,Values={vpc_id}\"")
    print()
    print(f"# Ver regras do EC2 Security Group")
    print(f"aws ec2 describe-security-groups --group-ids {config['sg_ec2_id']}")
    print()
    print(f"# Ver regras do RDS Security Group")
    print(f"aws ec2 describe-security-groups --group-ids {config['sg_rds_id']}")
    
    return True

def main():
    print("🚀 Iniciando criação de Security Groups adicionais...")
    
    # Verificar se AWS CLI está configurado
    check_command = "aws sts get-caller-identity"
    check_result = run_aws_command(check_command)
    
    if not check_result:
        print("❌ AWS CLI não configurado ou credenciais inválidas")
        print("💡 Execute: aws configure")
        return False
    
    print("✅ AWS CLI configurado e funcionando")
    
    # Criar Security Groups adicionais
    success = create_additional_security_groups()
    
    if success:
        print("\n🎯 SECURITY GROUPS ADICIONAIS CRIADOS COM SUCESSO!")
        print("A infraestrutura MaraBet AI está mais segura e organizada!")
    else:
        print("\n❌ Falha na criação dos Security Groups adicionais")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
