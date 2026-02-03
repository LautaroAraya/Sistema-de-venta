"""
Script para migrar fotos de reparaciones de ubicaciones antiguas a la ubicación correcta.
Ejecutar si las fotos no aparecen al abrir reparaciones en otra computadora.
"""

import os
import shutil
import sys
from pathlib import Path

# Obtener el directorio base (raíz del proyecto)
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Ubicación correcta donde deben estar las fotos
fotos_correcto = os.path.join(base_path, 'fotos_reparaciones')
os.makedirs(fotos_correcto, exist_ok=True)

# Ubicaciones antiguas donde podrían estar las fotos
ubicaciones_antiguas = [
    os.path.join(os.getcwd(), 'fotos_reparaciones'),
    os.path.join(base_path, 'Sistema de venta', 'fotos_reparaciones'),
]

print("=" * 60)
print("MIGRACIÓN DE FOTOS DE REPARACIONES")
print("=" * 60)
print(f"\nUbicación correcta: {fotos_correcto}")
print(f"Directorio base: {base_path}")
print(f"Directorio actual: {os.getcwd()}")
print("\nBuscando fotos en ubicaciones antiguas...")
print("-" * 60)

fotos_movidas = 0
errores = 0

for ubicacion_antigua in ubicaciones_antiguas:
    if not os.path.exists(ubicacion_antigua):
        print(f"❌ No existe: {ubicacion_antigua}")
        continue
    
    if not os.path.isdir(ubicacion_antigua):
        print(f"⚠️ No es carpeta: {ubicacion_antigua}")
        continue
    
    print(f"\n✅ Encontrada: {ubicacion_antigua}")
    
    # Buscar subcarpetas de tickets (ticket_REP-YYYYMMDD-XXXX)
    for ticket_folder in os.listdir(ubicacion_antigua):
        ticket_path = os.path.join(ubicacion_antigua, ticket_folder)
        
        if not os.path.isdir(ticket_path):
            continue
        
        if not ticket_folder.startswith('ticket_'):
            continue
        
        # Ruta de destino en la ubicación correcta
        destino_ticket = os.path.join(fotos_correcto, ticket_folder)
        
        # Si ya existe en la ubicación correcta, no hacer nada
        if os.path.exists(destino_ticket):
            print(f"  ℹ️ Ya existe: {ticket_folder}")
            continue
        
        # Mover carpeta
        try:
            shutil.move(ticket_path, destino_ticket)
            fotos_movidas += 1
            print(f"  ✅ Movido: {ticket_folder}")
        except Exception as e:
            errores += 1
            print(f"  ❌ Error moviendo {ticket_folder}: {str(e)}")

print("\n" + "=" * 60)
print(f"RESUMEN")
print("=" * 60)
print(f"Fotos/carpetas movidas: {fotos_movidas}")
print(f"Errores: {errores}")
print(f"\nUbicación final de fotos: {fotos_correcto}")

# Listar las fotos encontradas ahora
tickets_encontrados = 0
fotos_totales = 0

print("\n" + "=" * 60)
print("FOTOS DISPONIBLES")
print("=" * 60)

if os.path.exists(fotos_correcto):
    for item in sorted(os.listdir(fotos_correcto)):
        item_path = os.path.join(fotos_correcto, item)
        if os.path.isdir(item_path) and item.startswith('ticket_'):
            tickets_encontrados += 1
            fotos = [f for f in os.listdir(item_path) 
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
            fotos_totales += len(fotos)
            print(f"  {item}: {len(fotos)} fotos")

print(f"\nTotal de tickets: {tickets_encontrados}")
print(f"Total de fotos: {fotos_totales}")
print("\n" + "=" * 60)

input("\nPresiona Enter para cerrar...")
