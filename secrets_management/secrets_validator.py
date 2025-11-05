"""
Validador de Secrets - MaraBet AI
Validação e teste de chaves de API e credenciais
"""

import requests
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class SecretsValidator:
    """
    Validador de secrets para MaraBet AI
    Testa e valida chaves de API e credenciais
    """
    
    def __init__(self):
        """Inicializa o validador de secrets"""
        self.validation_results: Dict[str, Dict[str, Any]] = {}
        self.validation_history: List[Dict[str, Any]] = []
    
    def validate_api_football_key(self, api_key: str) -> Tuple[bool, str]:
        """
        Valida chave da API-Football
        
        Args:
            api_key: Chave da API-Football
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            url = "https://api-football-v1.p.rapidapi.com/v3/status"
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('response', {}).get('account', {}).get('plan'):
                    plan = data['response']['account']['plan']
                    requests_left = data['response']['account'].get('requests_left', 0)
                    
                    return True, f"✅ API-Football válida - Plano: {plan}, Requests restantes: {requests_left}"
                else:
                    return True, "✅ API-Football válida"
            elif response.status_code == 401:
                return False, "❌ API-Football inválida - Chave incorreta"
            elif response.status_code == 403:
                return False, "❌ API-Football inválida - Limite de requests excedido"
            else:
                return False, f"❌ API-Football inválida - Status: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "❌ API-Football inválida - Timeout na conexão"
        except requests.exceptions.ConnectionError:
            return False, "❌ API-Football inválida - Erro de conexão"
        except Exception as e:
            return False, f"❌ API-Football inválida - Erro: {e}"
    
    def validate_odds_api_key(self, api_key: str) -> Tuple[bool, str]:
        """
        Valida chave da The Odds API
        
        Args:
            api_key: Chave da The Odds API
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            url = f"https://api.the-odds-api.com/v4/sports/?apiKey={api_key}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return True, f"✅ The Odds API válida - {len(data)} esportes disponíveis"
                else:
                    return True, "✅ The Odds API válida"
            elif response.status_code == 401:
                return False, "❌ The Odds API inválida - Chave incorreta"
            elif response.status_code == 403:
                return False, "❌ The Odds API inválida - Limite de requests excedido"
            else:
                return False, f"❌ The Odds API inválida - Status: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "❌ The Odds API inválida - Timeout na conexão"
        except requests.exceptions.ConnectionError:
            return False, "❌ The Odds API inválida - Erro de conexão"
        except Exception as e:
            return False, f"❌ The Odds API inválida - Erro: {e}"
    
    def validate_telegram_bot_token(self, bot_token: str) -> Tuple[bool, str]:
        """
        Valida token do bot do Telegram
        
        Args:
            bot_token: Token do bot do Telegram
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            # Validar formato do token
            if not re.match(r'^\d+:[A-Za-z0-9_-]{35}$', bot_token):
                return False, "❌ Token do Telegram inválido - Formato incorreto"
            
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    bot_name = bot_info.get('first_name', 'Unknown')
                    username = bot_info.get('username', 'Unknown')
                    
                    return True, f"✅ Bot do Telegram válido - @{username} ({bot_name})"
                else:
                    return False, f"❌ Bot do Telegram inválido - {data.get('description', 'Erro desconhecido')}"
            elif response.status_code == 401:
                return False, "❌ Bot do Telegram inválido - Token incorreto"
            else:
                return False, f"❌ Bot do Telegram inválido - Status: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "❌ Bot do Telegram inválido - Timeout na conexão"
        except requests.exceptions.ConnectionError:
            return False, "❌ Bot do Telegram inválido - Erro de conexão"
        except Exception as e:
            return False, f"❌ Bot do Telegram inválido - Erro: {e}"
    
    def validate_smtp_credentials(self, 
                                smtp_server: str,
                                smtp_port: int,
                                username: str,
                                password: str) -> Tuple[bool, str]:
        """
        Valida credenciais SMTP
        
        Args:
            smtp_server: Servidor SMTP
            smtp_port: Porta SMTP
            username: Nome de usuário
            password: Senha
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            # Criar mensagem de teste
            msg = MIMEText("Teste de validação SMTP - MaraBet AI")
            msg['Subject'] = "Validação SMTP"
            msg['From'] = username
            msg['To'] = username
            
            # Conectar e testar
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.quit()
            
            return True, f"✅ SMTP válido - {smtp_server}:{smtp_port}"
            
        except smtplib.SMTPAuthenticationError:
            return False, "❌ SMTP inválido - Credenciais incorretas"
        except smtplib.SMTPConnectError:
            return False, "❌ SMTP inválido - Erro de conexão"
        except smtplib.SMTPException as e:
            return False, f"❌ SMTP inválido - Erro: {e}"
        except Exception as e:
            return False, f"❌ SMTP inválido - Erro: {e}"
    
    def validate_database_connection(self, 
                                   host: str,
                                   port: int,
                                   database: str,
                                   username: str,
                                   password: str) -> Tuple[bool, str]:
        """
        Valida conexão com banco de dados
        
        Args:
            host: Host do banco
            port: Porta do banco
            database: Nome do banco
            username: Nome de usuário
            password: Senha
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            import psycopg2
            
            # Testar conexão
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )
            
            # Testar query simples
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result and result[0] == 1:
                return True, f"✅ PostgreSQL válido - {host}:{port}/{database}"
            else:
                return False, "❌ PostgreSQL inválido - Query de teste falhou"
                
        except psycopg2.OperationalError as e:
            return False, f"❌ PostgreSQL inválido - Erro de conexão: {e}"
        except psycopg2.DatabaseError as e:
            return False, f"❌ PostgreSQL inválido - Erro de banco: {e}"
        except Exception as e:
            return False, f"❌ PostgreSQL inválido - Erro: {e}"
    
    def validate_redis_connection(self, redis_url: str) -> Tuple[bool, str]:
        """
        Valida conexão com Redis
        
        Args:
            redis_url: URL do Redis
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            import redis
            
            # Conectar ao Redis
            r = redis.from_url(redis_url)
            
            # Testar ping
            pong = r.ping()
            
            if pong:
                # Obter informações do Redis
                info = r.info()
                version = info.get('redis_version', 'Unknown')
                memory = info.get('used_memory_human', 'Unknown')
                
                return True, f"✅ Redis válido - Versão: {version}, Memória: {memory}"
            else:
                return False, "❌ Redis inválido - Ping falhou"
                
        except redis.ConnectionError:
            return False, "❌ Redis inválido - Erro de conexão"
        except redis.RedisError as e:
            return False, f"❌ Redis inválido - Erro: {e}"
        except Exception as e:
            return False, f"❌ Redis inválido - Erro: {e}"
    
    def validate_jwt_secret(self, jwt_secret: str) -> Tuple[bool, str]:
        """
        Valida chave secreta JWT
        
        Args:
            jwt_secret: Chave secreta JWT
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            # Validar comprimento mínimo
            if len(jwt_secret) < 32:
                return False, "❌ JWT Secret inválido - Muito curto (mínimo 32 caracteres)"
            
            # Validar complexidade
            if not re.search(r'[A-Z]', jwt_secret):
                return False, "❌ JWT Secret inválido - Deve conter pelo menos uma letra maiúscula"
            
            if not re.search(r'[a-z]', jwt_secret):
                return False, "❌ JWT Secret inválido - Deve conter pelo menos uma letra minúscula"
            
            if not re.search(r'[0-9]', jwt_secret):
                return False, "❌ JWT Secret inválido - Deve conter pelo menos um número"
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', jwt_secret):
                return False, "❌ JWT Secret inválido - Deve conter pelo menos um caractere especial"
            
            # Testar geração de token
            import jwt
            from datetime import datetime, timedelta
            
            payload = {
                'test': 'validation',
                'exp': datetime.utcnow() + timedelta(hours=1)
            }
            
            token = jwt.encode(payload, jwt_secret, algorithm='HS256')
            decoded = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            
            if decoded.get('test') == 'validation':
                return True, "✅ JWT Secret válido"
            else:
                return False, "❌ JWT Secret inválido - Teste de codificação falhou"
                
        except Exception as e:
            return False, f"❌ JWT Secret inválido - Erro: {e}"
    
    def validate_all_secrets(self, secrets_manager) -> Dict[str, Dict[str, Any]]:
        """
        Valida todos os secrets configurados
        
        Args:
            secrets_manager: Instância do gerenciador de secrets
            
        Returns:
            Dicionário com resultados de validação
        """
        try:
            results = {}
            
            # Validar chaves de API
            api_football_key = secrets_manager.get_api_key('api_football')
            if api_football_key:
                success, message = self.validate_api_football_key(api_football_key)
                results['api_football'] = {
                    'valid': success,
                    'message': message,
                    'validated_at': datetime.now().isoformat()
                }
            
            odds_api_key = secrets_manager.get_api_key('odds_api')
            if odds_api_key:
                success, message = self.validate_odds_api_key(odds_api_key)
                results['odds_api'] = {
                    'valid': success,
                    'message': message,
                    'validated_at': datetime.now().isoformat()
                }
            
            # Validar bot do Telegram
            telegram_token = secrets_manager.get_secret('telegram_bot_token')
            if telegram_token:
                success, message = self.validate_telegram_bot_token(telegram_token)
                results['telegram_bot'] = {
                    'valid': success,
                    'message': message,
                    'validated_at': datetime.now().isoformat()
                }
            
            # Validar credenciais SMTP
            smtp_username = secrets_manager.get_secret('smtp_username')
            smtp_password = secrets_manager.get_secret('smtp_password')
            smtp_server = secrets_manager.get_secret('smtp_server')
            smtp_port = secrets_manager.get_secret('smtp_port')
            
            if all([smtp_username, smtp_password, smtp_server, smtp_port]):
                try:
                    smtp_port_int = int(smtp_port)
                    success, message = self.validate_smtp_credentials(
                        smtp_server, smtp_port_int, smtp_username, smtp_password
                    )
                    results['smtp'] = {
                        'valid': success,
                        'message': message,
                        'validated_at': datetime.now().isoformat()
                    }
                except ValueError:
                    results['smtp'] = {
                        'valid': False,
                        'message': "❌ SMTP inválido - Porta deve ser um número",
                        'validated_at': datetime.now().isoformat()
                    }
            
            # Validar banco de dados
            db_credentials = secrets_manager.get_database_credentials()
            if db_credentials:
                success, message = self.validate_database_connection(
                    db_credentials['host'],
                    int(db_credentials['port']),
                    db_credentials['database'],
                    db_credentials['username'],
                    db_credentials['password']
                )
                results['database'] = {
                    'valid': success,
                    'message': message,
                    'validated_at': datetime.now().isoformat()
                }
            
            # Validar Redis
            redis_url = secrets_manager.get_secret('redis_url')
            if redis_url:
                success, message = self.validate_redis_connection(redis_url)
                results['redis'] = {
                    'valid': success,
                    'message': message,
                    'validated_at': datetime.now().isoformat()
                }
            
            # Validar JWT Secret
            jwt_secret = secrets_manager.get_secret('jwt_secret_key')
            if jwt_secret:
                success, message = self.validate_jwt_secret(jwt_secret)
                results['jwt_secret'] = {
                    'valid': success,
                    'message': message,
                    'validated_at': datetime.now().isoformat()
                }
            
            # Salvar resultados
            self.validation_results = results
            self.validation_history.append({
                'timestamp': datetime.now().isoformat(),
                'results': results
            })
            
            # Manter apenas últimos 100 registros
            if len(self.validation_history) > 100:
                self.validation_history = self.validation_history[-100:]
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro ao validar secrets: {e}")
            return {}
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo das validações
        
        Returns:
            Dicionário com resumo
        """
        try:
            if not self.validation_results:
                return {
                    'total_secrets': 0,
                    'valid_secrets': 0,
                    'invalid_secrets': 0,
                    'validation_rate': 0.0,
                    'last_validation': None
                }
            
            total_secrets = len(self.validation_results)
            valid_secrets = sum(1 for result in self.validation_results.values() if result.get('valid', False))
            invalid_secrets = total_secrets - valid_secrets
            validation_rate = (valid_secrets / total_secrets * 100) if total_secrets > 0 else 0.0
            
            return {
                'total_secrets': total_secrets,
                'valid_secrets': valid_secrets,
                'invalid_secrets': invalid_secrets,
                'validation_rate': round(validation_rate, 2),
                'last_validation': max(
                    result.get('validated_at', '') 
                    for result in self.validation_results.values()
                ) if self.validation_results else None
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter resumo de validação: {e}")
            return {}
    
    def get_validation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém histórico de validações
        
        Args:
            limit: Número máximo de registros
            
        Returns:
            Lista de validações
        """
        try:
            return self.validation_history[-limit:] if self.validation_history else []
        except Exception as e:
            logger.error(f"❌ Erro ao obter histórico de validação: {e}")
            return []
