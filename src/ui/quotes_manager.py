"""
Gestor de Presupuestos - Interfaz para gestión completa de presupuestos.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                              QHeaderView, QDialog, QFormLayout,
                              QTextEdit, QGroupBox, QDoubleSpinBox, QDateEdit,
                              QComboBox, QSplitter, QSpinBox, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from datetime import datetime, date
from src.database.database import (PresupuestoDAO, ClienteDAO, MaterialDAO,
                                   LineaPresupuesto, Database)
from src.utils.helpers import (show_error, show_info, confirm_dialog,
                               format_currency, format_date)
from src.ui.clients_manager import ClientDialog
from src.ui.materials_manager import MaterialDialog
from src.templates.template_engine import TemplateEngine
from src.ui.document_viewer import DocumentViewer


class AddLineDialog(QDialog):
    """Diálogo para añadir una línea al presupuesto"""

    material_updated = pyqtSignal(int)  # Señal que emite el ID del material actualizado

    def __init__(self, parent=None, db=None, linea=None):
        super().__init__(parent)
        self.db = db
        self.linea = linea
        self.materiales = []
        self._updating_prices = False  # Flag para evitar loops infinitos
        self.init_ui()

        # Conectar señales ANTES de cargar materiales
        self.cantidad_input.valueChanged.connect(self.calcular_totales)
        self.precio_compra_input.valueChanged.connect(self.on_precio_compra_changed)
        self.margen_input.valueChanged.connect(self.on_margen_changed)
        self.precio_venta_unitario_input.valueChanged.connect(self.on_precio_venta_changed)
        self.material_combo.currentIndexChanged.connect(self.on_material_changed)

        self.load_materials()

        if linea:
            self.load_line_data()

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Añadir Línea" if not self.linea else "Editar Línea")
        self.setModal(True)
        self.setMinimumWidth(600)

        layout = QVBoxLayout()

        # Grupo de búsqueda y filtros
        search_group = QGroupBox("Búsqueda de Material")
        search_layout = QVBoxLayout()

        # Búsqueda por nombre
        search_name_layout = QHBoxLayout()
        search_label = QLabel("Buscar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Escribe para buscar por nombre...")
        self.search_input.textChanged.connect(self.filter_materials)
        search_name_layout.addWidget(search_label)
        search_name_layout.addWidget(self.search_input)
        search_layout.addLayout(search_name_layout)

        # Filtro por familia
        family_layout = QHBoxLayout()
        family_label = QLabel("Familia:")
        self.family_combo = QComboBox()
        self.family_combo.addItem("Todas las familias", "")
        self.family_combo.currentTextChanged.connect(self.filter_materials)
        family_layout.addWidget(family_label)
        family_layout.addWidget(self.family_combo)
        search_layout.addLayout(family_layout)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        form_layout = QFormLayout()

        # Material
        material_layout = QHBoxLayout()
        self.material_combo = QComboBox()
        self.material_combo.setMinimumWidth(400)
        self.new_material_btn = QPushButton("+ Nuevo")
        self.new_material_btn.clicked.connect(self.new_material)
        material_layout.addWidget(self.material_combo)
        material_layout.addWidget(self.new_material_btn)
        form_layout.addRow("Material*:", material_layout)

        # Cantidad
        self.cantidad_input = QDoubleSpinBox()
        self.cantidad_input.setRange(0.01, 999999.99)
        self.cantidad_input.setDecimals(2)
        self.cantidad_input.setValue(1.0)
        form_layout.addRow("Cantidad*:", self.cantidad_input)

        # Precio de compra unitario (auto-rellenado desde material)
        self.precio_compra_input = QDoubleSpinBox()
        self.precio_compra_input.setRange(0, 999999.99)
        self.precio_compra_input.setDecimals(2)
        self.precio_compra_input.setSuffix(" €")
        self.precio_compra_input.setGroupSeparatorShown(True)
        form_layout.addRow("Precio Compra Unit.:", self.precio_compra_input)

        # Margen de ganancia
        self.margen_input = QDoubleSpinBox()
        self.margen_input.setRange(0, 1000)
        self.margen_input.setDecimals(2)
        self.margen_input.setSuffix(" %")
        self.margen_input.setValue(20.0)
        form_layout.addRow("Margen Ganancia (%):", self.margen_input)

        # Precio de venta unitario
        self.precio_venta_unitario_input = QDoubleSpinBox()
        self.precio_venta_unitario_input.setRange(0, 999999.99)
        self.precio_venta_unitario_input.setDecimals(2)
        self.precio_venta_unitario_input.setSuffix(" €")
        self.precio_venta_unitario_input.setGroupSeparatorShown(True)
        form_layout.addRow("Precio Venta Unit.:", self.precio_venta_unitario_input)

        # Descripción personalizada
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setMaximumHeight(60)
        form_layout.addRow("Descripción (opcional):", self.descripcion_input)

        layout.addLayout(form_layout)

        # Separador
        layout.addWidget(QLabel("─" * 80))

        # Resumen de cálculos
        summary_group = QGroupBox("Resumen de Cálculos")
        summary_layout = QFormLayout()

        self.coste_total_label = QLabel("0,00 €")
        self.ganancia_label = QLabel("0,00 €")
        self.precio_venta_label = QLabel("0,00 €")

        summary_layout.addRow("Coste Total:", self.coste_total_label)
        summary_layout.addRow("Ganancia:", self.ganancia_label)
        summary_layout.addRow("Precio Venta Total:", self.precio_venta_label)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Botones
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                       QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_dialog)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def load_materials(self):
        """Carga los materiales y las familias"""
        try:
            dao = MaterialDAO(self.db)
            self.materiales = dao.obtener_todos()

            # Cargar familias únicas
            familias = set()
            for material in self.materiales:
                if material.familia:
                    familias.add(material.familia)

            # Poblar combo de familias
            self.family_combo.clear()
            self.family_combo.addItem("Todas las familias", "")
            for familia in sorted(familias):
                self.family_combo.addItem(familia, familia)

            # Cargar materiales en el combo
            self.filter_materials()

        except Exception as e:
            show_error(self, "Error", f"Error al cargar materiales: {str(e)}")

    def filter_materials(self):
        """Filtra los materiales según búsqueda y familia"""
        search_text = self.search_input.text().lower() if hasattr(self, 'search_input') else ""
        selected_family = self.family_combo.currentData() if hasattr(self, 'family_combo') else ""

        self.material_combo.clear()

        for material in self.materiales:
            # Filtrar por familia
            if selected_family and material.familia != selected_family:
                continue

            # Filtrar por búsqueda de texto
            if search_text and search_text not in material.nombre.lower():
                continue

            # Añadir al combo
            familia_tag = f"[{material.familia}] " if material.familia else ""
            self.material_combo.addItem(
                f"{familia_tag}{material.nombre} ({material.unidad}) - {format_currency(material.precio_compra)}",
                material.id
            )

        # Si hay resultados, seleccionar el primero
        if self.material_combo.count() > 0:
            self.material_combo.setCurrentIndex(0)

    def on_material_changed(self, index):
        """Cuando se selecciona un material, auto-rellena los datos"""
        if index < 0:
            return

        material_id = self.material_combo.currentData()
        if not material_id:
            return

        # Buscar el material por ID
        material = next((m for m in self.materiales if m.id == material_id), None)
        if not material:
            return

        # Bloquear actualizaciones automáticas mientras cargamos los datos
        self._updating_prices = True
        try:
            # Establecer precio de compra del material
            self.precio_compra_input.setValue(material.precio_compra if material.precio_compra else 0.0)

            # Establecer precio de venta y margen
            if material.precio_venta and material.precio_compra and material.precio_compra > 0:
                # Usar el precio de venta del material
                self.precio_venta_unitario_input.setValue(material.precio_venta)
                # Calcular el margen real del material
                margen_real = ((material.precio_venta - material.precio_compra) / material.precio_compra) * 100
                self.margen_input.setValue(margen_real)
            else:
                # Si no hay precio de venta, usar el margen por defecto del material
                margen_defecto = material.margen_ganancia_defecto if material.margen_ganancia_defecto else 20.0
                self.margen_input.setValue(margen_defecto)
                # Calcular precio de venta basado en margen
                precio_venta = material.precio_compra * (1 + margen_defecto / 100.0)
                self.precio_venta_unitario_input.setValue(precio_venta)

        finally:
            self._updating_prices = False

        # Recalcular totales con los nuevos valores
        self.calcular_totales()

    def on_precio_compra_changed(self):
        """Cuando cambia el precio de compra, recalcular precio de venta basado en margen"""
        if self._updating_prices:
            return

        self._updating_prices = True
        try:
            precio_compra = self.precio_compra_input.value()
            margen = self.margen_input.value()
            precio_venta_unitario = precio_compra * (1 + margen / 100.0)
            self.precio_venta_unitario_input.setValue(precio_venta_unitario)
            self.calcular_totales()
        finally:
            self._updating_prices = False

    def on_margen_changed(self):
        """Cuando cambia el margen, recalcular precio de venta"""
        if self._updating_prices:
            return

        self._updating_prices = True
        try:
            precio_compra = self.precio_compra_input.value()
            margen = self.margen_input.value()
            precio_venta_unitario = precio_compra * (1 + margen / 100.0)
            self.precio_venta_unitario_input.setValue(precio_venta_unitario)
            self.calcular_totales()
        finally:
            self._updating_prices = False

    def on_precio_venta_changed(self):
        """Cuando cambia el precio de venta, recalcular margen"""
        if self._updating_prices:
            return

        self._updating_prices = True
        try:
            precio_compra = self.precio_compra_input.value()
            precio_venta = self.precio_venta_unitario_input.value()

            if precio_compra > 0:
                margen = ((precio_venta - precio_compra) / precio_compra) * 100
                self.margen_input.setValue(margen)

            self.calcular_totales()
        finally:
            self._updating_prices = False

    def calcular_totales(self):
        """Calcula los totales automáticamente"""
        cantidad = self.cantidad_input.value()
        precio_compra = self.precio_compra_input.value()
        precio_venta_unitario = self.precio_venta_unitario_input.value()

        coste_total = cantidad * precio_compra
        precio_venta_total = cantidad * precio_venta_unitario
        ganancia = precio_venta_total - coste_total

        self.coste_total_label.setText(format_currency(coste_total))
        self.ganancia_label.setText(format_currency(ganancia))
        self.precio_venta_label.setText(format_currency(precio_venta_total))

    def new_material(self):
        """Crea un nuevo material desde el diálogo"""
        dialog = MaterialDialog(self, db=self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            show_info(self, "Éxito", "Material creado correctamente")
            self.load_materials()
            # Seleccionar el material recién creado
            material = dialog.get_material()
            for i, m in enumerate(self.materiales):
                if m.id == material.id:
                    self.material_combo.setCurrentIndex(i)
                    break

    def load_line_data(self):
        """Carga los datos de una línea existente"""
        # Bloquear actualizaciones automáticas mientras cargamos los datos
        self._updating_prices = True
        try:
            # Buscar y seleccionar el material
            for i, m in enumerate(self.materiales):
                if m.id == self.linea.material_id:
                    self.material_combo.setCurrentIndex(i)
                    break

            self.cantidad_input.setValue(self.linea.cantidad)
            self.precio_compra_input.setValue(self.linea.precio_compra_unitario)
            self.margen_input.setValue(self.linea.margen_ganancia_porc)

            # Calcular precio de venta unitario desde la línea
            precio_venta_unitario = self.linea.precio_compra_unitario * (1 + self.linea.margen_ganancia_porc / 100.0)
            self.precio_venta_unitario_input.setValue(precio_venta_unitario)

            self.descripcion_input.setPlainText(self.linea.descripcion_personalizada or "")
        finally:
            self._updating_prices = False

        self.calcular_totales()

    def accept_dialog(self):
        """Valida y acepta el diálogo"""
        if self.material_combo.currentIndex() < 0:
            show_error(self, "Error", "Debe seleccionar un material")
            return

        if self.cantidad_input.value() <= 0:
            show_error(self, "Error", "La cantidad debe ser mayor que 0")
            return

        # Actualizar el material en la base de datos con los nuevos precios
        try:
            material_id = self.material_combo.currentData()
            material = next((m for m in self.materiales if m.id == material_id), None)

            if material:
                precio_compra_actual = self.precio_compra_input.value()
                precio_venta_actual = self.precio_venta_unitario_input.value()
                margen_actual = self.margen_input.value()

                # Solo actualizar si los precios han cambiado
                if (precio_compra_actual != material.precio_compra or
                    precio_venta_actual != material.precio_venta or
                    margen_actual != material.margen_ganancia_defecto):

                    dao = MaterialDAO(self.db)
                    dao.actualizar(
                        material_id,
                        precio_compra=precio_compra_actual,
                        precio_venta=precio_venta_actual,
                        margen_ganancia_defecto=margen_actual
                    )

                    # Recargar la lista de materiales para reflejar los cambios
                    self.load_materials()

                    # Emitir señal de que el material fue actualizado
                    self.material_updated.emit(material_id)
        except Exception as e:
            # No fallar si hay error al actualizar el material, solo mostrar advertencia
            show_error(self, "Advertencia", f"No se pudo actualizar el material: {str(e)}")

        self.accept()

    def get_line_data(self):
        """Retorna los datos de la línea"""
        return {
            'material_id': self.material_combo.currentData(),
            'cantidad': self.cantidad_input.value(),
            'precio_compra_unitario': self.precio_compra_input.value(),
            'margen_ganancia_porc': self.margen_input.value(),
            'descripcion_personalizada': self.descripcion_input.toPlainText().strip()
        }


class QuoteEditor(QDialog):
    """Editor de presupuesto"""

    material_updated = pyqtSignal(int)  # Señal para propagar actualizaciones de materiales

    def __init__(self, parent=None, db=None, presupuesto=None):
        super().__init__(parent)
        self.db = db
        self.presupuesto = presupuesto
        self.lineas_temp = []  # Líneas temporales antes de guardar
        self.init_ui()

        if presupuesto:
            self.load_quote_data()

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Nuevo Presupuesto" if not self.presupuesto else f"Editar Presupuesto")
        self.setModal(True)
        self.resize(1000, 700)

        layout = QVBoxLayout()

        # Datos del presupuesto
        header_group = QGroupBox("Datos del Presupuesto")
        header_layout = QFormLayout()

        self.numero_input = QLineEdit()
        self.numero_input.setReadOnly(True)

        # Cliente
        cliente_layout = QHBoxLayout()
        self.cliente_combo = QComboBox()
        self.cliente_combo.setMinimumWidth(300)
        self.new_cliente_btn = QPushButton("+ Nuevo Cliente")
        self.new_cliente_btn.clicked.connect(self.new_cliente)
        cliente_layout.addWidget(self.cliente_combo)
        cliente_layout.addWidget(self.new_cliente_btn)

        self.fecha_input = QDateEdit()
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setDisplayFormat("dd/MM/yyyy")

        self.fecha_validez_input = QDateEdit()
        self.fecha_validez_input.setCalendarPopup(True)
        self.fecha_validez_input.setDate(QDate.currentDate().addDays(30))
        self.fecha_validez_input.setDisplayFormat("dd/MM/yyyy")

        self.titulo_input = QLineEdit()

        self.descripcion_input = QTextEdit()
        self.descripcion_input.setMaximumHeight(60)

        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["borrador", "enviado", "aceptado", "rechazado", "facturado"])

        self.coste_mano_obra_input = QDoubleSpinBox()
        self.coste_mano_obra_input.setRange(0, 999999.99)
        self.coste_mano_obra_input.setDecimals(2)
        self.coste_mano_obra_input.setSuffix(" €")
        self.coste_mano_obra_input.setGroupSeparatorShown(True)
        self.coste_mano_obra_input.valueChanged.connect(self.calcular_totales)

        self.descuento_input = QDoubleSpinBox()
        self.descuento_input.setRange(0, 100)
        self.descuento_input.setDecimals(2)
        self.descuento_input.setSuffix(" %")
        self.descuento_input.valueChanged.connect(self.calcular_totales)

        header_layout.addRow("Nº Presupuesto:", self.numero_input)
        header_layout.addRow("Cliente*:", cliente_layout)
        header_layout.addRow("Fecha:", self.fecha_input)
        header_layout.addRow("Validez hasta:", self.fecha_validez_input)
        header_layout.addRow("Título:", self.titulo_input)
        header_layout.addRow("Descripción:", self.descripcion_input)
        header_layout.addRow("Estado:", self.estado_combo)
        header_layout.addRow("Coste Mano de Obra:", self.coste_mano_obra_input)
        header_layout.addRow("Descuento Global (%):", self.descuento_input)

        header_group.setLayout(header_layout)
        layout.addWidget(header_group)

        # Líneas del presupuesto
        lines_group = QGroupBox("Líneas de Materiales")
        lines_layout = QVBoxLayout()

        # Barra de herramientas de líneas
        lines_toolbar = QHBoxLayout()
        self.add_line_btn = QPushButton("Añadir Línea")
        self.add_line_btn.clicked.connect(self.add_line)
        self.edit_line_btn = QPushButton("Editar Línea")
        self.edit_line_btn.clicked.connect(self.edit_line)
        self.edit_line_btn.setEnabled(False)
        self.delete_line_btn = QPushButton("Eliminar Línea")
        self.delete_line_btn.clicked.connect(self.delete_line)
        self.delete_line_btn.setEnabled(False)

        lines_toolbar.addWidget(self.add_line_btn)
        lines_toolbar.addWidget(self.edit_line_btn)
        lines_toolbar.addWidget(self.delete_line_btn)
        lines_toolbar.addStretch()

        lines_layout.addLayout(lines_toolbar)

        # Tabla de líneas
        self.lines_table = QTableWidget()
        self.lines_table.setColumnCount(7)
        self.lines_table.setHorizontalHeaderLabels([
            "Material", "Cantidad", "Unidad", "P. Compra Unit.", "Margen %", "P. Venta Unit.", "Total Venta"
        ])
        self.lines_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.lines_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.lines_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.lines_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.lines_table.itemSelectionChanged.connect(self.on_line_selection_changed)
        self.lines_table.doubleClicked.connect(self.edit_line)

        lines_layout.addWidget(self.lines_table)

        lines_group.setLayout(lines_layout)
        layout.addWidget(lines_group)

        # Resumen de totales
        totals_group = QGroupBox("Resumen de Totales")
        totals_layout = QFormLayout()

        self.total_materiales_coste_label = QLabel("0,00 €")
        self.total_materiales_venta_label = QLabel("0,00 €")
        self.ganancia_materiales_label = QLabel("0,00 €")
        self.subtotal_label = QLabel("0,00 €")
        self.descuento_importe_label = QLabel("0,00 €")
        self.total_final_label = QLabel("0,00 €")
        self.total_final_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        totals_layout.addRow("Total Materiales (Coste):", self.total_materiales_coste_label)
        totals_layout.addRow("Total Materiales (Venta):", self.total_materiales_venta_label)
        totals_layout.addRow("Ganancia en Materiales:", self.ganancia_materiales_label)
        totals_layout.addRow("Subtotal:", self.subtotal_label)
        totals_layout.addRow("Descuento:", self.descuento_importe_label)
        totals_layout.addRow("TOTAL FINAL:", self.total_final_label)

        totals_group.setLayout(totals_layout)
        layout.addWidget(totals_group)

        # Botones
        buttons_layout = QHBoxLayout()

        self.preview_button = QPushButton("👁️ Vista Previa")
        self.preview_button.clicked.connect(self.preview_quote)
        buttons_layout.addWidget(self.preview_button)

        buttons_layout.addStretch()

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save |
                                       QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_quote)
        button_box.rejected.connect(self.reject)
        buttons_layout.addWidget(button_box)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Cargar clientes
        self.load_clientes()

        # Generar número de presupuesto si es nuevo
        if not self.presupuesto:
            self.generar_numero()

    def load_clientes(self):
        """Carga los clientes en el combo"""
        try:
            dao = ClienteDAO(self.db)
            clientes = dao.obtener_todos()

            self.cliente_combo.clear()
            for cliente in clientes:
                display_text = str(cliente)
                self.cliente_combo.addItem(display_text, cliente.id)

        except Exception as e:
            show_error(self, "Error", f"Error al cargar clientes: {str(e)}")

    def new_cliente(self):
        """Crea un nuevo cliente desde el diálogo"""
        dialog = ClientDialog(self, db=self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            show_info(self, "Éxito", "Cliente creado correctamente")
            self.load_clientes()
            # Seleccionar el cliente recién creado
            cliente = dialog.get_cliente()
            for i in range(self.cliente_combo.count()):
                if self.cliente_combo.itemData(i) == cliente.id:
                    self.cliente_combo.setCurrentIndex(i)
                    break

    def generar_numero(self):
        """Genera un nuevo número de presupuesto"""
        try:
            dao = PresupuestoDAO(self.db)
            numero = dao.generar_numero_presupuesto()
            self.numero_input.setText(numero)
        except Exception as e:
            show_error(self, "Error", f"Error al generar número: {str(e)}")

    def add_line(self):
        """Añade una línea al presupuesto"""
        dialog = AddLineDialog(self, db=self.db)
        # Conectar señal de actualización de material
        dialog.material_updated.connect(self.material_updated.emit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            line_data = dialog.get_line_data()
            self.lineas_temp.append(line_data)
            self.refresh_lines_table()
            self.calcular_totales()

    def edit_line(self):
        """Edita una línea del presupuesto"""
        selected_row = self.lines_table.currentRow()
        if selected_row < 0:
            return

        if selected_row >= len(self.lineas_temp):
            return

        # Obtener la línea a editar
        linea_data = self.lineas_temp[selected_row]

        # Crear objeto similar a LineaPresupuesto para el diálogo
        class LineaTemporal:
            def __init__(self, data):
                self.material_id = data['material_id']
                self.cantidad = data['cantidad']
                self.precio_compra_unitario = data['precio_compra_unitario']
                self.margen_ganancia_porc = data['margen_ganancia_porc']
                self.descripcion_personalizada = data.get('descripcion_personalizada', '')

        linea_temp = LineaTemporal(linea_data)

        # Abrir diálogo de edición
        dialog = AddLineDialog(self, db=self.db, linea=linea_temp)
        # Conectar señal de actualización de material
        dialog.material_updated.connect(self.material_updated.emit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Actualizar la línea
            new_data = dialog.get_line_data()
            self.lineas_temp[selected_row] = new_data
            self.refresh_lines_table()
            self.calcular_totales()

    def delete_line(self):
        """Elimina una línea del presupuesto"""
        selected_row = self.lines_table.currentRow()
        if selected_row < 0:
            return

        if confirm_dialog(self, "Confirmar", "¿Eliminar esta línea?"):
            del self.lineas_temp[selected_row]
            self.refresh_lines_table()
            self.calcular_totales()

    def refresh_lines_table(self):
        """Actualiza la tabla de líneas"""
        self.lines_table.setRowCount(0)

        dao_material = MaterialDAO(self.db)

        for line_data in self.lineas_temp:
            material = dao_material.obtener_por_id(line_data['material_id'])
            if not material:
                continue

            row = self.lines_table.rowCount()
            self.lines_table.insertRow(row)

            cantidad = line_data['cantidad']
            precio_compra = line_data['precio_compra_unitario']
            margen = line_data['margen_ganancia_porc']

            precio_venta_unit = precio_compra * (1 + margen / 100)
            total_venta = precio_venta_unit * cantidad

            self.lines_table.setItem(row, 0, QTableWidgetItem(material.nombre))
            self.lines_table.setItem(row, 1, QTableWidgetItem(f"{cantidad:.2f}"))
            self.lines_table.setItem(row, 2, QTableWidgetItem(material.unidad))
            self.lines_table.setItem(row, 3, QTableWidgetItem(format_currency(precio_compra)))
            self.lines_table.setItem(row, 4, QTableWidgetItem(f"{margen:.2f}%"))
            self.lines_table.setItem(row, 5, QTableWidgetItem(format_currency(precio_venta_unit)))
            self.lines_table.setItem(row, 6, QTableWidgetItem(format_currency(total_venta)))

    def calcular_totales(self):
        """Calcula los totales del presupuesto"""
        total_coste = 0.0
        total_venta = 0.0

        for line_data in self.lineas_temp:
            cantidad = line_data['cantidad']
            precio_compra = line_data['precio_compra_unitario']
            margen = line_data['margen_ganancia_porc']

            coste = cantidad * precio_compra
            venta = coste * (1 + margen / 100)

            total_coste += coste
            total_venta += venta

        ganancia = total_venta - total_coste
        coste_mano_obra = self.coste_mano_obra_input.value()
        subtotal = total_venta + coste_mano_obra

        descuento_porc = self.descuento_input.value()
        descuento_importe = subtotal * (descuento_porc / 100)

        total_final = subtotal - descuento_importe

        self.total_materiales_coste_label.setText(format_currency(total_coste))
        self.total_materiales_venta_label.setText(format_currency(total_venta))
        self.ganancia_materiales_label.setText(format_currency(ganancia))
        self.subtotal_label.setText(format_currency(subtotal))
        self.descuento_importe_label.setText(format_currency(descuento_importe))
        self.total_final_label.setText(format_currency(total_final))

    def on_line_selection_changed(self):
        """Maneja el cambio de selección en la tabla de líneas"""
        has_selection = len(self.lines_table.selectedItems()) > 0
        self.edit_line_btn.setEnabled(has_selection)
        self.delete_line_btn.setEnabled(has_selection)

    def load_quote_data(self):
        """Carga los datos de un presupuesto existente"""
        self.numero_input.setText(self.presupuesto.numero)

        # Seleccionar cliente
        for i in range(self.cliente_combo.count()):
            if self.cliente_combo.itemData(i) == self.presupuesto.cliente_id:
                self.cliente_combo.setCurrentIndex(i)
                break

        # Fechas
        fecha = self.presupuesto.fecha_creacion
        qdate = QDate(fecha.year, fecha.month, fecha.day)
        self.fecha_input.setDate(qdate)

        if self.presupuesto.fecha_validez:
            fecha_validez = self.presupuesto.fecha_validez
            qdate_validez = QDate(fecha_validez.year, fecha_validez.month, fecha_validez.day)
            self.fecha_validez_input.setDate(qdate_validez)

        self.titulo_input.setText(self.presupuesto.titulo or "")
        self.descripcion_input.setPlainText(self.presupuesto.descripcion or "")

        # Estado
        index = self.estado_combo.findText(self.presupuesto.estado)
        if index >= 0:
            self.estado_combo.setCurrentIndex(index)

        self.coste_mano_obra_input.setValue(self.presupuesto.coste_mano_obra)
        self.descuento_input.setValue(self.presupuesto.descuento_global)

        # Cargar líneas
        for linea in self.presupuesto.lineas:
            self.lineas_temp.append({
                'id': linea.id,
                'material_id': linea.material_id,
                'cantidad': linea.cantidad,
                'precio_compra_unitario': linea.precio_compra_unitario,
                'margen_ganancia_porc': linea.margen_ganancia_porc,
                'descripcion_personalizada': linea.descripcion_personalizada
            })

        self.refresh_lines_table()
        self.calcular_totales()

    def preview_quote(self):
        """Muestra una vista previa del presupuesto"""
        # Validaciones básicas
        if self.cliente_combo.currentIndex() < 0:
            show_error(self, "Error", "Debe seleccionar un cliente para la vista previa")
            return

        if len(self.lineas_temp) == 0:
            show_error(self, "Error", "Debe añadir al menos una línea para la vista previa")
            return

        try:
            # Crear un presupuesto temporal con los datos actuales
            from src.templates.template_engine import TemplateEngine
            from src.ui.document_viewer import DocumentViewer

            # Obtener datos del cliente
            cliente_dao = ClienteDAO(self.db)
            cliente = cliente_dao.obtener_por_id(self.cliente_combo.currentData())

            # Crear objeto presupuesto temporal
            class PresupuestoTemporal:
                def __init__(self, editor):
                    self.numero = editor.numero_input.text()
                    self.fecha_creacion = datetime(
                        editor.fecha_input.date().year(),
                        editor.fecha_input.date().month(),
                        editor.fecha_input.date().day()
                    )
                    qdate_validez = editor.fecha_validez_input.date()
                    self.fecha_validez = date(qdate_validez.year(), qdate_validez.month(), qdate_validez.day())
                    self.estado = editor.estado_combo.currentText()
                    self.titulo = editor.titulo_input.text()
                    self.descripcion = editor.descripcion_input.toPlainText()
                    self.coste_mano_obra = editor.coste_mano_obra_input.value()
                    self.descuento_global = editor.descuento_input.value()
                    self.notas_internas = ""
                    self.cliente = cliente
                    self.lineas = []

                    # Crear líneas temporales
                    dao_material = MaterialDAO(editor.db)
                    for linea_data in editor.lineas_temp:
                        material = dao_material.obtener_por_id(linea_data['material_id'])
                        linea = type('LineaTemporal', (), {
                            'material': material,
                            'cantidad': linea_data['cantidad'],
                            'precio_compra_unitario': linea_data['precio_compra_unitario'],
                            'margen_ganancia_porc': linea_data['margen_ganancia_porc'],
                            'descripcion_personalizada': linea_data.get('descripcion_personalizada', ''),
                            'coste_total': linea_data['cantidad'] * linea_data['precio_compra_unitario'],
                            'ganancia_importe': (linea_data['cantidad'] * linea_data['precio_compra_unitario']) * (linea_data['margen_ganancia_porc'] / 100),
                            'precio_venta_unitario': linea_data['precio_compra_unitario'] * (1 + linea_data['margen_ganancia_porc'] / 100),
                            'precio_venta_total': (linea_data['cantidad'] * linea_data['precio_compra_unitario']) * (1 + linea_data['margen_ganancia_porc'] / 100)
                        })()
                        self.lineas.append(linea)

                @property
                def total_materiales_coste(self):
                    return sum(l.coste_total for l in self.lineas)

                @property
                def total_materiales_venta(self):
                    return sum(l.precio_venta_total for l in self.lineas)

                @property
                def ganancia_materiales(self):
                    return self.total_materiales_venta - self.total_materiales_coste

                @property
                def subtotal(self):
                    return self.total_materiales_venta + self.coste_mano_obra

                @property
                def descuento_importe(self):
                    return self.subtotal * (self.descuento_global / 100.0)

                @property
                def total_final(self):
                    return self.subtotal - self.descuento_importe

            presupuesto_temp = PresupuestoTemporal(self)

            # Generar HTML
            engine = TemplateEngine()
            html_content = engine.render_quote(presupuesto_temp)

            # Mostrar en visor editable
            viewer = DocumentViewer(
                self,
                html_content,
                f"Vista Previa - Presupuesto {presupuesto_temp.numero}",
                editable=True
            )
            viewer.exec()

        except Exception as e:
            show_error(self, "Error", f"Error al generar vista previa: {str(e)}")

    def save_quote(self):
        """Guarda el presupuesto"""
        # Validaciones
        if self.cliente_combo.currentIndex() < 0:
            show_error(self, "Error", "Debe seleccionar un cliente")
            return

        if len(self.lineas_temp) == 0:
            show_error(self, "Error", "Debe añadir al menos una línea de material")
            return

        try:
            dao = PresupuestoDAO(self.db)
            session = self.db.get_session()

            qdate = self.fecha_input.date()
            fecha = datetime(qdate.year(), qdate.month(), qdate.day())

            qdate_validez = self.fecha_validez_input.date()
            fecha_validez = date(qdate_validez.year(), qdate_validez.month(), qdate_validez.day())

            data = {
                'numero': self.numero_input.text(),
                'cliente_id': self.cliente_combo.currentData(),
                'fecha_creacion': fecha,
                'fecha_validez': fecha_validez,
                'titulo': self.titulo_input.text().strip(),
                'descripcion': self.descripcion_input.toPlainText().strip(),
                'estado': self.estado_combo.currentText(),
                'coste_mano_obra': self.coste_mano_obra_input.value(),
                'descuento_global': self.descuento_input.value()
            }

            if self.presupuesto:
                # Actualizar presupuesto existente
                presupuesto = dao.actualizar(self.presupuesto.id, **data)

                # Eliminar líneas antiguas
                for linea in self.presupuesto.lineas:
                    session.delete(linea)
                session.commit()
            else:
                # Crear nuevo presupuesto
                presupuesto = dao.crear(**data)

            # Añadir líneas
            for orden, line_data in enumerate(self.lineas_temp):
                linea = LineaPresupuesto(
                    presupuesto_id=presupuesto.id,
                    material_id=line_data['material_id'],
                    cantidad=line_data['cantidad'],
                    precio_compra_unitario=line_data['precio_compra_unitario'],
                    margen_ganancia_porc=line_data['margen_ganancia_porc'],
                    descripcion_personalizada=line_data.get('descripcion_personalizada', ''),
                    orden=orden
                )
                session.add(linea)

            session.commit()
            self.db.close_session(session)

            self.presupuesto = presupuesto
            self.accept()

        except Exception as e:
            show_error(self, "Error", f"Error al guardar el presupuesto: {str(e)}")

    def get_presupuesto(self):
        """Retorna el presupuesto creado/editado"""
        return self.presupuesto


class QuotesManager(QWidget):
    """Widget para gestionar presupuestos"""

    quote_selected = pyqtSignal(object)
    material_updated = pyqtSignal(int)  # Señal para propagar actualizaciones de materiales

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.dao = PresupuestoDAO(db)
        self.init_ui()
        self.load_quotes()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()

        # Barra de herramientas
        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar presupuesto...")

        self.new_button = QPushButton("Nuevo Presupuesto")
        self.new_button.clicked.connect(self.new_quote)

        self.edit_button = QPushButton("Editar")
        self.edit_button.clicked.connect(self.edit_quote)
        self.edit_button.setEnabled(False)

        self.view_button = QPushButton("Ver/Generar PDF")
        self.view_button.clicked.connect(self.view_quote)
        self.view_button.setEnabled(False)

        self.delete_button = QPushButton("Eliminar")
        self.delete_button.clicked.connect(self.delete_quote)
        self.delete_button.setEnabled(False)

        toolbar.addWidget(QLabel("Buscar:"))
        toolbar.addWidget(self.search_input)
        toolbar.addStretch()
        toolbar.addWidget(self.new_button)
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.view_button)
        toolbar.addWidget(self.delete_button)

        layout.addLayout(toolbar)

        # Tabla de presupuestos
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Número", "Cliente", "Fecha", "Total", "Estado", "Líneas"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(self.edit_quote)

        # Ocultar columna ID
        self.table.setColumnHidden(0, True)

        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_quotes(self):
        """Carga todos los presupuestos en la tabla"""
        try:
            presupuestos = self.dao.obtener_todos()
            self.populate_table(presupuestos)
        except Exception as e:
            show_error(self, "Error", f"Error al cargar presupuestos: {str(e)}")

    def populate_table(self, presupuestos):
        """Rellena la tabla con los presupuestos"""
        self.table.setRowCount(0)

        for presupuesto in presupuestos:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(presupuesto.id)))
            self.table.setItem(row, 1, QTableWidgetItem(presupuesto.numero))
            self.table.setItem(row, 2, QTableWidgetItem(str(presupuesto.cliente)))
            self.table.setItem(row, 3, QTableWidgetItem(format_date(presupuesto.fecha_creacion)))
            self.table.setItem(row, 4, QTableWidgetItem(format_currency(presupuesto.total_final)))
            self.table.setItem(row, 5, QTableWidgetItem(presupuesto.estado))
            self.table.setItem(row, 6, QTableWidgetItem(str(len(presupuesto.lineas))))

    def new_quote(self):
        """Crea un nuevo presupuesto"""
        dialog = QuoteEditor(self, db=self.db)
        # Conectar señal de actualización de material
        dialog.material_updated.connect(self.material_updated.emit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            show_info(self, "Éxito", "Presupuesto creado correctamente")
            self.load_quotes()

    def edit_quote(self):
        """Edita el presupuesto seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        presupuesto_id = int(self.table.item(selected_row, 0).text())
        presupuesto = self.dao.obtener_por_id(presupuesto_id)

        if not presupuesto:
            show_error(self, "Error", "Presupuesto no encontrado")
            return

        dialog = QuoteEditor(self, db=self.db, presupuesto=presupuesto)
        # Conectar señal de actualización de material
        dialog.material_updated.connect(self.material_updated.emit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            show_info(self, "Éxito", "Presupuesto actualizado correctamente")
            self.load_quotes()

    def view_quote(self):
        """Ver/Generar PDF del presupuesto"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        presupuesto_id = int(self.table.item(selected_row, 0).text())
        presupuesto = self.dao.obtener_por_id(presupuesto_id)

        if not presupuesto:
            show_error(self, "Error", "Presupuesto no encontrado")
            return

        try:
            # Si ya existe HTML guardado, usarlo; si no, generar desde plantilla
            if presupuesto.contenido_html:
                html_content = presupuesto.contenido_html
            else:
                # Generar HTML desde la plantilla
                engine = TemplateEngine()
                html_content = engine.render_quote(presupuesto)

            # Mostrar en el visor con opción de editar
            viewer = DocumentViewer(
                self,
                html_content,
                f"Presupuesto {presupuesto.numero}",
                editable=True
            )

            if viewer.exec() == QDialog.DialogCode.Accepted:
                # Solo guardar si se editó el documento
                if viewer.was_edited():
                    edited_html = viewer.get_html_content()
                    # Guardar el HTML editado en la base de datos
                    self.dao.actualizar(presupuesto.id, contenido_html=edited_html)
                    show_info(self, "Guardado", "Los cambios se han guardado correctamente")

        except Exception as e:
            show_error(self, "Error", f"Error al generar el documento: {str(e)}")

    def delete_quote(self):
        """Elimina el presupuesto seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        presupuesto_id = int(self.table.item(selected_row, 0).text())
        numero = self.table.item(selected_row, 1).text()

        if not confirm_dialog(self, "Confirmar",
                              f"¿Está seguro de eliminar el presupuesto '{numero}'?\n"
                              f"Esta acción es irreversible."):
            return

        try:
            if self.dao.eliminar(presupuesto_id):
                show_info(self, "Éxito", "Presupuesto eliminado correctamente")
                self.load_quotes()
            else:
                show_error(self, "Error", "No se pudo eliminar el presupuesto")
        except Exception as e:
            show_error(self, "Error", f"Error al eliminar el presupuesto: {str(e)}")

    def on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.view_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

        if has_selection:
            selected_row = self.table.currentRow()
            presupuesto_id = int(self.table.item(selected_row, 0).text())
            presupuesto = self.dao.obtener_por_id(presupuesto_id)
            self.quote_selected.emit(presupuesto)
