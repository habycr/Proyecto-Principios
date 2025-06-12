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
    @staticmethod
    def register_user(data):
        try:
            # 1. Validaciones básicas
            required_fields = ['nombre', 'email', 'password', 'rol', 'numero_serie']
            missing_fields = validate_required_fields(data, required_fields)
            if missing_fields:
                raise ValueError(f"Faltan campos obligatorios: {', '.join(missing_fields)}")

            if not validate_email(data['email']):
                raise ValueError("Formato de email inválido")

            # 2. Verificar unicidad del email
            if User.exists(data['email']):
                raise ValueError("El email ya está registrado")

            serial_numbers = [s.strip() for s in data['numero_serie'].split(',')]
            for serial in serial_numbers:
                if not Device.exists(serial):
                    raise ValueError(f"El número de serie {serial} no existe en el sistema")
                if not Device.is_available(serial):
                    raise ValueError(f"El dispositivo {serial} ya está asignado a otro usuario")
                if User.is_device_assigned(serial):
                    raise ValueError(f"El dispositivo {serial} ya está registrado por otro usuario")

            # 4. Hash de contraseña
            hashed_password = User.create_password_hash(data['password'])

            # 5. PRIMERO asociar dispositivo (operación más crítica)
            try:
                for serial in serial_numbers:
                    Device.associate_to_user(serial, data['email'])
            except Exception as e:
                raise ValueError(f"No se pudo asignar el/los dispositivo(s): {str(e)}")

            # 6. SOLO SI lo anterior funcionó, crear el usuario
            try:
                user = User(
                    nombre=data['nombre'],
                    email=data['email'],
                    password=hashed_password,
                    rol=data['rol'],
                    numero_serie=serial_numbers,
                    telefono=data.get('telefono', ''),
                    ubicacion=data.get('ubicacion', '')
                )
                user.save()
            except Exception as e:
                # Revertir la asociación del dispositivo si falla crear usuario
                try:
                    Device.associate_to_user(serial_numbers, '')  # Desasociar
                except:
                    pass  # Si falla el rollback, al menos registramos el error
                raise ValueError(f"Error al guardar usuario: {str(e)}")

            # 7. Log y retorno
            log_user_action(data['email'], f"Registro exitoso - Dispositivo: {serial_numbers}")
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
            log_error(f"Error inesperado en registro: {str(e)}", "auth_service.register_user")
            raise ValueError("Error interno durante el registro")


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

