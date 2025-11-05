"""
Gerenciador de Modo Escuro - MaraBet AI
Sistema completo de modo escuro para o dashboard
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

@dataclass
class ThemeConfig:
    """Configuração de tema"""
    name: str
    primary_color: str
    secondary_color: str
    background_color: str
    surface_color: str
    text_color: str
    text_secondary_color: str
    accent_color: str
    success_color: str
    warning_color: str
    error_color: str
    info_color: str
    border_color: str
    shadow_color: str
    chart_colors: List[str]

class DarkModeManager:
    """
    Gerenciador de modo escuro para MaraBet AI
    Gerencia temas, preferências do usuário e persistência
    """
    
    def __init__(self, config_file: str = "accessibility/theme_config.json"):
        """
        Inicializa o gerenciador de modo escuro
        
        Args:
            config_file: Arquivo de configuração de temas
        """
        self.config_file = config_file
        self.themes = self._load_theme_configs()
        self.current_theme = "light"
        self.user_preferences = self._load_user_preferences()
        
        logger.info("DarkModeManager inicializado")
    
    def _load_theme_configs(self) -> Dict[str, ThemeConfig]:
        """Carrega configurações de temas"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = self._get_default_theme_configs()
                self._save_theme_configs(data)
            
            themes = {}
            for theme_name, theme_data in data.items():
                themes[theme_name] = ThemeConfig(**theme_data)
            
            return themes
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar temas: {e}")
            return self._get_default_theme_configs()
    
    def _get_default_theme_configs(self) -> Dict[str, Dict[str, Any]]:
        """Retorna configurações padrão de temas"""
        return {
            "light": {
                "name": "Claro",
                "primary_color": "#667eea",
                "secondary_color": "#764ba2",
                "background_color": "#ffffff",
                "surface_color": "#f8f9fa",
                "text_color": "#212529",
                "text_secondary_color": "#6c757d",
                "accent_color": "#007bff",
                "success_color": "#28a745",
                "warning_color": "#ffc107",
                "error_color": "#dc3545",
                "info_color": "#17a2b8",
                "border_color": "#dee2e6",
                "shadow_color": "rgba(0, 0, 0, 0.1)",
                "chart_colors": ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe", "#00f2fe"]
            },
            "dark": {
                "name": "Escuro",
                "primary_color": "#667eea",
                "secondary_color": "#764ba2",
                "background_color": "#121212",
                "surface_color": "#1e1e1e",
                "text_color": "#ffffff",
                "text_secondary_color": "#b0b0b0",
                "accent_color": "#0d6efd",
                "success_color": "#198754",
                "warning_color": "#ffc107",
                "error_color": "#dc3545",
                "info_color": "#0dcaf0",
                "border_color": "#333333",
                "shadow_color": "rgba(0, 0, 0, 0.3)",
                "chart_colors": ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe", "#00f2fe"]
            },
            "high_contrast": {
                "name": "Alto Contraste",
                "primary_color": "#0000ff",
                "secondary_color": "#800080",
                "background_color": "#ffffff",
                "surface_color": "#f0f0f0",
                "text_color": "#000000",
                "text_secondary_color": "#333333",
                "accent_color": "#0000ff",
                "success_color": "#008000",
                "warning_color": "#ff8000",
                "error_color": "#ff0000",
                "info_color": "#0080ff",
                "border_color": "#000000",
                "shadow_color": "rgba(0, 0, 0, 0.5)",
                "chart_colors": ["#0000ff", "#800080", "#008000", "#ff8000", "#ff0000", "#0080ff"]
            },
            "blue_theme": {
                "name": "Tema Azul",
                "primary_color": "#1e3a8a",
                "secondary_color": "#3b82f6",
                "background_color": "#f8fafc",
                "surface_color": "#ffffff",
                "text_color": "#1e293b",
                "text_secondary_color": "#64748b",
                "accent_color": "#3b82f6",
                "success_color": "#059669",
                "warning_color": "#d97706",
                "error_color": "#dc2626",
                "info_color": "#0891b2",
                "border_color": "#e2e8f0",
                "shadow_color": "rgba(0, 0, 0, 0.1)",
                "chart_colors": ["#1e3a8a", "#3b82f6", "#06b6d4", "#8b5cf6", "#ec4899", "#f59e0b"]
            }
        }
    
    def _save_theme_configs(self, data: Dict[str, Dict[str, Any]]):
        """Salva configurações de temas"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar temas: {e}")
    
    def _load_user_preferences(self) -> Dict[str, Any]:
        """Carrega preferências do usuário"""
        try:
            prefs_file = "accessibility/user_preferences.json"
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "theme": "light",
                    "auto_switch": False,
                    "preferred_time": "18:00",
                    "font_size": "medium",
                    "high_contrast": False
                }
        except Exception as e:
            logger.error(f"❌ Erro ao carregar preferências: {e}")
            return {"theme": "light", "auto_switch": False}
    
    def save_user_preferences(self, preferences: Dict[str, Any]):
        """Salva preferências do usuário"""
        try:
            prefs_file = "accessibility/user_preferences.json"
            os.makedirs(os.path.dirname(prefs_file), exist_ok=True)
            
            self.user_preferences.update(preferences)
            
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Preferências salvas")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar preferências: {e}")
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Define tema atual
        
        Args:
            theme_name: Nome do tema
            
        Returns:
            True se definido com sucesso
        """
        try:
            if theme_name not in self.themes:
                logger.error(f"❌ Tema não encontrado: {theme_name}")
                return False
            
            self.current_theme = theme_name
            self.user_preferences["theme"] = theme_name
            self.save_user_preferences(self.user_preferences)
            
            logger.info(f"✅ Tema definido para: {theme_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao definir tema: {e}")
            return False
    
    def get_current_theme(self) -> ThemeConfig:
        """Retorna tema atual"""
        return self.themes.get(self.current_theme, self.themes["light"])
    
    def get_available_themes(self) -> List[str]:
        """Retorna lista de temas disponíveis"""
        return list(self.themes.keys())
    
    def generate_css_variables(self, theme_name: Optional[str] = None) -> str:
        """
        Gera variáveis CSS para o tema
        
        Args:
            theme_name: Nome do tema (opcional)
            
        Returns:
            CSS com variáveis do tema
        """
        try:
            theme = self.themes.get(theme_name or self.current_theme, self.themes["light"])
            
            css = f"""
:root {{
    /* Cores principais */
    --primary-color: {theme.primary_color};
    --secondary-color: {theme.secondary_color};
    --accent-color: {theme.accent_color};
    
    /* Cores de fundo */
    --background-color: {theme.background_color};
    --surface-color: {theme.surface_color};
    
    /* Cores de texto */
    --text-color: {theme.text_color};
    --text-secondary-color: {theme.text_secondary_color};
    
    /* Cores de status */
    --success-color: {theme.success_color};
    --warning-color: {theme.warning_color};
    --error-color: {theme.error_color};
    --info-color: {theme.info_color};
    
    /* Cores de interface */
    --border-color: {theme.border_color};
    --shadow-color: {theme.shadow_color};
    
    /* Cores de gráficos */
    --chart-color-1: {theme.chart_colors[0]};
    --chart-color-2: {theme.chart_colors[1]};
    --chart-color-3: {theme.chart_colors[2]};
    --chart-color-4: {theme.chart_colors[3]};
    --chart-color-5: {theme.chart_colors[4]};
    --chart-color-6: {theme.chart_colors[5]};
    
    /* Transições */
    --transition-duration: 0.3s;
    --transition-timing: ease-in-out;
}}
"""
            return css
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar CSS: {e}")
            return ""
    
    def generate_theme_switcher_html(self) -> str:
        """Gera HTML para seletor de tema"""
        try:
            themes = self.get_available_themes()
            current_theme = self.current_theme
            
            html = f"""
<div class="theme-switcher" role="group" aria-label="Seletor de Tema">
    <label for="theme-select" class="theme-label">Tema:</label>
    <select id="theme-select" class="theme-select" onchange="changeTheme(this.value)">
        {''.join(f'<option value="{theme}" {"selected" if theme == current_theme else ""}>{self.themes[theme].name}</option>' for theme in themes)}
    </select>
    
    <div class="theme-options">
        <label class="theme-option">
            <input type="checkbox" id="auto-switch" {"checked" if self.user_preferences.get("auto_switch", False) else ""} onchange="toggleAutoSwitch(this.checked)">
            <span>Alternância automática</span>
        </label>
        
        <label class="theme-option">
            <input type="checkbox" id="high-contrast" {"checked" if self.user_preferences.get("high_contrast", False) else ""} onchange="toggleHighContrast(this.checked)">
            <span>Alto contraste</span>
        </label>
    </div>
</div>

<script>
function changeTheme(themeName) {{
    fetch('/api/theme', {{
        method: 'POST',
        headers: {{
            'Content-Type': 'application/json',
        }},
        body: JSON.stringify({{ theme: themeName }})
    }})
    .then(response => response.json())
    .then(data => {{
        if (data.success) {{
            location.reload();
        }}
    }})
    .catch(error => {{
        console.error('Erro ao alterar tema:', error);
    }});
}}

function toggleAutoSwitch(enabled) {{
    fetch('/api/theme/preferences', {{
        method: 'POST',
        headers: {{
            'Content-Type': 'application/json',
        }},
        body: JSON.stringify({{ auto_switch: enabled }})
    }});
}}

function toggleHighContrast(enabled) {{
    fetch('/api/theme/preferences', {{
        method: 'POST',
        headers: {{
            'Content-Type': 'application/json',
        }},
        body: JSON.stringify({{ high_contrast: enabled }})
    }});
}}
</script>

<style>
.theme-switcher {{
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 10px;
    background: var(--surface-color);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    margin: 10px 0;
}}

.theme-label {{
    font-weight: 500;
    color: var(--text-color);
}}

.theme-select {{
    padding: 5px 10px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--background-color);
    color: var(--text-color);
    font-size: 14px;
}}

.theme-options {{
    display: flex;
    gap: 15px;
}}

.theme-option {{
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 14px;
    color: var(--text-color);
    cursor: pointer;
}}

.theme-option input[type="checkbox"] {{
    margin: 0;
}}
</style>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar seletor de tema: {e}")
            return ""
    
    def generate_dark_mode_css(self) -> str:
        """Gera CSS específico para modo escuro"""
        try:
            dark_theme = self.themes["dark"]
            
            css = f"""
/* Modo Escuro - MaraBet AI */

[data-theme="dark"] {{
    background-color: {dark_theme.background_color};
    color: {dark_theme.text_color};
}}

[data-theme="dark"] .card {{
    background-color: {dark_theme.surface_color};
    border-color: {dark_theme.border_color};
    box-shadow: 0 4px 6px {dark_theme.shadow_color};
}}

[data-theme="dark"] .btn-primary {{
    background-color: {dark_theme.primary_color};
    border-color: {dark_theme.primary_color};
}}

[data-theme="dark"] .btn-primary:hover {{
    background-color: {dark_theme.secondary_color};
    border-color: {dark_theme.secondary_color};
}}

[data-theme="dark"] .table {{
    color: {dark_theme.text_color};
}}

[data-theme="dark"] .table th {{
    background-color: {dark_theme.surface_color};
    border-color: {dark_theme.border_color};
}}

[data-theme="dark"] .table td {{
    border-color: {dark_theme.border_color};
}}

[data-theme="dark"] .form-control {{
    background-color: {dark_theme.surface_color};
    border-color: {dark_theme.border_color};
    color: {dark_theme.text_color};
}}

[data-theme="dark"] .form-control:focus {{
    background-color: {dark_theme.surface_color};
    border-color: {dark_theme.accent_color};
    color: {dark_theme.text_color};
    box-shadow: 0 0 0 0.2rem {dark_theme.accent_color}33;
}}

[data-theme="dark"] .alert-success {{
    background-color: {dark_theme.success_color}20;
    border-color: {dark_theme.success_color};
    color: {dark_theme.success_color};
}}

[data-theme="dark"] .alert-warning {{
    background-color: {dark_theme.warning_color}20;
    border-color: {dark_theme.warning_color};
    color: {dark_theme.warning_color};
}}

[data-theme="dark"] .alert-danger {{
    background-color: {dark_theme.error_color}20;
    border-color: {dark_theme.error_color};
    color: {dark_theme.error_color};
}}

[data-theme="dark"] .alert-info {{
    background-color: {dark_theme.info_color}20;
    border-color: {dark_theme.info_color};
    color: {dark_theme.info_color};
}}

/* Transições suaves */
* {{
    transition: background-color var(--transition-duration) var(--transition-timing),
                color var(--transition-duration) var(--transition-timing),
                border-color var(--transition-duration) var(--transition-timing);
}}

/* Scrollbar personalizada para modo escuro */
[data-theme="dark"] ::-webkit-scrollbar {{
    width: 8px;
}}

[data-theme="dark"] ::-webkit-scrollbar-track {{
    background: {dark_theme.surface_color};
}}

[data-theme="dark"] ::-webkit-scrollbar-thumb {{
    background: {dark_theme.border_color};
    border-radius: 4px;
}}

[data-theme="dark"] ::-webkit-scrollbar-thumb:hover {{
    background: {dark_theme.text_secondary_color};
}}
            """
            
            return css
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar CSS do modo escuro: {e}")
            return ""
    
    def generate_theme_preview(self) -> str:
        """Gera preview dos temas"""
        try:
            html = """
<div class="theme-preview">
    <h3>Preview dos Temas</h3>
    <div class="theme-preview-grid">
"""
            
            for theme_name, theme in self.themes.items():
                html += f"""
        <div class="theme-preview-card" data-theme="{theme_name}">
            <div class="theme-preview-header">
                <h4>{theme.name}</h4>
                <button class="btn btn-sm btn-primary" onclick="setTheme('{theme_name}')">
                    Usar
                </button>
            </div>
            <div class="theme-preview-content">
                <div class="color-palette">
                    <div class="color-swatch" style="background-color: {theme.primary_color}"></div>
                    <div class="color-swatch" style="background-color: {theme.secondary_color}"></div>
                    <div class="color-swatch" style="background-color: {theme.accent_color}"></div>
                    <div class="color-swatch" style="background-color: {theme.success_color}"></div>
                    <div class="color-swatch" style="background-color: {theme.warning_color}"></div>
                    <div class="color-swatch" style="background-color: {theme.error_color}"></div>
                </div>
                <div class="theme-preview-text">
                    <p>Texto principal</p>
                    <p class="text-secondary">Texto secundário</p>
                </div>
            </div>
        </div>
                """
            
            html += """
    </div>
</div>

<style>
.theme-preview {
    margin: 20px 0;
}

.theme-preview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 15px;
}

.theme-preview-card {
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 15px;
    background: var(--surface-color);
}

.theme-preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.theme-preview-header h4 {
    margin: 0;
    color: var(--text-color);
}

.color-palette {
    display: flex;
    gap: 5px;
    margin-bottom: 15px;
}

.color-swatch {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    border: 1px solid var(--border-color);
}

.theme-preview-text p {
    margin: 5px 0;
    color: var(--text-color);
}

.theme-preview-text .text-secondary {
    color: var(--text-secondary-color);
}
</style>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar preview: {e}")
            return ""
    
    def get_theme_for_time(self) -> str:
        """Retorna tema baseado na hora do dia"""
        try:
            if not self.user_preferences.get("auto_switch", False):
                return self.current_theme
            
            from datetime import datetime
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            preferred_time = self.user_preferences.get("preferred_time", "18:00")
            
            # Se a hora atual é maior que a preferida, usar tema escuro
            if current_time >= preferred_time:
                return "dark"
            else:
                return "light"
                
        except Exception as e:
            logger.error(f"❌ Erro ao determinar tema por hora: {e}")
            return self.current_theme
    
    def create_theme_api_endpoints(self) -> Dict[str, Any]:
        """Cria endpoints da API para temas"""
        return {
            "set_theme": {
                "method": "POST",
                "path": "/api/theme",
                "handler": self._api_set_theme
            },
            "get_theme": {
                "method": "GET",
                "path": "/api/theme",
                "handler": self._api_get_theme
            },
            "get_themes": {
                "method": "GET",
                "path": "/api/themes",
                "handler": self._api_get_themes
            },
            "update_preferences": {
                "method": "POST",
                "path": "/api/theme/preferences",
                "handler": self._api_update_preferences
            }
        }
    
    def _api_set_theme(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """API endpoint para definir tema"""
        try:
            theme = request_data.get("theme")
            if theme and self.set_theme(theme):
                return {"success": True, "theme": theme}
            else:
                return {"success": False, "error": "Tema inválido"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _api_get_theme(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """API endpoint para obter tema atual"""
        try:
            theme = self.get_current_theme()
            return {
                "success": True,
                "theme": self.current_theme,
                "config": {
                    "name": theme.name,
                    "primary_color": theme.primary_color,
                    "background_color": theme.background_color,
                    "text_color": theme.text_color
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _api_get_themes(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """API endpoint para obter todos os temas"""
        try:
            themes = {}
            for name, theme in self.themes.items():
                themes[name] = {
                    "name": theme.name,
                    "primary_color": theme.primary_color,
                    "background_color": theme.background_color,
                    "text_color": theme.text_color
                }
            
            return {"success": True, "themes": themes}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _api_update_preferences(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """API endpoint para atualizar preferências"""
        try:
            self.save_user_preferences(request_data)
            return {"success": True, "preferences": self.user_preferences}
        except Exception as e:
            return {"success": False, "error": str(e)}
