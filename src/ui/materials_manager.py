"""
Gestión de materiales - Refactorizado con clases base
"""
import tkinter as tk
from tkinter import ttk
from src.database import db
from src.ui.ui_utils import (
    BaseCRUDFrame, BaseEditor, format_price_es,
    create_form_field, show_info, show_error, show_warning, ask_yes_no
)


class MaterialsFrame(BaseCRUDFrame):
    """Frame principal para la gestión de materiales"""

    def get_columns(self):
        return ('name', 'category', 'desc', 'supplier_price', 'price')

    def get_headings(self):
        return ('Nombre', 'Categoría', 'Descripción', 'P. Proveedor', 'P. Venta')

    def get_column_widths(self):
        return (150, 100, 200, 120, 100)

    def get_buttons_config(self):
        return [
            ('➕ Añadir', self.add, 'success'),
            ('✏️ Editar', self.edit, 'primary'),
            ('🗑️ Borrar', self.delete, 'danger')
        ]

    def refresh(self):
        """Actualiza la lista de materiales"""
        materials = db.list_materials()

        def filter_func(material, search_term):
            if not search_term:
                return True
            # sqlite3.Row no tiene .get(), usar acceso directo con try/except
            try:
                name = (material['name'] or '').lower()
                desc = (material['description'] or '').lower()
                category = (material['category'] or '').lower()
            except (KeyError, TypeError):
                return False
            return (search_term in name or
                   search_term in desc or
                   search_term in category)

        def format_func(material):
            # sqlite3.Row - acceso directo
            try:
                supplier_price = material['supplier_price'] or 0
            except (KeyError, TypeError):
                supplier_price = 0

            try:
                price = material['price'] or 0
            except (KeyError, TypeError):
                price = 0

            return (
                material['name'],
                material['category'] or 'Sin categoría',
                material['description'] or '',
                f"{float(supplier_price):.2f} €",
                f"{float(price):.2f} €"
            )

        self._refresh_tree_with_data(materials, filter_func, format_func)

    def add(self):
        """Abre el editor para añadir un nuevo material"""
        MaterialEditor(self, material_id=None, on_save=self.refresh)

    def edit(self):
        """Abre el editor para editar el material seleccionado"""
        selected = self.tree.selection()
        if not selected:
            show_warning('Advertencia', 'Selecciona un material', self)
            return

        material_id = int(selected[0])
        MaterialEditor(self, material_id=material_id, on_save=self.refresh)

    def delete(self):
        """Elimina el material seleccionado"""
        selected = self.tree.selection()
        if not selected:
            show_warning('Advertencia', 'Selecciona un material', self)
            return

        material_id = int(selected[0])
        if ask_yes_no('Confirmar', '¿Borrar este material?', self):
            try:
                db.delete_material(material_id)
                self.refresh()
                show_info('Éxito', 'Material eliminado', self)
            except Exception as e:
                show_error('Error', f'Error al eliminar: {e}', self)


class MaterialEditor(BaseEditor):
    """Editor de materiales - Ventana modal"""

    def __init__(self, parent, material_id=None, on_save=None):
        # Establecer atributos ANTES de llamar a super().__init__()
        self.material_id = material_id

        super().__init__(
            parent,
            item_id=material_id,
            on_save=on_save,
            title='Editar Material' if material_id else 'Nuevo Material',
            width=600,
            height=450
        )

    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal del formulario
        form = ttk.Frame(self, padding=20)
        form.pack(fill='both', expand=True)

        # Nombre
        self.name_entry = create_form_field(
            form, 'Nombre *', 'entry', row=0,
            width=40, font=('Helvetica', 11)
        )
        self.name_entry.focus()

        # Descripción
        self.description_text = create_form_field(
            form, 'Descripción', 'text', row=1,
            height=5, width=40, font=('Helvetica', 10)
        )

        # Precio Proveedor
        self.supplier_price_entry = create_form_field(
            form, 'Precio Proveedor (€)', 'entry', row=2,
            width=20, font=('Helvetica', 11)
        )
        self.supplier_price_entry.insert(0, '0')

        # Precio Venta
        self.price_entry = create_form_field(
            form, 'Precio Venta (€) *', 'entry', row=3,
            width=20, font=('Helvetica', 11)
        )

        # Categoría con combobox
        ttk.Label(form, text='Categoría', font=('Helvetica', 10, 'bold')).grid(
            row=4, column=0, sticky='w', pady=5
        )

        # Obtener categorías existentes (CORREGIDO: list_material_categories en vez de get_categories)
        categories = db.list_material_categories() or []
        if 'Sin categoría' not in categories:
            categories.insert(0, 'Sin categoría')

        self.category_combo = ttk.Combobox(
            form, values=categories, width=37, font=('Helvetica', 11)
        )
        self.category_combo.set('Sin categoría')
        self.category_combo.grid(row=4, column=1, pady=5, sticky='ew')

        # Texto de ayuda
        ttk.Label(form, text='Escribe o selecciona una categoría',
                 font=('Helvetica', 8), foreground='gray').grid(
            row=5, column=1, sticky='w'
        )

        form.columnconfigure(1, weight=1)

        # Botones estándar
        self._create_buttons_frame()

    def _load_data(self):
        """Carga los datos del material si está editando"""
        if not self.material_id:
            return

        material = db.get_material(self.material_id)
        if not material:
            return

        # Cargar datos en los campos
        self.name_entry.insert(0, material['name'])

        if material.get('description'):
            self.description_text.insert('1.0', material['description'])

        self.price_entry.insert(0, str(material['price']))

        supplier_price = material.get('supplier_price') or 0
        self.supplier_price_entry.delete(0, tk.END)
        self.supplier_price_entry.insert(0, str(supplier_price))

        if material.get('category'):
            self.category_combo.set(material['category'])

    def _save(self):
        """Valida y guarda el material"""
        # Validar nombre
        name = self.name_entry.get().strip()
        if not name:
            show_error('Error', 'El nombre es obligatorio', self)
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
            show_error('Error', 'Precio de proveedor inválido (debe ser ≥ 0)', self)
            self.supplier_price_entry.focus()
            return

        # Validar precio de venta
        try:
            price = float(self.price_entry.get())
            if price < 0:
                raise ValueError()
        except ValueError:
            show_error('Error', 'Precio de venta inválido (debe ser ≥ 0)', self)
            self.price_entry.focus()
            return

        # Obtener categoría
        category = self.category_combo.get().strip() or 'Sin categoría'

        # Guardar en base de datos
        try:
            if self.material_id:
                db.update_material(
                    material_id=self.material_id,
                    name=name,
                    description=description,
                    image_path=None,
                    price=price,
                    supplier_price=supplier_price,
                    category=category
                )
                show_info('Éxito', 'Material actualizado', self)
            else:
                db.add_material(
                    name=name,
                    description=description,
                    image_path=None,
                    price=price,
                    supplier_price=supplier_price,
                    category=category
                )
                show_info('Éxito', 'Material creado', self)

            # Callback de actualización
            if self.on_save:
                self.on_save()

            self.destroy()

        except Exception as e:
            show_error('Error', f'Error al guardar: {e}', self)
