#!/usr/bin/env python
"""
Script reiniciador que se ejecuta después de una actualización.
Asegura que se ejecuta desde la carpeta correcta.
"""
import os
import sys
import subprocess
import time

# Obtener la carpeta donde está este script (debe ser Sistema de venta)
restart_script_dir = os.path.dirname(os.path.abspath(__file__))

print(f"[RESTART] Esperando a que se cierre la aplicación...")
time.sleep(2)

print(f"[RESTART] Reiniciando desde: {restart_script_dir}")

# Cambiar a la carpeta correcta
os.chdir(restart_script_dir)

if getattr(sys, 'frozen', False):
    # Si somos un ejecutable PyInstaller
    print(f"[RESTART] Ejecutando como EXE")
    subprocess.Popen([sys.executable])
else:
    # Si somos un script Python
    print(f"[RESTART] Ejecutando main.py con Python")
    python = sys.executable
    main_script = os.path.join(restart_script_dir, "main.py")
    
    print(f"[RESTART] Python: {python}")
    print(f"[RESTART] Script: {main_script}")
    print(f"[RESTART] Working dir: {os.getcwd()}")
    
    subprocess.Popen([python, main_script], cwd=restart_script_dir)

print(f"[RESTART] Aplicación reiniciada")
