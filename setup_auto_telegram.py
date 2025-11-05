#!/usr/bin/env python3
"""
Configuração do Sistema Automático de Telegram
MaraBet AI - Setup do sistema automático de predições
"""

import json
import os
import sys
import requests
from datetime import datetime

class AutoTelegramSetup:
    """Configurador do sistema automático"""
    
    def __init__(self):
        self.config_file = 'auto_telegram_config.json'
        self.telegram_config_file = 'telegram_config.json'
    
    def check_telegram_config(self):
        """Verifica se o Telegram já está configurado"""
        if os.path.exists(self.telegram_config_file):
            try:
                with open(self.telegram_config_file, 'r') as f:
                    config = json.load(f)
                    if config.get('telegram_bot_token') and config.get('telegram_chat_id'):
                        print("✅ Configuração do Telegram encontrada")
                        return True
            except:
                pass
        
        print("❌ Configuração do Telegram não encontrada")
        return False
    
    def setup_telegram_if_needed(self):
        """Configura o Telegram se necessário"""
        if not self.check_telegram_config():
            print("\n🔧 CONFIGURANDO TELEGRAM...")
            print("=" * 50)
            
            # Importar e executar setup do Telegram
            try:
                from setup_telegram_bot import TelegramBotSetup
                setup = TelegramBotSetup()
                return setup.run_setup()
            except ImportError:
                print("❌ Arquivo setup_telegram_bot.py não encontrado")
                return False
            except Exception as e:
                print(f"❌ Erro ao configurar Telegram: {e}")
                return False
        
        return True
    
    def create_auto_config(self):
        """Cria configuração do sistema automático"""
        config = {
            'check_interval_hours': 6,
            'days_ahead': 7,
            'max_predictions': 5,
            'max_sends_per_day': 3,
            'enabled': True,
            'created_at': datetime.now().isoformat(),
            'last_check': None,
            'total_sends': 0
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Configuração automática criada: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar configuração: {e}")
            return False
    
    def test_telegram_connection(self):
        """Testa conexão com o Telegram"""
        try:
            with open(self.telegram_config_file, 'r') as f:
                config = json.load(f)
            
            bot_token = config['telegram_bot_token']
            chat_id = config['telegram_chat_id']
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': '🤖 Teste do Sistema Automático MaraBet AI!\n\nSe você recebeu esta mensagem, o sistema automático está configurado corretamente!',
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print("✅ Teste de conexão bem-sucedido!")
                return True
            else:
                print(f"❌ Erro no teste: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False
    
    def create_startup_script(self):
        """Cria script de inicialização"""
        script_content = '''#!/usr/bin/env python3
"""
Script de Inicialização do Sistema Automático
MaraBet AI - Inicia o sistema automático de predições
"""

import sys
import os

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auto_telegram_predictions import AutoTelegramPredictions

if __name__ == "__main__":
    print("🚀 INICIANDO SISTEMA AUTOMÁTICO MARABET AI")
    print("=" * 50)
    
    auto_system = AutoTelegramPredictions()
    auto_system.start_automation()
'''
        
        try:
            with open('start_auto_predictions.py', 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            print("✅ Script de inicialização criado: start_auto_predictions.py")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar script: {e}")
            return False
    
    def create_batch_file(self):
        """Cria arquivo .bat para Windows"""
        batch_content = '''@echo off
echo Iniciando Sistema Automático MaraBet AI...
python start_auto_predictions.py
pause
'''
        
        try:
            with open('start_auto_predictions.bat', 'w') as f:
                f.write(batch_content)
            
            print("✅ Arquivo .bat criado: start_auto_predictions.bat")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar arquivo .bat: {e}")
            return False
    
    def show_instructions(self):
        """Mostra instruções de uso"""
        print("\n🎯 INSTRUÇÕES DE USO:")
        print("=" * 50)
        print("1. O sistema verificará partidas futuras a cada 6 horas")
        print("2. Enviará até 5 predições por vez")
        print("3. Máximo de 3 envios por dia")
        print("4. Usa dados reais da API Football")
        print("5. Foca apenas em partidas futuras")
        
        print("\n🚀 COMO INICIAR:")
        print("=" * 50)
        print("Opção 1 - Python:")
        print("   python start_auto_predictions.py")
        print()
        print("Opção 2 - Windows:")
        print("   Clique duplo em start_auto_predictions.bat")
        print()
        print("Opção 3 - Direto:")
        print("   python auto_telegram_predictions.py")
        
        print("\n⚙️ CONFIGURAÇÕES:")
        print("=" * 50)
        print("• Verificação: A cada 6 horas")
        print("• Período: Próximos 7 dias")
        print("• Predições: Máximo 5 por envio")
        print("• Envios: Máximo 3 por dia")
        print("• Dados: Reais da API Football")
        
        print("\n📊 MONITORAMENTO:")
        print("=" * 50)
        print("• Logs detalhados no console")
        print("• Controle de envios diários")
        print("• Verificação de partidas novas")
        print("• Análise de forma dos times")
    
    def run_setup(self):
        """Executa configuração completa"""
        print("🤖 CONFIGURAÇÃO DO SISTEMA AUTOMÁTICO - MARABET AI")
        print("=" * 80)
        
        # 1. Configurar Telegram se necessário
        if not self.setup_telegram_if_needed():
            print("❌ Falha na configuração do Telegram")
            return False
        
        # 2. Testar conexão
        print("\n🧪 TESTANDO CONEXÃO...")
        if not self.test_telegram_connection():
            print("❌ Falha no teste de conexão")
            return False
        
        # 3. Criar configuração automática
        print("\n⚙️ CRIANDO CONFIGURAÇÃO AUTOMÁTICA...")
        if not self.create_auto_config():
            return False
        
        # 4. Criar scripts de inicialização
        print("\n📝 CRIANDO SCRIPTS DE INICIALIZAÇÃO...")
        self.create_startup_script()
        self.create_batch_file()
        
        # 5. Mostrar instruções
        self.show_instructions()
        
        print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        print("✅ Telegram configurado")
        print("✅ Conexão testada")
        print("✅ Configuração automática criada")
        print("✅ Scripts de inicialização criados")
        print("✅ Sistema pronto para uso")
        
        return True

def main():
    """Função principal"""
    setup = AutoTelegramSetup()
    return setup.run_setup()

if __name__ == "__main__":
    main()
