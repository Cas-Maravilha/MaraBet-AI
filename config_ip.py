#!/usr/bin/env python3
"""
MaraBet AI - Configuração de IP
Configura o IP do sistema para acesso às APIs
"""

import os
import json
from datetime import datetime

# IP do sistema
SYSTEM_IP = "102.206.57.108"

def update_env_file():
    """Atualiza arquivo .env com o IP"""
    print("📝 Atualizando arquivo .env...")
    
    env_files = [
        'config_personal.env',
        'config_production.env',
        '.env'
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Atualizar ou adicionar linha SYSTEM_IP
            found = False
            for i, line in enumerate(lines):
                if line.startswith('SYSTEM_IP='):
                    lines[i] = f'SYSTEM_IP={SYSTEM_IP}\n'
                    found = True
                    break
            
            if not found:
                lines.append(f'\n# IP do Sistema\nSYSTEM_IP={SYSTEM_IP}\n')
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"  ✅ {env_file} atualizado")

def create_ip_config_json():
    """Cria arquivo JSON com configuração de IP"""
    print("\n📋 Criando ip_config.json...")
    
    config = {
        "system_ip": SYSTEM_IP,
        "configured_at": datetime.now().isoformat(),
        "api_whitelist": {
            "api_football": {
                "ip_required": True,
                "current_ip": SYSTEM_IP,
                "dashboard_url": "https://dashboard.api-football.com/",
                "instructions": "Adicionar este IP na seção 'IP Whitelist' do dashboard"
            },
            "football_data_org": {
                "ip_required": False,
                "note": "Esta API não requer whitelist de IP"
            }
        },
        "server_config": {
            "location": "Angola",
            "provider": "Local/Angoweb",
            "environment": "development"
        }
    }
    
    with open('ip_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("  ✅ ip_config.json criado")

def create_ip_instructions():
    """Cria arquivo de instruções para whitelist"""
    print("\n📄 Criando instruções de whitelist...")
    
    instructions = f"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║  🔐 CONFIGURAÇÃO DE IP - MARABET AI                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

📍 SEU IP: {SYSTEM_IP}

═══════════════════════════════════════════════════════════════
 ADICIONAR IP NA API-FOOTBALL (URGENTE)
═══════════════════════════════════════════════════════════════

1. Acessar Dashboard:
   🌐 https://dashboard.api-football.com/

2. Fazer Login:
   📧 Email: [seu email de cadastro]
   🔑 Senha: [sua senha]

3. Ir para IP Whitelist:
   Procurar no menu: "IP Whitelist" ou "Allowed IPs"

4. Adicionar IP:
   Clicar em: "Add IP" ou "+ New IP"
   
   Preencher:
   ┌─────────────────────────────────────────┐
   │ IP Address: {SYSTEM_IP}                 │
   │ Description: MaraBet AI - Development   │
   │ Status: Active                          │
   └─────────────────────────────────────────┘

5. Salvar:
   Clicar em "Save" ou "Add"

6. Aguardar:
   ⏱️ 1-2 minutos para propagação

7. Testar:
   python test_api_ultra_plan.py

═══════════════════════════════════════════════════════════════
 STATUS DAS APIs
═══════════════════════════════════════════════════════════════

API-Football (api-sports.io)
├─ Status: 🔴 BLOQUEADA (necessita adicionar IP)
├─ IP Atual: {SYSTEM_IP}
├─ Ação: Adicionar na whitelist
└─ Dashboard: https://dashboard.api-football.com/

football-data.org
├─ Status: ✅ FUNCIONANDO
├─ IP: Sem restrição
└─ Nenhuma ação necessária

═══════════════════════════════════════════════════════════════
 APÓS ADICIONAR IP
═══════════════════════════════════════════════════════════════

✅ API-Football funcionará 100%
✅ Plano Ultra totalmente ativo
✅ Acesso a:
   • Jogos ao vivo
   • Odds de +200 bookmakers
   • Previsões avançadas
   • Estatísticas completas
   • Alta taxa de requisições

═══════════════════════════════════════════════════════════════
 PARA PRODUÇÃO (ANGOWEB)
═══════════════════════════════════════════════════════════════

Quando receber o servidor Angoweb, você receberá um novo IP.
Será necessário adicionar TAMBÉM esse novo IP no dashboard.

Exemplo: 197.149.XX.XX (IP fornecido pela Angoweb)

═══════════════════════════════════════════════════════════════
 SUPORTE
═══════════════════════════════════════════════════════════════

MaraBet AI:
📧 Suporte: suporte@marabet.ao
📧 Técnico: dpo@marabet.ao
📞 WhatsApp: +224 932027393

API-Football:
🌐 Dashboard: https://dashboard.api-football.com/
📧 Support: support@api-football.com

═══════════════════════════════════════════════════════════════

IP CONFIGURADO: {SYSTEM_IP}
DATA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

═══════════════════════════════════════════════════════════════
"""
    
    with open('IP_WHITELIST_INSTRUCTIONS.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("  ✅ IP_WHITELIST_INSTRUCTIONS.txt criado")

def update_readme():
    """Atualiza README com informação do IP"""
    print("\n📚 Atualizando referências no projeto...")
    
    # Criar nota sobre IP
    note = f"""
## 🌐 CONFIGURAÇÃO DE IP

**IP do Sistema**: `{SYSTEM_IP}`  
**Configurado em**: {datetime.now().strftime('%d/%m/%Y')}

### API-Football Whitelist

⚠️ **IMPORTANTE**: Adicionar este IP no dashboard da API-Football para acesso completo.

**Passos:**
1. Acesse: https://dashboard.api-football.com/
2. Login com suas credenciais
3. Vá para "IP Whitelist"
4. Adicione o IP: `{SYSTEM_IP}`
5. Descrição: "MaraBet AI - Development"
6. Salve e aguarde 1-2 minutos

**Teste após adicionar:**
```bash
python test_api_ultra_plan.py
```

Ver instruções completas: `IP_WHITELIST_INSTRUCTIONS.txt`
"""
    
    with open('IP_CONFIG_NOTE.md', 'w', encoding='utf-8') as f:
        f.write(note)
    
    print("  ✅ IP_CONFIG_NOTE.md criado")

def create_test_script():
    """Cria script de teste de IP"""
    print("\n🧪 Criando script de teste...")
    
    script = f'''#!/usr/bin/env python3
"""
MaraBet AI - Teste de IP e APIs
Verifica se o IP está configurado corretamente
"""

import requests
import json

SYSTEM_IP = "{SYSTEM_IP}"
API_FOOTBALL_KEY = "71b2b62386f2d1275cd3201a73e1e045"

def test_current_ip():
    """Verifica IP atual"""
    print("\\n" + "="*60)
    print("📍 VERIFICANDO IP ATUAL")
    print("="*60)
    
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        current_ip = response.json()['ip']
        
        print(f"\\nIP Configurado: {{SYSTEM_IP}}")
        print(f"IP Detectado:   {{current_ip}}")
        
        if current_ip == SYSTEM_IP:
            print("\\n✅ IP CORRETO!")
        else:
            print(f"\\n⚠️  ATENÇÃO: IP diferente!")
            print(f"   Usar {{current_ip}} na whitelist")
        
        return current_ip
    except Exception as e:
        print(f"\\n❌ Erro ao verificar IP: {{e}}")
        return None

def test_api_football():
    """Testa API-Football"""
    print("\\n" + "="*60)
    print("🔵 TESTANDO API-FOOTBALL")
    print("="*60)
    
    try:
        headers = {{'x-apisports-key': API_FOOTBALL_KEY}}
        response = requests.get(
            'https://v3.football.api-sports.io/status',
            headers=headers,
            timeout=10
        )
        
        print(f"\\nStatus Code: {{response.status_code}}")
        
        if response.status_code == 200:
            data = response.json()
            print("\\n✅ API-FOOTBALL: OK")
            print(f"   Requests Remaining: {{data.get('response', {{}}).get('requests', {{}}).get('current', 'N/A')}}")
        else:
            print(f"\\n❌ API-FOOTBALL: ERRO")
            print(f"   Resposta: {{response.text}}")
            
            if "IP" in response.text or "not allowed" in response.text.lower():
                print("\\n⚠️  PROBLEMA DE IP WHITELIST!")
                print("   Ação: Adicionar IP na dashboard")
                print("   URL: https://dashboard.api-football.com/")
        
        return response.status_code == 200
    except Exception as e:
        print(f"\\n❌ Erro: {{e}}")
        return False

def test_football_data_org():
    """Testa football-data.org"""
    print("\\n" + "="*60)
    print("🟢 TESTANDO FOOTBALL-DATA.ORG")
    print("="*60)
    
    try:
        headers = {{'X-Auth-Token': '721b0aaec5794327bab715da2abc7a7b'}}
        response = requests.get(
            'https://api.football-data.org/v4/competitions/',
            headers=headers,
            timeout=10
        )
        
        print(f"\\nStatus Code: {{response.status_code}}")
        
        if response.status_code == 200:
            data = response.json()
            print("\\n✅ FOOTBALL-DATA.ORG: OK")
            comps = len(data.get('competitions', []))
            print(f"   Competições: {{comps}}")
        else:
            print(f"\\n❌ FOOTBALL-DATA.ORG: ERRO")
            print(f"   Resposta: {{response.text}}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"\\n❌ Erro: {{e}}")
        return False

def main():
    print("\\n" + "="*60)
    print("🔍 MARABET AI - TESTE DE CONFIGURAÇÃO DE IP")
    print("="*60)
    
    current_ip = test_current_ip()
    api_football_ok = test_api_football()
    football_data_ok = test_football_data_org()
    
    print("\\n" + "="*60)
    print("📊 RESUMO")
    print("="*60)
    
    print(f"\\nIP Configurado: {{SYSTEM_IP}}")
    if current_ip:
        print(f"IP Detectado:   {{current_ip}}")
    
    print(f"\\nAPI-Football:       {{'✅ OK' if api_football_ok else '❌ BLOQUEADA'}}")
    print(f"football-data.org:  {{'✅ OK' if football_data_ok else '❌ ERRO'}}")
    
    if not api_football_ok:
        print("\\n⚠️  AÇÃO NECESSÁRIA:")
        print("   1. Acessar: https://dashboard.api-football.com/")
        print("   2. Adicionar IP na whitelist")
        print("   3. Testar novamente")
        print("\\n   Ver: IP_WHITELIST_INSTRUCTIONS.txt")
    
    if api_football_ok and football_data_ok:
        print("\\n🎉 TUDO OK! Sistema pronto para usar.")
    
    print("\\n" + "="*60)

if __name__ == "__main__":
    main()
'''
    
    with open('test_ip_config.py', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print("  ✅ test_ip_config.py criado")

def main():
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                                                               ║")
    print("║         CONFIGURAÇÃO DE IP - MARABET AI                       ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print(f"📍 IP a configurar: {SYSTEM_IP}")
    print()
    
    # Executar configurações
    update_env_file()
    create_ip_config_json()
    create_ip_instructions()
    update_readme()
    create_test_script()
    
    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                                                               ║")
    print("║         ✅ CONFIGURAÇÃO DE IP CONCLUÍDA!                      ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print("📁 Arquivos criados:")
    print("   ✅ .env (atualizado)")
    print("   ✅ ip_config.json")
    print("   ✅ IP_WHITELIST_INSTRUCTIONS.txt")
    print("   ✅ IP_CONFIG_NOTE.md")
    print("   ✅ test_ip_config.py")
    print()
    print("🔥 PRÓXIMOS PASSOS:")
    print()
    print("1️⃣  ADICIONAR IP NA API-FOOTBALL:")
    print("    🌐 https://dashboard.api-football.com/")
    print(f"    📍 IP: {SYSTEM_IP}")
    print("    📄 Ver: IP_WHITELIST_INSTRUCTIONS.txt")
    print()
    print("2️⃣  TESTAR CONFIGURAÇÃO:")
    print("    python test_ip_config.py")
    print()
    print("3️⃣  APÓS ADICIONAR IP, TESTAR API:")
    print("    python test_api_ultra_plan.py")
    print()
    print("📧 Suporte: suporte@marabet.ao")
    print("📞 WhatsApp: +224 932027393")
    print()

if __name__ == "__main__":
    main()

