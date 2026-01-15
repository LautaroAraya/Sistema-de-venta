@echo off
echo ======================================
echo    GENERANDO EJECUTABLE
echo ======================================
echo.
echo Instalando dependencias...
pip install -r requirements.txt
echo.
echo Generando ejecutable con PyInstaller...
pyinstaller --clean --onefile --windowed --name "SistemaVentas" main.py
echo.
echo ======================================
echo    PROCESO COMPLETADO
echo ======================================
echo.
echo El ejecutable se encuentra en la carpeta "dist"
echo.
pause
