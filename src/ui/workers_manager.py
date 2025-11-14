"""
Gestor de Trabajadores - Interfaz CRUD para gestión de trabajadores.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                              QMessageBox, QHeaderView, QDialog, QFormLayout,
                              QTextEdit, QGroupBox, QDoubleSpinBox, QDateEdit,
                              QCheckBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from datetime import date
from src.database.database import TrabajadorDAO, Database
from src.utils.helpers import (show_error, show_info, confirm_dialog,
                               format_currency, format_date, adjust_dialog_to_screen)


class WorkerDialog(QDialog):
    """Diálogo para crear/editar un trabajador"""

    def __init__(self, parent=None, trabajador=None, db=None):
        super().__init__(parent)
        self.trabajador = trabajador
        self.db = db
        self.init_ui()

        if trabajador:
            self.load_data()

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Nuevo Trabajador" if not self.trabajador else "Editar Trabajador")
        self.setModal(True)
        # Ajustar tamaño al monitor disponible
        adjust_dialog_to_screen(self, preferred_width=650, preferred_height=600, min_width=500, min_height=450)

        # Layout principal
        main_layout = QVBoxLayout()

        # Widget de contenido scrollable
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Grupo de datos personales
        personal_group = QGroupBox("Datos Personales")
        personal_layout = QFormLayout()

        self.nombre_input = QLineEdit()
        self.apellidos_input = QLineEdit()
        self.dni_input = QLineEdit()

        personal_layout.addRow("Nombre*:", self.nombre_input)
        personal_layout.addRow("Apellidos*:", self.apellidos_input)
        personal_layout.addRow("DNI:", self.dni_input)

        personal_group.setLayout(personal_layout)
        content_layout.addWidget(personal_group)

        # Grupo de contacto
        contacto_group = QGroupBox("Contacto")
        contacto_layout = QFormLayout()

        self.telefono_input = QLineEdit()
        self.email_input = QLineEdit()
        self.direccion_input = QLineEdit()

        contacto_layout.addRow("Teléfono:", self.telefono_input)
        contacto_layout.addRow("Email:", self.email_input)
        contacto_layout.addRow("Dirección:", self.direccion_input)

        contacto_group.setLayout(contacto_layout)
        content_layout.addWidget(contacto_group)

        # Grupo de datos laborales
        laboral_group = QGroupBox("Datos Laborales")
        laboral_layout = QFormLayout()

        self.puesto_input = QLineEdit()

        self.coste_hora_input = QDoubleSpinBox()
        self.coste_hora_input.setRange(0, 999.99)
        self.coste_hora_input.setDecimals(2)
        self.coste_hora_input.setSuffix(" €/h")
        self.coste_hora_input.setGroupSeparatorShown(True)

        self.fecha_alta_input = QDateEdit()
        self.fecha_alta_input.setCalendarPopup(True)
        self.fecha_alta_input.setDate(QDate.currentDate())
        self.fecha_alta_input.setDisplayFormat("dd/MM/yyyy")

        self.activo_checkbox = QCheckBox("Trabajador activo")
        self.activo_checkbox.setChecked(True)

        laboral_layout.addRow("Puesto:", self.puesto_input)
        laboral_layout.addRow("Coste por Hora*:", self.coste_hora_input)
        laboral_layout.addRow("Fecha de Alta:", self.fecha_alta_input)
        laboral_layout.addRow("", self.activo_checkbox)

        laboral_group.setLayout(laboral_layout)
        content_layout.addWidget(laboral_group)

        # Notas
        notas_group = QGroupBox("Notas")
        notas_layout = QVBoxLayout()
        self.notas_input = QTextEdit()
        self.notas_input.setMaximumHeight(80)
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

    def load_data(self):
        """Carga los datos del trabajador en el formulario"""
        self.nombre_input.setText(self.trabajador.nombre or "")
        self.apellidos_input.setText(self.trabajador.apellidos or "")
        self.dni_input.setText(self.trabajador.dni or "")
        self.telefono_input.setText(self.trabajador.telefono or "")
        self.email_input.setText(self.trabajador.email or "")
        self.direccion_input.setText(self.trabajador.direccion or "")
        self.puesto_input.setText(self.trabajador.puesto or "")
        self.coste_hora_input.setValue(self.trabajador.coste_hora)

        if self.trabajador.fecha_alta:
            qdate = QDate(self.trabajador.fecha_alta.year,
                          self.trabajador.fecha_alta.month,
                          self.trabajador.fecha_alta.day)
            self.fecha_alta_input.setDate(qdate)

        self.activo_checkbox.setChecked(self.trabajador.activo == 1)
        self.notas_input.setPlainText(self.trabajador.notas or "")

    def validate_form(self):
        """Valida los datos del formulario"""
        if not self.nombre_input.text().strip():
            show_error(self, "Error", "El nombre es obligatorio")
            return False

        if not self.apellidos_input.text().strip():
            show_error(self, "Error", "Los apellidos son obligatorios")
            return False

        if self.coste_hora_input.value() <= 0:
            show_error(self, "Error", "El coste por hora debe ser mayor que 0")
            return False

        return True

    def save(self):
        """Guarda el trabajador"""
        if not self.validate_form():
            return

        try:
            dao = TrabajadorDAO(self.db)

            qdate = self.fecha_alta_input.date()
            fecha_alta = date(qdate.year(), qdate.month(), qdate.day())

            data = {
                'nombre': self.nombre_input.text().strip(),
                'apellidos': self.apellidos_input.text().strip(),
                'dni': self.dni_input.text().strip(),
                'telefono': self.telefono_input.text().strip(),
                'email': self.email_input.text().strip(),
                'direccion': self.direccion_input.text().strip(),
                'puesto': self.puesto_input.text().strip(),
                'coste_hora': self.coste_hora_input.value(),
                'fecha_alta': fecha_alta,
                'activo': 1 if self.activo_checkbox.isChecked() else 0,
                'notas': self.notas_input.toPlainText().strip()
            }

            if self.trabajador:
                # Actualizar
                dao.actualizar(self.trabajador.id, **data)
            else:
                # Crear
                self.trabajador = dao.crear(**data)

            self.accept()

        except Exception as e:
            show_error(self, "Error", f"Error al guardar el trabajador: {str(e)}")

    def get_trabajador(self):
        """Retorna el trabajador creado/editado"""
        return self.trabajador


class WorkersManager(QWidget):
    """Widget para gestionar trabajadores"""

    worker_selected = pyqtSignal(object)  # Señal cuando se selecciona un trabajador

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.dao = TrabajadorDAO(db)
        self.init_ui()
        self.load_workers()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()

        # Barra de herramientas
        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar trabajador...")
        self.search_input.textChanged.connect(self.search_workers)

        self.show_inactive_checkbox = QCheckBox("Mostrar inactivos")
        self.show_inactive_checkbox.stateChanged.connect(self.load_workers)

        self.new_button = QPushButton("Nuevo Trabajador")
        self.new_button.clicked.connect(self.new_worker)

        self.edit_button = QPushButton("Editar")
        self.edit_button.clicked.connect(self.edit_worker)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("Desactivar")
        self.delete_button.clicked.connect(self.delete_worker)
        self.delete_button.setEnabled(False)

        toolbar.addWidget(QLabel("Buscar:"))
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.show_inactive_checkbox)
        toolbar.addStretch()
        toolbar.addWidget(self.new_button)
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.delete_button)

        layout.addLayout(toolbar)

        # Tabla de trabajadores
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Apellidos", "Puesto", "Coste/Hora", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(self.edit_worker)

        # Ocultar columna ID
        self.table.setColumnHidden(0, True)

        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_workers(self):
        """Carga todos los trabajadores en la tabla"""
        try:
            solo_activos = not self.show_inactive_checkbox.isChecked()
            trabajadores = self.dao.obtener_todos(solo_activos=solo_activos)
            self.populate_table(trabajadores)
        except Exception as e:
            show_error(self, "Error", f"Error al cargar trabajadores: {str(e)}")

    def populate_table(self, trabajadores):
        """Rellena la tabla con los trabajadores"""
        self.table.setRowCount(0)

        for trabajador in trabajadores:
            row = self.table.rowCount()
            self.table.insertRow(row)

            estado = "Activo" if trabajador.activo == 1 else "Inactivo"

            self.table.setItem(row, 0, QTableWidgetItem(str(trabajador.id)))
            self.table.setItem(row, 1, QTableWidgetItem(trabajador.nombre or ""))
            self.table.setItem(row, 2, QTableWidgetItem(trabajador.apellidos or ""))
            self.table.setItem(row, 3, QTableWidgetItem(trabajador.puesto or ""))
            self.table.setItem(row, 4, QTableWidgetItem(format_currency(trabajador.coste_hora)))
            self.table.setItem(row, 5, QTableWidgetItem(estado))

    def search_workers(self):
        """Busca trabajadores por el criterio introducido"""
        criterio = self.search_input.text().strip()

        if not criterio:
            self.load_workers()
            return

        try:
            trabajadores = self.dao.buscar(criterio)
            self.populate_table(trabajadores)
        except Exception as e:
            show_error(self, "Error", f"Error al buscar trabajadores: {str(e)}")

    def new_worker(self):
        """Crea un nuevo trabajador"""
        dialog = WorkerDialog(self, db=self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            show_info(self, "Éxito", "Trabajador creado correctamente")
            self.load_workers()

    def edit_worker(self):
        """Edita el trabajador seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        trabajador_id = int(self.table.item(selected_row, 0).text())
        trabajador = self.dao.obtener_por_id(trabajador_id)

        if not trabajador:
            show_error(self, "Error", "Trabajador no encontrado")
            return

        dialog = WorkerDialog(self, trabajador=trabajador, db=self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            show_info(self, "Éxito", "Trabajador actualizado correctamente")
            self.load_workers()

    def delete_worker(self):
        """Desactiva el trabajador seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        trabajador_id = int(self.table.item(selected_row, 0).text())
        nombre = self.table.item(selected_row, 1).text()
        apellidos = self.table.item(selected_row, 2).text()

        if not confirm_dialog(self, "Confirmar",
                              f"¿Está seguro de desactivar el trabajador '{nombre} {apellidos}'?"):
            return

        try:
            if self.dao.eliminar(trabajador_id):
                show_info(self, "Éxito", "Trabajador desactivado correctamente")
                self.load_workers()
            else:
                show_error(self, "Error", "No se pudo desactivar el trabajador")
        except Exception as e:
            show_error(self, "Error", f"Error al desactivar el trabajador: {str(e)}")

    def on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

        if has_selection:
            selected_row = self.table.currentRow()
            trabajador_id = int(self.table.item(selected_row, 0).text())
            trabajador = self.dao.obtener_por_id(trabajador_id)
            self.worker_selected.emit(trabajador)

    def get_selected_worker(self):
        """Retorna el trabajador seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return None

        trabajador_id = int(self.table.item(selected_row, 0).text())
        return self.dao.obtener_por_id(trabajador_id)
