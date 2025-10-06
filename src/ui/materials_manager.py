"""
Gestión de materiales - Interface y lógica
"""
import tkinter as tk
from tkinter import ttk, messagebox
from src.database import db
from src.config.settings import MATERIAL_EDITOR_SIZE
from src.ui.ui_utils import (
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
        columns = ('name', 'category', 'desc', 'supplier_price', 'price')
        headings = ('Nombre', 'Categoría', 'Descripción', 'P. Proveedor (€)', 'P. Venta (€)')
        column_widths = (150, 100, 200, 120, 100)
        
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
        
        row_count = 0
        for material in materials:
            # Aplicar filtro de búsqueda
            if search_term:
                name = material['name'].lower()
                desc = (material['description'] or '').lower()
                category = (material['category'] or '').lower()
                if search_term not in name and search_term not in desc and search_term not in category:
                    continue
            
            # Alternar colores de filas
            tag = 'evenrow' if row_count % 2 == 0 else 'oddrow'
            
            # Obtener precio de proveedor
            try:
                supplier_price = material['supplier_price'] or 0
            except (KeyError, IndexError):
                supplier_price = 0
            
            # Añadir item al árbol
            self.tree.insert('', 'end', iid=str(material['id']), values=(
                material['name'],
                material['category'] or 'Sin categoría',
                material['description'] or '',
                f"{supplier_price:.2f}",
                f"{material['price']:.2f}"
            ), tags=(tag,))
            
            row_count += 1
    
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
        
        self.supplier_price_entry = create_form_field(
            form, 'Precio Proveedor (€)', 'entry', row=2,
            width=20, font=('Helvetica', 11)
        )
        self.supplier_price_entry.insert(0, '0')
        
        self.price_entry = create_form_field(
            form, 'Precio Venta (€) *', 'entry', row=3,
            width=20, font=('Helvetica', 11)
        )
        
        # Campo de categoría con combobox editable
        self._setup_category_field(form)
        
        form.columnconfigure(1, weight=1)
        
        # Frame de botones
        self._setup_buttons()
    
    def _setup_category_field(self, parent):
        """Configura el campo de categoría"""
        ttk.Label(parent, text='Categoría', font=('Helvetica', 10, 'bold')).grid(
            row=4, column=0, sticky='w', pady=5
        )
        
        cat_frame = ttk.Frame(parent)
        cat_frame.grid(row=4, column=1, pady=5, sticky='ew')
        
        # Obtener categorías existentes
        self.all_categories = db.get_categories() or ['Sin categoría']
        
        # Crear el Entry (en lugar de Combobox) para mejor control
        self.category_var = tk.StringVar()
        self.category_var.set('Sin categoría')
        
        self.category_entry = ttk.Entry(
            cat_frame, textvariable=self.category_var, width=37, 
            font=('Helvetica', 11)
        )
        self.category_entry.pack(side='left', fill='x', expand=True)
        
        # Bind para mostrar sugerencias
        self.category_entry.bind('<KeyRelease>', self._on_category_keyrelease)
        self.category_entry.bind('<FocusIn>', self._on_category_focus)
        self.category_entry.bind('<FocusOut>', self._on_category_focus_out)
        
        # Ícono informativo
        ttk.Label(cat_frame, text='💡', font=('Helvetica', 8)).pack(side='right', padx=2)
        
        # Crear listbox para sugerencias (inicialmente oculto)
        self.suggestions_listbox = None
        self.suggestions_window = None
        
        # Texto de ayuda
        help_text = 'Escribe una categoría (se sugerirán existentes)'
        ttk.Label(parent, text=help_text, font=('Helvetica', 8), 
                 foreground='gray').grid(row=5, column=1, sticky='w')
    
    def _on_category_keyrelease(self, event=None):
        """Maneja el evento de soltar tecla en el campo de categoría"""
        # Ignorar teclas especiales
        if event and event.keysym in ('Shift_L', 'Shift_R', 'Control_L', 'Control_R', 
                                       'Alt_L', 'Alt_R', 'Caps_Lock', 'Tab', 'Escape'):
            return
        
        # Si presiona Down, navegar en la lista de sugerencias
        if event and event.keysym == 'Down':
            if self.suggestions_listbox and self.suggestions_listbox.winfo_viewable():
                self.suggestions_listbox.focus_set()
                self.suggestions_listbox.selection_set(0)
            return
        
        # Si presiona Return, cerrar sugerencias
        if event and event.keysym in ('Return', 'KP_Enter'):
            self._hide_suggestions()
            return
        
        # Mostrar sugerencias filtradas
        self._show_filtered_suggestions()
    
    def _on_category_focus(self, event=None):
        """Muestra sugerencias cuando el campo recibe foco"""
        self._show_filtered_suggestions()
    
    def _on_category_focus_out(self, event=None):
        """Oculta sugerencias cuando el campo pierde foco"""
        # Usar after para dar tiempo a hacer clic en la lista
        self.after(200, self._hide_suggestions)
    
    def _show_filtered_suggestions(self):
        """Muestra las sugerencias filtradas"""
        typed = self.category_var.get().lower().strip()
        
        # Filtrar categorías
        if typed == '':
            filtered = self.all_categories
        else:
            filtered = [cat for cat in self.all_categories 
                       if typed in cat.lower()]
        
        # Si no hay sugerencias relevantes, no mostrar nada
        if not filtered or (len(filtered) == 1 and filtered[0].lower() == typed):
            self._hide_suggestions()
            return
        
        # Crear o actualizar el listbox de sugerencias
        if not self.suggestions_window:
            self._create_suggestions_window()
        
        # Limpiar y llenar con sugerencias
        self.suggestions_listbox.delete(0, tk.END)
        for cat in filtered[:10]:  # Máximo 10 sugerencias
            self.suggestions_listbox.insert(tk.END, cat)
        
        # Mostrar la ventana de sugerencias
        self._position_suggestions_window()
        self.suggestions_window.deiconify()
    
    def _create_suggestions_window(self):
        """Crea la ventana flotante de sugerencias"""
        # Crear ventana toplevel sin decoraciones
        self.suggestions_window = tk.Toplevel(self)
        self.suggestions_window.wm_overrideredirect(True)
        self.suggestions_window.withdraw()
        
        # Crear listbox
        self.suggestions_listbox = tk.Listbox(
            self.suggestions_window,
            height=5,
            font=('Helvetica', 10),
            relief='solid',
            borderwidth=1
        )
        self.suggestions_listbox.pack(fill='both', expand=True)
        
        # Bind para seleccionar con clic o Enter
        self.suggestions_listbox.bind('<Button-1>', self._on_suggestion_click)
        self.suggestions_listbox.bind('<Return>', self._on_suggestion_select)
        self.suggestions_listbox.bind('<Double-Button-1>', self._on_suggestion_select)
    
    def _position_suggestions_window(self):
        """Posiciona la ventana de sugerencias debajo del entry"""
        # Actualizar geometría
        self.update_idletasks()
        
        # Obtener posición del entry
        x = self.category_entry.winfo_rootx()
        y = self.category_entry.winfo_rooty() + self.category_entry.winfo_height()
        width = self.category_entry.winfo_width()
        
        # Posicionar la ventana
        self.suggestions_window.geometry(f'{width}x100+{x}+{y}')
    
    def _on_suggestion_click(self, event=None):
        """Maneja el clic en una sugerencia"""
        # Esperar un momento para que se complete la selección
        self.after(50, self._on_suggestion_select)
    
    def _on_suggestion_select(self, event=None):
        """Selecciona la sugerencia actual"""
        if not self.suggestions_listbox:
            return
        
        selection = self.suggestions_listbox.curselection()
        if selection:
            selected_text = self.suggestions_listbox.get(selection[0])
            self.category_var.set(selected_text)
            self._hide_suggestions()
            self.category_entry.focus_set()
    
    def _hide_suggestions(self):
        """Oculta la ventana de sugerencias"""
        if self.suggestions_window:
            self.suggestions_window.withdraw()
    
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
        
        # Cargar precio de proveedor
        try:
            supplier_price = material['supplier_price'] or 0
        except (KeyError, IndexError):
            supplier_price = 0
        self.supplier_price_entry.delete(0, tk.END)
        self.supplier_price_entry.insert(0, str(supplier_price))
        
        if material['category']:
            self.category_var.set(material['category'])
    
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
        
        # Validar precio de proveedor
        try:
            supplier_price = float(self.supplier_price_entry.get())
            if supplier_price < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror('Error', 'Precio de proveedor inválido (debe ser ≥ 0)')
            self.supplier_price_entry.focus()
            return
        
        # Validar precio de venta
        try:
            price = float(self.price_entry.get())
            if price < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror('Error', 'Precio de venta inválido (debe ser ≥ 0)')
            self.price_entry.focus()
            return
        
        # Obtener datos adicionales
        category = self.category_var.get().strip() or 'Sin categoría'
        
        # Guardar en base de datos (image_path siempre None)
        try:
            if self.material_id:
                db.update_material(
                    self.material_id, name, description, 
                    None, price, category, supplier_price
                )
            else:
                db.add_material(name, description, None, price, category, supplier_price)
            
            # Callback de actualización
            if self.on_save:
                self.on_save()
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror('Error', f'Error al guardar: {str(e)}')