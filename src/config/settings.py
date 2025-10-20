"""
Configuración global de la aplicación
"""
from pathlib import Path

COMPANY_NAME = "Barajas Peña SL"
# Paleta de colores moderna y minimalista
BRAND_COLOR_PRIMARY = "#1E88E5"  # Azul más suave
BRAND_COLOR_SECONDARY = "#64B5F6"  # Azul claro
BRAND_COLOR_ACCENT = "#0D47A1"  # Azul oscuro
BRAND_COLOR_SUCCESS = "#43A047"  # Verde más natural
BRAND_COLOR_WARNING = "#FFA726"  # Naranja suave
BRAND_COLOR_DANGER = "#E53935"  # Rojo más suave
BRAND_COLOR_LIGHT = "#E3F2FD"  # Azul muy claro
BRAND_COLOR_WHITE = "#FFFFFF"
BRAND_COLOR_TEXT = "#212121"  # Negro más suave
BRAND_COLOR_TEXT_LIGHT = "#757575"  # Gris medio

HEADER_GRADIENT = f"linear-gradient(135deg, {BRAND_COLOR_PRIMARY} 0%, {BRAND_COLOR_SECONDARY} 100%)"
SIDEBAR_COLOR = "#FAFAFA"  # Gris muy claro
CARD_SHADOW = "0 1px 3px rgba(0, 0, 0, 0.12)"  # Sombra más sutil
CARD_BACKGROUND = "#FFFFFF"
BACKGROUND_COLOR = "#FAFAFA"  # Fondo más limpio

# Rutas ajustadas para la nueva estructura
APP_DIR = Path(__file__).parent.parent.parent  # Subir a raíz del proyecto
ASSETS_DIR = APP_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"

MAIN_WINDOW_SIZE = '1200x800'
MAIN_WINDOW_TITLE = f"{COMPANY_NAME} - Gestión de Presupuestos"

MATERIAL_EDITOR_SIZE = '700x600'
CLIENT_EDITOR_SIZE = '650x500'
QUOTE_EDITOR_SIZE = '1600x850'
QUOTE_VIEWER_SIZE = '950x650'

BUTTON_STYLE = {'padding': (12, 8), 'width': 18}
SMALL_BUTTON_STYLE = {'padding': (8, 6), 'width': 12}
ACTION_BUTTON_STYLE = {'padding': (15, 10), 'width': 20}

HEADER_FONT = ('Segoe UI', 22, 'bold')
SUBHEADER_FONT = ('Segoe UI', 12, 'normal')
BUTTON_FONT = ('Segoe UI', 10, 'bold')
LABEL_FONT = ('Segoe UI', 10, 'bold')
TEXT_FONT = ('Segoe UI', 10, 'normal')

HEADER_PADDING = (20, 12)
SECTION_PADDING = (15, 10)
WIDGET_PADDING = (8, 4)

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    HAS_TTKBOOTSTRAP = True
    DEFAULT_THEME = 'cosmo'
except ImportError:
    HAS_TTKBOOTSTRAP = False
    DEFAULT_THEME = 'clam'

IMAGE_FILETYPES = [('Imágenes','*.png *.jpg *.jpeg *.bmp *.gif')]
PDF_FILETYPES = [('PDF','*.pdf')]

ICONS = {
    'quote': '📋',
    'material': '🧱', 
    'client': '👥',
    'add': '➕',
    'edit': '✏️',
    'delete': '🗑️',
    'pdf': '📄',
    'view': '👁️',
    'save': '💾',
    'cancel': '❌',
    'search': '🔍',
    'folder': '📁',
    'company': '🏗️',
    'phone': '📞',
    'email': '📧',
    'location': '📍'
}