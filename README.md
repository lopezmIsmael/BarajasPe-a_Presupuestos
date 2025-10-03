# Barajar Peña - Gestión de Presupuestos

**Aplica## ✨ Características

- 🏢 **Branding personalizado**: Empresa "Barajar Peña"
- 📦 **Gestión completa de materiales**: Crear, editar, eliminar materiales con nombre, descripción, categoría, foto y precio
- 🔍 **Búsqueda inteligente**: Encuentra materiales al instante escribiendo (busca en nombre, descripción y categoría)
- 📂 **Categorías**: Organiza tus materiales por tipo (Arenas, Cementos, Ladrillos, etc.)
- 👥 **Gestión completa de clientes**: Crear, editar, eliminar clientes con todos sus datos
- 📋 **Presupuestos editables**: Crea, edita y elimina presupuestos con búsqueda en tiempo real de materiales
- 📄 **Exportación a PDF**: con imágenes, detalles y totales profesionales con branding
- 🔎 **Búsqueda multi-campo**: filtra materiales, clientes y presupuestos al escribir
- ⚡ **Interfaz moderna**: diseño limpio con ttkbootstrap (estilo Bootstrap)
- ⌨️ **Atajos de teclado**: workflow rápido y eficiente (Ctrl+N, Ctrl+M, Enter, Esc, doble-click)
- 🚀 **Alto rendimiento**: base de datos optimizada con índices (soporta miles de materiales sin ralentizar)de escritori## 📋 Crear un Presupuesto (workflow optimizado)

### Búsqueda inteligente de materiales

Cuando creas un presupuesto, verás un **buscador en tiempo real**:

1. **Sin búsqueda** (campo vacío): Muestra todos los materiales agrupados por categoría
2. **Con búsqueda** (escribe "arena"): Filtra y muestra solo coincidencias
   - Prioriza coincidencias exactas en el nombre
   - Busca también en descripción y categoría
   - Ordena resultados por relevancia
   - Limita a top 20 para mantener velocidad

**Ventajas**:
- ✅ Soporta **miles de materiales** sin ralentizarse
- ✅ **Doble-click** para añadir directamente
- ✅ Busca en **nombre, descripción y categoría**
- ✅ Resultados **ordenados por relevancia**
- ✅ Búsqueda **fuzzy** (encuentra "cemento" aunque escribas "cemt")

### Paso a paso completo

1. Click **➕ Nuevo Presupuesto**
2. Selecciona cliente del desplegable
3. En el buscador de materiales:
   - Escribe "arena" → aparecen todos los tipos de arena
   - Doble-click en "Arena fina lavada"
   - Indica cantidad (ej: 100)
4. Repite para más materiales
5. Indica mano de obra en euros
6. Click **💾 Guardar Presupuesto**

## 📂 Categorías de Materiales

Organiza tus materiales en categorías para facilitar la búsqueda:
- Arenas
- Cementos
- Ladrillos
- Bloques
- Yesos
- Pinturas
- Maderas
- Hierros
- Tuberías
- *(o crea las tuyas propias)*

Al añadir un material, elige una categoría existente o escribe una nueva.

## 🔧 Operaciones Disponibles

### CRUD Completo para todas las entidades

#### 📦 Materiales
- **✅ Crear**: Click "📦 Nuevo Material" → Rellenar formulario → Guardar
- **✏️ Editar**: Doble-click en material o seleccionar + "✏️ Editar"
- **🗑️ Eliminar**: Seleccionar material + "🗑️ Borrar" → Confirmar
- **🔍 Buscar**: Búsqueda en tiempo real por nombre, descripción o categoría

#### 👥 Clientes
- **✅ Crear**: Click "👤 Nuevo Cliente" → Rellenar datos → Guardar
- **✏️ Editar**: Doble-click en cliente o seleccionar + "✏️ Editar"
- **🗑️ Eliminar**: Seleccionar cliente + "🗑️ Borrar" → Confirmar
- **🔍 Buscar**: Búsqueda por nombre o DNI

#### 📋 Presupuestos
- **✅ Crear**: Click "➕ Nuevo Presupuesto" → Buscar materiales → Añadir items → Guardar
- **✏️ Editar**: Seleccionar presupuesto + "✏️ Editar" → Modificar items/datos → Guardar
- **🗑️ Eliminar**: Seleccionar presupuesto + "🗑️ Eliminar" → Confirmar (elimina todos los items)
- **👁️ Ver**: Previsualiza el presupuesto completo antes de exportar
- **📄 Exportar**: Genera PDF profesional con branding "Barajar Peña"

> 💡 **Atajos rápidos**: 
> - Doble-click para editar materiales/clientes
> - Doble-click en presupuesto para exportar a PDF
> - Enter para guardar formularios
> - Esc para cancelar

## 🚀 Flujo de Trabajo Típicondows y Linux) para crear presupuestos para empresas de construcción.

## ✨ Características

- 🏢 **Branding personalizado**: Empresa "Barajar Peña"
- 📦 **Gestión de materiales**: nombre, descripción, categoría, foto opcional, precio
- 🔍 **Búsqueda inteligente**: Encuentra materiales al instante escribiendo (busca en nombre, descripción y categoría)
- � **Categorías**: Organiza tus materiales por tipo (Arenas, Cementos, Ladrillos, etc.)
- �👥 **Gestión de clientes**: nombre, dirección, DNI, teléfono, email
- 📋 **Presupuestos rápidos**: búsqueda en tiempo real de materiales, cantidades y coste de mano de obra
- 📄 **Exportación a PDF**: con imágenes, detalles y totales profesionales
- � **Búsqueda multi-campo**: filtra materiales, clientes y presupuestos al escribir
- ⚡ **Interfaz moderna**: diseño limpio con ttkbootstrap (estilo Bootstrap)
- ⌨️ **Atajos de teclado**: workflow rápido y eficiente
- 🚀 **Alto rendimiento**: base de datos optimizada con índices (soporta miles de materiales)

## 🎨 Diseño Moderno

- Interfaz con tema Bootstrap (flatly)
- Iconos emoji para mejor UX
- Acciones rápidas en pantalla principal (<3 clicks para todo)
- Doble-click para editar
- Búsqueda inline instantánea
- Ventanas modales optimizadas

## ⌨️ Atajos de Teclado

- `Ctrl+N` - Nuevo presupuesto
- `Ctrl+M` - Nuevo material
- `Ctrl+U` - Nuevo cliente
- `F5` - Actualizar todo
- `Enter` - Guardar en formularios
- `Esc` - Cancelar/cerrar
- `Doble-click` - Editar elemento seleccionado

## 📋 Requisitos

- Python 3.8+
- Dependencias:
  - reportlab (PDF)
  - Pillow (imágenes)
  - ttkbootstrap (UI moderna)

## 🚀 Instalación y Uso

### Linux

```bash
# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

### Windows

```powershell
# Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

## 📖 Guía de Uso Rápida

### Crear un presupuesto (3 clicks)

1. **Click** en "➕ Nuevo Presupuesto" (barra superior)
2. Seleccionar cliente y materiales
3. **Click** en "💾 Guardar Presupuesto"

### Añadir material (2 clicks)

1. **Click** en "📦 Nuevo Material" (barra superior)
2. Rellenar datos y **Click** "💾 Guardar" (o `Enter`)

### Exportar PDF (2 clicks)

1. Seleccionar presupuesto en la lista
2. **Click** en "📄 Exportar PDF" (o doble-click en presupuesto)

## 🎯 Flujo Optimizado

- **Sin navegación profunda**: acciones principales en pantalla principal
- **Creación inline**: crea clientes/materiales mientras haces presupuestos
- **Búsqueda instantánea**: escribe para filtrar en cualquier pestaña
- **Feedback visual**: mensajes claros de éxito/error
- **Validaciones inteligentes**: previene errores comunes

## 🗄️ Base de Datos

- SQLite embebido (`data.db`)
- Sin servidor externo
- Índices optimizados para búsquedas rápidas
- Portable (copia el archivo .db para backup)

## 📄 Estructura del Proyecto

```
presupuestos/
├── main.py              # Aplicación principal (UI moderna)
├── db.py                # Capa de datos (SQLite + índices)
├── pdf_generator.py     # Exportador PDF con branding
├── requirements.txt     # Dependencias
├── README.md           # Este archivo
└── data.db             # Base de datos (creada al ejecutar)
```

## 🔧 Optimizaciones de Rendimiento

- Índices en tablas de búsqueda frecuente
- Lazy loading de imágenes
- Queries optimizadas con row_factory
- UI responsiva con validaciones asíncronas
- Mínimo uso de memoria (SQLite embebido)

## 💡 Características Avanzadas

- **Vista previa de presupuestos**: Ver detalles antes de exportar
- **Edición rápida de cantidades**: Doble-click en items
- **Búsqueda multi-campo**: nombre, DNI, descripción
- **Totales automáticos**: Calculo en tiempo real
- **Historial completo**: Todos los presupuestos guardados

## 📞 Soporte

Empresa: **Barajar Peña**
Aplicación: Gestor de Presupuestos v2.0
