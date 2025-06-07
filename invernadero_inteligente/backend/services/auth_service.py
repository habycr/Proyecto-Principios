# backend/services/auth_service.py
from ..models.user import User
from ..utils.validators import validate_serial_number


class AuthService:
    @staticmethod
    def register_user(nombre, email, password, rol, numero_serie):
        """
        Registra un nuevo usuario cumpliendo con RF01 y RF31
        """
        # Validaciones
        if User.exists(email):
            raise ValueError("El usuario ya existe")

        if not validate_serial_number(numero_serie):
            raise ValueError("Número de serie inválido")

        # Crear y guardar usuario
        user = User(nombre, email, password, rol, numero_serie)
        user.save()

        # Asociar dispositivo (RF31)
        Device.associate_to_user(numero_serie, email)

        return user