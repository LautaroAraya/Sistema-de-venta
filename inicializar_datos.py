"""
Script para inicializar la base de datos con datos de ejemplo
Ejecutar después de la primera instalación para poblar el sistema
"""

from database.db_manager import DatabaseManager
from models.categoria import Categoria
from models.proveedor import Proveedor
from models.producto import Producto
from models.usuario import Usuario

def inicializar_datos():
    """Inicializar base de datos con datos de ejemplo"""
    print("Inicializando base de datos...")
    
    db = DatabaseManager()
    
    # Modelos
    categoria_model = Categoria(db)
    proveedor_model = Proveedor(db)
    producto_model = Producto(db)
    usuario_model = Usuario(db)
    
    # Crear categorías
    print("\nCreando categorías...")
    categorias = [
        ("Bebidas", "Bebidas frías y calientes"),
        ("Comida Rápida", "Hamburguesas, hot dogs, etc."),
        ("Snacks", "Papas, nachos, etc."),
        ("Postres", "Helados, pasteles, etc."),
        ("Otros", "Productos varios")
    ]
    
    for nombre, desc in categorias:
        exito, msg = categoria_model.crear_categoria(nombre, desc)
        print(f"  {nombre}: {msg}")
    
    # Crear proveedores
    print("\nCreando proveedores...")
    proveedores = [
        ("Coca-Cola Company", "Juan Pérez", "555-1234", "ventas@coca-cola.com", "Av. Principal 123"),
        ("Bimbo S.A.", "María González", "555-5678", "contacto@bimbo.com", "Calle Comercio 456"),
        ("Lácteos del Valle", "Pedro Ramírez", "555-9012", "ventas@lacteos.com", "Zona Industrial 789")
    ]
    
    for nombre, contacto, tel, email, dir in proveedores:
        exito, msg = proveedor_model.crear_proveedor(nombre, contacto, tel, email, dir)
        print(f"  {nombre}: {msg}")
    
    # Crear productos
    print("\nCreando productos...")
    productos = [
        ("BEB001", "Coca Cola 500ml", "Bebida gaseosa", 1, 2.50, 100, 1),
        ("BEB002", "Pepsi 500ml", "Bebida gaseosa", 1, 2.30, 80, 1),
        ("BEB003", "Agua Mineral 600ml", "Agua embotellada", 1, 1.50, 150, 1),
        ("BEB004", "Jugo de Naranja 1L", "Jugo natural", 1, 3.50, 50, 3),
        ("COM001", "Hamburguesa Simple", "Pan, carne, lechuga, tomate", 2, 5.00, 200, 2),
        ("COM002", "Hamburguesa Doble", "Pan, doble carne, queso", 2, 7.50, 150, 2),
        ("COM003", "Hot Dog", "Pan, salchicha, salsas", 2, 3.50, 100, 2),
        ("SNK001", "Papas Fritas Medianas", "Papas fritas crujientes", 3, 2.50, 120, 2),
        ("SNK002", "Papas Fritas Grandes", "Papas fritas crujientes", 3, 3.50, 100, 2),
        ("SNK003", "Nachos con Queso", "Nachos con salsa de queso", 3, 4.00, 80, 2),
        ("POS001", "Helado de Vainilla", "Copa de helado", 4, 2.50, 60, 3),
        ("POS002", "Helado de Chocolate", "Copa de helado", 4, 2.50, 60, 3),
        ("POS003", "Pastel de Chocolate", "Porción individual", 4, 3.50, 40, 2),
    ]
    
    for codigo, nombre, desc, cat, precio, stock, prov in productos:
        exito, msg = producto_model.crear_producto(codigo, nombre, desc, cat, precio, stock, prov)
        print(f"  {codigo} - {nombre}: {msg}")
    
    # Crear usuario empleado de ejemplo
    print("\nCreando usuario empleado...")
    exito, msg = usuario_model.crear_usuario(
        "empleado1", 
        "empleado123", 
        "María Empleado", 
        "empleado"
    )
    print(f"  {msg}")
    
    print("\n" + "="*50)
    print("DATOS DE EJEMPLO CREADOS EXITOSAMENTE")
    print("="*50)
    print("\nCredenciales disponibles:")
    print("  Admin:")
    print("    Usuario: admin")
    print("    Contraseña: admin123")
    print("\n  Empleado:")
    print("    Usuario: empleado1")
    print("    Contraseña: empleado123")
    print("\n" + "="*50)
    
    db.close()

if __name__ == "__main__":
    inicializar_datos()
