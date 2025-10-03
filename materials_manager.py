"""
Gestión de materiales - Interface y lógica
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import db
from config import MATERIAL_EDITOR_SIZE, IMAGE_FILETYPES
from ui_utils import (
    center_window, create_styled_button, create_search_frame, 
    create_treeview_with_scrollbar, create_button_frame, 
    create_form_field, bind_keyboard_shortcuts
)


class MaterialsFrame(ttk.Frame):
    """Frame principal para la gestión de materiales"""
    
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
        
        # Tabla de materiales
        columns = ('name', 'category', 'desc', 'price')
        headings = ('Nombre', 'Categoría', 'Descripción', 'Precio (€)')
        column_widths = (180, 120, 250, 100)
        
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
        """Actualiza la lista de materiales"""
        # Limpiar items existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrar materiales
        search_term = self.search_var.get().lower()
        materials = db.list_materials()
        
        for material in materials:
            category = material['category'] or 'Sin categoría'
            description = (material['description'] or '')[:50]
            
            # Aplicar filtro de búsqueda
            if search_term:
                if (search_term not in material['name'].lower() and
                    search_term not in description.lower() and
                    search_term not in category.lower()):
                    continue
            
            # Añadir item al árbol
            self.tree.insert('', 'end', iid=str(material['id']), values=(
                material['name'],
                category,
                description,
                f"{material['price']:.2f}"
            ))
    
    def add(self):
        """Abre el editor para añadir un nuevo material"""
        MaterialEditor(self, material_id=None, on_save=self.refresh)
    
    def edit(self):
        """Abre el editor para editar el material seleccionado"""
        selected = self.tree.selection()
        if not selected:
            return
        
        material_id = int(selected[0])
        MaterialEditor(self, material_id=material_id, on_save=self.refresh)
    
    def delete(self):
        """Elimina el material seleccionado"""
        selected = self.tree.selection()
        if not selected:
            return
        
        material_id = int(selected[0])
        if messagebox.askyesno('Confirmar', '¿Borrar este material?'):
            db.delete_material(material_id)
            self.refresh()


class MaterialEditor(tk.Toplevel):
    """Editor de materiales - Ventana modal"""
    
    def __init__(self, master, material_id=None, on_save=None):
        super().__init__(master)
        self.material_id = material_id
        self.on_save = on_save
        
        self._setup_window()
        self._setup_ui()
        self._load_data()
        self._setup_keyboard_shortcuts()
    
    def _setup_window(self):
        """Configura la ventana"""
        title = 'Editar Material' if self.material_id else 'Nuevo Material'
        self.title(title)
        
        width, height = map(int, MATERIAL_EDITOR_SIZE.split('x'))
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
        
        # Campos del formulario
        self.name_entry = create_form_field(
            form, 'Nombre *', 'entry', row=0, 
            width=40, font=('Helvetica', 11)
        )
        self.name_entry.focus()
        
        self.description_text = create_form_field(
            form, 'Descripción', 'text', row=1,
            height=5, width=40, font=('Helvetica', 10)
        )
        
        self.price_entry = create_form_field(
            form, 'Precio (€) *', 'entry', row=2,
            width=20, font=('Helvetica', 11)
        )
        
        # Campo de categoría con combobox editable
        self._setup_category_field(form)
        
        # Campo de imagen
        self._setup_image_field(form)
        
        form.columnconfigure(1, weight=1)
        
        # Frame de botones
        self._setup_buttons()
    
    def _setup_category_field(self, parent):
        """Configura el campo de categoría"""
        ttk.Label(parent, text='Categoría', font=('Helvetica', 10, 'bold')).grid(
            row=3, column=0, sticky='w', pady=5
        )
        
        cat_frame = ttk.Frame(parent)
        cat_frame.grid(row=3, column=1, pady=5, sticky='ew')
        
        # Obtener categorías existentes
        categories = db.get_categories() or ['Sin categoría']
        
        self.category_combo = ttk.Combobox(
            cat_frame, values=categories, width=37, 
            font=('Helvetica', 11), state='normal'
        )
        self.category_combo.pack(side='left', fill='x', expand=True)
        self.category_combo.set('Sin categoría')
        
        # Ícono informativo
        ttk.Label(cat_frame, text='💡', font=('Helvetica', 8)).pack(side='right', padx=2)
        
        # Texto de ayuda
        help_text = 'Escribe una nueva categoría o selecciona una existente'
        ttk.Label(parent, text=help_text, font=('Helvetica', 8), 
                 foreground='gray').grid(row=4, column=1, sticky='w')
    
    def _setup_image_field(self, parent):
        """Configura el campo de imagen"""
        ttk.Label(parent, text='Imagen', font=('Helvetica', 10, 'bold')).grid(
            row=5, column=0, sticky='w', pady=5
        )
        
        img_frame = ttk.Frame(parent)
        img_frame.grid(row=5, column=1, pady=5, sticky='ew')
        
        self.img_path_var = tk.StringVar()
        ttk.Entry(img_frame, textvariable=self.img_path_var, 
                 state='readonly').pack(side='left', fill='x', expand=True)
        
        ttk.Button(img_frame, text='📁', command=self._choose_image, 
                  width=3).pack(side='right', padx=5)
    
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
    
    def _choose_image(self):
        """Abre el diálogo para seleccionar una imagen"""
        file_path = filedialog.askopenfilename(filetypes=IMAGE_FILETYPES)
        if file_path:
            self.img_path_var.set(file_path)
    
    def _load_data(self):
        """Carga los datos del material si está editando"""
        if not self.material_id:
            return
        
        material = db.get_material(self.material_id)
        if not material:
            return
        
        # Cargar datos en los campos
        self.name_entry.insert(0, material['name'])
        
        if material['description']:
            self.description_text.insert('1.0', material['description'])
        
        self.price_entry.insert(0, str(material['price']))
        
        if material['category']:
            self.category_combo.set(material['category'])
        
        if material['image_path']:
            self.img_path_var.set(material['image_path'])
    
    def _save(self):
        """Valida y guarda el material"""
        # Validar nombre
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror('Error', 'El nombre es obligatorio')
            self.name_entry.focus()
            return
        
        # Obtener descripción
        description = self.description_text.get('1.0', 'end').strip()
        
        # Validar precio
        try:
            price = float(self.price_entry.get())
            if price < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror('Error', 'Precio inválido (debe ser ≥ 0)')
            self.price_entry.focus()
            return
        
        # Obtener datos adicionales
        image_path = self.img_path_var.get() or None
        category = self.category_combo.get().strip() or 'Sin categoría'
        
        # Guardar en base de datos
        try:
            if self.material_id:
                db.update_material(
                    self.material_id, name, description, 
                    image_path, price, category
                )
            else:
                db.add_material(name, description, image_path, price, category)
            
            # Callback de actualización
            if self.on_save:
                self.on_save()
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror('Error', f'Error al guardar: {str(e)}')