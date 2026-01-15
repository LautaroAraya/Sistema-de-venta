@echo off
echo ======================================
echo    INSTALACION Y PRUEBA DEL SISTEMA
echo ======================================
echo.
echo Instalando dependencias...
pip install -r requirements.txt
echo.
echo Inicializando base de datos con datos de ejemplo...
python inicializar_datos.py
echo.
echo Iniciando aplicacion...
python main.py
