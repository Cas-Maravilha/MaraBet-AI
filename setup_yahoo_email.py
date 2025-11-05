#!/usr/bin/env python3
"""
Script para configurar email do Yahoo no MaraBet AI
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurações do Yahoo
YAHOO_EMAIL = "kilamu_10@yahoo.com.br"
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587

def test_yahoo_connection(password):
    """Testa conexão com o Yahoo"""
    print("📧 MARABET AI - TESTANDO CONEXÃO COM YAHOO")
    print("=" * 50)
    
    print(f"📧 Email: {YAHOO_EMAIL}")
    print(f"🌐 Servidor: {SMTP_SERVER}:{SMTP_PORT}")
    
    try:
        # Criar conexão SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Habilitar TLS
        
        print("🔐 Tentando autenticar...")
        server.login(YAHOO_EMAIL, password)
        print("✅ Autenticação bem-sucedida!")
        
        # Criar mensagem de teste
        msg = MIMEMultipart('alternative')
        msg['From'] = YAHOO_EMAIL
        msg['To'] = YAHOO_EMAIL
        msg['Subject'] = "🎉 Teste de Notificação - MaraBet AI"
        
        # Conteúdo da mensagem
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; border-radius: 8px; }
                .content { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 10px 0; }
                .success { color: #28a745; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🔮 MaraBet AI</h2>
                <h3>Teste de Notificação de Email</h3>
            </div>
            
            <div class="content">
                <p class="success">✅ Configuração de email bem-sucedida!</p>
                <p>Se você recebeu esta mensagem, o sistema de notificações por email está funcionando corretamente.</p>
                
                <h4>📊 Informações do Sistema:</h4>
                <ul>
                    <li><strong>Email:</strong> kilamu_10@yahoo.com.br</li>
                    <li><strong>Servidor:</strong> smtp.mail.yahoo.com</li>
                    <li><strong>Porta:</strong> 587</li>
                    <li><strong>Status:</strong> Configurado e funcionando</li>
                </ul>
                
                <p>🎯 Agora você receberá notificações sobre:</p>
                <ul>
                    <li>🔮 Predições com valor</li>
                    <li>🤖 Status do sistema</li>
                    <li>❌ Alertas de erro</li>
                    <li>📊 Relatórios de performance</li>
                    <li>📈 Relatórios diários</li>
                </ul>
            </div>
            
            <div style="color: #666; font-size: 12px; margin-top: 20px;">
                <p>MaraBet AI - Sistema de Apostas Esportivas Inteligentes</p>
                <p>Este é um email automático, não responda.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = """
        MaraBet AI - Teste de Notificação de Email
        ==========================================
        
        ✅ Configuração de email bem-sucedida!
        
        Se você recebeu esta mensagem, o sistema de notificações por email está funcionando corretamente.
        
        Informações do Sistema:
        - Email: kilamu_10@yahoo.com.br
        - Servidor: smtp.mail.yahoo.com
        - Porta: 587
        - Status: Configurado e funcionando
        
        Agora você receberá notificações sobre:
        - Predições com valor
        - Status do sistema
        - Alertas de erro
        - Relatórios de performance
        - Relatórios diários
        
        MaraBet AI - Sistema de Apostas Esportivas Inteligentes
        Este é um email automático, não responda.
        """
        
        # Adicionar conteúdo
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Enviar email
        print("📤 Enviando email de teste...")
        server.send_message(msg)
        server.quit()
        
        print("✅ Email de teste enviado com sucesso!")
        print("📧 Verifique sua caixa de entrada (e spam)")
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Erro de autenticação!")
        print("💡 Verifique se a senha está correta")
        print("💡 Para Yahoo, use uma senha de app, não sua senha normal")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ Erro SMTP: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def show_yahoo_setup_instructions():
    """Mostra instruções para configurar senha de app do Yahoo"""
    print("\n📋 COMO CONFIGURAR SENHA DE APP DO YAHOO")
    print("=" * 50)
    
    print("1. 🌐 Acesse: https://login.yahoo.com/")
    print("2. 🔐 Faça login na sua conta Yahoo")
    print("3. ⚙️  Vá em 'Account Info' ou 'Gerenciar Conta'")
    print("4. 🔒 Clique em 'Account Security' ou 'Segurança da Conta'")
    print("5. 🔑 Procure por 'App passwords' ou 'Senhas de App'")
    print("6. ➕ Clique em 'Generate app password' ou 'Gerar senha de app'")
    print("7. 📝 Digite um nome (ex: 'MaraBet AI')")
    print("8. 📋 Copie a senha gerada (16 caracteres)")
    print("9. 🔄 Use esta senha no lugar da sua senha normal")
    
    print("\n⚠️  IMPORTANTE:")
    print("- Use a senha de app, NÃO sua senha normal do Yahoo")
    print("- A senha de app tem 16 caracteres")
    print("- Se não encontrar a opção, ative a verificação em duas etapas primeiro")

def main():
    """Função principal"""
    print("🔮 MARABET AI - CONFIGURAÇÃO DE EMAIL YAHOO")
    print("=" * 60)
    
    print(f"📧 Email configurado: {YAHOO_EMAIL}")
    print(f"🌐 Servidor: {SMTP_SERVER}:{SMTP_PORT}")
    
    show_yahoo_setup_instructions()
    
    print(f"\n🔑 Digite sua senha de app do Yahoo (16 caracteres):")
    password = input("Senha: ").strip()
    
    if len(password) != 16:
        print("⚠️  A senha de app do Yahoo deve ter 16 caracteres")
        print("💡 Verifique se você copiou a senha corretamente")
        return
    
    # Testar conexão
    if test_yahoo_connection(password):
        print(f"\n🎉 Configuração de email concluída!")
        print(f"📧 Email: {YAHOO_EMAIL}")
        print(f"🔑 Senha de app: {password[:4]}...{password[-4:]}")
        
        print(f"\n📝 Adicione estas linhas ao seu arquivo .env:")
        print(f"SMTP_SERVER=smtp.mail.yahoo.com")
        print(f"SMTP_PORT=587")
        print(f"SMTP_USERNAME={YAHOO_EMAIL}")
        print(f"SMTP_PASSWORD={password}")
        print(f"NOTIFICATION_EMAIL={YAHOO_EMAIL}")
        print(f"ADMIN_EMAIL={YAHOO_EMAIL}")
        
        print(f"\n🧪 Para testar o sistema completo:")
        print(f"python test_notifications.py")
    else:
        print(f"\n❌ Configuração de email falhou")
        print(f"💡 Verifique as instruções acima e tente novamente")

if __name__ == "__main__":
    main()
