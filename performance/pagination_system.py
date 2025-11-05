#!/usr/bin/env python3
"""
Sistema de Paginação para o MaraBet AI
Paginação eficiente com metadados completos
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from math import ceil
import logging

logger = logging.getLogger(__name__)

@dataclass
class PaginationMeta:
    """Metadados de paginação"""
    page: int
    per_page: int
    total: int
    pages: int
    has_prev: bool
    has_next: bool
    prev_num: Optional[int]
    next_num: Optional[int]

@dataclass
class PaginatedResult:
    """Resultado paginado"""
    items: List[Any]
    meta: PaginationMeta

class PaginationManager:
    """Gerenciador de paginação"""
    
    def __init__(self, default_per_page: int = 20, max_per_page: int = 100):
        """Inicializa gerenciador de paginação"""
        self.default_per_page = default_per_page
        self.max_per_page = max_per_page
    
    def paginate(self, items: List[Any], page: int = 1, per_page: int = None) -> PaginatedResult:
        """Pagina uma lista de itens"""
        # Validar parâmetros
        page = max(1, page)
        per_page = per_page or self.default_per_page
        per_page = min(per_page, self.max_per_page)
        per_page = max(1, per_page)
        
        total = len(items)
        pages = ceil(total / per_page) if total > 0 else 1
        
        # Ajustar página se necessário
        page = min(page, pages)
        
        # Calcular índices
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Obter itens da página
        paginated_items = items[start_idx:end_idx]
        
        # Criar metadados
        meta = PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            pages=pages,
            has_prev=page > 1,
            has_next=page < pages,
            prev_num=page - 1 if page > 1 else None,
            next_num=page + 1 if page < pages else None
        )
        
        return PaginatedResult(items=paginated_items, meta=meta)
    
    def paginate_query(self, query, page: int = 1, per_page: int = None) -> PaginatedResult:
        """Pagina uma query de banco de dados"""
        # Validar parâmetros
        page = max(1, page)
        per_page = per_page or self.default_per_page
        per_page = min(per_page, self.max_per_page)
        per_page = max(1, per_page)
        
        # Contar total de registros
        total = query.count()
        pages = ceil(total / per_page) if total > 0 else 1
        
        # Ajustar página se necessário
        page = min(page, pages)
        
        # Calcular offset
        offset = (page - 1) * per_page
        
        # Obter itens da página
        paginated_items = query.offset(offset).limit(per_page).all()
        
        # Criar metadados
        meta = PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            pages=pages,
            has_prev=page > 1,
            has_next=page < pages,
            prev_num=page - 1 if page > 1 else None,
            next_num=page + 1 if page < pages else None
        )
        
        return PaginatedResult(items=paginated_items, meta=meta)
    
    def create_links(self, meta: PaginationMeta, base_url: str, params: Dict[str, Any] = None) -> Dict[str, str]:
        """Cria links de navegação"""
        params = params or {}
        links = {}
        
        # Link da página atual
        current_params = params.copy()
        current_params['page'] = meta.page
        current_params['per_page'] = meta.per_page
        links['self'] = self._build_url(base_url, current_params)
        
        # Link da primeira página
        if meta.page > 1:
            first_params = params.copy()
            first_params['page'] = 1
            first_params['per_page'] = meta.per_page
            links['first'] = self._build_url(base_url, first_params)
        
        # Link da última página
        if meta.page < meta.pages:
            last_params = params.copy()
            last_params['page'] = meta.pages
            last_params['per_page'] = meta.per_page
            links['last'] = self._build_url(base_url, last_params)
        
        # Link da página anterior
        if meta.has_prev:
            prev_params = params.copy()
            prev_params['page'] = meta.prev_num
            prev_params['per_page'] = meta.per_page
            links['prev'] = self._build_url(base_url, prev_params)
        
        # Link da próxima página
        if meta.has_next:
            next_params = params.copy()
            next_params['page'] = meta.next_num
            next_params['per_page'] = meta.per_page
            links['next'] = self._build_url(base_url, next_params)
        
        return links
    
    def _build_url(self, base_url: str, params: Dict[str, Any]) -> str:
        """Constrói URL com parâmetros"""
        if not params:
            return base_url
        
        param_strings = []
        for key, value in params.items():
            if value is not None:
                param_strings.append(f"{key}={value}")
        
        separator = "&" if "?" in base_url else "?"
        return f"{base_url}{separator}{'&'.join(param_strings)}"
    
    def to_dict(self, result: PaginatedResult, base_url: str = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Converte resultado paginado para dicionário"""
        response = {
            "items": result.items,
            "pagination": {
                "page": result.meta.page,
                "per_page": result.meta.per_page,
                "total": result.meta.total,
                "pages": result.meta.pages,
                "has_prev": result.meta.has_prev,
                "has_next": result.meta.has_next,
                "prev_num": result.meta.prev_num,
                "next_num": result.meta.next_num
            }
        }
        
        # Adicionar links se base_url fornecida
        if base_url:
            response["links"] = self.create_links(result.meta, base_url, params)
        
        return response

class CursorPagination:
    """Paginação baseada em cursor para grandes datasets"""
    
    def __init__(self, cursor_field: str = "id", default_limit: int = 20, max_limit: int = 100):
        """Inicializa paginação por cursor"""
        self.cursor_field = cursor_field
        self.default_limit = default_limit
        self.max_limit = max_limit
    
    def paginate(self, query, cursor: str = None, limit: int = None, direction: str = "next") -> Dict[str, Any]:
        """Pagina query usando cursor"""
        limit = limit or self.default_limit
        limit = min(limit, self.max_limit)
        limit = max(1, limit)
        
        # Aplicar filtro de cursor
        if cursor:
            if direction == "next":
                query = query.filter(getattr(query.column_descriptions[0]['entity'], self.cursor_field) > cursor)
            else:  # prev
                query = query.filter(getattr(query.column_descriptions[0]['entity'], self.cursor_field) < cursor)
        
        # Ordenar por cursor field
        query = query.order_by(getattr(query.column_descriptions[0]['entity'], self.cursor_field))
        
        # Obter itens
        items = query.limit(limit + 1).all()  # +1 para verificar se há próxima página
        
        # Verificar se há próxima página
        has_next = len(items) > limit
        if has_next:
            items = items[:-1]  # Remover item extra
        
        # Obter cursor do último item
        next_cursor = None
        if items and has_next:
            next_cursor = str(getattr(items[-1], self.cursor_field))
        
        return {
            "items": items,
            "next_cursor": next_cursor,
            "has_next": has_next,
            "limit": limit
        }

class SearchPagination:
    """Paginação para resultados de busca"""
    
    def __init__(self, default_per_page: int = 20):
        """Inicializa paginação de busca"""
        self.default_per_page = default_per_page
    
    def paginate_search(self, search_results: List[Dict], page: int = 1, per_page: int = None) -> Dict[str, Any]:
        """Pagina resultados de busca"""
        per_page = per_page or self.default_per_page
        per_page = min(per_page, 100)  # Limite para busca
        per_page = max(1, per_page)
        
        page = max(1, page)
        total = len(search_results)
        pages = ceil(total / per_page) if total > 0 else 1
        page = min(page, pages)
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_items = search_results[start_idx:end_idx]
        
        return {
            "items": paginated_items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages,
                "has_prev": page > 1,
                "has_next": page < pages
            },
            "search_meta": {
                "query_time": 0.0,  # Será preenchido pelo sistema de busca
                "total_found": total
            }
        }

# Instância global
pagination_manager = PaginationManager()

# Decorators para paginação automática
def paginate_results(default_per_page: int = 20):
    """Decorator para paginação automática de endpoints"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extrair parâmetros de paginação
            page = kwargs.get('page', 1)
            per_page = kwargs.get('per_page', default_per_page)
            
            # Remover parâmetros de paginação dos kwargs
            kwargs.pop('page', None)
            kwargs.pop('per_page', None)
            
            # Executar função original
            result = func(*args, **kwargs)
            
            # Se resultado for lista, paginar
            if isinstance(result, list):
                paginated = pagination_manager.paginate(result, page, per_page)
                return pagination_manager.to_dict(paginated)
            
            return result
        return wrapper
    return decorator

def paginate_query(default_per_page: int = 20):
    """Decorator para paginação automática de queries"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extrair parâmetros de paginação
            page = kwargs.get('page', 1)
            per_page = kwargs.get('per_page', default_per_page)
            
            # Remover parâmetros de paginação dos kwargs
            kwargs.pop('page', None)
            kwargs.pop('per_page', None)
            
            # Executar função original
            query = func(*args, **kwargs)
            
            # Se resultado for query, paginar
            if hasattr(query, 'count') and hasattr(query, 'offset'):
                paginated = pagination_manager.paginate_query(query, page, per_page)
                return pagination_manager.to_dict(paginated)
            
            return query
        return wrapper
    return decorator

if __name__ == "__main__":
    # Teste do sistema de paginação
    print("🧪 TESTANDO SISTEMA DE PAGINAÇÃO")
    print("=" * 40)
    
    # Dados de teste
    test_items = [f"Item {i}" for i in range(1, 101)]  # 100 itens
    
    # Teste de paginação básica
    result = pagination_manager.paginate(test_items, page=1, per_page=20)
    print(f"Página 1: {len(result.items)} itens")
    print(f"Total: {result.meta.total}, Páginas: {result.meta.pages}")
    print(f"Tem anterior: {result.meta.has_prev}, Tem próximo: {result.meta.has_next}")
    
    # Teste de paginação avançada
    result = pagination_manager.paginate(test_items, page=3, per_page=15)
    print(f"\nPágina 3 (15 por página): {len(result.items)} itens")
    print(f"Página anterior: {result.meta.prev_num}, Próxima: {result.meta.next_num}")
    
    # Teste de conversão para dicionário
    dict_result = pagination_manager.to_dict(result, "http://api.example.com/items")
    print(f"\nResultado em dicionário:")
    print(f"  Items: {len(dict_result['items'])}")
    print(f"  Links: {list(dict_result['links'].keys())}")
    
    # Teste de paginação de busca
    search_pagination = SearchPagination()
    search_results = [{"id": i, "name": f"Result {i}"} for i in range(1, 51)]
    
    search_result = search_pagination.paginate_search(search_results, page=2, per_page=10)
    print(f"\nBusca paginada:")
    print(f"  Items: {len(search_result['items'])}")
    print(f"  Página: {search_result['pagination']['page']}")
    print(f"  Total: {search_result['pagination']['total']}")
    
    print("\n🎉 TESTES DE PAGINAÇÃO CONCLUÍDOS!")
