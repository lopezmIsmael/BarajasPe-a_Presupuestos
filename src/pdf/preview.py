"""
Módulo para generar previsualizaciones de PDF en tiempo real
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from src.pdf.formatter import render_formatted_notes
import tempfile
import os
from datetime import datetime

# Intentar importar pdf2image
try:
    from pdf2image import convert_from_bytes
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False
    print("Advertencia: pdf2image no está instalado. Las previsualizaciones serán limitadas.")

BRAND_COLOR = HexColor('#2B7DE9')

def generate_quote_preview(client_name, client_address, client_dni, work_name, 
                          items_data, labor_cost, notes, date_str, formatted_notes=None):
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
    # Usar fecha en formato DD/MM/YYYY si date_str no viene con formato completo
    if '/' not in date_str:
        date_str = datetime.now().strftime('%d/%m/%Y')
    c.drawString(margin, y, f"Fecha: {date_str}")
    
    # Datos del cliente arriba a la derecha en formato tabla
    client_x = width - margin - 85*mm
    client_y = y
    
    c.setFont('Helvetica-Bold', 10)
    c.drawString(client_x, client_y, "CLIENTE:")
    c.setFont('Helvetica', 10)
    c.drawString(client_x + 20*mm, client_y, client_name or '')
    client_y -= 12
    
    if client_address:
        c.setFont('Helvetica-Bold', 10)
        c.drawString(client_x, client_y, "DIRECCIÓN:")
        c.setFont('Helvetica', 10)
        c.drawString(client_x + 20*mm, client_y, client_address)
        client_y -= 12
    
    if client_dni:
        c.setFont('Helvetica-Bold', 10)
        c.drawString(client_x, client_y, "DNI/CIF:")
        c.setFont('Helvetica', 10)
        c.drawString(client_x + 20*mm, client_y, client_dni)
    
    if work_name:
        client_y -= 12
        c.setFont('Helvetica-Bold', 10)
        c.drawString(client_x, client_y, "OBRA:")
        c.setFont('Helvetica', 10)
        c.drawString(client_x + 20*mm, client_y, work_name)
    
    # Ajustar Y para continuar después de la tabla de cliente
    y -= 60

    # Saludo y descripción
    c.setFont('Helvetica', 10)
    c.drawString(margin, y, "Muy Sr. Nuestro:")
    y -= 12
    c.drawString(margin, y, "A continuación, detallamos desglose de presupuesto aproximado de trabajos a realizar en")
    y -= 12
    c.drawString(margin, y, "sus instalaciones.")
    y -= 16

    # Lista de items - CON CANTIDAD pero SIN PRECIOS
    total_materials = 0.0
    for idx, item in enumerate(items_data, 1):
        if y < 80*mm:
            c.showPage()
            y = height - margin
        
        # Calcular total pero no mostrarlo
        line_total = item['price'] * item['quantity']
        total_materials += line_total
        
        # Punto numerado - CON cantidad pero SIN precio
        c.setFont('Helvetica-Bold', 10)
        quantity_text = f" (Cantidad: {item['quantity']:.0f})" if item['quantity'] > 1 else ""
        bullet_text = f"• {item['name']}{quantity_text}"
        c.drawString(margin + 5, y, bullet_text)
        y -= 12
        
        if item.get('description'):
            c.setFont('Helvetica', 9)
            desc_lines = _wrap_text(c, item['description'], width - 2*margin - 10, 'Helvetica', 9)
            for desc_line in desc_lines:
                c.drawString(margin + 10, y, desc_line)
                y -= 10
        
        y -= 6

    # Notas (formateadas o simples)
    if formatted_notes or notes:
        y -= 6
        c.setFont('Helvetica-Bold', 10)
        c.drawString(margin, y, "Notas / Observaciones:")
        y -= 12
        
        # Usar notas formateadas si existen
        if formatted_notes:
            y = render_formatted_notes(c, formatted_notes, margin, y, 
                                      width - 2*margin, default_font_size=9)
            y -= 6
        elif notes:
            # Fallback a notas simples
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

    # Total - CENTRADO Y EN NEGRITA
    y -= 8
    c.setFont('Helvetica-Bold', 11)
    text1 = "EL TOTAL DE LOS TRABAJOS PRESUPUESTADOS, INCLUYENDO MANO DE OBRA,"
    text2 = "MATERIALES, ASCIENDE A LA CANTIDAD DE:"
    c.drawCentredString(width / 2, y, text1)
    y -= 12
    c.drawCentredString(width / 2, y, text2)
    y -= 16
    
    # Total - ÚNICO PRECIO MOSTRADO
    total_with_labor = total_materials + labor_cost
    c.setFont('Helvetica-Bold', 14)
    total_text = f"{total_with_labor:.2f} EUROS"
    c.drawCentredString(width / 2, y, total_text)
    y -= 30

    # Condiciones adicionales - CENTRADAS Y EN MAYÚSCULAS
    c.setFont('Helvetica', 9)
    
    # Primera condición
    text = "LOS TRABAJOS NO PRESUPUESTADOS SE COBRARÍAN A 25€ LA HORA O SE PRESUPUESTARÁN EN CASO DE OBRA MAYOR."
    c.drawCentredString(width / 2, y, text)
    y -= 14
    
    # Segunda condición - SUBRAYADA Y EN NEGRITA
    c.setFont('Helvetica-Bold', 9)
    text = "ESTE PRESUPUESTO TIENE UNA VALIDEZ DE 15 DÍAS."
    text_width = c.stringWidth(text, 'Helvetica-Bold', 9)
    text_x = (width - text_width) / 2
    c.drawString(text_x, y, text)
    # Línea de subrayado
    c.line(text_x, y - 2, text_x + text_width, y - 2)
    y -= 14
    
    # Tercera condición
    c.setFont('Helvetica', 9)
    text1 = "NO SE INCLUYEN LOS PERMISOS NI LICENCIAS QUE SEAN NECESARIOS, LOS CUALES SE DEBERÁ CONTAR"
    text2 = "CON ELLOS AL COMIENZO DE LOS TRABAJOS. NO SE INCLUYEN PROYECTOS O MEMORIAS TÉCNICAS SI FUERAN NECESARIOS."
    c.drawCentredString(width / 2, y, text1)
    y -= 10
    c.drawCentredString(width / 2, y, text2)
    y -= 14
    
    # Nota del IVA - SUBRAYADA Y EN NEGRITA
    c.setFont('Helvetica-Bold', 9)
    text = "EL IVA SE INCREMENTARÁ EN LA FACTURA CORRESPONDIENTE"
    text_width = c.stringWidth(text, 'Helvetica-Bold', 9)
    text_x = (width - text_width) / 2
    c.drawString(text_x, y, text)
    # Línea de subrayado
    c.line(text_x, y - 2, text_x + text_width, y - 2)
    y -= 30
    
    # Espacio para firmas
    if y < 80*mm:  # Si no hay espacio, nueva página
        c.showPage()
        y = height - margin - 100
    
    # Líneas de firma
    signature_y = y
    signature_width = 60*mm
    
    # Firma del Constructor
    c.setFont('Helvetica', 10)
    c.drawString(margin, signature_y, "EL CONSTRUCTOR")
    c.line(margin, signature_y - 20, margin + signature_width, signature_y - 20)
    c.setFont('Helvetica', 8)
    c.drawString(margin, signature_y - 28, "Barajas Peña S.L.")
    
    # Firma del Promotor (Cliente)
    promotor_x = width - margin - signature_width
    c.setFont('Helvetica', 10)
    c.drawString(promotor_x, signature_y, "EL PROMOTOR")
    c.line(promotor_x, signature_y - 20, promotor_x + signature_width, signature_y - 20)
    c.setFont('Helvetica', 8)
    c.drawString(promotor_x, signature_y - 28, client_name)

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
