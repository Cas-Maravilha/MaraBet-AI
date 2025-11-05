"""
Tarefas Celery para otimização de hiperparâmetros
Permite execução assíncrona de otimizações longas
"""

from celery import Celery
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import logging
import json
from datetime import datetime
import os
from pathlib import Path

from optimization.optimizers.hyperparameter_optimizer import HyperparameterOptimizer, MultiModelOptimizer
from optimization.optimizers.model_optimizers import ModelOptimizerFactory
from optimization.validation.time_series_cv import create_time_series_cv

logger = logging.getLogger(__name__)

# Configurar Celery
from tasks.celery_app import celery_app

@celery_app.task(bind=True, name='optimization.optimize_single_model')
def optimize_single_model(
    self,
    model_name: str,
    X_data: List[List[float]],
    y_data: List[int],
    study_name: str,
    n_trials: int = 100,
    timeout: Optional[int] = None,
    cv_strategy: str = "time_series",
    cv_params: Optional[Dict[str, Any]] = None,
    scoring: str = "accuracy",
    random_state: Optional[int] = None
) -> Dict[str, Any]:
    """
    Otimiza hiperparâmetros de um único modelo
    
    Args:
        model_name: Nome do modelo para otimizar
        X_data: Dados de features (lista de listas)
        y_data: Dados de target (lista)
        study_name: Nome do estudo
        n_trials: Número de tentativas
        timeout: Timeout em segundos
        cv_strategy: Estratégia de validação cruzada
        cv_params: Parâmetros da validação cruzada
        scoring: Métrica de avaliação
        random_state: Seed para reprodutibilidade
        
    Returns:
        Dicionário com resultados da otimização
    """
    try:
        # Converter dados para numpy arrays
        X = np.array(X_data)
        y = np.array(y_data)
        
        # Criar otimizador
        optimizer = HyperparameterOptimizer(
            study_name=study_name,
            direction="maximize",
            n_trials=n_trials,
            timeout=timeout,
            cv_strategy=cv_strategy,
            cv_params=cv_params or {},
            scoring=scoring,
            random_state=random_state
        )
        
        # Otimizar modelo específico
        if model_name == "random_forest":
            study = optimizer.optimize_random_forest(X, y)
        elif model_name == "xgboost":
            study = optimizer.optimize_xgboost(X, y)
        elif model_name == "lightgbm":
            study = optimizer.optimize_lightgbm(X, y)
        elif model_name == "catboost":
            study = optimizer.optimize_catboost(X, y)
        elif model_name == "logistic_regression":
            study = optimizer.optimize_logistic_regression(X, y)
        elif model_name == "bayesian_neural_network":
            study = optimizer.optimize_bayesian_neural_network(X, y)
        elif model_name == "poisson_model":
            study = optimizer.optimize_poisson_model(X, y)
        else:
            raise ValueError(f"Modelo {model_name} não suportado")
        
        # Preparar resultados
        results = {
            'task_id': self.request.id,
            'model_name': model_name,
            'study_name': study_name,
            'status': 'completed',
            'best_score': optimizer.get_best_score(),
            'best_params': optimizer.get_best_params(),
            'n_trials': len(study.trials),
            'cv_strategy': cv_strategy,
            'scoring': scoring,
            'completed_at': datetime.now().isoformat(),
            'optimization_history': optimizer.get_optimization_history()
        }
        
        # Salvar resultados
        results_file = f"optimization/results/{study_name}_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Otimização de {model_name} concluída. Score: {results['best_score']:.4f}")
        
        return results
        
    except Exception as e:
        logger.error(f"Erro na otimização de {model_name}: {str(e)}")
        return {
            'task_id': self.request.id,
            'model_name': model_name,
            'study_name': study_name,
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        }


@celery_app.task(bind=True, name='optimization.optimize_multiple_models')
def optimize_multiple_models(
    self,
    model_names: List[str],
    X_data: List[List[float]],
    y_data: List[int],
    study_name: str,
    n_trials: int = 100,
    timeout: Optional[int] = None,
    cv_strategy: str = "time_series",
    cv_params: Optional[Dict[str, Any]] = None,
    scoring: str = "accuracy",
    random_state: Optional[int] = None
) -> Dict[str, Any]:
    """
    Otimiza hiperparâmetros de múltiplos modelos
    
    Args:
        model_names: Lista de nomes dos modelos
        X_data: Dados de features (lista de listas)
        y_data: Dados de target (lista)
        study_name: Nome do estudo
        n_trials: Número de tentativas por modelo
        timeout: Timeout em segundos por modelo
        cv_strategy: Estratégia de validação cruzada
        cv_params: Parâmetros da validação cruzada
        scoring: Métrica de avaliação
        random_state: Seed para reprodutibilidade
        
    Returns:
        Dicionário com resultados de todas as otimizações
    """
    try:
        # Converter dados para numpy arrays
        X = np.array(X_data)
        y = np.array(y_data)
        
        # Criar otimizador multi-modelo
        multi_optimizer = MultiModelOptimizer(
            models=model_names,
            study_name=study_name,
            direction="maximize",
            n_trials=n_trials,
            timeout=timeout,
            cv_strategy=cv_strategy,
            cv_params=cv_params or {},
            scoring=scoring,
            random_state=random_state
        )
        
        # Otimizar todos os modelos
        studies = multi_optimizer.optimize_all(X, y)
        
        # Preparar resultados
        results = {
            'task_id': self.request.id,
            'study_name': study_name,
            'status': 'completed',
            'models': {},
            'best_model': None,
            'best_score': float('-inf'),
            'completed_at': datetime.now().isoformat()
        }
        
        # Processar resultados de cada modelo
        for model_name, study in studies.items():
            optimizer = multi_optimizer.optimizers[model_name]
            
            model_results = {
                'best_score': optimizer.get_best_score(),
                'best_params': optimizer.get_best_params(),
                'n_trials': len(study.trials),
                'cv_strategy': cv_strategy,
                'scoring': scoring
            }
            
            results['models'][model_name] = model_results
            
            # Atualizar melhor modelo
            if model_results['best_score'] > results['best_score']:
                results['best_score'] = model_results['best_score']
                results['best_model'] = model_name
        
        # Salvar resultados
        results_file = f"optimization/results/{study_name}_multi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Otimização multi-modelo concluída. Melhor: {results['best_model']} ({results['best_score']:.4f})")
        
        return results
        
    except Exception as e:
        logger.error(f"Erro na otimização multi-modelo: {str(e)}")
        return {
            'task_id': self.request.id,
            'study_name': study_name,
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        }


@celery_app.task(bind=True, name='optimization.optimize_with_custom_objective')
def optimize_with_custom_objective(
    self,
    model_name: str,
    X_data: List[List[float]],
    y_data: List[int],
    study_name: str,
    custom_objective: str,
    n_trials: int = 100,
    timeout: Optional[int] = None,
    cv_strategy: str = "time_series",
    cv_params: Optional[Dict[str, Any]] = None,
    random_state: Optional[int] = None
) -> Dict[str, Any]:
    """
    Otimiza hiperparâmetros com função objetivo customizada
    
    Args:
        model_name: Nome do modelo
        X_data: Dados de features
        y_data: Dados de target
        study_name: Nome do estudo
        custom_objective: Função objetivo customizada (código Python)
        n_trials: Número de tentativas
        timeout: Timeout em segundos
        cv_strategy: Estratégia de validação cruzada
        cv_params: Parâmetros da validação cruzada
        random_state: Seed para reprodutibilidade
        
    Returns:
        Dicionário com resultados da otimização
    """
    try:
        # Converter dados para numpy arrays
        X = np.array(X_data)
        y = np.array(y_data)
        
        # Criar otimizador
        optimizer = HyperparameterOptimizer(
            study_name=study_name,
            direction="maximize",
            n_trials=n_trials,
            timeout=timeout,
            cv_strategy=cv_strategy,
            cv_params=cv_params or {},
            scoring="accuracy",  # Será sobrescrito pela função customizada
            random_state=random_state
        )
        
        # Executar função objetivo customizada
        # NOTA: Em produção, isso deve ser feito de forma mais segura
        exec(custom_objective, globals(), locals())
        
        # Preparar resultados
        results = {
            'task_id': self.request.id,
            'model_name': model_name,
            'study_name': study_name,
            'status': 'completed',
            'custom_objective': True,
            'completed_at': datetime.now().isoformat()
        }
        
        logger.info(f"Otimização customizada de {model_name} concluída")
        
        return results
        
    except Exception as e:
        logger.error(f"Erro na otimização customizada: {str(e)}")
        return {
            'task_id': self.request.id,
            'model_name': model_name,
            'study_name': study_name,
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        }


@celery_app.task(bind=True, name='optimization.resume_optimization')
def resume_optimization(
    self,
    study_name: str,
    model_name: str,
    additional_trials: int = 50
) -> Dict[str, Any]:
    """
    Retoma uma otimização existente
    
    Args:
        study_name: Nome do estudo
        model_name: Nome do modelo
        additional_trials: Número adicional de tentativas
        
    Returns:
        Dicionário com resultados da otimização retomada
    """
    try:
        # Carregar estudo existente
        optimizer = HyperparameterOptimizer(study_name=study_name)
        
        # Continuar otimização
        if model_name == "random_forest":
            study = optimizer.optimize_random_forest(X, y)
        elif model_name == "xgboost":
            study = optimizer.optimize_xgboost(X, y)
        elif model_name == "lightgbm":
            study = optimizer.optimize_lightgbm(X, y)
        elif model_name == "catboost":
            study = optimizer.optimize_catboost(X, y)
        elif model_name == "logistic_regression":
            study = optimizer.optimize_logistic_regression(X, y)
        elif model_name == "bayesian_neural_network":
            study = optimizer.optimize_bayesian_neural_network(X, y)
        elif model_name == "poisson_model":
            study = optimizer.optimize_poisson_model(X, y)
        else:
            raise ValueError(f"Modelo {model_name} não suportado")
        
        # Preparar resultados
        results = {
            'task_id': self.request.id,
            'model_name': model_name,
            'study_name': study_name,
            'status': 'resumed',
            'best_score': optimizer.get_best_score(),
            'best_params': optimizer.get_best_params(),
            'total_trials': len(study.trials),
            'additional_trials': additional_trials,
            'completed_at': datetime.now().isoformat()
        }
        
        logger.info(f"Otimização de {model_name} retomada. Score: {results['best_score']:.4f}")
        
        return results
        
    except Exception as e:
        logger.error(f"Erro ao retomar otimização: {str(e)}")
        return {
            'task_id': self.request.id,
            'model_name': model_name,
            'study_name': study_name,
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        }


@celery_app.task(bind=True, name='optimization.export_optimization_results')
def export_optimization_results(
    self,
    study_name: str,
    model_name: str,
    export_format: str = "json"
) -> Dict[str, Any]:
    """
    Exporta resultados de otimização
    
    Args:
        study_name: Nome do estudo
        model_name: Nome do modelo
        export_format: Formato de exportação (json, csv, pickle)
        
    Returns:
        Dicionário com informações da exportação
    """
    try:
        # Carregar otimizador
        optimizer = HyperparameterOptimizer(study_name=study_name)
        
        # Exportar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == "json":
            filepath = f"optimization/exports/{study_name}_{model_name}_{timestamp}.json"
            optimizer.export_results(filepath)
        elif export_format == "csv":
            # Exportar histórico como CSV
            history = optimizer.get_optimization_history()
            df = pd.DataFrame(history)
            filepath = f"optimization/exports/{study_name}_{model_name}_{timestamp}.csv"
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            df.to_csv(filepath, index=False)
        elif export_format == "pickle":
            filepath = f"optimization/exports/{study_name}_{model_name}_{timestamp}.pkl"
            optimizer.save_study(filepath)
        else:
            raise ValueError(f"Formato {export_format} não suportado")
        
        results = {
            'task_id': self.request.id,
            'study_name': study_name,
            'model_name': model_name,
            'export_format': export_format,
            'filepath': filepath,
            'status': 'completed',
            'exported_at': datetime.now().isoformat()
        }
        
        logger.info(f"Resultados exportados: {filepath}")
        
        return results
        
    except Exception as e:
        logger.error(f"Erro ao exportar resultados: {str(e)}")
        return {
            'task_id': self.request.id,
            'study_name': study_name,
            'model_name': model_name,
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        }


@celery_app.task(bind=True, name='optimization.cleanup_old_studies')
def cleanup_old_studies(
    self,
    days_old: int = 30
) -> Dict[str, Any]:
    """
    Limpa estudos antigos para liberar espaço
    
    Args:
        days_old: Idade em dias para considerar estudos antigos
        
    Returns:
        Dicionário com informações da limpeza
    """
    try:
        import glob
        from datetime import timedelta
        
        # Encontrar arquivos antigos
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Limpar arquivos de resultados
        results_pattern = "optimization/results/*.json"
        results_files = glob.glob(results_pattern)
        
        # Limpar arquivos de exportação
        exports_pattern = "optimization/exports/*"
        exports_files = glob.glob(exports_pattern)
        
        # Limpar arquivos de estudo
        studies_pattern = "optimization/*.db"
        studies_files = glob.glob(studies_pattern)
        
        cleaned_files = []
        
        for file_path in results_files + exports_files + studies_files:
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_date:
                os.remove(file_path)
                cleaned_files.append(file_path)
        
        results = {
            'task_id': self.request.id,
            'status': 'completed',
            'days_old': days_old,
            'cleaned_files': len(cleaned_files),
            'cleaned_at': datetime.now().isoformat()
        }
        
        logger.info(f"Limpeza concluída: {len(cleaned_files)} arquivos removidos")
        
        return results
        
    except Exception as e:
        logger.error(f"Erro na limpeza: {str(e)}")
        return {
            'task_id': self.request.id,
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        }


# Exemplo de uso
if __name__ == "__main__":
    # Exemplo de como usar as tarefas
    import numpy as np
    
    # Criar dados de exemplo
    X = np.random.randn(1000, 10).tolist()
    y = np.random.randint(0, 3, 1000).tolist()
    
    # Executar otimização assíncrona
    task = optimize_single_model.delay(
        model_name="random_forest",
        X_data=X,
        y_data=y,
        study_name="test_optimization",
        n_trials=50
    )
    
    print(f"Tarefa iniciada: {task.id}")
    print(f"Status: {task.status}")
    
    # Aguardar conclusão (em produção, usar callback ou polling)
    result = task.get(timeout=300)
    print(f"Resultado: {result}")
