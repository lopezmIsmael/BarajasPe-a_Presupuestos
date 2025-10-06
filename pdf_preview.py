"""
Módulo para generar previsualizaciones de PDF en tiempo real
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os

# Intentar importar pdf2image
try:
    from pdf2image import convert_from_bytes
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False
    print("Advertencia: pdf2image no está instalado. Las previsualizaciones serán limitadas.")

BRAND_COLOR = HexColor('#2B7DE9')

def generate_quote_preview(client_name, client_address, client_dni, work_name, 
                          items_data, labor_cost, notes, date_str):
    """
    Genera una imagen de preview del presupuesto sin guardar archivo
    
    Returns:
        PIL.Image: Imagen del PDF para mostrar en la UI
    """
    # Crear PDF en memoria
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 20*mm
    
    # Comenzar más abajo para el folio pre-impreso
    y = height - 80*mm

    # Título del documento
    c.setFont('Helvetica-Bold', 14)
    c.drawString(margin, y, "PRESUPUESTO")
    c.setFont('Helvetica', 10)
    y -= 12
    c.drawString(margin, y, f"Fecha: {date_str}")
    y -= 18

    # Información del cliente
    c.setFont('Helvetica-Bold', 11)
    c.drawString(margin, y, f"CLIENTE: {client_name or ''}")
    c.setFont('Helvetica', 10)
    y -= 12
    
    if client_address:
        c.drawString(margin, y, f"DIRECCIÓN: {client_address}")
        y -= 12
    
    if client_dni:
        c.drawString(margin, y, f"DNI: {client_dni}")
        y -= 12

    y -= 8
    
    # Saludo y descripción
    c.setFont('Helvetica', 10)
    c.drawString(margin, y, "Muy Sr. Nuestro:")
    y -= 12
    
    if work_name:
        c.drawString(margin, y, f"A continuación, detallamos desglose de presupuesto aproximado de trabajos a realizar en")
        y -= 12
        c.drawString(margin, y, f"sus instalaciones: {work_name}")
        y -= 16
    else:
        c.drawString(margin, y, "A continuación, detallamos desglose de presupuesto aproximado de trabajos a realizar en")
        y -= 12
        c.drawString(margin, y, "sus instalaciones.")
        y -= 16

    # Lista de items
    total_materials = 0.0
    for idx, item in enumerate(items_data, 1):
        if y < 80*mm:
            c.showPage()
            y = height - margin
        
        line_total = item['price'] * item['quantity']
        total_materials += line_total
        
        c.setFont('Helvetica-Bold', 10)
        bullet_text = f"• {item['name']}"
        if item['quantity'] > 1:
            bullet_text += f" x{item['quantity']}"
        c.drawString(margin + 5, y, bullet_text)
        y -= 12
        
        if item.get('description'):
            c.setFont('Helvetica', 9)
            desc_lines = _wrap_text(c, item['description'], width - 2*margin - 10, 'Helvetica', 9)
            for desc_line in desc_lines:
                c.drawString(margin + 10, y, desc_line)
                y -= 10
        
        y -= 6

    # Notas
    if notes:
        y -= 6
        c.setFont('Helvetica-Bold', 10)
        c.drawString(margin, y, "Notas / Observaciones:")
        y -= 12
        c.setFont('Helvetica', 9)
        
        notes_lines = notes.split('\n')
        for notes_line in notes_lines:
            if not notes_line.strip():
                y -= 10
                continue
            wrapped = _wrap_text(c, notes_line, width - 2*margin, 'Helvetica', 9)
            for line in wrapped:
                c.drawString(margin, y, line)
                y -= 10
        
        y -= 6

    # Verificar espacio para totales
    if y < 100*mm:
        c.showPage()
        y = height - margin

    # Total
    y -= 8
    c.setFont('Helvetica-Bold', 11)
    c.drawString(margin, y, "El total de los trabajos presupuestados incluyendo mano de obra,")
    y -= 12
    c.drawString(margin, y, "materiales y medio de elevación, asciende a la cantidad de:")
    y -= 16
    
    total_with_labor = total_materials + labor_cost
    c.setFont('Helvetica-Bold', 14)
    total_text = f"{total_with_labor:.2f} EUROS"
    c.drawCentredString(width / 2, y, total_text)
    y -= 20

    if labor_cost == 0:
        c.setFont('Helvetica', 9)
        c.drawString(margin, y, "* Mano de obra incluida en el precio")
        y -= 12

    # Textos fijos
    y -= 12
    c.setFont('Helvetica-Bold', 10)
    c.drawString(margin, y, "ESTE PRESUPUESTO TIENE UNA VALIDEZ DE 15 DÍAS")
    y -= 14
    c.setFont('Helvetica-Oblique', 10)
    c.drawString(margin, y, "El IVA se incrementará en la factura correspondiente")

    c.showPage()
    c.save()
    
    # Convertir PDF a imagen
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    
    if HAS_PDF2IMAGE:
        try:
            # Convertir primera página del PDF a imagen
            images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=100)
            if images:
                return images[0]
        except Exception as e:
            print(f"Error generando preview con pdf2image: {e}")
    
    # Fallback: crear una imagen simple con el mensaje
    fallback_img = Image.new('RGB', (595, 842), 'white')
    draw = ImageDraw.Draw(fallback_img)
    
    try:
        # Intentar usar una fuente por defecto
        draw.text((50, 100), "Vista previa del PDF", fill='black')
        draw.text((50, 130), f"Cliente: {client_name}", fill='black')
        draw.text((50, 150), f"Trabajo: {work_name or 'Sin especificar'}", fill='black')
        draw.text((50, 180), f"Items: {len(items_data)}", fill='black')
        draw.text((50, 210), f"Total: {total_materials + labor_cost:.2f} €", fill='black')
        draw.text((50, 250), "Instala 'pdf2image' y 'poppler-utils'", fill='red')
        draw.text((50, 270), "para ver la preview completa", fill='red')
    except:
        pass
    
    return fallback_img


def _wrap_text(canvas_obj, text, max_width, font_name, font_size):
    """Divide texto largo en múltiples líneas"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        if canvas_obj.stringWidth(test_line, font_name, font_size) < max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())
    
    return lines
