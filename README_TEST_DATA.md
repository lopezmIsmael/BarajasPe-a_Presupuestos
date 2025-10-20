# Generador de Datos de Prueba

Este script genera datos de prueba completos para la aplicación de gestión de constructora.

## Uso

```bash
# Activar el entorno virtual
source myenv/bin/activate

# Ejecutar el script
python generate_test_data.py
```

## Datos Generados

El script genera:

### 👥 **5 Clientes**
- **Juan García Martínez** - Cliente individual, DNI 12345678A
- **María López Sánchez** - Cliente individual, DNI 87654321B
- **Constructora Alba S.L.** - Empresa, CIF B12345678 (cliente corporativo con descuento)
- **Pedro Fernández González** - Cliente individual, DNI 45678912C
- **Inmobiliaria Hogar Feliz** - Empresa, CIF B87654321 (cliente corporativo)

### 👷 **7 Trabajadores**
- **Carlos Rodríguez García** - Albañil (18.50€/h)
- **Antonio Martín López** - Electricista (22.00€/h)
- **José Luis Pérez Sánchez** - Fontanero (20.00€/h)
- **Francisco Jiménez Ruiz** - Carpintero (19.50€/h)
- **Manuel Torres Moreno** - Pintor (17.00€/h)
- **Ayudante Genérico 1** - Ayudante sin DNI (12.00€/h)
- **Ayudante Genérico 2** - Ayudante sin DNI (12.00€/h)

### 🧱 **42 Materiales**
Incluye materiales de:
- Construcción (cemento, arena, ladrillos, bloques)
- Acabados (azulejos, gres, pinturas, yeso, pladur)
- Electricidad (cables, tubos, cajas, interruptores, enchufes, cuadros)
- Fontanería (tubos multicapa, codos, llaves, grifos, sanitarios)
- Carpintería (puertas, marcos, manivelas, cerraduras, rodapiés)
- Otros (silicona, espuma, tornillería, adhesivos)

### 📋 **5 Presupuestos**
1. **PRE-2025-001** - Reforma baño principal (Juan García) - Estado: enviado
2. **PRE-2025-002** - Reforma integral 90m² (María López) - Estado: aceptado
3. **PRE-2025-003** - Instalación eléctrica edificio (Constructora Alba) - Estado: enviado
4. **PRE-2025-004** - Instalación fontanería vivienda (Pedro Fernández) - Estado: borrador
5. **PRE-2025-005** - Acabados 4 viviendas (Inmobiliaria) - Estado: aceptado

Cada presupuesto incluye múltiples líneas de materiales con cantidades y márgenes de ganancia.

### 📝 **5 Partes de Trabajo**
1. **PT-2025-001** - Reforma baño (Juan García) - Estado: finalizado
2. **PT-2025-002** - Instalaciones reforma (María López) - Estado: en_curso
3. **PT-2025-003** - Carpintería reforma (María López) - Estado: en_curso
4. **PT-2025-004** - Fontanería (Pedro Fernández) - Estado: en_curso
5. **PT-2025-005** - Pintura promoción (Inmobiliaria) - Estado: en_curso

Cada parte incluye detalles de mano de obra (trabajadores y horas) y materiales utilizados.

## Características

- ✅ Limpia la base de datos existente antes de generar nuevos datos
- ✅ Datos realistas con nombres, direcciones y precios de mercado
- ✅ Relaciones correctas entre presupuestos, partes de trabajo y clientes
- ✅ Diferentes estados para presupuestos y partes de trabajo
- ✅ Márgenes de ganancia variables según tipo de material
- ✅ Trabajadores con DNI y sin DNI (para probar validación)
- ✅ Empresas y particulares como clientes

## Notas

- El script **borra toda la base de datos existente** antes de crear los datos de prueba
- La base de datos generada se guarda como `constructora.db`
- Los precios incluyen precio de compra y precio de venta para cada material
- Las fechas están distribuidas en los últimos 15 días
