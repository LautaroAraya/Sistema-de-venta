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
    
    def check_for_updates(self):
        """Verificar si hay actualizaciones en GitHub"""
        if not self.should_check_for_updates():
            return False
        
        try:
            # Obtener releases de GitHub
            url = f"{self.github_api}/{self.repo}/releases/latest"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                release = response.json()
                latest_version = release.get("tag_name", "").lstrip('v')
                
                config = self.get_update_config()
                config["last_check"] = datetime.now().isoformat()
                
                if latest_version and latest_version != self.current_version:
                    config["update_available"] = True
                    config["latest_version"] = latest_version
                    config["download_url"] = release.get("zipball_url")
                    self.save_update_config(config)
                    return True
                else:
                    config["update_available"] = False
                    self.save_update_config(config)
                    return False
        except:
            pass
        
        return False
    
    def is_update_time(self):
        """Verificar si es hora de actualizar (14:00-16:00 Argentina UTC-3)"""
        # Zona horaria Argentina (UTC-3)
        tz_offset = -3
        current_utc = datetime.utcnow()
        current_argentina = current_utc.replace(tzinfo=None) + timedelta(hours=tz_offset)
        
        hour = current_argentina.hour
        return 14 <= hour < 16
    
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
            config = self.get_update_config()
            download_url = config.get("download_url")
            latest_version = config.get("latest_version")
            
            if not download_url:
                return False
            
            # Descargar ZIP
            zip_path = os.path.join(self.base_path, "update.zip")
            response = requests.get(download_url, timeout=30)
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extraer archivos
            extract_path = os.path.join(self.base_path, "update_temp")
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Buscar la carpeta principal extraída
            temp_dirs = os.listdir(extract_path)
            if temp_dirs:
                source_dir = os.path.join(extract_path, temp_dirs[0])
                
                # Copiar archivos (excepto database y assets)
                exclude_dirs = {'database', 'build', 'installer', '.git', '.gitignore'}
                
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
            
            # Guardar nueva versión
            self.save_version(latest_version)
            
            # Limpiar
            shutil.rmtree(extract_path)
            os.remove(zip_path)
            
            # Actualizar config
            config["update_available"] = False
            self.save_update_config(config)
            
            # Reiniciar aplicación
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
