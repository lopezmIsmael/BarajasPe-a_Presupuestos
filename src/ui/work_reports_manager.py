"""
Gestor de Partes de Trabajo - Interfaz para gestión de partes de trabajo.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                              QHeaderView, QDialog, QFormLayout,
                              QTextEdit, QGroupBox, QDateEdit,
                              QComboBox, QDialogButtonBox, QDoubleSpinBox,
                              QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from datetime import datetime, date
from src.database.database import (ParteTrabajoDAO, PresupuestoDAO, TrabajadorDAO,
                                   MaterialDAO, DetalleManoObra, MaterialUsado, Database)
from src.utils.helpers import (show_error, show_info, confirm_dialog,
                               format_currency, format_date)


class WorkReportEditor(QDialog):
    """Editor de parte de trabajo"""

    def __init__(self, parent=None, db=None, parte=None):
        super().__init__(parent)
        self.db = db
        self.parte = parte
        self.detalles_mano_obra_temp = []
        self.materiales_usados_temp = []
        self.init_ui()

        if parte:
            self.load_work_report_data()

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Nuevo Parte de Trabajo" if not self.parte else "Editar Parte de Trabajo")
        self.setModal(True)
        self.resize(1000, 700)

        layout = QVBoxLayout()

        # Datos del parte
        header_group = QGroupBox("Datos del Parte de Trabajo")
        header_layout = QFormLayout()

        self.numero_input = QLineEdit()
        self.numero_input.setReadOnly(True)

        self.presupuesto_combo = QComboBox()
        self.presupuesto_combo.addItem("(Sin presupuesto asociado)", None)

        self.fecha_inicio_input = QDateEdit()
        self.fecha_inicio_input.setCalendarPopup(True)
        self.fecha_inicio_input.setDate(QDate.currentDate())
        self.fecha_inicio_input.setDisplayFormat("dd/MM/yyyy")

        self.fecha_fin_input = QDateEdit()
        self.fecha_fin_input.setCalendarPopup(True)
        self.fecha_fin_input.setDate(QDate.currentDate())
        self.fecha_fin_input.setDisplayFormat("dd/MM/yyyy")

        self.titulo_input = QLineEdit()
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setMaximumHeight(60)

        self.ubicacion_input = QLineEdit()

        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["en_curso", "finalizado", "facturado"])

        header_layout.addRow("Nº Parte:", self.numero_input)
        header_layout.addRow("Presupuesto:", self.presupuesto_combo)
        header_layout.addRow("Fecha Inicio*:", self.fecha_inicio_input)
        header_layout.addRow("Fecha Fin:", self.fecha_fin_input)
        header_layout.addRow("Título*:", self.titulo_input)
        header_layout.addRow("Descripción:", self.descripcion_input)
        header_layout.addRow("Ubicación:", self.ubicacion_input)
        header_layout.addRow("Estado:", self.estado_combo)

        header_group.setLayout(header_layout)
        layout.addWidget(header_group)

        # Tabs para mano de obra y materiales
        tabs = QTabWidget()

        # Tab de Mano de Obra
        mano_obra_tab = QWidget()
        mano_obra_layout = QVBoxLayout()

        mano_obra_toolbar = QHBoxLayout()
        self.add_mano_obra_btn = QPushButton("Añadir Trabajo")
        self.add_mano_obra_btn.clicked.connect(self.add_mano_obra)
        self.delete_mano_obra_btn = QPushButton("Eliminar")
        self.delete_mano_obra_btn.clicked.connect(self.delete_mano_obra)
        self.delete_mano_obra_btn.setEnabled(False)

        mano_obra_toolbar.addWidget(self.add_mano_obra_btn)
        mano_obra_toolbar.addWidget(self.delete_mano_obra_btn)
        mano_obra_toolbar.addStretch()

        mano_obra_layout.addLayout(mano_obra_toolbar)

        self.mano_obra_table = QTableWidget()
        self.mano_obra_table.setColumnCount(6)
        self.mano_obra_table.setHorizontalHeaderLabels([
            "Trabajador", "Fecha", "Horas", "Coste/Hora", "Total", "Labor Realizada"
        ])
        self.mano_obra_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.mano_obra_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.mano_obra_table.itemSelectionChanged.connect(self.on_mano_obra_selection_changed)

        mano_obra_layout.addWidget(self.mano_obra_table)

        # Total mano de obra
        total_mo_layout = QHBoxLayout()
        total_mo_layout.addStretch()
        total_mo_layout.addWidget(QLabel("Total Mano de Obra:"))
        self.total_mano_obra_label = QLabel("0,00 €")
        self.total_mano_obra_label.setStyleSheet("font-weight: bold;")
        total_mo_layout.addWidget(self.total_mano_obra_label)
        mano_obra_layout.addLayout(total_mo_layout)

        mano_obra_tab.setLayout(mano_obra_layout)
        tabs.addTab(mano_obra_tab, "Mano de Obra")

        # Tab de Materiales
        materiales_tab = QWidget()
        materiales_layout = QVBoxLayout()

        materiales_toolbar = QHBoxLayout()
        self.add_material_btn = QPushButton("Añadir Material")
        self.add_material_btn.clicked.connect(self.add_material)
        self.delete_material_btn = QPushButton("Eliminar")
        self.delete_material_btn.clicked.connect(self.delete_material)
        self.delete_material_btn.setEnabled(False)

        materiales_toolbar.addWidget(self.add_material_btn)
        materiales_toolbar.addWidget(self.delete_material_btn)
        materiales_toolbar.addStretch()

        materiales_layout.addLayout(materiales_toolbar)

        self.materiales_table = QTableWidget()
        self.materiales_table.setColumnCount(6)
        self.materiales_table.setHorizontalHeaderLabels([
            "Material", "Fecha", "Cantidad", "Unidad", "P. Unit.", "Total"
        ])
        self.materiales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.materiales_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.materiales_table.itemSelectionChanged.connect(self.on_material_selection_changed)

        materiales_layout.addWidget(self.materiales_table)

        # Total materiales
        total_mat_layout = QHBoxLayout()
        total_mat_layout.addStretch()
        total_mat_layout.addWidget(QLabel("Total Materiales:"))
        self.total_materiales_label = QLabel("0,00 €")
        self.total_materiales_label.setStyleSheet("font-weight: bold;")
        total_mat_layout.addWidget(self.total_materiales_label)
        materiales_layout.addLayout(total_mat_layout)

        materiales_tab.setLayout(materiales_layout)
        tabs.addTab(materiales_tab, "Materiales Usados")

        layout.addWidget(tabs)

        # Resumen total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(QLabel("COSTE TOTAL DEL PARTE:"))
        self.total_parte_label = QLabel("0,00 €")
        self.total_parte_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        total_layout.addWidget(self.total_parte_label)
        layout.addLayout(total_layout)

        # Botones
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save |
                                       QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_work_report)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        # Cargar presupuestos
        self.load_presupuestos()

        # Generar número de parte si es nuevo
        if not self.parte:
            self.generar_numero()

    def load_presupuestos(self):
        """Carga los presupuestos en el combo"""
        try:
            dao = PresupuestoDAO(self.db)
            presupuestos = dao.obtener_todos()

            for presupuesto in presupuestos:
                display_text = f"{presupuesto.numero} - {presupuesto.cliente}"
                self.presupuesto_combo.addItem(display_text, presupuesto.id)

        except Exception as e:
            show_error(self, "Error", f"Error al cargar presupuestos: {str(e)}")

    def generar_numero(self):
        """Genera un nuevo número de parte"""
        try:
            dao = ParteTrabajoDAO(self.db)
            numero = dao.generar_numero_parte()
            self.numero_input.setText(numero)
        except Exception as e:
            show_error(self, "Error", f"Error al generar número: {str(e)}")

    def add_mano_obra(self):
        """Añade un detalle de mano de obra"""
        dialog = AddManoObraDialog(self, db=self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            detalle = dialog.get_data()
            self.detalles_mano_obra_temp.append(detalle)
            self.refresh_mano_obra_table()
            self.calcular_totales()

    def delete_mano_obra(self):
        """Elimina un detalle de mano de obra"""
        selected_row = self.mano_obra_table.currentRow()
        if selected_row < 0:
            return

        if confirm_dialog(self, "Confirmar", "¿Eliminar este registro?"):
            del self.detalles_mano_obra_temp[selected_row]
            self.refresh_mano_obra_table()
            self.calcular_totales()

    def add_material(self):
        """Añade un material usado"""
        dialog = AddMaterialUsadoDialog(self, db=self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            material = dialog.get_data()
            self.materiales_usados_temp.append(material)
            self.refresh_materiales_table()
            self.calcular_totales()

    def delete_material(self):
        """Elimina un material usado"""
        selected_row = self.materiales_table.currentRow()
        if selected_row < 0:
            return

        if confirm_dialog(self, "Confirmar", "¿Eliminar este registro?"):
            del self.materiales_usados_temp[selected_row]
            self.refresh_materiales_table()
            self.calcular_totales()

    def refresh_mano_obra_table(self):
        """Actualiza la tabla de mano de obra"""
        self.mano_obra_table.setRowCount(0)

        dao_trabajador = TrabajadorDAO(self.db)

        for detalle in self.detalles_mano_obra_temp:
            trabajador = dao_trabajador.obtener_por_id(detalle['trabajador_id'])
            if not trabajador:
                continue

            row = self.mano_obra_table.rowCount()
            self.mano_obra_table.insertRow(row)

            horas = detalle['horas']
            coste_hora = detalle['coste_hora_aplicado']
            total = horas * coste_hora

            self.mano_obra_table.setItem(row, 0, QTableWidgetItem(str(trabajador)))
            self.mano_obra_table.setItem(row, 1, QTableWidgetItem(format_date(detalle['fecha'])))
            self.mano_obra_table.setItem(row, 2, QTableWidgetItem(f"{horas:.2f}"))
            self.mano_obra_table.setItem(row, 3, QTableWidgetItem(format_currency(coste_hora)))
            self.mano_obra_table.setItem(row, 4, QTableWidgetItem(format_currency(total)))
            self.mano_obra_table.setItem(row, 5, QTableWidgetItem(detalle['labor_realizada'][:50]))

    def refresh_materiales_table(self):
        """Actualiza la tabla de materiales"""
        self.materiales_table.setRowCount(0)

        dao_material = MaterialDAO(self.db)

        for mat_usado in self.materiales_usados_temp:
            material = dao_material.obtener_por_id(mat_usado['material_id'])
            if not material:
                continue

            row = self.materiales_table.rowCount()
            self.materiales_table.insertRow(row)

            cantidad = mat_usado['cantidad']
            precio = mat_usado['precio_compra_unitario']
            total = cantidad * precio

            self.materiales_table.setItem(row, 0, QTableWidgetItem(material.nombre))
            self.materiales_table.setItem(row, 1, QTableWidgetItem(format_date(mat_usado['fecha_uso'])))
            self.materiales_table.setItem(row, 2, QTableWidgetItem(f"{cantidad:.2f}"))
            self.materiales_table.setItem(row, 3, QTableWidgetItem(material.unidad))
            self.materiales_table.setItem(row, 4, QTableWidgetItem(format_currency(precio)))
            self.materiales_table.setItem(row, 5, QTableWidgetItem(format_currency(total)))

    def calcular_totales(self):
        """Calcula los totales del parte"""
        total_mano_obra = sum(d['horas'] * d['coste_hora_aplicado'] for d in self.detalles_mano_obra_temp)
        total_materiales = sum(m['cantidad'] * m['precio_compra_unitario'] for m in self.materiales_usados_temp)
        total_parte = total_mano_obra + total_materiales

        self.total_mano_obra_label.setText(format_currency(total_mano_obra))
        self.total_materiales_label.setText(format_currency(total_materiales))
        self.total_parte_label.setText(format_currency(total_parte))

    def on_mano_obra_selection_changed(self):
        """Maneja la selección en tabla de mano de obra"""
        has_selection = len(self.mano_obra_table.selectedItems()) > 0
        self.delete_mano_obra_btn.setEnabled(has_selection)

    def on_material_selection_changed(self):
        """Maneja la selección en tabla de materiales"""
        has_selection = len(self.materiales_table.selectedItems()) > 0
        self.delete_material_btn.setEnabled(has_selection)

    def load_work_report_data(self):
        """Carga los datos de un parte existente"""
        self.numero_input.setText(self.parte.numero)

        # Seleccionar presupuesto
        if self.parte.presupuesto_id:
            for i in range(self.presupuesto_combo.count()):
                if self.presupuesto_combo.itemData(i) == self.parte.presupuesto_id:
                    self.presupuesto_combo.setCurrentIndex(i)
                    break

        # Fechas
        fecha_inicio = self.parte.fecha_inicio
        qdate_inicio = QDate(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day)
        self.fecha_inicio_input.setDate(qdate_inicio)

        if self.parte.fecha_fin:
            fecha_fin = self.parte.fecha_fin
            qdate_fin = QDate(fecha_fin.year, fecha_fin.month, fecha_fin.day)
            self.fecha_fin_input.setDate(qdate_fin)

        self.titulo_input.setText(self.parte.titulo or "")
        self.descripcion_input.setPlainText(self.parte.descripcion or "")
        self.ubicacion_input.setText(self.parte.ubicacion or "")

        # Estado
        index = self.estado_combo.findText(self.parte.estado)
        if index >= 0:
            self.estado_combo.setCurrentIndex(index)

        # Cargar detalles de mano de obra
        for detalle in self.parte.detalles_mano_obra:
            self.detalles_mano_obra_temp.append({
                'id': detalle.id,
                'trabajador_id': detalle.trabajador_id,
                'fecha': detalle.fecha,
                'horas': detalle.horas,
                'coste_hora_aplicado': detalle.coste_hora_aplicado,
                'labor_realizada': detalle.labor_realizada,
                'comentarios': detalle.comentarios
            })

        # Cargar materiales usados
        for mat_usado in self.parte.materiales_usados:
            self.materiales_usados_temp.append({
                'id': mat_usado.id,
                'material_id': mat_usado.material_id,
                'cantidad': mat_usado.cantidad,
                'precio_compra_unitario': mat_usado.precio_compra_unitario,
                'fecha_uso': mat_usado.fecha_uso,
                'comentarios': mat_usado.comentarios
            })

        self.refresh_mano_obra_table()
        self.refresh_materiales_table()
        self.calcular_totales()

    def save_work_report(self):
        """Guarda el parte de trabajo"""
        if not self.titulo_input.text().strip():
            show_error(self, "Error", "El título es obligatorio")
            return

        try:
            dao = ParteTrabajoDAO(self.db)
            session = self.db.get_session()

            qdate_inicio = self.fecha_inicio_input.date()
            fecha_inicio = date(qdate_inicio.year(), qdate_inicio.month(), qdate_inicio.day())

            qdate_fin = self.fecha_fin_input.date()
            fecha_fin = date(qdate_fin.year(), qdate_fin.month(), qdate_fin.day())

            presupuesto_id = self.presupuesto_combo.currentData()

            data = {
                'numero': self.numero_input.text(),
                'presupuesto_id': presupuesto_id if presupuesto_id else None,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'titulo': self.titulo_input.text().strip(),
                'descripcion': self.descripcion_input.toPlainText().strip(),
                'ubicacion': self.ubicacion_input.text().strip(),
                'estado': self.estado_combo.currentText()
            }

            if self.parte:
                # Actualizar parte existente
                parte = dao.actualizar(self.parte.id, **data)

                # Eliminar detalles antiguos
                for detalle in self.parte.detalles_mano_obra:
                    session.delete(detalle)
                for mat_usado in self.parte.materiales_usados:
                    session.delete(mat_usado)
                session.commit()
            else:
                # Crear nuevo parte
                parte = dao.crear(**data)

            # Añadir detalles de mano de obra
            for detalle_data in self.detalles_mano_obra_temp:
                detalle = DetalleManoObra(
                    parte_trabajo_id=parte.id,
                    trabajador_id=detalle_data['trabajador_id'],
                    fecha=detalle_data['fecha'],
                    horas=detalle_data['horas'],
                    coste_hora_aplicado=detalle_data['coste_hora_aplicado'],
                    labor_realizada=detalle_data['labor_realizada'],
                    comentarios=detalle_data.get('comentarios', '')
                )
                session.add(detalle)

            # Añadir materiales usados
            for mat_data in self.materiales_usados_temp:
                mat_usado = MaterialUsado(
                    parte_trabajo_id=parte.id,
                    material_id=mat_data['material_id'],
                    cantidad=mat_data['cantidad'],
                    precio_compra_unitario=mat_data['precio_compra_unitario'],
                    fecha_uso=mat_data['fecha_uso'],
                    comentarios=mat_data.get('comentarios', '')
                )
                session.add(mat_usado)

            session.commit()
            self.db.close_session(session)

            self.parte = parte
            self.accept()

        except Exception as e:
            show_error(self, "Error", f"Error al guardar el parte: {str(e)}")

    def get_parte(self):
        """Retorna el parte creado/editado"""
        return self.parte


class AddManoObraDialog(QDialog):
    """Diálogo para añadir un detalle de mano de obra"""

    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
        self.load_trabajadores()

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Añadir Trabajo Realizado")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QFormLayout()

        self.trabajador_combo = QComboBox()
        self.trabajador_combo.currentIndexChanged.connect(self.on_trabajador_changed)

        self.fecha_input = QDateEdit()
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setDisplayFormat("dd/MM/yyyy")

        self.horas_input = QDoubleSpinBox()
        self.horas_input.setRange(0.01, 24.0)
        self.horas_input.setDecimals(2)
        self.horas_input.setValue(8.0)
        self.horas_input.setSuffix(" h")

        self.coste_hora_input = QDoubleSpinBox()
        self.coste_hora_input.setRange(0, 999.99)
        self.coste_hora_input.setDecimals(2)
        self.coste_hora_input.setSuffix(" €/h")

        self.labor_input = QTextEdit()
        self.labor_input.setMaximumHeight(80)

        self.comentarios_input = QTextEdit()
        self.comentarios_input.setMaximumHeight(60)

        layout.addRow("Trabajador*:", self.trabajador_combo)
        layout.addRow("Fecha*:", self.fecha_input)
        layout.addRow("Horas*:", self.horas_input)
        layout.addRow("Coste/Hora*:", self.coste_hora_input)
        layout.addRow("Labor Realizada*:", self.labor_input)
        layout.addRow("Comentarios:", self.comentarios_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                       QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_dialog)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def load_trabajadores(self):
        """Carga los trabajadores en el combo"""
        try:
            dao = TrabajadorDAO(self.db)
            trabajadores = dao.obtener_todos()

            self.trabajador_combo.clear()
            for trabajador in trabajadores:
                self.trabajador_combo.addItem(str(trabajador), trabajador.id)

        except Exception as e:
            show_error(self, "Error", f"Error al cargar trabajadores: {str(e)}")

    def on_trabajador_changed(self, index):
        """Auto-rellena el coste/hora del trabajador"""
        if index < 0:
            return

        trabajador_id = self.trabajador_combo.currentData()
        dao = TrabajadorDAO(self.db)
        trabajador = dao.obtener_por_id(trabajador_id)

        if trabajador:
            self.coste_hora_input.setValue(trabajador.coste_hora)

    def accept_dialog(self):
        """Valida y acepta"""
        if self.trabajador_combo.currentIndex() < 0:
            show_error(self, "Error", "Debe seleccionar un trabajador")
            return

        if not self.labor_input.toPlainText().strip():
            show_error(self, "Error", "Debe describir la labor realizada")
            return

        self.accept()

    def get_data(self):
        """Retorna los datos"""
        qdate = self.fecha_input.date()
        fecha = date(qdate.year(), qdate.month(), qdate.day())

        return {
            'trabajador_id': self.trabajador_combo.currentData(),
            'fecha': fecha,
            'horas': self.horas_input.value(),
            'coste_hora_aplicado': self.coste_hora_input.value(),
            'labor_realizada': self.labor_input.toPlainText().strip(),
            'comentarios': self.comentarios_input.toPlainText().strip()
        }


class AddMaterialUsadoDialog(QDialog):
    """Diálogo para añadir un material usado"""

    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
        self.load_materiales()

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Añadir Material Usado")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QFormLayout()

        self.material_combo = QComboBox()
        self.material_combo.currentIndexChanged.connect(self.on_material_changed)

        self.fecha_input = QDateEdit()
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setDisplayFormat("dd/MM/yyyy")

        self.cantidad_input = QDoubleSpinBox()
        self.cantidad_input.setRange(0.01, 999999.99)
        self.cantidad_input.setDecimals(2)
        self.cantidad_input.setValue(1.0)

        self.precio_input = QDoubleSpinBox()
        self.precio_input.setRange(0, 999999.99)
        self.precio_input.setDecimals(2)
        self.precio_input.setSuffix(" €")

        self.comentarios_input = QTextEdit()
        self.comentarios_input.setMaximumHeight(60)

        layout.addRow("Material*:", self.material_combo)
        layout.addRow("Fecha*:", self.fecha_input)
        layout.addRow("Cantidad*:", self.cantidad_input)
        layout.addRow("Precio Unitario*:", self.precio_input)
        layout.addRow("Comentarios:", self.comentarios_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                       QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_dialog)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def load_materiales(self):
        """Carga los materiales en el combo"""
        try:
            dao = MaterialDAO(self.db)
            materiales = dao.obtener_todos()

            self.material_combo.clear()
            for material in materiales:
                self.material_combo.addItem(
                    f"{material.nombre} ({material.unidad})",
                    material.id
                )

        except Exception as e:
            show_error(self, "Error", f"Error al cargar materiales: {str(e)}")

    def on_material_changed(self, index):
        """Auto-rellena el precio del material"""
        if index < 0:
            return

        material_id = self.material_combo.currentData()
        dao = MaterialDAO(self.db)
        material = dao.obtener_por_id(material_id)

        if material:
            self.precio_input.setValue(material.precio_compra)

    def accept_dialog(self):
        """Valida y acepta"""
        if self.material_combo.currentIndex() < 0:
            show_error(self, "Error", "Debe seleccionar un material")
            return

        self.accept()

    def get_data(self):
        """Retorna los datos"""
        qdate = self.fecha_input.date()
        fecha = date(qdate.year(), qdate.month(), qdate.day())

        return {
            'material_id': self.material_combo.currentData(),
            'fecha_uso': fecha,
            'cantidad': self.cantidad_input.value(),
            'precio_compra_unitario': self.precio_input.value(),
            'comentarios': self.comentarios_input.toPlainText().strip()
        }


class WorkReportsManager(QWidget):
    """Widget para gestionar partes de trabajo"""

    report_selected = pyqtSignal(object)

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.dao = ParteTrabajoDAO(db)
        self.init_ui()
        self.load_reports()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()

        # Barra de herramientas
        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar parte...")

        self.new_button = QPushButton("Nuevo Parte")
        self.new_button.clicked.connect(self.new_report)

        self.edit_button = QPushButton("Editar")
        self.edit_button.clicked.connect(self.edit_report)
        self.edit_button.setEnabled(False)

        self.view_button = QPushButton("Ver/Generar PDF")
        self.view_button.clicked.connect(self.view_report)
        self.view_button.setEnabled(False)

        self.delete_button = QPushButton("Eliminar")
        self.delete_button.clicked.connect(self.delete_report)
        self.delete_button.setEnabled(False)

        toolbar.addWidget(QLabel("Buscar:"))
        toolbar.addWidget(self.search_input)
        toolbar.addStretch()
        toolbar.addWidget(self.new_button)
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.view_button)
        toolbar.addWidget(self.delete_button)

        layout.addLayout(toolbar)

        # Tabla de partes
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Número", "Título", "Fecha Inicio", "Total", "Horas", "Estado"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(self.edit_report)

        # Ocultar columna ID
        self.table.setColumnHidden(0, True)

        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_reports(self):
        """Carga todos los partes en la tabla"""
        try:
            partes = self.dao.obtener_todos()
            self.populate_table(partes)
        except Exception as e:
            show_error(self, "Error", f"Error al cargar partes: {str(e)}")

    def populate_table(self, partes):
        """Rellena la tabla con los partes"""
        self.table.setRowCount(0)

        for parte in partes:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(parte.id)))
            self.table.setItem(row, 1, QTableWidgetItem(parte.numero))
            self.table.setItem(row, 2, QTableWidgetItem(parte.titulo))
            self.table.setItem(row, 3, QTableWidgetItem(format_date(parte.fecha_inicio)))
            self.table.setItem(row, 4, QTableWidgetItem(format_currency(parte.coste_total)))
            self.table.setItem(row, 5, QTableWidgetItem(f"{parte.total_horas:.2f}h"))
            self.table.setItem(row, 6, QTableWidgetItem(parte.estado))

    def new_report(self):
        """Crea un nuevo parte"""
        dialog = WorkReportEditor(self, db=self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            show_info(self, "Éxito", "Parte creado correctamente")
            self.load_reports()

    def edit_report(self):
        """Edita el parte seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        parte_id = int(self.table.item(selected_row, 0).text())
        parte = self.dao.obtener_por_id(parte_id)

        if not parte:
            show_error(self, "Error", "Parte no encontrado")
            return

        dialog = WorkReportEditor(self, db=self.db, parte=parte)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            show_info(self, "Éxito", "Parte actualizado correctamente")
            self.load_reports()

    def view_report(self):
        """Ver/Generar PDF del parte"""
        show_info(self, "Info", "Función de generación de PDF en desarrollo (Fase 3)")

    def delete_report(self):
        """Elimina el parte seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        parte_id = int(self.table.item(selected_row, 0).text())
        numero = self.table.item(selected_row, 1).text()

        if not confirm_dialog(self, "Confirmar",
                              f"¿Está seguro de eliminar el parte '{numero}'?\n"
                              f"Esta acción es irreversible."):
            return

        try:
            if self.dao.eliminar(parte_id):
                show_info(self, "Éxito", "Parte eliminado correctamente")
                self.load_reports()
            else:
                show_error(self, "Error", "No se pudo eliminar el parte")
        except Exception as e:
            show_error(self, "Error", f"Error al eliminar el parte: {str(e)}")

    def on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.view_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

        if has_selection:
            selected_row = self.table.currentRow()
            parte_id = int(self.table.item(selected_row, 0).text())
            parte = self.dao.obtener_por_id(parte_id)
            self.report_selected.emit(parte)
