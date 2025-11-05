"""
Hardener de Segurança - MaraBet AI
Sistema completo de hardening de segurança para produção
"""

import os
import json
import logging
import hashlib
import secrets
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import yaml
import psutil
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """Configuração de segurança"""
    enable_firewall: bool = True
    enable_ssl: bool = True
    enable_2fa: bool = True
    enable_audit_logs: bool = True
    enable_intrusion_detection: bool = True
    password_policy: Dict[str, Any] = None
    session_timeout: int = 3600
    max_login_attempts: int = 5
    lockout_duration: int = 900

@dataclass
class SecurityReport:
    """Relatório de segurança"""
    timestamp: datetime
    overall_score: float
    vulnerabilities_found: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    recommendations: List[str]
    compliance_status: Dict[str, bool]

class SecurityHardener:
    """
    Hardener de segurança para MaraBet AI
    Implementa medidas de hardening para produção
    """
    
    def __init__(self, config_file: str = "security/security_config.yaml"):
        """
        Inicializa o hardener de segurança
        
        Args:
            config_file: Arquivo de configuração de segurança
        """
        self.config_file = config_file
        self.config = self._load_security_config()
        self.security_checks = self._initialize_security_checks()
        
        logger.info("SecurityHardener inicializado")
    
    def _load_security_config(self) -> SecurityConfig:
        """Carrega configuração de segurança"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                return SecurityConfig(**data)
            else:
                default_config = SecurityConfig(
                    password_policy={
                        "min_length": 12,
                        "require_uppercase": True,
                        "require_lowercase": True,
                        "require_numbers": True,
                        "require_special_chars": True,
                        "max_age_days": 90,
                        "history_count": 5
                    }
                )
                self._save_security_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configuração: {e}")
            return SecurityConfig()
    
    def _save_security_config(self, config: SecurityConfig):
        """Salva configuração de segurança"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config.__dict__, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar configuração: {e}")
    
    def _initialize_security_checks(self) -> List[Dict[str, Any]]:
        """Inicializa verificações de segurança"""
        return [
            {
                "name": "firewall_status",
                "description": "Verificar status do firewall",
                "critical": True,
                "check_function": self._check_firewall_status
            },
            {
                "name": "ssl_certificates",
                "description": "Verificar certificados SSL",
                "critical": True,
                "check_function": self._check_ssl_certificates
            },
            {
                "name": "password_policy",
                "description": "Verificar política de senhas",
                "critical": True,
                "check_function": self._check_password_policy
            },
            {
                "name": "file_permissions",
                "description": "Verificar permissões de arquivos",
                "critical": True,
                "check_function": self._check_file_permissions
            },
            {
                "name": "database_security",
                "description": "Verificar segurança do banco de dados",
                "critical": True,
                "check_function": self._check_database_security
            },
            {
                "name": "api_security",
                "description": "Verificar segurança da API",
                "critical": True,
                "check_function": self._check_api_security
            },
            {
                "name": "logging_security",
                "description": "Verificar logs de segurança",
                "critical": False,
                "check_function": self._check_logging_security
            },
            {
                "name": "network_security",
                "description": "Verificar configurações de rede",
                "critical": False,
                "check_function": self._check_network_security
            },
            {
                "name": "system_updates",
                "description": "Verificar atualizações do sistema",
                "critical": False,
                "check_function": self._check_system_updates
            },
            {
                "name": "backup_security",
                "description": "Verificar segurança dos backups",
                "critical": False,
                "check_function": self._check_backup_security
            }
        ]
    
    def run_security_audit(self) -> SecurityReport:
        """
        Executa auditoria completa de segurança
        
        Returns:
            Relatório de segurança
        """
        try:
            logger.info("🔍 Iniciando auditoria de segurança...")
            
            vulnerabilities = []
            critical_issues = 0
            high_issues = 0
            medium_issues = 0
            low_issues = 0
            recommendations = []
            compliance_status = {}
            
            # Executar verificações de segurança
            for check in self.security_checks:
                try:
                    result = check["check_function"]()
                    
                    if not result["passed"]:
                        severity = result.get("severity", "medium")
                        vulnerabilities.append({
                            "check": check["name"],
                            "description": check["description"],
                            "severity": severity,
                            "message": result["message"],
                            "recommendation": result.get("recommendation", "")
                        })
                        
                        if severity == "critical":
                            critical_issues += 1
                        elif severity == "high":
                            high_issues += 1
                        elif severity == "medium":
                            medium_issues += 1
                        else:
                            low_issues += 1
                        
                        if result.get("recommendation"):
                            recommendations.append(result["recommendation"])
                    
                    compliance_status[check["name"]] = result["passed"]
                    
                except Exception as e:
                    logger.error(f"❌ Erro na verificação {check['name']}: {e}")
                    vulnerabilities.append({
                        "check": check["name"],
                        "description": check["description"],
                        "severity": "high",
                        "message": f"Erro na verificação: {str(e)}",
                        "recommendation": "Corrigir erro na verificação"
                    })
                    high_issues += 1
                    compliance_status[check["name"]] = False
            
            # Calcular score geral
            total_checks = len(self.security_checks)
            passed_checks = sum(1 for status in compliance_status.values() if status)
            overall_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
            
            # Gerar recomendações adicionais
            recommendations.extend(self._generate_security_recommendations(
                critical_issues, high_issues, medium_issues, low_issues
            ))
            
            report = SecurityReport(
                timestamp=datetime.now(),
                overall_score=overall_score,
                vulnerabilities_found=len(vulnerabilities),
                critical_issues=critical_issues,
                high_issues=high_issues,
                medium_issues=medium_issues,
                low_issues=low_issues,
                recommendations=recommendations,
                compliance_status=compliance_status
            )
            
            # Salvar relatório
            self._save_security_report(report)
            
            logger.info(f"✅ Auditoria concluída - Score: {overall_score:.1f}%")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro na auditoria de segurança: {e}")
            return self._empty_security_report()
    
    def _check_firewall_status(self) -> Dict[str, Any]:
        """Verifica status do firewall"""
        try:
            # Verificar se o firewall está ativo (Windows)
            if os.name == 'nt':
                result = subprocess.run(
                    ['netsh', 'advfirewall', 'show', 'allprofiles', 'state'],
                    capture_output=True, text=True, timeout=30
                )
                
                if "ON" in result.stdout:
                    return {"passed": True, "message": "Firewall ativo"}
                else:
                    return {
                        "passed": False,
                        "severity": "critical",
                        "message": "Firewall desativado",
                        "recommendation": "Ativar firewall do Windows"
                    }
            else:
                # Linux/Unix
                result = subprocess.run(
                    ['ufw', 'status'],
                    capture_output=True, text=True, timeout=30
                )
                
                if "Status: active" in result.stdout:
                    return {"passed": True, "message": "Firewall ativo"}
                else:
                    return {
                        "passed": False,
                        "severity": "critical",
                        "message": "Firewall desativado",
                        "recommendation": "Ativar UFW: sudo ufw enable"
                    }
                    
        except Exception as e:
            return {
                "passed": False,
                "severity": "high",
                "message": f"Erro ao verificar firewall: {str(e)}",
                "recommendation": "Verificar configuração do firewall manualmente"
            }
    
    def _check_ssl_certificates(self) -> Dict[str, Any]:
        """Verifica certificados SSL"""
        try:
            # Verificar se há certificados SSL configurados
            ssl_files = [
                "ssl/cert.pem",
                "ssl/key.pem",
                "ssl/ca.pem",
                "certs/server.crt",
                "certs/server.key"
            ]
            
            ssl_found = False
            for ssl_file in ssl_files:
                if os.path.exists(ssl_file):
                    ssl_found = True
                    break
            
            if ssl_found:
                return {"passed": True, "message": "Certificados SSL encontrados"}
            else:
                return {
                    "passed": False,
                    "severity": "critical",
                    "message": "Certificados SSL não encontrados",
                    "recommendation": "Configurar certificados SSL para HTTPS"
                }
                
        except Exception as e:
            return {
                "passed": False,
                "severity": "high",
                "message": f"Erro ao verificar SSL: {str(e)}",
                "recommendation": "Verificar configuração SSL manualmente"
            }
    
    def _check_password_policy(self) -> Dict[str, Any]:
        """Verifica política de senhas"""
        try:
            policy = self.config.password_policy
            
            if not policy:
                return {
                    "passed": False,
                    "severity": "high",
                    "message": "Política de senhas não configurada",
                    "recommendation": "Configurar política de senhas robusta"
                }
            
            # Verificar requisitos mínimos
            min_length = policy.get("min_length", 8)
            if min_length < 12:
                return {
                    "passed": False,
                    "severity": "medium",
                    "message": f"Comprimento mínimo de senha muito baixo: {min_length}",
                    "recommendation": "Aumentar comprimento mínimo para 12 caracteres"
                }
            
            # Verificar se todos os requisitos estão habilitados
            required_checks = [
                "require_uppercase", "require_lowercase", 
                "require_numbers", "require_special_chars"
            ]
            
            missing_checks = [check for check in required_checks if not policy.get(check, False)]
            
            if missing_checks:
                return {
                    "passed": False,
                    "severity": "medium",
                    "message": f"Requisitos de senha faltando: {', '.join(missing_checks)}",
                    "recommendation": "Habilitar todos os requisitos de complexidade de senha"
                }
            
            return {"passed": True, "message": "Política de senhas adequada"}
            
        except Exception as e:
            return {
                "passed": False,
                "severity": "high",
                "message": f"Erro ao verificar política de senhas: {str(e)}",
                "recommendation": "Verificar configuração da política de senhas"
            }
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """Verifica permissões de arquivos"""
        try:
            critical_files = [
                "config.py",
                "config_personal.env",
                "requirements.txt",
                "docker-compose.yml",
                "Dockerfile"
            ]
            
            insecure_files = []
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    # Verificar se arquivo é legível por outros usuários
                    stat = os.stat(file_path)
                    if stat.st_mode & 0o004:  # Outros podem ler
                        insecure_files.append(file_path)
            
            if insecure_files:
                return {
                    "passed": False,
                    "severity": "high",
                    "message": f"Arquivos com permissões inseguras: {', '.join(insecure_files)}",
                    "recommendation": "Restringir permissões de arquivos sensíveis: chmod 600"
                }
            
            return {"passed": True, "message": "Permissões de arquivos adequadas"}
            
        except Exception as e:
            return {
                "passed": False,
                "severity": "medium",
                "message": f"Erro ao verificar permissões: {str(e)}",
                "recommendation": "Verificar permissões de arquivos manualmente"
            }
    
    def _check_database_security(self) -> Dict[str, Any]:
        """Verifica segurança do banco de dados"""
        try:
            # Verificar se há arquivos de banco expostos
            db_files = [
                "data/marabets.db",
                "data/matches.db",
                "*.db",
                "*.sqlite",
                "*.sqlite3"
            ]
            
            exposed_dbs = []
            for db_pattern in db_files:
                if "*" in db_pattern:
                    import glob
                    files = glob.glob(db_pattern)
                    exposed_dbs.extend(files)
                elif os.path.exists(db_pattern):
                    exposed_dbs.append(db_pattern)
            
            if exposed_dbs:
                return {
                    "passed": False,
                    "severity": "critical",
                    "message": f"Arquivos de banco expostos: {', '.join(exposed_dbs)}",
                    "recommendation": "Mover arquivos de banco para diretório seguro e restrito"
                }
            
            # Verificar se há credenciais hardcoded
            config_files = ["config.py", "app.py", "main.py"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "password" in content.lower() and "=" in content:
                            return {
                                "passed": False,
                                "severity": "high",
                                "message": f"Possíveis credenciais hardcoded em {config_file}",
                                "recommendation": "Usar variáveis de ambiente para credenciais"
                            }
            
            return {"passed": True, "message": "Segurança do banco adequada"}
            
        except Exception as e:
            return {
                "passed": False,
                "severity": "medium",
                "message": f"Erro ao verificar banco: {str(e)}",
                "recommendation": "Verificar configuração do banco manualmente"
            }
    
    def _check_api_security(self) -> Dict[str, Any]:
        """Verifica segurança da API"""
        try:
            # Verificar se há rate limiting configurado
            api_files = ["app.py", "main.py", "dashboard/app.py"]
            rate_limiting_found = False
            
            for api_file in api_files:
                if os.path.exists(api_file):
                    with open(api_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if any(keyword in content.lower() for keyword in 
                               ["rate_limit", "throttle", "limiter"]):
                            rate_limiting_found = True
                            break
            
            if not rate_limiting_found:
                return {
                    "passed": False,
                    "severity": "medium",
                    "message": "Rate limiting não configurado na API",
                    "recommendation": "Implementar rate limiting para prevenir ataques"
                }
            
            # Verificar se há CORS configurado adequadamente
            cors_configured = False
            for api_file in api_files:
                if os.path.exists(api_file):
                    with open(api_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "cors" in content.lower() and "origins" in content.lower():
                            cors_configured = True
                            break
            
            if not cors_configured:
                return {
                    "passed": False,
                    "severity": "medium",
                    "message": "CORS não configurado adequadamente",
                    "recommendation": "Configurar CORS com origens específicas"
                }
            
            return {"passed": True, "message": "Segurança da API adequada"}
            
        except Exception as e:
            return {
                "passed": False,
                "severity": "medium",
                "message": f"Erro ao verificar API: {str(e)}",
                "recommendation": "Verificar configuração da API manualmente"
            }
    
    def _check_logging_security(self) -> Dict[str, Any]:
        """Verifica logs de segurança"""
        try:
            # Verificar se há logs de auditoria
            log_files = [
                "logs/security.log",
                "logs/audit.log",
                "logs/access.log",
                "marabet.log"
            ]
            
            log_found = False
            for log_file in log_files:
                if os.path.exists(log_file):
                    log_found = True
                    break
            
            if not log_found:
                return {
                    "passed": False,
                    "severity": "low",
                    "message": "Logs de segurança não encontrados",
                    "recommendation": "Implementar logging de segurança e auditoria"
                }
            
            return {"passed": True, "message": "Logs de segurança configurados"}
            
        except Exception as e:
            return {
                "passed": False,
                "severity": "low",
                "message": f"Erro ao verificar logs: {str(e)}",
                "recommendation": "Verificar configuração de logs manualmente"
            }
    
    def _check_network_security(self) -> Dict[str, Any]:
        """Verifica configurações de rede"""
        try:
            # Verificar se há portas abertas desnecessárias
            import socket
            
            dangerous_ports = [21, 23, 135, 139, 445, 1433, 3389]
            open_dangerous_ports = []
            
            for port in dangerous_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    open_dangerous_ports.append(port)
            
            if open_dangerous_ports:
                return {
                    "passed": False,
                    "severity": "high",
                    "message": f"Portas perigosas abertas: {open_dangerous_ports}",
                    "recommendation": "Fechar portas desnecessárias e configurar firewall"
                }
            
            return {"passed": True, "message": "Configurações de rede adequadas"}
            
        except Exception as e:
            return {
                "passed": False,
                "severity": "medium",
                "message": f"Erro ao verificar rede: {str(e)}",
                "recommendation": "Verificar configurações de rede manualmente"
            }
    
    def _check_system_updates(self) -> Dict[str, Any]:
        """Verifica atualizações do sistema"""
        try:
            # Verificar se há atualizações pendentes (Windows)
            if os.name == 'nt':
                result = subprocess.run(
                    ['powershell', '-Command', 'Get-WindowsUpdate'],
                    capture_output=True, text=True, timeout=30
                )
                
                if "No updates available" in result.stdout:
                    return {"passed": True, "message": "Sistema atualizado"}
                else:
                    return {
                        "passed": False,
                        "severity": "medium",
                        "message": "Atualizações do sistema pendentes",
                        "recommendation": "Instalar atualizações de segurança do Windows"
                    }
            else:
                # Linux/Unix
                result = subprocess.run(
                    ['apt', 'list', '--upgradable'],
                    capture_output=True, text=True, timeout=30
                )
                
                if "upgradable" in result.stdout and result.stdout.strip():
                    return {
                        "passed": False,
                        "severity": "medium",
                        "message": "Atualizações do sistema pendentes",
                        "recommendation": "Executar: sudo apt update && sudo apt upgrade"
                    }
                else:
                    return {"passed": True, "message": "Sistema atualizado"}
                    
        except Exception as e:
            return {
                "passed": False,
                "severity": "low",
                "message": f"Erro ao verificar atualizações: {str(e)}",
                "recommendation": "Verificar atualizações manualmente"
            }
    
    def _check_backup_security(self) -> Dict[str, Any]:
        """Verifica segurança dos backups"""
        try:
            # Verificar se há backups configurados
            backup_dirs = [
                "backups/",
                "data/backups/",
                "storage/backups/"
            ]
            
            backup_found = False
            for backup_dir in backup_dirs:
                if os.path.exists(backup_dir) and os.listdir(backup_dir):
                    backup_found = True
                    break
            
            if not backup_found:
                return {
                    "passed": False,
                    "severity": "high",
                    "message": "Backups não encontrados",
                    "recommendation": "Implementar sistema de backups automáticos"
                }
            
            return {"passed": True, "message": "Backups configurados"}
            
        except Exception as e:
            return {
                "passed": False,
                "severity": "medium",
                "message": f"Erro ao verificar backups: {str(e)}",
                "recommendation": "Verificar configuração de backups manualmente"
            }
    
    def _generate_security_recommendations(self, critical: int, high: int, medium: int, low: int) -> List[str]:
        """Gera recomendações de segurança"""
        recommendations = []
        
        if critical > 0:
            recommendations.append(f"🚨 {critical} problemas críticos encontrados - Resolver imediatamente")
        
        if high > 0:
            recommendations.append(f"🔴 {high} problemas de alta prioridade - Resolver em 24h")
        
        if medium > 0:
            recommendations.append(f"🟡 {medium} problemas de média prioridade - Resolver em 1 semana")
        
        if low > 0:
            recommendations.append(f"🔵 {low} problemas de baixa prioridade - Resolver em 1 mês")
        
        # Recomendações gerais
        recommendations.extend([
            "🔐 Implementar autenticação de dois fatores (2FA)",
            "🛡️ Configurar WAF (Web Application Firewall)",
            "📊 Implementar monitoramento de segurança em tempo real",
            "🔍 Realizar testes de penetração regulares",
            "📋 Estabelecer política de segurança da informação",
            "👥 Treinar equipe em práticas de segurança",
            "🔄 Implementar rotação de credenciais",
            "📈 Configurar alertas de segurança"
        ])
        
        return recommendations
    
    def _save_security_report(self, report: SecurityReport):
        """Salva relatório de segurança"""
        try:
            filename = f"security_report_{report.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join("security", filename)
            
            # Converter para dicionário
            report_dict = {
                "timestamp": report.timestamp.isoformat(),
                "overall_score": report.overall_score,
                "vulnerabilities_found": report.vulnerabilities_found,
                "critical_issues": report.critical_issues,
                "high_issues": report.high_issues,
                "medium_issues": report.medium_issues,
                "low_issues": report.low_issues,
                "recommendations": report.recommendations,
                "compliance_status": report.compliance_status
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Relatório de segurança salvo em {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {e}")
    
    def _empty_security_report(self) -> SecurityReport:
        """Retorna relatório vazio"""
        return SecurityReport(
            timestamp=datetime.now(),
            overall_score=0.0,
            vulnerabilities_found=0,
            critical_issues=0,
            high_issues=0,
            medium_issues=0,
            low_issues=0,
            recommendations=[],
            compliance_status={}
        )
    
    def generate_security_hardening_script(self) -> str:
        """Gera script de hardening de segurança"""
        try:
            script_content = """#!/bin/bash
# Script de Hardening de Segurança - MaraBet AI
# Execute com privilégios de administrador

echo "🔐 Iniciando hardening de segurança..."

# 1. Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# 2. Configurar firewall
echo "🛡️ Configurando firewall..."
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 3. Configurar fail2ban
echo "🚫 Configurando fail2ban..."
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 4. Configurar logwatch
echo "📊 Configurando logwatch..."
sudo apt install logwatch -y

# 5. Configurar chkrootkit
echo "🔍 Configurando chkrootkit..."
sudo apt install chkrootkit -y

# 6. Configurar rkhunter
echo "🕵️ Configurando rkhunter..."
sudo apt install rkhunter -y
sudo rkhunter --update
sudo rkhunter --propupd

# 7. Configurar AIDE
echo "📋 Configurando AIDE..."
sudo apt install aide -y
sudo aideinit
sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# 8. Configurar auditoria
echo "📝 Configurando auditoria..."
sudo apt install auditd -y
sudo systemctl enable auditd
sudo systemctl start auditd

# 9. Configurar AppArmor
echo "🛡️ Configurando AppArmor..."
sudo apt install apparmor-utils -y
sudo systemctl enable apparmor
sudo systemctl start apparmor

# 10. Configurar permissões
echo "🔒 Configurando permissões..."
sudo chmod 600 /etc/ssh/sshd_config
sudo chmod 600 /etc/mysql/my.cnf
sudo chmod 600 /etc/nginx/nginx.conf

echo "✅ Hardening de segurança concluído!"
echo "📋 Execute 'sudo rkhunter -c' para verificar rootkits"
echo "📋 Execute 'sudo aide -c' para verificar integridade"
"""
            
            script_path = "security/hardening_script.sh"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Tornar executável
            os.chmod(script_path, 0o755)
            
            logger.info(f"✅ Script de hardening salvo em {script_path}")
            return script_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar script: {e}")
            return ""
