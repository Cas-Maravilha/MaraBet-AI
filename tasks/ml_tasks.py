"""
Tarefas de Machine Learning para MaraBet AI
Processamento assíncrono de treinamento e predição de modelos
"""

from celery import current_task
from tasks.celery_app import celery_app
from cache.redis_cache import cache, cache_predictions, get_predictions
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os
from typing import Dict, List, Any, Optional
import traceback

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks.ml_tasks.train_model')
def train_model(self, model_type: str, league_id: int, features: List[str], 
                target: str, test_size: float = 0.2, random_state: int = 42):
    """
    Treina um modelo de machine learning específico
    
    Args:
        model_type: Tipo do modelo (random_forest, xgboost, etc.)
        league_id: ID da liga
        features: Lista de features para treinamento
        target: Variável alvo
        test_size: Proporção de dados para teste
        random_state: Seed para reprodutibilidade
    
    Returns:
        Dict com informações do modelo treinado
    """
    try:
        # Atualiza status da tarefa
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando treinamento do modelo', 'progress': 0}
        )
        
        logger.info(f"Iniciando treinamento do modelo {model_type} para liga {league_id}")
        
        # Importa módulos necessários
        from ml.ml_models import MLModelManager
        from armazenamento.banco_de_dados import DatabaseManager
        
        # Conecta ao banco de dados
        db = DatabaseManager()
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Carregando dados de treinamento', 'progress': 20}
        )
        
        # Carrega dados de treinamento
        query = """
        SELECT * FROM match_statistics 
        WHERE league_id = ? AND match_date >= ?
        ORDER BY match_date DESC
        """
        
        cutoff_date = datetime.now() - timedelta(days=365)  # Último ano
        data = db.execute_query(query, (league_id, cutoff_date))
        
        if not data or len(data) < 100:
            raise ValueError(f"Dados insuficientes para treinamento: {len(data) if data else 0} registros")
        
        # Converte para DataFrame
        df = pd.DataFrame(data)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Preparando features', 'progress': 40}
        )
        
        # Prepara features e target
        X = df[features]
        y = df[target]
        
        # Remove valores nulos
        mask = X.notna().all(axis=1) & y.notna()
        X = X[mask]
        y = y[mask]
        
        if len(X) < 50:
            raise ValueError(f"Dados válidos insuficientes após limpeza: {len(X)} registros")
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Treinando modelo', 'progress': 60}
        )
        
        # Inicializa e treina modelo
        ml_manager = MLModelManager()
        model = ml_manager.create_model(model_type)
        
        # Treina o modelo
        model.fit(X, y)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Avaliando modelo', 'progress': 80}
        )
        
        # Avalia o modelo
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        # Calcula métricas
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted')
        }
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Salvando modelo', 'progress': 90}
        )
        
        # Salva o modelo
        model_path = f"models/{model_type}_league_{league_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)
        
        # Atualiza banco de dados com informações do modelo
        model_info = {
            'model_type': model_type,
            'league_id': league_id,
            'features': features,
            'target': target,
            'model_path': model_path,
            'metrics': metrics,
            'training_samples': len(X),
            'created_at': datetime.now(),
            'status': 'trained'
        }
        
        db.execute_query("""
            INSERT INTO ml_models (model_type, league_id, features, target, model_path, 
                                 metrics, training_samples, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            model_info['model_type'],
            model_info['league_id'],
            str(model_info['features']),
            model_info['target'],
            model_info['model_path'],
            str(model_info['metrics']),
            model_info['training_samples'],
            model_info['created_at'],
            model_info['status']
        ))
        
        # Atualiza progresso final
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Treinamento concluído', 'progress': 100}
        )
        
        logger.info(f"Modelo {model_type} treinado com sucesso para liga {league_id}")
        
        return {
            'status': 'success',
            'model_info': model_info,
            'metrics': metrics
        }
        
    except Exception as e:
        logger.error(f"Erro no treinamento do modelo: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro no treinamento', 'error': str(e)}
        )
        
        raise

@celery_app.task(bind=True, name='tasks.ml_tasks.train_all_models')
def train_all_models(self):
    """
    Treina todos os modelos para todas as ligas monitoradas
    
    Returns:
        Dict com resumo do treinamento
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando treinamento de todos os modelos', 'progress': 0}
        )
        
        logger.info("Iniciando treinamento de todos os modelos")
        
        from armazenamento.banco_de_dados import DatabaseManager
        
        db = DatabaseManager()
        
        # Obtém ligas monitoradas
        leagues = db.execute_query("SELECT id, name FROM leagues WHERE active = 1")
        
        if not leagues:
            raise ValueError("Nenhuma liga ativa encontrada")
        
        # Configurações de modelos
        model_types = ['random_forest', 'xgboost', 'lightgbm', 'catboost']
        features = [
            'home_goals_avg', 'away_goals_avg', 'home_conceded_avg', 'away_conceded_avg',
            'home_form', 'away_form', 'home_attendance', 'away_attendance',
            'head_to_head_home_wins', 'head_to_head_away_wins', 'head_to_head_draws',
            'home_goals_scored', 'away_goals_scored', 'home_goals_conceded', 'away_goals_conceded'
        ]
        target = 'result'  # 1=home_win, 0=draw, -1=away_win
        
        results = []
        total_tasks = len(leagues) * len(model_types)
        completed_tasks = 0
        
        for league in leagues:
            league_id = league['id']
            league_name = league['name']
            
            for model_type in model_types:
                try:
                    # Atualiza progresso
                    progress = int((completed_tasks / total_tasks) * 100)
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'status': f'Treinando {model_type} para {league_name}',
                            'progress': progress
                        }
                    )
                    
                    # Treina modelo
                    result = train_model.delay(
                        model_type=model_type,
                        league_id=league_id,
                        features=features,
                        target=target
                    )
                    
                    results.append({
                        'league_id': league_id,
                        'league_name': league_name,
                        'model_type': model_type,
                        'task_id': result.id,
                        'status': 'started'
                    })
                    
                    completed_tasks += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao iniciar treinamento de {model_type} para {league_name}: {e}")
                    results.append({
                        'league_id': league_id,
                        'league_name': league_name,
                        'model_type': model_type,
                        'error': str(e),
                        'status': 'failed'
                    })
                    completed_tasks += 1
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Treinamento de todos os modelos iniciado', 'progress': 100}
        )
        
        logger.info(f"Treinamento de {len(results)} modelos iniciado")
        
        return {
            'status': 'success',
            'total_models': len(results),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Erro no treinamento de todos os modelos: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro no treinamento', 'error': str(e)}
        )
        
        raise

@celery_app.task(bind=True, name='tasks.ml_tasks.predict_match')
def predict_match(self, match_id: int, model_type: str = 'ensemble'):
    """
    Faz predição para uma partida específica
    
    Args:
        match_id: ID da partida
        model_type: Tipo do modelo para usar
    
    Returns:
        Dict com predições
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Iniciando predição da partida', 'progress': 0}
        )
        
        logger.info(f"Iniciando predição para partida {match_id}")
        
        from armazenamento.banco_de_dados import DatabaseManager
        from ml.ml_models import MLModelManager
        
        db = DatabaseManager()
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Carregando dados da partida', 'progress': 20}
        )
        
        # Obtém dados da partida
        match_data = db.execute_query("""
            SELECT m.*, l.id as league_id, l.name as league_name
            FROM matches m
            JOIN leagues l ON m.league_id = l.id
            WHERE m.id = ?
        """, (match_id,))
        
        if not match_data:
            raise ValueError(f"Partida {match_id} não encontrada")
        
        match = match_data[0]
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Preparando features', 'progress': 40}
        )
        
        # Prepara features para predição
        features = self._prepare_match_features(match, db)
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Carregando modelo', 'progress': 60}
        )
        
        # Carrega modelo
        ml_manager = MLModelManager()
        model = ml_manager.load_latest_model(model_type, match['league_id'])
        
        if model is None:
            raise ValueError(f"Modelo {model_type} não encontrado para liga {match['league_id']}")
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Fazendo predição', 'progress': 80}
        )
        
        # Faz predição
        prediction = model.predict([features])[0]
        prediction_proba = model.predict_proba([features])[0] if hasattr(model, 'predict_proba') else None
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Salvando predição', 'progress': 90}
        )
        
        # Prepara resultado
        result = {
            'match_id': match_id,
            'league_id': match['league_id'],
            'league_name': match['league_name'],
            'home_team': match['home_team'],
            'away_team': match['away_team'],
            'match_date': match['match_date'],
            'prediction': int(prediction),
            'prediction_proba': prediction_proba.tolist() if prediction_proba is not None else None,
            'model_type': model_type,
            'features_used': list(features.keys()),
            'created_at': datetime.now()
        }
        
        # Salva predição no banco
        db.execute_query("""
            INSERT INTO predictions (match_id, league_id, model_type, prediction, 
                                   prediction_proba, features_used, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            result['match_id'],
            result['league_id'],
            result['model_type'],
            result['prediction'],
            str(result['prediction_proba']) if result['prediction_proba'] else None,
            str(result['features_used']),
            result['created_at']
        ))
        
        # Cache da predição
        cache_key = f"prediction_{match_id}_{model_type}"
        cache_predictions(cache_key, result, ttl=3600)  # 1 hora
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Predição concluída', 'progress': 100}
        )
        
        logger.info(f"Predição concluída para partida {match_id}")
        
        return {
            'status': 'success',
            'prediction': result
        }
        
    except Exception as e:
        logger.error(f"Erro na predição da partida {match_id}: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro na predição', 'error': str(e)}
        )
        
        raise

def _prepare_match_features(self, match: Dict, db: DatabaseManager) -> Dict[str, float]:
    """
    Prepara features para predição de uma partida
    
    Args:
        match: Dados da partida
        db: Instância do banco de dados
    
    Returns:
        Dict com features preparadas
    """
    try:
        # Implementação simplificada - em produção seria mais complexa
        features = {}
        
        # Features básicas da partida
        features['home_goals_avg'] = match.get('home_goals_avg', 0.0)
        features['away_goals_avg'] = match.get('away_goals_avg', 0.0)
        features['home_conceded_avg'] = match.get('home_conceded_avg', 0.0)
        features['away_conceded_avg'] = match.get('away_conceded_avg', 0.0)
        features['home_form'] = match.get('home_form', 0.0)
        features['away_form'] = match.get('away_form', 0.0)
        features['home_attendance'] = match.get('home_attendance', 0.0)
        features['away_attendance'] = match.get('away_attendance', 0.0)
        
        # Features de confronto direto
        features['head_to_head_home_wins'] = match.get('head_to_head_home_wins', 0.0)
        features['head_to_head_away_wins'] = match.get('head_to_head_away_wins', 0.0)
        features['head_to_head_draws'] = match.get('head_to_head_draws', 0.0)
        
        # Features de gols
        features['home_goals_scored'] = match.get('home_goals_scored', 0.0)
        features['away_goals_scored'] = match.get('away_goals_scored', 0.0)
        features['home_goals_conceded'] = match.get('home_goals_conceded', 0.0)
        features['away_goals_conceded'] = match.get('away_goals_conceded', 0.0)
        
        return features
        
    except Exception as e:
        logger.error(f"Erro ao preparar features da partida: {e}")
        return {}

@celery_app.task(bind=True, name='tasks.ml_tasks.update_model_performance')
def update_model_performance(self, model_id: int):
    """
    Atualiza performance de um modelo baseado em resultados reais
    
    Args:
        model_id: ID do modelo
    
    Returns:
        Dict com métricas atualizadas
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Atualizando performance do modelo', 'progress': 0}
        )
        
        logger.info(f"Atualizando performance do modelo {model_id}")
        
        from armazenamento.banco_de_dados import DatabaseManager
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        db = DatabaseManager()
        
        # Obtém modelo
        model_data = db.execute_query("SELECT * FROM ml_models WHERE id = ?", (model_id,))
        if not model_data:
            raise ValueError(f"Modelo {model_id} não encontrado")
        
        model = model_data[0]
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Carregando predições', 'progress': 30}
        )
        
        # Obtém predições do modelo
        predictions = db.execute_query("""
            SELECT p.*, m.result as actual_result
            FROM predictions p
            JOIN matches m ON p.match_id = m.id
            WHERE p.model_type = ? AND p.league_id = ? 
            AND m.match_date < ? AND m.result IS NOT NULL
            ORDER BY p.created_at DESC
            LIMIT 100
        """, (model['model_type'], model['league_id'], datetime.now()))
        
        if not predictions:
            raise ValueError("Nenhuma predição encontrada para avaliação")
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Calculando métricas', 'progress': 60}
        )
        
        # Calcula métricas
        y_true = [p['actual_result'] for p in predictions]
        y_pred = [p['prediction'] for p in predictions]
        
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted'),
            'recall': recall_score(y_true, y_pred, average='weighted'),
            'f1_score': f1_score(y_true, y_pred, average='weighted'),
            'total_predictions': len(predictions),
            'updated_at': datetime.now()
        }
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Salvando métricas', 'progress': 90}
        )
        
        # Atualiza banco de dados
        db.execute_query("""
            UPDATE ml_models 
            SET metrics = ?, updated_at = ?
            WHERE id = ?
        """, (str(metrics), metrics['updated_at'], model_id))
        
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Performance atualizada', 'progress': 100}
        )
        
        logger.info(f"Performance do modelo {model_id} atualizada")
        
        return {
            'status': 'success',
            'model_id': model_id,
            'metrics': metrics
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar performance do modelo {model_id}: {str(e)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={'status': 'Erro na atualização', 'error': str(e)}
        )
        
        raise
