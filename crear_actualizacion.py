#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para automatizar el proceso de crear una nueva versión y release en GitHub
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def main():
    print("=" * 60)
    print("🚀 CREAR NUEVA ACTUALIZACIÓN")
    print("=" * 60)
    
    # Leer versión actual
    version_file = "version.txt"
    try:
        with open(version_file, 'r') as f:
            current_version = f.read().strip()
    except:
        print("❌ Error: No se encontró version.txt")
        return
    
    print(f"\n📦 Versión actual: {current_version}")
    
    # Solicitar nueva versión
    new_version = input("📝 Ingresa la nueva versión (ej: 1.0.2): ").strip()
    
    if not new_version:
        print("❌ Versión cancelada")
        return
    
    # Solicitar descripción
    print("\n📄 Escribe la descripción de cambios (presiona Enter dos veces al terminar):")
    print("(Ejemplos: nuevas características, correcciones, mejoras)")
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            if lines and not input("¿Terminar? (s/n): ").lower().startswith('n'):
                break
    
    changes = "\n".join(lines) if lines else "Actualización de versión"
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE CAMBIOS")
    print("=" * 60)
    print(f"Versión: {current_version} → {new_version}")
    print(f"Cambios:\n{changes}")
    print("=" * 60)
    
    confirm = input("\n¿Proceder con la actualización? (s/n): ").lower()
    if confirm != 's':
        print("❌ Cancelado")
        return
    
    try:
        # 1. Actualizar version.txt
        print("\n✅ Actualizando version.txt...")
        with open(version_file, 'w') as f:
            f.write(new_version)
        
        # 2. Hacer commit
        print("✅ Haciendo commit...")
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"v{new_version}: {changes.split(chr(10))[0]}"],
            check=True,
            capture_output=True
        )
        
        # 3. Crear tag
        print("✅ Creando tag...")
        subprocess.run(["git", "tag", f"v{new_version}"], check=True, capture_output=True)
        
        # 4. Push
        print("✅ Subiendo a GitHub...")
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", f"v{new_version}"], check=True, capture_output=True)
        
        print("\n" + "=" * 60)
        print("🎉 ¡ACTUALIZACIÓN COMPLETADA!")
        print("=" * 60)
        print(f"\n✓ Versión {new_version} lista en GitHub")
        print("\n📢 Ahora debes crear un RELEASE en GitHub:")
        print("   1. Ve a: https://github.com/LautaroAraya/Sistema-de-venta/releases")
        print(f"   2. Presiona 'Create a new release'")
        print(f"   3. Tag: v{new_version}")
        print(f"   4. Título: v{new_version} - Actualización")
        print(f"   5. Descripción:\n{changes}")
        print("   6. Presiona 'Publish release'")
        print("\n💡 Los usuarios verán la actualización en Configuración → Actualizaciones")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error en Git: {e}")
        print("Asegúrate de tener Git configurado y conectividad a GitHub")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
