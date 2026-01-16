#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear una release en GitHub automáticamente.
Requiere: pip install PyGithub

Uso:
    python crear_release_github.py
"""

import os
import sys
from pathlib import Path

def main():
    print("\n" + "="*70)
    print("🚀 CREAR RELEASE EN GITHUB - SISTEMA DE VENTAS")
    print("="*70)
    
    # Verificar que estamos en la carpeta correcta
    base_dir = os.getcwd()
    if not os.path.exists(os.path.join(base_dir, "version.txt")):
        print("\n❌ Error: No estás en la carpeta raíz del proyecto")
        print(f"   Carpeta actual: {base_dir}")
        return False
    
    # Leer versión actual
    try:
        with open("version.txt", "r") as f:
            current_version = f.read().strip()
        print(f"\n📌 Versión actual: {current_version}")
    except:
        print("❌ Error: No se encontró version.txt")
        return False
    
    # Solicitar nueva versión
    new_version = input("\n📝 Ingresa la nueva versión (ej: 1.0.12): ").strip()
    
    if not new_version:
        print("❌ Cancelado: Sin versión ingresada")
        return False
    
    # Validar formato de versión
    parts = new_version.split('.')
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        print("❌ Error: Formato inválido. Usa formato: 1.0.12")
        return False
    
    # Verificar que la versión es más nueva
    if new_version <= current_version:
        print(f"❌ Error: La nueva versión ({new_version}) debe ser mayor a {current_version}")
        return False
    
    # Solicitar descripción
    print("\n📄 Descripción de cambios:")
    print("   (Presiona Enter dos veces para terminar)")
    lines = []
    empty_lines = 0
    while True:
        line = input()
        if not line:
            empty_lines += 1
            if empty_lines >= 2:
                break
        else:
            empty_lines = 0
            lines.append(line)
    
    description = "\n".join(lines) if lines else "Actualización de versión"
    
    # Resumen
    print("\n" + "="*70)
    print("📋 RESUMEN DE RELEASE")
    print("="*70)
    print(f"Versión: {new_version}")
    print(f"Tag: v{new_version}")
    print(f"\nDescripción:\n{description}")
    
    exe_file = os.path.join(base_dir, "installer", "SistemaVentas_Setup.exe")
    if os.path.exists(exe_file):
        size_mb = os.path.getsize(exe_file) / (1024*1024)
        print(f"\n📦 Ejecutable encontrado: SistemaVentas_Setup.exe ({size_mb:.2f} MB)")
    else:
        print(f"\n⚠️  Advertencia: No se encontró {exe_file}")
        print("   Asegúrate de ejecutar deploy.bat primero")
    
    confirm = input("\n¿Continuar con la creación de la release? (s/n): ").strip().lower()
    if confirm != 's':
        print("❌ Cancelado por el usuario")
        return False
    
    # Ahora intentar usar PyGithub
    try:
        print("\n📦 Intentando importar PyGithub...")
        from github import Github
        
        print("\n🔑 Se necesita un token de GitHub para continuar.")
        print("   Crear token en: https://github.com/settings/tokens")
        print("   Permisos necesarios: repo (completo)")
        
        token = input("\n🔐 Ingresa tu token de GitHub: ").strip()
        if not token:
            print("❌ Token vacío, cancelado")
            return False
        
        print("\n⏳ Conectando a GitHub...")
        g = Github(token)
        
        # Obtener repositorio
        print("⏳ Obteniendo información del repositorio...")
        repo = g.get_repo("LautaroAraya/Sistema-de-venta")
        
        # Crear release
        print(f"⏳ Creando release v{new_version}...")
        
        release = repo.create_git_release(
            tag=f"v{new_version}",
            name=f"Versión {new_version}",
            message=description,
            draft=False,
            prerelease=False
        )
        
        # Subir archivo ejecutable
        if os.path.exists(exe_file):
            print("⏳ Subiendo ejecutable...")
            with open(exe_file, 'rb') as f:
                release.upload_asset(
                    file_path=exe_file,
                    label="SistemaVentas_Setup.exe",
                    content_type="application/octet-stream"
                )
            print("✅ Ejecutable subido exitosamente")
        
        # Actualizar version.txt
        print("\n⏳ Actualizando version.txt...")
        with open("version.txt", "w") as f:
            f.write(new_version)
        
        print("\n" + "="*70)
        print("✅ ¡RELEASE CREADA EXITOSAMENTE!")
        print("="*70)
        print(f"\n📌 Versión: v{new_version}")
        print(f"🔗 URL: {release.html_url}")
        print(f"\n💾 Archivo: {exe_file}")
        print("\n✅ Los clientes recibirán la actualización automáticamente")
        print("="*70 + "\n")
        
        return True
        
    except ImportError:
        print("\n" + "="*70)
        print("⚠️  PyGithub no está instalado")
        print("="*70)
        print("\nPara crear releases automáticamente, instala PyGithub:")
        print("\n  pip install PyGithub")
        print("\nO crea la release manualmente:")
        print("  1. Ve a: https://github.com/LautaroAraya/Sistema-de-venta/releases")
        print("  2. Click: Create a new release")
        print(f"  3. Tag: v{new_version}")
        print(f"  4. Title: Versión {new_version}")
        print("  5. Description: (copia el texto arriba)")
        print("  6. Attach: SistemaVentas_Setup.exe")
        print("  7. Publish\n")
        
        # Actualizar version.txt igual
        print("⏳ Actualizando version.txt (igual si lo haces manual)...")
        with open("version.txt", "w") as f:
            f.write(new_version)
        print("✅ version.txt actualizado\n")
        
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nIntenta crear la release manualmente:")
        print("  https://github.com/LautaroAraya/Sistema-de-venta/releases\n")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
