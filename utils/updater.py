import requests
import json
import os
import sys
import shutil
import zipfile
import threading
from datetime import datetime, timedelta
from tkinter import messagebox
import subprocess
from typing import List, Dict

class UpdateManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.repo = "LautaroAraya/Sistema-de-venta"
        self.github_api = "https://api.github.com/repos"
        self.config_file = os.path.join(base_path, ".update_config.json")
        self.version_file = os.path.join(base_path, "version.txt")
        self.current_version = self.get_current_version()
        
    def get_current_version(self):
        """Obtener versión actual del archivo version.txt"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    return f.read().strip()
        except:
            pass
        return "1.0.0"
    
    def save_version(self, version):
        """Guardar nueva versión"""
        try:
            with open(self.version_file, 'w') as f:
                f.write(version)
        except:
            pass
    
    def _is_newer_version(self, latest, current):
        """Comparar versiones (ej: 1.0.1 > 1.0.0)"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            return latest_parts > current_parts
        except:
            return latest != current
    
    def get_update_config(self):
        """Obtener configuración de actualizaciones"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"last_check": None, "update_available": False}
    
    def save_update_config(self, config):
        """Guardar configuración de actualizaciones"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass
    
    def should_check_for_updates(self):
        """Verificar si pasaron 5 días desde el último chequeo"""
        config = self.get_update_config()
        last_check = config.get("last_check")
        
        if not last_check:
            return True
        
        try:
            last_check_date = datetime.fromisoformat(last_check)
            days_passed = (datetime.now() - last_check_date).days
            return days_passed >= 5
        except:
            return True
    
    def check_for_updates(self, force=False):
        """Verificar si hay actualizaciones en GitHub
        
        Args:
            force: Si True, no espera 5 días, busca siempre
        
        Returns:
            tuple: (has_updates: bool, error_message: str or None)
        """
        if not force and not self.should_check_for_updates():
            return False, None
        
        try:
            # Obtener releases de GitHub
            url = f"{self.github_api}/{self.repo}/releases/latest"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 404:
                # No hay releases creados
                config = self.get_update_config()
                config["last_check"] = datetime.now().isoformat()
                config["update_available"] = False
                config["latest_version"] = self.current_version
                self.save_update_config(config)
                return False, "No hay releases publicados en GitHub todavía"
            
            if response.status_code == 200:
                release = response.json()
                latest_version = release.get("tag_name", "").lstrip('v')
                
                config = self.get_update_config()
                config["last_check"] = datetime.now().isoformat()
                
                if latest_version and self._is_newer_version(latest_version, self.current_version):
                    config["update_available"] = True
                    config["latest_version"] = latest_version
                    config["download_url"] = release.get("zipball_url")
                    config["release_notes"] = release.get("body", "Sin descripción")
                    config["release_url"] = release.get("html_url", "")
                    self.save_update_config(config)
                    return True, None
                else:
                    config["update_available"] = False
                    config["latest_version"] = latest_version or self.current_version
                    self.save_update_config(config)
                    return False, None
            else:
                return False, f"Error HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Timeout: No se pudo conectar a GitHub"
        except requests.exceptions.ConnectionError:
            return False, "Sin conexión a Internet"
        except Exception as e:
            return False, str(e)
        
        return False, "Error desconocido"
    
    def get_latest_version_info(self):
        """Obtener información de la última versión disponible"""
        config = self.get_update_config()
        return {
            "current_version": self.current_version,
            "latest_version": config.get("latest_version", self.current_version),
            "available": config.get("update_available", False),
            "release_notes": config.get("release_notes", ""),
            "download_url": config.get("download_url", "")
        }
    
    def is_update_time(self):
        """Verificar si es hora de actualizar (14:00-16:00 Argentina UTC-3)"""
        # Zona horaria Argentina (UTC-3)
        tz_offset = -3
        current_utc = datetime.utcnow()
        current_argentina = current_utc.replace(tzinfo=None) + timedelta(hours=tz_offset)
        
        hour = current_argentina.hour
        return 14 <= hour < 16

    def _compare_versions(self, latest_version: str) -> List[Dict]:
        """Obtener lista de archivos cambiados entre la versión actual y la nueva.

        Usa la API de GitHub /compare para traer solo los archivos modificados.
        """
        current_tag = f"v{self.current_version}"
        latest_tag = f"v{latest_version}"
        url = f"{self.github_api}/{self.repo}/compare/{current_tag}...{latest_tag}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise RuntimeError(f"No se pudo comparar versiones: {response.status_code}")
        data = response.json()
        return data.get("files", [])

    def _is_excluded(self, path: str) -> bool:
        """Definir rutas que no deben tocarse (datos y build)."""
        excluded = ("database/", "build/", "dist/", "installer/", ".git/", "__pycache__/")
        return any(path.startswith(e) for e in excluded)

    def _download_raw_file(self, file_path: str, tag: str):
        """Descargar un archivo individual desde GitHub raw a la ruta local."""
        raw_url = f"https://raw.githubusercontent.com/{self.repo}/{tag}/{file_path}"
        response = requests.get(raw_url, timeout=15)
        if response.status_code != 200:
            raise RuntimeError(f"No se pudo descargar {file_path}: {response.status_code}")
        local_path = os.path.join(self.base_path, file_path.replace('/', os.sep))
        local_dir = os.path.dirname(local_path)
        if local_dir:
            os.makedirs(local_dir, exist_ok=True)
        with open(local_path, 'wb') as f:
            f.write(response.content)

    def _apply_incremental_update(self, latest_version: str):
        """Aplicar actualización descargando solo archivos cambiados.

        Si falla, se propagará la excepción para que el flujo haga fallback al ZIP completo.
        """
        changed_files = self._compare_versions(latest_version)
        latest_tag = f"v{latest_version}"
        for file_info in changed_files:
            path = file_info.get("filename", "")
            status = file_info.get("status", "")
            if not path or self._is_excluded(path + "/"):
                continue  # no tocar datos ni builds
            if status in ("modified", "added"):
                self._download_raw_file(path, latest_tag)
            elif status == "removed":
                local_path = os.path.join(self.base_path, path.replace('/', os.sep))
                if os.path.exists(local_path):
                    os.remove(local_path)
    
    def show_update_alert(self, root):
        """Mostrar alerta de actualización disponible"""
        config = self.get_update_config()
        
        if not config.get("update_available"):
            return False
        
        latest_version = config.get("latest_version", "?")
        
        if self.is_update_time():
            # Mostrar diálogo para actualizar ahora
            result = messagebox.askyesno(
                "Actualización Disponible",
                f"Versión nueva disponible: {latest_version}\n\n"
                f"Versión actual: {self.current_version}\n\n"
                f"El sistema se reiniciará para instalar la actualización.\n"
                f"¿Desea continuar?"
            )
            
            if result:
                self.perform_update()
                return True
        else:
            # Mostrar alerta de actualización pendiente
            messagebox.showinfo(
                "Actualización Pendiente",
                f"Hay una actualización disponible: {latest_version}\n\n"
                f"Se descargará automáticamente entre las 14:00 y 16:00 hs.\n"
                f"El sistema se reiniciará en ese horario."
            )
        
        return False
    
    def perform_update(self):
        """Descargar e instalar actualización"""
        try:
            # Garantizar que todas las operaciones se hagan dentro del directorio base
            os.chdir(self.base_path)

            config = self.get_update_config()
            download_url = config.get("download_url")
            latest_version = config.get("latest_version")
            
            if not latest_version:
                return False
            
            # 1) Intento incremental: solo archivos modificados
            try:
                self._apply_incremental_update(latest_version)
            except Exception:
                # 2) Fallback: descarga completa del ZIP
                if not download_url:
                    raise
                zip_path = os.path.join(self.base_path, "update.zip")
                response = requests.get(download_url, timeout=30)
                
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                extract_path = os.path.join(self.base_path, "update_temp")
                if os.path.exists(extract_path):
                    shutil.rmtree(extract_path)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                
                temp_dirs = os.listdir(extract_path)
                if temp_dirs:
                    source_dir = os.path.join(extract_path, temp_dirs[0])
                    exclude_dirs = {'database', 'build', 'installer', 'dist', '.git', '.gitignore'}
                    
                    for item in os.listdir(source_dir):
                        if item not in exclude_dirs:
                            src = os.path.join(source_dir, item)
                            dst = os.path.join(self.base_path, item)
                            
                            if os.path.isdir(src):
                                if os.path.exists(dst):
                                    shutil.rmtree(dst)
                                shutil.copytree(src, dst)
                            else:
                                shutil.copy2(src, dst)
                
                shutil.rmtree(extract_path)
                os.remove(zip_path)
            
            # Guardar nueva versión y config
            self.save_version(latest_version)
            config["update_available"] = False
            self.save_update_config(config)
            
            messagebox.showinfo("Actualización Exitosa", "El sistema se reiniciará ahora.")
            self.restart_app()
            
            return True
        except Exception as e:
            messagebox.showerror("Error en Actualización", f"Error: {str(e)}")
            return False
    
    def restart_app(self):
        """Reiniciar la aplicación"""
        try:
            if getattr(sys, 'frozen', False):
                # Si es ejecutable
                os.execl(sys.executable, sys.executable)
            else:
                # Si es script Python
                python = sys.executable
                script = os.path.join(self.base_path, "main.py")
                os.execl(python, python, script)
        except:
            # Fallback: cerrar y que el usuario reinicie
            sys.exit(0)
    
    def check_updates_async(self, root):
        """Verificar actualizaciones en background (no bloquea UI)"""
        def check():
            try:
                if self.check_for_updates():
                    self.show_update_alert(root)
            except:
                pass
        
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
    
    def check_updates_sync(self, callback=None):
        """Verificar actualizaciones de forma síncrona (bloqueante)
        
        Args:
            callback: Función a ejecutar con el resultado: callback(has_updates, info_dict)
        """
        try:
            has_updates = self.check_for_updates(force=True)
            info = self.get_latest_version_info()
            
            if callback:
                callback(has_updates, info)
            
            return has_updates, info
        except Exception as e:
            if callback:
                callback(False, {"error": str(e)})
            return False, {"error": str(e)}
