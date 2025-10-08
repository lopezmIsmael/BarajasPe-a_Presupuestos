"""
Gestión de trabajadores
"""
import tkinter as tk
from tkinter import ttk
from src.database import db
from src.ui.ui_utils import (
    center_window, create_styled_button, create_search_frame,
    create_treeview_with_scrollbar, show_info, show_error, 
    show_warning, ask_yes_no
)


class WorkersFrame(ttk.Frame):
    """Frame para gestión de trabajadores"""
    
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
        
        # Tabla de trabajadores
        columns = ('id', 'name', 'phone', 'role')
        headings = ('ID', 'Nombre', 'Teléfono', 'Rol')
        column_widths = (50, 250, 150, 150)
        
        tree_frame, self.tree = create_treeview_with_scrollbar(
            self, columns, headings, column_widths
        )
        
        # Doble click para editar
        self.tree.bind('<Double-Button-1>', lambda e: self.edit_worker())
        
        # Botones de acción
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        create_styled_button(
            btn_frame, '+ Nuevo Trabajador', self.new_worker, 'success'
        ).pack(side='left', padx=5)
        
        create_styled_button(
            btn_frame, '✏️ Editar', self.edit_worker, 'primary'
        ).pack(side='left', padx=5)
        
        create_styled_button(
            btn_frame, '🗑️ Eliminar', self.delete_worker, 'danger'
        ).pack(side='left', padx=5)
    
    def refresh(self):
        """Actualiza la lista de trabajadores"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar trabajadores
        workers = db.list_workers()
        search_term = self.search_var.get().lower()
        
        # Configurar tags para filas alternadas
        self.tree.tag_configure('oddrow', background='#FFFFFF')
        self.tree.tag_configure('evenrow', background='#F0F4F8')
        
        row_count = 0
        for worker in workers:
            # Filtro de búsqueda
            if search_term:
                name = worker['name'] or ''
                if search_term not in name.lower():
                    continue
            
            tag = 'evenrow' if row_count % 2 == 0 else 'oddrow'
            
            self.tree.insert('', 'end', iid=str(worker['id']), values=(
                worker['id'],
                worker['name'],
                worker['phone'] or '',
                worker['role']
            ), tags=(tag,))
            
            row_count += 1
    
    def new_worker(self):
        """Abre el diálogo para crear trabajador"""
        WorkerEditor(self, worker_id=None, on_save=self.refresh)
    
    def edit_worker(self):
        """Edita el trabajador seleccionado"""
        selection = self.tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un trabajador', self)
            return
        
        worker_id = int(selection[0])
        WorkerEditor(self, worker_id=worker_id, on_save=self.refresh)
    
    def delete_worker(self):
        """Elimina el trabajador seleccionado"""
        selection = self.tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un trabajador', self)
            return
        
        worker_id = int(selection[0])
        worker = db.get_worker(worker_id)
        
        if ask_yes_no('Confirmar', f'¿Eliminar trabajador "{worker["name"]}"?', self):
            db.delete_worker(worker_id)
            self.refresh()
            show_info('Éxito', 'Trabajador eliminado', self)


class WorkerEditor(tk.Toplevel):
    """Editor de trabajadores"""
    
    def __init__(self, parent, worker_id=None, on_save=None):
        super().__init__(parent)
        self.worker_id = worker_id
        self.on_save = on_save
        
        self.title('Editar Trabajador' if worker_id else 'Nuevo Trabajador')
        self.geometry('400x250')
        center_window(self, 400, 250)
        
        self._setup_ui()
        self._load_data()
        
        # Modal
        self.transient(parent)
        self.grab_set()
    
    def _setup_ui(self):
        """Configura la interfaz"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Nombre
        ttk.Label(main_frame, text='Nombre:', font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5
        )
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Teléfono
        ttk.Label(main_frame, text='Teléfono:', font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=5
        )
        self.phone_entry = ttk.Entry(main_frame, width=40)
        self.phone_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Rol (entrada manual)
        ttk.Label(main_frame, text='Rol:', font=('Helvetica', 10, 'bold')).grid(
            row=2, column=0, sticky='w', pady=5
        )
        self.role_entry = ttk.Entry(main_frame, width=40)
        self.role_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        self.role_entry.insert(0, 'Oficial')
        
        # Sugerencias de roles comunes
        ttk.Label(main_frame, text='(Ej: Oficial, Ayudante, Encargado, etc.)', 
                 font=('Helvetica', 8), foreground='gray').grid(
            row=3, column=1, sticky='w', padx=(10, 0)
        )
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        create_styled_button(
            btn_frame, 'Cancelar', self.destroy, 'secondary'
        ).pack(side='left', padx=5)
        
        create_styled_button(
            btn_frame, '💾 Guardar', self._save, 'success'
        ).pack(side='left', padx=5)
    
    def _load_data(self):
        """Carga datos del trabajador si se está editando"""
        if self.worker_id:
            worker = db.get_worker(self.worker_id)
            if worker:
                self.name_entry.insert(0, worker['name'])
                self.phone_entry.insert(0, worker['phone'] or '')
                self.role_entry.delete(0, tk.END)
                self.role_entry.insert(0, worker['role'])
    
    def _save(self):
        """Guarda el trabajador"""
        name = self.name_entry.get().strip()
        if not name:
            show_error('Error', 'El nombre es obligatorio', self)
            return
        
        phone = self.phone_entry.get().strip()
        role = self.role_entry.get().strip() or 'Oficial'
        
        try:
            if self.worker_id:
                db.update_worker(self.worker_id, name, phone, role)
                show_info('Éxito', 'Trabajador actualizado', self)
            else:
                db.add_worker(name, phone, role)
                show_info('Éxito', 'Trabajador creado', self)
            
            if self.on_save:
                self.on_save()
            
            self.destroy()
        except Exception as e:
            show_error('Error', f'Error al guardar: {e}', self)
