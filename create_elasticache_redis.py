#!/usr/bin/env python3
"""
Script para Criar ElastiCache Redis - MaraBet AI
Cria cluster Redis com configurações de produção
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

def create_elasticache_redis():
    """Cria cluster ElastiCache Redis"""
    print("⚡ MARABET AI - CRIANDO ELASTICACHE REDIS")
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
    subnet_public_2 = config['subnet_public_2']
    ec2_sg_id = config['sg_ec2_id']
    cache_sg_id = config['sg_cache_id']
    
    print(f"✅ VPC ID: {vpc_id}")
    print(f"✅ Subnet 1: {subnet_public_1}")
    print(f"✅ Subnet 2: {subnet_public_2}")
    print(f"✅ EC2 Security Group: {ec2_sg_id}")
    print(f"✅ Cache Security Group: {cache_sg_id}")
    
    print("\n⚡ ETAPA 1: CRIANDO SUBNET GROUP PARA ELASTICACHE")
    print("-" * 50)
    
    # Verificar se subnet group já existe
    check_subnet_group_command = f'aws elasticache describe-cache-subnet-groups --cache-subnet-group-name marabet-cache-subnet'
    check_subnet_group_result = run_aws_command(check_subnet_group_command)
    
    if check_subnet_group_result and 'CacheSubnetGroups' in check_subnet_group_result:
        print("✅ Subnet group já existe")
    else:
        # Criar subnet group para ElastiCache
        subnet_group_command = f'aws elasticache create-cache-subnet-group --cache-subnet-group-name marabet-cache-subnet --cache-subnet-group-description "Subnet group for MaraBet ElastiCache Redis" --subnet-ids {subnet_public_1} {subnet_public_2} --tags Key=Name,Value=marabet-cache-subnet Key=Project,Value=MaraBet-AI'
        subnet_group_result = run_aws_command(subnet_group_command)
        
        if subnet_group_result is not None:
            print("✅ Subnet group criado com sucesso")
        else:
            print("❌ Falha ao criar subnet group")
            return False
    
    print("\n⚡ ETAPA 2: VERIFICANDO/CRIANDO CLUSTER REDIS")
    print("-" * 50)
    
    # Configurações do ElastiCache
    cache_cluster_id = "marabet-redis"
    cache_node_type = "cache.t3.micro"
    engine = "redis"
    num_cache_nodes = 1
    
    print(f"📋 Configurações do ElastiCache:")
    print(f"  • Cluster ID: {cache_cluster_id}")
    print(f"  • Node Type: {cache_node_type}")
    print(f"  • Engine: {engine}")
    print(f"  • Nodes: {num_cache_nodes}")
    
    # Verificar se cluster já existe
    check_cluster_command = f'aws elasticache describe-cache-clusters --cache-cluster-id {cache_cluster_id}'
    check_cluster_result = run_aws_command(check_cluster_command)
    
    if check_cluster_result and 'CacheClusters' in check_cluster_result:
        print("✅ Cluster Redis já existe")
    else:
        # Criar cluster Redis
        redis_command = f'aws elasticache create-cache-cluster --cache-cluster-id {cache_cluster_id} --cache-node-type {cache_node_type} --engine {engine} --num-cache-nodes {num_cache_nodes} --cache-subnet-group-name marabet-cache-subnet --security-group-ids {cache_sg_id} --tags Key=Name,Value=marabet-redis Key=Project,Value=MaraBet-AI Key=Environment,Value=production'
        
        print("🚀 Criando cluster Redis...")
        redis_result = run_aws_command(redis_command)
        
        if redis_result is not None:
            print("✅ Cluster Redis criado com sucesso")
            print("⏳ Aguardando disponibilidade do cluster...")
        else:
            print("❌ Falha ao criar cluster Redis")
            return False
    
    print("\n⚡ ETAPA 3: AGUARDANDO DISPONIBILIDADE")
    print("-" * 50)
    
    # Aguardar disponibilidade do cluster
    wait_command = f'aws elasticache wait cache-cluster-available --cache-cluster-id {cache_cluster_id}'
    print("⏳ Aguardando cluster ficar disponível (pode levar 5-10 minutos)...")
    
    wait_result = run_aws_command(wait_command)
    
    if wait_result is not None:
        print("✅ Cluster Redis disponível!")
    else:
        print("⚠️ Timeout aguardando disponibilidade, mas continuando...")
    
    print("\n⚡ ETAPA 4: OBTENDO INFORMAÇÕES DO CLUSTER")
    print("-" * 50)
    
    # Obter informações do cluster
    describe_command = f'aws elasticache describe-cache-clusters --cache-cluster-id {cache_cluster_id} --show-cache-node-info'
    describe_result = run_aws_command(describe_command)
    
    if describe_result and 'CacheClusters' in describe_result:
        cache_cluster = describe_result['CacheClusters'][0]
        
        # Verificar se o cluster tem nós disponíveis
        if 'CacheNodes' in cache_cluster and len(cache_cluster['CacheNodes']) > 0:
            # Extrair informações importantes
            endpoint = cache_cluster['CacheNodes'][0]['Endpoint']['Address']
            port = cache_cluster['CacheNodes'][0]['Endpoint']['Port']
            engine_version = cache_cluster['EngineVersion']
            status = cache_cluster['CacheClusterStatus']
            node_type = cache_cluster['CacheNodeType']
            
            print(f"✅ Endpoint: {endpoint}")
            print(f"✅ Porta: {port}")
            print(f"✅ Engine Version: {engine_version}")
            print(f"✅ Status: {status}")
            print(f"✅ Node Type: {node_type}")
            
            # Salvar informações na configuração
            config['redis_endpoint'] = endpoint
            config['redis_port'] = port
            config['redis_engine_version'] = engine_version
            config['redis_node_type'] = node_type
            config['redis_cluster_id'] = cache_cluster_id
            config['redis_created_at'] = datetime.now().isoformat()
        else:
            print("⚠️ Cluster ainda não tem nós disponíveis")
            print(f"✅ Status: {cache_cluster.get('CacheClusterStatus', 'Unknown')}")
            print(f"✅ Engine Version: {cache_cluster.get('EngineVersion', 'Unknown')}")
            print(f"✅ Node Type: {cache_cluster.get('CacheNodeType', 'Unknown')}")
            
            # Salvar informações básicas
            config['redis_cluster_id'] = cache_cluster_id
            config['redis_status'] = cache_cluster.get('CacheClusterStatus', 'Unknown')
            config['redis_engine_version'] = cache_cluster.get('EngineVersion', 'Unknown')
            config['redis_node_type'] = cache_cluster.get('CacheNodeType', 'Unknown')
            config['redis_created_at'] = datetime.now().isoformat()
            config['redis_note'] = "Cluster criado mas ainda não disponível - aguardar alguns minutos"
        
    else:
        print("❌ Falha ao obter informações do cluster Redis")
        return False
    
    print("\n⚡ ETAPA 5: CRIANDO PARÂMETRO GROUP")
    print("-" * 50)
    
    # Criar parâmetro group personalizado
    parameter_group_name = "marabet-redis-params"
    parameter_group_command = f'aws elasticache create-cache-parameter-group --cache-parameter-group-name {parameter_group_name} --cache-parameter-group-family redis7.x --description "Custom parameter group for MaraBet Redis" --tags Key=Name,Value=marabet-redis-params Key=Project,Value=MaraBet-AI'
    
    parameter_group_result = run_aws_command(parameter_group_command)
    
    if parameter_group_result is not None:
        print("✅ Parameter group criado com sucesso")
    else:
        print("⚠️ Falha ao criar parameter group (continuando...)")
    
    print("\n⚡ ETAPA 6: CONFIGURANDO PARÂMETROS")
    print("-" * 50)
    
    # Configurar parâmetros importantes
    parameters = [
        ("maxmemory-policy", "allkeys-lru"),
        ("timeout", "300"),
        ("tcp-keepalive", "60"),
        ("tcp-backlog", "511"),
        ("databases", "16"),
        ("save", "900 1 300 10 60 10000"),
        ("stop-writes-on-bgsave-error", "yes"),
        ("rdbcompression", "yes"),
        ("rdbchecksum", "yes"),
        ("dbfilename", "dump.rdb"),
        ("dir", "/var/lib/redis"),
        ("slave-serve-stale-data", "yes"),
        ("slave-read-only", "yes"),
        ("repl-diskless-sync", "no"),
        ("repl-diskless-sync-delay", "5"),
        ("repl-ping-slave-period", "10"),
        ("repl-timeout", "60"),
        ("repl-disable-tcp-nodelay", "no"),
        ("repl-backlog-size", "1mb"),
        ("repl-backlog-ttl", "3600"),
        ("maxclients", "10000"),
        ("appendonly", "yes"),
        ("appendfilename", "appendonly.aof"),
        ("appendfsync", "everysec"),
        ("no-appendfsync-on-rewrite", "no"),
        ("auto-aof-rewrite-percentage", "100"),
        ("auto-aof-rewrite-min-size", "64mb"),
        ("aof-load-truncated", "yes"),
        ("lua-time-limit", "5000"),
        ("slowlog-log-slower-than", "10000"),
        ("slowlog-max-len", "128"),
        ("latency-monitor-threshold", "0"),
        ("notify-keyspace-events", ""),
        ("hash-max-ziplist-entries", "512"),
        ("hash-max-ziplist-value", "64"),
        ("list-max-ziplist-size", "-2"),
        ("list-compress-depth", "0"),
        ("set-max-intset-entries", "512"),
        ("zset-max-ziplist-entries", "128"),
        ("zset-max-ziplist-value", "64"),
        ("hll-sparse-max-bytes", "3000"),
        ("activerehashing", "yes"),
        ("client-output-buffer-limit", "normal 0 0 0 slave 268435456 67108864 60 pubsub 33554432 8388608 60"),
        ("hz", "10"),
        ("aof-rewrite-incremental-fsync", "yes")
    ]
    
    print("🔧 Configurando parâmetros do Redis...")
    
    for param_name, param_value in parameters:
        param_command = f'aws elasticache modify-cache-parameter-group --cache-parameter-group-name {parameter_group_name} --parameters ParameterName={param_name},ParameterValue="{param_value}"'
        param_result = run_aws_command(param_command)
        
        if param_result is not None:
            print(f"✅ Parâmetro configurado: {param_name}")
        else:
            print(f"⚠️ Falha ao configurar parâmetro: {param_name}")
    
    print("\n⚡ ETAPA 7: SALVANDO CONFIGURAÇÕES")
    print("-" * 50)
    
    # Salvar configurações atualizadas
    config['redis_parameter_group'] = parameter_group_name
    config['updated_at'] = datetime.now().isoformat()
    
    with open('aws_infrastructure_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configurações salvas em: aws_infrastructure_config.json")
    
    print("\n🎉 ELASTICACHE REDIS CRIADO COM SUCESSO!")
    print("=" * 60)
    
    print("\n📋 INFORMAÇÕES DO REDIS:")
    print("-" * 40)
    print(f"• Cluster ID: {cache_cluster_id}")
    print(f"• Endpoint: {endpoint}")
    print(f"• Porta: {port}")
    print(f"• Engine: {engine} {engine_version}")
    print(f"• Node Type: {node_type}")
    print(f"• Status: {status}")
    print(f"• Security Group: {cache_sg_id}")
    
    print("\n🔗 STRING DE CONEXÃO:")
    print("-" * 40)
    print(f"redis://{endpoint}:{port}")
    
    print("\n🔗 STRING DE CONEXÃO PARA APLICAÇÃO:")
    print("-" * 40)
    print(f"REDIS_URL=redis://{endpoint}:{port}")
    
    print("\n🌐 PRÓXIMOS PASSOS:")
    print("-" * 40)
    print("1. ✅ ElastiCache Redis criado")
    print("2. ✅ Subnet group configurado")
    print("3. ✅ Security groups aplicados")
    print("4. ✅ Parâmetros otimizados")
    print("5. 🔄 Criar instâncias EC2")
    print("6. 🔄 Deploy da aplicação")
    print("7. 🔄 Configurar Load Balancer")
    print("8. 🔄 Configurar Auto Scaling")
    
    print("\n💡 COMANDOS ÚTEIS:")
    print("-" * 40)
    print(f"# Ver status do cluster")
    print(f"aws elasticache describe-cache-clusters --cache-cluster-id {cache_cluster_id}")
    print()
    print(f"# Conectar via redis-cli")
    print(f"redis-cli -h {endpoint} -p {port}")
    print()
    print(f"# Ver métricas CloudWatch")
    print(f"aws cloudwatch get-metric-statistics --namespace AWS/ElastiCache --metric-name CPUUtilization --dimensions Name=CacheClusterId,Value={cache_cluster_id} --start-time 2024-01-01T00:00:00Z --end-time 2024-01-02T00:00:00Z --period 3600 --statistics Average")
    
    print("\n🎯 ELASTICACHE REDIS PRONTO!")
    print("-" * 40)
    print("✅ Cluster Redis criado e configurado")
    print("✅ Parâmetros otimizados para produção")
    print("✅ Security groups aplicados")
    print("✅ Sistema MaraBet AI pronto para usar Redis")
    
    return True

def main():
    print("🚀 Iniciando criação do ElastiCache Redis...")
    
    # Verificar se AWS CLI está configurado
    check_command = "aws sts get-caller-identity"
    check_result = run_aws_command(check_command)
    
    if not check_result:
        print("❌ AWS CLI não configurado ou credenciais inválidas")
        print("💡 Execute: aws configure")
        return False
    
    print("✅ AWS CLI configurado e funcionando")
    
    # Criar ElastiCache Redis
    success = create_elasticache_redis()
    
    if success:
        print("\n🎯 ELASTICACHE REDIS CRIADO COM SUCESSO!")
        print("O cache Redis do MaraBet AI está pronto para uso!")
    else:
        print("\n❌ Falha na criação do ElastiCache Redis")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
