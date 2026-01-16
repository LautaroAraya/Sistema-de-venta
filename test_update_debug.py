#!/usr/bin/env python
"""Script de debug para ver exactamente dónde se crean archivos durante actualización"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.updater import UpdateManager

# Inicializar UpdateManager desde la carpeta correcta
base_path = os.path.dirname(os.path.abspath(__file__))
print(f"BASE_PATH detectado: {base_path}")
print(f"Working directory actual: {os.getcwd()}")

updater = UpdateManager(base_path)
print(f"UpdateManager.base_path: {updater.base_path}")
print(f"UpdateManager.version_file: {updater.version_file}")
print(f"UpdateManager.config_file: {updater.config_file}")

# Verificar configuración de actualización
config = updater.get_update_config()
print(f"\nConfiguraciónde actualización: {config}")

if config.get("update_available"):
    print(f"\n⚠️  Hay actualización disponible: {config.get('latest_version')}")
    print(f"URL de descarga: {config.get('download_url')}")
    print(f"\nProcediendo con actualización...")
    
    # Mostrar estado antes
    print(f"\nArchivos en Escritorio ANTES de actualizar:")
    desktop = os.path.dirname(base_path)
    for item in os.listdir(desktop):
        if item != "Sistema de venta":
            full_path = os.path.join(desktop, item)
            mtime = os.path.getmtime(full_path)
            from datetime import datetime
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  - {item} ({mtime_str})")
    
    # Realizar actualización
    try:
        updater.perform_update()
        print("\n✓ Actualización completada")
    except Exception as e:
        print(f"\n✗ Error en actualización: {e}")
        import traceback
        traceback.print_exc()
    
    # Mostrar estado después
    print(f"\nArchivos en Escritorio DESPUÉS de actualizar:")
    for item in os.listdir(desktop):
        if item != "Sistema de venta":
            full_path = os.path.join(desktop, item)
            mtime = os.path.getmtime(full_path)
            from datetime import datetime
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  - {item} ({mtime_str})")
else:
    print("\n✓ No hay actualización disponible")
