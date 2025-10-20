"""
Motor de plantillas para generación de documentos HTML.
"""
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from src.utils.helpers import format_currency, format_date


class TemplateEngine:
    """Motor para renderizar plantillas HTML"""

    def __init__(self):
        """Inicializa el motor de plantillas"""
        template_dir = os.path.dirname(os.path.abspath(__file__))
        self.env = Environment(loader=FileSystemLoader(template_dir))

        # Añadir filtros personalizados
        self.env.filters['currency'] = format_currency
        self.env.filters['date'] = format_date

    def render_quote(self, presupuesto, simple=True):
        """
        Renderiza un presupuesto a HTML.

        Args:
            presupuesto: Objeto Presupuesto
            simple: Si True, usa plantilla simple tipo carta

        Returns:
            String con HTML renderizado
        """
        template_name = 'quote_template_simple.html' if simple else 'quote_template.html'
        template = self.env.get_template(template_name)

        # Preparar datos
        lineas_data = []
        for linea in presupuesto.lineas:
            lineas_data.append({
                'material_nombre': linea.material.nombre,
                'descripcion_personalizada': linea.descripcion_personalizada,
                'cantidad': f"{linea.cantidad:.2f}",
                'cantidad_simple': f"{linea.cantidad:.1f}",  # Para plantilla simple
                'unidad': linea.material.unidad,
                'precio_venta_unitario': format_currency(linea.precio_venta_unitario),
                'precio_venta_total': format_currency(linea.precio_venta_total)
            })

        context = {
            'numero': presupuesto.numero,
            'fecha': format_date(presupuesto.fecha_creacion),
            'fecha_validez': format_date(presupuesto.fecha_validez) if presupuesto.fecha_validez else 'N/A',
            'estado': presupuesto.estado.upper(),
            'cliente_nombre': f"{presupuesto.cliente.nombre} {presupuesto.cliente.apellidos or ''}".strip(),
            'cliente_empresa': presupuesto.cliente.empresa,
            'cliente_nif': presupuesto.cliente.nif_cif,
            'cliente_direccion': presupuesto.cliente.direccion,
            'cliente_ciudad': presupuesto.cliente.ciudad,
            'cliente_cp': presupuesto.cliente.codigo_postal,
            'cliente_telefono': presupuesto.cliente.telefono,
            'cliente_email': presupuesto.cliente.email,
            'titulo': presupuesto.titulo,
            'descripcion': presupuesto.descripcion,
            'lineas': lineas_data,
            'total_materiales_venta': format_currency(presupuesto.total_materiales_venta),
            'coste_mano_obra': presupuesto.coste_mano_obra,
            'subtotal': format_currency(presupuesto.subtotal),
            'descuento_global': presupuesto.descuento_global,
            'descuento_importe': format_currency(presupuesto.descuento_importe),
            'total_final': format_currency(presupuesto.total_final),
            'notas_internas': presupuesto.notas_internas
        }

        return template.render(**context)

    def render_work_report(self, parte):
        """
        Renderiza un parte de trabajo a HTML.

        Args:
            parte: Objeto ParteTrabajo

        Returns:
            String con HTML renderizado
        """
        template = self.env.get_template('work_report_template.html')

        # Preparar datos de mano de obra
        detalles_mo_data = []
        for detalle in parte.detalles_mano_obra:
            detalles_mo_data.append({
                'trabajador_nombre': f"{detalle.trabajador.nombre} {detalle.trabajador.apellidos}",
                'fecha': format_date(detalle.fecha),
                'horas': f"{detalle.horas:.2f}",
                'coste_hora': format_currency(detalle.coste_hora_aplicado),
                'total': format_currency(detalle.coste_total),
                'labor_realizada': detalle.labor_realizada,
                'comentarios': detalle.comentarios
            })

        # Preparar datos de materiales
        materiales_data = []
        for mat in parte.materiales_usados:
            materiales_data.append({
                'material_nombre': mat.material.nombre,
                'fecha_uso': format_date(mat.fecha_uso),
                'cantidad': f"{mat.cantidad:.2f}",
                'unidad': mat.material.unidad,
                'precio_unitario': format_currency(mat.precio_compra_unitario),
                'total': format_currency(mat.coste_total)
            })

        context = {
            'numero': parte.numero,
            'fecha_inicio': format_date(parte.fecha_inicio),
            'fecha_fin': format_date(parte.fecha_fin) if parte.fecha_fin else 'En curso',
            'estado': parte.estado,
            'titulo': parte.titulo,
            'descripcion': parte.descripcion,
            'ubicacion': parte.ubicacion,
            'presupuesto_numero': parte.presupuesto.numero if parte.presupuesto else None,
            'detalles_mano_obra': detalles_mo_data,
            'materiales_usados': materiales_data,
            'total_horas': f"{parte.total_horas:.2f}",
            'total_mano_obra': format_currency(parte.total_coste_mano_obra),
            'total_materiales': format_currency(parte.total_coste_materiales),
            'coste_total': format_currency(parte.coste_total),
            'notas': parte.notas,
            'fecha_actual': format_date(datetime.now())
        }

        return template.render(**context)
