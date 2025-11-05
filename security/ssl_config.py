#!/usr/bin/env python3
"""
Configuração SSL/HTTPS para o MaraBet AI
Implementa SSL/TLS seguro para produção
"""

import os
import ssl
from pathlib import Path
from flask import Flask, redirect, request
import logging

logger = logging.getLogger(__name__)

class SSLConfig:
    """Configuração SSL/HTTPS"""
    
    def __init__(self, app=None):
        """Inicializa configuração SSL"""
        self.app = app
        self.ssl_context = None
        self.cert_path = None
        self.key_path = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa SSL na aplicação Flask"""
        self.app = app
        
        # Configurações SSL
        app.config['SECURE_SSL_REDIRECT'] = True
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['CSRF_COOKIE_SECURE'] = True
        app.config['SECURE_BROWSER_XSS_FILTER'] = True
        app.config['SECURE_CONTENT_TYPE_NOSNIFF'] = True
        app.config['SECURE_HSTS_SECONDS'] = 31536000  # 1 ano
        app.config['SECURE_HSTS_INCLUDE_SUBDOMAINS'] = True
        app.config['SECURE_HSTS_PRELOAD'] = True
        
        # Configurar SSL context
        self.setup_ssl_context()
        
        # Configurar redirecionamento HTTPS
        self.setup_https_redirect()
        
        # Configurar headers de segurança
        self.setup_security_headers()
    
    def setup_ssl_context(self):
        """Configura contexto SSL"""
        try:
            # Caminhos dos certificados
            self.cert_path = os.getenv('SSL_CERT_PATH', 'ssl/cert.pem')
            self.key_path = os.getenv('SSL_KEY_PATH', 'ssl/key.pem')
            
            # Verificar se os arquivos existem
            if os.path.exists(self.cert_path) and os.path.exists(self.key_path):
                # Criar contexto SSL
                self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                self.ssl_context.load_cert_chain(self.cert_path, self.key_path)
                
                # Configurações de segurança
                self.ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
                self.ssl_context.options |= ssl.OP_NO_SSLv2
                self.ssl_context.options |= ssl.OP_NO_SSLv3
                self.ssl_context.options |= ssl.OP_NO_TLSv1
                self.ssl_context.options |= ssl.OP_NO_TLSv1_1
                
                logger.info("SSL context configurado com sucesso")
            else:
                logger.warning("Certificados SSL não encontrados. SSL desabilitado.")
                self.ssl_context = None
                
        except Exception as e:
            logger.error(f"Erro ao configurar SSL: {e}")
            self.ssl_context = None
    
    def setup_https_redirect(self):
        """Configura redirecionamento HTTPS"""
        @self.app.before_request
        def force_https():
            """Força redirecionamento para HTTPS"""
            if not request.is_secure and self.app.config.get('SECURE_SSL_REDIRECT'):
                # Verificar se não é localhost
                if request.host != 'localhost' and request.host != '127.0.0.1':
                    url = request.url.replace('http://', 'https://', 1)
                    return redirect(url, code=301)
    
    def setup_security_headers(self):
        """Configura headers de segurança"""
        @self.app.after_request
        def add_security_headers(response):
            """Adiciona headers de segurança"""
            # HSTS
            if self.app.config.get('SECURE_HSTS_SECONDS'):
                response.headers['Strict-Transport-Security'] = (
                    f"max-age={self.app.config['SECURE_HSTS_SECONDS']}; "
                    f"includeSubDomains; preload"
                )
            
            # XSS Protection
            if self.app.config.get('SECURE_BROWSER_XSS_FILTER'):
                response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Content Type Options
            if self.app.config.get('SECURE_CONTENT_TYPE_NOSNIFF'):
                response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # Frame Options
            response.headers['X-Frame-Options'] = 'DENY'
            
            # Content Security Policy
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
            
            # Referrer Policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Permissions Policy
            response.headers['Permissions-Policy'] = (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=(), "
                "vibrate=(), "
                "fullscreen=(self), "
                "sync-xhr=()"
            )
            
            return response
    
    def get_ssl_context(self):
        """Retorna contexto SSL"""
        return self.ssl_context
    
    def is_ssl_enabled(self):
        """Verifica se SSL está habilitado"""
        return self.ssl_context is not None
    
    def generate_self_signed_cert(self, domain='localhost'):
        """Gera certificado auto-assinado para desenvolvimento"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from datetime import datetime, timedelta
            
            # Criar diretório SSL
            ssl_dir = Path('ssl')
            ssl_dir.mkdir(exist_ok=True)
            
            # Gerar chave privada
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Criar certificado
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "BR"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "São Paulo"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "São Paulo"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MaraBet AI"),
                x509.NameAttribute(NameOID.COMMON_NAME, domain),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(domain),
                    x509.DNSName("localhost"),
                    x509.IPAddress("127.0.0.1"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Salvar certificado
            cert_path = ssl_dir / 'cert.pem'
            with open(cert_path, 'wb') as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Salvar chave privada
            key_path = ssl_dir / 'key.pem'
            with open(key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info(f"Certificado auto-assinado gerado: {cert_path}")
            return str(cert_path), str(key_path)
            
        except ImportError:
            logger.error("cryptography não instalado. Execute: pip install cryptography")
            return None, None
        except Exception as e:
            logger.error(f"Erro ao gerar certificado: {e}")
            return None, None

def create_ssl_app(app):
    """Cria aplicação com SSL configurado"""
    ssl_config = SSLConfig(app)
    return ssl_config

# Função para verificar configuração SSL
def check_ssl_config():
    """Verifica configuração SSL"""
    ssl_config = SSLConfig()
    
    return {
        'ssl_enabled': ssl_config.is_ssl_enabled(),
        'cert_path': ssl_config.cert_path,
        'key_path': ssl_config.key_path,
        'cert_exists': os.path.exists(ssl_config.cert_path) if ssl_config.cert_path else False,
        'key_exists': os.path.exists(ssl_config.key_path) if ssl_config.key_path else False
    }

if __name__ == "__main__":
    # Teste da configuração SSL
    print("🧪 TESTANDO CONFIGURAÇÃO SSL")
    print("=" * 40)
    
    # Verificar configuração
    config = check_ssl_config()
    
    print(f"SSL Habilitado: {config['ssl_enabled']}")
    print(f"Certificado: {config['cert_path']}")
    print(f"Chave: {config['key_path']}")
    print(f"Certificado existe: {config['cert_exists']}")
    print(f"Chave existe: {config['key_exists']}")
    
    if not config['ssl_enabled']:
        print("\n⚠️ SSL não configurado!")
        print("Para configurar SSL:")
        print("1. Obtenha certificados SSL válidos")
        print("2. Configure SSL_CERT_PATH e SSL_KEY_PATH")
        print("3. Ou gere certificado auto-assinado para desenvolvimento")
        
        # Gerar certificado auto-assinado para teste
        ssl_config = SSLConfig()
        cert_path, key_path = ssl_config.generate_self_signed_cert()
        
        if cert_path and key_path:
            print(f"\n✅ Certificado auto-assinado gerado:")
            print(f"   Certificado: {cert_path}")
            print(f"   Chave: {key_path}")
            print("   ⚠️ Use apenas para desenvolvimento!")
        else:
            print("\n❌ Falha ao gerar certificado auto-assinado")
    else:
        print("\n✅ SSL configurado corretamente!")
