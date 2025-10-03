# 📦 Cómo Crear y Distribuir el Ejecutable

## ✅ Ejecutable Creado Exitosamente

El ejecutable se encuentra en: `dist/BarajasPena_Presupuestos`

## 🚀 Para Linux

El ejecutable ya está listo para usar en Linux:

```bash
cd dist
./BarajasPena_Presupuestos
```

## 🪟 Para Windows

### Opción 1: Compilar en Windows (Recomendado)

1. **Instalar Python 3.11** en Windows
2. **Clonar el repositorio** o copiar los archivos
3. **Crear entorno virtual**:
   ```cmd
   python -m venv myenv
   myenv\Scripts\activate
   ```

4. **Instalar dependencias**:
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```

5. **Crear el ejecutable**:
   ```cmd
   pyinstaller build_exe.spec --clean
   ```

6. El ejecutable estará en: `dist\BarajasPena_Presupuestos.exe`

### Opción 2: Wine en Linux (Compilación Cruzada)

**NOTA**: PyInstaller no crea verdaderos ejecutables multiplataforma desde Linux a Windows. Necesitas compilar en Windows nativamente.

Puedes usar Wine + Python para Windows:

```bash
# Instalar Wine
sudo apt install wine wine64

# Descargar Python para Windows
wget https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

# Instalar Python en Wine
wine python-3.11.9-amd64.exe

# Instalar dependencias
wine pip install -r requirements.txt
wine pip install pyinstaller

# Crear ejecutable
wine pyinstaller build_exe.spec --clean
```

## 📋 Contenido del Ejecutable

El ejecutable incluye:
- ✅ Aplicación completa
- ✅ Todas las dependencias Python
- ✅ SQLite integrado
- ✅ Reportlab para PDFs
- ✅ PIL/Pillow para imágenes
- ✅ Assets y recursos
- ✅ Tkinter para la interfaz

## 📦 Distribución

### Archivo Único

El ejecutable es un archivo único que contiene todo. Para distribuir:

1. **Comprime el directorio `dist/`**:
   ```bash
   cd dist
   zip -r BarajasPena_Presupuestos.zip BarajasPena_Presupuestos
   ```

2. **Comparte el .zip** con los usuarios

3. Los usuarios solo necesitan:
   - Descomprimir
   - Ejecutar el archivo

### Primera Ejecución

En la primera ejecución, la aplicación:
- ✅ Crea automáticamente la base de datos `data.db`
- ✅ Inicializa las tablas necesarias
- ✅ Se abre en pantalla completa

## 🔧 Recomendaciones

### Para Producción en Windows

1. **Añadir icono**:
   - Crea un archivo `icon.ico`
   - Modifica `build_exe.spec`: `icon='assets/icon.ico'`

2. **Firma digital** (opcional):
   - Para evitar advertencias de Windows Defender
   - Requiere certificado de firma de código

3. **Instalador** (opcional):
   - Usar Inno Setup o NSIS
   - Crea instalador profesional con desinstalador

## 📊 Tamaño del Ejecutable

- **Linux**: ~50-60 MB
- **Windows**: ~40-50 MB

El tamaño incluye:
- Python runtime
- Todas las librerías
- Tcl/Tk para la interfaz
- Bibliotecas de imagen y PDF

## 🐛 Solución de Problemas

### "El archivo no es ejecutable"
```bash
chmod +x BarajasPena_Presupuestos
```

### "Falta librería .so en Linux"
Asegúrate de tener instalado:
```bash
sudo apt install python3-tk libtk8.6
```

### "Windows bloquea la ejecución"
- Click derecho → Propiedades → Desbloquear
- O firma el ejecutable con certificado

## 🔄 Reconstruir el Ejecutable

Si haces cambios en el código:

```bash
# Activar entorno
source myenv/bin/activate

# Limpiar builds anteriores
rm -rf build dist

# Reconstruir
pyinstaller build_exe.spec --clean
```

## 📝 Script Automatizado

Usa el script `build_windows.sh`:

```bash
./build_windows.sh
```

Este script:
- Activa el entorno virtual
- Limpia builds anteriores  
- Crea el ejecutable
- Muestra el resultado
