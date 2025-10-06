"""
Gestión de presupuestos - Interface y lógica
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import db
from pdf_generator import export_quote_to_pdf
from pdf_preview import generate_quote_preview
from config import QUOTE_EDITOR_SIZE, QUOTE_VIEWER_SIZE, PDF_FILETYPES
from ui_utils import (
    center_window, create_styled_button, create_search_frame,
    create_treeview_with_scrollbar, create_button_frame,
    bind_keyboard_shortcuts
)
from materials_manager import MaterialEditor
from clients_manager import ClientEditor
from PIL import Image, ImageTk
from datetime import datetime


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
                f"{total:.2f}"
            ), tags=(tag,))
            
            row_count += 1
    
    def new_quote(self):
        """Abre el editor para crear un nuevo presupuesto"""
        QuoteEditor(self, quote_id=None, on_save=self.refresh)
    
    def edit_quote(self):
        """Abre el editor para editar el presupuesto seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Atención', 'Selecciona un presupuesto para editar')
            return
        
        quote_id = int(selected[0])
        QuoteEditor(self, quote_id=quote_id, on_save=self.refresh)
    
    def delete_quote(self):
        """Elimina el presupuesto seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Atención', 'Selecciona un presupuesto para eliminar')
            return
        
        quote_id = int(selected[0])
        confirm_msg = f'¿Eliminar el presupuesto #{quote_id}?\\n\\nEsta acción no se puede deshacer.'
        
        if messagebox.askyesno('Confirmar', confirm_msg):
            try:
                db.delete_quote(quote_id)
                self.refresh()
                messagebox.showinfo('Éxito', 'Presupuesto eliminado correctamente')
            except Exception as e:
                messagebox.showerror('Error', f'Error al eliminar: {str(e)}')
    
    def export_pdf(self):
        """Exporta el presupuesto seleccionado a PDF"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Atención', 'Selecciona un presupuesto')
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
            export_quote_to_pdf(quote_id, file_path)
            messagebox.showinfo('Éxito', f'PDF exportado:\\n{file_path}')
        except Exception as e:
            messagebox.showerror('Error', f'Error al exportar: {str(e)}')
    
    def view_details(self):
        """Muestra los detalles del presupuesto seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Atención', 'Selecciona un presupuesto')
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
        
        # Configurar treeview para items con columnas de ambos precios
        columns = ('name', 'qty', 'supplier_price', 'price', 'total')
        tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=10)
        
        tree.heading('name', text='Material', anchor='w')
        tree.heading('qty', text='Cantidad', anchor='w')
        tree.heading('supplier_price', text='P. Proveedor', anchor='w')
        tree.heading('price', text='P. Venta', anchor='w')
        tree.heading('total', text='Total', anchor='w')
        
        tree.column('name', anchor='w')
        tree.column('qty', anchor='w')
        tree.column('supplier_price', anchor='w')
        tree.column('price', anchor='w')
        tree.column('total', anchor='w')
        
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
            
            tree.insert('', 'end', values=(
                item['name'],
                item['quantity'],
                f"{supplier_price:.2f}",
                f"{item['unit_price']:.2f}",
                f"{line_total:.2f}"
            ), tags=(tag,))
    
    def _create_totals_section(self, quote, items):
        """Crea la sección de totales"""
        totals_frame = ttk.Frame(self, padding=20)
        totals_frame.pack(fill='x')
        
        # Calcular totales
        subtotal = sum(item['unit_price'] * item['quantity'] for item in items)
        labor_cost = quote['labor_cost'] or 0
        total = subtotal + labor_cost
        
        # Mostrar totales
        ttk.Label(totals_frame, text=f"Subtotal materiales: {subtotal:.2f} €", 
                 font=('Helvetica', 11)).pack(anchor='e')
        ttk.Label(totals_frame, text=f"Mano de obra: {labor_cost:.2f} €", 
                 font=('Helvetica', 11)).pack(anchor='e')
        ttk.Label(totals_frame, text=f"TOTAL: {total:.2f} €", 
                 font=('Helvetica', 14, 'bold')).pack(anchor='e')


class QuoteEditor(tk.Toplevel):
    """Editor de presupuestos - Ventana modal"""
    
    def __init__(self, master, quote_id=None, on_save=None):
        super().__init__(master)
        self.quote_id = quote_id
        self.on_save = on_save
        self.items_data = []  # Lista de items del presupuesto
        self.preview_photo = None  # Para evitar garbage collection
        self.preview_update_job = None  # Para debouncing de updates
        
        self._setup_window()
        self._setup_ui()
        self._load_data()
        self._setup_keyboard_shortcuts()
    
    def _setup_window(self):
        """Configura la ventana"""
        title = 'Editar Presupuesto' if self.quote_id else 'Nuevo Presupuesto'
        self.title(title)
        
        # Configurar como modal primero
        self.transient(self.master)
        
        # Obtener tamaño y configurar ventana
        width, height = map(int, QUOTE_EDITOR_SIZE.split('x'))
        
        # Configurar tamaño mínimo (85% del tamaño original)
        self.minsize(int(width * 0.85), int(height * 0.85))
        
        # Hacer la ventana redimensionable
        self.resizable(True, True)
        
        # Centrar la ventana (esto debe ser lo último)
        center_window(self, width, height)
        
        # Establecer grab después de centrar
        self.grab_set()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Contenedor principal con grid
        main_container = ttk.Frame(self)
        main_container.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        
        # Configurar peso de filas y columnas para redimensionamiento
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=0)  # Panel izquierdo fijo
        main_container.grid_columnconfigure(1, weight=1)  # Panel centro expandible
        main_container.grid_columnconfigure(2, weight=0)  # Panel derecho preview fijo
        
        # Panel izquierdo - Cliente y configuración (más compacto)
        self._create_left_panel(main_container)
        
        # Panel centro - Items del presupuesto
        self._create_center_panel(main_container)
        
        # Panel derecho - Preview del PDF
        self._create_preview_panel(main_container)
        
        # Botones principales en la parte inferior
        self._create_bottom_buttons()
    
    def _create_left_panel(self, parent):
        """Crea el panel izquierdo con cliente y búsqueda de materiales"""
        left_panel = ttk.Frame(parent, padding=10)
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=10)
        
        # Configurar expansión de filas
        left_panel.grid_rowconfigure(3, weight=1)  # La sección de notas se expande
        left_panel.grid_rowconfigure(4, weight=1)  # La sección de materiales se expande
        
        # Sección cliente
        self._create_client_section(left_panel)
        
        # Sección nombre de obra
        self._create_work_name_section(left_panel)
        
        # Sección mano de obra
        self._create_labor_section(left_panel)
        
        # Sección notas
        self._create_notes_section(left_panel)
        
        # Sección búsqueda de materiales
        self._create_material_search_section(left_panel)
    
    def _create_client_section(self, parent):
        """Crea la sección de selección de cliente con búsqueda"""
        client_frame = ttk.LabelFrame(parent, text='Cliente', padding=10)
        client_frame.grid(row=0, column=0, sticky='ew', pady=(0, 8))
        
        # Cargar lista de clientes
        self.clients_list = db.list_clients()
        self.filtered_clients = self.clients_list.copy()
        self.selected_client = None
        
        # Campo de búsqueda de cliente
        self.client_search_var = tk.StringVar()
        self.client_search_var.trace('w', lambda *args: self._filter_clients())
        
        search_container = ttk.Frame(client_frame)
        search_container.pack(fill='x', pady=(0, 5))
        
        self.client_entry = ttk.Entry(search_container, textvariable=self.client_search_var, 
                                      font=('Helvetica', 10))
        self.client_entry.pack(fill='x')
        
        # Lista de resultados de clientes (más compacta)
        list_frame = ttk.Frame(client_frame)
        list_frame.pack(fill='both', expand=False, pady=(0, 5))
        
        self.client_listbox = tk.Listbox(list_frame, height=3, font=('Helvetica', 9))
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
        
        # Botón para añadir nuevo cliente (más compacto)
        new_client_btn = create_styled_button(
            client_frame, '+ Nuevo', self._quick_add_client, 'success'
        )
        new_client_btn.pack(fill='x')
    
    def _create_work_name_section(self, parent):
        """Crea la sección de nombre de obra"""
        work_frame = ttk.LabelFrame(parent, text='Nombre de Obra', padding=10)
        work_frame.grid(row=1, column=0, sticky='ew', pady=(0, 8))
        
        self.work_name_entry = ttk.Entry(work_frame, font=('Helvetica', 10))
        self.work_name_entry.pack(fill='x')
    
    def _create_labor_section(self, parent):
        """Crea la sección de mano de obra"""
        labor_frame = ttk.LabelFrame(parent, text='Mano de obra (€)', padding=10)
        labor_frame.grid(row=2, column=0, sticky='ew', pady=(0, 8))
        
        self.labor_entry = ttk.Entry(labor_frame, font=('Helvetica', 10))
        self.labor_entry.insert(0, '0')
        self.labor_entry.pack(fill='x')
        
        # Actualizar totales cuando cambie
        self.labor_entry.bind('<KeyRelease>', lambda e: self._update_totals())
    
    def _create_notes_section(self, parent):
        """Crea la sección de notas"""
        notes_frame = ttk.LabelFrame(parent, text='Notas / Observaciones', padding=10)
        notes_frame.grid(row=3, column=0, sticky='nsew', pady=(0, 8))
        
        # Configurar para que se expanda
        notes_frame.grid_rowconfigure(0, weight=1)
        notes_frame.grid_columnconfigure(0, weight=1)
        
        # Text widget para notas con scrollbar (más grande)
        text_container = ttk.Frame(notes_frame)
        text_container.grid(row=0, column=0, sticky='nsew')
        
        self.notes_text = tk.Text(text_container, height=8, width=35, 
                                  font=('Helvetica', 10), wrap='word')
        self.notes_text.pack(side='left', fill='both', expand=True)
        
        notes_scrollbar = ttk.Scrollbar(text_container, orient='vertical', 
                                       command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scrollbar.set)
        notes_scrollbar.pack(side='right', fill='y')
        
        # Actualizar preview cuando cambien las notas
        self.notes_text.bind('<KeyRelease>', lambda e: self._schedule_preview_update())
    
    def _create_material_search_section(self, parent):
        """Crea la sección de búsqueda y adición de materiales"""
        mat_frame = ttk.LabelFrame(parent, text='Buscar y añadir material', padding=10)
        mat_frame.grid(row=4, column=0, sticky='nsew', pady=(0, 0))
        
        # Configurar para que se expanda verticalmente
        parent.grid_rowconfigure(4, weight=1)
        
        # Campo de búsqueda
        self.mat_search_var = tk.StringVar()
        self.mat_search_var.trace('w', lambda *args: self._filter_materials())
        
        search_entry = ttk.Entry(mat_frame, textvariable=self.mat_search_var, 
                                font=('Helvetica', 10))
        search_entry.pack(fill='x', pady=(0, 5))
        
        # Lista de resultados (más compacta)
        self._create_material_results_list(mat_frame)
        
        # Botones de acción (más compactos)
        self._create_material_action_buttons(mat_frame)
    
    def _create_material_results_list(self, parent):
        """Crea la lista de resultados de materiales"""
        results_frame = ttk.Frame(parent)
        results_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.mat_listbox = tk.Listbox(
            results_frame, height=8, yscrollcommand=scrollbar.set,
            font=('Helvetica', 9)
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
        
        # Título
        title_label = ttk.Label(center_panel, text='Items del presupuesto', 
                 font=('Helvetica', 12, 'bold'))
        title_label.grid(row=0, column=0, sticky='w', pady=(0, 8))
        
        # Frame con borde visible para la tabla
        border_canvas = tk.Canvas(center_panel, highlightthickness=2,
                                 highlightbackground='#2B7DE9',
                                 highlightcolor='#2B7DE9',
                                 background='#FFFFFF')
        border_canvas.grid(row=1, column=0, sticky='nsew', pady=(0, 8))
        
        tree_container = ttk.Frame(border_canvas)
        tree_container.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Tabla de items con columnas de ambos precios
        columns = ('name', 'supplier_price', 'price', 'qty', 'total')
        self.items_tree = ttk.Treeview(tree_container, columns=columns, show='headings')
        
        self.items_tree.heading('name', text='Material', anchor='w')
        self.items_tree.heading('supplier_price', text='P. Proveedor', anchor='w')
        self.items_tree.heading('price', text='P. Venta', anchor='w')
        self.items_tree.heading('qty', text='Cantidad', anchor='w')
        self.items_tree.heading('total', text='Total', anchor='w')
        
        self.items_tree.column('name', width=200, anchor='w')
        self.items_tree.column('supplier_price', width=100, anchor='w')
        self.items_tree.column('price', width=80, anchor='w')
        self.items_tree.column('qty', width=80, anchor='w')
        self.items_tree.column('total', width=100, anchor='w')
        
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
        
        # Resumen de totales (más compacto)
        totals_frame = ttk.LabelFrame(center_panel, text='Resumen', padding=8)
        totals_frame.grid(row=3, column=0, sticky='ew')
        
        self.total_label = ttk.Label(totals_frame, text='Total: 0.00 €', 
                                   font=('Helvetica', 12, 'bold'))
        self.total_label.pack()
    
    def _create_preview_panel(self, parent):
        """Crea el panel derecho con la previsualización del PDF"""
        preview_panel = ttk.Frame(parent, padding=10)
        preview_panel.grid(row=0, column=2, sticky='nsew', padx=(5, 10), pady=10)
        
        # Configurar para que se expanda
        preview_panel.grid_rowconfigure(1, weight=1)
        preview_panel.grid_columnconfigure(0, weight=1)
        
        # Título
        title_label = ttk.Label(preview_panel, text='Vista Previa del PDF', 
                 font=('Helvetica', 12, 'bold'))
        title_label.grid(row=0, column=0, sticky='w', pady=(0, 8))
        
        # Frame con scroll para la imagen del PDF
        canvas_frame = ttk.Frame(preview_panel)
        canvas_frame.grid(row=1, column=0, sticky='nsew')
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas con scrollbars
        self.preview_canvas = tk.Canvas(canvas_frame, width=400, height=600, 
                                       bg='#E0E0E0', highlightthickness=1,
                                       highlightbackground='#2B7DE9')
        self.preview_canvas.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', 
                                   command=self.preview_canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal',
                                   command=self.preview_canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        self.preview_canvas.configure(yscrollcommand=v_scrollbar.set,
                                     xscrollcommand=h_scrollbar.set)
        
        # Botón para actualizar manualmente
        refresh_btn = create_styled_button(preview_panel, '🔄 Actualizar Vista Previa', 
                                          self._update_preview, 'primary')
        refresh_btn.grid(row=2, column=0, sticky='ew', pady=(8, 0))
    
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
        
        # Enfocar en el siguiente campo
        self.work_name_entry.focus()
    
    def _quick_add_material(self):
        """Abre el editor para añadir un nuevo material"""
        MaterialEditor(self, material_id=None, on_save=self._reload_materials)
    
    def _reload_materials(self):
        """Recarga la lista de materiales"""
        self.materials_list = db.list_materials()
        self._filter_materials()
    
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
                display = f"  {material['name']} - {material['price']:.2f}€"
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
                display = f"{material['name']} [{category}] - Prov: {supplier_price:.2f}€ | Venta: {material['price']:.2f}€"
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
            
            self.items_tree.insert('', 'end', iid=str(i), values=(
                item['name'],
                f"{supplier_price:.2f}",
                f"{item['price']:.2f}",
                item['quantity'],
                f"{total:.2f}"
            ), tags=(tag,))
        
        self._update_totals()
    
    def _update_totals(self):
        """Actualiza la visualización de totales"""
        subtotal = sum(item['price'] * item['quantity'] for item in self.items_data)
        
        try:
            labor_cost = float(self.labor_entry.get() or 0)
        except ValueError:
            labor_cost = 0
        
        total = subtotal + labor_cost
        
        self.total_label.config(
            text=f'Subtotal: {subtotal:.2f} € | Mano de obra: {labor_cost:.2f} € | TOTAL: {total:.2f} €'
        )
        
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
        
        # Solo permitir editar columnas de precio de venta y cantidad
        # #2=supplier_price (no editable aquí), #3=price (editable), #4=qty (editable)
        if column not in ('#3', '#4'):  
            return
        
        idx = int(row_id)
        item = self.items_data[idx]
        
        # Obtener el valor actual y el bbox de la celda
        col_name = 'price' if column == '#3' else 'quantity'
        current_value = item['price'] if column == '#3' else item['quantity']
        
        # Obtener posición de la celda
        bbox = self.items_tree.bbox(row_id, column)
        if not bbox:
            return
        
        # Crear Entry temporal sobre la celda
        x, y, width, height = bbox
        
        entry_var = tk.StringVar(value=str(current_value))
        # Usar tk.Entry en lugar de ttk.Entry para evitar problemas de visualización
        entry = tk.Entry(self.items_tree, textvariable=entry_var, 
                        font=('Segoe UI', 10), 
                        relief='solid',
                        borderwidth=2,
                        justify='center')
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus_set()
        entry.select_range(0, tk.END)
        entry.icursor(tk.END)  # Colocar cursor al final
        
        def save_edit(event=None):
            try:
                new_value = float(entry_var.get())
                if new_value < 0:
                    raise ValueError()
                
                if column == '#3':  # Precio de venta
                    self.items_data[idx]['price'] = new_value
                    # Actualizar precio original si no existía
                    if 'original_price' not in self.items_data[idx]:
                        self.items_data[idx]['original_price'] = item['price']
                else:  # Cantidad
                    if new_value == 0:
                        raise ValueError()
                    self.items_data[idx]['quantity'] = new_value
                
                self._refresh_items()
            except ValueError:
                messagebox.showerror('Error', 'Valor inválido')
            finally:
                entry.destroy()
        
        def cancel_edit(event=None):
            entry.destroy()
        
        entry.bind('<Return>', save_edit)
        entry.bind('<Escape>', cancel_edit)
        entry.bind('<FocusOut>', save_edit)
    
    def _edit_item(self):
        """Mensaje informativo para usar doble click"""
        messagebox.showinfo(
            'Editar items',
            'Para editar precio o cantidad, haz doble click directamente sobre el valor que quieres cambiar.'
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
        if not self.quote_id:
            return
        
        quote, items = db.get_quote(self.quote_id)
        if not quote:
            messagebox.showerror('Error', 'Presupuesto no encontrado')
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
        
        # Cargar notas
        if quote.get('notes'):
            self.notes_text.delete('1.0', tk.END)
            self.notes_text.insert('1.0', quote['notes'])
        
        # Cargar items
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
    
    def _schedule_preview_update(self):
        """Programa una actualización de la preview con debounce"""
        # Cancelar actualización pendiente
        if self.preview_update_job:
            self.after_cancel(self.preview_update_job)
        
        # Programar nueva actualización en 500ms
        self.preview_update_job = self.after(500, self._update_preview)
    
    def _update_preview(self):
        """Actualiza la vista previa del PDF"""
        try:
            # Obtener datos actuales
            client_name = self.client_search_var.get().strip() or "Cliente"
            client_address = ""
            client_dni = ""
            
            if self.selected_client:
                client_address = self.selected_client.get('address', '')
                client_dni = self.selected_client.get('dni', '')
            
            work_name = self.work_name_entry.get().strip()
            notes = self.notes_text.get('1.0', tk.END).strip()
            
            try:
                labor_cost = float(self.labor_entry.get())
            except:
                labor_cost = 0.0
            
            # Fecha actual
            date_str = datetime.now().strftime('%d de %B de %Y')
            
            # Generar preview
            preview_image = generate_quote_preview(
                client_name, client_address, client_dni, work_name,
                self.items_data, labor_cost, notes, date_str
            )
            
            if preview_image:
                # Redimensionar imagen para que quepa en el canvas
                canvas_width = 400
                img_width, img_height = preview_image.size
                scale = canvas_width / img_width
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                preview_image = preview_image.resize((new_width, new_height), Image.LANCZOS)
                
                # Convertir a PhotoImage
                self.preview_photo = ImageTk.PhotoImage(preview_image)
                
                # Limpiar canvas
                self.preview_canvas.delete('all')
                
                # Mostrar imagen
                self.preview_canvas.create_image(0, 0, anchor='nw', image=self.preview_photo)
                
                # Actualizar scrollregion
                self.preview_canvas.configure(scrollregion=(0, 0, new_width, new_height))
        
        except Exception as e:
            print(f"Error actualizando preview: {e}")
            import traceback
            traceback.print_exc()
    
    def _save(self):
        """Valida y guarda el presupuesto"""
        # Validar cliente
        client_name = self.client_search_var.get().strip()
        if not client_name:
            messagebox.showerror('Error', 'Selecciona un cliente')
            self.client_entry.focus()
            return
        
        # Validar items
        if not self.items_data:
            messagebox.showerror('Error', 'Añade al menos un item')
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
            messagebox.showerror('Error', 'Mano de obra inválida')
            self.labor_entry.focus()
            return
        
        # Obtener nombre de obra
        work_name = self.work_name_entry.get().strip() or None
        
        # Obtener notas
        notes = self.notes_text.get('1.0', tk.END).strip() or None
        
        try:
            # Crear o actualizar presupuesto
            if self.quote_id:
                # Actualizar presupuesto existente
                db.update_quote(
                    self.quote_id, client_id, client_name, 
                    client_address, client_dni, work_name=work_name, 
                    labor_cost=labor_cost, notes=notes
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
                    notes=notes
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
            messagebox.showinfo('Éxito', f'Presupuesto #{quote_id} {action}')
            
        except Exception as e:
            messagebox.showerror('Error', f'Error al guardar: {str(e)}')