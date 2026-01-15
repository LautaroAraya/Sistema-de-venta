import hashlib
from database.db_manager import DatabaseManager

class Usuario:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def autenticar(self, username, password):
        """Autenticar usuario"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            SELECT id, username, nombre_completo, rol
            FROM usuarios
            WHERE username = ? AND password = ? AND activo = 1
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'nombre_completo': user[2],
                'rol': user[3]
            }
        return None
    
    def crear_usuario(self, username, password, nombre_completo, rol):
        """Crear nuevo usuario"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT INTO usuarios (username, password, nombre_completo, rol)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, nombre_completo, rol))
            conn.commit()
            return True, "Usuario creado exitosamente"
        except sqlite3.IntegrityError:
            return False, "El nombre de usuario ya existe"
        except Exception as e:
            return False, f"Error al crear usuario: {str(e)}"
    
    def listar_usuarios(self):
        """Listar todos los usuarios activos"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, nombre_completo, rol, fecha_creacion
            FROM usuarios
            WHERE activo = 1
            ORDER BY nombre_completo
        ''')
        
        return cursor.fetchall()
    
    def cambiar_password(self, user_id, nueva_password):
        """Cambiar contraseña de usuario"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(nueva_password.encode()).hexdigest()
        
        cursor.execute('''
            UPDATE usuarios
            SET password = ?
            WHERE id = ?
        ''', (password_hash, user_id))
        
        conn.commit()
        return True

import sqlite3
