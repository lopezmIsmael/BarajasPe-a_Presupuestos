"""
Gestor de Clientes - Interfaz CRUD para gestión de clientes.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                              QMessageBox, QHeaderView, QDialog, QFormLayout,
                              QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from src.database.database import ClienteDAO, Database
from src.utils.helpers import show_error, show_info, confirm_dialog, validate_nif_cif, validate_email, validate_phone


class ClientDialog(QDialog):
    """Diálogo para crear/editar un cliente"""

    def __init__(self, parent=None, cliente=None, db=None):
        super().__init__(parent)
        self.cliente = cliente
        self.db = db
        self.init_ui()

        if cliente:
            self.load_data()

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Cliente" if not self.cliente else f"Editar Cliente")
        self.setModal(True)
        self.setMinimumWidth(600)

        layout = QVBoxLayout()

        # Grupo de datos personales
        personal_group = QGroupBox("Datos Personales")
        personal_layout = QFormLayout()

        self.nombre_input = QLineEdit()
        self.apellidos_input = QLineEdit()
        self.nif_input = QLineEdit()

        personal_layout.addRow("Nombre*:", self.nombre_input)
        personal_layout.addRow("Apellidos:", self.apellidos_input)
        personal_layout.addRow("NIF/CIF:", self.nif_input)

        personal_group.setLayout(personal_layout)
        layout.addWidget(personal_group)

        # Grupo de datos empresa
        empresa_group = QGroupBox("Datos Empresa (Opcional)")
        empresa_layout = QFormLayout()

        self.empresa_input = QLineEdit()
        empresa_layout.addRow("Empresa:", self.empresa_input)

        empresa_group.setLayout(empresa_layout)
        layout.addWidget(empresa_group)

        # Grupo de contacto
        contacto_group = QGroupBox("Contacto")
        contacto_layout = QFormLayout()

        self.telefono_input = QLineEdit()
        self.email_input = QLineEdit()

        contacto_layout.addRow("Teléfono:", self.telefono_input)
        contacto_layout.addRow("Email:", self.email_input)

        contacto_group.setLayout(contacto_layout)
        layout.addWidget(contacto_group)

        # Grupo de dirección
        direccion_group = QGroupBox("Dirección")
        direccion_layout = QFormLayout()

        self.direccion_input = QLineEdit()
        self.ciudad_input = QLineEdit()
        self.cp_input = QLineEdit()
        self.provincia_input = QLineEdit()

        direccion_layout.addRow("Dirección:", self.direccion_input)
        direccion_layout.addRow("Ciudad:", self.ciudad_input)
        direccion_layout.addRow("Código Postal:", self.cp_input)
        direccion_layout.addRow("Provincia:", self.provincia_input)

        direccion_group.setLayout(direccion_layout)
        layout.addWidget(direccion_group)

        # Notas
        notas_group = QGroupBox("Notas")
        notas_layout = QVBoxLayout()
        self.notas_input = QTextEdit()
        self.notas_input.setMaximumHeight(80)
        notas_layout.addWidget(self.notas_input)
        notas_group.setLayout(notas_layout)
        layout.addWidget(notas_group)

        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def load_data(self):
        """Carga los datos del cliente en el formulario"""
        self.nombre_input.setText(self.cliente.nombre or "")
        self.apellidos_input.setText(self.cliente.apellidos or "")
        self.empresa_input.setText(self.cliente.empresa or "")
        self.nif_input.setText(self.cliente.nif_cif or "")
        self.telefono_input.setText(self.cliente.telefono or "")
        self.email_input.setText(self.cliente.email or "")
        self.direccion_input.setText(self.cliente.direccion or "")
        self.ciudad_input.setText(self.cliente.ciudad or "")
        self.cp_input.setText(self.cliente.codigo_postal or "")
        self.provincia_input.setText(self.cliente.provincia or "")
        self.notas_input.setPlainText(self.cliente.notas or "")

    def validate_form(self):
        """Valida los datos del formulario"""
        if not self.nombre_input.text().strip():
            show_error(self, "Error", "El nombre es obligatorio")
            return False

        nif = self.nif_input.text().strip()
        if nif and not validate_nif_cif(nif):
            show_error(self, "Error", "El NIF/CIF no es válido")
            return False

        email = self.email_input.text().strip()
        if email and not validate_email(email):
            show_error(self, "Error", "El email no es válido")
            return False

        telefono = self.telefono_input.text().strip()
        if telefono and not validate_phone(telefono):
            show_error(self, "Error", "El teléfono no es válido")
            return False

        return True

    def save(self):
        """Guarda el cliente"""
        if not self.validate_form():
            return

        try:
            dao = ClienteDAO(self.db)

            data = {
                'nombre': self.nombre_input.text().strip(),
                'apellidos': self.apellidos_input.text().strip(),
                'empresa': self.empresa_input.text().strip(),
                'nif_cif': self.nif_input.text().strip(),
                'telefono': self.telefono_input.text().strip(),
                'email': self.email_input.text().strip(),
                'direccion': self.direccion_input.text().strip(),
                'ciudad': self.ciudad_input.text().strip(),
                'codigo_postal': self.cp_input.text().strip(),
                'provincia': self.provincia_input.text().strip(),
                'notas': self.notas_input.toPlainText().strip()
            }

            if self.cliente:
                # Actualizar
                dao.actualizar(self.cliente.id, **data)
            else:
                # Crear
                self.cliente = dao.crear(**data)

            self.accept()

        except Exception as e:
            show_error(self, "Error", f"Error al guardar el cliente: {str(e)}")

    def get_cliente(self):
        """Retorna el cliente creado/editado"""
        return self.cliente


class ClientsManager(QWidget):
    """Widget para gestionar clientes"""

    cliente_selected = pyqtSignal(object)  # Señal cuando se selecciona un cliente

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.dao = ClienteDAO(db)
        self.init_ui()
        self.load_clients()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()

        # Barra de herramientas
        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar cliente...")
        self.search_input.textChanged.connect(self.search_clients)

        self.new_button = QPushButton("Nuevo Cliente")
        self.new_button.clicked.connect(self.new_client)

        self.edit_button = QPushButton("Editar")
        self.edit_button.clicked.connect(self.edit_client)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("Eliminar")
        self.delete_button.clicked.connect(self.delete_client)
        self.delete_button.setEnabled(False)

        toolbar.addWidget(QLabel("Buscar:"))
        toolbar.addWidget(self.search_input)
        toolbar.addStretch()
        toolbar.addWidget(self.new_button)
        toolbar.addWidget(self.edit_button)
        toolbar.addWidget(self.delete_button)

        layout.addLayout(toolbar)

        # Tabla de clientes
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Apellidos", "Empresa", "Teléfono", "Email"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(self.edit_client)

        # Ocultar columna ID
        self.table.setColumnHidden(0, True)

        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_clients(self):
        """Carga todos los clientes en la tabla"""
        try:
            clientes = self.dao.obtener_todos()
            self.populate_table(clientes)
        except Exception as e:
            show_error(self, "Error", f"Error al cargar clientes: {str(e)}")

    def populate_table(self, clientes):
        """Rellena la tabla con los clientes"""
        self.table.setRowCount(0)

        for cliente in clientes:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(cliente.id)))
            self.table.setItem(row, 1, QTableWidgetItem(cliente.nombre or ""))
            self.table.setItem(row, 2, QTableWidgetItem(cliente.apellidos or ""))
            self.table.setItem(row, 3, QTableWidgetItem(cliente.empresa or ""))
            self.table.setItem(row, 4, QTableWidgetItem(cliente.telefono or ""))
            self.table.setItem(row, 5, QTableWidgetItem(cliente.email or ""))

    def search_clients(self):
        """Busca clientes por el criterio introducido"""
        criterio = self.search_input.text().strip()

        if not criterio:
            self.load_clients()
            return

        try:
            clientes = self.dao.buscar(criterio)
            self.populate_table(clientes)
        except Exception as e:
            show_error(self, "Error", f"Error al buscar clientes: {str(e)}")

    def new_client(self):
        """Crea un nuevo cliente"""
        dialog = ClientDialog(self, db=self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            show_info(self, "Éxito", "Cliente creado correctamente")
            self.load_clients()

    def edit_client(self):
        """Edita el cliente seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        cliente_id = int(self.table.item(selected_row, 0).text())
        cliente = self.dao.obtener_por_id(cliente_id)

        if not cliente:
            show_error(self, "Error", "Cliente no encontrado")
            return

        dialog = ClientDialog(self, cliente=cliente, db=self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            show_info(self, "Éxito", "Cliente actualizado correctamente")
            self.load_clients()

    def delete_client(self):
        """Elimina el cliente seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return

        cliente_id = int(self.table.item(selected_row, 0).text())
        nombre = self.table.item(selected_row, 1).text()
        apellidos = self.table.item(selected_row, 2).text()

        if not confirm_dialog(self, "Confirmar",
                              f"¿Está seguro de eliminar el cliente '{nombre} {apellidos}'?\n"
                              f"Esta acción eliminará también todos sus presupuestos."):
            return

        try:
            if self.dao.eliminar(cliente_id):
                show_info(self, "Éxito", "Cliente eliminado correctamente")
                self.load_clients()
            else:
                show_error(self, "Error", "No se pudo eliminar el cliente")
        except Exception as e:
            show_error(self, "Error", f"Error al eliminar el cliente: {str(e)}")

    def on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

        if has_selection:
            selected_row = self.table.currentRow()
            cliente_id = int(self.table.item(selected_row, 0).text())
            cliente = self.dao.obtener_por_id(cliente_id)
            self.cliente_selected.emit(cliente)

    def get_selected_client(self):
        """Retorna el cliente seleccionado"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return None

        cliente_id = int(self.table.item(selected_row, 0).text())
        return self.dao.obtener_por_id(cliente_id)
