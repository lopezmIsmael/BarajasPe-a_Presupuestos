"""
Estilos modernos y elegantes para toda la aplicación.
Paleta de colores corporativa y diseño profesional.
"""

# Paleta de colores moderna - Inspirada en diseño de constructoras profesionales
COLORS = {
    # Colores principales (tonos azules profesionales)
    'primary': '#1e3a5f',       # Azul oscuro profesional
    'primary_light': '#2c5282',  # Azul medio
    'primary_dark': '#152a46',   # Azul muy oscuro

    # Colores de acento (azul brillante moderno)
    'accent': '#3b82f6',        # Azul brillante
    'accent_light': '#60a5fa',  # Azul claro
    'accent_dark': '#2563eb',   # Azul oscuro

    # Colores secundarios
    'success': '#10b981',       # Verde éxito moderno
    'warning': '#f59e0b',       # Naranja advertencia
    'danger': '#ef4444',        # Rojo peligro moderno
    'info': '#3b82f6',          # Azul información

    # Grises (tonos suaves)
    'background': '#f8fafc',    # Fondo principal muy claro
    'card': '#ffffff',          # Tarjetas/widgets
    'border': '#cbd5e1',        # Bordes suaves
    'border_light': '#e2e8f0',  # Bordes muy claros
    'text': '#1e293b',          # Texto principal
    'text_light': '#64748b',    # Texto secundario
    'hover': '#f1f5f9',         # Hover ligero

    # Estados
    'selected': '#3b82f6',
    'disabled': '#94a3b8',
}

# Estilos globales de la aplicación
APP_STYLE = f"""
/* ===== ESTILOS GLOBALES ===== */
QMainWindow {{
    background-color: {COLORS['background']};
}}

/* ===== WIDGETS PRINCIPALES ===== */
QWidget {{
    color: {COLORS['text']};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}}

/* ===== PESTAÑAS (TABS) - Modernas y elegantes ===== */
QTabWidget::pane {{
    border: none;
    background: {COLORS['card']};
    border-radius: 8px;
    padding: 12px;
}}

QTabBar::tab {{
    background: transparent;
    border: none;
    padding: 12px 28px;
    margin-right: 4px;
    border-radius: 8px 8px 0 0;
    color: {COLORS['text_light']};
    font-weight: 500;
    font-size: 11pt;
    min-width: 100px;
}}

QTabBar::tab:selected {{
    background: {COLORS['card']};
    color: {COLORS['accent']};
    font-weight: 600;
    border-bottom: 3px solid {COLORS['accent']};
}}

QTabBar::tab:hover:!selected {{
    background: {COLORS['hover']};
    color: {COLORS['text']};
}}

/* ===== BOTONES - Modernos con efectos ===== */
QPushButton {{
    background-color: {COLORS['accent']};
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 6px;
    font-weight: 500;
    font-size: 10pt;
    min-width: 100px;
}}

QPushButton:hover {{
    background-color: {COLORS['accent_dark']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary']};
    padding: 11px 23px 9px 25px;
}}

QPushButton:disabled {{
    background-color: {COLORS['disabled']};
    color: {COLORS['border_light']};
}}

/* Botones secundarios */
QPushButton[class="secondary"] {{
    background-color: {COLORS['card']};
    color: {COLORS['text']};
    border: 2px solid {COLORS['border']};
}}

QPushButton[class="secondary"]:hover {{
    background-color: {COLORS['hover']};
    border-color: {COLORS['accent']};
    color: {COLORS['accent']};
}}

/* Botones de peligro */
QPushButton[class="danger"] {{
    background-color: {COLORS['danger']};
}}

QPushButton[class="danger"]:hover {{
    background-color: #dc2626;
}}

/* Botones de éxito */
QPushButton[class="success"] {{
    background-color: {COLORS['success']};
}}

QPushButton[class="success"]:hover {{
    background-color: #059669;
}}

/* ===== TABLAS - Modernas con hover suave ===== */
QTableWidget {{
    background-color: {COLORS['card']};
    alternate-background-color: {COLORS['background']};
    border: 1px solid {COLORS['border_light']};
    border-radius: 8px;
    gridline-color: {COLORS['border_light']};
}}

QTableWidget::item {{
    padding: 10px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {COLORS['accent']};
    color: white;
}}

QTableWidget::item:hover {{
    background-color: {COLORS['hover']};
}}

QHeaderView::section {{
    background-color: {COLORS['primary']};
    color: white;
    padding: 12px;
    border: none;
    font-weight: 600;
    font-size: 10pt;
}}

QHeaderView::section:horizontal {{
    border-right: 1px solid {COLORS['primary_light']};
}}

QHeaderView::section:horizontal:last {{
    border-right: none;
}}

/* ===== INPUTS - Modernos con efectos de foco ===== */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: white;
    border: 2px solid {COLORS['border_light']};
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 10pt;
    selection-background-color: {COLORS['accent']};
}}

QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
    border-color: {COLORS['border']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS['accent']};
    background-color: {COLORS['card']};
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    background-color: {COLORS['background']};
    color: {COLORS['disabled']};
    border-color: {COLORS['border_light']};
}}

/* ===== COMBOBOX - Moderno con flecha elegante ===== */
QComboBox {{
    background-color: white;
    border: 2px solid {COLORS['border_light']};
    border-radius: 6px;
    padding: 10px 14px;
    min-height: 24px;
    font-size: 10pt;
}}

QComboBox:hover {{
    border-color: {COLORS['border']};
}}

QComboBox:focus {{
    border-color: {COLORS['accent']};
}}

QComboBox::drop-down {{
    border: none;
    width: 35px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 7px solid {COLORS['text_light']};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: white;
    border: 2px solid {COLORS['border']};
    border-radius: 6px;
    selection-background-color: {COLORS['accent']};
    selection-color: white;
    padding: 6px;
    outline: none;
}}

QComboBox QAbstractItemView::item {{
    padding: 8px 12px;
    border-radius: 4px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: {COLORS['hover']};
}}

/* ===== SPINBOX ===== */
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['card']};
    border: 2px solid {COLORS['border']};
    border-radius: 4px;
    padding: 8px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS['accent']};
}}

/* ===== GROUPBOX - Moderno con título destacado ===== */
QGroupBox {{
    background-color: {COLORS['card']};
    border: 2px solid {COLORS['border_light']};
    border-radius: 8px;
    margin-top: 18px;
    padding: 20px 16px 16px 16px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 6px 14px;
    background-color: {COLORS['accent']};
    color: white;
    border-radius: 5px;
    margin-left: 12px;
    font-size: 10pt;
    font-weight: 600;
}}

/* ===== SCROLLBAR - Minimalista y moderno ===== */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['text_light']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS['border']};
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {COLORS['text_light']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ===== TOOLBAR ===== */
QToolBar {{
    background: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    spacing: 5px;
    padding: 5px;
}}

QToolButton {{
    background-color: transparent;
    border: none;
    padding: 6px;
    border-radius: 4px;
}}

QToolButton:hover {{
    background-color: {COLORS['hover']};
}}

QToolButton:pressed {{
    background-color: {COLORS['accent_light']};
}}

/* ===== STATUSBAR - Moderna y elegante ===== */
QStatusBar {{
    background-color: {COLORS['primary']};
    color: white;
    font-size: 9pt;
    padding: 6px 12px;
    border: none;
}}

/* ===== LABELS ===== */
QLabel {{
    color: {COLORS['text']};
}}

QLabel[class="title"] {{
    font-size: 18px;
    font-weight: bold;
    color: {COLORS['primary']};
}}

QLabel[class="subtitle"] {{
    font-size: 14px;
    font-weight: 600;
    color: {COLORS['text_light']};
}}

/* ===== DIALOGOS ===== */
QDialog {{
    background-color: {COLORS['background']};
}}

QDialogButtonBox QPushButton {{
    min-width: 80px;
}}

/* ===== MENU - Moderno con acento profesional ===== */
QMenuBar {{
    background-color: {COLORS['primary']};
    color: white;
    padding: 6px;
    spacing: 6px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 10pt;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['primary_light']};
}}

QMenu {{
    background-color: white;
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 6px;
}}

QMenu::item {{
    padding: 10px 35px 10px 20px;
    border-radius: 5px;
    font-size: 10pt;
}}

QMenu::item:selected {{
    background-color: {COLORS['accent']};
    color: white;
}}

QMenu::separator {{
    height: 1px;
    background: {COLORS['border_light']};
    margin: 8px 12px;
}}

/* ===== SPLITTER ===== */
QSplitter::handle {{
    background-color: {COLORS['border']};
}}

QSplitter::handle:hover {{
    background-color: {COLORS['accent']};
}}

/* ===== CHECKBOX - Moderno y elegante ===== */
QCheckBox {{
    spacing: 10px;
    font-size: 10pt;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {COLORS['border']};
    border-radius: 4px;
    background: white;
}}

QCheckBox::indicator:hover {{
    border: 2px solid {COLORS['accent']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent']};
    border: 2px solid {COLORS['accent']};
    image: none;
}}

QCheckBox::indicator:checked:hover {{
    background-color: {COLORS['accent_dark']};
}}

/* ===== RADIOBUTTON - Moderno y elegante ===== */
QRadioButton {{
    spacing: 10px;
    font-size: 10pt;
}}

QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {COLORS['border']};
    border-radius: 10px;
    background: white;
}}

QRadioButton::indicator:hover {{
    border: 2px solid {COLORS['accent']};
}}

QRadioButton::indicator:checked {{
    background-color: white;
    border: 2px solid {COLORS['accent']};
}}

/* ===== TOOLTIPS - Modernos ===== */
QToolTip {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 9pt;
}}

/* ===== PROGRESSBAR - Moderno ===== */
QProgressBar {{
    border: 2px solid {COLORS['border_light']};
    border-radius: 6px;
    background-color: {COLORS['background']};
    text-align: center;
    font-size: 9pt;
    color: {COLORS['text']};
    height: 20px;
}}

QProgressBar::chunk {{
    background-color: {COLORS['accent']};
    border-radius: 4px;
}}
"""

def apply_stylesheet(app):
    """Aplica la hoja de estilos global a la aplicación"""
    app.setStyleSheet(APP_STYLE)
