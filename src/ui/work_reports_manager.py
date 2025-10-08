"""
Gestión de partes de obra
"""
import tkinter as tk
from tkinter import ttk, simpledialog
from src.database import db
from src.ui.ui_utils import (
    center_window, create_styled_button, create_search_frame,
    create_treeview_with_scrollbar, show_info, show_error,
    show_warning, ask_yes_no
)
from datetime import datetime


class WorkReportsFrame(ttk.Frame):
    """Frame para gestión de partes de obra"""
    
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        """Configura la interfaz"""
        # Barra de búsqueda
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh())
        search_frame, search_entry = create_search_frame(self, self.search_var)
        
        # Tabla de partes
        columns = ('id', 'work_name', 'client', 'date', 'quote_id')
        headings = ('#', 'Obra', 'Cliente', 'Fecha', 'Presupuesto')
        column_widths = (50, 250, 200, 100, 100)
        
        tree_frame, self.tree = create_treeview_with_scrollbar(
            self, columns, headings, column_widths
        )
        
        # Doble click para editar
        self.tree.bind('<Double-Button-1>', lambda e: self.edit_report())
        
        # Botones de acción
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        create_styled_button(
            btn_frame, '+ Nuevo Parte', self.new_report, 'success'
        ).pack(side='left', padx=5)
        
        create_styled_button(
            btn_frame, '✏️ Editar', self.edit_report, 'primary'
        ).pack(side='left', padx=5)
        
        create_styled_button(
            btn_frame, '🗑️ Eliminar', self.delete_report, 'danger'
        ).pack(side='left', padx=5)
        
        create_styled_button(
            btn_frame, '📄 Exportar PDF', self.export_pdf, 'info'
        ).pack(side='left', padx=5)
    
    def refresh(self):
        """Actualiza la lista de partes"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar partes
        reports = db.list_work_reports()
        search_term = self.search_var.get().lower()
        
        # Configurar tags para filas alternadas
        self.tree.tag_configure('oddrow', background='#FFFFFF')
        self.tree.tag_configure('evenrow', background='#F0F4F8')
        
        row_count = 0
        for report in reports:
            # Filtro de búsqueda
            if search_term:
                work_name = report['work_name'] or ''
                client_name = report['client_name'] or ''
                if search_term not in work_name.lower() and search_term not in client_name.lower():
                    continue
            
            tag = 'evenrow' if row_count % 2 == 0 else 'oddrow'
            quote_text = f"#{report['quote_id']}" if report['quote_id'] else 'Sin presup.'
            
            self.tree.insert('', 'end', iid=str(report['id']), values=(
                report['id'],
                report['work_name'],
                report['client_name'] or '',
                report['date_created'],
                quote_text
            ), tags=(tag,))
            
            row_count += 1
    
    def new_report(self):
        """Abre el diálogo para crear parte"""
        WorkReportEditor(self, report_id=None, on_save=self.refresh)
    
    def edit_report(self):
        """Edita el parte seleccionado"""
        selection = self.tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un parte', self)
            return
        
        report_id = int(selection[0])
        WorkReportEditor(self, report_id=report_id, on_save=self.refresh)
    
    def delete_report(self):
        """Elimina el parte seleccionado"""
        selection = self.tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un parte', self)
            return
        
        report_id = int(selection[0])
        report = db.get_work_report(report_id)
        
        if ask_yes_no('Confirmar', f'¿Eliminar parte "{report["work_name"]}"?', self):
            db.delete_work_report(report_id)
            self.refresh()
            show_info('Éxito', 'Parte eliminado', self)
    
    def export_pdf(self):
        """Exporta el parte a PDF"""
        selection = self.tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un parte', self)
            return
        
        report_id = int(selection[0])
        # TODO: Implementar exportación PDF
        show_info('Info', 'Exportación PDF pendiente de implementar', self)


class WorkReportEditor(tk.Toplevel):
    """Editor de partes de obra"""
    
    def __init__(self, parent, report_id=None, quote_id=None, on_save=None):
        super().__init__(parent)
        self.report_id = report_id
        self.quote_id = quote_id
        self.on_save = on_save
        
        self.title('Editar Parte de Obra' if report_id else 'Nuevo Parte de Obra')
        self.geometry('1200x700')
        center_window(self, 1200, 700)
        
        self._setup_ui()
        self._load_data()
        
        # Modal
        self.transient(parent)
        self.grab_set()
    
    def _setup_ui(self):
        """Configura la interfaz"""
        # Panel principal con scroll
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True)
        
        # Datos básicos del parte
        header_frame = ttk.LabelFrame(main_container, text='Datos del Parte', padding=10)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        # Nombre de obra
        ttk.Label(header_frame, text='Nombre de Obra:', font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5
        )
        self.work_name_entry = ttk.Entry(header_frame, width=40)
        self.work_name_entry.grid(row=0, column=1, pady=5, padx=(10, 20), sticky='w')
        
        # Cliente
        ttk.Label(header_frame, text='Cliente:', font=('Helvetica', 10, 'bold')).grid(
            row=0, column=2, sticky='w', pady=5
        )
        self.client_entry = ttk.Entry(header_frame, width=40)
        self.client_entry.grid(row=0, column=3, pady=5, padx=(10, 0), sticky='w')
        
        # Tabla de horas por trabajador/fecha
        hours_frame = ttk.LabelFrame(main_container, text='Horas de Trabajo', padding=10)
        hours_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self._create_hours_section(hours_frame)
        
        # Materiales
        materials_frame = ttk.LabelFrame(main_container, text='Materiales', padding=10)
        materials_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self._create_materials_section(materials_frame)
        
        # Botones inferiores
        btn_frame = ttk.Frame(main_container)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        create_styled_button(
            btn_frame, 'Cancelar', self.destroy, 'secondary'
        ).pack(side='left', padx=5)
        
        create_styled_button(
            btn_frame, '💾 Guardar Parte', self._save, 'success'
        ).pack(side='right', padx=5)
    
    def _create_hours_section(self, parent):
        """Crea la sección de horas"""
        # Botones de acción
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', pady=(0, 10))
        
        create_styled_button(
            btn_frame, '+ Añadir Fecha', self._add_date_column, 'success'
        ).pack(side='left', padx=5)
        
        create_styled_button(
            btn_frame, '+ Añadir Trabajador', self._add_worker_row, 'primary'
        ).pack(side='left', padx=5)
        
        # Contenedor con scroll para la tabla
        canvas_container = ttk.Frame(parent)
        canvas_container.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(canvas_container, height=300)
        scrollbar_x = ttk.Scrollbar(canvas_container, orient='horizontal', command=canvas.xview)
        scrollbar_y = ttk.Scrollbar(canvas_container, orient='vertical', command=canvas.yview)
        
        self.hours_table_frame = ttk.Frame(canvas)
        
        canvas.create_window((0, 0), window=self.hours_table_frame, anchor='nw')
        canvas.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')
        
        self.hours_canvas = canvas
        
        # Inicializar estructura de datos
        self.dates = []  # Lista de fechas (strings)
        self.workers_hours = {}  # {worker_id: {date: hours}}
        
        # Bind para actualizar scroll region
        self.hours_table_frame.bind('<Configure>', 
                                   lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        self._render_hours_table()
    
    def _create_materials_section(self, parent):
        """Crea la sección de materiales con selector como en presupuestos"""
        # Dividir en dos partes: búsqueda/lista y tabla de añadidos
        left_frame = ttk.Frame(parent)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(parent)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Panel izquierdo: Búsqueda y lista de materiales
        ttk.Label(left_frame, text='Buscar material:', font=('Helvetica', 9, 'bold')).pack(anchor='w')
        
        self.mat_search_var = tk.StringVar()
        self.mat_search_var.trace('w', lambda *args: self._filter_materials_list())
        search_entry = ttk.Entry(left_frame, textvariable=self.mat_search_var)
        search_entry.pack(fill='x', pady=(5, 10))
        
        results_frame = ttk.Frame(left_frame)
        results_frame.pack(fill='both', expand=True)
        
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
        
        # Botón añadir
        create_styled_button(
            left_frame, '+ Añadir Seleccionado', self._add_selected_material, 'success'
        ).pack(fill='x', pady=(10, 0))
        
        # Cargar materiales
        self.materials_list = db.list_materials()
        self.filtered_materials = []
        self._filter_materials_list()
        
        # Panel derecho: Materiales añadidos
        ttk.Label(right_frame, text='Materiales añadidos:', font=('Helvetica', 9, 'bold')).pack(anchor='w')
        
        # Botón quitar
        create_styled_button(
            right_frame, '🗑️ Quitar Seleccionado', self._remove_material, 'danger'
        ).pack(fill='x', pady=(5, 10))
        
        # Tabla de materiales añadidos
        columns = ('name', 'quantity')
        self.materials_tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=8)
        
        self.materials_tree.heading('name', text='Material', anchor='w')
        self.materials_tree.heading('quantity', text='Cantidad', anchor='center')
        
        self.materials_tree.column('name', width=300, anchor='w')
        self.materials_tree.column('quantity', width=100, anchor='center')
        
        # Doble click para editar cantidad
        self.materials_tree.bind('<Double-Button-1>', lambda e: self._edit_material_quantity())
        
        scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=self.materials_tree.yview)
        self.materials_tree.configure(yscrollcommand=scrollbar.set)
        
        self.materials_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.materials_data = []  # Lista de {material_id, name, quantity}
    
    def _filter_materials_list(self):
        """Filtra la lista de materiales"""
        self.mat_listbox.delete(0, tk.END)
        self.filtered_materials = []
        
        query = self.mat_search_var.get().lower().strip()
        
        if not query:
            # Mostrar por categorías
            materials_by_cat = {}
            for material in self.materials_list:
                category = material['category'] or 'Sin categoría'
                if category not in materials_by_cat:
                    materials_by_cat[category] = []
                materials_by_cat[category].append(material)
            
            for category in sorted(materials_by_cat.keys()):
                self.mat_listbox.insert(tk.END, f"━━ {category} ━━")
                self.filtered_materials.append(None)  # Separador
                
                for material in sorted(materials_by_cat[category], key=lambda x: x['name']):
                    display = f"  {material['name']}"
                    self.mat_listbox.insert(tk.END, display)
                    self.filtered_materials.append(material)
        else:
            # Búsqueda
            for material in self.materials_list:
                if query in material['name'].lower():
                    category = material['category'] or 'Sin categoría'
                    display = f"{material['name']} [{category}]"
                    self.mat_listbox.insert(tk.END, display)
                    self.filtered_materials.append(material)
    
    def _add_selected_material(self):
        """Añade el material seleccionado"""
        selection = self.mat_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        material = self.filtered_materials[idx]
        
        if material is None:  # Es un separador
            return
        
        # Pedir cantidad
        quantity = simpledialog.askfloat('Cantidad', f'Cantidad de {material["name"]}:', 
                                        initialvalue=1.0)
        if quantity is None or quantity <= 0:
            return
        
        self.materials_data.append({
            'material_id': material['id'],
            'name': material['name'],
            'quantity': quantity
        })
        self._refresh_materials()
    
    def _edit_material_quantity(self):
        """Edita la cantidad de un material"""
        selection = self.materials_tree.selection()
        if not selection:
            return
        
        idx = int(selection[0])
        material = self.materials_data[idx]
        
        new_quantity = simpledialog.askfloat('Editar Cantidad', 
                                            f'Nueva cantidad de {material["name"]}:',
                                            initialvalue=material['quantity'])
        if new_quantity and new_quantity > 0:
            self.materials_data[idx]['quantity'] = new_quantity
            self._refresh_materials()
    
    def _render_hours_table(self):
        """Renderiza la tabla de horas"""
        # Limpiar tabla
        for widget in self.hours_table_frame.winfo_children():
            widget.destroy()
        
        # Encabezado: Trabajador | Fecha1 | Fecha2 | ... | TOTAL
        ttk.Label(self.hours_table_frame, text='Trabajador', font=('Helvetica', 10, 'bold'),
                 relief='solid', borderwidth=1, width=20).grid(row=0, column=0, sticky='ew')
        
        for col_idx, date in enumerate(self.dates, start=1):
            ttk.Label(self.hours_table_frame, text=date, font=('Helvetica', 10, 'bold'),
                     relief='solid', borderwidth=1, width=12).grid(row=0, column=col_idx, sticky='ew')
        
        ttk.Label(self.hours_table_frame, text='TOTAL', font=('Helvetica', 10, 'bold'),
                 relief='solid', borderwidth=1, width=10).grid(row=0, column=len(self.dates)+1, sticky='ew')
        
        # Filas de trabajadores
        workers = db.list_workers()
        for row_idx, worker in enumerate(workers, start=1):
            worker_id = worker['id']
            
            # Nombre trabajador
            ttk.Label(self.hours_table_frame, text=f"{worker['name']} ({worker['role']})",
                     relief='solid', borderwidth=1).grid(row=row_idx, column=0, sticky='ew')
            
            # Celdas de horas por fecha
            total_hours = 0
            for col_idx, date in enumerate(self.dates, start=1):
                if worker_id not in self.workers_hours:
                    self.workers_hours[worker_id] = {}
                
                hours = self.workers_hours[worker_id].get(date, 0)
                total_hours += hours
                
                entry = ttk.Entry(self.hours_table_frame, width=10, justify='center')
                entry.insert(0, str(hours) if hours else '')
                entry.grid(row=row_idx, column=col_idx, padx=1, pady=1)
                
                # Bind para actualizar
                entry.bind('<FocusOut>', lambda e, wid=worker_id, d=date: self._update_hours(wid, d, e.widget.get()))
            
            # Total de horas
            ttk.Label(self.hours_table_frame, text=f"{total_hours:.1f}",
                     relief='solid', borderwidth=1, font=('Helvetica', 10, 'bold')).grid(
                         row=row_idx, column=len(self.dates)+1, sticky='ew')
    
    def _add_date_column(self):
        """Añade una columna de fecha"""
        date_str = simpledialog.askstring('Nueva Fecha', 'Fecha (DD/MM/YYYY):')
        if date_str:
            # Validar formato
            try:
                datetime.strptime(date_str, '%d/%m/%Y')
                if date_str not in self.dates:
                    self.dates.append(date_str)
                    self._render_hours_table()
            except ValueError:
                show_error('Error', 'Formato de fecha inválido. Use DD/MM/YYYY', self)
    
    def _add_worker_row(self):
        """Añade un trabajador (abre el gestor de trabajadores)"""
        show_info('Info', 'Use la sección de Trabajadores para añadir nuevos trabajadores.\n'
                          'Los trabajadores ya existentes aparecen automáticamente aquí.', self)
    
    def _update_hours(self, worker_id, date, value):
        """Actualiza las horas de un trabajador en una fecha"""
        try:
            hours = float(value) if value.strip() else 0
            if worker_id not in self.workers_hours:
                self.workers_hours[worker_id] = {}
            self.workers_hours[worker_id][date] = hours
            self._render_hours_table()
        except ValueError:
            pass
    
    def _remove_material(self):
        """Quita un material"""
        selection = self.materials_tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un material', self)
            return
        
        idx = int(selection[0])
        del self.materials_data[idx]
        self._refresh_materials()
    
    def _refresh_materials(self):
        """Actualiza la tabla de materiales"""
        self.materials_tree.delete(*self.materials_tree.get_children())
        
        for idx, mat in enumerate(self.materials_data):
            self.materials_tree.insert('', 'end', iid=str(idx), values=(
                mat['name'],
                mat['quantity']
            ))
    
    def _load_data(self):
        """Carga datos del parte si se está editando"""
        if self.report_id:
            report = db.get_work_report(self.report_id)
            if report:
                self.work_name_entry.insert(0, report['work_name'])
                self.client_entry.insert(0, report['client_name'] or '')
                
                # Cargar horas
                hours = db.list_work_hours(self.report_id)
                for hour in hours:
                    date = hour['date']
                    if date not in self.dates:
                        self.dates.append(date)
                    
                    worker_id = hour['worker_id']
                    if worker_id not in self.workers_hours:
                        self.workers_hours[worker_id] = {}
                    self.workers_hours[worker_id][date] = hour['hours']
                
                # Cargar materiales
                materials = db.list_work_materials(self.report_id)
                for mat in materials:
                    self.materials_data.append({
                        'material_id': mat['material_id'],
                        'name': mat['name'],
                        'quantity': mat['quantity']
                    })
                
                self._render_hours_table()
                self._refresh_materials()
        
        elif self.quote_id:
            # Si viene de un presupuesto, cargar datos automáticamente
            quote, items = db.get_quote(self.quote_id)
            if quote:
                try:
                    work_name = quote['work_name'] or 'Obra'
                except (KeyError, IndexError):
                    work_name = 'Obra'
                
                self.work_name_entry.insert(0, work_name)
                self.client_entry.insert(0, quote['client_name'] or '')
                
                # Cargar materiales del presupuesto
                for item in items:
                    self.materials_data.append({
                        'material_id': item['material_id'],
                        'name': item['name'],
                        'quantity': item['quantity']
                    })
                
                self._refresh_materials()
    
    def _save(self):
        """Guarda el parte"""
        work_name = self.work_name_entry.get().strip()
        if not work_name:
            show_error('Error', 'El nombre de obra es obligatorio', self)
            return
        
        client_name = self.client_entry.get().strip()
        
        try:
            if self.report_id:
                # Actualizar parte existente
                db.update_work_report(self.report_id, work_name, client_name, '')
                report_id = self.report_id
                
                # Eliminar horas y materiales antiguos para reemplazar
                conn = db.get_conn()
                cur = conn.cursor()
                cur.execute('DELETE FROM work_report_hours WHERE report_id=?', (report_id,))
                cur.execute('DELETE FROM work_report_materials WHERE report_id=?', (report_id,))
                conn.commit()
                conn.close()
            else:
                # Crear nuevo parte
                report_id = db.add_work_report(self.quote_id, work_name, client_name)
            
            # Guardar horas
            for worker_id, dates_hours in self.workers_hours.items():
                for date, hours in dates_hours.items():
                    if hours > 0:
                        db.add_work_hour(report_id, worker_id, date, hours)
            
            # Guardar materiales
            for mat in self.materials_data:
                db.add_work_material(report_id, mat['material_id'], mat['name'], mat['quantity'])
            
            show_info('Éxito', 'Parte guardado correctamente', self)
            
            if self.on_save:
                self.on_save()
            
            self.destroy()
        
        except Exception as e:
            show_error('Error', f'Error al guardar: {e}', self)
