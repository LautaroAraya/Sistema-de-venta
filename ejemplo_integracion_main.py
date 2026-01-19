# Ejemplo de Integración en main.py

"""
Este archivo muestra cómo integrar el sistema de licencias
al inicio de tu aplicación main.py
"""

# ==========================================
# PASO 1: Importaciones al inicio del archivo
# ==========================================

import sys
from utils.validador import validar_licencia_inicio

# Tus otras importaciones...
# from views.main_view import MainView
# from database.db_manager import DatabaseManager
# etc.


# ==========================================
# PASO 2: Validar licencia ANTES de cualquier inicialización
# ==========================================

def main():
    """Función principal de la aplicación"""
    
    # VALIDACIÓN DE LICENCIA - DEBE SER LO PRIMERO
    print("Validando licencia del sistema...")
    resultado_licencia = validar_licencia_inicio()
    
    # Si resultado_licencia es None, la app se habrá cerrado automáticamente
    # Si llegamos aquí, la licencia es válida
    
    if resultado_licencia:
        # Opcional: Mostrar información de la licencia en consola
        print(f"✓ Sistema autorizado para: {resultado_licencia.get('cliente', 'N/A')}")
        
        if resultado_licencia['dias_restantes'] > 0 and resultado_licencia['dias_restantes'] <= 30:
            print(f"⚠️  La licencia vence en {resultado_licencia['dias_restantes']} días")
    
    # ==========================================
    # PASO 3: Continuar con la inicialización normal
    # ==========================================
    
    # Aquí va tu código normal de inicialización
    # Por ejemplo:
    
    # Inicializar base de datos
    # db = DatabaseManager()
    
    # Crear ventana principal
    # app = MainView()
    # app.mainloop()
    
    print("Iniciando aplicación...")
    # ... resto de tu código ...


if __name__ == "__main__":
    main()


# ==========================================
# NOTAS IMPORTANTES:
# ==========================================

"""
1. La validación DEBE ejecutarse ANTES de cualquier otra inicialización
   
2. Si la licencia no es válida:
   - Se mostrará automáticamente una ventana de bloqueo
   - La aplicación se cerrará con sys.exit(0)
   - El usuario NO podrá acceder a ninguna funcionalidad
   
3. El HWID se muestra en la ventana de bloqueo para que el cliente
   te lo envíe y puedas registrar su licencia en Firebase
   
4. Puedes usar resultado_licencia para:
   - Mostrar nombre del cliente en la UI
   - Mostrar advertencias de vencimiento
   - Habilitar/deshabilitar funciones según tipo de licencia
   
5. No es necesario hacer nada más - el sistema se encarga de todo

6. Para testing durante desarrollo, puedes comentar temporalmente
   la validación, pero NO olvides habilitarla antes de distribuir
"""
