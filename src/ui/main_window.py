"""
Gestor visual y de estilos modernos para la aplicación
"""
import tkinter as tk
from tkinter import ttk
from src.config.settings import (
    BRAND_COLOR_PRIMARY, BRAND_COLOR_SECONDARY, BRAND_COLOR_ACCENT,
    BRAND_COLOR_SUCCESS, BRAND_COLOR_DANGER, BRAND_COLOR_LIGHT,
    BRAND_COLOR_WHITE, BRAND_COLOR_TEXT, BRAND_COLOR_TEXT_LIGHT,
    BACKGROUND_COLOR, CARD_BACKGROUND,
    HEADER_FONT, SUBHEADER_FONT, BUTTON_FONT, LABEL_FONT, TEXT_FONT,
    HEADER_PADDING, HAS_TTKBOOTSTRAP,
    DEFAULT_THEME, COMPANY_NAME, ICONS
)

if HAS_TTKBOOTSTRAP:
    import ttkbootstrap as ttkb


class ModernStyleManager:
    """Gestor de estilos modernos y profesionales"""
    
    def __init__(self, root):
        self.root = root
        self.style = None
        self._setup_modern_theme()
    
    def _setup_modern_theme(self):
        """Configura un tema moderno y profesional"""
        if HAS_TTKBOOTSTRAP:
            self.style = ttkb.Style(DEFAULT_THEME)
            self._customize_ttkbootstrap_theme()
        else:
            self.style = ttk.Style()
            self.style.theme_use('clam')
            self._create_custom_theme()
    
    def _customize_ttkbootstrap_theme(self):
        """Personaliza el tema de ttkbootstrap"""
        # Configurar colores personalizados
        self.style.configure('Header.TFrame', background=BRAND_COLOR_PRIMARY)
        self.style.configure('Header.TLabel', 
                           background=BRAND_COLOR_PRIMARY, 
                           foreground='white',
                           font=HEADER_FONT)
        
        self.style.configure('Subheader.TLabel',
                           foreground=BRAND_COLOR_SECONDARY,
                           font=SUBHEADER_FONT)
        
        # Botones de acción principales
        self.style.configure('Action.TButton',
                           font=BUTTON_FONT,
                           padding=(15, 10))
    
    def _create_custom_theme(self):
        """Crea un tema personalizado para tkinter estándar"""
        self.style.configure('TFrame', background=BACKGROUND_COLOR)
        self.style.configure('TLabel', background=BACKGROUND_COLOR, foreground=BRAND_COLOR_TEXT)
        
        self.style.configure('Header.TFrame', 
                           background=BRAND_COLOR_PRIMARY,
                           relief='flat')
        
        self.style.configure('Header.TLabel',
                           background=BRAND_COLOR_PRIMARY,
                           foreground='white',
                           font=HEADER_FONT)
        
        self.style.configure('Subheader.TLabel',
                           background=BRAND_COLOR_PRIMARY,
                           foreground='white',
                           font=SUBHEADER_FONT)
        
        self.style.configure('Modern.TButton',
                           background=BRAND_COLOR_PRIMARY,
                           foreground='white',
                           font=BUTTON_FONT,
                           borderwidth=1,
                           focuscolor='none',
                           relief='flat',
                           padding=(15, 10))
        
        self.style.map('Modern.TButton',
                      background=[('active', BRAND_COLOR_SECONDARY),
                                ('pressed', BRAND_COLOR_ACCENT)],
                      relief=[('pressed', 'sunken')])
        
        self.style.configure('Success.TButton',
                           background=BRAND_COLOR_SUCCESS,
                           foreground='white',
                           font=BUTTON_FONT,
                           borderwidth=1,
                           relief='flat',
                           padding=(15, 10))
        
        self.style.map('Success.TButton',
                      background=[('active', '#45A049'),
                                ('pressed', '#3D8B40')])
        
        self.style.configure('Danger.TButton',
                           background=BRAND_COLOR_DANGER,
                           foreground='white',
                           font=BUTTON_FONT,
                           borderwidth=1,
                           relief='flat',
                           padding=(12, 8))
        
        self.style.map('Danger.TButton',
                      background=[('active', '#E53935'),
                                ('pressed', '#C62828')])
        
        self.style.configure('Modern.TNotebook',
                           background=BACKGROUND_COLOR,
                           borderwidth=0)
        
        self.style.configure('Modern.TNotebook.Tab',
                           background=BRAND_COLOR_WHITE,
                           foreground=BRAND_COLOR_TEXT,
                           font=LABEL_FONT,
                           padding=(20, 12),
                           borderwidth=1)
        
        self.style.map('Modern.TNotebook.Tab',
                      background=[('selected', BRAND_COLOR_PRIMARY),
                                ('active', BRAND_COLOR_LIGHT)],
                      foreground=[('selected', 'white'),
                                ('active', BRAND_COLOR_PRIMARY)])
        
        self.style.configure('TEntry',
                           fieldbackground=BRAND_COLOR_WHITE,
                           foreground=BRAND_COLOR_TEXT,
                           borderwidth=2,
                           relief='solid',
                           insertcolor=BRAND_COLOR_PRIMARY)
        
        self.style.map('TEntry',
                      bordercolor=[('focus', BRAND_COLOR_PRIMARY),
                                 ('!focus', '#D0D7DE')])
        
        self.style.configure('TCombobox',
                           fieldbackground=BRAND_COLOR_WHITE,
                           foreground=BRAND_COLOR_TEXT,
                           borderwidth=2,
                           arrowcolor=BRAND_COLOR_PRIMARY)
        
        # Estilos mejorados para Treeview con bordes muy visibles
        self.style.configure('Treeview',
                           background='#FFFFFF',  # Fondo blanco puro
                           foreground='#000000',  # Texto negro puro para máximo contraste
                           fieldbackground='#FFFFFF',
                           font=('Segoe UI', 10),
                           rowheight=32,  # Filas más altas
                           borderwidth=0)  # Sin borde en el treeview, lo pondremos en el frame
        
        self.style.configure('Treeview.Heading',
                           background=BRAND_COLOR_PRIMARY,
                           foreground='white',
                           font=('Segoe UI', 10, 'bold'),
                           borderwidth=1,
                           relief='solid')
        
        self.style.map('Treeview.Heading',
                      background=[('active', BRAND_COLOR_SECONDARY),
                                ('pressed', BRAND_COLOR_ACCENT)])
        
        # Alternar colores de filas para mejor legibilidad
        self.style.map('Treeview',
                      background=[('selected', BRAND_COLOR_PRIMARY),
                                ('active', BRAND_COLOR_LIGHT)],
                      foreground=[('selected', 'white'),
                                ('active', '#000000')])


def create_modern_header(parent, title="Sistema de Presupuestos", subtitle="Barajas Peña SL"):
    """
    Crea un header moderno con título
    
    Args:
        parent: Widget padre
        title: Título principal
        subtitle: Subtítulo (nombre de la empresa)
    """
    # Frame principal con fondo de marca
    header_frame = ttk.Frame(parent, style='Header.TFrame')
    header_frame.pack(fill='x', padx=0, pady=0)
    
    # Contenedor interno con padding
    content_frame = ttk.Frame(header_frame, style='Header.TFrame')
    content_frame.pack(fill='x', padx=HEADER_PADDING[0], pady=HEADER_PADDING[1])
    
    # Frame izquierdo para texto
    left_frame = ttk.Frame(content_frame, style='Header.TFrame')
    left_frame.pack(side='left', fill='y')
    
    # Frame para títulos
    title_frame = ttk.Frame(left_frame, style='Header.TFrame')
    title_frame.pack(side='left', fill='y')
    
    # Título principal
    title_label = ttk.Label(title_frame, text=title, style='Header.TLabel')
    title_label.pack(anchor='w')
    
    # Subtítulo
    if subtitle:
        subtitle_label = ttk.Label(title_frame, text=subtitle, style='Subheader.TLabel')
        subtitle_label.pack(anchor='w', pady=(5, 0))
    
    # Frame derecho para información adicional
    right_frame = ttk.Frame(content_frame, style='Header.TFrame')
    right_frame.pack(side='right', fill='y')
    
    # Se puede añadir información adicional aquí en el futuro si se necesita
    # Por ahora lo dejamos vacío para un diseño más limpio
    
    # Línea separadora elegante
    separator_frame = ttk.Frame(parent)
    separator_frame.pack(fill='x')
    
    separator_canvas = tk.Canvas(separator_frame, height=3, 
                               background=BRAND_COLOR_ACCENT,
                               highlightthickness=0)
    separator_canvas.pack(fill='x')
    
    return header_frame


def create_action_card(parent, title, icon, description, command, style='primary'):
    """
    Crea una tarjeta de acción moderna estilo card
    
    Args:
        parent: Widget padre
        title: Título de la acción
        icon: Icono (emoji)
        description: Descripción
        command: Función a ejecutar
        style: Estilo del botón
    
    Returns:
        Frame de la tarjeta
    """
    def on_enter(e):
        card_canvas.configure(highlightbackground=BRAND_COLOR_PRIMARY, highlightthickness=3)
        card_canvas.itemconfig(rect_id, fill=BRAND_COLOR_LIGHT)
    
    def on_leave(e):
        card_canvas.configure(highlightbackground='#D0D7DE', highlightthickness=2)
        card_canvas.itemconfig(rect_id, fill=CARD_BACKGROUND)
    
    card_frame = ttk.Frame(parent)
    card_frame.pack(side='left', padx=8, pady=3)
    
    card_canvas = tk.Canvas(card_frame, width=170, height=100,
                          background=CARD_BACKGROUND, highlightthickness=2,
                          highlightbackground='#D0D7DE')
    card_canvas.pack()
    
    rect_id = card_canvas.create_rectangle(2, 2, 168, 98, fill=CARD_BACKGROUND, outline='#E3F2FD', width=2)
    
    card_canvas.create_text(85, 25, text=icon, font=('Segoe UI', 20))
    
    card_canvas.create_text(85, 50, text=title, 
                          font=('Segoe UI', 11, 'bold'),
                          fill=BRAND_COLOR_TEXT)
    
    card_canvas.create_text(85, 70, text=description,
                          font=('Segoe UI', 8),
                          fill=BRAND_COLOR_TEXT_LIGHT)
    
    card_canvas.bind('<Button-1>', lambda e: command())
    card_canvas.bind('<Enter>', on_enter)
    card_canvas.bind('<Leave>', on_leave)
    
    card_canvas.configure(cursor='hand2')
    
    return card_frame


def create_professional_button(parent, text, command, style='primary', size='normal'):
    """
    Crea un botón con estilo profesional moderno
    
    Args:
        parent: Widget padre
        text: Texto del botón
        command: Función a ejecutar
        style: Estilo ('primary', 'success', 'danger', 'secondary')
        size: Tamaño ('small', 'normal', 'large')
    
    Returns:
        Button widget
    """
    # Configurar estilo según parámetros
    if HAS_TTKBOOTSTRAP:
        style_map = {
            'primary': 'primary',
            'success': 'success',
            'danger': 'danger',
            'secondary': 'secondary'
        }
        button = ttkb.Button(parent, text=text, command=command,
                           bootstyle=style_map.get(style, 'primary'))
    else:
        style_map = {
            'primary': 'Modern.TButton',
            'success': 'Success.TButton', 
            'danger': 'Danger.TButton',
            'secondary': 'Modern.TButton'
        }
        button = ttk.Button(parent, text=text, command=command,
                          style=style_map.get(style, 'Modern.TButton'))
    
    return button


def create_modern_statusbar(parent, initial_text="Listo"):
    """
    Crea una barra de estado moderna
    
    Args:
        parent: Widget padre
        initial_text: Texto inicial
        
    Returns:
        Tuple (frame, label)
    """
    # Frame con fondo de marca
    status_frame = ttk.Frame(parent)
    status_frame.pack(fill='x', side='bottom')
    
    # Canvas para crear línea superior con gradiente
    top_line = tk.Canvas(status_frame, height=2, highlightthickness=0)
    top_line.pack(fill='x')
    top_line.configure(background=BRAND_COLOR_ACCENT)
    
    # Frame interno
    content_frame = ttk.Frame(status_frame)
    content_frame.pack(fill='x', padx=20, pady=8)
    
    # Label de estado
    status_label = ttk.Label(content_frame, text=initial_text, 
                           font=TEXT_FONT, foreground='#6C757D')
    status_label.pack(side='left')
    
    # Información adicional a la derecha
    info_label = ttk.Label(content_frame, 
                         text=f"Powered by Smarthive",
                         font=('Segoe UI', 8), foreground='#ADB5BD')
    info_label.pack(side='right')
    
    return status_frame, status_label