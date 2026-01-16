#!/usr/bin/env python
"""
Script reiniciador que se ejecuta después de una actualización.
Asegura que se ejecuta desde la carpeta correcta (buscando version.txt).
"""
import os
import sys
import subprocess
import time

def find_project_root(start_path):
    """Encontrar la carpeta raíz buscando version.txt"""
    # Si estamos en una carpeta "dist", buscar en la carpeta padre
    if os.path.basename(os.path.abspath(start_path)).lower() == 'dist':
        parent = os.path.dirname(start_path)
        if os.path.exists(os.path.join(parent, "version.txt")):
            return parent
    
    # Primero verificar si existe version.txt en start_path
    if os.path.exists(os.path.join(start_path, "version.txt")):
        return start_path
    
    # Si no, buscar en directorios padre
    current = start_path
    for _ in range(15):
        parent = os.path.dirname(current)
        if parent == current:
            break
        version_file = os.path.join(parent, "version.txt")
        if os.path.exists(version_file):
            return parent
        current = parent
    
    return start_path

# Obtener la carpeta donde está este script
restart_script_dir = os.path.dirname(os.path.abspath(__file__))

# Buscar la carpeta correcta
project_root = find_project_root(restart_script_dir)

print(f"[RESTART] Esperando a que se cierre la aplicación...")
time.sleep(2)

print(f"[RESTART] Reiniciando desde: {project_root}")

# Cambiar a la carpeta correcta
os.chdir(project_root)

if getattr(sys, 'frozen', False):
    # Si somos un ejecutable PyInstaller
    print(f"[RESTART] Ejecutando como EXE")
    subprocess.Popen([sys.executable])
else:
    # Si somos un script Python
    print(f"[RESTART] Ejecutando main.py con Python")
    python = sys.executable
    main_script = os.path.join(project_root, "main.py")
    
    print(f"[RESTART] Python: {python}")
    print(f"[RESTART] Script: {main_script}")
    print(f"[RESTART] Working dir: {os.getcwd()}")
    
    subprocess.Popen([python, main_script], cwd=project_root)

print(f"[RESTART] Aplicación reiniciada")

