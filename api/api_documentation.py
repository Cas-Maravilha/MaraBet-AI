#!/usr/bin/env python3
"""
Sistema de Documentação Automática da API
Decorators e utilitários para documentação automática
"""

from functools import wraps
from typing import Dict, List, Any, Optional, Callable
import inspect
import json
from datetime import datetime

class APIDocumentation:
    """Sistema de documentação automática da API"""
    
    def __init__(self):
        """Inicializa sistema de documentação"""
        self.endpoints = {}
        self.schemas = {}
        self.examples = {}
    
    def document_endpoint(self, 
                         summary: str,
                         description: str = "",
                         tags: List[str] = None,
                         parameters: List[Dict] = None,
                         responses: Dict[str, Dict] = None,
                         request_body: Dict = None,
                         security: List[Dict] = None,
                         deprecated: bool = False):
        """Decorator para documentar endpoint"""
        def decorator(func):
            # Extrair informações da função
            func_name = func.__name__
            module_name = func.__module__
            endpoint_id = f"{module_name}.{func_name}"
            
            # Obter assinatura da função
            sig = inspect.signature(func)
            func_params = list(sig.parameters.keys())
            
            # Documentar endpoint
            endpoint_doc = {
                "function": func_name,
                "module": module_name,
                "summary": summary,
                "description": description,
                "tags": tags or [],
                "parameters": parameters or [],
                "responses": responses or {},
                "request_body": request_body,
                "security": security or [],
                "deprecated": deprecated,
                "function_parameters": func_params,
                "docstring": func.__doc__ or "",
                "created_at": datetime.now().isoformat()
            }
            
            self.endpoints[endpoint_id] = endpoint_doc
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Log da chamada da API
                self._log_api_call(func_name, args, kwargs)
                
                try:
                    result = func(*args, **kwargs)
                    self._log_api_response(func_name, result, success=True)
                    return result
                except Exception as e:
                    self._log_api_response(func_name, str(e), success=False)
                    raise
            
            return wrapper
        return decorator
    
    def document_schema(self, schema_name: str, schema_definition: Dict[str, Any]):
        """Documenta schema de dados"""
        self.schemas[schema_name] = {
            "name": schema_name,
            "definition": schema_definition,
            "created_at": datetime.now().isoformat()
        }
    
    def add_example(self, endpoint_id: str, example_name: str, 
                   request: Dict = None, response: Dict = None):
        """Adiciona exemplo para endpoint"""
        if endpoint_id not in self.examples:
            self.examples[endpoint_id] = []
        
        example = {
            "name": example_name,
            "request": request,
            "response": response,
            "created_at": datetime.now().isoformat()
        }
        
        self.examples[endpoint_id].append(example)
    
    def _log_api_call(self, func_name: str, args: tuple, kwargs: dict):
        """Log de chamada da API"""
        print(f"🔍 API Call: {func_name}")
        print(f"   Args: {args}")
        print(f"   Kwargs: {kwargs}")
    
    def _log_api_response(self, func_name: str, result: Any, success: bool):
        """Log de resposta da API"""
        status = "✅ Success" if success else "❌ Error"
        print(f"📤 API Response: {func_name} - {status}")
        if success:
            print(f"   Result: {type(result).__name__}")
        else:
            print(f"   Error: {result}")
    
    def get_endpoint_documentation(self, endpoint_id: str) -> Optional[Dict]:
        """Obtém documentação de um endpoint"""
        return self.endpoints.get(endpoint_id)
    
    def get_all_endpoints(self) -> Dict[str, Dict]:
        """Obtém documentação de todos os endpoints"""
        return self.endpoints
    
    def get_schema_documentation(self, schema_name: str) -> Optional[Dict]:
        """Obtém documentação de um schema"""
        return self.schemas.get(schema_name)
    
    def get_all_schemas(self) -> Dict[str, Dict]:
        """Obtém documentação de todos os schemas"""
        return self.schemas
    
    def get_examples_for_endpoint(self, endpoint_id: str) -> List[Dict]:
        """Obtém exemplos para um endpoint"""
        return self.examples.get(endpoint_id, [])
    
    def generate_openapi_from_docs(self) -> Dict[str, Any]:
        """Gera especificação OpenAPI a partir da documentação"""
        paths = {}
        
        for endpoint_id, doc in self.endpoints.items():
            # Converter documentação para formato OpenAPI
            path_item = self._convert_to_openapi_path_item(doc)
            
            # Adicionar aos paths (simplificado)
            paths[f"/api/{doc['function']}"] = path_item
        
        return {
            "openapi": "3.0.3",
            "info": {
                "title": "MaraBet AI API (Auto-generated)",
                "version": "1.0.0"
            },
            "paths": paths,
            "components": {
                "schemas": {
                    name: schema["definition"] 
                    for name, schema in self.schemas.items()
                }
            }
        }
    
    def _convert_to_openapi_path_item(self, doc: Dict) -> Dict:
        """Converte documentação para formato OpenAPI"""
        return {
            "get": {
                "summary": doc["summary"],
                "description": doc["description"],
                "tags": doc["tags"],
                "parameters": doc["parameters"],
                "responses": doc["responses"]
            }
        }
    
    def export_documentation(self, format: str = "json") -> str:
        """Exporta documentação em formato específico"""
        if format == "json":
            return json.dumps({
                "endpoints": self.endpoints,
                "schemas": self.schemas,
                "examples": self.examples
            }, indent=2, ensure_ascii=False)
        elif format == "markdown":
            return self._generate_markdown_docs()
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    def _generate_markdown_docs(self) -> str:
        """Gera documentação em Markdown"""
        md = "# MaraBet AI API Documentation\n\n"
        md += f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Endpoints
        md += "## Endpoints\n\n"
        for endpoint_id, doc in self.endpoints.items():
            md += f"### {doc['function']}\n"
            md += f"**Resumo:** {doc['summary']}\n\n"
            md += f"**Descrição:** {doc['description']}\n\n"
            
            if doc['tags']:
                md += f"**Tags:** {', '.join(doc['tags'])}\n\n"
            
            if doc['parameters']:
                md += "**Parâmetros:**\n"
                for param in doc['parameters']:
                    md += f"- `{param.get('name', 'N/A')}`: {param.get('description', 'N/A')}\n"
                md += "\n"
            
            if doc['responses']:
                md += "**Respostas:**\n"
                for status, response in doc['responses'].items():
                    md += f"- `{status}`: {response.get('description', 'N/A')}\n"
                md += "\n"
            
            md += "---\n\n"
        
        return md

# Instância global
api_docs = APIDocumentation()

# Decorators de conveniência
def api_endpoint(summary: str, description: str = "", tags: List[str] = None):
    """Decorator simplificado para documentar endpoint"""
    return api_docs.document_endpoint(
        summary=summary,
        description=description,
        tags=tags or []
    )

def api_parameter(name: str, param_type: str, description: str, 
                 required: bool = False, example: Any = None) -> Dict:
    """Cria parâmetro para documentação"""
    param = {
        "name": name,
        "in": "query",
        "description": description,
        "required": required,
        "schema": {"type": param_type}
    }
    
    if example is not None:
        param["example"] = example
    
    return param

def api_response(status_code: str, description: str, 
                schema_ref: str = None, example: Dict = None) -> Dict:
    """Cria resposta para documentação"""
    response = {
        "description": description
    }
    
    if schema_ref:
        response["content"] = {
            "application/json": {
                "schema": {"$ref": f"#/components/schemas/{schema_ref}"}
            }
        }
    
    if example:
        if "content" not in response:
            response["content"] = {"application/json": {}}
        response["content"]["application/json"]["example"] = example
    
    return response

def api_request_body(schema_ref: str, description: str = "", 
                    example: Dict = None) -> Dict:
    """Cria request body para documentação"""
    body = {
        "required": True,
        "content": {
            "application/json": {
                "schema": {"$ref": f"#/components/schemas/{schema_ref}"}
            }
        }
    }
    
    if description:
        body["description"] = description
    
    if example:
        body["content"]["application/json"]["example"] = example
    
    return body

# Exemplos de uso
if __name__ == "__main__":
    # Teste do sistema de documentação
    print("🧪 TESTANDO SISTEMA DE DOCUMENTAÇÃO")
    print("=" * 40)
    
    # Exemplo de endpoint documentado
    @api_docs.document_endpoint(
        summary="Obter predições de partida",
        description="Retorna predições de uma partida específica",
        tags=["Predictions"],
        parameters=[
            api_parameter("match_id", "string", "ID da partida", True, "39_12345"),
            api_parameter("include_odds", "boolean", "Incluir odds na resposta", False, True)
        ],
        responses={
            "200": api_response("200", "Predições encontradas", "PredictionResponse"),
            "404": api_response("404", "Partida não encontrada", "ErrorResponse")
        }
    )
    def get_match_predictions(match_id: str, include_odds: bool = False):
        """Obtém predições de uma partida"""
        return {
            "match_id": match_id,
            "predictions": {
                "home_win": 0.45,
                "draw": 0.30,
                "away_win": 0.25
            },
            "confidence": 0.85
        }
    
    # Testar função documentada
    result = get_match_predictions("39_12345", True)
    print(f"Resultado: {result}")
    
    # Verificar documentação
    endpoint_doc = api_docs.get_endpoint_documentation("__main__.get_match_predictions")
    if endpoint_doc:
        print(f"\nDocumentação do endpoint:")
        print(f"  Resumo: {endpoint_doc['summary']}")
        print(f"  Tags: {endpoint_doc['tags']}")
        print(f"  Parâmetros: {len(endpoint_doc['parameters'])}")
        print(f"  Respostas: {len(endpoint_doc['responses'])}")
    
    # Exportar documentação
    json_docs = api_docs.export_documentation("json")
    print(f"\nDocumentação JSON: {len(json_docs)} caracteres")
    
    markdown_docs = api_docs.export_documentation("markdown")
    print(f"Documentação Markdown: {len(markdown_docs)} caracteres")
    
    print("\n🎉 TESTES DE DOCUMENTAÇÃO CONCLUÍDOS!")
