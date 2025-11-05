#!/usr/bin/env python3
"""
MaraBet AI - Gerador de Imagens Responsivas
Gera múltiplos tamanhos de imagens otimizadas para diferentes dispositivos
"""

import os
from PIL import Image, ImageDraw, ImageFont
import json

# Diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = BASE_DIR

# Tamanhos para PWA Icons
PWA_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Tamanhos para Favicons
FAVICON_SIZES = [16, 32, 180]  # 16x16, 32x32, 180x180 (Apple Touch Icon)

# Cores do tema
PRIMARY_COLOR = (26, 115, 232)  # #1a73e8
SECONDARY_COLOR = (52, 168, 83)  # #34a853
WHITE = (255, 255, 255)
DARK = (32, 33, 36)

def create_logo_icon(size, color=PRIMARY_COLOR, bg_color=WHITE):
    """Cria ícone do logo MaraBet AI"""
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Círculo de fundo
    padding = size // 10
    draw.ellipse([padding, padding, size-padding, size-padding], fill=color)
    
    # Letra "M" estilizada
    try:
        # Tentar usar fonte do sistema
        font_size = size // 2
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback para fonte padrão
        font = ImageFont.load_default()
    
    text = "M"
    
    # Centralizar texto
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - size // 20
    
    draw.text((x, y), text, fill=WHITE, font=font)
    
    return img

def create_badge_icon(size):
    """Cria badge icon para notificações"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Círculo vermelho
    draw.ellipse([0, 0, size, size], fill=(234, 67, 53))
    
    return img

def create_placeholder_image(width, height, text="MaraBet AI"):
    """Cria imagem placeholder"""
    img = Image.new('RGB', (width, height), (240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Texto
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), text, fill=(153, 153, 153), font=font)
    
    return img

def generate_pwa_icons():
    """Gera ícones PWA em múltiplos tamanhos"""
    print("📱 Gerando ícones PWA...")
    
    for size in PWA_SIZES:
        icon = create_logo_icon(size)
        filename = f"icon-{size}x{size}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        icon.save(filepath, 'PNG', optimize=True)
        print(f"  ✅ {filename}")

def generate_favicons():
    """Gera favicons"""
    print("🌐 Gerando favicons...")
    
    # 16x16 e 32x32
    for size in [16, 32]:
        icon = create_logo_icon(size)
        filename = f"favicon-{size}x{size}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        icon.save(filepath, 'PNG', optimize=True)
        print(f"  ✅ {filename}")
    
    # Apple Touch Icon 180x180
    icon = create_logo_icon(180)
    filepath = os.path.join(OUTPUT_DIR, "apple-touch-icon.png")
    icon.save(filepath, 'PNG', optimize=True)
    print(f"  ✅ apple-touch-icon.png")
    
    # favicon.ico (multi-size)
    icon_16 = create_logo_icon(16)
    icon_32 = create_logo_icon(32)
    filepath = os.path.join(OUTPUT_DIR, "favicon.ico")
    icon_32.save(filepath, format='ICO', sizes=[(16, 16), (32, 32)])
    print(f"  ✅ favicon.ico")

def generate_badges():
    """Gera badges para notificações"""
    print("🔔 Gerando badges...")
    
    badge = create_badge_icon(72)
    filepath = os.path.join(OUTPUT_DIR, "badge-72x72.png")
    badge.save(filepath, 'PNG', optimize=True)
    print(f"  ✅ badge-72x72.png")

def generate_shortcuts():
    """Gera ícones para shortcuts do PWA"""
    print("⚡ Gerando ícones de shortcuts...")
    
    shortcuts = [
        ("predictions", "⚽", PRIMARY_COLOR),
        ("live", "🔴", (234, 67, 53)),
        ("bankroll", "💰", (251, 188, 4))
    ]
    
    for name, emoji, color in shortcuts:
        icon = create_logo_icon(192, color)
        filename = f"shortcut-{name}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        icon.save(filepath, 'PNG', optimize=True)
        print(f"  ✅ {filename}")

def generate_og_images():
    """Gera imagens Open Graph e Twitter"""
    print("🌍 Gerando imagens Open Graph...")
    
    # Open Graph (1200x630)
    og_img = create_placeholder_image(1200, 630, "MaraBet AI")
    filepath = os.path.join(OUTPUT_DIR, "og-image.png")
    og_img.save(filepath, 'PNG', optimize=True)
    print(f"  ✅ og-image.png")
    
    # Twitter (1200x600)
    twitter_img = create_placeholder_image(1200, 600, "MaraBet AI")
    filepath = os.path.join(OUTPUT_DIR, "twitter-image.png")
    twitter_img.save(filepath, 'PNG', optimize=True)
    print(f"  ✅ twitter-image.png")

def generate_screenshots():
    """Gera screenshots placeholder"""
    print("📸 Gerando screenshots...")
    
    # Mobile (540x720)
    mobile_1 = create_placeholder_image(540, 720, "Dashboard")
    filepath = os.path.join(OUTPUT_DIR, "screenshot-mobile-1.png")
    mobile_1.save(filepath, 'PNG', optimize=True)
    print(f"  ✅ screenshot-mobile-1.png")
    
    mobile_2 = create_placeholder_image(540, 720, "Previsões")
    filepath = os.path.join(OUTPUT_DIR, "screenshot-mobile-2.png")
    mobile_2.save(filepath, 'PNG', optimize=True)
    print(f"  ✅ screenshot-mobile-2.png")
    
    # Desktop (1280x720)
    desktop = create_placeholder_image(1280, 720, "MaraBet AI Desktop")
    filepath = os.path.join(OUTPUT_DIR, "screenshot-desktop-1.png")
    desktop.save(filepath, 'PNG', optimize=True)
    print(f"  ✅ screenshot-desktop-1.png")

def generate_team_placeholders():
    """Gera placeholders para logos de times"""
    print("⚽ Gerando placeholders de times...")
    
    teams_dir = os.path.join(OUTPUT_DIR, "teams")
    os.makedirs(teams_dir, exist_ok=True)
    
    teams = ["benfica", "porto", "sporting", "braga"]
    
    for team in teams:
        team_icon = create_logo_icon(100, SECONDARY_COLOR)
        filepath = os.path.join(teams_dir, f"{team}.png")
        team_icon.save(filepath, 'PNG', optimize=True)
        print(f"  ✅ teams/{team}.png")

def generate_responsive_images():
    """Gera imagens em múltiplas resoluções"""
    print("🖼️  Gerando imagens responsivas...")
    
    # Configurações de breakpoints
    breakpoints = {
        'mobile': 640,
        'tablet': 1024,
        'desktop': 1920
    }
    
    # Exemplo: banner hero
    for name, width in breakpoints.items():
        height = int(width * 0.5625)  # 16:9 aspect ratio
        img = create_placeholder_image(width, height, f"MaraBet AI - {name.title()}")
        filename = f"hero-{name}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        img.save(filepath, 'JPEG', quality=85, optimize=True)
        print(f"  ✅ {filename}")

def create_logo_svg():
    """Cria logo em SVG (escalável)"""
    print("🎨 Gerando logo SVG...")
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <!-- Círculo de fundo -->
  <circle cx="50" cy="50" r="45" fill="rgb{PRIMARY_COLOR}"/>
  
  <!-- Letra M -->
  <text x="50" y="70" font-family="Arial, sans-serif" font-size="60" 
        font-weight="bold" fill="white" text-anchor="middle">M</text>
</svg>'''
    
    filepath = os.path.join(OUTPUT_DIR, "logo.svg")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"  ✅ logo.svg")

def generate_image_config():
    """Gera arquivo de configuração JSON"""
    print("📋 Gerando configuração de imagens...")
    
    config = {
        "version": "1.0.0",
        "pwa_icons": [f"icon-{size}x{size}.png" for size in PWA_SIZES],
        "favicons": [
            "favicon-16x16.png",
            "favicon-32x32.png",
            "apple-touch-icon.png",
            "favicon.ico"
        ],
        "shortcuts": [
            "shortcut-predictions.png",
            "shortcut-live.png",
            "shortcut-bankroll.png"
        ],
        "social": [
            "og-image.png",
            "twitter-image.png"
        ],
        "screenshots": [
            "screenshot-mobile-1.png",
            "screenshot-mobile-2.png",
            "screenshot-desktop-1.png"
        ],
        "responsive": {
            "mobile": "hero-mobile.jpg",
            "tablet": "hero-tablet.jpg",
            "desktop": "hero-desktop.jpg"
        },
        "logo": "logo.svg"
    }
    
    filepath = os.path.join(OUTPUT_DIR, "images-config.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"  ✅ images-config.json")

def main():
    print("=" * 60)
    print("MaraBet AI - Gerador de Imagens Responsivas")
    print("=" * 60)
    print()
    
    # Criar diretório se não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Gerar todos os assets
    generate_pwa_icons()
    generate_favicons()
    generate_badges()
    generate_shortcuts()
    generate_og_images()
    generate_screenshots()
    generate_team_placeholders()
    generate_responsive_images()
    create_logo_svg()
    generate_image_config()
    
    print()
    print("=" * 60)
    print("✅ Todas as imagens foram geradas com sucesso!")
    print(f"📁 Localização: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()

