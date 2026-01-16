@echo off
chcp 65001 > nul
color 0A
echo.
echo ================================================================================
echo                    🚀 SISTEMA DE VENTAS - DEPLOY AUTOMÁTICO
echo ================================================================================
echo.
echo Este script compilará el ejecutable, regenerará el instalador y preparará
echo la distribución de la nueva versión.
echo.
echo Asegúrate de haber actualizado version.txt con la nueva versión.
echo.
pause

python deploy_actualizacion.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ ¡Proceso completado exitosamente!
    echo.
    pause
) else (
    echo.
    echo ❌ Error durante el proceso
    echo.
    pause
)
