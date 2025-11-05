"""
MaraBet AI - Database Configuration
Obtém credenciais do RDS PostgreSQL via AWS Secrets Manager
"""

import json
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, Optional


class DatabaseConfig:
    """Gerenciador de configuração do banco de dados RDS"""
    
    def __init__(self):
        self.secret_name = "rds!db-3758a324-12a2-4675-b5ff-b92acdf38483"
        self.region_name = "eu-west-1"
        self.database_name = "marabet_production"
        self._credentials = None
    
    def get_secret(self) -> Dict[str, str]:
        """
        Obtém credenciais do AWS Secrets Manager
        
        Returns:
            Dict com username, password, host, port, engine
        """
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=self.region_name
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=self.secret_name
            )
        except ClientError as e:
            # Tratar erros específicos
            error_code = e.response['Error']['Code']
            
            if error_code == 'ResourceNotFoundException':
                raise Exception(f"Secret {self.secret_name} não encontrado")
            elif error_code == 'InvalidRequestException':
                raise Exception(f"Requisição inválida: {e}")
            elif error_code == 'InvalidParameterException':
                raise Exception(f"Parâmetro inválido: {e}")
            elif error_code == 'DecryptionFailure':
                raise Exception(f"Falha ao descriptografar secret: {e}")
            elif error_code == 'InternalServiceError':
                raise Exception(f"Erro interno do serviço AWS: {e}")
            else:
                raise e
        except NoCredentialsError:
            raise Exception(
                "Credenciais AWS não configuradas. "
                "Execute: aws configure"
            )

        # Parse do JSON
        secret_string = get_secret_value_response['SecretString']
        secret = json.loads(secret_string)
        
        return secret
    
    @property
    def credentials(self) -> Dict[str, str]:
        """
        Obtém credenciais (com cache)
        
        Returns:
            Dict com credenciais
        """
        if self._credentials is None:
            self._credentials = self.get_secret()
        return self._credentials
    
    def get_connection_string(self, database: Optional[str] = None) -> str:
        """
        Gera connection string para PostgreSQL
        
        Args:
            database: Nome do database (padrão: marabet_production)
        
        Returns:
            Connection string no formato postgresql://
        """
        creds = self.credentials
        db_name = database or self.database_name
        
        return (
            f"postgresql://{creds['username']}:{creds['password']}"
            f"@{creds['host']}:{creds['port']}/{db_name}?sslmode=require"
        )
    
    def get_sqlalchemy_url(self, database: Optional[str] = None) -> str:
        """
        Gera URL para SQLAlchemy
        
        Args:
            database: Nome do database (padrão: marabet_production)
        
        Returns:
            SQLAlchemy URL
        """
        return self.get_connection_string(database)
    
    def get_django_config(self, database: Optional[str] = None) -> Dict[str, any]:
        """
        Gera configuração para Django DATABASES
        
        Args:
            database: Nome do database (padrão: marabet_production)
        
        Returns:
            Dict com configuração Django
        """
        creds = self.credentials
        db_name = database or self.database_name
        
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'USER': creds['username'],
            'PASSWORD': creds['password'],
            'HOST': creds['host'],
            'PORT': creds['port'],
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    
    def get_psycopg2_config(self, database: Optional[str] = None) -> Dict[str, any]:
        """
        Gera configuração para psycopg2
        
        Args:
            database: Nome do database (padrão: marabet_production)
        
        Returns:
            Dict com configuração psycopg2
        """
        creds = self.credentials
        db_name = database or self.database_name
        
        return {
            'dbname': db_name,
            'user': creds['username'],
            'password': creds['password'],
            'host': creds['host'],
            'port': int(creds['port']),
            'sslmode': 'require',
        }
    
    def get_env_vars(self, database: Optional[str] = None) -> Dict[str, str]:
        """
        Gera variáveis de ambiente
        
        Args:
            database: Nome do database (padrão: marabet_production)
        
        Returns:
            Dict com variáveis de ambiente
        """
        creds = self.credentials
        db_name = database or self.database_name
        
        return {
            'DATABASE_URL': self.get_connection_string(db_name),
            'DB_HOST': creds['host'],
            'DB_PORT': str(creds['port']),
            'DB_NAME': db_name,
            'DB_USER': creds['username'],
            'DB_PASSWORD': creds['password'],
            'DB_ENGINE': creds['engine'],
            'DB_SSL_MODE': 'require',
        }
    
    def test_connection(self) -> bool:
        """
        Testa conexão com o banco de dados
        
        Returns:
            True se conectou com sucesso
        """
        try:
            import psycopg2
            
            config = self.get_psycopg2_config()
            conn = psycopg2.connect(**config)
            
            # Testar query simples
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            print(f"✅ Conexão bem-sucedida!")
            print(f"   PostgreSQL: {version[0][:50]}...")
            
            return True
            
        except ImportError:
            print("⚠️  psycopg2 não instalado")
            print("   Instale: pip install psycopg2-binary")
            return False
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    def export_env_file(self, filepath: str = ".env.rds"):
        """
        Exporta variáveis para arquivo .env
        
        Args:
            filepath: Caminho do arquivo (padrão: .env.rds)
        """
        env_vars = self.get_env_vars()
        
        with open(filepath, 'w') as f:
            f.write("# MaraBet AI - RDS PostgreSQL Configuration\n")
            f.write(f"# Generated from AWS Secrets Manager\n")
            f.write(f"# Secret: {self.secret_name}\n")
            f.write(f"# Region: {self.region_name}\n\n")
            
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Arquivo {filepath} criado com sucesso!")
    
    def print_info(self):
        """Imprime informações do banco de dados"""
        creds = self.credentials
        
        print("=" * 70)
        print("🗄️  MARABET AI - RDS POSTGRESQL")
        print("=" * 70)
        print()
        print(f"Host:         {creds['host']}")
        print(f"Port:         {creds['port']}")
        print(f"Username:     {creds['username']}")
        print(f"Password:     {'*' * len(creds['password'])}")
        print(f"Engine:       {creds['engine']}")
        print(f"Database:     {self.database_name}")
        print()
        print("Connection String:")
        print("-" * 70)
        print(self.get_connection_string())
        print()
        print("=" * 70)


# Instância global para uso direto
db_config = DatabaseConfig()


# Funções de conveniência
def get_connection_string(database: Optional[str] = None) -> str:
    """Obtém connection string"""
    return db_config.get_connection_string(database)


def get_credentials() -> Dict[str, str]:
    """Obtém credenciais do Secrets Manager"""
    return db_config.credentials


def test_connection() -> bool:
    """Testa conexão com o banco"""
    return db_config.test_connection()


def export_env_file(filepath: str = ".env.rds"):
    """Exporta variáveis para arquivo .env"""
    db_config.export_env_file(filepath)


if __name__ == "__main__":
    """
    Script executável para testar configuração
    
    Uso:
        python db_config.py
    """
    import sys
    
    print("🚀 MaraBet AI - Database Configuration\n")
    
    try:
        # Mostrar informações
        db_config.print_info()
        
        # Testar conexão
        print("\n🔌 Testando conexão...")
        print("-" * 70)
        test_connection()
        
        # Perguntar se quer exportar .env
        print("\n" + "=" * 70)
        response = input("\nExportar para arquivo .env.rds? (s/n): ")
        
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            export_env_file()
            print("\n✅ Configuração concluída!")
        else:
            print("\n✅ Configuração disponível no código")
        
        print("\n" + "=" * 70)
        print("Exemplo de uso:")
        print("-" * 70)
        print("""
from db_config import get_connection_string, get_credentials

# Opção 1: Connection string
DATABASE_URL = get_connection_string()

# Opção 2: Credenciais individuais
creds = get_credentials()
print(f"Host: {creds['host']}")
        """)
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

