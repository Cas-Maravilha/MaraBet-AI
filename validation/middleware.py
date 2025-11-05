#!/usr/bin/env python3
"""
Middleware de Validação para o MaraBet AI
Middleware robusto para validação e sanitização de dados
"""

import json
import logging
from functools import wraps
from flask import request, jsonify, g
from werkzeug.exceptions import BadRequest
from validation.data_models import (
    PredictionRequest, OddsRequest, NotificationRequest, 
    UserRequest, BetRequest, SearchRequest,
    ValidationError, DataSanitizer
)

logger = logging.getLogger(__name__)

class ValidationMiddleware:
    """Middleware de validação de dados"""
    
    def __init__(self, app=None):
        """Inicializa middleware"""
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa middleware na aplicação Flask"""
        self.app = app
        
        # Registrar handlers de erro
        app.register_error_handler(ValidationError, self.handle_validation_error)
        app.register_error_handler(BadRequest, self.handle_bad_request)
        
        # Middleware global
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Middleware executado antes de cada requisição"""
        # Sanitizar headers
        self.sanitize_headers()
        
        # Validar Content-Type para POST/PUT
        if request.method in ['POST', 'PUT', 'PATCH']:
            self.validate_content_type()
        
        # Rate limiting básico por IP
        self.check_basic_rate_limit()
    
    def after_request(self, response):
        """Middleware executado após cada requisição"""
        # Adicionar headers de segurança
        self.add_security_headers(response)
        
        # Log de requisições suspeitas
        self.log_suspicious_requests(response)
        
        return response
    
    def sanitize_headers(self):
        """Sanitiza headers da requisição"""
        # Lista de headers perigosos
        dangerous_headers = [
            'X-Forwarded-For', 'X-Real-IP', 'X-Forwarded-Proto',
            'X-Forwarded-Host', 'X-Forwarded-Port'
        ]
        
        for header in dangerous_headers:
            if header in request.headers:
                value = request.headers[header]
                # Sanitizar valor do header
                sanitized_value = DataSanitizer.sanitize_string(str(value))
                request.headers[header] = sanitized_value
    
    def validate_content_type(self):
        """Valida Content-Type da requisição"""
        content_type = request.content_type
        
        if not content_type:
            raise ValidationError("Content-Type é obrigatório para requisições POST/PUT")
        
        if not content_type.startswith('application/json'):
            raise ValidationError("Content-Type deve ser application/json")
    
    def check_basic_rate_limit(self):
        """Verifica rate limiting básico"""
        # Implementação básica de rate limiting
        # Em produção, usar Redis
        client_ip = request.remote_addr
        
        # Verificar se IP está em blacklist
        if self.is_ip_blacklisted(client_ip):
            raise ValidationError("IP bloqueado", code="IP_BLOCKED")
    
    def is_ip_blacklisted(self, ip: str) -> bool:
        """Verifica se IP está na blacklist"""
        # Implementar blacklist de IPs
        # Em produção, usar Redis ou banco de dados
        blacklisted_ips = [
            '127.0.0.1',  # Exemplo - remover em produção
        ]
        return ip in blacklisted_ips
    
    def add_security_headers(self, response):
        """Adiciona headers de segurança"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
    
    def log_suspicious_requests(self, response):
        """Log de requisições suspeitas"""
        if response.status_code >= 400:
            logger.warning(f"Requisição suspeita: {request.method} {request.path} - {response.status_code}")
    
    def handle_validation_error(self, error):
        """Handler para erros de validação"""
        return jsonify({
            'error': 'Validation Error',
            'message': error.message,
            'field': error.field,
            'code': error.code
        }), 400
    
    def handle_bad_request(self, error):
        """Handler para BadRequest"""
        return jsonify({
            'error': 'Bad Request',
            'message': 'Dados inválidos na requisição',
            'code': 'BAD_REQUEST'
        }), 400

def validate_json_data(model_class):
    """Decorator para validação de dados JSON"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Obter dados JSON
                if not request.is_json:
                    raise ValidationError("Content-Type deve ser application/json")
                
                data = request.get_json()
                if not data:
                    raise ValidationError("Dados JSON são obrigatórios")
                
                # Validar e sanitizar dados
                validated_data = validate_and_sanitize_data(data, model_class)
                
                # Adicionar dados validados ao contexto
                g.validated_data = validated_data
                
                # Executar função original
                return f(*args, **kwargs)
                
            except ValidationError as e:
                return jsonify({
                    'error': 'Validation Error',
                    'message': e.message,
                    'field': e.field,
                    'code': e.code
                }), 400
            except Exception as e:
                logger.error(f"Erro inesperado na validação: {e}")
                return jsonify({
                    'error': 'Internal Server Error',
                    'message': 'Erro interno do servidor'
                }), 500
        
        return decorated_function
    return decorator

def validate_query_params(model_class):
    """Decorator para validação de parâmetros de query"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Obter parâmetros de query
                query_params = dict(request.args)
                
                # Validar e sanitizar parâmetros
                validated_params = validate_and_sanitize_data(query_params, model_class)
                
                # Adicionar parâmetros validados ao contexto
                g.validated_params = validated_params
                
                # Executar função original
                return f(*args, **kwargs)
                
            except ValidationError as e:
                return jsonify({
                    'error': 'Validation Error',
                    'message': e.message,
                    'field': e.field,
                    'code': e.code
                }), 400
            except Exception as e:
                logger.error(f"Erro inesperado na validação: {e}")
                return jsonify({
                    'error': 'Internal Server Error',
                    'message': 'Erro interno do servidor'
                }), 500
        
        return decorated_function
    return decorator

def validate_path_params(param_types: dict):
    """Decorator para validação de parâmetros de path"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Validar parâmetros de path
                for param_name, param_type in param_types.items():
                    if param_name in kwargs:
                        value = kwargs[param_name]
                        
                        # Validar tipo
                        if param_type == 'int':
                            try:
                                kwargs[param_name] = int(value)
                            except (ValueError, TypeError):
                                raise ValidationError(f"Parâmetro {param_name} deve ser um número inteiro")
                        
                        elif param_type == 'float':
                            try:
                                kwargs[param_name] = float(value)
                            except (ValueError, TypeError):
                                raise ValidationError(f"Parâmetro {param_name} deve ser um número")
                        
                        elif param_type == 'str':
                            # Sanitizar string
                            kwargs[param_name] = DataSanitizer.sanitize_string(str(value))
                
                # Executar função original
                return f(*args, **kwargs)
                
            except ValidationError as e:
                return jsonify({
                    'error': 'Validation Error',
                    'message': e.message,
                    'field': e.field,
                    'code': e.code
                }), 400
            except Exception as e:
                logger.error(f"Erro inesperado na validação: {e}")
                return jsonify({
                    'error': 'Internal Server Error',
                    'message': 'Erro interno do servidor'
                }), 500
        
        return decorated_function
    return decorator

def validate_file_upload(allowed_extensions: list, max_size: int = 5 * 1024 * 1024):
    """Decorator para validação de upload de arquivos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Verificar se há arquivo
                if 'file' not in request.files:
                    raise ValidationError("Arquivo é obrigatório")
                
                file = request.files['file']
                
                # Verificar se arquivo foi selecionado
                if file.filename == '':
                    raise ValidationError("Nenhum arquivo selecionado")
                
                # Verificar extensão
                if not file.filename.lower().endswith(tuple(allowed_extensions)):
                    raise ValidationError(f"Extensão de arquivo não permitida. Extensões permitidas: {allowed_extensions}")
                
                # Verificar tamanho
                file.seek(0, 2)  # Ir para o final
                file_size = file.tell()
                file.seek(0)  # Voltar para o início
                
                if file_size > max_size:
                    raise ValidationError(f"Arquivo muito grande. Tamanho máximo: {max_size} bytes")
                
                # Adicionar arquivo validado ao contexto
                g.validated_file = file
                
                # Executar função original
                return f(*args, **kwargs)
                
            except ValidationError as e:
                return jsonify({
                    'error': 'Validation Error',
                    'message': e.message,
                    'field': e.field,
                    'code': e.code
                }), 400
            except Exception as e:
                logger.error(f"Erro inesperado na validação: {e}")
                return jsonify({
                    'error': 'Internal Server Error',
                    'message': 'Erro interno do servidor'
                }), 500
        
        return decorated_function
    return decorator

def validate_and_sanitize_data(data: dict, model_class):
    """Valida e sanitiza dados usando modelo Pydantic"""
    try:
        # Sanitizar dados de entrada
        sanitized_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized_data[key] = DataSanitizer.sanitize_string(value)
            else:
                sanitized_data[key] = value
        
        # Validar com Pydantic
        return model_class(**sanitized_data)
    
    except Exception as e:
        raise ValidationError(f"Erro de validação: {str(e)}")

# Instância global do middleware
validation_middleware = ValidationMiddleware()

if __name__ == "__main__":
    # Teste do middleware
    print("🧪 TESTANDO MIDDLEWARE DE VALIDAÇÃO")
    print("=" * 40)
    
    # Teste de sanitização
    test_string = "<script>alert('xss')</script>Hello World"
    sanitized = DataSanitizer.sanitize_string(test_string)
    print(f"String original: {test_string}")
    print(f"String sanitizada: {sanitized}")
    
    # Teste de validação de email
    try:
        email = DataSanitizer.sanitize_email("test@example.com")
        print(f"✅ Email válido: {email}")
    except Exception as e:
        print(f"❌ Email inválido: {e}")
    
    print("\n🎉 TESTES DO MIDDLEWARE CONCLUÍDOS!")
