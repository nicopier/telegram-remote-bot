@echo off
SET BOT_PATH=%~dp0bot.py
SET PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe

:: Buscar pythonw automaticamente
where pythonw >nul 2>&1
if %ERRORLEVEL% == 0 (
    FOR /F "tokens=*" %%i IN ('where pythonw') DO SET PYTHON_PATH=%%i
)

echo Instalando tarea de inicio automatico...
echo Python: %PYTHON_PATH%
echo Bot: %BOT_PATH%

schtasks /create /tn "TelegramBot" /tr "\"%PYTHON_PATH%\" \"%BOT_PATH%\"" /sc onlogon /rl highest /ru "%USERNAME%" /f

if %ERRORLEVEL% == 0 (
    echo.
    echo OK - El bot va a arrancar automaticamente al iniciar Windows.
    echo Para desinstalarlo ejecuta: desinstalar_autostart.bat
) else (
    echo.
    echo ERROR - No se pudo crear la tarea. Intenta ejecutar como Administrador.
)
pause
