"""
Cliente HashiCorp Vault - MaraBet AI
Integração com HashiCorp Vault para gerenciamento de secrets
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class VaultClient:
    """
    Cliente para HashiCorp Vault
    Gerencia secrets usando a API do Vault
    """
    
    def __init__(self, 
                 url: str = "http://localhost:8200",
                 token: Optional[str] = None,
                 mount_point: str = "marabet"):
        """
        Inicializa o cliente Vault
        
        Args:
            url: URL do servidor Vault
            token: Token de autenticação
            mount_point: Ponto de montagem para secrets
        """
        self.url = url.rstrip('/')
        self.token = token
        self.mount_point = mount_point
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({
                'X-Vault-Token': self.token
            })
        
        # Verificar conectividade
        self._check_connection()
    
    def _check_connection(self) -> bool:
        """Verifica se o Vault está acessível"""
        try:
            response = self.session.get(f"{self.url}/v1/sys/health")
            if response.status_code == 200:
                logger.info("✅ Conectado ao HashiCorp Vault")
                return True
            else:
                logger.warning(f"⚠️ Vault retornou status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com Vault: {e}")
            return False
    
    def _get_secret_path(self, key: str) -> str:
        """Constrói o caminho completo do secret"""
        return f"/v1/{self.mount_point}/data/{key}"
    
    def _get_metadata_path(self, key: str) -> str:
        """Constrói o caminho de metadados do secret"""
        return f"/v1/{self.mount_point}/metadata/{key}"
    
    def write_secret(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Escreve um secret no Vault
        
        Args:
            key: Chave do secret
            data: Dados do secret
            
        Returns:
            True se bem-sucedido
        """
        try:
            url = self._get_secret_path(key)
            payload = {
                "data": data
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Secret {key} escrito no Vault")
                return True
            else:
                logger.error(f"❌ Erro ao escrever secret {key}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao escrever secret {key}: {e}")
            return False
    
    def read_secret(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Lê um secret do Vault
        
        Args:
            key: Chave do secret
            
        Returns:
            Dados do secret ou None se não encontrado
        """
        try:
            url = self._get_secret_path(key)
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('data', {})
            elif response.status_code == 404:
                logger.warning(f"⚠️ Secret {key} não encontrado no Vault")
                return None
            else:
                logger.error(f"❌ Erro ao ler secret {key}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao ler secret {key}: {e}")
            return None
    
    def delete_secret(self, key: str) -> bool:
        """
        Remove um secret do Vault
        
        Args:
            key: Chave do secret
            
        Returns:
            True se bem-sucedido
        """
        try:
            # Vault v2 usa DELETE para remover secrets
            url = self._get_metadata_path(key)
            response = self.session.delete(url)
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Secret {key} removido do Vault")
                return True
            else:
                logger.error(f"❌ Erro ao remover secret {key}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao remover secret {key}: {e}")
            return False
    
    def list_secrets(self) -> List[str]:
        """
        Lista todos os secrets no mount point
        
        Returns:
            Lista de chaves de secrets
        """
        try:
            url = f"/v1/{self.mount_point}/metadata"
            response = self.session.request('LIST', f"{self.url}{url}")
            
            if response.status_code == 200:
                data = response.json()
                keys = data.get('data', {}).get('keys', [])
                # Remover barras finais das chaves
                return [key.rstrip('/') for key in keys]
            else:
                logger.error(f"❌ Erro ao listar secrets: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro ao listar secrets: {e}")
            return []
    
    def get_secret_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Obtém metadados de um secret
        
        Args:
            key: Chave do secret
            
        Returns:
            Metadados do secret ou None
        """
        try:
            url = self._get_metadata_path(key)
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {})
            else:
                logger.error(f"❌ Erro ao obter metadados do secret {key}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter metadados do secret {key}: {e}")
            return None
    
    def update_secret_metadata(self, key: str, metadata: Dict[str, Any]) -> bool:
        """
        Atualiza metadados de um secret
        
        Args:
            key: Chave do secret
            metadata: Novos metadados
            
        Returns:
            True se bem-sucedido
        """
        try:
            url = self._get_metadata_path(key)
            payload = {
                "custom_metadata": metadata
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Metadados do secret {key} atualizados")
                return True
            else:
                logger.error(f"❌ Erro ao atualizar metadados do secret {key}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar metadados do secret {key}: {e}")
            return False
    
    def create_policy(self, policy_name: str, policy_rules: str) -> bool:
        """
        Cria uma política no Vault
        
        Args:
            policy_name: Nome da política
            policy_rules: Regras da política em HCL
            
        Returns:
            True se bem-sucedido
        """
        try:
            url = f"/v1/sys/policies/acl/{policy_name}"
            payload = {
                "policy": policy_rules
            }
            
            response = self.session.put(url, json=payload)
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Política {policy_name} criada no Vault")
                return True
            else:
                logger.error(f"❌ Erro ao criar política {policy_name}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar política {policy_name}: {e}")
            return False
    
    def create_token(self, 
                    policies: List[str], 
                    ttl: str = "1h",
                    renewable: bool = True) -> Optional[str]:
        """
        Cria um token no Vault
        
        Args:
            policies: Lista de políticas para o token
            ttl: Time-to-live do token
            renewable: Se o token pode ser renovado
            
        Returns:
            Token criado ou None se falhou
        """
        try:
            url = "/v1/auth/token/create"
            payload = {
                "policies": policies,
                "ttl": ttl,
                "renewable": renewable
            }
            
            response = self.session.post(f"{self.url}{url}", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('auth', {}).get('client_token')
                logger.info(f"✅ Token criado com políticas: {policies}")
                return token
            else:
                logger.error(f"❌ Erro ao criar token: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar token: {e}")
            return None
    
    def renew_token(self, token: str) -> bool:
        """
        Renova um token do Vault
        
        Args:
            token: Token a ser renovado
            
        Returns:
            True se bem-sucedido
        """
        try:
            url = "/v1/auth/token/renew-self"
            headers = {'X-Vault-Token': token}
            
            response = requests.post(f"{self.url}{url}", headers=headers)
            
            if response.status_code == 200:
                logger.info("✅ Token renovado com sucesso")
                return True
            else:
                logger.error(f"❌ Erro ao renovar token: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao renovar token: {e}")
            return False
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoga um token do Vault
        
        Args:
            token: Token a ser revogado
            
        Returns:
            True se bem-sucedido
        """
        try:
            url = "/v1/auth/token/revoke"
            headers = {'X-Vault-Token': token}
            
            response = requests.post(f"{self.url}{url}", headers=headers)
            
            if response.status_code in [200, 204]:
                logger.info("✅ Token revogado com sucesso")
                return True
            else:
                logger.error(f"❌ Erro ao revogar token: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao revogar token: {e}")
            return False
    
    def enable_kv_engine(self, path: str = "marabet", version: int = 2) -> bool:
        """
        Habilita o motor KV (Key-Value) no Vault
        
        Args:
            path: Caminho do motor
            version: Versão do motor (1 ou 2)
            
        Returns:
            True se bem-sucedido
        """
        try:
            url = f"/v1/sys/mounts/{path}"
            payload = {
                "type": "kv",
                "options": {
                    "version": str(version)
                }
            }
            
            response = self.session.post(f"{self.url}{url}", json=payload)
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Motor KV habilitado em {path}")
                return True
            else:
                logger.error(f"❌ Erro ao habilitar motor KV: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao habilitar motor KV: {e}")
            return False
    
    def get_vault_status(self) -> Dict[str, Any]:
        """
        Obtém status do Vault
        
        Returns:
            Dicionário com informações de status
        """
        try:
            response = self.session.get(f"{self.url}/v1/sys/health")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def setup_marabet_secrets(self) -> bool:
        """
        Configura secrets específicos do MaraBet AI no Vault
        
        Returns:
            True se bem-sucedido
        """
        try:
            # Habilitar motor KV se não estiver habilitado
            if not self.enable_kv_engine(self.mount_point):
                logger.warning("⚠️ Motor KV pode já estar habilitado")
            
            # Criar política para MaraBet AI
            policy_rules = f"""
path "{self.mount_point}/data/*" {{
  capabilities = ["create", "read", "update", "delete", "list"]
}}

path "{self.mount_point}/metadata/*" {{
  capabilities = ["read", "list"]
}}
"""
            
            if not self.create_policy("marabet-policy", policy_rules):
                logger.warning("⚠️ Política pode já existir")
            
            logger.info("✅ Configuração do MaraBet AI no Vault concluída")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar MaraBet AI no Vault: {e}")
            return False
