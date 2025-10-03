# 🚀 INICIO RÁPIDO

## Para usuarios NO técnicos

### 🐧 Linux / Mac

1. Abre una terminal en esta carpeta
2. Ejecuta:
   ```bash
   ./run.sh
   ```
3. ¡Listo! La aplicación se abrirá automáticamente

### 🪟 Windows

1. Haz doble-click en `run.bat`
2. ¡Listo! La aplicación se abrirá automáticamente

---

## 📖 ¿Primera vez usando la aplicación?

Lee la **[Guía de Usuario](GUIA_USUARIO.md)** para un tutorial completo.

### Inicio rápido:

1. **Gestiona materiales**: 
   - **Crear**: Click "📦 Nuevo Material"
   - **Editar**: Doble-click en un material o selecciona + "✏️ Editar"
   - **Eliminar**: Selecciona + "🗑️ Borrar"
   - Pon nombre, precio y categoría (foto opcional)

2. **Gestiona clientes**: 
   - **Crear**: Click "👤 Nuevo Cliente"
   - **Editar**: Doble-click en un cliente o selecciona + "✏️ Editar"
   - **Eliminar**: Selecciona + "🗑️ Borrar"
   - Mínimo: nombre (resto opcional pero recomendado)

3. **Crea/edita presupuestos**: 
   - **Crear**: Click "➕ Nuevo Presupuesto"
   - **Editar**: Selecciona presupuesto + "✏️ Editar"
   - **Eliminar**: Selecciona presupuesto + "🗑️ Eliminar"
   - Selecciona cliente
   - **Busca materiales escribiendo** (ej: "arena")
   - Doble-click en material para añadir
   - Indica cantidad
   - Repite para más materiales
   - Pon mano de obra (en euros)
   - Guarda

4. **Exporta a PDF**: 
   - Ve a pestaña "📋 Presupuestos"
   - **Opción A**: Doble-click en presupuesto → PDF directo
   - **Opción B**: Selecciona + Click "📄 Exportar PDF"

---

## 🔍 Búsqueda Inteligente

La **mejor característica** de esta aplicación:

- Al crear un presupuesto, verás un **buscador de materiales**
- Escribe "arena" → aparecen todos los tipos de arena
- Escribe "cemento" → aparecen todos los cementos
- Escribe "blanco" → aparecen cemento blanco, pintura blanca, yeso blanco...

**Soporta miles de materiales** sin ralentizarse. ¡Pruébalo!

---

## ⌨️ Atajos útiles

- `Ctrl+N` → Nuevo presupuesto
- `Ctrl+M` → Nuevo material
- `Ctrl+U` → Nuevo cliente
- `F5` → Actualizar listas
- `Enter` → Guardar formularios
- `Esc` → Cancelar/cerrar
- `Doble-click` → Editar elemento

---

## ❓ ¿Problemas?

### No se abre la aplicación

**Linux**: 
```bash
sudo apt install python3-tk
./run.sh
```

**Windows**:
- Instala Python desde python.org
- Ejecuta `run.bat` de nuevo

### Error "No module named..."

Ejecuta en terminal:
```bash
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
python main.py
```

---

## 📚 Más Información

- **[README.md](README.md)** - Documentación técnica completa
- **[GUIA_USUARIO.md](GUIA_USUARIO.md)** - Tutorial paso a paso
- **[EJEMPLOS_BUSQUEDA.md](EJEMPLOS_BUSQUEDA.md)** - Cómo usar la búsqueda
- **[RESUMEN_MEJORAS.md](RESUMEN_MEJORAS.md)** - Características implementadas

---

**Empresa**: Barajar Peña  
**Aplicación**: Gestor de Presupuestos v2.0  
**Fecha**: Octubre 2025
