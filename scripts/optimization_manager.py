"""
Script de gerenciamento de otimizações de hiperparâmetros
Interface de linha de comando para controlar otimizações
"""

import argparse
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimization.optimizers.hyperparameter_optimizer import HyperparameterOptimizer, MultiModelOptimizer
from optimization.optimizers.model_optimizers import ModelOptimizerFactory
from optimization.validation.time_series_cv import create_time_series_cv
from tasks.optimization_tasks import (
    optimize_single_model, optimize_multiple_models, 
    export_optimization_results, cleanup_old_studies
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizationManager:
    """Gerenciador de otimizações de hiperparâmetros"""
    
    def __init__(self):
        self.supported_models = ModelOptimizerFactory.get_supported_models()
        self.cv_strategies = ["time_series", "purged", "walk_forward", "monte_carlo"]
    
    def list_models(self) -> None:
        """Lista modelos suportados"""
        print("\n📊 Modelos Suportados para Otimização:")
        print("=" * 50)
        
        for i, model in enumerate(self.supported_models, 1):
            default_params = ModelOptimizerFactory.get_default_params(model)
            print(f"{i:2d}. {model.replace('_', ' ').title()}")
            print(f"    Parâmetros padrão: {len(default_params)} parâmetros")
            print()
    
    def list_cv_strategies(self) -> None:
        """Lista estratégias de validação cruzada"""
        print("\n🔄 Estratégias de Validação Cruzada:")
        print("=" * 50)
        
        strategy_descriptions = {
            "time_series": "Validação cruzada temporal com janelas deslizantes ou expansivas",
            "purged": "Validação cruzada com purga para evitar data leakage",
            "walk_forward": "Análise walk-forward para estratégias de trading",
            "monte_carlo": "Validação cruzada com splits aleatórios"
        }
        
        for i, strategy in enumerate(self.cv_strategies, 1):
            print(f"{i:2d}. {strategy.replace('_', ' ').title()}")
            print(f"    {strategy_descriptions[strategy]}")
            print()
    
    def list_studies(self) -> None:
        """Lista estudos de otimização existentes"""
        print("\n📚 Estudos de Otimização Existentes:")
        print("=" * 50)
        
        import glob
        
        # Buscar arquivos de estudo
        study_files = glob.glob("optimization/*.db")
        
        if not study_files:
            print("Nenhum estudo encontrado.")
            return
        
        for i, file_path in enumerate(study_files, 1):
            study_name = os.path.basename(file_path).replace(".db", "")
            
            # Obter informações do arquivo
            stat = os.stat(file_path)
            created_at = datetime.fromtimestamp(stat.st_ctime)
            modified_at = datetime.fromtimestamp(stat.st_mtime)
            size = stat.st_size
            
            print(f"{i:2d}. {study_name}")
            print(f"    Criado: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    Modificado: {modified_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    Tamanho: {size:,} bytes")
            print()
    
    def show_study_details(self, study_name: str) -> None:
        """Mostra detalhes de um estudo"""
        try:
            optimizer = HyperparameterOptimizer(study_name=study_name)
            
            print(f"\n📊 Detalhes do Estudo: {study_name}")
            print("=" * 50)
            
            print(f"Melhor Score: {optimizer.get_best_score():.6f}")
            print(f"Número de Tentativas: {len(optimizer.study.trials)}")
            print(f"Direção: {optimizer.direction}")
            print(f"Estratégia CV: {optimizer.cv_manager.strategy}")
            print(f"Scoring: {optimizer.scoring}")
            
            print("\nMelhores Parâmetros:")
            best_params = optimizer.get_best_params()
            for param, value in best_params.items():
                print(f"  {param}: {value}")
            
            print("\nHistórico de Otimização (últimas 5 tentativas):")
            history = optimizer.get_optimization_history()
            for trial in history[-5:]:
                print(f"  Trial {trial['trial_number']}: {trial['value']:.6f}")
                print(f"    Parâmetros: {trial['params']}")
                print()
                
        except Exception as e:
            print(f"❌ Erro ao carregar estudo: {e}")
    
    def start_optimization(
        self,
        model_name: str,
        study_name: str,
        n_trials: int = 100,
        timeout: Optional[int] = None,
        cv_strategy: str = "time_series",
        scoring: str = "accuracy",
        random_state: Optional[int] = None,
        async_mode: bool = False
    ) -> None:
        """Inicia uma otimização"""
        
        if model_name not in self.supported_models:
            print(f"❌ Modelo '{model_name}' não suportado.")
            print(f"Modelos disponíveis: {', '.join(self.supported_models)}")
            return
        
        if cv_strategy not in self.cv_strategies:
            print(f"❌ Estratégia CV '{cv_strategy}' não suportada.")
            print(f"Estratégias disponíveis: {', '.join(self.cv_strategies)}")
            return
        
        print(f"\n🚀 Iniciando Otimização:")
        print(f"   Modelo: {model_name}")
        print(f"   Estudo: {study_name}")
        print(f"   Tentativas: {n_trials}")
        print(f"   Estratégia CV: {cv_strategy}")
        print(f"   Scoring: {scoring}")
        print(f"   Modo: {'Assíncrono' if async_mode else 'Síncrono'}")
        print("=" * 50)
        
        if async_mode:
            # Modo assíncrono usando Celery
            try:
                # Criar dados de exemplo (em produção, carregar do banco)
                import numpy as np
                X_data = np.random.randn(1000, 10).tolist()
                y_data = np.random.randint(0, 3, 1000).tolist()
                
                task = optimize_single_model.delay(
                    model_name=model_name,
                    X_data=X_data,
                    y_data=y_data,
                    study_name=study_name,
                    n_trials=n_trials,
                    timeout=timeout,
                    cv_strategy=cv_strategy,
                    scoring=scoring,
                    random_state=random_state
                )
                
                print(f"✅ Tarefa iniciada: {task.id}")
                print(f"Status: {task.status}")
                
                # Monitorar progresso
                self.monitor_task(task.id)
                
            except Exception as e:
                print(f"❌ Erro ao iniciar otimização assíncrona: {e}")
        else:
            # Modo síncrono
            try:
                # Criar dados de exemplo
                import numpy as np
                X = np.random.randn(1000, 10)
                y = np.random.randint(0, 3, 1000)
                
                optimizer = HyperparameterOptimizer(
                    study_name=study_name,
                    n_trials=n_trials,
                    timeout=timeout,
                    cv_strategy=cv_strategy,
                    cv_params={"n_splits": 3, "gap": 1},
                    scoring=scoring,
                    random_state=random_state
                )
                
                # Executar otimização baseada no modelo
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
                    print(f"❌ Modelo '{model_name}' não implementado.")
                    return
                
                print(f"✅ Otimização concluída!")
                print(f"Melhor Score: {optimizer.get_best_score():.6f}")
                print(f"Melhores Parâmetros: {optimizer.get_best_params()}")
                
            except Exception as e:
                print(f"❌ Erro na otimização: {e}")
    
    def start_multi_optimization(
        self,
        model_names: List[str],
        study_name: str,
        n_trials: int = 100,
        timeout: Optional[int] = None,
        cv_strategy: str = "time_series",
        scoring: str = "accuracy",
        random_state: Optional[int] = None,
        async_mode: bool = False
    ) -> None:
        """Inicia otimização de múltiplos modelos"""
        
        # Validar modelos
        invalid_models = [m for m in model_names if m not in self.supported_models]
        if invalid_models:
            print(f"❌ Modelos não suportados: {', '.join(invalid_models)}")
            print(f"Modelos disponíveis: {', '.join(self.supported_models)}")
            return
        
        print(f"\n🚀 Iniciando Otimização Multi-Modelo:")
        print(f"   Modelos: {', '.join(model_names)}")
        print(f"   Estudo: {study_name}")
        print(f"   Tentativas por modelo: {n_trials}")
        print(f"   Estratégia CV: {cv_strategy}")
        print(f"   Scoring: {scoring}")
        print(f"   Modo: {'Assíncrono' if async_mode else 'Síncrono'}")
        print("=" * 50)
        
        if async_mode:
            # Modo assíncrono usando Celery
            try:
                import numpy as np
                X_data = np.random.randn(1000, 10).tolist()
                y_data = np.random.randint(0, 3, 1000).tolist()
                
                task = optimize_multiple_models.delay(
                    model_names=model_names,
                    X_data=X_data,
                    y_data=y_data,
                    study_name=study_name,
                    n_trials=n_trials,
                    timeout=timeout,
                    cv_strategy=cv_strategy,
                    scoring=scoring,
                    random_state=random_state
                )
                
                print(f"✅ Tarefa multi-modelo iniciada: {task.id}")
                print(f"Status: {task.status}")
                
                self.monitor_task(task.id)
                
            except Exception as e:
                print(f"❌ Erro ao iniciar otimização multi-modelo: {e}")
        else:
            # Modo síncrono
            try:
                import numpy as np
                X = np.random.randn(1000, 10)
                y = np.random.randint(0, 3, 1000)
                
                multi_optimizer = MultiModelOptimizer(
                    models=model_names,
                    study_name=study_name,
                    n_trials=n_trials,
                    timeout=timeout,
                    cv_strategy=cv_strategy,
                    cv_params={"n_splits": 3, "gap": 1},
                    scoring=scoring,
                    random_state=random_state
                )
                
                results = multi_optimizer.optimize_all(X, y)
                
                print(f"✅ Otimização multi-modelo concluída!")
                
                for model_name, study in results.items():
                    optimizer = multi_optimizer.optimizers[model_name]
                    print(f"   {model_name}: {optimizer.get_best_score():.6f}")
                
                best_model, best_params, best_score = multi_optimizer.get_best_model()
                print(f"   Melhor modelo: {best_model} ({best_score:.6f})")
                
            except Exception as e:
                print(f"❌ Erro na otimização multi-modelo: {e}")
    
    def monitor_task(self, task_id: str) -> None:
        """Monitora uma tarefa assíncrona"""
        from celery.result import AsyncResult
        
        result = AsyncResult(task_id)
        
        print(f"\n📊 Monitorando Tarefa: {task_id}")
        print("=" * 30)
        
        while not result.ready():
            print(f"Status: {result.status}")
            if result.info:
                print(f"Info: {result.info}")
            time.sleep(5)
        
        print(f"Status Final: {result.status}")
        
        if result.successful():
            print("✅ Tarefa concluída com sucesso!")
            print(f"Resultado: {result.result}")
        else:
            print("❌ Tarefa falhou!")
            print(f"Erro: {result.result}")
    
    def export_results(
        self,
        study_name: str,
        model_name: str,
        export_format: str = "json"
    ) -> None:
        """Exporta resultados de otimização"""
        
        if export_format not in ["json", "csv", "pickle"]:
            print(f"❌ Formato '{export_format}' não suportado.")
            print("Formatos disponíveis: json, csv, pickle")
            return
        
        print(f"\n📤 Exportando Resultados:")
        print(f"   Estudo: {study_name}")
        print(f"   Modelo: {model_name}")
        print(f"   Formato: {export_format}")
        print("=" * 40)
        
        try:
            task = export_optimization_results.delay(
                study_name=study_name,
                model_name=model_name,
                export_format=export_format
            )
            
            print(f"✅ Exportação iniciada: {task.id}")
            self.monitor_task(task.id)
            
        except Exception as e:
            print(f"❌ Erro ao exportar resultados: {e}")
    
    def cleanup_old_studies(self, days_old: int = 30) -> None:
        """Limpa estudos antigos"""
        
        print(f"\n🧹 Limpando Estudos Antigos (>{days_old} dias):")
        print("=" * 40)
        
        try:
            task = cleanup_old_studies.delay(days_old=days_old)
            
            print(f"✅ Limpeza iniciada: {task.id}")
            self.monitor_task(task.id)
            
        except Exception as e:
            print(f"❌ Erro na limpeza: {e}")
    
    def run_interactive_mode(self) -> None:
        """Executa modo interativo"""
        print("\n🎯 Modo Interativo - Otimização de Hiperparâmetros")
        print("=" * 60)
        
        while True:
            print("\nOpções disponíveis:")
            print("1. Listar modelos suportados")
            print("2. Listar estratégias de validação cruzada")
            print("3. Listar estudos existentes")
            print("4. Mostrar detalhes de um estudo")
            print("5. Iniciar otimização (modelo único)")
            print("6. Iniciar otimização (múltiplos modelos)")
            print("7. Exportar resultados")
            print("8. Limpar estudos antigos")
            print("9. Sair")
            
            choice = input("\nEscolha uma opção (1-9): ").strip()
            
            if choice == "1":
                self.list_models()
            elif choice == "2":
                self.list_cv_strategies()
            elif choice == "3":
                self.list_studies()
            elif choice == "4":
                study_name = input("Nome do estudo: ").strip()
                if study_name:
                    self.show_study_details(study_name)
            elif choice == "5":
                self._interactive_single_optimization()
            elif choice == "6":
                self._interactive_multi_optimization()
            elif choice == "7":
                self._interactive_export()
            elif choice == "8":
                days = input("Dias para considerar antigos (padrão: 30): ").strip()
                days_old = int(days) if days.isdigit() else 30
                self.cleanup_old_studies(days_old)
            elif choice == "9":
                print("👋 Até logo!")
                break
            else:
                print("❌ Opção inválida. Tente novamente.")
    
    def _interactive_single_optimization(self) -> None:
        """Interface interativa para otimização única"""
        print("\nModelos disponíveis:")
        for i, model in enumerate(self.supported_models, 1):
            print(f"{i}. {model}")
        
        model_idx = input("Escolha o modelo (número): ").strip()
        try:
            model_idx = int(model_idx) - 1
            model_name = self.supported_models[model_idx]
        except (ValueError, IndexError):
            print("❌ Modelo inválido.")
            return
        
        study_name = input("Nome do estudo: ").strip()
        if not study_name:
            print("❌ Nome do estudo é obrigatório.")
            return
        
        n_trials = input("Número de tentativas (padrão: 100): ").strip()
        n_trials = int(n_trials) if n_trials.isdigit() else 100
        
        timeout = input("Timeout em segundos (opcional): ").strip()
        timeout = int(timeout) if timeout.isdigit() else None
        
        cv_strategy = input("Estratégia CV (padrão: time_series): ").strip()
        cv_strategy = cv_strategy if cv_strategy else "time_series"
        
        scoring = input("Métrica de avaliação (padrão: accuracy): ").strip()
        scoring = scoring if scoring else "accuracy"
        
        async_mode = input("Modo assíncrono? (s/N): ").strip().lower() == 's'
        
        self.start_optimization(
            model_name=model_name,
            study_name=study_name,
            n_trials=n_trials,
            timeout=timeout,
            cv_strategy=cv_strategy,
            scoring=scoring,
            async_mode=async_mode
        )
    
    def _interactive_multi_optimization(self) -> None:
        """Interface interativa para otimização multi-modelo"""
        print("\nModelos disponíveis:")
        for i, model in enumerate(self.supported_models, 1):
            print(f"{i}. {model}")
        
        model_indices = input("Escolha os modelos (números separados por vírgula): ").strip()
        try:
            indices = [int(x.strip()) - 1 for x in model_indices.split(',')]
            model_names = [self.supported_models[i] for i in indices]
        except (ValueError, IndexError):
            print("❌ Modelos inválidos.")
            return
        
        study_name = input("Nome do estudo: ").strip()
        if not study_name:
            print("❌ Nome do estudo é obrigatório.")
            return
        
        n_trials = input("Número de tentativas por modelo (padrão: 100): ").strip()
        n_trials = int(n_trials) if n_trials.isdigit() else 100
        
        timeout = input("Timeout em segundos (opcional): ").strip()
        timeout = int(timeout) if timeout.isdigit() else None
        
        cv_strategy = input("Estratégia CV (padrão: time_series): ").strip()
        cv_strategy = cv_strategy if cv_strategy else "time_series"
        
        scoring = input("Métrica de avaliação (padrão: accuracy): ").strip()
        scoring = scoring if scoring else "accuracy"
        
        async_mode = input("Modo assíncrono? (s/N): ").strip().lower() == 's'
        
        self.start_multi_optimization(
            model_names=model_names,
            study_name=study_name,
            n_trials=n_trials,
            timeout=timeout,
            cv_strategy=cv_strategy,
            scoring=scoring,
            async_mode=async_mode
        )
    
    def _interactive_export(self) -> None:
        """Interface interativa para exportação"""
        study_name = input("Nome do estudo: ").strip()
        if not study_name:
            print("❌ Nome do estudo é obrigatório.")
            return
        
        model_name = input("Nome do modelo: ").strip()
        if not model_name:
            print("❌ Nome do modelo é obrigatório.")
            return
        
        print("Formatos disponíveis: json, csv, pickle")
        export_format = input("Formato (padrão: json): ").strip()
        export_format = export_format if export_format else "json"
        
        self.export_results(study_name, model_name, export_format)


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Gerenciador de Otimizações de Hiperparâmetros")
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando list-models
    subparsers.add_parser('list-models', help='Lista modelos suportados')
    
    # Comando list-cv-strategies
    subparsers.add_parser('list-cv-strategies', help='Lista estratégias de validação cruzada')
    
    # Comando list-studies
    subparsers.add_parser('list-studies', help='Lista estudos existentes')
    
    # Comando show-study
    show_parser = subparsers.add_parser('show-study', help='Mostra detalhes de um estudo')
    show_parser.add_argument('study_name', help='Nome do estudo')
    
    # Comando optimize
    optimize_parser = subparsers.add_parser('optimize', help='Inicia otimização')
    optimize_parser.add_argument('model_name', help='Nome do modelo')
    optimize_parser.add_argument('study_name', help='Nome do estudo')
    optimize_parser.add_argument('--n-trials', type=int, default=100, help='Número de tentativas')
    optimize_parser.add_argument('--timeout', type=int, help='Timeout em segundos')
    optimize_parser.add_argument('--cv-strategy', default='time_series', help='Estratégia de validação cruzada')
    optimize_parser.add_argument('--scoring', default='accuracy', help='Métrica de avaliação')
    optimize_parser.add_argument('--async', action='store_true', help='Modo assíncrono')
    
    # Comando optimize-multi
    multi_parser = subparsers.add_parser('optimize-multi', help='Inicia otimização multi-modelo')
    multi_parser.add_argument('model_names', nargs='+', help='Nomes dos modelos')
    multi_parser.add_argument('study_name', help='Nome do estudo')
    multi_parser.add_argument('--n-trials', type=int, default=100, help='Número de tentativas por modelo')
    multi_parser.add_argument('--timeout', type=int, help='Timeout em segundos')
    multi_parser.add_argument('--cv-strategy', default='time_series', help='Estratégia de validação cruzada')
    multi_parser.add_argument('--scoring', default='accuracy', help='Métrica de avaliação')
    multi_parser.add_argument('--async', action='store_true', help='Modo assíncrono')
    
    # Comando export
    export_parser = subparsers.add_parser('export', help='Exporta resultados')
    export_parser.add_argument('study_name', help='Nome do estudo')
    export_parser.add_argument('model_name', help='Nome do modelo')
    export_parser.add_argument('--format', default='json', choices=['json', 'csv', 'pickle'], help='Formato de exportação')
    
    # Comando cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='Limpa estudos antigos')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Idade em dias para considerar antigos')
    
    # Comando interactive
    subparsers.add_parser('interactive', help='Modo interativo')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = OptimizationManager()
    
    try:
        if args.command == 'list-models':
            manager.list_models()
        elif args.command == 'list-cv-strategies':
            manager.list_cv_strategies()
        elif args.command == 'list-studies':
            manager.list_studies()
        elif args.command == 'show-study':
            manager.show_study_details(args.study_name)
        elif args.command == 'optimize':
            manager.start_optimization(
                model_name=args.model_name,
                study_name=args.study_name,
                n_trials=args.n_trials,
                timeout=args.timeout,
                cv_strategy=args.cv_strategy,
                scoring=args.scoring,
                async_mode=getattr(args, 'async', False)
            )
        elif args.command == 'optimize-multi':
            manager.start_multi_optimization(
                model_names=args.model_names,
                study_name=args.study_name,
                n_trials=args.n_trials,
                timeout=args.timeout,
                cv_strategy=args.cv_strategy,
                scoring=args.scoring,
                async_mode=getattr(args, 'async', False)
            )
        elif args.command == 'export':
            manager.export_results(args.study_name, args.model_name, args.format)
        elif args.command == 'cleanup':
            manager.cleanup_old_studies(args.days)
        elif args.command == 'interactive':
            manager.run_interactive_mode()
    
    except KeyboardInterrupt:
        print("\n\n👋 Operação cancelada pelo usuário.")
    except Exception as e:
        logger.error(f"Erro: {e}")
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    main()
