"""
Funciones auxiliares y utilidades comunes.
"""
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtGui import QScreen


def format_currency(amount):
    """
    Formatea un número como moneda en formato español.

    Args:
        amount: Cantidad numérica

    Returns:
        String formateado como moneda (ej: "1.234,56 €")
    """
    if amount is None:
        return "0,00 €"
    return f"{amount:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def format_date(date):
    """
    Formatea una fecha en formato español.

    Args:
        date: Objeto datetime o date

    Returns:
        String con formato DD/MM/YYYY
    """
    if date is None:
        return ""
    if isinstance(date, str):
        return date
    return date.strftime("%d/%m/%Y")


def format_datetime(dt):
    """
    Formatea una fecha y hora en formato español.

    Args:
        dt: Objeto datetime

    Returns:
        String con formato DD/MM/YYYY HH:MM
    """
    if dt is None:
        return ""
    if isinstance(dt, str):
        return dt
    return dt.strftime("%d/%m/%Y %H:%M")


def parse_float(value):
    """
    Convierte un string a float, manejando formato español.

    Args:
        value: String con número

    Returns:
        Float o 0.0 si hay error
    """
    if not value:
        return 0.0
    try:
        # Reemplazar formato español por formato estándar
        value_str = str(value).replace(".", "").replace(",", ".")
        return float(value_str)
    except ValueError:
        return 0.0


def show_error(parent, title, message):
    """
    Muestra un diálogo de error.

    Args:
        parent: Widget padre
        title: Título del diálogo
        message: Mensaje a mostrar
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec()


def show_info(parent, title, message):
    """
    Muestra un diálogo informativo.

    Args:
        parent: Widget padre
        title: Título del diálogo
        message: Mensaje a mostrar
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec()


def show_warning(parent, title, message):
    """
    Muestra un diálogo de advertencia.

    Args:
        parent: Widget padre
        title: Título del diálogo
        message: Mensaje a mostrar
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec()


def confirm_dialog(parent, title, message):
    """
    Muestra un diálogo de confirmación.

    Args:
        parent: Widget padre
        title: Título del diálogo
        message: Mensaje a mostrar

    Returns:
        True si el usuario confirma, False en caso contrario
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Icon.Question)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg_box.setDefaultButton(QMessageBox.StandardButton.No)

    result = msg_box.exec()
    return result == QMessageBox.StandardButton.Yes


def validate_nif_cif(nif_cif):
    """
    Valida un NIF/CIF español (validación básica).

    Args:
        nif_cif: String con el NIF/CIF

    Returns:
        True si es válido, False en caso contrario
    """
    if not nif_cif:
        return True  # Permitir vacío

    nif_cif = nif_cif.strip().upper().replace("-", "").replace(" ", "")

    if len(nif_cif) < 9:
        return False

    # Validación básica: 8 dígitos + letra o letra + 7 dígitos + letra
    if nif_cif[0].isalpha():
        # CIF
        return len(nif_cif) == 9 and nif_cif[1:-1].isdigit() and nif_cif[-1].isalnum()
    else:
        # NIF
        return len(nif_cif) == 9 and nif_cif[:-1].isdigit() and nif_cif[-1].isalpha()


def validate_email(email):
    """
    Valida un email (validación básica).

    Args:
        email: String con el email

    Returns:
        True si es válido, False en caso contrario
    """
    if not email:
        return True  # Permitir vacío

    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """
    Valida un teléfono español (validación básica).

    Args:
        phone: String con el teléfono

    Returns:
        True si es válido, False en caso contrario
    """
    if not phone:
        return True  # Permitir vacío

    import re
    # Eliminar espacios, guiones y paréntesis
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)

    # Validar que tenga entre 9 y 15 dígitos (con posible + al inicio)
    pattern = r'^\+?\d{9,15}$'
    return re.match(pattern, phone_clean) is not None


def adjust_dialog_to_screen(dialog, preferred_width=1000, preferred_height=700,
                            max_screen_ratio=0.9, min_width=600, min_height=400):
    """
    Ajusta el tamaño de un diálogo al tamaño de la pantalla disponible.

    Args:
        dialog: El diálogo QDialog a ajustar
        preferred_width: Ancho preferido si la pantalla lo permite
        preferred_height: Alto preferido si la pantalla lo permite
        max_screen_ratio: Ratio máximo de pantalla a usar (0.9 = 90%)
        min_width: Ancho mínimo del diálogo
        min_height: Alto mínimo del diálogo
    """
    # Obtener la pantalla primaria o la del widget padre
    screen = None

    # Intentar obtener la pantalla del padre si existe
    parent = dialog.parent()
    if parent is not None:
        screen = QApplication.screenAt(parent.pos())

    # Si no hay padre o no se pudo obtener, usar pantalla primaria
    if screen is None:
        screen = QApplication.primaryScreen()

    if screen is None:
        # Si aún no hay pantalla, usar tamaño preferido
        dialog.resize(preferred_width, preferred_height)
        return

    # Obtener geometría disponible (excluyendo barras de tareas, etc.)
    available_geometry = screen.availableGeometry()
    screen_width = available_geometry.width()
    screen_height = available_geometry.height()

    # Calcular tamaño máximo permitido
    max_width = int(screen_width * max_screen_ratio)
    max_height = int(screen_height * max_screen_ratio)

    # Determinar tamaño final
    final_width = max(min_width, min(preferred_width, max_width))
    final_height = max(min_height, min(preferred_height, max_height))

    # Aplicar tamaño
    dialog.resize(final_width, final_height)

    # Centrar el diálogo en la pantalla
    dialog_geometry = dialog.frameGeometry()
    center_point = available_geometry.center()
    dialog_geometry.moveCenter(center_point)
    dialog.move(dialog_geometry.topLeft())
