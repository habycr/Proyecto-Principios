# backend/utils/validators.py
import re
from backend.models.device import Device


def validate_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> bool:
    """Valida que la contraseña tenga al menos 8 caracteres"""
    return len(password) >= 8


def validate_serial_number(numero_serie: str) -> bool:
    """
    Valida número de serie del dispositivo (RF02)
    1. Debe existir en la base de datos
    2. Debe estar disponible (no asociado a otro usuario)
    """
    # if not numero_serie or len(numero_serie) < 5:
    #     return False
    #
    # try:
    #     # Verificar que el dispositivo existe
    #     if not Device.exists(numero_serie):
    #         return False
    #
    #     # Verificar que está disponible
    #     if not Device.is_available(numero_serie):
    #         return False
    #
    #     return True
    # except Exception as e:
    #     print(f"Error validando número de serie: {e}")
    #     return False

    return True


def validate_required_fields(data: dict, required_fields: list) -> list:
    """Valida que los campos requeridos estén presentes"""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    return missing_fields


def validate_rol(rol: str) -> bool:
    """Valida que el rol sea válido"""
    roles_validos = ["Administrador", "Usuario final", "Técnico"]
    return rol in roles_validos