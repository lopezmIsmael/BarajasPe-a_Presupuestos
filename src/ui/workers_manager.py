"""
Gestión de trabajadores - Refactorizado con clases base
"""
import tkinter as tk
from tkinter import ttk
from src.database import db
from src.ui.ui_utils import (
    BaseCRUDFrame, BaseEditor,
    show_info, show_error, show_warning, ask_yes_no
)


class WorkersFrame(BaseCRUDFrame):
    """Frame para gestión de trabajadores"""

    def get_columns(self):
        return ('id', 'name', 'phone', 'role')

    def get_headings(self):
        return ('ID', 'Nombre', 'Teléfono', 'Rol')

    def get_column_widths(self):
        return (50, 250, 150, 150)

    def get_buttons_config(self):
        return [
            ('+ Nuevo Trabajador', self.add, 'success'),
            ('✏️ Editar', self.edit, 'primary'),
            ('🗑️ Eliminar', self.delete, 'danger')
        ]

    def refresh(self):
        """Actualiza la lista de trabajadores"""
        workers = db.list_workers()

        def filter_func(worker, search_term):
            if not search_term:
                return True
            # sqlite3.Row - acceso directo
            try:
                name = worker['name'] or ''
            except (KeyError, TypeError):
                return False
            return search_term in name.lower()

        def format_func(worker):
            return (
                worker['id'],
                worker['name'],
                worker['phone'] or '',
                worker['role'] if 'role' in worker.keys() else 'Oficial'
            )

        self._refresh_tree_with_data(workers, filter_func, format_func)

    def add(self):
        """Abre el diálogo para crear trabajador"""
        WorkerEditor(self, worker_id=None, on_save=self.refresh)

    def edit(self):
        """Edita el trabajador seleccionado"""
        selection = self.tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un trabajador', self)
            return

        worker_id = int(selection[0])
        WorkerEditor(self, worker_id=worker_id, on_save=self.refresh)

    def delete(self):
        """Elimina el trabajador seleccionado"""
        selection = self.tree.selection()
        if not selection:
            show_warning('Advertencia', 'Selecciona un trabajador', self)
            return

        worker_id = int(selection[0])
        worker = db.get_worker(worker_id)

        if not worker:
            show_error('Error', 'El trabajador no existe', self)
            return

        if ask_yes_no('Confirmar', f'¿Eliminar trabajador "{worker["name"]}"?', self):
            try:
                db.delete_worker(worker_id)
                self.refresh()
                show_info('Éxito', 'Trabajador eliminado', self)
            except Exception as e:
                show_error('Error', f'Error al eliminar: {e}', self)


class WorkerEditor(BaseEditor):
    """Editor de trabajadores"""

    def __init__(self, parent, worker_id=None, on_save=None):
        # Establecer atributos ANTES de llamar a super().__init__()
        self.worker_id = worker_id

        super().__init__(
            parent,
            item_id=worker_id,
            on_save=on_save,
            title='Editar Trabajador' if worker_id else 'Nuevo Trabajador',
            width=400,
            height=250
        )

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

        # Rol
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

        # Botones estándar
        self._create_buttons_frame()

    def _load_data(self):
        """Carga datos del trabajador si se está editando"""
        if self.worker_id:
            worker = db.get_worker(self.worker_id)
            if worker:
                self.name_entry.insert(0, worker['name'])
                self.phone_entry.insert(0, worker.get('phone') or '')
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
