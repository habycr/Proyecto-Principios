# backend/utils/security.py
import hashlib
import secrets
import binascii


def hash_password(password, salt=None):
    """
    Hashea una contraseña usando PBKDF2_HMAC con SHA256
    Si no se proporciona salt, genera uno nuevo
    """
    if salt is None:
        salt = secrets.token_hex(16)

    # Convertir la contraseña y salt a bytes
    password_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')

    # Hashear usando PBKDF2_HMAC
    dk = hashlib.pbkdf2_hmac(
        'sha256',
        password_bytes,
        salt_bytes,
        100000  # Número de iteraciones
    )

    # Convertir el hash a representación hexadecimal
    hash_hex = binascii.hexlify(dk).decode('utf-8')

    # Retornar el hash y salt concatenados (hash:salt)
    return f"{hash_hex}:{salt}"


def verify_password(hashed_password, input_password):
    """
    Verifica si una contraseña coincide con el hash almacenado
    """
    if not hashed_password or ":" not in hashed_password:
        return False

    hash_hex, salt = hashed_password.split(":")

    # Hashear la contraseña de entrada con el mismo salt
    new_hash = hash_password(input_password, salt).split(":")[0]

    return secrets.compare_digest(hash_hex, new_hash)