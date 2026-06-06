@echo off
REM Script para instalar dependencias en Windows

echo.
echo ===================================
echo Instalador del Bot de Telegram
echo ===================================
echo.

echo Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Descarga Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Hubo un problema al instalar las dependencias
    pause
    exit /b 1
)

echo.
echo ===================================
echo Instalacion completada exitosamente!
echo ===================================
echo.
echo Ahora debes:
echo 1. Editar bot.py
echo 2. Reemplazar "TU_TOKEN_AQUI" con tu token de Telegram
echo 3. Guardar el archivo
echo 4. Ejecutar: python bot.py
echo.
pause
