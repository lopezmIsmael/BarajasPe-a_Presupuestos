"""
Gestor de Materiales - Interfaz CRUD para gestión de materiales.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                              QMessageBox, QHeaderView, QDialog, QFormLayout,
                              QTextEdit, QGroupBox, QComboBox, QDoubleSpinBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from src.database.database import MaterialDAO, Database
from src.utils.helpers import (show_error, show_info, confirm_dialog,
                               format_currency, adjust_dialog_to_screen)


class MaterialDialog(QDialog):
    """Diálogo para crear/editar un material"""

    UNIDADES = ['ud', 'm', 'm²', 'm³', 'kg', 'g', 'l', 'ml', 'caja', 'palet', 'saco']

    def __init__(self, parent=None, material=None, db=None):
        super().__init__(parent)
        self.material = material
        self.db = db
        self.init_ui()

        if material:
            self.load_data()
        else:
            # Calcular precio de venta automáticamente al cambiar precio de compra o margen
            self.precio_compra_input.valueChanged.connect(self.calcular_precio_venta)
            self.margen_input.valueChanged.connect(self.calcular_precio_venta)

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Nuevo Material" if not self.material else "Editar Material")
        self.setModal(True)
        # Ajustar tamaño al monitor disponible
        adjust_dialog_to_screen(self, preferred_width=650, preferred_height=600, min_width=500, min_height=450)

        # Layout principal
        main_layout = QVBoxLayout()

        # Widget de contenido scrollable
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Grupo de información básica
        basic_group = QGroupBox("Información Básica")
        basic_layout = QFormLayout()

        self.nombre_input = QLineEdit()
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setMaximumHeight(60)
        self.referencia_input = QLineEdit()
        self.proveedor_input = QLineEdit()

        basic_layout.addRow("Nombre*:", self.nombre_input)
        basic_layout.addRow("Descripción:", self.descripcion_input)
        basic_layout.addRow("Referencia:", self.referencia_input)
        basic_layout.addRow("Proveedor:", self.proveedor_input)

        basic_group.setLayout(basic_layout)
        content_layout.addWidget(basic_group)

        # Grupo de unidad y precios
        precio_group = QGroupBox("Unidad y Precios")
        precio_layout = QFormLayout()

        self.unidad_combo = QComboBox()
        self.unidad_combo.addItems(self.UNIDADES)

        self.precio_compra_input = QDoubleSpinBox()
        self.precio_compra_input.setRange(0, 999999.99)
        self.precio_compra_input.setDecimals(2)
        self.precio_compra_input.setSuffix(" €")
        self.precio_compra_input.setGroupSeparatorShown(True)

        self.margen_input = QDoubleSpinBox()
        self.margen_input.setRange(0, 1000)
        self.margen_input.setDecimals(2)
        self.margen_input.setSuffix(" %")
        self.margen_input.setValue(20.0)

        self.precio_venta_input = QDoubleSpinBox()
        self.precio_venta_input.setRange(0, 999999.99)
        self.precio_venta_input.setDecimals(2)
        self.precio_venta_input.setSuffix(" €")
        self.precio_venta_input.setGroupSeparatorShown(True)

        precio_layout.addRow("Unidad*:", self.unidad_combo)
        precio_layout.addRow("Precio Compra*:", self.precio_compra_input)
        precio_layout.addRow("Margen Ganancia (%):", self.margen_input)
        precio_layout.addRow("Precio Venta*:", self.precio_venta_input)

        precio_group.setLayout(precio_layout)
        content_layout.addWidget(precio_group)

        # Grupo de stock
        stock_group = QGroupBox("Control de Stock (Opcional)")
        stock_layout = QFormLayout()

        self.stock_actual_input = QDoubleSpinBox()
        self.stock_actual_input.setRange(0, 999999.99)
        self.stock_actual_input.setDecimals(2)

        self.stock_minimo_input = QDoubleSpinBox()
        self.stock_minimo_input.setRange(0, 999999.99)
        self.stock_minimo_input.setDecimals(2)

        stock_layout.addRow("Stock Actual:", self.stock_actual_input)
        stock_layout.addRow("Stock Mínimo:", self.stock_minimo_input)

        stock_group.setLayout(stock_layout)
        content_layout.addWidget(stock_group)

        # Notas
        notas_group = QGroupBox("Notas")
        notas_layout = QVBoxLayout()
        self.notas_input = QTextEdit()
        self.notas_input.setMaximumHeight(60)
        notas_layout.addWidget(self.notas_input)
        notas_group.setLayout(notas_layout)
        content_layout.addWidget(notas_group)

        # Crear scroll area
        scroll = QScrollArea()
        scroll.setWidget(content_widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        main_layout.addWidget(scroll)

        # Botones fuera del scroll area
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def calcular_precio_venta(self):
        """Calcula automáticamente el precio de venta basado en el precio de compra y el margen"""
        precio_compra = self.precio_compra_input.value()
        margen = self.margen_input.value()

        precio_venta = precio_compra * (1 + margen / 100)
        self.precio_venta_input.setValue(precio_venta)

    def load_data(self):
        """Carga los datos del material en el formulario"""
        self.nombre_input.setText(self.material.nombre or "")
        self.descripcion_input.setPlainText(self.material.descripcion or "")
        self.referencia_input.setText(self.material.referencia or "")
        self.proveedor_input.setText(self.material.proveedor or "")

        # Establecer unidad
        index = self.unidad_combo.findText(self.material.unidad)
        if index >= 0:
            self.unidad_combo.setCurrentIndex(index)

        self.precio_compra_input.setValue(self.material.precio_compra)
        self.margen_input.setValue(self.material.margen_ganancia_defecto)
        self.precio_venta_input.setValue(self.material.precio_venta)

        self.stock_actual_input.setValue(self.material.stock_actual)
        self.stock_minimo_input.setValue(self.material.stock_minimo)

        self.notas_input.setPlainText(self.material.notas or "")

    def validate_form(self):
        """Valida los datos del formulario"""
        if not self.nombre_input.text().strip():
            show_error(self, "Error", "El nombre es obligatorio")
            return False

        if self.precio_compra_input.value() <= 0:
            show_error(self, "Error", "El precio de compra debe ser mayor que 0")
            return False

        if self.precio_venta_input.value() <= 0:
            show_error(self, "Error", "El precio de venta debe ser mayor que 0")
            return False

        return True

    def save(self):
        """Guarda el material"""
        if not self.validate_form():
            return

        try:
            dao = MaterialDAO(self.db)

            data = {
                'nombre': self.nombre_input.text().strip(),
                'descripcion': self.descripcion_input.toPlainText().strip(),
                'referencia': self.referencia_input.text().strip(),
                'proveedor': self.proveedor_input.text().strip(),
                'unidad': self.unidad_combo.currentText(),
                'precio_compra': self.precio_compra_input.value(),
                'precio_venta': self.precio_venta_input.value(),
                'margen_ganancia_defecto': self.margen_input.value(),
                'stock_actual': self.stock_actual_input.value(),
                'stock_minimo': self.stock_minimo_input.value(),
                'notas': self.notas_input.toPlainText().strip()
            }

            if self.material:
                # Actualizar
                dao.actualizar(self.material.id, **data)
            else:
                # Crear
                self.material = dao.crear(**data)

            self.accept()

        except Exception as e:
            show_error(self, "Error", f"Error al guardar el material: {str(e)}")

    def get_material(self):
        """Retorna el material creado/editado"""
        return self.material


class MaterialsManager(QWidget):
    """Widget para gestionar materiales"""

    material_selected = pyqtSignal(object)  # Señal cuando se selecciona un material
    material_updated = pyqtSignal(object)   # Señal cuando se actualiza un material
    material_created = pyqtSignal(object)   # Señal cuando se crea un material

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.dao = MaterialDAO(db)
        self.init_ui()
        self.load_materials()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()

        # Barra de herramientas
        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar material...")
        self.search_input.textChanged.connect(self.search_materials)

        self.new_button = QPushButton("Nuevo Material")
        self.new_button.clicked.connect(self.new_material)

        self.edit_button = QPushButton("Editar")
        self.edit_button.clicked.connect(self.edit_material)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("Eliminar")
        self.delete_button.clicked.connect(self.delete_material)
        self.delete_button.setEnabled(False)

        toolbar.addWidget(QLabel("Buscar:"))
        toolbar.addWidget(self.search_input)
        toolbar.addStretch()
        toolbar.addWidget(self.new_button)
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.delete_button)

        layout.addLayout(toolbar)

        # Tabla de materiales
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Unidad", "P. Compra", "Margen %", "P. Venta", "Stock"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(self.edit_material)

        # Ocultar columna ID
        self.table.setColumnHidden(0, True)

        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_materials(self):
        """Carga todos los materiales en la tabla"""
        try:
            materiales = self.dao.obtener_todos()
            self.populate_table(materiales)
        except Exception as e:
            show_error(self, "Error", f"Error al cargar materiales: {str(e)}")

    def populate_table(self, materiales):
        """Rellena la tabla con los materiales"""
        self.table.setRowCount(0)

        for material in materiales:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(material.id)))
            self.table.setItem(row, 1, QTableWidgetItem(material.nombre or ""))
            self.table.setItem(row, 2, QTableWidgetItem(material.unidad or ""))
            self.table.setItem(row, 3, QTableWidgetItem(format_currency(material.precio_compra)))
            self.table.setItem(row, 4, QTableWidgetItem(f"{material.margen_ganancia_defecto:.2f}%"))
            self.table.setItem(row, 5, QTableWidgetItem(format_currency(material.precio_venta)))
            self.table.setItem(row, 6, QTableWidgetItem(f"{material.stock_actual:.2f}"))

    def search_materials(self):
        """Busca materiales por el criterio introducido"""
        criterio = self.search_input.text().strip()

        if not criterio:
            self.load_materials()
            return

        try:
            materiales = self.dao.buscar(criterio)
            self.populate_table(materiales)
        except Exception as e:
            show_error(self, "Error", f"Error al buscar materiales: {str(e)}")

    def new_material(self):
        """Crea un nuevo material"""
        dialog = MaterialDialog(self, db=self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            material = dialog.get_material()
            show_info(self, "Éxito", "Material creado correctamente")
            self.load_materials()
            self.material_created.emit(material)  # Emitir señal

    def edit_material(self):
        """Edita el material seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        material_id = int(self.table.item(selected_row, 0).text())
        material = self.dao.obtener_por_id(material_id)

        if not material:
            show_error(self, "Error", "Material no encontrado")
            return

        dialog = MaterialDialog(self, material=material, db=self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            material_updated = dialog.get_material()
            show_info(self, "Éxito", "Material actualizado correctamente")
            self.load_materials()
            self.material_updated.emit(material_updated)  # Emitir señal

    def delete_material(self):
        """Elimina el material seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        material_id = int(self.table.item(selected_row, 0).text())
        nombre = self.table.item(selected_row, 1).text()

        if not confirm_dialog(self, "Confirmar",
                              f"¿Está seguro de eliminar el material '{nombre}'?\n"
                              f"Esta acción marcará el material como inactivo."):
            return

        try:
            if self.dao.eliminar(material_id):
                show_info(self, "Éxito", "Material eliminado correctamente")
                self.load_materials()
            else:
                show_error(self, "Error", "No se pudo eliminar el material")
        except Exception as e:
            show_error(self, "Error", f"Error al eliminar el material: {str(e)}")

    def on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

        if has_selection:
            selected_row = self.table.currentRow()
            material_id = int(self.table.item(selected_row, 0).text())
            material = self.dao.obtener_por_id(material_id)
            self.material_selected.emit(material)

    def get_selected_material(self):
        """Retorna el material seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return None

        material_id = int(self.table.item(selected_row, 0).text())
        return self.dao.obtener_por_id(material_id)
