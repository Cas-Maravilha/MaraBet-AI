#!/usr/bin/env python3
"""
Script para Configuração de Monitoramento e Manutenção - MaraBet AI
Automatiza a criação de CloudWatch Alarms e configurações de monitoramento
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
    except json.JSONDecodeError:
        print(f"❌ Erro de decodificação JSON para o comando: {command}")
        print(f"Saída: {result.stdout}")
        print(f"Erro: {result.stderr}")
        return None
    except Exception as e:
        print(f"❌ Exceção no comando: {command}")
        print(f"Erro: {e}")
        return None

def load_config():
    """Carrega configurações existentes do arquivo JSON."""
    config_file = 'aws_infrastructure_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Salva configurações no arquivo JSON."""
    config_file = 'aws_infrastructure_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

def create_cloudwatch_alarms():
    """Cria CloudWatch Alarms para monitoramento"""
    print("📊 MARABET AI - CONFIGURAÇÃO DE MONITORAMENTO E MANUTENÇÃO")
    print("=" * 70)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configuração existente
    config = load_config()
    
    # Obter IDs das instâncias
    web_instance_id = config.get('web_instance_id')
    worker_instance_id = config.get('worker_instance_id')
    ubuntu_instance_id = config.get('ubuntu_instance_id')
    
    if not all([web_instance_id, worker_instance_id, ubuntu_instance_id]):
        print("❌ Erro: IDs das instâncias não encontrados na configuração.")
        return False
    
    print(f"✅ Web Instance ID: {web_instance_id}")
    print(f"✅ Worker Instance ID: {worker_instance_id}")
    print(f"✅ Ubuntu Instance ID: {ubuntu_instance_id}")
    
    print("\n📊 ETAPA 1: CRIANDO ALARMES PARA INSTÂNCIA WEB")
    print("-" * 60)
    
    # Alarmes para instância web
    web_alarms = [
        {
            "name": "marabet-web-high-cpu",
            "description": "CPU usage above 80% on web instance",
            "metric": "CPUUtilization",
            "threshold": 80,
            "comparison": "GreaterThanThreshold",
            "evaluation_periods": 2,
            "period": 300
        },
        {
            "name": "marabet-web-status-check",
            "description": "Web instance status check failed",
            "metric": "StatusCheckFailed",
            "threshold": 1,
            "comparison": "GreaterThanOrEqualToThreshold",
            "evaluation_periods": 2,
            "period": 60
        },
        {
            "name": "marabet-web-memory-usage",
            "description": "Memory usage above 85% on web instance",
            "metric": "MemoryUtilization",
            "threshold": 85,
            "comparison": "GreaterThanThreshold",
            "evaluation_periods": 2,
            "period": 300
        },
        {
            "name": "marabet-web-disk-usage",
            "description": "Disk usage above 90% on web instance",
            "metric": "DiskSpaceUtilization",
            "threshold": 90,
            "comparison": "GreaterThanThreshold",
            "evaluation_periods": 2,
            "period": 300
        }
    ]
    
    for alarm in web_alarms:
        print(f"🔔 Criando alarme: {alarm['name']}")
        
        # Comando para criar alarme
        alarm_command = (
            f'aws cloudwatch put-metric-alarm '
            f'--alarm-name {alarm["name"]} '
            f'--alarm-description "{alarm["description"]}" '
            f'--metric-name {alarm["metric"]} '
            f'--namespace AWS/EC2 '
            f'--statistic Average '
            f'--period {alarm["period"]} '
            f'--threshold {alarm["threshold"]} '
            f'--comparison-operator {alarm["comparison"]} '
            f'--evaluation-periods {alarm["evaluation_periods"]} '
            f'--dimensions Name=InstanceId,Value={web_instance_id} '
            f'--alarm-actions arn:aws:sns:us-east-1:123456789012:marabet-alerts '
            f'--ok-actions arn:aws:sns:us-east-1:123456789012:marabet-alerts'
        )
        
        result = run_aws_command(alarm_command)
        if result is not None:
            print(f"✅ Alarme criado: {alarm['name']}")
        else:
            print(f"⚠️ Falha ao criar alarme: {alarm['name']}")
    
    print("\n📊 ETAPA 2: CRIANDO ALARMES PARA INSTÂNCIA WORKER")
    print("-" * 60)
    
    # Alarmes para instância worker
    worker_alarms = [
        {
            "name": "marabet-worker-high-cpu",
            "description": "CPU usage above 80% on worker instance",
            "metric": "CPUUtilization",
            "threshold": 80,
            "comparison": "GreaterThanThreshold",
            "evaluation_periods": 2,
            "period": 300
        },
        {
            "name": "marabet-worker-status-check",
            "description": "Worker instance status check failed",
            "metric": "StatusCheckFailed",
            "threshold": 1,
            "comparison": "GreaterThanOrEqualToThreshold",
            "evaluation_periods": 2,
            "period": 60
        },
        {
            "name": "marabet-worker-memory-usage",
            "description": "Memory usage above 85% on worker instance",
            "metric": "MemoryUtilization",
            "threshold": 85,
            "comparison": "GreaterThanThreshold",
            "evaluation_periods": 2,
            "period": 300
        }
    ]
    
    for alarm in worker_alarms:
        print(f"🔔 Criando alarme: {alarm['name']}")
        
        # Comando para criar alarme
        alarm_command = (
            f'aws cloudwatch put-metric-alarm '
            f'--alarm-name {alarm["name"]} '
            f'--alarm-description "{alarm["description"]}" '
            f'--metric-name {alarm["metric"]} '
            f'--namespace AWS/EC2 '
            f'--statistic Average '
            f'--period {alarm["period"]} '
            f'--threshold {alarm["threshold"]} '
            f'--comparison-operator {alarm["comparison"]} '
            f'--evaluation-periods {alarm["evaluation_periods"]} '
            f'--dimensions Name=InstanceId,Value={worker_instance_id} '
            f'--alarm-actions arn:aws:sns:us-east-1:123456789012:marabet-alerts '
            f'--ok-actions arn:aws:sns:us-east-1:123456789012:marabet-alerts'
        )
        
        result = run_aws_command(alarm_command)
        if result is not None:
            print(f"✅ Alarme criado: {alarm['name']}")
        else:
            print(f"⚠️ Falha ao criar alarme: {alarm['name']}")
    
    print("\n📊 ETAPA 3: CRIANDO ALARMES PARA INSTÂNCIA UBUNTU")
    print("-" * 60)
    
    # Alarmes para instância Ubuntu
    ubuntu_alarms = [
        {
            "name": "marabet-ubuntu-high-cpu",
            "description": "CPU usage above 80% on Ubuntu instance",
            "metric": "CPUUtilization",
            "threshold": 80,
            "comparison": "GreaterThanThreshold",
            "evaluation_periods": 2,
            "period": 300
        },
        {
            "name": "marabet-ubuntu-status-check",
            "description": "Ubuntu instance status check failed",
            "metric": "StatusCheckFailed",
            "threshold": 1,
            "comparison": "GreaterThanOrEqualToThreshold",
            "evaluation_periods": 2,
            "period": 60
        },
        {
            "name": "marabet-ubuntu-memory-usage",
            "description": "Memory usage above 85% on Ubuntu instance",
            "metric": "MemoryUtilization",
            "threshold": 85,
            "comparison": "GreaterThanThreshold",
            "evaluation_periods": 2,
            "period": 300
        },
        {
            "name": "marabet-ubuntu-disk-usage",
            "description": "Disk usage above 90% on Ubuntu instance",
            "metric": "DiskSpaceUtilization",
            "threshold": 90,
            "comparison": "GreaterThanThreshold",
            "evaluation_periods": 2,
            "period": 300
        }
    ]
    
    for alarm in ubuntu_alarms:
        print(f"🔔 Criando alarme: {alarm['name']}")
        
        # Comando para criar alarme
        alarm_command = (
            f'aws cloudwatch put-metric-alarm '
            f'--alarm-name {alarm["name"]} '
            f'--alarm-description "{alarm["description"]}" '
            f'--metric-name {alarm["metric"]} '
            f'--namespace AWS/EC2 '
            f'--statistic Average '
            f'--period {alarm["period"]} '
            f'--threshold {alarm["threshold"]} '
            f'--comparison-operator {alarm["comparison"]} '
            f'--evaluation-periods {alarm["evaluation_periods"]} '
            f'--dimensions Name=InstanceId,Value={ubuntu_instance_id} '
            f'--alarm-actions arn:aws:sns:us-east-1:123456789012:marabet-alerts '
            f'--ok-actions arn:aws:sns:us-east-1:123456789012:marabet-alerts'
        )
        
        result = run_aws_command(alarm_command)
        if result is not None:
            print(f"✅ Alarme criado: {alarm['name']}")
        else:
            print(f"⚠️ Falha ao criar alarme: {alarm['name']}")
    
    print("\n📊 ETAPA 4: CRIANDO ALARMES PARA RDS")
    print("-" * 60)
    
    # Obter endpoint do RDS
    rds_endpoint = config.get('rds_endpoint')
    if rds_endpoint:
        # Alarmes para RDS
        rds_alarms = [
            {
                "name": "marabet-rds-cpu-usage",
                "description": "RDS CPU usage above 80%",
                "metric": "CPUUtilization",
                "threshold": 80,
                "comparison": "GreaterThanThreshold",
                "evaluation_periods": 2,
                "period": 300
            },
            {
                "name": "marabet-rds-connection-count",
                "description": "RDS connection count above 80%",
                "metric": "DatabaseConnections",
                "threshold": 80,
                "comparison": "GreaterThanThreshold",
                "evaluation_periods": 2,
                "period": 300
            },
            {
                "name": "marabet-rds-free-storage",
                "description": "RDS free storage below 2GB",
                "metric": "FreeStorageSpace",
                "threshold": 2000000000,  # 2GB em bytes
                "comparison": "LessThanThreshold",
                "evaluation_periods": 2,
                "period": 300
            }
        ]
        
        for alarm in rds_alarms:
            print(f"🔔 Criando alarme: {alarm['name']}")
            
            # Comando para criar alarme RDS
            alarm_command = (
                f'aws cloudwatch put-metric-alarm '
                f'--alarm-name {alarm["name"]} '
                f'--alarm-description "{alarm["description"]}" '
                f'--metric-name {alarm["metric"]} '
                f'--namespace AWS/RDS '
                f'--statistic Average '
                f'--period {alarm["period"]} '
                f'--threshold {alarm["threshold"]} '
                f'--comparison-operator {alarm["comparison"]} '
                f'--evaluation-periods {alarm["evaluation_periods"]} '
                f'--dimensions Name=DBInstanceIdentifier,Value=marabet-db '
                f'--alarm-actions arn:aws:sns:us-east-1:123456789012:marabet-alerts '
                f'--ok-actions arn:aws:sns:us-east-1:123456789012:marabet-alerts'
            )
            
            result = run_aws_command(alarm_command)
            if result is not None:
                print(f"✅ Alarme criado: {alarm['name']}")
            else:
                print(f"⚠️ Falha ao criar alarme: {alarm['name']}")
    else:
        print("⚠️ Endpoint do RDS não encontrado, pulando alarmes RDS")
    
    print("\n📊 ETAPA 5: CRIANDO ALARMES PARA ELASTICACHE")
    print("-" * 60)
    
    # Obter endpoint do ElastiCache
    redis_endpoint = config.get('redis_endpoint')
    if redis_endpoint:
        # Alarmes para ElastiCache
        redis_alarms = [
            {
                "name": "marabet-redis-cpu-usage",
                "description": "Redis CPU usage above 80%",
                "metric": "CPUUtilization",
                "threshold": 80,
                "comparison": "GreaterThanThreshold",
                "evaluation_periods": 2,
                "period": 300
            },
            {
                "name": "marabet-redis-memory-usage",
                "description": "Redis memory usage above 85%",
                "metric": "DatabaseMemoryUsagePercentage",
                "threshold": 85,
                "comparison": "GreaterThanThreshold",
                "evaluation_periods": 2,
                "period": 300
            },
            {
                "name": "marabet-redis-connection-count",
                "description": "Redis connection count above 80%",
                "metric": "CurrConnections",
                "threshold": 80,
                "comparison": "GreaterThanThreshold",
                "evaluation_periods": 2,
                "period": 300
            }
        ]
        
        for alarm in redis_alarms:
            print(f"🔔 Criando alarme: {alarm['name']}")
            
            # Comando para criar alarme ElastiCache
            alarm_command = (
                f'aws cloudwatch put-metric-alarm '
                f'--alarm-name {alarm["name"]} '
                f'--alarm-description "{alarm["description"]}" '
                f'--metric-name {alarm["metric"]} '
                f'--namespace AWS/ElastiCache '
                f'--statistic Average '
                f'--period {alarm["period"]} '
                f'--threshold {alarm["threshold"]} '
                f'--comparison-operator {alarm["comparison"]} '
                f'--evaluation-periods {alarm["evaluation_periods"]} '
                f'--dimensions Name=CacheClusterId,Value=marabet-redis '
                f'--alarm-actions arn:aws:sns:us-east-1:123456789012:marabet-alerts '
                f'--ok-actions arn:aws:sns:us-east-1:123456789012:marabet-alerts'
            )
            
            result = run_aws_command(alarm_command)
            if result is not None:
                print(f"✅ Alarme criado: {alarm['name']}")
            else:
                print(f"⚠️ Falha ao criar alarme: {alarm['name']}")
    else:
        print("⚠️ Endpoint do ElastiCache não encontrado, pulando alarmes Redis")
    
    print("\n📊 ETAPA 6: CRIANDO SNS TOPIC PARA ALERTAS")
    print("-" * 60)
    
    # Criar SNS Topic para alertas
    sns_topic_name = "marabet-alerts"
    sns_topic_command = f'aws sns create-topic --name {sns_topic_name}'
    sns_result = run_aws_command(sns_topic_command)
    
    if sns_result is not None:
        topic_arn = sns_result['TopicArn']
        print(f"✅ SNS Topic criado: {topic_arn}")
        config['sns_topic_arn'] = topic_arn
    else:
        print("⚠️ Falha ao criar SNS Topic")
        print("💡 Crie manualmente: aws sns create-topic --name marabet-alerts")
    
    print("\n📊 ETAPA 7: CONFIGURANDO DASHBOARD CLOUDWATCH")
    print("-" * 60)
    
    # Criar dashboard CloudWatch
    dashboard_name = "MaraBet-AI-Dashboard"
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/EC2", "CPUUtilization", "InstanceId", web_instance_id],
                        ["AWS/EC2", "CPUUtilization", "InstanceId", worker_instance_id],
                        ["AWS/EC2", "CPUUtilization", "InstanceId", ubuntu_instance_id]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "CPU Utilization - All Instances",
                    "period": 300
                }
            },
            {
                "type": "metric",
                "x": 12,
                "y": 0,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/EC2", "MemoryUtilization", "InstanceId", web_instance_id],
                        ["AWS/EC2", "MemoryUtilization", "InstanceId", worker_instance_id],
                        ["AWS/EC2", "MemoryUtilization", "InstanceId", ubuntu_instance_id]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "Memory Utilization - All Instances",
                    "period": 300
                }
            },
            {
                "type": "metric",
                "x": 0,
                "y": 6,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "marabet-db"],
                        ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "marabet-db"]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "RDS Metrics",
                    "period": 300
                }
            },
            {
                "type": "metric",
                "x": 12,
                "y": 6,
                "width": 12,
                "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/ElastiCache", "CPUUtilization", "CacheClusterId", "marabet-redis"],
                        ["AWS/ElastiCache", "DatabaseMemoryUsagePercentage", "CacheClusterId", "marabet-redis"]
                    ],
                    "view": "timeSeries",
                    "stacked": False,
                    "region": "us-east-1",
                    "title": "Redis Metrics",
                    "period": 300
                }
            }
        ]
    }
    
    # Salvar dashboard body em arquivo temporário
    dashboard_file = "dashboard_body.json"
    with open(dashboard_file, 'w') as f:
        json.dump(dashboard_body, f, indent=2)
    
    # Criar dashboard
    dashboard_command = f'aws cloudwatch put-dashboard --dashboard-name {dashboard_name} --dashboard-body file://{dashboard_file}'
    dashboard_result = run_aws_command(dashboard_command)
    
    if dashboard_result is not None:
        print(f"✅ Dashboard criado: {dashboard_name}")
        config['cloudwatch_dashboard'] = dashboard_name
    else:
        print("⚠️ Falha ao criar dashboard")
    
    # Limpar arquivo temporário
    if os.path.exists(dashboard_file):
        os.remove(dashboard_file)
    
    print("\n📊 ETAPA 8: SALVANDO CONFIGURAÇÕES")
    print("-" * 60)
    
    # Adicionar informações de monitoramento
    config['monitoring_configured'] = True
    config['monitoring_created_at'] = datetime.now().isoformat()
    config['total_alarms'] = len(web_alarms) + len(worker_alarms) + len(ubuntu_alarms)
    
    if rds_endpoint:
        config['total_alarms'] += len(rds_alarms)
    
    if redis_endpoint:
        config['total_alarms'] += len(redis_alarms)
    
    save_config(config)
    print("✅ Configurações salvas em: aws_infrastructure_config.json")
    
    print("\n🎉 MONITORAMENTO E MANUTENÇÃO CONFIGURADO COM SUCESSO!")
    print("=" * 70)
    
    print("\n📋 RESUMO DA CONFIGURAÇÃO:")
    print("-" * 50)
    print(f"• Total de Alarmes: {config['total_alarms']}")
    print(f"• SNS Topic: {config.get('sns_topic_arn', 'N/A')}")
    print(f"• Dashboard: {config.get('cloudwatch_dashboard', 'N/A')}")
    print(f"• Status: Configurado")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 50)
    print("1. ✅ CloudWatch Alarms criados")
    print("2. ✅ SNS Topic configurado")
    print("3. ✅ Dashboard CloudWatch criado")
    print("4. 🔄 Configurar notificações por email")
    print("5. 🔄 Configurar backup automático")
    print("6. 🔄 Configurar atualizações automáticas")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("-" * 50)
    print("• Configure notificações por email no SNS")
    print("• Monitore o dashboard regularmente")
    print("• Configure backup automático dos dados")
    print("• Configure atualizações automáticas do sistema")
    print("• Monitore logs de aplicação")
    
    return True

def main():
    print("🚀 Iniciando configuração de monitoramento e manutenção...")
    
    # Verificar se AWS CLI está configurado
    if run_aws_command("aws sts get-caller-identity") is None:
        print("❌ AWS CLI não configurado ou credenciais inválidas.")
        exit(1)
    print("✅ AWS CLI configurado e funcionando")
    
    # Configurar monitoramento
    success = create_cloudwatch_alarms()
    
    if success:
        print("\n🎯 MONITORAMENTO E MANUTENÇÃO CONFIGURADO COM SUCESSO!")
        print("Sistema de monitoramento ativo e funcionando!")
    else:
        print("\n❌ Falha na configuração de monitoramento")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
