"""
Gestión de clientes - Interface y lógica
"""
import tkinter as tk
from tkinter import ttk, messagebox
from src.database import db
from src.config.settings import CLIENT_EDITOR_SIZE
from src.ui.ui_utils import (
    center_window, create_styled_button, create_search_frame,
    create_treeview_with_scrollbar, create_button_frame,
    create_form_field, bind_keyboard_shortcuts
)


class ClientsFrame(ttk.Frame):
    """Frame principal para la gestión de clientes"""
    
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
        
        # Tabla de clientes
        columns = ('name', 'address', 'dni', 'phone')
        headings = ('Nombre', 'Dirección', 'DNI', 'Teléfono')
        column_widths = (200, 250, 120, 120)
        
        tree_frame, self.tree = create_treeview_with_scrollbar(
            self, columns, headings, column_widths
        )
        
        # Doble click para editar
        self.tree.bind('<Double-Button-1>', lambda e: self.edit())
        
        # Botones de acción
        buttons_config = [
            ('➕ Añadir', self.add, 'success'),
            ('✏️ Editar', self.edit, 'info'),
            ('🗑️ Borrar', self.delete, 'danger')
        ]
        
        btn_frame, self.buttons = create_button_frame(self, buttons_config)
    
    def refresh(self):
        """Actualiza la lista de clientes"""
        # Limpiar items existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrar clientes
        search_term = self.search_var.get().lower()
        clients = db.list_clients()
        
        row_count = 0
        for client in clients:
            # Aplicar filtro de búsqueda
            if search_term:
                name = client['name'].lower()
                address = (client['address'] or '').lower()
                dni = (client['dni'] or '').lower()
                if search_term not in name and search_term not in address and search_term not in dni:
                    continue
            
            # Alternar colores de filas
            tag = 'evenrow' if row_count % 2 == 0 else 'oddrow'
            
            # Añadir item al árbol
            self.tree.insert('', 'end', iid=str(client['id']), values=(
                client['name'],
                client['address'] or '',
                client['dni'] or '',
                client['phone'] or ''
            ), tags=(tag,))
            
            row_count += 1
    
    def add(self):
        """Abre el editor para añadir un nuevo cliente"""
        ClientEditor(self, client_id=None, on_save=self.refresh)
    
    def edit(self):
        """Abre el editor para editar el cliente seleccionado"""
        selected = self.tree.selection()
        if not selected:
            return
        
        client_id = int(selected[0])
        ClientEditor(self, client_id=client_id, on_save=self.refresh)
    
    def delete(self):
        """Elimina el cliente seleccionado"""
        selected = self.tree.selection()
        if not selected:
            return
        
        client_id = int(selected[0])
        if messagebox.askyesno('Confirmar', '¿Borrar este cliente?'):
            db.delete_client(client_id)
            self.refresh()


class ClientEditor(tk.Toplevel):
    """Editor de clientes - Ventana modal"""
    
    def __init__(self, master, client_id=None, on_save=None):
        super().__init__(master)
        self.client_id = client_id
        self.on_save = on_save
        
        self._setup_window()
        self._setup_ui()
        self._load_data()
        self._setup_keyboard_shortcuts()
    
    def _setup_window(self):
        """Configura la ventana"""
        title = 'Editar Cliente' if self.client_id else 'Nuevo Cliente'
        self.title(title)
        
        width, height = map(int, CLIENT_EDITOR_SIZE.split('x'))
        center_window(self, width, height)
        
        # Configurar tamaño mínimo (90% del tamaño original)
        self.minsize(int(width * 0.9), int(height * 0.9))
        
        # Hacer la ventana redimensionable
        self.resizable(True, True)
        
        # Modal
        self.transient(self.master)
        self.grab_set()
    
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
        
        # Frame de botones
        self._setup_buttons()
    
    def _setup_buttons(self):
        """Configura los botones de acción"""
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill='x', side='bottom')
        
        save_btn = create_styled_button(
            btn_frame, '💾 Guardar', self._save, 'success'
        )
        save_btn.pack(side='right', padx=5)
        
        cancel_btn = create_styled_button(
            btn_frame, '❌ Cancelar', self.destroy, 'secondary'
        )
        cancel_btn.pack(side='right', padx=5)
    
    def _setup_keyboard_shortcuts(self):
        """Configura los atajos de teclado"""
        shortcuts = {
            '<Return>': self._save,
            '<Escape>': self.destroy
        }
        bind_keyboard_shortcuts(self, shortcuts)
    
    def _load_data(self):
        """Carga los datos del cliente si está editando"""
        if not self.client_id:
            return
        
        client = db.get_client(self.client_id)
        if not client:
            return
        
        # Cargar datos en los campos
        for field_key, entry in self.entries.items():
            value = client[field_key]
            if value:
                entry.insert(0, value)
    
    def _save(self):
        """Valida y guarda el cliente"""
        # Validar nombre
        name = self.entries['name'].get().strip()
        if not name:
            messagebox.showerror('Error', 'El nombre es obligatorio')
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
            else:
                db.add_client(name, address, dni, phone, email)
            
            # Callback de actualización
            if self.on_save:
                self.on_save()
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror('Error', f'Error al guardar: {str(e)}')