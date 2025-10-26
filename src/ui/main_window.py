"""
Ventana principal de la aplicación.
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QTabWidget, QStatusBar, QMenuBar, QMenu,
                              QMessageBox, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from src.database.database import Database
from src.ui.clients_manager import ClientsManager
from src.ui.materials_manager import MaterialsManager
from src.ui.workers_manager import WorkersManager
from src.ui.quotes_manager import QuotesManager
from src.ui.work_reports_manager import WorkReportsManager


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""

    def __init__(self):
        super().__init__()
        self.db = Database('constructora.db')
        self.db.create_tables()
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Gestión de Constructora - Barajas Peña Presupuestos")
        self.setGeometry(100, 100, 1400, 800)

        # Menú
        self.create_menu()

        # Widget central con tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Tabs principales
        self.tabs = QTabWidget()

        # Tab de Presupuestos
        self.quotes_tab = QuotesManager(self.db)
        self.tabs.addTab(self.quotes_tab, "📋 Presupuestos")

        # Tab de Partes de Trabajo
        self.reports_tab = WorkReportsManager(self.db)
        self.tabs.addTab(self.reports_tab, "🔧 Partes de Trabajo")

        # Tab de Clientes
        self.clients_tab = ClientsManager(self.db)
        self.tabs.addTab(self.clients_tab, "👤 Clientes")

        # Tab de Materiales
        self.materials_tab = MaterialsManager(self.db)
        self.tabs.addTab(self.materials_tab, "📦 Materiales")

        # Tab de Trabajadores
        self.workers_tab = WorkersManager(self.db)
        self.tabs.addTab(self.workers_tab, "👷 Trabajadores")

        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")

        # Conectar señales
        self.connect_signals()

    def create_menu(self):
        """Crea el menú de la aplicación"""
        menubar = self.menuBar()

        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")

        new_quote_action = QAction("Nuevo &Presupuesto", self)
        new_quote_action.setShortcut("Ctrl+P")
        new_quote_action.triggered.connect(self.new_quote)
        file_menu.addAction(new_quote_action)

        new_report_action = QAction("Nuevo P&arte de Trabajo", self)
        new_report_action.setShortcut("Ctrl+T")
        new_report_action.triggered.connect(self.new_report)
        file_menu.addAction(new_report_action)

        file_menu.addSeparator()

        exit_action = QAction("&Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menú Datos Maestros
        data_menu = menubar.addMenu("&Datos Maestros")

        clients_action = QAction("&Clientes", self)
        clients_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        data_menu.addAction(clients_action)

        materials_action = QAction("&Materiales", self)
        materials_action.triggered.connect(lambda: self.tabs.setCurrentIndex(3))
        data_menu.addAction(materials_action)

        workers_action = QAction("&Trabajadores", self)
        workers_action.triggered.connect(lambda: self.tabs.setCurrentIndex(4))
        data_menu.addAction(workers_action)

        # Menú Ayuda
        help_menu = menubar.addMenu("A&yuda")

        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def connect_signals(self):
        """Conecta las señales entre componentes"""
        # Actualizar barra de estado con selecciones
        self.quotes_tab.quote_selected.connect(
            lambda q: self.status_bar.showMessage(f"Presupuesto seleccionado: {q.numero} - {q.cliente}")
        )

        self.reports_tab.report_selected.connect(
            lambda r: self.status_bar.showMessage(f"Parte seleccionado: {r.numero} - {r.titulo}")
        )

        self.clients_tab.cliente_selected.connect(
            lambda c: self.status_bar.showMessage(f"Cliente seleccionado: {c}")
        )

        self.materials_tab.material_selected.connect(
            lambda m: self.status_bar.showMessage(f"Material seleccionado: {m.nombre}")
        )

        self.workers_tab.worker_selected.connect(
            lambda w: self.status_bar.showMessage(f"Trabajador seleccionado: {w}")
        )

        # Conectar señales de actualización de materiales
        self.materials_tab.material_created.connect(self.on_material_changed)
        self.materials_tab.material_updated.connect(self.on_material_changed)

        # Conectar señal de actualización de materiales desde presupuestos
        self.quotes_tab.material_updated.connect(self.on_material_updated_from_quote)

    def on_material_changed(self, material):
        """Maneja cuando se crea o actualiza un material"""
        self.status_bar.showMessage(f"Material actualizado: {material.nombre} - Actualizando vistas...")
        # Recargar presupuestos para reflejar cambios
        self.quotes_tab.load_quotes()
        # Recargar partes de trabajo
        self.reports_tab.load_reports()

    def on_material_updated_from_quote(self, material_id):
        """Maneja cuando se actualiza un material desde un presupuesto"""
        # Recargar el gestor de materiales para reflejar los cambios
        self.materials_tab.load_materials()
        self.status_bar.showMessage(f"Material actualizado desde presupuesto - ID: {material_id}")

    def new_quote(self):
        """Crea un nuevo presupuesto"""
        self.tabs.setCurrentIndex(0)
        self.quotes_tab.new_quote()

    def new_report(self):
        """Crea un nuevo parte de trabajo"""
        self.tabs.setCurrentIndex(1)
        self.reports_tab.new_report()

    def show_about(self):
        """Muestra el diálogo 'Acerca de'"""
        QMessageBox.about(
            self,
            "Acerca de",
            "<h2>Gestión de Constructora</h2>"
            "<p><b>Barajas Peña Presupuestos</b></p>"
            "<p>Versión 1.0</p>"
            "<p>Aplicación de gestión integral para empresas constructoras.</p>"
            "<p>Incluye gestión de presupuestos, partes de trabajo, clientes, materiales y trabajadores.</p>"
            "<hr>"
            "<p>Desarrollado con Python, PyQt6 y SQLite</p>"
            "<p>© 2025 - Todos los derechos reservados</p>"
        )

    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        reply = QMessageBox.question(
            self,
            "Confirmar Salida",
            "¿Está seguro de que desea salir de la aplicación?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
