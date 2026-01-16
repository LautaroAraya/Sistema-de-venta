#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script mejorado para verificar y buscar nuevas versiones disponibles
Este script comprueba si hay actualizaciones en GitHub y descarga la nueva versión
"""

import os
import sys
import requests
import json
from datetime import datetime

# Colores para la consola
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Imprimir encabezado con formato"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.END}\n")

def print_success(text):
    """Imprimir mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Imprimir mensaje de error"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    """Imprimir mensaje informativo"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text):
    """Imprimir mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def get_current_version():
    """Obtener la versión actual del sistema"""
    try:
        version_file = "version.txt"
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return f.read().strip()
        else:
            print_error("No se encontró el archivo version.txt")
            return None
    except Exception as e:
        print_error(f"Error al leer version.txt: {e}")
        return None

def compare_versions(version1, version2):
    """
    Comparar dos versiones
    Retorna: 1 si version1 > version2, -1 si version1 < version2, 0 si son iguales
    """
    try:
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        # Rellenar con ceros si tienen diferentes longitudes
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts += [0] * (max_len - len(v1_parts))
        v2_parts += [0] * (max_len - len(v2_parts))
        
        for i in range(max_len):
            if v1_parts[i] > v2_parts[i]:
                return 1
            elif v1_parts[i] < v2_parts[i]:
                return -1
        
        return 0
    except:
        return -1

def check_github_release():
    """Verificar si hay una nueva versión en GitHub"""
    repo = "LautaroAraya/Sistema-de-venta"
    github_api = "https://api.github.com/repos"
    
    try:
        print_info("Conectando con GitHub...")
        url = f"{github_api}/{repo}/releases/latest"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            print_warning("No se encontraron releases publicados en GitHub")
            return None
        
        if response.status_code != 200:
            print_error(f"Error al conectar con GitHub: {response.status_code}")
            return None
        
        data = response.json()
        
        # Extraer información del release
        release_info = {
            'version': data.get('tag_name', '').replace('v', ''),
            'name': data.get('name', ''),
            'description': data.get('body', ''),
            'published_at': data.get('published_at', ''),
            'download_url': None,
            'size': 0
        }
        
        # Buscar el asset ZIP
        assets = data.get('assets', [])
        for asset in assets:
            if asset.get('name', '').endswith('.zip'):
                release_info['download_url'] = asset.get('browser_download_url')
                release_info['size'] = asset.get('size', 0)
                break
        
        return release_info
    
    except requests.exceptions.Timeout:
        print_error("Tiempo de espera agotado al conectar con GitHub")
        return None
    except requests.exceptions.ConnectionError:
        print_error("Error de conexión. Verifica tu conexión a internet")
        return None
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        return None

def format_size(size_bytes):
    """Formatear tamaño en bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def download_update(url, filename="update.zip"):
    """Descargar actualización desde GitHub"""
    try:
        print_info(f"Descargando actualización desde: {url}")
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        # Crear carpeta de descargas si no existe
        downloads_dir = "actualizaciones"
        os.makedirs(downloads_dir, exist_ok=True)
        
        filepath = os.path.join(downloads_dir, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Mostrar progreso
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rProgreso: {progress:.1f}% ({format_size(downloaded)} / {format_size(total_size)})", end='')
        
        print()  # Nueva línea después del progreso
        print_success(f"Descarga completada: {filepath}")
        return filepath
    
    except Exception as e:
        print_error(f"Error al descargar actualización: {e}")
        return None

def main():
    """Función principal"""
    print_header("🔍 BUSCAR NUEVA VERSIÓN - SISTEMA DE VENTAS")
    
    # Obtener versión actual
    current_version = get_current_version()
    
    if not current_version:
        print_error("No se pudo determinar la versión actual")
        return
    
    print_info(f"Versión actual instalada: {Colors.BOLD}{current_version}{Colors.END}")
    
    # Buscar en GitHub
    release_info = check_github_release()
    
    if not release_info:
        print_warning("No se pudo verificar si hay actualizaciones disponibles")
        return
    
    latest_version = release_info['version']
    print_info(f"Última versión disponible: {Colors.BOLD}{latest_version}{Colors.END}")
    
    # Comparar versiones
    comparison = compare_versions(latest_version, current_version)
    
    if comparison > 0:
        # Hay una nueva versión
        print()
        print_success("¡Hay una nueva versión disponible!")
        print()
        print(f"{Colors.BOLD}Detalles del release:{Colors.END}")
        print(f"  • Nombre: {release_info['name']}")
        print(f"  • Versión: {latest_version}")
        print(f"  • Publicado: {release_info['published_at']}")
        
        if release_info['size'] > 0:
            print(f"  • Tamaño: {format_size(release_info['size'])}")
        
        if release_info['description']:
            print(f"\n{Colors.BOLD}Cambios en esta versión:{Colors.END}")
            print(release_info['description'])
        
        print()
        
        # Preguntar si desea descargar
        if release_info['download_url']:
            respuesta = input(f"{Colors.YELLOW}¿Desea descargar la actualización ahora? (s/n): {Colors.END}").lower()
            
            if respuesta == 's':
                filename = f"Sistema_de_Venta_v{latest_version}.zip"
                downloaded_file = download_update(release_info['download_url'], filename)
                
                if downloaded_file:
                    print()
                    print_success("Actualización descargada correctamente")
                    print_info(f"Ubicación: {os.path.abspath(downloaded_file)}")
                    print()
                    print_warning("IMPORTANTE: Para instalar la actualización:")
                    print("  1. Cierra el Sistema de Ventas completamente")
                    print("  2. Extrae el archivo ZIP descargado")
                    print("  3. Reemplaza los archivos antiguos con los nuevos")
                    print("  4. Vuelve a ejecutar el sistema")
            else:
                print_info("Descarga cancelada")
        else:
            print_warning("No se encontró archivo de descarga en el release")
    
    elif comparison == 0:
        print_success("Tu sistema está actualizado")
        print_info("No hay nuevas versiones disponibles")
    
    else:
        print_warning("Tu versión es más reciente que la publicada en GitHub")
        print_info("Es posible que estés usando una versión de desarrollo")
    
    print()
    print(f"{Colors.BOLD}Presiona Enter para salir...{Colors.END}")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)
