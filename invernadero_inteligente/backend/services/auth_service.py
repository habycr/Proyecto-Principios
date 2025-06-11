# backend/services/auth_service.py
from datetime import datetime
from invernadero_inteligente.backend.models.user import User
from invernadero_inteligente.backend.models.device import Device
from invernadero_inteligente.backend.utils.validators import (
    validate_email,
    validate_password,
    validate_serial_number,
    validate_required_fields,
    validate_rol
)
from invernadero_inteligente.backend.utils.security import verify_password
from invernadero_inteligente.backend.utils.logger import log, log_user_action, log_error


class AuthService:
    @staticmethod
    def register_user(data):
        try:
            # Validar campos requeridos
            required_fields = ['nombre', 'email', 'password', 'rol', 'numero_serie']
            missing_fields = validate_required_fields(data, required_fields)
            if missing_fields:
                raise ValueError(f"Faltan campos obligatorios: {', '.join(missing_fields)}")

            # Validaciones específicas
            if not validate_email(data['email']):
                raise ValueError("Formato de email inválido")

            if User.exists(data['email']):
                raise ValueError("El email ya está registrado")

            if not validate_serial_number(data['numero_serie']):
                raise ValueError("Número de serie inválido o no disponible")

            print(f"DEBUG: número de serie recibido: {data['numero_serie']}")
            if not Device.exists(data['numero_serie']):
                raise ValueError(f"El número de serie {data['numero_serie']} no está registrado en el sistema")

            if not Device.is_available(data['numero_serie']):
                raise ValueError(f"El dispositivo {data['numero_serie']} ya está asignado a otro usuario")
            print(f"Contraseña original: {data['password']}")
            hashed_password = User.create_password_hash(data['password'])
            print(f"Contraseña hasheada: {hashed_password}")
            # Crear y guardar usuario
            user = User(
                nombre=data['nombre'],
                email=data['email'],
                password=hashed_password,  # Guardar el hash, no la contraseña en texto plano
                rol=data['rol'],
                numero_serie=data['numero_serie'],
                telefono=data.get('telefono', ''),
                ubicacion=data.get('ubicacion', '')
            )
            user.save()

            Device.associate_to_user(data['numero_serie'], data['email'])

            log_user_action(data['email'], f"Registro exitoso - Dispositivo: {data['numero_serie']}")

            # Devuelve un diccionario serializable
            return {
                "nombre": user.nombre,
                "email": user.email,
                "rol": user.rol,
                "numero_serie": user.numero_serie,
                "telefono": user.telefono,
                "ubicacion": user.ubicacion
            }

        except ValueError as e:
            log_error(e, "register_user")
            raise
        except Exception as e:
            log_error(f"Error en registro: {str(e)}", "auth_service.register_user")
            raise


    @staticmethod
    def login_user(email, password):
        try:
            print(f"DEBUG: Intentando login con email: {email}")  # Log de depuración
            print(f"Datos recibidos - Email: {email}, Password: {password}")  # Debug
            if not email or not password:  # Verificación explícita
                raise ValueError("Email y contraseña son requeridos")

            if not validate_email(email):
                raise ValueError("Formato de email inválido")

            print("DEBUG: Email válido, buscando usuario...")
            user = User.find_by_email(email)

            if not user:
                print(f"DEBUG: Usuario no encontrado para email: {email}")
                raise ValueError("Credenciales inválidas")
            print(f"Usuario encontrado. Hash almacenado: {user.get('password')}")  # Debug
            print("DEBUG: Usuario encontrado, verificando contraseña...")
            if not User.verify_password(user['password'], password):
                print("DEBUG: Contraseña incorrecta")
                raise ValueError("Credenciales inválidas")

            log_user_action(email, "Inicio de sesión exitoso")
            print(f"DEBUG: Login exitoso para {email}")

            return {
                "status": "success",
                "user": {
                    "email": user['email'],
                    "nombre": user['nombre'],
                    "rol": user['rol']
                },
                "message": "Inicio de sesión exitoso"
            }

        except Exception as e:
            log_error(f"Error en login: {str(e)}", "auth_service.login_user")
            print(f"ERROR DETALLADO: {str(e)}")  # Esto aparecerá en la consola del servidor
            raise  # Re-lanza la excepción para que Flask la capture

