"""
Utilidades para la interfaz de usuario
"""
import tkinter as tk
from tkinter import ttk
from src.config.settings import HAS_TTKBOOTSTRAP, SMALL_BUTTON_STYLE

if HAS_TTKBOOTSTRAP:
    import ttkbootstrap as ttkb


def center_window(window, width, height):
    """Centra una ventana sobre su ventana padre sin salirse del monitor"""
    # Forzar actualización de la ventana
    window.withdraw()  # Ocultar temporalmente
    window.update_idletasks()
    
    # Obtener dimensiones de pantalla
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Intentar obtener las dimensiones de la ventana padre (master)
    try:
        master = window.master
        if master and master.winfo_ismapped():
            master.update_idletasks()
            parent_x = master.winfo_x()
            parent_y = master.winfo_y()
            parent_width = master.winfo_width()
            parent_height = master.winfo_height()
            
            # Calcular el centro de la ventana padre
            center_x = parent_x + parent_width // 2
            center_y = parent_y + parent_height // 2
            
            # Calcular posición para centrar la ventana modal
            x = center_x - width // 2
            y = center_y - height // 2
            
            # Limitar al rango visible (asumiendo monitor principal)
            # Si la ventana padre está en un monitor específico, mantener ahí
            monitor_left = max(0, parent_x - 100)  # Un poco de margen
            monitor_right = min(screen_width, parent_x + parent_width + 100)
            monitor_top = max(0, parent_y - 50)
            monitor_bottom = min(screen_height, parent_y + parent_height + 50)
            
            # Ajustar para que no se salga del área del monitor
            if x < monitor_left:
                x = monitor_left + 20
            if x + width > monitor_right:
                x = monitor_right - width - 20
            if y < monitor_top:
                y = monitor_top + 20
            if y + height > monitor_bottom:
                y = monitor_bottom - height - 20
            
            # Si aún así es muy grande, reducir tamaño
            available_width = monitor_right - monitor_left - 40
            available_height = monitor_bottom - monitor_top - 40
            
            if width > available_width:
                width = available_width
                x = monitor_left + 20
            if height > available_height:
                height = available_height
                y = monitor_top + 20
                
        else:
            raise AttributeError("No hay ventana padre visible")
    except:
        # Fallback: centrar en la pantalla
        max_width = int(screen_width * 0.95)
        max_height = int(screen_height * 0.9)
        
        actual_width = min(width, max_width)
        actual_height = min(height, max_height)
        
        x = (screen_width - actual_width) // 2
        y = (screen_height - actual_height) // 2
        
        width = actual_width
        height = actual_height
    
    # Asegurar valores mínimos
    x = max(0, x)
    y = max(0, y)
    
    # Establecer geometría y mostrar ventana
    window.geometry(f'{width}x{height}+{x}+{y}')
    window.deiconify()  # Mostrar ventana centrada


def create_styled_button(parent, text, command, style_type="default", **kwargs):
    """Crea un botón con estilo dependiendo de si ttkbootstrap está disponible"""
    button_kwargs = kwargs.copy()
    
    if HAS_TTKBOOTSTRAP:
        incompatible_params = ['padding', 'font', 'width', 'height']
        for param in incompatible_params:
            button_kwargs.pop(param, None)
            
        if style_type == "success":
            button_kwargs['bootstyle'] = "success"
        elif style_type == "primary":
            button_kwargs['bootstyle'] = "primary" 
        elif style_type == "info":
            button_kwargs['bootstyle'] = "info"
        elif style_type == "danger":
            button_kwargs['bootstyle'] = "danger"
        elif style_type == "secondary":
            button_kwargs['bootstyle'] = "secondary"
    
    return ttk.Button(parent, text=text, command=command, **button_kwargs)


def setup_theme(root):
    """Configura el tema de la aplicación"""
    if HAS_TTKBOOTSTRAP:
        style = ttkb.Style('flatly')
        return style
    else:
        style = ttk.Style()
        style.theme_use('clam')
        return style


def create_search_frame(parent, search_var, placeholder_text="🔍 Buscar:"):
    """Crea un frame de búsqueda estándar"""
    search_frame = ttk.Frame(parent)
    search_frame.pack(fill='x', padx=10, pady=10)
    
    ttk.Label(search_frame, text=placeholder_text).pack(side='left', padx=5)
    
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side='left', padx=5)
    
    return search_frame, search_entry


def create_treeview_with_scrollbar(parent, columns, headings, column_widths=None):
    """Crea un treeview con scrollbar, borde visible y estilos mejorados"""
    # Frame exterior con padding
    outer_frame = ttk.Frame(parent)
    outer_frame.pack(fill='both', expand=True, padx=10, pady=5)
    
    # Frame interior con borde visible usando Canvas
    border_canvas = tk.Canvas(outer_frame, highlightthickness=3, 
                             highlightbackground='#2B7DE9',  # Borde azul visible
                             highlightcolor='#2B7DE9',
                             background='#FFFFFF')
    border_canvas.pack(fill='both', expand=True)
    
    # Frame contenedor para el treeview dentro del canvas
    tree_frame = ttk.Frame(border_canvas)
    tree_frame.pack(fill='both', expand=True, padx=2, pady=2)
    
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
    
    for i, (col, heading) in enumerate(zip(columns, headings)):
        tree.heading(col, text=heading, anchor='w')
        if column_widths and i < len(column_widths):
            tree.column(col, width=column_widths[i], anchor='w')
        else:
            tree.column(col, anchor='w')
    
    # Configurar tags para filas alternadas con bordes visibles
    tree.tag_configure('oddrow', background='#FFFFFF')
    tree.tag_configure('evenrow', background='#F0F4F8')  # Gris más visible
    
    scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')
    
    return outer_frame, tree


def create_button_frame(parent, buttons_config):
    """
    Crea un frame con botones basado en configuración
    buttons_config: lista de tuplas (texto, comando, estilo)
    """
    btns_frame = ttk.Frame(parent)
    btns_frame.pack(fill='x', padx=10, pady=10)
    
    buttons = []
    for config in buttons_config:
        if len(config) == 3:
            text, command, style_type = config
            btn = create_styled_button(btns_frame, text, command, style_type, **SMALL_BUTTON_STYLE)
        else:
            text, command = config
            btn = create_styled_button(btns_frame, text, command, **SMALL_BUTTON_STYLE)
        
        btn.pack(side='left', padx=5)
        buttons.append(btn)
    
    return btns_frame, buttons


def create_form_field(parent, label_text, entry_type='entry', row=0, **kwargs):
    """Crea un campo de formulario estándar"""
    ttk.Label(parent, text=label_text, font=('Helvetica', 10, 'bold')).grid(
        row=row, column=0, sticky='w', pady=5
    )
    
    if entry_type == 'entry':
        widget = ttk.Entry(parent, **kwargs)
    elif entry_type == 'text':
        widget = tk.Text(parent, **kwargs)
    elif entry_type == 'combobox':
        widget = ttk.Combobox(parent, **kwargs)
    else:
        raise ValueError(f"Tipo de entrada no soportado: {entry_type}")
    
    widget.grid(row=row, column=1, pady=5, sticky='ew')
    return widget


def bind_keyboard_shortcuts(window, shortcuts_dict):
    """
    Asocia atajos de teclado a una ventana
    shortcuts_dict: dict con formato {'<shortcut>': callback}
    """
    for shortcut, callback in shortcuts_dict.items():
        window.bind(shortcut, lambda e, cb=callback: cb())


def create_status_bar(parent, initial_text="Listo"):
    """Crea una barra de estado"""
    status_frame = ttk.Frame(parent)
    status_frame.pack(fill='x', side='bottom')
    
    status_label = ttk.Label(status_frame, text=initial_text, font=('Helvetica', 9))
    status_label.pack(side='left', padx=20, pady=5)
    
    return status_frame, status_label