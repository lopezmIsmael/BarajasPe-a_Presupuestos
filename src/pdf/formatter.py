"""
Utilidad para renderizar texto formateado (JSON) en PDF usando ReportLab
"""
import json
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT


def json_to_pdf_paragraphs(json_string, canvas, x, y, max_width, default_font_size=10, bottom_margin=40):
    """
    Renderiza texto formateado desde JSON directamente en el canvas
    CON PAGINACIÓN AUTOMÁTICA
    
    Args:
        json_string: String JSON con segmentos de texto y formatos
        canvas: Canvas de ReportLab
        x, y: Coordenadas iniciales
        max_width: Ancho máximo para el texto
        default_font_size: Tamaño de fuente por defecto
        bottom_margin: Margen inferior antes de crear nueva página
    
    Returns:
        Nueva posición Y después de renderizar
    """
    if not json_string:
        return y
    
    try:
        segments = json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        # Si falla, renderizar como texto plano con paginación
        canvas.setFont('Helvetica', default_font_size)
        text_lines = json_string.split('\n') if isinstance(json_string, str) else []
        for line in text_lines:
            if y < bottom_margin:  # Verificar si necesita nueva página
                canvas.showPage()
                from reportlab.lib.pagesizes import A4
                y = A4[1] - 80  # Resetear Y al inicio de nueva página
            canvas.drawString(x, y, line)
            y -= default_font_size + 2
        return y
    
    # Procesar segmentos
    current_line = []
    current_y = y
    line_height = default_font_size + 4
    
    for segment in segments:
        text = segment.get('text', '')
        formats = segment.get('formats', [])
        
        # Procesar líneas
        lines = text.split('\n')
        
        for i, line_text in enumerate(lines):
            if i > 0:
                # Verificar si necesita nueva página antes de renderizar
                if current_y < bottom_margin:
                    canvas.showPage()
                    from reportlab.lib.pagesizes import A4
                    current_y = A4[1] - 80  # Resetear Y al inicio de nueva página
                
                # Nueva línea: renderizar línea actual y resetear
                _render_line_segments(canvas, current_line, x, current_y, max_width)
                current_y -= line_height
                current_line = []
            
            if line_text:
                # Determinar estilo basado en formatos
                font_name, font_size, underline, strikethrough = _get_font_style(formats, default_font_size)
                
                current_line.append({
                    'text': line_text,
                    'font': font_name,
                    'size': font_size,
                    'underline': underline,
                    'strikethrough': strikethrough
                })
    
    # Renderizar última línea
    if current_line:
        if current_y < bottom_margin:
            canvas.showPage()
            from reportlab.lib.pagesizes import A4
            current_y = A4[1] - 80
        _render_line_segments(canvas, current_line, x, current_y, max_width)
        current_y -= line_height
    
    return current_y


def _get_font_style(formats, default_size):
    """
    Determina el estilo de fuente basado en los formatos
    
    Returns:
        (font_name, font_size, underline, strikethrough)
    """
    font_name = 'Helvetica'
    font_size = default_size
    underline = False
    strikethrough = False
    
    # Detectar tamaño
    for fmt in formats:
        if fmt.startswith('size_'):
            try:
                size_str = fmt.replace('size_', '').replace('_bold', '')
                font_size = int(size_str)
            except ValueError:
                pass
    
    # Detectar negrita
    if 'bold' in formats or any('_bold' in fmt for fmt in formats):
        font_name = 'Helvetica-Bold'
    
    # Detectar subrayado
    if 'underline' in formats:
        underline = True
    
    # Detectar tachado
    if 'strikethrough' in formats:
        strikethrough = True
    
    return font_name, font_size, underline, strikethrough


def _render_line_segments(canvas, segments, x, y, max_width):
    """
    Renderiza una línea de texto con múltiples segmentos de diferente formato
    """
    current_x = x
    
    for seg in segments:
        text = seg['text']
        font = seg['font']
        size = seg['size']
        underline = seg['underline']
        strikethrough = seg['strikethrough']
        
        # Configurar fuente
        canvas.setFont(font, size)
        
        # Dibujar texto
        canvas.drawString(current_x, y, text)
        
        # Calcular ancho del texto
        text_width = canvas.stringWidth(text, font, size)
        
        # Aplicar subrayado si es necesario
        if underline:
            underline_y = y - 2
            canvas.line(current_x, underline_y, current_x + text_width, underline_y)
        
        # Aplicar tachado si es necesario
        if strikethrough:
            strike_y = y + size * 0.3
            canvas.line(current_x, strike_y, current_x + text_width, strike_y)
        
        # Avanzar x
        current_x += text_width


def render_formatted_notes(canvas, json_string, x, y, max_width, default_font_size=10):
    """
    Función principal para renderizar notas formateadas en el PDF
    
    Args:
        canvas: Canvas de ReportLab
        json_string: String JSON con el contenido formateado
        x, y: Coordenadas iniciales
        max_width: Ancho máximo
        default_font_size: Tamaño de fuente por defecto
    
    Returns:
        Nueva posición Y después de renderizar
    """
    return json_to_pdf_paragraphs(json_string, canvas, x, y, max_width, default_font_size)
