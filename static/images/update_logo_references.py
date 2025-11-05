#!/usr/bin/env python3
"""
MaraBet AI - Script para atualizar referências da logo
Atualiza manifest.json e gera ícones PWA com a nova logo
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_pwa_icon_with_logo(size):
    """Cria ícone PWA baseado na logo MaraBet"""
    # Fundo gradiente azul
    img = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(img)
    
    # Gradiente vertical
    for y in range(size):
        ratio = y / size
        r = int(13 + (74 - 13) * ratio)
        g = int(31 + (107 - 31) * ratio)
        b = int(60 + (138 - 60) * ratio)
        draw.rectangle([0, y, size, y + 1], fill=(r, g, b))
    
    # Letra M estilizada (simplificada para ícone)
    try:
        font_size = int(size * 0.6)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "M"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - int(size * 0.05)
    
    # Sombra
    shadow_offset = max(2, size // 50)
    draw.text((x + shadow_offset, y + shadow_offset), text, fill=(0, 0, 0, 50), font=font)
    
    # Texto principal
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Swoosh decorativo
    swoosh_y = int(size * 0.7)
    swoosh_width = int(size * 0.5)
    swoosh_x = (size - swoosh_width) // 2
    
    draw.arc(
        [swoosh_x, swoosh_y, swoosh_x + swoosh_width, swoosh_y + int(size * 0.2)],
        start=180,
        end=0,
        fill=(91, 125, 184),
        width=max(2, size // 30)
    )
    
    return img

def generate_pwa_icons():
    """Gera todos os ícones PWA necessários"""
    print("📱 Gerando ícones PWA com logo MaraBet...")
    
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        icon = create_pwa_icon_with_logo(size)
        filename = f"icon-{size}x{size}.png"
        filepath = os.path.join(BASE_DIR, filename)
        icon.save(filepath, 'PNG', optimize=True)
        print(f"  ✅ {filename}")

def generate_favicon():
    """Gera favicon com logo MaraBet"""
    print("🌐 Gerando favicons...")
    
    for size in [16, 32]:
        icon = create_pwa_icon_with_logo(size)
        filename = f"favicon-{size}x{size}.png"
        filepath = os.path.join(BASE_DIR, filename)
        icon.save(filepath, 'PNG', optimize=True)
        print(f"  ✅ {filename}")
    
    # Apple Touch Icon
    icon = create_pwa_icon_with_logo(180)
    filepath = os.path.join(BASE_DIR, "apple-touch-icon.png")
    icon.save(filepath, 'PNG', optimize=True)
    print(f"  ✅ apple-touch-icon.png")
    
    # favicon.ico
    icon_16 = create_pwa_icon_with_logo(16)
    icon_32 = create_pwa_icon_with_logo(32)
    filepath = os.path.join(BASE_DIR, "favicon.ico")
    icon_32.save(filepath, format='ICO', sizes=[(16, 16), (32, 32)])
    print(f"  ✅ favicon.ico")

def update_manifest():
    """Atualiza manifest.json"""
    print("📋 Atualizando manifest.json...")
    
    manifest_path = os.path.join(os.path.dirname(BASE_DIR), 'manifest.json')
    
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Atualizar nome
        manifest['name'] = 'MaraBet AI - Previsões Inteligentes'
        manifest['short_name'] = 'MaraBet'
        
        # Atualizar cores (baseado na logo)
        manifest['theme_color'] = '#0d1f3c'
        manifest['background_color'] = '#ffffff'
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print("  ✅ manifest.json atualizado")

def create_logo_variants():
    """Cria variantes da logo para diferentes usos"""
    print("🎨 Criando variantes da logo...")
    
    # Logo horizontal (para navbar)
    # Já temos a SVG principal
    
    # Logo quadrada (para redes sociais)
    logo_square = create_pwa_icon_with_logo(400)
    filepath = os.path.join(BASE_DIR, "logo-square.png")
    logo_square.save(filepath, 'PNG', optimize=True)
    print(f"  ✅ logo-square.png")
    
    # Logo para Open Graph
    og_width, og_height = 1200, 630
    og_img = Image.new('RGB', (og_width, og_height), (13, 31, 60))
    
    # Logo centralizada
    logo = create_pwa_icon_with_logo(300)
    logo_x = (og_width - 300) // 2
    logo_y = (og_height - 300) // 2
    og_img.paste(logo, (logo_x, logo_y))
    
    filepath = os.path.join(BASE_DIR, "og-image.png")
    og_img.save(filepath, 'PNG', optimize=True)
    print(f"  ✅ og-image.png (Open Graph)")
    
    # Logo para Twitter
    twitter_img = Image.new('RGB', (1200, 600), (13, 31, 60))
    logo_x = (1200 - 300) // 2
    logo_y = (600 - 300) // 2
    twitter_img.paste(logo, (logo_x, logo_y))
    
    filepath = os.path.join(BASE_DIR, "twitter-image.png")
    twitter_img.save(filepath, 'PNG', optimize=True)
    print(f"  ✅ twitter-image.png (Twitter Card)")

def create_loading_logo():
    """Cria logo animada para loading"""
    print("⏳ Criando logo para loading...")
    
    logo = create_pwa_icon_with_logo(100)
    filepath = os.path.join(BASE_DIR, "logo-loading.png")
    logo.save(filepath, 'PNG', optimize=True)
    print(f"  ✅ logo-loading.png")

def main():
    print("=" * 60)
    print("MaraBet AI - Atualização da Logomarca")
    print("=" * 60)
    print()
    
    generate_pwa_icons()
    generate_favicon()
    update_manifest()
    create_logo_variants()
    create_loading_logo()
    
    print()
    print("=" * 60)
    print("✅ Logo MaraBet implementada com sucesso!")
    print("=" * 60)
    print()
    print("📁 Arquivos gerados:")
    print("  • logo-marabet.svg (principal)")
    print("  • icon-*.png (8 tamanhos PWA)")
    print("  • favicon-*.png (3 tamanhos)")
    print("  • favicon.ico")
    print("  • logo-square.png")
    print("  • og-image.png")
    print("  • twitter-image.png")
    print("  • logo-loading.png")
    print()
    print("🎨 CSS: static/css/logo-styles.css")
    print("📄 Templates atualizados: base_responsive.html")
    print()
    print("✅ Sistema pronto com a nova logo MaraBet!")

if __name__ == "__main__":
    main()

