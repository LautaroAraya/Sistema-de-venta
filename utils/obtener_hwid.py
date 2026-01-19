#!/usr/bin/env python
"""
Utilidad para obtener el HWID de la computadora
Uso: python utils/obtener_hwid.py
"""

import platform
import subprocess
import uuid
import sys


def obtener_hwid():
    """
    Obtiene un identificador único del hardware de la computadora
    
    Returns:
        str: HWID único de la computadora
    """
    try:
        sistema = platform.system()
        print(f"Sistema Operativo: {sistema}")
        
        if sistema == "Windows":
            # Obtener UUID de Windows (más confiable que la placa base)
            try:
                print("Intentando obtener UUID de Windows...")
                hwid = str(subprocess.check_output('wmic csproduct get uuid', 
                                                   shell=True).decode().split('\n')[1].strip())
                print(f"UUID obtenido exitosamente: {hwid}")
                return hwid
            except:
                print("No se pudo obtener UUID, intentando con número de serie de placa base...")
                try:
                    hwid = str(subprocess.check_output('wmic baseboard get serialnumber', 
                                                       shell=True).decode().split('\n')[1].strip())
                    print(f"Serial de placa base obtenido: {hwid}")
                    return hwid
                except:
                    print("No se pudo obtener serial de placa base, usando UUID del sistema...")
                    hwid = str(uuid.getnode())
                    return hwid
        
        elif sistema == "Linux":
            # En Linux, usar /etc/machine-id o UUID del disco
            try:
                print("Intentando leer /etc/machine-id...")
                with open('/etc/machine-id', 'r') as f:
                    hwid = f.read().strip()
                print(f"Machine ID obtenido: {hwid}")
                return hwid
            except:
                print("No se pudo leer /etc/machine-id, usando UUID del nodo...")
                hwid = str(uuid.getnode())
                return hwid
        
        elif sistema == "Darwin":  # macOS
            try:
                print("Obteniendo UUID de macOS...")
                hwid = str(subprocess.check_output("ioreg -rd1 -c IOPlatformExpertDevice | grep UUID", 
                                                   shell=True).decode().split('"')[3])
                print(f"UUID de macOS obtenido: {hwid}")
                return hwid
            except:
                print("No se pudo obtener UUID de macOS, usando fallback...")
                hwid = str(uuid.getnode())
                return hwid
        else:
            # Fallback genérico
            print("Sistema no reconocido, usando fallback...")
            hwid = str(uuid.getnode())
            return hwid
        
    except Exception as e:
        print(f"Error obteniendo HWID: {e}")
        # Fallback final: generar UUID único basado en características del sistema
        fallback = uuid.uuid5(uuid.NAMESPACE_DNS, 
                             f"{platform.node()}-{platform.machine()}-{uuid.getnode()}").hex.upper()
        print(f"Usando fallback UUID: {fallback}")
        return fallback


if __name__ == "__main__":
    print("=" * 60)
    print("UTILIDAD PARA OBTENER HWID DE LA COMPUTADORA")
    print("=" * 60)
    print()
    
    hwid = obtener_hwid()
    
    print()
    print("=" * 60)
    print(f"HWID DE TU PC: {hwid}")
    print("=" * 60)
    print()
    print("📋 Copia este ID y envíalo al administrador del sistema")
    print("   para que registre tu computadora en la base de datos")
    print("   de licencias.")
    print()
    
    # Ofrecer copiar al portapapeles si es Windows
    if platform.system() == "Windows":
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(hwid)
        root.update()
        root.destroy()
        print("✓ El HWID ha sido copiado al portapapeles")
