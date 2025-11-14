"""
Script de prueba para verificar el ajuste automático de ventanas al tamaño del monitor.
"""
import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
from src.utils.helpers import adjust_dialog_to_screen


class TestDialog(QDialog):
    """Diálogo de prueba"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Prueba de Ajuste de Ventana")

        # Ajustar tamaño al monitor disponible
        adjust_dialog_to_screen(self, preferred_width=1000, preferred_height=700)

        layout = QVBoxLayout()

        # Obtener información del tamaño de la ventana
        screen = QApplication.screenAt(self.pos()) or QApplication.primaryScreen()
        screen_info = f"Monitor: {screen.name()}\n"
        screen_info += f"Resolución: {screen.size().width()}x{screen.size().height()}\n"
        screen_info += f"Área disponible: {screen.availableGeometry().width()}x{screen.availableGeometry().height()}\n"
        screen_info += f"Tamaño de ventana: {self.width()}x{self.height()}"

        label = QLabel(screen_info)
        layout.addWidget(label)

        info_label = QLabel(
            "Esta ventana debería ajustarse automáticamente al tamaño de tu monitor.\n"
            "En pantallas pequeñas, será más pequeña (máximo 90% de la pantalla).\n"
            "En pantallas grandes, usará el tamaño preferido de 1000x700."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = TestDialog()
    dialog.exec()
    print("Prueba completada correctamente")
