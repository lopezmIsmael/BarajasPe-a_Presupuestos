from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from pathlib import Path
from db import get_quote
from PIL import Image

COMPANY_NAME = "Barajar Peña"
BRAND_COLOR = HexColor('#2196F3')

def export_quote_to_pdf(qid, out_path):
    quote, items = get_quote(qid)
    if quote is None:
        raise ValueError('Quote not found')

    out_path = Path(out_path)
    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4
    margin = 20*mm
    y = height - margin

    # Company Header
    c.setFillColor(BRAND_COLOR)
    c.setFont('Helvetica-Bold', 20)
    c.drawString(margin, y, COMPANY_NAME)
    c.setFillColor(HexColor('#000000'))
    y -= 10
    c.setFont('Helvetica-Bold', 16)
    c.drawString(margin, y, f"Presupuesto #{quote['id']}")
    c.setFont('Helvetica', 10)
    y -= 12
    c.drawString(margin, y, f"Fecha: {quote['date']}")
    y -= 18

    # Client
    c.setFont('Helvetica-Bold', 12)
    c.drawString(margin, y, "Cliente:")
    c.setFont('Helvetica', 10)
    c.drawString(margin+60, y, quote['client_name'] or '')
    y -= 14
    if quote['client_address']:
        c.drawString(margin+60, y, quote['client_address'])
        y -= 14
    if quote['client_dni']:
        c.drawString(margin+60, y, f"DNI: {quote['client_dni']}")
        y -= 14

    y -= 6
    c.setFont('Helvetica-Bold', 11)
    c.drawString(margin, y, "Items:")
    y -= 14

    total = 0.0
    for item in items:
        line_total = item['unit_price'] * item['quantity']
        total += line_total
        # If image exists, try to show thumbnail
        if item['image_path']:
            imgp = Path(item['image_path'])
            if imgp.exists():
                try:
                    im = Image.open(imgp)
                    im.thumbnail((80,80))
                    ir = ImageReader(im)
                    c.drawImage(ir, margin, y-60, width=40*mm, height=30*mm)
                    x_text = margin + 45*mm
                except Exception:
                    x_text = margin
            else:
                x_text = margin
        else:
            x_text = margin

        c.setFont('Helvetica-Bold', 10)
        c.drawString(x_text, y, f"{item['name']} x{item['quantity']}")
        y -= 12
        c.setFont('Helvetica', 9)
        if item['description']:
            c.drawString(x_text, y, item['description'])
            y -= 12
        c.drawString(x_text, y, f"{item['unit_price']:.2f} €/u  -  Total: {line_total:.2f} €")
        y -= 30
        if y < 100*mm:
            c.showPage()
            y = height - margin

    # Labor cost
    labor = quote['labor_cost'] or 0.0
    total_with_labor = total + labor

    c.setFont('Helvetica-Bold', 11)
    c.drawString(margin, y, f"Subtotal materiales: {total:.2f} €")
    y -= 14
    c.drawString(margin, y, f"Mano de obra: {labor:.2f} €")
    y -= 14
    c.drawString(margin, y, f"TOTAL: {total_with_labor:.2f} €")

    c.showPage()
    c.save()
