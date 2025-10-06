"""
Generador de preview de PDF desde contenido formateado JSON
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
from src.pdf.formatter import render_formatted_notes

# Intentar importar pdf2image
try:
    from pdf2image import convert_from_bytes
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False


def generate_document_preview(formatted_content):
    """
    Genera una imagen de preview del documento formateado
    
    Args:
        formatted_content: String JSON con el contenido formateado
    
    Returns:
        PIL.Image: Imagen del PDF para mostrar en la UI
    """
    if not formatted_content:
        return None
    
    # Crear PDF en memoria
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 20*mm
    
    # Comenzar más abajo para el folio pre-impreso
    y = height - 80*mm
    
    # Renderizar el contenido formateado
    try:
        y = render_formatted_notes(c, formatted_content, margin, y, width - 2*margin, default_font_size=10)
    except Exception as e:
        print(f"Error renderizando contenido formateado: {e}")
        # Fallback: renderizar como texto plano
        c.setFont('Helvetica', 10)
        if isinstance(formatted_content, str):
            lines = formatted_content.split('\n')[:50]  # Limitar líneas
            for line in lines:
                c.drawString(margin, y, line[:80])  # Limitar ancho
                y -= 12
    
    c.showPage()
    c.save()
    
    # Convertir PDF a imagen
    pdf_bytes = buffer.getvalue()
    
    if HAS_PDF2IMAGE:
        try:
            images = convert_from_bytes(pdf_bytes, dpi=150)
            if images:
                return images[0]
        except Exception as e:
            print(f"Error convirtiendo PDF a imagen: {e}")
    
    # Fallback: crear una imagen simple con mensaje
    img = Image.new('RGB', (595, 842), color='white')
    return img
