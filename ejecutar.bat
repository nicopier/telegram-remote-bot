@echo off
REM Script para ejecutar el bot de Telegram

echo.
echo ===================================
echo Iniciando Bot de Telegram...
echo ===================================
echo.

python bot.py

if errorlevel 1 (
    echo.
    echo ERROR: Hubo un problema al ejecutar el bot
    echo Verifica que:
    echo 1. Python está instalado
    echo 2. Las dependencias están instaladas (ejecuta instalar.bat)
    echo 3. El token está configurado en bot.py
    echo.
    pause
)
