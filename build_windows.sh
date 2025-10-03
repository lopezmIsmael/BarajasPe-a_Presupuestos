#!/bin/bash
# Script para crear ejecutable de Windows con PyInstaller

echo "================================================"
echo "  Barajas Peña - Constructor de Ejecutable"
echo "================================================"
echo ""

# Activar entorno virtual
echo "✓ Activando entorno virtual..."
source myenv/bin/activate

# Limpiar builds anteriores
echo "✓ Limpiando builds anteriores..."
rm -rf build dist

# Crear ejecutable
echo "✓ Generando ejecutable con PyInstaller..."
pyinstaller build_exe.spec --clean

# Verificar resultado
if [ -f "dist/BarajasPena_Presupuestos" ]; then
    echo ""
    echo "================================================"
    echo "  ✓ Ejecutable creado exitosamente!"
    echo "================================================"
    echo ""
    echo "Ubicación: dist/BarajasPena_Presupuestos"
    echo ""
    echo "El ejecutable incluye:"
    echo "  - Aplicación principal"
    echo "  - Todas las dependencias"
    echo "  - Assets y recursos"
    echo "  - Base de datos SQLite"
    echo ""
    echo "Para Windows, copia el archivo a Windows y ejecútalo."
else
    echo ""
    echo "✗ Error al crear el ejecutable"
    echo "Revisa los mensajes anteriores para más detalles"
fi
