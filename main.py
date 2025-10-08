import tkinter as tk
from tkinter import ttk
from src.database import db
from src.config.settings import (
    COMPANY_NAME, MAIN_WINDOW_SIZE, MAIN_WINDOW_TITLE, 
    HAS_TTKBOOTSTRAP, ICONS
)
from src.ui.main_window import (
    ModernStyleManager, create_modern_header, create_action_card,
    create_modern_statusbar
)
from src.ui.ui_utils import bind_keyboard_shortcuts
from src.ui.materials_manager import MaterialsFrame, MaterialEditor
from src.ui.clients_manager import ClientsFrame, ClientEditor
from src.ui.quotes_manager import QuotesFrame
from src.ui.workers_manager import WorkersFrame
from src.ui.work_reports_manager import WorkReportsFrame

if HAS_TTKBOOTSTRAP:
    import ttkbootstrap as ttkb


def ensure_db():
    """Inicializa la base de datos"""
    db.init_db()


class ModernApp:
    """Aplicación principal - Ventana principal y coordinación de módulos"""
    
    def __init__(self, root):
        self.root = root
        self._setup_window()
        self._setup_ui()
        self._setup_keyboard_shortcuts()
        self.refresh_all()
    
    def _setup_window(self):
        """Configura la ventana principal con estilo moderno - Compatible con Linux y Windows"""
        self.root.title(MAIN_WINDOW_TITLE)
        
        # Forzar actualización inicial de la ventana
        self.root.update_idletasks()
        
        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Configurar ventana para que ocupe toda la pantalla
        # Intentar maximizar la ventana según la plataforma
        maximized = False
        try:
            # Linux con X11: usar atributo -zoomed
            self.root.attributes('-zoomed', True)
            maximized = True
        except:
            pass
        
        if not maximized:
            try:
                # Windows: usar state zoomed
                self.root.state('zoomed')
                maximized = True
            except:
                pass
        
        if not maximized:
            # Fallback: usar geometría de pantalla completa
            self.root.geometry(f'{screen_width}x{screen_height}+0+0')
        
        # Forzar actualización para aplicar cambios
        self.root.update_idletasks()
        
        # Variable para controlar estado fullscreen
        self.is_fullscreen = False
        
        # Atajos de teclado para pantalla completa
        self.root.bind('<F11>', lambda e: self._toggle_fullscreen())  # Alternar fullscreen
        self.root.bind('<Escape>', lambda e: self._exit_fullscreen())  # Salir de fullscreen
        
        try:
            self.root.iconname(COMPANY_NAME)
        except:
            pass
        
        self.style_manager = ModernStyleManager(self.root)
        self.root.configure(bg='#F5F8FA')
    
    def _toggle_fullscreen(self):
        """Alterna entre pantalla completa y ventana normal (F11)"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
    
    def _exit_fullscreen(self):
        """Sale del modo pantalla completa (ESC)"""
        self.is_fullscreen = False
        self.root.attributes('-fullscreen', False)
    
    def _setup_ui(self):
        """Configura la interfaz de usuario moderna"""
        self._create_modern_header()
        self._create_modern_actions()
        self._create_main_notebook()
        self._create_modern_status_bar()
    
    def _create_modern_header(self):
        """Crea el header moderno"""
        self.header_frame = create_modern_header(
            self.root, 
            COMPANY_NAME, 
            None  # Sin subtítulo
        )
        # El header ya se posiciona con pack internamente
    
    def _create_modern_actions(self):
        """Crea las acciones rápidas como cards modernas"""
        actions_container = ttk.Frame(self.root)
        actions_container.pack(fill='x', padx=20, pady=(10, 5))
        
        section_title = ttk.Label(
            actions_container, 
            text="Acciones Rápidas", 
            font=('Segoe UI', 12, 'bold'),
            foreground='#263238'
        )
        section_title.pack(anchor='w', pady=(0, 5))
        
        cards_frame = ttk.Frame(actions_container)
        cards_frame.pack(fill='x')
        create_action_card(
            cards_frame, 
            "Nuevo Presupuesto", 
            ICONS['quote'], 
            "Crear cotización",
            self.quick_new_quote, 
            'success'
        )
        
        create_action_card(
            cards_frame, 
            "Nuevo Parte de Obra", 
            "📋", 
            "Crear parte",
            self.quick_new_work_report, 
            'info'
        )
        
        create_action_card(
            cards_frame, 
            "Nuevo Material", 
            ICONS['material'], 
            "Añadir producto",
            self.quick_new_material, 
            'primary'
        )
        
        create_action_card(
            cards_frame, 
            "Nuevo Cliente", 
            ICONS['client'], 
            "Registrar contacto",
            self.quick_new_client, 
            'info'
        )
    
    def _create_main_notebook(self):
        """Crea el notebook principal con las pestañas modernas"""
        notebook_container = ttk.Frame(self.root)
        notebook_container.pack(fill='both', expand=True, padx=20, pady=(5, 5))
        
        self.notebook = ttk.Notebook(notebook_container, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        self.quotes_frame = QuotesFrame(self.notebook, self)
        self.notebook.add(self.quotes_frame, text=f'{ICONS["quote"]} Presupuestos')
        
        self.work_reports_frame = WorkReportsFrame(self.notebook, self)
        self.notebook.add(self.work_reports_frame, text='📋 Partes de Obra')
        
        self.materials_frame = MaterialsFrame(self.notebook, self)
        self.notebook.add(self.materials_frame, text=f'{ICONS["material"]} Materiales')
        
        self.clients_frame = ClientsFrame(self.notebook, self)
        self.notebook.add(self.clients_frame, text=f'{ICONS["client"]} Clientes')
        
        self.workers_frame = WorkersFrame(self.notebook, self)
        self.notebook.add(self.workers_frame, text='👷 Trabajadores')
    
    def _create_modern_status_bar(self):
        """Crea la barra de estado moderna"""
        self.status_frame, self.status_label = create_modern_statusbar(
            self.root, 
            f"{ICONS['company']} Sistema listo"
        )
        # El status bar ya se posiciona con pack internamente (side='bottom')
    
    def _setup_keyboard_shortcuts(self):
        """Configura los atajos de teclado globales"""
        shortcuts = {
            '<Control-n>': self.quick_new_quote,
            '<Control-m>': self.quick_new_material,
            '<Control-u>': self.quick_new_client,
            '<F5>': self.refresh_all
        }
        bind_keyboard_shortcuts(self.root, shortcuts)
    
    def quick_new_quote(self):
        """Abre el editor para crear un nuevo presupuesto"""
        self.notebook.select(0)
        self.quotes_frame.new_quote()
    
    def quick_new_work_report(self):
        """Abre el editor para crear un nuevo parte de obra"""
        from src.ui.work_reports_manager import WorkReportEditor
        WorkReportEditor(self.root, report_id=None, quote_id=None, on_save=self.work_reports_frame.refresh)
    
    def quick_new_material(self):
        """Abre el editor para crear un nuevo material"""
        MaterialEditor(self.root, material_id=None, on_save=self.materials_frame.refresh)
    
    def quick_new_client(self):
        """Abre el editor para crear un nuevo cliente"""
        ClientEditor(self.root, client_id=None, on_save=self.clients_frame.refresh)
    
    def quick_new_worker(self):
        """Abre el editor para crear un nuevo trabajador"""
        from src.ui.workers_manager import WorkerEditor
        WorkerEditor(self.root, worker_id=None, on_save=self.workers_frame.refresh)
    
    def refresh_all(self):
        """Actualiza todas las pestañas y la barra de estado"""
        self.quotes_frame.refresh()
        self.materials_frame.refresh()
        self.clients_frame.refresh()
        
        quotes_count = len(db.list_quotes())
        self.status_label.config(text=f"Actualizado - {quotes_count} presupuestos")


def main():
    """Función principal de la aplicación"""
    ensure_db()
    
    if HAS_TTKBOOTSTRAP:
        root = ttkb.Window(themename="cosmo")
    else:
        root = tk.Tk()
    
    app = ModernApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()