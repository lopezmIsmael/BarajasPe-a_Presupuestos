"""
Gestión de clientes - Refactorizado con clases base
"""
import tkinter as tk
from tkinter import ttk
from src.database import db
from src.ui.ui_utils import (
    BaseCRUDFrame, BaseEditor,
    create_form_field, show_info, show_error, show_warning, ask_yes_no
)


class ClientsFrame(BaseCRUDFrame):
    """Frame principal para la gestión de clientes"""

    def get_columns(self):
        return ('name', 'address', 'dni', 'phone')

    def get_headings(self):
        return ('Nombre', 'Dirección', 'DNI', 'Teléfono')

    def get_column_widths(self):
        return (200, 250, 120, 120)

    def get_buttons_config(self):
        return [
            ('➕ Añadir', self.add, 'success'),
            ('✏️ Editar', self.edit, 'primary'),
            ('🗑️ Borrar', self.delete, 'danger')
        ]

    def refresh(self):
        """Actualiza la lista de clientes"""
        clients = db.list_clients()

        def filter_func(client, search_term):
            if not search_term:
                return True
            # sqlite3.Row - acceso directo
            try:
                name = (client['name'] or '').lower()
                address = (client['address'] or '').lower()
                dni = (client['dni'] or '').lower()
            except (KeyError, TypeError):
                return False
            return (search_term in name or
                   search_term in address or
                   search_term in dni)

        def format_func(client):
            return (
                client['name'],
                client['address'] or '',
                client['dni'] or '',
                client['phone'] or ''
            )

        self._refresh_tree_with_data(clients, filter_func, format_func)

    def add(self):
        """Abre el editor para añadir un nuevo cliente"""
        ClientEditor(self, client_id=None, on_save=self.refresh)

    def edit(self):
        """Abre el editor para editar el cliente seleccionado"""
        selected = self.tree.selection()
        if not selected:
            show_warning('Advertencia', 'Selecciona un cliente', self)
            return

        client_id = int(selected[0])
        ClientEditor(self, client_id=client_id, on_save=self.refresh)

    def delete(self):
        """Elimina el cliente seleccionado"""
        selected = self.tree.selection()
        if not selected:
            show_warning('Advertencia', 'Selecciona un cliente', self)
            return

        client_id = int(selected[0])
        if ask_yes_no('Confirmar', '¿Borrar este cliente?', self):
            try:
                db.delete_client(client_id)
                self.refresh()
                show_info('Éxito', 'Cliente eliminado', self)
            except Exception as e:
                show_error('Error', f'Error al eliminar: {e}', self)


class ClientEditor(BaseEditor):
    """Editor de clientes - Ventana modal"""

    def __init__(self, parent, client_id=None, on_save=None):
        # Establecer atributos ANTES de llamar a super().__init__()
        self.client_id = client_id

        super().__init__(
            parent,
            item_id=client_id,
            on_save=on_save,
            title='Editar Cliente' if client_id else 'Nuevo Cliente',
            width=500,
            height=350
        )

    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal del formulario
        form = ttk.Frame(self, padding=20)
        form.pack(fill='both', expand=True)

        # Definir campos del formulario
        fields = [
            ('Nombre *', 'name'),
            ('Dirección', 'address'),
            ('DNI', 'dni'),
            ('Teléfono', 'phone'),
            ('Email', 'email')
        ]

        # Crear campos
        self.entries = {}
        for i, (label_text, field_key) in enumerate(fields):
            entry = create_form_field(
                form, label_text, 'entry', row=i,
                width=40, font=('Helvetica', 11)
            )
            self.entries[field_key] = entry

        # Focus en el primer campo
        self.entries['name'].focus()

        form.columnconfigure(1, weight=1)

        # Botones estándar
        self._create_buttons_frame()

    def _load_data(self):
        """Carga los datos del cliente si está editando"""
        if not self.client_id:
            return

        client = db.get_client(self.client_id)
        if not client:
            return

        # Cargar datos en los campos
        for field_key, entry in self.entries.items():
            value = client.get(field_key)
            if value:
                entry.insert(0, value)

    def _save(self):
        """Valida y guarda el cliente"""
        # Validar nombre
        name = self.entries['name'].get().strip()
        if not name:
            show_error('Error', 'El nombre es obligatorio', self)
            self.entries['name'].focus()
            return

        # Obtener datos de los campos
        address = self.entries['address'].get().strip()
        dni = self.entries['dni'].get().strip()
        phone = self.entries['phone'].get().strip()
        email = self.entries['email'].get().strip()

        # Guardar en base de datos
        try:
            if self.client_id:
                db.update_client(
                    self.client_id, name, address, dni, phone, email
                )
                show_info('Éxito', 'Cliente actualizado', self)
            else:
                db.add_client(name, address, dni, phone, email)
                show_info('Éxito', 'Cliente creado', self)

            # Callback de actualización
            if self.on_save:
                self.on_save()

            self.destroy()

        except Exception as e:
            show_error('Error', f'Error al guardar: {e}', self)
