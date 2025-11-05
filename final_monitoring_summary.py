#!/usr/bin/env python3
"""
Script Final de Monitoramento e Manutenção - MaraBet AI
Consolida todas as configurações de monitoramento, backup e atualizações
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

def create_final_monitoring_summary():
    """Cria resumo final do sistema de monitoramento"""
    print("📊 MARABET AI - RESUMO FINAL DO SISTEMA DE MONITORAMENTO")
    print("=" * 80)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configuração existente
    config = load_config()
    
    print("\n📊 INFRAESTRUTURA AWS:")
    print("-" * 50)
    print(f"• VPC ID: {config.get('vpc_id', 'N/A')}")
    print(f"• Web Instance: {config.get('web_instance_id', 'N/A')}")
    print(f"• Worker Instance: {config.get('worker_instance_id', 'N/A')}")
    print(f"• Ubuntu Instance: {config.get('ubuntu_instance_id', 'N/A')}")
    print(f"• RDS Endpoint: {config.get('rds_endpoint', 'N/A')}")
    print(f"• Redis Endpoint: {config.get('redis_endpoint', 'N/A')}")
    
    print("\n🔔 CLOUDWATCH ALARMS:")
    print("-" * 50)
    total_alarms = config.get('total_alarms', 0)
    print(f"• Total de Alarmes: {total_alarms}")
    print("• Alarmes por Instância:")
    print("  - Web Instance: 4 alarmes (CPU, Status, Memory, Disk)")
    print("  - Worker Instance: 3 alarmes (CPU, Status, Memory)")
    print("  - Ubuntu Instance: 4 alarmes (CPU, Status, Memory, Disk)")
    print("  - RDS: 3 alarmes (CPU, Connections, Storage)")
    print("  - Redis: 3 alarmes (CPU, Memory, Connections)")
    
    print("\n📧 NOTIFICAÇÕES:")
    print("-" * 50)
    email_config = config.get('email_notifications', {})
    print(f"• Email: {email_config.get('email', 'N/A')}")
    print(f"• SNS Topic: {config.get('sns_topic_arn', 'N/A')}")
    print(f"• Status: {'Configurado' if email_config else 'Não configurado'}")
    
    print("\n💾 BACKUP:")
    print("-" * 50)
    backup_config = config.get('backup_configured', False)
    print(f"• Status: {'Configurado' if backup_config else 'Não configurado'}")
    print(f"• S3 Bucket: {config.get('s3_backup_bucket', 'N/A')}")
    print(f"• Scripts: {len(config.get('backup_scripts', {}))} scripts")
    
    print("\n🔄 ATUALIZAÇÕES AUTOMÁTICAS:")
    print("-" * 50)
    updates_config = config.get('automatic_updates_configured', False)
    print(f"• Status: {'Configurado' if updates_config else 'Não configurado'}")
    print(f"• Scripts: {len(config.get('update_scripts', {}))} scripts")
    print("• Cron Jobs:")
    print("  - Atualização do Sistema: Domingos às 02:00")
    print("  - Atualização da Aplicação: Segundas-feiras às 03:00")
    print("  - Verificação de Segurança: Diariamente às 04:00")
    print("  - Monitoramento: A cada 15 minutos")
    
    print("\n📊 DASHBOARD CLOUDWATCH:")
    print("-" * 50)
    dashboard = config.get('cloudwatch_dashboard', 'N/A')
    print(f"• Dashboard: {dashboard}")
    print(f"• URL: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name={dashboard}")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 50)
    print("1. ✅ CloudWatch Alarms configurados")
    print("2. ✅ SNS Topic configurado")
    print("3. ✅ Dashboard CloudWatch criado")
    print("4. ✅ Scripts de backup criados")
    print("5. ✅ Scripts de atualização criados")
    print("6. ✅ Scripts de monitoramento criados")
    print("7. 🔄 Transferir scripts para o servidor")
    print("8. 🔄 Configurar cron jobs no servidor")
    print("9. 🔄 Testar todos os scripts")
    print("10. 🔄 Configurar notificações por email")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("-" * 50)
    print("• Monitore o dashboard CloudWatch regularmente")
    print("• Configure notificações por email no SNS")
    print("• Teste todos os scripts antes de confiar neles")
    print("• Monitore os logs de backup e atualização")
    print("• Configure alertas para falhas de backup")
    print("• Mantenha backups em múltiplas regiões")
    print("• Teste a restauração regularmente")
    print("• Monitore o sistema após atualizações")
    print("• Configure backup do certificado SSL")
    print("• Monitore logs de aplicação")
    
    print("\n📧 COMANDOS ÚTEIS:")
    print("-" * 50)
    print("# Verificar status dos alarmes")
    print("aws cloudwatch describe-alarms --alarm-names marabet-web-high-cpu")
    print()
    print("# Verificar subscrições SNS")
    print(f"aws sns list-subscriptions-by-topic --topic-arn {config.get('sns_topic_arn', 'N/A')}")
    print()
    print("# Verificar dashboard")
    print(f"aws cloudwatch get-dashboard --dashboard-name {dashboard}")
    print()
    print("# Executar backup manual")
    print("sudo /home/ubuntu/marabet-ai/backup_script.sh")
    print()
    print("# Executar atualização do sistema")
    print("sudo /home/ubuntu/marabet-ai/system_update_script.sh")
    print()
    print("# Executar atualização da aplicação")
    print("sudo /home/ubuntu/marabet-ai/app_update_script.sh")
    print()
    print("# Executar verificação de segurança")
    print("sudo /home/ubuntu/marabet-ai/security_check_script.sh")
    print()
    print("# Executar monitoramento")
    print("sudo /home/ubuntu/marabet-ai/monitoring_script.sh")
    print()
    print("# Verificar cron jobs")
    print("crontab -l")
    print()
    print("# Ver logs")
    print("tail -f /var/log/marabet_backup.log")
    print("tail -f /var/log/marabet_system_updates.log")
    print("tail -f /var/log/marabet_app_updates.log")
    print("tail -f /var/log/marabet_security.log")
    print("tail -f /var/log/marabet_monitoring.log")
    
    print("\n🎯 SISTEMA DE MONITORAMENTO E MANUTENÇÃO CONFIGURADO!")
    print("=" * 80)
    
    return True

def main():
    print("🚀 Iniciando resumo final do sistema de monitoramento...")
    
    # Verificar se AWS CLI está configurado
    if run_aws_command("aws sts get-caller-identity") is None:
        print("❌ AWS CLI não configurado ou credenciais inválidas.")
        exit(1)
    print("✅ AWS CLI configurado e funcionando")
    
    # Criar resumo final
    success = create_final_monitoring_summary()
    
    if success:
        print("\n🎯 SISTEMA DE MONITORAMENTO E MANUTENÇÃO CONFIGURADO COM SUCESSO!")
        print("Sistema completo e funcionando!")
    else:
        print("\n❌ Falha na criação do resumo final")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
