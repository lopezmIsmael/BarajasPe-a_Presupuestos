#!/bin/bash
# Script de inicio rápido para Linux

echo "🚀 Iniciando Gestor de Presupuestos - Barajar Peña"
echo ""

# Verificar si existe el entorno virtual
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv .venv
fi

# Activar entorno virtual
echo "⚡ Activando entorno virtual..."
source .venv/bin/activate

# Instalar dependencias si es necesario
echo "📋 Verificando dependencias..."
pip install -q -r requirements.txt

echo ""
echo "✅ Todo listo!"
echo ""
echo "🎯 Ejecutando aplicación..."
echo ""

# Ejecutar aplicación
python main.py
