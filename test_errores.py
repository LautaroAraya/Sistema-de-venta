#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema de reporte de errores
Genera errores de prueba para verificar el funcionamiento
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.error_logger import get_error_logger, log_error, log_exception

def test_error_logging():
    """Probar el registro de errores"""
    print("=" * 70)
    print("PRUEBA DEL SISTEMA DE REPORTE DE ERRORES")
    print("=" * 70)
    
    logger = get_error_logger()
    
    print(f"\n✓ Logger inicializado")
    print(f"  Ruta del log: {logger.get_log_file_path()}")
    
    # Test 1: Error simple
    print("\n[TEST 1] Registrando error simple...")
    log_error(
        error_type="TestError",
        error_message="Este es un error de prueba",
        context={
            'usuario': 'test_user',
            'modulo': 'test_module',
            'accion': 'test_action'
        },
        severity="ERROR"
    )
    print("✓ Error simple registrado")
    
    # Test 2: Warning
    print("\n[TEST 2] Registrando advertencia...")
    log_error(
        error_type="TestWarning",
        error_message="Esta es una advertencia de prueba",
        context={
            'usuario': 'admin',
            'modulo': 'productos',
            'accion': 'actualizar_stock'
        },
        severity="WARNING"
    )
    print("✓ Advertencia registrada")
    
    # Test 3: Error crítico con traceback
    print("\n[TEST 3] Registrando error crítico con traceback...")
    try:
        resultado = 10 / 0
    except Exception as e:
        log_exception(e, context={
            'usuario': 'vendedor1',
            'modulo': 'ventas',
            'accion': 'calcular_total'
        })
        print("✓ Error crítico registrado")
    
    # Test 4: Error de validación
    print("\n[TEST 4] Registrando error de validación...")
    log_error(
        error_type="ValidationError",
        error_message="El precio no puede ser negativo: -50.00",
        context={
            'usuario': 'admin',
            'modulo': 'productos',
            'accion': 'crear_producto',
            'producto': 'Producto X',
            'precio': -50.00
        },
        severity="ERROR"
    )
    print("✓ Error de validación registrado")
    
    # Test 5: Error de base de datos
    print("\n[TEST 5] Registrando error de base de datos...")
    log_error(
        error_type="DatabaseError",
        error_message="No se pudo conectar a la base de datos",
        error_traceback="sqlite3.OperationalError: unable to open database file",
        context={
            'usuario': 'system',
            'modulo': 'database',
            'accion': 'connect'
        },
        severity="CRITICAL"
    )
    print("✓ Error de base de datos registrado")
    
    # Obtener resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE ERRORES")
    print("=" * 70)
    
    summary = logger.get_error_summary()
    if summary:
        print(f"\nTotal de errores: {summary['total_errores']}")
        print(f"Último error: {summary['ultimo_error']}")
        
        print("\nErrores por tipo:")
        for error_type, count in summary['errores_por_tipo'].items():
            print(f"  • {error_type}: {count}")
        
        print("\nErrores por severidad:")
        for severity, count in summary['errores_por_severidad'].items():
            print(f"  • {severity}: {count}")
    
    # Mostrar errores recientes
    print("\n" + "=" * 70)
    print("ÚLTIMOS 3 ERRORES REGISTRADOS")
    print("=" * 70)
    
    recent_errors = logger.get_recent_errors(limit=3)
    for i, error in enumerate(reversed(recent_errors), 1):
        print(f"\n--- Error #{i} ---")
        print(error[:300] + "..." if len(error) > 300 else error)
    
    print("\n" + "=" * 70)
    print("✓ PRUEBA COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print(f"\nPuedes revisar el archivo de log completo en:")
    print(f"  {logger.get_log_file_path()}")
    print("\nO desde la interfaz gráfica:")
    print("  1. Inicia sesión como Administrador")
    print("  2. Ve al menú 'Errores del Sistema'")

if __name__ == "__main__":
    try:
        test_error_logging()
        print("\n✓ Todo funcionó correctamente")
    except Exception as e:
        print(f"\n✗ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPresiona Enter para salir...")
