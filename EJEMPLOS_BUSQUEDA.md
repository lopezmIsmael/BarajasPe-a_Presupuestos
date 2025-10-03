# 🔍 Ejemplos de Búsqueda Inteligente

La aplicación incluye un **sistema de búsqueda avanzado** que te permite encontrar materiales al instante, incluso con catálogos de miles de artículos.

## 🎯 Cómo Funciona

### Búsqueda por Nombre (Prioridad Alta)
```
Buscas: "arena"
Resultados:
  ✓ Arena fina lavada [Arenas] - 2.30€
  ✓ Arena gruesa [Arenas] - 2.50€
  ✓ Arena sílice [Arenas] - 3.80€
  ✓ Arena volcánica [Arenas] - 4.20€
```

### Búsqueda por Características
```
Buscas: "blanco"
Resultados:
  ✓ Cemento blanco [Cementos] - 12.90€
  ✓ Pintura plástica blanca [Pinturas] - 32.50€
  ✓ Yeso blanco YF [Yesos] - 4.20€
```

### Búsqueda por Categoría
```
Buscas: "tubería"
Resultados:
  ✓ Tubería PVC 40mm [Tuberías] - 2.80€
  ✓ Tubería PVC 110mm [Tuberías] - 8.50€
  ✓ Tubería cobre 15mm [Tuberías] - 85.00€
  ✓ Tubería multicapa [Tuberías] - 95.00€
```

### Búsqueda Parcial
```
Buscas: "ladri"
Resultados:
  ✓ Ladrillo hueco doble [Ladrillos]
  ✓ Ladrillo macizo [Ladrillos]
  ✓ Ladrillo caravista [Ladrillos]
  ✓ Ladrillo refractario [Ladrillos]
```

## 📊 Sistema de Puntuación

El buscador ordena resultados por relevancia:

| Tipo de coincidencia | Puntos | Ejemplo |
|---------------------|--------|---------|
| **Coincidencia exacta** | 100 | "arena" encuentra "Arena" |
| **Empieza con...** | 90 | "cem" encuentra "Cemento" |
| **Contiene en nombre** | 80 | "rápido" encuentra "Cemento rápido" |
| **En descripción** | 50 | "decorativa" encuentra arena con desc "Arena... decorativa" |
| **En categoría** | 40 | "maderas" encuentra todos en categoría Maderas |

## 💡 Tips de Búsqueda

### ✅ Buenas prácticas
- **Escribe pocas letras**: "cem" es suficiente para encontrar todos los cementos
- **Usa características clave**: "fino", "grueso", "blanco", "doble"
- **Busca por medidas**: "40mm", "15cm", "25kg"
- **Sin tildes necesarias**: busca "cemento" o "cémento" indistintamente

### ⚡ Velocidad
- Búsquedas **instantáneas** (filtrado mientras escribes)
- Optimizado para **catálogos grandes** (1000+ materiales)
- Limita resultados a **top 20** más relevantes

### 📂 Sin búsqueda = Vista por categorías
Si dejas el campo vacío, verás **todos los materiales agrupados por categoría**:
```
━━ Arenas ━━
  Arena fina lavada - 2.30€
  Arena gruesa - 2.50€
━━ Cementos ━━
  Cemento Portland CEM I - 8.50€
  Cemento blanco - 12.90€
━━ Ladrillos ━━
  Ladrillo hueco doble - 0.45€
  ...
```

## 🎮 Interacción Rápida

### Añadir material al presupuesto
1. Escribe en el buscador (ej: "arena")
2. **Doble-click** en resultado deseado
3. Indica cantidad → Listo

O bien:
1. Escribe búsqueda
2. Click en resultado
3. Click **➕ Añadir**
4. Indica cantidad

### Atajos
- `Enter` después de buscar → Añade primer resultado
- `Doble-click` → Añade directamente
- `Esc` → Limpia búsqueda

## 🏆 Casos de Uso Reales

### Escenario 1: Obra de albañilería
```
Usuario busca:     Resultado inmediato:
"cemento"       → 4 tipos de cemento
"arena"         → 4 tipos de arena  
"ladrillo"      → 4 tipos de ladrillo
```
**Tiempo total**: <30 segundos para añadir 12 materiales

### Escenario 2: Instalación de fontanería
```
Usuario busca:     Resultado:
"tubería"       → Todas las tuberías (PVC, cobre, multicapa)
"40mm"          → Solo tuberías de 40mm
"pvc"           → Solo tuberías PVC
```

### Escenario 3: Catálogo grande (1000+ materiales)
```
Sin búsqueda inteligente:
  ❌ Scroll infinito en desplegable
  ❌ Difícil encontrar artículo específico
  ❌ Lento y frustrante

Con búsqueda inteligente:
  ✅ Escribe "arena fina" → resultado en <0.1s
  ✅ Top 20 resultados relevantes
  ✅ Ordenados por importancia
```

## 🔧 Personalización

### Añadir categorías propias
Al crear un material, el campo "Categoría" es editable:
- Selecciona una existente del desplegable
- O escribe una nueva (se crea automáticamente)

### Sugerencias de categorías
- **Construcción**: Arenas, Cementos, Ladrillos, Bloques
- **Acabados**: Yesos, Pinturas, Barnices, Revestimientos
- **Estructura**: Hierros, Vigas, Perfiles
- **Instalaciones**: Tuberías, Cables, Conductos
- **Carpintería**: Maderas, Tableros, Herrajes
- **Herramientas**: Consumibles, Equipos

---

**Resultado**: Encuentra cualquier material en tu catálogo en **menos de 3 segundos** 🚀
