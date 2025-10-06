from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from pathlib import Path
from src.database.db import get_quote
from PIL import Image
from src.pdf.formatter import render_formatted_notes

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

    # Información del cliente
    c.setFont('Helvetica-Bold', 11)
    c.drawString(margin, y, f"CLIENTE: {quote['client_name'] or ''}")
    c.setFont('Helvetica', 10)
    y -= 12
    
    if quote['client_address']:
        c.drawString(margin, y, f"DIRECCIÓN: {quote['client_address']}")
        y -= 12
    
    location_parts = []
    if quote.get('client_city'):
        location_parts.append(quote['client_city'])
    if quote.get('client_postal_code'):
        location_parts.append(f"CP: {quote['client_postal_code']}")
    
    if location_parts:
        c.drawString(margin, y, f"LOCALIDAD: {', '.join(location_parts)}")
        y -= 12
    
    if quote.get('client_dni'):
        c.drawString(margin, y, f"DNI: {quote['client_dni']}")
        y -= 12

    y -= 8
    
    # Saludo y descripción
    c.setFont('Helvetica', 10)
    c.drawString(margin, y, "Muy Sr. Nuestro:")
    y -= 12
    
    # Descripción de trabajos (si hay nombre de obra)
    if quote.get('work_name'):
        c.drawString(margin, y, f"A continuación, detallamos desglose de presupuesto aproximado de trabajos a realizar en")
        y -= 12
        c.drawString(margin, y, f"sus instalaciones: {quote['work_name']}")
        y -= 16
    else:
        c.drawString(margin, y, "A continuación, detallamos desglose de presupuesto aproximado de trabajos a realizar en")
        y -= 12
        c.drawString(margin, y, "sus instalaciones.")
        y -= 16

    # Lista de items (materiales)
    total_materials = 0.0
    for idx, item in enumerate(items, 1):
        # Verificar si hay espacio suficiente para el item
        if y < 80*mm:  # Dejar margen inferior
            c.showPage()
            y = height - margin
        
        line_total = item['unit_price'] * item['quantity']
        total_materials += line_total
        
        # Punto numerado
        c.setFont('Helvetica-Bold', 10)
        bullet_text = f"• {item['name']}"
        if item['quantity'] > 1:
            bullet_text += f" x{item['quantity']}"
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

    # Mano de obra
    labor = quote['labor_cost'] or 0.0
    
    # Línea de resumen
    y -= 8
    c.setFont('Helvetica-Bold', 11)
    c.drawString(margin, y, "El total de los trabajos presupuestados incluyendo mano de obra,")
    y -= 12
    c.drawString(margin, y, "materiales y medio de elevación, asciende a la cantidad de:")
    y -= 16
    
    # Total
    total_with_labor = total_materials + labor
    c.setFont('Helvetica-Bold', 14)
    total_text = f"{total_with_labor:.2f} EUROS"
    c.drawCentredString(width / 2, y, total_text)
    y -= 20

    # Notas adicionales si no hay mano de obra explícita pero hay descripción
    if labor == 0:
        c.setFont('Helvetica', 9)
        c.drawString(margin, y, "* Mano de obra incluida en el precio")
        y -= 12

    # Textos fijos finales
    y -= 12
    c.setFont('Helvetica-Bold', 10)
    c.drawString(margin, y, "ESTE PRESUPUESTO TIENE UNA VALIDEZ DE 15 DÍAS")
    y -= 14
    c.setFont('Helvetica-Oblique', 10)
    c.drawString(margin, y, "El IVA se incrementará en la factura correspondiente")

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
