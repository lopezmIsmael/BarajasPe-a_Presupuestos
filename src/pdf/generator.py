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


def format_price_es(value):
    """
    Formatea un precio en formato español:
    - Punto como separador de miles
    - Coma como separador decimal
    """
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def export_quote_to_pdf(qid, out_path):
    """
    Genera PDF del presupuesto.
    Si el presupuesto tiene formatted_notes (documento WYSIWYG), lo usa directamente.
    Si no, genera el PDF con el formato tradicional.
    """
    quote, items = get_quote(qid)
    if quote is None:
        raise ValueError('Quote not found')

    # Si existe formatted_notes (documento WYSIWYG), usarlo directamente
    # sqlite3.Row no tiene .get(), usar acceso directo con try-except
    try:
        formatted_notes = quote['formatted_notes']
        if formatted_notes:
            print(f"DEBUG: Usando formatted_notes para export (longitud: {len(formatted_notes)})")
            export_document_to_pdf(formatted_notes, out_path)
            return
        else:
            print("DEBUG: formatted_notes está vacío, usando formato tradicional")
    except (KeyError, IndexError, TypeError) as e:
        print(f"DEBUG: No existe formatted_notes ({e}), usando formato tradicional")


    # Si no, generar PDF con formato tradicional
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
    try:
        if quote['client_city']:
            location_parts.append(quote['client_city'])
    except (KeyError, IndexError):
        pass
    
    try:
        if quote['client_postal_code']:
            location_parts.append(f"CP: {quote['client_postal_code']}")
    except (KeyError, IndexError):
        pass
    
    if location_parts:
        c.setFont('Helvetica-Bold', 10)
        c.drawString(client_x, client_y, "LOCALIDAD:")
        c.setFont('Helvetica', 10)
        c.drawString(client_x + 20*mm, client_y, ', '.join(location_parts))
        client_y -= 12
    
    try:
        if quote['client_dni']:
            c.setFont('Helvetica-Bold', 10)
            c.drawString(client_x, client_y, "DNI/CIF:")
            c.setFont('Helvetica', 10)
            c.drawString(client_x + 20*mm, client_y, quote['client_dni'])
    except (KeyError, IndexError, TypeError):
        pass
    
    try:
        if quote['work_name']:
            client_y -= 12
            c.setFont('Helvetica-Bold', 10)
            c.drawString(client_x, client_y, "OBRA:")
            c.setFont('Helvetica', 10)
            c.drawString(client_x + 20*mm, client_y, quote['work_name'])
    except (KeyError, IndexError, TypeError):
        pass
    
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
    has_formatted_notes = False
    has_notes = False
    try:
        has_formatted_notes = bool(quote['formatted_notes'])
    except (KeyError, IndexError, TypeError):
        pass
    try:
        has_notes = bool(quote['notes'])
    except (KeyError, IndexError, TypeError):
        pass
    
    if has_formatted_notes or has_notes:
        y -= 6
        c.setFont('Helvetica-Bold', 10)
        c.drawString(margin, y, "Notas / Observaciones:")
        y -= 12
        
        # Usar notas formateadas si existen
        if has_formatted_notes:
            y = render_formatted_notes(c, quote['formatted_notes'], margin, y, 
                                      width - 2*margin, default_font_size=9)
            y -= 6
        elif has_notes:
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
    
    # Total - ÚNICO PRECIO MOSTRADO EN NEGRITA Y CENTRADO (formato español)
    total_with_labor = total_materials + labor
    c.setFont('Helvetica-Bold', 14)
    total_text = f"{format_price_es(total_with_labor)} EUROS"
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
    try:
        client_name = quote['client_name'] or ''
    except (KeyError, IndexError, TypeError):
        client_name = ''
    c.drawString(promotor_x, signature_y - 28, client_name)

    c.showPage()
    c.save()


def export_document_to_pdf(formatted_content, out_path):
    """
    Genera PDF directamente desde el contenido formateado del documento editado.
    Aplica ajustes específicos: cliente más a la derecha, firmas lado a lado, word wrapping.
    """
    out_path = Path(out_path)
    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4
    margin = 20*mm
    max_width = width - 2*margin  # Ancho máximo para el texto
    
    # Comenzar más abajo para el folio pre-impreso
    y = height - 80*mm
    
    font_name = 'Times-Roman'
    font_size = 10
    line_height = font_size + 4
    
    c.setFont(font_name, font_size)
    
    # Renderizar línea por línea con ajustes específicos
    lines = formatted_content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Verificar si necesitamos nueva página
        if y < 40*mm:
            c.showPage()
            y = height - 80*mm
            c.setFont(font_name, font_size)
        
        # AJUSTE 1: Mover cliente más a la derecha
        # Detectar líneas con tabs al inicio (datos del cliente)
        if line.startswith('\t'):
            # Contar tabs y reemplazar cada uno por desplazamiento a la derecha
            num_tabs = len(line) - len(line.lstrip('\t'))
            # Mover mucho más a la derecha: usar margen + offset grande
            x_offset = margin + (num_tabs * 20*mm)  # 20mm por cada tab
            line_content = line.lstrip('\t')
            c.drawString(x_offset, y, line_content)
            y -= line_height
            i += 1
            continue
        
        # AJUSTE 2: Detectar y separar firmas HORIZONTALMENTE (lado a lado)
        if 'FIRMA DEL CONSTRUCTOR:' in line and 'FIRMA DEL PROMOTOR:' in line:
            # Separar las dos firmas en columnas
            y -= line_height  # Espacio extra antes
            
            # Columna izquierda: FIRMA DEL CONSTRUCTOR
            left_x = margin
            # Columna derecha: FIRMA DEL PROMOTOR
            right_x = margin + (width - 2*margin) / 2 + 20*mm  # Más separación
            
            # Dibujar títulos de firma
            c.drawString(left_x, y, "FIRMA DEL CONSTRUCTOR:")
            c.drawString(right_x, y, "FIRMA DEL PROMOTOR:")
            y -= line_height * 4  # Espacio para firmar
            
            # Dibujar líneas de firma
            c.drawString(left_x, y, "_______________________")
            c.drawString(right_x, y, "_______________________")
            y -= line_height
            
            # Dibujar nombres debajo
            c.drawString(left_x, y, "BARAJAS PEÑA S.L.")
            
            # Buscar el nombre del cliente en las siguientes líneas
            # El formato es: "BARAJAS PEÑA S.L.                    NombreCliente"
            client_name = ""
            
            # Buscar en las siguientes 5 líneas la que tiene "BARAJAS" y el cliente
            for j in range(i+1, min(i+6, len(lines))):
                current_line = lines[j]
                if 'BARAJAS' in current_line or 'PEÑA' in current_line:
                    # Esta línea tiene ambos nombres, extraer el cliente
                    # Dividir por múltiples espacios y tomar la última parte
                    parts = current_line.split()
                    # Filtrar "BARAJAS", "PEÑA", "S.L."
                    client_parts = [p for p in parts if p not in ['BARAJAS', 'PEÑA', 'S.L.', 'SL', 'S.L']]
                    if client_parts:
                        client_name = ' '.join(client_parts)
                        break
            
            # Si no encontró, buscar cualquier línea que no sea vacía ni tenga guiones
            if not client_name:
                for j in range(i+1, min(i+10, len(lines))):
                    potential = lines[j].strip()
                    if potential and not potential.startswith('_') and 'BARAJAS' not in potential:
                        # Limpiar espacios múltiples
                        client_name = ' '.join(potential.split())
                        if len(client_name) > 3:
                            break
            
            if client_name:
                c.drawString(right_x, y, client_name)
            
            y -= line_height * 2
            i = len(lines)  # Terminar procesamiento, las firmas son lo último
            continue
        
        # AJUSTE 3: Word wrapping para líneas largas
        if line.strip():
            # Calcular ancho de la línea
            text_width = c.stringWidth(line, font_name, font_size)
            
            if text_width > max_width:
                # La línea es muy larga, dividirla
                words = line.split()
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    test_width = c.stringWidth(test_line, font_name, font_size)
                    
                    if test_width <= max_width:
                        current_line = test_line
                    else:
                        # Dibujar la línea actual y empezar una nueva
                        if current_line:
                            c.drawString(margin, y, current_line)
                            y -= line_height
                            if y < 40*mm:
                                c.showPage()
                                y = height - 80*mm
                                c.setFont(font_name, font_size)
                        current_line = word
                
                # Dibujar la última línea
                if current_line:
                    c.drawString(margin, y, current_line)
                    y -= line_height
            else:
                # Línea normal, dibujar directamente
                c.drawString(margin, y, line)
                y -= line_height
        else:
            # AJUSTE 4: Más espacio entre párrafos (líneas vacías)
            y -= line_height * 1.3  # 30% más de espacio
        
        i += 1
    
    c.showPage()
    c.save()
