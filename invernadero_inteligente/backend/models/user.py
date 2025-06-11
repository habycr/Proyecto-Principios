# backend/models/user.py
import hashlib
from datetime import datetime
from invernadero_inteligente.backend.config.settings import PASSWORD_SALT
from invernadero_inteligente.backend.services.google_sheets import GoogleSheetsDB
from invernadero_inteligente.backend.utils.security import hash_password, verify_password
class User:
    def __init__(self, nombre, email, password, rol, numero_serie, telefono='', ubicacion=''):
        self.nombre = nombre
        self.email = email
        self.rol = rol
        self.telefono = telefono
        self.ubicacion = ubicacion
        self.numero_serie = numero_serie
        self.password_hash = password
        self.fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Nueva línea

    # @staticmethod
    # def _hash_password(password: str) -> str:
    #     """Genera hash SHA-256 con salt estático"""
    #     if not PASSWORD_SALT:
    #         raise ValueError("Salt de contraseña no configurado")
    #     return hashlib.sha256(
    #         f"{password}--{PASSWORD_SALT}".encode('utf-8')
    #     ).hexdigest()

    @classmethod
    def exists(cls, email):
        """Verifica si un usuario ya existe"""
        db = GoogleSheetsDB()
        try:
            worksheet = db.sheet.worksheet("Usuarios")
            records = worksheet.get_all_records()
            return any(user['Email'] == email for user in records)
        except Exception as e:
            print(f"Error verificando usuario existente: {e}")
            return False

    def save(self):
        """Guarda el usuario en Google Sheets"""
        db = GoogleSheetsDB()
        worksheet = db.get_worksheet("Usuarios")
        worksheet.append_row([
            self.nombre,
            self.email,
            self.rol,
            self.telefono,
            self.numero_serie,
            self.ubicacion,
            self.password_hash, # Asegúrate de que esto es el hash (no la contraseña en texto plano)
            self.fecha_registro
        ])

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "telefono": self.telefono,
            "ubicacion": self.ubicacion,
            "fecha_registro": self.fecha_registro  # Nuevo campo
        }

    # Añadir estos métodos a la clase User
    @staticmethod
    def find_by_email(email):
        """Busca un usuario por email en la hoja de Google Sheets"""
        db = GoogleSheetsDB()
        try:
            worksheet = db.get_worksheet("Usuarios")
            records = worksheet.get_all_records()

            for user in records:
                if str(user.get('Email', '')).strip().lower() == email.strip().lower():
                    return {
                        'email': user.get('Email', ''),
                        'nombre': user.get('Nombre', ''),
                        'rol': user.get('Rol', ''),
                        'password': user.get('Password', ''),  # Asegúrate que coincide con Google Sheets
                        'fecha_registro': user.get('Fecha Registro', '')  # Nuevo campo
                    }
            return None
        except Exception as e:
            print(f"Error buscando usuario: {e}")
            return None

    @staticmethod
    def verify_password(hashed_password, input_password):
        """Verifica si la contraseña coincide con el hash almacenado"""
        return verify_password(hashed_password, input_password)

    @staticmethod
    def create_password_hash(password):
        """Crea un hash seguro para almacenar la contraseña"""
        return hash_password(password)