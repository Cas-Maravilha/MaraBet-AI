#!/usr/bin/env python3
"""
Demonstração de Acessibilidade e UX - MaraBet AI
Script de demonstração do sistema de acessibilidade
"""

import os
import sys
import argparse
import logging
import json
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from accessibility import (
    LighthouseValidator, AccessibilityChecker, DarkModeManager,
    ExportManager, UXOptimizer
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_lighthouse_validation():
    """Demonstra validação com Lighthouse"""
    try:
        logger.info("🔍 Demonstração do LighthouseValidator")
        
        # Criar validador
        validator = LighthouseValidator()
        
        # URL de exemplo (substituir por URL real do dashboard)
        test_url = "http://localhost:8000"  # Assumindo que o dashboard está rodando localmente
        
        print(f"\n📊 Validando: {test_url}")
        print("⚠️ Nota: Certifique-se de que o dashboard está rodando em http://localhost:8000")
        
        # Validar dashboard
        result = validator.validate_dashboard(test_url)
        
        print(f"\n✅ Validação concluída!")
        print(f"   Acessibilidade: {result.accessibility_score:.1f}%")
        print(f"   Performance: {result.performance_score:.1f}%")
        print(f"   Melhores Práticas: {result.best_practices_score:.1f}%")
        print(f"   SEO: {result.seo_score:.1f}%")
        print(f"   Status: {'✅ APROVADO' if result.passed else '❌ REPROVADO'}")
        
        if result.issues:
            print(f"\n🔍 Problemas encontrados ({len(result.issues)}):")
            for i, issue in enumerate(result.issues[:5], 1):  # Mostrar apenas os primeiros 5
                print(f"   {i}. {issue['title']} ({issue['severity']})")
        
        if result.recommendations:
            print(f"\n💡 Recomendações:")
            for i, rec in enumerate(result.recommendations[:3], 1):  # Mostrar apenas as primeiras 3
                print(f"   {i}. {rec}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração do Lighthouse: {e}")
        return False

def demo_accessibility_checker():
    """Demonstra verificador de acessibilidade"""
    try:
        logger.info("🔍 Demonstração do AccessibilityChecker")
        
        # Criar verificador
        checker = AccessibilityChecker()
        
        # HTML de exemplo para teste
        sample_html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Dashboard MaraBet AI</title>
</head>
<body>
    <h1>Dashboard MaraBet AI</h1>
    
    <img src="chart.png" alt="Gráfico de performance">
    <img src="logo.png">
    
    <form>
        <input type="text" name="username">
        <input type="password" name="password">
        <button type="submit">Entrar</button>
    </form>
    
    <table>
        <tr>
            <th>Liga</th>
            <th>ROI</th>
        </tr>
        <tr>
            <td>Premier League</td>
            <td>15.2%</td>
        </tr>
    </table>
    
    <a href="#">Clique aqui</a>
    <a href="https://example.com">Saiba mais</a>
</body>
</html>
        """
        
        # Salvar HTML temporário
        temp_file = "temp_dashboard.html"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(sample_html)
        
        print(f"\n📊 Verificando arquivo HTML de exemplo...")
        
        # Verificar acessibilidade
        report = checker.check_html_file(temp_file)
        
        print(f"\n✅ Verificação concluída!")
        print(f"   Score: {report.score:.1f}%")
        print(f"   Total de problemas: {report.total_issues}")
        print(f"   Críticos: {report.critical_issues}")
        print(f"   Avisos: {report.warning_issues}")
        print(f"   Informações: {report.info_issues}")
        print(f"   Status: {'✅ APROVADO' if report.passed else '❌ REPROVADO'}")
        
        if report.issues:
            print(f"\n🔍 Problemas encontrados:")
            for i, issue in enumerate(report.issues[:5], 1):  # Mostrar apenas os primeiros 5
                print(f"   {i}. {issue.message} ({issue.severity})")
                print(f"      Sugestão: {issue.suggestion}")
        
        if report.recommendations:
            print(f"\n💡 Recomendações:")
            for i, rec in enumerate(report.recommendations[:3], 1):  # Mostrar apenas as primeiras 3
                print(f"   {i}. {rec}")
        
        # Limpar arquivo temporário
        os.remove(temp_file)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração do AccessibilityChecker: {e}")
        return False

def demo_dark_mode():
    """Demonstra gerenciador de modo escuro"""
    try:
        logger.info("🔍 Demonstração do DarkModeManager")
        
        # Criar gerenciador
        dark_mode = DarkModeManager()
        
        print(f"\n📊 Temas disponíveis:")
        themes = dark_mode.get_available_themes()
        for theme in themes:
            theme_config = dark_mode.themes[theme]
            print(f"   - {theme_config.name} ({theme})")
        
        # Mostrar tema atual
        current_theme = dark_mode.get_current_theme()
        print(f"\n🎨 Tema atual: {current_theme.name}")
        print(f"   Cor primária: {current_theme.primary_color}")
        print(f"   Cor de fundo: {current_theme.background_color}")
        print(f"   Cor do texto: {current_theme.text_color}")
        
        # Gerar CSS
        css = dark_mode.generate_css_variables()
        print(f"\n📝 CSS gerado ({len(css)} caracteres)")
        
        # Gerar seletor de tema
        theme_switcher = dark_mode.generate_theme_switcher_html()
        print(f"🎛️ Seletor de tema gerado ({len(theme_switcher)} caracteres)")
        
        # Testar mudança de tema
        print(f"\n🔄 Testando mudança de tema...")
        if dark_mode.set_theme("dark"):
            print("   ✅ Tema alterado para escuro")
        else:
            print("   ❌ Erro ao alterar tema")
        
        # Mostrar tema após mudança
        new_theme = dark_mode.get_current_theme()
        print(f"   Novo tema: {new_theme.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração do DarkModeManager: {e}")
        return False

def demo_export_manager():
    """Demonstra gerenciador de exportação"""
    try:
        logger.info("🔍 Demonstração do ExportManager")
        
        # Criar gerenciador
        export_manager = ExportManager()
        
        # Dados de exemplo
        sample_data = {
            "relatorio": "Performance MaraBet AI",
            "data": "2024-01-15",
            "metricas": {
                "roi_total": 15.2,
                "taxa_acerto": 68.5,
                "sharpe_ratio": 1.8
            },
            "ligas": [
                {"nome": "Premier League", "roi": 18.3, "partidas": 45},
                {"nome": "La Liga", "roi": 12.7, "partidas": 38},
                {"nome": "Serie A", "roi": 14.1, "partidas": 42}
            ]
        }
        
        print(f"\n📊 Dados de exemplo preparados")
        print(f"   Relatório: {sample_data['relatorio']}")
        print(f"   Data: {sample_data['data']}")
        print(f"   ROI Total: {sample_data['metricas']['roi_total']}%")
        print(f"   Ligas: {len(sample_data['ligas'])}")
        
        # Testar exportação CSV
        print(f"\n📄 Testando exportação CSV...")
        from accessibility.export_manager import ExportConfig
        config = ExportConfig(format="csv", filename="demo_relatorio")
        
        result = export_manager.export_to_csv(sample_data, config)
        if result.success:
            print(f"   ✅ CSV exportado: {result.filename}")
            print(f"   Tamanho: {result.file_size} bytes")
        else:
            print(f"   ❌ Erro: {result.error_message}")
        
        # Testar exportação JSON
        print(f"\n📄 Testando exportação JSON...")
        config.format = "json"
        result = export_manager.export_to_json(sample_data, config)
        if result.success:
            print(f"   ✅ JSON exportado: {result.filename}")
            print(f"   Tamanho: {result.file_size} bytes")
        else:
            print(f"   ❌ Erro: {result.error_message}")
        
        # Mostrar histórico
        history = export_manager.get_export_history()
        print(f"\n📋 Histórico de exportações ({len(history)} arquivos):")
        for file_info in history[:3]:  # Mostrar apenas os primeiros 3
            print(f"   - {file_info['filename']} ({file_info['size']} bytes)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração do ExportManager: {e}")
        return False

def demo_ux_optimizer():
    """Demonstra otimizador de UX"""
    try:
        logger.info("🔍 Demonstração do UXOptimizer")
        
        # Criar otimizador
        ux_optimizer = UXOptimizer()
        
        # Funcionalidades atuais (exemplo)
        current_features = ["dark_mode", "export", "dashboard"]
        
        print(f"\n📊 Funcionalidades atuais: {', '.join(current_features)}")
        
        # Analisar UX
        report = ux_optimizer.analyze_ux(current_features)
        
        print(f"\n✅ Análise UX concluída!")
        print(f"   Score: {report.score:.1f}%")
        print(f"   Total de otimizações: {report.total_optimizations}")
        print(f"   Alta prioridade: {report.high_priority}")
        print(f"   Média prioridade: {report.medium_priority}")
        print(f"   Baixa prioridade: {report.low_priority}")
        
        if report.optimizations:
            print(f"\n🔍 Otimizações sugeridas:")
            for i, opt in enumerate(report.optimizations[:5], 1):  # Mostrar apenas as primeiras 5
                print(f"   {i}. {opt.title} ({opt.priority})")
                print(f"      {opt.description}")
        
        if report.recommendations:
            print(f"\n💡 Recomendações:")
            for i, rec in enumerate(report.recommendations[:3], 1):  # Mostrar apenas as primeiras 3
                print(f"   {i}. {rec}")
        
        # Gerar plano de implementação
        plan = ux_optimizer.generate_implementation_plan(report.optimizations)
        if plan:
            print(f"\n📋 Plano de implementação:")
            print(f"   Esforço total: {plan['estimated_effort']}")
            print(f"   Cronograma sugerido:")
            for sprint, tasks in plan['timeline'].items():
                if tasks:
                    print(f"     {sprint}: {len(tasks)} tarefas")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração do UXOptimizer: {e}")
        return False

def create_comprehensive_demo():
    """Cria demonstração abrangente do sistema de acessibilidade"""
    try:
        logger.info("🚀 Iniciando demonstração abrangente do sistema de acessibilidade")
        
        # Criar diretório de saída
        os.makedirs("accessibility/demo_results", exist_ok=True)
        
        # Executar todas as demonstrações
        demos = [
            ("LighthouseValidator", demo_lighthouse_validation),
            ("AccessibilityChecker", demo_accessibility_checker),
            ("DarkModeManager", demo_dark_mode),
            ("ExportManager", demo_export_manager),
            ("UXOptimizer", demo_ux_optimizer)
        ]
        
        results = {}
        for name, demo_func in demos:
            logger.info(f"\n{'='*50}")
            logger.info(f"Executando demonstração: {name}")
            logger.info(f"{'='*50}")
            
            try:
                success = demo_func()
                results[name] = success
                if success:
                    logger.info(f"✅ {name} - Demonstração concluída com sucesso")
                else:
                    logger.error(f"❌ {name} - Demonstração falhou")
            except Exception as e:
                logger.error(f"❌ {name} - Erro: {e}")
                results[name] = False
        
        # Resumo final
        logger.info(f"\n{'='*50}")
        logger.info("RESUMO DA DEMONSTRAÇÃO")
        logger.info(f"{'='*50}")
        
        successful = sum(results.values())
        total = len(results)
        
        for name, success in results.items():
            status = "✅ SUCESSO" if success else "❌ FALHOU"
            logger.info(f"{name}: {status}")
        
        logger.info(f"\nTotal: {successful}/{total} demonstrações bem-sucedidas")
        
        if successful == total:
            logger.info("🎉 Todas as demonstrações foram executadas com sucesso!")
        else:
            logger.warning(f"⚠️ {total - successful} demonstrações falharam")
        
        return successful == total
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração abrangente: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Demonstração de Acessibilidade e UX - MaraBet AI")
    parser.add_argument("--demo", choices=[
        "lighthouse", "accessibility", "darkmode", "export", "ux", "all"
    ], default="all", help="Tipo de demonstração a executar")
    parser.add_argument("--url", default="http://localhost:8000",
                       help="URL do dashboard para teste")
    parser.add_argument("--output-dir", default="accessibility/demo_results",
                       help="Diretório de saída")
    
    args = parser.parse_args()
    
    # Configurar diretório de saída
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        if args.demo == "all":
            success = create_comprehensive_demo()
        elif args.demo == "lighthouse":
            success = demo_lighthouse_validation()
        elif args.demo == "accessibility":
            success = demo_accessibility_checker()
        elif args.demo == "darkmode":
            success = demo_dark_mode()
        elif args.demo == "export":
            success = demo_export_manager()
        elif args.demo == "ux":
            success = demo_ux_optimizer()
        else:
            logger.error(f"❌ Demonstração desconhecida: {args.demo}")
            success = False
        
        if success:
            logger.info("🎉 Demonstração concluída com sucesso!")
            sys.exit(0)
        else:
            logger.error("❌ Demonstração falhou")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⚠️ Demonstração cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
