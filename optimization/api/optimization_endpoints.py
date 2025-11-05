"""
API endpoints para gerenciar otimizações de hiperparâmetros
Integração com FastAPI para controle via web
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import json
import os

from tasks.optimization_tasks import (
    optimize_single_model,
    optimize_multiple_models,
    optimize_with_custom_objective,
    resume_optimization,
    export_optimization_results,
    cleanup_old_studies
)
from optimization.optimizers.hyperparameter_optimizer import HyperparameterOptimizer, MultiModelOptimizer
from optimization.optimizers.model_optimizers import ModelOptimizerFactory
from optimization.validation.time_series_cv import create_time_series_cv

# Importar dependências de autenticação
from auth.jwt_auth import get_current_active_user, require_role
from auth.models import UserRole
from armazenamento.banco_de_dados import SessionLocal

logger = logging.getLogger(__name__)

# Configurar router
router = APIRouter(prefix="/optimization", tags=["Hyperparameter Optimization"])

# Dependência para banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos Pydantic
class OptimizationRequest(BaseModel):
    model_name: str = Field(..., description="Nome do modelo para otimizar")
    study_name: str = Field(..., description="Nome do estudo")
    n_trials: int = Field(100, ge=1, le=1000, description="Número de tentativas")
    timeout: Optional[int] = Field(None, ge=60, description="Timeout em segundos")
    cv_strategy: str = Field("time_series", description="Estratégia de validação cruzada")
    cv_params: Optional[Dict[str, Any]] = Field(None, description="Parâmetros da validação cruzada")
    scoring: str = Field("accuracy", description="Métrica de avaliação")
    random_state: Optional[int] = Field(None, description="Seed para reprodutibilidade")

class MultiModelOptimizationRequest(BaseModel):
    model_names: List[str] = Field(..., description="Lista de modelos para otimizar")
    study_name: str = Field(..., description="Nome do estudo")
    n_trials: int = Field(100, ge=1, le=1000, description="Número de tentativas por modelo")
    timeout: Optional[int] = Field(None, ge=60, description="Timeout em segundos por modelo")
    cv_strategy: str = Field("time_series", description="Estratégia de validação cruzada")
    cv_params: Optional[Dict[str, Any]] = Field(None, description="Parâmetros da validação cruzada")
    scoring: str = Field("accuracy", description="Métrica de avaliação")
    random_state: Optional[int] = Field(None, description="Seed para reprodutibilidade")

class CustomObjectiveRequest(BaseModel):
    model_name: str = Field(..., description="Nome do modelo")
    study_name: str = Field(..., description="Nome do estudo")
    custom_objective: str = Field(..., description="Código Python da função objetivo")
    n_trials: int = Field(100, ge=1, le=1000, description="Número de tentativas")
    timeout: Optional[int] = Field(None, ge=60, description="Timeout em segundos")
    cv_strategy: str = Field("time_series", description="Estratégia de validação cruzada")
    cv_params: Optional[Dict[str, Any]] = Field(None, description="Parâmetros da validação cruzada")
    random_state: Optional[int] = Field(None, description="Seed para reprodutibilidade")

class ResumeOptimizationRequest(BaseModel):
    study_name: str = Field(..., description="Nome do estudo")
    model_name: str = Field(..., description="Nome do modelo")
    additional_trials: int = Field(50, ge=1, le=500, description="Número adicional de tentativas")

class ExportRequest(BaseModel):
    study_name: str = Field(..., description="Nome do estudo")
    model_name: str = Field(..., description="Nome do modelo")
    export_format: str = Field("json", description="Formato de exportação (json, csv, pickle)")

class CleanupRequest(BaseModel):
    days_old: int = Field(30, ge=1, le=365, description="Idade em dias para considerar estudos antigos")

# Endpoints
@router.post("/start-single")
async def start_single_optimization(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    Inicia otimização de hiperparâmetros para um único modelo
    """
    try:
        # Validar modelo
        if request.model_name not in ModelOptimizerFactory.get_supported_models():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Modelo {request.model_name} não suportado"
            )
        
        # Buscar dados do banco (implementar conforme necessário)
        # Por enquanto, usar dados de exemplo
        import numpy as np
        X_data = np.random.randn(1000, 10).tolist()
        y_data = np.random.randint(0, 3, 1000).tolist()
        
        # Iniciar tarefa assíncrona
        task = optimize_single_model.delay(
            model_name=request.model_name,
            X_data=X_data,
            y_data=y_data,
            study_name=request.study_name,
            n_trials=request.n_trials,
            timeout=request.timeout,
            cv_strategy=request.cv_strategy,
            cv_params=request.cv_params,
            scoring=request.scoring,
            random_state=request.random_state
        )
        
        return {
            "message": "Otimização iniciada com sucesso",
            "task_id": task.id,
            "model_name": request.model_name,
            "study_name": request.study_name,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Erro ao iniciar otimização: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/start-multi")
async def start_multi_optimization(
    request: MultiModelOptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    Inicia otimização de hiperparâmetros para múltiplos modelos
    """
    try:
        # Validar modelos
        for model_name in request.model_names:
            if model_name not in ModelOptimizerFactory.get_supported_models():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Modelo {model_name} não suportado"
                )
        
        # Buscar dados do banco (implementar conforme necessário)
        import numpy as np
        X_data = np.random.randn(1000, 10).tolist()
        y_data = np.random.randint(0, 3, 1000).tolist()
        
        # Iniciar tarefa assíncrona
        task = optimize_multiple_models.delay(
            model_names=request.model_names,
            X_data=X_data,
            y_data=y_data,
            study_name=request.study_name,
            n_trials=request.n_trials,
            timeout=request.timeout,
            cv_strategy=request.cv_strategy,
            cv_params=request.cv_params,
            scoring=request.scoring,
            random_state=request.random_state
        )
        
        return {
            "message": "Otimização multi-modelo iniciada com sucesso",
            "task_id": task.id,
            "model_names": request.model_names,
            "study_name": request.study_name,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Erro ao iniciar otimização multi-modelo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/start-custom")
async def start_custom_optimization(
    request: CustomObjectiveRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    Inicia otimização com função objetivo customizada
    """
    try:
        # Validar modelo
        if request.model_name not in ModelOptimizerFactory.get_supported_models():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Modelo {request.model_name} não suportado"
            )
        
        # Buscar dados do banco (implementar conforme necessário)
        import numpy as np
        X_data = np.random.randn(1000, 10).tolist()
        y_data = np.random.randint(0, 3, 1000).tolist()
        
        # Iniciar tarefa assíncrona
        task = optimize_with_custom_objective.delay(
            model_name=request.model_name,
            X_data=X_data,
            y_data=y_data,
            study_name=request.study_name,
            custom_objective=request.custom_objective,
            n_trials=request.n_trials,
            timeout=request.timeout,
            cv_strategy=request.cv_strategy,
            cv_params=request.cv_params,
            random_state=request.random_state
        )
        
        return {
            "message": "Otimização customizada iniciada com sucesso",
            "task_id": task.id,
            "model_name": request.model_name,
            "study_name": request.study_name,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Erro ao iniciar otimização customizada: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/resume")
async def resume_optimization_endpoint(
    request: ResumeOptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    Retoma uma otimização existente
    """
    try:
        # Iniciar tarefa assíncrona
        task = resume_optimization.delay(
            study_name=request.study_name,
            model_name=request.model_name,
            additional_trials=request.additional_trials
        )
        
        return {
            "message": "Otimização retomada com sucesso",
            "task_id": task.id,
            "study_name": request.study_name,
            "model_name": request.model_name,
            "status": "resumed"
        }
        
    except Exception as e:
        logger.error(f"Erro ao retomar otimização: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/export")
async def export_optimization_results_endpoint(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    Exporta resultados de otimização
    """
    try:
        # Validar formato
        if request.export_format not in ["json", "csv", "pickle"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de exportação deve ser json, csv ou pickle"
            )
        
        # Iniciar tarefa assíncrona
        task = export_optimization_results.delay(
            study_name=request.study_name,
            model_name=request.model_name,
            export_format=request.export_format
        )
        
        return {
            "message": "Exportação iniciada com sucesso",
            "task_id": task.id,
            "study_name": request.study_name,
            "model_name": request.model_name,
            "export_format": request.export_format,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Erro ao exportar resultados: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/cleanup")
async def cleanup_old_studies_endpoint(
    request: CleanupRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    Limpa estudos antigos
    """
    try:
        # Iniciar tarefa assíncrona
        task = cleanup_old_studies.delay(days_old=request.days_old)
        
        return {
            "message": "Limpeza iniciada com sucesso",
            "task_id": task.id,
            "days_old": request.days_old,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar estudos antigos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/status/{task_id}")
async def get_optimization_status(
    task_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtém status de uma otimização
    """
    try:
        from celery.result import AsyncResult
        
        # Obter resultado da tarefa
        result = AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "info": result.info if not result.ready() else None
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/models")
async def get_supported_models(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista modelos suportados para otimização
    """
    try:
        models = ModelOptimizerFactory.get_supported_models()
        
        # Adicionar informações sobre cada modelo
        model_info = []
        for model in models:
            default_params = ModelOptimizerFactory.get_default_params(model)
            model_info.append({
                "name": model,
                "display_name": model.replace("_", " ").title(),
                "default_params": default_params
            })
        
        return {
            "models": model_info,
            "total": len(models)
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar modelos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/cv-strategies")
async def get_cv_strategies(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista estratégias de validação cruzada disponíveis
    """
    try:
        strategies = [
            {
                "name": "time_series",
                "display_name": "Time Series Cross-Validation",
                "description": "Validação cruzada temporal com janelas deslizantes ou expansivas"
            },
            {
                "name": "purged",
                "display_name": "Purged Cross-Validation",
                "description": "Validação cruzada com purga para evitar data leakage"
            },
            {
                "name": "walk_forward",
                "display_name": "Walk-Forward Analysis",
                "description": "Análise walk-forward para estratégias de trading"
            },
            {
                "name": "monte_carlo",
                "display_name": "Monte Carlo Cross-Validation",
                "description": "Validação cruzada com splits aleatórios"
            }
        ]
        
        return {
            "strategies": strategies,
            "total": len(strategies)
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar estratégias CV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/studies")
async def list_optimization_studies(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Lista estudos de otimização existentes
    """
    try:
        import glob
        
        # Buscar arquivos de estudo
        study_files = glob.glob("optimization/*.db")
        studies = []
        
        for file_path in study_files:
            study_name = os.path.basename(file_path).replace(".db", "")
            
            # Obter informações do arquivo
            stat = os.stat(file_path)
            created_at = datetime.fromtimestamp(stat.st_ctime)
            modified_at = datetime.fromtimestamp(stat.st_mtime)
            size = stat.st_size
            
            studies.append({
                "name": study_name,
                "file_path": file_path,
                "created_at": created_at.isoformat(),
                "modified_at": modified_at.isoformat(),
                "size_bytes": size
            })
        
        return {
            "studies": studies,
            "total": len(studies)
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar estudos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/results/{study_name}")
async def get_optimization_results(
    study_name: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtém resultados de um estudo de otimização
    """
    try:
        # Carregar otimizador
        optimizer = HyperparameterOptimizer(study_name=study_name)
        
        # Obter resultados
        results = {
            "study_name": study_name,
            "best_score": optimizer.get_best_score(),
            "best_params": optimizer.get_best_params(),
            "n_trials": len(optimizer.study.trials),
            "optimization_history": optimizer.get_optimization_history()
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Erro ao obter resultados: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/studies/{study_name}")
async def delete_optimization_study(
    study_name: str,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    Remove um estudo de otimização
    """
    try:
        # Remover arquivo do estudo
        study_file = f"optimization/{study_name}.db"
        if os.path.exists(study_file):
            os.remove(study_file)
        
        # Remover arquivos de resultados
        import glob
        result_files = glob.glob(f"optimization/results/{study_name}*")
        for file_path in result_files:
            os.remove(file_path)
        
        return {
            "message": f"Estudo {study_name} removido com sucesso",
            "study_name": study_name
        }
        
    except Exception as e:
        logger.error(f"Erro ao remover estudo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
