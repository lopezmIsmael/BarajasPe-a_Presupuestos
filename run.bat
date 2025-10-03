@echo off
REM Script de inicio rápido para Windows

echo.
echo Iniciando Gestor de Presupuestos - Barajar Peña
echo.

REM Verificar si existe el entorno virtual
if not exist ".venv\" (
    echo Creando entorno virtual...
    python -m venv .venv
)

REM Activar entorno virtual
echo Activando entorno virtual...
call .venv\Scripts\activate.bat

REM Instalar dependencias si es necesario
echo Verificando dependencias...
pip install -q -r requirements.txt

echo.
echo Todo listo!
echo.
echo Ejecutando aplicación...
echo.

REM Ejecutar aplicación
python main.py

pause
