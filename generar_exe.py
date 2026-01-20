#!/usr/bin/env python
"""Script para generar el ejecutable con PyInstaller"""
import subprocess
import sys
import os
import io

# Forzar UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

os.chdir(r'c:\Users\lauty\OneDrive\Escritorio\Sistema de venta')

# Detectar si estamos en un entorno virtual
venv_python = os.path.join(os.getcwd(), '.venv', 'Scripts', 'python.exe')
if os.path.exists(venv_python):
    python_exe = venv_python
    print(f"✓ Usando Python del entorno virtual: {python_exe}")
else:
    python_exe = sys.executable
    print(f"⚠ Usando Python del sistema: {python_exe}")

# Verificar que PyInstaller esté instalado
try:
    result = subprocess.run([python_exe, '-m', 'pip', 'show', 'pyinstaller'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("Instalando PyInstaller...")
        subprocess.run([python_exe, '-m', 'pip', 'install', 'pyinstaller'], check=True)
except Exception as e:
    print(f"Error verificando PyInstaller: {e}")

# Usar el archivo .spec en lugar de parámetros de línea de comandos
spec_file = 'SistemaVentas.spec'
if os.path.exists(spec_file):
    cmd = [python_exe, '-m', 'PyInstaller', '--clean', spec_file]
    print(f"Generando ejecutable usando {spec_file}...")
else:
    cmd = [
        python_exe, 
        '-m', 
        'PyInstaller',
        '--icon=assets\\logoinstalador.ico',
        '--exclude-module=pkg_resources',
        '--clean',
        '--onefile',
        '--windowed',
        '--name', 'SistemaVentas',
        'main.py'
    ]
    print("Generando ejecutable con PyInstaller...")

print(" ".join(cmd))
result = subprocess.run(cmd)
sys.exit(result.returncode)
