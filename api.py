from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import sqlite3
import os

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# Ruta de la base de datos
DB_PATH = os.getenv("SQLITE_PATH")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Ruta de prueba
@app.route('/')
def home():
    return jsonify({"mensaje": "API del sistema de reparaciones funcionando correctamente"})

# 🔧 Endpoint para técnicos: ver todas las reparaciones
@app.route('/api/reparaciones', methods=['GET'])
def obtener_reparaciones():
    conn = get_db_connection()
    reparaciones = conn.execute("""
        SELECT 
            id,
            numero_orden,
            cliente_nombre,
            cliente_telefono,
            cliente_email,
            cliente_dni,
            dispositivo,
            modelo,
            numero_serie,
            problema,
            contrasena,
            patron,
            sena,
            total,
            estado,
            fecha_creacion,
            fecha_entrega,
            observaciones
        FROM reparaciones
        ORDER BY fecha_creacion DESC
    """).fetchall()
    conn.close()

    return jsonify([dict(r) for r in reparaciones])

# 👤 Endpoint para clientes: búsqueda por DNI (sin datos sensibles)
@app.route('/api/reparaciones/cliente/<cliente_dni>', methods=['GET'])
def buscar_reparaciones_cliente(cliente_dni):
    conn = get_db_connection()
    reparaciones = conn.execute("""
        SELECT 
            numero_orden,
            cliente_nombre,
            dispositivo,
            modelo,
            problema,
            estado,
            fecha_creacion,
            fecha_entrega,
            observaciones
        FROM reparaciones
        WHERE cliente_dni = ?
        ORDER BY fecha_creacion DESC
    """, (cliente_dni,)).fetchall()
    conn.close()

    return jsonify([dict(r) for r in reparaciones])

# 🔍 Endpoint para técnicos: ver una reparación específica por número de orden
@app.route('/api/reparaciones/orden/<numero_orden>', methods=['GET'])
def obtener_reparacion_por_orden(numero_orden):
    conn = get_db_connection()
    reparacion = conn.execute("""
        SELECT *
        FROM reparaciones
        WHERE numero_orden = ?
    """, (numero_orden,)).fetchone()
    conn.close()

    if reparacion:
        return jsonify(dict(reparacion))
    else:
        return jsonify({"error": "Reparación no encontrada"}), 404

# 🔄 Endpoint para actualizar el estado de una reparación
@app.route('/api/reparaciones/<int:id>/estado', methods=['PUT'])
def actualizar_estado(id):
    data = request.get_json()
    nuevo_estado = data.get('estado')

    if not nuevo_estado:
        return jsonify({"error": "El campo 'estado' es obligatorio"}), 400

    conn = get_db_connection()
    conn.execute(
        "UPDATE reparaciones SET estado = ? WHERE id = ?",
        (nuevo_estado, id)
    )
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Estado actualizado correctamente"})

# 🧾 Endpoint para registrar el pago final
@app.route('/api/reparaciones/<int:id>/pago', methods=['PUT'])
def registrar_pago_final(id):
    data = request.get_json()
    monto = data.get('monto_pago_final')
    medio_pago = data.get('medio_pago_final')
    fecha_pago = data.get('fecha_pago_final')

    conn = get_db_connection()
    conn.execute("""
        UPDATE reparaciones
        SET monto_pago_final = ?, medio_pago_final = ?, fecha_pago_final = ?
        WHERE id = ?
    """, (monto, medio_pago, fecha_pago, id))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Pago final registrado correctamente"})

if __name__ == '__main__':
    if not DB_PATH:
        raise ValueError("No se encontró la variable SQLITE_PATH en el archivo .env")

    app.run(host='0.0.0.0', port=5000, debug=True)
