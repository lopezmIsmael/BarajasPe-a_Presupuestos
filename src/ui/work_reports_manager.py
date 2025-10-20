"""
Gestión de partes de obra
"""
import tkinter as tk
from tkinter import ttk, simpledialog
from src.database import db, quotes as db_quotes
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
        WorkReportEditor(self, on_save=lambda: self.refresh())
    
    def edit_report(self):
        """Edita el parte seleccionado"""
        selection = self.tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un parte', self)
            return
        
        report_id = int(selection[0])
        WorkReportEditor(self, report_id=report_id, on_save=lambda: self.refresh())
    
    def delete_report(self):
        """Elimina el parte seleccionado"""
        selection = self.tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un parte', self)
            return
        
        report_id = int(selection[0])
        report = db.get_work_report(report_id)
        
        if not report:
            show_error('Error', 'El parte no existe', self)
            return
        
        if not ask_yes_no('Confirmar', '¿Eliminar este parte?', self):
            return
        
        try:
            db.delete_work_report(report_id)
            self.refresh()
            show_info('Éxito', 'Parte eliminado', self)
        except Exception as e:
            show_error('Error', f'Error al eliminar: {e}', self)
    
    def export_pdf(self):
        """Exporta a PDF el parte seleccionado"""
        from tkinter import filedialog
        from src.pdf.generator import export_work_report_to_pdf

        selection = self.tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un parte', self)
            return

        report_id = int(selection[0])
        report = db.get_work_report(report_id)

        if not report:
            show_error('Error', 'El parte no existe', self)
            return

        # Diálogo para guardar archivo
        filename = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF', '*.pdf')],
            initialfile=f"parte_obra_{report['work_name'].replace(' ', '_')}.pdf"
        )

        if filename:
            try:
                export_work_report_to_pdf(report_id, filename)
                show_info('Éxito', f'PDF exportado a:\n{filename}', self)
            except Exception as e:
                show_error('Error', f'Error al exportar PDF:\n{e}', self)


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
    
    def _remove_material(self):
        """Elimina el material seleccionado"""
        selection = self.materials_tree.selection()
        if not selection:
            return
        
        idx = int(selection[0])
        if 0 <= idx < len(self.materials_data):
            del self.materials_data[idx]
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
    
    def _refresh_materials(self):
        """Actualiza la tabla de materiales"""
        self.materials_tree.delete(*self.materials_tree.get_children())
        
        for idx, mat in enumerate(self.materials_data):
            self.materials_tree.insert('', 'end', iid=str(idx), values=(
                mat['name'],
                mat['quantity']
            ))
    
    def _render_hours_table(self):
        """Renderiza la tabla de horas"""
        # Limpiar tabla
        for widget in self.hours_table_frame.winfo_children():
            widget.destroy()
        
        # Si no hay fechas o trabajadores, mostrar mensaje
        if not self.dates and not self.workers_hours:
            ttk.Label(self.hours_table_frame, text='Sin datos. Añade fechas y trabajadores.').pack()
            return
        
        # Ordenar fechas y obtener lista de trabajadores
        self.dates.sort()
        workers = sorted(self.workers_hours.keys())
        
        # Crear header con fechas
        ttk.Label(self.hours_table_frame, text='Trabajador', width=30).grid(
            row=0, column=0, sticky='ew', padx=5, pady=5
        )
        
        for col, date in enumerate(self.dates, start=1):
            ttk.Label(self.hours_table_frame, text=date).grid(
                row=0, column=col, sticky='ew', padx=5, pady=5
            )
        
        # Añadir filas de trabajadores
        for row, worker_id in enumerate(workers, start=1):
            worker = db.get_worker(worker_id)
            if not worker:
                continue
            
            worker_name = worker['name']
            ttk.Label(self.hours_table_frame, text=worker_name).grid(
                row=row, column=0, sticky='w', padx=5, pady=5
            )
            
            # Celdas de horas
            for col, date in enumerate(self.dates, start=1):
                hours = self.workers_hours.get(worker_id, {}).get(date, 0)
                cell = ttk.Entry(self.hours_table_frame, width=5)
                cell.insert(0, str(hours))
                cell.grid(row=row, column=col, padx=5, pady=5)
                
                # Bind para actualizar horas al cambiar
                cell.bind('<FocusOut>', lambda e, w=worker_id, d=date, c=cell:
                         self._update_hours(w, d, c))
                cell.bind('<Return>', lambda e, w=worker_id, d=date, c=cell:
                         self._update_hours(w, d, c))
    
    def _update_hours(self, worker_id, date, cell):
        """Actualiza las horas de un trabajador en una fecha"""
        try:
            hours = float(cell.get())
            if hours < 0:
                raise ValueError
        except ValueError:
            cell.delete(0, tk.END)
            cell.insert(0, '0')
            hours = 0
        
        if worker_id not in self.workers_hours:
            self.workers_hours[worker_id] = {}
        self.workers_hours[worker_id][date] = hours
    
    def _add_date_column(self):
        """Añade una nueva fecha"""
        # Seleccionar fecha (podríamos usar un calendar widget mejor)
        new_date = datetime.today().strftime('%Y-%m-%d')
        
        if new_date in self.dates:
            show_warning('Advertencia', 'Esta fecha ya está añadida', self)
            return
        
        self.dates.append(new_date)
        self._render_hours_table()
    
    def _add_worker_row(self):
        """Añade un nuevo trabajador"""
        # Mostrar diálogo de selección de trabajador
        workers = db.list_workers()
        
        # Filtrar trabajadores ya añadidos
        available_workers = [w for w in workers if w['id'] not in self.workers_hours]
        
        if not available_workers:
            show_warning('Advertencia', 'No hay más trabajadores disponibles', self)
            return
        
        # Crear ventana de selección
        dialog = tk.Toplevel(self)
        dialog.title('Seleccionar Trabajador')
        dialog.geometry('300x400')
        center_window(dialog, 300, 400)
        dialog.transient(self)
        dialog.grab_set()
        
        # Lista de trabajadores
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        listbox.pack(fill='both', expand=True, pady=(0, 10))
        scrollbar.config(command=listbox.yview)
        
        for worker in available_workers:
            listbox.insert(tk.END, worker['name'])
        
        def on_select():
            selection = listbox.curselection()
            if not selection:
                return
            
            worker = available_workers[selection[0]]
            self.workers_hours[worker['id']] = {}
            self._render_hours_table()
            dialog.destroy()
        
        ttk.Button(frame, text='Seleccionar', command=on_select).pack(side='right', padx=5)
        ttk.Button(frame, text='Cancelar', command=dialog.destroy).pack(side='right')
    
    def _load_data(self):
        """Carga datos del parte si se está editando o datos del presupuesto si es nuevo"""
        # Inicializar/limpiar datos
        self.materials_data = []
        self.dates = []
        self.workers_hours = {}

        if self.report_id:
            # Cargar datos del parte existente
            report = db.get_work_report(self.report_id)
            if not report:
                return
            
            # Datos básicos
            self.work_name_entry.insert(0, report['work_name'])
            self.client_entry.insert(0, report['client_name'] or '')
            
            # Cargar horas desde work_report_assignments
            if 'workers' in report:
                for worker_id, worker_data in report['workers'].items():
                    self.workers_hours[worker_id] = {}
                    for assignment in worker_data['assignments']:
                        date = assignment['date']
                        if date not in self.dates:
                            self.dates.append(date)
                        self.workers_hours[worker_id][date] = assignment['hours']

            # Cargar materiales desde work_report_materials
            if 'materials' in report:
                for date, materials in report['materials'].items():
                    for mat in materials:
                        self.materials_data.append({
                            'material_id': mat['id'],
                            'name': mat['name'],
                            'quantity': mat['quantity']
                        })
        
        elif self.quote_id:
            # Cargar datos del presupuesto
            quote, quote_items = db_quotes.get_quote(self.quote_id)
            if not quote:
                return
            
            # Datos básicos
            self.work_name_entry.insert(0, quote['work_name'])
            self.client_entry.insert(0, quote['client_name'] or '')
            
            # Cargar materiales del presupuesto
            for item in quote_items:
                self.materials_data.append({
                    'material_id': item['material_id'],
                    'name': item['name'],
                    'quantity': item['quantity']
                })
        
        # Actualizar las vistas
        self._render_hours_table()
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
                db.update_work_report(
                    self.report_id,
                    work_name=work_name,
                    client_name=client_name
                )
                report_id = self.report_id

                # Eliminar asignaciones y materiales antiguos para reemplazar
                conn = db.get_conn()
                cur = conn.cursor()
                cur.execute('DELETE FROM work_report_assignments WHERE report_id=?', (report_id,))
                cur.execute('DELETE FROM work_report_materials WHERE report_id=?', (report_id,))
                conn.commit()
                conn.close()
            else:
                # Crear nuevo parte (usar fecha de hoy si no hay fechas)
                today = datetime.today().strftime('%Y-%m-%d')
                date_start = min(self.dates) if self.dates else today
                date_end = max(self.dates) if self.dates else today

                report_id = db.add_work_report(
                    work_name=work_name,
                    date_start=date_start,
                    date_end=date_end,
                    client_name=client_name,
                    quote_id=self.quote_id
                )

            # Guardar asignaciones de trabajo
            for worker_id, dates_hours in self.workers_hours.items():
                for date, hours in dates_hours.items():
                    if hours > 0:
                        db.add_work_assignment(
                            report_id=report_id,
                            worker_id=worker_id,
                            date=date,
                            hours=hours
                        )

            # Guardar materiales (usar primera fecha o hoy)
            today = datetime.today().strftime('%Y-%m-%d')
            material_date = self.dates[0] if self.dates else today

            for mat in self.materials_data:
                db.add_work_material(
                    report_id=report_id,
                    date=material_date,
                    material_id=mat['material_id'],
                    material_name=mat['name'],
                    quantity=mat['quantity']
                )
            
            show_info('Éxito', 'Parte guardado correctamente', self)
            
            if self.on_save:
                self.on_save()
            
            self.destroy()
        
        except Exception as e:
            show_error('Error', f'Error al guardar: {e}', self)