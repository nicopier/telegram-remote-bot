@echo off
schtasks /delete /tn "TelegramBot" /f
if %ERRORLEVEL% == 0 (
    echo OK - Tarea eliminada. El bot ya no arranca con Windows.
) else (
    echo ERROR - No se encontro la tarea o no se pudo eliminar.
)
pause
