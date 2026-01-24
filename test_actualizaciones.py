#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema de actualizaciones
Ejecutar este script para verificar que todo funcione correctamente
"""

import os
import sys
import io

# Forzar UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Agregar el directorio raíz al path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

## from utils.updater import UpdateManager

def test_update_system():
    """Probar el sistema de actualizaciones"""
    
    print("="*60)
    print("🔧 PRUEBA DEL SISTEMA DE ACTUALIZACIONES")
    print("="*60)
    
    ## # Inicializar UpdateManager
    ## update_manager = UpdateManager(BASE_DIR)
    
    print(f"\n📦 Versión actual: v{update_manager.current_version}")
    print(f"📂 Directorio base: {BASE_DIR}")
    print(f"📄 Archivo de versión: {update_manager.version_file}")
    print(f"🔗 Repositorio: {update_manager.repo}")
    
    # Verificar archivo version.txt
    print(f"\n{'='*60}")
    print("1️⃣ VERIFICANDO ARCHIVO version.txt")
    print("="*60)
    
    if os.path.exists(update_manager.version_file):
        print(f"✅ Archivo version.txt existe")
        with open(update_manager.version_file, 'r') as f:
            version_content = f.read().strip()
        print(f"   Contenido: '{version_content}'")
    else:
        print(f"❌ ERROR: No se encuentra version.txt")
        return
    
    # Verificar configuración
    print(f"\n{'='*60}")
    print("2️⃣ VERIFICANDO CONFIGURACIÓN")
    print("="*60)
    
    config = update_manager.get_update_config()
    print(f"✅ Configuración cargada:")
    print(f"   Última búsqueda: {config.get('last_check', 'Nunca')}")
    print(f"   Actualización disponible: {config.get('update_available', False)}")
    if config.get('latest_version'):
        print(f"   Última versión conocida: v{config.get('latest_version')}")
    
    # Buscar actualizaciones
    print(f"\n{'='*60}")
    print("3️⃣ BUSCANDO ACTUALIZACIONES EN GITHUB")
    print("="*60)
    print("⏳ Conectando a GitHub...")
    
    try:
        has_update, error_msg = update_manager.check_for_updates(force=True)
        
        if error_msg:
            print(f"⚠️  Advertencia: {error_msg}")
            if "No hay releases" in error_msg:
                print("\n💡 SOLUCIÓN:")
                print("   1. Ve a GitHub: https://github.com/LautaroAraya/Sistema-de-venta/releases")
                print("   2. Crea un nuevo Release:")
                print("      - Tag: v1.0.1")
                print("      - Título: v1.0.1 - Primera actualización")
                print("      - Descripción: Prueba del sistema de actualizaciones")
                print("   3. Publica el Release")
                print("   4. Vuelve a ejecutar este script")
        elif has_update:
            info = update_manager.get_latest_version_info()
            print(f"✅ ¡ACTUALIZACIÓN DISPONIBLE!")
            print(f"\n   Versión actual:  v{info['current_version']}")
            print(f"   Nueva versión:   v{info['latest_version']}")
            print(f"\n   📝 Notas de la versión:")
            notes = info['release_notes'][:200]
            print(f"   {notes}{'...' if len(info['release_notes']) > 200 else ''}")
            
            print(f"\n{'='*60}")
            print("4️⃣ ¿DESEAS INSTALAR LA ACTUALIZACIÓN?")
            print("="*60)
            print("⚠️  ADVERTENCIA: Este es un script de prueba.")
            print("   Para instalar actualizaciones, usa la aplicación principal:")
            print("   → Configuración → Actualizaciones → Buscar Actualizaciones")
            
        else:
            print(f"✅ Sistema actualizado")
            print(f"   Ya tienes la versión más reciente: v{update_manager.current_version}")
            
    except Exception as e:
        print(f"❌ ERROR al buscar actualizaciones: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE LA PRUEBA")
    print("="*60)
    
    final_config = update_manager.get_update_config()
    
    print(f"✓ Versión actual: v{update_manager.current_version}")
    print(f"✓ Última verificación: {final_config.get('last_check', 'N/A')}")
    print(f"✓ Estado: {'Actualización disponible' if final_config.get('update_available') else 'Actualizado'}")
    
    print(f"\n{'='*60}")
    print("✅ PRUEBA COMPLETADA")
    print("="*60)
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Si hay actualización disponible, pruébala desde la app principal")
    print("   2. Si no hay releases, crea uno en GitHub")
    print("   3. Lee GUIA_ACTUALIZACIONES.md para más información")
    print()

if __name__ == "__main__":
    test_update_system()
