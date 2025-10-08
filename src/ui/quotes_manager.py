"""
Gestión de presupuestos - Interface y lógica
"""
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from src.database import db
from src.pdf.generator import export_quote_to_pdf, export_document_to_pdf
from src.pdf.preview import generate_quote_preview
from src.ui.wysiwyg_editor import PDFStyleEditor
from src.pdf.document_preview import generate_document_preview
from src.config.settings import QUOTE_EDITOR_SIZE, QUOTE_VIEWER_SIZE, PDF_FILETYPES
from src.ui.ui_utils import (
    center_window, create_styled_button, create_search_frame,
    create_treeview_with_scrollbar, create_button_frame,
    bind_keyboard_shortcuts, show_info, show_error, show_warning, ask_yes_no
)
from src.ui.materials_manager import MaterialEditor
from src.ui.clients_manager import ClientEditor
from PIL import Image, ImageTk
from datetime import datetime


def format_price_es(value):
    """
    Formatea un precio en formato español:
    - Punto como separador de miles
    - Coma como separador decimal
    """
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class QuotesFrame(ttk.Frame):
    """Frame principal para la gestión de presupuestos"""
    
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Barra de búsqueda
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh())
        search_frame, search_entry = create_search_frame(self, self.search_var)
        
        # Tabla de presupuestos
        columns = ('id', 'work_name', 'client', 'date', 'total')
        headings = ('#', 'Obra', 'Cliente', 'Fecha', 'Total (€)')
        column_widths = (50, 250, 200, 100, 100)
        
        tree_frame, self.tree = create_treeview_with_scrollbar(
            self, columns, headings, column_widths
        )
        
        # Doble click para exportar PDF
        self.tree.bind('<Double-Button-1>', lambda e: self.export_pdf())
        
        # Menú contextual (click derecho)
        self._create_context_menu()
        self.tree.bind('<Button-3>', self._show_context_menu)
        
        # Botones de acción
        buttons_config = [
            ('✏️ Editar', self.edit_quote, 'info'),
            ('🗑️ Eliminar', self.delete_quote, 'danger'),
            ('📄 Exportar PDF', self.export_pdf, 'primary'),
            ('👁️ Ver Detalles', self.view_details, 'secondary')
        ]
        
        btn_frame, self.buttons = create_button_frame(self, buttons_config)
    
    def refresh(self):
        """Actualiza la lista de presupuestos"""
        # Limpiar items existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrar presupuestos
        search_term = self.search_var.get().lower()
        quotes = db.list_quotes()
        
        row_count = 0
        for quote in quotes:
            # Obtener work_name de forma segura
            try:
                work_name = quote['work_name'] or ''
            except (KeyError, IndexError):
                work_name = ''
            
            # Aplicar filtro de búsqueda
            if search_term:
                client_name = quote['client_name'] or ''
                if search_term not in client_name.lower() and search_term not in work_name.lower():
                    continue
            
            # Calcular total
            _, items = db.get_quote(quote['id'])
            total = sum(item['unit_price'] * item['quantity'] for item in items)
            total += quote['labor_cost'] or 0
            
            # Alternar colores de filas
            tag = 'evenrow' if row_count % 2 == 0 else 'oddrow'
            
            # Añadir item al árbol
            self.tree.insert('', 'end', iid=str(quote['id']), values=(
                quote['id'],
                work_name or 'Sin nombre',
                quote['client_name'] or '',
                quote['date'],
                format_price_es(total)
            ), tags=(tag,))
            
            row_count += 1
    
    def _create_context_menu(self):
        """Crea el menú contextual"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="✏️ Editar Presupuesto", command=self.edit_quote)
        self.context_menu.add_command(label="📄 Exportar PDF", command=self.export_pdf)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Crear Parte de Obra", command=self.create_work_report)
        self.context_menu.add_command(label="📋 Ver Partes de Obra", command=self.view_work_reports)
    
    def _show_context_menu(self, event):
        """Muestra el menú contextual"""
        # Seleccionar el item bajo el cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def create_work_report(self):
        """Crea un parte de obra desde el presupuesto seleccionado"""
        selection = self.tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un presupuesto', self)
            return
        
        quote_id = int(selection[0])
        
        # Importar aquí para evitar dependencia circular
        from src.ui.work_reports_manager import WorkReportEditor
        
        WorkReportEditor(self, report_id=None, quote_id=quote_id, on_save=None)
    
    def view_work_reports(self):
        """Muestra los partes de obra del presupuesto seleccionado"""
        selection = self.tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un presupuesto', self)
            return
        
        quote_id = int(selection[0])
        reports = db.list_work_reports(quote_id)
        
        if not reports:
            show_info('Info', 'Este presupuesto no tiene partes de obra asociados', self)
            return
        
        # Mostrar ventana con lista de partes
        WorkReportsListDialog(self, quote_id, reports)
    
    def new_quote(self):
        """Abre el editor para crear un nuevo presupuesto"""
        QuoteEditor(self, quote_id=None, on_save=self.refresh)
    
    def edit_quote(self):
        """Abre el editor para editar el presupuesto seleccionado"""
        selected = self.tree.selection()
        if not selected:
            show_warning('Atención', 'Selecciona un presupuesto para editar', self)
            return
        
        quote_id = int(selected[0])
        QuoteEditor(self, quote_id=quote_id, on_save=self.refresh)
    
    def delete_quote(self):
        """Elimina el presupuesto seleccionado"""
        selected = self.tree.selection()
        if not selected:
            show_warning('Atención', 'Selecciona un presupuesto para eliminar', self)
            return
        
        quote_id = int(selected[0])
        confirm_msg = f'¿Eliminar el presupuesto #{quote_id}?\\n\\nEsta acción no se puede deshacer.'
        
        if ask_yes_no('Confirmar', confirm_msg, self):
            try:
                db.delete_quote(quote_id)
                self.refresh()
                show_info('Éxito', 'Presupuesto eliminado correctamente', self)
            except Exception as e:
                show_error('Error', f'Error al eliminar: {str(e)}', self)
    
    def export_pdf(self):
        """Exporta el presupuesto seleccionado a PDF"""
        selected = self.tree.selection()
        if not selected:
            show_warning('Atención', 'Selecciona un presupuesto', self)
            return
        
        quote_id = int(selected[0])
        default_name = f"presupuesto_{quote_id}.pdf"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            initialfile=default_name,
            filetypes=PDF_FILETYPES
        )
        
        if not file_path:
            return
        
        try:
            # SIEMPRE usar export_quote_to_pdf que tiene el formato correcto
            # (datos a la derecha, negritas, subrayado, centrado, etc.)
            export_quote_to_pdf(quote_id, file_path)
            
            show_info('Éxito', f'PDF exportado:\n{file_path}', self)
        except Exception as e:
            show_error('Error', f'Error al exportar: {str(e)}', self)
    
    def view_details(self):
        """Muestra los detalles del presdupuesto seleccionado"""
        selected = self.tree.selection()
        if not selected:
            show_warning('Atención', 'Selecciona un presupuesto', self)
            return
        
        quote_id = int(selected[0])
        QuoteViewer(self, quote_id)


class QuoteViewer(tk.Toplevel):
    """Visor de detalles de presupuesto - Ventana modal"""
    
    def __init__(self, master, quote_id):
        super().__init__(master)
        self.quote_id = quote_id
        
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """Configura la ventana"""
        self.title(f'Presupuesto #{self.quote_id}')
        
        width, height = map(int, QUOTE_VIEWER_SIZE.split('x'))
        center_window(self, width, height)
        
        # Configurar tamaño mínimo (85% del tamaño original)
        self.minsize(int(width * 0.85), int(height * 0.85))
        
        # Hacer la ventana redimensionable
        self.resizable(True, True)
        
        # Modal
        self.transient(self.master)
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Obtener datos del presupuesto
        quote, items = db.get_quote(self.quote_id)
        
        # Header con información del presupuesto
        self._create_header(quote)
        
        # Lista de items
        self._create_items_section(items)
        
        # Resumen de totales
        self._create_totals_section(quote, items)
        
        # Botón cerrar
        ttk.Button(self, text='Cerrar', command=self.destroy).pack(pady=10)
    
    def _create_header(self, quote):
        """Crea la sección del header con información del presupuesto"""
        header = ttk.Frame(self, padding=20)
        header.pack(fill='x')
        
        ttk.Label(header, text=f"Presupuesto #{quote['id']}", 
                 font=('Helvetica', 16, 'bold')).pack(anchor='w')
        
        # Mostrar nombre de obra si existe
        try:
            work_name = quote['work_name']
            if work_name:
                ttk.Label(header, text=f"Obra: {work_name}", 
                         font=('Helvetica', 12, 'bold'), 
                         foreground='#2B7DE9').pack(anchor='w', pady=(5, 0))
        except (KeyError, IndexError):
            pass
        
        ttk.Label(header, text=f"Fecha: {quote['date']}").pack(anchor='w')
        ttk.Label(header, text=f"Cliente: {quote['client_name'] or 'N/A'}").pack(anchor='w')
        
        if quote['client_address']:
            ttk.Label(header, text=f"Dirección: {quote['client_address']}").pack(anchor='w')
        
        if quote['client_dni']:
            ttk.Label(header, text=f"DNI: {quote['client_dni']}").pack(anchor='w')
    
    def _create_items_section(self, items):
        """Crea la sección de items del presupuesto"""
        items_frame = ttk.LabelFrame(self, text='Items', padding=10)
        items_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Frame con borde visible
        border_canvas = tk.Canvas(items_frame, highlightthickness=3,
                                 highlightbackground='#2B7DE9',
                                 highlightcolor='#2B7DE9',
                                 background='#FFFFFF')
        border_canvas.pack(fill='both', expand=True)
        
        tree_container = ttk.Frame(border_canvas)
        tree_container.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Configurar treeview para items con columnas incluyendo beneficio y margen
        columns = ('name', 'qty', 'supplier_price', 'price', 'benefit', 'margin', 'total')
        tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=10)
        
        tree.heading('name', text='Material', anchor='w')
        tree.heading('qty', text='Cantidad', anchor='center')
        tree.heading('supplier_price', text='P. Proveedor', anchor='e')
        tree.heading('price', text='PVP', anchor='e')
        tree.heading('benefit', text='Beneficio', anchor='e')
        tree.heading('margin', text='Margen %', anchor='center')
        tree.heading('total', text='Total', anchor='e')
        
        tree.column('name', width=200, anchor='w')
        tree.column('qty', width=85, anchor='center')
        tree.column('supplier_price', width=110, anchor='e')
        tree.column('price', width=95, anchor='e')
        tree.column('benefit', width=95, anchor='e')
        tree.column('margin', width=90, anchor='center')
        tree.column('total', width=110, anchor='e')
        
        # Configurar tags para filas alternadas con mejor contraste
        tree.tag_configure('oddrow', background='#FFFFFF')
        tree.tag_configure('evenrow', background='#F0F4F8')
        
        tree.pack(fill='both', expand=True)
        
        # Cargar items con filas alternadas
        for i, item in enumerate(items):
            line_total = item['unit_price'] * item['quantity']
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Obtener precio de proveedor (sqlite3.Row no tiene .get())
            try:
                supplier_price = item['supplier_price'] or 0
            except (KeyError, IndexError):
                supplier_price = 0
            
            sale_price = item['unit_price']
            
            # Calcular beneficio y margen
            benefit = sale_price - supplier_price
            margin = ((benefit / sale_price) * 100) if sale_price > 0 else 0
            
            tree.insert('', 'end', values=(
                item['name'],
                item['quantity'],
                format_price_es(supplier_price),
                format_price_es(sale_price),
                format_price_es(benefit),
                f"{margin:.1f}%",
                format_price_es(line_total)
            ), tags=(tag,))
    
    def _create_totals_section(self, quote, items):
        """Crea la sección de totales"""
        totals_frame = ttk.Frame(self, padding=20)
        totals_frame.pack(fill='x')
        
        # Calcular totales
        subtotal = sum(item['unit_price'] * item['quantity'] for item in items)
        labor_cost = quote['labor_cost'] or 0
        total = subtotal + labor_cost
        
        # Calcular beneficio total de materiales
        total_cost = 0
        for item in items:
            try:
                supplier_price = item['supplier_price'] or 0
            except (KeyError, IndexError):
                supplier_price = 0
            total_cost += supplier_price * item['quantity']
        
        total_benefit = subtotal - total_cost
        overall_margin = ((total_benefit / subtotal) * 100) if subtotal > 0 else 0
        
        # Mostrar totales
        ttk.Label(totals_frame, text=f"Coste materiales (proveedor): {format_price_es(total_cost)} €", 
                 font=('Helvetica', 10), foreground='gray').pack(anchor='e')
        ttk.Label(totals_frame, text=f"Subtotal materiales (venta): {format_price_es(subtotal)} €", 
                 font=('Helvetica', 11)).pack(anchor='e')
        ttk.Label(totals_frame, text=f"Beneficio materiales: {format_price_es(total_benefit)} € ({overall_margin:.1f}%)", 
                 font=('Helvetica', 11), foreground='green').pack(anchor='e', pady=(0, 10))
        ttk.Label(totals_frame, text=f"Mano de obra: {format_price_es(labor_cost)} €", 
                 font=('Helvetica', 11)).pack(anchor='e')
        ttk.Label(totals_frame, text=f"TOTAL: {format_price_es(total)} €", 
                 font=('Helvetica', 14, 'bold')).pack(anchor='e')


class QuoteEditor(tk.Toplevel):
    """Editor de presupuestos - Ventana modal"""
    
    def __init__(self, master, quote_id=None, on_save=None):
        super().__init__(master)
        print(f"DEBUG QuoteEditor.__init__: quote_id={quote_id}")
        self.quote_id = quote_id
        self.on_save = on_save
        self.items_data = []  # Lista de items del presupuesto
        self.preview_photo = None  # Para evitar garbage collection
        self.preview_update_job = None  # Para debouncing de updates
        self.document_update_job = None  # Para debouncing de regeneración de documento
        self.document_needs_save = False  # Flag para indicar si el documento ha cambiado
        
        self._setup_window()
        self._setup_ui()
        self._load_data()
        self._setup_keyboard_shortcuts()
        
        # Generar el documento inicial
        self.update_idletasks()
        self.after(100, self._regenerate_document)
        
        # Establecer grab después de que la ventana esté completamente visible
        self.after(200, self.grab_set)
        
        print("DEBUG: QuoteEditor inicializado completamente")
    
    def _setup_window(self):
        """Configura la ventana"""
        title = 'Editar Presupuesto' if self.quote_id else 'Nuevo Presupuesto'
        self.title(title)
        
        # Configurar como modal primero
        self.transient(self.master)
        
        # Hacer la ventana redimensionable
        self.resizable(True, True)
        
        # Obtener tamaño de la pantalla y maximizar
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Configurar geometría para ocupar toda la pantalla
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Intentar maximizar usando diferentes métodos según el sistema
        try:
            # Para algunos gestores de ventanas en Linux
            self.attributes('-zoomed', True)
        except:
            pass
        
        try:
            # Método alternativo
            self.state('zoomed')
        except:
            pass
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Contenedor principal con grid
        main_container = ttk.Frame(self)
        main_container.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        
        # Configurar peso de filas y columnas para redimensionamiento
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=0)  # Panel izquierdo (datos + items) - tamaño fijo
        main_container.grid_columnconfigure(1, weight=2)  # Panel derecho (documento + preview) - más espacio
        
        # Panel izquierdo - Datos y items
        left_container = ttk.Frame(main_container)
        left_container.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=10)
        left_container.grid_rowconfigure(0, weight=0)  # Datos básicos
        left_container.grid_rowconfigure(1, weight=1)  # Items
        left_container.grid_columnconfigure(0, weight=1)
        
        # Sub-panel: datos básicos
        self._create_left_panel(left_container)
        
        # Sub-panel: items del presupuesto
        self._create_center_panel(left_container)
        
        # Panel derecho - Documento editable y preview
        self._create_document_and_preview_panel(main_container)
        
        # Botones principales en la parte inferior
        self._create_bottom_buttons()
    
    def _create_left_panel(self, parent):
        """Crea el panel con datos básicos del presupuesto"""
        left_panel = ttk.Frame(parent, padding=10)
        left_panel.grid(row=0, column=0, sticky='nsew')
        
        # Configurar expansión de filas
        left_panel.grid_rowconfigure(4, weight=1)  # La sección de materiales se expande
        
        # Sección cliente
        self._create_client_section(left_panel)
        
        # Sección nombre de obra
        self._create_work_name_section(left_panel)
        
        # Sección mano de obra
        self._create_labor_section(left_panel)
        
        # Sección búsqueda de materiales (expande para llenar espacio)
        self._create_material_search_section(left_panel)
        
        # Sección nombre de obra
        self._create_work_name_section(left_panel)
        
        # Sección mano de obra
        self._create_labor_section(left_panel)
        
        # Sección búsqueda de materiales (expande para llenar espacio)
        self._create_material_search_section(left_panel)
    
    def _create_client_section(self, parent):
        """Crea la sección de selección de cliente con búsqueda"""
        client_frame = ttk.LabelFrame(parent, text='👤 Cliente', padding=12)
        client_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        # Cargar lista de clientes
        self.clients_list = db.list_clients()
        self.filtered_clients = self.clients_list.copy()
        self.selected_client = None
        
        # Campo de búsqueda de cliente
        self.client_search_var = tk.StringVar()
        self.client_search_var.trace('w', lambda *args: self._filter_clients())
        
        search_container = ttk.Frame(client_frame)
        search_container.pack(fill='x', pady=(0, 8))
        
        # Búsqueda con icono
        search_label = ttk.Label(search_container, text='🔍', font=('Helvetica', 11))
        search_label.pack(side='left', padx=(0, 5))
        
        self.client_entry = ttk.Entry(search_container, textvariable=self.client_search_var, 
                                      font=('Helvetica', 10))
        self.client_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Botón para añadir nuevo cliente
        new_client_btn = create_styled_button(
            search_container, '+ Nuevo', self._quick_add_client, 'success'
        )
        new_client_btn.pack(side='left')
        
        # Lista de resultados de clientes (compacta y elegante)
        list_frame = ttk.Frame(client_frame)
        list_frame.pack(fill='both', expand=False)
        
        self.client_listbox = tk.Listbox(list_frame, height=3, font=('Helvetica', 9),
                                         relief='solid', borderwidth=1,
                                         selectmode='single', activestyle='none')
        self.client_listbox.pack(side='left', fill='both', expand=True)
        
        client_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', 
                                        command=self.client_listbox.yview)
        self.client_listbox.configure(yscrollcommand=client_scrollbar.set)
        client_scrollbar.pack(side='right', fill='y')
        
        # Doble click o Enter para seleccionar
        self.client_listbox.bind('<Double-Button-1>', lambda e: self._select_client())
        self.client_listbox.bind('<Return>', lambda e: self._select_client())
        
        # Mostrar todos los clientes inicialmente
        self._show_all_clients()
    
    def _create_work_name_section(self, parent):
        """Crea la sección de nombre de obra"""
        work_frame = ttk.LabelFrame(parent, text='🏗️ Nombre de Obra', padding=12)
        work_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        
        self.work_name_entry = ttk.Entry(work_frame, font=('Helvetica', 10))
        self.work_name_entry.pack(fill='x')
        self.work_name_entry.bind('<KeyRelease>', lambda e: self._schedule_document_update())
    
    def _create_labor_section(self, parent):
        """Crea la sección de mano de obra"""
        labor_frame = ttk.LabelFrame(parent, text='💰 Mano de obra', padding=12)
        labor_frame.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        
        # Frame horizontal para label y entry
        labor_container = ttk.Frame(labor_frame)
        labor_container.pack(fill='x')
        
        ttk.Label(labor_container, text='Coste:', font=('Helvetica', 10)).pack(side='left', padx=(0, 5))
        
        self.labor_entry = ttk.Entry(labor_container, font=('Helvetica', 10), width=15)
        self.labor_entry.insert(0, '0')
        self.labor_entry.pack(side='left', padx=(0, 5))
        
        ttk.Label(labor_container, text='€', font=('Helvetica', 10, 'bold')).pack(side='left')
        
        # Actualizar totales y documento cuando cambie
        def on_labor_change(e):
            self._update_totals()
            self._schedule_document_update()
        self.labor_entry.bind('<KeyRelease>', on_labor_change)
    
    def _create_material_search_section(self, parent):
        """Crea la sección de búsqueda y adición de materiales"""
        mat_frame = ttk.LabelFrame(parent, text='📦 Buscar y añadir material', padding=12)
        mat_frame.grid(row=4, column=0, sticky='nsew', pady=(0, 0))
        
        # Configurar para que se expanda verticalmente
        parent.grid_rowconfigure(4, weight=1)
        
        # Campo de búsqueda con icono
        search_container = ttk.Frame(mat_frame)
        search_container.pack(fill='x', pady=(0, 8))
        
        ttk.Label(search_container, text='🔍', font=('Helvetica', 12)).pack(side='left', padx=(0, 5))
        
        self.mat_search_var = tk.StringVar()
        self.mat_search_var.trace('w', lambda *args: self._filter_materials())
        
        search_entry = ttk.Entry(search_container, textvariable=self.mat_search_var, 
                                font=('Helvetica', 10))
        search_entry.pack(side='left', fill='x', expand=True)
        
        # Lista de resultados (más compacta)
        self._create_material_results_list(mat_frame)
        
        # Botones de acción (más compactos)
        self._create_material_action_buttons(mat_frame)
    
    def _create_material_results_list(self, parent):
        """Crea la lista de resultados de materiales"""
        results_frame = ttk.Frame(parent)
        results_frame.pack(fill='both', expand=True, pady=(0, 8))
        
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.mat_listbox = tk.Listbox(
            results_frame, height=8, yscrollcommand=scrollbar.set,
            font=('Helvetica', 9), relief='solid', borderwidth=1
        )
        self.mat_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.mat_listbox.yview)
        
        # Doble click para añadir
        self.mat_listbox.bind('<Double-Button-1>', lambda e: self._add_selected_material())
        
        # Cargar materiales
        self.materials_list = db.list_materials()
        self.filtered_materials = []
        self._filter_materials()
    
    def _create_material_action_buttons(self, parent):
        """Crea los botones de acción para materiales"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x')
        
        add_btn = create_styled_button(
            btn_frame, '+ Añadir', self._add_selected_material, 'success'
        )
        add_btn.pack(side='left', fill='x', expand=True, padx=(0, 3))
        
        new_btn = create_styled_button(
            btn_frame, 'Nuevo', self._quick_add_material, 'primary'
        )
        new_btn.pack(side='right', fill='x', expand=True, padx=(3, 0))
    
    def _create_center_panel(self, parent):
        """Crea el panel central con la lista de items"""
        center_panel = ttk.Frame(parent, padding=10)
        center_panel.grid(row=0, column=1, sticky='nsew', padx=(5, 5), pady=10)
        
        # Configurar para que se expanda
        center_panel.grid_rowconfigure(1, weight=1)
        center_panel.grid_columnconfigure(0, weight=1)
        
        # Título con icono
        title_label = ttk.Label(center_panel, text='📋 Items del presupuesto', 
                 font=('Helvetica', 12, 'bold'))
        title_label.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        # Frame con borde visible para la tabla
        border_canvas = tk.Canvas(center_panel, highlightthickness=2,
                                 highlightbackground='#2B7DE9',
                                 highlightcolor='#2B7DE9',
                                 background='#FFFFFF')
        border_canvas.grid(row=1, column=0, sticky='nsew', pady=(0, 8))
        
        tree_container = ttk.Frame(border_canvas)
        tree_container.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Tabla de items con columnas incluyendo beneficio y margen (height reducido)
        columns = ('name', 'supplier_price', 'price', 'benefit', 'margin', 'qty', 'total')
        self.items_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=6)
        
        self.items_tree.heading('name', text='📦 Material', anchor='w')
        self.items_tree.heading('supplier_price', text='💶 P. Proveedor', anchor='e')
        self.items_tree.heading('price', text='💰 PVP', anchor='e')
        self.items_tree.heading('benefit', text='📈 Beneficio', anchor='e')
        self.items_tree.heading('margin', text='📊 Margen %', anchor='center')
        self.items_tree.heading('qty', text='🔢 Cantidad', anchor='center')
        self.items_tree.heading('total', text='💵 Total', anchor='e')
        
        self.items_tree.column('name', width=160, anchor='w')
        self.items_tree.column('supplier_price', width=105, anchor='e')
        self.items_tree.column('price', width=90, anchor='e')
        self.items_tree.column('benefit', width=90, anchor='e')
        self.items_tree.column('margin', width=85, anchor='center')
        self.items_tree.column('qty', width=80, anchor='center')
        self.items_tree.column('total', width=110, anchor='e')
        
        # Configurar tags para filas alternadas con mejor contraste
        self.items_tree.tag_configure('oddrow', background='#FFFFFF')
        self.items_tree.tag_configure('evenrow', background='#F0F4F8')
        
        self.items_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Doble click para editar la celda
        self.items_tree.bind('<Double-Button-1>', lambda e: self._edit_item_cell(e))
        
        # Botones de items (más compactos y ordenados)
        item_btns = ttk.Frame(center_panel)
        item_btns.grid(row=2, column=0, sticky='ew', pady=(0, 8))
        
        edit_btn = create_styled_button(item_btns, '✏️ Editar', self._edit_item, 'info')
        edit_btn.pack(side='left', padx=(0, 5))
        
        remove_btn = create_styled_button(item_btns, '🗑️ Quitar', self._remove_item, 'danger')
        remove_btn.pack(side='left')
        
        # Resumen de totales (más compacto y visible)
        totals_frame = ttk.LabelFrame(center_panel, text='💵 Resumen', padding=10)
        totals_frame.grid(row=3, column=0, sticky='ew')
        
        self.total_label = ttk.Label(totals_frame, text='Total: 0.00 €', 
                                   font=('Helvetica', 13, 'bold'),
                                   foreground='#2B7DE9')
        self.total_label.pack()
    
    def _create_document_and_preview_panel(self, parent):
        """Crea el panel derecho con editor WYSIWYG del documento completo"""
        right_panel = ttk.Frame(parent, padding=10)
        right_panel.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=10)
        
        # Configurar para que se expanda
        right_panel.grid_rowconfigure(0, weight=1)  # Editor ocupa todo el espacio
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Editor WYSIWYG para el documento completo (incluye su propia toolbar con botón regenerar)
        self.document_editor = PDFStyleEditor(right_panel, regenerate_callback=self._regenerate_document)
        self.document_editor.grid(row=0, column=0, sticky='nsew')
        
        # Configurar callback para marcar como modificado
        self.document_editor.on_change_callback = self._on_document_change
    
    def _create_preview_panel(self, parent):
        """LEGACY: Mantener por compatibilidad - ahora usa _create_document_and_preview_panel"""
        pass
    
    def _create_bottom_buttons(self):
        """Crea los botones principales de la ventana"""
        bottom_frame = ttk.Frame(self, padding=(10, 8))
        bottom_frame.grid(row=1, column=0, sticky='ew')
        
        # Configurar grid para centrar
        self.grid_rowconfigure(1, weight=0)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=0)
        bottom_frame.grid_columnconfigure(2, weight=1)
        
        # Botón cancelar (izquierda)
        cancel_btn = create_styled_button(
            bottom_frame, 'Cancelar', self.destroy, 'secondary'
        )
        cancel_btn.grid(row=0, column=0, sticky='w', padx=5)
        
        # Texto de ayuda (centrado)
        help_text = 'Ctrl+S: Guardar | Esc: Cancelar'
        ttk.Label(bottom_frame, text=help_text, font=('Helvetica', 8), 
                 foreground='gray').grid(row=0, column=1, padx=10)
        
        # Botón guardar (derecha, prominente)
        save_btn = create_styled_button(
            bottom_frame, '💾 GUARDAR PRESUPUESTO', self._save, 'success'
        )
        save_btn.grid(row=0, column=2, sticky='e', padx=5, ipadx=15, ipady=5)
    
    def _setup_keyboard_shortcuts(self):
        """Configura los atajos de teclado"""
        shortcuts = {
            '<Escape>': self.destroy,
            '<Control-s>': self._save,
            '<Control-S>': self._save
        }
        bind_keyboard_shortcuts(self, shortcuts)
    
    def _quick_add_client(self):
        """Abre el editor para añadir un nuevo cliente"""
        ClientEditor(self, client_id=None, on_save=self._reload_clients)
    
    def _reload_clients(self):
        """Recarga la lista de clientes después de añadir uno nuevo"""
        self.clients_list = db.list_clients()
        self._filter_clients()
    
    def _filter_clients(self):
        """Filtra la lista de clientes según la búsqueda"""
        query = self.client_search_var.get().strip().lower()
        
        if not query:
            self._show_all_clients()
            return
        
        # Filtrar clientes
        self.filtered_clients = []
        for client in self.clients_list:
            name = client['name'].lower()
            dni = (client['dni'] or '').lower()
            
            if query in name or query in dni:
                self.filtered_clients.append(client)
        
        # Mostrar resultados filtrados
        self._show_filtered_clients()
    
    def _show_all_clients(self):
        """Muestra todos los clientes"""
        self.filtered_clients = self.clients_list.copy()
        self.client_listbox.delete(0, tk.END)
        
        for client in self.filtered_clients:
            display_text = client['name']
            if client['dni']:
                display_text += f" - {client['dni']}"
            self.client_listbox.insert(tk.END, display_text)
    
    def _show_filtered_clients(self):
        """Muestra los clientes filtrados"""
        self.client_listbox.delete(0, tk.END)
        
        for client in self.filtered_clients:
            display_text = client['name']
            if client['dni']:
                display_text += f" - {client['dni']}"
            self.client_listbox.insert(tk.END, display_text)
    
    def _select_client(self):
        """Selecciona el cliente de la lista"""
        selection = self.client_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        if idx >= len(self.filtered_clients):
            return
        
        client = self.filtered_clients[idx]
        self.selected_client = client
        
        # Actualizar el campo de búsqueda con el nombre seleccionado
        self.client_search_var.set(client['name'])
        
        # Actualizar el documento con los nuevos datos del cliente
        self._schedule_document_update()
        
        # Enfocar en el siguiente campo
        self.work_name_entry.focus()
    
    def _quick_add_material(self):
        """Abre el editor para añadir un nuevo material"""
        MaterialEditor(self, material_id=None, on_save=self._reload_materials)
    
    def _reload_materials(self):
        """Recarga la lista de materiales"""
        self.materials_list = db.list_materials()
        self._filter_materials()
    
    def _reload_materials_list(self):
        """Alias para recargar la lista de materiales (usado al actualizar precios)"""
        self._reload_materials()
    
    def _filter_materials(self):
        """Filtra los materiales según el término de búsqueda"""
        query = self.mat_search_var.get().strip().lower()
        
        self.mat_listbox.delete(0, tk.END)
        self.filtered_materials = []
        
        if not query:
            # Mostrar todos los materiales agrupados por categoría
            self._show_all_materials()
        else:
            # Buscar y mostrar materiales coincidentes
            self._show_filtered_materials(query)
    
    def _show_all_materials(self):
        """Muestra todos los materiales agrupados por categoría"""
        materials_by_cat = {}
        for material in self.materials_list:
            category = material['category'] or 'Sin categoría'
            if category not in materials_by_cat:
                materials_by_cat[category] = []
            materials_by_cat[category].append(material)
        
        for category in sorted(materials_by_cat.keys()):
            self.mat_listbox.insert(tk.END, f"━━ {category} ━━")
            self.filtered_materials.append(None)  # Separador de categoría
            
            for material in sorted(materials_by_cat[category], key=lambda x: x['name']):
                display = f"  {material['name']} - {format_price_es(material['price'])}€"
                self.mat_listbox.insert(tk.END, display)
                self.filtered_materials.append(material)
    
    def _show_filtered_materials(self, query):
        """Muestra los materiales filtrados por búsqueda"""
        matches = []
        for material in self.materials_list:
            score = self._calculate_search_score(material, query)
            if score > 0:
                matches.append((score, material))
        
        # Ordenar por puntuación y luego por nombre
        matches.sort(key=lambda x: (-x[0], x[1]['name']))
        
        if matches:
            for score, material in matches[:20]:  # Limitar a 20 resultados
                category = material['category'] or 'Sin categoría'
                try:
                    supplier_price = material['supplier_price'] or 0
                except (KeyError, IndexError):
                    supplier_price = 0
                display = f"{material['name']} [{category}] - Prov: {format_price_es(supplier_price)}€ | Venta: {format_price_es(material['price'])}€"
                self.mat_listbox.insert(tk.END, display)
                self.filtered_materials.append(material)
        else:
            self.mat_listbox.insert(tk.END, "❌ No se encontraron materiales")
            self.filtered_materials.append(None)
    
    def _calculate_search_score(self, material, query):
        """Calcula la puntuación de coincidencia para la búsqueda"""
        name_lower = material['name'].lower()
        desc_lower = (material['description'] or '').lower()
        cat_lower = (material['category'] or '').lower()
        
        # Coincidencia exacta en nombre
        if query == name_lower:
            return 100
        elif name_lower.startswith(query):
            return 90
        elif query in name_lower:
            return 80
        elif query in desc_lower:
            return 50
        elif query in cat_lower:
            return 40
        
        return 0
    
    def _add_selected_material(self):
        """Añade el material seleccionado a la lista de items"""
        selection = self.mat_listbox.curselection()
        if not selection:
            if self.filtered_materials and self.filtered_materials[0]:
                # Auto-seleccionar el primero si no hay selección
                selection = (0,)
            else:
                return
        
        idx = selection[0]
        if idx >= len(self.filtered_materials):
            return
        
        material = self.filtered_materials[idx]
        if material is None:  # Separador de categoría
            return
        
        # Obtener precio de proveedor
        try:
            supplier_price = material['supplier_price'] or 0
        except (KeyError, IndexError):
            supplier_price = 0
        
        # Añadir directamente con cantidad 1 y precio por defecto
        self.items_data.append({
            'material_id': material['id'],
            'name': material['name'],
            'description': material['description'],
            'image_path': material['image_path'],
            'price': material['price'],  # Precio de venta por defecto
            'supplier_price': supplier_price,  # Precio del proveedor
            'quantity': 1.0,  # Cantidad 1 por defecto
            'original_price': material['price']  # Guardar precio original para comparación
        })
        
        self._refresh_items()
        self.mat_search_var.set('')  # Limpiar búsqueda
    
    def _refresh_items(self):
        """Actualiza la visualización de items"""
        # Limpiar items existentes
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Añadir items actuales con filas alternadas
        for i, item in enumerate(self.items_data):
            total = item['price'] * item['quantity']
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Obtener precio de proveedor (items_data es dict, sí tiene .get())
            supplier_price = item.get('supplier_price', 0) or 0
            sale_price = item['price']
            
            # Calcular beneficio y margen
            benefit = sale_price - supplier_price
            margin = ((benefit / sale_price) * 100) if sale_price > 0 else 0
            
            self.items_tree.insert('', 'end', iid=str(i), values=(
                item['name'],
                format_price_es(supplier_price),
                format_price_es(sale_price),
                format_price_es(benefit),
                f"{margin:.1f}%",
                item['quantity'],
                format_price_es(total)
            ), tags=(tag,))
        
        self._update_totals()
        
        # Regenerar el documento para reflejar los cambios
        self._schedule_document_update()
    
    def _update_totals(self):
        """Actualiza la visualización de totales"""
        subtotal = sum(item['price'] * item['quantity'] for item in self.items_data)
        
        try:
            labor_cost = float(self.labor_entry.get() or 0)
        except ValueError:
            labor_cost = 0
        
        total = subtotal + labor_cost
        
        self.total_label.config(
            text=f'Subtotal: {format_price_es(subtotal)} € | Mano de obra: {format_price_es(labor_cost)} € | TOTAL: {format_price_es(total)} €'
        )
    
    def _schedule_document_update(self):
        """Programa una actualización del documento con debouncing"""
        if hasattr(self, 'document_update_job') and self.document_update_job:
            self.after_cancel(self.document_update_job)
        self.document_update_job = self.after(500, self._regenerate_document)
        
        # Actualizar preview
        self._schedule_preview_update()
    
    def _edit_item_cell(self, event):
        """Edita la celda clickeada directamente en el Treeview"""
        region = self.items_tree.identify('region', event.x, event.y)
        if region != 'cell':
            return
        
        column = self.items_tree.identify_column(event.x)
        row_id = self.items_tree.identify_row(event.y)
        
        if not row_id:
            return
        
        # Permitir editar: supplier_price (#2), price (#3), benefit (#4), margin (#5), qty (#6)
        if column not in ('#2', '#3', '#4', '#5', '#6'):  
            return
        
        idx = int(row_id)
        item = self.items_data[idx]
        
        # Obtener valores actuales
        supplier_price = item.get('supplier_price', 0) or 0
        sale_price = item['price']
        quantity = item['quantity']
        
        # Determinar qué estamos editando
        if column == '#2':  # Precio proveedor
            col_label = 'Precio Proveedor'
            current_value = supplier_price
        elif column == '#3':  # Precio venta
            col_label = 'Precio Venta'
            current_value = sale_price
        elif column == '#4':  # Beneficio
            col_label = 'Beneficio'
            current_value = sale_price - supplier_price
        elif column == '#5':  # Margen %
            col_label = 'Margen %'
            current_value = ((sale_price - supplier_price) / sale_price * 100) if sale_price > 0 else 0
        else:  # column == '#6' - Cantidad
            col_label = 'Cantidad'
            current_value = quantity
        
        # Obtener posición de la celda
        bbox = self.items_tree.bbox(row_id, column)
        if not bbox:
            return
        
        # Crear Entry temporal sobre la celda
        x, y, width, height = bbox
        
        entry_var = tk.StringVar(value=str(current_value).replace('%', ''))
        entry = tk.Entry(self.items_tree, textvariable=entry_var, 
                        font=('Segoe UI', 10), 
                        relief='solid',
                        borderwidth=2,
                        justify='center')
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus_set()
        entry.select_range(0, tk.END)
        entry.icursor(tk.END)
        
        def save_edit(event=None):
            try:
                new_value = float(entry_var.get())
                material_updated = False  # Flag para saber si debemos recargar la lista de materiales
                
                if column == '#2':  # Precio proveedor
                    if new_value < 0:
                        raise ValueError("El precio no puede ser negativo")
                    old_supplier_price = self.items_data[idx]['supplier_price']
                    self.items_data[idx]['supplier_price'] = new_value
                    # El precio de venta se mantiene, beneficio y margen se recalculan
                    
                    # Actualizar en la base de datos si cambió
                    if old_supplier_price != new_value and 'material_id' in self.items_data[idx]:
                        material_id = self.items_data[idx]['material_id']
                        db.update_material_supplier_price(material_id, new_value)
                        material_updated = True
                    
                elif column == '#3':  # Precio venta
                    if new_value < 0:
                        raise ValueError("El precio no puede ser negativo")
                    old_price = self.items_data[idx]['price']
                    self.items_data[idx]['price'] = new_value
                    # El precio proveedor se mantiene, beneficio y margen se recalculan
                    
                    # Actualizar en la base de datos si cambió
                    if old_price != new_value and 'material_id' in self.items_data[idx]:
                        material_id = self.items_data[idx]['material_id']
                        db.update_material_price(material_id, new_value)
                        material_updated = True
                    
                elif column == '#4':  # Beneficio
                    if new_value < 0:
                        raise ValueError("El beneficio no puede ser negativo")
                    # Beneficio = Precio Venta - Precio Proveedor
                    # Nuevo Precio Venta = Precio Proveedor + Beneficio
                    supplier_price = item.get('supplier_price', 0) or 0
                    new_sale_price = supplier_price + new_value
                    if new_sale_price < 0:
                        raise ValueError("El precio de venta resultante no puede ser negativo")
                    old_price = self.items_data[idx]['price']
                    self.items_data[idx]['price'] = new_sale_price
                    
                    # Actualizar precio de venta en la base de datos
                    if old_price != new_sale_price and 'material_id' in self.items_data[idx]:
                        material_id = self.items_data[idx]['material_id']
                        db.update_material_price(material_id, new_sale_price)
                        material_updated = True
                    
                elif column == '#5':  # Margen %
                    if new_value < 0 or new_value >= 100:
                        raise ValueError("El margen debe estar entre 0 y 99.9%")
                    # Margen = ((Precio Venta - Precio Proveedor) / Precio Venta) * 100
                    # Precio Venta = Precio Proveedor / (1 - Margen/100)
                    supplier_price = item.get('supplier_price', 0) or 0
                    margin_decimal = new_value / 100
                    if margin_decimal >= 1:
                        raise ValueError("El margen no puede ser 100% o superior")
                    new_sale_price = supplier_price / (1 - margin_decimal) if margin_decimal < 1 else supplier_price * 2
                    old_price = self.items_data[idx]['price']
                    self.items_data[idx]['price'] = new_sale_price
                    
                    # Actualizar precio de venta en la base de datos
                    if old_price != new_sale_price and 'material_id' in self.items_data[idx]:
                        material_id = self.items_data[idx]['material_id']
                        db.update_material_price(material_id, new_sale_price)
                        material_updated = True
                    
                else:  # column == '#6' - Cantidad
                    if new_value <= 0:
                        raise ValueError("La cantidad debe ser mayor que 0")
                    self.items_data[idx]['quantity'] = new_value
                
                self._refresh_items()
                
                # Si se actualizó un material en la BD, recargar la lista de materiales
                if material_updated:
                    self._reload_materials_list()
            except ValueError as e:
                show_error('Error', str(e) if str(e) else 'Valor inválido', self)
            finally:
                entry.destroy()
        
        def cancel_edit(event=None):
            entry.destroy()
        
        entry.bind('<Return>', save_edit)
        entry.bind('<Escape>', cancel_edit)
        entry.bind('<FocusOut>', save_edit)
    
    def _edit_item(self):
        """Mensaje informativo para usar doble click"""
        show_info(
            'Editar items',
            'Para editar cualquier valor (precio proveedor, precio venta, beneficio, margen, cantidad), '
            'haz doble click directamente sobre el valor que quieres cambiar.\n\n'
            'Los campos están sincronizados:\n'
            '• Si cambias el precio proveedor → se recalculan beneficio y margen\n'
            '• Si cambias el precio venta → se recalculan beneficio y margen\n'
            '• Si cambias el beneficio → se recalcula el precio de venta\n'
            '• Si cambias el margen → se recalcula el precio de venta',
            self
        )
    
    def _remove_item(self):
        """Elimina el item seleccionado"""
        selected = self.items_tree.selection()
        if not selected:
            return
        
        idx = int(selected[0])
        del self.items_data[idx]
        self._refresh_items()
    
    def _load_data(self):
        """Carga los datos del presupuesto si está editando"""
        print(f"DEBUG _load_data: quote_id={self.quote_id}")
        
        if not self.quote_id:
            # Si es nuevo presupuesto, no hay datos que cargar
            print("DEBUG: Nuevo presupuesto, sin datos que cargar")
            return
        
        quote, items = db.get_quote(self.quote_id)
        if not quote:
            show_error('Error', 'Presupuesto no encontrado', self)
            self.destroy()
            return
        
        # Cargar información del presupuesto
        if quote['client_name']:
            self.client_search_var.set(quote['client_name'])
            # Buscar el cliente en la lista para seleccionarlo
            for client in self.clients_list:
                if client['name'] == quote['client_name']:
                    self.selected_client = client
                    break
        
        # Cargar work_name de forma segura
        try:
            if quote['work_name']:
                self.work_name_entry.delete(0, tk.END)
                self.work_name_entry.insert(0, quote['work_name'])
        except (KeyError, IndexError):
            pass  # La columna no existe en presupuestos antiguos
        
        if quote['labor_cost']:
            self.labor_entry.delete(0, tk.END)
            self.labor_entry.insert(0, str(quote['labor_cost']))
        
        # Cargar items PRIMERO
        for item in items:
            # Obtener precio de proveedor
            try:
                supplier_price = item['supplier_price'] or 0
            except (KeyError, IndexError):
                supplier_price = 0
            
            self.items_data.append({
                'material_id': item['material_id'],
                'name': item['name'],
                'description': item['description'],
                'image_path': item['image_path'],
                'price': item['unit_price'],
                'supplier_price': supplier_price,
                'quantity': item['quantity'],
                'original_price': item['unit_price']  # Guardar precio original
            })
        
        self._refresh_items()
        
        # Cargar condiciones si existen
        if hasattr(self, 'document_editor'):
            try:
                if quote.get('formatted_notes'):
                    # Extraer solo las condiciones del texto guardado
                    saved_text = quote['formatted_notes']
                    # Las condiciones están después de "CONDICIONES:" o al principio
                    self.saved_conditions = saved_text
                else:
                    self.saved_conditions = None
            except (KeyError, AttributeError):
                self.saved_conditions = None
        
        # La regeneración del documento se hará después al final de __init__
        print("DEBUG: Todos los datos cargados")
    
    def _schedule_preview_update(self):
        """Programa una actualización de la vista previa cuando cambien los datos"""
        # Llamar directamente al método que actualiza la preview
        self._on_document_change()
    
    def _regenerate_document(self):
        """Regenera el documento completo en el editor desde los datos actuales"""
        if not hasattr(self, 'document_editor'):
            return
        
        # Obtener datos actuales
        client_name = self.client_search_var.get().strip() or "Cliente"
        client_address = ""
        client_dni = ""
        
        if hasattr(self, 'selected_client') and self.selected_client:
            try:
                client_address = self.selected_client['address'] or ''
            except (KeyError, IndexError, TypeError):
                client_address = ''
            
            try:
                client_dni = self.selected_client['dni'] or ''
            except (KeyError, IndexError, TypeError):
                client_dni = ''
        
        try:
            labor_cost = float(self.labor_entry.get())
        except:
            labor_cost = 0.0
        
        # Fecha actual en formato DD/MM/AA
        from datetime import datetime
        date_str = datetime.now().strftime('%d/%m/%y')
        
        # Calcular total
        subtotal = sum(item['price'] * item['quantity'] for item in self.items_data)
        total = subtotal + labor_cost
        
        # Generar el contenido del documento siguiendo el formato exacto de la plantilla
        # Datos del cliente alineados a la derecha
        doc_text = "\t\t\t\t\t\t" + client_name + "\n"
        if client_address:
            doc_text += "\t\t\t\t\t\t" + client_address + "\n"
        if client_dni:
            doc_text += "\t\t\t\t\t\tDNI/CIF: " + client_dni + "\n"
        
        doc_text += f"\nFecha: {date_str}\n\n"
        doc_text += "Muy Sr. Nuestro:\n\n"
        doc_text += "A continuación, detallamos desglose de presupuesto aproximado de trabajos a realizar en sus instalaciones\n\n"
        
        # Sección de materiales
        doc_text += "MATERIALES\n"
        if self.items_data:
            for item in self.items_data:
                # Solo mostrar nombre y cantidad, sin 'OBRA:' ni precio ni descripción
                doc_text += f"{item['name']}\n"
                doc_text += f"       Cantidad: {item['quantity']}\n"
        
        # Texto del total en negrita (el usuario puede editarlo)
        doc_text += "\nEl total de los trabajos presupuestados, incluyendo mano de obra, materiales, asciende a la cantidad de\n"
        
        # Total centrado (formato español)
        total_text = f"{format_price_es(total)} EUROS"
        doc_text += f"\t\t\t\t{total_text}\n\n"
        
        # IVA (mayúsculas y subrayado - el usuario puede aplicar formato)
        doc_text += "EL IVA SE INCREMENTARÁ EN LA FACTURA CORRESPONDIENTE\n\n"
        
        # Condiciones en mayúsculas
        doc_text += "LOS TRABAJOS NO PRESUPUESTADOS SE COBRARÍAN A 25€/HORA O SE PRESUPUESTARÍA EN CASO DE OBRA MAYOR\n\n"
        doc_text += "ESTE PRESUPUESTO TIENE UNA VALIDEZ DE 15 DÍAS\n\n"
        
        # Texto sobre permisos (normal)
        doc_text += "No se incluyen los permisos ni licencias que sean necesarios, los cuales se deberá contar con ellos al comienzo de los trabajos. No se incluyen proyectos o memorias técnicas si fueran necesarios.\n\n\n\n"
        
        # Firmas con separación correcta
        doc_text += "FIRMA DEL CONSTRUCTOR:                                        FIRMA DEL PROMOTOR:\n\n\n\n"
        doc_text += "_______________________                                       _______________________\n"
        doc_text += f"BARAJAS PEÑA S.L.                                             {client_name}\n"
        
        # Actualizar el editor
        self.document_editor.set_plain_text(doc_text)
        self.document_needs_save = True
    
    def _force_update_preview(self):
        """Fuerza actualización inmediata del documento"""
        self._regenerate_document()
    
    def _on_document_change(self):
        """Se llama cuando cambian los datos del presupuesto"""
        self.document_needs_save = True
    
    def _save(self):
        """Valida y guarda el presupuesto"""
        # Validar cliente
        client_name = self.client_search_var.get().strip()
        if not client_name:
            show_error('Error', 'Selecciona un cliente', self)
            self.client_entry.focus()
            return
        
        # Validar items
        if not self.items_data:
            show_error('Error', 'Añade al menos un item', self)
            return
        
        # Usar el cliente seleccionado si existe, sino buscar por nombre
        client = self.selected_client
        if not client:
            # Buscar por nombre escrito
            for c in self.clients_list:
                if c['name'].lower() == client_name.lower():
                    client = c
                    break
        
        if client:
            client_id = client['id']
            client_address = client['address']
            client_dni = client['dni']
        else:
            # Cliente no encontrado, usar el nombre tal cual
            client_id = None
            client_address = ''
            client_dni = ''
        
        # Validar mano de obra
        try:
            labor_cost = float(self.labor_entry.get())
            if labor_cost < 0:
                raise ValueError()
        except ValueError:
            show_error('Error', 'Mano de obra inválida', self)
            self.labor_entry.focus()
            return
        
        # Obtener nombre de obra
        work_name = self.work_name_entry.get().strip() or None
        
        # Obtener el documento completo del editor WYSIWYG
        notes = None
        formatted_notes = None
        if hasattr(self, 'document_editor'):
            # Guardar el documento completo tal como está en el editor
            formatted_notes = self.document_editor.get_plain_text()
            notes = formatted_notes  # notes se usa para búsquedas simples
        
        try:
            # Crear o actualizar presupuesto
            if self.quote_id:
                # Actualizar presupuesto existente
                db.update_quote(
                    self.quote_id, client_id, client_name, 
                    client_address, client_dni, work_name=work_name, 
                    labor_cost=labor_cost, notes=notes, formatted_notes=formatted_notes
                )
                # Eliminar items antiguos y añadir nuevos
                quote, old_items = db.get_quote(self.quote_id)
                for old_item in old_items:
                    db.delete_quote_item(old_item['id'])
                quote_id = self.quote_id
            else:
                # Crear nuevo presupuesto
                quote_id = db.create_quote(
                    client_id, client_name, client_address, 
                    client_dni, work_name=work_name, labor_cost=labor_cost,
                    notes=notes, formatted_notes=formatted_notes
                )
            
            # Añadir items y actualizar precios en BD si han cambiado
            for item in self.items_data:
                # Obtener precio de proveedor (items_data es dict, sí tiene .get())
                supplier_price = item.get('supplier_price', 0) or 0
                
                db.add_quote_item(
                    quote_id, item['material_id'], item['name'],
                    item['description'], item['image_path'],
                    item['price'], item['quantity'], supplier_price
                )
                
                # Actualizar precio del material en BD si ha cambiado
                if item['material_id']:
                    original_price = item.get('original_price', item['price'])
                    if item['price'] != original_price:
                        # Obtener material actual de la BD
                        material = db.get_material(item['material_id'])
                        if material:
                            # Actualizar solo el precio de venta, manteniendo otros campos
                            try:
                                material_supplier_price = material['supplier_price'] or 0
                            except (KeyError, IndexError):
                                material_supplier_price = 0
                            db.update_material(
                                item['material_id'],
                                material['name'],
                                material['description'],
                                material['image_path'],
                                item['price'],  # Nuevo precio de venta
                                material['category'],
                                material_supplier_price  # Mantener precio de proveedor
                            )
            
            action = 'actualizado' if self.quote_id else 'creado'
            
            # Callback de actualización
            if self.on_save:
                self.on_save()
            
            # Cerrar la ventana primero
            self.destroy()
            
            # Mostrar mensaje después de cerrar (se muestra en la ventana padre)
            # Necesitamos mantener una referencia al parent antes de destruir
            parent = self.master
            # Esperar a que se cierre la ventana
            parent.after(100, lambda: show_info('Éxito', f'Presupuesto #{quote_id} {action}', parent))
            
        except Exception as e:
            show_error('Error', f'Error al guardar: {str(e)}', self)


class WorkReportsListDialog(tk.Toplevel):
    """Diálogo para mostrar partes de obra de un presupuesto"""
    
    def __init__(self, parent, quote_id, reports):
        super().__init__(parent)
        self.quote_id = quote_id
        self.reports = reports
        
        self.title('Partes de Obra del Presupuesto')
        self.geometry('600x400')
        center_window(self, 600, 400)
        
        self._setup_ui()
        
        # Modal
        self.transient(parent)
        self.grab_set()
    
    def _setup_ui(self):
        """Configura la interfaz"""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text='Partes de Obra Asociados', 
                 font=('Helvetica', 12, 'bold')).pack(pady=(0, 10))
        
        # Tabla de partes
        columns = ('id', 'work_name', 'date')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=12)
        
        tree.heading('id', text='ID', anchor='w')
        tree.heading('work_name', text='Nombre', anchor='w')
        tree.heading('date', text='Fecha', anchor='w')
        
        tree.column('id', width=50, anchor='w')
        tree.column('work_name', width=300, anchor='w')
        tree.column('date', width=150, anchor='w')
        
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Cargar partes
        for report in self.reports:
            tree.insert('', 'end', values=(
                report['id'],
                report['work_name'],
                report['date_created']
            ))
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        create_styled_button(
            btn_frame, 'Cerrar', self.destroy, 'secondary'
        ).pack(side='right', padx=5)
