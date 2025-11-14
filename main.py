"""
Punto de entrada principal de la aplicación.
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from src.ui.main_window import MainWindow
from src.ui.styles import apply_stylesheet


def main():
    """Función principal"""
    app = QApplication(sys.argv)

    # Configurar estilo base de la aplicación
    app.setStyle("Fusion")

    # Configurar fuente global
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Aplicar hoja de estilos moderna
    apply_stylesheet(app)

    # Configurar nombre de la aplicación
    app.setApplicationName("Barajas Peña - Gestión de Construcciones")
    app.setOrganizationName("Barajas Peña S.L.")

    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()

    # Ejecutar aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
