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
        # Auto-detectar la ruta correcta buscando version.txt
        # Esto evita que si se ejecuta desde otro directorio, use la ruta incorrecta
        detected_path = self._find_project_root(base_path)
        self.base_path = os.path.abspath(detected_path if detected_path else base_path)
        
        # VALIDACIÓN CRÍTICA: Si no hay version.txt en base_path, forzar búsqueda en carpeta padre
        if not os.path.exists(os.path.join(self.base_path, "version.txt")):
            # Última búsqueda: intentar encontrar "Sistema de venta" en la ruta
            parts = self.base_path.split(os.sep)
            if "Sistema de venta" in parts:
                idx = parts.index("Sistema de venta")
                sistema_venta_path = os.sep.join(parts[:idx+1])
                if os.path.exists(os.path.join(sistema_venta_path, "version.txt")):
                    self.base_path = sistema_venta_path
        
        self.repo = "LautaroAraya/Sistema-de-venta"
        self.github_api = "https://api.github.com/repos"
        self.config_file = os.path.abspath(os.path.join(self.base_path, ".update_config.json"))
        self.version_file = os.path.abspath(os.path.join(self.base_path, "version.txt"))
        self.current_version = self.get_current_version()
    
    def _find_project_root(self, start_path):
        """Buscar la carpeta raíz del proyecto buscando version.txt
        
        Esto asegura que incluso si se ejecuta desde otro directorio,
        se usa la carpeta correcta para las actualizaciones.
        
        Estrategia:
        1. Si estamos en dist/, buscar en carpeta padre (donde está version.txt)
        2. Si no, buscar en start_path
        3. Si no, buscar hacia arriba hasta 10 niveles
        """
        # Si estamos en una carpeta "dist", buscar en la carpeta padre
        if os.path.basename(os.path.abspath(start_path)).lower() == 'dist':
            parent = os.path.dirname(start_path)
            if os.path.exists(os.path.join(parent, "version.txt")):
                return parent
        
        # Primero verificar si existe version.txt en start_path
        if os.path.exists(os.path.join(start_path, "version.txt")):
            return start_path
        
        # Si no, buscar en directorios padre
        current = start_path
        for _ in range(10):  # Limitar a 10 niveles de profundidad
            parent = os.path.dirname(current)
            if parent == current:  # Llegamos a la raíz del filesystem
                break
            version_file = os.path.join(parent, "version.txt")
            if os.path.exists(version_file):
                return parent
            current = parent
        
        # Si no se encuentra, retornar None (usar start_path)
        return None
        
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
        """(DESHABILITADO) Verificar si pasaron 5 días desde el último chequeo"""
        # return True para deshabilitar el chequeo automático por días
        # Código original comentado para futura reactivación
        # config = self.get_update_config()
        # last_check = config.get("last_check")
        # if not last_check:
        #     return True
        # try:
        #     last_check_date = datetime.fromisoformat(last_check)
        #     days_passed = (datetime.now() - last_check_date).days
        #     return days_passed >= 5
        # except:
        #     return True
        return False
    
    def check_for_updates(self, force=False):
        """(DESHABILITADO) Verificar si hay actualizaciones en GitHub"""
        # Código original comentado para futura reactivación
        # if not force and not self.should_check_for_updates():
        #     return False, None
        # try:
        #     url = f"{self.github_api}/{self.repo}/releases/latest"
        #     response = requests.get(url, timeout=10)
        #     if response.status_code == 404:
        #         config = self.get_update_config()
        #         config["last_check"] = datetime.now().isoformat()
        #         config["update_available"] = False
        #         config["latest_version"] = self.current_version
        #         self.save_update_config(config)
        #         return False, "No hay releases publicados en GitHub todavía"
        #     if response.status_code == 200:
        #         release = response.json()
        #         latest_version = release.get("tag_name", "").lstrip('v')
        #         config = self.get_update_config()
        #         config["last_check"] = datetime.now().isoformat()
        #         if latest_version and self._is_newer_version(latest_version, self.current_version):
        #             config["update_available"] = True
        #             config["latest_version"] = latest_version
        #             config["download_url"] = release.get("zipball_url")
        #             config["release_notes"] = release.get("body", "Sin descripción")
        #             config["release_url"] = release.get("html_url", "")
        #             self.save_update_config(config)
        #             return True, None
        #         else:
        #             config["update_available"] = False
        #             config["latest_version"] = latest_version or self.current_version
        #             self.save_update_config(config)
        #             return False, None
        #     else:
        #         return False, f"Error HTTP {response.status_code}"
        # except requests.exceptions.Timeout:
        #     return False, "Timeout: No se pudo conectar a GitHub"
        # except requests.exceptions.ConnectionError:
        #     return False, "Sin conexión a Internet"
        # except Exception as e:
        #     return False, str(e)
        # return False, "Error desconocido"
        return False, None
    
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
        """(DESHABILITADO) Verificar si es hora de actualizar (14:00-16:00 Argentina UTC-3)"""
        # return False para deshabilitar el chequeo por horario
        # Código original comentado para futura reactivación
        # tz_offset = -3
        # current_utc = datetime.utcnow()
        # current_argentina = current_utc.replace(tzinfo=None) + timedelta(hours=tz_offset)
        # hour = current_argentina.hour
        # return 14 <= hour < 16
        return False

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
        excluded = ("database/", "build/", "dist/", "installer/", ".git/")
        return any(path.startswith(e) for e in excluded)
    
    def _clean_pycache(self):
        """Limpiar todos los archivos de caché de Python (__pycache__ y .pyc)"""
        try:
            for root, dirs, files in os.walk(self.base_path):
                # Eliminar carpetas __pycache__
                if '__pycache__' in dirs:
                    pycache_path = os.path.join(root, '__pycache__')
                    try:
                        shutil.rmtree(pycache_path)
                    except:
                        pass
                
                # Eliminar archivos .pyc
                for file in files:
                    if file.endswith('.pyc'):
                        try:
                            os.remove(os.path.join(root, file))
                        except:
                            pass
        except:
            pass

    def _download_raw_file(self, file_path: str, tag: str):
        """Descargar un archivo individual desde GitHub raw a la ruta local."""
        raw_url = f"https://raw.githubusercontent.com/{self.repo}/{tag}/{file_path}"
        response = requests.get(raw_url, timeout=15)
        if response.status_code != 200:
            raise RuntimeError(f"No se pudo descargar {file_path}: {response.status_code}")
        local_path = os.path.abspath(os.path.join(self.base_path, file_path.replace('/', os.sep)))
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
                local_path = os.path.abspath(os.path.join(self.base_path, path.replace('/', os.sep)))
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
    
    def _download_exe_update(self, latest_version):
        """Descargar el ejecutable compilado directamente desde GitHub releases
        
        Esto es más rápido y eficiente que descargar el código fuente completo
        """
        try:
            # Buscar release específica con tag v{version}
            url = f"{self.github_api}/{self.repo}/releases/tags/v{latest_version}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            release = response.json()
            assets = release.get("assets", [])
            
            # Buscar el ejecutable (SistemaVentas.exe o similar)
            exe_asset = None
            for asset in assets:
                if asset["name"].endswith(".exe"):
                    exe_asset = asset
                    break
            
            if not exe_asset:
                return None
            
            return exe_asset["browser_download_url"]
        except:
            return None
    
    def _apply_exe_update(self, exe_download_url):
        """Descargar y reemplazar el ejecutable
        
        Esta es la forma más eficiente de actualizar para usuarios con EXE compilado
        """
        try:
            abs_base = os.path.abspath(self.base_path)
            exe_path = os.path.join(abs_base, "SistemaVentas.exe")
            exe_backup = exe_path + ".backup"
            
            # Descargar el nuevo ejecutable
            response = requests.get(exe_download_url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Crear backup del ejecutable actual
            if os.path.exists(exe_path):
                if os.path.exists(exe_backup):
                    os.remove(exe_backup)
                shutil.copy2(exe_path, exe_backup)
            
            # Guardar el nuevo ejecutable
            with open(exe_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return True
        except Exception as e:
            # Restaurar backup si falló
            if os.path.exists(exe_backup):
                try:
                    shutil.copy2(exe_backup, exe_path)
                except:
                    pass
            raise e

    def perform_update(self):
        """Descargar e instalar actualización"""
        try:
            config = self.get_update_config()
            latest_version = config.get("latest_version")
            
            if not latest_version:
                return False
            
            # Usar rutas ABSOLUTAS siempre para evitar que se cree en otros directorios
            abs_base = os.path.abspath(self.base_path)
            
            # VALIDACIÓN CRÍTICA: Verificar que abs_base tiene version.txt
            # Si no existe, es una ruta incorrecta y NO extraemos nada
            version_file = os.path.join(abs_base, "version.txt")
            if not os.path.exists(version_file):
                raise RuntimeError(
                    f"Ruta de actualización inválida. No se encontró version.txt en {abs_base}\n"
                    f"Se canceló la actualización para evitar corrupción de archivos."
                )
            
            original_cwd = os.getcwd()
            
            try:
                # Cambiar a la carpeta correcta ANTES de hacer nada
                os.chdir(abs_base)
                
                # Estrategia 1: Si hay ejecutable compilado disponible, usarlo (RECOMENDADO)
                exe_url = self._download_exe_update(latest_version)
                if exe_url:
                    try:
                        self._apply_exe_update(exe_url)
                        # Limpiar caché de Python
                        self._clean_pycache()
                        # Éxito: solo actualizar versión y reinicar
                        self.save_version(latest_version)
                        config["update_available"] = False
                        self.save_update_config(config)
                        messagebox.showinfo("Actualización Exitosa", "El sistema se reiniciará ahora.")
                        self.restart_app()
                        return True
                    except Exception as e:
                        # Si falla el EXE, intentar actualización de código fuente
                        pass
                
                # Estrategia 2: Intento incremental: solo archivos modificados
                try:
                    self._apply_incremental_update(latest_version)
                except Exception as e:
                    # Estrategia 3: Fallback: descarga completa del ZIP
                    download_url = config.get("download_url")
                    if not download_url:
                        raise
                    
                    # Rutas absolutas explícitas - garantizar que están en la carpeta correcta
                    zip_path = os.path.abspath(os.path.join(abs_base, "update.zip"))
                    extract_path = os.path.abspath(os.path.join(abs_base, "update_temp"))
                    
                    response = requests.get(download_url, timeout=30)
                    
                    with open(zip_path, 'wb') as f:
                        f.write(response.content)
                    
                    if os.path.exists(extract_path):
                        shutil.rmtree(extract_path)
                    
                    os.makedirs(extract_path, exist_ok=True)
                    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_path)
                    
                    temp_dirs = os.listdir(extract_path)
                    if temp_dirs:
                        source_dir = os.path.abspath(os.path.join(extract_path, temp_dirs[0]))
                        
                        # Verificar si la carpeta extraída contiene los archivos directamente
                        # o si están dentro de una subcarpeta
                        items_to_copy = os.listdir(source_dir) if os.path.isdir(source_dir) else []
                        
                        if not items_to_copy or (len(items_to_copy) == 1 and 
                                                  os.path.isdir(os.path.join(source_dir, items_to_copy[0]))):
                            # Si hay una única carpeta dentro, usar esa como source_dir
                            if items_to_copy:
                                source_dir = os.path.abspath(os.path.join(source_dir, items_to_copy[0]))
                                items_to_copy = os.listdir(source_dir)
                        
                        exclude_dirs = {'database', 'build', 'installer', 'dist', '.git', '.gitignore', '__pycache__'}
                        
                        for item in items_to_copy:
                            if item not in exclude_dirs:
                                src = os.path.abspath(os.path.join(source_dir, item))
                                dst = os.path.abspath(os.path.join(abs_base, item))
                                
                                if os.path.isdir(src):
                                    if os.path.exists(dst):
                                        shutil.rmtree(dst)
                                    shutil.copytree(src, dst)
                                else:
                                    shutil.copy2(src, dst)
                    
                    # Limpiar archivos temporales
                    shutil.rmtree(extract_path)
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
            finally:
                # Restaurar el working directory original
                os.chdir(original_cwd)
            
            # Limpiar caché de Python ANTES de reiniciar
            self._clean_pycache()
            
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
        """Reiniciar la aplicación de forma segura"""
        try:
            # Usar script restart.py que garantiza ejecución desde la carpeta correcta
            restart_script = os.path.abspath(os.path.join(self.base_path, "restart.py"))
            
            if os.path.exists(restart_script):
                # Si existe restart.py, usarlo
                python = sys.executable
                subprocess.Popen([python, restart_script], cwd=os.path.abspath(self.base_path))
            else:
                # Fallback: intentar reiniciar directamente
                if getattr(sys, 'frozen', False):
                    subprocess.Popen([sys.executable])
                else:
                    python = sys.executable
                    script = os.path.abspath(os.path.join(self.base_path, "main.py"))
                    subprocess.Popen([python, script], cwd=os.path.abspath(self.base_path))
            
            # Cerrar la aplicación actual
            sys.exit(0)
        except Exception as e:
            # Fallback: cerrar y que el usuario reinicie
            messagebox.showerror("Error", f"No se pudo reiniciar: {str(e)}")
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
