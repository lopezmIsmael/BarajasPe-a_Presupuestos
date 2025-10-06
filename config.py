"""
Configuración global de la aplicación
"""
from pathlib import Path

COMPANY_NAME = "Barajas Peña SL"
BRAND_COLOR_PRIMARY = "#2B7DE9"
BRAND_COLOR_SECONDARY = "#5BA3F5"
BRAND_COLOR_ACCENT = "#1E5CBE"
BRAND_COLOR_SUCCESS = "#4CAF50"
BRAND_COLOR_WARNING = "#FFC107"
BRAND_COLOR_DANGER = "#F44336"
BRAND_COLOR_LIGHT = "#E3F2FD"
BRAND_COLOR_WHITE = "#FFFFFF"
BRAND_COLOR_TEXT = "#263238"
BRAND_COLOR_TEXT_LIGHT = "#546E7A"

HEADER_GRADIENT = f"linear-gradient(135deg, {BRAND_COLOR_PRIMARY} 0%, {BRAND_COLOR_SECONDARY} 100%)"
SIDEBAR_COLOR = "#FAFBFC"
CARD_SHADOW = "0 2px 8px rgba(43, 125, 233, 0.15)"
CARD_BACKGROUND = "#FFFFFF"
BACKGROUND_COLOR = "#F5F8FA"

APP_DIR = Path(__file__).parent
ASSETS_DIR = APP_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"

MAIN_WINDOW_SIZE = '1200x800'
MAIN_WINDOW_TITLE = f"{COMPANY_NAME} - Gestión de Presupuestos"

MATERIAL_EDITOR_SIZE = '700x600'
CLIENT_EDITOR_SIZE = '650x500'
QUOTE_EDITOR_SIZE = '1200x750'
QUOTE_VIEWER_SIZE = '950x650'

BUTTON_STYLE = {'padding': (12, 8), 'width': 18}
SMALL_BUTTON_STYLE = {'padding': (8, 6), 'width': 12}
ACTION_BUTTON_STYLE = {'padding': (15, 10), 'width': 20}

HEADER_FONT = ('Segoe UI', 28, 'bold')
SUBHEADER_FONT = ('Segoe UI', 14, 'normal')
BUTTON_FONT = ('Segoe UI', 10, 'bold')
LABEL_FONT = ('Segoe UI', 10, 'bold')
TEXT_FONT = ('Segoe UI', 10, 'normal')

HEADER_PADDING = (25, 20)
SECTION_PADDING = (20, 15)
WIDGET_PADDING = (10, 5)

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