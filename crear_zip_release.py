#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear el archivo ZIP de distribución para GitHub Release
Incluye todos los archivos necesarios del sistema
"""

import os
import zipfile
import sys
from datetime import datetime
import argparse

def create_release_zip(no_pause=False):
    """Crear archivo ZIP para el release"""
    
    # Leer versión
    try:
        with open('version.txt', 'r') as f:
            version = f.read().strip()
    except:
        print("❌ Error: No se encontró version.txt")
        return
    
    print("=" * 70)
    print(f"📦 CREAR ZIP DE DISTRIBUCIÓN - v{version}")
    print("=" * 70)
    
    # Nombre del archivo ZIP
    zip_filename = f"Sistema_de_Venta_v{version}.zip"
    
    # Directorios a EXCLUIR (por nombre exacto)
    exclude_dirs = {
        '.git',
        '.venv',
        'venv',
        '__pycache__',
        'build',
        'dist',
        '.vs',
        '.vscode',
        'actualizaciones',
        'fotos_reparaciones',
        'fotos_temporales',
    }

    # Patrones o archivos a EXCLUIR
    exclude_patterns = [
        '.pyc',
        '.pyo',
        '.pyd',
        '.spec',
        '.update_config.json',
        zip_filename,  # No incluirse a sí mismo
    ]
    
    # Archivos que DEBEN incluirse
    important_files = [
        'main.py',
        'version.txt',
        'requirements.txt',
        'run.bat',
        'README.md',
        'MANUAL_USO.md',
        'INICIO_RAPIDO.txt',
        'SISTEMA_ERRORES.md',
        'INSTRUCCIONES_ERRORES_Y_ACTUALIZACIONES.md',
        'NOTAS_VERSION_1.0.11.md',
        'buscar_actualizacion.py',
        'buscar_actualizacion.bat',
        'test_errores.py',
    ]
    
    def should_exclude(path):
        """Verificar si un archivo/carpeta debe excluirse"""
        parts = set(os.path.normpath(path).split(os.sep))
        if parts.intersection(exclude_dirs):
            return True

        for pattern in exclude_patterns:
            if path.endswith(pattern):
                return True
            if pattern in path:
                return True

        return False
    
    print(f"\n📝 Creando: {zip_filename}")
    print(f"📂 Carpeta: {os.getcwd()}\n")
    
    files_added = 0
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            # Recorrer todos los archivos del directorio
            for root, dirs, files in os.walk('.'):
                # Filtrar directorios a excluir
                dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Saltar archivos a excluir
                    if should_exclude(file_path):
                        continue
                    
                    # Crear ruta relativa para el ZIP
                    arcname = file_path[2:]  # Remover './'
                    
                    # Agregar al ZIP
                    zipf.write(file_path, arcname)
                    files_added += 1
                    
                    # Mostrar archivos importantes
                    if file in important_files or 'utils/' in arcname or 'views/' in arcname:
                        print(f"  ✓ {arcname}")
            
            # Crear carpeta logs/errors vacía en el ZIP
            zipf.writestr('logs/errors/.gitkeep', '')
            print(f"  ✓ logs/errors/ (carpeta vacía)")
        
        # Obtener tamaño del archivo
        size_bytes = os.path.getsize(zip_filename)
        size_mb = size_bytes / (1024 * 1024)
        
        print("\n" + "=" * 70)
        print("✅ ¡ZIP CREADO EXITOSAMENTE!")
        print("=" * 70)
        print(f"\n📦 Archivo: {zip_filename}")
        print(f"📊 Tamaño: {size_mb:.2f} MB ({size_bytes:,} bytes)")
        print(f"📁 Archivos incluidos: {files_added}")
        print(f"📍 Ubicación: {os.path.abspath(zip_filename)}")
        
        print("\n📢 PRÓXIMOS PASOS:")
        print("=" * 70)
        print(f"1. Ve a: https://github.com/LautaroAraya/Sistema-de-venta/releases")
        print(f"2. Click en 'Create a new release'")
        print(f"3. Selecciona tag: v{version}")
        print(f"4. Sube este archivo: {zip_filename}")
        print(f"5. Publica el release")
        print("\n💡 Los usuarios podrán descargar esta versión con:")
        print(f"   python buscar_actualizacion.py")
        
    except Exception as e:
        print(f"\n❌ Error al crear ZIP: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crear ZIP de distribucion")
    parser.add_argument("--no-pause", action="store_true", help="No esperar Enter al finalizar")
    args = parser.parse_args()

    try:
        create_release_zip(no_pause=args.no_pause)
    except Exception as e:
        print(f"❌ Error: {e}")

    if not args.no_pause and sys.stdin.isatty():
        input("\n\nPresiona Enter para salir...")
