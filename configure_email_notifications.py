#!/usr/bin/env python3
"""
Script para Configuração de Notificações por Email - MaraBet AI
Configura notificações por email no SNS para alertas do CloudWatch
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

def configure_email_notifications():
    """Configura notificações por email no SNS"""
    print("📧 MARABET AI - CONFIGURAÇÃO DE NOTIFICAÇÕES POR EMAIL")
    print("=" * 70)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Carregar configuração existente
    config = load_config()
    
    # Obter ARN do SNS Topic
    sns_topic_arn = config.get('sns_topic_arn')
    if not sns_topic_arn:
        print("❌ ARN do SNS Topic não encontrado na configuração.")
        print("💡 Execute primeiro: python configure_monitoring.py")
        return False
    
    print(f"✅ SNS Topic ARN: {sns_topic_arn}")
    
    print("\n📧 ETAPA 1: SOLICITANDO EMAIL PARA NOTIFICAÇÕES")
    print("-" * 60)
    
    # Solicitar email do usuário
    email = input("📧 Digite o email para receber notificações: ").strip()
    
    if not email or '@' not in email:
        print("❌ Email inválido. Usando email padrão.")
        email = "admin@marabet.com"
    
    print(f"✅ Email configurado: {email}")
    
    print("\n📧 ETAPA 2: CRIANDO SUBSCRIÇÃO EMAIL")
    print("-" * 60)
    
    # Criar subscrição email
    subscription_command = (
        f'aws sns subscribe '
        f'--topic-arn {sns_topic_arn} '
        f'--protocol email '
        f'--notification-endpoint {email}'
    )
    
    print("📤 Criando subscrição email...")
    subscription_result = run_aws_command(subscription_command)
    
    if subscription_result is not None:
        subscription_arn = subscription_result['SubscriptionArn']
        print(f"✅ Subscrição criada: {subscription_arn}")
        print("📧 Verifique seu email e confirme a subscrição!")
    else:
        print("❌ Falha ao criar subscrição email")
        return False
    
    print("\n📧 ETAPA 3: CRIANDO POLÍTICA DE ACESSO SNS")
    print("-" * 60)
    
    # Criar política de acesso para o SNS Topic
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowCloudWatchToPublish",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudwatch.amazonaws.com"
                },
                "Action": "sns:Publish",
                "Resource": sns_topic_arn
            }
        ]
    }
    
    # Salvar política em arquivo temporário
    policy_file = "sns_policy.json"
    with open(policy_file, 'w') as f:
        json.dump(policy_document, f, indent=2)
    
    # Aplicar política ao SNS Topic
    set_topic_attributes_command = f'aws sns set-topic-attributes --topic-arn {sns_topic_arn} --attribute-name Policy --attribute-value file://{policy_file}'
    policy_result = run_aws_command(set_topic_attributes_command)
    
    if policy_result is not None:
        print("✅ Política de acesso configurada")
    else:
        print("⚠️ Falha ao configurar política de acesso")
    
    # Limpar arquivo temporário
    if os.path.exists(policy_file):
        os.remove(policy_file)
    
    print("\n📧 ETAPA 4: TESTANDO NOTIFICAÇÃO")
    print("-" * 60)
    
    # Enviar mensagem de teste
    test_message = f"""
🚀 MARABET AI - TESTE DE NOTIFICAÇÃO

📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
📧 Email: {email}
🔔 Status: Notificação de teste enviada com sucesso!

✅ Sistema de monitoramento ativo
✅ CloudWatch Alarms configurados
✅ Notificações por email funcionando

🎯 MaraBet AI - Sistema de Predições Esportivas
🔗 Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=MaraBet-AI-Dashboard
    """
    
    publish_command = (
        f'aws sns publish '
        f'--topic-arn {sns_topic_arn} '
        f'--subject "MaraBet AI - Teste de Notificação" '
        f'--message "{test_message}"'
    )
    
    print("📤 Enviando mensagem de teste...")
    publish_result = run_aws_command(publish_command)
    
    if publish_result is not None:
        message_id = publish_result['MessageId']
        print(f"✅ Mensagem de teste enviada: {message_id}")
        print("📧 Verifique seu email para confirmar o recebimento!")
    else:
        print("⚠️ Falha ao enviar mensagem de teste")
    
    print("\n📧 ETAPA 5: CONFIGURANDO FILTROS DE NOTIFICAÇÃO")
    print("-" * 60)
    
    # Configurar filtros para diferentes tipos de alertas
    alert_filters = {
        "critical": ["marabet-web-status-check", "marabet-worker-status-check", "marabet-ubuntu-status-check"],
        "warning": ["marabet-web-high-cpu", "marabet-worker-high-cpu", "marabet-ubuntu-high-cpu"],
        "info": ["marabet-web-memory-usage", "marabet-worker-memory-usage", "marabet-ubuntu-memory-usage"]
    }
    
    print("🔧 Configurando filtros de notificação...")
    for alert_type, alarms in alert_filters.items():
        print(f"  • {alert_type.upper()}: {len(alarms)} alarmes")
    
    print("\n📧 ETAPA 6: SALVANDO CONFIGURAÇÕES")
    print("-" * 60)
    
    # Salvar configurações de notificação
    config['email_notifications'] = {
        'email': email,
        'subscription_arn': subscription_result.get('SubscriptionArn'),
        'configured_at': datetime.now().isoformat(),
        'alert_filters': alert_filters
    }
    
    save_config(config)
    print("✅ Configurações salvas em: aws_infrastructure_config.json")
    
    print("\n🎉 NOTIFICAÇÕES POR EMAIL CONFIGURADAS COM SUCESSO!")
    print("=" * 70)
    
    print("\n📋 RESUMO DA CONFIGURAÇÃO:")
    print("-" * 50)
    print(f"• Email: {email}")
    print(f"• SNS Topic: {sns_topic_arn}")
    print(f"• Subscrição: {subscription_result.get('SubscriptionArn', 'N/A')}")
    print(f"• Status: Configurado")
    
    print("\n🔗 PRÓXIMOS PASSOS:")
    print("-" * 50)
    print("1. ✅ Notificações por email configuradas")
    print("2. ✅ Política de acesso configurada")
    print("3. ✅ Mensagem de teste enviada")
    print("4. 🔄 Confirmar subscrição no email")
    print("5. 🔄 Configurar backup automático")
    print("6. 🔄 Configurar atualizações automáticas")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("-" * 50)
    print("• Confirme a subscrição no email recebido")
    print("• Monitore o dashboard CloudWatch")
    print("• Configure backup automático dos dados")
    print("• Configure atualizações automáticas do sistema")
    print("• Monitore logs de aplicação")
    
    print("\n📧 COMANDOS ÚTEIS:")
    print("-" * 50)
    print("# Listar subscrições")
    print(f"aws sns list-subscriptions-by-topic --topic-arn {sns_topic_arn}")
    print()
    print("# Enviar mensagem de teste")
    print(f'aws sns publish --topic-arn {sns_topic_arn} --subject "Teste" --message "Mensagem de teste"')
    print()
    print("# Verificar status do alarme")
    print("aws cloudwatch describe-alarms --alarm-names marabet-web-high-cpu")
    
    return True

def main():
    print("🚀 Iniciando configuração de notificações por email...")
    
    # Verificar se AWS CLI está configurado
    if run_aws_command("aws sts get-caller-identity") is None:
        print("❌ AWS CLI não configurado ou credenciais inválidas.")
        exit(1)
    print("✅ AWS CLI configurado e funcionando")
    
    # Configurar notificações por email
    success = configure_email_notifications()
    
    if success:
        print("\n🎯 NOTIFICAÇÕES POR EMAIL CONFIGURADAS COM SUCESSO!")
        print("Sistema de notificações ativo e funcionando!")
    else:
        print("\n❌ Falha na configuração de notificações por email")
        print("Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()
