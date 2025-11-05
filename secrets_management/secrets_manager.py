"""
Gerenciador Principal de Secrets - MaraBet AI
Sistema centralizado para gerenciar chaves de API e credenciais
"""

import os
import json
import base64
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import yaml

logger = logging.getLogger(__name__)

class SecretsManager:
    """
    Gerenciador principal de secrets para MaraBet AI
    Suporta múltiplos backends: arquivos locais, HashiCorp Vault, AWS Secrets Manager
    """
    
    def __init__(self, 
                 backend: str = "local",
                 config_path: str = "secrets/config.yaml",
                 master_key: Optional[str] = None):
        """
        Inicializa o gerenciador de secrets
        
        Args:
            backend: Backend a ser usado ('local', 'vault', 'aws')
            config_path: Caminho para arquivo de configuração
            master_key: Chave mestra para criptografia (opcional)
        """
        self.backend = backend
        self.config_path = Path(config_path)
        self.master_key = master_key or os.getenv('MARABET_MASTER_KEY')
        self.secrets_dir = Path("secrets/data")
        self.secrets_dir.mkdir(exist_ok=True)
        
        # Carregar configuração
        self.config = self._load_config()
        
        # Inicializar backend específico
        self._init_backend()
        
        logger.info(f"SecretsManager inicializado com backend: {backend}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo YAML"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                # Criar configuração padrão
                default_config = {
                    'encryption': {
                        'algorithm': 'AES-256-GCM',
                        'key_derivation': 'PBKDF2',
                        'iterations': 100000
                    },
                    'rotation': {
                        'enabled': True,
                        'interval_days': 90,
                        'warning_days': 7
                    },
                    'backends': {
                        'local': {
                            'enabled': True,
                            'path': 'secrets/data'
                        },
                        'vault': {
                            'enabled': False,
                            'url': 'http://localhost:8200',
                            'token': None,
                            'mount_point': 'marabet'
                        },
                        'aws': {
                            'enabled': False,
                            'region': 'us-east-1',
                            'secret_name': 'marabet-ai-secrets'
                        }
                    }
                }
                self._save_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return {}
    
    def _save_config(self, config: Dict[str, Any]):
        """Salva configuração no arquivo YAML"""
        try:
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
    
    def _init_backend(self):
        """Inicializa o backend específico"""
        if self.backend == "vault" and self.config.get('backends', {}).get('vault', {}).get('enabled'):
            try:
                from .vault_client import VaultClient
                vault_config = self.config['backends']['vault']
                self.vault_client = VaultClient(
                    url=vault_config['url'],
                    token=vault_config['token'],
                    mount_point=vault_config['mount_point']
                )
            except ImportError:
                logger.warning("HashiCorp Vault não disponível, usando backend local")
                self.backend = "local"
        elif self.backend == "aws" and self.config.get('backends', {}).get('aws', {}).get('enabled'):
            try:
                import boto3
                aws_config = self.config['backends']['aws']
                self.aws_client = boto3.client(
                    'secretsmanager',
                    region_name=aws_config['region']
                )
                self.aws_secret_name = aws_config['secret_name']
            except ImportError:
                logger.warning("AWS SDK não disponível, usando backend local")
                self.backend = "local"
    
    def _generate_master_key(self) -> bytes:
        """Gera chave mestra baseada em senha"""
        if not self.master_key:
            raise ValueError("Master key não definida")
        
        salt = b'marabet_salt_2024'  # Em produção, usar salt aleatório
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.config.get('encryption', {}).get('iterations', 100000)
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
    
    def _encrypt_value(self, value: str) -> str:
        """Criptografa um valor"""
        try:
            key = self._generate_master_key()
            fernet = Fernet(key)
            encrypted_value = fernet.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted_value).decode()
        except Exception as e:
            logger.error(f"Erro ao criptografar valor: {e}")
            raise
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Descriptografa um valor"""
        try:
            key = self._generate_master_key()
            fernet = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted_value = fernet.decrypt(encrypted_bytes)
            return decrypted_value.decode()
        except Exception as e:
            logger.error(f"Erro ao descriptografar valor: {e}")
            raise
    
    def set_secret(self, key: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Define um secret
        
        Args:
            key: Chave do secret
            value: Valor do secret
            metadata: Metadados adicionais
            
        Returns:
            True se bem-sucedido
        """
        try:
            secret_data = {
                'value': self._encrypt_value(value),
                'created_at': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            if self.backend == "vault":
                return self._set_vault_secret(key, secret_data)
            elif self.backend == "aws":
                return self._set_aws_secret(key, secret_data)
            else:
                return self._set_local_secret(key, secret_data)
                
        except Exception as e:
            logger.error(f"Erro ao definir secret {key}: {e}")
            return False
    
    def get_secret(self, key: str) -> Optional[str]:
        """
        Obtém um secret
        
        Args:
            key: Chave do secret
            
        Returns:
            Valor do secret ou None se não encontrado
        """
        try:
            if self.backend == "vault":
                secret_data = self._get_vault_secret(key)
            elif self.backend == "aws":
                secret_data = self._get_aws_secret(key)
            else:
                secret_data = self._get_local_secret(key)
            
            if secret_data:
                return self._decrypt_value(secret_data['value'])
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter secret {key}: {e}")
            return None
    
    def delete_secret(self, key: str) -> bool:
        """
        Remove um secret
        
        Args:
            key: Chave do secret
            
        Returns:
            True se bem-sucedido
        """
        try:
            if self.backend == "vault":
                return self._delete_vault_secret(key)
            elif self.backend == "aws":
                return self._delete_aws_secret(key)
            else:
                return self._delete_local_secret(key)
                
        except Exception as e:
            logger.error(f"Erro ao deletar secret {key}: {e}")
            return False
    
    def list_secrets(self) -> List[str]:
        """
        Lista todos os secrets disponíveis
        
        Returns:
            Lista de chaves de secrets
        """
        try:
            if self.backend == "vault":
                return self._list_vault_secrets()
            elif self.backend == "aws":
                return self._list_aws_secrets()
            else:
                return self._list_local_secrets()
                
        except Exception as e:
            logger.error(f"Erro ao listar secrets: {e}")
            return []
    
    def _set_local_secret(self, key: str, secret_data: Dict[str, Any]) -> bool:
        """Define secret no backend local"""
        try:
            secret_file = self.secrets_dir / f"{key}.json"
            with open(secret_file, 'w', encoding='utf-8') as f:
                json.dump(secret_data, f, indent=2)
            
            # Definir permissões restritivas
            os.chmod(secret_file, 0o600)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar secret local {key}: {e}")
            return False
    
    def _get_local_secret(self, key: str) -> Optional[Dict[str, Any]]:
        """Obtém secret do backend local"""
        try:
            secret_file = self.secrets_dir / f"{key}.json"
            if secret_file.exists():
                with open(secret_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Erro ao ler secret local {key}: {e}")
            return None
    
    def _delete_local_secret(self, key: str) -> bool:
        """Remove secret do backend local"""
        try:
            secret_file = self.secrets_dir / f"{key}.json"
            if secret_file.exists():
                secret_file.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao deletar secret local {key}: {e}")
            return False
    
    def _list_local_secrets(self) -> List[str]:
        """Lista secrets do backend local"""
        try:
            secrets = []
            for secret_file in self.secrets_dir.glob("*.json"):
                secrets.append(secret_file.stem)
            return secrets
        except Exception as e:
            logger.error(f"Erro ao listar secrets locais: {e}")
            return []
    
    def _set_vault_secret(self, key: str, secret_data: Dict[str, Any]) -> bool:
        """Define secret no HashiCorp Vault"""
        try:
            return self.vault_client.write_secret(key, secret_data)
        except Exception as e:
            logger.error(f"Erro ao definir secret no Vault {key}: {e}")
            return False
    
    def _get_vault_secret(self, key: str) -> Optional[Dict[str, Any]]:
        """Obtém secret do HashiCorp Vault"""
        try:
            return self.vault_client.read_secret(key)
        except Exception as e:
            logger.error(f"Erro ao obter secret do Vault {key}: {e}")
            return None
    
    def _delete_vault_secret(self, key: str) -> bool:
        """Remove secret do HashiCorp Vault"""
        try:
            return self.vault_client.delete_secret(key)
        except Exception as e:
            logger.error(f"Erro ao deletar secret do Vault {key}: {e}")
            return False
    
    def _list_vault_secrets(self) -> List[str]:
        """Lista secrets do HashiCorp Vault"""
        try:
            return self.vault_client.list_secrets()
        except Exception as e:
            logger.error(f"Erro ao listar secrets do Vault: {e}")
            return []
    
    def _set_aws_secret(self, key: str, secret_data: Dict[str, Any]) -> bool:
        """Define secret no AWS Secrets Manager"""
        try:
            # AWS Secrets Manager armazena como JSON
            secret_value = json.dumps({key: secret_data})
            
            try:
                # Tentar atualizar secret existente
                self.aws_client.update_secret(
                    SecretId=self.aws_secret_name,
                    SecretString=secret_value
                )
            except self.aws_client.exceptions.ResourceNotFoundException:
                # Criar novo secret se não existir
                self.aws_client.create_secret(
                    Name=self.aws_secret_name,
                    SecretString=secret_value
                )
            
            return True
        except Exception as e:
            logger.error(f"Erro ao definir secret no AWS {key}: {e}")
            return False
    
    def _get_aws_secret(self, key: str) -> Optional[Dict[str, Any]]:
        """Obtém secret do AWS Secrets Manager"""
        try:
            response = self.aws_client.get_secret_value(SecretId=self.aws_secret_name)
            secrets = json.loads(response['SecretString'])
            return secrets.get(key)
        except Exception as e:
            logger.error(f"Erro ao obter secret do AWS {key}: {e}")
            return None
    
    def _delete_aws_secret(self, key: str) -> bool:
        """Remove secret do AWS Secrets Manager"""
        try:
            # AWS Secrets Manager não suporta deleção individual de chaves
            # Apenas marca para remoção do secret inteiro
            self.aws_client.delete_secret(
                SecretId=self.aws_secret_name,
                ForceDeleteWithoutRecovery=True
            )
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar secret do AWS {key}: {e}")
            return False
    
    def _list_aws_secrets(self) -> List[str]:
        """Lista secrets do AWS Secrets Manager"""
        try:
            response = self.aws_client.get_secret_value(SecretId=self.aws_secret_name)
            secrets = json.loads(response['SecretString'])
            return list(secrets.keys())
        except Exception as e:
            logger.error(f"Erro ao listar secrets do AWS: {e}")
            return []
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Obtém chave de API para um serviço específico
        
        Args:
            service: Nome do serviço (api_football, odds_api, telegram, etc.)
            
        Returns:
            Chave de API ou None se não encontrada
        """
        return self.get_secret(f"api_key_{service}")
    
    def set_api_key(self, service: str, api_key: str) -> bool:
        """
        Define chave de API para um serviço específico
        
        Args:
            service: Nome do serviço
            api_key: Chave de API
            
        Returns:
            True se bem-sucedido
        """
        metadata = {
            'service': service,
            'type': 'api_key',
            'last_updated': datetime.now().isoformat()
        }
        return self.set_secret(f"api_key_{service}", api_key, metadata)
    
    def get_database_credentials(self) -> Optional[Dict[str, str]]:
        """
        Obtém credenciais do banco de dados
        
        Returns:
            Dicionário com credenciais ou None
        """
        try:
            username = self.get_secret("db_username")
            password = self.get_secret("db_password")
            host = self.get_secret("db_host")
            port = self.get_secret("db_port")
            database = self.get_secret("db_database")
            
            if all([username, password, host, port, database]):
                return {
                    'username': username,
                    'password': password,
                    'host': host,
                    'port': port,
                    'database': database
                }
            return None
        except Exception as e:
            logger.error(f"Erro ao obter credenciais do banco: {e}")
            return None
    
    def set_database_credentials(self, credentials: Dict[str, str]) -> bool:
        """
        Define credenciais do banco de dados
        
        Args:
            credentials: Dicionário com credenciais
            
        Returns:
            True se bem-sucedido
        """
        try:
            success = True
            for key, value in credentials.items():
                if not self.set_secret(f"db_{key}", value):
                    success = False
            return success
        except Exception as e:
            logger.error(f"Erro ao definir credenciais do banco: {e}")
            return False
    
    def export_secrets(self, output_file: str) -> bool:
        """
        Exporta todos os secrets para um arquivo (criptografado)
        
        Args:
            output_file: Caminho do arquivo de saída
            
        Returns:
            True se bem-sucedido
        """
        try:
            secrets = {}
            for key in self.list_secrets():
                value = self.get_secret(key)
                if value:
                    secrets[key] = value
            
            # Criptografar arquivo de exportação
            encrypted_data = self._encrypt_value(json.dumps(secrets))
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            logger.info(f"Secrets exportados para {output_file}")
            return True
        except Exception as e:
            logger.error(f"Erro ao exportar secrets: {e}")
            return False
    
    def import_secrets(self, input_file: str) -> bool:
        """
        Importa secrets de um arquivo (criptografado)
        
        Args:
            input_file: Caminho do arquivo de entrada
            
        Returns:
            True se bem-sucedido
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            # Descriptografar arquivo
            decrypted_data = self._decrypt_value(encrypted_data)
            secrets = json.loads(decrypted_data)
            
            # Importar cada secret
            success = True
            for key, value in secrets.items():
                if not self.set_secret(key, value):
                    success = False
            
            logger.info(f"Secrets importados de {input_file}")
            return success
        except Exception as e:
            logger.error(f"Erro ao importar secrets: {e}")
            return False
