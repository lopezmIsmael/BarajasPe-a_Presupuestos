# Gestión de Constructora - Barajas Peña Presupuestos

Aplicación de gestión integral para empresas constructoras, desarrollada con Python, PyQt6 y SQLite.

## Características

### ✅ Funcionalidades Implementadas (Fases 1, 2 y 4)

- **Gestión de Clientes**: CRUD completo con búsqueda, validación de NIF/CIF, email y teléfono
- **Gestión de Materiales**: Control de inventario con precios de compra/venta y cálculo automático de márgenes
- **Gestión de Trabajadores**: Control de personal con coste por hora y estado activo/inactivo
- **Presupuestos Completos**:
  - Creación y edición de presupuestos
  - Adición de líneas de materiales con cálculo automático
  - Margen de ganancia personalizable por línea
  - Cálculo automático de totales, ganancias y precios finales
  - Descuento global
  - Asociación a clientes
  - Creación rápida de clientes y materiales desde el mismo formulario
- **Partes de Trabajo**:
  - Registro de trabajos realizados
  - Control de horas de trabajo por día y trabajador
  - Registro de materiales consumidos
  - Cálculo automático de costes
  - Asociación opcional a presupuestos
  - Control de múltiples días de trabajo

### 🚧 Funcionalidades Pendientes (Fase 3)

- **Edición WYSIWYG**: Integración de QWebEngineView con editor HTML/JS (Quill)
- **Generación de PDF**: Exportación de presupuestos y partes a PDF con plantillas HTML/CSS
- **Plantillas HTML**: Diseño profesional para documentos

## Requisitos

- Python 3.8 o superior
- Windows 10 (compatible también con Linux y macOS)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd BarajasPe-a_Presupuestos
```

2. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
```

3. Activar el entorno virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/macOS:
```bash
source venv/bin/activate
```

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar la aplicación:

```bash
python main.py
```

### Primera Ejecución

Al ejecutar la aplicación por primera vez, se creará automáticamente la base de datos SQLite (`constructora.db`) con todas las tablas necesarias.

### Flujo de Trabajo Recomendado

1. **Configurar Datos Maestros**:
   - Ir a la pestaña "Clientes" y añadir clientes
   - Ir a "Materiales" y añadir el catálogo de materiales con precios
   - Ir a "Trabajadores" y registrar al personal con sus costes/hora

2. **Crear Presupuestos**:
   - Ir a la pestaña "Presupuestos"
   - Hacer clic en "Nuevo Presupuesto"
   - Seleccionar cliente (o crear uno nuevo desde el botón "+")
   - Añadir líneas de materiales (o crear materiales nuevos desde el botón "+")
   - Los cálculos se actualizan automáticamente
   - Guardar el presupuesto

3. **Gestionar Partes de Trabajo**:
   - Ir a "Partes de Trabajo"
   - Crear un nuevo parte (opcionalmente asociado a un presupuesto)
   - Registrar trabajos realizados (trabajador, fecha, horas, labor)
   - Registrar materiales consumidos
   - Los costes se calculan automáticamente

## Estructura del Proyecto

```
BarajasPe-a_Presupuestos/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
├── constructora.db        # Base de datos SQLite (se crea automáticamente)
├── src/
│   ├── models/
│   │   └── models.py      # Modelos de datos (SQLAlchemy)
│   ├── database/
│   │   └── database.py    # Capa de acceso a datos (DAOs)
│   ├── ui/
│   │   ├── main_window.py           # Ventana principal
│   │   ├── clients_manager.py       # Gestión de clientes
│   │   ├── materials_manager.py     # Gestión de materiales
│   │   ├── workers_manager.py       # Gestión de trabajadores
│   │   ├── quotes_manager.py        # Gestión de presupuestos
│   │   └── work_reports_manager.py  # Gestión de partes de trabajo
│   ├── utils/
│   │   └── helpers.py     # Funciones auxiliares
│   └── templates/         # Plantillas HTML (Fase 3)
└── resources/             # Recursos (iconos, estilos)
```

## Características Técnicas

### Base de Datos

La aplicación utiliza SQLite como base de datos embebida. El esquema incluye:

- **clientes**: Información de clientes
- **trabajadores**: Datos de empleados y costes
- **materiales**: Catálogo de materiales con precios
- **presupuestos**: Cabeceras de presupuestos
- **lineas_presupuesto**: Detalle de líneas de materiales
- **partes_trabajo**: Cabeceras de partes de trabajo
- **detalles_mano_obra**: Registros de trabajo realizado
- **materiales_usados**: Materiales consumidos en partes

### Cálculos Automáticos

#### Presupuestos:
- **Coste Total Materiales** = Σ(Cantidad × Precio Compra)
- **Ganancia por Línea** = (Precio Compra × Margen %) × Cantidad
- **Precio Venta Material** = Coste + Ganancia
- **Subtotal** = Total Materiales Venta + Coste Mano de Obra
- **Descuento** = Subtotal × (Descuento % / 100)
- **PRECIO FINAL** = Subtotal - Descuento

#### Partes de Trabajo:
- **Coste Mano de Obra** = Σ(Horas × Coste/Hora)
- **Coste Materiales** = Σ(Cantidad × Precio Unitario)
- **COSTE TOTAL** = Coste Mano de Obra + Coste Materiales

## Atajos de Teclado

- `Ctrl+P`: Nuevo Presupuesto
- `Ctrl+T`: Nuevo Parte de Trabajo
- `Ctrl+Q`: Salir de la aplicación

## Validaciones Implementadas

- Validación de NIF/CIF español
- Validación de formato de email
- Validación de formato de teléfono
- Campos obligatorios marcados con asterisco (*)
- Diálogos de confirmación para eliminaciones

## Rendimiento y Compatibilidad

- ✅ Uso mínimo de CPU y memoria (compatible con PCs de bajos recursos)
- ✅ 100% funcional en Windows 10
- ✅ Base de datos embebida (un solo archivo)
- ✅ No requiere conexión a internet
- ✅ Interfaz nativa gracias a PyQt6
- ✅ Máximo 2 clics para acciones críticas

## Próximas Funcionalidades (Fase 3)

La Fase 3 incluirá:

1. **Editor WYSIWYG**:
   - Integración de QWebEngineView
   - Editor de texto enriquecido JavaScript (Quill)
   - Edición en vivo del documento

2. **Generación de PDF**:
   - Plantillas HTML/CSS profesionales
   - Exportación directa a PDF
   - Dos versiones: una para presupuestos (solo precios finales) y otra para partes de trabajo

3. **Plantillas Personalizables**:
   - Diseño elegante y profesional
   - Campos dinámicos con datos del documento
   - Logo y personalización de empresa

## Compilación a Ejecutable

Para crear un ejecutable portable de Windows:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="GestionConstructora" main.py
```

El ejecutable se generará en la carpeta `dist/`.

## Soporte

Para reportar problemas o sugerencias, por favor crea un issue en el repositorio.

## Licencia

© 2025 - Todos los derechos reservados

---

**Desarrollado con ❤️ usando Python, PyQt6 y SQLite**
