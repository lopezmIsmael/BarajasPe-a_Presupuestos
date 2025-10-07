from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from pathlib import Path
from src.database.db import get_quote
from PIL import Image
from src.pdf.formatter import render_formatted_notes
from datetime import datetime

BRAND_COLOR = HexColor('#2B7DE9')

def export_quote_to_pdf(qid, out_path):
    """
    Genera PDF del presupuesto adaptado a folios pre-impresos de Barajas Peña.
    El folio ya incluye logo y datos de la empresa en la parte superior.
    """
    quote, items = get_quote(qid)
    if quote is None:
        raise ValueError('Quote not found')

    out_path = Path(out_path)
    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4
    margin = 20*mm
    
    # Comenzar más abajo para no sobreescribir el header del folio pre-impreso
    # Dejamos espacio para el logo y datos de la empresa (aprox 80mm desde arriba)
    y = height - 80*mm

    # Fecha a la izquierda
    current_date = datetime.now().strftime('%d/%m/%Y')
    c.setFont('Helvetica', 10)
    c.drawString(margin, y, f"Fecha: {current_date}")
    
    # Datos del cliente arriba a la derecha en formato tabla
    client_x = width - margin - 85*mm  # Posición derecha
    client_y = y
    
    c.setFont('Helvetica-Bold', 10)
    c.drawString(client_x, client_y, "CLIENTE:")
    c.setFont('Helvetica', 10)
    c.drawString(client_x + 20*mm, client_y, quote['client_name'] or '')
    client_y -= 12
    
    if quote['client_address']:
        c.setFont('Helvetica-Bold', 10)
        c.drawString(client_x, client_y, "DIRECCIÓN:")
        c.setFont('Helvetica', 10)
        c.drawString(client_x + 20*mm, client_y, quote['client_address'])
        client_y -= 12
    
    location_parts = []
    if quote.get('client_city'):
        location_parts.append(quote['client_city'])
    if quote.get('client_postal_code'):
        location_parts.append(f"CP: {quote['client_postal_code']}")
    
    if location_parts:
        c.setFont('Helvetica-Bold', 10)
        c.drawString(client_x, client_y, "LOCALIDAD:")
        c.setFont('Helvetica', 10)
        c.drawString(client_x + 20*mm, client_y, ', '.join(location_parts))
        client_y -= 12
    
    if quote.get('client_dni'):
        c.setFont('Helvetica-Bold', 10)
        c.drawString(client_x, client_y, "DNI/CIF:")
        c.setFont('Helvetica', 10)
        c.drawString(client_x + 20*mm, client_y, quote['client_dni'])
    
    if quote.get('work_name'):
        client_y -= 12
        c.setFont('Helvetica-Bold', 10)
        c.drawString(client_x, client_y, "OBRA:")
        c.setFont('Helvetica', 10)
        c.drawString(client_x + 20*mm, client_y, quote['work_name'])
    
    # Ajustar Y para continuar después de la tabla de cliente
    y -= 60  # Espacio suficiente para la tabla del cliente

    # Saludo y descripción
    c.setFont('Helvetica', 10)
    c.drawString(margin, y, "Muy Sr. Nuestro:")
    y -= 12
    c.drawString(margin, y, "A continuación, detallamos desglose de presupuesto aproximado de trabajos a realizar en")
    y -= 12
    c.drawString(margin, y, "sus instalaciones.")
    y -= 16

    # Lista de items (materiales) - CON CANTIDAD pero SIN PRECIOS
    total_materials = 0.0
    for idx, item in enumerate(items, 1):
        # Verificar si hay espacio suficiente para el item
        if y < 80*mm:  # Dejar margen inferior
            c.showPage()
            y = height - margin
        
        # Calcular total pero no mostrarlo
        line_total = item['unit_price'] * item['quantity']
        total_materials += line_total
        
        # Punto numerado - CON cantidad pero SIN precio
        c.setFont('Helvetica-Bold', 10)
        quantity_text = f" (Cantidad: {item['quantity']:.0f})" if item['quantity'] > 1 else ""
        bullet_text = f"• {item['name']}{quantity_text}"
        c.drawString(margin + 5, y, bullet_text)
        y -= 12
        
        # Descripción del item
        if item['description']:
            c.setFont('Helvetica', 9)
            # Dividir descripción en líneas si es muy larga
            desc_lines = []
            words = item['description'].split()
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if c.stringWidth(test_line, 'Helvetica', 9) < (width - 2*margin - 10):
                    current_line = test_line
                else:
                    if current_line:
                        desc_lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                desc_lines.append(current_line.strip())
            
            for desc_line in desc_lines:
                c.drawString(margin + 10, y, desc_line)
                y -= 10
        
        y -= 6

    # Mostrar notas si existen (formateadas o simples)
    if quote.get('formatted_notes') or quote.get('notes'):
        y -= 6
        c.setFont('Helvetica-Bold', 10)
        c.drawString(margin, y, "Notas / Observaciones:")
        y -= 12
        
        # Usar notas formateadas si existen
        if quote.get('formatted_notes'):
            y = render_formatted_notes(c, quote['formatted_notes'], margin, y, 
                                      width - 2*margin, default_font_size=9)
            y -= 6
        elif quote.get('notes'):
            # Fallback a notas simples
            c.setFont('Helvetica', 9)
            
            # Dividir notas en líneas
            notes_lines = quote['notes'].split('\n')
            for notes_line in notes_lines:
                if not notes_line.strip():
                    y -= 10
                    continue
                # Dividir línea larga en múltiples líneas
                words = notes_line.split()
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    if c.stringWidth(test_line, 'Helvetica', 9) < (width - 2*margin):
                        current_line = test_line
                    else:
                        if current_line:
                            c.drawString(margin, y, current_line.strip())
                            y -= 10
                        current_line = word + " "
                if current_line:
                    c.drawString(margin, y, current_line.strip())
                    y -= 10
        
        y -= 6

    # Verificar espacio para totales
    if y < 100*mm:
        c.showPage()
        y = height - margin

    # Calcular total incluyendo mano de obra (pero no se muestra desglose)
    labor = quote['labor_cost'] or 0.0
    
    # Línea de resumen - CENTRADA Y EN NEGRITA Y EN MAYÚSCULAS
    y -= 8
    c.setFont('Helvetica-Bold', 11)
    text1 = "EL TOTAL DE LOS TRABAJOS PRESUPUESTADOS, INCLUYENDO MANO DE OBRA,"
    text2 = "MATERIALES, ASCIENDE A LA CANTIDAD DE:"
    c.drawCentredString(width / 2, y, text1)
    y -= 12
    c.drawCentredString(width / 2, y, text2)
    y -= 16
    
    # Total - ÚNICO PRECIO MOSTRADO EN NEGRITA Y CENTRADO
    total_with_labor = total_materials + labor
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
    client_name = quote.get('client_name', '') or ''
    c.drawString(promotor_x, signature_y - 28, client_name)

    c.showPage()
    c.save()


def export_document_to_pdf(formatted_content, out_path):
    """
    Genera PDF directamente desde el contenido formateado del documento editado.
    """
    out_path = Path(out_path)
    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4
    margin = 20*mm
    
    # Comenzar más abajo para el folio pre-impreso
    y = height - 80*mm
    
    # Renderizar el contenido formateado
    y = render_formatted_notes(c, formatted_content, margin, y, width - 2*margin, default_font_size=10)
    
    c.showPage()
    c.save()
