#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script maestro para automatizar todo el proceso de actualización:
1. Compilar el ejecutable con PyInstaller
2. Regenerar el instalador con Inno Setup
3. Crear el archivo ZIP con la release
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Ejecutar un comando y mostrar progreso"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode != 0:
            print(f"❌ Error en: {description}")
            return False
        print(f"✅ {description} - COMPLETADO")
        return True
    except Exception as e:
        print(f"❌ Error ejecutando: {description}")
        print(str(e))
        return False

def main():
    os.chdir(r'c:\Users\lauty\OneDrive\Escritorio\Sistema de venta')
    
    print("\n" + "="*60)
    print("🚀 DEPLOY AUTOMATIZADO - SISTEMA DE VENTAS")
    print("="*60)
    
    # Leer versión actual
    try:
        with open("version.txt", "r") as f:
            version = f.read().strip()
        print(f"\n📌 Versión: {version}")
    except:
        print("❌ Error: No se encontró version.txt")
        return False
    
    # Paso 1: Compilar ejecutable
    print("\n" + "="*60)
    print("PASO 1: Compilar Ejecutable")
    print("="*60)
    if not run_command(f"{sys.executable} generar_exe.py", "Compilación con PyInstaller"):
        return False
    
    # Paso 2: Copiar ejecutable a raíz
    print("\n" + "="*60)
    print("PASO 2: Actualizar ejecutable en raíz")
    print("="*60)
    try:
        import shutil
        src = r'c:\Users\lauty\OneDrive\Escritorio\Sistema de venta\dist\SistemaVentas.exe'
        dst = r'c:\Users\lauty\OneDrive\Escritorio\Sistema de venta\SistemaVentas.exe'
        shutil.copy2(src, dst)
        print(f"✅ Ejecutable copiado: {dst}")
    except Exception as e:
        print(f"❌ Error al copiar ejecutable: {e}")
        return False
    
    # Paso 3: Regenerar instalador
    print("\n" + "="*60)
    print("PASO 3: Regenerar Instalador")
    print("="*60)
    inno_cmd = r'"C:\Program Files (x86)\Inno Setup 6\iscc.exe" "c:\Users\lauty\OneDrive\Escritorio\Sistema de venta\installer_script.iss"'
    if not run_command(inno_cmd, "Compilación del instalador con Inno Setup"):
        print("⚠️ Advertencia: El instalador puede no estar actualizado")
    
    # Paso 4: Crear ZIP de release (opcional)
    print("\n" + "="*60)
    print("PASO 4: Crear archivo ZIP de release")
    print("="*60)
    try:
        crear_zip = Path("crear_zip_release.py")
        if crear_zip.exists():
            if run_command(f"{sys.executable} crear_zip_release.py", "Creación del ZIP"):
                print("✅ ZIP de release creado")
        else:
            print("⚠️ Archivo crear_zip_release.py no encontrado - saltando...")
    except:
        print("⚠️ No se pudo crear el ZIP")
    
    # Resumen final
    print("\n" + "="*60)
    print("✅ ¡DEPLOY COMPLETADO EXITOSAMENTE!")
    print("="*60)
    print(f"\n📦 Archivos generados para distribución:")
    print(f"  • Ejecutable: dist\\SistemaVentas.exe")
    print(f"  • Instalador: installer\\SistemaVentas_Setup.exe")
    
    instalador_path = Path("installer/SistemaVentas_Setup.exe")
    if instalador_path.exists():
        tamaño_mb = instalador_path.stat().st_size / (1024*1024)
        print(f"  • Tamaño instalador: {tamaño_mb:.2f} MB")
    
    print(f"\n🎯 Para distribuir, copia:")
    print(f"   installer\\SistemaVentas_Setup.exe")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
