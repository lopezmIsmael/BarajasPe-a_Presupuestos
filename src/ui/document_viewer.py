"""
Visor de documentos WYSIWYG con capacidad de edición y exportación a PDF.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QFileDialog, QMessageBox, QToolBar, QSizePolicy)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import Qt, QUrl, QMarginsF
from PyQt6.QtGui import QPageLayout, QPageSize, QAction
from PyQt6.QtPrintSupport import QPrinter
import os


class DocumentViewer(QDialog):
    """Visor WYSIWYG de documentos con edición y exportación a PDF"""

    def __init__(self, parent=None, html_content="", title="Documento", editable=False):
        super().__init__(parent)
        self.html_content = html_content
        self.editable = editable
        self.init_ui(title)
        self.load_content()

    def init_ui(self, title):
        """Inicializa la interfaz"""
        self.setWindowTitle(title)
        self.resize(1000, 800)

        layout = QVBoxLayout()

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)

        # Acción de guardar como PDF
        self.save_pdf_action = QAction("💾 Guardar como PDF", self)
        self.save_pdf_action.triggered.connect(self.save_as_pdf)
        toolbar.addAction(self.save_pdf_action)

        toolbar.addSeparator()

        # Acción de imprimir
        self.print_action = QAction("🖨️ Imprimir", self)
        self.print_action.triggered.connect(self.print_document)
        toolbar.addAction(self.print_action)

        toolbar.addSeparator()

        # Acción de zoom
        zoom_in_action = QAction("🔍+ Ampliar", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction("🔍- Reducir", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)

        zoom_reset_action = QAction("↻ Restablecer", self)
        zoom_reset_action.triggered.connect(self.zoom_reset)
        toolbar.addAction(zoom_reset_action)

        if self.editable:
            toolbar.addSeparator()

            # Acción para habilitar edición
            self.edit_action = QAction("✏️ Editar Documento", self)
            self.edit_action.setCheckable(True)
            self.edit_action.toggled.connect(self.toggle_edit_mode)
            toolbar.addAction(self.edit_action)

        layout.addWidget(toolbar)

        # WebEngineView
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Configurar ajustes
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        layout.addWidget(self.web_view)

        # Botones inferiores
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if self.editable:
            self.save_changes_button = QPushButton("Guardar Cambios")
            self.save_changes_button.clicked.connect(self.save_changes)
            self.save_changes_button.setEnabled(False)
            button_layout.addWidget(self.save_changes_button)

        self.close_button = QPushButton("Cerrar")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_content(self):
        """Carga el contenido HTML en el visor"""
        self.web_view.setHtml(self.html_content)

        # Si es editable, habilitar modo edición automáticamente tras cargar
        if self.editable:
            # Esperar a que se cargue el contenido
            self.web_view.loadFinished.connect(self.enable_editing_on_load)

    def enable_editing_on_load(self):
        """Habilita la edición automáticamente después de cargar"""
        script = """
            // Hacer todos los elementos con clase 'editable' editables
            var editables = document.querySelectorAll('.editable');
            editables.forEach(function(el) {
                el.contentEditable = true;
                el.style.outline = '1px dashed #ccc';
                el.style.minHeight = '20px';
                el.addEventListener('focus', function() {
                    this.style.outline = '2px solid #3498db';
                });
                el.addEventListener('blur', function() {
                    this.style.outline = '1px dashed #ccc';
                });
            });

            // Si no hay elementos editables, hacer todo el body editable
            if (editables.length === 0) {
                document.body.contentEditable = true;
                document.body.style.outline = '2px dashed #3498db';
            }
        """
        self.web_view.page().runJavaScript(script)
        if hasattr(self, 'save_changes_button'):
            self.save_changes_button.setEnabled(True)

    def toggle_edit_mode(self, enabled):
        """Habilita o deshabilita el modo de edición"""
        if enabled:
            # Hacer el contenido editable usando JavaScript
            script = """
                document.body.contentEditable = true;
                document.body.style.outline = '2px dashed #3498db';
            """
            self.web_view.page().runJavaScript(script)
            self.save_changes_button.setEnabled(True)
            QMessageBox.information(
                self,
                "Modo Edición",
                "El documento ahora es editable.\n\n"
                "Puede modificar el texto directamente.\n"
                "Use 'Guardar Cambios' para aplicar las modificaciones."
            )
        else:
            # Deshabilitar edición
            script = """
                document.body.contentEditable = false;
                document.body.style.outline = 'none';
            """
            self.web_view.page().runJavaScript(script)
            self.save_changes_button.setEnabled(False)

    def save_changes(self):
        """Guarda los cambios realizados en el documento"""
        # Obtener el HTML editado
        self.web_view.page().toHtml(self.on_html_received)

    def on_html_received(self, html):
        """Callback cuando se recibe el HTML editado"""
        self.html_content = html
        QMessageBox.information(
            self,
            "Guardado",
            "Los cambios han sido guardados en memoria.\n\n"
            "Nota: Los cambios se aplicarán al documento actual."
        )

    def get_html_content(self):
        """Retorna el contenido HTML actual"""
        return self.html_content

    def save_as_pdf(self):
        """Guarda el documento como PDF"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar como PDF",
            "",
            "Archivos PDF (*.pdf)"
        )

        if not file_path:
            return

        if not file_path.endswith('.pdf'):
            file_path += '.pdf'

        # Configurar el layout de página
        page_layout = QPageLayout()
        page_layout.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        page_layout.setOrientation(QPageLayout.Orientation.Portrait)
        page_layout.setMargins(QMarginsF(15, 15, 15, 15))

        # Exportar a PDF
        self.web_view.page().printToPdf(file_path, page_layout)

        # Esperar un momento y mostrar mensaje
        QMessageBox.information(
            self,
            "PDF Guardado",
            f"El documento se ha guardado correctamente en:\n{file_path}"
        )

    def print_document(self):
        """Imprime el documento"""
        # Crear printer
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setPageOrientation(QPageLayout.Orientation.Portrait)

        # Configurar márgenes
        page_layout = QPageLayout()
        page_layout.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        page_layout.setOrientation(QPageLayout.Orientation.Portrait)
        page_layout.setMargins(QMarginsF(15, 15, 15, 15))

        # Mostrar diálogo de impresión
        from PyQt6.QtPrintSupport import QPrintDialog
        print_dialog = QPrintDialog(printer, self)

        if print_dialog.exec() == QDialog.DialogCode.Accepted:
            # Imprimir
            self.web_view.page().print(printer, lambda success:
                QMessageBox.information(
                    self,
                    "Impresión",
                    "Documento enviado a la impresora" if success else "Error al imprimir"
                )
            )

    def zoom_in(self):
        """Amplía el zoom"""
        current_zoom = self.web_view.zoomFactor()
        self.web_view.setZoomFactor(min(current_zoom + 0.1, 3.0))

    def zoom_out(self):
        """Reduce el zoom"""
        current_zoom = self.web_view.zoomFactor()
        self.web_view.setZoomFactor(max(current_zoom - 0.1, 0.3))

    def zoom_reset(self):
        """Restablece el zoom"""
        self.web_view.setZoomFactor(1.0)


def show_document(parent, html_content, title="Documento", editable=False):
    """
    Función auxiliar para mostrar un documento.

    Args:
        parent: Widget padre
        html_content: Contenido HTML
        title: Título de la ventana
        editable: Si el documento es editable

    Returns:
        El HTML modificado si fue editado, o None
    """
    viewer = DocumentViewer(parent, html_content, title, editable)
    if viewer.exec() == QDialog.DialogCode.Accepted:
        if editable:
            return viewer.get_html_content()
    return None
