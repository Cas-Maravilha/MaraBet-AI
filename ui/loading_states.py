#!/usr/bin/env python3
"""
Sistema de Loading States para o MaraBet AI
Estados de carregamento para melhorar UX
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class LoadingState(Enum):
    """Estados de carregamento"""
    IDLE = "idle"
    LOADING = "loading"
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"

@dataclass
class LoadingInfo:
    """Informações de carregamento"""
    operation_id: str
    state: LoadingState
    message: str
    progress: float  # 0.0 a 1.0
    start_time: float
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

class LoadingManager:
    """Gerenciador de estados de carregamento"""
    
    def __init__(self):
        """Inicializa gerenciador de loading"""
        self.active_operations: Dict[str, LoadingInfo] = {}
        self.completed_operations: List[LoadingInfo] = []
        self.callbacks: Dict[str, List[Callable]] = {}
    
    def start_operation(self, operation_id: str, message: str = "Carregando...", 
                       metadata: Dict[str, Any] = None) -> LoadingInfo:
        """Inicia uma operação de carregamento"""
        loading_info = LoadingInfo(
            operation_id=operation_id,
            state=LoadingState.LOADING,
            message=message,
            progress=0.0,
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        self.active_operations[operation_id] = loading_info
        self._notify_callbacks(operation_id, loading_info)
        
        logger.debug(f"Operação iniciada: {operation_id}")
        return loading_info
    
    def update_progress(self, operation_id: str, progress: float, message: str = None):
        """Atualiza progresso de uma operação"""
        if operation_id not in self.active_operations:
            logger.warning(f"Operação não encontrada: {operation_id}")
            return
        
        loading_info = self.active_operations[operation_id]
        loading_info.progress = max(0.0, min(1.0, progress))
        
        if message:
            loading_info.message = message
        
        self._notify_callbacks(operation_id, loading_info)
        logger.debug(f"Progresso atualizado: {operation_id} - {progress:.1%}")
    
    def complete_operation(self, operation_id: str, success: bool = True, 
                         message: str = None, error_message: str = None):
        """Completa uma operação"""
        if operation_id not in self.active_operations:
            logger.warning(f"Operação não encontrada: {operation_id}")
            return
        
        loading_info = self.active_operations[operation_id]
        loading_info.state = LoadingState.SUCCESS if success else LoadingState.ERROR
        loading_info.progress = 1.0
        loading_info.end_time = time.time()
        
        if message:
            loading_info.message = message
        
        if error_message:
            loading_info.error_message = error_message
        
        # Mover para operações completadas
        self.completed_operations.append(loading_info)
        del self.active_operations[operation_id]
        
        self._notify_callbacks(operation_id, loading_info)
        logger.debug(f"Operação completada: {operation_id} - {'Sucesso' if success else 'Erro'}")
    
    def get_operation_status(self, operation_id: str) -> Optional[LoadingInfo]:
        """Obtém status de uma operação"""
        if operation_id in self.active_operations:
            return self.active_operations[operation_id]
        
        # Procurar em operações completadas
        for op in reversed(self.completed_operations):
            if op.operation_id == operation_id:
                return op
        
        return None
    
    def get_active_operations(self) -> List[LoadingInfo]:
        """Obtém operações ativas"""
        return list(self.active_operations.values())
    
    def is_loading(self, operation_id: str = None) -> bool:
        """Verifica se há operações carregando"""
        if operation_id:
            return operation_id in self.active_operations
        
        return len(self.active_operations) > 0
    
    def add_callback(self, operation_id: str, callback: Callable):
        """Adiciona callback para uma operação"""
        if operation_id not in self.callbacks:
            self.callbacks[operation_id] = []
        self.callbacks[operation_id].append(callback)
    
    def _notify_callbacks(self, operation_id: str, loading_info: LoadingInfo):
        """Notifica callbacks de uma operação"""
        if operation_id in self.callbacks:
            for callback in self.callbacks[operation_id]:
                try:
                    callback(loading_info)
                except Exception as e:
                    logger.error(f"Erro no callback {operation_id}: {e}")
    
    def clear_completed_operations(self, older_than_seconds: int = 300):
        """Limpa operações completadas antigas"""
        cutoff_time = time.time() - older_than_seconds
        self.completed_operations = [
            op for op in self.completed_operations 
            if op.end_time and op.end_time > cutoff_time
        ]
        logger.debug(f"Operações completadas limpas: {len(self.completed_operations)} restantes")

class LoadingStates:
    """Estados de carregamento específicos do MaraBet AI"""
    
    def __init__(self):
        """Inicializa estados de carregamento"""
        self.manager = LoadingManager()
        self.operation_templates = {
            'predictions': {
                'message': 'Gerando predições...',
                'steps': [
                    'Coletando dados da partida',
                    'Processando estatísticas',
                    'Executando modelo de ML',
                    'Calculando probabilidades',
                    'Finalizando predições'
                ]
            },
            'odds': {
                'message': 'Buscando odds...',
                'steps': [
                    'Conectando com bookmakers',
                    'Coletando odds atuais',
                    'Processando dados',
                    'Calculando valores',
                    'Finalizando busca'
                ]
            },
            'analysis': {
                'message': 'Analisando dados...',
                'steps': [
                    'Carregando histórico',
                    'Processando métricas',
                    'Calculando ROI',
                    'Gerando insights',
                    'Finalizando análise'
                ]
            },
            'backup': {
                'message': 'Criando backup...',
                'steps': [
                    'Preparando dados',
                    'Comprimindo arquivos',
                    'Validando integridade',
                    'Salvando backup',
                    'Finalizando processo'
                ]
            }
        }
    
    def start_prediction_loading(self, match_id: str) -> str:
        """Inicia carregamento de predições"""
        operation_id = f"predictions_{match_id}_{int(time.time())}"
        template = self.operation_templates['predictions']
        
        self.manager.start_operation(
            operation_id=operation_id,
            message=template['message'],
            metadata={'match_id': match_id, 'type': 'predictions', 'steps': template['steps']}
        )
        
        return operation_id
    
    def start_odds_loading(self, match_id: str) -> str:
        """Inicia carregamento de odds"""
        operation_id = f"odds_{match_id}_{int(time.time())}"
        template = self.operation_templates['odds']
        
        self.manager.start_operation(
            operation_id=operation_id,
            message=template['message'],
            metadata={'match_id': match_id, 'type': 'odds', 'steps': template['steps']}
        )
        
        return operation_id
    
    def start_analysis_loading(self, analysis_type: str) -> str:
        """Inicia carregamento de análise"""
        operation_id = f"analysis_{analysis_type}_{int(time.time())}"
        template = self.operation_templates['analysis']
        
        self.manager.start_operation(
            operation_id=operation_id,
            message=template['message'],
            metadata={'analysis_type': analysis_type, 'type': 'analysis', 'steps': template['steps']}
        )
        
        return operation_id
    
    def start_backup_loading(self) -> str:
        """Inicia carregamento de backup"""
        operation_id = f"backup_{int(time.time())}"
        template = self.operation_templates['backup']
        
        self.manager.start_operation(
            operation_id=operation_id,
            message=template['message'],
            metadata={'type': 'backup', 'steps': template['steps']}
        )
        
        return operation_id
    
    def simulate_loading_steps(self, operation_id: str, total_steps: int = 5):
        """Simula carregamento com passos"""
        def loading_worker():
            for i in range(total_steps + 1):
                progress = i / total_steps
                step_message = f"Passo {i + 1} de {total_steps}"
                
                self.manager.update_progress(operation_id, progress, step_message)
                time.sleep(0.5)  # Simular tempo de processamento
            
            self.manager.complete_operation(operation_id, success=True, message="Concluído!")
        
        thread = threading.Thread(target=loading_worker)
        thread.daemon = True
        thread.start()
    
    def get_loading_status(self, operation_id: str) -> Dict[str, Any]:
        """Obtém status de carregamento formatado"""
        loading_info = self.manager.get_operation_status(operation_id)
        
        if not loading_info:
            return {"status": "not_found"}
        
        duration = 0
        if loading_info.end_time:
            duration = loading_info.end_time - loading_info.start_time
        elif loading_info.state == LoadingState.LOADING:
            duration = time.time() - loading_info.start_time
        
        return {
            "operation_id": loading_info.operation_id,
            "state": loading_info.state.value,
            "message": loading_info.message,
            "progress": loading_info.progress,
            "duration": round(duration, 2),
            "error_message": loading_info.error_message,
            "metadata": loading_info.metadata
        }
    
    def get_all_loading_status(self) -> Dict[str, Any]:
        """Obtém status de todas as operações"""
        active_ops = self.manager.get_active_operations()
        completed_ops = self.manager.completed_operations[-10:]  # Últimas 10
        
        return {
            "active_operations": len(active_ops),
            "completed_operations": len(completed_ops),
            "is_loading": self.manager.is_loading(),
            "operations": {
                "active": [self.get_loading_status(op.operation_id) for op in active_ops],
                "recent": [self.get_loading_status(op.operation_id) for op in completed_ops]
            }
        }

# Decorator para operações com loading
def with_loading(operation_type: str, message: str = None):
    """Decorator para adicionar loading a operações"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            loading_states = LoadingStates()
            
            # Iniciar loading
            if operation_type == 'predictions':
                operation_id = loading_states.start_prediction_loading(kwargs.get('match_id', 'unknown'))
            elif operation_type == 'odds':
                operation_id = loading_states.start_odds_loading(kwargs.get('match_id', 'unknown'))
            elif operation_type == 'analysis':
                operation_id = loading_states.start_analysis_loading(kwargs.get('analysis_type', 'general'))
            elif operation_type == 'backup':
                operation_id = loading_states.start_backup_loading()
            else:
                operation_id = loading_states.manager.start_operation(
                    f"{operation_type}_{int(time.time())}",
                    message or f"Executando {operation_type}..."
                )
            
            try:
                # Simular loading steps
                loading_states.simulate_loading_steps(operation_id)
                
                # Executar função original
                result = func(*args, **kwargs)
                
                # Completar com sucesso
                loading_states.manager.complete_operation(
                    operation_id, 
                    success=True, 
                    message="Operação concluída com sucesso!"
                )
                
                return result
                
            except Exception as e:
                # Completar com erro
                loading_states.manager.complete_operation(
                    operation_id, 
                    success=False, 
                    error_message=str(e)
                )
                raise
        
        return wrapper
    return decorator

# Instância global
loading_states = LoadingStates()

if __name__ == "__main__":
    # Teste do sistema de loading states
    print("🧪 TESTANDO SISTEMA DE LOADING STATES")
    print("=" * 40)
    
    # Testar operação de predições
    operation_id = loading_states.start_prediction_loading("39_12345")
    print(f"Operação iniciada: {operation_id}")
    
    # Simular carregamento
    loading_states.simulate_loading_steps(operation_id, 5)
    
    # Aguardar um pouco
    time.sleep(3)
    
    # Verificar status
    status = loading_states.get_loading_status(operation_id)
    print(f"Status: {status['state']}")
    print(f"Progresso: {status['progress']:.1%}")
    print(f"Mensagem: {status['message']}")
    
    # Testar decorator
    @with_loading('predictions')
    def test_prediction_function(match_id: str):
        time.sleep(1)  # Simular processamento
        return {"prediction": "home_win", "confidence": 0.75}
    
    print(f"\nTestando decorator:")
    result = test_prediction_function("39_12346")
    print(f"Resultado: {result}")
    
    # Status geral
    all_status = loading_states.get_all_loading_status()
    print(f"\nStatus geral:")
    print(f"  Operações ativas: {all_status['active_operations']}")
    print(f"  Carregando: {all_status['is_loading']}")
    
    print("\n🎉 TESTES DE LOADING STATES CONCLUÍDOS!")
