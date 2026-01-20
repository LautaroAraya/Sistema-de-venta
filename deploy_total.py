#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script TOTAL para automatizar TODO el proceso de deploy:
1. Actualizar versión
2. Compilar .exe con PyInstaller (deploy.bat)
3. Generar instalador con Inno Setup
4. Hacer git commit/push
5. Crear release en GitHub
6. Limpiar archivos temporales

Uso:
    python deploy_total.py
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime
import importlib

# Forzar UTF-8 en Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class DeployTotal:
    def __init__(self):
        self.base_dir = os.getcwd()
        self.version_file = os.path.join(self.base_dir, "version.txt")
        self.config_file = os.path.join(self.base_dir, ".deploy_config.json")
        self.exe_path = os.path.join(self.base_dir, "installer", "SistemaVentas_Setup.exe")
        self.github_token = None
        
        # Verificar que estamos en la carpeta correcta
        if not os.path.exists(self.version_file):
            print("\n❌ Error: No estás en la carpeta raíz del proyecto")
            print(f"   Carpeta actual: {self.base_dir}")
            sys.exit(1)
    
    def read_version(self):
        """Leer versión actual"""
        try:
            with open(self.version_file, 'r') as f:
                return f.read().strip()
        except:
            return "1.0.0"
    
    def save_version(self, version):
        """Guardar nueva versión"""
        try:
            with open(self.version_file, 'w') as f:
                f.write(version)
            return True
        except:
            return False
    
    def load_github_token(self):
        """Cargar token de GitHub desde archivo local (si existe)"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    token = config.get("github_token")
                    if token:
                        print("✅ Token de GitHub cargado desde archivo local")
                        return token
        except:
            pass
        return None
    
    def save_github_token(self, token):
        """Guardar token de GitHub en archivo local (encriptado sería mejor)"""
        try:
            config = {"github_token": token}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass
    
    def run_command(self, cmd, description):
        """Ejecutar comando y mostrar progreso"""
        print(f"\n{'='*70}")
        print(f"⏳ {description}")
        print(f"{'='*70}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
            
            if result.returncode != 0:
                print(f"❌ Error en: {description}")
                if result.stderr:
                    print(f"   {result.stderr}")
                return False
            
            if result.stdout:
                print(result.stdout)
            
            print(f"✅ {description} - OK")
            return True
        except Exception as e:
            print(f"❌ Error ejecutando: {description}")
            print(f"   {str(e)}")
            return False
    
    def run_deploy_bat(self):
        """Ejecutar deploy.bat"""
        if not os.path.exists(os.path.join(self.base_dir, "deploy.bat")):
            print("❌ No se encontró deploy.bat")
            return False
        
        return self.run_command(
            f'"{sys.executable}" deploy_actualizacion.py',
            "Compilación de ejecutable y setup"
        )
    
    def verify_exe(self):
        """Verificar que el .exe se compiló correctamente"""
        if not os.path.exists(self.exe_path):
            print(f"\n❌ Error: No se encontró {self.exe_path}")
            print("   La compilación puede haber fallado")
            return False
        
        size_mb = os.path.getsize(self.exe_path) / (1024*1024)
        print(f"✅ Ejecutable verificado: {size_mb:.2f} MB")
        return True
    
    def git_commit_and_push(self, version, changes):
        """Hacer commit y push a GitHub"""
        print(f"\n{'='*70}")
        print(f"⏳ Git commit and push")
        print(f"{'='*70}")
        
        try:
            # Git add
            subprocess.run(["git", "add", "."], check=True, capture_output=True, cwd=self.base_dir)
            print("✅ Files staged")
            
            # Git commit
            commit_msg = f"v{version}: {changes.split(chr(10))[0]}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                check=True,
                capture_output=True,
                cwd=self.base_dir
            )
            print(f"✅ Commit: {commit_msg}")
            
            # Git tag
            subprocess.run(
                ["git", "tag", f"v{version}"],
                check=True,
                capture_output=True,
                cwd=self.base_dir
            )
            print(f"✅ Tag created: v{version}")
            
            # Git push
            subprocess.run(
                ["git", "push", "origin", "main"],
                check=True,
                capture_output=True,
                cwd=self.base_dir
            )
            print("✅ Pushed to GitHub (main branch)")
            
            subprocess.run(
                ["git", "push", "origin", f"v{version}"],
                check=True,
                capture_output=True,
                cwd=self.base_dir
            )
            print(f"✅ Pushed tag: v{version}")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Git error: {e}")
            return False

    def ensure_pygithub(self):
        """Asegurar que PyGithub esté instalado (intenta instalar si falta)."""
        try:
            importlib.import_module("github")
            return True
        except ImportError:
            print(f"\n{'='*70}")
            print("⚠️  PyGithub no está instalado. Instalando automáticamente...")
            print(f"{'='*70}")
            try:
                install_cmd = [sys.executable, "-m", "pip", "install", "PyGithub"]
                result = subprocess.run(install_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print("❌ No se pudo instalar PyGithub")
                    if result.stderr:
                        print(result.stderr)
                    return False
                print("✅ PyGithub instalado")
                return True
            except Exception as e:
                print(f"❌ Error instalando PyGithub: {e}")
                return False
    
    def create_github_release(self, version, changes):
        """Crear release en GitHub con PyGithub"""
        # Asegurar que PyGithub está disponible
        if not self.ensure_pygithub():
            print("\n⚠️  PyGithub no está instalado y no se pudo instalar automáticamente")
            print("   Puedes crear la release manualmente:")
            print("   1. https://github.com/LautaroAraya/Sistema-de-venta/releases")
            print(f"   2. Tag: v{version}")
            print("   3. Adjunta installer/SistemaVentas_Setup.exe")
            return False

        try:
            from github import Github
            
            print(f"\n{'='*70}")
            print(f"⏳ Creando release en GitHub")
            print(f"{'='*70}")
            
            # Cargar token desde archivo o pedir
            token = self.load_github_token()
            if not token:
                print("\n🔑 Se necesita un token de GitHub")
                print("   Crear en: https://github.com/settings/tokens")
                print("   Permisos: repo (completo)")
                token = input("\n🔐 Ingresa tu token de GitHub: ").strip()
                
                if not token:
                    print("❌ Token vacío")
                    return False
                
                save = input("\n💾 ¿Guardar token para próximas veces? (s/n): ").strip().lower()
                if save == 's':
                    self.save_github_token(token)
                    print("✅ Token guardado")
            
            # Conectar a GitHub
            g = Github(token)
            repo = g.get_repo("LautaroAraya/Sistema-de-venta")
            print("✅ Conectado a GitHub")
            
            # Crear release
            release = repo.create_git_release(
                tag=f"v{version}",
                name=f"Versión {version}",
                message=changes,
                draft=False,
                prerelease=False
            )
            print(f"✅ Release creada: v{version}")
            
            # Subir .exe
            if os.path.exists(self.exe_path):
                print("⏳ Subiendo ejecutable...")
                with open(self.exe_path, 'rb') as f:
                    release.upload_asset(
                        file_path=self.exe_path,
                        label="SistemaVentas_Setup.exe",
                        content_type="application/octet-stream"
                    )
                print("✅ Ejecutable subido")
            
            print(f"\n🔗 Release URL: {release.html_url}")
            return True
            
        except ImportError:
            print(f"\n{'='*70}")
            print("⚠️  PyGithub no está instalado")
            print(f"{'='*70}")
            print("\nPara crear releases automáticas, instala PyGithub:")
            print("  pip install PyGithub")
            print("\nO crea la release manualmente:")
            print("  1. https://github.com/LautaroAraya/Sistema-de-venta/releases")
            print("  2. Click: Create a new release")
            print(f"  3. Tag: v{version}")
            print("  4. Attach: installer/SistemaVentas_Setup.exe")
            print("  5. Publish\n")
            return False
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def clean_temp_files(self):
        """Limpiar archivos temporales"""
        print(f"\n{'='*70}")
        print(f"🧹 Limpiando archivos temporales")
        print(f"{'='*70}")
        
        temp_files = ["update.zip", "update_temp"]
        for temp in temp_files:
            temp_path = os.path.join(self.base_dir, temp)
            if os.path.exists(temp_path):
                try:
                    if os.path.isfile(temp_path):
                        os.remove(temp_path)
                    else:
                        shutil.rmtree(temp_path)
                    print(f"✅ Eliminado: {temp}")
                except:
                    pass
    
    def run(self):
        """Ejecutar todo el proceso"""
        print("\n" + "="*70)
        print("🚀 DEPLOY TOTAL - SISTEMA DE VENTAS")
        print("="*70)
        
        current_version = self.read_version()
        print(f"\n📦 Versión actual: {current_version}")
        
        # Pedir nueva versión
        new_version = input("\n📝 Nueva versión (ej: 1.0.13): ").strip()
        
        if not new_version:
            print("❌ Cancelado")
            return False
        
        # Validar formato
        parts = new_version.split('.')
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            print("❌ Formato inválido. Usa: 1.0.13")
            return False
        
        if new_version <= current_version:
            print(f"❌ Nueva versión debe ser mayor a {current_version}")
            return False
        
        # Pedir descripción de cambios
        print("\n📄 Descripción de cambios:")
        print("   (Presiona Enter dos veces para terminar)")
        lines = []
        empty = 0
        while True:
            line = input()
            if not line:
                empty += 1
                if empty >= 2:
                    break
            else:
                empty = 0
                lines.append(line)
        
        changes = "\n".join(lines) if lines else "Actualización de versión"
        
        # Resumen
        print("\n" + "="*70)
        print("📋 RESUMEN")
        print("="*70)
        print(f"Versión: {current_version} → {new_version}")
        print(f"Cambios: {changes.split(chr(10))[0]}...")
        
        confirm = input("\n¿Continuar? (s/n): ").strip().lower()
        if confirm != 's':
            print("❌ Cancelado")
            return False
        
        # 1. Ejecutar deploy.bat
        if not self.run_deploy_bat():
            return False
        
        # 2. Verificar .exe
        if not self.verify_exe():
            return False
        
        # 3. Guardar versión
        if not self.save_version(new_version):
            print("❌ Error guardando versión")
            return False
        
        # 4. Git commit/push
        if not self.git_commit_and_push(new_version, changes):
            return False
        
        # 5. Crear release en GitHub
        if not self.create_github_release(new_version, changes):
            print("\n⚠️  Release no se creó automáticamente")
            print("   Pero puedes crearla manualmente en GitHub")
        
        # 6. Limpiar temp
        self.clean_temp_files()
        
        # Final
        print("\n" + "="*70)
        print("✅ ¡DEPLOY COMPLETADO!")
        print("="*70)
        print(f"\n📌 Versión: v{new_version}")
        print("✅ Los usuarios recibirán la actualización automáticamente")
        print("="*70 + "\n")
        
        return True

if __name__ == "__main__":
    deployer = DeployTotal()
    success = deployer.run()
    sys.exit(0 if success else 1)
