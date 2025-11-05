#!/usr/bin/env python3
"""
Gerador de PDF - MaraBet AI
Converte documentos Markdown para PDF profissional
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_pdf_from_markdown(markdown_file: str, output_file: str = None, style: str = "professional"):
    """
    Gera PDF a partir de arquivo Markdown
    
    Args:
        markdown_file: Arquivo Markdown de entrada
        output_file: Arquivo PDF de saída
        style: Estilo do PDF (professional, corporate, modern)
    """
    try:
        if not os.path.exists(markdown_file):
            logger.error(f"❌ Arquivo Markdown não encontrado: {markdown_file}")
            return False
        
        if output_file is None:
            output_file = markdown_file.replace('.md', '.pdf')
        
        logger.info(f"📄 Convertendo {markdown_file} para {output_file}")
        
        # Verificar se pandoc está disponível
        if not check_pandoc():
            logger.error("❌ Pandoc não encontrado. Instale: https://pandoc.org/installing.html")
            return False
        
        # Comando pandoc
        cmd = [
            'pandoc',
            markdown_file,
            '-o', output_file,
            '--pdf-engine=xelatex',
            '--variable', 'geometry:margin=2cm',
            '--variable', 'fontsize=11pt',
            '--variable', 'documentclass=article',
            '--variable', 'colorlinks=true',
            '--variable', 'linkcolor=blue',
            '--variable', 'urlcolor=blue',
            '--variable', 'toccolor=black',
            '--toc',
            '--toc-depth=3',
            '--highlight-style=tango',
            '--metadata', f'title=MaraBet AI - Guia Comercial',
            '--metadata', f'author=Equipe MaraBet AI',
            '--metadata', f'date={datetime.now().strftime("%d/%m/%Y")}'
        ]
        
        # Adicionar estilo específico
        if style == "corporate":
            cmd.extend([
                '--variable', 'mainfont=Times New Roman',
                '--variable', 'sansfont=Arial',
                '--variable', 'monofont=Courier New'
            ])
        elif style == "modern":
            cmd.extend([
                '--variable', 'mainfont=Helvetica',
                '--variable', 'sansfont=Helvetica',
                '--variable', 'monofont=Monaco'
            ])
        else:  # professional
            cmd.extend([
                '--variable', 'mainfont=Georgia',
                '--variable', 'sansfont=Verdana',
                '--variable', 'monofont=Consolas'
            ])
        
        # Executar conversão
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"✅ PDF gerado com sucesso: {output_file}")
            return True
        else:
            logger.error(f"❌ Erro na conversão: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao gerar PDF: {e}")
        return False

def check_pandoc():
    """Verifica se pandoc está disponível"""
    try:
        import subprocess
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def generate_html_from_markdown(markdown_file: str, output_file: str = None, style: str = "professional"):
    """
    Gera HTML a partir de arquivo Markdown
    
    Args:
        markdown_file: Arquivo Markdown de entrada
        output_file: Arquivo HTML de saída
        style: Estilo do HTML
    """
    try:
        if not os.path.exists(markdown_file):
            logger.error(f"❌ Arquivo Markdown não encontrado: {markdown_file}")
            return False
        
        if output_file is None:
            output_file = markdown_file.replace('.md', '.html')
        
        logger.info(f"🌐 Convertendo {markdown_file} para {output_file}")
        
        # Ler arquivo Markdown
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Converter para HTML
        html_content = convert_markdown_to_html(markdown_content, style)
        
        # Salvar HTML
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ HTML gerado com sucesso: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar HTML: {e}")
        return False

def convert_markdown_to_html(markdown_content: str, style: str = "professional") -> str:
    """Converte conteúdo Markdown para HTML"""
    
    # CSS base
    css_styles = {
        "professional": """
        <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f9f9f9;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        h1 {
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
        }
        code {
            background: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
        }
        blockquote {
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background: #f8f9fa;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background: #3498db;
            color: white;
        }
        .toc {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .toc h2 {
            margin-top: 0;
        }
        .toc ul {
            list-style-type: none;
            padding-left: 0;
        }
        .toc li {
            margin: 5px 0;
        }
        .toc a {
            text-decoration: none;
            color: #3498db;
        }
        .toc a:hover {
            text-decoration: underline;
        }
        </style>
        """,
        "corporate": """
        <style>
        body {
            font-family: 'Times New Roman', serif;
            line-height: 1.5;
            color: #000;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background: white;
        }
        .container {
            background: white;
            padding: 30px;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #000;
            font-weight: bold;
        }
        h1 {
            text-align: center;
            font-size: 24pt;
        }
        h2 {
            font-size: 18pt;
            border-bottom: 1px solid #000;
        }
        h3 {
            font-size: 14pt;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            border: 1px solid #000;
            padding: 8px;
            text-align: left;
        }
        th {
            background: #f0f0f0;
            font-weight: bold;
        }
        </style>
        """,
        "modern": """
        <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.7;
            color: #2c3e50;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 50px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            font-weight: 300;
        }
        h1 {
            font-size: 2.5em;
            text-align: center;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        h2 {
            font-size: 1.8em;
            border-left: 4px solid #667eea;
            padding-left: 20px;
            margin-top: 40px;
        }
        code {
            background: #f8f9fa;
            padding: 3px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Consolas', monospace;
            color: #e74c3c;
        }
        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 25px;
            border-radius: 8px;
            overflow-x: auto;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        blockquote {
            border-left: 4px solid #667eea;
            margin: 25px 0;
            padding: 15px 25px;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        th, td {
            border: 1px solid #ddd;
            padding: 15px;
            text-align: left;
        }
        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 500;
        }
        tr:nth-child(even) {
            background: #f8f9fa;
        }
        </style>
        """
    }
    
    # Converter Markdown básico para HTML
    html_content = markdown_content
    
    # Headers
    html_content = html_content.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
    html_content = html_content.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
    html_content = html_content.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
    html_content = html_content.replace('#### ', '<h4>').replace('\n#### ', '</h4>\n<h4>')
    
    # Fechar headers
    html_content = html_content.replace('<h1>', '<h1>', 1) + '</h1>'
    html_content = html_content.replace('<h2>', '<h2>', 1) + '</h2>'
    html_content = html_content.replace('<h3>', '<h3>', 1) + '</h3>'
    html_content = html_content.replace('<h4>', '<h4>', 1) + '</h4>'
    
    # Bold e Italic
    html_content = html_content.replace('**', '<strong>').replace('**', '</strong>')
    html_content = html_content.replace('*', '<em>').replace('*', '</em>')
    
    # Code
    html_content = html_content.replace('`', '<code>').replace('`', '</code>')
    
    # Links
    import re
    html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html_content)
    
    # Listas
    html_content = html_content.replace('- ', '<li>')
    html_content = html_content.replace('\n<li>', '\n<ul>\n<li>')
    html_content = html_content.replace('\n\n', '</ul>\n\n')
    
    # Quebras de linha
    html_content = html_content.replace('\n', '<br>\n')
    
    # Criar HTML completo
    full_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MaraBet AI - Guia Comercial</title>
    {css_styles.get(style, css_styles["professional"])}
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>
    """
    
    return full_html

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Gerador de PDF/HTML - MaraBet AI")
    parser.add_argument("input_file", help="Arquivo Markdown de entrada")
    parser.add_argument("--output", "-o", help="Arquivo de saída")
    parser.add_argument("--format", "-f", choices=["pdf", "html"], default="pdf", help="Formato de saída")
    parser.add_argument("--style", "-s", choices=["professional", "corporate", "modern"], default="professional", help="Estilo do documento")
    
    args = parser.parse_args()
    
    try:
        if args.format == "pdf":
            success = generate_pdf_from_markdown(args.input_file, args.output, args.style)
        else:
            success = generate_html_from_markdown(args.input_file, args.output, args.style)
        
        if success:
            print(f"✅ Documento gerado com sucesso!")
            return 0
        else:
            print("❌ Erro ao gerar documento")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
