# 📘 Guía de Usuario - Barajar Peña

## 🚀 Inicio Rápido

### Primera ejecución

1. Abre una terminal en la carpeta del proyecto
2. Activa el entorno virtual:
   - **Linux/Mac**: `source .venv/bin/activate`
   - **Windows**: `.\.venv\Scripts\Activate.ps1`
3. Ejecuta: `python main.py`

### Interfaz principal

Al abrir la aplicación verás:
- **Barra superior**: Botones de acción rápida (siempre visibles)
- **Pestañas**: Presupuestos, Materiales, Clientes
- **Barra de estado**: Información sobre el estado actual

## 📋 Crear tu Primer Presupuesto (en 3 clicks)

### Paso 1: Preparar datos básicos

**Añadir un cliente** (desde barra superior):
1. Click en **👤 Nuevo Cliente**
2. Rellena: Nombre (obligatorio), Dirección, DNI, Teléfono, Email
3. Presiona `Enter` o click en **💾 Guardar**

**Añadir materiales** (desde barra superior):
1. Click en **📦 Nuevo Material**
2. Rellena: 
   - Nombre (obligatorio)
   - Descripción
   - Precio (obligatorio)
   - **Categoría**: Selecciona existente o **escribe una nueva**
     - 💡 Las categorías nuevas se guardan automáticamente
     - Ejemplo: escribe "Herramientas" y quedará disponible
3. Opcional: Click 📁 para añadir foto del material
4. Presiona `Enter` o **💾 Guardar**

> 💡 **Tip**: Puedes crear clientes y materiales mientras creas el presupuesto

### Paso 2: Crear presupuesto

1. Click en **➕ Nuevo Presupuesto** (barra superior)
2. En el panel izquierdo:
   - Selecciona **Cliente** del desplegable
   - Indica **Mano de obra** en euros
3. Para añadir materiales:
   - **Opción A**: Selecciona material del desplegable → Click **➕ Añadir a presupuesto** → Indica cantidad
   - **Opción B**: Click **📦 Nuevo material** para crear uno nuevo
4. Los items aparecen en el panel derecho con totales calculados
5. Click **💾 Guardar Presupuesto**

### Paso 3: Exportar a PDF

1. En la pestaña **📋 Presupuestos**, selecciona uno de la lista
2. Click **📄 Exportar PDF**
3. Elige ubicación y nombre del archivo
4. ¡Listo! El PDF incluye branding "Barajar Peña", items con fotos (si las hay) y totales

> 🎯 **Atajo rápido**: Doble-click en un presupuesto exporta directamente a PDF

## 🔍 Búsqueda Rápida

En cada pestaña hay una barra de búsqueda:
- Escribe cualquier término
- Los resultados se filtran **en tiempo real**
- Funciona en: nombres, descripciones, DNI, direcciones

## ⌨️ Atajos de Teclado

### Globales (desde cualquier parte)
- `Ctrl+N` → Nuevo presupuesto
- `Ctrl+M` → Nuevo material
- `Ctrl+U` → Nuevo cliente (User)
- `F5` → Actualizar todas las listas

### En formularios
- `Enter` → Guardar
- `Esc` → Cancelar/Cerrar

### En listas
- `Doble-click` → Editar elemento seleccionado

## ✏️ Editar y Eliminar

### Materiales y Clientes

**Editar**:
1. Ve a la pestaña correspondiente (📦 Materiales o 👥 Clientes)
2. **Opción A**: Selecciona elemento → Click **✏️ Editar**
3. **Opción B**: Haz **doble-click** directamente en el elemento
4. Modifica los datos necesarios
5. Presiona `Enter` o click **💾 Guardar**

**Eliminar**:
1. Ve a la pestaña correspondiente
2. Selecciona elemento
3. Click **🗑️ Borrar**
4. Confirma la eliminación en el diálogo

> ⚠️ **Advertencia**: Eliminar es permanente y no se puede deshacer

### Presupuestos

**Editar**:
1. Ve a la pestaña **📋 Presupuestos**
2. Selecciona un presupuesto de la lista
3. Click **✏️ Editar**
4. Se abre el editor con:
   - **Panel izquierdo**: Cliente, mano de obra, búsqueda de materiales
   - **Panel derecho**: Lista de items y resumen de totales
5. Modifica:
   - Cliente (combo desplegable)
   - Mano de obra (se actualiza el total automáticamente)
   - Items: 
     - Buscar y añadir materiales (doble-click o botón ➕)
     - Editar cantidades (doble-click en item)
     - Quitar items (seleccionar + botón 🗑️)
6. **Ver totales en tiempo real**:
   - El panel "Resumen" muestra:
     - Subtotal (suma de items)
     - Mano de obra
     - **TOTAL** (en grande)
7. **Guardar**:
   - **Opción A**: Click en botón verde grande **💾 GUARDAR PRESUPUESTO**
   - **Opción B**: Presiona `Ctrl+S`
8. Confirmar mensaje de éxito

> 💡 **Tip**: El total se actualiza automáticamente mientras añades items o cambias la mano de obra

**Eliminar**:
1. Selecciona un presupuesto
2. Click **🗑️ Eliminar**
3. Confirma (se eliminarán todos los items asociados)

> ⚠️ **Advertencia**: Eliminar es permanente y no se puede deshacer

> 🎯 **Atajos de teclado en el editor**:
> - `Ctrl+S` → Guardar presupuesto
> - `Esc` → Cancelar y cerrar sin guardar
> - Doble-click en material → Añadir al presupuesto
> - Doble-click en item → Editar cantidad

### Validaciones

- No puedes dejar campos obligatorios vacíos (marcados con *)
- Los precios deben ser ≥ 0
- Las cantidades deben ser > 0
- Al eliminar un presupuesto, se eliminan automáticamente todos sus items

## 👁️ Ver Detalles de Presupuesto

1. En pestaña **📋 Presupuestos**, selecciona uno
2. Click **👁️ Ver Detalles**
3. Verás: datos del cliente, lista de items, subtotales y total general

## 💡 Consejos y Trucos

### Velocidad
- Usa atajos de teclado (`Ctrl+N`, `Ctrl+M`, etc.)
- Doble-click para editar en lugar de seleccionar + botón
- La búsqueda filtra mientras escribes (no necesitas Enter)

### Organización
- Crea tus materiales más usados primero
- Añade descripciones detalladas para reconocerlos rápidamente
- Las fotos de materiales aparecen en los PDFs

### Fotos de materiales
- Formatos soportados: PNG, JPG, JPEG, BMP
- Las fotos se redimensionan automáticamente en el PDF
- Puedes dejar materiales sin foto

### Presupuestos
- Los presupuestos se guardan automáticamente con fecha actual
- Puedes crear múltiples presupuestos para el mismo cliente
- Los totales se calculan automáticamente
- La mano de obra es opcional (pon 0 si no aplica)

## 🔧 Solución de Problemas

### La aplicación no arranca
- Verifica que el entorno virtual esté activado
- Reinstala dependencias: `pip install -r requirements.txt`

### No aparece el tema moderno
- Verifica que ttkbootstrap esté instalado: `pip install ttkbootstrap`
- La app funcionará igual con tema básico si falta

### Error al exportar PDF
- Verifica que reportlab esté instalado
- Asegúrate de tener permisos de escritura en la carpeta destino
- Si hay fotos, verifica que las rutas existan

### Error con fotos de materiales
- Las fotos no se copian, solo se guarda la ruta
- Si mueves las fotos, actualiza la ruta en el material
- Los PDFs funcionan aunque falten fotos

## 📊 Rendimiento

La aplicación está optimizada para:
- ✅ Cientos de materiales sin ralentizarse
- ✅ Cientos de clientes con búsqueda instant
- ✅ Exportación rápida de PDFs (<1 segundo)
- ✅ Uso mínimo de memoria (~20-50 MB)
- ✅ Inicio rápido (<2 segundos)

## 🗄️ Base de Datos

- Archivo: `data.db` (SQLite)
- **Backup**: Simplemente copia `data.db` a otra carpeta
- **Restaurar**: Reemplaza `data.db` con tu backup
- **Borrar todo**: Elimina `data.db` y se creará vacía al iniciar

## 🎨 Personalización

### Cambiar nombre de empresa
Edita `main.py` y `pdf_generator.py`:
```python
COMPANY_NAME = "Tu Empresa"
```

### Cambiar colores
En `main.py` y `pdf_generator.py`:
```python
BRAND_COLOR = "#2196F3"  # Azul actual
```

### Cambiar tema visual
En `main.py`, línea del tema:
```python
root = ttkb.Window(themename="flatly")  
# Otros temas: cosmo, litera, minty, pulse, sandstone, etc.
```

## 📞 Soporte

**Empresa**: Barajar Peña  
**Aplicación**: Gestor de Presupuestos v2.0  
**Última actualización**: Octubre 2025

---

¡Disfruta de una gestión de presupuestos rápida y profesional! 🚀
