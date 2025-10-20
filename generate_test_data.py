#!/usr/bin/env python3
"""
Script para generar datos de prueba en la base de datos
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.database import (
    Database, ClienteDAO, TrabajadorDAO, MaterialDAO,
    PresupuestoDAO, ParteTrabajoDAO
)
from src.models.models import Base


def generar_datos_prueba():
    """Genera datos de prueba completos"""

    # Inicializar base de datos
    db = Database()

    # Crear DAOs
    cliente_dao = ClienteDAO(db)
    trabajador_dao = TrabajadorDAO(db)
    material_dao = MaterialDAO(db)
    presupuesto_dao = PresupuestoDAO(db)
    parte_trabajo_dao = ParteTrabajoDAO(db)

    print("🗑️  Limpiando base de datos existente...")
    # Recrear todas las tablas
    Base.metadata.drop_all(db.engine)
    Base.metadata.create_all(db.engine)

    print("👥 Creando clientes...")
    # Crear clientes
    clientes_data = [
        {
            'nombre': 'Juan García',
            'apellidos': 'Martínez',
            'nif_cif': '12345678A',
            'direccion': 'Calle Mayor 123',
            'ciudad': 'Madrid',
            'codigo_postal': '28001',
            'provincia': 'Madrid',
            'telefono': '912345678',
            'email': 'juan.garcia@email.com',
            'notas': 'Cliente preferente, solicita facturas detalladas'
        },
        {
            'nombre': 'María López',
            'apellidos': 'Sánchez',
            'nif_cif': '87654321B',
            'direccion': 'Avenida de la Constitución 45',
            'ciudad': 'Madrid',
            'codigo_postal': '28002',
            'provincia': 'Madrid',
            'telefono': '913456789',
            'email': 'maria.lopez@email.com',
            'notas': 'Proyecto de reforma integral'
        },
        {
            'nombre': 'Constructora Alba S.L.',
            'empresa': 'Constructora Alba S.L.',
            'nif_cif': 'B12345678',
            'direccion': 'Polígono Industrial Sur, Nave 7',
            'ciudad': 'Arganda del Rey',
            'codigo_postal': '28500',
            'provincia': 'Madrid',
            'telefono': '918765432',
            'email': 'info@constructoraalba.com',
            'notas': 'Empresa asociada, descuento del 10%'
        },
        {
            'nombre': 'Pedro Fernández',
            'apellidos': 'González',
            'nif_cif': '45678912C',
            'direccion': 'Calle del Sol 89',
            'ciudad': 'Madrid',
            'codigo_postal': '28003',
            'provincia': 'Madrid',
            'telefono': '915678901',
            'email': 'pedro.fernandez@gmail.com',
            'notas': 'Obra nueva, vivienda unifamiliar'
        },
        {
            'nombre': 'Inmobiliaria Hogar Feliz',
            'empresa': 'Inmobiliaria Hogar Feliz',
            'nif_cif': 'B87654321',
            'direccion': 'Gran Vía 234',
            'ciudad': 'Madrid',
            'codigo_postal': '28013',
            'provincia': 'Madrid',
            'telefono': '911234567',
            'email': 'contacto@hogarfeliz.es',
            'notas': 'Cliente corporativo, múltiples proyectos'
        }
    ]

    clientes = []
    for datos in clientes_data:
        cliente = cliente_dao.crear(**datos)
        clientes.append(cliente)
        print(f"  ✓ Cliente creado: {cliente.nombre}")

    print(f"\n👷 Creando trabajadores...")
    # Crear trabajadores
    trabajadores_data = [
        {
            'nombre': 'Carlos',
            'apellidos': 'Rodríguez García',
            'dni': '11223344D',
            'direccion': 'Calle Trabajo 12, 28010 Madrid',
            'telefono': '654321098',
            'puesto': 'Albañil',
            'coste_hora': 18.50,
            'activo': 1
        },
        {
            'nombre': 'Antonio',
            'apellidos': 'Martín López',
            'dni': '22334455E',
            'direccion': 'Avenida Obrera 34, 28011 Madrid',
            'telefono': '654987654',
            'puesto': 'Electricista',
            'coste_hora': 22.00,
            'activo': 1
        },
        {
            'nombre': 'José Luis',
            'apellidos': 'Pérez Sánchez',
            'dni': '33445566F',
            'direccion': 'Calle Taller 56, 28012 Madrid',
            'telefono': '655123456',
            'puesto': 'Fontanero',
            'coste_hora': 20.00,
            'activo': 1
        },
        {
            'nombre': 'Francisco',
            'apellidos': 'Jiménez Ruiz',
            'dni': '44556677G',
            'direccion': 'Plaza Construcción 7, 28013 Madrid',
            'telefono': '656789012',
            'puesto': 'Carpintero',
            'coste_hora': 19.50,
            'activo': 1
        },
        {
            'nombre': 'Manuel',
            'apellidos': 'Torres Moreno',
            'dni': '55667788H',
            'direccion': 'Calle Reforma 90, 28014 Madrid',
            'telefono': '657345678',
            'puesto': 'Pintor',
            'coste_hora': 17.00,
            'activo': 1
        },
        {
            'nombre': 'Ayudante',
            'apellidos': 'Genérico 1',
            'dni': '',
            'direccion': '',
            'telefono': '600000001',
            'puesto': 'Ayudante',
            'coste_hora': 12.00,
            'activo': 1
        },
        {
            'nombre': 'Ayudante',
            'apellidos': 'Genérico 2',
            'dni': '',
            'direccion': '',
            'telefono': '600000002',
            'puesto': 'Ayudante',
            'coste_hora': 12.00,
            'activo': 1
        }
    ]

    trabajadores = []
    for datos in trabajadores_data:
        trabajador = trabajador_dao.crear(**datos)
        trabajadores.append(trabajador)
        print(f"  ✓ Trabajador creado: {trabajador.nombre} {trabajador.apellidos} ({trabajador.puesto})")

    print(f"\n🧱 Creando materiales...")
    # Crear materiales
    materiales_data = [
        # Materiales de construcción
        {'nombre': 'Cemento Portland (saco 25kg)', 'unidad': 'ud', 'precio_compra': 8.50, 'precio_venta': 10.50},
        {'nombre': 'Arena lavada (m³)', 'unidad': 'm³', 'precio_compra': 25.00, 'precio_venta': 30.00},
        {'nombre': 'Grava (m³)', 'unidad': 'm³', 'precio_compra': 28.00, 'precio_venta': 35.00},
        {'nombre': 'Ladrillo hueco doble', 'unidad': 'ud', 'precio_compra': 0.35, 'precio_venta': 0.45},
        {'nombre': 'Ladrillo macizo', 'unidad': 'ud', 'precio_compra': 0.45, 'precio_venta': 0.55},
        {'nombre': 'Bloque hormigón 20x20x40', 'unidad': 'ud', 'precio_compra': 1.20, 'precio_venta': 1.50},
        {'nombre': 'Mortero preparado (saco 25kg)', 'unidad': 'ud', 'precio_compra': 6.80, 'precio_venta': 8.50},

        # Materiales de acabado
        {'nombre': 'Azulejo blanco 20x20', 'unidad': 'm²', 'precio_compra': 12.50, 'precio_venta': 16.00},
        {'nombre': 'Gres porcelánico imitación madera', 'unidad': 'm²', 'precio_compra': 28.00, 'precio_venta': 36.00},
        {'nombre': 'Pintura plástica blanca interior (15L)', 'unidad': 'ud', 'precio_compra': 45.00, 'precio_venta': 55.00},
        {'nombre': 'Pintura esmalte satinado (4L)', 'unidad': 'ud', 'precio_compra': 32.00, 'precio_venta': 40.00},
        {'nombre': 'Yeso blanco (saco 25kg)', 'unidad': 'ud', 'precio_compra': 7.50, 'precio_venta': 9.50},
        {'nombre': 'Pladur tipo A 13mm', 'unidad': 'm²', 'precio_compra': 8.90, 'precio_venta': 11.50},

        # Materiales eléctricos
        {'nombre': 'Cable RZ1-K 1x2,5mm² (rollo 100m)', 'unidad': 'ud', 'precio_compra': 45.00, 'precio_venta': 55.00},
        {'nombre': 'Cable RZ1-K 1x4mm² (rollo 100m)', 'unidad': 'ud', 'precio_compra': 68.00, 'precio_venta': 85.00},
        {'nombre': 'Tubo corrugado PVC Ø20mm (rollo 50m)', 'unidad': 'ud', 'precio_compra': 15.50, 'precio_venta': 19.50},
        {'nombre': 'Caja mecanismos universal', 'unidad': 'ud', 'precio_compra': 0.45, 'precio_venta': 0.65},
        {'nombre': 'Interruptor blanco', 'unidad': 'ud', 'precio_compra': 3.20, 'precio_venta': 4.50},
        {'nombre': 'Base enchufe schuko blanca', 'unidad': 'ud', 'precio_compra': 3.80, 'precio_venta': 5.20},
        {'nombre': 'Cuadro eléctrico 24 elementos', 'unidad': 'ud', 'precio_compra': 65.00, 'precio_venta': 85.00},
        {'nombre': 'Magnetotérmico 2P 25A', 'unidad': 'ud', 'precio_compra': 12.50, 'precio_venta': 16.00},
        {'nombre': 'Diferencial 2P 40A 30mA', 'unidad': 'ud', 'precio_compra': 35.00, 'precio_venta': 45.00},

        # Fontanería
        {'nombre': 'Tubo multicapa Ø16mm (barra 5m)', 'unidad': 'ud', 'precio_compra': 18.00, 'precio_venta': 23.00},
        {'nombre': 'Tubo multicapa Ø20mm (barra 5m)', 'unidad': 'ud', 'precio_compra': 24.00, 'precio_venta': 30.00},
        {'nombre': 'Codo multicapa 90° Ø16mm', 'unidad': 'ud', 'precio_compra': 0.85, 'precio_venta': 1.10},
        {'nombre': 'Codo multicapa 90° Ø20mm', 'unidad': 'ud', 'precio_compra': 1.10, 'precio_venta': 1.45},
        {'nombre': 'Llave de paso Ø20mm', 'unidad': 'ud', 'precio_compra': 8.50, 'precio_venta': 11.00},
        {'nombre': 'Grifo monomando lavabo cromado', 'unidad': 'ud', 'precio_compra': 45.00, 'precio_venta': 60.00},
        {'nombre': 'Grifo monomando ducha cromado', 'unidad': 'ud', 'precio_compra': 65.00, 'precio_venta': 85.00},
        {'nombre': 'Inodoro completo con tapa', 'unidad': 'ud', 'precio_compra': 120.00, 'precio_venta': 155.00},
        {'nombre': 'Lavabo suspendido 60cm', 'unidad': 'ud', 'precio_compra': 85.00, 'precio_venta': 110.00},

        # Carpintería
        {'nombre': 'Puerta interior lisa blanca 72,5x203', 'unidad': 'ud', 'precio_compra': 95.00, 'precio_venta': 120.00},
        {'nombre': 'Puerta interior lisa blanca 82,5x203', 'unidad': 'ud', 'precio_compra': 105.00, 'precio_venta': 135.00},
        {'nombre': 'Marco puerta blanco 72,5cm', 'unidad': 'ud', 'precio_compra': 28.00, 'precio_venta': 36.00},
        {'nombre': 'Marco puerta blanco 82,5cm', 'unidad': 'ud', 'precio_compra': 32.00, 'precio_venta': 42.00},
        {'nombre': 'Manivela puerta cromada', 'unidad': 'ud', 'precio_compra': 12.50, 'precio_venta': 16.50},
        {'nombre': 'Cerradura embutir 40mm', 'unidad': 'ud', 'precio_compra': 18.00, 'precio_venta': 23.50},
        {'nombre': 'Rodapié MDF blanco 7cm (barra 2,4m)', 'unidad': 'ud', 'precio_compra': 4.50, 'precio_venta': 6.00},

        # Otros
        {'nombre': 'Silicona neutra cartucho', 'unidad': 'ud', 'precio_compra': 3.20, 'precio_venta': 4.50},
        {'nombre': 'Espuma poliuretano spray', 'unidad': 'ud', 'precio_compra': 6.50, 'precio_venta': 8.50},
        {'nombre': 'Tornillería variada (caja)', 'unidad': 'ud', 'precio_compra': 12.00, 'precio_venta': 15.00},
        {'nombre': 'Adhesivo cementoso (saco 25kg)', 'unidad': 'ud', 'precio_compra': 8.90, 'precio_venta': 11.50},
    ]

    materiales = []
    for datos in materiales_data:
        material = material_dao.crear(**datos)
        materiales.append(material)
        print(f"  ✓ Material creado: {material.nombre}")

    print(f"\n📋 Creando presupuestos...")
    # Crear presupuestos
    presupuestos_data = [
        {
            'numero': 'PRE-2025-001',
            'cliente': clientes[0],  # Juan García
            'fecha_creacion': datetime.now() - timedelta(days=15),
            'lineas': [
                (materiales[0], 20, 1.15),  # Cemento
                (materiales[1], 3, 1.20),   # Arena
                (materiales[3], 500, 1.10), # Ladrillos
                (materiales[9], 3, 1.25),   # Pintura
            ],
            'titulo': 'Reforma baño principal',
            'descripcion': 'Reforma completa de baño con cambio de sanitarios y alicatado',
            'estado': 'enviado'
        },
        {
            'numero': 'PRE-2025-002',
            'cliente': clientes[1],  # María López
            'fecha_creacion': datetime.now() - timedelta(days=10),
            'lineas': [
                (materiales[8], 45, 1.20),  # Gres porcelánico
                (materiales[12], 35, 1.15), # Pladur
                (materiales[31], 3, 1.10),  # Puertas
                (materiales[9], 5, 1.20),   # Pintura
                (materiales[17], 15, 1.15), # Enchufes
            ],
            'titulo': 'Reforma integral vivienda 90m²',
            'descripcion': 'Reforma completa incluyendo electricidad, fontanería y acabados',
            'estado': 'aceptado'
        },
        {
            'numero': 'PRE-2025-003',
            'cliente': clientes[2],  # Constructora Alba
            'fecha_creacion': datetime.now() - timedelta(days=5),
            'lineas': [
                (materiales[13], 5, 1.05),  # Cable 2,5mm
                (materiales[14], 3, 1.05),  # Cable 4mm
                (materiales[19], 1, 1.05),  # Cuadro eléctrico
                (materiales[20], 8, 1.05),  # Magnetotérmicos
                (materiales[21], 2, 1.05),  # Diferenciales
            ],
            'titulo': 'Instalación eléctrica edificio oficinas',
            'descripcion': 'Instalación eléctrica completa para edificio de 3 plantas',
            'estado': 'enviado'
        },
        {
            'numero': 'PRE-2025-004',
            'cliente': clientes[3],  # Pedro Fernández
            'fecha_creacion': datetime.now() - timedelta(days=2),
            'lineas': [
                (materiales[22], 15, 1.15),  # Tubo multicapa 16mm
                (materiales[23], 10, 1.15),  # Tubo multicapa 20mm
                (materiales[27], 3, 1.20),   # Grifo lavabo
                (materiales[28], 2, 1.20),   # Grifo ducha
                (materiales[29], 2, 1.15),   # Inodoro
                (materiales[30], 2, 1.15),   # Lavabo
            ],
            'titulo': 'Instalación fontanería vivienda nueva',
            'descripcion': 'Instalación completa de fontanería para vivienda unifamiliar',
            'estado': 'borrador'
        },
        {
            'numero': 'PRE-2025-005',
            'cliente': clientes[4],  # Inmobiliaria Hogar Feliz
            'fecha_creacion': datetime.now(),
            'lineas': [
                (materiales[7], 120, 1.25),  # Azulejo
                (materiales[8], 180, 1.20),  # Gres
                (materiales[9], 15, 1.20),   # Pintura plástica
                (materiales[10], 8, 1.20),   # Pintura esmalte
                (materiales[31], 12, 1.15),  # Puertas 72,5
                (materiales[35], 12, 1.10),  # Manivelas
            ],
            'titulo': 'Acabados 4 viviendas promoción',
            'descripcion': 'Acabados para 4 viviendas en promoción nueva construcción',
            'estado': 'aceptado'
        }
    ]

    presupuestos = []
    for datos in presupuestos_data:
        presupuesto = presupuesto_dao.crear(
            numero=datos['numero'],
            cliente_id=datos['cliente'].id,
            fecha_creacion=datos['fecha_creacion'],
            titulo=datos['titulo'],
            descripcion=datos['descripcion'],
            estado=datos['estado']
        )

        # Añadir líneas
        session = db.get_session()
        try:
            from src.models.models import LineaPresupuesto
            for idx, (material, cantidad, margen) in enumerate(datos['lineas']):
                linea = LineaPresupuesto(
                    presupuesto_id=presupuesto.id,
                    material_id=material.id,
                    cantidad=cantidad,
                    precio_compra_unitario=material.precio_compra,
                    margen_ganancia_porc=margen,
                    orden=idx
                )
                session.add(linea)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"    ⚠️  Error al añadir líneas: {e}")
        finally:
            db.close_session(session)

        presupuestos.append(presupuesto)
        print(f"  ✓ Presupuesto creado: {presupuesto.titulo} - Cliente: {datos['cliente'].nombre}")

    print(f"\n📝 Creando partes de trabajo...")
    # Crear partes de trabajo
    partes_data = [
        {
            'numero': 'PT-2025-001',
            'presupuesto': presupuestos[0],  # Reforma baño Juan García
            'fecha_inicio': (datetime.now() - timedelta(days=7)).date(),
            'trabajadores': [
                (trabajadores[0], 8.0, 'Demolición y obra de albañilería'),
                (trabajadores[5], 8.0, 'Ayuda en albañilería'),
            ],
            'materiales': [
                (materiales[0], 5),
                (materiales[6], 10),
            ],
            'titulo': 'Parte día 1 - Reforma baño Juan García',
            'descripcion': 'Demolición alicatado antiguo y preparación de paredes',
            'estado': 'finalizado'
        },
        {
            'numero': 'PT-2025-002',
            'presupuesto': presupuestos[1],  # Reforma María López
            'fecha_inicio': (datetime.now() - timedelta(days=6)).date(),
            'trabajadores': [
                (trabajadores[1], 7.5, 'Instalación eléctrica nueva'),
                (trabajadores[2], 6.0, 'Instalación fontanería'),
            ],
            'materiales': [
                (materiales[13], 2),
                (materiales[15], 3),
                (materiales[22], 5),
            ],
            'titulo': 'Parte día 1 - Reforma María López',
            'descripcion': 'Instalaciones eléctricas y fontanería primera fase',
            'estado': 'en_curso'
        },
        {
            'numero': 'PT-2025-003',
            'presupuesto': presupuestos[1],  # Reforma María López
            'fecha_inicio': (datetime.now() - timedelta(days=5)).date(),
            'trabajadores': [
                (trabajadores[3], 8.0, 'Instalación puertas y marcos'),
                (trabajadores[6], 8.0, 'Ayuda carpintería'),
            ],
            'materiales': [
                (materiales[31], 3),
                (materiales[33], 3),
                (materiales[35], 3),
            ],
            'titulo': 'Parte día 2 - Reforma María López',
            'descripcion': 'Instalación de carpintería interior',
            'estado': 'en_curso'
        },
        {
            'numero': 'PT-2025-004',
            'presupuesto': presupuestos[3],  # Fontanería Pedro Fernández
            'fecha_inicio': (datetime.now() - timedelta(days=3)).date(),
            'trabajadores': [
                (trabajadores[2], 8.0, 'Instalación fontanería completa'),
                (trabajadores[5], 6.0, 'Ayuda fontanería'),
            ],
            'materiales': [
                (materiales[22], 8),
                (materiales[23], 6),
                (materiales[24], 15),
                (materiales[25], 10),
                (materiales[26], 1),
            ],
            'titulo': 'Parte día 1 - Fontanería Pedro Fernández',
            'descripcion': 'Instalación de tuberías agua fría y caliente',
            'estado': 'en_curso'
        },
        {
            'numero': 'PT-2025-005',
            'presupuesto': presupuestos[4],  # Inmobiliaria promoción
            'fecha_inicio': (datetime.now() - timedelta(days=1)).date(),
            'trabajadores': [
                (trabajadores[4], 8.0, 'Pintura 2 viviendas'),
                (trabajadores[6], 8.0, 'Ayuda pintura'),
            ],
            'materiales': [
                (materiales[9], 6),
                (materiales[10], 3),
            ],
            'titulo': 'Parte día 1 - Pintura promoción',
            'descripcion': 'Pintura interior de 2 viviendas',
            'estado': 'en_curso'
        }
    ]

    partes = []
    for datos in partes_data:
        parte = parte_trabajo_dao.crear(
            numero=datos['numero'],
            presupuesto_id=datos['presupuesto'].id if datos.get('presupuesto') else None,
            fecha_inicio=datos['fecha_inicio'],
            titulo=datos['titulo'],
            descripcion=datos['descripcion'],
            estado=datos['estado']
        )

        # Añadir trabajadores y materiales
        session = db.get_session()
        try:
            from src.models.models import DetalleManoObra, MaterialUsado

            # Añadir trabajadores
            for trabajador, horas, labor in datos['trabajadores']:
                detalle = DetalleManoObra(
                    parte_trabajo_id=parte.id,
                    trabajador_id=trabajador.id,
                    fecha=datos['fecha_inicio'],
                    horas=horas,
                    coste_hora_aplicado=trabajador.coste_hora,
                    labor_realizada=labor
                )
                session.add(detalle)

            # Añadir materiales
            for material, cantidad in datos['materiales']:
                material_usado = MaterialUsado(
                    parte_trabajo_id=parte.id,
                    material_id=material.id,
                    cantidad=cantidad,
                    precio_compra_unitario=material.precio_compra,
                    fecha_uso=datos['fecha_inicio']
                )
                session.add(material_usado)

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"    ⚠️  Error al añadir detalles: {e}")
        finally:
            db.close_session(session)

        partes.append(parte)
        print(f"  ✓ Parte creado: {parte.titulo}")

    print(f"\n✅ Generación completada!")
    print(f"\n📊 Resumen:")
    print(f"   • {len(clientes)} clientes")
    print(f"   • {len(trabajadores)} trabajadores")
    print(f"   • {len(materiales)} materiales")
    print(f"   • {len(presupuestos)} presupuestos")
    print(f"   • {len(partes)} partes de trabajo")
    print(f"\n💾 Base de datos: {db.db_path}")


if __name__ == '__main__':
    try:
        generar_datos_prueba()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
