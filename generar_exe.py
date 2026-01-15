#!/usr/bin/env python
"""Script para generar el ejecutable con PyInstaller"""
import subprocess
import sys
import os

os.chdir(r'c:\Users\lauty\OneDrive\Escritorio\Sistema de venta')

# Instalar dependencias necesarias
print("Instalando dependencias necesarias...")
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'jaraco.functools'], 
               capture_output=True)

cmd = [
    sys.executable, 
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
