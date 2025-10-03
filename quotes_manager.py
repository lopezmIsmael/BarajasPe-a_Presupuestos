"""
Gestión de presupuestos - Interface y lógica
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import db
from pdf_generator import export_quote_to_pdf
from config import QUOTE_EDITOR_SIZE, QUOTE_VIEWER_SIZE, PDF_FILETYPES
from ui_utils import (
    center_window, create_styled_button, create_search_frame,
    create_treeview_with_scrollbar, create_button_frame,
    bind_keyboard_shortcuts
)
from materials_manager import MaterialEditor
from clients_manager import ClientEditor


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
        columns = ('id', 'date', 'client', 'total')
        headings = ('#', 'Fecha', 'Cliente', 'Total (€)')
        column_widths = (60, 120, 250, 120)
        
        tree_frame, self.tree = create_treeview_with_scrollbar(
            self, columns, headings, column_widths
        )
        
        # Doble click para exportar PDF
        self.tree.bind('<Double-Button-1>', lambda e: self.export_pdf())
        
        # Botones de acción
        buttons_config = [
            ('➕ Nuevo Presupuesto', self.new_quote, 'success'),
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
        
        for quote in quotes:
            # Aplicar filtro de búsqueda
            if search_term:
                client_name = quote['client_name'] or ''
                if search_term not in client_name.lower():
                    continue
            
            # Calcular total
            _, items = db.get_quote(quote['id'])
            total = sum(item['unit_price'] * item['quantity'] for item in items)
            total += quote['labor_cost'] or 0
            
            # Añadir item al árbol
            self.tree.insert('', 'end', iid=str(quote['id']), values=(
                quote['id'],
                quote['date'],
                quote['client_name'] or '',
                f"{total:.2f}"
            ))
    
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
        
        # Configurar treeview para items
        columns = ('name', 'qty', 'price', 'total')
        tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=10)
        
        tree.heading('name', text='Material')
        tree.heading('qty', text='Cantidad')
        tree.heading('price', text='Precio Unit.')
        tree.heading('total', text='Total')
        
        tree.pack(fill='both', expand=True)
        
        # Cargar items
        for item in items:
            line_total = item['unit_price'] * item['quantity']
            tree.insert('', 'end', values=(
                item['name'],
                item['quantity'],
                f"{item['unit_price']:.2f} €",
                f"{line_total:.2f} €"
            ))
    
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
        # Panel izquierdo - Cliente y configuración
        self._create_left_panel()
        
        # Panel derecho - Items del presupuesto
        self._create_right_panel()
        
        # Botones principales
        self._create_bottom_buttons()
    
    def _create_left_panel(self):
        """Crea el panel izquierdo con cliente y búsqueda de materiales"""
        left_panel = ttk.Frame(self, padding=15)
        left_panel.pack(side='left', fill='y')
        
        # Sección cliente
        self._create_client_section(left_panel)
        
        # Separador
        ttk.Separator(left_panel, orient='horizontal').pack(fill='x', pady=15)
        
        # Sección mano de obra
        self._create_labor_section(left_panel)
        
        # Separador
        ttk.Separator(left_panel, orient='horizontal').pack(fill='x', pady=15)
        
        # Sección búsqueda de materiales
        self._create_material_search_section(left_panel)
    
    def _create_client_section(self, parent):
        """Crea la sección de selección de cliente"""
        ttk.Label(parent, text='Cliente', font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0,5))
        
        client_frame = ttk.Frame(parent)
        client_frame.pack(fill='x', pady=5)
        
        # Cargar lista de clientes
        self.clients_list = db.list_clients()
        client_names = [c['name'] for c in self.clients_list]
        
        self.client_cb = ttk.Combobox(client_frame, values=client_names, width=25)
        self.client_cb.pack(side='top', fill='x')
        
        # Botón para añadir nuevo cliente
        new_client_btn = create_styled_button(
            client_frame, '➕ Nuevo cliente', self._quick_add_client, 'success'
        )
        new_client_btn.pack(fill='x', pady=5)
    
    def _create_labor_section(self, parent):
        """Crea la sección de mano de obra"""
        ttk.Label(parent, text='Mano de obra (€)', font=('Helvetica', 11, 'bold')).pack(anchor='w')
        
        self.labor_entry = ttk.Entry(parent, width=15, font=('Helvetica', 12))
        self.labor_entry.insert(0, '0')
        self.labor_entry.pack(anchor='w', pady=5)
        
        # Actualizar totales cuando cambie
        self.labor_entry.bind('<KeyRelease>', lambda e: self._update_totals())
    
    def _create_material_search_section(self, parent):
        """Crea la sección de búsqueda y adición de materiales"""
        ttk.Label(parent, text='Buscar y añadir material', 
                 font=('Helvetica', 11, 'bold')).pack(anchor='w', pady=(0,5))
        
        # Campo de búsqueda
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill='x', pady=5)
        
        self.mat_search_var = tk.StringVar()
        self.mat_search_var.trace('w', lambda *args: self._filter_materials())
        
        search_entry = ttk.Entry(search_frame, textvariable=self.mat_search_var, 
                                font=('Helvetica', 10))
        search_entry.pack(fill='x')
        
        ttk.Label(search_frame, text='🔍 Escribe para buscar...', 
                 font=('Helvetica', 8)).pack(anchor='w')
        
        # Lista de resultados
        self._create_material_results_list(parent)
        
        # Botones de acción
        self._create_material_action_buttons(parent)
    
    def _create_material_results_list(self, parent):
        """Crea la lista de resultados de materiales"""
        results_frame = ttk.Frame(parent)
        results_frame.pack(fill='both', expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.mat_listbox = tk.Listbox(
            results_frame, height=12, yscrollcommand=scrollbar.set,
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
        btn_frame.pack(fill='x', pady=5)
        
        add_btn = create_styled_button(
            btn_frame, '➕ Añadir', self._add_selected_material, 'success'
        )
        add_btn.pack(side='left', fill='x', expand=True, padx=2)
        
        new_btn = create_styled_button(
            btn_frame, '📦 Nuevo', self._quick_add_material, 'primary'
        )
        new_btn.pack(side='right', fill='x', expand=True, padx=2)
    
    def _create_right_panel(self):
        """Crea el panel derecho con la lista de items"""
        right_panel = ttk.Frame(self, padding=15)
        right_panel.pack(side='right', fill='both', expand=True)
        
        ttk.Label(right_panel, text='Items del presupuesto', 
                 font=('Helvetica', 12, 'bold')).pack(anchor='w', pady=(0,10))
        
        # Tabla de items
        columns = ('name', 'price', 'qty', 'total')
        self.items_tree = ttk.Treeview(right_panel, columns=columns, show='headings', height=15)
        
        self.items_tree.heading('name', text='Material')
        self.items_tree.heading('price', text='Precio')
        self.items_tree.heading('qty', text='Cantidad')
        self.items_tree.heading('total', text='Total')
        
        self.items_tree.column('name', width=250)
        self.items_tree.column('price', width=80)
        self.items_tree.column('qty', width=80)
        self.items_tree.column('total', width=100)
        
        self.items_tree.pack(fill='both', expand=True, pady=(0,10))
        
        # Doble click para editar
        self.items_tree.bind('<Double-Button-1>', lambda e: self._edit_item())
        
        # Botones de items
        item_btns = ttk.Frame(right_panel)
        item_btns.pack(fill='x', pady=(0, 10))
        
        edit_btn = create_styled_button(item_btns, '✏️ Editar', self._edit_item, 'info')
        edit_btn.pack(side='left', padx=5)
        
        remove_btn = create_styled_button(item_btns, '🗑️ Quitar', self._remove_item, 'danger')
        remove_btn.pack(side='left', padx=5)
        
        # Resumen de totales
        totals_frame = ttk.LabelFrame(right_panel, text='Resumen', padding=10)
        totals_frame.pack(fill='x', pady=10)
        
        self.total_label = ttk.Label(totals_frame, text='Total: 0.00 €', 
                                   font=('Helvetica', 14, 'bold'))
        self.total_label.pack()
    
    def _create_bottom_buttons(self):
        """Crea los botones principales de la ventana"""
        bottom_frame = ttk.Frame(self, padding=15)
        bottom_frame.pack(side='bottom', fill='x')
        
        # Botón cancelar (izquierda)
        cancel_btn = create_styled_button(
            bottom_frame, '❌ Cancelar', self.destroy, 'secondary'
        )
        cancel_btn.pack(side='left', padx=5)
        
        # Botón guardar (derecha, prominente)
        save_btn = create_styled_button(
            bottom_frame, '💾 GUARDAR PRESUPUESTO', self._save, 'success'
        )
        save_btn.pack(side='right', padx=5, ipadx=20, ipady=10)
        
        # Texto de ayuda
        help_text = '(Ctrl+S para guardar | Esc para cancelar)'
        ttk.Label(bottom_frame, text=help_text, font=('Helvetica', 8), 
                 foreground='gray').pack(side='right', padx=10)
    
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
        """Recarga la lista de clientes"""
        self.clients_list = db.list_clients()
        self.client_cb['values'] = [c['name'] for c in self.clients_list]
    
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
                display = f"{material['name']} [{category}] - {material['price']:.2f}€"
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
        
        # Diálogo para cantidad
        qty = simpledialog.askfloat(
            'Cantidad', f'Cantidad de {material["name"]}:',
            initialvalue=1.0, minvalue=0.01
        )
        if qty is None:
            return
        
        # Añadir a la lista de items
        self.items_data.append({
            'material_id': material['id'],
            'name': material['name'],
            'description': material['description'],
            'image_path': material['image_path'],
            'price': material['price'],
            'quantity': qty
        })
        
        self._refresh_items()
        self.mat_search_var.set('')  # Limpiar búsqueda
    
    def _refresh_items(self):
        """Actualiza la visualización de items"""
        # Limpiar items existentes
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Añadir items actuales
        for i, item in enumerate(self.items_data):
            total = item['price'] * item['quantity']
            self.items_tree.insert('', 'end', iid=str(i), values=(
                item['name'],
                f"{item['price']:.2f}",
                item['quantity'],
                f"{total:.2f}"
            ))
        
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
    
    def _edit_item(self):
        """Edita la cantidad del item seleccionado"""
        selected = self.items_tree.selection()
        if not selected:
            return
        
        idx = int(selected[0])
        item = self.items_data[idx]
        
        new_qty = simpledialog.askfloat(
            'Editar cantidad',
            f'Nueva cantidad para {item["name"]}:',
            initialvalue=item['quantity'],
            minvalue=0.01
        )
        
        if new_qty is not None:
            self.items_data[idx]['quantity'] = new_qty
            self._refresh_items()
    
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
            self.client_cb.set(quote['client_name'])
        
        if quote['labor_cost']:
            self.labor_entry.delete(0, tk.END)
            self.labor_entry.insert(0, str(quote['labor_cost']))
        
        # Cargar items
        for item in items:
            self.items_data.append({
                'material_id': item['material_id'],
                'name': item['name'],
                'description': item['description'],
                'image_path': item['image_path'],
                'price': item['unit_price'],
                'quantity': item['quantity']
            })
        
        self._refresh_items()
    
    def _save(self):
        """Valida y guarda el presupuesto"""
        # Validar cliente
        client_name = self.client_cb.get().strip()
        if not client_name:
            messagebox.showerror('Error', 'Selecciona un cliente')
            self.client_cb.focus()
            return
        
        # Validar items
        if not self.items_data:
            messagebox.showerror('Error', 'Añade al menos un item')
            return
        
        # Buscar información del cliente
        client = None
        for c in self.clients_list:
            if c['name'] == client_name:
                client = c
                break
        
        if client:
            client_id = client['id']
            client_address = client['address']
            client_dni = client['dni']
        else:
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
        
        try:
            # Crear o actualizar presupuesto
            if self.quote_id:
                # Actualizar presupuesto existente
                db.update_quote(
                    self.quote_id, client_id, client_name, 
                    client_address, client_dni, labor_cost=labor_cost
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
                    client_dni, labor_cost=labor_cost
                )
            
            # Añadir items
            for item in self.items_data:
                db.add_quote_item(
                    quote_id, item['material_id'], item['name'],
                    item['description'], item['image_path'],
                    item['price'], item['quantity']
                )
            
            action = 'actualizado' if self.quote_id else 'creado'
            messagebox.showinfo('Éxito', f'Presupuesto #{quote_id} {action}')
            
            # Callback de actualización
            if self.on_save:
                self.on_save()
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror('Error', f'Error al guardar: {str(e)}')