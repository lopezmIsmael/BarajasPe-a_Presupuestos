"""
Funciones auxiliares y utilidades comunes.
"""
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox


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
